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
        self,
        full_name: str,
        total_debt: float,
        telegram_user_id: int,
        creditors: list[dict],
        procedure_type: str | None = None
    ) -> dict:
        """Create new case and add creditors"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Create case
                case_data = {
                    "full_name": full_name,
                    "total_debt": total_debt,
                    "telegram_user_id": telegram_user_id,
                }
                if procedure_type:
                    case_data["procedure_type"] = procedure_type

                response = await client.post(
                    f"{self.base_url}/api/cases",
                    headers=self._headers,
                    json=case_data,
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

    # ==================== GROUP 1: FAMILY DATA ====================

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def update_case_family_data(self, case_id: int, family_data: dict) -> dict:
        """Update family data (marital status, spouse)"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.patch(
                    f"{self.base_url}/api/cases/{case_id}/family-data",
                    json=family_data,
                    headers=self._headers
                )
                return self._handle_response(response)
        except httpx.TimeoutException:
            logger.error(f"Timeout updating family data for case {case_id}")
            raise APITimeoutError("Timeout updating family data")
        except httpx.NetworkError as e:
            logger.error(f"Network error updating family data: {e}")
            raise APIError(f"Network error: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def add_child(self, case_id: int, child_data: dict) -> dict:
        """Add child to case"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/children/{case_id}",
                    json=child_data,
                    headers=self._headers
                )
                return self._handle_response(response)
        except httpx.TimeoutException:
            logger.error("Timeout adding child")
            raise APITimeoutError("Timeout adding child")
        except httpx.NetworkError as e:
            logger.error(f"Network error adding child: {e}")
            raise APIError(f"Network error: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def get_children(self, case_id: int) -> list:
        """Get children for case"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/children/{case_id}",
                    headers=self._headers
                )
                return self._handle_response(response)
        except httpx.TimeoutException:
            logger.error(f"Timeout getting children for case {case_id}")
            raise APITimeoutError("Timeout getting children")
        except httpx.NetworkError as e:
            logger.error(f"Network error getting children: {e}")
            raise APIError(f"Network error: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def delete_child(self, child_id: int) -> None:
        """Delete child"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.delete(
                    f"{self.base_url}/api/children/{child_id}",
                    headers=self._headers
                )
                if response.status_code != 204:
                    raise APIError(f"Delete failed: {response.status_code}")
        except httpx.TimeoutException:
            logger.error(f"Timeout deleting child {child_id}")
            raise APITimeoutError(f"Timeout deleting child {child_id}")
        except httpx.NetworkError as e:
            logger.error(f"Network error deleting child: {e}")
            raise APIError(f"Network error: {str(e)}")

    # ==================== GROUP 1: EMPLOYMENT DATA ====================

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def update_case_employment_data(self, case_id: int, employment_data: dict) -> dict:
        """Update employment data"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.patch(
                    f"{self.base_url}/api/cases/{case_id}/employment-data",
                    json=employment_data,
                    headers=self._headers
                )
                return self._handle_response(response)
        except httpx.TimeoutException:
            logger.error(f"Timeout updating employment data for case {case_id}")
            raise APITimeoutError("Timeout updating employment data")
        except httpx.NetworkError as e:
            logger.error(f"Network error updating employment data: {e}")
            raise APIError(f"Network error: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def add_income(self, case_id: int, income_data: dict) -> dict:
        """Add income record"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/income/{case_id}",
                    json=income_data,
                    headers=self._headers
                )
                return self._handle_response(response)
        except httpx.TimeoutException:
            logger.error("Timeout adding income")
            raise APITimeoutError("Timeout adding income")
        except httpx.NetworkError as e:
            logger.error(f"Network error adding income: {e}")
            raise APIError(f"Network error: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def get_income(self, case_id: int) -> list:
        """Get income records"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/income/{case_id}",
                    headers=self._headers
                )
                return self._handle_response(response)
        except httpx.TimeoutException:
            logger.error(f"Timeout getting income for case {case_id}")
            raise APITimeoutError("Timeout getting income")
        except httpx.NetworkError as e:
            logger.error(f"Network error getting income: {e}")
            raise APIError(f"Network error: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def delete_income(self, income_id: int) -> None:
        """Delete income record"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.delete(
                    f"{self.base_url}/api/income/{income_id}",
                    headers=self._headers
                )
                if response.status_code != 204:
                    raise APIError(f"Delete failed: {response.status_code}")
        except httpx.TimeoutException:
            logger.error(f"Timeout deleting income {income_id}")
            raise APITimeoutError(f"Timeout deleting income {income_id}")
        except httpx.NetworkError as e:
            logger.error(f"Network error deleting income: {e}")
            raise APIError(f"Network error: {str(e)}")

    # ==================== GROUP 2: PROPERTY DATA ====================

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def toggle_real_estate(self, case_id: int) -> dict:
        """Toggle real estate flag"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.patch(
                    f"{self.base_url}/api/cases/{case_id}/toggle-real-estate",
                    headers=self._headers
                )
                return self._handle_response(response)
        except httpx.TimeoutException:
            logger.error(f"Timeout toggling real estate for case {case_id}")
            raise APITimeoutError("Timeout toggling real estate")
        except httpx.NetworkError as e:
            logger.error(f"Network error toggling real estate: {e}")
            raise APIError(f"Network error: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def add_property(self, case_id: int, property_data: dict) -> dict:
        """Add property"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/properties/{case_id}",
                    json=property_data,
                    headers=self._headers
                )
                return self._handle_response(response)
        except httpx.TimeoutException:
            logger.error("Timeout adding property")
            raise APITimeoutError("Timeout adding property")
        except httpx.NetworkError as e:
            logger.error(f"Network error adding property: {e}")
            raise APIError(f"Network error: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def get_properties(self, case_id: int) -> list:
        """Get properties"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/properties/{case_id}",
                    headers=self._headers
                )
                return self._handle_response(response)
        except httpx.TimeoutException:
            logger.error(f"Timeout getting properties for case {case_id}")
            raise APITimeoutError("Timeout getting properties")
        except httpx.NetworkError as e:
            logger.error(f"Network error getting properties: {e}")
            raise APIError(f"Network error: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def delete_property(self, property_id: int) -> None:
        """Delete property"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.delete(
                    f"{self.base_url}/api/properties/{property_id}",
                    headers=self._headers
                )
                if response.status_code != 204:
                    raise APIError(f"Delete failed: {response.status_code}")
        except httpx.TimeoutException:
            logger.error(f"Timeout deleting property {property_id}")
            raise APITimeoutError(f"Timeout deleting property {property_id}")
        except httpx.NetworkError as e:
            logger.error(f"Network error deleting property: {e}")
            raise APIError(f"Network error: {str(e)}")

    # ==================== GROUP 2: TRANSACTIONS ====================

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def add_transaction(self, case_id: int, transaction_data: dict) -> dict:
        """Add transaction"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/transactions/{case_id}",
                    json=transaction_data,
                    headers=self._headers
                )
                return self._handle_response(response)
        except httpx.TimeoutException:
            logger.error("Timeout adding transaction")
            raise APITimeoutError("Timeout adding transaction")
        except httpx.NetworkError as e:
            logger.error(f"Network error adding transaction: {e}")
            raise APIError(f"Network error: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def get_transactions(self, case_id: int, transaction_type: str = None) -> list:
        """Get transactions, optionally by type"""
        try:
            params = {}
            if transaction_type:
                params['transaction_type'] = transaction_type

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/transactions/{case_id}",
                    params=params,
                    headers=self._headers
                )
                return self._handle_response(response)
        except httpx.TimeoutException:
            logger.error(f"Timeout getting transactions for case {case_id}")
            raise APITimeoutError("Timeout getting transactions")
        except httpx.NetworkError as e:
            logger.error(f"Network error getting transactions: {e}")
            raise APIError(f"Network error: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def delete_transaction(self, transaction_id: int) -> None:
        """Delete transaction"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.delete(
                    f"{self.base_url}/api/transactions/{transaction_id}",
                    headers=self._headers
                )
                if response.status_code != 204:
                    raise APIError(f"Delete failed: {response.status_code}")
        except httpx.TimeoutException:
            logger.error(f"Timeout deleting transaction {transaction_id}")
            raise APITimeoutError(f"Timeout deleting transaction {transaction_id}")
        except httpx.NetworkError as e:
            logger.error(f"Network error deleting transaction: {e}")
            raise APIError(f"Network error: {str(e)}")

    # ==================== GROUP 3: COURT DATA ====================

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def update_case_court_data(self, case_id: int, court_data: dict) -> dict:
        """Update court and SRO data"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.patch(
                    f"{self.base_url}/api/cases/{case_id}/court-data",
                    json=court_data,
                    headers=self._headers
                )
                return self._handle_response(response)
        except httpx.TimeoutException:
            logger.error(f"Timeout updating court data for case {case_id}")
            raise APITimeoutError("Timeout updating court data")
        except httpx.NetworkError as e:
            logger.error(f"Network error updating court data: {e}")
            raise APIError(f"Network error: {str(e)}")

    # ==================== TELEGRAM LINKING ====================

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def confirm_telegram_link(
        self,
        linking_code: str,
        telegram_id: int,
        telegram_username: str | None = None
    ) -> dict | None:
        """
        Confirm Telegram account linking.

        Args:
            linking_code: The code generated by web app
            telegram_id: Telegram user ID
            telegram_username: Telegram username (optional)

        Returns:
            User data if successful, None if code invalid/expired
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/auth/telegram/confirm",
                    json={
                        "linking_code": linking_code,
                        "telegram_id": telegram_id,
                        "telegram_username": telegram_username
                    },
                    headers=self._headers
                )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 400:
                    # Invalid or already used code
                    logger.warning(f"Invalid linking code: {linking_code}")
                    return None
                elif response.status_code == 404:
                    # Code not found or expired
                    logger.warning(f"Linking code not found or expired: {linking_code}")
                    return None
                else:
                    logger.error(f"Unexpected status {response.status_code} confirming telegram link")
                    return None

        except httpx.TimeoutException:
            logger.error("Timeout confirming telegram link")
            raise APITimeoutError("Timeout confirming telegram link")
        except httpx.NetworkError as e:
            logger.error(f"Network error confirming telegram link: {e}")
            raise APIError(f"Network error: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def get_user_by_telegram_id(self, telegram_id: int) -> dict | None:
        """
        Get user by Telegram ID.

        Args:
            telegram_id: Telegram user ID

        Returns:
            User data if found, None otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/auth/telegram/user/{telegram_id}",
                    headers=self._headers
                )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return None
                else:
                    logger.error(f"Unexpected status {response.status_code} getting user by telegram")
                    return None

        except httpx.TimeoutException:
            logger.error(f"Timeout getting user by telegram ID {telegram_id}")
            raise APITimeoutError("Timeout getting user")
        except httpx.NetworkError as e:
            logger.error(f"Network error getting user by telegram: {e}")
            raise APIError(f"Network error: {str(e)}")

    # ==================== DOCUMENTS ====================

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def get_document_types(self) -> list:
        """Get available document types"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/documents/types",
                    headers=self._headers
                )
                return self._handle_response(response)
        except httpx.TimeoutException:
            logger.error("Timeout getting document types")
            raise APITimeoutError("Timeout getting document types")
        except httpx.NetworkError as e:
            logger.error(f"Network error getting document types: {e}")
            raise APIError(f"Network error: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def generate_document(self, case_id: int, document_type: str) -> dict:
        """Generate a document for a case"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/documents/cases/{case_id}/generate",
                    headers=self._headers,
                    json={"document_type": document_type}
                )
                return self._handle_response(response)
        except httpx.TimeoutException:
            logger.error(f"Timeout generating document for case {case_id}")
            raise APITimeoutError("Timeout generating document")
        except httpx.NetworkError as e:
            logger.error(f"Network error generating document: {e}")
            raise APIError(f"Network error: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def get_case_documents(self, case_id: int) -> list:
        """Get list of documents for a case"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/documents/cases/{case_id}/files",
                    headers=self._headers
                )
                return self._handle_response(response)
        except httpx.TimeoutException:
            logger.error(f"Timeout getting documents for case {case_id}")
            raise APITimeoutError("Timeout getting case documents")
        except httpx.NetworkError as e:
            logger.error(f"Network error getting case documents: {e}")
            raise APIError(f"Network error: {str(e)}")

    async def download_document(self, case_id: int, file_name: str) -> bytes | None:
        """Download a document file"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/documents/cases/{case_id}/files/{file_name}",
                    headers=self._headers
                )
                if response.status_code == 200:
                    return response.content
                return None
        except httpx.TimeoutException:
            logger.error(f"Timeout downloading document {file_name}")
            raise APITimeoutError("Timeout downloading document")
        except httpx.NetworkError as e:
            logger.error(f"Network error downloading document: {e}")
            raise APIError(f"Network error: {str(e)}")

    @property
    def _headers(self) -> dict:
        """Attach API token when configured."""
        if self.api_token:
            return {"X-API-Token": self.api_token}
        return {}
