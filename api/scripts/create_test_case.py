#!/usr/bin/env python3
"""
Create a comprehensive test case with all fields populated.

This script creates a complete bankruptcy case with:
- Full debtor information (passport, INN, SNILS, addresses, etc.)
- Court information
- Multiple creditors with full details
- Debts linked to creditors
- Children (with passport and birth certificate)
- Income records
- Property (real estate and vehicles)
- Transactions (all types)
- All boolean flags

Usage:
    # From Docker:
    docker-compose exec api python /app/scripts/create_test_case.py

    # Or locally (from project root with env vars set):
    cd api && python scripts/create_test_case.py
"""
import asyncio
import sys
import os
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

# Add api directory to path for imports (parent of scripts/)
api_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(api_dir))

# Now we can import from api
from sqlalchemy import text
from database import async_session_maker, engine
from models.case import Case, Creditor, Debt, Child, Income, Property, Transaction


async def create_test_case():
    """Create a comprehensive test case with all fields populated."""

    async with async_session_maker() as db:
        # Generate case number
        year = datetime.now().year
        result = await db.execute(text("SELECT nextval('case_number_seq')"))
        seq_num = result.scalar()
        case_number = f"BP-{year}-{seq_num:04d}"

        # ===== CREATE MAIN CASE =====
        case = Case(
            case_number=case_number,

            # Basic info
            full_name="Иванов Иван Иванович",
            status="in_progress",
            telegram_user_id=123456789,

            # Personal Information (will be auto-encrypted by SQLAlchemy)
            passport_series="4515",
            passport_number="123456",
            passport_issued_by="Отделом УФМС России по г. Москве по району Тверской",
            passport_issued_date=date(2015, 3, 15),
            passport_code="770-001",

            birth_date=date(1985, 6, 20),
            registration_address="г. Москва, ул. Тверская, д. 15, кв. 42",
            phone="+7 (999) 123-45-67",
            email="ivanov@example.com",
            inn="771234567890",
            snils="123-456-789 01",
            gender="M",

            # Court Information
            court_name="Арбитражный суд города Москвы",
            court_address="115225, г. Москва, ул. Большая Тульская, д. 17",

            # Procedure Type
            procedure_type="realization",  # or "restructuring"

            # IP Status (Individual Entrepreneur)
            ip_certificate_number="",  # Not an IP
            ip_certificate_date=None,

            # Marital Status & Family
            marital_status="married",
            spouse_name="Иванова Мария Петровна",
            marriage_certificate_number="I-АГ № 654321",
            marriage_certificate_date=date(2010, 8, 12),
            divorce_certificate_number=None,
            divorce_certificate_date=None,

            # Employment
            is_employed=True,
            is_self_employed=False,
            employer_name="ООО 'Рога и Копыта'",

            # Property Flags
            has_real_estate=True,
            has_movable_property=True,

            # Financial
            total_debt=Decimal("1250000.50"),
            monthly_income=Decimal("85000.00"),

            # Financial Manager (SRO)
            sro_name="Ассоциация арбитражных управляющих 'Сибирь'",
            sro_address="630099, г. Новосибирск, ул. Ленина, д. 1, оф. 100",
            restructuring_duration="3 года",

            # Document generation
            insolvency_grounds="Гражданин прекратил расчеты с кредиторами, то есть перестал исполнять денежные обязательства, срок исполнения которых наступил",

            notes="Тестовое дело для проверки генерации документов. Все данные вымышленные.",
        )

        db.add(case)
        await db.flush()  # Get case.id

        # ===== CREATE CREDITORS =====
        creditors_data = [
            {
                "number": 1,
                "name": "ПАО Сбербанк",
                "ogrn": "1027700132195",
                "inn": "7707083893",
                "address": "117997, г. Москва, ул. Вавилова, д. 19",
                "creditor_type": "bank",
                "debt_amount": Decimal("750000.00"),
                "debt_type": "Кредит потребительский",
                "contract_number": "12345678",
                "contract_date": date(2020, 5, 15),
            },
            {
                "number": 2,
                "name": "АО 'Тинькофф Банк'",
                "ogrn": "1027739642281",
                "inn": "7710140679",
                "address": "127287, г. Москва, ул. Хуторская 2-я, д. 38А, стр. 26",
                "creditor_type": "bank",
                "debt_amount": Decimal("350000.50"),
                "debt_type": "Кредитная карта",
                "contract_number": "0987654321",
                "contract_date": date(2019, 11, 20),
            },
            {
                "number": 3,
                "name": "ООО МКК 'Быстроденьги'",
                "ogrn": "1116315000167",
                "inn": "6315640296",
                "address": "443080, г. Самара, ул. Революционная, д. 70, лит. А",
                "creditor_type": "mfo",
                "debt_amount": Decimal("150000.00"),
                "debt_type": "Микрозайм",
                "contract_number": "МЗ-2021-55555",
                "contract_date": date(2021, 3, 10),
            },
        ]

        creditor_objects = []
        for cred_data in creditors_data:
            creditor = Creditor(case_id=case.id, **cred_data)
            db.add(creditor)
            creditor_objects.append(creditor)

        await db.flush()  # Get creditor IDs

        # ===== CREATE DEBTS =====
        debts_data = [
            {
                "number": 1,
                "creditor_name": "ПАО Сбербанк",
                "amount_rubles": 750000,
                "amount_kopecks": 0,
                "source": "ОКБ",
                "creditor_id": creditor_objects[0].id,
            },
            {
                "number": 2,
                "creditor_name": "АО 'Тинькофф Банк'",
                "amount_rubles": 350000,
                "amount_kopecks": 50,
                "source": "НБКИ",
                "creditor_id": creditor_objects[1].id,
            },
            {
                "number": 3,
                "creditor_name": "ООО МКК 'Быстроденьги'",
                "amount_rubles": 150000,
                "amount_kopecks": 0,
                "source": "Эквифакс",
                "creditor_id": creditor_objects[2].id,
            },
        ]

        for debt_data in debts_data:
            debt = Debt(case_id=case.id, **debt_data)
            db.add(debt)

        # ===== CREATE CHILDREN =====
        children_data = [
            {
                # Child with passport (14+ years old)
                "child_name": "Иванов Петр Иванович",
                "child_birth_date": date(2008, 9, 5),
                "child_has_certificate": True,
                "child_certificate_number": "I-МЮ № 789012",
                "child_certificate_date": date(2008, 9, 20),
                "child_has_passport": True,
                "child_passport_series": "4520",
                "child_passport_number": "654321",
                "child_passport_issued_by": "Отделом УФМС России по г. Москве",
                "child_passport_date": date(2022, 9, 10),
                "child_passport_code": "770-002",
            },
            {
                # Child with birth certificate only (under 14)
                "child_name": "Иванова Анна Ивановна",
                "child_birth_date": date(2015, 4, 12),
                "child_has_certificate": True,
                "child_certificate_number": "II-МЮ № 456789",
                "child_certificate_date": date(2015, 4, 25),
                "child_has_passport": False,
                "child_passport_series": None,
                "child_passport_number": None,
                "child_passport_issued_by": None,
                "child_passport_date": None,
                "child_passport_code": None,
            },
        ]

        for child_data in children_data:
            child = Child(case_id=case.id, **child_data)
            db.add(child)

        # ===== CREATE INCOME RECORDS =====
        income_data = [
            {
                "year": "2023",
                "amount_rubles": 1020000,
                "amount_kopecks": 0,
                "certificate_number": "2-НДФЛ-2023-001",
            },
            {
                "year": "2022",
                "amount_rubles": 960000,
                "amount_kopecks": 0,
                "certificate_number": "2-НДФЛ-2022-001",
            },
            {
                "year": "2021",
                "amount_rubles": 840000,
                "amount_kopecks": 0,
                "certificate_number": "2-НДФЛ-2021-001",
            },
        ]

        for inc_data in income_data:
            income = Income(case_id=case.id, **inc_data)
            db.add(income)

        # ===== CREATE PROPERTIES =====
        properties_data = [
            {
                # Real estate
                "property_type": "real_estate",
                "description": "Квартира, общей площадью 65 кв.м., расположенная по адресу: г. Москва, ул. Тверская, д. 15, кв. 42",
                "vehicle_make": None,
                "vehicle_model": None,
                "vehicle_year": None,
                "vehicle_vin": None,
                "vehicle_color": None,
                "is_pledged": True,
                "pledge_creditor": "ПАО Сбербанк",
                "pledge_document": "Договор ипотеки № 12345678-И от 15.05.2020",
            },
            {
                # Vehicle
                "property_type": "vehicle",
                "description": "Легковой автомобиль Toyota Camry 2019 года выпуска",
                "vehicle_make": "Toyota",
                "vehicle_model": "Camry",
                "vehicle_year": 2019,
                "vehicle_vin": "XW7BF4FK70S123456",
                "vehicle_color": "черный",
                "is_pledged": False,
                "pledge_creditor": None,
                "pledge_document": None,
            },
        ]

        for prop_data in properties_data:
            prop = Property(case_id=case.id, **prop_data)
            db.add(prop)

        # ===== CREATE TRANSACTIONS =====
        transactions_data = [
            {
                "transaction_type": "real_estate",
                "description": "Продажа дачного участка площадью 6 соток в СНТ 'Радуга' Московской области",
                "transaction_date": date(2022, 7, 15),
                "amount": Decimal("850000.00"),
            },
            {
                "transaction_type": "securities",
                "description": "Продажа акций ПАО 'Газпром' в количестве 100 штук",
                "transaction_date": date(2023, 2, 20),
                "amount": Decimal("25000.00"),
            },
            {
                "transaction_type": "llc_shares",
                "description": "Выход из состава участников ООО 'Ромашка' с долей 25%",
                "transaction_date": date(2021, 11, 30),
                "amount": Decimal("100000.00"),
            },
            {
                "transaction_type": "vehicles",
                "description": "Продажа мотоцикла Honda CBR600RR 2017 года выпуска",
                "transaction_date": date(2022, 4, 10),
                "amount": Decimal("450000.00"),
            },
        ]

        for trans_data in transactions_data:
            transaction = Transaction(case_id=case.id, **trans_data)
            db.add(transaction)

        # ===== COMMIT ALL =====
        await db.commit()

        print(f"\n{'='*60}")
        print(f"  TEST CASE CREATED SUCCESSFULLY!")
        print(f"{'='*60}")
        print(f"  Case Number: {case_number}")
        print(f"  Case ID:     {case.id}")
        print(f"  Full Name:   {case.full_name}")
        print(f"{'='*60}")
        print(f"\n  Created records:")
        print(f"    - 1 Case with all fields populated")
        print(f"    - {len(creditors_data)} Creditors")
        print(f"    - {len(debts_data)} Debts")
        print(f"    - {len(children_data)} Children")
        print(f"    - {len(income_data)} Income records")
        print(f"    - {len(properties_data)} Properties")
        print(f"    - {len(transactions_data)} Transactions")
        print(f"\n  Encrypted PII fields:")
        print(f"    - Passport: {case.passport_series} {case.passport_number}")
        print(f"    - INN: {case.inn}")
        print(f"    - SNILS: {case.snils}")
        print(f"    - Phone: {case.phone}")
        print(f"    - Address: {case.registration_address[:30]}...")
        print(f"\n{'='*60}\n")

        return case


async def main():
    """Main entry point."""
    print("\nCreating comprehensive test case...")
    print("This will populate all fields for document generation testing.\n")

    try:
        case = await create_test_case()
        print("Done! You can now test document generation with this case.\n")
    except Exception as e:
        print(f"\nERROR: Failed to create test case: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
