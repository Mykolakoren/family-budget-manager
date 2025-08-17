# -*- coding: utf-8 -*-
"""
Менеджер семейных групп для бота семейного бюджета
"""

import uuid
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class FamilyManager:
    """Менеджер для работы с семейными группами"""

    def __init__(self, database_manager, user_manager):
        self.db = database_manager
        self.user_manager = user_manager

    def create_family_group(self, creator_user_id: int, family_name: str = "Семейный бюджет") -> str:
        """Создать семейную группу"""
        family_id = str(uuid.uuid4())[:8]  # Короткий уникальный ID

        family_data = {
            'id': family_id,
            'name': family_name,
            'created_by': creator_user_id,
            'created_at': datetime.now().isoformat(),
            'members': [creator_user_id],
            'transactions': [],
            'settings': {
                'default_currency': 'GEL',
                'shared_categories': True,
                'notification_enabled': True
            }
        }

        # Сохраняем группу в БД
        if self.db.update_family_data(family_id, family_data):
            # Привязываем пользователя к группе
            user_data = self.user_manager.get_user_data(creator_user_id)
            user_data['family_id'] = family_id
            user_data['family_role'] = 'admin'
            self.user_manager.update_user_data(creator_user_id, user_data)

            logger.info(f"Создана семейная группа {family_id} пользователем {creator_user_id}")
            return family_id

        raise Exception("Ошибка создания семейной группы")

    def join_family_group(self, user_id: int, family_id: str) -> bool:
        """Присоединиться к семейной группе"""
        family_data = self.db.get_family_data(family_id)

        if not family_data:
            return False

        # Проверяем, не состоит ли уже в группе
        if user_id in family_data['members']:
            return True

        # Добавляем в участники
        family_data['members'].append(user_id)

        # Привязываем пользователя к группе
        user_data = self.user_manager.get_user_data(user_id)
        user_data['family_id'] = family_id
        user_data['family_role'] = 'member'

        # Сохраняем изменения
        if (self.db.update_family_data(family_id, family_data) and
                self.user_manager.update_user_data(user_id, user_data)):
            logger.info(f"Пользователь {user_id} присоединился к семье {family_id}")
            return True

        return False

    def get_family_data(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получить данные семейной группы пользователя"""
        user_data = self.user_manager.get_user_data(user_id)
        family_id = user_data.get('family_id')

        if not family_id:
            return None

        return self.db.get_family_data(family_id)

    def add_family_transaction(self, user_id: int, transaction: Dict[str, Any], user_name: str = None) -> bool:
        """Добавить транзакцию в семейный бюджет"""
        family_data = self.get_family_data(user_id)

        if not family_data:
            # Если нет семьи, добавляем как личную транзакцию
            return self.user_manager.add_transaction(user_id, transaction)

        # Добавляем информацию о том, кто добавил транзакцию
        if not user_name:
            user_name = self.user_manager.get_user_name(user_id)

        transaction['added_by'] = user_id
        transaction['added_by_name'] = user_name

        # Добавляем в семейные транзакции
        family_data['transactions'].append(transaction)

        # Обучаем ИИ пользователя
        self.user_manager.learn_from_transaction(user_id, transaction)

        # Сохраняем данные
        if self.db.update_family_data(family_data['id'], family_data):
            logger.info(f"Семейная транзакция добавлена пользователем {user_id}")
            return True

        return False

    def get_family_transactions(self, user_id: int) -> List[Dict[str, Any]]:
        """Получить все транзакции (семейные или личные)"""
        family_data = self.get_family_data(user_id)

        if family_data:
            return family_data['transactions']
        else:
            # Возвращаем личные транзакции
            return self.user_manager.get_user_transactions(user_id)

    def get_family_statistics(self, user_id: int) -> Dict[str, Any]:
        """Получить статистику семейной группы"""
        transactions = self.get_family_transactions(user_id)

        total_transactions = len(transactions)
        total_income = sum(t['amount'] for t in transactions if t['amount'] > 0)
        total_expenses = sum(abs(t['amount']) for t in transactions if t['amount'] < 0)
        total_balance = total_income - total_expenses

        return {
            'total_transactions': total_transactions,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'total_balance': total_balance
        }

    def get_detailed_family_stats(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получить детальную семейную статистику"""
        family_data = self.get_family_data(user_id)
        if not family_data:
            return None

        transactions = family_data['transactions']
        if not transactions:
            return None

        # Статистика по периодам
        today = datetime.now()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        week_transactions = []
        month_transactions = []

        for trans in transactions:
            try:
                trans_date = datetime.strptime(trans['date'][:10], '%Y-%m-%d')
                if trans_date >= week_ago:
                    week_transactions.append(trans)
                if trans_date >= month_ago:
                    month_transactions.append(trans)
            except (ValueError, KeyError):
                continue

        # Расчеты по периодам
        week_expenses = sum(abs(t['amount']) for t in week_transactions if t['amount'] < 0)
        month_expenses = sum(abs(t['amount']) for t in month_transactions if t['amount'] < 0)
        week_income = sum(t['amount'] for t in week_transactions if t['amount'] > 0)
        month_income = sum(t['amount'] for t in month_transactions if t['amount'] > 0)

        # Статистика по участникам
        by_member = defaultdict(lambda: {'expenses': 0, 'income': 0, 'count': 0})
        for trans in month_transactions:
            member_name = trans.get('added_by_name', 'Неизвестно')
            by_member[member_name]['count'] += 1
            if trans['amount'] < 0:
                by_member[member_name]['expenses'] += abs(trans['amount'])
            else:
                by_member[member_name]['income'] += trans['amount']

        # Топ категории
        by_category = defaultdict(float)
        for trans in month_transactions:
            if trans['amount'] < 0:
                by_category[trans['category']] += abs(trans['amount'])

        top_categories = sorted(by_category.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            'family_data': family_data,
            'week': {
                'expenses': week_expenses,
                'income': week_income,
                'balance': week_income - week_expenses
            },
            'month': {
                'expenses': month_expenses,
                'income': month_income,
                'balance': month_income - month_expenses
            },
            'by_member': dict(by_member),
            'top_categories': top_categories
        }

    def leave_family(self, user_id: int) -> bool:
        """Покинуть семейную группу"""
        family_data = self.get_family_data(user_id)
        if not family_data:
            return False

        family_id = family_data['id']

        # Удаляем из участников
        if user_id in family_data['members']:
            family_data['members'].remove(user_id)

        # Убираем привязку у пользователя
        user_data = self.user_manager.get_user_data(user_id)
        user_data['family_id'] = None
        user_data['family_role'] = None

        # Если это был единственный участник, удаляем группу
        if not family_data['members']:
            success = self.db.delete_family(family_id)
        else:
            success = self.db.update_family_data(family_id, family_data)

        # Сохраняем изменения пользователя
        if success and self.user_manager.update_user_data(user_id, user_data):
            logger.info(f"Пользователь {user_id} покинул семью {family_id}")
            return True

        return False

    def get_family_members_info(self, user_id: int) -> List[Dict[str, Any]]:
        """Получить информацию о участниках семьи"""
        family_data = self.get_family_data(user_id)
        if not family_data:
            return []

        members_info = []
        for member_id in family_data['members']:
            member_name = self.user_manager.get_user_name(member_id)
            role = "admin" if member_id == family_data['created_by'] else "member"

            members_info.append({
                'id': member_id,
                'name': member_name,
                'role': role,
                'is_admin': member_id == family_data['created_by']
            })

        return members_info

    def is_family_admin(self, user_id: int) -> bool:
        """Проверить, является ли пользователь админом семьи"""
        family_data = self.get_family_data(user_id)
        if not family_data:
            return False

        return family_data['created_by'] == user_id

    def get_family_balance_by_accounts(self, user_id: int) -> Dict[str, float]:
        """Получить баланс по счетам"""
        transactions = self.get_family_transactions(user_id)

        balances = {}
        for trans in transactions:
            account = trans.get('account', 'Неизвестно')
            amount = trans.get('amount', 0)
            currency = trans.get('currency', 'GEL')

            key = f"{account} ({currency})"
            if key not in balances:
                balances[key] = 0
            balances[key] += amount

        return balances