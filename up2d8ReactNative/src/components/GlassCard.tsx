import React, { ReactNode } from 'react';
import {
  View,
  StyleSheet,
  ViewStyle,
  StyleProp,
  Platform,
} from 'react-native';
import { BlurView } from '@react-native-community/blur';
import { colors, glass, borderRadius, shadows, spacing } from '../theme/tokens';

interface GlassCardProps {
  children: ReactNode;
  style?: StyleProp<ViewStyle>;
  blurIntensity?: 'light' | 'medium' | 'heavy';
  variant?: 'light' | 'dark';
  elevated?: boolean;
  borderless?: boolean;
}

export const GlassCard: React.FC<GlassCardProps> = ({
  children,
  style,
  blurIntensity = 'medium',
  variant = 'light',
  elevated = true,
  borderless = false,
}) => {
  const blurAmount = {
    light: glass.blur.small,
    medium: glass.blur.medium,
    heavy: glass.blur.large,
  }[blurIntensity];

  const backgroundColor =
    variant === 'light' ? glass.background.light : glass.background.dark;

  if (Platform.OS === 'ios') {
    return (
      <View
        style={[
          styles.container,
          elevated && shadows.glass,
          !borderless && styles.border,
          style,
        ]}
      >
        <BlurView
          style={styles.absolute}
          blurType={variant === 'light' ? 'light' : 'dark'}
          blurAmount={blurAmount}
          reducedTransparencyFallbackColor={backgroundColor}
        />
        <View style={styles.content}>{children}</View>
      </View>
    );
  }

  // Android fallback with semi-transparent background
  return (
    <View
      style={[
        styles.container,
        {
          backgroundColor,
        },
        elevated && shadows.glass,
        !borderless && styles.border,
        style,
      ]}
    >
      <View style={styles.content}>{children}</View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    borderRadius: borderRadius.xl,
    overflow: 'hidden',
  },
  absolute: {
    position: 'absolute',
    top: 0,
    left: 0,
    bottom: 0,
    right: 0,
  },
  content: {
    padding: spacing[4],
  },
  border: {
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.2)',
  },
});
