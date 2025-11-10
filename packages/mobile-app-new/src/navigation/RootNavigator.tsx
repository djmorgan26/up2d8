/**
 * Root Navigator
 * Main navigation container for the app
 * Phase 2: Showing component showcase
 */

import React from 'react';
import {NavigationContainer} from '@react-navigation/native';
import {createNativeStackNavigator} from '@react-navigation/native-stack';
import {useTheme} from '@context/ThemeContext';
import ComponentShowcase from '@screens/ComponentShowcase';

const Stack = createNativeStackNavigator();

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
          name="ComponentShowcase"
          component={ComponentShowcase}
          options={{title: 'UP2D8 Components'}}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
