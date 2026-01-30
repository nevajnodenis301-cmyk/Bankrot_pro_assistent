from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.case import Child, Case
from schemas.case import ChildCreate, ChildResponse
from security import get_user_or_api_token

router = APIRouter(
    prefix="/api/children",
    tags=["children"],
    dependencies=[Depends(get_user_or_api_token)]
)


@router.post("/{case_id}", response_model=ChildResponse, status_code=201)
async def create_child(
    case_id: int,
    child: ChildCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add child to case"""
    # Verify case exists
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Create child
    new_child = Child(case_id=case_id, **child.model_dump())
    db.add(new_child)
    await db.commit()
    await db.refresh(new_child)

    return new_child


@router.get("/{case_id}", response_model=list[ChildResponse])
async def get_children(case_id: int, db: AsyncSession = Depends(get_db)):
    """Get all children for case"""
    result = await db.execute(
        select(Child).where(Child.case_id == case_id)
    )
    return result.scalars().all()


@router.get("/single/{child_id}", response_model=ChildResponse)
async def get_child(child_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single child by ID"""
    result = await db.execute(select(Child).where(Child.id == child_id))
    child = result.scalar_one_or_none()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    return child


@router.delete("/{child_id}", status_code=204)
async def delete_child(child_id: int, db: AsyncSession = Depends(get_db)):
    """Delete child"""
    result = await db.execute(select(Child).where(Child.id == child_id))
    child = result.scalar_one_or_none()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    await db.delete(child)
    await db.commit()
