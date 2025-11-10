/**
 * UP2D8 Shared Theme
 * Design tokens and theme system for web and mobile apps
 *
 * This package provides a single source of truth for all design tokens,
 * converted from the web app's Tailwind configuration to be compatible
 * with both web and React Native.
 */

export * from './colors';
export * from './typography';
export * from './spacing';
export * from './borderRadius';
export * from './shadows';
export * from './glass';
export * from './animations';

import { colors, brandColors, lightColors, darkColors, gradientBackgrounds } from './colors';
import { typography, fontSize, fontWeight, lineHeight, letterSpacing, textStyles } from './typography';
import { spacing, padding, margin, gap } from './spacing';
import { borderRadius, cardRadius } from './borderRadius';
import { shadows, lightShadows, darkShadows } from './shadows';
import { glassEffects } from './glass';
import { animations } from './animations';

/**
 * Complete theme object
 */
export const theme = {
  colors,
  typography,
  spacing,
  padding,
  margin,
  gap,
  borderRadius,
  shadows,
  glass: glassEffects,
  animations,
} as const;

/**
 * Light theme
 */
export const lightTheme = {
  colors: {
    ...brandColors,
    ...lightColors,
  },
  typography,
  spacing,
  padding,
  margin,
  gap,
  borderRadius,
  shadows: lightShadows,
  glass: glassEffects.light,
  animations,
} as const;

/**
 * Dark theme
 */
export const darkTheme = {
  colors: {
    ...brandColors,
    ...darkColors,
  },
  typography,
  spacing,
  padding,
  margin,
  gap,
  borderRadius,
  shadows: darkShadows,
  glass: glassEffects.dark,
  animations,
} as const;

/**
 * Theme type
 */
export type Theme = typeof lightTheme;

/**
 * Export individual tokens for convenience
 */
export {
  // Colors
  colors,
  brandColors,
  lightColors,
  darkColors,
  gradientBackgrounds,

  // Typography
  typography,
  fontSize,
  fontWeight,
  lineHeight,
  letterSpacing,
  textStyles,

  // Spacing
  spacing,
  padding,
  margin,
  gap,

  // Border radius
  borderRadius,
  cardRadius,

  // Shadows
  shadows,
  lightShadows,
  darkShadows,

  // Glass effects
  glassEffects,

  // Animations
  animations,
};
