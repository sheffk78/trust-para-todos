#!/usr/bin/env python3
"""
Trust Para Todos — OG Image Render Pipeline

Renders all per-page OG HTML templates into 1200x630 PNG files using Playwright.

Usage:
  cd /Users/socializerender/Projects/trust-para-todos
  python3 scripts/render-og-images.py

Prerequisites:
  pip install playwright
  playwright install chromium
"""

import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "public" / "og-templates"
OUTPUT_DIR = PROJECT_ROOT / "public"

# Map: template HTML filename -> output PNG filename
OG_PAGES = {
    "og-home-gen.html": "og-home.png",
    "og-que-es-gen.html": "og-que-es.png",
    "og-como-funciona-gen.html": "og-como-funciona.png",
    "og-evaluacion-gen.html": "og-evaluacion.png",
    "og-faq-gen.html": "og-faq.png",
    "og-testimonios-gen.html": "og-testimonios.png",
    "og-asociaciones-gen.html": "og-asociaciones.png",
    "og-contacto-gen.html": "og-contacto.png",
}

def render_og(page, template_path, output_path):
    """Render a single OG template HTML to PNG at 1200x630."""
    file_url = f"file://{template_path.resolve()}"
    page.goto(file_url)
    page.wait_for_timeout(2500)  # Wait for Google Fonts to load
    card = page.query_selector(".og-card")
    if not card:
        print(f"  ERROR: .og-card not found in {template_path.name}")
        return False
    card.screenshot(path=str(output_path))
    print(f"  OK: {template_path.name} -> {output_path.name}")
    return True

def main():
    # Check templates exist
    missing = [t for t in OG_PAGES if not (TEMPLATES_DIR / t).exists()]
    if missing:
        print(f"ERROR: Missing template files: {missing}")
        sys.exit(1)

    rendered = 0
    failed = 0

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 630})

        for template_name, output_name in OG_PAGES.items():
            template_path = TEMPLATES_DIR / template_name
            output_path = OUTPUT_DIR / output_name

            print(f"Rendering {template_name}...")
            if render_og(page, template_path, output_path):
                rendered += 1
            else:
                failed += 1

        browser.close()

    print(f"\nDone: {rendered} rendered, {failed} failed.")
    if failed:
        sys.exit(1)

if __name__ == "__main__":
    main()