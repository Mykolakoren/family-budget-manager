import React, { createContext, useContext, useState } from 'react';
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

// Translation resources
const resources = {
  en: {
    translation: {
      dashboard: 'Dashboard',
      transactions: 'Transactions',
      accounts: 'Accounts',
      analytics: 'Analytics',
      settings: 'Settings',
      logout: 'Logout',
      welcome: 'Welcome to Family Budget Manager',
      addTransaction: 'Add Transaction',
      amount: 'Amount',
      description: 'Description',
      category: 'Category',
      account: 'Account',
      date: 'Date',
      type: 'Type',
      income: 'Income',
      expense: 'Expense',
      save: 'Save',
      cancel: 'Cancel',
      totalBalance: 'Total Balance',
      monthlyExpenses: 'Monthly Expenses',
      monthlyIncome: 'Monthly Income',
    }
  },
  ru: {
    translation: {
      dashboard: 'Панель управления',
      transactions: 'Транзакции',
      accounts: 'Счета',
      analytics: 'Аналитика',
      settings: 'Настройки',
      logout: 'Выйти',
      welcome: 'Добро пожаловать в Family Budget Manager',
      addTransaction: 'Добавить транзакцию',
      amount: 'Сумма',
      description: 'Описание',
      category: 'Категория',
      account: 'Счет',
      date: 'Дата',
      type: 'Тип',
      income: 'Доход',
      expense: 'Расход',
      save: 'Сохранить',
      cancel: 'Отмена',
      totalBalance: 'Общий баланс',
      monthlyExpenses: 'Расходы за месяц',
      monthlyIncome: 'Доходы за месяц',
    }
  },
  uk: {
    translation: {
      dashboard: 'Панель керування',
      transactions: 'Транзакції',
      accounts: 'Рахунки',
      analytics: 'Аналітика',
      settings: 'Налаштування',
      logout: 'Вийти',
      welcome: 'Ласкаво просимо до Family Budget Manager',
      addTransaction: 'Додати транзакцію',
      amount: 'Сума',
      description: 'Опис',
      category: 'Категорія',
      account: 'Рахунок',
      date: 'Дата',
      type: 'Тип',
      income: 'Дохід',
      expense: 'Витрата',
      save: 'Зберегти',
      cancel: 'Скасувати',
      totalBalance: 'Загальний баланс',
      monthlyExpenses: 'Витрати за місяць',
      monthlyIncome: 'Доходи за місяць',
    }
  },
  ka: {
    translation: {
      dashboard: 'დაშბორდი',
      transactions: 'ტრანზაქციები',
      accounts: 'ანგარიშები',
      analytics: 'ანალიტიკა',
      settings: 'პარამეტრები',
      logout: 'გამოსვლა',
      welcome: 'მოგესალმებით Family Budget Manager-ში',
      addTransaction: 'ტრანზაქციის დამატება',
      amount: 'თანხა',
      description: 'აღწერა',
      category: 'კატეგორია',
      account: 'ანგარიში',
      date: 'თარიღი',
      type: 'ტიპი',
      income: 'შემოსავალი',
      expense: 'ხარჯი',
      save: 'შენახვა',
      cancel: 'გაუქმება',
      totalBalance: 'მთლიანი ბალანსი',
      monthlyExpenses: 'თვიური ხარჯები',
      monthlyIncome: 'თვიური შემოსავალი',
    }
  }
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'en',
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false,
    },
  });

const I18nContext = createContext();

export const useI18n = () => {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error('useI18n must be used within an I18nProvider');
  }
  return context;
};

export const I18nProvider = ({ children }) => {
  const [language, setLanguage] = useState(i18n.language);

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
    setLanguage(lng);
  };

  const value = {
    language,
    changeLanguage,
    t: i18n.t,
  };

  return (
    <I18nContext.Provider value={value}>
      {children}
    </I18nContext.Provider>
  );
};