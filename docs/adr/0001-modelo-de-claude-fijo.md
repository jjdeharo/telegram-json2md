# 0001. Modelo de Claude fijo

- Fecha: 26/09/2026
- Estado: aceptada

## Contexto

Los guiones llaman a `claude -p` sin `--model`, y el `settings.json` del
contenedor estaba vacío. El modelo era, por tanto, el que Claude Code usara por
defecto con la cuenta: Sonnet 5 el 26/09/2026, según las sesiones guardadas. Una
actualización de Claude Code podía cambiarlo sin que nadie lo decidiera.

## Decisión

Fijar `claude-sonnet-5` en `home/.claude/settings.json` del contenedor
(`/volume1/docker/memoria-telegram/home/.claude/settings.json` en el NAS), con el
identificador completo y no con un alias, que se mueve solo cuando sale un modelo
nuevo.

Lo que hace Claude aquí es rutinario: decidir si una fuente entra en el cuaderno, en una sola vuelta, y reparar lo que falle. Sonnet 5 basta, y cada llamada gasta del mismo límite de uso de la cuenta de claude.ai que Juanjo usa para su propio trabajo; Opus lo agotaría antes.

## Consecuencias

- Cambiar de modelo es una decisión explícita: se edita ese `settings.json`.
- Un modelo nuevo puede exigir una versión reciente de Claude Code. La 2.1.263,
  la que traía la imagen, rechazaba Opus 5.5 con «version 2.1.280 or newer is
  required»; se actualizaron los tres contenedores de agentes a la 2.1.283.
- Claude Code no se actualiza solo dentro del contenedor, así que su versión
  también queda fijada, en `nas/Dockerfile` (`ARG CLAUDE_CODE_VERSION`). Para
  subirla se cambia ese valor y se reconstruye la imagen. Un
  `docker exec memoria-telegram sh -c "HOME=/opt/claude claude update"` sirve como arreglo
  inmediato, pero se pierde en cuanto el contenedor se recrea.

## Validación

El 26/09/2026 se lanzó `claude -p --output-format json` con un encargo mínimo
dentro del contenedor, ya reconstruido con Claude Code 2.1.283 en la imagen, y `modelUsage` devolvió solo `claude-sonnet-5`.
