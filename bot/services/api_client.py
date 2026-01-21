import httpx
from config import settings


class APIClient:
    def __init__(self):
        self.base_url = settings.API_BASE_URL
        self.api_token = settings.API_TOKEN

    async def create_case(
        self, full_name: str, total_debt: float, telegram_user_id: int, creditors: list[dict]
    ) -> dict:
        """Create new case and add creditors"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Create case
            response = await client.post(
                f"{self.base_url}/api/cases",
                headers=self._headers,
                json={
                    "full_name": full_name,
                    "total_debt": total_debt,
                    "telegram_user_id": telegram_user_id,
                },
            )
            response.raise_for_status()
            case = response.json()

            # Add creditors
            for creditor in creditors:
                await client.post(
                    f"{self.base_url}/api/creditors/{case['id']}",
                    headers=self._headers,
                    json=creditor,
                )

            return case

    async def get_cases_by_user(self, telegram_user_id: int) -> list[dict]:
        """Get all cases for telegram user"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/api/cases",
                headers=self._headers,
                params={"telegram_user_id": telegram_user_id},
            )
            response.raise_for_status()
            return response.json()

    async def get_case_public(self, case_id: int) -> dict:
        """Get public case data (without confidential info)"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{self.base_url}/api/cases/{case_id}/public")
            response.raise_for_status()
            return response.json()

    async def ask_ai(self, question: str) -> str:
        """Ask AI assistant"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/api/ai/ask",
                headers=self._headers,
                json={"question": question},
            )
            response.raise_for_status()
            return response.json()["answer"]

    @property
    def _headers(self) -> dict:
        """Attach API token when configured."""
        if self.api_token:
            return {"X-API-Token": self.api_token}
        return {}
