from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.case import Property, Case
from schemas.case import PropertyCreate, PropertyResponse
from security import get_user_or_api_token

router = APIRouter(
    prefix="/api/properties",
    tags=["properties"],
    dependencies=[Depends(get_user_or_api_token)]
)


@router.post("/{case_id}", response_model=PropertyResponse, status_code=201)
async def create_property(
    case_id: int,
    property_data: PropertyCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add property to case"""
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    new_property = Property(case_id=case_id, **property_data.model_dump())
    db.add(new_property)
    await db.commit()
    await db.refresh(new_property)

    return new_property


@router.get("/{case_id}", response_model=list[PropertyResponse])
async def get_properties(case_id: int, db: AsyncSession = Depends(get_db)):
    """Get all properties for case"""
    result = await db.execute(
        select(Property).where(Property.case_id == case_id)
    )
    return result.scalars().all()


@router.get("/single/{property_id}", response_model=PropertyResponse)
async def get_property(property_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single property by ID"""
    result = await db.execute(select(Property).where(Property.id == property_id))
    prop = result.scalar_one_or_none()

    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    return prop


@router.delete("/{property_id}", status_code=204)
async def delete_property(property_id: int, db: AsyncSession = Depends(get_db)):
    """Delete property"""
    result = await db.execute(select(Property).where(Property.id == property_id))
    prop = result.scalar_one_or_none()

    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    await db.delete(prop)
    await db.commit()
