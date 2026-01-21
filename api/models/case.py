from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Text, Numeric, BigInteger, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_number: Mapped[str] = mapped_column(String(20), unique=True, index=True)  # BP-2024-0001

    # Public data (accessible by bot)
    full_name: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="new")  # new, in_progress, court, completed
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    telegram_user_id: Mapped[int | None] = mapped_column(BigInteger, index=True)

    # CONFIDENTIAL data (API/Web only)
    passport_series: Mapped[str | None] = mapped_column(String(4))
    passport_number: Mapped[str | None] = mapped_column(String(6))
    passport_issued_by: Mapped[str | None] = mapped_column(Text)
    passport_issued_date: Mapped[datetime | None] = mapped_column(Date)
    passport_code: Mapped[str | None] = mapped_column(String(10))  # код подразделения
    court_name: Mapped[str | None] = mapped_column(String(255))  # название арбитражного суда
    court_address: Mapped[str | None] = mapped_column(Text)  # адрес суда
    gender: Mapped[str | None] = mapped_column(String(1))  # M or F (for word declension in Russian)
    marital_status: Mapped[str | None] = mapped_column(String(50))  # married/single/divorced/widowed
    sro_name: Mapped[str | None] = mapped_column(String(255))  # название СРО финансового управляющего
    sro_address: Mapped[str | None] = mapped_column(Text)  # адрес СРО
    inn: Mapped[str | None] = mapped_column(String(12))
    snils: Mapped[str | None] = mapped_column(String(14))
    birth_date: Mapped[datetime | None] = mapped_column(Date)
    registration_address: Mapped[str | None] = mapped_column(Text)
    phone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(100))

    # Financial data
    total_debt: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    monthly_income: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))

    notes: Mapped[str | None] = mapped_column(Text)

    creditors: Mapped[list["Creditor"]] = relationship(back_populates="case", cascade="all, delete-orphan")


class Creditor(Base):
    __tablename__ = "creditors"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"))

    name: Mapped[str] = mapped_column(String(255))
    creditor_type: Mapped[str | None] = mapped_column(String(50))  # bank, mfo, individual, tax
    debt_amount: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    debt_type: Mapped[str | None] = mapped_column(String(100))  # credit, microloan, alimony
    contract_number: Mapped[str | None] = mapped_column(String(100))
    contract_date: Mapped[datetime | None] = mapped_column(Date)

    case: Mapped["Case"] = relationship(back_populates="creditors")
