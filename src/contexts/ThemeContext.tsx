import React, { createContext, useContext, useEffect, useState } from 'react';

type Theme = 'blue' | 'black' | 'green' | 'purple';

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<Theme>(() => {
    const stored = localStorage.getItem('app-theme');
    return (stored as Theme) || 'blue';
  });

  useEffect(() => {
    const root = document.documentElement;
    
    // Remove all theme classes
    root.classList.remove('theme-blue', 'theme-black', 'theme-green', 'theme-purple');
    
    // Add current theme class
    root.classList.add(`theme-${theme}`);
    
    // Store preference
    localStorage.setItem('app-theme', theme);
  }, [theme]);

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme);
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
