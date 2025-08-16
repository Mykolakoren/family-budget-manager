import React from 'react';
import { Typography, Box } from '@mui/material';

const Settings = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Settings
      </Typography>
      <Typography variant="body1">
        Settings interface will be implemented here.
        Features will include:
        - User profile management
        - Language preferences
        - Currency settings
        - Notification preferences
        - Category management
        - Budget configuration
        - Data export/import
      </Typography>
    </Box>
  );
};

export default Settings;