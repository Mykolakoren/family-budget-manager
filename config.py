# -*- coding: utf-8 -*-
"""
Файл конфигурации бота семейного бюджета
"""

# Токен от BotFather
TELEGRAM_TOKEN = "8008521714:AAEtYOi3CRJ-dtuNo23zn-0b7BQUeG0rx2Y"

# OpenAI API ключ
OPENAI_API_KEY = "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"

# Категории по умолчанию
DEFAULT_CATEGORIES = {
    'expense': [
        'Еда', 'Продукты', 'Рестораны', 'Кафе',
        'Транспорт', 'Такси', 'Бензин', 'Общественный транспорт',
        'Жилье', 'Аренда', 'Коммунальные', 'Интернет',
        'Здоровье', 'Медицина', 'Аптека', 'Врачи',
        'Развлечения', 'Кино', 'Спорт', 'Хобби',
        'Одежда', 'Обувь', 'Аксессуары',
        'Образование', 'Курсы', 'Книги',
        'Техника', 'Электроника', 'Софт',
        'Дети', 'Игрушки', 'Детская одежда',
        'Красота', 'Косметика', 'Парикмахерская',
        'Подарки', 'Благотворительность',
        'Прочее'
    ],
    'income': [
        'Зарплата', 'Фриланс', 'Бизнес',
        'Инвестиции', 'Дивиденды', 'Проценты',
        'Подарки', 'Возврат', 'Кешбэк',
        'Прочее'
    ]
}

# Счета по умолчанию
DEFAULT_ACCOUNTS = [
    'BOG Card', 'TBC Card', 'Liberty Card',
    'Наличные GEL', 'Наличные USD', 'Наличные EUR',
    'PayPal', 'Crypto Wallet', 'Сбережения'
]

# Настройки базы данных
DATABASE_CONFIG = {
    'data_file': 'budget_data.json',
    'backup_enabled': True,
    'auto_backup_interval': 3600  # секунды
}

# Настройки ИИ
AI_CONFIG = {
    'model': 'gpt-3.5-turbo',
    'max_tokens': 300,
    'temperature': 0.1,
    'confidence_threshold': 0.7
}

# Валюты
SUPPORTED_CURRENCIES = ['GEL', 'USD', 'EUR']

# Лимиты
LIMITS = {
    'max_transactions_per_day': 100,
    'max_family_members': 10,
    'max_description_length': 500
}