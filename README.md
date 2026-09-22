# NERISOFT

ERP administrativo, comercial y contable para uso multiusuario en red local.

## Estado

Proyecto en etapa inicial de diseño y bootstrap técnico.

## Stack oficial

- Python
- FastAPI
- SQLAlchemy 2
- SQLite
- Alembic
- Jinja2
- HTMX
- Vanilla JavaScript
- CSS propio
- Tabler Icons por CDN
- Uvicorn

## Entorno previsto

- Repositorio único: `Nerpiti86/NeriSoft`
- Rama de trabajo: `main`
- Instalación local prevista: `D:\NeriSoft`
- Uso: multiusuario en red local
- Base de datos: alojada únicamente en el servidor de NERISOFT
- Los puestos cliente acceden por navegador HTTP; nunca acceden directamente al archivo SQLite

## Principios del proyecto

1. Una tarea = un cambio coherente = un commit.
2. `main` debe quedar ejecutable después de cada tarea.
3. No se trabaja en ramas auxiliares salvo decisión explícita posterior.
4. El código y la documentación oficial viven exclusivamente en este repositorio.
5. La lógica de negocio debe estar centralizada y ser trazable.
6. Las operaciones críticas deben ser transaccionales: o se completa todo, o no se guarda nada.
7. Stock, cuentas corrientes, tesorería y contabilidad se modelan mediante movimientos; no se editan saldos finales de forma directa.
8. La contabilidad estará integrada desde el inicio y será configurable, sin cuentas hardcodeadas.

## Diseño visual

- Nombre de producto: **NERISOFT**
- Layout: 100% del viewport
- Sidebar: colapsable
- Paleta: grafito + dorado
- Tipografía: Geist
- Datos numéricos: `font-variant-numeric: tabular-nums`
- Interfaz desktop-first, densa y orientada a productividad administrativa

## Convenciones de datos

- Dinero: `BIGINT`, almacenado en centavos
- Fechas: `DATE`
- Fecha/hora: `DATETIME`
- IDs internos: enteros como claves primarias
- Formato visible argentino:
  - Fecha: `22/09/2026`
  - Importe: `$ 1.234.567,89`

## Módulos previstos

- Sistema
- Ventas
- Compras
- Stock
- Tesorería
- Contabilidad
- Reportes
- Configuración

Multiempresa queda fuera de la primera etapa. El diseño debe evitar dependencias innecesarias que dificulten incorporarla posteriormente.

## Documentación

- [Arquitectura](docs/01-arquitectura.md)
- [Diseño de interfaz](docs/02-diseno-ui.md)
- [Datos y reglas de negocio](docs/03-datos-y-reglas.md)
- [Roadmap](docs/04-roadmap.md)
- [Flujo de trabajo Git](docs/05-flujo-trabajo.md)

## Flujo de actualización local

Cuando una tarea haya sido finalizada y publicada en `main`:

```bash
git pull origin main
```

El directorio local previsto es:

```text
D:\NeriSoft
```
