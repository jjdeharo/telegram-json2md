# 0002. Licencias: AGPL v3 para el código y CC BY-SA 4.0 para la documentación

- Fecha: 29/10/2026
- Estado: aceptada

## Contexto

El repositorio es público y su web, el conversor de JSON de Telegram a Markdown
(`https://jjdeharo.github.io/telegram-json2md/`), está en el Repositorio de recursos
educativos digitales de Vibe Coding Educativo. Ese repositorio solo admite recursos con
una licencia abierta que conste en el código, y la revisión del 29/10/2026 marcó el
conversor como «sin licencia»: no había archivo LICENSE ni licencia en la web. Juanjo
pidió añadírsela.

## Decisión

- El código (scripts, imagen del NAS y la web) se publica bajo AGPL-3.0-or-later:
  archivo `LICENSE` y una línea `SPDX-License-Identifier` al inicio de cada archivo de
  código.
- La documentación (README, `docs/` y `skills/`) se publica bajo CC BY-SA 4.0
  (`LICENSE-CONTENIDOS`).
- La web lleva un pie con la autoría, la licencia del código, el enlace al código
  fuente, la declaración de uso de IA (nivel 4 del MIAE) y el crédito de JSZip, la
  biblioteca que usa para descargar todos los meses en un ZIP. La rama `gh-pages`, que
  sirve la web, recibe la misma página y los archivos de licencia.

## Alternativas descartadas

- Una licencia permisiva (MIT): las licencias por defecto de la guía «Vibe coding
  responsable» son AGPL v3 para el código y CC BY-SA 4.0 para los contenidos.

## Consecuencias

- Los archivos de código nuevos llevan la línea SPDX desde el principio.
- Los datos que procesa el repositorio (mensajes de los grupos) no se publican aquí y
  no quedan cubiertos por estas licencias.
