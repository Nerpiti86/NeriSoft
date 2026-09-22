# 15 — Sistema de movimiento NERISOFT

Actualizado: 22/09/2026

## Objetivo

NERISOFT incorpora una primera capa global de movimiento para reducir la sensación de corte o salto entre pantallas sin convertir el ERP en una interfaz ornamental ni en una SPA.

El movimiento debe reforzar continuidad, jerarquía y respuesta. No debe distraer ni ralentizar operaciones administrativas repetitivas.

## Principios

El sistema utiliza tiempos cortos y desplazamientos mínimos:

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
- no introducir esperas artificiales antes de navegar;
- priorizar `opacity` y `transform`;
- mantener la interfaz rápida para uso administrativo intensivo.

## Navegación entre páginas

Se habilita la API CSS de **View Transitions** mediante mejora progresiva:

```css
@view-transition {
    navigation: auto;
}
```

Cuando el navegador la soporta, NERISOFT conserva visualmente la continuidad de:

- sidebar;
- topbar;
- workspace.

El sidebar y la topbar usan nombres de transición estables. El workspace aplica una salida y entrada muy corta con opacidad y un desplazamiento vertical de pocos píxeles.

No se interceptan enlaces ni se retrasan clics con JavaScript.

En navegadores sin soporte de View Transitions la navegación continúa funcionando de forma normal, sin dependencia funcional de esta característica.

## Entrada inicial

`workspace` y las tarjetas de acceso usan `@starting-style` para aparecer de manera suave cuando el navegador soporta esta capacidad.

Esto evita esconder contenido mediante JavaScript y mantiene un fallback seguro.

## Paneles y mensajes

Los paneles de edición/alta y mensajes contextuales usan una microentrada de aproximadamente 150 ms.

Ejemplos actuales:

- formulario de alta de usuario;
- formulario de edición de usuario;
- avisos de éxito, advertencia o error.

## Select NERISOFT

El menú del Select NERISOFT recibe una apertura corta con:

- opacidad;
- desplazamiento vertical mínimo;
- escala prácticamente imperceptible.

El objetivo es evitar que el dropdown aparezca de forma brusca sin convertirlo en una animación protagonista.

## Sidebar

La transición de expansión/contracción mantiene su comportamiento existente, pero adopta el tiempo y easing globales del sistema de movimiento.

La modificación afecta únicamente la percepción de movimiento, no el estado persistido de la sidebar.

## Accesibilidad

Se respeta:

```css
@media (prefers-reduced-motion: reduce)
```

Cuando el sistema operativo solicita movimiento reducido:

- las animaciones quedan prácticamente anuladas;
- las transiciones se reducen al mínimo;
- la funcionalidad permanece intacta.

## Estado actual

Esta etapa es deliberadamente conservadora.

Todavía no se implementa:

- navegación parcial con HTMX;
- reemplazo dinámico del workspace;
- skeletons de carga;
- animaciones complejas de tablas;
- transiciones entre estados de datos asincrónicos.

La navegación parcial con HTMX podrá evaluarse más adelante si las pruebas de uso indican que la recarga completa sigue produciendo una interrupción visual significativa.
