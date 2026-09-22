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
3. Cinco KPIs principales en una sola línea en escritorio.
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
