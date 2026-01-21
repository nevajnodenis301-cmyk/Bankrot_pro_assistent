from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from io import BytesIO
from database import get_db
from services.case_service import CaseService
from services.document_service import generate_bankruptcy_application, generate_bankruptcy_petition

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.get("/{case_id}/bankruptcy-application")
async def get_bankruptcy_application(case_id: int, db: AsyncSession = Depends(get_db)):
    """Generate bankruptcy application document"""
    service = CaseService(db)
    case = await service.get_by_id(case_id)
    if not case:
        raise HTTPException(404, "Дело не найдено")

    # Convert case to dict for document generation
    case_data = {
        "case_number": case.case_number,
        "full_name": case.full_name,
        "birth_date": case.birth_date.strftime("%d.%m.%Y") if case.birth_date else None,
        "passport_series": case.passport_series,
        "passport_number": case.passport_number,
        "inn": case.inn,
        "registration_address": case.registration_address,
        "total_debt": float(case.total_debt) if case.total_debt else 0,
        "creditors": [
            {
                "name": c.name,
                "debt_amount": float(c.debt_amount) if c.debt_amount else 0,
                "debt_type": c.debt_type,
            }
            for c in case.creditors
        ],
    }

    doc_bytes = generate_bankruptcy_application(case_data)

    return StreamingResponse(
        BytesIO(doc_bytes),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename=bankruptcy_{case.case_number}.docx"},
    )


@router.get("/cases/{case_id}/document/petition")
async def get_bankruptcy_petition(case_id: int, db: AsyncSession = Depends(get_db)):
    """Generate bankruptcy petition document with full Russian formatting"""
    service = CaseService(db)
    case = await service.get_by_id(case_id)
    if not case:
        raise HTTPException(404, "Дело не найдено")

    # Generate document using new service
    doc_buffer = generate_bankruptcy_petition(case)

    return StreamingResponse(
        doc_buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename=bankruptcy_petition_{case.case_number}.docx"},
    )
