# HANDOFF ACTUAL — LEER PRIMERO EN EL PRÓXIMO HILO

Fecha de cierre: 22/09/2026

## Objetivo del próximo hilo

**Ejecutar Tarea 10.2 — Backend + validaciones de Configuración de empresa.**

No implementar todavía la UI final de Empresa; eso corresponde a 10.3.

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
Tarea 10.1 — Modelo + migración + permiso de Empresa ✅
```

También completada:

```text
Tarea 10.0 — Normalización de documentación vigente ✅
```

`9.4 — Validación integral de permisos` queda pendiente, pero **no bloquea** Empresa.

## Qué quedó implementado en 10.1

### Modelo

Existe:

```text
app/models/company.py
Company
companies
```

Campos:

```text
id
legal_name
trade_name
tax_id
tax_condition
fiscal_address
city
province
postal_code
phone
email
```

La tabla es singleton mediante:

```text
CHECK (id = 1)
```

Esto hace cumplir a nivel de base la decisión de una sola empresa por instalación.

### Migración

Nueva migración:

```text
0004_company
↓
0003_roles_permissions
```

Crea `companies` e inserta el permiso de Empresa.

No modificar migraciones históricas ya aplicadas.

### Permiso

Permiso implementado:

```text
system.company.manage
```

Definición funcional:

```text
Sistema
└── Empresa
    └── Administrar datos de empresa
```

Permite consultar y actualizar los datos generales y fiscales de la empresa.

El Administrador del sistema mantiene acceso total por bypass y no necesita roles.

### Tests

Se incorporaron pruebas para:

- persistencia de los 10 campos aprobados;
- rechazo de una segunda empresa;
- migración completa a `head`;
- igualdad exacta entre permisos sembrados por migraciones y `ALL_PERMISSION_CODES`.

La regla queda:

```text
catálogo vigente en código
+
migraciones históricas/incrementales
+
test de consistencia
```

No crear sincronizador automático de permisos.

## Alcance de Empresa que NO hay que volver a discutir

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

## Tarea 10.2 — alcance exacto

Implementar únicamente backend y validaciones necesarias para Empresa.

Debe resolver:

- obtener la única empresa si existe;
- crearla si todavía no existe;
- actualizarla si ya existe;
- proteger lectura/escritura con `system.company.manage`;
- mantener bypass del Administrador del sistema;
- CSRF en escritura;
- normalización y validación de CUIT;
- validación de campos obligatorios;
- validación de email cuando se informe;
- límites de longitud coherentes con el modelo;
- tests de backend/validaciones.

No implementar todavía:

- diseño final de formulario;
- tarjeta visual definitiva en Configuración;
- navegación UI final;
- maestros auxiliares;
- Auditoría;
- ARCA;
- multiempresa.

La Tarea 10.3 será la responsable de la UI y prueba visual/funcional.

## Roles y Permisos

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

Catálogo actual después de 10.1:

```text
Sistema
├── Usuarios
├── Roles y permisos
└── Empresa
```

Cada módulo nuevo define, aplica y prueba sus permisos junto con su funcionalidad.

## Auditoría se posterga

No construir ahora:

- motor genérico de auditoría;
- event bus;
- snapshots universales;
- historial transversal;
- infraestructura “por las dudas”.

Cuando existan suficientes operaciones reales, se diseña Auditoría sobre casos concretos.

## Regla arquitectónica de prioridad

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

## Holistor

Referencia funcional permanente:

https://holistor.atlassian.net/wiki/spaces/TDADGC/overview?homepageId=566427761

Usarla para descubrir entidades, dependencias y casos reales.

No usarla para copiar UI ni trasladar toda su complejidad a NERISOFT.

```text
Holistor = universo de referencia
NERISOFT = mínimo necesario para el circuito actual
```

## Secuencia actual

```text
10.0 Documentación ✅
↓
10.1 Modelo + migración + permiso ✅
↓
10.2 Backend + validaciones
↓
10.3 UI + prueba funcional
↓
Clientes
```

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
→ prueba
→ siguiente
```

Durante pruebas locales: **una sola acción o comando por mensaje**.

## Primera instrucción sugerida para el próximo hilo

```text
Leé primero docs/HANDOFF-ACTUAL.md y docs/00-lectura-rapida.md.
Después revisá main y ejecutemos únicamente la Tarea 10.2:
backend + validaciones de Company, permiso system.company.manage, CSRF y tests.
No implementar todavía la UI final de Empresa.
```
