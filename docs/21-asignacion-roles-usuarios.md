# 21 — Asignación de Roles a Usuarios

## Alcance de la Tarea 9.3

La Tarea 9.3 integra el esquema de Roles y Permisos con Gestión de Usuarios. No agrega tablas ni migraciones: utiliza la relación `user_roles` creada en la Tarea 9.1.

## Operaciones incorporadas

Desde Configuración → Usuarios ahora se puede:

- ver los roles asignados a cada cuenta;
- asignar uno o más roles al crear un usuario;
- agregar o quitar roles al editar un usuario;
- conservar asignaciones fuera del alcance del gestor sin exponerlas ni eliminarlas;
- distinguir roles activos e inactivos;
- administrar identidad, estado y roles con permisos granulares independientes.

## Permisos aplicados

```text
system.users.view
system.users.create
system.users.edit
system.users.status
system.users.assign_roles
```

`superuser` conserva bypass administrativo total.

La Gestión de Usuarios deja de depender de `superuser_or_redirect(...)` y utiliza permisos efectivos para cada operación.

## Reglas de seguridad

Para un usuario delegado:

- nunca puede crear ni promover un `superuser`;
- nunca puede modificar un `superuser`;
- solo puede modificar cuentas cuyo conjunto efectivo de permisos sea subconjunto del propio;
- solo puede asignar roles cuyos permisos completos estén dentro de su alcance;
- no puede modificar sus propios roles;
- no puede cambiar su propio estado;
- asignaciones de roles fuera de su alcance se preservan intactas;
- valores de rol manipulados manualmente son rechazados;
- todas las escrituras mantienen validación CSRF.

Estas reglas se ejecutan en backend y no dependen de controles visuales.

## Roles inactivos

Un rol inactivo puede permanecer asignado a una cuenta, pero no aporta permisos efectivos. La interfaz lo identifica visualmente y no elimina la asignación por desactivación.

## Alcance de usuarios

Se incorpora `user_is_within_user_scope(...)`.

Para gestores delegados, un usuario objetivo es administrable solamente cuando:

```text
permisos_efectivos(usuario_objetivo) ⊆ permisos_efectivos(usuario_actual)
```

Los `superuser` siempre quedan fuera del alcance de otro usuario delegado.

## Siguiente tarea

```text
Tarea 9.4 — Validación integral de permisos
```

La siguiente subetapa verificará navegación, rutas, combinaciones de permisos y regresiones antes de cerrar el bloque de Roles y Permisos.
