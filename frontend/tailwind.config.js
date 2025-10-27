/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#667eea',
          dark: '#5568d3',
          pale: '#e0e7ff',
        },
        secondary: {
          DEFAULT: '#764ba2',
          dark: '#5f3d84',
          pale: '#f3e8ff',
        },
        bg: {
          DEFAULT: '#ffffff',
          alt: '#f5f5f7',
          soft: '#fafafa',
        },
        text: {
          primary: '#1a202c',
          secondary: '#718096',
          tertiary: '#86868b',
          muted: '#a0aec0',
        },
        border: {
          light: '#e2e8f0',
          DEFAULT: '#cbd5e0',
        },
        success: '#48bb78',
        warning: '#ed8936',
        error: '#f56565',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      boxShadow: {
        card: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        'card-hover': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
      },
    },
  },
  plugins: [],
}
