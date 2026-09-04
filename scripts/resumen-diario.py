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

# Los grupos se registran por su nombre de usuario de Telegram, que no siempre
# se parece al nombre con el que Juanjo los conoce. El aviso lleva el segundo.
NOMBRES = {
    "chatgptedu": "ChatGPT-IA-edu",
    "exelearning": "eXeLearning",
    "vceduca": "Vibe Coding Educativo",
}


def bonito(clave: str) -> str:
    return NOMBRES.get(clave.lower(), clave)


def listar(titulos: list[str], tope: int = 6) -> list[str]:
    """Enumera los archivos tocados, recortando la lista si se hace larga."""
    lineas = [f"   – {t}" for t in titulos[:tope]]
    if len(titulos) > tope:
        lineas.append(f"   – …y {len(titulos) - tope} más")
    return lineas


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

    # --- Conversaciones de los grupos de Telegram
    hasta = re.search(r"=== actualización hasta (\S+) ===", registro)
    subidas = re.search(r"=== terminado: (\d+) subida", registro)
    fecha = f" hasta el {hasta.group(1)[8:10]}/{hasta.group(1)[5:7]}" if hasta else ""

    # Cada grupo deja rastro de cuántos mensajes exportó, o de que no había nada.
    mensajes: dict[str, int] = {}
    al_dia: list[str] = []
    grupo = None
    for linea in registro.splitlines():
        if exp := re.search(r"(\S+): exportando ", linea):
            grupo = bonito(exp.group(1))
        elif sin := re.search(r"(\S+): al día, nada que hacer", linea):
            al_dia.append(bonito(sin.group(1)))
        elif con := re.search(r"(\d+) mensajes con texto", linea):
            if grupo:
                mensajes[grupo] = mensajes.get(grupo, 0) + int(con.group(1))

    if subidas:
        cuantas = int(subidas.group(1))
        if cuantas:
            lineas.append(f"• *Telegram*: {cuantas} conversación(es) subida(s) a "
                          f"NotebookLM{fecha}")
            lineas += [f"   – {g}: {n} mensajes" for g, n in mensajes.items()]
        else:
            lineas.append(f"• *Telegram*: sin mensajes nuevos{fecha}")
            if al_dia:
                lineas.append(f"   – ya al día: {', '.join(al_dia)}")
    else:
        lineas.append("• *Telegram*: la exportación no llegó a terminar")
        problema = True

    # --- Documentación de eXeLearning que va al cuaderno de Karla
    sincro = re.search(r"resumen: (\d+) nueva\(s\), (\d+) actualizada\(s\), (\d+) retirada",
                       registro)
    total = re.search(r"(\d+) documentos deben estar en el cuaderno", registro)
    cuantos = f" (de {total.group(1)} en total)" if total else ""
    if sincro:
        nuevas, cambiadas, retiradas = (int(x) for x in sincro.groups())
        # Se conserva qué le pasó a cada archivo: alta, cambio o baja.
        verbos = {"añadiendo": "nuevo", "actualizando": "actualizado",
                  "retirando": "retirado"}
        tocados = [f"{titulo} ({verbos[verbo]})" for verbo, titulo in
                   re.findall(r"^\s+[+~-] (añadiendo|actualizando|retirando) (.+)$",
                              registro, re.M)]
        if nuevas or cambiadas or retiradas:
            partes = []
            if nuevas:
                partes.append(f"{nuevas} nuevo(s)")
            if cambiadas:
                partes.append(f"{cambiadas} actualizado(s)")
            if retiradas:
                partes.append(f"{retiradas} retirado(s)")
            lineas.append(f"• *Documentación de eXeLearning* en el cuaderno de Karla: "
                          f"{', '.join(partes)}{cuantos}")
            lineas += listar(tocados)
        else:
            lineas.append(f"• *Documentación de eXeLearning*: sin cambios{cuantos}")
    else:
        lineas.append("• *Documentación de eXeLearning*: no se pudo sincronizar")
        problema = True

    # --- Documentación nueva que hubo que clasificar
    if "no hay documentación nueva que clasificar" in registro:
        pass   # lo normal; no merece línea propia
    elif clasificados := re.search(r"aplicado: (\d+) al cuaderno", registro):
        lineas.append(f"• *Clasificada sola*: {clasificados.group(1)} documento(s) nuevo(s)")

    # --- El CLI del que depende todo
    if version := re.search(r"CLI de NotebookLM al día \(([\d.]+)\)", registro):
        lineas.append(f"• *CLI de NotebookLM*: al día (versión {version.group(1)})")
    elif actualizado := re.search(r"actualizado a ([\d.]+) y comprobado", registro):
        lineas.append(f"• *CLI de NotebookLM*: actualizado a la versión "
                      f"{actualizado.group(1)} y comprobado")

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
