"""
Конфигурация базы данных
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from contextlib import contextmanager
from typing import Generator
from config.settings import settings

# Создаем engine для PostgreSQL
engine = create_engine(
    settings.database_url,
    poolclass=NullPool,  # Для асинхронной работы
    echo=settings.log_level == "DEBUG",
    pool_pre_ping=True,  # Проверка соединения перед использованием
)

# Создаем фабрику сессий
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Базовый класс для моделей
Base = declarative_base()


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Контекстный менеджер для работы с БД
    
    Использование:
        with get_db() as db:
            users = db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """Создает все таблицы в БД"""
    Base.metadata.create_all(bind=engine)


def drop_db():
    """Удаляет все таблицы (осторожно!)"""
    Base.metadata.drop_all(bind=engine)
