import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: ['class'],
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        fondo: '#0a0c10',
        superficie: '#0f1318',
        borde: '#1e2530',
        cyan: '#00d4ff',
        violeta: '#7c3aed',
        verde: '#00ff88',
        amarillo: '#ffd700',
        rojo: '#ff4466',
        naranja: '#ff8c42',
        rosa: '#ec4899',
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'monospace'],
        ui: ['Syne', 'sans-serif'],
      },
      animation: {
        'pulse-dot': 'pulse 1.5s ease-in-out infinite',
        'fade-in': 'fadeIn 0.3s ease-in',
      },
      keyframes: {
        fadeIn: {
          from: { opacity: '0', transform: 'translateY(4px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
}

export default config
