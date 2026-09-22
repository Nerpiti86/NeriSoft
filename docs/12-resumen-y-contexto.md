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
- CSRF en login, logout y escrituras de Usuarios;
- helpers de auth/CSRF centralizados;
- `/setup` bloqueado cuando ya existen usuarios;
- en una instalación vacía `/setup` solo acepta loopback por defecto;
- `NERISOFT_SETUP_ALLOW_REMOTE=true` permite habilitar temporalmente setup remoto;
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
- Inicio y Usuarios usan el mismo shell;
- navegación Inicio ↔ Usuarios y GET internos de Usuarios usan HTMX y reemplazan solo `.workspace`;
- fallback HTML normal si HTMX no está disponible;
- Select NERISOFT reutilizable, con listeners globales únicos y limpieza de instancias al retirar nodos.

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

## Base de datos

```text
D:\NeriSoft\data\nerisoft.db
```

Migraciones:

```text
0001_users
0002_user_superuser
```

## Tests

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

GitHub Actions ejecuta compilación, pytest y `node --check` para los JS principales en cada push a `main`.

## Próximo bloque

La siguiente tarea funcional prevista es:

```text
Roles y Permisos
```

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
- navegación parcial HTMX entre Inicio y Usuarios
- Select NERISOFT
- tests básicos + GitHub Actions
- roles/permisos todavía no implementados

Antes de modificar, revisar main y docs relacionados. Mantener convenciones visuales y de datos.
```
