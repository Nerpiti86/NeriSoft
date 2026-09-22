# 00 — Lectura rápida de NERISOFT

> Entrada de 2 minutos para retomar el proyecto. Para contexto completo, ver [`12-resumen-y-contexto.md`](12-resumen-y-contexto.md).

Actualizado: 22/09/2026

## Qué es

NERISOFT es un ERP administrativo, comercial y contable, desktop-first, pensado para uso multiusuario en red local.

Repositorio: `Nerpiti86/NeriSoft`  
Rama estable: `main`  
Instalación local habitual: `D:\NeriSoft`

## Estado actual

Ya están implementados y funcionando:

- shell principal y dashboard base;
- login, sesión, CSRF y logout;
- primer administrador del sistema;
- gestión de usuarios;
- roles y permisos;
- asignación de uno o más roles a usuarios;
- permisos granulares y controles contra escalada;
- Configuración con portada propia;
- Usuarios y Roles y permisos como destinos independientes;
- Mi cuenta separado de la administración de usuarios;
- navegación parcial HTMX;
- assets críticos locales;
- tests y GitHub Actions.

Próxima tarea funcional:

```text
Tarea 9.4 — Validación integral de permisos
```

Después: Auditoría → Configuración de empresa → Clientes → resto de maestros y circuitos.

## Modelo mental de acceso

```text
Usuario = cuenta/persona que ingresa al sistema
Rol = conjunto reutilizable de permisos
Permiso = acción concreta habilitada por un rol
Administrador del sistema = acceso total; no es un rol y no depende de roles
```

Flujo normal:

```text
Crear rol → elegir permisos → crear usuario → asignar rol(es) → obtener acceso
```

Nunca mostrar `Administrador del sistema` dentro de una columna o concepto llamado `Roles`.

## Navegación de Configuración

```text
Configuración
└── Accesos y seguridad
    ├── Usuarios
    └── Roles y permisos
```

`Mi cuenta` es información de la sesión actual y se accede desde el usuario de la barra superior. No forma parte de Gestión de Usuarios.

## Reglas de trabajo

```text
1 tarea → validación → 1 commit coherente en main → pull local → prueba → siguiente tarea
```

Durante validación local: una sola acción o comando por paso.

No tapar síntomas con CSS/JavaScript ni sumar workarounds innecesarios. Corregir la causa en la capa responsable y retirar cualquier solución temporal previa.

## Reglas UI que no se negocian

- Interfaz sobria, densa y orientada a productividad.
- No agregar niveles de navegación sin necesidad.
- No sobrecargar pantallas con información secundaria.
- Las tablas deben servir para identificar, comparar y actuar rápidamente.
- Mostrar en tablas solo columnas y metadatos necesarios para esa decisión.
- Evitar repetir tipo, estado, roles, permisos, badges o descripciones si no aportan una acción o comparación real.
- El detalle secundario pertenece a la ficha/vista del registro, no a la grilla.
- Mantener patrones reutilizables entre módulos.
- Desktop-first; no diseñar como una interfaz móvil ampliada.

## Stack

```text
Python / FastAPI / SQLAlchemy 2 / SQLite / Alembic
Jinja2 / HTMX / Vanilla JS / CSS propio
Geist / Tabler Icons / Uvicorn / Argon2 / pytest
```

SQLite vive solo en el servidor. Los clientes acceden por HTTP/HTTPS; nunca abren directamente el archivo `.db`.

## Comandos habituales

Desde `D:\NeriSoft`.

Actualizar código:

```powershell
git pull origin main
```

Levantar la aplicación sin depender de la activación de PowerShell:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Aplicar migraciones:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

Tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Base local habitual:

```text
D:\NeriSoft\data\nerisoft.db
```

## Dónde leer más

- Arquitectura: [`01-arquitectura.md`](01-arquitectura.md)
- Diseño UI: [`02-diseno-ui.md`](02-diseno-ui.md)
- Datos y reglas: [`03-datos-y-reglas.md`](03-datos-y-reglas.md)
- Roadmap: [`04-roadmap.md`](04-roadmap.md)
- Flujo de trabajo: [`05-flujo-trabajo.md`](05-flujo-trabajo.md)
- Contexto consolidado: [`12-resumen-y-contexto.md`](12-resumen-y-contexto.md)

Regla práctica: empezar siempre por este archivo. Abrir documentación específica solo cuando la tarea lo requiera.
