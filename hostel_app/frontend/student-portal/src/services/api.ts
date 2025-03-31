import axios from 'axios';

const API_URL = 'http://localhost:8000/api/';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add an interceptor to include the token with each request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Auth services
export const login = (username: string, password: string) => {
  return axios.post(`${API_URL}token/`, { username, password });
};

export const refreshToken = (refresh: string) => {
  return axios.post(`${API_URL}token/refresh/`, { refresh });
};

// Student services
export const getProfile = () => {
  return api.get('students/my_profile/');
};

export const updateProfile = (profileData: any) => {
  return api.patch('students/me/', profileData);
};

export const changePassword = (oldPassword: string, newPassword: string) => {
  return api.post('students/change_password/', {
    old_password: oldPassword,
    new_password: newPassword,
  });
};

// Room services
export const getRooms = (filters?: any) => {
  return api.get('rooms/', { params: filters });
};

export const bookRoom = (roomId: number) => {
  return api.post(`rooms/${roomId}/book/`);
};

// Payment services
export const getPayments = () => {
  return api.get('payments/');
};

export const makePayment = (paymentData: { room_id: number, amount: number, transaction_id: string }) => {
  return api.post('student/make-payment/', paymentData);
};

// OTP verification services
export const requestOtp = () => {
  return api.post('student/request-otp/');
};

export const verifyOtp = (otp: string) => {
  return api.post('student/verify-otp/', { otp });
};

export default api; 