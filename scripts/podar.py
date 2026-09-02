#!/usr/bin/env python3
"""Mantiene acotado lo que el proceso diario va dejando por el camino.

El archivo de conversaciones —salida/— crece por definición: es la memoria de
los grupos y no se toca. Lo que sí se poda es lo redundante:

- Las exportaciones JSON de meses ya cerrados se comprimen. Son el paso
  intermedio, no el producto: su contenido útil ya está en el Markdown, y
  comprimidas ocupan la décima parte. No se borran porque son la única copia
  congelada de lo que Telegram tenía ese día.
- estado.json solo necesita los meses recientes: el del mes en curso y el
  anterior, por el cambio de mes. El resto es historia inerte.
"""

from __future__ import annotations

import gzip
import shutil
from datetime import date
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATOS = BASE / "datos"

# Meses que se dejan sin comprimir. Con tres hay de sobra para rehacer el mes en
# curso, el anterior y uno más de margen sin descomprimir nada.
MESES_EN_CLARO = 3
# Meses que se conservan en estado.json.
MESES_EN_ESTADO = 3


def _meses_recientes(cuantos: int, hoy: date | None = None) -> set[str]:
    """Los últimos N meses en formato 'YYYY-MM', contando el actual."""
    hoy = hoy or date.today()
    meses, anio, mes = set(), hoy.year, hoy.month
    for _ in range(cuantos):
        meses.add(f"{anio}-{mes:02d}")
        anio, mes = (anio - 1, 12) if mes == 1 else (anio, mes - 1)
    return meses


def comprimir_exportaciones(hoy: date | None = None) -> list[str]:
    """Comprime los JSON de meses cerrados. Devuelve los que ha comprimido."""
    recientes = _meses_recientes(MESES_EN_CLARO, hoy)
    comprimidos = []
    for archivo in sorted(DATOS.glob("*.json")):
        mes = archivo.stem[-7:]  # <prefijo>-YYYY-MM
        if mes in recientes:
            continue
        destino = archivo.with_suffix(".json.gz")
        with open(archivo, "rb") as origen, gzip.open(destino, "wb", compresslevel=9) as salida:
            shutil.copyfileobj(origen, salida)
        archivo.unlink()
        comprimidos.append(archivo.name)
    return comprimidos


def podar_estado(estado: dict, hoy: date | None = None) -> int:
    """Deja en estado.json solo los meses recientes. Devuelve cuántos quitó."""
    recientes = _meses_recientes(MESES_EN_ESTADO, hoy)
    quitados = 0
    for datos_grupo in estado.get("grupos", {}).values():
        meses = datos_grupo.get("meses", {})
        for mes in [m for m in meses if m not in recientes]:
            del meses[mes]
            quitados += 1
    return quitados


if __name__ == "__main__":
    import json

    comprimidos = comprimir_exportaciones()
    print(f"{len(comprimidos)} exportación(es) comprimida(s)")

    ruta = BASE / "estado.json"
    if ruta.exists():
        with open(ruta, encoding="utf-8") as f:
            estado = json.load(f)
        quitados = podar_estado(estado)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(estado, f, ensure_ascii=False, indent=2)
        print(f"{quitados} mes(es) retirado(s) de estado.json")
