# Family Budget Manager Documentation

## Project Overview

This is a multi-platform family budget management solution with web interface and Telegram bot support.

## Features

- Multi-platform support (Web + Telegram Bot)
- Multiple budget management (Family, Unbox, Neoschool, Personal)
- Multi-currency support (GEL, USD, EUR, UAH, USDT)
- Smart transaction input using LLM (OpenAI)
- Authentication via email/password and Telegram ID
- Analytics and reporting
- Data export capabilities

## Technology Stack

- **Backend**: FastAPI with SQLAlchemy ORM
- **Frontend**: React with Material-UI and Vite
- **Database**: PostgreSQL (SQLite for development)
- **Bot**: python-telegram-bot
- **LLM**: OpenAI API
- **Containerization**: Docker & Docker Compose

## Development Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and configure
3. Run with Docker: `docker-compose up -d`
4. Access web app at http://localhost:3000
5. Backend API docs at http://localhost:8000/docs

## API Documentation

The backend provides a RESTful API with automatic documentation via FastAPI.
Access the interactive docs at `/docs` endpoint.

## Bot Commands

- `/start` - Start the bot and show welcome message
- `/budgets` - Manage budgets
- `/add` - Add transaction manually
- `/balance` - Check current balance
- `/analytics` - View spending analytics
- `/export` - Export data
- `/help` - Show help message

## Smart Input Examples

The bot and web app support natural language input:
- "Bought groceries for 50 GEL at Carrefour"
- "Salary 2000 USD"
- "Coffee 8.50 GEL at Starbucks"
- "Transfer 100 USD to savings"

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request