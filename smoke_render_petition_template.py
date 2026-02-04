#!/usr/bin/env python3
from pathlib import Path

from docxtpl import DocxTemplate


TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
TEMPLATE_NAME = "bankruptcy_petition_template_v1_jinja2.docx"


def build_test_context() -> dict:
    return {
        "court_name": "Арбитражный суд",
        "court_address": "Тестовый адрес",
        "debtor_full_name": "Тестовый Пользователь",
        "debtor_surname": "Пользователь",
        "debtor_initials": "Т.П.",
        "debtor_birth_date": "01 января 1980",
        "debtor_passport_series": "0000",
        "debtor_passport_number": "000000",
        "debtor_passport_issued_by": "Тестовый орган",
        "debtor_passport_date": "01 января 2000",
        "debtor_passport_code": "000-000",
        "debtor_address": "Тестовый адрес",
        "debtor_inn": "000000000000",
        "debtor_snils": "000-000-000 00",
        "debtor_phone": "+70000000000",
        "debtor_gender_pronoun": "он",
        "ip_certificate_number": "",
        "ip_certificate_date": "",
        "total_debt_rubles": "0",
        "total_debt_rubles_word": "рублей",
        "total_debt_kopecks": "00",
        "total_debt_kopecks_word": "копеек",
        "creditors": [
            {
                "number": 1,
                "name": "Тестовый кредитор",
                "ogrn": "",
                "inn": "",
                "address": "",
            }
        ],
        "debts": [
            {
                "number": 1,
                "creditor_name": "Тестовый кредитор",
                "amount_rubles": "0",
                "amount_rubles_word": "рублей",
                "amount_kopecks": "00",
                "amount_kopecks_word": "копеек",
                "source": "ОКБ",
            }
        ],
        "is_married": False,
        "is_divorced": False,
        "spouse_name": "",
        "marriage_certificate_number": "",
        "marriage_certificate_date": "",
        "divorce_certificate_number": "",
        "divorce_certificate_date": "",
        "has_children": False,
        "multiple_children": False,
        "children": [],
        "is_employed": False,
        "is_self_employed": False,
        "income_years": [],
        "has_real_estate": False,
        "real_estate_description": "",
        "has_movable_property": False,
        "movable_property_description": "",
        "is_pledged": False,
        "property_type": "автомобиль",
        "pledge_creditor": "",
        "pledge_document": "",
        "transactions_real_estate": False,
        "transactions_securities": False,
        "transactions_llc_shares": False,
        "transactions_vehicles": False,
        "insolvency_grounds": "тестовые основания",
        "sro_name": "Тестовое СРО",
        "restructuring_duration": "3 месяца",
        "creditor_registry": [
            {"number": 1, "name": "Тестовый кредитор", "amount": "0", "kopecks": "00"}
        ],
        "appendices": [{"number": 1, "description": "Тестовое приложение", "pages": 1}],
        "petition_date": "01.01.2026",
        "procedure_type": "",
        "procedure_type_label": "",
    }


def main() -> None:
    template_path = TEMPLATES_DIR / TEMPLATE_NAME
    if not template_path.exists():
        raise FileNotFoundError(
            "Template not found: templates/bankruptcy_petition_template_v1_jinja2.docx"
        )

    doc = DocxTemplate(template_path)
    doc.render(build_test_context())

    output_path = Path(__file__).resolve().parent / "out_test.docx"
    doc.save(output_path)
    print(f"Rendered template to {output_path}")


if __name__ == "__main__":
    main()
