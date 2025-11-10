/**
 * GlassCard Component
 * Glassmorphism card with blur effect matching web app design
 * iOS: Uses BlurView for native blur
 * Android: Uses semi-transparent background fallback
 */

import React, {ReactNode, useRef} from 'react';
import {
  View,
  StyleSheet,
  ViewStyle,
  StyleProp,
  Platform,
  Animated,
  Pressable,
} from 'react-native';
import {BlurView} from '@react-native-community/blur';
import LinearGradient from 'react-native-linear-gradient';
import {useTheme} from '@context/ThemeContext';

interface GlassCardProps {
  children: ReactNode;
  style?: StyleProp<ViewStyle>;
  blurIntensity?: 'small' | 'medium' | 'large' | 'xLarge';
  elevated?: boolean;
  borderless?: boolean;
  onPress?: () => void;
  pressable?: boolean;
}

export function GlassCard({
  children,
  style,
  blurIntensity = 'medium',
  elevated = true,
  borderless = false,
  onPress,
  pressable = false,
}: GlassCardProps) {
  const {theme, isDark} = useTheme();
  const scaleAnim = useRef(new Animated.Value(1)).current;

  const blurAmount = {
    small: theme.glass.blur.small,
    medium: theme.glass.blur.medium,
    large: theme.glass.blur.large,
    xLarge: theme.glass.blur.xLarge,
  }[blurIntensity];

  const handlePressIn = () => {
    if (!pressable && !onPress) return;
    Animated.spring(scaleAnim, {
      toValue: theme.animations.scale.press,
      ...theme.animations.spring.snappy,
    }).start();
  };

  const handlePressOut = () => {
    if (!pressable && !onPress) return;
    Animated.spring(scaleAnim, {
      toValue: 1,
      ...theme.animations.spring.snappy,
    }).start();
  };

  const containerStyle = [
    styles.container,
    {borderRadius: theme.borderRadius.xl},
    elevated && theme.shadows.glass,
    style,
  ];

  const content = <View style={styles.content}>{children}</View>;

  const cardContent = (
    <>
      {Platform.OS === 'ios' ? (
        <>
          {/* iOS: Native blur effect */}
          <BlurView
            style={styles.absolute}
            blurType={isDark ? 'dark' : 'light'}
            blurAmount={blurAmount}
            reducedTransparencyFallbackColor={
              isDark ? theme.glass.background : theme.glass.backgroundStrong
            }
          />
          {/* Border gradient */}
          {!borderless && (
            <LinearGradient
              colors={[
                theme.colors.primary + '40',
                theme.colors.accent + '40',
              ]}
              start={{x: 0, y: 0}}
              end={{x: 1, y: 1}}
              style={[
                styles.border,
                {borderRadius: theme.borderRadius.xl},
              ]}
            />
          )}
        </>
      ) : (
        /* Android: Fallback with semi-transparent background */
        <View
          style={[
            styles.absolute,
            {
              backgroundColor: isDark
                ? theme.glass.background
                : theme.glass.backgroundStrong,
            },
            !borderless && {
              borderWidth: 1,
              borderColor: theme.glass.border,
            },
          ]}
        />
      )}
      {content}
    </>
  );

  if (pressable || onPress) {
    return (
      <Animated.View style={[containerStyle, {transform: [{scale: scaleAnim}]}]}>
        <Pressable
          onPress={onPress}
          onPressIn={handlePressIn}
          onPressOut={handlePressOut}
          style={styles.pressable}>
          {cardContent}
        </Pressable>
      </Animated.View>
    );
  }

  return <View style={containerStyle}>{cardContent}</View>;
}

const styles = StyleSheet.create({
  container: {
    overflow: 'hidden',
    position: 'relative',
  },
  absolute: {
    position: 'absolute',
    top: 0,
    left: 0,
    bottom: 0,
    right: 0,
  },
  content: {
    padding: 16, // theme.spacing[4]
  },
  border: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    borderWidth: 1,
    borderColor: 'transparent',
  },
  pressable: {
    flex: 1,
  },
});
