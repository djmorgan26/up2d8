import { ApiError } from '../types';

// Configuration
// TODO: Replace with your actual backend URL
// Dev: Use your local backend or ngrok tunnel for testing on physical device
// Prod: Use your deployed Azure/cloud backend URL
const API_BASE_URL = __DEV__
  ? 'http://localhost:8000'  // Local development backend
  : 'https://your-backend.azurewebsites.net';  // Production backend URL

// You can override this by setting a custom URL
let customApiUrl: string | null = null;
let useMockData = false;

export const setApiBaseUrl = (url: string) => {
  customApiUrl = url;
};

export const getApiBaseUrl = (): string => {
  return customApiUrl || API_BASE_URL;
};

export const setUseMockData = (enabled: boolean) => {
  useMockData = enabled;
  console.log(`[API] Mock data ${enabled ? 'enabled' : 'disabled'}`);
};

export const isUsingMockData = (): boolean => {
  return useMockData;
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
   * Core request method with error handling and offline fallback
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
        // Add timeout for faster offline detection
        signal: AbortSignal.timeout(10000), // 10 second timeout
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

      // Backend is online, disable mock data
      if (useMockData) {
        setUseMockData(false);
      }

      return data as T;

    } catch (error) {
      // Handle network errors and timeouts - backend appears offline
      if (error instanceof TypeError || error.name === 'AbortError' || error.name === 'TimeoutError') {
        console.warn('[API] Backend appears offline, enabling mock data mode');

        // Enable mock data for future requests
        if (!useMockData) {
          setUseMockData(true);
        }

        // Re-throw with offline indicator
        const apiError: ApiError = {
          message: 'Backend offline - using demo data',
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
