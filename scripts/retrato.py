"""Convierte assets/foto.jpg en un retrato ASCII animado (assets/retrato.svg).

El fondo azul de estudio se quita por color; el resto se ecualiza y se pasa a
caracteres por densidad. Cada renglón aparece en orden, como si se imprimiera.
Uso: python scripts/retrato.py [--estatico]
"""
import sys
from html import escape
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageFilter

RAIZ = Path(__file__).resolve().parent.parent
COLUMNAS = 110
ASPECTO = 0.5          # alto/ancho de un carácter monoespaciado
RAMPA = " .:-=+*#%@"   # de vacío a lleno
FUENTE = 7             # px
ANCHO_CAR = FUENTE * 0.6
ALTO_LINEA = FUENTE * 1.15
POR_RENGLON = 0.035    # segundos entre renglones
ESTATICO = "--estatico" in sys.argv


def cargar():
    img = Image.open(RAIZ / "assets/foto.jpg").convert("RGB")
    w, h = img.size
    # encuadre de cabeza y hombros
    return img.crop((int(w * 0.12), int(h * 0.08), int(w * 0.88), int(h * 0.58)))


def mascara_sujeto(rgb):
    r, g, b = (rgb[..., i].astype(int) for i in range(3))
    fondo = (b - r > 35) & (b - g > 15)
    m = Image.fromarray(np.where(fondo, 0, 255).astype(np.uint8))
    return np.asarray(m.filter(ImageFilter.MedianFilter(7))) > 127


def main():
    img = cargar()
    filas = int(COLUMNAS * img.height / img.width * ASPECTO)
    peq = img.resize((COLUMNAS, filas), Image.LANCZOS)
    rgb = np.asarray(peq)
    sujeto = mascara_sujeto(rgb)

    # contraste local (CLAHE) a resolución alta y luego se reduce: así sobreviven ojos, nariz y boca
    alta = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2GRAY)
    alta = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8)).apply(alta)
    luz = cv2.resize(alta, (COLUMNAS, filas), interpolation=cv2.INTER_AREA).astype(float) / 255
    vals = luz[sujeto]
    luz = np.clip((luz - np.percentile(vals, 3)) / (np.percentile(vals, 97) - np.percentile(vals, 3)), 0, 1)
    # sobre fondo oscuro, lo claro lleva más carácter; el sujeto nunca queda vacío
    idx = np.clip(1 + (luz ** 1.2 * (len(RAMPA) - 2)).round().astype(int), 1, len(RAMPA) - 1)
    idx[~sujeto] = 0
    # las esquinas viñeteadas del estudio no son sujeto
    idx[:, :3] = 0
    idx[:, -3:] = 0

    lineas = ["".join(RAMPA[i] for i in fila).rstrip() for fila in idx]
    while lineas and not lineas[0].strip():
        lineas.pop(0)

    pad = 16
    ancho = int(COLUMNAS * ANCHO_CAR + pad * 2)
    alto = int(len(lineas) * ALTO_LINEA + pad * 2)
    css = "" if ESTATICO else (
        ".r{animation:in .15s linear both}"
        "@keyframes in{from{opacity:0}to{opacity:1}}"
    )
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}" viewBox="0 0 {ancho} {alto}">',
        f"<style>text{{font:{FUENTE}px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:#d6e2f0;white-space:pre}}{css}</style>",
        f'<rect width="100%" height="100%" rx="10" fill="#0d1117"/>',
    ]
    for n, linea in enumerate(lineas):
        y = pad + (n + 0.8) * ALTO_LINEA
        retraso = "" if ESTATICO else f' style="animation-delay:{n * POR_RENGLON:.3f}s"'
        out.append(f'<text class="r" x="{pad}" y="{y:.1f}" xml:space="preserve"{retraso}>{escape(linea)}</text>')
    out.append("</svg>")
    (RAIZ / "assets/retrato.svg").write_text("\n".join(out))
    print(f"retrato.svg: {len(lineas)} renglones, {ancho}x{alto}")


if __name__ == "__main__":
    main()
