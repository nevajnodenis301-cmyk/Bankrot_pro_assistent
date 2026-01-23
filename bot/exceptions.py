"""Custom exceptions for the bankruptcy bot."""


class BotException(Exception):
    """Base exception for bot errors."""

    def __init__(self, message: str, user_message: str = None):
        """
        Args:
            message: Technical error message for logging
            user_message: User-friendly error message in Russian
        """
        super().__init__(message)
        self.user_message = user_message or "Произошла ошибка. Попробуйте позже."


class APIError(BotException):
    """API communication error."""

    def __init__(self, message: str, status_code: int = None):
        user_message = (
            "Не удалось связаться с сервером. Проверьте подключение к интернету и попробуйте позже."
        )
        super().__init__(message, user_message)
        self.status_code = status_code


class APITimeoutError(APIError):
    """API request timeout."""

    def __init__(self, message: str = "API request timeout"):
        user_message = "Сервер не отвечает. Попробуйте позже или обратитесь к администратору."
        super().__init__(message)
        self.user_message = user_message


class AuthenticationError(BotException):
    """Authentication failed."""

    def __init__(self, message: str = "Authentication failed"):
        user_message = (
            "Ошибка авторизации. Обратитесь к администратору для проверки настроек."
        )
        super().__init__(message, user_message)


class ValidationError(BotException):
    """Data validation error."""

    def __init__(self, message: str, field: str = None):
        user_message = f"Некорректные данные: {message}"
        super().__init__(message, user_message)
        self.field = field


class CaseNotFoundError(BotException):
    """Case not found."""

    def __init__(self, case_id: int):
        message = f"Case {case_id} not found"
        user_message = f"Дело не найдено. Проверьте номер дела."
        super().__init__(message, user_message)
        self.case_id = case_id


class AIServiceError(BotException):
    """AI service error."""

    def __init__(self, message: str = "AI service error"):
        user_message = (
            "AI-сервис временно недоступен. Попробуйте позже или обратитесь к администратору."
        )
        super().__init__(message, user_message)


class DocumentGenerationError(BotException):
    """Document generation error."""

    def __init__(self, message: str):
        user_message = "Не удалось сформировать документ. Проверьте данные дела или обратитесь к администратору."
        super().__init__(message, user_message)


class RateLimitError(BotException):
    """Rate limit exceeded."""

    def __init__(self, retry_after: int = None):
        message = "Rate limit exceeded"
        if retry_after:
            user_message = f"Слишком много запросов. Повторите попытку через {retry_after} секунд."
        else:
            user_message = "Слишком много запросов. Подождите немного и попробуйте снова."
        super().__init__(message, user_message)
        self.retry_after = retry_after
