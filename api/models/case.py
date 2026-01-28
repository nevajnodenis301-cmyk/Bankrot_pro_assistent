from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Text, Numeric, BigInteger, Date, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base



class Case(Base):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_number: Mapped[str] = mapped_column(String(20), unique=True, index=True)

    # Public data
    full_name: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="new")
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    telegram_user_id: Mapped[int | None] = mapped_column(BigInteger, index=True)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    # Personal Information
    passport_series: Mapped[str | None] = mapped_column(String(4))
    passport_number: Mapped[str | None] = mapped_column(String(6))
    passport_issued_by: Mapped[str | None] = mapped_column(Text)
    passport_issued_date: Mapped[datetime | None] = mapped_column(Date)
    passport_code: Mapped[str | None] = mapped_column(String(10))
    
    birth_date: Mapped[datetime | None] = mapped_column(Date)
    registration_address: Mapped[str | None] = mapped_column(Text)
    phone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(100))
    inn: Mapped[str | None] = mapped_column(String(12))
    snils: Mapped[str | None] = mapped_column(String(14))
    gender: Mapped[str | None] = mapped_column(String(1))  # M or F
    
    # Court Information
    court_name: Mapped[str | None] = mapped_column(String(255))
    court_address: Mapped[str | None] = mapped_column(Text)
    
    # IP Status
    ip_certificate_number: Mapped[str | None] = mapped_column(String(100))
    ip_certificate_date: Mapped[datetime | None] = mapped_column(Date)
    
    # Marital Status & Family
    marital_status: Mapped[str | None] = mapped_column(String(50))  # married/divorced/single/widowed
    spouse_name: Mapped[str | None] = mapped_column(String(255))
    marriage_certificate_number: Mapped[str | None] = mapped_column(String(100))
    marriage_certificate_date: Mapped[datetime | None] = mapped_column(Date)
    divorce_certificate_number: Mapped[str | None] = mapped_column(String(100))
    divorce_certificate_date: Mapped[datetime | None] = mapped_column(Date)
    
    # Employment
    is_employed: Mapped[bool | None] = mapped_column(Boolean, default=False)
    is_self_employed: Mapped[bool | None] = mapped_column(Boolean, default=False)
    employer_name: Mapped[str | None] = mapped_column(String(255))
    
    # Property Flags
    has_real_estate: Mapped[bool | None] = mapped_column(Boolean, default=False)
    has_movable_property: Mapped[bool | None] = mapped_column(Boolean, default=False)
    
    # Financial
    total_debt: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    monthly_income: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    
    # Financial Manager
    sro_name: Mapped[str | None] = mapped_column(String(255))
    sro_address: Mapped[str | None] = mapped_column(Text)
    restructuring_duration: Mapped[str | None] = mapped_column(String(50))  # "3 месяца", "6 месяцев"
    
    # Document generation
    insolvency_grounds: Mapped[str | None] = mapped_column(Text)
    
    notes: Mapped[str | None] = mapped_column(Text)

    # Relationships
    creditors: Mapped[list["Creditor"]] = relationship(back_populates="case", cascade="all, delete-orphan")
    debts: Mapped[list["Debt"]] = relationship(back_populates="case", cascade="all, delete-orphan")
    children: Mapped[list["Child"]] = relationship(back_populates="case", cascade="all, delete-orphan")
    income_records: Mapped[list["Income"]] = relationship(back_populates="case", cascade="all, delete-orphan")
    properties: Mapped[list["Property"]] = relationship(back_populates="case", cascade="all, delete-orphan")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="case", cascade="all, delete-orphan")
    owner: Mapped["User"] = relationship(back_populates="cases")

class Creditor(Base):
    __tablename__ = "creditors"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"))
    
    number: Mapped[int | None] = mapped_column()  # Sequential number in list
    name: Mapped[str] = mapped_column(String(255))
    ogrn: Mapped[str | None] = mapped_column(String(20))
    inn: Mapped[str | None] = mapped_column(String(12))
    address: Mapped[str | None] = mapped_column(Text)
    
    creditor_type: Mapped[str | None] = mapped_column(String(50))  # bank, mfo, individual
    debt_amount: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    debt_type: Mapped[str | None] = mapped_column(String(100))
    contract_number: Mapped[str | None] = mapped_column(String(100))
    contract_date: Mapped[datetime | None] = mapped_column(Date)

    case: Mapped["Case"] = relationship(back_populates="creditors")


class Debt(Base):
    """Detailed debt breakdown per creditor"""
    __tablename__ = "debts"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"))
    creditor_id: Mapped[int | None] = mapped_column(ForeignKey("creditors.id", ondelete="SET NULL"))
    
    number: Mapped[int | None] = mapped_column()  # Sequential number
    creditor_name: Mapped[str] = mapped_column(String(255))
    amount_rubles: Mapped[int] = mapped_column()
    amount_kopecks: Mapped[int] = mapped_column()
    source: Mapped[str | None] = mapped_column(String(50))  # "СКОРИНГ БЮРО" or "ОКБ"
    
    case: Mapped["Case"] = relationship(back_populates="debts")


class Child(Base):
    """Child dependents"""
    __tablename__ = "children"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"))
    
    child_name: Mapped[str] = mapped_column(String(255))
    child_birth_date: Mapped[datetime] = mapped_column(Date)
    
    # Birth certificate (for children under 14)
    child_has_certificate: Mapped[bool] = mapped_column(Boolean, default=True)
    child_certificate_number: Mapped[str | None] = mapped_column(String(100))
    child_certificate_date: Mapped[datetime | None] = mapped_column(Date)
    
    # Passport (for children 14+)
    child_has_passport: Mapped[bool] = mapped_column(Boolean, default=False)
    child_passport_series: Mapped[str | None] = mapped_column(String(4))
    child_passport_number: Mapped[str | None] = mapped_column(String(6))
    child_passport_issued_by: Mapped[str | None] = mapped_column(Text)
    child_passport_date: Mapped[datetime | None] = mapped_column(Date)
    child_passport_code: Mapped[str | None] = mapped_column(String(10))
    
    case: Mapped["Case"] = relationship(back_populates="children")


class Income(Base):
    """Yearly income records for self-employed"""
    __tablename__ = "income"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"))
    
    year: Mapped[str] = mapped_column(String(4))  # "2024"
    amount_rubles: Mapped[int] = mapped_column()
    amount_kopecks: Mapped[int] = mapped_column()
    certificate_number: Mapped[str | None] = mapped_column(String(100))
    
    case: Mapped["Case"] = relationship(back_populates="income_records")


class Property(Base):
    """Real estate and movable property"""
    __tablename__ = "properties"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"))
    
    property_type: Mapped[str] = mapped_column(String(50))  # "real_estate", "vehicle", "other"
    description: Mapped[str] = mapped_column(Text)
    
    # For vehicles
    vehicle_make: Mapped[str | None] = mapped_column(String(100))
    vehicle_model: Mapped[str | None] = mapped_column(String(100))
    vehicle_year: Mapped[int | None] = mapped_column()
    vehicle_vin: Mapped[str | None] = mapped_column(String(50))
    vehicle_color: Mapped[str | None] = mapped_column(String(50))
    
    # Pledge information
    is_pledged: Mapped[bool] = mapped_column(Boolean, default=False)
    pledge_creditor: Mapped[str | None] = mapped_column(String(255))
    pledge_document: Mapped[str | None] = mapped_column(Text)
    
    case: Mapped["Case"] = relationship(back_populates="properties")


class Transaction(Base):
    """3-year transaction history"""
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"))
    
    transaction_type: Mapped[str] = mapped_column(String(50))  # "real_estate", "securities", "llc_shares", "vehicles"
    description: Mapped[str] = mapped_column(Text)
    transaction_date: Mapped[datetime | None] = mapped_column(Date)
    amount: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    
    case: Mapped["Case"] = relationship(back_populates="transactions")
