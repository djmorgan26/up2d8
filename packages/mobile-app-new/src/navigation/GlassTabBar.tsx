/**
 * Custom Glass Tab Bar
 * Glassmorphism bottom tab bar with blur effect
 */

import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Platform,
  Dimensions,
} from 'react-native';
import {BlurView} from '@react-native-community/blur';
import {BottomTabBarProps} from '@react-navigation/bottom-tabs';
import {useTheme} from '@context/ThemeContext';
import {useSafeAreaInsets} from 'react-native-safe-area-context';
import Animated, {
  useAnimatedStyle,
  withSpring,
  useSharedValue,
  withTiming,
} from 'react-native-reanimated';

const {width} = Dimensions.get('window');

export function GlassTabBar({
  state,
  descriptors,
  navigation,
}: BottomTabBarProps) {
  const {theme, isDark} = useTheme();
  const insets = useSafeAreaInsets();

  const tabWidth = width / state.routes.length;

  return (
    <View
      style={[
        styles.container,
        {
          paddingBottom: insets.bottom,
          backgroundColor: 'transparent',
        },
      ]}>
      {Platform.OS === 'ios' ? (
        <BlurView
          style={StyleSheet.absoluteFill}
          blurType={isDark ? 'dark' : 'light'}
          blurAmount={20}
          reducedTransparencyFallbackColor={theme.colors.background}
        />
      ) : (
        <View
          style={[
            StyleSheet.absoluteFill,
            {
              backgroundColor: isDark
                ? 'rgba(15, 15, 20, 0.85)'
                : 'rgba(255, 255, 255, 0.85)',
            },
          ]}
        />
      )}

      {/* Border top */}
      <View
        style={[
          styles.border,
          {
            backgroundColor: isDark
              ? 'rgba(255, 255, 255, 0.1)'
              : 'rgba(0, 0, 0, 0.1)',
          },
        ]}
      />

      {/* Tab items */}
      <View style={styles.tabsContainer}>
        {state.routes.map((route, index) => {
          const {options} = descriptors[route.key];
          const label =
            options.tabBarLabel !== undefined
              ? options.tabBarLabel
              : options.title !== undefined
                ? options.title
                : route.name;

          const isFocused = state.index === index;

          const onPress = () => {
            const event = navigation.emit({
              type: 'tabPress',
              target: route.key,
              canPreventDefault: true,
            });

            if (!isFocused && !event.defaultPrevented) {
              navigation.navigate(route.name);
            }
          };

          const onLongPress = () => {
            navigation.emit({
              type: 'tabLongPress',
              target: route.key,
            });
          };

          return (
            <TabButton
              key={route.key}
              isFocused={isFocused}
              options={options}
              onPress={onPress}
              onLongPress={onLongPress}
              label={label as string}
              theme={theme}
            />
          );
        })}
      </View>
    </View>
  );
}

interface TabButtonProps {
  isFocused: boolean;
  options: any;
  onPress: () => void;
  onLongPress: () => void;
  label: string;
  theme: any;
}

function TabButton({
  isFocused,
  options,
  onPress,
  onLongPress,
  label,
  theme,
}: TabButtonProps) {
  const scale = useSharedValue(1);

  const animatedStyle = useAnimatedStyle(() => {
    return {
      transform: [{scale: scale.value}],
    };
  });

  const handlePressIn = () => {
    scale.value = withSpring(0.9, {
      damping: 15,
      stiffness: 300,
    });
  };

  const handlePressOut = () => {
    scale.value = withSpring(1, {
      damping: 15,
      stiffness: 300,
    });
  };

  return (
    <TouchableOpacity
      accessibilityRole="button"
      accessibilityState={isFocused ? {selected: true} : {}}
      accessibilityLabel={options.tabBarAccessibilityLabel}
      testID={options.tabBarTestID}
      onPress={onPress}
      onLongPress={onLongPress}
      onPressIn={handlePressIn}
      onPressOut={handlePressOut}
      style={styles.tabButton}>
      <Animated.View style={[styles.tabContent, animatedStyle]}>
        {options.tabBarIcon?.({
          focused: isFocused,
          color: isFocused ? theme.colors.primary : theme.colors.textSecondary,
          size: 24,
        })}
        <Text
          style={[
            styles.tabLabel,
            {
              color: isFocused
                ? theme.colors.primary
                : theme.colors.textSecondary,
              fontSize: theme.typography.fontSize.xs,
              fontWeight: isFocused
                ? theme.typography.fontWeight.semibold
                : theme.typography.fontWeight.medium,
            },
          ]}>
          {label}
        </Text>
        {isFocused && (
          <View
            style={[
              styles.activeIndicator,
              {backgroundColor: theme.colors.primary},
            ]}
          />
        )}
      </Animated.View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    overflow: 'hidden',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
  },
  border: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: 1,
  },
  tabsContainer: {
    flexDirection: 'row',
    height: 65,
    alignItems: 'center',
  },
  tabButton: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  tabContent: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 8,
  },
  tabLabel: {
    marginTop: 4,
  },
  activeIndicator: {
    position: 'absolute',
    top: -8,
    width: 32,
    height: 3,
    borderRadius: 2,
  },
});
