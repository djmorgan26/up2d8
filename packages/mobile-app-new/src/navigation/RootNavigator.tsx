/**
 * Root Navigator
 * Main navigation container for the app
 * Currently a placeholder - will be expanded in Phase 4
 */

import React from 'react';
import {NavigationContainer} from '@react-navigation/native';
import {createNativeStackNavigator} from '@react-navigation/native-stack';
import {View, Text, StyleSheet} from 'react-native';
import {useTheme} from '@context/ThemeContext';

const Stack = createNativeStackNavigator();

// Placeholder screen
function PlaceholderScreen() {
  const {theme, isDark} = useTheme();

  return (
    <View
      style={[
        styles.container,
        {backgroundColor: theme.colors.background},
      ]}>
      <Text style={[styles.title, {color: theme.colors.textPrimary}]}>
        UP2D8
      </Text>
      <Text style={[styles.subtitle, {color: theme.colors.textSecondary}]}>
        Mobile App - {isDark ? 'Dark' : 'Light'} Mode
      </Text>
      <Text style={[styles.subtitle, {color: theme.colors.textSecondary}]}>
        Phase 1.2 Complete ✅
      </Text>
    </View>
  );
}

export default function RootNavigator() {
  const {theme} = useTheme();

  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{
          headerStyle: {
            backgroundColor: theme.colors.primary,
          },
          headerTintColor: '#FFFFFF',
          headerTitleStyle: {
            fontWeight: '600',
          },
        }}>
        <Stack.Screen
          name="Home"
          component={PlaceholderScreen}
          options={{title: 'UP2D8'}}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    fontSize: 48,
    fontWeight: '700',
    marginBottom: 12,
  },
  subtitle: {
    fontSize: 16,
    marginTop: 8,
  },
});
