import type { Config } from "tailwindcss"

const config: Config = {
  darkMode: "class",
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Agent Forge Brand Colors
        'ancient-gold': {
          DEFAULT: '#F59E0B',
          50: '#FFFBEB',
          100: '#FEF3C7',
          200: '#FDE68A',
          300: '#FCD34D',
          400: '#FBBF24',
          500: '#F59E0B',
          600: '#D97706',
          700: '#B45309',
          800: '#92400E',
          900: '#78350F',
          950: '#451A03'
        },
        'nuru-purple': {
          DEFAULT: '#7C3AED',
          50: '#F5F3FF',
          100: '#EDE9FE',
          200: '#DDD6FE',
          300: '#C4B5FD',
          400: '#A78BFA',
          500: '#8B5CF6',
          600: '#7C3AED',
          700: '#6D28D9',
          800: '#5B21B6',
          900: '#4C1D95',
          950: '#2E1065'
        },
        'ancient-bronze': {
          DEFAULT: '#CD7F32',
          50: '#FAF7F0',
          100: '#F4EDD9',
          200: '#E9DAB3',
          300: '#DDC387',
          400: '#D5AD64',
          500: '#CD7F32',
          600: '#B8722C',
          700: '#A36527',
          800: '#8E5A25',
          900: '#794E22'
        },
        'charcoal-anvil': '#36454F',
        'ember-inspiration': '#FF6B35',
        'steel-wisdom': '#708090',
        'forge-white': '#FEFEFE',
        'ancient-stone': '#F7F7F7',
        'shadow-depth': '#1A1A1A',
        
        // shadcn/ui color system
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'Consolas', 'monospace'],
      },
      animation: {
        'forge-glow': 'forge-glow 2s ease-in-out infinite alternate',
        'ancient-fade': 'ancient-fade 3s ease-in-out infinite',
        'ember-float': 'ember-float 3s ease-in-out infinite',
      },
      keyframes: {
        'forge-glow': {
          '0%, 100%': { 
            boxShadow: '0 0 5px rgba(245, 158, 11, 0.3)' 
          },
          '50%': { 
            boxShadow: '0 0 20px rgba(245, 158, 11, 0.6)' 
          }
        },
        'ancient-fade': {
          '0%': { opacity: '0.7' },
          '100%': { opacity: '1' }
        },
        'ember-float': {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' }
        }
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}

export default config