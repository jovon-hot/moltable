/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // Moltable VI v3 — Indigo + Coral · #0D0D14 deep dark
        'ln-bg': '#0D0D14',
        'ln-surface': '#14141E',
        'ln-raised': '#1A1A26',
        'ln-hover': '#1F1F2D',
        'ln-text': '#F5F4F8',
        'ln-secondary': '#A8A5B8',
        'ln-tertiary': '#85829E',
        'ln-quaternary': '#6E6B80',
        'ln-accent': '#4338CA',
        'ln-accent-hover': '#3730A3',
        'ln-accent-muted': 'rgba(99,102,241,0.12)',
        'ln-accent-glow': 'rgba(99,102,241,0.15)',
        'ln-border': 'rgba(255,255,255,0.06)',
        'ln-border-subtle': 'rgba(255,255,255,0.04)',
        'ln-border-accent': 'rgba(99,102,241,0.25)',
        'ln-btn-bg': 'rgba(255,255,255,0.04)',
        'ln-success': '#22C55E',
        'ln-warning': '#FB6B4B',
        'ln-error': '#EF4444',
        'ln-info': '#6366F1',
      },
      fontFamily: {
        sans: ['Geist', '-apple-system', 'SF Pro Display', 'system-ui', 'sans-serif'],
        mono: ['Geist Mono', 'SF Mono', 'Fira Code', 'monospace'],
      },
      borderRadius: {
        'btn': '8px',
        'card': '12px',
        'panel': '16px',
        'pill': '9999px',
      },
      fontWeight: {
        'body': '400',
        'ui': '500',
        'heading': '600',
      },
      boxShadow: {
        'border': '0 0 0 1px rgba(255,255,255,0.06)',
        'border-subtle': '0 0 0 1px rgba(255,255,255,0.04)',
        'border-accent': '0 0 0 1px rgba(99,102,241,0.25)',
        'card': '0 0 0 1px rgba(255,255,255,0.06)',
        'card-hover': '0 0 0 1px rgba(99,102,241,0.15), 0 4px 12px rgba(0,0,0,0.3)',
        'accent-glow': '0 0 0 1px rgba(99,102,241,0.25), 0 0 20px rgba(99,102,241,0.12)',
        'focus': '0 0 0 2px #6366F1, 0 0 0 4px #0D0D14',
      },
    },
  },
  plugins: [],
}
