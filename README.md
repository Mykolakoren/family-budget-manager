# Family Budget Manager

Мультиплатформенное решение для ведения семейного бюджета с поддержкой веб-интерфейса и Telegram бота.

## 🚀 Возможности

- **Мультиплатформенность**: Веб-интерфейс + Telegram бот
- **Множественные бюджеты**: Семейный, Unbox, Neoschool, личный
- **Многовалютность**: GEL, USD, EUR, UAH, USDT
- **Умный ввод данных**: Обработка естественного языка через LLM (OpenAI)
- **Аутентификация**: Email/пароль и Telegram ID
- **Аналитика и отчеты**: Визуализация трат и доходов
- **Экспорт данных**: CSV, Excel, PDF

## 🏗️ Архитектура

```
family-budget-manager/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── core/        # Configuration and database
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic
│   │   └── utils/       # Utility functions
│   ├── tests/           # Backend tests
│   ├── requirements.txt # Python dependencies
│   └── main.py         # Application entry point
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   └── ...
│   ├── public/
│   ├── package.json
│   └── vite.config.js
├── telegram-bot/        # Telegram bot
│   ├── handlers/        # Bot command handlers
│   ├── utils/          # Bot utilities
│   ├── requirements.txt
│   └── bot.py
├── docs/               # Documentation
├── docker-compose.yml  # Docker configuration
├── .env.example       # Environment variables template
└── README.md
```

## 🚀 Быстрый старт

### Требования

- Python 3.9+
- Node.js 18+
- PostgreSQL (опционально, SQLite для разработки)
- Docker & Docker Compose (опционально)

### Установка

1. **Клонирование репозитория**
```bash
git clone https://github.com/Mykolakoren/family-budget-manager.git
cd family-budget-manager
```

2. **Настройка окружения**
```bash
cp .env.example .env
# Отредактируйте .env файл с вашими настройками
```

3. **Запуск с Docker (рекомендуется)**
```bash
docker-compose up -d
```

4. **Или запуск вручную**

Backend:
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

Telegram Bot:
```bash
cd telegram-bot
pip install -r requirements.txt
python bot.py
```

## 🔧 Конфигурация

### Переменные окружения

Скопируйте `.env.example` в `.env` и настройте:

- `DATABASE_URL` - URL базы данных
- `SECRET_KEY` - Секретный ключ для JWT
- `OPENAI_API_KEY` - API ключ OpenAI для LLM функций
- `TELEGRAM_BOT_TOKEN` - Токен Telegram бота от @BotFather

### База данных

По умолчанию используется SQLite для разработки. Для продакшена рекомендуется PostgreSQL.

## 📱 Использование

### Веб-интерфейс

Откройте http://localhost:3000 в браузере.

Доступные функции:
- Dashboard с общей статистикой
- Управление бюджетами
- Добавление транзакций (обычный и умный ввод)
- Аналитика и отчеты

### Telegram бот

1. Найдите вашего бота в Telegram
2. Запустите командой `/start`
3. Используйте команды:
   - `/budgets` - управление бюджетами
   - `/add` - добавить транзакцию
   - `/balance` - проверить баланс
   - `/analytics` - аналитика
   - `/help` - помощь

**Умный ввод**: Просто напишите боту естественным языком:
- "Купил продукты за 50 лари в Carrefour"
- "Зарплата 2000 долларов"
- "Кофе 8.50 лари в Starbucks"

## 🔌 API

Backend предоставляет REST API:

- `GET /` - информация о API
- `GET /health` - проверка здоровья
- `POST /api/v1/auth/register` - регистрация
- `POST /api/v1/auth/token` - аутентификация
- `GET /api/v1/budgets` - список бюджетов
- `POST /api/v1/transactions` - создание транзакции
- `GET /api/v1/analytics/summary` - аналитика

Полную документацию API можно найти по адресу http://localhost:8000/docs

## 🧪 Тестирование

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📊 Поддерживаемые валюты

- GEL (Грузинский лари)
- USD (Доллар США)
- EUR (Евро)
- UAH (Украинская гривна)
- USDT (Tether)

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit изменения (`git commit -m 'Add some AmazingFeature'`)
4. Push в branch (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

## 📝 Лицензия

Distributed under the MIT License. See `LICENSE` for more information.

## 📞 Контакты

Mykola Koren - [@mykolakoren](https://github.com/Mykolakoren)

Project Link: [https://github.com/Mykolakoren/family-budget-manager](https://github.com/Mykolakoren/family-budget-manager)
