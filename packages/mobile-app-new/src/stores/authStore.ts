/**
 * Auth Store
 * Zustand store for authentication state and user management
 * Supports both basic auth and MSAL (Entra ID) tokens
 */

import {create} from 'zustand';
import {persist, createJSONStorage} from 'zustand/middleware';
import * as SecureStore from 'expo-secure-store';
import {User} from '@up2d8/shared-types';

// Secure storage wrapper for tokens
const secureStorage = {
  getItem: async (key: string): Promise<string | null> => {
    try {
      return await SecureStore.getItemAsync(key);
    } catch (error) {
      console.error(`Error getting ${key}:`, error);
      return null;
    }
  },
  setItem: async (key: string, value: string): Promise<void> => {
    try {
      await SecureStore.setItemAsync(key, value);
    } catch (error) {
      console.error(`Error setting ${key}:`, error);
    }
  },
  removeItem: async (key: string): Promise<void> => {
    try {
      await SecureStore.deleteItemAsync(key);
    } catch (error) {
      console.error(`Error removing ${key}:`, error);
    }
  },
};

export interface AuthState {
  // State
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Auth type (basic or msal)
  authType: 'basic' | 'msal' | null;

  // Actions
  setUser: (user: User) => void;
  setTokens: (accessToken: string, refreshToken?: string, authType?: 'basic' | 'msal') => Promise<void>;
  clearAuth: () => Promise<void>;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshAccessToken: () => Promise<boolean>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      authType: null,

      // Set user
      setUser: (user) =>
        set({
          user,
          isAuthenticated: true,
          error: null,
        }),

      // Set tokens (stored securely)
      setTokens: async (accessToken, refreshToken, authType = 'basic') => {
        try {
          await secureStorage.setItem('access_token', accessToken);
          if (refreshToken) {
            await secureStorage.setItem('refresh_token', refreshToken);
          }

          set({
            accessToken,
            refreshToken: refreshToken || null,
            authType,
            isAuthenticated: true,
            error: null,
          });
        } catch (error) {
          console.error('Error storing tokens:', error);
          set({error: 'Failed to store authentication tokens'});
        }
      },

      // Clear all auth data
      clearAuth: async () => {
        try {
          await secureStorage.removeItem('access_token');
          await secureStorage.removeItem('refresh_token');

          set({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
            authType: null,
            error: null,
          });
        } catch (error) {
          console.error('Error clearing auth:', error);
        }
      },

      // Set loading state
      setLoading: (loading) =>
        set({isLoading: loading}),

      // Set error
      setError: (error) =>
        set({error}),

      // Login with email/password (basic auth)
      login: async (email: string, password: string) => {
        set({isLoading: true, error: null});

        try {
          // This will be implemented when we add the API call
          // For now, just set error
          set({
            isLoading: false,
            error: 'Login not yet implemented. Use MSAL authentication.',
          });

          // TODO: Implement actual login API call
          // const response = await apiClient.post('/auth/login', {email, password});
          // const {access_token, refresh_token, user} = response.data;
          // await get().setTokens(access_token, refresh_token, 'basic');
          // set({user, isLoading: false});
        } catch (error: any) {
          const errorMessage = error.response?.data?.message || error.message || 'Login failed';
          set({
            isLoading: false,
            error: errorMessage,
            isAuthenticated: false,
          });
          throw error;
        }
      },

      // Logout
      logout: async () => {
        set({isLoading: true});

        try {
          // Clear local auth state
          await get().clearAuth();

          set({isLoading: false});
        } catch (error) {
          console.error('Logout error:', error);
          set({isLoading: false});
        }
      },

      // Refresh access token
      refreshAccessToken: async () => {
        const {refreshToken, authType} = get();

        if (!refreshToken) {
          return false;
        }

        try {
          // For MSAL, handle token refresh differently
          if (authType === 'msal') {
            // MSAL will handle this automatically
            return true;
          }

          // For basic auth, call refresh endpoint
          // TODO: Implement actual refresh API call
          // const response = await apiClient.post('/auth/refresh', {refresh_token: refreshToken});
          // const {access_token} = response.data;
          // await get().setTokens(access_token, refreshToken, authType);
          // return true;

          return false;
        } catch (error) {
          console.error('Token refresh failed:', error);
          await get().clearAuth();
          return false;
        }
      },
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => ({
        // Only persist user and auth type, NOT tokens (those go in SecureStore)
        getItem: async (name) => {
          const value = await secureStorage.getItem(name);
          return value;
        },
        setItem: async (name, value) => {
          await secureStorage.setItem(name, value);
        },
        removeItem: async (name) => {
          await secureStorage.removeItem(name);
        },
      })),
      partialize: (state) => ({
        user: state.user,
        authType: state.authType,
        // Don't persist tokens here - they're in SecureStore
      }),
    }
  )
);

// Helper to get access token from secure storage
export const getAccessToken = async (): Promise<string | null> => {
  return await secureStorage.getItem('access_token');
};

// Helper to get refresh token from secure storage
export const getRefreshToken = async (): Promise<string | null> => {
  return await secureStorage.getItem('refresh_token');
};
