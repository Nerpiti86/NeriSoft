# 14 — Select NERISOFT

Actualizado: 22/09/2026

## Objetivo

NERISOFT define un componente visual propio para selecciones simples y deja de depender del aspecto nativo del navegador como interfaz principal.

El componente forma parte del lenguaje visual general del ERP y debe reutilizarse en filtros y formularios con listas cortas.

## Principio técnico

El control conserva un `<select>` HTML real como fuente de datos y mecanismo de envío del formulario.

La mejora visual se aplica mediante JavaScript:

```text
<select real>
      ↓
mejora progresiva
      ↓
botón NERISOFT + lista personalizada
```

Si JavaScript no se ejecuta, el `select` nativo permanece utilizable.

Cuando JavaScript está disponible:

- el `select` real permanece en el DOM;
- queda visualmente oculto;
- conserva `name`, `value` y las opciones reales;
- el componente visual sincroniza su selección con ese control;
- al elegir una opción se dispara el evento `change` normal.

Esto evita duplicar la lógica de formularios y mantiene compatibilidad con FastAPI.

## Alcance automático

Por defecto se mejoran los:

```html
<select>
```

simples de la aplicación.

No se transforman:

- `select[multiple]`;
- controles que declaren `data-native-select`.

Ejemplo de excepción explícita:

```html
<select data-native-select>
```

## Diseño

El Select NERISOFT utiliza:

- Geist;
- altura base de `34px`;
- radio de `6px`;
- fondo claro;
- borde contenido;
- icono Tabler `ti-chevron-down`;
- dorado únicamente como acento de foco y selección;
- `ti-check` para la opción seleccionada;
- menú compacto;
- sombra moderada;
- scroll interno en listas largas.

El menú se renderiza con posición fija respecto del viewport para evitar recortes causados por paneles con `overflow`.

La apertura intenta usar el espacio inferior disponible y cambia hacia arriba cuando corresponde.

## Accesibilidad e interacción

El disparador visual expone:

- `aria-haspopup="listbox"`;
- `aria-expanded`;
- `aria-controls`;
- nombre accesible derivado de `aria-label`, `aria-labelledby` o su etiqueta.

La lista usa:

```text
role="listbox"
role="option"
aria-selected
```

Interacciones soportadas:

- clic para abrir/cerrar;
- clic en una opción para seleccionar;
- `ArrowDown` / `ArrowUp` para recorrer opciones;
- `Home` / `End`;
- `Enter` o `Space` para seleccionar;
- `Escape` para cerrar;
- `Tab` conserva el flujo normal de foco;
- clic fuera del control cierra el menú.

Los controles deshabilitados y las opciones deshabilitadas conservan su estado.

## Sincronización

El componente escucha el evento `change` del `select` real y actualiza la interfaz.

También vuelve a sincronizarse después de un `reset` del formulario.

Los `select` simples agregados dinámicamente al DOM se detectan mediante `MutationObserver`.

Para integraciones manuales queda disponible:

```javascript
window.NERISOFTSelect.enhance();
```

## Primera aplicación

La primera aplicación real del componente es:

```text
Configuración → Usuarios → filtro Estado
```

El filtro continúa enviando:

```text
estado=todos
estado=activos
estado=inactivos
```

por lo que no cambia ninguna ruta ni lógica del backend.

## Archivos

Implementación global:

```text
app/static/css/select.css
app/static/js/select.js
```

Carga global:

```text
app/templates/base.html
```

## Select vs. Combobox

Este componente está pensado para listas cortas o medianas de opciones conocidas.

No debe convertirse en un buscador improvisado.

Para entidades con muchas opciones, como:

- clientes;
- productos;
- proveedores;
- cuentas contables;

se desarrollará un componente **Combobox NERISOFT** independiente, reutilizando el mismo lenguaje visual cuando corresponda.
