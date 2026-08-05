# DESIGN.md — Moltable.ai

> Generated: 2026-08-05 · Source: VI v3 Indigo+Coral · Impeccable-audited

---

## Brand Identity

- **Name:** Moltable.ai
- **Tagline:** AI Identity Sync — One Registration, Every AI Knows You
- **Tagline (ZH):** 一次注册，所有 AI 认识你
- **Category:** AI Infrastructure / Developer Tools / Identity Layer
- **Metaphor:** "iCloud for AI Agents"

## Color System

### Core Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `--primary` | `#4338CA` | Primary buttons, brand marks, focus rings |
| `--primary-hover` | `#3730A3` | Button hover states |
| `--primary-glow` | `rgba(99,102,241,0.12)` | Glow effects, subtle backgrounds |
| `--accent` | `#FB6B4B` | Warm emphasis, decorative, secondary CTAs |
| `--accent-hover` | `#E85A3A` | Accent hover states |
| `--accent-glow` | `rgba(251,107,75,0.1)` | Warm glow effects |

### Surface Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `--bg` | `#0D0D14` | Page background |
| `--surface` | `#14141E` | Cards, panels, raised surfaces |
| `--raised` | `#1A1A26` | Hover states, elevated elements |
| `--border` | `rgba(255,255,255,0.06)` | Default borders |
| `--border-subtle` | `rgba(255,255,255,0.04)` | Subtle dividers |
| `--border-glow` | `rgba(99,102,241,0.15)` | Accent borders on hover |

### Text Colors

| Token | Hex | WCAG | Usage |
|-------|-----|------|-------|
| `--text` | `#F5F4F8` | AAA (15:1) | Primary text on dark bg |
| `--text-secondary` | `#A8A5B8` | AA (7:1) | Secondary text, descriptions |
| `--text-tertiary` | `#85829E` | AA (4.5:1) | Muted text, placeholders |

### Gradient Tokens

```
--gradient-brand: linear-gradient(90deg, #4338CA, #FB6B4B)
--gradient-glow: radial-gradient(circle, rgba(99,102,241,0.1), transparent 60%)
--gradient-divider: linear-gradient(90deg, transparent, #4338CA, #FB6B4B, #4338CA, transparent)
```

## Typography

| Token | Font | Weight | Size | Usage |
|-------|------|--------|------|-------|
| `--font-ui` | Geist | 400-600 | 13-15px | UI, buttons, forms |
| `--font-body` | Geist | 400 | 14-16px | Body text |
| `--font-heading` | Geist | 700-800 | 18-58px | Headings, hero |
| `--font-mono` | Geist Mono | 400 | 12-14px | Code, API keys |

Font stack: `Geist, -apple-system, 'SF Pro Display', system-ui, sans-serif`

## Component Tokens

### Buttons

```
--btn-primary-bg: #4338CA
--btn-primary-text: #FFFFFF
--btn-primary-hover: #3730A3
--btn-primary-glow: 0 0 0 1px rgba(99,102,241,0.3)

--btn-outline-bg: rgba(255,255,255,0.04)
--btn-outline-border: rgba(255,255,255,0.08)
--btn-outline-text: #A8A5B8

--btn-radius: 8px · 12px
--btn-padding: 13px 28px (lg) · 8px 18px (sm)
```

### Cards

```
--card-bg: #14141E
--card-border: rgba(255,255,255,0.06)
--card-hover-border: rgba(99,102,241,0.15)
--card-hover-lift: -2px
--card-radius: 12px
--card-padding: 24px
```

### Stats

```
--stat-bg: #14141E
--stat-border: rgba(255,255,255,0.06)
--stat-hover-glow: linear-gradient(90deg, transparent, #6366F1, transparent)
--stat-value-indigo: #6366F1
--stat-value-coral: #FB6B4B
```

## Spacing Scale

```
xs: 4px · sm: 8px · md: 12px · lg: 16px
xl: 24px · 2xl: 32px · 3xl: 48px · 4xl: 64px
section-padding: 80px (y) · 24px (x)
```

## Design Principles

1. **No pure black** — background always tinted (#0D0D14 has blue undertone)
2. **Coral decorative only** — never as text on dark bg (WCAG fail at 4.2:1)
3. **Gradient as rhythm** — brand-gradient dividers between sections
4. **Hover tells story** — cards lift + border glow, never just color change
5. **Indigo = AI/System** — Coral = Human/Identity
6. **No purple-blue gradients** — Impeccable audit banned
7. **Geist only** — no Inter, no system defaults (Impeccable anti-pattern)

## Logo Assets

| File | Variant | Usage |
|------|---------|-------|
| `logo-brand.svg` | Indigo | Primary branding |
| `logo-white.svg` | White | Dark backgrounds |
| `logo-brand.png` | Indigo PNG | OG images, email |
| `favicon.svg` | — | Browser tab icon |
| `og-image.png` | 1200×630 | Social sharing |

## Implementation

- **Framework:** Next.js 14 (App Router)
- **Styling:** Tailwind + CSS custom properties
- **Icons:** Lucide React
- **Colors:** All in :root CSS variables → overridable by theme
- **Security:** CSP, HSTS, X-Frame-Options, Referrer-Policy
- **Accessibility:** WCAG AAA (text), AA (muted), focus-visible rings
