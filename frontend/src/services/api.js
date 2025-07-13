import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (userData) => api.post('/api/v1/auth/register', userData),
  login: (credentials) => api.post('/api/v1/auth/login', credentials),
  getCurrentUser: () => api.get('/api/v1/auth/me'),
  getSubscription: () => api.get('/api/v1/auth/subscription'),
  logout: () => api.post('/api/v1/auth/logout'),
  refreshToken: () => api.post('/api/v1/auth/refresh'),
};

// Payment API
export const paymentAPI = {
  getPlans: () => api.get('/api/v1/payment/plans'),
  createCheckoutSession: (plan, successUrl, cancelUrl) => 
    api.post('/api/v1/payment/create-checkout-session', { plan, success_url: successUrl, cancel_url: cancelUrl }),
  createPortalSession: (returnUrl) => 
    api.post('/api/v1/payment/create-portal-session', { return_url: returnUrl }),
  getUsage: () => api.get('/api/v1/payment/usage'),
};

// Research API
export const researchAPI = {
  conductResearch: (researchData) => api.post('/api/v1/research', researchData),
  streamResearch: (query, maxResults = 10) => 
    api.get('/api/v1/research/stream', { params: { query, max_results: maxResults } }),
  saveResearch: (researchData, tags) => 
    api.post('/api/v1/research/save', researchData, { params: { tags } }),
  getSavedResearch: (limit = 10, offset = 0) => 
    api.get('/api/v1/research/saved', { params: { limit, offset } }),
  exportResearch: (exportData) => api.post('/api/v1/research/export', exportData),
  getSubscription: () => api.get('/api/v1/research/subscription'),
  getTrendingTopics: (limit = 10) => 
    api.get('/api/v1/research/trending', { params: { limit } }),
  getAnalytics: (days = 30) => 
    api.get('/api/v1/research/analytics', { params: { days } }),
};

// Chat API (original endpoints)
export const chatAPI = {
  chat: (message) => api.get('/api/v1/chat/chat', { params: { message } }),
  websearch: (query) => api.get('/api/v1/chat/websearch', { params: { query } }),
  summary: (data) => api.post('/api/v1/chat/celery/summary', data),
};

export default api; 