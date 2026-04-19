import os
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, DateTime, func
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from sshtunnel import SSHTunnelForwarder

# Загружаем переменные окружения
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# SSH параметры
SSH_HOST = "1f77efc1400c.vps.myjino.ru"
SSH_PORT = 49288
SSH_USERNAME = os.getenv("SSH_USERNAME")
SSH_PASSWORD = os.getenv("SSH_PASSWORD")
LOCAL_PORT = 5432

# Параметры БД на удаленном сервере
REMOTE_DB_HOST = "localhost"
REMOTE_DB_PORT = 5432

tunnel = None
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
    global engine, tunnel

    if not all([DB_USER, DB_PASSWORD, DB_NAME, SSH_USERNAME, SSH_PASSWORD]):
        print("ОШИБКА: Не все параметры подключения найдены в окружении.")
        return False

    print(f"Создание SSH-туннеля к {SSH_HOST}...")

    try:
        # Простая конфигурация туннеля
        tunnel = SSHTunnelForwarder(
            ssh_address_or_host=(SSH_HOST, SSH_PORT),
            ssh_username=SSH_USERNAME,
            ssh_password=SSH_PASSWORD,
            remote_bind_address=(REMOTE_DB_HOST, REMOTE_DB_PORT),
            local_bind_address=('localhost', int(LOCAL_PORT))
        )

        # Запускаем туннель
        tunnel.start()
        print(f"SSH-туннель запущен. Локальный порт: {tunnel.local_bind_port}")

        # Используем строку подключения
        DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@localhost:{LOCAL_PORT}/{DB_NAME}"

        # Создаем движок SQLAlchemy
        engine = create_engine(DATABASE_URL)

        with engine.connect() as connection:
            # Проверка соединения
            connection.execute(text("SELECT 1"))
            print("УСПЕХ: Соединение с удаленной БД через SSH-туннель установлено.")
            create_tables()
            return True

    except Exception as e:
        print(f"КРИТИЧЕСКАЯ ОШИБКА при подключении к БД: {e}")
        if tunnel:
            try:
                tunnel.close()
            except:
                pass
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


def close_connection():
    """Функция для закрытия соединения"""
    global engine, tunnel

    if engine:
        engine.dispose()
        print("Соединение с БД закрыто.")

    if tunnel:
        try:
            tunnel.close()
            print("SSH-туннель остановлен.")
        except:
            pass