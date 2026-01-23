from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from services.ai_service import get_ai_provider
from security import require_api_token

router = APIRouter(prefix="/api/ai", tags=["ai"], dependencies=[Depends(require_api_token)])


class AIQuestion(BaseModel):
    question: str


class AIAnswer(BaseModel):
    answer: str


@router.post("/ask", response_model=AIAnswer)
async def ask_ai(request: Request, data: AIQuestion):
    """Ask AI assistant about bankruptcy law (127-FZ)"""
    limiter = request.app.state.limiter
    await limiter.check_request_limit(request, "3/minute")

    if not data.question.strip():
        raise HTTPException(400, "Вопрос не может быть пустым")

    try:
        provider = get_ai_provider()
        answer = await provider.ask(data.question)
        return AIAnswer(answer=answer)
    except Exception as e:
        raise HTTPException(503, "AI сервис временно недоступен")
