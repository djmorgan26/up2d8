
import React from 'react';
import { useTheme } from '../hooks/useTheme';

const MoonIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 24 24" fill="currentColor"><path d="M12.3 4.9c.4-.2.6-.7.4-1.1-.2-.4-.7-.6-1.1-.4C7.7 4.9 5 8.1 5 12c0 3.9 2.7 7.1 6.2 8.6.4.2.9 0 1.1-.4.2-.4 0-.9-.4-1.1C9.2 18.1 7 15.3 7 12c0-2.5 1.5-4.7 3.7-5.8.4-.2.9 0 1.1.4.2.4 0 .9-.4 1.1-1.5.8-2.4 2.3-2.4 4.1 0 2.5 2 4.5 4.5 4.5s4.5-2 4.5-4.5c0-1.8-.9-3.3-2.4-4.1z"/></svg>
);

const themes = [
    { name: 'dark', icon: <MoonIcon /> },
];

export const ThemeSwitcher: React.FC = () => {
  const { theme, setTheme } = useTheme();

  return (
    <div className="flex items-center p-1 rounded-full" style={{ backgroundColor: 'var(--background)' }}>
      {themes.map((t) => (
        <button
          key={t.name}
          onClick={() => setTheme('dark')}
          className={`p-1.5 rounded-full transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2`}
          style={{
            backgroundColor: theme === t.name ? 'var(--surface)' : 'transparent',
            color: theme === t.name ? 'var(--primary)' : 'var(--text-secondary)',
            boxShadow: theme === t.name ? '0 1px 2px 0 rgba(0, 0, 0, 0.05)' : 'none',
            ringColor: 'var(--primary)'
          }}
          aria-label={`Switch to ${t.name} theme`}
          aria-pressed={theme === t.name}
        >
          {t.icon}
        </button>
      ))}
    </div>
  );
};