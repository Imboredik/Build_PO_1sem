import pytest
from unittest.mock import AsyncMock, patch
from my_tg_bot.bot.handlers import start, cocktail
from telegram import Update, Message
from telegram.ext import ContextTypes


@pytest.mark.asyncio
async def test_start_handler():
    update = AsyncMock(spec=Update)
    update.message = AsyncMock(spec=Message)
    context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)

    await start(update, context)

    update.message.reply_text.assert_called_once_with(
        "Привет! 🍹\n"
        "Я подскажу случайный коктейль.\n"
        "Напиши /cocktail"
    )


@pytest.mark.asyncio
@patch('my_tg_bot.bot.handlers.get_random_cocktail')
async def test_cocktail_handler_success_with_photo(mock_get_random_cocktail):
    mock_get_random_cocktail.return_value = (
        "Test Cocktail",
        "Mix ingredients.",
        ["1 oz Ingredient1", "2 oz Ingredient2"],
        "https://example.com/image.jpg"
    )

    update = AsyncMock(spec=Update)
    update.message = AsyncMock(spec=Message)
    context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)

    await cocktail(update, context)

    update.message.reply_photo.assert_called_once()
    args, kwargs = update.message.reply_photo.call_args
    assert kwargs['photo'] == "https://example.com/image.jpg"
    assert "<b>Test Cocktail</b>" in kwargs['caption']
    assert "• 1 oz Ingredient1" in kwargs['caption']
    assert "Mix ingredients." in kwargs['caption']
    assert kwargs['parse_mode'] == "HTML"


@pytest.mark.asyncio
@patch('my_tg_bot.bot.handlers.get_random_cocktail')
async def test_cocktail_handler_success_no_photo(mock_get_random_cocktail):
    mock_get_random_cocktail.return_value = (
        "Test Cocktail",
        "Mix ingredients.",
        ["1 oz Ingredient1", "2 oz Ingredient2"],
        None
    )

    update = AsyncMock(spec=Update)
    update.message = AsyncMock(spec=Message)
    context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)

    await cocktail(update, context)

    update.message.reply_text.assert_called_once()
    args, kwargs = update.message.reply_text.call_args
    assert "<b>Test Cocktail</b>" in args[0]
    assert "• 1 oz Ingredient1" in args[0]
    assert "Mix ingredients." in args[0]
    assert kwargs['parse_mode'] == "HTML"


@pytest.mark.asyncio
@patch('my_tg_bot.bot.handlers.get_random_cocktail')
async def test_cocktail_handler_failure(mock_get_random_cocktail):
    mock_get_random_cocktail.return_value = (None, None, None, None)

    update = AsyncMock(spec=Update)
    update.message = AsyncMock(spec=Message)
    context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)

    await cocktail(update, context)

    update.message.reply_text.assert_called_once_with("Ошибка API. Попробуй позже.")