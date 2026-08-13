# Trust Para Todos — OG Image Template Specification

_Canonical template reference for all TrustParaTodos Open Graph images. Every OG image must follow this spec._

## Template Files

**Source templates:** `public/og-templates/og-{page}-gen.html`
**Render output:** `public/og-{page}.png` (per-page OG images)
**Default fallback:** `public/og-image.png` (legacy static image)
**Render method:** Playwright screenshots the `.og-card` element at 1200x630
**Render script:** `scripts/render-og-images.py`

## Dimensions

- **Size:** 1200 x 630 px (standard OG image)
- **Layout:** Split-panel, left text (~55%) + right visual (~45%)

## Brand Colors (from `src/styles/global.css`)

| Token | Hex | Usage in OG |
|---|---|---|
| Teal | `#0d7377` | Logo icon background, headline text, top accent band, step numbers |
| Teal-dark | `#0a5a5d` | (available, not currently used in OG) |
| Terracotta | `#dd7054` | Feature icon backgrounds, headline accent word, top accent band |
| Cream | `#faf5ed` | Card background (left panel) |
| Dark | `#1a1a2e` | Logo text color, body text |
| Text-body | `#3d3d4a` | Tagline/body text |
| Text-muted | `#7a7a88` | Footer URL text |
| White | `#FFFFFF` | Logo icon content, feature icon content |

## Logo (MUST match website header)

The website header (`src/layouts/BaseLayout.astro`) uses:
- **Container:** Teal (`#0d7377`) rounded square, `border-radius: 10px`, 44px
- **Icon:** Shield SVG from `public/assets/logo-shield.svg`, rendered in white + terracotta
- **Text:** "Trust Para Todos" in **Playfair Display** 700, 24px, dark (`#1a1a2e`)

The OG image logo matches this exactly. The shield SVG paths are embedded directly in the template HTML.

**CRITICAL:** The shield logo is the only approved brand mark. Never generate, substitute, or invent a different logo.

## Typography (from `src/styles/fonts.css` and `global.css`)

| Role | Font | Weight | Size in OG |
|---|---|---|---|
| Logo text | Playfair Display | 700 | 24px |
| Headline | Playfair Display | 700 | 52-58px, line-height 1.08 |
| Tagline/body | DM Sans | 400 | 18px, line-height 1.55 |
| Feature labels | DM Sans | 700 | 13px |
| Footer URL | DM Sans | 400 | 11px, letter-spacing 0.06em |

**Font loading:** Google Fonts via `<link>` in the HTML template:
```
https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:ital,wght@0,400;0,500;0,700;1,400&display=swap
```

## Layout Structure

```
+------------------------------------------------------------------+
| [5px teal top band] [2px terracotta band]                        |
|                                                                  |
|  [Logo]                    |                                     |
|  Trust Para Todos           |        Right Visual Panel           |
|                             |        (page-specific illustration   |
|  Headline (Playfair)        |         or photo)                    |
|  52-58px, teal +            |        560px x 630px                |
|  terracotta accent          |                                     |
|                             |                                     |
|  Tagline (DM Sans 18px)     |                                     |
|  dark gray                  |                                     |
|                             |                                     |
|  [feature] [feature] [feature]                                   |
|  terracotta icon + DM Sans 13px                                  |
|                             |                                     |
|  trustparatodos.com         |                                     |
|  (footer, 11px)             |                                     |
+------------------------------------------------------------------+
```

## Left Panel Elements

1. **Top accent bands:** 5px teal + 2px terracotta at very top
2. **Logo row:** Teal rounded square with white shield SVG + "Trust Para Todos" in Playfair Display 700
3. **Headline:** Playfair Display, 52-58px, teal. One word or phrase highlighted in terracotta.
4. **Tagline:** DM Sans 18px, dark gray (`#3d3d4a`), max-width 480px. One sentence describing the page.
5. **Feature pills:** Three features with terracotta icon squares (24px, border-radius 6px) + white SVG icons + DM Sans 700 13px labels. Default: "Protege tu hogar", "Todo en español", "100% en línea"
6. **Footer:** "trustparatodos.com" in DM Sans 11px, text-muted, letter-spacing 0.06em
7. **Subtle dot grid:** Radial gradient dots in terracotta at 3% opacity on left panel background

## Right Panel

- **Width:** 560px, height: 630px
- **Content:** Page-specific illustration or photo
- **Background:** When using an illustration (not photo): linear gradient `135deg, #e6f2f4 0%, #fdf0ec 100%`
- **Divider:** 1px teal gradient line between panels at 25% opacity

### Per-page right panel content:

| Page | Right Panel Content |
|---|---|
| Home (`/`) | Family photo (`hero-family.jpg`) |
| ¿Qué es? (`/que-es`) | Shield + house SVG illustration |
| Cómo funciona (`/como-funciona`) | 5-step numbered vertical list |
| Evaluación (`/evaluacion`) | CTA card with checkmark icon |
| FAQ (`/preguntas-frecuentes`) | 4 question cards with "?" marks |
| Testimonios (`/testimonios`) | 2 quote cards with customer testimonials |
| Asociaciones (`/asociaciones`) | 3 partner cards with icons |
| Contacto (`/contacto`) | Contact card with WhatsApp + email icons |

## Pages with Unique OG Images

| Page | OG File | Template |
|---|---|---|
| Homepage (`/`) | og-home.png | og-home-gen.html |
| ¿Qué es un trust? (`/que-es`) | og-que-es.png | og-que-es-gen.html |
| Cómo funciona (`/como-funciona`) | og-como-funciona.png | og-como-funciona-gen.html |
| Evaluación (`/evaluacion`) | og-evaluacion.png | og-evaluacion-gen.html |
| FAQ (`/preguntas-frecuentes`) | og-faq.png | og-faq-gen.html |
| Testimonios (`/testimonios`) | og-testimonios.png | og-testimonios-gen.html |
| Asociaciones (`/asociaciones`) | og-asociaciones.png | og-asociaciones-gen.html |
| Contacto (`/contacto`) | og-contacto.png | og-contacto-gen.html |
| Legal (`/legal`) | (pending) | Needs unique OG |
| Exito (`/exito`) | (pending) | Needs unique OG |
| Recomendación (`/recomendacion`) | (pending) | Needs unique OG |
| Pago (`/pago`) | (pending) | Needs unique OG |

## BaseLayout Integration

The `BaseLayout.astro` accepts an optional `ogImage` prop:

```astro
<BaseLayout
  title="..."
  description="..."
  canonicalPath="/que-es"
  ogImage="og-que-es.png"
>
```

If `ogImage` is omitted, it falls back to `og-image.png` (the legacy static image). Each public page has been wired with its per-page OG image filename.

## Render Command (Playwright)

```bash
cd /Users/socializerender/.openclaw/workspace/Kit/life/brands/TrustParaTodos/projects/trust-para-todos
python3 scripts/render-og-images.py
```

This renders all 8 per-page OG templates into PNG files in `public/`.

## Customizing for a New Page

1. **Copy** `og-template.html` (the blank template) to a new file (e.g., `og-legal-gen.html`)
2. **Update the headline** to the page title
3. **Update the tagline** to a one-sentence description of the page
4. **Customize feature pills** with page-relevant features
5. **Design the right panel** visual (illustration, cards, or photo)
6. **Add** the new page to the `OG_PAGES` dict in `scripts/render-og-images.py`
7. **Render** via the script
8. **Save** as `public/og-{slug}.png`
9. **Wire** in the page's `BaseLayout` call: `ogImage="og-{slug}.png"`

## Quality Checks

- [ ] Logo shield is white + terracotta inside teal square
- [ ] Logo text is "Trust Para Todos" in Playfair Display 700
- [ ] Headline uses Playfair Display
- [ ] Body/tagline uses DM Sans
- [ ] Colors match global.css tokens (teal, terracotta, cream)
- [ ] Output is exactly 1200x630
- [ ] Right panel is page-relevant (not the default homepage visual)
- [ ] Feature pills use terracotta icon squares with white SVG icons
- [ ] "trustparatodos.com" in footer
- [ ] Text is crisp and readable (no font loading issues)

## Right Panel Visual Direction (Jeff preference, June 2026)

Current set uses SVG illustrations and card-based graphics. Jeff has approved these but prefers **AI-generated photos** for future OG images. When creating new page OGs or replacing existing ones, use AI-generated professional photography (family scenes, legal office settings, notary signings, etc.) for the right panel instead of vector illustrations.

## What NOT to Do

- Never use `image_generate` for the full OG image (it garbles text). Use it only for the right panel photo, then compose in the HTML template and render with Playwright.
- Never use a different logo. The shield SVG is the only approved brand mark.
- Never change the split ratio. Left ~55% text, right ~45% visual.
- Never use Inter or other sans-serif fonts. TPT uses DM Sans + Playfair Display.
- Never put text on the right visual panel (except labels in card-based visuals like steps, FAQs, testimonials).