/**
 * SearchBar Component
 * Search input with icon and clear button
 */

import React from 'react';
import {View, TextInput, StyleSheet, Pressable, ViewStyle} from 'react-native';
import {useTheme} from '@context/ThemeContext';
import {Search, X} from 'lucide-react-native';

interface SearchBarProps {
  value: string;
  onChangeText: (text: string) => void;
  placeholder?: string;
  onClear?: () => void;
  style?: ViewStyle;
}

export function SearchBar({
  value,
  onChangeText,
  placeholder = 'Search...',
  onClear,
  style,
}: SearchBarProps) {
  const {theme} = useTheme();

  const handleClear = () => {
    onChangeText('');
    onClear?.();
  };

  return (
    <View
      style={[
        styles.container,
        {
          backgroundColor: theme.colors.muted,
          borderRadius: theme.borderRadius.lg,
        },
        style,
      ]}>
      <Search size={20} color={theme.colors.textSecondary} />
      <TextInput
        value={value}
        onChangeText={onChangeText}
        placeholder={placeholder}
        placeholderTextColor={theme.colors.textTertiary}
        style={[
          styles.input,
          {
            color: theme.colors.textPrimary,
            fontSize: theme.typography.fontSize.base,
          },
        ]}
        returnKeyType="search"
        clearButtonMode="never" // Use custom clear button
      />
      {value.length > 0 && (
        <Pressable onPress={handleClear} style={styles.clearButton}>
          <X size={18} color={theme.colors.textSecondary} />
        </Pressable>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 10,
    gap: 8,
  },
  input: {
    flex: 1,
    paddingVertical: 0, // Remove default padding
    height: 24, // Fixed height for consistent layout
  },
  clearButton: {
    padding: 4,
  },
});
