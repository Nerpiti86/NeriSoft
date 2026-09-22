# 08 — Login

## Alcance

La primera etapa del login de NERISOFT es exclusivamente visual. Todavía no implementa autenticación, sesiones, recuperación de contraseña ni validación contra usuarios reales.

## Ruta

La pantalla de acceso queda disponible en:

```text
/login
```

El dashboard existente continúa disponible en `/` mientras la autenticación real no esté implementada.

## Dirección visual

La pantalla mantiene el sistema visual aprobado de NERISOFT:

- Geist como tipografía principal.
- Grafito + dorado como identidad.
- Fondo claro cálido para el área del formulario.
- Radios contenidos de `6/8/10px`.
- Sombras moderadas.
- Interfaz desktop-first y legible al `100%` de zoom.
- Sin introducir nuevas familias tipográficas.

## Estructura

La pantalla se divide en dos áreas:

1. Panel de identidad grafito con marca NERISOFT.
2. Área clara con formulario de acceso.

El formulario visual contiene:

- usuario o correo
- contraseña
- acción visual de recuperación de contraseña
- botón `Ingresar`
- estado general de error preparado
- estado de error por campo preparado

## Estados de error

Los estilos quedan definidos para una futura integración funcional:

- `.login-alert` para error general de autenticación
- `.form-field.is-error` para campo inválido
- `.field-error` para mensaje asociado al campo

En esta etapa estos estados no se activan mediante lógica de servidor.

## Regla de implementación futura

Cuando se implemente autenticación real:

- no se deben almacenar contraseñas en texto plano
- las credenciales deben validarse en servidor
- la sesión debe proteger rutas privadas
- `/` deberá requerir sesión válida o redirigir al login
- errores de acceso no deben revelar si un usuario existe o no

La implementación funcional de autenticación se realizará como una tarea separada.
