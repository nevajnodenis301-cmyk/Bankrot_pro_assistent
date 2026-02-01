from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
from models import Case
from schemas.documents import DocumentTypeResponse, DocumentGenerateRequest, DocumentFileResponse
from services.document_service import generate_bankruptcy_petition, generate_bankruptcy_application
from services.document_storage import (
    build_document_filename,
    save_document,
    list_case_documents,
    resolve_case_document_path,
)
from security import get_user_or_api_token
from utils.authorization import verify_case_access

router = APIRouter(
    prefix="/api/documents",
    tags=["documents"],
    dependencies=[Depends(get_user_or_api_token)]
)

DOCUMENT_TYPES = {
    "bankruptcy_petition": {
        "label": "Bankruptcy Petition",
        "description": "Full petition with comprehensive data",
        "generator": generate_bankruptcy_petition,
    },
    "bankruptcy_application": {
        "label": "Bankruptcy Application",
        "description": "Basic application template",
        "generator": generate_bankruptcy_application,
    },
}


async def load_case_for_document(case_id: int, db: AsyncSession) -> Case | None:
    result = await db.execute(
        select(Case)
        .options(
            selectinload(Case.creditors),
            selectinload(Case.debts),
            selectinload(Case.children),
            selectinload(Case.income_records),
            selectinload(Case.properties),
            selectinload(Case.transactions)
        )
        .where(Case.id == case_id)
    )
    return result.scalar_one_or_none()


async def get_case_with_access(case_id: int, db: AsyncSession, current_user):
    if current_user:
        return await verify_case_access(case_id, current_user, db)

    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Р”РµР»Рѕ РЅРµ РЅР°Р№РґРµРЅРѕ")
    return case


def build_document_response(file_path, file_name: str):
    return StreamingResponse(
        open(file_path, "rb"),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={file_name}"},
    )


@router.get("/types", response_model=list[DocumentTypeResponse])
async def list_document_types():
    return [
        DocumentTypeResponse(
            document_type=doc_type,
            label=meta["label"],
            description=meta["description"],
        )
        for doc_type, meta in DOCUMENT_TYPES.items()
    ]


@router.get("/cases/{case_id}/files", response_model=list[DocumentFileResponse])
async def list_case_files(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_user_or_api_token),
):
    case = await get_case_with_access(case_id, db, current_user)
    documents = list_case_documents(case)
    results = []
    for doc in documents:
        document_type = None
        for doc_type in DOCUMENT_TYPES:
            if doc["file_name"].startswith(f"{doc_type}_"):
                document_type = doc_type
                break
        results.append(
            DocumentFileResponse(
                file_name=doc["file_name"],
                size_bytes=doc["size_bytes"],
                modified_at=doc["modified_at"],
                document_type=document_type,
            )
        )
    return results


@router.post("/cases/{case_id}/generate", response_model=DocumentFileResponse)
async def generate_case_document(
    case_id: int,
    payload: DocumentGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_user_or_api_token),
):
    if payload.document_type not in DOCUMENT_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported document type")

    case = await get_case_with_access(case_id, db, current_user)
    case_with_relations = await load_case_for_document(case_id, db)
    if not case_with_relations:
        raise HTTPException(status_code=404, detail="Р”РµР»Рѕ РЅРµ РЅР°Р№РґРµРЅРѕ")

    generator = DOCUMENT_TYPES[payload.document_type]["generator"]
    doc_buffer = generator(case_with_relations)
    file_name = build_document_filename(payload.document_type, case.case_number)
    file_path = save_document(case, file_name, doc_buffer)
    stat = file_path.stat()
    return DocumentFileResponse(
        file_name=file_name,
        size_bytes=stat.st_size,
        modified_at=datetime.fromtimestamp(stat.st_mtime),
        document_type=payload.document_type,
    )


@router.get("/cases/{case_id}/files/{file_name}")
async def download_case_document(
    case_id: int,
    file_name: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_user_or_api_token),
):
    case = await get_case_with_access(case_id, db, current_user)
    try:
        file_path = resolve_case_document_path(case, file_name)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document path")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Document not found")

    return build_document_response(file_path, file_name)


@router.get("/{case_id}/bankruptcy-application")
async def get_bankruptcy_application(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_user_or_api_token),
):
    """Generate bankruptcy application document (basic template)."""
    case = await get_case_with_access(case_id, db, current_user)
    case_with_relations = await load_case_for_document(case_id, db)

    if not case_with_relations:
        raise HTTPException(status_code=404, detail="Р”РµР»Рѕ РЅРµ РЅР°Р№РґРµРЅРѕ")

    try:
        doc_buffer = generate_bankruptcy_application(case_with_relations)
        file_name = build_document_filename("bankruptcy_application", case.case_number)
        file_path = save_document(case, file_name, doc_buffer)
        return build_document_response(file_path, file_name)
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"РЁР°Р±Р»РѕРЅ РґРѕРєСѓРјРµРЅС‚Р° РЅРµ РЅР°Р№РґРµРЅ: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"РћС€РёР±РєР° РіРµРЅРµСЂР°С†РёРё РґРѕРєСѓРјРµРЅС‚Р°: {str(e)}")


@router.get("/cases/{case_id}/document/petition")
async def get_bankruptcy_petition(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_user_or_api_token),
):
    """Generate full bankruptcy petition document."""
    case = await get_case_with_access(case_id, db, current_user)
    case_with_relations = await load_case_for_document(case_id, db)

    if not case_with_relations:
        raise HTTPException(status_code=404, detail="Р”РµР»Рѕ РЅРµ РЅР°Р№РґРµРЅРѕ")

    try:
        doc_buffer = generate_bankruptcy_petition(case_with_relations)
        file_name = build_document_filename("bankruptcy_petition", case.case_number)
        file_path = save_document(case, file_name, doc_buffer)
        return build_document_response(file_path, file_name)
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"РЁР°Р±Р»РѕРЅ РґРѕРєСѓРјРµРЅС‚Р° РЅРµ РЅР°Р№РґРµРЅ: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"РћС€РёР±РєР° РіРµРЅРµСЂР°С†РёРё РґРѕРєСѓРјРµРЅС‚Р°: {str(e)}")
