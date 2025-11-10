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
import type {Article} from '@up2d8/shared-types';

// Stack navigator params for each tab
export type HomeStackParamList = {
  DashboardMain: undefined;
  ArticleDetail: {
    article: Article;
  };
};

export type FeedsStackParamList = {
  FeedsMain: undefined;
  // Future: AddFeed, EditFeed
};

export type ChatStackParamList = {
  ChatMain: undefined;
};

export type SettingsStackParamList = {
  SettingsMain: undefined;
  // Future: Account, Notifications, Privacy
};

// Tab navigator params (now with stack navigators)
export type TabParamList = {
  Dashboard: NavigatorScreenParams<HomeStackParamList>;
  Feeds: NavigatorScreenParams<FeedsStackParamList>;
  Chat: NavigatorScreenParams<ChatStackParamList>;
  Settings: NavigatorScreenParams<SettingsStackParamList>;
};

// Root navigator params
export type RootStackParamList = {
  Main: NavigatorScreenParams<TabParamList>;
  // Future: Onboarding, Auth flows
};

// Navigation props for each screen
export type DashboardScreenProps = CompositeScreenProps<
  NativeStackScreenProps<HomeStackParamList, 'DashboardMain'>,
  BottomTabScreenProps<TabParamList>
>;

export type ArticleDetailScreenProps = CompositeScreenProps<
  NativeStackScreenProps<HomeStackParamList, 'ArticleDetail'>,
  BottomTabScreenProps<TabParamList>
>;

export type FeedsScreenProps = CompositeScreenProps<
  NativeStackScreenProps<FeedsStackParamList, 'FeedsMain'>,
  BottomTabScreenProps<TabParamList>
>;

export type ChatScreenProps = CompositeScreenProps<
  NativeStackScreenProps<ChatStackParamList, 'ChatMain'>,
  BottomTabScreenProps<TabParamList>
>;

export type SettingsScreenProps = CompositeScreenProps<
  NativeStackScreenProps<SettingsStackParamList, 'SettingsMain'>,
  BottomTabScreenProps<TabParamList>
>;

// Type for useNavigation hook
declare global {
  namespace ReactNavigation {
    interface RootParamList extends RootStackParamList {}
  }
}
