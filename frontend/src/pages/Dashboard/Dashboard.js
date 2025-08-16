import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  CircularProgress,
} from '@mui/material';
import {
  AccountBalance as BalanceIcon,
  TrendingUp as IncomeIcon,
  TrendingDown as ExpenseIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { Doughnut, Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
} from 'chart.js';
import { analyticsAPI } from '../../services/api';
import { useI18n } from '../../contexts/I18nContext';

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title
);

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const { t } = useI18n();

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      // Mock data for now since analytics endpoints are not implemented
      const mockData = {
        totalBalance: 15420.50,
        monthlyIncome: 5000.00,
        monthlyExpenses: 3250.75,
        currency: 'USD',
        expensesByCategory: [
          { category: 'Food', amount: 850 },
          { category: 'Transport', amount: 320 },
          { category: 'Entertainment', amount: 180 },
          { category: 'Health', amount: 240 },
          { category: 'Other', amount: 160 },
        ],
        incomeVsExpenses: {
          labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
          income: [4800, 5200, 4900, 5100, 5000, 5300],
          expenses: [3200, 3400, 3100, 3300, 3250, 3500],
        }
      };
      
      setDashboardData(mockData);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  const expenseChartData = {
    labels: dashboardData.expensesByCategory.map(item => item.category),
    datasets: [
      {
        data: dashboardData.expensesByCategory.map(item => item.amount),
        backgroundColor: [
          '#FF6384',
          '#36A2EB',
          '#FFCE56',
          '#4BC0C0',
          '#9966FF',
        ],
      },
    ],
  };

  const incomeExpenseChartData = {
    labels: dashboardData.incomeVsExpenses.labels,
    datasets: [
      {
        label: 'Income',
        data: dashboardData.incomeVsExpenses.income,
        borderColor: '#4CAF50',
        backgroundColor: 'rgba(76, 175, 80, 0.1)',
        tension: 0.1,
      },
      {
        label: 'Expenses',
        data: dashboardData.incomeVsExpenses.expenses,
        borderColor: '#F44336',
        backgroundColor: 'rgba(244, 67, 54, 0.1)',
        tension: 0.1,
      },
    ],
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          {t('dashboard')}
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => {/* TODO: Open add transaction dialog */}}
        >
          {t('addTransaction')}
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* Stats Cards */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <BalanceIcon color="primary" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    {t('totalBalance')}
                  </Typography>
                  <Typography variant="h5">
                    ${dashboardData.totalBalance.toFixed(2)}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <IncomeIcon color="success" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    {t('monthlyIncome')}
                  </Typography>
                  <Typography variant="h5" color="success.main">
                    +${dashboardData.monthlyIncome.toFixed(2)}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <ExpenseIcon color="error" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    {t('monthlyExpenses')}
                  </Typography>
                  <Typography variant="h5" color="error.main">
                    -${dashboardData.monthlyExpenses.toFixed(2)}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Charts */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Expenses by Category
              </Typography>
              <Box height={300}>
                <Doughnut 
                  data={expenseChartData} 
                  options={{ maintainAspectRatio: false }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Income vs Expenses
              </Typography>
              <Box height={300}>
                <Line 
                  data={incomeExpenseChartData} 
                  options={{ 
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        position: 'top',
                      },
                    },
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;