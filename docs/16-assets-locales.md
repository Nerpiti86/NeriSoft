# 16 — Assets de interfaz locales

Actualizado: 22/09/2026

## Objetivo

NERISOFT deja de depender de la velocidad de Internet para renderizar tipografía, iconos y HTMX durante el uso normal.

Los recursos se descargan una sola vez al servidor y luego FastAPI los sirve desde `/static/vendor/` junto con el resto de la aplicación.

## Versiones fijadas

- Geist `v1.7.2`;
- Tabler Icons Webfont `3.35.0`;
- HTMX `2.0.7`.

Estas versiones preservan el aspecto y comportamiento existentes sin introducir actualizaciones implícitas.

## Instalación

Desde la raíz del repositorio:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\vendor-assets.ps1
```

El script:

1. crea los directorios necesarios;
2. descarga los assets fijados;
3. valida tamaños mínimos para detectar descargas vacías o incompletas;
4. descarga las licencias de terceros;
5. conserva archivos existentes válidos salvo que se use `-Force`.

Para volver a descargarlos:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\vendor-assets.ps1 -Force
```

## Archivos locales críticos

```text
app/static/vendor/geist/Geist-Variable.woff2
app/static/vendor/tabler/tabler-icons.min.css
app/static/vendor/tabler/fonts/tabler-icons.woff2
app/static/vendor/htmx/htmx.min.js
```

El CSS local de Geist está versionado en:

```text
app/static/vendor/geist/geist.css
```

## Estrategia de carga

`base.html` ahora intenta primero los recursos locales.

Geist y Tabler Icons se pre-cargan como fuentes críticas para reducir cambios de métrica y aparición tardía de iconos.

Mientras el servidor todavía no tenga los archivos generados, se conserva un fallback remoto para no dejar la interfaz inutilizable. Después de ejecutar el script, el navegador debe resolver esos recursos desde `127.0.0.1` o desde el servidor LAN.

## Git

Los binarios y archivos de terceros reproducibles se excluyen de Git. El repositorio versiona:

- el script de instalación;
- las versiones fijadas;
- el CSS propio de Geist;
- la configuración de carga;
- la documentación.

Así se evita inflar el historial con binarios y se mantiene un procedimiento reproducible para cualquier servidor nuevo.

## Relación con los artefactos visuales

La carga anterior dependía directamente de:

- Google Fonts;
- jsDelivr;
- unpkg.

Una respuesta lenta de cualquiera de esos servicios podía provocar:

- cambio de fuente después del primer render;
- cambios en ancho/alto del texto;
- iconos que aparecían tarde;
- reflow del layout;
- artefactos amplificados por transiciones de página completa.

Con los assets locales, la interfaz deja de depender de esas latencias durante la operación normal.

## Diagnóstico de Uvicorn

Una línea como:

```text
GET /.well-known/appspecific/com.chrome.devtools.json 404 Not Found
```

proviene de Chrome/DevTools y no representa un error funcional de NERISOFT.

Una respuesta:

```text
304 Not Modified
```

indica uso normal de caché del navegador.
