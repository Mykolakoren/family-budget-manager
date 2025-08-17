# -*- coding: utf-8 -*-
"""
Обработчики аналитики и ИИ анализа для бота семейного бюджета
"""

from telegram import Update
from telegram.ext import ContextTypes
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class AnalyticsHandlers:
    """Обработчики для аналитики и ИИ анализа"""

    def __init__(self, family_manager, user_manager, ai_analyzer):
        self.family = family_manager
        self.user_manager = user_manager
        self.ai = ai_analyzer

    async def analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /analyze - ИИ анализ трат"""
        user_id = update.effective_user.id

        transactions = self.family.get_family_transactions(user_id)

        if len(transactions) < 5:
            family_data = self.family.get_family_data(user_id)
            family_hint = "\n• Создайте семейную группу через /family" if not family_data else ""

            await update.message.reply_text(
                "🤖 **Для ИИ анализа нужно минимум 5 транзакций.**\n\n"
                "Добавьте еще несколько:\n"
                "• \"Потратил 50 лари на еду\"\n"
                "• Пришлите файл выписки\n"
                "• /balance для просмотра текущих данных" + family_hint
            )
            return

        await update.message.reply_text("🤖 **ИИ анализирует данные...**\nДай мне секундочку! 🧠")

        # Проводим анализ
        analysis = await self.ai.analyze_spending_patterns(transactions)

        # Получаем дополнительную информацию
        user_data = self.user_manager.get_user_data(user_id)
        learning_stats = user_data['ai_learning']

        family_data = self.family.get_family_data(user_id)
        family_prefix = f"🏠 **{family_data['name']}** - " if family_data else ""

        # Эмодзи для настроения
        mood_emoji = {
            'positive': '😊',
            'neutral': '😐',
            'concern': '😟'
        }

        emoji = mood_emoji.get(analysis['mood'], '🤖')

        response = f"{emoji} **{family_prefix}Персональный ИИ анализ:**\n\n"
        response += f"📊 {analysis['analysis']}\n\n"
        response += f"🔥 **Топ категория:** {analysis['top_category']}\n\n"
        response += "💡 **ИИ рекомендации:**\n"

        for i, advice in enumerate(analysis['advice'], 1):
            response += f"{i}. {advice}\n"

        response += f"\n🧠 **Обучение ИИ:**\n"
        response += f"• Изучено {len(learning_stats['category_preferences'])} слов\n"
        response += f"• Запомнено {len(learning_stats['merchant_categories'])} мест\n"
        response += f"• Общий опыт: {learning_stats['learning_score']} примеров\n\n"

        if family_data:
            response += f"👥 **Семейная группа:** {len(family_data['members'])} участников\n"
            response += f"📊 /family_stats для детальной семейной статистики\n\n"

        response += f"🎯 **Точность ИИ растет с каждой транзакцией!**"

        await update.message.reply_text(response, parse_mode='Markdown')

    async def show_spending_summary(self, update: Update, transactions: list):
        """Показать краткую сводку трат"""
        expenses = [t for t in transactions if t['amount'] < 0]

        if not expenses:
            await update.message.reply_text("💰 Пока нет расходов!")
            return

        # Считаем статистику
        from datetime import datetime, timedelta
        today = datetime.now()
        month_ago = today - timedelta(days=30)

        recent_expenses = []
        for trans in expenses:
            try:
                trans_date = datetime.strptime(trans['date'][:10], '%Y-%m-%d')
                if trans_date >= month_ago:
                    recent_expenses.append(trans)
            except (ValueError, KeyError):
                continue

        total_month = sum(abs(t['amount']) for t in recent_expenses)
        total_all = sum(abs(t['amount']) for t in expenses)

        summary = f"💸 **Твои траты:**\n\n"
        summary += f"📅 За месяц: {total_month:,.2f} лари\n"
        summary += f"📊 Всего: {total_all:,.2f} лари\n"
        summary += f"📝 Транзакций: {len(expenses)}\n\n"

        if recent_expenses:
            avg_daily = total_month / 30
            summary += f"📈 В среднем в день: {avg_daily:.2f} лари\n\n"

        summary += "🤖 Команда /analyze для детального ИИ анализа!"

        await update.message.reply_text(summary, parse_mode='Markdown')

    async def show_top_categories(self, update: Update, transactions: list):
        """Показать топ категорий трат"""
        expenses = [t for t in transactions if t['amount'] < 0]

        if not expenses:
            await update.message.reply_text("💰 Пока нет расходов!")
            return

        # Группируем по категориям (последние 30 транзакций)
        by_category = defaultdict(float)
        for trans in expenses[-30:]:
            by_category[trans['category']] += abs(trans['amount'])

        sorted_categories = sorted(by_category.items(), key=lambda x: x[1], reverse=True)

        response = "🔥 **Топ категории трат:**\n\n"

        # Эмодзи для категорий
        emojis = {
            'Еда': '🍽️',
            'Транспорт': '🚗',
            'Развлечения': '🎬',
            'Здоровье': '💊',
            'Одежда': '👕',
            'Техника': '📱',
            'Прочее': '📦'
        }

        for i, (category, amount) in enumerate(sorted_categories[:5], 1):
            emoji = emojis.get(category, '📦')
            percentage = (amount / sum(by_category.values())) * 100
            response += f"{i}. {emoji} {category}: {amount:.2f} лари ({percentage:.1f}%)\n"

        response += f"\n🤖 /analyze для персональных советов!"

        await update.message.reply_text(response, parse_mode='Markdown')

    def get_insights_from_transactions(self, transactions: list) -> dict:
        """Получить инсайты из транзакций"""
        if not transactions:
            return {}

        expenses = [t for t in transactions if t['amount'] < 0]
        incomes = [t for t in transactions if t['amount'] > 0]

        # Базовая статистика
        total_expenses = sum(abs(t['amount']) for t in expenses)
        total_incomes = sum(t['amount'] for t in incomes)

        # Анализ по категориям
        by_category = defaultdict(float)
        for trans in expenses:
            by_category[trans['category']] += abs(trans['amount'])

        top_category = max(by_category.items(), key=lambda x: x[1])[0] if by_category else None

        # Анализ по времени
        from datetime import datetime, timedelta
        today = datetime.now()
        week_ago = today - timedelta(days=7)

        week_expenses = []
        for trans in expenses:
            try:
                trans_date = datetime.strptime(trans['date'][:10], '%Y-%m-%d')
                if trans_date >= week_ago:
                    week_expenses.append(trans)
            except (ValueError, KeyError):
                continue

        week_total = sum(abs(t['amount']) for t in week_expenses)
        daily_average = week_total / 7 if week_expenses else 0

        return {
            'total_expenses': total_expenses,
            'total_incomes': total_incomes,
            'balance': total_incomes - total_expenses,
            'top_category': top_category,
            'categories_count': len(by_category),
            'weekly_spending': week_total,
            'daily_average': daily_average,
            'transactions_count': len(transactions)
        }