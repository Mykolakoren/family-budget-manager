import React from 'react';
import { Typography, Box } from '@mui/material';

const Analytics = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Analytics
      </Typography>
      <Typography variant="body1">
        Analytics and reporting interface will be implemented here.
        Features will include:
        - Spending trends and patterns
        - Category breakdown analysis
        - Budget vs actual comparisons
        - Income/expense forecasting
        - Custom date range reports
        - Export to PDF/Excel
      </Typography>
    </Box>
  );
};

export default Analytics;