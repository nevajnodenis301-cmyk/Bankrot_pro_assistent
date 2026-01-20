from io import BytesIO
from docxtpl import DocxTemplate
from datetime import datetime
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def generate_bankruptcy_application(case_data: dict) -> bytes:
    """Generate bankruptcy application document"""
    template_path = TEMPLATES_DIR / "bankruptcy_application.docx"
    doc = DocxTemplate(template_path)

    context = {
        "case_number": case_data["case_number"],
        "full_name": case_data["full_name"],
        "birth_date": case_data.get("birth_date", "___________"),
        "passport": f"{case_data.get('passport_series', '____')} {case_data.get('passport_number', '______')}",
        "inn": case_data.get("inn", "____________"),
        "address": case_data.get("registration_address", "_________________________"),
        "total_debt": f"{case_data.get('total_debt', 0):,.2f}".replace(",", " "),
        "creditors": case_data.get("creditors", []),
        "creditors_count": len(case_data.get("creditors", [])),
        "current_date": datetime.now().strftime("%d.%m.%Y"),
    }

    doc.render(context)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()
