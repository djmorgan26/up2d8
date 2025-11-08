import { ApiError } from '../types';

// Configuration
// In production, this should be loaded from environment variables
// For now, we'll use a placeholder that can be configured later
const API_BASE_URL = __DEV__
  ? 'http://localhost:8000'  // Local development
  : 'https://your-backend.azurewebsites.net';  // Production (replace with actual URL)

// You can override this by setting a custom URL
let customApiUrl: string | null = null;

export const setApiBaseUrl = (url: string) => {
  customApiUrl = url;
};

export const getApiBaseUrl = (): string => {
  return customApiUrl || API_BASE_URL;
};

/**
 * Base API client with error handling
 */
class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = getApiBaseUrl();
  }

  /**
   * Make a GET request
   */
  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'GET',
    });
  }

  /**
   * Make a POST request
   */
  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  /**
   * Make a PUT request
   */
  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  /**
   * Make a DELETE request
   */
  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'DELETE',
    });
  }

  /**
   * Core request method with error handling
   */
  private async request<T>(endpoint: string, options: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    try {
      console.log(`[API] ${options.method} ${url}`);

      const response = await fetch(url, {
        ...options,
        headers: {
          ...options.headers,
        },
      });

      // Try to parse JSON response
      let data: any;
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        data = await response.text();
      }

      // Handle non-OK responses
      if (!response.ok) {
        const errorMessage = data?.message || data?.detail || `Request failed with status ${response.status}`;
        console.error(`[API Error] ${options.method} ${url}:`, errorMessage);

        const error: ApiError = {
          message: errorMessage,
          status: response.status,
        };
        throw error;
      }

      console.log(`[API Success] ${options.method} ${url}`);
      return data as T;

    } catch (error) {
      // Handle network errors
      if (error instanceof TypeError) {
        console.error('[API Network Error]:', error.message);
        const apiError: ApiError = {
          message: 'Network error. Please check your connection and try again.',
          status: 0,
        };
        throw apiError;
      }

      // Re-throw API errors
      throw error;
    }
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Export helper function for error messages
export const getErrorMessage = (error: unknown): string => {
  if (typeof error === 'object' && error !== null && 'message' in error) {
    return (error as ApiError).message;
  }
  return 'An unexpected error occurred. Please try again.';
};
