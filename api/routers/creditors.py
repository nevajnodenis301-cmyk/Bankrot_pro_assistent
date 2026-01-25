from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas.case import CreditorCreate, CreditorUpdate, CreditorResponse
from services.case_service import CaseService
from security import require_api_token

router = APIRouter(prefix="/api/creditors", tags=["creditors"], dependencies=[Depends(require_api_token)])


@router.get("/{case_id}", response_model=list[CreditorResponse])
async def get_creditors(request: Request, case_id: int, db: AsyncSession = Depends(get_db)):
    """Get all creditors for a case"""
    limiter = request.app.state.limiter
    await limiter.check_request_limit(request, "30/minute")
    service = CaseService(db)
    creditors = await service.get_creditors(case_id)
    if creditors is None:
        raise HTTPException(404, "Дело не найдено")
    return creditors


@router.get("/single/{creditor_id}", response_model=CreditorResponse)
async def get_creditor(request: Request, creditor_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single creditor by ID"""
    limiter = request.app.state.limiter
    await limiter.check_request_limit(request, "30/minute")
    service = CaseService(db)
    creditor = await service.get_creditor_by_id(creditor_id)
    if not creditor:
        raise HTTPException(404, "Кредитор не найден")
    return creditor


@router.post("/{case_id}", response_model=CreditorResponse, status_code=201)
async def add_creditor(request: Request, case_id: int, data: CreditorCreate, db: AsyncSession = Depends(get_db)):
    """Add creditor to case"""
    limiter = request.app.state.limiter
    service = CaseService(db)
    creditor = await service.add_creditor(case_id, data.model_dump())
    if not creditor:
        raise HTTPException(404, "Дело не найдено")
    return creditor


@router.put("/{creditor_id}", response_model=CreditorResponse)
async def update_creditor(
    request: Request, creditor_id: int, data: CreditorUpdate, db: AsyncSession = Depends(get_db)
):
    """Update a creditor"""
    limiter = request.app.state.limiter
    await limiter.check_request_limit(request, "30/minute")
    service = CaseService(db)
    creditor = await service.update_creditor(creditor_id, data.model_dump(exclude_unset=True))
    if not creditor:
        raise HTTPException(404, "Кредитор не найден")
    return creditor


@router.delete("/{creditor_id}", status_code=204)
async def delete_creditor(request: Request, creditor_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a creditor"""
    limiter = request.app.state.limiter
    await limiter.check_request_limit(request, "20/minute")
    service = CaseService(db)
    deleted = await service.delete_creditor(creditor_id)
    if not deleted:
        raise HTTPException(404, "Кредитор не найден")
    return None
