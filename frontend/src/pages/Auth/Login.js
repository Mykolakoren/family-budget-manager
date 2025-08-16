import React, { useState } from 'react';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  Tab,
  Tabs,
} from '@mui/material';
import { useAuth } from '../../contexts/AuthContext';

const Login = () => {
  const [tab, setTab] = useState(0);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    telegram_id: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleTabChange = (event, newValue) => {
    setTab(newValue);
    setError('');
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const credentials = tab === 0 
        ? { email: formData.email, password: formData.password }
        : { telegram_id: formData.telegram_id };
      
      await login(credentials);
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container component="main" maxWidth="sm">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper elevation={3} sx={{ padding: 4, width: '100%' }}>
          <Typography component="h1" variant="h4" align="center" gutterBottom>
            Family Budget Manager
          </Typography>
          
          <Tabs value={tab} onChange={handleTabChange} centered>
            <Tab label="Email Login" />
            <Tab label="Telegram Login" />
          </Tabs>

          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3 }}>
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            {tab === 0 && (
              <>
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  id="email"
                  label="Email Address"
                  name="email"
                  autoComplete="email"
                  autoFocus
                  value={formData.email}
                  onChange={handleChange}
                />
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  name="password"
                  label="Password"
                  type="password"
                  id="password"
                  autoComplete="current-password"
                  value={formData.password}
                  onChange={handleChange}
                />
              </>
            )}

            {tab === 1 && (
              <TextField
                margin="normal"
                required
                fullWidth
                id="telegram_id"
                label="Telegram ID"
                name="telegram_id"
                autoFocus
                value={formData.telegram_id}
                onChange={handleChange}
                helperText="Enter your Telegram user ID (numbers only)"
              />
            )}

            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={loading}
            >
              {loading ? 'Signing In...' : 'Sign In'}
            </Button>

            {tab === 1 && (
              <Typography variant="body2" color="text.secondary" align="center">
                To get your Telegram ID, message @userinfobot on Telegram
              </Typography>
            )}
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default Login;