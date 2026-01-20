import pytest
from unittest.mock import AsyncMock, MagicMock
from aiogram.types import Message, User, Chat
from bot.handlers.start import cmd_start
from bot.handlers.cases import process_full_name, process_total_debt


@pytest.mark.asyncio
async def test_start_command():
    """Test /start command handler"""
    # Mock message
    message = MagicMock(spec=Message)
    message.from_user = MagicMock(spec=User)
    message.from_user.first_name = "Тест"
    message.answer = AsyncMock()

    await cmd_start(message)

    # Verify answer was called
    message.answer.assert_called_once()
    call_args = message.answer.call_args
    assert "Здравствуйте, Тест" in call_args[0][0]
    assert "дисклеймер" in call_args[0][0].lower()


@pytest.mark.asyncio
async def test_process_full_name():
    """Test full name processing in case creation"""
    # Mock message and state
    message = MagicMock(spec=Message)
    message.text = "Тестов Тест Тестович"
    message.answer = AsyncMock()

    state = AsyncMock()
    state.update_data = AsyncMock()
    state.set_state = AsyncMock()

    await process_full_name(message, state)

    # Verify state was updated
    state.update_data.assert_called_once_with(full_name="Тестов Тест Тестович")
    state.set_state.assert_called_once()
    message.answer.assert_called_once()


@pytest.mark.asyncio
async def test_process_total_debt_valid():
    """Test processing valid debt amount"""
    message = MagicMock(spec=Message)
    message.text = "500000"
    message.answer = AsyncMock()

    state = AsyncMock()
    state.update_data = AsyncMock()
    state.set_state = AsyncMock()

    await process_total_debt(message, state)

    # Verify state was updated with float value
    state.update_data.assert_called_once()
    call_args = state.update_data.call_args[1]
    assert call_args["total_debt"] == 500000.0
    assert call_args["creditors"] == []


@pytest.mark.asyncio
async def test_process_total_debt_invalid():
    """Test processing invalid debt amount"""
    message = MagicMock(spec=Message)
    message.text = "invalid_number"
    message.answer = AsyncMock()

    state = AsyncMock()
    state.update_data = AsyncMock()
    state.set_state = AsyncMock()

    await process_total_debt(message, state)

    # Verify error message was sent
    message.answer.assert_called_once()
    call_args = message.answer.call_args[0][0]
    assert "Введите число" in call_args

    # Verify state was not updated
    state.update_data.assert_not_called()
    state.set_state.assert_not_called()


# Note: More comprehensive bot tests would require mocking the API client
# and testing the full flow of case creation
