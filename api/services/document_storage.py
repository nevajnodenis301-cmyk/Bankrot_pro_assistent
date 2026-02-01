from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Iterable


BASE_DOCUMENTS_DIR = Path(
    os.getenv(
        "CASE_DOCUMENTS_DIR",
        Path(__file__).parent.parent / "case_documents"
    )
)


def get_case_documents_dir(case) -> Path:
    case_dir = BASE_DOCUMENTS_DIR / case.case_number / "Case Documents"
    case_dir.mkdir(parents=True, exist_ok=True)
    return case_dir


def build_document_filename(document_type: str, case_number: str, timestamp: datetime | None = None) -> str:
    safe_type = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in document_type)
    ts = (timestamp or datetime.now()).strftime("%Y%m%d_%H%M%S")
    return f"{safe_type}_{case_number}_{ts}.docx"


def save_document(case, filename: str, buffer) -> Path:
    case_dir = get_case_documents_dir(case)
    file_path = case_dir / filename
    with open(file_path, "wb") as f:
        f.write(buffer.getvalue())
    return file_path


def list_case_documents(case) -> list[dict]:
    case_dir = get_case_documents_dir(case)
    if not case_dir.exists():
        return []

    documents = []
    for path in sorted(case_dir.glob("*.docx"), key=lambda p: p.stat().st_mtime, reverse=True):
        stat = path.stat()
        documents.append(
            {
                "file_name": path.name,
                "size_bytes": stat.st_size,
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            }
        )
    return documents


def resolve_case_document_path(case, file_name: str) -> Path:
    case_dir = get_case_documents_dir(case).resolve()
    file_path = (case_dir / file_name).resolve()
    if not str(file_path).startswith(str(case_dir)):
        raise ValueError("Invalid document path")
    return file_path
