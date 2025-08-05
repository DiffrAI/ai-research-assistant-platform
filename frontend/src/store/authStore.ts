import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authAPI } from '../services/api';
import type { User, LoginCredentials, RegisterData } from '../types';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  login: (credentials: LoginCredentials) => Promise<{ success: boolean; error?: string }>;
  register: (userData: RegisterData) => Promise<{ success: boolean; error?: string }>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  clearError: () => void;
}

const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      // State
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Actions
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      setToken: (token) => set({ token }),
      setLoading: (isLoading) => set({ isLoading }),
      setError: (error) => set({ error }),

      // Login
      login: async (credentials: LoginCredentials) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authAPI.login(credentials);
          const { access_token } = response.data.data;

          // Store token in localStorage first
          localStorage.setItem('authToken', access_token);

          // Get user info with the token
          const userResponse = await authAPI.getCurrentUser();
          const user = userResponse.data.data;

          // Store user in localStorage
          localStorage.setItem('user', JSON.stringify(user));

          set({
            user,
            token: access_token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });

          return { success: true };
        } catch (error: any) {
          const errorMessage = error.response?.data?.message || 'Login failed';
          set({ error: errorMessage, isLoading: false });
          return { success: false, error: errorMessage };
        }
      },

      // Register
      register: async (userData: RegisterData) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authAPI.register(userData);
          const user = response.data.data;

          set({
            user,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });

          return { success: true };
        } catch (error: any) {
          const errorMessage =
            error.response?.data?.message || 'Registration failed';
          set({ error: errorMessage, isLoading: false });
          return { success: false, error: errorMessage };
        }
      },

      // Logout
      logout: async () => {
        try {
          await authAPI.logout();
        } catch (error: any) {
          console.error('Logout error:', error);
        } finally {
          // Clear localStorage
          localStorage.removeItem('authToken');
          localStorage.removeItem('user');

          set({
            user: null,
            token: null,
            isAuthenticated: false,
            error: null,
          });
        }
      },

      // Check auth status
      checkAuth: async () => {
        const token = localStorage.getItem('authToken');
        if (!token) {
          set({ isAuthenticated: false });
          return;
        }

        try {
          const response = await authAPI.getCurrentUser();
          const user = response.data.data;

          set({
            user,
            token,
            isAuthenticated: true,
          });
        } catch (error: any) {
          localStorage.removeItem('authToken');
          localStorage.removeItem('user');
          set({
            user: null,
            token: null,
            isAuthenticated: false,
          });
        }
      },

      // Clear error
      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

export default useAuthStore;
