import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import ChatPage from './src/screens/ChatPage';
import BrowsePage from './src/screens/BrowsePage';
import SubscribePage from './src/screens/SubscribePage';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { ThemeProvider, useTheme } from './src/context/ThemeContext';
import { GlassTabBar } from './src/components/GlassTabBar';
import Icon from 'react-native-vector-icons/Ionicons';

const Tab = createBottomTabNavigator();

const AppContent = () => {
  const { theme } = useTheme();

  return (
    <NavigationContainer>
      <Tab.Navigator
        tabBar={(props) => <GlassTabBar {...props} />}
        screenOptions={{
          headerShown: false,
        }}
      >
        <Tab.Screen
          name="Chat"
          component={ChatPage}
          options={{
            tabBarIcon: ({ color, size }) => (
              <Icon name="chatbubbles-outline" size={size} color={color} />
            ),
          }}
        />
        <Tab.Screen
          name="Browse"
          component={BrowsePage}
          options={{
            tabBarIcon: ({ color, size }) => (
              <Icon name="compass-outline" size={size} color={color} />
            ),
          }}
        />
        <Tab.Screen
          name="Subscribe"
          component={SubscribePage}
          options={{
            tabBarIcon: ({ color, size }) => (
              <Icon name="sparkles-outline" size={size} color={color} />
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