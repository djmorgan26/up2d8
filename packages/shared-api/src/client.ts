/**
 * Base API client configuration
 */
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

export interface ApiClientConfig {
  baseURL: string;
  timeout?: number;
  headers?: Record<string, string>;
}

export class ApiClient {
  private client: AxiosInstance;
  private authToken: string | null = null;
  private refreshTokenFn: (() => Promise<string | null>) | null = null;
  private isRefreshing = false;
  private failedQueue: Array<{resolve: (value?: any) => void; reject: (reason?: any) => void}> = [];

  constructor(config: ApiClientConfig) {
    this.client = axios.create({
      baseURL: config.baseURL,
      timeout: config.timeout || 30000,
      headers: {
        'Content-Type': 'application/json',
        ...config.headers,
      },
    });

    // Request interceptor for auth token
    this.client.interceptors.request.use(
      (config) => {
        if (this.authToken) {
          config.headers.Authorization = `Bearer ${this.authToken}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling and token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        // Handle 401 Unauthorized - token expired
        if (error.response?.status === 401 && !originalRequest._retry) {
          if (this.isRefreshing) {
            // Queue this request while refresh is in progress
            return new Promise((resolve, reject) => {
              this.failedQueue.push({resolve, reject});
            })
              .then((token) => {
                originalRequest.headers.Authorization = `Bearer ${token}`;
                return this.client(originalRequest);
              })
              .catch((err) => Promise.reject(err));
          }

          originalRequest._retry = true;
          this.isRefreshing = true;

          if (this.refreshTokenFn) {
            try {
              const newToken = await this.refreshTokenFn();

              if (newToken) {
                this.authToken = newToken;

                // Retry all queued requests
                this.failedQueue.forEach((prom) => {
                  prom.resolve(newToken);
                });
                this.failedQueue = [];

                originalRequest.headers.Authorization = `Bearer ${newToken}`;
                return this.client(originalRequest);
              }
            } catch (refreshError) {
              // Refresh failed - reject all queued requests
              this.failedQueue.forEach((prom) => {
                prom.reject(refreshError);
              });
              this.failedQueue = [];
              return Promise.reject(refreshError);
            } finally {
              this.isRefreshing = false;
            }
          }
        }

        // Handle other errors
        if (error.response) {
          // Server responded with error status
          const apiError = {
            status: error.response.status,
            message: error.response.data?.message || error.message,
            error: error.response.data?.error || 'API Error',
            details: error.response.data,
          };
          return Promise.reject(apiError);
        } else if (error.request) {
          // Request made but no response received
          return Promise.reject({
            status: 0,
            message: 'Network error - please check your connection',
            error: 'NetworkError',
          });
        } else {
          // Something else happened
          return Promise.reject({
            status: 0,
            message: error.message,
            error: 'UnknownError',
          });
        }
      }
    );
  }

  /**
   * Set authentication token
   */
  setAuthToken(token: string | null) {
    this.authToken = token;
  }

  /**
   * Get authentication token
   */
  getAuthToken(): string | null {
    return this.authToken;
  }

  /**
   * Set refresh token function
   * This function will be called when a 401 error occurs
   */
  setRefreshTokenFn(fn: (() => Promise<string | null>) | null) {
    this.refreshTokenFn = fn;
  }

  /**
   * Generic GET request
   */
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.get<T>(url, config);
  }

  /**
   * Generic POST request
   */
  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.post<T>(url, data, config);
  }

  /**
   * Generic PUT request
   */
  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.put<T>(url, data, config);
  }

  /**
   * Generic DELETE request
   */
  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.delete<T>(url, config);
  }

  /**
   * Generic PATCH request
   */
  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.client.patch<T>(url, data, config);
  }
}

/**
 * Default API client instance (can be configured)
 */
let defaultClient: ApiClient | null = null;

export function createApiClient(config: ApiClientConfig): ApiClient {
  defaultClient = new ApiClient(config);
  return defaultClient;
}

export function getApiClient(): ApiClient {
  if (!defaultClient) {
    throw new Error('API client not initialized. Call createApiClient() first.');
  }
  return defaultClient;
}

/**
 * Helper to set auth token on default client
 */
export function setAuthToken(token: string | null): void {
  if (defaultClient) {
    defaultClient.setAuthToken(token);
  }
}

/**
 * Helper to get auth token from default client
 */
export function getAuthToken(): string | null {
  if (defaultClient) {
    return defaultClient.getAuthToken();
  }
  return null;
}

/**
 * Helper to set refresh token function on default client
 */
export function setRefreshTokenFn(fn: (() => Promise<string | null>) | null): void {
  if (defaultClient) {
    defaultClient.setRefreshTokenFn(fn);
  }
}
