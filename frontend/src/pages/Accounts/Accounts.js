import React from 'react';
import { Typography, Box } from '@mui/material';

const Accounts = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Accounts
      </Typography>
      <Typography variant="body1">
        Account management interface will be implemented here.
        Features will include:
        - List of all accounts with balances
        - Add/edit/delete accounts
        - Multi-currency support
        - Account types (cash, bank, crypto, etc.)
        - Transfer between accounts
      </Typography>
    </Box>
  );
};

export default Accounts;