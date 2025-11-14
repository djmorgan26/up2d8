/**
 * Offline Indicator
 * Shows a banner when there are network errors
 *
 * NOTE: Install @react-native-community/netinfo for automatic detection
 * Currently shows on API errors only
 */

import React from 'react';
import {View, Text, StyleSheet} from 'react-native';
import {WifiOff} from 'lucide-react-native';

interface OfflineIndicatorProps {
  visible?: boolean;
  style?: any;
}

export default function OfflineIndicator({visible = false, style}: OfflineIndicatorProps) {
  if (!visible) {
    return null;
  }

  return (
    <View style={[styles.container, style]}>
      <View style={styles.content}>
        <WifiOff size={16} color="#FFFFFF" />
        <Text style={styles.text}>Connection Problem - Check Your Network</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    backgroundColor: '#EF4444',
    paddingVertical: 12,
    paddingHorizontal: 16,
    paddingTop: 50, // Account for status bar
    zIndex: 9999,
  },
  content: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
  },
  text: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
});
