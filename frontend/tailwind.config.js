/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // ComChat brand palette - refined blue to orange
        brand: {
          50: '#fff7ed',
          100: '#ffedd5',
          200: '#fed7aa',
          300: '#fdba74',
          400: '#fb923c',
          500: '#f97316',
          600: '#ea580c',
          700: '#c2410c',
          800: '#9a3412',
          900: '#7c2d12',
          950: '#431407',
        },
        // Refined Apple-style grays with perfect contrast
        gray: {
          25: '#fcfcfd',
          50: '#f9fafb',
          100: '#f3f4f6',
          200: '#e5e7eb',
          300: '#d1d5db',
          400: '#9ca3af',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
          800: '#1f2937',
          900: '#111827',
          950: '#030712',
        },
        // New dark gray-black clean palette
        dark: {
          25: '#fefefe',
          50: '#fafafa',
          100: '#f0f0f0',
          200: '#e4e4e4',
          300: '#d1d1d1',
          400: '#a3a3a3',
          500: '#737373',
          600: '#525252',
          700: '#404040',
          800: '#262626',
          900: '#171717',
          950: '#0a0a0a',
        },
        // Modern Apple-style accent colors
        accent: {
          blue: '#007AFF',
          indigo: '#5856D6',
          purple: '#AF52DE',
          pink: '#FF2D92',
          red: '#FF3B30',
          orange: '#FF9500',
          yellow: '#FFCC00',
          green: '#30D158',
          mint: '#00C7BE',
          teal: '#59C4C4',
          cyan: '#55BEF0',
        },
        // Surface colors for modern layering
        surface: {
          primary: '#ffffff',
          secondary: '#f9fafb',
          tertiary: '#f3f4f6',
          elevated: 'rgba(255, 255, 255, 0.95)',
          overlay: 'rgba(0, 0, 0, 0.05)',
        }
      },
      fontFamily: {
        'system': ['-apple-system', 'BlinkMacSystemFont', 'SF Pro Display', 'SF Pro Text', 'Helvetica Neue', 'Roboto', 'Arial', 'sans-serif'],
        'display': ['-apple-system', 'BlinkMacSystemFont', 'SF Pro Display', 'system-ui', 'sans-serif'],
        'body': ['-apple-system', 'BlinkMacSystemFont', 'SF Pro Text', 'system-ui', 'sans-serif'],
        'mono': ['SF Mono', 'Menlo', 'Monaco', 'Cascadia Code', 'Roboto Mono', 'Courier New', 'monospace'],
      },
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
        '5xl': ['3rem', { lineHeight: '1' }],
        '6xl': ['3.75rem', { lineHeight: '1' }],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      borderRadius: {
        'none': '0',
        'sm': '0.25rem',
        'DEFAULT': '0.375rem',
        'md': '0.5rem',
        'lg': '0.75rem',
        'xl': '1rem',
        '2xl': '1.5rem',
        '3xl': '2rem',
        'full': '9999px',
      },
      boxShadow: {
        'xs': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'sm': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        'DEFAULT': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'md': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        'lg': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        'xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
        '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
        'inner': 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
        'apple': '0 4px 16px rgba(0, 0, 0, 0.12)',
        'apple-lg': '0 8px 32px rgba(0, 0, 0, 0.12)',
        'glass': '0 8px 32px rgba(31, 38, 135, 0.37)',
      },
      animation: {
        'fade-in': 'fadeIn 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
        'fade-in-up': 'fadeInUp 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
        'slide-up': 'slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        'slide-down': 'slideDown 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        'scale-in': 'scaleIn 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
        'bounce-gentle': 'bounceGentle 0.6s cubic-bezier(0.4, 0, 0.2, 1)',
        'pulse-subtle': 'pulseSubtle 2s cubic-bezier(0.4, 0, 0.2, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeInUp: {
          '0%': { 
            opacity: '0',
            transform: 'translateY(16px)',
          },
          '100%': { 
            opacity: '1',
            transform: 'translateY(0)',
          },
        },
        slideUp: {
          '0%': { 
            transform: 'translateY(8px)', 
            opacity: '0' 
          },
          '100%': { 
            transform: 'translateY(0)', 
            opacity: '1' 
          },
        },
        slideDown: {
          '0%': { 
            transform: 'translateY(-8px)', 
            opacity: '0' 
          },
          '100%': { 
            transform: 'translateY(0)', 
            opacity: '1' 
          },
        },
        scaleIn: {
          '0%': { 
            transform: 'scale(0.95)', 
            opacity: '0' 
          },
          '100%': { 
            transform: 'scale(1)', 
            opacity: '1' 
          },
        },
        bounceGentle: {
          '0%, 100%': { 
            transform: 'translateY(0)',
            animationTimingFunction: 'cubic-bezier(0.8, 0, 1, 1)',
          },
          '50%': { 
            transform: 'translateY(-4px)',
            animationTimingFunction: 'cubic-bezier(0, 0, 0.2, 1)',
          },
        },
        pulseSubtle: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.8' },
        },
      },
      backdropBlur: {
        'xs': '2px',
        'sm': '4px',
        'md': '8px',
        'lg': '12px',
        'xl': '16px',
        '2xl': '24px',
        '3xl': '40px',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'gradient-apple': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'gradient-brand': 'linear-gradient(135deg, #0284c7 0%, #f97316 100%)',
        'gradient-surface': 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
        'gradient-hero': 'linear-gradient(135deg, #f0f9ff 0%, #fff7ed 50%, #fed7aa 100%)',
        'gradient-mesh': 'radial-gradient(at 40% 20%, #0284c7 0%, transparent 50%), radial-gradient(at 80% 0%, #f97316 0%, transparent 50%), radial-gradient(at 0% 50%, #fb923c 0%, transparent 50%)',
        'gradient-glass': 'linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%)',
        'gradient-dark-blur': 'radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.15) 0%, transparent 50%), radial-gradient(circle at 40% 40%, rgba(120, 119, 198, 0.15) 0%, transparent 50%)',
        'gradient-dark-hero': 'linear-gradient(135deg, #0a0a0a 0%, #171717 25%, #262626 50%, #171717 75%, #0a0a0a 100%)',
      },
      blur: {
        '4xl': '72px',
        '5xl': '96px',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}