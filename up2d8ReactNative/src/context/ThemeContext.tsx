import React, { createContext, useState, useContext, ReactNode } from 'react';
import { Appearance, ColorSchemeName } from 'react-native';

interface ThemeColors {
  primary: string;
  accent: string;
  background: string;
  surface: string;
  textPrimary: string;
  textSecondary: string;
  // Add more colors as needed
}

interface Theme {
  dark: boolean;
  colors: ThemeColors;
}

const LightTheme: Theme = {
  dark: false,
  colors: {
    primary: '#6200EE', // Deep Purple
    accent: '#03DAC6',  // Teal
    background: '#F5F5F5', // Light Grey
    surface: '#FFFFFF',   // White
    textPrimary: '#212121', // Dark Grey
    textSecondary: '#757575', // Medium Grey
  },
};

const DarkTheme: Theme = {
  dark: true,
  colors: {
    primary: '#BB86FC', // Light Purple
    accent: '#03DAC6',  // Teal
    background: '#121212', // Dark Grey
    surface: '#1E1E1E',   // Even Darker Grey
    textPrimary: '#FFFFFF', // White
    textSecondary: '#B0B0B0', // Light Grey
  },
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
