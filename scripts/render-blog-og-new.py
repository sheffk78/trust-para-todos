#!/usr/bin/env python3
"""Trust Para Todos — Blog OG Image Generator (fontTools variant for the 4 new articles)

Renders the same two-column OG template (1200x630) used by the standard
render-blog-og.py, but builds the HTML in this script and converts it to PNG
without playwright (not installed in this environment): PIL draws directly on
canvas using the repo's brand fonts converted woff2→ttf via fontTools.

Usage:
  cd <repo> && python3 scripts/render-blog-og-new.py
"""
import re
from pathlib import Path
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont, ImageOps

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FONTS = PROJECT_ROOT / "public" / "fonts"
OUT = PROJECT_ROOT / "public"

ARTICLES = [
    {
        "slug": "fideicomiso-para-tu-casa",
        "headline_l1": "Fideicomiso",
        "headline_l2": "para tu casa",
        "tagline": "Evita el probate, deja tu casa directo a tu familia y mantén el control total. Guía completa en español.",
        "photo": "images/blog/01-hero-family-home.jpg",
        "features": ["Protege tu hogar", "Sin probate", "$997 total"],
    },
    {
        "slug": "fideicomiso-para-inmigrantes",
        "headline_l1": "Fideicomiso",
        "headline_l2": "sin papeles",
        "tagline": "Se puede hacer un trust sin importar tu estatus migratorio. Protege tu casa y a tu familia. Explicado simple.",
        "photo": "images/blog/03-hero-family-protection.jpg",
        "features": ["Sin estatus", "Todo en español", "100% en línea"],
    },
    {
        "slug": "proteger-casa-medicaid",
        "headline_l1": "Proteger tu casa",
        "headline_l2": "de Medicaid",
        "tagline": "¿El Estado puede quedarse tu casa si vas a un asilo? Cómo funciona la recuperación y qué caminos legales hay.",
        "photo": "images/blog/08-hero-family-property.jpg",
        "features": ["Regla de 5 años", "Casos reales", "En español"],
    },
    {
        "slug": "trust-online-sin-abogado",
        "headline_l1": "Trust online",
        "headline_l2": "paso a paso",
        "tagline": "Crea tu trust en línea sin abogado: 4 pasos, requisitos, costos y los errores que debes evitar.",
        "photo": "images/blog/05-hero-financial-planning.jpg",
        "features": ["4 pasos", "Sin abogado", "En menos de un mes"],
    },
]

TEAL = (13, 115, 119)
TERRA = (221, 112, 84)
CREAM = (250, 245, 237)
DARK = (26, 26, 46)
BODY = (61, 61, 74)


def woff2_to_ttf(src: Path, dst: Path):
    if dst.exists():
        return dst
    f = TTFont(str(src))
    f.flavor = None
    f.save(str(dst))
    return dst


def load_fonts(tmp: Path):
    tmp.mkdir(exist_ok=True)
    serif_bold = woff2_to_ttf(FONTS / "playfair-display-700.woff2", tmp / "playfair-700.ttf")
    serif = woff2_to_ttf(FONTS / "playfair-display-400.woff2", tmp / "playfair-400.ttf")
    dmr = tmp / "dmsans-regular.ttf"
    dmb = tmp / "dmsans-bold.ttf"
    if not dmr.exists():
        f = TTFont(str(FONTS / "dm-sans-variable.woff2"))
        # instantiate default weight (400) as static
        from fontTools.varLib.instancer import instantiateVariableFont
        instantiateVariableFont(f, {"wght": 400}, inplace=True)
        f.flavor = None
        f.save(str(dmr))
    if not dmb.exists():
        f = TTFont(str(FONTS / "dm-sans-variable.woff2"))
        from fontTools.varLib.instancer import instantiateVariableFont
        instantiateVariableFont(f, {"wght": 700}, inplace=True)
        f.flavor = None
        f.save(str(dmb))
    return str(serif_bold), str(serif), str(dmr), str(dmb)


def render(article, fonts, tmp):
    slug = article["slug"]
    s700, s400, dmr, dmb = fonts
    W, H = 1200, 630
    LEFT_W = 700
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # right panel photo
    photo = Image.open(PROJECT_ROOT / "public" / article["photo"]).convert("RGB")
    pw = W - LEFT_W
    photo = ImageOps.fit(photo, (pw, H), Image.LANCZOS, centering=(0.5, 0.4))
    img.paste(photo, (LEFT_W, 0))

    # top accent bands
    d.rectangle([0, 0, W, 5], fill=TEAL)
    d.rectangle([0, 5, W, 7], fill=TERRA)
    # divider between panels
    d.line([(LEFT_W - 2, 0), (LEFT_W - 2, H)], fill=(228, 219, 205), width=4)
    # dotted texture placeholder left edge
    for y in range(40, H - 40, 28):
        d.ellipse([28, y, 31, y + 3], fill=(221, 112, 84, 8))

    # logo row
    lx, ly = 72, 50
    d.rounded_rectangle([lx, ly, lx + 44, ly + 44], radius=10, fill=TEAL)
    f_shield = ImageFont.truetype(s700, 26)
    d.text((lx + 22, ly + 21), "T", font=f_shield, fill=CREAM, anchor="mm")
    f_logo = ImageFont.truetype(s700, 24)
    d.text((lx + 58, ly + 22), "Trust Para Todos", font=f_logo, fill=DARK, anchor="lm")

    # headline (serif, teal + terracotta second line)
    y = 150
    f_h1 = ImageFont.truetype(s700, 56)
    d.text((72, y), article["headline_l1"], font=f_h1, fill=TEAL)
    w1 = d.textlength(article["headline_l1"], font=f_h1)
    d.text((72, y + 66), article["headline_l2"], font=f_h1, fill=TERRA)
    y += 150

    # tagline
    f_tag = ImageFont.truetype(dmr, 19)
    words, line, lines = article["tagline"].split(), "", []
    maxw = 540
    for wd in words:
        test = (line + " " + wd).strip()
        if d.textlength(test, font=f_tag) > maxw:
            lines.append(line)
            line = wd
        else:
            line = test
    lines.append(line)
    for ln in lines:
        d.text((72, y), ln, font=f_tag, fill=BODY)
        y += 30

    y += 18
    # feature pills
    f_p = ImageFont.truetype(dmb, 15)
    px = 72
    for feat in article["features"]:
        tw = d.textlength(feat, font=f_p)
        d.rounded_rectangle([px, y, px + tw + 44, y + 34], radius=17, outline=(13, 115, 119), width=2)
        d.ellipse([px + 10, y + 10, px + 24, y + 24], fill=TEAL)
        d.text((px + 30, y + 17), feat, font=f_p, fill=DARK, anchor="lm")
        px += int(tw) + 58

    # footer
    d.rectangle([0, H - 48, LEFT_W, H], fill=(247, 240, 229))
    d.text((72, H - 24), "trustparatodos.com/blog", font=ImageFont.truetype(dmr, 16), fill=BODY, anchor="lm")

    png_path = OUT / f"og-blog-{slug}.png"
    img.save(png_path, "PNG")

    webp_path = OUT / f"og-blog-{slug}.webp"
    img.save(webp_path, "WEBP", quality=88, method=6)
    return slug


def main():
    tmp = PROJECT_ROOT / "public" / "og-templates" / "_fonttmp"
    fonts = load_fonts(tmp)
    done, failed = [], []
    for a in ARTICLES:
        try:
            render(a, fonts, tmp)
            done.append(a["slug"])
        except Exception as e:
            failed.append((a["slug"], str(e)))
    print(f"OK: {done}")
    if failed:
        print("FAILED:", failed)


if __name__ == "__main__":
    main()