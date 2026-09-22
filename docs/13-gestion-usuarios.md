# 13 — Gestión de usuarios

Actualizado: 22/09/2026

## Objetivo

NERISOFT incorpora la primera pantalla administrativa real de **Configuración → Usuarios** sobre la tabla `users` existente.

Esta tarea no agrega nuevas columnas ni migraciones: reutiliza el modelo creado en las etapas anteriores.

## Acceso

Ruta principal:

```text
/configuracion/usuarios
```

Requisitos:

- sesión autenticada válida;
- usuario activo;
- `is_superuser = true`.

Si no existe sesión válida, se redirige a `/login`.

Si la sesión corresponde a un usuario que no es superusuario, se redirige al dashboard `/`.

Hasta que se implementen roles y permisos granulares, `is_superuser` funciona como permiso administrativo para esta pantalla.

## Listado

La pantalla muestra usuarios reales almacenados en SQLite con:

- nombre;
- nombre de usuario;
- correo electrónico;
- tipo de cuenta;
- estado activo/inactivo;
- fecha y hora de creación;
- acciones disponibles.

La fecha visible usa la convención:

```text
dd/mm/yyyy HH:mm
```

La interfaz mantiene números tabulares para fechas y datos comparables.

## Búsqueda y filtro

El listado permite buscar por:

- nombre;
- usuario;
- correo electrónico.

También permite filtrar por:

- todos los estados;
- activos;
- inactivos.

La pantalla muestra contadores de:

- usuarios totales;
- usuarios activos;
- administradores.

## Alta de usuarios

Ruta:

```text
/configuracion/usuarios/nuevo
```

Datos requeridos:

- nombre;
- usuario;
- correo electrónico;
- contraseña;
- repetición de contraseña.

Opcionalmente el administrador puede marcar la nueva cuenta como **Administrador del sistema**.

Reglas:

- nombre entre 2 y 120 caracteres;
- usuario entre 3 y 64 caracteres;
- usuario formado por letras minúsculas, números, punto, guion o guion bajo;
- correo válido de hasta 254 caracteres;
- contraseña entre 10 y 128 caracteres;
- las dos contraseñas deben coincidir;
- usuario único;
- correo único.

Las contraseñas continúan almacenándose únicamente mediante hash Argon2. Nunca se guarda la contraseña en texto plano.

Las cuentas nuevas se crean activas por defecto.

## Edición

Ruta:

```text
/configuracion/usuarios/{id}/editar
```

Permite modificar:

- nombre;
- usuario;
- correo electrónico;
- condición de superusuario, salvo para el usuario que está operando su propia sesión.

La contraseña no se modifica desde esta tarea. El cambio de contraseña queda reservado para una etapa independiente.

## Activación y desactivación

Ruta de escritura:

```text
POST /configuracion/usuarios/{id}/estado
```

Permite alternar entre usuario activo e inactivo.

Reglas:

- un usuario inactivo no puede iniciar sesión;
- un administrador no puede desactivar su propia cuenta desde la sesión que está usando;
- si una cuenta que tenía una sesión abierta es desactivada por otro administrador, esa sesión deja de ser válida en la siguiente solicitud autenticada.

## Protección CSRF

Las operaciones de escritura del módulo requieren el token CSRF asociado a la sesión:

- alta;
- edición;
- activación/desactivación.

Una solicitud con token inválido no modifica la base de datos.

## Navegación

El acceso **Configuración** del sidebar dirige a:

```text
/configuracion/usuarios
```

En el dashboard existente, el enlace se normaliza al cargar el shell mediante el JavaScript común. La nueva pantalla incluye el destino directamente en su HTML.

## Diseño

La pantalla sigue el patrón documentado para maestros y listados:

```text
Título
Acción primaria
Buscar
Filtros
Tabla
```

Se mantiene:

- shell de viewport completo;
- sidebar grafito;
- topbar oscura;
- acento dorado;
- Geist;
- Tabler Icons;
- radios contenidos;
- densidad desktop-first;
- estados semánticos para activo/inactivo.

## Decisiones de seguridad

En esta etapa se aplican dos protecciones para evitar perder el acceso administrativo por accidente:

1. el administrador autenticado no puede desactivar su propia cuenta;
2. el administrador autenticado no puede quitarse a sí mismo `is_superuser` desde esta pantalla.

Otro superusuario sí puede administrar esas propiedades de las demás cuentas.

## Fuera de alcance

Esta tarea todavía no implementa:

- roles;
- permisos granulares;
- cambio de contraseña;
- recuperación de contraseña;
- bloqueo por intentos fallidos;
- rate limiting;
- auditoría general;
- paginación del listado;
- multiempresa.

Esas funciones permanecen para tareas posteriores.
