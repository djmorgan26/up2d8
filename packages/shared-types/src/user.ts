/**
 * User-related types
 */

export interface User {
  id: string;
  email: string;
  name?: string;
  created_at: string;
  updated_at: string;
}

export interface UserPreferences {
  user_id: string;
  topics: string[];
  notification_enabled: boolean;
  theme?: 'light' | 'dark' | 'system';
  language?: string;
}

export interface UserProfile {
  user: User;
  preferences: UserPreferences;
}
