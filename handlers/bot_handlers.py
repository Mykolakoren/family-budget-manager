# -*- coding: utf-8 -*-
"""
Обработчики команд и сообщений для бота семейного бюджета
"""

import io
from datetime import datetime
from typing import Dict, Any
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)

from parsers.transaction_parser import TransactionParser
from handlers.family_handlers import FamilyHandlers
from handlers.analytics_handlers import AnalyticsHandlers

logger = logging.getLogger(__name__)


class BotHandlers:
    """Основные обработчики бота"""

    def __init__(self, db_manager, ai_analyzer, user_manager, family_manager):
        self.db = db_manager
        self.ai = ai_analyzer
        self.user_manager = user_manager
        self.family_manager = family_manager

        # Инициализируем вспомогательные обработчики
        self.transaction_parser = TransactionParser(ai_analyzer, user_manager)
        self.family_handlers = FamilyHandlers(family_manager, user_manager)
        self.analytics_handlers = AnalyticsHandlers(family_manager, user_manager, ai_analyzer)

    def setup_handlers(self, application: Application) -> None:
        """Регистрация всех обработчиков"""
        # Основные команды
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("balance", self.balance_command))
        application.add_handler(CommandHandler("analyze", self.analytics_handlers.analyze_command))
        application.add_handler(CommandHandler("stats", self.stats_command))
        application.add_handler(CommandHandler("export", self.export_command))

        # Семейные команды
        application.add_handler(CommandHandler("family", self.family_handlers.family_command))
        application.add_handler(CommandHandler("family_invite", self.family_handlers.family_invite_command))
        application.add_handler(CommandHandler("family_stats", self.family_handlers.family_stats_command))
        application.add_handler(CommandHandler("family_leave", self.family_handlers.family_leave_command))

        # Обработчики сообщений
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))
        application.add_handler(CallbackQueryHandler(self.handle_callback_query))

        # Обработчик ошибок
        application.add_error_handler(self.error_handler)

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        user = update.effective_user
        user_id = user.id

        # Сохраняем/обновляем данные пользователя
        self.user_manager.set_user_name(user_id, user.first_name)

        # Получаем статистику
        user_stats = self.user_manager.get_user_statistics(user_id)
        transactions = self.family_manager.get_family_transactions(user_id)
        total_transactions = len(transactions)

        # Информация о семье
        family_data = self.family_manager.get_family_data(user_id)
        family_info = f"\n🏠 **Семья:** {family_data['name']}" if family_data else "\n💡 **Совет:** Создайте семейную группу через /family"

        welcome_text = f"""
👋 Привет, {user.first_name}!

Я умный помощник для семейного бюджета с персональным обучением!{family_info}

🔥 **Твоя статистика:**
📊 Транзакций: {total_transactions}
🧠 ИИ обучение: {user_stats['learning_score']} примеров

🤖 **ИИ возможности:**
• Умная категоризация с обучением
• Персональные советы и анализ
• Запоминание твоих предпочтений
• Обработка банковских выписок

**Команды:**
/family - 🏠 семейный бюджет
/analyze - 🧠 ИИ анализ трат
/stats - 📊 статистика обучения
/export - 📤 экспорт данных
/balance - 💰 баланс счетов

**Попробуй:**
• "Потратил 50 лари на еду в Carrefour"
• Пришли файл выписки 📎
        """

        await update.message.reply_text(welcome_text, parse_mode='Markdown')

    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        text = update.message.text
        user_id = update.effective_user.id
        user_data = self.user_manager.get_user_data(user_id)

        # Проверяем, ожидаем ли мы ID семейной группы
        if user_data.get('waiting_for_family_id'):
            result = self.family_handlers.handle_family_id_input(user_id, text)
            user_data['waiting_for_family_id'] = False
            self.user_manager.update_user_data(user_id, user_data)

            await update.message.reply_text(result['message'], parse_mode='Markdown')
            return

        # Определяем тип сообщения и обрабатываем
        text_lower = text.lower()

        if any(word in text_lower for word in ['потратил', 'купил', 'заплатил', 'потрачено']):
            await self._handle_expense(update, context)
        elif any(word in text_lower for word in ['получил', 'зарплата', 'доход', 'заработал']):
            await self._handle_income(update, context)
        elif any(word in text_lower for word in ['сколько', 'баланс', 'отчет', 'покажи', 'топ']):
            await self._handle_question(update, context)
        else:
            await self._show_help_message(update)

    async def _handle_expense(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка расходной транзакции"""
        text = update.message.text
        user_id = update.effective_user.id

        # Парсим транзакцию
        parsed = await self.transaction_parser.parse_transaction_text(user_id, text)

        if not parsed:
            await update.message.reply_text("🤔 Не смог распознать транзакцию")
            return

        # Убеждаемся, что это расход
        if parsed['amount'] > 0:
            parsed['amount'] = -parsed['amount']
            parsed['type'] = 'expense'

        # Создаем транзакцию
        transaction = self.transaction_parser.create_transaction_dict(parsed)

        # Добавляем в базу
        user_name = self.user_manager.get_user_name(user_id)
        if self.family_manager.add_family_transaction(user_id, transaction, user_name):
            await self._send_transaction_confirmation(update, parsed, 'расход')
        else:
            await update.message.reply_text("❌ Ошибка сохранения в базу данных")

    async def _handle_income(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка доходной транзакции"""
        text = update.message.text
        user_id = update.effective_user.id

        # Парсим транзакцию
        parsed = await self.transaction_parser.parse_transaction_text(user_id, text)

        if not parsed:
            await update.message.reply_text("🤔 Не смог распознать доход")
            return

        # Убеждаемся, что это доход
        if parsed['amount'] < 0:
            parsed['amount'] = abs(parsed['amount'])
        parsed['type'] = 'income'

        # Создаем транзакцию
        transaction = self.transaction_parser.create_transaction_dict(parsed)

        # Добавляем в базу
        user_name = self.user_manager.get_user_name(user_id)
        if self.family_manager.add_family_transaction(user_id, transaction, user_name):
            await self._send_transaction_confirmation(update, parsed, 'доход')
        else:
            await update.message.reply_text("❌ Ошибка сохранения в базу данных")

    async def _send_transaction_confirmation(self, update: Update, parsed: Dict[str, Any], transaction_type: str):
        """Отправка подтверждения транзакции"""
        user_id = update.effective_user.id
        source_text = {
            'personal_ai': 'Персональный ИИ',
            'openai': 'ИИ',
            'simple': 'Базовый парсер'
        }.get(parsed.get('source'), 'Система')

        reasoning = f" ({parsed.get('reasoning', '')})" if 'reasoning' in parsed else ""

        family_data = self.family_manager.get_family_data(user_id)
        family_info = f" в группу **{family_data['name']}**" if family_data else ""

        sign = '+' if parsed['amount'] > 0 else ''

        response = f"""
✅ **{source_text} добавил {transaction_type}:**{reasoning}

💰 {sign}{parsed['amount']:.2f} {parsed['currency']}
🏷️ {parsed['category']}
💳 {parsed['account']}

🧠 Уверенность: {parsed.get('confidence', 0.5) * 100:.0f}%
💾 Сохранено{family_info}
        """

        await update.message.reply_text(response, parse_mode='Markdown')

    async def _handle_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка вопросов пользователя"""
        text = update.message.text.lower()
        user_id = update.effective_user.id

        if any(word in text for word in ['баланс', 'счет']):
            await self.balance_command(update, context)
        elif any(word in text for word in ['анализ', 'совет']):
            await self.analytics_handlers.analyze_command(update, context)
        else:
            await update.message.reply_text(
                "🤔 Попробуй спросить:\n"
                "• Покажи баланс\n"
                "• Сколько я потратил?\n"
                "• /analyze для полного ИИ анализа"
            )

    async def _show_help_message(self, update: Update):
        """Показать справочное сообщение"""
        await update.message.reply_text(
            "🤔 Попробуй:\n"
            "• \"Потратил 50 лари в Carrefour\" - ИИ запомнит!\n"
            "• \"Получил зарплату 1000 долларов\"\n"
            "• Пришли файл выписки 📎\n"
            "• /family для настройки семейного бюджета 🏠\n"
            "• /analyze для ИИ анализа 🤖"
        )

    async def balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /balance"""
        user_id = update.effective_user.id

        balances = self.family_manager.get_family_balance_by_accounts(user_id)

        if not balances:
            family_data = self.family_manager.get_family_data(user_id)
            if family_data:
                await update.message.reply_text("📊 Пока нет семейных транзакций. Добавьте первую!")
            else:
                await update.message.reply_text(
                    "📊 Пока нет транзакций.\n\n"
                    "💡 **Совет:** Используйте /family для создания семейной группы!"
                )
            return

        # Формируем ответ
        family_data = self.family_manager.get_family_data(user_id)
        if family_data:
            balance_text = f"🏠 **{family_data['name']}**\n\n💰 **Баланс счетов:**\n\n"
        else:
            balance_text = "💰 **Баланс счетов:**\n\n"

        for account, balance in balances.items():
            emoji = "💳" if "Card" in account else "💵"
            balance_text += f"{emoji} {account}: {balance:,.2f}\n"

        # Добавляем общую статистику
        stats = self.family_manager.get_family_statistics(user_id)
        balance_text += f"\n📈 Доходы: {stats['total_income']:,.2f}\n"
        balance_text += f"📉 Расходы: {stats['total_expenses']:,.2f}\n"
        balance_text += f"💎 Баланс: {stats['total_balance']:,.2f}\n\n"

        if family_data:
            balance_text += f"👥 Участников в семье: {len(family_data['members'])}\n"
            balance_text += f"📊 Команда /family_stats для детальной статистики"
        else:
            balance_text += f"💡 Команда /family для создания семейной группы"

        await update.message.reply_text(balance_text, parse_mode='Markdown')

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /stats - статистика обучения"""
        user_id = update.effective_user.id
        user_stats = self.user_manager.get_user_statistics(user_id)
        user_data = self.user_manager.get_user_data(user_id)
        ai_learning = user_data['ai_learning']

        stats_text = "📊 **Детальная статистика:**\n\n"
        stats_text += f"📁 Всего транзакций: {user_stats['total_transactions']}\n"
        stats_text += f"💸 Расходов: {user_stats['total_expenses']}\n"
        stats_text += f"💰 Доходов: {user_stats['total_incomes']}\n\n"

        stats_text += "🧠 **ИИ обучение:**\n"
        stats_text += f"📚 Изученных слов: {user_stats['known_words']}\n"
        stats_text += f"🏪 Запомненных мест: {user_stats['known_merchants']}\n"
        stats_text += f"🎯 Общий опыт: {user_stats['learning_score']} примеров\n"

        if ai_learning['merchant_categories']:
            stats_text += f"\n🏪 **Запомненные места:**\n"
            for merchant, category in list(ai_learning['merchant_categories'].items())[:5]:
                stats_text += f"• {merchant.title()} → {category}\n"

        stats_text += f"\n📅 Используешь бота: {user_stats['days_using']} дней\n"
        stats_text += f"📄 Данные сохраняются автоматически"

        await update.message.reply_text(stats_text, parse_mode='Markdown')

    async def export_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /export"""
        user_id = update.effective_user.id
        transactions = self.family_manager.get_family_transactions(user_id)

        if not transactions:
            await update.message.reply_text("📊 Нет данных для экспорта")
            return

        # Подготавливаем данные для экспорта
        export_data = {'transactions': transactions}
        csv_content = self.db.export_user_data(export_data, format='csv')

        filename = f"budget_export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"

        family_data = self.family_manager.get_family_data(user_id)
        family_info = f"🏠 Семейная группа: {family_data['name']}\n" if family_data else ""

        user_stats = self.user_manager.get_user_statistics(user_id)

        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=io.BytesIO(csv_content),
            filename=filename,
            caption=f"📊 **Экспорт данных:**\n"
                    f"{family_info}"
                    f"📁 {len(transactions)} транзакций\n"
                    f"🧠 ИИ обучение: {user_stats['learning_score']} примеров",
            parse_mode='Markdown'
        )

    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка callback запросов"""
        query = update.callback_query
        await query.answer()

        # Передаем обработку семейным функциям
        if await self.family_handlers.handle_callback_query(update, context):
            return

        # Если не обработано, отправляем стандартный ответ
        await query.edit_message_text("❌ Неизвестная команда")

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик ошибок"""
        logger.error("Ошибка в боте:", exc_info=context.error)

        if update and hasattr(update, 'effective_message') and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "🤖 Произошла техническая ошибка. Попробуйте еще раз или обратитесь к разработчику."
                )
            except Exception:
                pass