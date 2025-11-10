/**
 * Border radius scale
 * Matches Tailwind border radius values
 */

export const borderRadius = {
  none: 0,
  sm: 4,     // 0.25rem
  md: 6,     // 0.375rem (--radius - 4px)
  lg: 12,    // 0.75rem (--radius default)
  xl: 16,    // 1rem
  '2xl': 20, // 1.25rem
  '3xl': 24, // 1.5rem
  full: 9999,
} as const;

/**
 * Card border radius (commonly used)
 */
export const cardRadius = borderRadius.xl;
