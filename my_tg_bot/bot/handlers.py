from telegram import Update
from telegram.ext import ContextTypes
from api import get_random_cocktail
from html import escape

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! 🍹\n"
        "Я подскажу случайный коктейль.\n"
        "Напиши /cocktail"
    )



async def cocktail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    name, instructions, ingredients, photo_url = get_random_cocktail()

    if not name:
        await update.message.reply_text("Ошибка API. Попробуй позже.")
        return

    message = (
        f"<b>{escape(name)}</b>\n\n"
        f"<b>Ингредиенты:</b>\n"
        + "\n".join(f"• {escape(ing)}" for ing in ingredients)
        + f"\n\n<b>Инструкция:</b>\n{escape(instructions)}"
    )

    if photo_url:
        await update.message.reply_photo(
            photo=photo_url,
            caption=message,
            parse_mode="HTML"
        )
    else:
        await update.message.reply_text(message, parse_mode="HTML")