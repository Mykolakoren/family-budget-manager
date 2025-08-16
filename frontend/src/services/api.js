import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (credentials) => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },
  
  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },
  
  getProfile: async () => {
    const response = await api.get('/users/me');
    return response.data;
  },
};

// Accounts API
export const accountsAPI = {
  getAll: async () => {
    const response = await api.get('/accounts/');
    return response.data;
  },
  
  create: async (accountData) => {
    const response = await api.post('/accounts/', accountData);
    return response.data;
  },
  
  update: async (id, accountData) => {
    const response = await api.patch(`/accounts/${id}`, accountData);
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/accounts/${id}`);
    return response.data;
  },
};

// Transactions API
export const transactionsAPI = {
  getAll: async (params = {}) => {
    const response = await api.get('/transactions/', { params });
    return response.data;
  },
  
  create: async (transactionData) => {
    const response = await api.post('/transactions/', transactionData);
    return response.data;
  },
  
  update: async (id, transactionData) => {
    const response = await api.patch(`/transactions/${id}`, transactionData);
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/transactions/${id}`);
    return response.data;
  },
  
  parseText: async (text) => {
    const response = await api.post('/transactions/parse', { text });
    return response.data;
  },
};

// Categories API
export const categoriesAPI = {
  getAll: async () => {
    const response = await api.get('/categories/');
    return response.data;
  },
  
  create: async (categoryData) => {
    const response = await api.post('/categories/', categoryData);
    return response.data;
  },
};

// Analytics API
export const analyticsAPI = {
  getDashboardStats: async () => {
    const response = await api.get('/analytics/dashboard');
    return response.data;
  },
  
  getExpensesByCategory: async (period = 'month') => {
    const response = await api.get(`/analytics/expenses-by-category?period=${period}`);
    return response.data;
  },
  
  getIncomeVsExpenses: async (period = 'month') => {
    const response = await api.get(`/analytics/income-vs-expenses?period=${period}`);
    return response.data;
  },
};

export default api;