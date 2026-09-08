#!/usr/bin/env bash
# El reloj de la pasada diaria dentro del contenedor.
#
# En el portátil esto lo hacía cron: @reboot y cada cuarto de hora de 7 a 23.
# Aquí el contenedor está siempre vivo, así que el arranque hace de @reboot y
# este bucle hace de los cuartos de hora. La idempotencia sigue siendo de
# diario.sh: la marca del día corta los disparos sobrantes, así que llamarlo de
# más no cuesta nada y llamarlo de menos sí.
#
# Empieza a las 4 de la mañana y no a las 7: el NAS no se apaga, así que no hay
# ninguna razón para esperar a que haya alguien delante, y a esa hora ni
# Telegram ni NotebookLM tienen tráfico.
set -u

PASADA=/proyecto/scripts/diario.sh

while true; do
  hora=$((10#$(date +%H)))          # 10# para que las 08 y las 09 no sean octal
  if [ "$hora" -ge 4 ] && [ "$hora" -le 23 ]; then
    if [ -x "$PASADA" ]; then
      "$PASADA" --auto || true
    else
      printf '%s  no encuentro %s; ¿está montado el repositorio?\n' \
        "$(date '+%F %T')" "$PASADA"
    fi
  fi
  sleep 900
done
