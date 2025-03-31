import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { Box, TextField, Button, Typography, Container, Paper, Alert, Link } from '@mui/material';
import { loginUser } from '../features/auth/authSlice';
import { RootState, AppDispatch } from '../app/store';

const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { isAuthenticated, status, error: authError, isFirstLogin } = useSelector((state: RootState) => state.auth);
  
  useEffect(() => {
    if (isAuthenticated) {
      if (isFirstLogin) {
        navigate('/change-password');
      } else {
        navigate('/dashboard');
      }
    }
  }, [isAuthenticated, isFirstLogin, navigate]);
  
  useEffect(() => {
    if (authError) {
      setError(authError);
    }
  }, [authError]);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (!username || !password) {
      setError('Username and password are required');
      return;
    }
    
    if (!username.includes('@')) {
      setError('Please enter your student email address');
      return;
    }
    
    dispatch(loginUser({ username, password }));
  };
  
  return (
    <Container component="main" maxWidth="xs">
      <Paper 
        elevation={3} 
        sx={{ 
          mt: 8, 
          p: 4,
          borderRadius: 2,
          boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
        }}
      >
        <Box sx={{ 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center'
        }}>
          <Typography 
            component="h1" 
            variant="h5" 
            sx={{ 
              color: 'primary.main',
              fontWeight: 600,
              mb: 3
            }}
          >
            Student Portal Login
          </Typography>
          
          {error && (
            <Alert 
              severity="error" 
              sx={{ 
                mt: 2, 
                width: '100%',
                borderRadius: 1
              }}
            >
              {error}
            </Alert>
          )}
          
          <Box 
            component="form" 
            onSubmit={handleSubmit} 
            sx={{ mt: 1, width: '100%' }}
          >
            <TextField
              margin="normal"
              required
              fullWidth
              id="username"
              label="Student Email"
              name="username"
              autoComplete="email"
              autoFocus
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="student@example.com"
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
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ 
                mt: 3, 
                mb: 2,
                py: 1.5,
                fontSize: '1rem'
              }}
              disabled={status === 'loading'}
            >
              {status === 'loading' ? 'Logging in...' : 'Login'}
            </Button>
            
            <Box sx={{ mt: 2, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                First time login? Use your student email and
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
                Default password: changeme@123
              </Typography>
            </Box>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
};

export default Login; 