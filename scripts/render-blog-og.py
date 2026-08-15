#!/usr/bin/env python3
"""
Trust Para Todos — Blog OG Image Generator

Generates per-article OG images (1200x630) using the two-column template:
- Left panel: logo, headline, tagline, feature pills, URL
- Right panel: article hero photo

Usage:
  cd /Users/socializerender/.openclaw/workspace/Kit/life/brands/TrustParaTodos/projects/trust-para-todos
  python3 scripts/render-blog-og.py
"""

import os
import html
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "public" / "og-templates"
OUTPUT_DIR = PROJECT_ROOT / "public"

# Blog article OG image config
BLOG_ARTICLES = [
    {
        "slug": "que-es-trust-revocable",
        "headline": "¿Qué es un trust<br><span class='terracotta'>revocable?</span>",
        "tagline": "La guía completa en español sobre trusts revocables: cómo funcionan, cuánto cuestan y por qué protegen a tu familia mejor que un testamento.",
        "photo": "../images/blog/01-hero-family-home.jpg",
        "features": ["Protege tu hogar", "Todo en español", "100% en línea"],
    },
    {
        "slug": "como-crear-trust-online",
        "headline": "Cómo crear un trust<br><span class='terracotta'>online en español</span>",
        "tagline": "Guía paso a paso para crear tu trust online. Sin abogado, sin complicaciones, sin gastos innecesarios.",
        "photo": "../images/blog/02-hero-documents.jpg",
        "features": ["Paso a paso", "Sin abogado", "$997 total"],
    },
    {
        "slug": "seguro-vida-trust",
        "headline": "Seguro de vida + trust:<br><span class='terracotta'>protección completa</span>",
        "tagline": "Un trust y un seguro de vida funcionan juntos. Descubre cómo combinarlos para máxima protección familiar.",
        "photo": "../images/blog/03-hero-family-protection.jpg",
        "features": ["Protección total", "Para hispanos", "En español"],
    },
    {
        "slug": "trust-vs-testamento",
        "headline": "Trust vs testamento:<br><span class='terracotta'>¿cuál es mejor?</span>",
        "tagline": "Descubre las diferencias entre trust y testamento. Cuál te conviene según tu casa, hijos y patrimonio.",
        "photo": "../images/blog/04-hero-senior-couple.jpg",
        "features": ["Comparativa", "Caso real", "Evita el probate"],
    },
    {
        "slug": "cuanto-cuesta-fideicomiso",
        "headline": "¿Cuánto cuesta un<br><span class='terracotta'>fideicomiso?</span>",
        "tagline": "Comparativa 2026: de $0 a $5,000. Abogados, plantillas y servicios guiados con precios reales.",
        "photo": "../images/blog/05-hero-financial-planning.jpg",
        "features": ["Precios reales", "Comparativa", "Sin sorpresas"],
    },
    {
        "slug": "necesito-abogado-trust",
        "headline": "¿Necesito un abogado<br><span class='terracotta'>para un trust?</span>",
        "tagline": "La verdad sobre si necesitas un abogado para hacer un trust. La respuesta corta: no en la mayoría de los casos.",
        "photo": "../images/blog/06-hero-consultation.jpg",
        "features": ["La verdad", "3 opciones", "$997 vs $5,000"],
    },
    {
        "slug": "que-es-probate-como-evitarlo",
        "headline": "¿Qué es el probate<br><span class='terracotta'>y cómo evitarlo?</span>",
        "tagline": "Guía completa sobre probate en español: qué es, cuánto cuesta (3-7% del patrimonio) y 4 formas de evitarlo.",
        "photo": "../images/blog/07-hero-courtroom.jpg",
        "features": ["En español", "4 soluciones", "Evita el probate"],
    },
    {
        "slug": "fideicomiso-revocable-vs-irrevocable",
        "headline": "Revocable vs<br><span class='terracotta'>irrevocable</span>",
        "tagline": "Diferencias explicadas: control, impuestos, protección de activos y cuál trust te conviene según tu situación.",
        "photo": "../images/blog/08-hero-family-property.jpg",
        "features": ["Tabla comparativa", "Guía de decisión", "En español"],
    },
]

# SVG icons for feature pills
ICONS = {
    "Protege tu hogar": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>',
    "Todo en español": '<path d="M12 7v14"></path><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"></path>',
    "100% en línea": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"></path>',
    "Paso a paso": '<path d="M9 11l3 3L22 4"></path><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>',
    "Sin abogado": '<path d="M9 11l3 3L22 4"></path><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>',
    "$997 total": '<path d="M12 1v22"></path><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>',
    "Protección total": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>',
    "Para hispanos": '<path d="M12 7v14"></path><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"></path>',
    "En español": '<path d="M12 7v14"></path><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"></path>',
    "Comparativa": '<path d="M3 3v18h18"></path><path d="M7 12l4-4 4 4 5-5"></path>',
    "Caso real": '<path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path>',
    "Evita el probate": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"></path>',
    "Precios reales": '<path d="M12 1v22"></path><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>',
    "Sin sorpresas": '<path d="M9 11l3 3L22 4"></path><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>',
    "La verdad": '<circle cx="12" cy="12" r="10"></circle><path d="M12 16v-4"></path><path d="M12 8h.01"></path>',
    "3 opciones": '<path d="M3 3v18h18"></path><path d="M7 12l4-4 4 4 5-5"></path>',
    "$997 vs $5,000": '<path d="M12 1v22"></path><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>',
    "4 soluciones": '<path d="M9 11l3 3L22 4"></path><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>',
    "Tabla comparativa": '<path d="M3 3v18h18"></path><path d="M7 12l4-4 4 4 5-5"></path>',
    "Guía de decisión": '<circle cx="12" cy="12" r="10"></circle><path d="M12 16v-4"></path><path d="M12 8h.01"></path>',
}

# Shield SVG (embedded from logo)
SHIELD_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="728 627 595 784" width="26" height="26">
          <path fill="#FFFFFF" d="M1024.64 851.874c1.19 1.309 5.85 18.696 6.73 21.981 32.24 119.945 137.1 216.195 263.61 224.435a276.6 276.6 0 0 1-77.78 196.15 266.83 266.83 0 0 1-190.24 80.57c-156.649.66-271.141-122.21-271.942-276.7 42.284-2.42 90.994-18.68 127.129-41.13 78.601-48.84 120.903-117.6 142.493-205.306"/>
          <path fill="#dd7054" d="M1024.39 661.627c2.77 2.473 14.15 22.741 17.37 27.738 57.84 89.691 146.38 145.464 253.32 156.885v51.204c-2.02-.035-4.05-.091-6.07-.168-27.8-1.075-56.54-7.094-83.04-15.266-75.6-23.317-127.7-62.219-180.7-119.365-13.79 12.202-25.384 27.395-41.032 40.81-64.077 54.935-143.701 91.354-228.845 93.673-.659-16.165-.339-34.557-.422-50.892 27.064-3.184 48.112-6.703 74.323-15.376a341.33 341.33 0 0 0 195.096-169.243"/>
          <path fill="#dd7054" d="M1079.55 869.978c76.22 45.234 124.88 68.339 215.31 74.001l.13 107.301a238.5 238.5 0 0 1-127.32-51.329c-34.42-27.618-60.22-61.681-78.23-101.823-3.26-7.284-9.03-20.283-9.89-28.15M970.321 868.86l.946.279c.577 4.809-6.637 20.69-8.886 25.843-30.099 68.938-85.903 122.438-157.447 146.668-15.051 5.1-31.185 7.46-47.094 9.95l-1.825-1.12c-.93-8.15-.24-29.18-.194-38.23l-.016-67.592a412.3 412.3 0 0 0 214.516-75.798"/>
        </svg>'''

def generate_og_html(article):
    """Generate OG image HTML for a blog article."""
    slug = article["slug"]
    
    # Feature pills
    feature_html = ""
    for feat in article["features"]:
        icon_path = ICONS.get(feat, '<circle cx="12" cy="12" r="10"></circle>')
        feature_html += f'''<div class="feature">
        <div class="feature-icon"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">{icon_path}</svg></div>
        {html.escape(feat)}
      </div>'''

    return f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=1200, initial-scale=1.0">
<title>Trust Para Todos — {html.escape(slug)}</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:ital,wght@0,400;0,500;0,700;1,400&display=swap" rel="stylesheet">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ width: 1200px; height: 630px; overflow: hidden; font-family: 'DM Sans', sans-serif; }}
  .og-card {{ width: 1200px; height: 630px; background: #faf5ed; position: relative; overflow: hidden; display: flex; flex-direction: row; }}
  .top-teal {{ position: absolute; top: 0; left: 0; right: 0; height: 5px; background: #0d7377; z-index: 10; }}
  .top-terracotta {{ position: absolute; top: 5px; left: 0; right: 0; height: 2px; background: #dd7054; z-index: 10; }}
  .left-content {{ flex: 1; padding: 55px 60px 48px 72px; display: flex; flex-direction: column; justify-content: center; z-index: 2; }}
  .logo-row {{ display: flex; align-items: center; gap: 12px; margin-bottom: 28px; }}
  .logo-icon {{ width: 44px; height: 44px; background: #0d7377; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }}
  .logo-text {{ font-family: 'Playfair Display', Georgia, serif; font-size: 24px; font-weight: 700; color: #1a1a2e; letter-spacing: -0.01em; }}
  .headline {{ font-family: 'Playfair Display', Georgia, serif; font-size: 48px; line-height: 1.08; color: #0d7377; margin-bottom: 14px; }}
  .headline .terracotta {{ color: #dd7054; }}
  .tagline {{ font-family: 'DM Sans', sans-serif; font-size: 17px; line-height: 1.55; color: #3d3d4a; max-width: 480px; margin-bottom: 28px; }}
  .features {{ display: flex; gap: 24px; }}
  .feature {{ display: flex; align-items: center; gap: 8px; font-family: 'DM Sans', sans-serif; font-size: 13px; font-weight: 700; color: #0d7377; }}
  .feature-icon {{ width: 24px; height: 24px; background: #dd7054; border-radius: 6px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }}
  .feature-icon svg {{ width: 14px; height: 14px; color: #FFFFFF; }}
  .footer {{ position: absolute; bottom: 20px; left: 72px; font-family: 'DM Sans', sans-serif; font-size: 11px; color: #7a7a88; letter-spacing: 0.06em; z-index: 2; }}
  .right-visual {{ width: 560px; height: 630px; position: relative; overflow: hidden; flex-shrink: 0; }}
  .right-visual img {{ width: 560px; height: 630px; object-fit: cover; object-position: center; }}
  .divider {{ position: absolute; left: 615px; top: 80px; bottom: 80px; width: 1px; background: linear-gradient(to bottom, transparent, #0d7377 30%, #0d7377 70%, transparent); opacity: 0.25; z-index: 3; }}
  .left-content::before {{ content: ''; position: absolute; inset: 0; background-image: radial-gradient(circle, #dd7054 0.5px, transparent 0.5px); background-size: 28px 28px; opacity: 0.03; z-index: -1; }}
</style>
</head>
<body>
<div class="og-card">
  <div class="top-teal"></div>
  <div class="top-terracotta"></div>
  <div class="left-content">
    <div class="logo-row">
      <div class="logo-icon">
        {SHIELD_SVG}
      </div>
      <span class="logo-text">Trust Para Todos</span>
    </div>
    <div class="headline">
      {article['headline']}
    </div>
    <div class="tagline">
      {html.escape(article['tagline'])}
    </div>
    <div class="features">
      {feature_html}
    </div>
  </div>
  <div class="right-visual">
    <img src="{article['photo']}" alt="" />
  </div>
  <div class="divider"></div>
  <div class="footer">trustparatodos.com/blog</div>
</div>
</body>
</html>'''


def main():
    from playwright.sync_api import sync_playwright

    generated = 0
    failed = 0

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 630})

        for article in BLOG_ARTICLES:
            slug = article["slug"]
            template_html = generate_og_html(article)
            template_path = TEMPLATES_DIR / f"og-blog-{slug}-gen.html"
            output_path = OUTPUT_DIR / f"og-blog-{slug}.png"

            # Write template HTML
            template_path.write_text(template_html, encoding="utf-8")

            # Render to PNG
            file_url = f"file://{template_path.resolve()}"
            try:
                page.goto(file_url)
                page.wait_for_timeout(2500)
                card = page.query_selector(".og-card")
                if card:
                    card.screenshot(path=str(output_path))
                    print(f"  OK: og-blog-{slug}.png")
                    generated += 1
                else:
                    print(f"  ERROR: .og-card not found in og-blog-{slug}")
                    failed += 1
            except Exception as e:
                print(f"  ERROR: {slug}: {e}")
                failed += 1

        browser.close()

    print(f"\nDone: {generated} rendered, {failed} failed.")


if __name__ == "__main__":
    main()