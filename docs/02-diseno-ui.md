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

- Geist para toda la interfaz.
- Geist Mono solo cuando exista una razón concreta de legibilidad técnica.
- Datos numéricos importantes con números tabulares.

```css
.numeric,
.amount,
.quantity,
.percentage {
  font-variant-numeric: tabular-nums lining-nums;
}
```

Importes alineados a la derecha.

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

Reglas:

- alta densidad de información
- columnas numéricas alineadas a la derecha
- cabecera clara y persistente cuando corresponda
- filtros visibles
- búsqueda rápida
- paginación consistente
- estados con badges semánticos
- acciones previsibles

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
