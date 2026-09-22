# 16 — Assets de interfaz locales

Actualizado: 22/09/2026

## Objetivo

NERISOFT no depende de Internet para renderizar tipografía, iconos ni HTMX durante la operación normal.

Los recursos se descargan una vez al servidor y luego FastAPI los sirve desde `/static/vendor/`.

## Versiones fijadas

- Geist `v1.7.2`;
- Tabler Icons Webfont `3.35.0`;
- HTMX `2.0.7`.

## Instalación

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\vendor-assets.ps1
```

El script:

1. crea los directorios necesarios;
2. descarga las versiones fijadas;
3. valida tamaños mínimos;
4. informa SHA-256 de descargas nuevas;
5. descarga licencias;
6. elimina del CSS de Tabler la referencia al source map que generaba un `404` de diagnóstico.

Para forzar descarga:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\vendor-assets.ps1 -Force
```

## Archivos críticos

```text
app/static/vendor/geist/Geist-Variable.woff2
app/static/vendor/tabler/tabler-icons.min.css
app/static/vendor/tabler/fonts/tabler-icons.woff2
app/static/vendor/htmx/htmx.min.js
```

## Sin fallback remoto

`base.html` referencia exclusivamente recursos locales.

`app/core/assets.py` valida los cuatro archivos críticos durante el lifespan de FastAPI. Si falta alguno, el arranque se detiene con un error que indica ejecutar el instalador.

Esto evita una situación peligrosa para diagnóstico:

```text
asset local faltante
↓
fallback CDN silencioso
↓
interfaz aparentemente funcional pero dependiente de Internet
```

Ahora la condición es explícita:

```text
asset local presente -> NERISOFT arranca
asset local faltante -> NERISOFT no arranca
```

## Git

Los binarios reproducibles y licencias descargadas siguen excluidos de Git. El repositorio versiona:

- script de instalación;
- versiones fijadas;
- CSS local de Geist;
- validación de arranque;
- documentación.

## Diagnóstico

```text
GET /.well-known/appspecific/com.chrome.devtools.json 404
```

proviene de Chrome/DevTools y no representa un error de NERISOFT.

```text
304 Not Modified
```

indica uso normal de caché del navegador.

Después de volver a ejecutar el instalador actualizado, Tabler deja de solicitar `tabler-icons.min.css.map`.
