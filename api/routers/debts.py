from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas.case import DebtCreate, DebtUpdate, DebtResponse
from services.case_service import CaseService
from security import get_user_or_api_token

router = APIRouter(prefix="/api/debts", tags=["debts"], dependencies=[Depends(get_user_or_api_token)])


@router.get("/{case_id}", response_model=list[DebtResponse])
async def get_debts(request: Request, case_id: int, db: AsyncSession = Depends(get_db)):
    """Get all debts for a case"""
    service = CaseService(db)
    debts = await service.get_debts(case_id)
    if debts is None:
        raise HTTPException(404, "Дело не найдено")
    return debts


@router.get("/single/{debt_id}", response_model=DebtResponse)
async def get_debt(request: Request, debt_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single debt by ID"""
    service = CaseService(db)
    debt = await service.get_debt_by_id(debt_id)
    if not debt:
        raise HTTPException(404, "Задолженность не найдена")
    return debt


@router.post("/{case_id}", response_model=DebtResponse, status_code=201)
async def add_debt(request: Request, case_id: int, data: DebtCreate, db: AsyncSession = Depends(get_db)):
    """Add debt to case"""
    service = CaseService(db)
    debt = await service.add_debt(case_id, data.model_dump())
    if not debt:
        raise HTTPException(404, "Дело не найдено")
    return debt


@router.put("/{debt_id}", response_model=DebtResponse)
async def update_debt(
    request: Request, debt_id: int, data: DebtUpdate, db: AsyncSession = Depends(get_db)
):
    """Update a debt"""
    service = CaseService(db)
    debt = await service.update_debt(debt_id, data.model_dump(exclude_unset=True))
    if not debt:
        raise HTTPException(404, "Задолженность не найдена")
    return debt


@router.delete("/{debt_id}", status_code=204)
async def delete_debt(request: Request, debt_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a debt"""
    service = CaseService(db)
    deleted = await service.delete_debt(debt_id)
    if not deleted:
        raise HTTPException(404, "Задолженность не найдена")
    return None
