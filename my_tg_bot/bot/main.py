import logging
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import BOT_TOKEN
from handlers import start, cocktail

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)  # Уровень DEBUG для больше логов

def main():

    try:
        print("Запуск main... Тестируем вывод.")
        if not BOT_TOKEN:
            print("Ошибка: BOT_TOKEN не загружен! Проверьте .env.")
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