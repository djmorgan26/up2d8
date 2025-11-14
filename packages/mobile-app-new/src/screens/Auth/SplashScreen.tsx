/**
 * Splash Screen
 * Loading screen during auth initialization
 */

import React from 'react';
import {View, Text, StyleSheet, ActivityIndicator} from 'react-native';
import {useTheme} from '@context/ThemeContext';
import {Newspaper} from 'lucide-react-native';
import LinearGradient from 'react-native-linear-gradient';

export default function SplashScreen() {
  const {theme} = useTheme();

  return (
    <View style={[styles.container, {backgroundColor: theme.colors.background}]}>
      <View style={styles.content}>
        {/* Logo */}
        <LinearGradient
          colors={[theme.colors.primary, theme.colors.accent]}
          start={{x: 0, y: 0}}
          end={{x: 1, y: 1}}
          style={[styles.logoContainer, {borderRadius: theme.borderRadius.xl}]}>
          <Newspaper size={48} color="#FFFFFF" />
        </LinearGradient>

        {/* App Name */}
        <Text
          style={[
            styles.appName,
            {
              color: theme.colors.textPrimary,
              fontSize: theme.typography.fontSize['3xl'],
              fontWeight: theme.typography.fontWeight.bold,
            },
          ]}>
          UP2D8
        </Text>

        {/* Tagline */}
        <Text
          style={[
            styles.tagline,
            {
              color: theme.colors.textSecondary,
              fontSize: theme.typography.fontSize.base,
            },
          ]}>
          Your personalized news digest
        </Text>

        {/* Loading Indicator */}
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={theme.colors.primary} />
          <Text
            style={[
              styles.loadingText,
              {
                color: theme.colors.textSecondary,
                fontSize: theme.typography.fontSize.sm,
              },
            ]}>
            Loading...
          </Text>
        </View>
      </View>

      {/* Version */}
      <Text
        style={[
          styles.version,
          {
            color: theme.colors.textSecondary,
            fontSize: theme.typography.fontSize.xs,
          },
        ]}>
        Version 1.0.0
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  content: {
    alignItems: 'center',
  },
  logoContainer: {
    width: 100,
    height: 100,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24,
  },
  appName: {
    marginBottom: 8,
  },
  tagline: {
    textAlign: 'center',
    marginBottom: 48,
  },
  loadingContainer: {
    alignItems: 'center',
    gap: 12,
  },
  loadingText: {},
  version: {
    position: 'absolute',
    bottom: 40,
  },
});
