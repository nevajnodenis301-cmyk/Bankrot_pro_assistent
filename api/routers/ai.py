from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from api.services.ai_service import get_ai_provider

router = APIRouter(prefix="/api/ai", tags=["ai"])


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
        raise HTTPException(500, f"Ошибка AI сервиса: {str(e)}")
