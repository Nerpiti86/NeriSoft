# HANDOFF ACTUAL — LEER PRIMERO EN EL PRÓXIMO HILO

Fecha de cierre: 22/09/2026

## Objetivo del próximo hilo

**Ejecutar Tarea 10.1 — Modelo + migración + permiso de Configuración de empresa.**

No volver a discutir desde cero el alcance de Empresa: quedó cerrado en la Tarea 10.0.

No continuar con Roles y Permisos salvo que aparezca un problema concreto.

No empezar Auditoría.

## Estado exacto al cerrar

Repositorio:

```text
Nerpiti86/NeriSoft
rama estable: main
local habitual: D:\NeriSoft
```

Última tarea completada:

```text
Tarea 10.0 — Normalización de documentación vigente ✅
```

Último bloque funcional previo:

```text
Tarea 9.3.5 — Normalización de Roles y Permisos ✅
```

`9.4 — Validación integral de permisos` queda pendiente, pero **no bloquea** Empresa.

## Decisiones que NO hay que volver a discutir desde cero

### 1. Configuración de empresa: alcance aprobado

Primera etapa:

```text
una sola empresa por instalación
sin listado de empresas
sin ABM multiempresa
acceso directo desde Configuración
```

Campos aprobados:

```text
Razón social        obligatoria
Nombre comercial    opcional
CUIT                 obligatorio, normalizado y validado
Condición fiscal    obligatoria
Domicilio fiscal    obligatorio
Localidad            obligatoria
Provincia            obligatoria
Código postal        opcional
Teléfono             opcional
Email                opcional
```

No crear todavía maestros separados para:

```text
Localidades
Provincias
Monedas
Condiciones fiscales
```

La moneda principal queda fuera de esta primera versión hasta que un circuito monetario real la necesite.

También quedan fuera por ahora:

```text
IIBB
inicio de actividades
logo
ARCA / CAE
certificados
puntos de venta
talonarios
retenciones / percepciones
SMTP
contabilidad
parámetros genéricos masivos
```

### 2. Permiso de Empresa

Se acordó un único permiso funcional:

```text
system.company.manage
```

Debe permitir consultar y actualizar los datos de la empresa.

El Administrador del sistema mantiene acceso total por bypass y no necesita roles.

No crear permisos ficticios de módulos futuros.

### 3. Regla para catálogo de permisos y migraciones

`app/core/permissions.py` representa el catálogo vigente esperado por la aplicación.

Las migraciones de Alembic representan la evolución histórica de bases existentes.

Por lo tanto:

- **no modificar** `0003_roles_permissions.py`;
- agregar `system.company.manage` al catálogo vigente;
- insertar el nuevo permiso mediante una migración nueva;
- no crear un sincronizador automático de permisos;
- agregar tests que detecten desalineación entre el catálogo esperado y una base migrada.

La coexistencia entre catálogo actual y migraciones históricas no se considera una duplicación incorrecta.

### 4. Roles y Permisos se dejan por ahora

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

Catálogo actualmente implementado antes de Empresa:

```text
Sistema
├── Usuarios
└── Roles y permisos
```

Cada módulo nuevo define, aplica y prueba sus permisos junto con su funcionalidad.

### 5. Auditoría se posterga

No construir ahora:

- motor genérico de auditoría;
- event bus;
- snapshots universales;
- historial transversal;
- infraestructura “por las dudas”.

Motivo:

Todavía no hay suficientes operaciones reales de negocio para saber qué debe auditarse y con qué granularidad.

Cuando existan altas/modificaciones de maestros, movimientos, comprobantes, anulaciones, ajustes y otras operaciones sensibles, se diseña Auditoría sobre casos reales.

### 6. Regla arquitectónica de prioridad

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

### 7. Holistor es referencia funcional permanente

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

## Próximas tareas del bloque Empresa

```text
10.1 Modelo + migración + permiso
↓
10.2 Backend + validaciones
↓
10.3 UI + prueba funcional
↓
Clientes
```

### Tarea 10.1

Objetivo limitado:

- crear modelo `Company`;
- crear tabla `companies`;
- sostener una sola empresa por instalación en esta etapa;
- crear migración nueva posterior a `0003_roles_permissions`;
- agregar `system.company.manage`;
- agregar tests de modelo/migración/permisos necesarios.

No implementar todavía formulario ni UI de Empresa en 10.1.

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
→ crear rama
→ implementar
→ validar
→ PR
→ squash merge a main
→ GitHub Actions
→ git pull local
→ prueba visual/funcional
→ siguiente
```

Durante pruebas locales: **una sola acción o comando por mensaje**.

## Primera instrucción sugerida para el próximo hilo

```text
Leé primero docs/HANDOFF-ACTUAL.md y docs/00-lectura-rapida.md.
Después revisá main y ejecutemos únicamente la Tarea 10.1:
modelo Company + migración + permiso system.company.manage + tests correspondientes.
No implementar todavía backend/formulario/UI de Empresa.
```
