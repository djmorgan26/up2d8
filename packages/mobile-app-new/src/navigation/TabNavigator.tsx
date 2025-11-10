/**
 * Bottom Tab Navigator
 * Main navigation with glassmorphism tab bar
 */

import React from 'react';
import {createBottomTabNavigator} from '@react-navigation/bottom-tabs';
import {Home, Rss, MessageSquare, Settings} from 'lucide-react-native';
import {useTheme} from '@context/ThemeContext';

// Screens
import DashboardScreen from '@screens/Dashboard';
import FeedsScreen from '@screens/Feeds';
import ChatScreen from '@screens/Chat';
import SettingsScreen from '@screens/Settings';

// Custom tab bar
import {GlassTabBar} from './GlassTabBar';

export type TabParamList = {
  Dashboard: undefined;
  Feeds: undefined;
  Chat: undefined;
  Settings: undefined;
};

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
        component={DashboardScreen}
        options={{
          tabBarIcon: ({color, size}) => <Home size={size} color={color} />,
          tabBarLabel: 'Home',
        }}
      />
      <Tab.Screen
        name="Feeds"
        component={FeedsScreen}
        options={{
          tabBarIcon: ({color, size}) => <Rss size={size} color={color} />,
          tabBarLabel: 'Feeds',
        }}
      />
      <Tab.Screen
        name="Chat"
        component={ChatScreen}
        options={{
          tabBarIcon: ({color, size}) => (
            <MessageSquare size={size} color={color} />
          ),
          tabBarLabel: 'Chat',
        }}
      />
      <Tab.Screen
        name="Settings"
        component={SettingsScreen}
        options={{
          tabBarIcon: ({color, size}) => <Settings size={size} color={color} />,
          tabBarLabel: 'Settings',
        }}
      />
    </Tab.Navigator>
  );
}
