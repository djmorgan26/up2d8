import React from 'react';
import {
  View,
  TouchableOpacity,
  Text,
  StyleSheet,
  Platform,
} from 'react-native';
import { BlurView } from '@react-native-community/blur';
import { BottomTabBarProps } from '@react-navigation/bottom-tabs';
import {
  colors,
  glass,
  borderRadius,
  shadows,
  spacing,
  typography,
} from '../theme/tokens';

export const GlassTabBar: React.FC<BottomTabBarProps> = ({
  state,
  descriptors,
  navigation,
}) => {
  return (
    <View style={styles.container}>
      {Platform.OS === 'ios' ? (
        <BlurView
          style={styles.absolute}
          blurType="light"
          blurAmount={glass.blur.medium}
          reducedTransparencyFallbackColor={glass.background.light}
        />
      ) : (
        <View
          style={[
            styles.absolute,
            { backgroundColor: glass.background.light },
          ]}
        />
      )}
      <View style={styles.tabContainer}>
        {state.routes.map((route, index) => {
          const { options } = descriptors[route.key];
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

          const icon = options.tabBarIcon
            ? options.tabBarIcon({
                focused: isFocused,
                color: isFocused ? colors.primary[500] : colors.neutral[500],
                size: 24,
              })
            : null;

          return (
            <TouchableOpacity
              key={route.key}
              accessibilityRole="button"
              accessibilityState={isFocused ? { selected: true } : {}}
              accessibilityLabel={options.tabBarAccessibilityLabel}
              testID={options.tabBarTestID}
              onPress={onPress}
              onLongPress={onLongPress}
              style={styles.tab}
            >
              {isFocused && (
                <View style={[styles.activeIndicator, shadows.sm]} />
              )}
              <View style={styles.iconContainer}>{icon}</View>
              <Text
                style={[
                  styles.label,
                  {
                    color: isFocused
                      ? colors.primary[500]
                      : colors.neutral[500],
                    fontWeight: isFocused
                      ? typography.fontWeight.semibold
                      : typography.fontWeight.regular,
                  },
                ]}
              >
                {typeof label === 'string' ? label : route.name}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    paddingBottom: Platform.OS === 'ios' ? spacing[6] : spacing[2],
    borderTopWidth: 1,
    borderTopColor: 'rgba(255, 255, 255, 0.2)',
  },
  absolute: {
    position: 'absolute',
    top: 0,
    left: 0,
    bottom: 0,
    right: 0,
  },
  tabContainer: {
    flexDirection: 'row',
    paddingTop: spacing[2],
    paddingHorizontal: spacing[4],
  },
  tab: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing[2],
    position: 'relative',
  },
  activeIndicator: {
    position: 'absolute',
    top: 0,
    left: '20%',
    right: '20%',
    height: 3,
    borderRadius: borderRadius.full,
    backgroundColor: colors.primary[500],
  },
  iconContainer: {
    marginBottom: spacing[1],
  },
  label: {
    fontSize: typography.fontSize.xs,
    letterSpacing: typography.letterSpacing.tight,
  },
});
