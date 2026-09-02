#!/usr/bin/env python3
"""Resume en unas líneas lo que hizo la pasada del día y lo manda por Telegram.

La pasada avisa por su cuenta cuando ocurre algo gordo —una reparación, una
actualización—, pero eso deja al día normal en silencio y sin manera de saber si
llegó a ejecutarse. Este resumen cierra ese hueco: una nota corta, todos los
días, con lo hecho.

Se arma leyendo el registro del día, que ya lleva las líneas que hacen falta.

    python3 scripts/resumen-diario.py [registro/diario-2026-09-03.log]
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "scripts"))

from informar import informar  # noqa: E402


def resumir(registro: str) -> tuple[str, bool]:
    """Devuelve el texto del resumen y si hubo algún problema.

    Del registro solo interesa la última pasada: el archivo acumula todas las del
    día —los reintentos del cuarto de hora, alguna ejecución a mano— y contar
    sobre el conjunto daría cifras infladas.
    """
    trozos = registro.split("=== actualización hasta ")
    if len(trozos) > 1:
        registro = "=== actualización hasta " + trozos[-1]
    lineas = []
    problema = False

    # --- Conversaciones
    hasta = re.search(r"=== actualización hasta (\S+) ===", registro)
    subidas = re.search(r"=== terminado: (\d+) subida", registro)
    al_dia = len(re.findall(r": al día, nada que hacer", registro))
    if subidas:
        cuantas = int(subidas.group(1))
        detalle = (f"{cuantas} conversación(es) actualizada(s)" if cuantas
                   else f"sin novedades ({al_dia} grupos al día)")
        lineas.append(f"• *Telegram*: {detalle}"
                      + (f", hasta el {hasta.group(1)[8:10]}/{hasta.group(1)[5:7]}" if hasta else ""))
    else:
        lineas.append("• *Telegram*: no llegó a terminar")
        problema = True

    # --- Documentación de eXeLearning
    sincro = re.search(r"resumen: (\d+) nueva\(s\), (\d+) actualizada\(s\), (\d+) retirada", registro)
    if sincro:
        nuevas, cambiadas, retiradas = (int(x) for x in sincro.groups())
        if nuevas or cambiadas or retiradas:
            lineas.append(f"• *eXeLearning*: {nuevas} nueva(s), {cambiadas} actualizada(s), "
                          f"{retiradas} retirada(s)")
        else:
            lineas.append("• *eXeLearning*: documentación sin cambios")
    else:
        lineas.append("• *eXeLearning*: no se pudo sincronizar")
        problema = True

    # --- Documentación nueva que hubo que clasificar
    if "no hay documentación nueva que clasificar" in registro:
        pass   # lo normal; no merece línea propia
    elif clasificados := re.search(r"aplicado: (\d+) al cuaderno", registro):
        lineas.append(f"• *Clasificada sola*: {clasificados.group(1)} documento(s) nuevo(s)")

    # --- El CLI del que depende todo
    if version := re.search(r"CLI de NotebookLM al día \(([\d.]+)\)", registro):
        lineas.append(f"• *CLI*: al día ({version.group(1)})")
    elif actualizado := re.search(r"actualizado a ([\d.]+) y comprobado", registro):
        lineas.append(f"• *CLI*: actualizado a la {actualizado.group(1)} y comprobado")

    # --- Lo que haya ido mal
    for aviso in re.findall(r"^\S+ \S+  (la .*falló.*|fallo: .*)$", registro, re.M):
        lineas.append(f"⚠️ {aviso}")
        problema = True

    return "\n".join(lineas), problema


def main() -> int:
    ruta = Path(sys.argv[1]) if len(sys.argv) > 1 else \
        BASE / "registro" / f"diario-{date.today():%Y-%m-%d}.log"
    if not ruta.exists():
        print(f"no hay registro en {ruta}")
        return 1

    resumen, problema = resumir(ruta.read_text(encoding="utf-8", errors="replace"))
    cabecera = "Pasada diaria" + (" · con incidencias" if problema else "")
    print(resumen)
    informar(f"{'⚠️' if problema else '✅'} *{cabecera}*\n\n{resumen}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
