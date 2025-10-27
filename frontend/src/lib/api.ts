import axios from 'axios';
import type { AxiosInstance, AxiosError } from 'axios';
import type {
  AuthResponse,
  LoginCredentials,
  SignupData,
  User,
  Digest,
  Article,
  ChatSession,
} from '../types';

// In production, use the deployed backend URL
// In development, use localhost
const API_URL = import.meta.env.VITE_API_URL || 
  (import.meta.env.PROD 
    ? 'https://up2d8.azurewebsites.net'  // Update this to your actual backend URL
    : 'http://localhost:8000');

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_URL}/api/v1`,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to include auth token
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Add response interceptor to handle token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Try to refresh token
          const refreshToken = localStorage.getItem('refresh_token');
          if (refreshToken) {
            try {
              const response = await axios.post(
                `${API_URL}/api/v1/auth/refresh`,
                { refresh_token: refreshToken }
              );
              const { access_token } = response.data;
              localStorage.setItem('access_token', access_token);

              // Retry original request
              if (error.config) {
                error.config.headers.Authorization = `Bearer ${access_token}`;
                return this.client.request(error.config);
              }
            } catch {
              // Refresh failed, logout
              localStorage.removeItem('access_token');
              localStorage.removeItem('refresh_token');
              window.location.href = '/login';
            }
          }
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await this.client.post('/auth/login', credentials);
    return response.data;
  }

  async signup(data: SignupData): Promise<AuthResponse> {
    const response = await this.client.post('/auth/signup', data);
    return response.data;
  }

  async logout(): Promise<void> {
    const token = localStorage.getItem('access_token');
    if (token) {
      await this.client.post('/auth/logout');
    }
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get('/auth/me');
    return response.data;
  }

  // Digest endpoints
  async getDigests(limit = 10, offset = 0): Promise<Digest[]> {
    const response = await this.client.get('/digests', {
      params: { limit, offset },
    });
    return response.data;
  }

  async getDigest(digestId: string): Promise<Digest> {
    const response = await this.client.get(`/digests/${digestId}`);
    return response.data;
  }

  // Article endpoints
  async getArticles(limit = 20, offset = 0): Promise<Article[]> {
    const response = await this.client.get('/articles', {
      params: { limit, offset },
    });
    return response.data;
  }

  async getArticle(articleId: string): Promise<Article> {
    const response = await this.client.get(`/articles/${articleId}`);
    return response.data;
  }

  // Chat endpoints
  async createChatSession(digestId?: string): Promise<ChatSession> {
    const response = await this.client.post('/chat/sessions', {
      digest_id: digestId,
    });
    return response.data;
  }

  async getChatHistory(sessionId: string) {
    const response = await this.client.get(`/chat/sessions/${sessionId}/messages`);
    return response.data;
  }

  getWebSocketUrl(sessionId: string): string {
    const token = localStorage.getItem('access_token');
    const wsUrl = API_URL.replace('http', 'ws');
    return `${wsUrl}/api/v1/chat/ws/${sessionId}?token=${token}`;
  }

  // Preferences
  async updatePreferences(preferences: any): Promise<void> {
    await this.client.put('/users/me/preferences', preferences);
  }

  async getPreferences(): Promise<any> {
    const response = await this.client.get('/users/me/preferences');
    return response.data;
  }
}

export const api = new ApiClient();
