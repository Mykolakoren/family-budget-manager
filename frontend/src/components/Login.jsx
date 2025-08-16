import React, { useState } from 'react'
import { 
  Paper, 
  TextField, 
  Button, 
  Typography, 
  Box, 
  Tab, 
  Tabs,
  Alert
} from '@mui/material'

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`login-tabpanel-${index}`}
      aria-labelledby={`login-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  )
}

function Login({ onLogin }) {
  const [tabValue, setTabValue] = useState(0)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const handleEmailLogin = () => {
    // TODO: Implement email/password authentication
    if (email && password) {
      onLogin()
    } else {
      setError('Please enter email and password')
    }
  }

  const handleTelegramLogin = () => {
    // TODO: Implement Telegram authentication
    onLogin()
  }

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        backgroundColor: '#f5f5f5'
      }}
    >
      <Paper sx={{ p: 4, maxWidth: 400, width: '100%' }}>
        <Typography variant="h4" align="center" gutterBottom>
          Family Budget Manager
        </Typography>
        
        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)} centered>
          <Tab label="Email Login" />
          <Tab label="Telegram" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          <TextField
            fullWidth
            label="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            margin="normal"
          />
          <Button
            fullWidth
            variant="contained"
            onClick={handleEmailLogin}
            sx={{ mt: 2 }}
          >
            Login
          </Button>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Typography variant="body1" align="center" sx={{ mb: 2 }}>
            Login with your Telegram account
          </Typography>
          <Button
            fullWidth
            variant="contained"
            onClick={handleTelegramLogin}
            sx={{ mt: 2 }}
          >
            Login with Telegram
          </Button>
        </TabPanel>
      </Paper>
    </Box>
  )
}

export default Login