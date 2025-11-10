/**
 * Glassmorphism effect properties
 * Based on web app glass-card utility class
 */

export const glassEffects = {
  /**
   * Blur amounts (for iOS BlurView)
   */
  blur: {
    small: 10,   // backdrop-blur-md
    medium: 20,  // backdrop-blur-xl
    large: 30,   // backdrop-blur-2xl
    xLarge: 40,
  },

  /**
   * Opacity levels for glass backgrounds
   */
  opacity: {
    ultraLight: 0.95,
    light: 0.7,
    medium: 0.5,
    heavy: 0.3,
  },

  /**
   * Light mode glass properties
   */
  light: {
    background: 'rgba(255, 255, 255, 0.4)',  // bg-white/40
    backgroundStrong: 'rgba(255, 255, 255, 0.6)', // For sidebar
    border: 'rgba(255, 255, 255, 0.2)',      // border-white/20
    borderDark: 'rgba(0, 0, 0, 0.1)',
    shadow: {
      color: '#2E3A47',
      opacity: 0.1,
    },
  },

  /**
   * Dark mode glass properties
   */
  dark: {
    background: 'rgba(255, 255, 255, 0.05)',  // bg-white/5
    backgroundStrong: 'rgba(15, 23, 42, 0.6)', // For sidebar
    border: 'rgba(255, 255, 255, 0.1)',       // border-white/10
    borderDark: 'rgba(255, 255, 255, 0.05)',
    shadow: {
      color: '#000000',
      opacity: 0.5,
    },
  },
} as const;

export type GlassBlurIntensity = keyof typeof glassEffects.blur;
export type GlassOpacity = keyof typeof glassEffects.opacity;
