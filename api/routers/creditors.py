from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas.case import CreditorCreate, CreditorUpdate, CreditorResponse
from services.case_service import CaseService
from security import get_current_user
from models.user import User
from utils.authorization import verify_case_access

router = APIRouter(prefix="/api/creditors", tags=["creditors"])


@router.get("/{case_id}", response_model=list[CreditorResponse])
async def get_creditors(
    request: Request,
    case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all creditors for a case"""
    await verify_case_access(case_id, current_user, db)
    service = CaseService(db)
    creditors = await service.get_creditors(case_id)
    if creditors is None:
        raise HTTPException(404, "Дело не найдено")
    return creditors


@router.get("/single/{creditor_id}", response_model=CreditorResponse)
async def get_creditor(
    request: Request,
    creditor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single creditor by ID"""
    service = CaseService(db)
    creditor = await service.get_creditor_by_id(creditor_id)
    if not creditor:
        raise HTTPException(404, "Кредитор не найден")
    return creditor


@router.post("/{case_id}", response_model=CreditorResponse, status_code=201)
async def add_creditor(
    request: Request,
    case_id: int,
    data: CreditorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add creditor to case"""
    await verify_case_access(case_id, current_user, db)
    service = CaseService(db)
    creditor = await service.add_creditor(case_id, data.model_dump())
    if not creditor:
        raise HTTPException(404, "Дело не найдено")
    return creditor


@router.put("/{creditor_id}", response_model=CreditorResponse)
async def update_creditor(
    request: Request,
    creditor_id: int,
    data: CreditorUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a creditor"""
    service = CaseService(db)
    existing_creditor = await service.get_creditor_by_id(creditor_id)
    if not existing_creditor:
        raise HTTPException(404, "Creditor not found")
    await verify_case_access(existing_creditor.case_id, current_user, db)
    creditor = await service.update_creditor(creditor_id, data.model_dump(exclude_unset=True))
    if not creditor:
        raise HTTPException(404, "Кредитор не найден")
    return creditor


@router.delete("/{creditor_id}", status_code=204)
async def delete_creditor(
    request: Request,
    creditor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a creditor"""
    service = CaseService(db)
    existing_creditor = await service.get_creditor_by_id(creditor_id)
    if not existing_creditor:
        raise HTTPException(404, "Creditor not found")
    await verify_case_access(existing_creditor.case_id, current_user, db)
    deleted = await service.delete_creditor(creditor_id)
    if not deleted:
        raise HTTPException(404, "Кредитор не найден")
    return None
