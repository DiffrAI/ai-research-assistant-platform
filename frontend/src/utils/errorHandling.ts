/**
 * Utility functions for handling API errors consistently across the frontend
 */

interface APIError {
  data: any;
  message: string;
  success: boolean;
  status_code: number;
  endpoint?: string;
  errors?: Array<{
    field: string;
    message: string;
    type: string;
    input?: any;
  }>;
  suggested_endpoint?: string;
  available_endpoints?: string[];
}

interface ErrorResponse {
  response?: {
    data?: APIError;
    status?: number;
  };
  message?: string;
}

/**
 * Extract user-friendly error message from API error response
 */
export function getErrorMessage(error: ErrorResponse): string {
  // Check if it's our standardized API error format
  if (error.response?.data?.message) {
    return error.response.data.message;
  }

  // Handle validation errors with detailed field information
  if (error.response?.data?.errors && Array.isArray(error.response.data.errors)) {
    const fieldErrors = error.response.data.errors
      .map(err => err.message)
      .join(', ');
    return `Validation failed: ${fieldErrors}`;
  }

  // Handle different HTTP status codes
  if (error.response?.status) {
    switch (error.response.status) {
      case 400:
        return 'Bad request. Please check your input and try again.';
      case 401:
        return 'Authentication required. Please log in again.';
      case 403:
        return 'Access denied. You don\'t have permission for this action.';
      case 404:
        return 'Resource not found. The requested endpoint may not exist.';
      case 422:
        return 'Invalid input. Please check your data and try again.';
      case 429:
        return 'Too many requests. Please wait a moment before trying again.';
      case 500:
        return 'Server error. Please try again later.';
      case 503:
        return 'Service temporarily unavailable. Please try again later.';
      default:
        return `Request failed with status ${error.response.status}`;
    }
  }

  // Fallback to generic error message
  return error.message || 'An unexpected error occurred. Please try again.';
}

/**
 * Extract validation errors for form field highlighting
 */
export function getValidationErrors(error: ErrorResponse): Record<string, string> {
  const fieldErrors: Record<string, string> = {};

  if (error.response?.data?.errors && Array.isArray(error.response.data.errors)) {
    error.response.data.errors.forEach(err => {
      // Convert nested field names (e.g., "body -> email") to simple field names
      const fieldName = err.field.split(' -> ').pop() || err.field;
      fieldErrors[fieldName] = err.message;
    });
  }

  return fieldErrors;
}

/**
 * Check if error is an authentication error
 */
export function isAuthError(error: ErrorResponse): boolean {
  if (!error.response) return false;
  
  return error.response.status === 401 || 
         (error.response.data?.message?.toLowerCase().includes('authentication') ?? false) ||
         (error.response.data?.message?.toLowerCase().includes('token') ?? false);
}

/**
 * Check if error is a validation error
 */
export function isValidationError(error: ErrorResponse): boolean {
  if (!error.response) return false;
  
  return error.response.status === 422 || 
         (error.response.data?.errors && Array.isArray(error.response.data.errors)) || false;
}

/**
 * Check if error is a rate limit error
 */
export function isRateLimitError(error: ErrorResponse): boolean {
  return error.response?.status === 429 || false;
}

/**
 * Get suggested endpoint from 404 error response
 */
export function getSuggestedEndpoint(error: ErrorResponse): string | null {
  if (error.response?.status === 404 && error.response?.data?.suggested_endpoint) {
    return error.response.data.suggested_endpoint;
  }
  return null;
}

/**
 * Get available endpoints from 404 error response
 */
export function getAvailableEndpoints(error: ErrorResponse): string[] {
  if (error.response?.status === 404 && error.response?.data?.available_endpoints) {
    return error.response.data.available_endpoints;
  }
  return [];
}

/**
 * Handle API errors with consistent logging and user feedback
 */
export function handleAPIError(error: ErrorResponse, context?: string): {
  message: string;
  isAuthError: boolean;
  validationErrors: Record<string, string>;
  suggestedEndpoint: string | null;
} {
  const message = getErrorMessage(error);
  const validationErrors = getValidationErrors(error);
  const suggestedEndpoint = getSuggestedEndpoint(error);
  const authError = isAuthError(error);

  // Log error for debugging (in development)
  if (process.env.NODE_ENV === 'development') {
    console.error(`API Error${context ? ` in ${context}` : ''}:`, {
      message,
      status: error.response?.status,
      endpoint: error.response?.data?.endpoint,
      validationErrors,
      suggestedEndpoint,
      originalError: error
    });
  }

  return {
    message,
    isAuthError: authError,
    validationErrors,
    suggestedEndpoint
  };
}