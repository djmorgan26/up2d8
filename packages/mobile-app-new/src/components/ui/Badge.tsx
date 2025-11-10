/**
 * Badge Component
 * Small badge for labels, tags, and status indicators
 */

import React, {ReactNode} from 'react';
import {View, Text, StyleSheet, ViewStyle, TextStyle, StyleProp} from 'react-native';
import {useTheme} from '@context/ThemeContext';

type BadgeVariant = 'default' | 'primary' | 'success' | 'warning' | 'error' | 'outline';

interface BadgeProps {
  children: ReactNode;
  variant?: BadgeVariant;
  style?: StyleProp<ViewStyle>;
  textStyle?: StyleProp<TextStyle>;
}

export function Badge({
  children,
  variant = 'default',
  style,
  textStyle,
}: BadgeProps) {
  const {theme} = useTheme();

  const getVariantStyles = () => {
    switch (variant) {
      case 'default':
        return {
          backgroundColor: theme.colors.muted,
          textColor: theme.colors.textPrimary,
        };
      case 'primary':
        return {
          backgroundColor: theme.colors.primary + '20',
          textColor: theme.colors.primary,
        };
      case 'success':
        return {
          backgroundColor: theme.colors.success + '20',
          textColor: theme.colors.success,
        };
      case 'warning':
        return {
          backgroundColor: theme.colors.warning + '20',
          textColor: theme.colors.warning,
        };
      case 'error':
        return {
          backgroundColor: theme.colors.error + '20',
          textColor: theme.colors.error,
        };
      case 'outline':
        return {
          backgroundColor: 'transparent',
          borderWidth: 1,
          borderColor: theme.colors.border,
          textColor: theme.colors.textPrimary,
        };
    }
  };

  const variantStyles = getVariantStyles();

  return (
    <View
      style={[
        styles.badge,
        {
          backgroundColor: variantStyles.backgroundColor,
          borderRadius: theme.borderRadius.full,
        },
        variantStyles.borderWidth && {
          borderWidth: variantStyles.borderWidth,
          borderColor: variantStyles.borderColor,
        },
        style,
      ]}>
      {typeof children === 'string' ? (
        <Text
          style={[
            styles.text,
            {
              color: variantStyles.textColor,
              fontSize: theme.typography.fontSize.xs,
              fontWeight: theme.typography.fontWeight.medium,
            },
            textStyle,
          ]}>
          {children}
        </Text>
      ) : (
        children
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    alignSelf: 'flex-start',
  },
  text: {
    textAlign: 'center',
  },
});
