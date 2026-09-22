# 11 — Login funcional y sesión

## Objetivo

NERISOFT valida credenciales reales contra `users`, mantiene una sesión autenticada y protege el dashboard principal.

Esta etapa convierte la pantalla visual documentada en `08-login.md` en un acceso funcional. Los documentos anteriores se conservan como registro de las etapas de implementación.

## Credenciales admitidas

El formulario `/login` permite ingresar con:

- nombre de usuario
- correo electrónico

Ambos se normalizan a minúsculas antes de buscar el usuario.

La contraseña se verifica contra `users.password_hash` mediante `verify_password()` y Argon2. La contraseña en texto plano nunca se persiste.

## Respuesta ante credenciales inválidas

El sistema utiliza el mensaje genérico:

```text
Usuario o contraseña incorrectos.
```

No se informa si falló el usuario, el correo, la contraseña o si la cuenta está inactiva. Esto evita exponer qué cuentas existen.

Los usuarios con `is_active = false` no pueden iniciar sesión.

## Sesión

La sesión se implementa con `SessionMiddleware` de Starlette.

La cookie de sesión:

- se llama `nerisoft_session`
- está firmada
- es `HttpOnly`
- usa `SameSite=Lax`
- tiene una duración máxima de 8 horas
- no almacena contraseñas
- guarda únicamente datos mínimos de sesión, como el `user_id` y el token CSRF

La cookie firmada protege la integridad de su contenido, pero no se considera un mecanismo de cifrado. Por ese motivo no se guardan secretos dentro de la sesión.

## Clave de firma

NERISOFT usa `NERISOFT_SESSION_SECRET` cuando la variable de entorno está configurada.

Si no existe, la aplicación genera una clave aleatoria local y la persiste en:

```text
data/session.secret
```

Ese archivo está excluido de Git y no debe copiarse al repositorio.

Para una instalación futura bajo HTTPS se puede activar:

```text
NERISOFT_SESSION_HTTPS_ONLY=true
```

En desarrollo local por HTTP permanece desactivado.

## Protección CSRF

Los formularios de login y cierre de sesión usan un token CSRF asociado a la sesión.

El servidor compara el token recibido con el token de la sesión antes de procesar la operación.

## Dashboard protegido

La ruta:

```text
/
```

requiere una sesión válida.

Comportamiento:

- si todavía no existen usuarios, redirige a `/setup`
- si existen usuarios pero no hay sesión válida, redirige a `/login`
- si la sesión pertenece a un usuario inexistente o inactivo, la sesión se descarta y se solicita un nuevo login
- si la sesión es válida, se muestra el dashboard

El nombre e iniciales visibles en el encabezado se toman del usuario autenticado.

## Login

`GET /login`:

- redirige a `/setup` si la instalación todavía no tiene usuarios
- redirige a `/` si ya existe una sesión autenticada
- en otro caso muestra el formulario de acceso

`POST /login`:

- valida CSRF
- busca por usuario o correo
- verifica `is_active`
- verifica el hash de contraseña
- crea la sesión
- redirige al dashboard

## Cierre de sesión

`POST /logout`:

- valida CSRF
- elimina el contenido de la sesión
- redirige a `/login`

El dashboard agrega un control de salida con el icono Tabler `ti-logout`.

## Dependencia

Se agrega:

```text
itsdangerous
```

requerida por el middleware de sesiones firmadas de Starlette.

## Fuera de alcance

Esta etapa todavía no incluye:

- roles y permisos
- recuperación de contraseña
- cambio de contraseña
- bloqueo por intentos fallidos
- rate limiting
- autenticación de dos factores
- administración normal de usuarios

Esas funciones se implementarán en tareas separadas.
