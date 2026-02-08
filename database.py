import os
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, DateTime, func
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv


DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


LOCAL_HOST = "1f77efc1400c.vps.myjino.ru"
LOCAL_PORT = "49288"


DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{LOCAL_HOST}:{LOCAL_PORT}/{DB_NAME}"
)

engine = None
metadata = MetaData()

UsersTable = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True),
    Column('telegram_user_id', Integer, unique=True, nullable=False),
    Column('username', String(100), nullable=True),
    Column('registered_at', DateTime, server_default=func.now()),
)


def initialize_db():
    global engine

    if not DATABASE_URL:
        print("ОШИБКА: Параметры БД не найдены в окружении.")
        return False

    print(f"Попытка подключения к БД через SSH-туннель на {LOCAL_HOST}:{LOCAL_PORT}...")

    try:
        engine = create_engine(DATABASE_URL)

        with engine.connect() as connection:
            # Проверка соединения
            connection.execute(text("SELECT 1"))
            print("УСПЕХ: Соединение с удаленной БД через туннель установлено.")
            create_tables()
            return True

    except SQLAlchemyError as e:
        print(f"КРИТИЧЕСКАЯ ОШИБКА при подключении к БД: {e}")
        engine = None
        return False


def create_tables():
    if engine:
        try:
            metadata.create_all(engine)
            print("Все необходимые таблицы проверены/созданы.")
        except Exception as e:
            print(f"Ошибка при создании таблиц: {e}")


def save_user_if_new(user_id, username):
    # ... (логика сохранения остается прежней)
    if engine:
        try:
            with engine.begin() as connection:
                result = connection.execute(
                    text("SELECT id FROM users WHERE telegram_user_id = :uid"),
                    {"uid": user_id}
                ).scalar()

                if result is None:
                    insert_stmt = UsersTable.insert().values(
                        telegram_user_id=user_id,
                        username=username
                    )
                    connection.execute(insert_stmt)
                    print(f"Новый пользователь {username} ({user_id}) добавлен в БД.")
                else:
                    update_stmt = UsersTable.update().where(UsersTable.c.telegram_user_id == user_id).values(
                        username=username
                    )
                    connection.execute(update_stmt)
                    print(f"Пользователь {username} обновлен в БД.")

        except SQLAlchemyError as e:
            print(f"Ошибка при записи в БД: {e}")