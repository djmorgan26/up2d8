import { create } from 'zustand';
import { User, UserPreferences } from '../types';
import {
  getUser,
  updateUserTopics,
  updateUserPreferences,
  updateUser,
  deleteUser,
} from '../services/userService';
import {
  saveUserId,
  saveUserEmail,
  saveUserTopics,
  saveUserPreferences,
  clearAllUserData,
  getUserId,
  getUserEmail,
  getUserTopics,
  getUserPreferences as getStoredUserPreferences,
} from '../services/storageService';

interface UserState {
  // State
  userId: string | null;
  email: string | null;
  topics: string[];
  preferences: UserPreferences;
  isLoading: boolean;
  error: string | null;

  // Actions
  setUser: (user: User) => Promise<void>;
  loadUserFromStorage: () => Promise<void>;
  fetchUser: (userId: string) => Promise<void>;
  updateTopics: (topics: string[]) => Promise<void>;
  updatePreferences: (newsletterStyle: 'concise' | 'detailed') => Promise<void>;
  updateUserData: (topics?: string[], newsletterStyle?: 'concise' | 'detailed') => Promise<void>;
  unsubscribe: () => Promise<void>;
  clearUser: () => Promise<void>;
  setError: (error: string | null) => void;
}

export const useUserStore = create<UserState>((set, get) => ({
  // Initial state
  userId: null,
  email: null,
  topics: [],
  preferences: {},
  isLoading: false,
  error: null,

  // Set user data (from API or storage)
  setUser: async (user: User) => {
    set({
      userId: user.user_id,
      email: user.email,
      topics: user.topics,
      preferences: user.preferences || {},
      error: null,
    });

    // Persist to storage
    try {
      await saveUserId(user.user_id);
      await saveUserEmail(user.email);
      await saveUserTopics(user.topics);
      if (user.preferences) {
        await saveUserPreferences(user.preferences);
      }
    } catch (error) {
      console.error('[UserStore] Error saving user to storage:', error);
    }
  },

  // Load user data from AsyncStorage (on app start)
  loadUserFromStorage: async () => {
    set({ isLoading: true, error: null });
    try {
      const userId = await getUserId();
      const email = await getUserEmail();
      const topics = await getUserTopics();
      const preferences = await getStoredUserPreferences();

      if (userId && email) {
        set({
          userId,
          email,
          topics,
          preferences,
          isLoading: false,
        });
      } else {
        set({ isLoading: false });
      }
    } catch (error) {
      console.error('[UserStore] Error loading user from storage:', error);
      set({ isLoading: false, error: 'Failed to load user data' });
    }
  },

  // Fetch user from API
  fetchUser: async (userId: string) => {
    set({ isLoading: true, error: null });
    try {
      const user = await getUser(userId);
      await get().setUser(user);
      set({ isLoading: false });
    } catch (error: any) {
      console.error('[UserStore] Error fetching user:', error);
      set({
        isLoading: false,
        error: error.message || 'Failed to fetch user data',
      });
    }
  },

  // Update user topics
  updateTopics: async (topics: string[]) => {
    const { userId } = get();
    if (!userId) {
      set({ error: 'No user ID found' });
      return;
    }

    set({ isLoading: true, error: null });
    try {
      await updateUserTopics(userId, topics);
      set({ topics, isLoading: false });
      await saveUserTopics(topics);
    } catch (error: any) {
      console.error('[UserStore] Error updating topics:', error);
      set({
        isLoading: false,
        error: error.message || 'Failed to update topics',
      });
      throw error;
    }
  },

  // Update user preferences
  updatePreferences: async (newsletterStyle: 'concise' | 'detailed') => {
    const { userId } = get();
    if (!userId) {
      set({ error: 'No user ID found' });
      return;
    }

    set({ isLoading: true, error: null });
    try {
      await updateUserPreferences(userId, newsletterStyle);
      const newPreferences = { newsletter_style: newsletterStyle };
      set({ preferences: newPreferences, isLoading: false });
      await saveUserPreferences(newPreferences);
    } catch (error: any) {
      console.error('[UserStore] Error updating preferences:', error);
      set({
        isLoading: false,
        error: error.message || 'Failed to update preferences',
      });
      throw error;
    }
  },

  // Update both topics and preferences
  updateUserData: async (topics?: string[], newsletterStyle?: 'concise' | 'detailed') => {
    const { userId } = get();
    if (!userId) {
      set({ error: 'No user ID found' });
      return;
    }

    set({ isLoading: true, error: null });
    try {
      await updateUser(userId, topics, newsletterStyle);

      const updates: Partial<UserState> = { isLoading: false };
      if (topics) {
        updates.topics = topics;
        await saveUserTopics(topics);
      }
      if (newsletterStyle) {
        updates.preferences = { newsletter_style: newsletterStyle };
        await saveUserPreferences(updates.preferences);
      }

      set(updates);
    } catch (error: any) {
      console.error('[UserStore] Error updating user:', error);
      set({
        isLoading: false,
        error: error.message || 'Failed to update user',
      });
      throw error;
    }
  },

  // Unsubscribe (delete user)
  unsubscribe: async () => {
    const { userId } = get();
    if (!userId) {
      set({ error: 'No user ID found' });
      return;
    }

    set({ isLoading: true, error: null });
    try {
      await deleteUser(userId);
      await clearAllUserData();
      set({
        userId: null,
        email: null,
        topics: [],
        preferences: {},
        isLoading: false,
        error: null,
      });
    } catch (error: any) {
      console.error('[UserStore] Error unsubscribing:', error);
      set({
        isLoading: false,
        error: error.message || 'Failed to unsubscribe',
      });
      throw error;
    }
  },

  // Clear user data (local only, no API call)
  clearUser: async () => {
    await clearAllUserData();
    set({
      userId: null,
      email: null,
      topics: [],
      preferences: {},
      error: null,
    });
  },

  // Set error manually
  setError: (error: string | null) => {
    set({ error });
  },
}));
