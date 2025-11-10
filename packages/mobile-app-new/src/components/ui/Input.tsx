/**
 * Input Component
 * Text input with consistent styling matching web app
 */

import React, {useState, forwardRef} from 'react';
import {
  TextInput,
  View,
  Text,
  StyleSheet,
  ViewStyle,
  TextStyle,
  StyleProp,
  TextInputProps,
} from 'react-native';
import {useTheme} from '@context/ThemeContext';

interface InputProps extends TextInputProps {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  containerStyle?: StyleProp<ViewStyle>;
  inputStyle?: StyleProp<TextStyle>;
}

export const Input = forwardRef<TextInput, InputProps>(
  (
    {
      label,
      error,
      helperText,
      leftIcon,
      rightIcon,
      containerStyle,
      inputStyle,
      editable = true,
      ...props
    },
    ref,
  ) => {
    const {theme} = useTheme();
    const [isFocused, setIsFocused] = useState(false);

    const hasError = !!error;
    const isDisabled = !editable;

    return (
      <View style={[styles.container, containerStyle]}>
        {label && (
          <Text
            style={[
              styles.label,
              {
                color: theme.colors.textPrimary,
                fontSize: theme.typography.fontSize.sm,
                fontWeight: theme.typography.fontWeight.medium,
              },
            ]}>
            {label}
          </Text>
        )}

        <View
          style={[
            styles.inputContainer,
            {
              backgroundColor: theme.colors.background,
              borderColor: hasError
                ? theme.colors.error
                : isFocused
                  ? theme.colors.primary
                  : theme.colors.border,
              borderWidth: isFocused ? 2 : 1,
              borderRadius: theme.borderRadius.md,
            },
            isDisabled && styles.disabled,
          ]}>
          {leftIcon && <View style={styles.leftIcon}>{leftIcon}</View>}

          <TextInput
            ref={ref}
            style={[
              styles.input,
              {
                color: theme.colors.textPrimary,
                fontSize: theme.typography.fontSize.base,
              },
              inputStyle,
            ]}
            placeholderTextColor={theme.colors.textTertiary}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            editable={editable}
            {...props}
          />

          {rightIcon && <View style={styles.rightIcon}>{rightIcon}</View>}
        </View>

        {(error || helperText) && (
          <Text
            style={[
              styles.helperText,
              {
                color: hasError ? theme.colors.error : theme.colors.textSecondary,
                fontSize: theme.typography.fontSize.sm,
              },
            ]}>
            {error || helperText}
          </Text>
        )}
      </View>
    );
  },
);

Input.displayName = 'Input';

const styles = StyleSheet.create({
  container: {
    marginBottom: 16,
  },
  label: {
    marginBottom: 8,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    minHeight: 44,
    paddingHorizontal: 12,
  },
  input: {
    flex: 1,
    paddingVertical: 10,
  },
  leftIcon: {
    marginRight: 8,
  },
  rightIcon: {
    marginLeft: 8,
  },
  helperText: {
    marginTop: 4,
    marginLeft: 4,
  },
  disabled: {
    opacity: 0.5,
  },
});
