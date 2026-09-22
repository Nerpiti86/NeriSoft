# 12 — Resumen del proyecto y contexto para nuevo hilo

Actualizado: 22/09/2026

Este documento es la fuente de contexto consolidado para continuar NERISOFT en un hilo nuevo.

## Proyecto

- Nombre: **NERISOFT**
- Repositorio: `Nerpiti86/NeriSoft`
- Rama: `main`
- Instalación local habitual: `D:\NeriSoft`
- Modalidad: multiusuario en red local
- SQLite vive únicamente en el servidor; los clientes acceden por HTTP.

## Regla de trabajo

```text
1 tarea -> validación -> 1 commit coherente en main -> pull local -> prueba -> siguiente tarea
```

Durante pruebas locales se avanza una acción/comando por mensaje.

No se ocultan problemas funcionales, de autorización o de renderizado mediante parches de CSS/JavaScript. La causa debe corregirse en la capa responsable (backend, template, datos o estilo según corresponda) y cualquier workaround previo debe eliminarse al aplicar la solución correcta.

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
- Multiempresa prevista, todavía no implementada.
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
- Select NERISOFT reutilizable, con listeners globales únicos y limpieza de instancias al retirar nodos;
- Configuración tiene una portada propia en `/configuracion`;
- Usuarios y Roles y permisos son destinos independientes dentro de Configuración, sin pestañas redundantes entre sí;
- el nombre/avatar de la barra superior abre `/mi-cuenta` para consultar los datos y tipo de acceso de la sesión actual;
- la tabla de Usuarios representa `Acceso` y no muestra al Administrador del sistema como si fuera un rol;
- Roles y permisos permite alta, edición y activación/desactivación;
- el listado de Roles y el formulario Nuevo/Editar rol son vistas diferenciadas y no se renderizan juntos;
- la tabla de Roles se limita a información operativa y no muestra códigos técnicos ni metadatos secundarios;
- la selección de permisos se organiza primero por área funcional y después por grupo.

## Densidad y metadatos en tablas

Las tablas son resúmenes operativos, no fichas completas.

Reglas:

- mostrar solo columnas y metadatos necesarios para identificar, comparar o actuar;
- evitar repetir tipo, estado, roles, permisos, badges, descripciones u otros datos secundarios cuando no aporten una decisión real;
- no confundir alta densidad de información útil con alta cantidad de metadatos;
- mover el detalle secundario a la ficha o vista del registro;
- mantener la tabla visualmente liviana y escalable a medida que los módulos crecen.

Regla corta:

```text
Tabla = resumen operativo
Ficha = detalle completo
```

## Arquitectura de navegación de Configuración

La navegación debe escalar sin agregar niveles innecesarios ni mezclar consulta personal con administración:

```text
Configuración
└── Accesos y seguridad
    ├── Usuarios
    └── Roles y permisos

Barra superior
└── Mi cuenta
```

Reglas:

- el menú lateral `Configuración` apunta a `/configuracion`, no a una pantalla hija;
- la portada de Configuración agrupa opciones por tema y solo incorpora áreas reales cuando se implementan;
- `Usuarios` administra cuentas del sistema;
- `Roles y permisos` administra roles parametrizables y sus permisos;
- `Mi cuenta` es una vista personal de consulta y no sustituye a Gestión de Usuarios;
- no agregar una pantalla intermedia `Accesos y seguridad`: es una categoría visual dentro de Configuración, no otro nivel de navegación;
- los breadcrumbs de las pantallas hijas vuelven a `/configuracion`.

## Terminología de acceso en la interfaz

La UI debe mantener un único modelo mental y no mezclar sinónimos técnicos:

- **Usuario**: cuenta de una persona que puede iniciar sesión en NERISOFT.
- **Rol**: conjunto reutilizable de permisos que se asigna a uno o más usuarios.
- **Permiso**: acción concreta que un rol habilita.
- **Administrador del sistema**: cuenta con acceso total que no depende de roles para obtener permisos.

Flujo que debe comunicar la interfaz:

```text
1. Crear un rol.
2. Elegir los permisos de ese rol.
3. Crear o editar un usuario.
4. Asignarle uno o más roles.
5. Los permisos de los roles asignados se combinan para definir el acceso del usuario.
```

En textos destinados al usuario final se evita usar `perfil`, `alcance` o `autorización` como sinónimos de rol/permisos. Esos términos pueden existir en documentación técnica o controles internos cuando sean precisos, pero la interfaz debe explicar la acción en lenguaje directo.

El Administrador del sistema no debe representarse dentro de una columna o listado de Roles. En vistas de usuarios debe mostrarse como **tipo de acceso**. Los usuarios comunes se muestran como **Acceso por roles** y debajo pueden detallarse los roles asignados.

## Catálogo de permisos y crecimiento por módulos

El motor RBAC es general, pero el catálogo visible debe representar únicamente funcionalidades que ya existen.

Estado actual:

```text
Sistema
├── Usuarios
└── Roles y permisos
```

Todos los permisos implementados actualmente pertenecen al área `Sistema`. No se deben crear permisos ficticios para Ventas, Compras, Stock, Tesorería, Contabilidad u otros módulos antes de implementar esas funciones.

El nombre de un rol no concede acceso por sí mismo. Roles operativos como `Vendedor`, `Cajero` o `Compras` solo adquieren sentido cuando existen permisos funcionales que puedan asignárseles.

Regla obligatoria para módulos futuros:

```text
Cada módulo nuevo debe definir, aplicar y probar sus permisos junto con su funcionalidad.
```

La autorización backend sigue siendo la fuente de verdad. La UI puede ocultar o simplificar opciones, pero nunca reemplaza el control de permisos del servidor.

## Assets locales

Versiones fijadas:

```text
Geist 1.7.2
Tabler Icons 3.35.0
HTMX 2.0.7
```

Instalación:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\vendor-assets.ps1
```

No existe fallback CDN de ejecución. Si falta un asset crítico, el arranque falla de forma explícita.

## Convenciones visibles

Comprobantes:

```text
FC  Factura
NC  Nota de Crédito
ND  Nota de Débito
RC  Recibo
OP  Orden de Pago
OC  Orden de Compra
RM  Remito
PR  Presupuesto
PD  Pedido
```

Letra fiscal:

```text
FC A 0004-00001842
```

El HTML debe emitir directamente estas abreviaturas; no se corrigen con JavaScript.

Fechas:

```text
dd/mm/yyyy
dd/mm/yyyy HH:mm
```

## Funcionalidad completada

1. Bootstrap técnico.
2. Shell principal.
3. Dashboard visual base con datos de muestra.
4. Login visual y luego funcional.
5. Modelo `users` + Argon2.
6. Configuración inicial del primer administrador.
7. Sesiones + CSRF + logout + dashboard protegido.
8. Gestión de usuarios: listar, buscar, filtrar, crear, editar, activar/desactivar.
9. Select NERISOFT.
10. Assets locales.
11. Navegación parcial HTMX.
12. Saneamiento técnico previo a Roles/Permisos: shell compartido, auth centralizado, fechas, setup, tests y documentación sincronizada.
13. Tarea 9.1: modelo `roles` / `permissions`, asociaciones, catálogo y helpers de autorización.
14. Tarea 9.2: gestión de roles, permisos y estado desde Configuración.
15. Tarea 9.3: asignación de roles a usuarios y permisos granulares en Gestión de Usuarios.
16. Reorganización de Configuración: portada propia, Usuarios/Roles como destinos independientes, Mi cuenta separada y representación explícita del tipo de acceso.
17. Tarea 9.3.5: normalización de Roles y Permisos; alcance actual explícito en `Sistema`, formulario separado del listado, reducción de metadatos y regla de permisos por módulo futuro.

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

La Tarea 9.3.5 no requiere una migración nueva: clasifica el catálogo de aplicación y reorganiza UI/backend sin cambiar el esquema relacional existente.

## Tests

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

GitHub Actions ejecuta compilación, migraciones sobre SQLite temporal, pytest y `node --check` para los JS principales en cada push a `main`.

## Próximo bloque

La siguiente tarea funcional prevista es:

```text
Tarea 9.4 — Validación integral de permisos
```

9.4 valida integralmente el motor y los permisos que existen en ese momento; no pretende anticipar permisos de módulos todavía no implementados.

Después:

```text
Auditoría
→ Configuración de empresa
→ Clientes
→ resto de maestros y circuitos
```

## Contexto breve para hilo nuevo

```text
Estamos desarrollando NERISOFT, ERP administrativo/comercial/contable.
Repo: Nerpiti86/NeriSoft, rama main, local D:\NeriSoft.
Flujo: 1 tarea -> validar -> 1 commit en main -> git pull -> prueba local -> siguiente.
En pruebas locales: una sola acción/comando por mensaje.

Estado actual:
- FastAPI + SQLAlchemy 2 + SQLite + Alembic
- login/sesión/CSRF funcional
- primer admin + Gestión de Usuarios funcional
- shell compartido
- assets Geist/Tabler/HTMX locales obligatorios
- navegación parcial HTMX
- Select NERISOFT
- tests básicos + GitHub Actions
- Roles y Permisos 9.1 y 9.2 completados
- asignación de roles a usuarios y permisos granulares 9.3 completados
- 9.3.5 normalizó Roles y Permisos: catálogo actual = Sistema, listado/formulario separados y UI sin códigos técnicos
- Configuración tiene portada propia en /configuracion
- Usuarios y Roles y permisos son pantallas hermanas, no pestañas entre sí
- Mi cuenta se abre desde el usuario de la barra superior
- siguiente tarea: 9.4 Validación integral de permisos existentes

Terminología UI de acceso:
Usuario = cuenta que entra al sistema.
Rol = conjunto de permisos asignable a usuarios.
Permiso = acción habilitada por un rol.
Administrador del sistema = acceso total sin depender de roles.
Administrador del sistema se representa como tipo de acceso, nunca como rol.
No mezclar estos términos con “perfil”, “alcance” o “autorización” en textos de interfaz.

Catálogo actual:
Sistema -> Usuarios / Roles y permisos.
No inventar permisos de módulos futuros.
Cada módulo nuevo define, aplica y prueba sus permisos junto con la funcionalidad.

Regla de tablas:
Tabla = resumen operativo; ficha = detalle completo.
Mostrar solo metadatos que ayuden a identificar, comparar o actuar.

Antes de modificar, revisar main y docs relacionados. Mantener convenciones visuales, de seguridad y de datos.
No tapar síntomas con CSS/JS: corregir la causa en la capa responsable y eliminar workarounds previos.
```
