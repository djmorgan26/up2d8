import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import ChatPage from './src/screens/ChatPage';
import BrowsePage from './src/screens/BrowsePage';
import SubscribePage from './src/screens/SubscribePage';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { ThemeProvider, useTheme } from './src/context/ThemeContext';
import { Text } from 'react-native';

const Tab = createBottomTabNavigator();

const AppContent = () => {
  const { theme } = useTheme();

  return (
    <NavigationContainer>
      <Tab.Navigator
        screenOptions={{
          tabBarActiveTintColor: theme.colors.primary,
          tabBarInactiveTintColor: theme.colors.textSecondary,
          tabBarStyle: {
            backgroundColor: theme.colors.surface,
            borderTopColor: theme.colors.textSecondary,
          },
          headerStyle: {
            backgroundColor: theme.colors.surface,
          },
          headerTitleStyle: {
            color: theme.colors.textPrimary,
          },
        }}
      >
        <Tab.Screen
          name="Chat"
          component={ChatPage}
          options={{
            tabBarIcon: ({ color, size }) => (
              <Text style={{ color, fontSize: size }}>💬</Text>
            ),
          }}
        />
        <Tab.Screen
          name="Browse"
          component={BrowsePage}
          options={{
            tabBarIcon: ({ color, size }) => (
              <Text style={{ color, fontSize: size }}>📚</Text>
            ),
          }}
        />
        <Tab.Screen
          name="Subscribe"
          component={SubscribePage}
          options={{
            tabBarIcon: ({ color, size }) => (
              <Text style={{ color, fontSize: size }}>✨</Text>
            ),
          }}
        />
      </Tab.Navigator>
    </NavigationContainer>
  );
};

const App = () => {
  return (
    <SafeAreaProvider>
      <ThemeProvider>
        <AppContent />
      </ThemeProvider>
    </SafeAreaProvider>
  );
};

export default App;


export default App;