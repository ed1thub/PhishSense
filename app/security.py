import logging
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.settings import get_settings

logger = logging.getLogger(__name__)
http_basic = HTTPBasic(auto_error=False)


def require_admin_user(credentials: HTTPBasicCredentials | None = Depends(http_basic)) -> str:
    settings = get_settings()

    if not settings.admin_mode_enabled:
        # Keep this route hidden when admin mode is disabled.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    if not settings.admin_username or not settings.admin_password:
        logger.warning("Admin mode enabled but credentials are not configured")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin credentials are not configured.",
        )

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    is_valid_user = secrets.compare_digest(credentials.username, settings.admin_username)
    is_valid_password = secrets.compare_digest(credentials.password, settings.admin_password)

    if not (is_valid_user and is_valid_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username
