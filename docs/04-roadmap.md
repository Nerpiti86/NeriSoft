# 04 — Roadmap de NERISOFT

El desarrollo se realiza por etapas cerradas. Cada tarea debe dejar `main` ejecutable y verificable.

## Estado actual — 22/09/2026

Completado:

- base técnica FastAPI + SQLAlchemy + SQLite + Alembic;
- sistema visual, shell y dashboard de referencia;
- login funcional y sesión;
- configuración inicial del administrador;
- gestión de usuarios;
- Select NERISOFT;
- assets locales de Geist, Tabler Icons y HTMX;
- navegación parcial HTMX con shell persistente;
- saneamiento técnico previo a Roles y Permisos;
- tests básicos y workflow automático;
- Tarea 9.1: modelo, catálogo y helpers base de Roles y Permisos;
- Tarea 9.2: gestión de roles, permisos y estado desde Configuración.

Siguiente bloque funcional previsto:

```text
Tarea 9.3 — Asignación de roles a usuarios
```

## Etapa 0 — Base técnica ✅

- estructura FastAPI
- Uvicorn
- SQLAlchemy 2
- SQLite
- Alembic
- Jinja2
- HTMX local
- Geist local
- Tabler Icons local
- configuración general

## Etapa 1 — Sistema visual ✅

- layout 100% viewport
- sidebar colapsable
- header
- workspace principal
- design tokens grafito/dorado
- Geist
- números tabulares
- componentes base
- navegación parcial de workspace

## Etapa 2 — Seguridad — EN CURSO

Completado:

- login;
- logout;
- sesiones;
- usuarios;
- protección de rutas;
- CSRF en operaciones existentes;
- setup inicial restringido al servidor por defecto;
- modelo relacional de roles y permisos;
- catálogo inicial de permisos de Sistema;
- helpers para permisos efectivos y control de alcance;
- `superuser` como bypass administrativo total;
- alta y edición de roles;
- asignación de permisos a roles;
- activación/desactivación de roles;
- prevención de escalada por edición de roles fuera del alcance propio;
- protección de roles asignados a la propia cuenta para gestores delegados.

Pendiente:

- asignación de roles a usuarios;
- reemplazo progresivo de controles `superuser` por permisos granulares;
- cambio de contraseña;
- recuperación de contraseña;
- rate limiting/bloqueo ante intentos fallidos;
- política de despliegue HTTPS.

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

Hasta esta etapa el shell no debe mostrar una empresa ficticia como si estuviera configurada.

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

## Etapa 15 — Dashboard real

El dashboard visual ya existe con datos de muestra. Se conectará a datos reales cuando existan los módulos correspondientes.

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

## Próximas tareas naturales

```text
9.3 Asignación de roles a usuarios
→ 9.4 Validación integral de permisos
→ Auditoría
→ Configuración de empresa
→ Clientes
→ Proveedores / Productos / Depósitos
→ Stock
→ Ventas
→ Cuenta corriente
→ Recibos
→ Compras
→ Tesorería
→ Contabilidad completa
```
