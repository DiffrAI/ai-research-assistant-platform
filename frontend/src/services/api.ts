import axios, { AxiosResponse } from 'axios';
import type { 
  LoginCredentials, 
  RegisterData, 
  User, 
  ResearchQuery, 
  ApiResponse 
} from '../types';

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
  register: (userData: RegisterData): Promise<AxiosResponse<ApiResponse<User>>> => 
    api.post('/api/v1/auth/register', userData),
  login: (credentials: LoginCredentials): Promise<AxiosResponse<ApiResponse<any>>> => 
    api.post('/api/v1/auth/login', credentials),
  getCurrentUser: (): Promise<AxiosResponse<ApiResponse<User>>> => 
    api.get('/api/v1/auth/me'),
  getSubscription: (): Promise<AxiosResponse<ApiResponse<any>>> => 
    api.get('/api/v1/auth/subscription'),
  logout: (): Promise<AxiosResponse<ApiResponse<any>>> => 
    api.post('/api/v1/auth/logout'),
  refreshToken: (): Promise<AxiosResponse<ApiResponse<any>>> => 
    api.post('/api/v1/auth/refresh'),
};

// Payment API
export const paymentAPI = {
  getPlans: (): Promise<AxiosResponse<ApiResponse<any>>> => 
    api.get('/api/v1/payment/plans'),
  createCheckoutSession: (plan: string, successUrl: string, cancelUrl: string): Promise<AxiosResponse<ApiResponse<any>>> =>
    api.post('/api/v1/payment/checkout', {
      plan,
      success_url: successUrl,
      cancel_url: cancelUrl,
    }),
  createPortalSession: (returnUrl: string): Promise<AxiosResponse<ApiResponse<any>>> =>
    api.post('/api/v1/payment/portal', {
      return_url: returnUrl,
    }),
  getSubscription: (): Promise<AxiosResponse<ApiResponse<any>>> => 
    api.get('/api/v1/payment/subscription'),
};

// Research API
export const researchAPI = {
  conductResearch: (researchData: ResearchQuery): Promise<AxiosResponse<ApiResponse<any>>> => 
    api.post('/api/v1/research', researchData),
  streamResearch: (query: string, maxResults: number = 10): Promise<AxiosResponse<ApiResponse<any>>> =>
    api.get('/api/v1/research/stream', {
      params: { query, max_results: maxResults },
    }),
  saveResearch: (researchData: any, tags: string[]): Promise<AxiosResponse<ApiResponse<any>>> =>
    api.post('/api/v1/research/save', researchData, { params: { tags } }),
  getSavedResearch: (limit: number = 10, offset: number = 0): Promise<AxiosResponse<ApiResponse<any>>> =>
    api.get('/api/v1/research/saved', { params: { limit, offset } }),
  exportResearch: (exportData: any): Promise<AxiosResponse<any>> =>
    api.post('/api/v1/research/export', exportData),
  getSubscription: (): Promise<AxiosResponse<ApiResponse<any>>> => 
    api.get('/api/v1/research/subscription'),
  getTrendingTopics: (limit: number = 10): Promise<AxiosResponse<ApiResponse<any>>> =>
    api.get('/api/v1/research/trending', { params: { limit } }),
  getAnalytics: (days: number = 30): Promise<AxiosResponse<ApiResponse<any>>> =>
    api.get('/api/v1/research/analytics', { params: { days } }),
};

// Chat API (aligned endpoints)
export const chatAPI = {
  chat: (message: string, sleep: number = 1.0, number: number = 10): Promise<AxiosResponse<ApiResponse<any>>> => 
    api.get('/api/v1/chat/stream', { params: { message, sleep, number } }),
  websearch: (query: string): Promise<AxiosResponse<ApiResponse<any>>> =>
    api.get('/api/v1/chat/websearch', { params: { query } }),
  summary: (data: any): Promise<AxiosResponse<ApiResponse<any>>> => 
    api.post('/api/v1/chat/summary', data),
};

export default api;
