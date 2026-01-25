from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.case import Transaction, Case
from schemas.case import TransactionCreate, TransactionResponse
from security import require_api_token

router = APIRouter(
    prefix="/api/transactions",
    tags=["transactions"],
    dependencies=[Depends(require_api_token)]
)


@router.post("/{case_id}", response_model=TransactionResponse, status_code=201)
async def create_transaction(
    case_id: int,
    transaction: TransactionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add transaction to case"""
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    new_transaction = Transaction(case_id=case_id, **transaction.model_dump())
    db.add(new_transaction)
    await db.commit()
    await db.refresh(new_transaction)

    return new_transaction


@router.get("/{case_id}", response_model=list[TransactionResponse])
async def get_transactions(
    case_id: int,
    transaction_type: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    """Get transactions, optionally filtered by type"""
    query = select(Transaction).where(Transaction.case_id == case_id)

    if transaction_type:
        query = query.where(Transaction.transaction_type == transaction_type)

    result = await db.execute(query.order_by(Transaction.transaction_date.desc()))
    return result.scalars().all()


@router.get("/single/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single transaction by ID"""
    result = await db.execute(select(Transaction).where(Transaction.id == transaction_id))
    trans = result.scalar_one_or_none()

    if not trans:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return trans


@router.delete("/{transaction_id}", status_code=204)
async def delete_transaction(transaction_id: int, db: AsyncSession = Depends(get_db)):
    """Delete transaction"""
    result = await db.execute(select(Transaction).where(Transaction.id == transaction_id))
    trans = result.scalar_one_or_none()

    if not trans:
        raise HTTPException(status_code=404, detail="Transaction not found")

    await db.delete(trans)
    await db.commit()
