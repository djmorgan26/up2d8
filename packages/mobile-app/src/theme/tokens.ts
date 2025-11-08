/**
 * Design Tokens for Liquid Glass iOS Theme
 * Modern iOS blue/purple palette with glassmorphism properties
 */

// Color Palette - Modern iOS Blues & Purples
export const colors = {
  // Primary gradient blues to purples
  primary: {
    50: '#F0F4FF',   // Lightest blue
    100: '#D6E4FF',  // Very light blue
    200: '#ADC8FF',  // Light blue
    300: '#84A9FF',  // Medium blue
    400: '#5B86E5',  // iOS Blue
    500: '#4169E1',  // Royal Blue (primary)
    600: '#364FC7',  // Deep Blue
    700: '#5F3DC4',  // Blue-Purple
    800: '#7C3AED',  // Purple
    900: '#9333EA',  // Deep Purple
  },

  // Accent colors
  accent: {
    50: '#FAF5FF',
    100: '#F3E8FF',
    200: '#E9D5FF',
    300: '#D8B4FE',
    400: '#C084FC',
    500: '#A855F7',  // Vibrant Purple (accent)
    600: '#9333EA',
    700: '#7E22CE',
    800: '#6B21A8',
    900: '#581C87',
  },

  // Neutral grays for backgrounds
  neutral: {
    50: '#FAFAFA',
    100: '#F5F5F5',
    200: '#E5E5E5',
    300: '#D4D4D4',
    400: '#A3A3A3',
    500: '#737373',
    600: '#525252',
    700: '#404040',
    800: '#262626',
    900: '#171717',
    950: '#0A0A0A',
  },

  // Semantic colors
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  info: '#3B82F6',

  // Special effects
  glass: {
    light: 'rgba(255, 255, 255, 0.7)',
    medium: 'rgba(255, 255, 255, 0.5)',
    dark: 'rgba(0, 0, 0, 0.3)',
    ultraLight: 'rgba(255, 255, 255, 0.9)',
  },

  // New border gradient
  borderGradient: ['rgba(255, 255, 255, 0.4)', 'rgba(255, 255, 255, 0.1)'],
};

// Glassmorphism constants (Medium intensity - iOS Widgets style)
export const glass = {
  blur: {
    small: 10,
    medium: 20,
    large: 30,
    xLarge: 40,
  },
  opacity: {
    ultraLight: 0.9,
    light: 0.7,
    medium: 0.5,
    heavy: 0.3,
  },
  background: {
    light: 'rgba(255, 255, 255, 0.7)',
    medium: 'rgba(255, 255, 255, 0.5)',
    dark: 'rgba(0, 0, 0, 0.3)',
    ultraDark: 'rgba(0, 0, 0, 0.5)',
  },
};

// Typography scale (SF Pro inspired)
export const typography = {
  fontSize: {
    xs: 12,
    sm: 14,
    base: 16,
    lg: 18,
    xl: 20,
    '2xl': 24,
    '3xl': 30,
    '4xl': 36,
    '5xl': 48,
  },
  fontWeight: {
    thin: '100',
    light: '300',
    regular: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
    heavy: '800',
    black: '900',
  },
  lineHeight: {
    tight: 1.2,
    normal: 1.5,
    relaxed: 1.75,
    loose: 2,
  },
  letterSpacing: {
    tighter: -0.05,
    tight: -0.025,
    normal: 0,
    wide: 0.025,
    wider: 0.05,
    widest: 0.1,
  },
};

// Spacing system (8pt grid)
export const spacing = {
  0: 0,
  1: 4,
  2: 8,
  3: 12,
  4: 16,
  5: 20,
  6: 24,
  7: 28,
  8: 32,
  9: 36,
  10: 40,
  12: 48,
  16: 64,
  20: 80,
  24: 96,
  32: 128,
};

// Border radius
export const borderRadius = {
  none: 0,
  sm: 4,
  base: 8,
  md: 12,
  lg: 16,
  xl: 20,
  '2xl': 24,
  '3xl': 32,
  full: 9999,
};

// Shadows and elevation
export const shadows = {
  sm: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  base: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  md: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 4,
  },
  lg: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.2,
    shadowRadius: 16,
    elevation: 6,
  },
  xl: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 0.25,
    shadowRadius: 24,
    elevation: 8,
  },
  // Special glass shadow
  glass: {
    shadowColor: '#5B86E5',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 12,
    elevation: 5,
  },
};

// Animation durations
export const animation = {
  fast: 150,
  base: 250,
  slow: 350,
  slower: 500,
};

// Z-index layers
export const zIndex = {
  base: 0,
  dropdown: 1000,
  sticky: 1020,
  fixed: 1030,
  modalBackdrop: 1040,
  modal: 1050,
  popover: 1060,
  tooltip: 1070,
};