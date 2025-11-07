import React from 'react';
import { Switch, View, Text, StyleSheet } from 'react-native';
import { useTheme } from '../context/ThemeContext';

const ThemeSwitcher: React.FC = () => {
  const { theme, toggleTheme } = useTheme();

  const styles = StyleSheet.create({
    container: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 10,
      backgroundColor: theme.colors.surface,
    },
    label: {
      color: theme.colors.textPrimary,
      marginRight: 10,
      fontSize: 16,
    },
  });

  return (
    <View style={styles.container}>
      <Text style={styles.label}>Dark Mode</Text>
      <Switch
        trackColor={{ false: theme.colors.textSecondary, true: theme.colors.primary }}
        thumbColor={theme.colors.accent}
        ios_backgroundColor={theme.colors.textSecondary}
        onValueChange={toggleTheme}
        value={theme.dark}
      />
    </View>
  );
};

export default ThemeSwitcher;
