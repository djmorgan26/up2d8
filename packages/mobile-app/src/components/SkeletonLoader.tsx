import React, { useEffect, useRef } from 'react';
import { View, StyleSheet, Animated, ViewStyle } from 'react-native';
import { useTheme } from '../context/ThemeContext';
import LinearGradient from 'react-native-linear-gradient';

interface SkeletonLoaderProps {
  width?: number | string;
  height?: number;
  borderRadius?: number;
  style?: ViewStyle;
}

export const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({
  width = '100%',
  height = 20,
  borderRadius = 8,
  style,
}) => {
  const { theme } = useTheme();
  const shimmerAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    const shimmer = Animated.loop(
      Animated.sequence([
        Animated.timing(shimmerAnim, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(shimmerAnim, {
          toValue: 0,
          duration: 1000,
          useNativeDriver: true,
        }),
      ])
    );
    shimmer.start();

    return () => shimmer.stop();
  }, [shimmerAnim]);

  const translateX = shimmerAnim.interpolate({
    inputRange: [0, 1],
    outputRange: [-300, 300],
  });

  const baseColor = theme.dark ? '#1F2937' : '#E5E7EB';
  const shimmerColor = theme.dark ? '#374151' : '#F3F4F6';

  return (
    <View
      style={[
        styles.container,
        {
          width,
          height,
          borderRadius,
          backgroundColor: baseColor,
          overflow: 'hidden',
        },
        style,
      ]}
    >
      <Animated.View
        style={[
          styles.shimmer,
          {
            transform: [{ translateX }],
          },
        ]}
      >
        <LinearGradient
          colors={[baseColor, shimmerColor, baseColor]}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 0 }}
          style={styles.gradient}
        />
      </Animated.View>
    </View>
  );
};

interface SkeletonCardProps {
  showAvatar?: boolean;
  lines?: number;
  style?: ViewStyle;
}

export const SkeletonCard: React.FC<SkeletonCardProps> = ({
  showAvatar = false,
  lines = 3,
  style,
}) => {
  return (
    <View style={[styles.card, style]}>
      {showAvatar && (
        <View style={styles.avatarRow}>
          <SkeletonLoader width={40} height={40} borderRadius={20} />
          <View style={styles.avatarText}>
            <SkeletonLoader width="60%" height={14} />
            <View style={{ height: 6 }} />
            <SkeletonLoader width="40%" height={12} />
          </View>
        </View>
      )}
      {Array.from({ length: lines }).map((_, index) => (
        <View key={index}>
          <SkeletonLoader
            width={index === lines - 1 ? '70%' : '100%'}
            height={16}
          />
          {index < lines - 1 && <View style={{ height: 8 }} />}
        </View>
      ))}
    </View>
  );
};

interface SkeletonListProps {
  count?: number;
  showAvatar?: boolean;
}

export const SkeletonList: React.FC<SkeletonListProps> = ({
  count = 5,
  showAvatar = false,
}) => {
  return (
    <View style={styles.list}>
      {Array.from({ length: count }).map((_, index) => (
        <SkeletonCard
          key={index}
          showAvatar={showAvatar}
          style={styles.listItem}
        />
      ))}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    position: 'relative',
  },
  shimmer: {
    width: 300,
    height: '100%',
  },
  gradient: {
    flex: 1,
  },
  card: {
    padding: 16,
  },
  avatarRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  avatarText: {
    flex: 1,
    marginLeft: 12,
  },
  list: {
    padding: 20,
  },
  listItem: {
    marginBottom: 12,
  },
});
