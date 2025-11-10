/**
 * Navigation type definitions
 * For type-safe navigation with React Navigation
 */

import type {BottomTabScreenProps} from '@react-navigation/bottom-tabs';
import type {
  CompositeScreenProps,
  NavigatorScreenParams,
} from '@react-navigation/native';
import type {NativeStackScreenProps} from '@react-navigation/native-stack';

// Tab navigator params
export type TabParamList = {
  Dashboard: undefined;
  Feeds: undefined;
  Chat: undefined;
  Settings: undefined;
};

// Root navigator params (for future stack navigators)
export type RootStackParamList = {
  Main: NavigatorScreenParams<TabParamList>;
  // Future: ArticleDetail, FeedDetail, etc.
};

// Navigation props for each screen
export type DashboardScreenProps = CompositeScreenProps<
  BottomTabScreenProps<TabParamList, 'Dashboard'>,
  NativeStackScreenProps<RootStackParamList>
>;

export type FeedsScreenProps = CompositeScreenProps<
  BottomTabScreenProps<TabParamList, 'Feeds'>,
  NativeStackScreenProps<RootStackParamList>
>;

export type ChatScreenProps = CompositeScreenProps<
  BottomTabScreenProps<TabParamList, 'Chat'>,
  NativeStackScreenProps<RootStackParamList>
>;

export type SettingsScreenProps = CompositeScreenProps<
  BottomTabScreenProps<TabParamList, 'Settings'>,
  NativeStackScreenProps<RootStackParamList>
>;

// Type for useNavigation hook
declare global {
  namespace ReactNavigation {
    interface RootParamList extends RootStackParamList {}
  }
}
