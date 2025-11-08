import { apiClient, isUsingMockData } from './api';
import {
  User,
  CreateUserRequest,
  CreateUserResponse,
  UpdateUserRequest,
  UpdateUserResponse,
  DeleteUserResponse,
} from '../types';
import { MOCK_USER, simulateNetworkDelay } from './mockData';

/**
 * User Service - Manages user subscriptions and preferences
 */

/**
 * Create a new user subscription
 * @param email - User's email address
 * @param topics - Array of topics user is interested in
 * @returns User ID and confirmation message
 */
export const createUser = async (
  email: string,
  topics: string[]
): Promise<CreateUserResponse> => {
  if (!email || email.trim().length === 0) {
    throw new Error('Email is required');
  }

  if (!topics || topics.length === 0) {
    throw new Error('At least one topic must be selected');
  }

  const request: CreateUserRequest = {
    email: email.trim().toLowerCase(),
    topics,
  };

  try {
    const response = await apiClient.post<CreateUserResponse>('/api/users', request);
    console.log('[UserService] User created:', response);
    return response;
  } catch (error) {
    console.error('[UserService] Error creating user:', error);

    // If backend is offline, return mock response
    if (isUsingMockData()) {
      console.log('[UserService] Using mock user creation');
      await simulateNetworkDelay();
      return {
        message: '[DEMO MODE] Subscription confirmed',
        user_id: MOCK_USER.user_id,
      };
    }

    throw error;
  }
};

/**
 * Get user profile by ID
 * @param userId - User's unique ID
 * @returns User profile with topics and preferences
 */
export const getUser = async (userId: string): Promise<User> => {
  if (!userId) {
    throw new Error('User ID is required');
  }

  try {
    const response = await apiClient.get<User>(`/api/users/${userId}`);
    console.log('[UserService] User fetched:', response);
    return response;
  } catch (error) {
    console.error('[UserService] Error fetching user:', error);

    // If backend is offline, return mock user
    if (isUsingMockData()) {
      console.log('[UserService] Using mock user data');
      await simulateNetworkDelay();
      return MOCK_USER;
    }

    throw error;
  }
};

/**
 * Update user's topics
 * @param userId - User's unique ID
 * @param topics - New array of topics
 * @returns Confirmation message
 */
export const updateUserTopics = async (
  userId: string,
  topics: string[]
): Promise<UpdateUserResponse> => {
  if (!userId) {
    throw new Error('User ID is required');
  }

  if (!topics || topics.length === 0) {
    throw new Error('At least one topic must be selected');
  }

  const request: UpdateUserRequest = {
    topics,
  };

  try {
    const response = await apiClient.put<UpdateUserResponse>(
      `/api/users/${userId}`,
      request
    );
    console.log('[UserService] Topics updated:', response);
    return response;
  } catch (error) {
    console.error('[UserService] Error updating topics:', error);

    // If backend is offline, return mock response
    if (isUsingMockData()) {
      console.log('[UserService] Using mock topics update');
      await simulateNetworkDelay();
      return {
        message: '[DEMO MODE] Preferences updated',
      };
    }

    throw error;
  }
};

/**
 * Update user's newsletter preferences
 * @param userId - User's unique ID
 * @param newsletterStyle - 'concise' or 'detailed'
 * @returns Confirmation message
 */
export const updateUserPreferences = async (
  userId: string,
  newsletterStyle: 'concise' | 'detailed'
): Promise<UpdateUserResponse> => {
  if (!userId) {
    throw new Error('User ID is required');
  }

  const request: UpdateUserRequest = {
    preferences: {
      newsletter_style: newsletterStyle,
    },
  };

  try {
    const response = await apiClient.put<UpdateUserResponse>(
      `/api/users/${userId}`,
      request
    );
    console.log('[UserService] Preferences updated:', response);
    return response;
  } catch (error) {
    console.error('[UserService] Error updating preferences:', error);

    // If backend is offline, return mock response
    if (isUsingMockData()) {
      console.log('[UserService] Using mock preference update');
      await simulateNetworkDelay();
      return {
        message: '[DEMO MODE] Preferences updated',
      };
    }

    throw error;
  }
};

/**
 * Update both topics and preferences
 * @param userId - User's unique ID
 * @param topics - New array of topics (optional)
 * @param newsletterStyle - Newsletter style preference (optional)
 * @returns Confirmation message
 */
export const updateUser = async (
  userId: string,
  topics?: string[],
  newsletterStyle?: 'concise' | 'detailed'
): Promise<UpdateUserResponse> => {
  if (!userId) {
    throw new Error('User ID is required');
  }

  if (!topics && !newsletterStyle) {
    throw new Error('At least one field must be provided for update');
  }

  const request: UpdateUserRequest = {};

  if (topics && topics.length > 0) {
    request.topics = topics;
  }

  if (newsletterStyle) {
    request.preferences = {
      newsletter_style: newsletterStyle,
    };
  }

  try {
    const response = await apiClient.put<UpdateUserResponse>(
      `/api/users/${userId}`,
      request
    );
    console.log('[UserService] User updated:', response);
    return response;
  } catch (error) {
    console.error('[UserService] Error updating user:', error);

    // If backend is offline, return mock response
    if (isUsingMockData()) {
      console.log('[UserService] Using mock user update');
      await simulateNetworkDelay();
      return {
        message: '[DEMO MODE] Preferences updated',
      };
    }

    throw error;
  }
};

/**
 * Delete user (unsubscribe)
 * @param userId - User's unique ID
 * @returns Confirmation message
 */
export const deleteUser = async (userId: string): Promise<DeleteUserResponse> => {
  if (!userId) {
    throw new Error('User ID is required');
  }

  try {
    const response = await apiClient.delete<DeleteUserResponse>(`/api/users/${userId}`);
    console.log('[UserService] User deleted:', response);
    return response;
  } catch (error) {
    console.error('[UserService] Error deleting user:', error);

    // If backend is offline, return mock response
    if (isUsingMockData()) {
      console.log('[UserService] Using mock user deletion');
      await simulateNetworkDelay();
      return {
        message: '[DEMO MODE] User deleted',
      };
    }

    throw error;
  }
};

/**
 * Validate email format
 * @param email - Email to validate
 * @returns True if valid, false otherwise
 */
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};
