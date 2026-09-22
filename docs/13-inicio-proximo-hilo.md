# 13 — LEER PRIMERO EN EL PRÓXIMO HILO

Fecha de cierre: 22/09/2026

## Objetivo del próximo hilo

**Empezar Configuración de empresa.**

No continuar con Roles y Permisos salvo que aparezca un problema concreto.

No empezar Auditoría.

## Estado exacto al cerrar

Repositorio:

```text
Nerpiti86/NeriSoft
rama estable: main
local habitual: D:\NeriSoft
```

Último bloque completado:

```text
Tarea 9.3.5 — Normalización de Roles y Permisos ✅
```

Merge:

```text
1d2e9ab2bf553a2bb53e9dd4f545152754c3a404
refactor: normalize roles and permission scope
```

GitHub Actions run #14: success.

`9.4 — Validación integral de permisos` queda pendiente, pero **no bloquea** el próximo módulo.

## Decisiones que NO hay que volver a discutir desde cero

### 1. Roles y Permisos se dejan por ahora

Motor actual:

```text
Usuario
→ Rol
→ Permisos
```

Administrador del sistema:

```text
acceso total
no es un rol
no necesita roles
```

Catálogo actual:

```text
Sistema
├── Usuarios
└── Roles y permisos
```

No crear permisos de módulos que todavía no existen.

Cada módulo nuevo define, aplica y prueba sus permisos junto con su funcionalidad.

### 2. Auditoría se posterga

No construir ahora:

- motor genérico de auditoría;
- event bus;
- snapshots universales;
- historial transversal;
- infraestructura “por las dudas”.

Motivo:

Todavía no hay suficientes operaciones reales de negocio para saber qué debe auditarse y con qué granularidad.

Cuando existan altas/modificaciones de maestros, movimientos, comprobantes, anulaciones, ajustes, etc., se diseña Auditoría sobre casos reales.

### 3. Regla arquitectónica de prioridad

Antes de construir algo preguntar:

```text
¿Lo necesitamos hoy?
¿Desbloquea la próxima operación?
¿Tenemos suficiente evidencia para diseñarlo?
¿Podemos postergarlo sin romper nada?
¿Es producto real o infraestructura imaginaria?
```

Secuencia preferida:

```text
Necesidad concreta
↓
Dependencias mínimas
↓
Funcionalidad real
↓
Uso real
↓
Patrón observado
↓
Abstracción
```

No generalizar antes de tiempo.

### 4. Holistor es referencia funcional permanente

Documentación:

https://holistor.atlassian.net/wiki/spaces/TDADGC/overview?homepageId=566427761

Usarla como:

- mapa de un ERP argentino real;
- fuente para descubrir entidades y dependencias;
- contraste para Ventas, Compras, Stock, Tesorería, Impuestos, Contabilidad y Administración;
- ayuda para no olvidar casos importantes.

NO usarla para:

- copiar UI;
- copiar pantalla por pantalla;
- implementar todos sus parámetros;
- trasladar su complejidad completa a NERISOFT.

Regla:

```text
Holistor = universo de referencia
NERISOFT = mínimo necesario para el circuito actual
```

La documentación de Administración de Holistor incluye, entre otros:

```text
Empresa
Puntos de Venta
Talonarios
Tipos de Comprobante
Monedas
Condiciones Fiscales
Tipos de Documento
Provincias
Localidades
Alícuotas
Tipos de Cobro y Pago
Conceptos
Unidades de Negocio
Parámetros
```

No crear todo eso ahora.

## Próximo foco: Configuración de empresa

La primera conversación del nuevo hilo debe resolver **qué necesita Empresa hoy** para habilitar los siguientes módulos.

Alcance candidato inicial:

```text
Razón social
Nombre comercial
CUIT
Domicilio
Localidad
Provincia
Código postal
Teléfono
Email
Condición fiscal
Moneda principal
```

Esto es candidato, no especificación cerrada.

Antes de implementar decidir:

- qué campos son realmente necesarios ahora;
- cuáles son simples datos de Empresa;
- cuáles merecen un maestro separado más adelante;
- si debe existir una sola empresa por instalación en esta etapa;
- cómo se integra en la portada de Configuración;
- qué permiso necesita, si corresponde.

No implementar todavía:

```text
ARCA / CAE
certificados
puntos de venta
talonarios
retenciones / percepciones
SMTP
contabilidad
parámetros genéricos masivos
```

salvo que el circuito que se está construyendo lo requiera.

## Orden funcional acordado

```text
Configuración de empresa
↓
Clientes
↓
Proveedores
↓
Productos
↓
Depósitos / Stock
↓
Ventas
↓
Cuenta corriente / cobranzas
↓
Compras
↓
Tesorería
↓
Contabilidad / Impuestos
```

Los maestros auxiliares se agregan cuando el circuito que los necesita aparezca.

## Reglas UI

- Desktop-first.
- No sobrecargar.
- No meter metadata porque sí.
- Tabla = resumen operativo.
- Ficha = detalle completo.
- No niveles de navegación innecesarios.
- No placeholders de funciones futuras.
- No parches CSS/JS para tapar causas de backend/template/datos.

## Reglas de datos

- SQLite solo en servidor.
- IDs enteros.
- Dinero futuro en centavos enteros, nunca FLOAT.
- Stock, cuenta corriente, tesorería y contabilidad derivados de movimientos.
- Operaciones compuestas atómicas.
- Fechas visibles en America/Argentina/Cordoba.

## Forma de trabajo

```text
1 tarea
→ revisar main
→ diseñar mínimo necesario
→ implementar en rama
→ PR
→ squash merge
→ GitHub Actions
→ git pull local
→ prueba visual/funcional
→ siguiente
```

Durante pruebas locales: **una sola acción o comando por mensaje**.

## Primera instrucción sugerida para el nuevo hilo

```text
Leé primero docs/13-inicio-proximo-hilo.md y docs/00-lectura-rapida.md del repo.
Después revisá main y empecemos a diseñar Configuración de empresa con el mínimo necesario, usando Holistor solo como referencia funcional y sin implementar complejidad futura.
```
