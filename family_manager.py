# family_manager.py
from datetime import datetime, timedelta
from collections import defaultdict
import uuid


class FamilyManager:
    """Менеджер семейных групп"""

    def __init__(self, database_manager, user_manager):
        self.db = database_manager
        self.user_manager = user_manager

    def create_family_group(self, creator_user_id, family_name="Семейный бюджет"):
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

        # Сохраняем группу
        users_data = self.db.load_data()
        if 'families' not in users_data:
            users_data['families'] = {}

        users_data['families'][family_id] = family_data

        # Привязываем пользователя к группе
        user_data = self.user_manager.get_user_data(creator_user_id)
        user_data['family_id'] = family_id
        user_data['family_role'] = 'admin'

        self.db.save_data(users_data)
        return family_id

    def join_family_group(self, user_id, family_id):
        """Присоединиться к семейной группе"""
        users_data = self.db.load_data()

        if 'families' not in users_data or family_id not in users_data['families']:
            return False

        family_data = users_data['families'][family_id]

        if user_id not in family_data['members']:
            family_data['members'].append(user_id)

            # Привязываем пользователя к группе
            user_data = self.user_manager.get_user_data(user_id)
            user_data['family_id'] = family_id
            user_data['family_role'] = 'member'

            self.db.save_data(users_data)
            return True

        return False

    def get_family_data(self, user_id):
        """Получить данные семейной группы пользователя"""
        user_data = self.user_manager.get_user_data(user_id)
        family_id = user_data.get('family_id')

        if not family_id:
            return None

        users_data = self.db.load_data()
        if 'families' not in users_data:
            return None

        return users_data['families'].get(family_id)

    def add_family_transaction(self, user_id, transaction):
        """Добавить транзакцию в семейный бюджет"""
        family_data = self.get_family_data(user_id)

        if not family_data:
            # Если нет семьи, добавляем как обычную транзакцию
            return self.user_manager.add_transaction(user_id, transaction)

        # Добавляем информацию о том, кто добавил транзакцию
        transaction['added_by'] = user_id
        transaction['added_by_name'] = self.get_user_name(user_id)

        # Добавляем в семейные транзакции
        users_data = self.db.load_data()
        users_data['families'][family_data['id']]['transactions'].append(transaction)

        # Обучаем ИИ
        self.user_manager.learn_from_transaction(user_id, transaction)

        # Сохраняем данные
        if self.db.save_data(users_data):
            print(f"💾 Семейная транзакция сохранена от пользователя {user_id}")
            return True
        return False

    def get_family_transactions(self, user_id):
        """Получить все семейные транзакции"""
        family_data = self.get_family_data(user_id)

        if not family_data:
            # Если нет семьи, возвращаем личные транзакции
            user_data = self.user_manager.get_user_data(user_id)
            return user_data['transactions']

        return family_data['transactions']

    def get_user_name(self, user_id):
        """Получить имя пользователя"""
        user_data = self.user_manager.get_user_data(user_id)
        return user_data.get('name', f'Пользователь {str(user_id)[-4:]}')

    def get_family_statistics(self, user_id):
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

    def get_detailed_family_stats(self, user_id):
        """Получить детальную семейную статистику"""
        family_data = self.get_family_data(user_id)
        if not family_data:
            return None

        transactions = self.get_family_transactions(user_id)

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
            except:
                continue

        # Расчеты
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

    def leave_family(self, user_id):
        """Покинуть семейную группу"""
        family_data = self.get_family_data(user_id)
        if not family_data:
            return False

        users_data = self.db.load_data()
        family_id = family_data['id']

        # Удаляем из участников
        if user_id in family_data['members']:
            family_data['members'].remove(user_id)

        # Убираем привязку у пользователя
        user_data = self.user_manager.get_user_data(user_id)
        if 'family_id' in user_data:
            del user_data['family_id']
        if 'family_role' in user_data:
            del user_data['family_role']

        # Если это был единственный участник, удаляем группу
        if not family_data['members']:
            del users_data['families'][family_id]

        self.db.save_data(users_data)
        return True