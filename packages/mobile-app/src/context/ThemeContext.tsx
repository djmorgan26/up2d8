import React, { createContext, useState, useContext, ReactNode } from 'react';
import { Appearance, ColorSchemeName } from 'react-native';
import { colors, glass, shadows } from '../theme/tokens';

interface ThemeColors {
  primary: string;
  primaryLight: string;
  primaryDark: string;
  accent: string;
  accentLight: string;
  background: string;
  surface: string;
  textPrimary: string;
  textSecondary: string;
  success: string;
  warning: string;
  error: string;
  info: string;
}

interface GlassProperties {
  light: string;
  medium: string;
  dark: string;
  ultraLight: string;
  blurAmount: number;
}

interface Theme {
  dark: boolean;
  colors: ThemeColors;
  glass: GlassProperties;
  shadows: typeof shadows;
}

const LightTheme: Theme = {
  dark: false,
  colors: {
    primary: colors.primary[500],      // Royal Blue
    primaryLight: colors.primary[400],  // iOS Blue
    primaryDark: colors.primary[700],   // Blue-Purple
    accent: colors.accent[500],         // Vibrant Purple
    accentLight: colors.accent[400],    // Light Purple
    background: colors.neutral[50],     // Very Light
    surface: 'rgba(255, 255, 255, 0.9)', // Translucent white
    textPrimary: colors.neutral[900],   // Near Black
    textSecondary: colors.neutral[500], // Medium Grey
    success: colors.success,
    warning: colors.warning,
    error: colors.error,
    info: colors.info,
  },
  glass: {
    light: glass.background.light,
    medium: glass.background.medium,
    dark: glass.background.dark,
    ultraLight: 'rgba(255, 255, 255, 0.95)',
    blurAmount: glass.blur.medium,
  },
  shadows,
};

const DarkTheme: Theme = {
  dark: true,
  colors: {
    primary: colors.primary[400],      // Lighter blue for dark mode
    primaryLight: colors.primary[300],  // Very light blue
    primaryDark: colors.primary[600],   // Medium blue
    accent: colors.accent[400],         // Light Purple
    accentLight: colors.accent[300],    // Very Light Purple
    background: colors.neutral[950],    // Near Black
    surface: 'rgba(30, 30, 30, 0.9)',  // Translucent dark
    textPrimary: colors.neutral[50],    // Near White
    textSecondary: colors.neutral[400], // Light Grey
    success: colors.success,
    warning: colors.warning,
    error: colors.error,
    info: colors.info,
  },
  glass: {
    light: 'rgba(50, 50, 50, 0.7)',
    medium: glass.background.dark,
    dark: glass.background.ultraDark,
    ultraLight: 'rgba(50, 50, 50, 0.9)',
    blurAmount: glass.blur.medium,
  },
  shadows,
};

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const colorScheme = Appearance.getColorScheme();
  const [isDark, setIsDark] = useState(colorScheme === 'dark');

  const theme = isDark ? DarkTheme : LightTheme;

  const toggleTheme = () => {
    setIsDark(prev => !prev);
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
