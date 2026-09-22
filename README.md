# NERISOFT

ERP administrativo, comercial y contable para uso multiusuario en red local.

## Stack

- Python
- FastAPI
- SQLAlchemy 2
- SQLite
- Alembic
- Jinja2
- HTMX
- Vanilla JavaScript
- CSS propio
- Tabler Icons CDN
- Uvicorn

La arquitectura y las decisiones del proyecto están documentadas en [`docs/`](docs/).

## Estado actual

**Tarea 1 — Bootstrap técnico:** completada.

La aplicación ya incluye:

- servidor FastAPI;
- configuración centralizada;
- SQLAlchemy 2;
- SQLite local en `data/nerisoft.db`;
- modo WAL, claves foráneas y `busy_timeout` para la base SQLite;
- Alembic preparado para las migraciones;
- Jinja2;
- HTMX por CDN;
- Tabler Icons por CDN;
- CSS y JavaScript propios;
- endpoint de salud `/health`;
- documentación automática de la API en `/api/docs`.

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

Si PowerShell bloquea la activación por política de ejecución, para la sesión actual se puede usar:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Ejecutar NERISOFT

Para desarrollo:

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

O bien:

```powershell
python run.py
```

### 5. Abrir en el navegador

En el servidor:

```text
http://127.0.0.1:8000
```

Desde otra PC de la misma red, usar la IP local del servidor, por ejemplo:

```text
http://192.168.1.50:8000
```

## Verificación rápida

```text
http://127.0.0.1:8000/health
```

Debe responder con un estado `ok` para la aplicación y la base de datos.

La documentación interactiva de FastAPI queda disponible en:

```text
http://127.0.0.1:8000/api/docs
```

## Base de datos

Por defecto NERISOFT crea:

```text
D:\NeriSoft\data\nerisoft.db
```

El archivo SQLite es exclusivo del servidor de NERISOFT. Las PCs cliente acceden por HTTP y nunca deben abrir o compartir directamente el archivo `.db`.

## Alembic

Cuando existan modelos funcionales, las migraciones se crearán con:

```powershell
alembic revision --autogenerate -m "descripcion"
alembic upgrade head
```

## Flujo de trabajo

El desarrollo se realiza exclusivamente en `main` y sigue la regla:

```text
1 tarea -> validación -> 1 commit -> push a main -> pull local -> prueba
```

Para actualizar la instalación local después de cada tarea:

```powershell
cd D:\NeriSoft
git pull origin main
```
