#!/usr/bin/env bash
# Instala (o quita) el disparo automático diario en el crontab del usuario.
#
#   ./instalar.sh           añade las líneas, respetando las que ya hubiera
#   ./instalar.sh --quitar  las retira
#
# Son dos disparos, los dos inofensivos si el día ya está hecho:
#   @reboot         por si el ordenador se enciende y el día está pendiente.
#   cada 15' de 7h  por si ya estaba encendido, o si al encender no había red.

set -euo pipefail

BASE="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/.." && pwd)"
ORDEN="$BASE/scripts/diario.sh --auto"
MARCA="# memoria-telegram: conversaciones diarias en NotebookLM"

actual="$(crontab -l 2>/dev/null || true)"
# Se filtran las líneas propias por la ruta, no por posición: así conviven con
# las del boletín semanal, que están en el mismo crontab.
limpio="$(printf '%s\n' "$actual" | grep -v -F "$BASE/scripts/diario.sh" | grep -v -F "$MARCA" || true)"

if [ "${1:-}" = "--quitar" ]; then
  printf '%s\n' "$limpio" | crontab -
  echo "Disparo diario retirado del crontab."
  exit 0
fi

{
  printf '%s\n' "$limpio" | sed '/^$/d'
  printf '%s\n' "$MARCA"
  printf '@reboot          %s\n' "$ORDEN"
  printf '*/15 7-23 * * *  %s\n' "$ORDEN"
} | crontab -

echo "Instalado. Así queda el crontab:"
crontab -l
