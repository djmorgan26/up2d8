/**
 * Avatar Component
 * User avatar with fallback initials
 */

import React from 'react';
import {View, Text, Image, StyleSheet, ViewStyle, StyleProp} from 'react-native';
import {useTheme} from '@context/ThemeContext';
import {getInitials} from '@up2d8/shared-utils';
import LinearGradient from 'react-native-linear-gradient';

type AvatarSize = 'sm' | 'md' | 'lg' | 'xl';

interface AvatarProps {
  name?: string;
  imageUrl?: string;
  size?: AvatarSize;
  style?: StyleProp<ViewStyle>;
}

export function Avatar({name, imageUrl, size = 'md', style}: AvatarProps) {
  const {theme} = useTheme();

  const sizeStyles = {
    sm: {width: 32, height: 32, fontSize: theme.typography.fontSize.sm},
    md: {width: 40, height: 40, fontSize: theme.typography.fontSize.base},
    lg: {width: 56, height: 56, fontSize: theme.typography.fontSize.xl},
    xl: {width: 80, height: 80, fontSize: theme.typography.fontSize['3xl']},
  }[size];

  const initials = name ? getInitials(name, 2) : '?';

  return (
    <View
      style={[
        styles.container,
        {
          width: sizeStyles.width,
          height: sizeStyles.height,
          borderRadius: sizeStyles.width / 2,
        },
        style,
      ]}>
      {imageUrl ? (
        <Image source={{uri: imageUrl}} style={styles.image} />
      ) : (
        <LinearGradient
          colors={[theme.colors.primary, theme.colors.accent]}
          start={{x: 0, y: 0}}
          end={{x: 1, y: 1}}
          style={styles.gradient}>
          <Text
            style={[
              styles.initials,
              {
                fontSize: sizeStyles.fontSize,
                fontWeight: theme.typography.fontWeight.semibold,
              },
            ]}>
            {initials}
          </Text>
        </LinearGradient>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    overflow: 'hidden',
  },
  image: {
    width: '100%',
    height: '100%',
  },
  gradient: {
    width: '100%',
    height: '100%',
    justifyContent: 'center',
    alignItems: 'center',
  },
  initials: {
    color: '#FFFFFF',
    textAlign: 'center',
  },
});
