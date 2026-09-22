# 06 — Referencia visual aprobada

## Estado

La versión de dashboard aprobada el 22/09/2026 queda como referencia visual oficial para modelar NERISOFT.

La implementación debe respetar la estructura y densidad del mock aprobado, reemplazando la marca temporal del mock por **NERISOFT** y usando datos reales del sistema cuando existan.

## Estructura principal

- Aplicación a 100% del viewport.
- Sidebar grafito a altura completa y colapsable.
- Header oscuro sobre el área principal.
- Buscador global en el header.
- Selector/contexto de empresa preparado para una futura etapa multiempresa.
- Notificaciones y menú de usuario en el extremo derecho.
- Workspace claro, sin `max-width` central.

## Dashboard

El dashboard de referencia contiene:

1. Título y saludo/contexto.
2. Selector de período.
3. Cinco KPIs principales en una sola línea en escritorio amplio.
4. Gráfico de ventas de los últimos 30 días.
5. Tabla de comprobantes recientes.
6. Tabla de cuentas por cobrar.
7. Tabla de productos con stock bajo.
8. Panel de alertas y pendientes.

## Navegación

Orden visual de referencia:

```text
Inicio
Ventas
Compras
Stock
Tesorería
Contabilidad
Reportes
Configuración
```

La opción activa utiliza dorado sobre el sidebar grafito.

## Lenguaje visual

- Grafito para navegación y header.
- Dorado para identidad, selección y acciones destacadas.
- Fondo principal claro cálido.
- Cards blancas con bordes suaves.
- Bordes y separadores discretos.
- Radios moderados.
- Geist como tipografía principal.
- Números con `tabular-nums`.
- Verde, rojo, ámbar y azul reservados para estados semánticos.
- Alta densidad de información; desktop-first.

## Regla de implementación

La referencia no implica copiar datos ficticios del mock. Deben reproducirse la jerarquía visual, distribución, proporciones y comportamiento general. Los datos, acciones y estados serán los definidos por los módulos funcionales de NERISOFT.

## Shell visual implementado

La primera implementación del shell queda fijada con estas reglas:

- `app-shell` ocupa `100vw × 100vh`.
- Sidebar expandida de aproximadamente `248px` y colapsada de `68px`.
- Header superior de `68px`.
- El workspace utiliza todo el ancho restante y mantiene scroll interno.
- La sidebar contiene la navegación oficial en el orden aprobado.
- `Inicio` aparece como sección activa con acento dorado.
- El estado colapsado de la sidebar se persiste en `localStorage` con la clave `nerisoft.sidebar.collapsed`.
- En estado colapsado se conservan los iconos y los `title` nativos para identificar cada sección.
- El header reserva las áreas de búsqueda global, empresa actual, notificaciones y usuario.
- La implementación mantiene Geist, números tabulares, radios `6/8/10px` y sombras según el sistema visual documentado.

## Dashboard visual implementado

La primera versión visual del dashboard de Inicio queda fijada con estas reglas:

- Los datos mostrados son **datos de muestra** y no provienen todavía de SQLite.
- La pantalla incluye cinco tarjetas KPI: ventas, comprobantes, cuentas por cobrar, tesorería y stock bajo.
- El bloque principal incluye un gráfico visual de ventas de 30 días y un panel de alertas.
- Se incluyen tablas de comprobantes recientes, cuentas por cobrar y productos con stock bajo.
- Los importes y cantidades visibles utilizan números tabulares.
- Los estados usan colores semánticos independientes del dorado de marca.
- El dashboard mantiene la densidad del mock aprobado y usa el ancho completo del workspace.
- En pantallas más angostas la grilla se reorganiza sin transformar la aplicación en una interfaz móvil.
- La lógica funcional, consultas reales, filtros y navegación quedan fuera de esta etapa y se incorporarán en tareas posteriores.
