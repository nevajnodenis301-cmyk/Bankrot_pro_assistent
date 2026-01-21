from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


# === Creditors ===
class CreditorCreate(BaseModel):
    name: str
    creditor_type: str | None = None
    debt_amount: Decimal | None = None
    debt_type: str | None = None
    contract_number: str | None = None
    contract_date: date | None = None


class CreditorResponse(CreditorCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


# === Case: creation ===
class CaseCreate(BaseModel):
    full_name: str
    total_debt: Decimal | None = None
    telegram_user_id: int | None = None


# === Case: update ===
class CaseUpdate(BaseModel):
    full_name: str | None = None
    status: str | None = None
    passport_series: str | None = None
    passport_number: str | None = None
    passport_issued_by: str | None = None
    passport_issued_date: date | None = None
    passport_code: str | None = None
    court_name: str | None = None
    court_address: str | None = None
    gender: str | None = None
    marital_status: str | None = None
    sro_name: str | None = None
    sro_address: str | None = None
    inn: str | None = None
    snils: str | None = None
    birth_date: date | None = None
    registration_address: str | None = None
    phone: str | None = None
    email: str | None = None
    total_debt: Decimal | None = None
    monthly_income: Decimal | None = None
    notes: str | None = None


# === Case: public response (for bot) ===
class CasePublic(BaseModel):
    id: int
    case_number: str
    full_name: str
    status: str
    total_debt: Decimal | None
    created_at: datetime
    creditors_count: int = 0
    model_config = ConfigDict(from_attributes=True)


# === Case: full response (for web) ===
class CaseResponse(BaseModel):
    id: int
    case_number: str
    full_name: str
    status: str
    created_at: datetime
    updated_at: datetime
    telegram_user_id: int | None
    passport_series: str | None
    passport_number: str | None
    passport_issued_by: str | None
    passport_issued_date: date | None
    passport_code: str | None
    court_name: str | None
    court_address: str | None
    gender: str | None
    marital_status: str | None
    sro_name: str | None
    sro_address: str | None
    inn: str | None
    snils: str | None
    birth_date: date | None
    registration_address: str | None
    phone: str | None
    email: str | None
    total_debt: Decimal | None
    monthly_income: Decimal | None
    notes: str | None
    creditors: list[CreditorResponse] = []
    model_config = ConfigDict(from_attributes=True)
