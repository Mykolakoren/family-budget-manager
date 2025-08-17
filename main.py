#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Основной файл запуска бота семейного бюджета
"""

import logging
import sys
import os

# Добавляем текущую директорию в Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Проверяем импорты
try:
    from telegram.ext import Application

    print("✅ Telegram библиотека найдена")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Выполни: pip3 install python-telegram-bot==20.6")
    sys.exit(1)

try:
    from config import TELEGRAM_TOKEN, OPENAI_API_KEY

    print("✅ Конфигурация загружена")
except ImportError:
    print("❌ Файл config.py не найден")
    sys.exit(1)

if not TELEGRAM_TOKEN:
    print("❌ Ошибка: Не настроен TELEGRAM_TOKEN в config.py")
    sys.exit(1)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Импортируем наши модули с обработкой ошибок
try:
    from database.db_manager import DatabaseManager

    print("✅ DatabaseManager загружен")
except ImportError as e:
    print(f"❌ Ошибка импорта DatabaseManager: {e}")
    sys.exit(1)

try:
    from ai.ai_analyzer import AIAnalyzer

    print("✅ AIAnalyzer загружен")
except ImportError as e:
    print(f"❌ Ошибка импорта AIAnalyzer: {e}")
    sys.exit(1)

try:
    from users.user_manager import UserManager

    print("✅ UserManager загружен")
except ImportError as e:
    print(f"❌ Ошибка импорта UserManager: {e}")
    sys.exit(1)

try:
    from family.family_manager import FamilyManager

    print("✅ FamilyManager загружен")
except ImportError as e:
    print(f"❌ Ошибка импорта FamilyManager: {e}")
    sys.exit(1)

try:
    from handlers.bot_handlers import BotHandlers

    print("✅ BotHandlers загружен")
except ImportError as e:
    print(f"❌ Ошибка импорта BotHandlers: {e}")
    print("Проверьте файлы в папке handlers/")
    sys.exit(1)


def main():
    """Главная функция запуска бота"""
    print("🚀 Запуск умного бота семейного бюджета...")
    print(f"🤖 Token: {TELEGRAM_TOKEN[:10]}...")
    print(f"🧠 OpenAI API: {'✅ Подключен' if OPENAI_API_KEY else '❌ Не настроен'}")

    # Инициализируем компоненты
    try:
        print("📊 Инициализация компонентов...")

        db_manager = DatabaseManager()
        print("✅ База данных инициализирована")

        ai_analyzer = AIAnalyzer(OPENAI_API_KEY)
        print("✅ ИИ анализатор инициализирован")

        user_manager = UserManager(db_manager, ai_analyzer)
        print("✅ Менеджер пользователей инициализирован")

        family_manager = FamilyManager(db_manager, user_manager)
        print("✅ Менеджер семей инициализирован")

        # Создаем приложение
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        print("✅ Telegram приложение создано")

        # Инициализируем обработчики
        bot_handlers = BotHandlers(
            db_manager=db_manager,
            ai_analyzer=ai_analyzer,
            user_manager=user_manager,
            family_manager=family_manager
        )
        print("✅ Обработчики инициализированы")

        # Регистрируем обработчики
        bot_handlers.setup_handlers(application)

        print("✅ Все обработчики зарегистрированы")
        print("🔥 Бот готов к работе!")
        print("-" * 50)
        print_help_info()
        print("-" * 50)
        print("🚀 Бот запущен и ожидает сообщений...")

        # Запускаем бота
        application.run_polling(allowed_updates=['message', 'callback_query'])

    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        logger.exception("Критическая ошибка при запуске бота")
        import traceback
        traceback.print_exc()
    finally:
        print("💾 Сохранение данных перед завершением...")
        print("✅ Бот завершил работу")


def print_help_info():
    """Выводит справочную информацию"""
    print("📱 Доступные команды:")
    print("• /start - начать работу")
    print("• /family - настройка семейного бюджета 🏠")
    print("• /balance - баланс счетов")
    print("• /analyze - ИИ анализ трат")
    print("• /family_stats - семейная статистика 👥")
    print("• /stats - статистика обучения")
    print("• /export - экспорт данных")
    print()
    print("🤖 Особенности:")
    print("• Персональное обучение ИИ")
    print("• Семейный общий бюджет 👨‍👩‍👧‍👦")
    print("• Автоматическая категоризация")
    print("• Умные советы и анализ")


if __name__ == '__main__':
    main()