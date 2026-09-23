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
- Tarea 9.2: gestión de roles, permisos y estado desde Configuración;
- Tarea 9.3: asignación de roles a usuarios y permisos granulares en Gestión de Usuarios;
- reorganización de Configuración: portada propia, Usuarios y Roles como destinos independientes, Mi cuenta separada y Administrador del sistema representado como tipo de acceso, no como rol;
- Tarea 9.3.5: normalización de Roles y Permisos, catálogo actual explícitamente limitado a Sistema, formulario separado del listado y UI reducida a información operativa;
- Tarea 10.0: normalización de documentación vigente y cierre del alcance mínimo de Configuración de empresa.

## Decisión de secuencia

Se deja Roles y Permisos en su estado actual.

`9.4 — Validación integral de permisos` permanece pendiente, pero no bloquea el comienzo de los módulos funcionales.

Auditoría también se posterga: no se construirá un motor transversal de auditoría antes de disponer de operaciones reales de negocio que permitan definir su alcance con evidencia.

Siguiente bloque funcional:

```text
Configuración de empresa
```

Después:

```text
Clientes
→ Proveedores
→ Productos
→ Depósitos / Stock
→ Ventas
→ Cuenta corriente / cobranzas
→ Compras
→ Tesorería
→ Contabilidad / Impuestos
```

## Regla de priorización

Antes de crear infraestructura transversal:

- debe existir una necesidad real;
- debe desbloquear una operación próxima;
- debe haber información suficiente para diseñarla;
- si puede postergarse sin romper lo existente, se posterga;
- no se generaliza antes de observar patrones reales.

Regla corta:

```text
Primero operación real.
Después patrón.
Recién entonces abstracción.
```

## Referencia funcional externa

Se adopta como referencia permanente la documentación pública de Holistor Gestión ERP:

https://holistor.atlassian.net/wiki/spaces/TDADGC/overview?homepageId=566427761

Uso permitido:

- mapa de módulos;
- detección de dependencias;
- revisión de maestros y parámetros usados por un ERP argentino real;
- contraste de circuitos antes de diseñarlos.

No usar como especificación para copiar UI o complejidad completa.

La referencia organiza, entre otras, áreas de Ventas, Compras, Stock, Tesorería, Impuestos, Contabilidad y Administración. En Administración aparecen Empresa, Puntos de Venta, Talonarios, Tipos de Comprobante, Monedas, Condiciones Fiscales, Tipos de Documento, Provincias, Localidades, Alícuotas, Tipos de Cobro/Pago, Conceptos y parámetros. NERISOFT incorporará cada pieza solo cuando una función real la necesite.

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

## Etapa 2 — Seguridad — PAUSA FUNCIONAL

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
- protección de roles asignados a la propia cuenta para gestores delegados;
- asignación de roles a usuarios;
- permisos granulares de consulta, alta, edición, estado y asignación de roles en Gestión de Usuarios;
- protección de cuentas con permisos superiores al alcance del gestor;
- Configuración con portada propia y navegación de Usuarios/Roles separada;
- Mi cuenta separada de la administración de usuarios;
- Administrador del sistema representado como tipo de acceso y no como rol;
- catálogo de permisos clasificado por área funcional, actualmente solo `Sistema`;
- formulario de Roles separado visual y funcionalmente del listado;
- códigos técnicos y metadatos secundarios retirados de la UI principal de Roles;
- regla de crecimiento: cada módulo nuevo debe definir, aplicar y probar sus propios permisos junto con su funcionalidad.

Pendiente, pero no bloqueante para el próximo módulo:

- Tarea 9.4: validación integral de permisos y regresiones;
- cambio de contraseña;
- recuperación de contraseña;
- rate limiting/bloqueo ante intentos fallidos;
- política de despliegue HTTPS.

## Etapa 3 — Auditoría — POSTERGADA

No es el próximo paso.

La auditoría se diseñará cuando existan operaciones reales como altas/modificaciones de maestros, movimientos, comprobantes, anulaciones o ajustes. En ese momento se decidirá qué registrar, con qué granularidad y qué necesita trazabilidad.

No crear ahora un motor genérico de eventos, snapshots o historial universal.

## Etapa 4 — Configuración general — PRÓXIMO FOCO

Primer bloque funcional:

```text
Configuración de empresa
```

Alcance mínimo aprobado:

- una sola empresa por instalación;
- razón social obligatoria;
- nombre comercial opcional;
- CUIT obligatorio, normalizado y validado;
- condición fiscal obligatoria;
- domicilio fiscal obligatorio;
- localidad obligatoria;
- provincia obligatoria;
- código postal opcional;
- teléfono opcional;
- email opcional.

No se crearán todavía maestros separados de localidades, provincias, monedas o condiciones fiscales. La moneda principal queda fuera del alcance inicial hasta que un circuito monetario real la necesite.

También quedan fuera por ahora ARCA, CAE, certificados, puntos de venta, talonarios, IIBB, inicio de actividades, logo, retenciones, percepciones, SMTP y configuración contable.

El acceso se incorporará desde la portada de Configuración y tendrá un único permiso funcional previsto:

```text
system.company.manage
```

Secuencia del bloque:

```text
10.0 Documentación vigente ✅
10.1 Modelo + migración + permiso ✅
10.2 Backend y validaciones
10.3 UI y prueba funcional
```

Hasta que Empresa esté implementada, el shell no debe mostrar una sociedad ficticia como si estuviera configurada.

## Etapa 5 — Maestros

- clientes
- proveedores
- productos
- categorías de productos
- depósitos
- condiciones IVA
- tipos de comprobante

Los maestros secundarios se agregan por necesidad del circuito, no todos por adelantado.

Patrón común:

```text
Listado
Nuevo
Editar
Ver
Buscar
Filtrar
Activar/desactivar
```

La auditoría no se presupone todavía como patrón obligatorio de pantalla; se incorporará cuando su diseño esté sustentado por operaciones reales.

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
10.2 Empresa: backend y validaciones
→ 10.3 Empresa: UI y prueba funcional
→ 10.3 Empresa: UI y prueba funcional
→ Clientes
→ Proveedores
→ Productos
→ Depósitos / Stock
→ Ventas
→ Cuenta corriente / cobranzas
→ Compras
→ Tesorería
→ Contabilidad / Impuestos
```

Pendientes transversales para retomar cuando exista evidencia suficiente o una necesidad concreta:

```text
9.4 Validación integral de permisos
Auditoría
Seguridad operativa adicional
```
