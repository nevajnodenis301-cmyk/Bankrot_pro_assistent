from fastapi import Header, HTTPException, status
from config import settings


async def require_api_token(x_api_token: str | None = Header(default=None)) -> None:
    """
    Simple token-based gatekeeper.
    Uses header X-API-Token; value must match settings.API_TOKEN (or SECRET_KEY as fallback).
    """
    expected = settings.API_TOKEN or settings.SECRET_KEY
    if not expected:
        # Misconfiguration: no secret to validate against
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API token is not configured",
        )

    if x_api_token != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API token",
        )





