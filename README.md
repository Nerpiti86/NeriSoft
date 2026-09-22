# NERISOFT

ERP administrativo, comercial y contable para uso multiusuario en red local.

## Lectura rápida

Para retomar el proyecto sin recorrer toda la documentación, empezar por:

[`docs/00-lectura-rapida.md`](docs/00-lectura-rapida.md)

El contexto consolidado y detallado sigue en [`docs/12-resumen-y-contexto.md`](docs/12-resumen-y-contexto.md).

## Stack

- Python 3
- FastAPI
- SQLAlchemy 2
- SQLite
- Alembic
- Jinja2
- HTMX
- Vanilla JavaScript
- CSS propio
- Geist local
- Tabler Icons Webfont local
- Uvicorn
- pwdlib + Argon2
- sesiones firmadas de Starlette

La arquitectura y las decisiones del proyecto están documentadas en [`docs/`](docs/).

## Estado actual

NERISOFT ya cuenta con:

- bootstrap técnico;
- shell principal y dashboard visual base;
- login funcional y sesión;
- configuración inicial del primer administrador;
- gestión de usuarios;
- Select NERISOFT;
- assets críticos locales;
- navegación parcial HTMX con shell persistente;
- saneamiento técnico previo a Roles y Permisos;
- base técnica de Roles y Permisos: modelo, catálogo, autorización y migración;
- gestión de roles: alta, edición, permisos y activación/desactivación;
- asignación de roles a usuarios con controles de alcance y permisos granulares;
- portada propia de Configuración;
- Usuarios y Roles y permisos como destinos independientes;
- Mi cuenta separado de la administración de usuarios;
- tests unitarios básicos y validación automática en GitHub Actions.

La siguiente tarea funcional prevista es **Tarea 9.4 — Validación integral de permisos**.

## Primera instalación en Windows

Abrir PowerShell en `D:\NeriSoft`.

### 1. Crear el entorno virtual

```powershell
cd D:\NeriSoft
python -m venv .venv
```

### 2. Activarlo

```powershell
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activación:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Instalar assets locales

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\vendor-assets.ps1
```

NERISOFT requiere estos assets para arrancar. No usa fallback remoto durante la ejecución normal.

### 5. Aplicar migraciones

```powershell
python -m alembic upgrade head
```

### 6. Ejecutar NERISOFT

Para desarrollo:

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

O bien:

```powershell
python run.py
```

### 7. Abrir en el navegador

En el servidor:

```text
http://127.0.0.1:8000
```

Desde otra PC de la LAN:

```text
http://IP-DEL-SERVIDOR:8000
```

## Configuración inicial segura

Mientras no existan usuarios, `/setup` permite crear el primer administrador.

Por defecto esa operación solo se admite desde el propio servidor (`127.0.0.1` / `::1`). Si una instalación necesita habilitar temporalmente el setup desde otra PC de la LAN:

```text
NERISOFT_SETUP_ALLOW_REMOTE=true
```

Después de crear el administrador, `/setup` deja de estar disponible.

## Sesiones y HTTPS

En desarrollo local por HTTP puede mantenerse:

```text
NERISOFT_SESSION_HTTPS_ONLY=false
```

Para una instalación real accesible por red se debe publicar NERISOFT detrás de HTTPS y activar:

```text
NERISOFT_SESSION_HTTPS_ONLY=true
```

## Verificación rápida

```text
http://127.0.0.1:8000/health
```

Debe responder estado `ok` para aplicación y base de datos.

Documentación FastAPI:

```text
http://127.0.0.1:8000/api/docs
```

## Tests

Dependencias de desarrollo:

```powershell
python -m pip install -r requirements-dev.txt
```

Ejecución:

```powershell
python -m pytest -q
```

El workflow `.github/workflows/tests.yml` ejecuta compilación, migraciones sobre una base SQLite temporal, tests y validación de sintaxis JavaScript en cada push a `main`.

## Base de datos

Por defecto:

```text
D:\NeriSoft\data\nerisoft.db
```

SQLite vive exclusivamente en el servidor. Los clientes acceden por HTTP y nunca deben abrir ni compartir directamente el archivo `.db`.

Migraciones actuales:

```text
0001_users
0002_user_superuser
0003_roles_permissions
```

## Flujo de trabajo

```text
1 tarea -> validación -> 1 commit -> main -> pull local -> prueba -> siguiente tarea
```

Para actualizar la instalación local:

```powershell
cd D:\NeriSoft
git pull origin main
```
