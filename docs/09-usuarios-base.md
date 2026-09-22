# 09 — Usuarios base

## Alcance

Esta etapa incorpora la base técnica de usuarios de NERISOFT. No activa todavía el login real, sesiones, roles, permisos ni la administración visual de usuarios.

## Modelo `users`

La tabla `users` contiene:

- `id`: clave primaria entera.
- `name`: nombre visible del usuario.
- `username`: identificador de acceso único.
- `email`: correo único.
- `password_hash`: hash de contraseña; nunca contraseña en texto plano.
- `is_active`: permite habilitar o deshabilitar el acceso sin borrar el usuario.
- `created_at`: fecha y hora de creación.
- `updated_at`: fecha y hora de última actualización.

`username` y `email` son únicos a nivel de base de datos.

## Contraseñas

NERISOFT no persiste contraseñas en texto plano.

El módulo `app/core/security.py` centraliza:

- `hash_password(password)`
- `verify_password(password, password_hash)`

Se utiliza `pwdlib` con backend Argon2 mediante `PasswordHash.recommended()`.

La aplicación debe almacenar únicamente el resultado de `hash_password()` en `users.password_hash`.

## Migración

La primera migración funcional es:

```text
alembic/versions/0001_users.py
```

Crea la tabla `users` y sus restricciones de unicidad.

Alembic importa `app.models` en `alembic/env.py` para registrar los modelos dentro de `Base.metadata`.

## Fuera de alcance

Esta tarea no incluye:

- usuario administrador inicial
- formulario de alta o edición
- login funcional
- cookies o sesiones
- recuperación de contraseña
- roles
- permisos
- auditoría

Esas capacidades se incorporarán en tareas separadas.
