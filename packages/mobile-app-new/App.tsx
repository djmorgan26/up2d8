/**
 * UP2D8 Mobile App
 * Main application component
 */

import React from 'react';
import {SafeAreaProvider} from 'react-native-safe-area-context';
import {GestureHandlerRootView} from 'react-native-gesture-handler';
import {QueryClient, QueryClientProvider} from '@tanstack/react-query';
import {StyleSheet} from 'react-native';

import {ThemeProvider} from '@context/ThemeContext';
import {createApiClient} from '@up2d8/shared-api';
import RootNavigator from '@navigation/RootNavigator';
import Toast from 'react-native-toast-message';

// Initialize API client
const API_BASE_URL = __DEV__
  ? 'http://localhost:8000/api'
  : 'https://api.up2d8.com/api';

createApiClient({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes
    },
  },
});

function App(): React.JSX.Element {
  return (
    <GestureHandlerRootView style={styles.container}>
      <SafeAreaProvider>
        <QueryClientProvider client={queryClient}>
          <ThemeProvider>
            <RootNavigator />
            <Toast />
          </ThemeProvider>
        </QueryClientProvider>
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});

export default App;
