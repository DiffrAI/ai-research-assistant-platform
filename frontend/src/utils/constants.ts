// API endpoints
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/api/v1/auth/login',
    REGISTER: '/api/v1/auth/register',
    ME: '/api/v1/auth/me',
    LOGOUT: '/api/v1/auth/logout',
    REFRESH: '/api/v1/auth/refresh',
  },
  RESEARCH: {
    CONDUCT: '/api/v1/research',
    STREAM: '/api/v1/research/stream',
    SAVE: '/api/v1/research/save',
    SAVED: '/api/v1/research/saved',
    EXPORT: '/api/v1/research/export',
    TRENDING: '/api/v1/research/trending',
    ANALYTICS: '/api/v1/research/analytics',
  },
  PAYMENT: {
    PLANS: '/api/v1/payment/plans',
    CHECKOUT: '/api/v1/payment/create-checkout-session',
    PORTAL: '/api/v1/payment/create-portal-session',
    USAGE: '/api/v1/payment/usage',
  },
} as const;

// Local storage keys
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'authToken',
  USER: 'user',
  THEME: 'theme',
  RESEARCH_HISTORY: 'researchHistory',
} as const;

// Query keys for React Query (if we upgrade)
export const QUERY_KEYS = {
  USER: 'user',
  RESEARCH: 'research',
  SAVED_RESEARCH: 'savedResearch',
  TRENDING: 'trending',
  ANALYTICS: 'analytics',
  SUBSCRIPTION: 'subscription',
} as const;

// App configuration
export const APP_CONFIG = {
  MAX_QUERY_LENGTH: 1000,
  MAX_RESULTS_OPTIONS: [5, 10, 15, 20, 25] as const,
  DEFAULT_MAX_RESULTS: 10,
  DEBOUNCE_DELAY: 300,
  TOAST_DURATION: 4000,
} as const;

// Export formats
export const EXPORT_FORMATS = {
  PDF: 'pdf',
  MARKDOWN: 'markdown',
  JSON: 'json',
  CSV: 'csv',
} as const;

// Research result types
export const RESULT_TYPES = {
  WEB: 'web',
  ACADEMIC: 'academic',
  NEWS: 'news',
  SOCIAL: 'social',
} as const;