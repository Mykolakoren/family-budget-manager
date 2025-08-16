import React from 'react';
import { Typography, Box } from '@mui/material';

const Transactions = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Transactions
      </Typography>
      <Typography variant="body1">
        Transaction management interface will be implemented here.
        Features will include:
        - Transaction list with filtering and sorting
        - Add/edit/delete transactions
        - Natural language input parsing
        - Bulk operations
        - Export functionality
      </Typography>
    </Box>
  );
};

export default Transactions;