# 12 — Resumen del proyecto y contexto para nuevo hilo

Actualizado: 22/09/2026

Este documento es la fuente de contexto consolidado para continuar NERISOFT. Para el próximo hilo leer primero [`HANDOFF-ACTUAL.md`](HANDOFF-ACTUAL.md).

## Proyecto

- Nombre: **NERISOFT**
- Repositorio: `Nerpiti86/NeriSoft`
- Rama: `main`
- Instalación local habitual: `D:\NeriSoft`
- Modalidad: multiusuario en red local
- SQLite vive únicamente en el servidor; los clientes acceden por HTTP.

## Regla de trabajo

```text
1 tarea -> revisar main -> rama -> implementar -> validar -> PR -> squash merge -> main -> GitHub Actions -> pull local -> prueba -> siguiente tarea
```

Durante pruebas locales se avanza una acción/comando por mensaje.

No se ocultan problemas funcionales, de autorización o de renderizado mediante parches de CSS/JavaScript. La causa debe corregirse en la capa responsable (backend, template, datos o estilo según corresponda) y cualquier workaround previo debe eliminarse al aplicar la solución correcta.

## Decisión vigente

Se decidió **dejar Roles y Permisos por ahora**.

La Tarea 9.3.5 quedó completada y mergeada en `main` en el commit `1d2e9ab2bf553a2bb53e9dd4f545152754c3a404`. GitHub Actions run #14 terminó correctamente.

La Tarea 9.4 — Validación integral de permisos — queda **pendiente**, pero deja de ser el próximo paso obligatorio.

También se decidió **postergar Auditoría**. La razón es arquitectónica: todavía no existen suficientes operaciones reales de negocio para definir un motor de auditoría transversal con fundamento. No se construirá ahora un sistema genérico de eventos, snapshots o historial universal “por las dudas”.

La Tarea 10.0 cerró la normalización documental y fijó el alcance mínimo de Empresa.

La Tarea 10.1 implementó el modelo `Company`, la tabla singleton `companies`, la migración `0004_company`, el permiso `system.company.manage` y la prueba de consistencia entre catálogo y base migrada.

El próximo trabajo es:

```text
10.2 Empresa: backend y validaciones
↓
10.3 Empresa: UI y prueba funcional
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
```

## Lógica de priorización

Para decidir si una infraestructura, abstracción o módulo transversal debe construirse ahora:

1. ¿Existe una necesidad real hoy?
2. ¿Desbloquea la próxima operación real?
3. ¿Tenemos suficiente información para diseñarlo correctamente?
4. ¿Puede postergarse sin romper lo existente?
5. ¿Estamos resolviendo un problema real o construyendo para un sistema imaginario?

Patrón preferido:

```text
Necesidad concreta
↓
Dependencias mínimas
↓
Funcionalidad real
↓
Uso real
↓
Problemas reales
↓
Generalizar cuando aparezca un patrón
```

Regla:

> No diseñar una capa transversal importante hasta tener uno o más casos reales que la justifiquen.

Los permisos tuvieron una necesidad concreta porque ya existían operaciones administrativas. Auditoría todavía no tiene suficiente negocio real debajo.

## Referencia funcional externa: Holistor Gestión ERP

Referencia principal:

https://holistor.atlassian.net/wiki/spaces/TDADGC/overview?homepageId=566427761

Se adopta como **referencia funcional permanente**, no como especificación de NERISOFT.

La documentación pública de Holistor organiza un ERP argentino maduro en áreas como Ventas, Compras, Stock, Tesorería, Impuestos, Contabilidad y Administración. Dentro de Administración incluye, entre otros, Empresa, Puntos de Venta, Talonarios, Tipos de Comprobante, Monedas, Condiciones Fiscales, Tipos de Documento, Provincias, Localidades, Alícuotas, Tipos de Cobro/Pago, Conceptos, Unidades de Negocio y parámetros.

Uso correcto:

- consultar qué entidades y dependencias utiliza un ERP real para resolver un circuito;
- descubrir maestros que quizá sean necesarios;
- contrastar nuestro diseño antes de inventar estructuras desde cero;
- revisar particularidades del contexto argentino cuando lleguen los módulos correspondientes.

Uso incorrecto:

- copiar pantalla por pantalla;
- copiar su UI;
- implementar ahora todos sus parámetros;
- crear maestros sin un circuito que los necesite;
- trasladar a NERISOFT toda la complejidad acumulada de un ERP maduro.

Regla:

```text
Holistor = mapa del universo posible
NERISOFT = implementar solo lo necesario en la etapa actual
```

## Próximo bloque: Configuración de empresa

Alcance mínimo aprobado:

- una sola empresa por instalación;
- razón social obligatoria;
- nombre comercial opcional;
- CUIT obligatorio, normalizado y validado;
- condición fiscal obligatoria;
- domicilio fiscal obligatorio;
- localidad obligatoria;
- provincia obligatoria;
- código postal opcional;
- teléfono opcional;
- email opcional.

En esta etapa localidad, provincia y condición fiscal no requieren maestros independientes.

No implementar ahora:

- moneda principal;
- IIBB;
- inicio de actividades;
- logo;
- ARCA/CAE;
- certificados digitales;
- puntos de venta;
- talonarios;
- retenciones/percepciones;
- SMTP;
- parámetros contables;
- grandes catálogos auxiliares que todavía no consume ninguna operación.

Los maestros secundarios se introducen cuando el módulo que los necesita exista.

La portada de Configuración tendrá una entrada directa a Empresa, sin listado intermedio ni ABM multiempresa. El permiso funcional previsto es `system.company.manage`.

## Stack actual

- Python
- FastAPI
- SQLAlchemy 2
- SQLite
- Alembic
- Jinja2
- HTMX local
- Vanilla JavaScript
- CSS propio
- Geist local
- Tabler Icons Webfont local
- Uvicorn
- pwdlib + Argon2
- SessionMiddleware de Starlette
- pytest para validaciones básicas

## Arquitectura y reglas

- SQLite: WAL + FK + `busy_timeout=5000`.
- Migración futura a PostgreSQL si la concurrencia lo requiere.
- Primera etapa: una sola empresa por instalación. Multiempresa queda fuera del alcance actual; no se agregará complejidad preventiva para soportarla.
- Dinero futuro: `BIGINT` en centavos; nunca `FLOAT`.
- Fechas: `DATE` / `DATETIME`.
- IDs internos: enteros.
- Stock, cuentas corrientes, tesorería y contabilidad se derivan de movimientos.
- Operaciones compuestas deben ser atómicas.
- Fechas/hora visibles se centralizan progresivamente y se presentan en `America/Argentina/Cordoba`.

## Seguridad actual

- login por username o email;
- Argon2;
- usuarios inactivos rechazados;
- sesión firmada, `HttpOnly`, `SameSite=Lax`, máximo 8 horas;
- CSRF en login, logout y escrituras administrativas;
- helpers de auth/CSRF centralizados;
- `/setup` bloqueado cuando ya existen usuarios;
- en una instalación vacía `/setup` solo acepta loopback por defecto;
- `NERISOFT_SETUP_ALLOW_REMOTE=true` permite habilitar temporalmente setup remoto;
- `superuser` mantiene bypass administrativo total;
- permisos efectivos se obtienen desde roles activos;
- roles y permisos cuentan con controles de alcance para evitar escalada;
- Gestión de Usuarios usa permisos granulares para ver, crear, editar, cambiar estado y asignar roles;
- un gestor delegado no puede modificar superusuarios ni usuarios con permisos efectivos superiores a los propios;
- un gestor delegado solo puede asignar roles dentro de su propio alcance y no puede modificar sus propios roles;
- para despliegue real en red se requiere HTTPS y `NERISOFT_SESSION_HTTPS_ONLY=true`.

`9.4 — Validación integral de permisos` sigue pendiente y deberá retomarse, pero no bloquea Configuración de empresa.

## UI actual

- viewport completo;
- sidebar grafito, topbar oscura, acento dorado, workspace claro;
- desktop-first, referencia 1920×1080 a 100%;
- Geist;
- Tabler Icons;
- radios 6/8/10 px;
- números tabulares;
- shell autenticado compartido en `authenticated.html`;
- Inicio y Configuración usan el mismo shell;
- navegación interna usa HTMX y reemplaza solo `.workspace`;
- fallback HTML normal si HTMX no está disponible;
- Select NERISOFT reutilizable;
- Configuración tiene una portada propia en `/configuracion`;
- Usuarios y Roles y permisos son destinos independientes dentro de Configuración;
- el nombre/avatar de la barra superior abre `/mi-cuenta`;
- la tabla de Usuarios representa `Acceso` y no muestra al Administrador del sistema como si fuera un rol;
- Roles y permisos permite alta, edición y activación/desactivación;
- el listado de Roles y el formulario Nuevo/Editar rol son vistas diferenciadas;
- la tabla de Roles se limita a información operativa;
- la selección de permisos se organiza primero por área funcional y después por grupo.

## Densidad y metadatos en tablas

Las tablas son resúmenes operativos, no fichas completas.

Reglas:

- mostrar solo columnas y metadatos necesarios para identificar, comparar o actuar;
- evitar repetir tipo, estado, roles, permisos, badges, descripciones u otros datos secundarios cuando no aporten una decisión real;
- no confundir alta densidad de información útil con alta cantidad de metadatos;
- mover el detalle secundario a la ficha o vista del registro;
- mantener la tabla visualmente liviana y escalable.

Regla corta:

```text
Tabla = resumen operativo
Ficha = detalle completo
```

## Arquitectura de navegación de Configuración

```text
Configuración
└── Accesos y seguridad
    ├── Usuarios
    └── Roles y permisos

Barra superior
└── Mi cuenta
```

La Tarea 10.3 incorporará **Empresa** como acceso directo desde la portada de Configuración. No crear niveles de navegación intermedios sin necesidad real.

## Terminología de acceso

- **Usuario**: cuenta de una persona que puede iniciar sesión en NERISOFT.
- **Rol**: conjunto reutilizable de permisos.
- **Permiso**: acción concreta que un rol habilita.
- **Administrador del sistema**: acceso total que no depende de roles.

El Administrador del sistema se representa como tipo de acceso, nunca como rol.

## Catálogo de permisos y crecimiento por módulos

Estado actual:

```text
Sistema
├── Usuarios
└── Roles y permisos
```

No se crean permisos ficticios de módulos futuros.

```text
Cada módulo nuevo debe definir, aplicar y probar sus permisos junto con su funcionalidad.
```

Esto no obliga a terminar 9.4 antes de iniciar Configuración de empresa; significa que, al crear funcionalidad sensible nueva, sus permisos deben diseñarse con el propio módulo cuando corresponda.

Las migraciones históricas no se reescriben. `0003_roles_permissions` permanece congelada. Cada permiso nuevo se agrega al catálogo vigente de `app/core/permissions.py` y mediante una migración nueva que lleve las bases existentes al mismo estado. No se construye un sincronizador automático: los tests deben detectar desalineaciones entre el catálogo esperado y una base migrada.

## Assets locales

Versiones fijadas:

```text
Geist 1.7.2
Tabler Icons 3.35.0
HTMX 2.0.7
```

## Base de datos

```text
D:\NeriSoft\data\nerisoft.db
```

Migraciones:

```text
0001_users
0002_user_superuser
0003_roles_permissions
```

## Tests

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

GitHub Actions ejecuta compilación, migraciones sobre SQLite temporal, pytest y `node --check` para los JS principales en cada push a `main`.

## Funcionalidad completada

1. Bootstrap técnico.
2. Shell principal.
3. Dashboard visual base.
4. Login funcional.
5. Modelo `users` + Argon2.
6. Primer administrador.
7. Sesiones + CSRF + logout.
8. Gestión de usuarios.
9. Select NERISOFT.
10. Assets locales.
11. Navegación parcial HTMX.
12. Saneamiento técnico previo a Roles/Permisos.
13. Tarea 9.1: modelo/catálogo/helpers de Roles y Permisos.
14. Tarea 9.2: gestión de roles.
15. Tarea 9.3: asignación de roles y permisos granulares.
16. Reorganización de Configuración y Mi cuenta.
17. Tarea 9.3.5: normalización de Roles y Permisos.
18. Tarea 10.0: normalización de documentación vigente y cierre del alcance mínimo de Empresa.
19. Tarea 10.1: modelo Company, migración 0004, permiso de Empresa y tests de consistencia.

## Próximo bloque

```text
10.2 Empresa: backend y validaciones
→ 10.3 Empresa: UI y prueba funcional
```

Después:

```text
Clientes
→ Proveedores
→ Productos
→ Depósitos / Stock
→ Ventas
→ Cuenta corriente / cobranzas
→ Compras
→ Tesorería
→ Contabilidad / Impuestos
```

Pendientes transversales que no deben confundirse con el próximo paso:

```text
9.4 Validación integral de permisos
Auditoría
Seguridad operativa adicional
```

## Contexto breve para hilo nuevo

```text
Estamos desarrollando NERISOFT, ERP administrativo/comercial/contable.
Repo: Nerpiti86/NeriSoft, main, local D:\NeriSoft.

LEER PRIMERO docs/HANDOFF-ACTUAL.md.

Decisión actual:
- dejamos Roles y Permisos por ahora;
- 9.4 queda pendiente, no bloquea;
- Auditoría se posterga hasta tener operaciones reales;
- Empresa queda limitada a una sola empresa por instalación y 10 campos aprobados;
- sin moneda principal ni maestros auxiliares en esta etapa;
- próximo paso: 10.1 modelo + migración + permiso system.company.manage;
- después: 10.2 backend → 10.3 UI → Clientes → Proveedores → Productos → Depósitos/Stock → Ventas.

Referencia funcional:
Holistor Gestión ERP:
https://holistor.atlassian.net/wiki/spaces/TDADGC/overview?homepageId=566427761
Usarla para descubrir dependencias/casos reales, NO para copiar UI ni implementar toda su complejidad.

Regla arquitectónica:
primero necesidad concreta y operación real; generalizar después de observar patrones.
No construir infraestructura imaginaria “por las dudas”.

UI:
tabla = resumen operativo; ficha = detalle completo.
No parches CSS/JS; resolver causa raíz.

Trabajo:
1 tarea -> validar -> commit/PR -> main -> pull local -> prueba.
En pruebas locales, una acción/comando por mensaje.
```
