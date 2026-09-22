# 20 — Gestión de Roles y Permisos

## Alcance de la Tarea 9.2

La Tarea 9.2 incorpora la interfaz administrativa para trabajar sobre el modelo creado en 9.1. No agrega tablas ni migraciones nuevas.

Rutas:

```text
GET  /configuracion/roles
GET  /configuracion/roles/nuevo
POST /configuracion/roles/nuevo
GET  /configuracion/roles/{id}/editar
POST /configuracion/roles/{id}/editar
POST /configuracion/roles/{id}/estado
```

## Operaciones disponibles

- listar roles;
- crear roles;
- editar nombre y descripción;
- seleccionar permisos del catálogo vigente;
- activar o desactivar roles;
- consultar cantidad de permisos y usuarios asignados.

Los roles pueden guardarse sin permisos. En ese estado no conceden ninguna acción.

## Seguridad

Cada operación se valida en backend mediante permisos específicos:

```text
system.roles.view
system.roles.create
system.roles.edit
system.roles.status
```

`superuser` mantiene bypass administrativo total.

Para usuarios delegados:

- solo pueden otorgar permisos incluidos en su propio alcance efectivo;
- no pueden editar ni cambiar el estado de un rol que contenga permisos fuera de su alcance;
- no pueden modificar ni desactivar un rol asignado a su propia cuenta;
- permisos desconocidos enviados manualmente son rechazados;
- todas las escrituras mantienen validación CSRF.

Estas reglas no dependen de que un botón esté visible o deshabilitado en HTML.

## Identidad del rol

El nombre visible se normaliza antes de persistirlo:

```text
"  Supervisor   de Ventas  " -> "Supervisor de Ventas"
```

`name_key` usa la versión `casefold()` para impedir duplicados por mayúsculas/minúsculas o espacios redundantes.

## Navegación

Configuración expone dos secciones:

```text
Usuarios
Roles y permisos
```

Los enlaces entre ambas pantallas participan de la navegación parcial HTMX y mantienen sidebar y topbar montados.

## Estado de roles inactivos

Desactivar un rol no borra:

- el rol;
- sus permisos;
- sus futuras o actuales asignaciones a usuarios.

Un rol inactivo simplemente deja de aportar permisos efectivos hasta que vuelva a activarse.

## Continuidad

La Tarea 9.3, documentada en [`21-asignacion-roles-usuarios.md`](21-asignacion-roles-usuarios.md), conecta estos roles con Gestión de Usuarios. El siguiente bloque es la Tarea 9.4 — validación integral de permisos.
