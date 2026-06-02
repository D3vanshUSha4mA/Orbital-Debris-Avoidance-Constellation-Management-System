/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        space: '#050a15',
        panel: 'rgba(10, 16, 30, 0.75)',
        hud: {
          cyan: '#00f3ff',
          blue: '#0d6efd',
          warn: '#ffaa00',
          crit: '#ff2a2a',
          dim: 'rgba(0, 243, 255, 0.2)'
        }
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', 'monospace']
      },
      animation: {
        'pulse-fast': 'pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'scanline': 'scanline 8s linear infinite',
      },
      keyframes: {
        scanline: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100vh)' }
        }
      }
    },
  },
  plugins: [],
}