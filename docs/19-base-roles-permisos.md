# 19 — Base de Roles y Permisos

## Alcance de la Tarea 9.1

Esta etapa incorpora únicamente la base técnica de autorización granular. No agrega todavía pantallas para administrar roles ni modifica la experiencia actual de Gestión de Usuarios.

## Modelo

Se incorporan cuatro estructuras:

```text
roles
permissions
user_roles
role_permissions
```

Un usuario puede tener varios roles y un rol puede contener varios permisos.

`users.is_superuser` se conserva como bypass administrativo total. Esto mantiene operativo al administrador inicial y ofrece una vía de recuperación ante una configuración incorrecta de roles.

## Catálogo inicial

La migración `0003_roles_permissions` crea y carga los permisos iniciales de Sistema:

### Usuarios

- `system.users.view`
- `system.users.create`
- `system.users.edit`
- `system.users.status`
- `system.users.assign_roles`

### Roles

- `system.roles.view`
- `system.roles.create`
- `system.roles.edit`
- `system.roles.status`

El catálogo se define también en `app/core/permissions.py`. Los códigos son contratos internos estables y no deben depender del texto visible de la interfaz.

## Reglas de autorización

- un `superuser` posee todos los permisos del catálogo;
- un usuario normal obtiene la unión de permisos de sus roles activos;
- un rol inactivo conserva sus asignaciones, pero deja de otorgar permisos;
- el backend es siempre la fuente de verdad de la autorización;
- la futura administración delegada solo podrá asignar roles cuyo conjunto de permisos sea subconjunto de los permisos del operador actual.

## Helpers

`app/core/permissions.py` centraliza:

- cálculo de permisos efectivos;
- verificación individual de permisos;
- consulta de permisos de un rol;
- validación de alcance para delegación.

`app/core/auth.py` incorpora `permission_or_redirect(...)` para rutas que en las siguientes subetapas dejarán de depender de `superuser_or_redirect(...)`.

## Migración

```powershell
python -m alembic upgrade head
```

La migración es aditiva: no modifica ni elimina usuarios existentes.

## Validación

Se agregan tests que verifican:

- permisos otorgados por roles activos;
- ausencia de permisos desde roles inactivos;
- bypass total de `superuser`;
- prevención de delegación por encima del propio alcance.

GitHub Actions también ejecuta ahora `alembic upgrade head` sobre una base SQLite temporal para detectar migraciones rotas.

## Próximas partes

```text
9.1 Base de roles y permisos        ← esta etapa
9.2 Gestión de Roles y Permisos     ← próxima
9.3 Asignación de roles a usuarios
9.4 Validación integral y cierre
```
