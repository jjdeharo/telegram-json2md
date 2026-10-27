#!/usr/bin/env python3
"""Consolida el manual web de eXeLearning en un único Markdown.

El manual oficial de CEDEC/INTEF es un sitio de más de ochenta páginas. Subirlo
página a página llenaría el cuaderno de fuentes minúsculas, y subir solo el
índice no capturaría nada: se recorre entero y se junta en un documento con la
jerarquía de títulos recompuesta, que es lo que NotebookLM trocea bien.

La versión del manual se busca sola (Juanjo, 27-10-2026: «el mecanismo
automático debe leer cuál es la última versión de la ayuda»). Cada versión
publicada vive en su carpeta (manual_exe401/, manual_exe405/…) y el servidor
no deja listarlas, pero una carpeta que no existe redirige al portal del
INTEF. Se prueban las versiones publicadas de eXeLearning, según las etiquetas
de su repositorio, de la más nueva a la más antigua, y vale la primera que
responde. El Markdown se llama con su versión y sustituye al anterior; la
sincronización retira del cuaderno el que desaparece.

    python3 scripts/manual_exelearning.py           rehacer el de la última versión
    python3 scripts/manual_exelearning.py --ultima  solo decir cuál es la última
"""
import json, re, subprocess, sys, urllib.error, urllib.parse, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from entorno import usar_venv  # noqa: E402

usar_venv()

from bs4 import BeautifulSoup  # noqa: E402

BASE = Path(__file__).resolve().parent.parent
MATERIAL = BASE / "material" / "exelearning"
MANUALES = "https://descargas.intef.es/cedec/exe_learning/Manuales/"
CONOCIDA = "4.0.1"  # la última que se sabe que existe, por si no se puede consultar nada más


class SinRedirigir(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None  # una redirección es «esa carpeta no existe»: no se sigue


def existe(version: str) -> bool:
    url = f"{MANUALES}manual_exe{version.replace('.', '')}/"
    try:
        with urllib.request.build_opener(SinRedirigir).open(url, timeout=30) as r:
            return r.status == 200
    except (urllib.error.URLError, OSError):
        return False


def candidatas() -> list[str]:
    """Las versiones publicadas de eXeLearning, de la más nueva a la más antigua."""
    vistas = set()
    try:
        config = json.loads((BASE / "config.json").read_text(encoding="utf-8"))
        repo = Path(config["repo_exelearning"]).expanduser()
        etiquetas = subprocess.run(["git", "-C", str(repo), "tag"], capture_output=True, text=True,
                                   timeout=60).stdout.split()
        vistas = {e[1:] for e in etiquetas if re.fullmatch(r"v\d+\.\d+\.\d+", e)}
    except (OSError, KeyError, ValueError, subprocess.SubprocessError):
        pass
    if not vistas:  # sin el repositorio, todas las de la 4.x hasta la 4.3.15
        vistas = {f"4.{m}.{p}" for m in range(4) for p in range(16)}
    vistas.add(CONOCIDA)
    return sorted(vistas, key=lambda v: tuple(map(int, v.split("."))), reverse=True)


def ultima() -> tuple[str, str]:
    """(versión, dirección) del manual más reciente publicado."""
    for v in candidatas():
        if existe(v):
            return v, f"{MANUALES}manual_exe{v.replace('.', '')}/"
    raise RuntimeError("no se encuentra ninguna versión del manual de eXeLearning")


def bajar(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def rehacer(VERSION: str, RAIZ: str) -> None:
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
    salida.append(f"# Manual de eXeLearning {VERSION}\n")
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
    if len(vistas) < 20:  # un manual a medio publicar no sustituye al que hay
        raise RuntimeError(f"el manual {VERSION} solo tiene {len(vistas)} páginas; se conserva el anterior")
    destino = MATERIAL / f"manual-exelearning-{VERSION}.md"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto, encoding="utf-8")
    for viejo in MATERIAL.glob("manual-exelearning-*.md"):  # sustituir, no acumular
        if viejo != destino:
            viejo.unlink()
            print(f"retirado {viejo.name}")
    print(f"{len(vistas)} páginas, {len(texto.split())} palabras → {destino}")


if __name__ == "__main__":
    version, raiz = ultima()
    if sys.argv[1:] == ["--ultima"]:
        print(version, raiz)
    else:
        rehacer(version, raiz)
