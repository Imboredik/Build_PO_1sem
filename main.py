import logging
import os
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

from database import initialize_db
from my_tg_bot.bot.handlers import start, cocktail  # Предполагается, что start и cocktail работают

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)


def main() -> None:
    # 1. Инициализация БД
    if not initialize_db():
        print("Не удалось инициализировать базу данных. Запуск бота может быть нестабильным.")

    # 2. Получаем BOT_TOKEN из окружения
    BOT_TOKEN = os.getenv("BOT_TOKEN")

    try:
        print("Запуск main... Тестируем вывод.")

        if not BOT_TOKEN:
            print("КРИТИЧЕСКАЯ ОШИБКА: BOT_TOKEN не загружен! Проверьте .env.")
            return

        print(f"Токен загружен: {BOT_TOKEN[:10]}... (первые символы для проверки)")

        application = ApplicationBuilder().token(BOT_TOKEN).build()
        print("Application создана.")

        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("cocktail", cocktail))
        print("Handlers добавлены.")

        print("Запуск polling...")
        application.run_polling()
        print("Polling завершён (это не должно выводиться, если polling работает).")

    except Exception as e:
        print(f"КРИТИЧЕСКАЯ ОШИБКА: {e}")
        raise


if __name__ == '__main__':
    main()