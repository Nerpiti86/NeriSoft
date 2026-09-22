# 01 — Arquitectura de NERISOFT

## Objetivo

NERISOFT es un ERP administrativo, comercial y contable pensado inicialmente para una empresa, con múltiples usuarios conectados por red local.

La prioridad es mantener una arquitectura simple, mantenible y trazable, evitando complejidad innecesaria.

## Stack oficial

### Backend

- Python
- FastAPI
- SQLAlchemy 2
- Alembic

### Persistencia

- SQLite en la primera etapa
- La base vive exclusivamente en el servidor
- No se comparte el archivo `.db` por red
- Los clientes acceden por HTTP a través de FastAPI

### Frontend

- Jinja2
- HTMX
- Vanilla JavaScript
- CSS propio
- Geist local
- Tabler Icons Webfont local

Los assets visuales críticos se sirven desde `app/static/vendor/`. No se depende de CDNs durante la ejecución normal.

### Servidor

- Uvicorn

## Topología de red

```text
PC Administración ─┐
PC Ventas ─────────┤
PC Contabilidad ───┼── LAN ── Servidor NERISOFT
PC Depósito ───────┤              │
PC Gerencia ───────┘              ├─ FastAPI/Uvicorn
                                  └─ SQLite
```

Los puestos cliente nunca deben abrir, montar o escribir directamente el archivo SQLite.

## SQLite multiusuario

SQLite es válido para la primera etapa si la aplicación centraliza todos los accesos a través del servidor.

Configuración actual:

```sql
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
PRAGMA synchronous=NORMAL;
PRAGMA busy_timeout=5000;
```

Reglas:

- transacciones cortas;
- nunca mantener una transacción abierta mientras el usuario edita una pantalla;
- la transacción comienza al confirmar una operación;
- toda operación compuesta debe ser atómica.

Ejemplo:

```text
BEGIN
crear comprobante
crear items
crear impuestos
crear movimiento de cuenta corriente
crear movimiento de stock
generar asiento
validar asiento
COMMIT
```

Ante cualquier error:

```text
ROLLBACK
```

## Shell y navegación

Las pantallas autenticadas reutilizan `authenticated.html` como shell compartido.

HTMX mejora progresivamente la navegación entre páginas compatibles:

```text
sidebar + topbar permanecen montados
            ↓
solo cambia .workspace
```

Las rutas FastAPI continúan devolviendo HTML completo. Si JavaScript o HTMX no están disponibles, los enlaces conservan navegación HTML normal.

La autorización nunca depende de HTMX: siempre se valida en backend.

## Seguridad base

- contraseñas con Argon2 mediante `pwdlib`;
- sesión firmada de Starlette;
- cookie `HttpOnly`, `SameSite=Lax`, máximo 8 horas;
- CSRF en operaciones de escritura existentes;
- usuarios inactivos no pueden mantener acceso;
- helpers de autenticación y CSRF centralizados en `app/core/auth.py`;
- `/setup` solo se admite desde loopback por defecto mientras la instalación está vacía;
- para producción en red debe utilizarse HTTPS y `NERISOFT_SESSION_HTTPS_ONLY=true`.

## Assets locales

NERISOFT requiere localmente:

- Geist `v1.7.2`;
- Tabler Icons Webfont `3.35.0`;
- HTMX `2.0.7`.

Se instalan con:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\vendor-assets.ps1
```

Si faltan assets críticos, el arranque se detiene con un error explícito en lugar de recurrir silenciosamente a Internet.

## Formateo

El formateo visible se centraliza progresivamente en `app/core/formatting.py`.

Los `DATETIME` sin zona horaria provenientes de `CURRENT_TIMESTAMP` de SQLite se interpretan como UTC y se convierten a `America/Argentina/Cordoba` para su presentación.

## Migración futura

El código debe evitar depender innecesariamente de particularidades de SQLite para facilitar una futura migración a PostgreSQL si la concurrencia o el volumen lo requieren.

## Estructura actual relevante

```text
nerisoft/
├── app/
│   ├── main.py
│   ├── users.py
│   ├── core/
│   │   ├── assets.py
│   │   ├── auth.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── formatting.py
│   │   ├── security.py
│   │   ├── templates.py
│   │   └── user_validation.py
│   ├── models/
│   ├── templates/
│   │   ├── base.html
│   │   └── authenticated.html
│   └── static/
│       ├── css/
│       ├── js/
│       └── vendor/
├── alembic/
├── scripts/
├── tests/
├── .github/workflows/
├── requirements.txt
├── requirements-dev.txt
└── run.py
```

No se crearán capas adicionales por costumbre. Cada abstracción debe reducir duplicación o aislar una responsabilidad real.

## Módulos funcionales

```text
NERISOFT
├── Sistema
│   ├── Usuarios
│   ├── Roles
│   ├── Permisos
│   ├── Configuración
│   └── Auditoría
├── Ventas
│   ├── Clientes
│   ├── Comprobantes
│   ├── Cuenta corriente
│   └── Recibos
├── Compras
│   ├── Proveedores
│   ├── Comprobantes
│   ├── Cuenta corriente
│   └── Órdenes de pago
├── Stock
│   ├── Productos
│   ├── Depósitos
│   └── Movimientos
├── Tesorería
│   ├── Cajas
│   ├── Bancos
│   └── Movimientos
└── Contabilidad
    ├── Plan de cuentas
    ├── Asientos
    ├── Ejercicios
    └── Configuración contable
```

## Multiempresa

Multiempresa no forma parte de la primera versión.

Deben evitarse decisiones que impidan incorporarla más adelante, pero no se agregará `empresa_id` indiscriminadamente antes de necesitarlo. Mientras Configuración de Empresa no esté implementada, el shell muestra un estado neutro `Sin configurar` y no hardcodea una sociedad ficticia.

## Contabilidad integrada

La contabilidad forma parte de la operación, no de un proceso diferido opcional.

```text
Factura
├── Cuenta corriente
├── IVA
├── Stock
└── Asiento contable
```

Las cuentas contables se asignarán mediante configuración y nunca mediante constantes de negocio hardcodeadas.

## Validación automática

El proyecto mantiene tests básicos en `tests/` y un workflow en `.github/workflows/tests.yml` que ejecuta:

- compilación de Python;
- pytest;
- validación de sintaxis de JavaScript.

Las pruebas locales de interfaz siguen siendo obligatorias después de cada tarea.
