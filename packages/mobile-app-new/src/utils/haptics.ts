/**
 * Haptic Feedback Utilities
 * Provides haptic feedback for user interactions
 */

import {Platform} from 'react-native';
import ReactNativeHapticFeedback from 'react-native-haptic-feedback';

const options = {
  enableVibrateFallback: true,
  ignoreAndroidSystemSettings: false,
};

export const haptics = {
  /**
   * Light impact - For selection changes, button taps
   */
  light: () => {
    if (Platform.OS === 'ios') {
      ReactNativeHapticFeedback.trigger('impactLight', options);
    }
  },

  /**
   * Medium impact - For navigation, swipe actions
   */
  medium: () => {
    if (Platform.OS === 'ios') {
      ReactNativeHapticFeedback.trigger('impactMedium', options);
    }
  },

  /**
   * Heavy impact - For important actions, confirmations
   */
  heavy: () => {
    if (Platform.OS === 'ios') {
      ReactNativeHapticFeedback.trigger('impactHeavy', options);
    }
  },

  /**
   * Success - For successful operations
   */
  success: () => {
    if (Platform.OS === 'ios') {
      ReactNativeHapticFeedback.trigger('notificationSuccess', options);
    }
  },

  /**
   * Warning - For warnings or important alerts
   */
  warning: () => {
    if (Platform.OS === 'ios') {
      ReactNativeHapticFeedback.trigger('notificationWarning', options);
    }
  },

  /**
   * Error - For errors or failures
   */
  error: () => {
    if (Platform.OS === 'ios') {
      ReactNativeHapticFeedback.trigger('notificationError', options);
    }
  },

  /**
   * Selection - For picker/selector changes
   */
  selection: () => {
    if (Platform.OS === 'ios') {
      ReactNativeHapticFeedback.trigger('selection', options);
    }
  },
};
