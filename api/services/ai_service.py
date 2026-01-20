import httpx
from abc import ABC, abstractmethod
from config import settings

SYSTEM_PROMPT = """Ты — юридический AI-ассистент по банкротству физических лиц в России.

Отвечай на вопросы по 127-ФЗ "О несостоятельности (банкротстве)":
- Процедуры: реструктуризация долгов, реализация имущества
- Права и обязанности должника
- Требования к документам
- Роль финансового управляющего

ВАЖНО:
- Ты НЕ заменяешь профессионального юриста
- Рекомендуй консультацию со специалистом для конкретных случаев
- Ссылайся на статьи 127-ФЗ где уместно
- Отвечай кратко и понятно на русском языке"""


class AIProvider(ABC):
    @abstractmethod
    async def ask(self, question: str) -> str:
        pass


class TimewebProvider(AIProvider):
    def __init__(self):
        self.api_key = settings.TIMEWEB_API_KEY
        self.api_url = settings.TIMEWEB_API_URL

    async def ask(self, question: str) -> str:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.api_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": "gpt-3.5-turbo",  # or another Timeweb model
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": question},
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.7,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]


class YandexGPTProvider(AIProvider):
    def __init__(self):
        self.api_key = settings.YANDEXGPT_API_KEY
        self.folder_id = settings.YANDEXGPT_FOLDER_ID

    async def ask(self, question: str) -> str:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
                headers={
                    "Authorization": f"Api-Key {self.api_key}",
                    "x-folder-id": self.folder_id,
                },
                json={
                    "modelUri": f"gpt://{self.folder_id}/yandexgpt-lite",
                    "completionOptions": {"maxTokens": 1000, "temperature": 0.7},
                    "messages": [
                        {"role": "system", "text": SYSTEM_PROMPT},
                        {"role": "user", "text": question},
                    ],
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["result"]["alternatives"][0]["message"]["text"]


def get_ai_provider() -> AIProvider:
    """Factory for AI providers"""
    provider = settings.AI_PROVIDER.lower()
    if provider == "yandexgpt":
        return YandexGPTProvider()
    return TimewebProvider()  # default
