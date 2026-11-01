"""Mapa de contribuciones animado (assets/contribuciones.svg).

Lee el calendario público de github.com/users/<usuario>/contributions (sin token)
y lo dibuja columna por columna. Lo corre GitHub Actions cada día.
Uso: python scripts/contribuciones.py [usuario] [--estatico]
"""
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

RAIZ = Path(__file__).resolve().parent.parent
ESTATICO = "--estatico" in sys.argv
USUARIO = next((a for a in sys.argv[1:] if not a.startswith("--")), "botellosantiago-bot")
NIVELES = ["#161b22", "#5a2e1a", "#8f4526", "#c45f33", "#e8834f"]  # del acento de la marca
CELDA, HUECO, PAD = 11, 3, 24


def leer():
    r = requests.get(f"https://github.com/users/{USUARIO}/contributions", timeout=30,
                     headers={"User-Agent": "perfil-readme"})
    r.raise_for_status()
    sopa = BeautifulSoup(r.text, "html.parser")
    dias = []
    for td in sopa.select("td.ContributionCalendar-day[data-date]"):
        dias.append((td["data-date"], int(td.get("data-level", 0))))
    dias.sort()
    total = sopa.select_one("h2#js-contribution-activity-description")
    n = re.search(r"[\d,]+", total.get_text()) if total else None
    texto = f"{n.group().replace(',', '')} contribuciones en el último año" if n else ""
    return dias, texto


def main():
    from datetime import date
    dias, texto = leer()
    if not dias:
        sys.exit("no se encontraron días en el calendario")
    inicio = date.fromisoformat(dias[0][0])
    desfase = (inicio.weekday() + 1) % 7  # GitHub empieza la semana en domingo
    celdas = []
    semanas = 0
    for i, (d, nivel) in enumerate(dias):
        k = i + desfase
        col, fila = divmod(k, 7)
        semanas = max(semanas, col + 1)
        x = PAD + col * (CELDA + HUECO)
        y = PAD + 30 + fila * (CELDA + HUECO)
        retraso = "" if ESTATICO else f' style="animation-delay:{col * 0.03:.2f}s"'
        celdas.append(f'<rect class="c" x="{x}" y="{y}" width="{CELDA}" height="{CELDA}" rx="2" '
                      f'fill="{NIVELES[nivel]}"{retraso}><title>{d}</title></rect>')
    ancho = PAD * 2 + semanas * (CELDA + HUECO) - HUECO
    alto = PAD * 2 + 30 + 7 * (CELDA + HUECO) - HUECO
    css = "" if ESTATICO else (
        ".c{animation:in .3s ease-out both}"
        "@keyframes in{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}"
    )
    svg = "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}" viewBox="0 0 {ancho} {alto}">',
        f"<style>text{{font:13px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:#7d8590}}{css}</style>",
        f'<rect width="100%" height="100%" rx="10" fill="#0d1117"/>',
        f'<text x="{PAD}" y="{PAD + 12}"><tspan fill="#e8834f">❯</tspan> {texto or "contribuciones del último año"}</text>',
        *celdas,
        "</svg>",
    ])
    (RAIZ / "assets/contribuciones.svg").write_text(svg)
    print(f"contribuciones.svg: {len(dias)} días, {semanas} semanas · {texto}")


if __name__ == "__main__":
    main()
