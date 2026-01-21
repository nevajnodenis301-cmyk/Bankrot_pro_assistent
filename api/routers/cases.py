from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas.case import CaseCreate, CaseUpdate, CaseResponse, CasePublic
from services.case_service import CaseService
from security import require_api_token

router = APIRouter(prefix="/api/cases", tags=["cases"], dependencies=[Depends(require_api_token)])


@router.post("", response_model=CaseResponse, status_code=201)
async def create_case(data: CaseCreate, db: AsyncSession = Depends(get_db)):
    """Create new bankruptcy case"""
    service = CaseService(db)
    return await service.create(data)


@router.get("", response_model=list[CasePublic])
async def list_cases(
    telegram_user_id: int | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List all cases with optional filters"""
    limit = max(1, min(limit, 200))
    offset = max(0, offset)
    service = CaseService(db)
    cases = await service.get_all(telegram_user_id=telegram_user_id, status=status, limit=limit, offset=offset)

    # Return public data only
    return [
        CasePublic(
            id=case.id,
            case_number=case.case_number,
            full_name=case.full_name,
            status=case.status,
            total_debt=case.total_debt,
            created_at=case.created_at,
            creditors_count=len(case.creditors),
        )
        for case in cases
    ]


@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(case_id: int, db: AsyncSession = Depends(get_db)):
    """Get case by ID (full data for web)"""
    service = CaseService(db)
    case = await service.get_by_id(case_id)
    if not case:
        raise HTTPException(404, "Дело не найдено")
    return case


@router.get("/{case_id}/public", response_model=CasePublic)
async def get_case_public(case_id: int, db: AsyncSession = Depends(get_db)):
    """Get case public data (for bot - without passport, INN)"""
    service = CaseService(db)
    case = await service.get_by_id(case_id)
    if not case:
        raise HTTPException(404, "Дело не найдено")

    return CasePublic(
        id=case.id,
        case_number=case.case_number,
        full_name=case.full_name,
        status=case.status,
        total_debt=case.total_debt,
        created_at=case.created_at,
        creditors_count=len(case.creditors),
    )


@router.put("/{case_id}", response_model=CaseResponse)
async def update_case(case_id: int, data: CaseUpdate, db: AsyncSession = Depends(get_db)):
    """Update case"""
    service = CaseService(db)
    case = await service.update(case_id, data)
    if not case:
        raise HTTPException(404, "Дело не найдено")
    return case


@router.delete("/{case_id}", status_code=204)
async def delete_case(case_id: int, db: AsyncSession = Depends(get_db)):
    """Delete case"""
    service = CaseService(db)
    if not await service.delete(case_id):
        raise HTTPException(404, "Дело не найдено")
