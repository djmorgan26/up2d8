/**
 * GlassButton Component
 * Button with glassmorphism effect and multiple variants
 * Matches web app button styles
 */

import React, {ReactNode, useRef} from 'react';
import {
  Text,
  StyleSheet,
  ViewStyle,
  TextStyle,
  StyleProp,
  Animated,
  Pressable,
  ActivityIndicator,
  View,
} from 'react-native';
import LinearGradient from 'react-native-linear-gradient';
import {useTheme} from '@context/ThemeContext';

type ButtonVariant = 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
type ButtonSize = 'sm' | 'default' | 'lg' | 'icon';

interface GlassButtonProps {
  children: ReactNode;
  variant?: ButtonVariant;
  size?: ButtonSize;
  onPress?: () => void;
  disabled?: boolean;
  loading?: boolean;
  style?: StyleProp<ViewStyle>;
  textStyle?: StyleProp<TextStyle>;
  icon?: ReactNode;
  iconPosition?: 'left' | 'right';
}

export function GlassButton({
  children,
  variant = 'default',
  size = 'default',
  onPress,
  disabled = false,
  loading = false,
  style,
  textStyle,
  icon,
  iconPosition = 'left',
}: GlassButtonProps) {
  const {theme} = useTheme();
  const scaleAnim = useRef(new Animated.Value(1)).current;

  const handlePressIn = () => {
    if (disabled || loading) return;
    Animated.spring(scaleAnim, {
      toValue: theme.animations.scale.press,
      ...theme.animations.spring.snappy,
    }).start();
  };

  const handlePressOut = () => {
    if (disabled || loading) return;
    Animated.spring(scaleAnim, {
      toValue: 1,
      ...theme.animations.spring.snappy,
    }).start();
  };

  // Size styles
  const sizeStyles = {
    sm: {
      height: 36,
      paddingHorizontal: theme.spacing[3],
      borderRadius: theme.borderRadius.md,
    },
    default: {
      height: 44,
      paddingHorizontal: theme.spacing[4],
      borderRadius: theme.borderRadius.md,
    },
    lg: {
      height: 48,
      paddingHorizontal: theme.spacing[8],
      borderRadius: theme.borderRadius.md,
    },
    icon: {
      height: 44,
      width: 44,
      paddingHorizontal: 0,
      borderRadius: theme.borderRadius.md,
    },
  }[size];

  const textSizeStyles = {
    sm: {fontSize: theme.typography.fontSize.sm},
    default: {fontSize: theme.typography.fontSize.base},
    lg: {fontSize: theme.typography.fontSize.lg},
    icon: {fontSize: theme.typography.fontSize.base},
  }[size];

  // Variant styles
  const getVariantStyles = () => {
    switch (variant) {
      case 'default':
        return {
          useGradient: true,
          textColor: '#FFFFFF',
        };
      case 'destructive':
        return {
          backgroundColor: theme.colors.error,
          textColor: '#FFFFFF',
        };
      case 'outline':
        return {
          backgroundColor: 'transparent',
          borderWidth: 1,
          borderColor: theme.colors.border,
          textColor: theme.colors.textPrimary,
        };
      case 'secondary':
        return {
          backgroundColor: theme.colors.muted,
          textColor: theme.colors.textPrimary,
        };
      case 'ghost':
        return {
          backgroundColor: 'transparent',
          textColor: theme.colors.textPrimary,
        };
      case 'link':
        return {
          backgroundColor: 'transparent',
          textColor: theme.colors.primary,
          textDecoration: 'underline',
        };
    }
  };

  const variantStyles = getVariantStyles();

  const buttonContent = (
    <View style={styles.content}>
      {loading ? (
        <ActivityIndicator color={variantStyles.textColor} />
      ) : (
        <>
          {icon && iconPosition === 'left' && <View style={styles.iconLeft}>{icon}</View>}
          {typeof children === 'string' ? (
            <Text
              style={[
                styles.text,
                textSizeStyles,
                {
                  color: variantStyles.textColor,
                  fontWeight: theme.typography.fontWeight.semibold,
                },
                disabled && styles.disabledText,
                textStyle,
              ]}>
              {children}
            </Text>
          ) : (
            children
          )}
          {icon && iconPosition === 'right' && <View style={styles.iconRight}>{icon}</View>}
        </>
      )}
    </View>
  );

  return (
    <Animated.View
      style={[
        {transform: [{scale: scaleAnim}]},
        disabled && styles.disabled,
      ]}>
      <Pressable
        onPress={onPress}
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        disabled={disabled || loading}
        style={[
          styles.button,
          sizeStyles,
          !variantStyles.useGradient && {
            backgroundColor: variantStyles.backgroundColor,
          },
          variantStyles.borderWidth && {
            borderWidth: variantStyles.borderWidth,
            borderColor: variantStyles.borderColor,
          },
          disabled && styles.disabled,
          style,
        ]}>
        {variantStyles.useGradient ? (
          <LinearGradient
            colors={[theme.colors.primary, theme.colors.accent]}
            start={{x: 0, y: 0}}
            end={{x: 1, y: 0}}
            style={[
              StyleSheet.absoluteFill,
              {borderRadius: sizeStyles.borderRadius},
            ]}>
            {buttonContent}
          </LinearGradient>
        ) : (
          buttonContent
        )}
      </Pressable>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  button: {
    justifyContent: 'center',
    alignItems: 'center',
    overflow: 'hidden',
  },
  content: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
  },
  text: {
    textAlign: 'center',
  },
  disabled: {
    opacity: 0.5,
  },
  disabledText: {
    opacity: 0.7,
  },
  iconLeft: {
    marginRight: 4,
  },
  iconRight: {
    marginLeft: 4,
  },
});
