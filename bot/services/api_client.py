import httpx
import logging
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
from config import settings
from exceptions import (
    APIError,
    APITimeoutError,
    AuthenticationError,
    CaseNotFoundError,
    AIServiceError,
    RateLimitError,
)

logger = logging.getLogger(__name__)


class APIClient:
    def __init__(self):
        self.base_url = settings.API_BASE_URL
        self.api_token = settings.API_TOKEN

    def _handle_response(self, response: httpx.Response) -> dict:
        """Handle API response and raise appropriate exceptions."""
        try:
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise AuthenticationError("API authentication failed")
            elif response.status_code == 404:
                raise CaseNotFoundError(0)  # Will be overridden with actual ID
            elif response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                raise RateLimitError(int(retry_after) if retry_after else None)
            elif response.status_code >= 500:
                raise APIError(
                    f"Server error: {response.status_code}",
                    status_code=response.status_code
                )
            else:
                raise APIError(
                    f"API error: {response.status_code}",
                    status_code=response.status_code
                )
        except httpx.JSONDecodeError:
            raise APIError("Invalid JSON response from server")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def create_case(
        self, full_name: str, total_debt: float, telegram_user_id: int, creditors: list[dict]
    ) -> dict:
        """Create new case and add creditors"""
        try:
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
                case = self._handle_response(response)

                # Add creditors
                for creditor in creditors:
                    creditor_response = await client.post(
                        f"{self.base_url}/api/creditors/{case['id']}",
                        headers=self._headers,
                        json=creditor,
                    )
                    self._handle_response(creditor_response)

                return case
        except httpx.TimeoutException:
            logger.error("Timeout creating case")
            raise APITimeoutError("Timeout creating case")
        except httpx.NetworkError as e:
            logger.error(f"Network error creating case: {e}")
            raise APIError(f"Network error: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def get_cases_by_user(self, telegram_user_id: int) -> list[dict]:
        """Get all cases for telegram user"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/cases",
                    headers=self._headers,
                    params={"telegram_user_id": telegram_user_id},
                )
                return self._handle_response(response)
        except httpx.TimeoutException:
            logger.error("Timeout getting cases by user")
            raise APITimeoutError("Timeout getting cases")
        except httpx.NetworkError as e:
            logger.error(f"Network error getting cases: {e}")
            raise APIError(f"Network error: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def get_case_public(self, case_id: int) -> dict:
        """Get public case data (without confidential info)"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.base_url}/api/cases/{case_id}/public")
                return self._handle_response(response)
        except httpx.TimeoutException:
            logger.error(f"Timeout getting case {case_id}")
            raise APITimeoutError(f"Timeout getting case {case_id}")
        except httpx.NetworkError as e:
            logger.error(f"Network error getting case {case_id}: {e}")
            raise APIError(f"Network error: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def get_case(self, case_id: int) -> dict:
        """Get full case data (including confidential info for editing)"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/cases/{case_id}",
                    headers=self._headers,
                )
                return self._handle_response(response)
        except httpx.TimeoutException:
            logger.error(f"Timeout getting full case {case_id}")
            raise APITimeoutError(f"Timeout getting case {case_id}")
        except httpx.NetworkError as e:
            logger.error(f"Network error getting full case {case_id}: {e}")
            raise APIError(f"Network error: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def update_case_client_data(self, case_id: int, client_data: dict) -> dict:
        """
        Update client personal data for a case.

        Args:
            case_id: Case ID
            client_data: Dict with fields like passport_series, passport_number, etc.

        Returns:
            Updated case data
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.patch(
                    f"{self.base_url}/api/cases/{case_id}/client-data",
                    json=client_data,
                    headers=self._headers,
                )
                return self._handle_response(response)
        except httpx.TimeoutException:
            logger.error(f"Timeout updating client data for case {case_id}")
            raise APITimeoutError("Timeout updating client data")
        except httpx.NetworkError as e:
            logger.error(f"Network error updating client data for case {case_id}: {e}")
            raise APIError(f"Network error: {str(e)}")

    @retry(
        stop=stop_after_attempt(2),  # Only 2 attempts for AI (it's slower)
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def ask_ai(self, question: str) -> str:
        """Ask AI assistant"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/ai/ask",
                    headers=self._headers,
                    json={"question": question},
                )
                result = self._handle_response(response)
                return result["answer"]
        except httpx.TimeoutException:
            logger.error("Timeout asking AI")
            raise AIServiceError("AI service timeout")
        except httpx.NetworkError as e:
            logger.error(f"Network error asking AI: {e}")
            raise AIServiceError(f"Network error: {str(e)}")
        except KeyError:
            logger.error("Invalid AI response format")
            raise AIServiceError("Invalid response from AI service")

    # ==================== CREDITORS ====================

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def add_creditor(self, case_id: int, creditor_data: dict) -> dict:
        """Add new creditor to case"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/creditors/{case_id}",
                    json=creditor_data,
                    headers=self._headers
                )
                return self._handle_response(response)
        except httpx.TimeoutException:
            logger.error("Timeout adding creditor")
            raise APITimeoutError("Timeout adding creditor")
        except httpx.NetworkError as e:
            logger.error(f"Network error adding creditor: {e}")
            raise APIError(f"Network error: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def get_creditor(self, creditor_id: int) -> dict:
        """Get a single creditor by ID"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/creditors/single/{creditor_id}",
                    headers=self._headers
                )
                return self._handle_response(response)
        except httpx.TimeoutException:
            logger.error(f"Timeout getting creditor {creditor_id}")
            raise APITimeoutError(f"Timeout getting creditor {creditor_id}")
        except httpx.NetworkError as e:
            logger.error(f"Network error getting creditor {creditor_id}: {e}")
            raise APIError(f"Network error: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def update_creditor(self, creditor_id: int, creditor_data: dict) -> dict:
        """Update creditor"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.put(
                    f"{self.base_url}/api/creditors/{creditor_id}",
                    json=creditor_data,
                    headers=self._headers
                )
                return self._handle_response(response)
        except httpx.TimeoutException:
            logger.error(f"Timeout updating creditor {creditor_id}")
            raise APITimeoutError(f"Timeout updating creditor {creditor_id}")
        except httpx.NetworkError as e:
            logger.error(f"Network error updating creditor {creditor_id}: {e}")
            raise APIError(f"Network error: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def delete_creditor(self, creditor_id: int) -> None:
        """Delete creditor"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.delete(
                    f"{self.base_url}/api/creditors/{creditor_id}",
                    headers=self._headers
                )
                if response.status_code != 204:
                    raise APIError(f"Delete failed: {response.status_code}")
        except httpx.TimeoutException:
            logger.error(f"Timeout deleting creditor {creditor_id}")
            raise APITimeoutError(f"Timeout deleting creditor {creditor_id}")
        except httpx.NetworkError as e:
            logger.error(f"Network error deleting creditor {creditor_id}: {e}")
            raise APIError(f"Network error: {str(e)}")

    # ==================== DEBTS ====================

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def add_debt(self, case_id: int, debt_data: dict) -> dict:
        """Add new debt to case"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/debts/{case_id}",
                    json=debt_data,
                    headers=self._headers
                )
                return self._handle_response(response)
        except httpx.TimeoutException:
            logger.error("Timeout adding debt")
            raise APITimeoutError("Timeout adding debt")
        except httpx.NetworkError as e:
            logger.error(f"Network error adding debt: {e}")
            raise APIError(f"Network error: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def get_debt(self, debt_id: int) -> dict:
        """Get a single debt by ID"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/debts/single/{debt_id}",
                    headers=self._headers
                )
                return self._handle_response(response)
        except httpx.TimeoutException:
            logger.error(f"Timeout getting debt {debt_id}")
            raise APITimeoutError(f"Timeout getting debt {debt_id}")
        except httpx.NetworkError as e:
            logger.error(f"Network error getting debt {debt_id}: {e}")
            raise APIError(f"Network error: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def update_debt(self, debt_id: int, debt_data: dict) -> dict:
        """Update debt"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.put(
                    f"{self.base_url}/api/debts/{debt_id}",
                    json=debt_data,
                    headers=self._headers
                )
                return self._handle_response(response)
        except httpx.TimeoutException:
            logger.error(f"Timeout updating debt {debt_id}")
            raise APITimeoutError(f"Timeout updating debt {debt_id}")
        except httpx.NetworkError as e:
            logger.error(f"Network error updating debt {debt_id}: {e}")
            raise APIError(f"Network error: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def delete_debt(self, debt_id: int) -> None:
        """Delete debt"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.delete(
                    f"{self.base_url}/api/debts/{debt_id}",
                    headers=self._headers
                )
                if response.status_code != 204:
                    raise APIError(f"Delete failed: {response.status_code}")
        except httpx.TimeoutException:
            logger.error(f"Timeout deleting debt {debt_id}")
            raise APITimeoutError(f"Timeout deleting debt {debt_id}")
        except httpx.NetworkError as e:
            logger.error(f"Network error deleting debt {debt_id}: {e}")
            raise APIError(f"Network error: {str(e)}")

    @property
    def _headers(self) -> dict:
        """Attach API token when configured."""
        if self.api_token:
            return {"X-API-Token": self.api_token}
        return {}
