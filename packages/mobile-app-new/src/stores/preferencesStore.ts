/**
 * User Preferences Store
 * Zustand store for user preferences and settings
 */

import {create} from 'zustand';
import {persist, createJSONStorage} from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

export interface UserPreferences {
  // Display preferences
  articlesPerPage: number;
  showImages: boolean;
  compactView: boolean;

  // Notification preferences
  pushNotificationsEnabled: boolean;
  emailNotificationsEnabled: boolean;

  // Content preferences
  selectedTopics: string[];
  blockedSources: string[];

  // Reading preferences
  fontSize: 'small' | 'medium' | 'large';
  readingMode: 'light' | 'dark' | 'system';
}

interface UserPreferencesState {
  preferences: UserPreferences;
  setPreference: <K extends keyof UserPreferences>(
    key: K,
    value: UserPreferences[K]
  ) => void;
  setPreferences: (preferences: Partial<UserPreferences>) => void;
  resetPreferences: () => void;
}

const defaultPreferences: UserPreferences = {
  articlesPerPage: 20,
  showImages: true,
  compactView: false,
  pushNotificationsEnabled: true,
  emailNotificationsEnabled: false,
  selectedTopics: [],
  blockedSources: [],
  fontSize: 'medium',
  readingMode: 'system',
};

export const usePreferencesStore = create<UserPreferencesState>()(
  persist(
    (set) => ({
      preferences: defaultPreferences,

      setPreference: (key, value) =>
        set((state) => ({
          preferences: {
            ...state.preferences,
            [key]: value,
          },
        })),

      setPreferences: (newPreferences) =>
        set((state) => ({
          preferences: {
            ...state.preferences,
            ...newPreferences,
          },
        })),

      resetPreferences: () =>
        set({
          preferences: defaultPreferences,
        }),
    }),
    {
      name: 'user-preferences-storage',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);
