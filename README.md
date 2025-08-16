# Family Budget Manager

🏠 **Мультиплатформенное решение для ведения семейного бюджета**  
Multi-platform family budget management solution

## 📋 Описание / Description

Комплексное решение для управления семейным бюджетом с поддержкой Telegram бота, веб-интерфейса и REST API. Включает возможности многовалютного учета, аналитики трат, интеграцию с LLM для обработки естественного языка.

Comprehensive family budget management solution with Telegram bot, web interface, and REST API support. Features multi-currency tracking, expense analytics, and LLM integration for natural language processing.

## 🚀 Функции / Features

### 💰 Управление финансами / Financial Management
- Учет доходов и расходов / Income and expense tracking
- Поддержка многовалютности (GEL, USD, EUR, UAH, USDT) / Multi-currency support
- Множественные счета (банковские карты, наличные, криптовалюты) / Multiple account types
- Переводы между счетами / Account transfers
- Категоризация транзакций / Transaction categorization

### 🤖 Telegram Bot
- Ввод транзакций естественным языком / Natural language transaction input
- Команды для управления бюджетом / Budget management commands
- Аналитика и отчеты / Analytics and reports
- Поддержка нескольких языков / Multi-language support

### 📊 Аналитика / Analytics
- Графики расходов по категориям / Expense charts by category
- Анализ доходов и расходов / Income vs expenses analysis
- Отчеты за период / Period reports
- Прогнозирование / Forecasting

### 🌐 Веб-интерфейс / Web Interface
- Интуитивная панель управления / Intuitive dashboard
- Управление счетами и категориями / Account and category management
- Визуализация данных / Data visualization
- Экспорт отчетов / Report export

## 🏗️ Архитектура / Architecture

```
family-budget-manager/
├── backend/          # FastAPI REST API
├── bot/             # Telegram Bot
├── frontend/        # React Web App
├── shared/          # Shared code
├── docker/          # Docker configurations
└── docs/           # Documentation
```

## 🛠️ Технологии / Technologies

- **Backend:** FastAPI, SQLAlchemy, PostgreSQL/SQLite
- **Frontend:** React, Material-UI, Chart.js
- **Bot:** Python Telegram Bot
- **LLM:** OpenAI API
- **Infrastructure:** Docker, Docker Compose

## 🚦 Быстрый старт / Quick Start

### Предварительные требования / Prerequisites
- Docker и Docker Compose
- Python 3.11+ (для локальной разработки)
- Node.js 18+ (для фронтенда)

### Установка / Installation

1. **Клонируйте репозиторий / Clone repository:**
```bash
git clone https://github.com/Mykolakoren/family-budget-manager.git
cd family-budget-manager
```

2. **Настройте переменные окружения / Set up environment:**
```bash
cp .env.example .env
# Отредактируйте .env файл с вашими настройками
# Edit .env file with your settings
```

3. **Запустите с Docker Compose:**
```bash
docker-compose up -d
```

4. **Откройте приложение / Open application:**
- Веб-интерфейс / Web UI: http://localhost:3000
- API документация / API docs: http://localhost:8000/docs

### Локальная разработка / Local Development

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

#### Telegram Bot
```bash
cd bot
pip install -r requirements.txt
python main.py
```

## 🔧 Конфигурация / Configuration

### Основные настройки / Basic Settings

Отредактируйте `.env` файл / Edit `.env` file:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/family_budget

# Security
SECRET_KEY=your-secret-key-here

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-bot-token

# OpenAI
OPENAI_API_KEY=your-openai-key
```

### Создание Telegram бота / Creating Telegram Bot

1. Напишите @BotFather в Telegram / Message @BotFather on Telegram
2. Используйте команду `/newbot` / Use `/newbot` command
3. Следуйте инструкциям / Follow instructions
4. Скопируйте токен в `.env` / Copy token to `.env`

## 📖 Использование / Usage

### Telegram Bot Команды / Commands

```
/start - Начать работу / Start using bot
/add 50 food bog - Добавить транзакцию / Add transaction
/balance - Показать баланс / Show balance
/report - Отчет за месяц / Monthly report
/help - Справка / Help
```

### Примеры естественного языка / Natural Language Examples

```
Потратил 50 лари на еду с карты BOG
Зарплата 3000 USD наличные
Bought coffee for 5 GEL
Freelance payment 500 EUR PayPal
```

## 🔌 API

REST API доступно на / REST API available at: `http://localhost:8000/api/v1`

### Основные эндпоинты / Main Endpoints

- `POST /auth/login` - Аутентификация / Authentication
- `GET /accounts/` - Список счетов / List accounts
- `POST /transactions/` - Создать транзакцию / Create transaction
- `GET /analytics/dashboard` - Данные дашборда / Dashboard data

Полная документация / Full documentation: http://localhost:8000/docs

## 🗃️ База данных / Database

### Миграции / Migrations

```bash
# Создать миграцию / Create migration
cd backend
alembic revision --autogenerate -m "Description"

# Применить миграции / Apply migrations
alembic upgrade head
```

### Схема базы данных / Database Schema

- **users** - Пользователи / Users
- **accounts** - Счета / Accounts  
- **categories** - Категории / Categories
- **transactions** - Транзакции / Transactions
- **budgets** - Бюджеты / Budgets

## 🧪 Тестирование / Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📈 Развертывание / Deployment

### Production с Docker / Production with Docker

```bash
# Продакшн сборка / Production build
docker-compose -f docker-compose.prod.yml up -d
```

### Переменные окружения для продакшн / Production Environment Variables

```env
DEBUG=False
DATABASE_URL=postgresql://user:password@db:5432/family_budget
SECRET_KEY=strong-secret-key
CORS_ORIGINS=["https://yourdomain.com"]
```

## 🤝 Участие в разработке / Contributing

1. Форкните репозиторий / Fork the repository
2. Создайте ветку для фичи / Create feature branch
3. Внесите изменения / Make changes
4. Добавьте тесты / Add tests
5. Создайте Pull Request / Create Pull Request

## 📄 Лицензия / License

MIT License

## 📞 Поддержка / Support

- GitHub Issues: [Issues](https://github.com/Mykolakoren/family-budget-manager/issues)
- Email: support@example.com

## 🔄 Статус разработки / Development Status

- ✅ Базовая архитектура / Basic architecture
- ✅ Backend API / Backend API
- ✅ Telegram Bot структура / Bot structure
- ✅ React Frontend основа / Frontend foundation
- 🔄 LLM интеграция / LLM integration
- 🔄 Аналитика / Analytics
- 📋 Тестирование / Testing
- 📋 Документация / Documentation
