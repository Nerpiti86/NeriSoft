# 15 — Sistema de movimiento NERISOFT

Actualizado: 22/09/2026

## Objetivo

NERISOFT mantiene una capa de movimiento corta y funcional para controles, paneles, popovers y reemplazos parciales de workspace.

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

## Navegación

La primera prueba con View Transitions de documentos completos se descartó porque amplificaba artefactos de carga.

El enfoque vigente es estructural:

```text
sidebar + topbar permanecen montados
            ↓
HTMX reemplaza solo .workspace
```

El workspace utiliza una salida breve de 60 ms y asentamiento de 100 ms. No se anima el documento completo.

## Movimiento que permanece

- alta/edición de usuarios;
- avisos de estado;
- Select NERISOFT;
- sidebar expandida/contraída;
- hover/focus de controles;
- swap parcial del workspace.

## Reduced motion

Con `prefers-reduced-motion: reduce` las animaciones y transiciones se reducen prácticamente a cero.

## Regla futura

Los módulos nuevos deben integrarse a la misma navegación parcial solo cuando sus GET puedan devolver una `.workspace` compatible sin alterar autorización ni semántica del backend.

Las mutaciones POST no se convierten automáticamente a HTMX: requieren una estrategia uniforme para errores, notices, redirects y CSRF.
