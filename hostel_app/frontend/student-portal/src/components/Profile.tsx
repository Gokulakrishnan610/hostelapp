import React, { useEffect, useState } from 'react';
import { Container, Paper, Typography, TextField, Button, Box, Alert, Divider } from '@mui/material';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { getProfile, updateProfile, changePassword } from '../services/api';
import { useNavigate } from 'react-router-dom';
import { StyledGrid } from './common/StyledGrid';
import Navbar from './common/Navbar';
import { toast } from 'react-toastify';

interface Profile {
  id: number;
  name: string;
  first_name: string;
  last_name: string;
  email: string;
  gender: string;
  department: string;
  year: string;
  roll_number: string;
  phone_number: string;
  parent_phone_number: string;
  room?: {
    category: string;
    location: string;
  };
  payment_status: string;
}

const Profile: React.FC = () => {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [updateSuccess, setUpdateSuccess] = useState(false);
  const [passwordSuccess, setPasswordSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState('');
  const [editing, setEditing] = useState<boolean>(false);
  const [formData, setFormData] = useState<Partial<Profile>>({});
  
  const navigate = useNavigate();
  
  useEffect(() => {
    fetchProfile();
  }, []);
  
    const fetchProfile = async () => {
      try {
        setLoading(true);
        const response = await getProfile();
        setProfile(response.data);
      setFormData(response.data);
      } catch (error) {
        console.error('Error fetching profile:', error);
      setError('Failed to load profile data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  const handleSubmit = async () => {
    try {
      await updateProfile(formData);
      setProfile(prev => ({ ...prev, ...formData } as Profile));
      setEditing(false);
      toast.success('Profile updated successfully!');
      } catch (error) {
        console.error('Error updating profile:', error);
      toast.error('Failed to update profile. Please try again.');
      }
  };
  
  const passwordFormik = useFormik({
    initialValues: {
      oldPassword: '',
      newPassword: '',
      confirmPassword: ''
    },
    validationSchema: Yup.object({
      oldPassword: Yup.string().required('Current password is required'),
      newPassword: Yup.string()
        .min(8, 'Password must be at least 8 characters')
        .required('New password is required'),
      confirmPassword: Yup.string()
        .oneOf([Yup.ref('newPassword')], 'Passwords must match')
        .required('Confirm password is required')
    }),
    onSubmit: async (values) => {
      try {
        setPasswordError('');
        setPasswordSuccess(false);
        await changePassword(values.oldPassword, values.newPassword);
        passwordFormik.resetForm();
        setPasswordSuccess(true);
      } catch (error: any) {
        console.error('Error changing password:', error);
        setPasswordError(error.response?.data?.detail || 'Failed to change password');
      }
    }
  });
  
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }
  
  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }
  
  if (!profile) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="warning">No profile data found.</Alert>
      </Box>
    );
  }
  
  return (
    <Box>
      <Navbar />
      <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
        <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
          Student Profile
      </Typography>
      
        <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h5">Personal Information</Typography>
            <Button 
              variant="outlined" 
              onClick={() => setEditing(!editing)}
            >
              {editing ? 'Cancel' : 'Edit'}
            </Button>
          </Box>
          <Divider sx={{ mb: 3 }} />
          
          {editing ? (
              <StyledGrid container spacing={2}>
              <StyledGrid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="First Name"
                  name="first_name"
                  value={formData.first_name || ''}
                  onChange={handleChange}
                />
              </StyledGrid>
              <StyledGrid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                  label="Last Name"
                  name="last_name"
                  value={formData.last_name || ''}
                  onChange={handleChange}
                  />
                </StyledGrid>
              <StyledGrid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                  label="Phone Number"
                  name="phone_number"
                  value={formData.phone_number || ''}
                  onChange={handleChange}
                  />
                </StyledGrid>
              <StyledGrid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                  label="Parent Phone Number"
                  name="parent_phone_number"
                  value={formData.parent_phone_number || ''}
                  onChange={handleChange}
                />
                </StyledGrid>
                <StyledGrid item xs={12}>
                <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
                  <Button
                    variant="contained"
                    onClick={handleSubmit}
                  >
                    Save Changes
                  </Button>
                </Box>
              </StyledGrid>
            </StyledGrid>
          ) : (
            <StyledGrid container spacing={2}>
              <StyledGrid item xs={12} sm={6} md={4}>
                <Typography variant="subtitle2" color="textSecondary">Full Name</Typography>
                <Typography variant="body1">{profile.name}</Typography>
              </StyledGrid>
              <StyledGrid item xs={12} sm={6} md={4}>
                <Typography variant="subtitle2" color="textSecondary">Email</Typography>
                <Typography variant="body1">{profile.email}</Typography>
              </StyledGrid>
              <StyledGrid item xs={12} sm={6} md={4}>
                <Typography variant="subtitle2" color="textSecondary">Gender</Typography>
                <Typography variant="body1">{profile.gender}</Typography>
              </StyledGrid>
              <StyledGrid item xs={12} sm={6} md={4}>
                <Typography variant="subtitle2" color="textSecondary">Phone Number</Typography>
                <Typography variant="body1">{profile.phone_number || 'Not provided'}</Typography>
              </StyledGrid>
              <StyledGrid item xs={12} sm={6} md={4}>
                <Typography variant="subtitle2" color="textSecondary">Parent Phone</Typography>
                <Typography variant="body1">{profile.parent_phone_number || 'Not provided'}</Typography>
                </StyledGrid>
              </StyledGrid>
          )}
          </Paper>
        
        <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
          <Typography variant="h5" gutterBottom>Academic Information</Typography>
          <Divider sx={{ mb: 3 }} />
          
          <StyledGrid container spacing={2}>
            <StyledGrid item xs={12} sm={6} md={4}>
              <Typography variant="subtitle2" color="textSecondary">Department</Typography>
              <Typography variant="body1">{profile.department}</Typography>
            </StyledGrid>
            <StyledGrid item xs={12} sm={6} md={4}>
              <Typography variant="subtitle2" color="textSecondary">Year</Typography>
              <Typography variant="body1">{profile.year}</Typography>
            </StyledGrid>
            <StyledGrid item xs={12} sm={6} md={4}>
              <Typography variant="subtitle2" color="textSecondary">Roll Number</Typography>
              <Typography variant="body1">{profile.roll_number}</Typography>
            </StyledGrid>
          </StyledGrid>
        </Paper>
        
        <Paper elevation={3} sx={{ p: 3 }}>
          <Typography variant="h5" gutterBottom>Accommodation Details</Typography>
          <Divider sx={{ mb: 3 }} />
          
          {profile.room ? (
              <StyledGrid container spacing={2}>
              <StyledGrid item xs={12} sm={6} md={4}>
                <Typography variant="subtitle2" color="textSecondary">Room Category</Typography>
                <Typography variant="body1">{profile.room.category}</Typography>
              </StyledGrid>
              <StyledGrid item xs={12} sm={6} md={4}>
                <Typography variant="subtitle2" color="textSecondary">Location</Typography>
                <Typography variant="body1">{profile.room.location}</Typography>
                </StyledGrid>
              <StyledGrid item xs={12} sm={6} md={4}>
                <Typography variant="subtitle2" color="textSecondary">Payment Status</Typography>
                <Typography 
                  variant="body1" 
                  sx={{ 
                    color: profile.payment_status === 'Confirmed' ? 'success.main' : 
                           profile.payment_status === 'Pending' ? 'warning.main' : 'error.main'
                  }}
                >
                  {profile.payment_status}
                </Typography>
                </StyledGrid>
                </StyledGrid>
          ) : (
            <Box sx={{ textAlign: 'center', py: 2 }}>
              <Typography color="textSecondary" sx={{ mb: 2 }}>
                No room assigned yet.
              </Typography>
                  <Button
                    variant="contained"
                onClick={() => navigate('/rooms')}
                  >
                Browse Available Rooms
                  </Button>
            </Box>
          )}
          </Paper>
      </Box>
    </Box>
  );
};

export default Profile; 