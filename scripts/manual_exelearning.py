#!/usr/bin/env python3
"""Consolida el manual web de eXeLearning en un único Markdown.

El manual oficial de CEDEC/INTEF es un sitio de más de ochenta páginas. Subirlo
página a página llenaría el cuaderno de fuentes minúsculas, y subir solo el
índice no capturaría nada: se recorre entero y se junta en un documento con la
jerarquía de títulos recompuesta, que es lo que NotebookLM trocea bien.

Se rehace de tanto en tanto, cuando sale una versión nueva del manual:

    python3 scripts/manual_exelearning.py
"""
import re, subprocess, urllib.parse, urllib.request
from bs4 import BeautifulSoup
from pathlib import Path

DESTINO = Path(__file__).resolve().parent.parent / "material" / "exelearning" / "manual-exelearning-4.0.1.md"

RAIZ = "https://descargas.intef.es/cedec/exe_learning/Manuales/manual_exe401/"

def bajar(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read().decode("utf-8", "replace")

indice = BeautifulSoup(bajar(RAIZ), "html.parser")

# El menú lateral da el orden y la jerarquía reales del manual.
paginas = []
for a in indice.select("nav#siteNav a"):
    href = a.get("href", "")
    if not href.endswith(".html"):
        continue
    nivel = len(a.find_parents("ul"))
    paginas.append((nivel, a.get_text(strip=True), href))

vistas, salida = set(), []
salida.append("# Manual de eXeLearning 4.0.1\n")
salida.append("Manual oficial de usuario (CEDEC/INTEF), licencia CC BY-SA 4.0.\n"
              f"Origen: {RAIZ}\n")

for nivel, titulo, href in paginas:
    if href in vistas:
        continue
    vistas.add(href)
    try:
        html = bajar(RAIZ + href)
    except Exception as e:
        print(f"  fallo {href}: {e}")
        continue

    sopa = BeautifulSoup(html, "html.parser")
    # Fuera el menú, los saltos de navegación y los scripts: solo el contenido.
    for basura in sopa.select("nav, script, style, #skipNav, .exe-node-nav, header, footer"):
        basura.decompose()
    cuerpo = sopa.select_one("#main, main, .exe-content") or sopa.body
    if cuerpo is None:
        continue

    # Enlaces e imágenes relativos: sin absolutizar no significan nada fuera
    # del sitio original.
    base = RAIZ + href.rsplit("/", 1)[0] + "/"
    for etiqueta, atributo in (("a", "href"), ("img", "src")):
        for nodo in cuerpo.find_all(etiqueta):
            valor = nodo.get(atributo, "")
            if valor and not valor.startswith(("http", "#", "mailto:", "data:")):
                nodo[atributo] = urllib.parse.urljoin(base, valor)

    md = subprocess.run(["pandoc", "-f", "html", "-t", "gfm-raw_html", "--wrap=none"],
                        input=str(cuerpo), capture_output=True, text=True).stdout
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    if not md:
        continue

    # Los títulos de cada página empiezan otra vez en #, así que se rebajan por
    # debajo del nivel que ocupa la página en el manual: sin esto la jerarquía
    # sale descuadrada y NotebookLM trocea mal.
    nivel_pagina = min(nivel + 1, 5)
    propios = [len(m.group(1)) for m in re.finditer(r"^(#{1,6}) ", md, re.M)]
    if propios:
        desplazamiento = nivel_pagina + 1 - min(propios)
        if desplazamiento:
            md = re.sub(r"^(#{1,6}) ",
                        lambda m: "#" * min(len(m.group(1)) + desplazamiento, 6) + " ",
                        md, flags=re.M)

    salida.append(f"\n{'#' * nivel_pagina} {titulo}\n")
    salida.append(md)

texto = "\n".join(salida) + "\n"
DESTINO.parent.mkdir(parents=True, exist_ok=True)
DESTINO.write_text(texto, encoding="utf-8")
print(f"{len(vistas)} páginas, {len(texto.split())} palabras → {DESTINO}")
