/**
 * Animation timing and easing
 */

export const animations = {
  /**
   * Animation durations (in milliseconds)
   */
  duration: {
    fast: 150,
    base: 250,
    slow: 350,
    slower: 500,
  },

  /**
   * Spring animation configs (React Native Animated.spring)
   */
  spring: {
    gentle: {
      friction: 8,
      tension: 100,
      useNativeDriver: true,
    },
    snappy: {
      friction: 5,
      tension: 100,
      useNativeDriver: true,
    },
    bouncy: {
      friction: 3,
      tension: 40,
      useNativeDriver: true,
    },
  },

  /**
   * Common animation values
   */
  scale: {
    press: 0.97,   // Scale down on press
    hover: 1.02,   // Scale up on hover (web)
  },

  /**
   * Easing functions (for Animated.timing)
   */
  easing: {
    easeIn: 'ease-in',
    easeOut: 'ease-out',
    easeInOut: 'ease-in-out',
  },
} as const;
