# 17 — Navegación parcial NERISOFT

Actualizado: 22/09/2026

## Objetivo

Reducir la sensación de recarga completa al navegar por el ERP sin convertir la aplicación en una SPA ni duplicar endpoints.

La primera etapa aplica navegación parcial a:

- Inicio;
- Configuración → Usuarios;
- alta/edición/cancelación de usuarios mediante enlaces GET;
- búsqueda y filtro GET de usuarios.

Las operaciones POST continúan usando navegación normal en esta etapa.

## Estrategia

NERISOFT mantiene las rutas FastAPI existentes y las respuestas HTML completas.

Cuando HTMX está disponible, `app/static/js/app.js` usa `htmx.ajax()` para:

1. solicitar la misma URL que usaría una navegación normal;
2. seleccionar únicamente `.workspace` de la respuesta;
3. reemplazar únicamente el `.workspace` actual;
4. conservar sidebar y topbar montados;
5. actualizar la URL del navegador y el historial.

Parámetros principales:

```text
target: .workspace
select: .workspace
swap: outerHTML swap:60ms settle:100ms
push: URL solicitada
```

No se agregan endpoints parciales paralelos.

## Fallback

Los enlaces conservan `href` reales y los formularios GET conservan `action` y `method`.

Si HTMX no está disponible, JavaScript falla o el navegador no puede ejecutar la mejora progresiva, la navegación continúa funcionando como una carga HTML tradicional.

## Recursos visuales

Dashboard y Usuarios usan hojas de estilo distintas. Como el `head` no se reemplaza durante la navegación parcial, al iniciar una sesión autenticada se precargan localmente:

```text
/static/css/dashboard.css
/static/css/users.css
/static/js/setup.js
```

Esto evita que el workspace nuevo aparezca un instante sin sus estilos o sin comportamiento de controles.

## Inicialización después de un swap

Después de cada reemplazo del workspace se vuelven a aplicar únicamente las mejoras que dependen del contenido dinámico:

- abreviaturas visibles de comprobantes;
- clases de fechas y códigos;
- saludo del usuario;
- estado activo de Inicio/Configuración;
- título del documento;
- controles de visibilidad de contraseña.

El Select NERISOFT ya posee un `MutationObserver`, por lo que los selects nuevos se mejoran automáticamente.

Antes de retirar un workspace se eliminan los menús flotantes del Select NERISOFT para no dejar nodos huérfanos en `document.body`.

## Redirecciones

Si una petición HTMX termina en otra ruta por una redirección del servidor —por ejemplo sesión vencida o usuario inexistente— NERISOFT cancela el swap parcial y realiza una navegación normal a la URL final.

La autorización sigue siendo responsabilidad exclusiva del backend.

## Movimiento

La transición ya no fotografía ni anima el documento completo.

Solo el workspace usa:

- salida de 60 ms;
- entrada/asentamiento de 100 ms;
- opacidad mínima;
- desplazamiento vertical de 1–2 px.

`prefers-reduced-motion` continúa anulando prácticamente todo movimiento.

## Alcance deliberadamente fuera de esta etapa

Todavía no se convierten a navegación parcial:

- creación/edición POST de usuarios;
- activar/desactivar usuarios;
- login;
- logout;
- setup inicial;
- módulos aún no implementados.

Las mutaciones se migrarán en una tarea separada cuando se defina de forma uniforme cómo manejar validaciones, redirects, notices y CSRF con HTMX.

## Criterio de aceptación

En la secuencia:

```text
Inicio
→ Configuración → Usuarios
→ Nuevo usuario
→ Cancelar
→ Editar usuario
→ Cancelar
→ Inicio
```

sidebar y topbar deben permanecer visualmente estables y las operaciones GET deben reemplazar solo el workspace.
