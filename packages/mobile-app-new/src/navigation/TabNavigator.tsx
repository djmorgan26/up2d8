/**
 * Bottom Tab Navigator
 * Main navigation with glassmorphism tab bar and stack navigators
 */

import React from 'react';
import {createBottomTabNavigator} from '@react-navigation/bottom-tabs';
import {Home, Rss, MessageSquare, Settings} from 'lucide-react-native';
import {useTheme} from '@context/ThemeContext';

// Stack Navigators
import {HomeStack, FeedsStack, ChatStack, SettingsStack} from './stacks';

// Custom tab bar
import {GlassTabBar} from './GlassTabBar';
import type {TabParamList} from './types';

const Tab = createBottomTabNavigator<TabParamList>();

export function TabNavigator() {
  const {theme} = useTheme();

  return (
    <Tab.Navigator
      tabBar={props => <GlassTabBar {...props} />}
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: theme.colors.primary,
        tabBarInactiveTintColor: theme.colors.textSecondary,
      }}>
      <Tab.Screen
        name="Dashboard"
        component={HomeStack}
        options={{
          tabBarIcon: ({color, size}) => <Home size={size} color={color} />,
          tabBarLabel: 'Home',
        }}
      />
      <Tab.Screen
        name="Feeds"
        component={FeedsStack}
        options={{
          tabBarIcon: ({color, size}) => <Rss size={size} color={color} />,
          tabBarLabel: 'Feeds',
        }}
      />
      <Tab.Screen
        name="Chat"
        component={ChatStack}
        options={{
          tabBarIcon: ({color, size}) => (
            <MessageSquare size={size} color={color} />
          ),
          tabBarLabel: 'Chat',
        }}
      />
      <Tab.Screen
        name="Settings"
        component={SettingsStack}
        options={{
          tabBarIcon: ({color, size}) => <Settings size={size} color={color} />,
          tabBarLabel: 'Settings',
        }}
      />
    </Tab.Navigator>
  );
}
