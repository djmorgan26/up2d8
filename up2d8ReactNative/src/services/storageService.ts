import AsyncStorage from '@react-native-async-storage/async-storage';
import { ChatMessage } from '../types';

/**
 * Storage Service - Manages local data persistence using AsyncStorage
 */

// Storage keys
const STORAGE_KEYS = {
  USER_ID: '@up2d8/user_id',
  USER_EMAIL: '@up2d8/user_email',
  USER_TOPICS: '@up2d8/user_topics',
  USER_PREFERENCES: '@up2d8/user_preferences',
  CHAT_HISTORY: '@up2d8/chat_history',
  ONBOARDING_COMPLETED: '@up2d8/onboarding_completed',
  CACHED_ARTICLES: '@up2d8/cached_articles',
  LAST_SYNC: '@up2d8/last_sync',
} as const;

/**
 * User ID storage
 */
export const saveUserId = async (userId: string): Promise<void> => {
  try {
    await AsyncStorage.setItem(STORAGE_KEYS.USER_ID, userId);
    console.log('[Storage] User ID saved');
  } catch (error) {
    console.error('[Storage] Error saving user ID:', error);
    throw error;
  }
};

export const getUserId = async (): Promise<string | null> => {
  try {
    const userId = await AsyncStorage.getItem(STORAGE_KEYS.USER_ID);
    return userId;
  } catch (error) {
    console.error('[Storage] Error getting user ID:', error);
    return null;
  }
};

/**
 * User email storage
 */
export const saveUserEmail = async (email: string): Promise<void> => {
  try {
    await AsyncStorage.setItem(STORAGE_KEYS.USER_EMAIL, email);
    console.log('[Storage] User email saved');
  } catch (error) {
    console.error('[Storage] Error saving user email:', error);
    throw error;
  }
};

export const getUserEmail = async (): Promise<string | null> => {
  try {
    const email = await AsyncStorage.getItem(STORAGE_KEYS.USER_EMAIL);
    return email;
  } catch (error) {
    console.error('[Storage] Error getting user email:', error);
    return null;
  }
};

/**
 * User topics storage
 */
export const saveUserTopics = async (topics: string[]): Promise<void> => {
  try {
    await AsyncStorage.setItem(STORAGE_KEYS.USER_TOPICS, JSON.stringify(topics));
    console.log('[Storage] User topics saved');
  } catch (error) {
    console.error('[Storage] Error saving user topics:', error);
    throw error;
  }
};

export const getUserTopics = async (): Promise<string[]> => {
  try {
    const topics = await AsyncStorage.getItem(STORAGE_KEYS.USER_TOPICS);
    return topics ? JSON.parse(topics) : [];
  } catch (error) {
    console.error('[Storage] Error getting user topics:', error);
    return [];
  }
};

/**
 * User preferences storage
 */
export const saveUserPreferences = async (
  preferences: { newsletter_style?: 'concise' | 'detailed' }
): Promise<void> => {
  try {
    await AsyncStorage.setItem(STORAGE_KEYS.USER_PREFERENCES, JSON.stringify(preferences));
    console.log('[Storage] User preferences saved');
  } catch (error) {
    console.error('[Storage] Error saving user preferences:', error);
    throw error;
  }
};

export const getUserPreferences = async (): Promise<{
  newsletter_style?: 'concise' | 'detailed';
}> => {
  try {
    const preferences = await AsyncStorage.getItem(STORAGE_KEYS.USER_PREFERENCES);
    return preferences ? JSON.parse(preferences) : {};
  } catch (error) {
    console.error('[Storage] Error getting user preferences:', error);
    return {};
  }
};

/**
 * Chat history storage
 */
export const saveChatHistory = async (messages: ChatMessage[]): Promise<void> => {
  try {
    await AsyncStorage.setItem(STORAGE_KEYS.CHAT_HISTORY, JSON.stringify(messages));
    console.log(`[Storage] Chat history saved (${messages.length} messages)`);
  } catch (error) {
    console.error('[Storage] Error saving chat history:', error);
    throw error;
  }
};

export const getChatHistory = async (): Promise<ChatMessage[]> => {
  try {
    const history = await AsyncStorage.getItem(STORAGE_KEYS.CHAT_HISTORY);
    if (!history) return [];

    const messages = JSON.parse(history);
    // Convert timestamp strings back to Date objects
    return messages.map((msg: any) => ({
      ...msg,
      timestamp: new Date(msg.timestamp),
    }));
  } catch (error) {
    console.error('[Storage] Error getting chat history:', error);
    return [];
  }
};

export const clearChatHistory = async (): Promise<void> => {
  try {
    await AsyncStorage.removeItem(STORAGE_KEYS.CHAT_HISTORY);
    console.log('[Storage] Chat history cleared');
  } catch (error) {
    console.error('[Storage] Error clearing chat history:', error);
    throw error;
  }
};

/**
 * Onboarding status
 */
export const setOnboardingCompleted = async (completed: boolean): Promise<void> => {
  try {
    await AsyncStorage.setItem(STORAGE_KEYS.ONBOARDING_COMPLETED, JSON.stringify(completed));
    console.log('[Storage] Onboarding status saved');
  } catch (error) {
    console.error('[Storage] Error saving onboarding status:', error);
    throw error;
  }
};

export const isOnboardingCompleted = async (): Promise<boolean> => {
  try {
    const completed = await AsyncStorage.getItem(STORAGE_KEYS.ONBOARDING_COMPLETED);
    return completed === 'true';
  } catch (error) {
    console.error('[Storage] Error getting onboarding status:', error);
    return false;
  }
};

/**
 * Clear all user data (for logout/unsubscribe)
 */
export const clearAllUserData = async (): Promise<void> => {
  try {
    await AsyncStorage.multiRemove([
      STORAGE_KEYS.USER_ID,
      STORAGE_KEYS.USER_EMAIL,
      STORAGE_KEYS.USER_TOPICS,
      STORAGE_KEYS.USER_PREFERENCES,
      STORAGE_KEYS.CHAT_HISTORY,
      STORAGE_KEYS.ONBOARDING_COMPLETED,
      STORAGE_KEYS.CACHED_ARTICLES,
      STORAGE_KEYS.LAST_SYNC,
    ]);
    console.log('[Storage] All user data cleared');
  } catch (error) {
    console.error('[Storage] Error clearing user data:', error);
    throw error;
  }
};

/**
 * Cache articles for offline viewing
 */
export const cacheArticles = async (articles: any[]): Promise<void> => {
  try {
    await AsyncStorage.setItem(STORAGE_KEYS.CACHED_ARTICLES, JSON.stringify(articles));
    await AsyncStorage.setItem(STORAGE_KEYS.LAST_SYNC, new Date().toISOString());
    console.log(`[Storage] Cached ${articles.length} articles`);
  } catch (error) {
    console.error('[Storage] Error caching articles:', error);
    throw error;
  }
};

export const getCachedArticles = async (): Promise<any[]> => {
  try {
    const articles = await AsyncStorage.getItem(STORAGE_KEYS.CACHED_ARTICLES);
    return articles ? JSON.parse(articles) : [];
  } catch (error) {
    console.error('[Storage] Error getting cached articles:', error);
    return [];
  }
};

export const getLastSyncTime = async (): Promise<Date | null> => {
  try {
    const lastSync = await AsyncStorage.getItem(STORAGE_KEYS.LAST_SYNC);
    return lastSync ? new Date(lastSync) : null;
  } catch (error) {
    console.error('[Storage] Error getting last sync time:', error);
    return null;
  }
};
