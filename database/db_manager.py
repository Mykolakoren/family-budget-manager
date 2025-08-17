# -*- coding: utf-8 -*-
"""
Менеджер базы данных для бота семейного бюджета
"""

import json
import os
import shutil
import csv
import io
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Менеджер для работы с базой данных"""

    def __init__(self, data_file: str = "budget_data.json"):
        self.data_file = data_file
        self.backup_file = f"{data_file}.backup"
        self._data_cache = None
        self._last_save_time = None

    def load_data(self) -> Dict[str, Any]:
        """Загрузить данные из файла"""
        if self._data_cache is not None:
            return self._data_cache

        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self._data_cache = json.load(f)
                print(f"✅ База данных загружена из {self.data_file}")
                return self._data_cache
            else:
                print(f"📁 Создается новая база данных: {self.data_file}")
                self._data_cache = self._create_empty_database()
                return self._data_cache
        except Exception as e:
            logger.error(f"Ошибка загрузки БД: {e}")
            print(f"❌ Ошибка загрузки БД: {e}")
            # Пытаемся восстановить из бэкапа
            return self._restore_from_backup()

    def save_data(self, data: Dict[str, Any]) -> bool:
        """Сохранить данные в файл"""
        try:
            # Создаем бэкап существующего файла
            if os.path.exists(self.data_file):
                shutil.copy2(self.data_file, self.backup_file)

            # Сохраняем новые данные
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            # Обновляем кэш
            self._data_cache = data
            self._last_save_time = datetime.now()

            file_size = os.path.getsize(self.data_file)
            print(f"💾 БД сохранена: {file_size} байт")
            return True

        except Exception as e:
            logger.error(f"Ошибка сохранения БД: {e}")
            print(f"❌ Ошибка сохранения БД: {e}")
            return False

    def _create_empty_database(self) -> Dict[str, Any]:
        """Создать пустую структуру базы данных"""
        return {
            'users': {},
            'families': {},
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'version': '1.0'
            }
        }

    def _restore_from_backup(self) -> Dict[str, Any]:
        """Восстановить данные из бэкапа"""
        try:
            if os.path.exists(self.backup_file):
                with open(self.backup_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print("🔄 Данные восстановлены из бэкапа")
                self._data_cache = data
                return data
        except Exception as e:
            logger.error(f"Ошибка восстановления из бэкапа: {e}")

        print("⚠️ Создается новая база данных")
        return self._create_empty_database()

    def export_user_data(self, user_data: Dict[str, Any], format: str = 'csv') -> bytes:
        """Экспорт данных пользователя"""
        if format == 'csv':
            return self._export_to_csv(user_data)
        elif format == 'json':
            return self._export_to_json(user_data)
        else:
            raise ValueError(f"Неподдерживаемый формат: {format}")

    def _export_to_csv(self, user_data: Dict[str, Any]) -> bytes:
        """Экспорт в CSV формат"""
        output = io.StringIO()
        writer = csv.writer(output)

        # Заголовки
        writer.writerow([
            'Дата', 'Сумма', 'Валюта', 'Категория',
            'Счет', 'Описание', 'Тип', 'Источник'
        ])

        # Данные транзакций
        for transaction in user_data.get('transactions', []):
            writer.writerow([
                transaction.get('date', ''),
                transaction.get('amount', 0),
                transaction.get('currency', 'GEL'),
                transaction.get('category', ''),
                transaction.get('account', ''),
                transaction.get('description', ''),
                transaction.get('type', ''),
                transaction.get('source', '')
            ])

        return output.getvalue().encode('utf-8')

    def _export_to_json(self, user_data: Dict[str, Any]) -> bytes:
        """Экспорт в JSON формат"""
        export_data = {
            'transactions': user_data.get('transactions', []),
            'ai_learning': user_data.get('ai_learning', {}),
            'export_date': datetime.now().isoformat()
        }
        return json.dumps(export_data, ensure_ascii=False, indent=2).encode('utf-8')

    def get_user_data(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получить данные пользователя"""
        data = self.load_data()
        return data.get('users', {}).get(str(user_id))

    def update_user_data(self, user_id: int, user_data: Dict[str, Any]) -> bool:
        """Обновить данные пользователя"""
        data = self.load_data()
        if 'users' not in data:
            data['users'] = {}

        data['users'][str(user_id)] = user_data
        return self.save_data(data)

    def get_family_data(self, family_id: str) -> Optional[Dict[str, Any]]:
        """Получить данные семьи"""
        data = self.load_data()
        return data.get('families', {}).get(family_id)

    def update_family_data(self, family_id: str, family_data: Dict[str, Any]) -> bool:
        """Обновить данные семьи"""
        data = self.load_data()
        if 'families' not in data:
            data['families'] = {}

        data['families'][family_id] = family_data
        return self.save_data(data)

    def delete_family(self, family_id: str) -> bool:
        """Удалить семью"""
        data = self.load_data()
        if 'families' in data and family_id in data['families']:
            del data['families'][family_id]
            return self.save_data(data)
        return False

    def get_statistics(self) -> Dict[str, Any]:
        """Получить общую статистику"""
        data = self.load_data()

        total_users = len(data.get('users', {}))
        total_families = len(data.get('families', {}))

        total_transactions = 0
        for user_data in data.get('users', {}).values():
            total_transactions += len(user_data.get('transactions', []))

        for family_data in data.get('families', {}).values():
            total_transactions += len(family_data.get('transactions', []))

        return {
            'total_users': total_users,
            'total_families': total_families,
            'total_transactions': total_transactions,
            'database_size': os.path.getsize(self.data_file) if os.path.exists(self.data_file) else 0,
            'last_save': self._last_save_time.isoformat() if self._last_save_time else None
        }