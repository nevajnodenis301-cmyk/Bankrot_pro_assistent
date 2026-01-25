from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.case import Income, Case
from schemas.case import IncomeCreate, IncomeResponse
from security import require_api_token

router = APIRouter(
    prefix="/api/income",
    tags=["income"],
    dependencies=[Depends(require_api_token)]
)


@router.post("/{case_id}", response_model=IncomeResponse, status_code=201)
async def create_income(
    case_id: int,
    income: IncomeCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add income record to case"""
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    new_income = Income(case_id=case_id, **income.model_dump())
    db.add(new_income)
    await db.commit()
    await db.refresh(new_income)

    return new_income


@router.get("/{case_id}", response_model=list[IncomeResponse])
async def get_income(case_id: int, db: AsyncSession = Depends(get_db)):
    """Get all income records for case"""
    result = await db.execute(
        select(Income)
        .where(Income.case_id == case_id)
        .order_by(Income.year.desc())
    )
    return result.scalars().all()


@router.get("/single/{income_id}", response_model=IncomeResponse)
async def get_single_income(income_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single income record by ID"""
    result = await db.execute(select(Income).where(Income.id == income_id))
    income = result.scalar_one_or_none()

    if not income:
        raise HTTPException(status_code=404, detail="Income not found")

    return income


@router.delete("/{income_id}", status_code=204)
async def delete_income(income_id: int, db: AsyncSession = Depends(get_db)):
    """Delete income record"""
    result = await db.execute(select(Income).where(Income.id == income_id))
    income = result.scalar_one_or_none()

    if not income:
        raise HTTPException(status_code=404, detail="Income not found")

    await db.delete(income)
    await db.commit()
