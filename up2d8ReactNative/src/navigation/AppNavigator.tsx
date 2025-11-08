import React, { useEffect, useState } from 'react';
import { ActivityIndicator, View, StyleSheet } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import Icon from 'react-native-vector-icons/Ionicons';

// Screens
import WelcomeScreen from '../screens/WelcomeScreen';
import TopicSelectionScreen from '../screens/TopicSelectionScreen';
import ChatScreen from '../screens/ChatScreen';
import DigestScreen from '../screens/DigestScreen';
import ProfileScreen from '../screens/ProfileScreen';

// Components
import { GlassTabBar } from '../components/GlassTabBar';
import { useTheme } from '../context/ThemeContext';

// Store & Services
import { useUserStore } from '../store/userStore';
import { getUserId } from '../services/storageService';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

// Main Tab Navigator (the app after onboarding)
const MainTabs = () => {
  return (
    <Tab.Navigator
      tabBar={(props) => <GlassTabBar {...props} />}
      screenOptions={{
        headerShown: false,
      }}
    >
      <Tab.Screen
        name="Chat"
        component={ChatScreen}
        options={{
          tabBarIcon: ({ color, size }) => (
            <Icon name="chatbubbles-outline" size={size} color={color} />
          ),
        }}
      />
      <Tab.Screen
        name="Digest"
        component={DigestScreen}
        options={{
          tabBarIcon: ({ color, size }) => (
            <Icon name="newspaper-outline" size={size} color={color} />
          ),
        }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileScreen}
        options={{
          tabBarIcon: ({ color, size }) => (
            <Icon name="person-outline" size={size} color={color} />
          ),
        }}
      />
    </Tab.Navigator>
  );
};

// Root Stack Navigator (handles onboarding flow)
const AppNavigator = () => {
  const { theme } = useTheme();
  const { loadUserFromStorage } = useUserStore();
  const [isLoading, setIsLoading] = useState(true);
  const [hasCompletedOnboarding, setHasCompletedOnboarding] = useState(false);

  useEffect(() => {
    checkOnboardingStatus();
  }, []);

  const checkOnboardingStatus = async () => {
    try {
      // Load user data from storage
      await loadUserFromStorage();

      // Check if user exists
      const userId = await getUserId();
      setHasCompletedOnboarding(!!userId);
    } catch (error) {
      console.error('Error checking onboarding status:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleOnboardingComplete = () => {
    setHasCompletedOnboarding(true);
  };

  if (isLoading) {
    return (
      <View style={[styles.loadingContainer, { backgroundColor: theme.colors.background }]}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
      </View>
    );
  }

  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{
          headerShown: false,
          animation: 'slide_from_right',
        }}
      >
        {!hasCompletedOnboarding ? (
          // Onboarding flow
          <>
            <Stack.Screen name="Welcome">
              {(props) => (
                <WelcomeScreen
                  {...props}
                  onGetStarted={() => props.navigation.navigate('TopicSelection')}
                />
              )}
            </Stack.Screen>
            <Stack.Screen name="TopicSelection">
              {(props) => (
                <TopicSelectionScreen
                  {...props}
                  onComplete={handleOnboardingComplete}
                />
              )}
            </Stack.Screen>
          </>
        ) : (
          // Main app
          <Stack.Screen name="MainTabs" component={MainTabs} />
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
};

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
});

export default AppNavigator;
