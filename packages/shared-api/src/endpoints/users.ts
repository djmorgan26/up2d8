/**
 * User API endpoints
 */
import type { User, UserProfile, UserPreferences, ApiResponse } from '@up2d8/shared-types';
import { getApiClient } from '../client';

/**
 * Get user by ID
 */
export async function getUser(userId: string) {
  const client = getApiClient();
  return client.get<ApiResponse<User>>(`/users/${userId}`);
}

/**
 * Update user
 */
export async function updateUser(userId: string, data: Partial<User>) {
  const client = getApiClient();
  return client.put<ApiResponse<User>>(`/users/${userId}`, data);
}

/**
 * Get user profile (user + preferences)
 */
export async function getUserProfile(userId: string) {
  const client = getApiClient();
  return client.get<ApiResponse<UserProfile>>(`/users/${userId}/profile`);
}

/**
 * Get user preferences
 */
export async function getUserPreferences(userId: string) {
  const client = getApiClient();
  return client.get<ApiResponse<UserPreferences>>(`/users/${userId}/preferences`);
}

/**
 * Update user preferences
 */
export async function updateUserPreferences(userId: string, preferences: Partial<UserPreferences>) {
  const client = getApiClient();
  return client.put<ApiResponse<UserPreferences>>(`/users/${userId}/preferences`, preferences);
}
