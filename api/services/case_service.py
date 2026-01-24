from datetime import datetime
from sqlalchemy import select
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.case import Case, Creditor
from schemas.case import CaseCreate, CaseUpdate


class CaseService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: CaseCreate) -> Case:
        """Create new bankruptcy case"""
        # Generate case number using database sequence
        year = datetime.now().year

        # Get next sequence value
        result = await self.db.execute(sa.text("SELECT nextval('case_number_seq')"))
        seq_num = result.scalar()

        case_number = f"BP-{year}-{seq_num:04d}"

        case = Case(
            case_number=case_number,
            full_name=data.full_name,
            total_debt=data.total_debt,
            telegram_user_id=data.telegram_user_id,
        )

        self.db.add(case)
        await self.db.commit()
        await self.db.refresh(case)
        return await self.get_by_id(case.id)

    async def get_all(
        self, telegram_user_id: int | None = None, status: str | None = None, limit: int = 50, offset: int = 0
    ) -> list[Case]:
        """Get all cases with optional filters"""
        query = select(Case).options(selectinload(Case.creditors))

        if telegram_user_id:
            query = query.where(Case.telegram_user_id == telegram_user_id)
        if status:
            query = query.where(Case.status == status)

        query = query.order_by(Case.created_at.desc())
        query = query.offset(offset).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, case_id: int) -> Case | None:
        """Get case by ID with creditors"""
        result = await self.db.execute(
            select(Case).where(Case.id == case_id).options(selectinload(Case.creditors))
        )
        return result.scalar_one_or_none()

    async def get_by_case_number(self, case_number: str) -> Case | None:
        """Get case by case number"""
        result = await self.db.execute(
            select(Case).where(Case.case_number == case_number).options(selectinload(Case.creditors))
        )
        return result.scalar_one_or_none()

    async def update(self, case_id: int, data: CaseUpdate) -> Case | None:
        """Update case"""
        case = await self.get_by_id(case_id)
        if not case:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(case, key, value)

        case.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(case)
        return case

    async def delete(self, case_id: int) -> bool:
        """Delete case"""
        case = await self.get_by_id(case_id)
        if not case:
            return False

        await self.db.delete(case)
        await self.db.commit()
        return True

    async def add_creditor(self, case_id: int, creditor_data: dict) -> Creditor | None:
        """Add creditor to case"""
        case = await self.get_by_id(case_id)
        if not case:
            return None

        creditor = Creditor(case_id=case_id, **creditor_data)
        self.db.add(creditor)
        await self.db.commit()
        await self.db.refresh(creditor)
        return creditor

    async def get_creditors(self, case_id: int) -> list[Creditor] | None:
        """Get all creditors for a case"""
        case = await self.get_by_id(case_id)
        if not case:
            return None
        return case.creditors

    async def delete_creditor(self, creditor_id: int) -> bool:
        """Delete a creditor by ID"""
        result = await self.db.execute(
            select(Creditor).where(Creditor.id == creditor_id)
        )
        creditor = result.scalar_one_or_none()
        if not creditor:
            return False

        await self.db.delete(creditor)
        await self.db.commit()
        return True

    async def get_creditor_by_id(self, creditor_id: int) -> Creditor | None:
        """Get a single creditor by ID"""
        result = await self.db.execute(
            select(Creditor).where(Creditor.id == creditor_id)
        )
        return result.scalar_one_or_none()
