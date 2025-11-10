/**
 * Feeds Stack Navigator
 * Feeds List → (Future: Add Feed, Edit Feed)
 */

import React from 'react';
import {createNativeStackNavigator} from '@react-navigation/native-stack';
import FeedsScreen from '@screens/Feeds';
import type {FeedsStackParamList} from '../types';

const Stack = createNativeStackNavigator<FeedsStackParamList>();

export function FeedsStack() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
      }}>
      <Stack.Screen name="FeedsMain" component={FeedsScreen} />
      {/* Future: AddFeed, EditFeed screens */}
    </Stack.Navigator>
  );
}
