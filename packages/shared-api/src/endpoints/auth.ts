/**
 * Authentication API endpoints
 */
import type { ApiResponse } from '@up2d8/shared-types';
import { getApiClient } from '../client';

/**
 * Handle login (post-MSAL authentication)
 * This endpoint is called after successful Azure MSAL authentication
 * to sync user data with backend
 */
export async function handleLogin(userProfile: any) {
  const client = getApiClient();
  return client.post<ApiResponse<any>>('/auth/login', userProfile);
}

/**
 * Handle logout
 */
export async function handleLogout() {
  const client = getApiClient();
  return client.post<ApiResponse<void>>('/auth/logout');
}

/**
 * Refresh token
 */
export async function refreshToken(refreshToken: string) {
  const client = getApiClient();
  return client.post<ApiResponse<{ access_token: string; refresh_token: string }>>('/auth/refresh', {
    refresh_token: refreshToken,
  });
}
