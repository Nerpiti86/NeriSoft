# Assets de interfaz locales

NERISOFT sirve Geist, Tabler Icons y HTMX exclusivamente desde `app/static/vendor/` durante la ejecución normal.

Los binarios y archivos de terceros se generan localmente con:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\vendor-assets.ps1
```

El script fija versiones concretas y descarga:

- Geist `v1.7.2`;
- Tabler Icons Webfont `3.35.0`;
- HTMX `2.0.7`.

Los archivos generados se excluyen de Git para no inflar el repositorio con binarios reproducibles. Este README y `geist.css` sí se versionan.

NERISOFT no usa fallback remoto durante la ejecución. Si falta un asset crítico, el arranque falla con un mensaje que indica ejecutar `scripts/vendor-assets.ps1`.

El instalador valida tamaños mínimos, informa el SHA-256 de cada descarga nueva y elimina la referencia al source map de Tabler para evitar solicitudes `404` innecesarias.

Las licencias de terceros se descargan junto con cada paquete.
