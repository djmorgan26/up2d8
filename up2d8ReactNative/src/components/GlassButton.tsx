import React, { ReactNode } from 'react';
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  ViewStyle,
  TextStyle,
  StyleProp,
  Platform,
  ActivityIndicator,
} from 'react-native';
import { BlurView } from '@react-native-community/blur';
import {
  colors,
  glass,
  borderRadius,
  shadows,
  spacing,
  typography,
} from '../theme/tokens';

interface GlassButtonProps {
  onPress: () => void;
  children: ReactNode;
  style?: StyleProp<ViewStyle>;
  textStyle?: StyleProp<TextStyle>;
  variant?: 'primary' | 'secondary' | 'accent';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  fullWidth?: boolean;
}

export const GlassButton: React.FC<GlassButtonProps> = ({
  onPress,
  children,
  style,
  textStyle,
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  fullWidth = false,
}) => {
  const sizeStyles = {
    sm: {
      paddingVertical: spacing[2],
      paddingHorizontal: spacing[4],
      fontSize: typography.fontSize.sm,
    },
    md: {
      paddingVertical: spacing[3],
      paddingHorizontal: spacing[6],
      fontSize: typography.fontSize.base,
    },
    lg: {
      paddingVertical: spacing[4],
      paddingHorizontal: spacing[8],
      fontSize: typography.fontSize.lg,
    },
  }[size];

  const variantColors = {
    primary: colors.primary[500],
    secondary: colors.neutral[600],
    accent: colors.accent[500],
  }[variant];

  const content = (
    <>
      {loading ? (
        <ActivityIndicator color="white" />
      ) : typeof children === 'string' ? (
        <Text
          style={[
            styles.text,
            { fontSize: sizeStyles.fontSize },
            textStyle,
            disabled && styles.disabledText,
          ]}
        >
          {children}
        </Text>
      ) : (
        children
      )}
    </>
  );

  if (Platform.OS === 'ios') {
    return (
      <TouchableOpacity
        onPress={onPress}
        disabled={disabled || loading}
        activeOpacity={0.7}
        style={[
          styles.container,
          {
            paddingVertical: sizeStyles.paddingVertical,
            paddingHorizontal: sizeStyles.paddingHorizontal,
          },
          shadows.md,
          fullWidth && styles.fullWidth,
          disabled && styles.disabled,
          style,
        ]}
      >
        <BlurView
          style={styles.absolute}
          blurType="light"
          blurAmount={glass.blur.medium}
          reducedTransparencyFallbackColor={variantColors}
        />
        {content}
      </TouchableOpacity>
    );
  }

  // Android fallback
  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={disabled || loading}
      activeOpacity={0.7}
      style={[
        styles.container,
        {
          backgroundColor: variantColors,
          paddingVertical: sizeStyles.paddingVertical,
          paddingHorizontal: sizeStyles.paddingHorizontal,
        },
        shadows.md,
        fullWidth && styles.fullWidth,
        disabled && styles.disabled,
        style,
      ]}
    >
      {content}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  container: {
    borderRadius: borderRadius.lg,
    overflow: 'hidden',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.3)',
  },
  absolute: {
    position: 'absolute',
    top: 0,
    left: 0,
    bottom: 0,
    right: 0,
  },
  fullWidth: {
    width: '100%',
  },
  disabled: {
    opacity: 0.5,
  },
  text: {
    color: 'white',
    fontWeight: typography.fontWeight.semibold as any,
    textAlign: 'center',
  },
  disabledText: {
    color: colors.neutral[400],
  },
});
