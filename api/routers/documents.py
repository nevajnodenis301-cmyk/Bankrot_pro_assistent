from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from io import BytesIO
from database import get_db
from models import Case
from services.document_service import generate_bankruptcy_petition
from security import require_api_token
from sqlalchemy import select

router = APIRouter(
    prefix="/api/documents", 
    tags=["documents"], 
    dependencies=[Depends(require_api_token)]
)


@router.get("/{case_id}/bankruptcy-application")
async def get_bankruptcy_application(case_id: int, db: AsyncSession = Depends(get_db)):
    """Generate bankruptcy petition document"""
    
    # Load case with all relationships
    result = await db.execute(
        select(Case)
        .options(
            selectinload(Case.creditors),
            selectinload(Case.debts),
            selectinload(Case.children),
            selectinload(Case.income_records),
            selectinload(Case.properties),
            selectinload(Case.transactions)
        )
        .where(Case.id == case_id)
    )
    case = result.scalar_one_or_none()
    
    if not case:
        raise HTTPException(status_code=404, detail="Дело не найдено")
    
    try:
        # Generate document - pass Case object directly
        doc_buffer = generate_bankruptcy_petition(case)
        
        return StreamingResponse(
            doc_buffer,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename=bankruptcy_petition_{case.case_number}.docx"
            }
        )
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"Шаблон документа не найден: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации документа: {str(e)}")
