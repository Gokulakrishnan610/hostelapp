import React, { useState } from 'react';
import { Container, Paper, Typography, TextField, Button, Box, Alert } from '@mui/material';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { changePassword } from '../services/api';
import { resetFirstLogin } from '../features/auth/authSlice';

const FirstLoginPassword: React.FC = () => {
  const [error, setError] = useState('');
  const dispatch = useDispatch();
  const navigate = useNavigate();
  
  const formik = useFormik({
    initialValues: {
      oldPassword: '',
      newPassword: '',
      confirmPassword: ''
    },
    validationSchema: Yup.object({
      oldPassword: Yup.string().required('Current password is required'),
      newPassword: Yup.string()
        .min(8, 'Password must be at least 8 characters')
        .notOneOf([Yup.ref('oldPassword')], 'New password must be different from old password')
        .required('New password is required'),
      confirmPassword: Yup.string()
        .oneOf([Yup.ref('newPassword')], 'Passwords must match')
        .required('Confirm password is required')
    }),
    onSubmit: async (values) => {
      try {
        setError('');
        await changePassword(values.oldPassword, values.newPassword);
        dispatch(resetFirstLogin());
        navigate('/dashboard');
      } catch (error: any) {
        console.error('Error changing password:', error);
        setError(error.response?.data?.detail || 'Failed to change password');
      }
    }
  });
  
  return (
    <Container maxWidth="sm" sx={{ mt: 8 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h5" align="center" gutterBottom>
          Change Default Password
        </Typography>
        
        <Typography variant="body1" sx={{ mb: 3 }}>
          For security reasons, you must change your default password before continuing.
        </Typography>
        
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}
        
        <Box component="form" onSubmit={formik.handleSubmit}>
          <TextField
            fullWidth
            margin="normal"
            id="oldPassword"
            name="oldPassword"
            label="Current Password (changeme@123)"
            type="password"
            value={formik.values.oldPassword}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            error={formik.touched.oldPassword && Boolean(formik.errors.oldPassword)}
            helperText={formik.touched.oldPassword && formik.errors.oldPassword}
          />
          
          <TextField
            fullWidth
            margin="normal"
            id="newPassword"
            name="newPassword"
            label="New Password"
            type="password"
            value={formik.values.newPassword}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            error={formik.touched.newPassword && Boolean(formik.errors.newPassword)}
            helperText={formik.touched.newPassword && formik.errors.newPassword}
          />
          
          <TextField
            fullWidth
            margin="normal"
            id="confirmPassword"
            name="confirmPassword"
            label="Confirm New Password"
            type="password"
            value={formik.values.confirmPassword}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            error={formik.touched.confirmPassword && Boolean(formik.errors.confirmPassword)}
            helperText={formik.touched.confirmPassword && formik.errors.confirmPassword}
          />
          
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3 }}
            disabled={!formik.isValid || formik.isSubmitting}
          >
            Change Password & Continue
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default FirstLoginPassword; 