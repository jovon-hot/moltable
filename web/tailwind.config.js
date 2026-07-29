/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // Design tokens from DESIGN.md
        'ln-bg': '#08090a',
        'ln-surface': '#0f1011',
        'ln-raised': '#191a1b',
        'ln-hover': '#23252a',
        'ln-text': '#f7f8f8',
        'ln-secondary': '#d0d6e0',
        'ln-tertiary': '#8a8f98',
        'ln-quaternary': '#62666d',
        'ln-accent': '#7170ff',
        'ln-accent-hover': '#828fff',
        'ln-accent-muted': 'rgba(113,112,255,0.12)',
        'ln-accent-glow': 'rgba(113,112,255,0.15)',
        'ln-border': 'rgba(255,255,255,0.08)',
        'ln-border-subtle': 'rgba(255,255,255,0.05)',
        'ln-border-accent': '#7170ff',
        'ln-btn-bg': 'rgba(255,255,255,0.04)',
        'ln-success': '#27a644',
        'ln-warning': '#eab308',
        'ln-error': '#f87171',
        'ln-info': '#7170ff',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      borderRadius: {
        'btn': '6px',
        'card': '8px',
        'panel': '12px',
        'pill': '9999px',
      },
      fontWeight: {
        'body': '400',
        'ui': '510',
        'heading': '590',
      },
      boxShadow: {
        'border': '0 0 0 1px rgba(255,255,255,0.08)',
        'border-subtle': '0 0 0 1px rgba(255,255,255,0.05)',
        'border-accent': '0 0 0 1px #7170ff',
        'card': '0 0 0 1px rgba(255,255,255,0.08)',
        'card-hover': '0 0 0 1px rgba(255,255,255,0.12), 0 4px 12px rgba(0,0,0,0.3)',
        'accent-glow': '0 0 0 1px #7170ff, 0 0 20px rgba(113,112,255,0.15)',
        'focus': '0 0 0 2px #7170ff, 0 0 0 4px #08090a',
      },
    },
  },
  plugins: [],
}
