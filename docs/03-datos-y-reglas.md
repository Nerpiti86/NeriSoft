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

La auditoría debe existir antes de liberar operaciones sensibles.

Datos mínimos:

```text
usuario
fecha_hora
acción
módulo
entidad
entidad_id
datos_anteriores
datos_nuevos
IP
```

Debe poder rastrearse quién creó, modificó, anuló o configuró información relevante.

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

Primera etapa: una empresa.

Datos societarios mínimos previstos:

- razón social
- nombre de fantasía
- CUIT
- domicilio
- condición IVA
- ingresos brutos
- inicio de actividades
- logo
- moneda principal

Los datos societarios no deben estar hardcodeados.
