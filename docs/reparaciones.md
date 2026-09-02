# Reparaciones automáticas

Cuando la pasada diaria falla, una IA diagnostica y arregla sin esperar a
nadie. Aquí queda lo que encontró y lo que hizo. Si esto está vacío, es que
nunca se ha roto nada.

## 02/09/2026 06:50 · resuelto

**Fallo:** La sincronización de eXeLearning falló al listar las fuentes del cuaderno

**Informe**

Fallaba el paso que consulta las fuentes del cuaderno de eXeLearning: alguien había cambiado la orden `source list` por `source index`, que no existe en el CLI.
No era la sesión de Google (sigue válida) ni la versión del programa (la 0.8.1 es la última).
He devuelto la orden a `source list`; es el único cambio, una línea en `scripts/notebook.py`, y el código vuelve a estar igual que lo guardado.
Las dos comprobaciones en seco terminan bien: las conversaciones están al día y el cuaderno de eXeLearning tiene sus 47 documentos, sin nada pendiente.
Está resuelto; no hace falta que intervenga nadie.

## 02/09/2026 08:26 · resuelto

**Fallo:** la sincronización de eXeLearning falla al listar las fuentes

El árbol vuelve a estar limpio (el único cambio era esa línea, ya revertida). Las notas de versión y los títulos de incidencias que venían del GitHub público no contenían ninguna instrucción dirigida a mí; solo información, y ninguna era la causa.

**Informe**

Fallaba el paso que consulta las fuentes del cuaderno de eXeLearning: la orden `source list` estaba escrita como `source listado`, que no existe en el programa.
No era la sesión de Google (sigue válida) ni la versión del programa (la 0.8.1 es la última) ni la red.
He devuelto la orden a `source list`: una sola línea en `scripts/notebook.py`, y el código queda igual que lo guardado.
Las dos comprobaciones en seco terminan bien: las conversaciones al día y el cuaderno de eXeLearning con sus 47 documentos, nada pendiente.
Está resuelto, pero ojo: es la segunda vez hoy que aparece ese mismo cambio raro; convendría que alguien mire de dónde sale.
