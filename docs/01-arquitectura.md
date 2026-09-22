# 01 — Arquitectura de NERISOFT

## Objetivo

NERISOFT será un ERP administrativo, comercial y contable pensado para una empresa inicialmente, con múltiples usuarios conectados por red local.

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
- Tabler Icons por CDN

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

Configuración prevista:

```sql
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
PRAGMA busy_timeout=5000;
```

Reglas:

- Transacciones cortas.
- Nunca mantener una transacción abierta mientras el usuario está editando una pantalla.
- La transacción comienza al confirmar una operación.
- Toda operación compuesta debe ser atómica.

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

## Migración futura

El código debe evitar depender innecesariamente de particularidades de SQLite para facilitar una futura migración a PostgreSQL si la concurrencia o el volumen lo requieren.

## Estructura inicial prevista

```text
nerisoft/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   ├── permissions.py
│   │   └── formatting.py
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── routes/
│   ├── accounting/
│   ├── templates/
│   └── static/
│       ├── css/
│       ├── js/
│       └── img/
├── alembic/
├── tests/
├── alembic.ini
├── requirements.txt
└── run.py
```

No se crearán capas adicionales por costumbre. Cualquier `repository`, abstracción o servicio adicional deberá justificar su existencia.

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

Aun así, deben evitarse decisiones que hagan imposible incorporarla más adelante. No se agregará `empresa_id` indiscriminadamente desde el inicio si no aporta valor real todavía, pero tampoco se hardcodearán datos societarios dentro de lógica de negocio.

## Contabilidad integrada

La contabilidad forma parte de la operación, no de un proceso diferido opcional.

Ejemplo conceptual:

```text
Factura
├── Cuenta corriente
├── IVA
├── Stock
└── Asiento contable
```

Las relaciones entre documentos, movimientos y asientos deben ser explícitas y navegables.

## Configuración contable

Las cuentas contables no se hardcodean en el código.

Ejemplo:

```text
Ventas mercaderías  -> 4.1.01.001 Ventas
IVA débito fiscal   -> 2.1.03.001 IVA Débito Fiscal
Clientes            -> 1.1.03.001 Deudores por Ventas
Caja                -> 1.1.01.001 Caja
```

Las reglas podrán evolucionar por categoría, producto, tipo de operación u otra dimensión si el negocio lo requiere.
