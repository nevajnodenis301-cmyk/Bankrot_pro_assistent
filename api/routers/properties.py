from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.case import Property
from models.user import User
from schemas.case import PropertyCreate, PropertyResponse
from security import get_current_user
from utils.authorization import verify_case_access

router = APIRouter(
    prefix="/api/properties",
    tags=["properties"],
)


@router.post("/{case_id}", response_model=PropertyResponse, status_code=201)
async def create_property(
    case_id: int,
    property_data: PropertyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add property to case"""
    await verify_case_access(case_id, current_user, db)

    new_property = Property(case_id=case_id, **property_data.model_dump())
    db.add(new_property)
    await db.commit()
    await db.refresh(new_property)

    return new_property


@router.get("/{case_id}", response_model=list[PropertyResponse])
async def get_properties(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all properties for case"""
    await verify_case_access(case_id, current_user, db)
    result = await db.execute(
        select(Property).where(Property.case_id == case_id)
    )
    return result.scalars().all()


@router.get("/single/{property_id}", response_model=PropertyResponse)
async def get_property(
    property_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single property by ID"""
    result = await db.execute(select(Property).where(Property.id == property_id))
    prop = result.scalar_one_or_none()

    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    await verify_case_access(prop.case_id, current_user, db)
    return prop


@router.delete("/{property_id}", status_code=204)
async def delete_property(
    property_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete property"""
    result = await db.execute(select(Property).where(Property.id == property_id))
    prop = result.scalar_one_or_none()

    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    await verify_case_access(prop.case_id, current_user, db)
    await db.delete(prop)
    await db.commit()
