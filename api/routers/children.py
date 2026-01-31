from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.case import Child
from models.user import User
from schemas.case import ChildCreate, ChildResponse
from security import get_current_user
from utils.authorization import verify_case_access

router = APIRouter(
    prefix="/api/children",
    tags=["children"],
)


@router.post("/{case_id}", response_model=ChildResponse, status_code=201)
async def create_child(
    case_id: int,
    child: ChildCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add child to case"""
    await verify_case_access(case_id, current_user, db)

    # Create child
    new_child = Child(case_id=case_id, **child.model_dump())
    db.add(new_child)
    await db.commit()
    await db.refresh(new_child)

    return new_child


@router.get("/{case_id}", response_model=list[ChildResponse])
async def get_children(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all children for case"""
    await verify_case_access(case_id, current_user, db)
    result = await db.execute(
        select(Child).where(Child.case_id == case_id)
    )
    return result.scalars().all()


@router.get("/single/{child_id}", response_model=ChildResponse)
async def get_child(
    child_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single child by ID"""
    result = await db.execute(select(Child).where(Child.id == child_id))
    child = result.scalar_one_or_none()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    await verify_case_access(child.case_id, current_user, db)
    return child


@router.delete("/{child_id}", status_code=204)
async def delete_child(
    child_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete child"""
    result = await db.execute(select(Child).where(Child.id == child_id))
    child = result.scalar_one_or_none()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    await verify_case_access(child.case_id, current_user, db)
    await db.delete(child)
    await db.commit()
