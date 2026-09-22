# 04 — Roadmap de NERISOFT

El desarrollo se realizará por etapas cerradas. Cada etapa se divide en tareas pequeñas; una tarea debe dejar `main` en estado ejecutable.

## Etapa 0 — Base técnica

Objetivo: proyecto arrancando limpio.

- estructura FastAPI
- Uvicorn
- SQLAlchemy 2
- SQLite
- Alembic
- Jinja2
- HTMX
- Tabler Icons CDN
- `static/css`, `static/js`, `templates`
- configuración general

Resultado esperado:

```bash
python -m uvicorn app.main:app --reload
```

## Etapa 1 — Sistema visual

- layout 100% viewport
- sidebar colapsable
- header
- workspace principal
- design tokens grafito/dorado
- Geist
- números tabulares
- componentes base

## Etapa 2 — Seguridad

- login
- logout
- sesiones
- usuarios
- roles
- permisos
- protección de rutas
- CSRF donde corresponda

## Etapa 3 — Auditoría

- registro de acciones
- entidad afectada
- usuario
- fecha/hora
- IP
- valores anteriores/nuevos cuando corresponda

## Etapa 4 — Configuración general

- datos de empresa
- parámetros generales
- moneda principal
- condiciones fiscales básicas

## Etapa 5 — Maestros

- clientes
- proveedores
- productos
- categorías de productos
- depósitos
- condiciones IVA
- tipos de comprobante

Patrón común:

```text
Listado
Nuevo
Editar
Ver
Buscar
Filtrar
Activar/desactivar
Auditoría
```

## Etapa 6 — Stock

- depósitos
- movimientos
- saldos
- ajustes
- transferencias
- trazabilidad

## Etapa 7 — Ventas

Primer circuito comercial completo:

```text
Cliente
↓
Comprobante
↓
Items
↓
Impuestos
↓
Cuenta corriente
↓
Stock
↓
Contabilidad
```

Tipos iniciales:

- Factura
- Nota de crédito
- Nota de débito

Posteriores:

- Presupuesto
- Pedido
- Remito

## Etapa 8 — Cuenta corriente de clientes

- movimientos
- saldo derivado
- imputaciones
- consulta histórica

## Etapa 9 — Recibos y caja

- recibos
- aplicaciones
- efectivo
- transferencia
- cheque
- tarjeta
- otros medios
- movimientos de caja

## Etapa 10 — Compras

```text
Proveedor
↓
Comprobante
↓
Impuestos
↓
Cuenta corriente
↓
Stock
↓
Contabilidad
```

## Etapa 11 — Pagos

- órdenes de pago
- aplicaciones
- caja
- bancos
- retenciones
- contabilidad

## Etapa 12 — Tesorería

- cajas
- bancos
- cuentas bancarias
- cheques
- transferencias
- movimientos

## Etapa 13 — Contabilidad completa

- plan de cuentas
- ejercicios
- asientos
- mayor
- balance
- configuración contable

La generación contable estará integrada antes de esta etapa; aquí se completa su interfaz y explotación.

## Etapa 14 — Integración transaccional completa

Validar que operaciones como una factura ejecuten todos sus impactos dentro de una única unidad transaccional.

## Etapa 15 — Dashboard

Se construirá cuando existan datos reales.

Indicadores previstos:

- ventas del día
- ventas del mes
- saldo clientes
- saldo proveedores
- caja
- productos bajo stock
- últimos comprobantes
- vencimientos
- alertas

## Etapa 16 — Fiscal argentino

A implementar contra normativa vigente al momento del desarrollo:

- IVA
- ARCA
- CAE
- factura electrónica
- percepciones
- retenciones
- IIBB
- Libro IVA
- IVA Simple

## Primeras 10 tareas concretas

1. Bootstrap técnico FastAPI + SQLAlchemy + SQLite + Jinja2
2. Layout principal NERISOFT
3. Design system CSS grafito/dorado
4. Sidebar colapsable
5. Login
6. Usuarios
7. Roles y permisos
8. Auditoría
9. Configuración de empresa
10. Clientes

Después:

```text
Productos
→ Depósitos
→ Stock
→ Ventas
→ Cuenta corriente
→ Recibos
→ Compras
→ Tesorería
→ Contabilidad completa
```
