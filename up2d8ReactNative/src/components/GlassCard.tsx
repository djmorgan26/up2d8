import React, { ReactNode } from 'react';
import {
  View,
  StyleSheet,
  ViewStyle,
  StyleProp,
  Platform,
  Text,
} from 'react-native';
import { BlurView } from '@react-native-community/blur';
import LinearGradient from 'react-native-linear-gradient';
import {
  colors,
  glass,
  borderRadius,
  shadows,
  spacing,
  typography,
} from '../theme/tokens';

interface GlassCardProps {
  children: ReactNode;
  style?: StyleProp<ViewStyle>;
  blurIntensity?: 'light' | 'medium' | 'heavy';
  variant?: 'light' | 'dark';
  elevated?: boolean;
  borderless?: boolean;
}

const applyTextShadow = (children: ReactNode): ReactNode => {
  return React.Children.map(children, (child) => {
    if (React.isValidElement(child) && child.type === Text) {
      return React.cloneElement(child as React.ReactElement<any>, {
        style: [child.props.style, styles.textShadow],
      });
    }
    if (React.isValidElement(child) && child.props.children) {
      return React.cloneElement(child as React.ReactElement<any>, {
        children: applyTextShadow(child.props.children),
      });
    }
    return child;
  });
};

export const GlassCard: React.FC<GlassCardProps> = ({
  children,
  style,
  blurIntensity = 'medium',
  variant = 'light',
  elevated = true,
  borderless = false,
}) => {
  const blurAmount = {
    light: glass.blur.small,
    medium: glass.blur.medium,
    heavy: glass.blur.large,
  }[blurIntensity];

  const backgroundColor =
    variant === 'light' ? glass.background.light : glass.background.dark;

  const content = (
    <View style={styles.content}>{applyTextShadow(children)}</View>
  );

  if (Platform.OS === 'ios') {
    return (
      <View
        style={[
          styles.container,
          elevated && shadows.glass,
          style,
        ]}
      >
        <BlurView
          style={styles.absolute}
          blurType={variant === 'light' ? 'light' : 'dark'}
          blurAmount={blurAmount}
          reducedTransparencyFallbackColor={backgroundColor}
        />
        {!borderless && (
          <LinearGradient
            colors={colors.borderGradient}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
            style={styles.border}
          />
        )}
        {content}
      </View>
    );
  }

  // Android fallback with semi-transparent background
  return (
    <View
      style={[
        styles.container,
        {
          backgroundColor,
        },
        elevated && shadows.glass,
        !borderless && styles.androidBorder,
        style,
      ]}
    >
      {content}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    borderRadius: borderRadius.xl,
    overflow: 'hidden',
  },
  absolute: {
    position: 'absolute',
    top: 0,
    left: 0,
    bottom: 0,
    right: 0,
  },
  content: {
    padding: spacing[4],
  },
  border: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: 'transparent',
  },
  androidBorder: {
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.2)',
  },
  textShadow: {
    textShadowColor: 'rgba(0, 0, 0, 0.1)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 2,
  },
});
