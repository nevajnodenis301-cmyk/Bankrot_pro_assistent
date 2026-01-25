from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, field_validator
from datetime import date
from database import get_db
from schemas.case import CaseCreate, CaseUpdate, CaseResponse, CasePublic
from services.case_service import CaseService
from security import require_api_token


class ClientDataUpdate(BaseModel):
    """Schema for updating client personal data"""
    passport_series: str | None = None
    passport_number: str | None = None
    passport_issued_by: str | None = None
    passport_issued_date: date | None = None
    passport_code: str | None = None
    birth_date: date | None = None
    registration_address: str | None = None
    phone: str | None = None
    inn: str | None = None
    snils: str | None = None
    gender: str | None = None

    @field_validator("passport_series")
    @classmethod
    def validate_passport_series(cls, v: str | None):
        if v and len(v) != 4:
            raise ValueError("passport_series must be 4 digits")
        return v

    @field_validator("passport_number")
    @classmethod
    def validate_passport_number(cls, v: str | None):
        if v and len(v) != 6:
            raise ValueError("passport_number must be 6 digits")
        return v

    @field_validator("inn")
    @classmethod
    def validate_inn(cls, v: str | None):
        if v and len(v) not in (10, 12):
            raise ValueError("inn must be 10 or 12 digits")
        return v

    @field_validator("snils")
    @classmethod
    def validate_snils(cls, v: str | None):
        if v and len(v.replace("-", "").replace(" ", "")) not in (11, 14):
            raise ValueError("snils must contain 11 digits")
        return v

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str | None):
        if v is None or v == "":
            return None
        if v not in {"M", "F"}:
            raise ValueError("gender must be 'M' or 'F'")
        return v

router = APIRouter(prefix="/api/cases", tags=["cases"], dependencies=[Depends(require_api_token)])

@router.post("", response_model=CaseResponse, status_code=201)
async def create_case(request: Request, data: CaseCreate, db: AsyncSession = Depends(get_db)):
    """Create new bankruptcy case"""
    # Rate limiting is handled by decorator in main.py or should be applied here as decorator
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


@router.patch("/{case_id}/client-data", response_model=CaseResponse)
async def update_client_data(
    case_id: int,
    data: ClientDataUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update client personal data (passport, address, INN, SNILS, etc.)"""
    service = CaseService(db)
    case = await service.get_by_id(case_id)

    if not case:
        raise HTTPException(status_code=404, detail="Дело не найдено")

    # Update only non-None values
    update_data = data.model_dump(exclude_unset=True)
    case_update = CaseUpdate(**update_data)

    updated_case = await service.update(case_id, case_update)
    return updated_case


# ==================== GROUP 1: FAMILY DATA ====================

class FamilyDataUpdate(BaseModel):
    """Schema for updating family data"""
    marital_status: str | None = None  # married, divorced, single
    spouse_name: str | None = None
    marriage_certificate_number: str | None = None
    marriage_certificate_date: date | None = None
    divorce_certificate_number: str | None = None
    divorce_certificate_date: date | None = None


@router.patch("/{case_id}/family-data", response_model=CaseResponse)
async def update_family_data(
    case_id: int,
    data: FamilyDataUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update family data (marital status, spouse info)"""
    service = CaseService(db)
    case = await service.get_by_id(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Дело не найдено")

    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(case, field, value)

    await db.commit()
    await db.refresh(case)

    return case


# ==================== GROUP 1: EMPLOYMENT DATA ====================

class EmploymentDataUpdate(BaseModel):
    """Schema for updating employment data"""
    is_employed: bool | None = None
    is_self_employed: bool | None = None
    employer_name: str | None = None


@router.patch("/{case_id}/employment-data", response_model=CaseResponse)
async def update_employment_data(
    case_id: int,
    data: EmploymentDataUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update employment status"""
    service = CaseService(db)
    case = await service.get_by_id(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Дело не найдено")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(case, field, value)

    await db.commit()
    await db.refresh(case)

    return case


# ==================== GROUP 2: PROPERTY DATA ====================

@router.patch("/{case_id}/toggle-real-estate", response_model=CaseResponse)
async def toggle_real_estate(case_id: int, db: AsyncSession = Depends(get_db)):
    """Toggle has_real_estate flag"""
    service = CaseService(db)
    case = await service.get_by_id(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Дело не найдено")

    case.has_real_estate = not case.has_real_estate

    await db.commit()
    await db.refresh(case)

    return case


# ==================== GROUP 3: COURT DATA ====================

class CourtDataUpdate(BaseModel):
    """Schema for updating court and SRO data"""
    court_name: str | None = None
    court_address: str | None = None
    sro_name: str | None = None
    restructuring_duration: str | None = None
    insolvency_grounds: str | None = None


@router.patch("/{case_id}/court-data", response_model=CaseResponse)
async def update_court_data(
    case_id: int,
    data: CourtDataUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update court and SRO information"""
    service = CaseService(db)
    case = await service.get_by_id(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Дело не найдено")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(case, field, value)

    await db.commit()
    await db.refresh(case)

    return case
