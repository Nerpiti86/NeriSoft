# 10 — Configuración inicial del administrador

## Objetivo

NERISOFT debe permitir crear el primer usuario administrador desde la propia aplicación, sin editar SQLite ni ejecutar scripts manuales para insertar credenciales.

## Comportamiento

La ruta de configuración inicial es:

```text
/setup
```

Reglas:

- La pantalla sólo está disponible mientras la tabla `users` no tenga registros.
- Si no existen usuarios y se intenta abrir `/login`, NERISOFT redirige a `/setup`.
- Una vez creado el primer usuario, `/setup` deja de estar disponible y redirige a `/login`.
- Esta tarea no activa todavía la autenticación del login ni protege el dashboard.

## Datos solicitados

La configuración inicial solicita:

- nombre completo
- usuario
- correo electrónico
- contraseña
- confirmación de contraseña

El usuario y el correo se normalizan a minúsculas antes de persistirlos.

## Visibilidad de contraseña

Los campos `Contraseña` y `Repetir contraseña` incluyen una acción visual para alternar entre contraseña oculta y visible.

- El control usa Tabler Icons (`ti-eye` / `ti-eye-off`).
- El cambio afecta únicamente la visualización en el navegador; no modifica el valor enviado al servidor.
- El estado se expone mediante `aria-pressed` y el texto accesible cambia entre `Mostrar contraseña` y `Ocultar contraseña`.

## Validaciones

- Nombre: entre 2 y 120 caracteres.
- Usuario: entre 3 y 64 caracteres; sólo letras minúsculas, números, punto, guion y guion bajo.
- Correo: formato básico válido y máximo 254 caracteres.
- Contraseña: entre 10 y 128 caracteres.
- Confirmación: debe coincidir exactamente con la contraseña.

Las contraseñas nunca se persisten en texto plano. Se almacenan mediante el hashing Argon2 ya definido en `app/core/security.py`.

## Administrador inicial

Se incorpora el campo booleano:

```text
users.is_superuser
```

El primer usuario creado desde `/setup` queda con:

```text
is_active = true
is_superuser = true
```

`is_superuser` representa acceso administrativo total y se mantiene separado del sistema de roles y permisos que se implementará después.

## Protección del setup

El formulario incluye un token aleatorio generado por el proceso de NERISOFT. El servidor valida ese token antes de crear el usuario inicial para impedir envíos externos no autorizados contra una instalación todavía vacía.

Además, el servidor vuelve a comprobar que no existan usuarios antes de aceptar el alta. Si ya existe alguno, redirige a `/login`.

## Migración

La migración:

```text
0002_user_superuser
```

agrega `is_superuser` a `users` con valor predeterminado `false`.

## Dependencia de formularios

Se incorpora `python-multipart`, requerida por FastAPI para recibir formularios HTML mediante `Form`.

## Fuera de alcance

Esta etapa no incluye:

- validación real de credenciales en `/login`
- sesiones
- cierre de sesión
- recuperación de contraseña
- roles y permisos
- pantalla normal de administración de usuarios
- protección de rutas privadas

Esas funciones se implementan en tareas separadas.
