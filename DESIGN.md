---
name: Moltable Design System
version: 1.0.0
description: >
  Moltable is an AI Identity Layer — a cross-platform system that lets any
  MCP-compatible AI agent load the user's identity, preferences, and personas.
  The design system reflects precision engineering and trust.

colors:
  primary: "#7170ff"
  background:
    darkest: "#08090a"
    panel: "#0f1011"
    raised: "#191a1b"
    hover: "#23252a"
  text:
    primary: "#f7f8f8"
    secondary: "#d0d6e0"
    tertiary: "#8a8f98"
    quaternary: "#62666d"
  accent:
    DEFAULT: "#7170ff"
    hover: "#828fff"
    muted: "rgba(113,112,255,0.12)"
    glow: "rgba(113,112,255,0.15)"
  semantic:
    success: "#27a644"
    warning: "#eab308"
    error: "#f87171"
    info: "#7170ff"
  border:
    DEFAULT: "rgba(255,255,255,0.08)"
    subtle: "rgba(255,255,255,0.05)"
    accent: "#7170ff"

typography:
  fontFamily:
    sans: "Inter, system-ui, -apple-system, 'Segoe UI', sans-serif"
    mono: "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace"
    chinese: "'PingFang SC', 'Noto Sans SC', 'Microsoft YaHei', sans-serif"
  weight:
    body: 400
    ui: 510
    heading: 590
  scale:
    display:
      fontSize: 3rem
      lineHeight: 1.0
      letterSpacing: "-0.7px"
      weight: 590
    h1:
      fontSize: 2rem
      lineHeight: 1.13
      letterSpacing: "-0.4px"
      weight: 590
    h2:
      fontSize: 1.5rem
      lineHeight: 1.33
      letterSpacing: "-0.3px"
      weight: 590
    h3:
      fontSize: 1.25rem
      lineHeight: 1.33
      letterSpacing: "-0.24px"
      weight: 590
    body-lg:
      fontSize: 1.125rem
      lineHeight: 1.7
      letterSpacing: normal
      weight: 400
    body:
      fontSize: 1rem
      lineHeight: 1.5
      letterSpacing: normal
      weight: 400
    body-sm:
      fontSize: 0.875rem
      lineHeight: 1.5
      letterSpacing: normal
      weight: 400
    caption:
      fontSize: 0.8125rem
      lineHeight: 1.5
      letterSpacing: "-0.13px"
      weight: 400
    label:
      fontSize: 0.75rem
      lineHeight: 1.4
      letterSpacing: normal
      weight: 510

rounded:
  btn: 6px
  card: 8px
  panel: 12px
  pill: 9999px

spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  2xl: 48px
  3xl: 64px

shadow:
  border: "0 0 0 1px rgba(255,255,255,0.08)"
  border-subtle: "0 0 0 1px rgba(255,255,255,0.05)"
  border-accent: "0 0 0 1px #7170ff"
  card: "0 0 0 1px rgba(255,255,255,0.08)"
  card-hover: "0 0 0 1px rgba(255,255,255,0.12), 0 4px 12px rgba(0,0,0,0.3)"
  accent-glow: "0 0 0 1px #7170ff, 0 0 20px rgba(113,112,255,0.15)"
  focus: "0 0 0 2px #7170ff, 0 0 0 4px #08090a"

motion:
  duration:
    fast: 150ms
    normal: 200ms
    slow: 300ms
  easing:
    DEFAULT: "cubic-bezier(0.4, 0, 0.2, 1)"
    spring: "cubic-bezier(0.34, 1.56, 0.64, 1)"
---
# Moltable Design System

## Philosophy

**Precision over decoration.** Moltable's dark interface treats darkness as the native medium. Content emerges from near-black backgrounds through carefully calibrated luminance steps, not through color. Every element earns its pixel.

### Core Principles

1. **Darkness as space** — `#08090a` is not absence; it's the canvas. Empty space communicates confidence.
2. **Shadow as border** — `box-shadow: 0 0 0 1px` replaces traditional borders. Softer, more precise, elevation-aware.
3. **One accent, disciplined use** — `#7170ff` appears only on CTAs, active states, and brand elements. Never decorative.
4. **Three weights, strict roles** — 400 reads, 510 navigates, 590 announces. No bold.
5. **Compression at scale** — Display text uses negative letter-spacing. The tension between dense type and generous space creates rhythm.

### Typography

Inter is the primary typeface with `font-feature-settings: 'cv01', 'ss03'` (Linear-inspired geometric alternates). The 510 weight is Moltable's signature — sitting between regular and medium, it creates subtle emphasis without heaviness.

Chinese text falls back to PingFang SC → Noto Sans SC → Microsoft YaHei. CJK rendering requires careful x-height alignment with Inter.

### Color

The palette is almost entirely achromatic — cool grays on near-black. The single chromatic accent `#7170ff` (indigo-violet) is used sparingly:
- **CTA buttons:** solid `#7170ff` background
- **Active states:** `rgba(113,112,255,0.12)` background + `0 0 0 1px #7170ff` border
- **Links:** `#7170ff` text
- **Focus rings:** `0 0 0 2px #7170ff`

Semantic colors (success green, warning yellow, error red) appear only in status contexts.

### Elevation

Depth is communicated through background luminance stepping, not shadow darkness:

| Level | Background | Use |
|-------|-----------|-----|
| Flat | `#08090a` | Page background |
| Surface | `#0f1011` | Panels, sidebar |
| Raised | `#191a1b` | Cards, dropdowns |
| Hover | `#23252a` | Hovered cards |

On dark surfaces, traditional shadows are invisible. Moltable uses semi-transparent white borders as the primary depth indicator.

### Motion

Motion serves clarity, not theater:
- `150ms` for micro-interactions (hover, focus)
- `200ms` for state transitions (expand, collapse)
- `300ms` for page transitions
- `prefers-reduced-motion` respected globally

## Component Patterns

### Button
- Primary: `#7170ff` bg, `#fff` text, 6px radius, `font-weight: 510`
- Secondary: `rgba(255,255,255,0.04)` bg, `0 0 0 1px rgba(255,255,255,0.08)` shadow, 6px radius
- Ghost: transparent, hover `rgba(255,255,255,0.04)`
- Disabled: `opacity: 0.5`, `cursor: not-allowed`

### Card
- Background: `#0f1011`
- Border: `0 0 0 1px rgba(255,255,255,0.08)` shadow
- Radius: 8px
- Padding: 20px (5 in Tailwind)
- Hover: `0 0 0 1px rgba(255,255,255,0.12), 0 4px 12px rgba(0,0,0,0.3)`

### Input
- Background: `#0f1011`
- Border: `0 0 0 1px rgba(255,255,255,0.08)` shadow
- Focus: `0 0 0 1px #7170ff`
- Radius: 6px
- Placeholder: `#8a8f98`

### Navigation
- Top bar: `rgba(8,9,10,0.85)` + `backdrop-blur-sm`, sticky
- Sidebar: `#0f1011`, 208px width
- Active link: `rgba(113,112,255,0.12)` bg + `0 0 0 1px rgba(113,112,255,0.2)` border + `#828fff` text

## Accessibility

- All interactive elements have visible `:focus-visible` rings
- Color contrast meets WCAG AA minimum (4.5:1 for text)
- Touch targets minimum 44px (buttons are `py-2.5` ≈ 40px)
- `aria-label` on icon-only controls
- `role="alert"` on toast notifications
- `aria-current="page"` on active navigation links
- Respects `prefers-reduced-motion`
