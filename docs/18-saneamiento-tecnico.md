# 18 — Saneamiento técnico previo a Roles y Permisos

Actualizado: 22/09/2026

## Objetivo

Cerrar deuda técnica detectada en la revisión general del repositorio antes de agregar Roles y Permisos.

No incorpora nuevas reglas de negocio.

## Cambios

### Auth y CSRF centralizados

Se incorpora `app/core/auth.py` para concentrar:

- token CSRF;
- validación CSRF;
- recuperación del usuario autenticado;
- requisito temporal de superusuario;
- nombre/iniciales visibles;
- validación del origen permitido para `/setup`.

`main.py` y `users.py` dejan de duplicar estas funciones.

### Validación de identidad centralizada

`app/core/user_validation.py` concentra:

- normalización de nombre/username/email;
- regex de username;
- validación de email;
- límites de longitud.

### Formateo horario

`app/core/formatting.py` incorpora `datetime_ar`.

Los `CURRENT_TIMESTAMP` de SQLite se interpretan como UTC y se convierten a `America/Argentina/Cordoba` antes de mostrarse.

### Templates compartidos

`app/core/templates.py` mantiene una sola instancia de `Jinja2Templates` y registra filtros/globales.

`authenticated.html` centraliza sidebar y topbar para las pantallas autenticadas.

### HTML como fuente de verdad

Se eliminan correcciones visuales posteriores en JS para:

- nombre/iniciales del usuario;
- enlaces Inicio/Configuración;
- abreviaturas FAC/NCA;
- logout.

El servidor entrega directamente el HTML correcto.

### Controles aún no implementados

Los controles visuales que todavía no tienen función real quedan deshabilitados o marcados como no disponibles, evitando que parezcan acciones funcionales.

La empresa del shell deja de mostrarse como `Demo S.A.` y aparece como `Sin configurar` hasta implementar Configuración de Empresa.

### Select NERISOFT

Se elimina la acumulación de listeners globales por instancia.

Ahora existe un solo listener global para eventos de documento/ventana y las instancias retiradas del DOM se destruyen mediante `MutationObserver`.

### Filtros HTMX

Se elimina `partial-filters.js`.

La lógica GET de filtros queda una sola vez en `app.js` y usa el workspace como `source` para no duplicar query params.

### Assets

Se eliminan los fallbacks remotos de Geist, Tabler y HTMX.

`app/core/assets.py` valida assets locales durante el arranque. El instalador informa SHA-256 y limpia la referencia al source map de Tabler.

### Setup inicial

Mientras no existan usuarios, `/setup` solo acepta conexiones loopback por defecto.

Para una instalación excepcional que necesite setup remoto:

```text
NERISOFT_SETUP_ALLOW_REMOTE=true
```

### Dependencias y tests

Las dependencias directas de runtime quedan fijadas a versiones concretas.

Se agrega:

- `requirements-dev.txt`;
- tests de hashing;
- tests de validación de usuarios;
- tests de zona horaria;
- tests de acceso al setup;
- parseo básico de templates;
- GitHub Actions con compilación Python, pytest y `node --check`.

## Resultado esperado

La siguiente tarea, Roles y Permisos, debe poder apoyarse en:

- una sola capa de autenticación;
- un solo shell;
- una sola estrategia HTMX;
- un solo formateador horario;
- tests básicos ejecutables automáticamente;
- documentación actualizada.
