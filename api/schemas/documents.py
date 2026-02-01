from datetime import datetime
from pydantic import BaseModel


class DocumentTypeResponse(BaseModel):
    document_type: str
    label: str
    description: str | None = None


class DocumentGenerateRequest(BaseModel):
    document_type: str


class DocumentFileResponse(BaseModel):
    file_name: str
    size_bytes: int
    modified_at: datetime
    document_type: str | None = None
