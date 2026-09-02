# El formato del Markdown

Lo produce `scripts/procesar_telegram.py` y está pensado para que NotebookLM lo
lea bien: un archivo por grupo y mes, los días como encabezados y los hilos de
respuesta reconstruidos.

**Este formato no debe cambiarse a la ligera.** Los archivos ya subidos a los
notebooks siguen esta forma, y cualquier variación —hasta un espacio— haría que
todos los meses se dieran por modificados y se resubieran enteros.

## Estructura de un archivo

```markdown
# ChatGPT-IA-edu (Supergupo público)

## 1 agosto 2026

**Juanjo de Haro (ID: 218499880) (04:44)**
Texto del mensaje

> ↩︎ **Otra persona (ID: 831346780) (19:46)** en respuesta a Juanjo de Haro (ID: 218499880) (04:44)
> Texto de la respuesta
```

- **Encabezado**: nombre del grupo y tipo de chat, en español.
- **Un `##` por día**, en español y en orden cronológico (`5 mayo 2025`).
- **Mensaje raíz**: `**Autor (ID: id) (HH:MM)**` y debajo el texto.
- **Respuesta**: en cita, con `↩︎` y a quién responde, reconstruido a partir de
  `reply_to_message_id`. Los hilos se ordenan por su primer mensaje.
- Cada línea de autor termina en **dos espacios**, que es el salto de línea de
  Markdown.

## Qué se descarta

- Mensajes de servicio (altas, bajas, cambios de título): `type != "message"`.
- Mensajes sin texto aprovechable, como los que solo llevan una imagen.
- Meses que se quedarían sin ningún mensaje: no se escribe el archivo.

## Formato del texto

Telegram entrega el texto como cadena o como lista de fragmentos con formato, y
se convierten a Markdown: negritas, cursivas, `código`, bloques de código,
enlaces, menciones y etiquetas. Los emojis se mantienen tal cual.

## Uso suelto

`scripts/procesar_telegram.py` funciona por su cuenta sobre una carpeta con
archivos JSON exportados de Telegram, sin el resto del automatismo:

```bash
cd carpeta-con-los-json && python3 .../scripts/procesar_telegram.py
```

Fusiona todos los JSON que encuentre —eliminando mensajes duplicados por
identificador—, parte el resultado por meses y escribe un `README.md` con el
índice. Es también el motor del conversor de navegador de `web/`.
