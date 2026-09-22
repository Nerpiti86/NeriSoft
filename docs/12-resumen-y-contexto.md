# 12 — Resumen del proyecto y contexto para nuevo hilo

Actualizado: 22/09/2026

Este documento concentra el estado real de NERISOFT hasta la Tarea 7 y sirve como punto de partida para continuar el desarrollo en un hilo nuevo sin perder decisiones previas.

## Proyecto

- Nombre: **NERISOFT**
- Repositorio: `Nerpiti86/NeriSoft`
- Rama de trabajo: `main`
- Instalación local habitual: `D:\NeriSoft`
- Modalidad prevista: multiusuario en red local
- La base SQLite vive solamente en el servidor. Los clientes acceden por HTTP y nunca comparten el archivo `.db`.

## Regla de trabajo acordada

El proyecto se desarrolla de forma incremental y estricta:

```text
1 tarea -> validación -> 1 commit coherente en main -> pull local -> prueba -> siguiente tarea
```

No usar ramas ni PR salvo que se cambie explícitamente esta regla.

Durante pruebas locales se avanza **una acción/comando por vez** para poder aislar errores.

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
- Tabler Icons webfont/CDN
- Uvicorn
- pwdlib + Argon2 para contraseñas
- SessionMiddleware de Starlette para sesiones firmadas

## Arquitectura y reglas de datos

- SQLite configurado con WAL, claves foráneas y `busy_timeout=5000`.
- Migración futura a PostgreSQL si la concurrencia lo requiere.
- Multiempresa: prevista, todavía no implementada.
- Stock: sí.
- Contabilidad: integrada desde el inicio y configurable.
- Dinero: `BIGINT` en centavos, nunca `float`.
- Fechas: `DATE`/`DATETIME`, no enteros.
- IDs: enteros como claves primarias.
- Operaciones importantes deben ser atómicas: cabecera, ítems, impuestos, cuenta corriente, stock y contabilidad dentro de una misma transacción.
- Saldos de stock, cuentas corrientes, tesorería y contabilidad se derivan de movimientos; no se editan directamente.

## Módulos previstos

- Sistema: Usuarios, Roles, Permisos, Configuración, Auditoría
- Ventas: Clientes, Comprobantes, Cuenta corriente, Recibos
- Compras: Proveedores, Comprobantes, Cuenta corriente, Órdenes de pago
- Stock: Productos, Depósitos, Movimientos
- Tesorería: Cajas, Bancos, Movimientos
- Contabilidad: Plan de cuentas, Asientos, Ejercicios, Configuración contable
- Reportes
- Configuración

Fiscal Argentina se implementará más adelante validando especificaciones vigentes al momento de desarrollar: IVA, ARCA/CAE, factura electrónica, percepciones/retenciones, IIBB, Libro IVA, IVA Simple, etc.

## Dirección visual aprobada

La referencia visual aprobada es un ERP de escritorio denso y limpio:

- viewport completo
- sidebar grafito
- topbar oscura
- acento dorado
- workspace claro
- diseño desktop-first
- sin shell centrado ni `max-width` global
- sidebar expandida aprox. 248 px y colapsada 68 px
- densidad calibrada para **1920×1080 al 100% de zoom del navegador**
- radios contenidos: 6/8/10 px
- sombras moderadas
- **Geist** como fuente de interfaz
- **Tabler Icons** para todos los iconos

No mezclar librerías de iconos.

### Convenciones numéricas y visibles

Usar `tabular-nums` en:

- comprobantes
- códigos
- fechas
- importes
- cantidades
- porcentajes comparables/alineados

Fechas visibles:

```text
dd/mm/yyyy
```

y cuando corresponde:

```text
dd/mm/yyyy HH:mm
```

Importes alineados a la derecha.

### Abreviaturas de comprobantes

Convención oficial:

- `FC` = Factura
- `NC` = Nota de Crédito
- `ND` = Nota de Débito
- `RC` = Recibo
- `OP` = Orden de Pago
- `OC` = Orden de Compra
- `RM` = Remito
- `PR` = Presupuesto
- `PD` = Pedido

La letra fiscal va después de la abreviatura:

```text
FC A 0004-00001842
FC B 0004-00002591
NC A 0004-00000163
```

No introducir abreviaturas nuevas sin documentarlas primero.

## Trabajo completado

### Tarea 1 — Bootstrap técnico

Commit principal:

```text
73bd0d89696ef4aee6c0189c318fc7b3f1b1982b
chore: bootstrap NERISOFT technical foundation
```

Incluyó FastAPI, SQLAlchemy, SQLite, Alembic, Jinja2, HTMX, JS/CSS base, Tabler Icons, Uvicorn, `/health` y `/api/docs`.

Refinamiento visual posterior:

```text
1544d3ff9404aefa3b1b5656f064d8f17f825951
style: refine typography radii and shadows
```

### Tarea 2 — Application shell

```text
eb4913780e976ab4eef67c5d511f42584b2af5fe
feat: build NERISOFT application shell
```

Incluyó sidebar, topbar, búsqueda, selector visual de empresa, notificaciones, usuario y persistencia del sidebar colapsado.

Corrección del icono Stock:

```text
ae4bf61b527830ce0a92583c6416f0ca3eea885d
fix: restore stock sidebar icon
```

### Tarea 3 — Dashboard visual base

```text
b58688a1a245415b1638a3ac2aacb6a96e364ab3
feat: build dashboard visual base
```

Dashboard con datos mock locales: KPIs, gráfico, alertas, comprobantes recientes, cuentas por cobrar y stock bajo.

### Calibración de densidad y convenciones

```text
ed32d975def0885f142e1bee1ace3e8e4c8147b9
style: calibrate dashboard density and data conventions
```

Se fijó 1920×1080 a zoom 100% como referencia oficial y se normalizaron convenciones visibles.

### Tarea 4 — Login visual

```text
05e6f64c1f8f51297cb01bcef3a95e61c96cf27e
feat: add login visual screen
```

Refinamiento del botón principal:

```text
bd288ba792d4d3ab7ee5baedd09a37a415f40e45
style: refine login primary button
```

### Tarea 5 — Usuarios base

```text
52fdc3b1f17cf77dfe630fb4825c3e4ecc60fdf1
feat: add base user model and password hashing
```

Se agregó:

- modelo `User`
- nombre
- username único
- email único
- `password_hash`
- `is_active`
- timestamps
- hashing seguro con Argon2 vía `pwdlib`
- migración `0001_users`

### Tarea 6 — Configuración inicial del administrador

```text
aff1cf63c782b95750d453a1cf950da0c70325e7
feat: add initial admin setup flow
```

Se agregó `/setup`, disponible solo mientras no existan usuarios. Permite crear desde la app el primer administrador y lo marca activo + superusuario.

Migración:

```text
0002_user_superuser
```

Corrección posterior para mostrar/ocultar ambas contraseñas con Tabler Icons:

```text
5d8e67513a5adf6dc520fffc5423cb4f04691860
fix: add password visibility toggles to setup
```

El primer administrador fue creado y verificado correctamente en la base local.

### Tarea 7 — Login real y sesión

```text
59e5ac479c9d1d82a24858c5dca2dfce6b3eb8ee
feat: enable authenticated login and sessions
```

Estado actual de autenticación:

- login por username o email
- verificación Argon2
- usuarios inactivos rechazados
- mensaje genérico para credenciales inválidas
- cookie de sesión firmada `HttpOnly`
- `SameSite=Lax`
- duración máxima de 8 horas
- CSRF en login y logout
- dashboard `/` protegido
- `/setup` bloqueado una vez creado el primer usuario
- logout funcional
- nombre e iniciales del usuario autenticado en el encabezado
- clave de sesión persistida localmente en `data/session.secret` si no se define `NERISOFT_SESSION_SECRET`

Todavía no existen roles ni permisos granulares.

## Base de datos y migraciones actuales

Base por defecto:

```text
D:\NeriSoft\data\nerisoft.db
```

Migraciones existentes:

```text
0001_users
0002_user_superuser
```

En una instalación nueva o después de incorporar migraciones:

```powershell
python -m alembic upgrade head
```

## Cómo levantar la app localmente

Desde `D:\NeriSoft`, con `.venv` activado:

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Servidor local:

```text
http://127.0.0.1:8000
```

## Documentación existente

- `docs/01-arquitectura.md`
- `docs/02-diseno-ui.md`
- `docs/03-datos-y-reglas.md`
- `docs/04-roadmap.md`
- `docs/05-flujo-trabajo.md`
- `docs/06-referencia-visual.md`
- `docs/07-convenciones-visuales.md`
- `docs/08-login.md`
- `docs/09-usuarios-base.md`
- `docs/10-configuracion-inicial-admin.md`
- `docs/11-login-sesion.md`
- `docs/12-resumen-y-contexto.md` — este documento

## Pendientes naturales, todavía NO implementados

No asumir orden sin aprobación. Entre los próximos bloques posibles están:

- pantalla **Configuración → Usuarios**
- alta/edición/activación/desactivación de usuarios
- roles y permisos
- cambio de contraseña
- recuperación de contraseña
- bloqueo/rate limiting ante intentos fallidos
- auditoría
- reemplazar progresivamente datos mock del dashboard por datos reales
- comenzar módulos funcionales de Ventas/Compras/Stock

## Contexto para pegar en un hilo nuevo

Copiar este bloque como primer mensaje del nuevo hilo:

```text
Estamos desarrollando NERISOFT, un ERP administrativo/comercial/contable.
Repositorio exclusivo: https://github.com/Nerpiti86/NeriSoft
Trabajamos directamente en main, sin ramas ni PRs.
Mi instalación local está en D:\NeriSoft.
Regla de trabajo: una tarea por vez -> vos modificás GitHub -> verificás -> un commit coherente en main -> me decís git pull -> yo pruebo localmente -> recién después seguimos.
Cuando me guíes en pruebas locales, dame una sola acción/comando por mensaje.

Antes de tocar código, leé docs/12-resumen-y-contexto.md y la documentación relacionada dentro de docs/.

Estado actual:
- bootstrap FastAPI + SQLAlchemy 2 + SQLite + Alembic completo
- shell y dashboard visual aprobados
- densidad calibrada para 1920x1080 a 100% de zoom
- Geist + Tabler Icons
- convenciones argentinas de fechas/importes y comprobantes documentadas
- usuarios base con Argon2
- primer administrador creado desde /setup
- login real por usuario/email
- sesión firmada + CSRF
- dashboard protegido
- logout funcional
- roles/permisos todavía no implementados

No rompas las convenciones visuales ni de datos ya documentadas. Todo cambio nuevo debe quedar documentado.
```

## Nota para continuidad

Antes de iniciar una nueva tarea, verificar siempre `main` actual y leer los archivos que se vayan a modificar. Mantener cada cambio acotado, documentado y ejecutable.
