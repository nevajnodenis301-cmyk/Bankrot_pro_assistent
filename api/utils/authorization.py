from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.user import User
from models.case import Case


class AuthorizationError(HTTPException):
    def __init__(self, message: str = "You dont have permission to access this resource"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=message)


def check_case_ownership(
    case: Case,
    current_user: User,
    allow_admin_override: bool = True
) -> None:
    """Validate case ownership or admin override."""
    if allow_admin_override and current_user.role == "admin":
        return

    if case.owner_id != current_user.id:
        raise AuthorizationError(
            f"You dont have permission to access case {case.case_number}"
        )


async def verify_case_access(
    case_id: int,
    current_user: User,
    db: AsyncSession,
    allow_admin_override: bool = True
) -> Case:
    """Verify user has access to a case and return it. Raises 404 if not found, 403 if not owner."""
    result = await db.execute(
        select(Case)
        .options(
            selectinload(Case.creditors),
            selectinload(Case.debts),
            selectinload(Case.children),
            selectinload(Case.income_records),
            selectinload(Case.properties),
            selectinload(Case.transactions),
        )
        .where(Case.id == case_id)
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case with ID {case_id} not found"
        )

    check_case_ownership(case, current_user, allow_admin_override=allow_admin_override)
    return case


def filter_user_cases(
    db_query,
    current_user: User,
    allow_admin_override: bool = True
):
    """Filter query to only show users cases (or all if admin)."""
    if allow_admin_override and current_user.role == "admin":
        return db_query
    return db_query.where(Case.owner_id == current_user.id)
