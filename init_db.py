#!/usr/bin/env python3
"""
Скрипт инициализации базы данных
"""
import sys
from loguru import logger

from config.database import Base, engine, init_db
from models import *  # Импортируем все модели


logger.remove()
logger.add(sys.stderr, level="INFO")


def main():
    """Инициализация БД"""
    logger.info("=" * 80)
    logger.info("ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ")
    logger.info("=" * 80)
    
    try:
        # Создаем все таблицы
        logger.info("Создание таблиц...")
        Base.metadata.create_all(bind=engine)
        
        logger.success("✅ База данных успешно инициализирована!")
        logger.info("\nСозданные таблицы:")
        for table in Base.metadata.sorted_tables:
            logger.info(f"  • {table.name}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
