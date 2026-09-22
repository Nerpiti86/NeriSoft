# 17 — Navegación parcial NERISOFT

Actualizado: 22/09/2026

## Objetivo

Reducir la sensación de recarga completa al navegar por el ERP sin convertir la aplicación en una SPA ni duplicar endpoints.

La primera etapa aplica navegación parcial a:

- Inicio;
- Configuración → Usuarios;
- alta/edición/cancelación de usuarios mediante enlaces GET;
- búsqueda y filtros GET de usuarios.

Las operaciones POST continúan usando navegación normal en esta etapa.

## Shell compartido

Las pantallas autenticadas extienden:

```text
app/templates/authenticated.html
```

Ese template contiene una única implementación de:

- sidebar;
- topbar;
- usuario actual;
- logout;
- accesos de navegación.

Inicio y Usuarios aportan únicamente su bloque `.workspace`.

Esto evita divergencias entre pantallas y elimina la necesidad de corregir usuario, enlaces o logout después con JavaScript.

## Estrategia HTMX

Las rutas FastAPI existentes continúan devolviendo HTML completo.

Cuando HTMX está disponible, `app/static/js/app.js` usa `htmx.ajax()` para:

1. solicitar la misma URL que una navegación normal;
2. seleccionar `.workspace` de la respuesta;
3. reemplazar el workspace actual;
4. conservar sidebar y topbar montados;
5. actualizar URL e historial.

Parámetros:

```text
target: .workspace
select: .workspace
swap: outerHTML swap:60ms settle:100ms
push: URL solicitada
```

## Fallback

Los enlaces conservan `href` reales y los formularios GET conservan `action`/`method` reales.

Sin HTMX la navegación sigue funcionando como HTML tradicional.

La autorización continúa siendo responsabilidad exclusiva del backend.

## Assets de pantallas autenticadas

`authenticated.html` carga desde el inicio:

```text
/static/css/dashboard.css
/static/css/users.css
/static/js/setup.js
```

Así un workspace obtenido por HTMX nunca depende de modificar el `<head>` durante el swap.

## Filtros GET de Usuarios

La lógica vive únicamente en `app/static/js/app.js`.

El formulario `.users-filters` se serializa una sola vez con `FormData`. La petición HTMX usa el propio workspace como `source`, por lo que no vuelve a adjuntar los campos del formulario.

Forma correcta:

```text
/configuracion/usuarios?q=&estado=activos
```

No existe ya `partial-filters.js` ni una segunda implementación paralela.

## Select NERISOFT y swaps

`select.js` mantiene un único conjunto de listeners globales para:

- clic exterior;
- resize;
- scroll.

Las instancias individuales ya no registran listeners globales repetidos.

Un `MutationObserver` detecta selects retirados del DOM y destruye su instancia/menu flotante. Esto evita acumular listeners o nodos huérfanos durante navegaciones HTMX prolongadas.

## Redirecciones

Si una petición HTMX termina en otra ruta por redirección del servidor —por ejemplo sesión vencida— se cancela el swap parcial y se realiza navegación normal a la URL final.

## Movimiento

Solo el workspace usa una transición corta:

- salida 60 ms;
- asentamiento 100 ms;
- opacidad/desplazamiento mínimos.

`prefers-reduced-motion` continúa anulando prácticamente todo movimiento.

## Fuera de alcance

Todavía no se convierten a navegación parcial:

- creación/edición POST de usuarios;
- activar/desactivar usuarios;
- login;
- logout;
- setup inicial;
- módulos aún no implementados.

Las mutaciones se migrarán cuando exista una política uniforme para validaciones, redirects, notices y CSRF con HTMX.
