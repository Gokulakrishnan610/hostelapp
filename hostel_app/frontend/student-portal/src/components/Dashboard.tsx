import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Grid, 
  CircularProgress, 
  Alert,
  Button,
  Divider,
  Chip
} from '@mui/material';
import { getProfile } from '../services/api';
import { useNavigate } from 'react-router-dom';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { ApiError } from '../types/api';
import { useDispatch } from 'react-redux';
import { logout } from '../features/auth/authSlice';
import { StyledGrid } from './common/StyledGrid';

interface Room {
  id: number;
  category: string;
  location: string;
  menu: string;
  price: number;
}

interface Profile {
  name: string;
  email: string;
  gender: string;
  room?: Room;
  payment_status: string;
}

const Dashboard: React.FC = () => {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const dispatch = useDispatch();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await getProfile();
        setProfile(response.data);
      } catch (error) {
        const apiError = error as ApiError;
        setError(apiError.response?.data?.detail || 'Failed to load profile');
        toast.error('Failed to load profile');
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <ToastContainer />
      
      <Typography variant="h4" gutterBottom>
        Welcome, {profile?.name}!
      </Typography>

      <StyledGrid container spacing={3}>
        <StyledGrid item xs={12} md={6}>
          <Paper 
            sx={{ 
              p: 3, 
              height: '100%',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
              borderRadius: 2
            }}
          >
            <Typography variant="h6" gutterBottom sx={{ color: 'primary.main' }}>
              Personal Information
            </Typography>
            <Divider sx={{ my: 2 }} />
            <StyledGrid container spacing={2}>
              <StyledGrid item xs={4}>
                <Typography color="textSecondary" variant="subtitle2">Name:</Typography>
              </StyledGrid>
              <StyledGrid item xs={8}>
                <Typography>{profile?.name}</Typography>
              </StyledGrid>
              <StyledGrid item xs={4}>
                <Typography color="textSecondary" variant="subtitle2">Email:</Typography>
              </StyledGrid>
              <StyledGrid item xs={8}>
                <Typography>{profile?.email}</Typography>
              </StyledGrid>
              <StyledGrid item xs={4}>
                <Typography color="textSecondary" variant="subtitle2">Gender:</Typography>
              </StyledGrid>
              <StyledGrid item xs={8}>
                <Typography>{profile?.gender}</Typography>
              </StyledGrid>
            </StyledGrid>
          </Paper>
        </StyledGrid>

        <StyledGrid item xs={12} md={6}>
          <Paper 
            sx={{ 
              p: 3, 
              height: '100%',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
              borderRadius: 2
            }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" sx={{ color: 'primary.main' }}>
                Room Information
              </Typography>
              {!profile?.room && (
                <Button 
                  variant="outlined" 
                  size="small"
                  onClick={() => navigate('/rooms')}
                  sx={{ textTransform: 'none' }}
                >
                  Select Room
                </Button>
              )}
            </Box>
            <Divider sx={{ my: 2 }} />
            {profile?.room ? (
              <StyledGrid container spacing={2}>
                <StyledGrid item xs={4}>
                  <Typography color="textSecondary" variant="subtitle2">Category:</Typography>
                </StyledGrid>
                <StyledGrid item xs={8}>
                  <Typography>{profile.room.category}</Typography>
                </StyledGrid>
                <StyledGrid item xs={4}>
                  <Typography color="textSecondary" variant="subtitle2">Location:</Typography>
                </StyledGrid>
                <StyledGrid item xs={8}>
                  <Typography>{profile.room.location}</Typography>
                </StyledGrid>
                <StyledGrid item xs={4}>
                  <Typography color="textSecondary" variant="subtitle2">Price:</Typography>
                </StyledGrid>
                <StyledGrid item xs={8}>
                  <Typography>₹{profile.room.price.toLocaleString()}</Typography>
                </StyledGrid>
                <StyledGrid item xs={4}>
                  <Typography color="textSecondary" variant="subtitle2">Payment Status:</Typography>
                </StyledGrid>
                <StyledGrid item xs={8}>
                  <Chip
                    label={profile.payment_status}
                    color={
                      profile.payment_status === 'Confirmed' ? 'success' :
                      profile.payment_status === 'Pending' ? 'warning' : 'error'
                    }
                    size="small"
                    sx={{ fontWeight: 500 }}
                  />
                </StyledGrid>
              </StyledGrid>
            ) : (
              <Box sx={{ textAlign: 'center', py: 3 }}>
                <Typography color="textSecondary" sx={{ mb: 2 }}>
                  No room assigned yet.
                </Typography>
                <Button 
                  variant="contained"
                  onClick={() => navigate('/rooms')}
                  sx={{ textTransform: 'none' }}
                >
                  Browse Available Rooms
                </Button>
              </Box>
            )}
          </Paper>
        </StyledGrid>
      </StyledGrid>
    </Box>
  );
};

export default Dashboard; 