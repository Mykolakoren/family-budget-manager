# -*- coding: utf-8 -*-
"""
Обработчики семейных функций для бота семейного бюджета
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)


class FamilyHandlers:
    """Обработчики семейных команд"""

    def __init__(self, family_manager, user_manager):
        self.family = family_manager
        self.user_manager = user_manager

    async def family_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /family - настройка семейного бюджета"""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name

        # Сохраняем имя пользователя
        self.user_manager.set_user_name(user_id, user_name)

        family_data = self.family.get_family_data(user_id)

        if family_data:
            # Пользователь уже в семье
            await self._show_family_info(update, family_data)
        else:
            # Пользователь не в семье
            await self._show_family_setup(update)

    async def _show_family_info(self, update: Update, family_data: dict):
        """Показать информацию о семье"""
        user_id = update.effective_user.id

        # Получаем информацию об участниках
        members_info = ""
        for member_id in family_data['members']:
            member_name = self.user_manager.get_user_name(member_id)
            role = "👑 Админ" if member_id == family_data['created_by'] else "👤 Участник"
            members_info += f"• {member_name} - {role}\n"

        # Получаем статистику
        family_stats = self.family.get_family_statistics(user_id)

        response = f"""
🏠 **Семейная группа:** {family_data['name']}
🆔 **ID группы:** `{family_data['id']}`

👥 **Участники ({len(family_data['members'])}):**
{members_info}

📊 **Общая статистика:**
💸 Транзакций: {family_stats['total_transactions']}
💰 Общий баланс: {family_stats['total_balance']:.2f} лари
📈 Доходы: {family_stats['total_income']:.2f} лари
📉 Расходы: {family_stats['total_expenses']:.2f} лари

**Команды:**
• `/family_invite` - пригласить члена семьи
• `/family_stats` - детальная статистика
• `/family_leave` - покинуть группу
        """

        await update.message.reply_text(response, parse_mode='Markdown')

    async def _show_family_setup(self, update: Update):
        """Показать настройку семьи"""
        keyboard = [
            [
                InlineKeyboardButton("✅ Да, покинуть", callback_data="confirm_leave_family"),
                InlineKeyboardButton("❌ Отмена", callback_data="cancel_leave_family")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"⚠️ **Подтверждение**\n\n"
            f"Вы действительно хотите покинуть группу **{family_data['name']}**?\n\n"
            f"После выхода вы не будете видеть семейные транзакции.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Обработка callback-ов для семейных функций"""
        query = update.callback_query
        user_id = query.from_user.id
        user_name = query.from_user.first_name
        callback_data = query.data

        if callback_data == "create_family":
            try:
                family_id = self.family.create_family_group(user_id, f"Семья {user_name}")
                await query.edit_message_text(
                    f"🏠 **Семейная группа создана!**\n\n"
                    f"**ID группы:** `{family_id}`\n\n"
                    f"📋 **Пригласите членов семьи:**\n"
                    f"1. Отправьте им команду /family_invite\n"
                    f"2. Или дайте им этот ID: `{family_id}`\n\n"
                    f"✅ Теперь все ваши транзакции будут общими!",
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Ошибка создания семьи: {e}")
                await query.edit_message_text("❌ Ошибка создания семейной группы")
            return True

        elif callback_data == "join_family":
            await query.edit_message_text(
                "👥 **Присоединение к семье**\n\n"
                "Введите ID семейной группы, который вам дал админ:\n\n"
                "Пример: `abc12345`",
                parse_mode='Markdown'
            )
            # Сохраняем состояние ожидания ID
            user_data = self.user_manager.get_user_data(user_id)
            user_data['waiting_for_family_id'] = True
            self.user_manager.update_user_data(user_id, user_data)
            return True

        elif callback_data == "confirm_leave_family":
            if self.family.leave_family(user_id):
                await query.edit_message_text(
                    "✅ **Вы покинули семейную группу**\n\n"
                    "Теперь ваши транзакции снова будут личными.\n"
                    "Вы можете создать новую группу или присоединиться к другой через /family"
                )
            else:
                await query.edit_message_text("❌ Ошибка при выходе из группы")
            return True

        elif callback_data == "cancel_leave_family":
            await query.edit_message_text(
                "🏠 Вы остались в семейной группе!\n"
                "Используйте /family для управления группой."
            )
            return True

        return False

    def handle_family_id_input(self, user_id: int, family_id_text: str) -> dict:
        """Обработка ввода ID семейной группы"""
        family_id = family_id_text.strip()

        if self.family.join_family_group(user_id, family_id):
            family_data = self.family.get_family_data(user_id)
            return {
                'success': True,
                'message': f"🏠 **Добро пожаловать в семью!**\n\n"
                           f"**Группа:** {family_data['name']}\n"
                           f"👥 **Участников:** {len(family_data['members'])}\n\n"
                           f"✅ Теперь вы видите все семейные транзакции!\n"
                           f"📊 Используйте /balance для просмотра общего баланса"
            }
        else:
            return {
                'success': False,
                'message': f"❌ **Группа не найдена**\n\n"
                           f"Проверьте правильность ID: `{family_id}`\n"
                           f"Попробуйте еще раз или обратитесь к админу группы"
            }🏠 Создать
            семью
            ", callback_data="
            create_family
            "),
            InlineKeyboardButton("👥 Присоединиться", callback_data="join_family")
        ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "🏠 **Семейный бюджет**\n\n"
            "Создайте семейную группу для ведения общего бюджета!\n\n"
            "**Преимущества:**\n"
            "• 👥 Общие транзакции для всей семьи\n"
            "• 📊 Совместная статистика и анализ\n"
            "• 🤖 ИИ обучается на данных всей семьи\n"
            "• 📈 Отчеты по дням, неделям, месяцам\n\n"
            "Выберите действие:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

        async

        def family_invite_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

            """Команда /family_invite"""
        user_id = update.effective_user.id
        family_data = self.family.get_family_data(user_id)

        if not family_data:
            await update.message.reply_text("❌ Вы не состоите в семейной группе. Используйте /family")
            return

        if not self.family.is_family_admin(user_id):
            await update.message.reply_text("❌ Только админ группы может приглашать участников")
            return

        bot_username = context.bot.username or "YourBotName"
        invite_text = f"""
🏠 **Приглашение в семейную группу**

**Название:** {family_data['name']}
**ID группы:** `{family_data['id']}`

📋 **Инструкция для присоединения:**
1. Запустите бота @{bot_username}
2. Отправьте команду `/family`
3. Нажмите "👥 Присоединиться"
4. Введите ID группы: `{family_data['id']}`

✅ После присоединения вы будете видеть все семейные транзакции!
        """

        await update.message.reply_text(invite_text, parse_mode='Markdown')

    async def family_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /family_stats"""
        user_id = update.effective_user.id

        stats = self.family.get_detailed_family_stats(user_id)

        if not stats:
            await update.message.reply_text(
                "❌ Вы не состоите в семейной группе или нет транзакций. Используйте /family")
            return

        response = f"""
🏠 **Детальная семейная статистика**

📅 **За неделю:**
💸 Расходы: {stats['week']['expenses']:.2f} лари
💰 Доходы: {stats['week']['income']:.2f} лари
💎 Баланс: {stats['week']['balance']:+.2f} лари

📅 **За месяц:**
💸 Расходы: {stats['month']['expenses']:.2f} лари
💰 Доходы: {stats['month']['income']:.2f} лари
💎 Баланс: {stats['month']['balance']:+.2f} лари

👥 **По участникам (месяц):**
"""

        for member, member_stats in stats['by_member'].items():
            response += f"• {member}: {member_stats['count']} транзакций, {member_stats['expenses']:.0f} лари расходов\n"

        if stats['top_categories']:
            response += f"\n🔥 **Топ категории (месяц):**\n"
            for category, amount in stats['top_categories']:
                response += f"• {category}: {amount:.2f} лари\n"

        response += f"\n🤖 Команда /analyze для ИИ анализа семейных трат"

        await update.message.reply_text(response, parse_mode='Markdown')

    async def family_leave_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /family_leave"""
        user_id = update.effective_user.id
        family_data = self.family.get_family_data(user_id)

        if not family_data:
            await update.message.reply_text("❌ Вы не состоите в семейной группе")
            return

        keyboard = [
            [
                InlineKeyboardButton("