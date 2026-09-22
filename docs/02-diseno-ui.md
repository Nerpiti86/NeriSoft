# 02 — Diseño de interfaz

## Dirección visual

NERISOFT usará una interfaz administrativa moderna, sobria y densa, priorizando productividad sobre ornamentación.

## Identidad

- Nombre: **NERISOFT**
- Paleta principal: grafito + dorado
- Fondo general claro
- Sidebar grafito
- Dorado como acento, no como superficie dominante

Paleta inicial de referencia:

```css
:root {
  --graphite-950: #141414;
  --graphite-900: #1A1A1A;
  --graphite-800: #242424;
  --graphite-700: #303030;
  --graphite-600: #444444;

  --gold-500: #C8A24A;
  --gold-400: #D7B75F;
  --gold-300: #E2C978;

  --surface: #F7F7F5;
  --surface-muted: #EFEFEC;
  --border: #D9D9D4;

  --text: #1A1A1A;
  --text-muted: #6A6A66;

  --success: #2E7D5B;
  --warning: #B7791F;
  --danger: #B44747;
  --info: #3F6F8F;
}
```

Los colores semánticos no deben reemplazarse por dorado. El dorado representa identidad; verde, rojo, ámbar y azul conservan significado funcional.

## Tipografía

- **Geist** es la tipografía de interfaz.
- No se usarán stacks de fuentes de sistema nombradas como reemplazo visual. El único fallback genérico será `sans-serif`.
- **Geist Mono** queda reservado para casos técnicos específicos y no se usa por defecto en datos administrativos.
- Datos numéricos importantes usan números tabulares sobre Geist.
- No se deben introducir otras familias tipográficas sin una decisión explícita de diseño.

```css
body {
  font-family: "Geist", sans-serif;
  font-synthesis: none;
  font-variant-numeric: tabular-nums lining-nums;
}

.numeric,
.amount,
.quantity,
.percentage {
  font-variant-numeric: tabular-nums lining-nums;
}
```

Importes alineados a la derecha.

## Radios y sombras

NERISOFT debe evitar el aspecto excesivamente redondeado. Los radios serán contenidos y consistentes.

```css
:root {
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 10px;

  --shadow-sm: 0 1px 2px rgb(0 0 0 / 7%),
               0 4px 12px rgb(0 0 0 / 4%);
  --shadow-md: 0 10px 28px rgb(0 0 0 / 10%),
               0 2px 8px rgb(0 0 0 / 5%);
}
```

Reglas:

- paneles y cards principales: hasta `10px`
- controles habituales: `6–8px`
- evitar radios grandes de `16–20px` en superficies administrativas
- pills y badges pueden usar radios mayores cuando su semántica lo requiera
- las sombras deben ser visibles pero limpias, con profundidad moderada y sin efecto flotante exagerado
- usar sombras por jerarquía: `shadow-sm` para controles destacados y `shadow-md` para paneles principales

## Layout

La aplicación ocupa el viewport completo.

```css
html,
body {
  width: 100%;
  height: 100%;
  margin: 0;
}

.app-shell {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}
```

No se usará un contenedor principal centrado con `max-width`.

## Sidebar

- Expandida: aproximadamente 240 px.
- Colapsada: aproximadamente 64 px.
- Debe conservar acceso a todas las secciones mediante iconos.
- En estado colapsado debe mostrar tooltips.
- Estado visual persistente por usuario o navegador.

Navegación prevista:

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

## Header

Debe reservar espacio para:

- contexto de página
- búsqueda global futura
- empresa actual
- usuario actual
- acciones rápidas futuras

## Densidad

Valores de referencia:

```text
Header:            ~52 px
Sidebar:           240 px
Sidebar colapsada: 64 px
Inputs:            34–38 px
Botones:           34–38 px
Filas de tabla:    36–40 px
Tabs:              ~40 px
```

NERISOFT es desktop-first. No debe desperdiciar espacio como una interfaz móvil ampliada.

## Tablas

Las tablas son un componente central del ERP.

La densidad no significa mostrar todo. Una tabla debe permitir **identificar, comparar y actuar rápidamente**; el detalle secundario pertenece a la ficha o vista del registro.

Reglas:

- alta densidad de información útil, no alta cantidad de metadatos
- incluir únicamente columnas necesarias para la decisión o acción principal de esa grilla
- evitar repetir tipo, estado, roles, permisos, descripciones, badges u otros metadatos si no aportan comparación o acción real
- no trasladar a la tabla toda la información disponible en el modelo de datos
- cuando un dato sea secundario, mostrarlo en la ficha/vista del registro en lugar de agregar otra columna
- antes de agregar una columna, comprobar si responde una pregunta frecuente del usuario en esa pantalla
- columnas numéricas alineadas a la derecha
- cabecera clara y persistente cuando corresponda
- filtros visibles
- búsqueda rápida
- paginación consistente
- estados con badges semánticos solo cuando el estado sea relevante para operar la lista
- acciones previsibles

Regla práctica:

```text
Tabla = resumen operativo
Ficha = detalle completo
```

## Patrón de listados

Todos los maestros y módulos deben reutilizar el mismo patrón:

```text
Título
Acción primaria
Buscar
Filtros
Tabla
Paginación
```

Ejemplo:

```text
CLIENTES                           [+ Nuevo cliente]

[ Buscar cliente... ]   Estado [Todos]   Provincia [Todas]

Código | Razón social | CUIT | Saldo | Estado
```

## Fichas

Las fichas extensas utilizarán pestañas cuando sea útil.

Ejemplo de cliente:

```text
[ Datos ] [ Cuenta corriente ] [ Comprobantes ] [ Contactos ] [ Auditoría ]
```

## Comprobantes

Una operación importante debe mostrar sus impactos y relaciones.

Ejemplo:

```text
Factura A 0004-00001234
Estado: Emitida

Impactos
✓ Cuenta corriente
✓ Stock
✓ IVA
✓ Contabilidad
✓ CAE

Relacionados
Pedido #882
Remito #713
Recibo #391
Asiento #14582
```

## Componentes base a normalizar

- botón
- input
- select
- checkbox
- tabla
- badge
- modal
- dropdown
- tabs
- card
- alert
- paginación
- empty state

La intención es evitar que cada módulo invente su propia interfaz.
