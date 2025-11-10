/**
 * Settings Stack Navigator
 * Settings Screen (single screen for now)
 */

import React from 'react';
import {createNativeStackNavigator} from '@react-navigation/native-stack';
import SettingsScreen from '@screens/Settings';
import type {SettingsStackParamList} from '../types';

const Stack = createNativeStackNavigator<SettingsStackParamList>();

export function SettingsStack() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
      }}>
      <Stack.Screen name="SettingsMain" component={SettingsScreen} />
      {/* Future: Account, Notifications, Privacy screens */}
    </Stack.Navigator>
  );
}
