import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { login, refreshToken, getProfile } from '../../services/api';
import { jwtDecode } from 'jwt-decode';

// Check if there's a token in localStorage
const token = localStorage.getItem('token');
const refreshTokenValue = localStorage.getItem('refreshToken');

let initialUser = null;
if (token) {
  try {
    // Decode the token to get user info
    const decoded: any = jwtDecode(token);
    initialUser = {
      id: decoded.user_id,
      username: decoded.username,
    };
  } catch (error) {
    // If token is invalid, clear it
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
  }
}

interface AuthState {
  user: any;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isFirstLogin: boolean;
  status: 'idle' | 'loading' | 'succeeded' | 'failed';
  error: string | null;
}

const initialState: AuthState = {
  user: initialUser,
  token: token,
  refreshToken: refreshTokenValue,
  isAuthenticated: !!token,
  isFirstLogin: false,
  status: 'idle',
  error: null,
};

export const loginUser = createAsyncThunk(
  'auth/login',
  async ({ username, password }: { username: string; password: string }, { rejectWithValue }) => {
    try {
      const response = await login(username, password);
      return response.data;
    } catch (err: any) {
      return rejectWithValue(err.response?.data || 'Failed to login');
    }
  }
);

export const loadProfile = createAsyncThunk(
  'auth/profile',
  async (_, { rejectWithValue }) => {
    try {
      const response = await getProfile();
      return response.data;
    } catch (err: any) {
      return rejectWithValue(err.response?.data || 'Failed to load profile');
    }
  }
);

export const refreshUserToken = createAsyncThunk(
  'auth/refresh',
  async (refreshTokenVal: string, { rejectWithValue }) => {
    try {
      const response = await refreshToken(refreshTokenVal);
      return response.data;
    } catch (err: any) {
      return rejectWithValue(err.response?.data || 'Failed to refresh token');
    }
  }
);

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    logout(state) {
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
      state.user = null;
      state.token = null;
      state.refreshToken = null;
      state.isAuthenticated = false;
      state.status = 'idle';
    },
    resetFirstLogin(state) {
      state.isFirstLogin = false;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(loginUser.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.token = action.payload.access;
        state.refreshToken = action.payload.refresh;
        
        // Decode token to get user info
        const decoded: any = jwtDecode(action.payload.access);
        state.user = {
          id: decoded.user_id,
          username: decoded.username,
        };
        
        state.isAuthenticated = true;
        state.isFirstLogin = decoded.is_first_login || false;
        
        // Save tokens to localStorage
        localStorage.setItem('token', action.payload.access);
        localStorage.setItem('refreshToken', action.payload.refresh);
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload as string;
      })
      .addCase(loadProfile.fulfilled, (state, action) => {
        state.user = { ...state.user, ...action.payload };
      })
      .addCase(refreshUserToken.fulfilled, (state, action) => {
        state.token = action.payload.access;
        localStorage.setItem('token', action.payload.access);
      });
  },
});

export const { logout, resetFirstLogin } = authSlice.actions;
export default authSlice.reducer; 