# Assets de interfaz locales

NERISOFT sirve Geist, Tabler Icons y HTMX desde `app/static/vendor/` para evitar dependencias visuales de CDNs durante el uso normal.

Los binarios y archivos de terceros se generan localmente con:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\vendor-assets.ps1
```

El script fija versiones concretas y descarga:

- Geist `v1.7.2`;
- Tabler Icons Webfont `3.35.0`;
- HTMX `2.0.7`.

Los archivos generados se excluyen de Git para no inflar el repositorio con binarios reproducibles. Este README y `geist.css` sí se versionan.

Mientras un asset local todavía no exista, `base.html` conserva un fallback remoto para no dejar la interfaz inutilizable. Después de ejecutar el script, el navegador debe resolver los recursos desde `/static/vendor/...`.

Las licencias de los terceros también se descargan junto con cada paquete.
