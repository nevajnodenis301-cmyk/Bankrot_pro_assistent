from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.ai_service import get_ai_provider
from security import require_api_token

router = APIRouter(prefix="/api/ai", tags=["ai"], dependencies=[Depends(require_api_token)])


class AIQuestion(BaseModel):
    question: str


class AIAnswer(BaseModel):
    answer: str


@router.post("/ask", response_model=AIAnswer)
async def ask_ai(data: AIQuestion):
    """Ask AI assistant about bankruptcy law (127-FZ)"""
    if not data.question.strip():
        raise HTTPException(400, "Вопрос не может быть пустым")

    try:
        provider = get_ai_provider()
        answer = await provider.ask(data.question)
        return AIAnswer(answer=answer)
    except Exception as e:
        raise HTTPException(503, "AI сервис временно недоступен")
