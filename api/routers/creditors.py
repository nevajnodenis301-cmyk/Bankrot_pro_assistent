from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from api.database import get_db
from api.schemas.case import CreditorCreate, CreditorResponse
from api.services.case_service import CaseService

router = APIRouter(prefix="/api/creditors", tags=["creditors"])


@router.post("/{case_id}", response_model=CreditorResponse, status_code=201)
async def add_creditor(case_id: int, data: CreditorCreate, db: AsyncSession = Depends(get_db)):
    """Add creditor to case"""
    service = CaseService(db)
    creditor = await service.add_creditor(case_id, data.model_dump())
    if not creditor:
        raise HTTPException(404, "Дело не найдено")
    return creditor
