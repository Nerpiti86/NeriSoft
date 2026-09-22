# 15 — Sistema de movimiento NERISOFT

Actualizado: 22/09/2026

## Objetivo

NERISOFT mantiene una capa de movimiento corta y funcional para controles, paneles y popovers, sin animar todavía la navegación completa entre páginas.

## Principios

Tiempos base:

```text
instantáneo:  80 ms
rápido:      110 ms
base:        150 ms
lento:       200 ms
```

Curva principal:

```css
cubic-bezier(.2, .8, .2, 1)
```

Reglas:

- evitar rebotes;
- evitar zooms notorios;
- evitar desplazamientos largos;
- no introducir esperas artificiales;
- priorizar `opacity` y `transform`;
- respetar `prefers-reduced-motion`;
- no ocultar problemas de carga mediante animaciones.

## Corrección de navegación

La primera prueba utilizó View Transitions sobre páginas completas. En la prueba real se observaron artefactos al coincidir la transición con la carga tardía de Geist y Tabler Icons desde Internet.

Por esa razón se retira temporalmente:

- `@view-transition`;
- nombres de transición para sidebar/topbar/workspace;
- fade de entrada global del workspace;
- `@starting-style` de página completa.

La navegación vuelve a ser directa y estable mientras se corrige primero el origen de los saltos visuales: los assets externos.

## Movimiento que permanece

Se conservan microtransiciones de bajo costo para:

- formulario de alta/edición de usuarios;
- avisos de estado;
- Select NERISOFT;
- sidebar expandida/contraída;
- hover/focus de controles y paneles.

## Próxima evolución

Si luego de estabilizar tipografía e iconos la navegación completa continúa sintiéndose brusca, el siguiente enfoque será mantener el shell persistente y reemplazar únicamente el workspace mediante HTMX.

Eso evita animar dos documentos completos y permite una transición realmente estructural.
