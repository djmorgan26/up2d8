import { Platform, Vibration } from 'react-native';

/**
 * Haptic feedback utilities using native Vibration API
 * For iOS, these will trigger tactile feedback. For Android, provides vibration patterns.
 */

export const haptics = {
  // Light tap - for small interactions like switches, checkboxes
  light: () => {
    if (Platform.OS === 'ios') {
      // iOS uses the Haptic Engine automatically
      Vibration.vibrate(10);
    } else {
      // Android - short vibration
      Vibration.vibrate(10);
    }
  },

  // Medium tap - for button presses, card selections
  medium: () => {
    if (Platform.OS === 'ios') {
      Vibration.vibrate(15);
    } else {
      Vibration.vibrate(20);
    }
  },

  // Heavy tap - for important actions, confirmations
  heavy: () => {
    if (Platform.OS === 'ios') {
      Vibration.vibrate(25);
    } else {
      Vibration.vibrate(30);
    }
  },

  // Selection changed - for picker/selector changes
  selection: () => {
    Vibration.vibrate(5);
  },

  // Success feedback - double tap pattern
  success: () => {
    if (Platform.OS === 'ios') {
      Vibration.vibrate([0, 10, 50, 10]);
    } else {
      Vibration.vibrate([0, 15, 60, 15]);
    }
  },

  // Warning feedback - triple tap pattern
  warning: () => {
    if (Platform.OS === 'ios') {
      Vibration.vibrate([0, 10, 30, 10, 30, 10]);
    } else {
      Vibration.vibrate([0, 15, 40, 15, 40, 15]);
    }
  },

  // Error feedback - strong double tap
  error: () => {
    if (Platform.OS === 'ios') {
      Vibration.vibrate([0, 20, 50, 20]);
    } else {
      Vibration.vibrate([0, 25, 60, 25]);
    }
  },
};

export default haptics;
