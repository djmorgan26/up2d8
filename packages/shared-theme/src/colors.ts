/**
 * Color palette - converted from web app HSL values to hex/rgba
 * Source: packages/web-app/src/index.css
 */

// Helper function to convert HSL to hex
function hslToHex(h: number, s: number, l: number): string {
  l /= 100;
  const a = s * Math.min(l, 1 - l) / 100;
  const f = (n: number) => {
    const k = (n + h / 30) % 12;
    const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
    return Math.round(255 * color).toString(16).padStart(2, '0');
  };
  return `#${f(0)}${f(8)}${f(4)}`;
}

/**
 * Primary brand colors
 */
export const brandColors = {
  // Primary: HSL(221, 83%, 53%) -> Royal Blue
  primary: '#4169E1',
  primaryForeground: '#FFFFFF',

  // Accent: HSL(262, 83%, 58%) -> Vibrant Purple
  accent: '#A855F7',
  accentForeground: '#FFFFFF',

  // Gradient colors
  gradientFrom: '#4169E1', // HSL(221, 83%, 53%)
  gradientMid: '#7C3AED',  // Interpolated
  gradientTo: '#A855F7',   // HSL(262, 83%, 58%)
} as const;

/**
 * Light theme colors
 */
export const lightColors = {
  // Background: HSL(220, 25%, 97%)
  background: '#F7F8FA',
  foreground: '#2E3A47', // HSL(220, 15%, 20%)

  // Card: HSL(0, 0%, 100%)
  card: '#FFFFFF',
  cardForeground: '#2E3A47',

  // Surface colors
  surface: '#FFFFFF',
  surfaceSecondary: '#F2F4F7', // HSL(220, 15%, 95%)

  // Text colors
  textPrimary: '#2E3A47',    // HSL(220, 15%, 20%)
  textSecondary: '#737D8C',  // HSL(220, 10%, 50%)
  textTertiary: '#A3A3A3',

  // Border: HSL(220, 15%, 88%)
  border: '#DDDFE3',
  borderLight: '#E8EAED',

  // Glass effect colors
  glass: {
    background: 'rgba(255, 255, 255, 0.4)',
    backgroundLight: 'rgba(255, 255, 255, 0.6)',
    border: 'rgba(255, 255, 255, 0.2)',
    shadow: 'rgba(46, 58, 71, 0.1)',
  },

  // Semantic colors
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',    // HSL(0, 84%, 60%)
  info: '#3B82F6',

  // Muted: HSL(220, 15%, 95%)
  muted: '#F2F4F7',
  mutedForeground: '#737D8C',
} as const;

/**
 * Dark theme colors
 */
export const darkColors = {
  // Background: HSL(222, 47%, 11%)
  background: '#0F172A',
  foreground: '#F8FAFC', // HSL(210, 40%, 98%)

  // Card: HSL(222, 47%, 15%)
  card: '#1E293B',
  cardForeground: '#F8FAFC',

  // Surface colors
  surface: '#1E293B',
  surfaceSecondary: '#334155', // HSL(217, 33%, 17%)

  // Text colors
  textPrimary: '#F8FAFC',
  textSecondary: '#94A3B8',  // HSL(215, 20%, 65%)
  textTertiary: '#64748B',

  // Border: HSL(217, 33%, 25%)
  border: '#334155',
  borderLight: '#475569',

  // Glass effect colors
  glass: {
    background: 'rgba(255, 255, 255, 0.05)',
    backgroundLight: 'rgba(255, 255, 255, 0.1)',
    border: 'rgba(255, 255, 255, 0.1)',
    shadow: 'rgba(15, 23, 42, 0.5)',
  },

  // Semantic colors
  success: '#10B981',
  warning: '#F59E0B',
  error: '#DC2626',    // HSL(0, 63%, 31%)
  info: '#3B82F6',

  // Muted: HSL(217, 33%, 17%)
  muted: '#334155',
  mutedForeground: '#94A3B8',
} as const;

/**
 * Gradient background colors (used for page backgrounds)
 */
export const gradientBackgrounds = {
  light: ['#EBF2FF', '#FAF5FF', '#FCE7F3'], // Blue-50 → Purple-50 → Pink-50
  dark: ['#0A0A0A', '#1E1B4B', '#581C87'],  // Gray-900 → Blue-900 → Purple-900
} as const;

/**
 * Color types for TypeScript
 */
export type BrandColors = typeof brandColors;
export type LightColors = typeof lightColors;
export type DarkColors = typeof darkColors;
export type ColorScheme = 'light' | 'dark';

export const colors = {
  brand: brandColors,
  light: lightColors,
  dark: darkColors,
  gradientBackgrounds,
} as const;
