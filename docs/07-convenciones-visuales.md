# 07 — Convenciones visuales de datos

## Objetivo

NERISOFT debe presentar datos administrativos de forma compacta, estable y fácil de escanear. Las convenciones de esta sección son obligatorias para nuevas pantallas.

## Números tabulares

Se usa `font-variant-numeric: tabular-nums lining-nums` en:

- comprobantes
- códigos
- fechas
- importes
- cantidades
- porcentajes cuando se comparan en columnas

Esto mantiene alineados los dígitos sin cambiar la familia tipográfica principal: **Geist**.

Clases de referencia:

```css
.document-number,
.code-value,
.date-value,
.amount,
.quantity,
.percentage {
  font-variant-numeric: tabular-nums lining-nums;
}
```

## Comprobantes abreviados

En listados, tablas y referencias compactas no se escribirá el nombre largo del comprobante. Se utilizarán abreviaturas en mayúsculas.

Convenciones iniciales:

| Abreviatura | Comprobante |
| --- | --- |
| `FC` | Factura |
| `NC` | Nota de Crédito |
| `ND` | Nota de Débito |
| `RC` | Recibo |
| `OP` | Orden de Pago |
| `OC` | Orden de Compra |
| `RM` | Remito |
| `PR` | Presupuesto |
| `PD` | Pedido |

Cuando corresponda letra fiscal, se muestra después de la abreviatura:

```text
FC A 0004-00001842
FC B 0004-00002591
NC A 0004-00000163
```

No usar en la interfaz abreviaturas heredadas como `FAC`, `NCA` o `NDA`.

Las nuevas clases de comprobante deberán recibir una abreviatura explícita y documentada antes de incorporarse a la interfaz.

## Fechas

Formato visible argentino:

```text
22/09/2026
22/09/2026 14:37
```

Las fechas visibles usan números tabulares.

## Códigos

Los códigos de productos, clientes, cuentas u otras entidades se muestran con Geist y números tabulares. No se utiliza Geist Mono por defecto.

Ejemplo:

```text
ART-0182
CLI-0042
```

## Densidad

La referencia principal de escritorio es **1920×1080 con el navegador al 100% de zoom**.

La aplicación no debe depender de reducir el zoom del navegador para visualizar correctamente un dashboard o listado normal. En resoluciones menores se permite scroll interno o reorganización de grillas, pero no se diseñará tomando 70% u 80% de zoom como referencia.
