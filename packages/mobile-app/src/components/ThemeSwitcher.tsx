import React from 'react';
import { Switch, View, Text, StyleSheet, Animated } from 'react-native';
import { useTheme } from '../context/ThemeContext';
import Icon from 'react-native-vector-icons/Ionicons';

const ThemeSwitcher: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const fadeAnim = React.useRef(new Animated.Value(0)).current;

  React.useEffect(() => {
    Animated.timing(fadeAnim, {
      toValue: theme.dark ? 1 : 0,
      duration: 300,
      useNativeDriver: true,
    }).start();
  }, [theme.dark]);

  const sunOpacity = fadeAnim.interpolate({
    inputRange: [0, 1],
    outputRange: [1, 0],
  });

  const moonOpacity = fadeAnim;

  const styles = StyleSheet.create({
    container: {
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
      width: '100%',
    },
    leftContent: {
      flexDirection: 'row',
      alignItems: 'center',
      flex: 1,
    },
    iconContainer: {
      width: 40,
      height: 40,
      borderRadius: 10,
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: theme.colors.primary + '20',
      marginRight: 12,
      position: 'relative',
    },
    icon: {
      position: 'absolute',
    },
    textContainer: {
      flex: 1,
    },
    label: {
      color: theme.colors.textPrimary,
      fontSize: 16,
      fontWeight: '600',
      marginBottom: 2,
    },
    description: {
      color: theme.colors.textSecondary,
      fontSize: 13,
      fontWeight: '400',
    },
  });

  return (
    <View style={styles.container}>
      <View style={styles.leftContent}>
        <View style={styles.iconContainer}>
          <Animated.View style={[styles.icon, { opacity: sunOpacity }]}>
            <Icon name="sunny" size={24} color={theme.colors.primary} />
          </Animated.View>
          <Animated.View style={[styles.icon, { opacity: moonOpacity }]}>
            <Icon name="moon" size={24} color={theme.colors.primary} />
          </Animated.View>
        </View>
        <View style={styles.textContainer}>
          <Text style={styles.label}>{theme.dark ? 'Dark Mode' : 'Light Mode'}</Text>
          <Text style={styles.description}>
            {theme.dark ? 'Using dark theme' : 'Using light theme'}
          </Text>
        </View>
      </View>
      <Switch
        trackColor={{ false: '#D1D5DB', true: theme.colors.primary }}
        thumbColor="#FFFFFF"
        ios_backgroundColor="#D1D5DB"
        onValueChange={toggleTheme}
        value={theme.dark}
      />
    </View>
  );
};

export default ThemeSwitcher;
