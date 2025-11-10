/**
 * Root Navigator
 * Main navigation container for the app
 * Phase 3: Tab navigation with all main screens
 */

import React from 'react';
import {NavigationContainer} from '@react-navigation/native';
import {useTheme} from '@context/ThemeContext';
import {TabNavigator} from './TabNavigator';

export default function RootNavigator() {
  const {theme} = useTheme();

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
      <TabNavigator />
    </NavigationContainer>
  );
}
