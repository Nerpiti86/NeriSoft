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
- pwdlib + Argon2
- sesiones firmadas de Starlette

La arquitectura y las decisiones del proyecto están documentadas en [`docs/`](docs/).

## Estado actual

NERISOFT ya completó las etapas de:

- bootstrap técnico;
- shell principal;
- dashboard visual base;
- calibración de densidad y convenciones;
- login visual;
- usuarios base;
- configuración inicial del primer administrador;
- login real, sesión, CSRF, protección del dashboard y logout.

El estado consolidado del proyecto y el contexto preparado para continuar en un hilo nuevo están en:

[`docs/12-resumen-y-contexto.md`](docs/12-resumen-y-contexto.md)

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
python -m pip install -r requirements.txt
```

### 4. Aplicar migraciones

```powershell
python -m alembic upgrade head
```

### 5. Ejecutar NERISOFT

Para desarrollo:

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

O bien:

```powershell
python run.py
```

### 6. Abrir en el navegador

En el servidor:

```text
http://127.0.0.1:8000
```

Desde otra PC de la misma red, usar la IP local del servidor, por ejemplo:

```text
http://192.168.1.50:8000
```

En una instalación vacía, NERISOFT redirige a `/setup` para crear el primer administrador. Después de creado, el acceso normal se realiza desde `/login`.

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

Por defecto NERISOFT usa:

```text
D:\NeriSoft\data\nerisoft.db
```

El archivo SQLite es exclusivo del servidor de NERISOFT. Las PCs cliente acceden por HTTP y nunca deben abrir o compartir directamente el archivo `.db`.

Migraciones actuales:

```text
0001_users
0002_user_superuser
```

## Flujo de trabajo

El desarrollo se realiza exclusivamente en `main` y sigue la regla:

```text
1 tarea -> validación -> 1 commit -> main -> pull local -> prueba
```

Para actualizar la instalación local después de cada tarea:

```powershell
cd D:\NeriSoft
git pull origin main
```
