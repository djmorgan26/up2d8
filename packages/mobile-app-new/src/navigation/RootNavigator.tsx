/**
 * Root Navigator
 * Main navigation container for the app
 * Includes auth guard to redirect unauthenticated users
 */

import React, {useEffect, useState} from 'react';
import {NavigationContainer} from '@react-navigation/native';
import {createNativeStackNavigator} from '@react-navigation/native-stack';
import {useTheme} from '@context/ThemeContext';
import {useAuthStore, getAccessToken} from '@stores';
import {setAuthToken, setRefreshTokenFn} from '@up2d8/shared-api';
import {TabNavigator} from './TabNavigator';
import {LoginScreen, SignupScreen, MSALLoginScreen, SplashScreen} from '@screens/Auth';

const Stack = createNativeStackNavigator();

export default function RootNavigator() {
  const {theme} = useTheme();
  const {isAuthenticated, setTokens, refreshAccessToken, clearAuth} = useAuthStore();
  const [isInitializing, setIsInitializing] = useState(true);

  // Set up token refresh function for API client
  useEffect(() => {
    setRefreshTokenFn(async () => {
      try {
        const success = await refreshAccessToken();
        if (success) {
          const token = await getAccessToken();
          return token;
        }
        // Refresh failed - clear auth
        await clearAuth();
        return null;
      } catch (error) {
        console.error('Token refresh failed:', error);
        await clearAuth();
        return null;
      }
    });

    return () => {
      setRefreshTokenFn(null);
    };
  }, [refreshAccessToken, clearAuth]);

  // Load token from secure storage on mount
  useEffect(() => {
    const loadToken = async () => {
      try {
        const token = await getAccessToken();
        if (token) {
          // Set token in API client
          setAuthToken(token);
          // Token exists, user is authenticated
          await setTokens(token);
        }
      } catch (error) {
        console.error('Failed to load token:', error);
      } finally {
        setIsInitializing(false);
      }
    };

    loadToken();
  }, []);

  // Update API client when token changes
  useEffect(() => {
    const updateApiToken = async () => {
      const token = await getAccessToken();
      setAuthToken(token);
    };

    if (isAuthenticated) {
      updateApiToken();
    } else {
      setAuthToken(null);
    }
  }, [isAuthenticated]);

  // Show splash screen during initialization
  if (isInitializing) {
    return <SplashScreen />;
  }

  return (
    <NavigationContainer
      theme={{
        dark: theme.colors.background === '#0F0F14',
        colors: {
          primary: theme.colors.primary,
          background: theme.colors.background,
          card: theme.colors.card,
          text: theme.colors.textPrimary,
          border: theme.colors.border,
          notification: theme.colors.accent,
        },
      }}>
      <Stack.Navigator screenOptions={{headerShown: false}}>
        {isAuthenticated ? (
          // Authenticated: Show main app
          <Stack.Screen name="Main" component={TabNavigator} />
        ) : (
          // Unauthenticated: Show auth screens
          <>
            <Stack.Screen name="Login" component={LoginScreen} />
            <Stack.Screen name="Signup" component={SignupScreen} />
            <Stack.Screen name="MSALLogin" component={MSALLoginScreen} />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
