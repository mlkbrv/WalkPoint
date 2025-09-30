import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = 'http://192.168.0.165:8000/api'; // Change this to your Django server URL

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = await AsyncStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/users/token/refresh/`, {
            refresh: refreshToken,
          });
          
          const {access} = response.data;
          await AsyncStorage.setItem('access_token', access);
          
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        await AsyncStorage.multiRemove(['access_token', 'refresh_token']);
        // You can add navigation logic here
      }
    }
    
    return Promise.reject(error);
  }
);

export const AuthService = {
  async login(email: string, password: string) {
    try {
      const response = await api.post('/users/token/', {
        email,
        password,
      });
      
      const {access, refresh} = response.data;
      await AsyncStorage.multiSet([
        ['access_token', access],
        ['refresh_token', refresh],
      ]);
      
      return {success: true, data: response.data};
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed',
      };
    }
  },

  async register(userData: {
    email: string;
    password: string;
    password2: string;
    first_name?: string;
    last_name?: string;
    phone?: string;
  }) {
    try {
      const response = await api.post('/users/register/', userData);
      return {success: true, data: response.data};
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data || 'Registration failed',
      };
    }
  },

  async logout() {
    try {
      await AsyncStorage.multiRemove(['access_token', 'refresh_token']);
      return {success: true};
    } catch (error) {
      return {success: false, error: 'Logout failed'};
    }
  },

  async getProfile() {
    try {
      const response = await api.get('/users/me/');
      return {success: true, data: response.data};
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data || 'Failed to fetch profile',
      };
    }
  },

  async updateProfile(profileData: any) {
    try {
      const response = await api.patch('/users/me/', profileData);
      return {success: true, data: response.data};
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data || 'Failed to update profile',
      };
    }
  },

  async getTodaySteps() {
    try {
      const response = await api.get('/users/steps/today/');
      return {success: true, data: response.data};
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data || 'Failed to fetch steps',
      };
    }
  },
};

export default api;