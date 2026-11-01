"""Tarjeta estilo neofetch (assets/tarjeta.svg): los datos aparecen línea por línea,
con un cursor que escribe el comando primero. Uso: python scripts/tarjeta.py [--estatico]
"""
import sys
from html import escape
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ESTATICO = "--estatico" in sys.argv

USUARIO = "santiago@construyendo-ia"
DATOS = [
    ("Rol", "CTO · Construyendo IA"),
    ("Negocio", "Soluciones de IA para empresas"),
    ("Web", "Implementaciones web a la medida"),
    ("Finanzas", "Administración empresarial y financiera"),
    ("Automatiza", "Agentes, CRM y flujos con IA"),
    ("Stack", "Next.js · TypeScript · Supabase · Python"),
    ("IA", "Claude · agentes · RAG"),
    ("Contenido", "@botellorex.ia · IA para negocios"),
    ("Base", "México"),
]
ACENTO = "#e8834f"
TEXTO = "#d6e2f0"
TENUE = "#7d8590"
COLORES = ["#e8834f", "#3fb950", "#d29922", "#58a6ff", "#bc8cff", "#39c5cf", "#d6e2f0"]

FUENTE = 14
LINEA = 22
PAD = 24
ANCHO = 520


def main():
    comando = "neofetch"
    t_cmd = 0.08 * len(comando)  # el comando se teclea primero
    filas = []
    y = PAD + FUENTE

    def fila(contenido, n):
        retraso = "" if ESTATICO else f' style="animation-delay:{t_cmd + 0.25 + n * 0.18:.2f}s"'
        filas.append(f'<g class="l"{retraso}>{contenido}</g>')

    # prompt con el comando tecleado letra por letra
    prompt = f'<text x="{PAD}" y="{y}"><tspan fill="{ACENTO}">❯</tspan> '
    if ESTATICO:
        prompt += f"{comando}</text>"
    else:
        prompt += "".join(
            f'<tspan class="k" style="animation-delay:{i * 0.08:.2f}s">{c}</tspan>' for i, c in enumerate(comando)
        ) + "</text>"
    filas.append(prompt)

    y += LINEA * 1.4
    fila(f'<text x="{PAD}" y="{y}" ><tspan fill="{ACENTO}" font-weight="700">{escape(USUARIO)}</tspan></text>', 0)
    y += LINEA * 0.6
    fila(f'<rect x="{PAD}" y="{y}" width="{len(USUARIO) * FUENTE * 0.6:.0f}" height="1.5" fill="{TENUE}"/>', 0)
    y += LINEA
    for n, (k, v) in enumerate(DATOS, start=1):
        fila(
            f'<text x="{PAD}" y="{y}"><tspan fill="{ACENTO}" font-weight="700">{escape(k)}</tspan>'
            f'<tspan fill="{TENUE}">: </tspan>{escape(v)}</text>',
            n,
        )
        y += LINEA
    y += LINEA * 0.3
    bloques = "".join(
        f'<rect x="{PAD + i * 26}" y="{y}" width="24" height="14" rx="2" fill="{c}"/>' for i, c in enumerate(COLORES)
    )
    fila(bloques, len(DATOS) + 1)
    y += 14 + PAD

    css = "" if ESTATICO else (
        ".l,.k{animation:in .06s linear both}"
        "@keyframes in{from{opacity:0}to{opacity:1}}"
    )
    svg = "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{ANCHO}" height="{y:.0f}" viewBox="0 0 {ANCHO} {y:.0f}">',
        f"<style>text{{font:{FUENTE}px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:{TEXTO}}}{css}</style>",
        f'<rect width="100%" height="100%" rx="10" fill="#0d1117"/>',
        *filas,
        "</svg>",
    ])
    (RAIZ / "assets/tarjeta.svg").write_text(svg)
    print(f"tarjeta.svg: {ANCHO}x{y:.0f}")


if __name__ == "__main__":
    main()
