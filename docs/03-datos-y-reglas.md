# 03 — Datos y reglas de negocio

## Convenciones de almacenamiento

### Dinero

Todo importe monetario se almacena como entero en centavos.

Ejemplos:

```text
$ 10,00       -> 1000
$ 125,50      -> 12550
$ 1.234,56    -> 123456
```

En SQLAlchemy se utilizará `BigInteger` para montos monetarios.

Nombres sugeridos:

```text
precio_centavos
subtotal_centavos
iva_centavos
total_centavos
saldo_centavos
```

No se utilizará `FLOAT` para dinero.

### Fechas

Las fechas no se almacenan como enteros arbitrarios.

- Fecha sin hora: `DATE`
- Fecha y hora: `DATETIME`

Formato visible argentino:

```text
22/09/2026
22/09/2026 14:37
```

### Cantidades y porcentajes

- Cantidades enteras: `INTEGER`
- Cantidades fraccionarias: tipo decimal apropiado según dominio
- Porcentajes: entero escalado o decimal exacto; nunca `FLOAT` sin control

### IDs

Las claves primarias internas serán enteras.

Los números comerciales, como número de comprobante, no se usan como clave primaria.

## Formato visible argentino

### Importe

```text
$ 1.234.567,89
```

### Fecha

```text
22/09/2026
```

Los formateadores deben centralizarse para no repetir lógica en templates.

## Stock

El stock se determina por movimientos.

No se modifica un saldo final directamente.

Ejemplos de movimiento:

```text
+10 compra
-2 venta
+3 ajuste positivo
-5 transferencia de salida
+5 transferencia de entrada
```

Tablas previstas:

```text
products
warehouses
stock_movements
stock_balances
```

`stock_balances` puede existir como proyección/cache de rendimiento, pero la trazabilidad primaria vive en `stock_movements`.

## Cuentas corrientes

El saldo se obtiene de movimientos, no de un campo editable.

Ejemplo cliente:

```text
Factura        +121.000,00
Recibo         -100.000,00
Nota crédito    -21.000,00
Saldo                 0,00
```

Tablas conceptuales:

```text
customer_account_movements
supplier_account_movements
```

## Tesorería

Caja y bancos siguen el mismo principio:

> ningún saldo se edita directamente; el saldo surge de movimientos.

Ejemplos:

```text
cash_accounts
cash_movements
bank_accounts
bank_movements
```

## Contabilidad

### Plan de cuentas

Jerárquico y configurable.

Ejemplo:

```text
1 Activo
1.1 Activo Corriente
1.1.01 Caja y Bancos
1.1.01.001 Caja
```

### Asientos

Tablas previstas:

```text
journal_entries
journal_entry_lines
```

Regla obligatoria:

```text
SUM(debe) == SUM(haber)
```

Un asiento desbalanceado no puede confirmarse.

### Reglas contables

Las cuentas se asignan mediante configuración, no mediante constantes de código.

Ejemplos:

```text
Venta general       -> Ventas
IVA débito fiscal   -> IVA Débito Fiscal
Cliente             -> Deudores por Ventas
Caja                -> Caja
```

## Operaciones atómicas

Las operaciones que impactan varios subsistemas deben ejecutarse en una única transacción lógica.

Ejemplo de factura:

```text
START TRANSACTION
1. Crear comprobante
2. Crear renglones
3. Calcular impuestos
4. Crear cuenta corriente
5. Crear movimientos de stock
6. Crear asiento contable
7. Validar Debe = Haber
COMMIT
```

Si falla cualquier paso:

```text
ROLLBACK
```

No se acepta una factura emitida sin los impactos obligatorios asociados.

## Auditoría

La auditoría transversal se **posterga** hasta disponer de operaciones reales que permitan definir con evidencia qué debe registrarse y con qué granularidad.

No se construirá ahora:

- un motor genérico de auditoría;
- un event bus;
- snapshots universales;
- historial transversal;
- infraestructura preventiva “por las dudas”.

Cuando existan altas y modificaciones de maestros, movimientos, comprobantes, anulaciones, ajustes u otras operaciones sensibles, la auditoría se diseñará sobre esos casos concretos. En ese momento se definirán los datos mínimos de trazabilidad necesarios para cada operación.

## Seguridad y permisos

Modelo previsto:

```text
users
roles
permissions
user_roles
role_permissions
```

Permisos granulares de referencia:

```text
ventas.ver
ventas.crear
ventas.editar
ventas.anular
clientes.ver
clientes.crear
clientes.editar
stock.ver
stock.mover
contabilidad.ver
contabilidad.generar
contabilidad.editar
```

## Empresa

Primera etapa: **una sola empresa por instalación**.

Alcance mínimo aprobado para Configuración de empresa:

- razón social — obligatoria;
- nombre comercial — opcional;
- CUIT — obligatorio, normalizado y validado;
- condición fiscal — obligatoria;
- domicilio fiscal — obligatorio;
- localidad — obligatoria;
- provincia — obligatoria;
- código postal — opcional;
- teléfono — opcional;
- email — opcional.

En esta etapa `localidad`, `provincia` y `condición fiscal` no requieren maestros independientes. Se almacenan o controlan dentro del módulo Empresa con la solución mínima necesaria.

No forman parte de este alcance inicial:

- moneda principal;
- ingresos brutos;
- inicio de actividades;
- logo;
- ARCA / CAE;
- certificados;
- puntos de venta;
- talonarios;
- retenciones y percepciones;
- SMTP;
- parámetros contables.

Esos datos o maestros se incorporarán cuando una operación real los necesite.

Los datos de la empresa no deben estar hardcodeados.
