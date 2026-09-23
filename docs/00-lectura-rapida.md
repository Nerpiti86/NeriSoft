# 00 — Lectura rápida de NERISOFT

> Entrada de 2 minutos para retomar el proyecto. Para el hilo siguiente, leer primero [`HANDOFF-ACTUAL.md`](HANDOFF-ACTUAL.md). Para contexto completo, ver [`12-resumen-y-contexto.md`](12-resumen-y-contexto.md).

Actualizado: 22/09/2026

## Qué es

NERISOFT es un ERP administrativo, comercial y contable, desktop-first, pensado para uso multiusuario en red local.

Repositorio: `Nerpiti86/NeriSoft`  
Rama estable: `main`  
Instalación local habitual: `D:\NeriSoft`

## Estado actual

Ya están implementados y funcionando:

- shell principal y dashboard base;
- login, sesión, CSRF y logout;
- primer administrador del sistema;
- gestión de usuarios;
- roles y permisos;
- asignación de uno o más roles a usuarios;
- permisos granulares y controles contra escalada;
- catálogo actual de permisos organizado explícitamente bajo el área `Sistema`;
- formulario de Roles separado del listado para no mezclar tareas ni sobrecargar la pantalla;
- Configuración con portada propia;
- Usuarios y Roles y permisos como destinos independientes;
- Mi cuenta separado de la administración de usuarios;
- navegación parcial HTMX;
- assets críticos locales;
- tests y GitHub Actions.

La Tarea 9.3.5 quedó integrada en `main` y validada por GitHub Actions.

## Decisión de continuidad

Se decidió **dejar Roles y Permisos por ahora**.

`9.4 — Validación integral de permisos` sigue pendiente, pero **no bloquea el avance funcional del ERP**.

También se decidió **postergar Auditoría**. No se construirá un motor transversal de auditoría antes de tener operaciones reales de negocio que permitan definir con evidencia qué debe registrarse.

Próximo foco:

```text
Configuración de empresa
↓
Clientes
↓
Proveedores
↓
Productos
↓
Depósitos / Stock
↓
Ventas
```

## Criterio para decidir qué construir

Antes de agregar infraestructura o una capa transversal, responder:

1. ¿Hay una necesidad real hoy?
2. ¿Esto desbloquea la próxima operación real?
3. ¿Tenemos suficiente información para diseñarlo bien?
4. ¿Podemos postergarlo sin romper lo existente?
5. ¿Estamos construyendo producto real o infraestructura imaginaria?

Regla práctica:

```text
Necesidad concreta
↓
Dependencias mínimas
↓
Funcionalidad real
↓
Uso real
↓
Generalizar cuando aparezca un patrón
```

No diseñar una capa transversal importante hasta tener casos reales que la justifiquen.

## Referencia funcional externa: Holistor

Referencia permanente:

https://holistor.atlassian.net/wiki/spaces/TDADGC/overview?homepageId=566427761

Se usa como **mapa funcional de un ERP argentino maduro**, no como especificación a copiar.

Sirve para:

- descubrir entidades y dependencias reales;
- revisar cómo se separan Ventas, Compras, Stock, Tesorería, Impuestos, Contabilidad y Administración;
- detectar maestros y parámetros que podrían ser necesarios más adelante;
- contrastar nuestros circuitos antes de inventarlos desde cero.

No sirve para:

- copiar su interfaz;
- implementar ahora todos sus parámetros;
- crear maestros o configuraciones “por las dudas”;
- trasladar su complejidad histórica a NERISOFT.

La documentación de Holistor muestra, entre otros, que Administración contempla Empresa, Puntos de Venta, Talonarios, Tipos de Comprobante, Monedas, Condiciones Fiscales, Tipos de Documento, Provincias, Localidades, Alícuotas, Tipos de Cobro/Pago, Conceptos y parámetros. En NERISOFT esas piezas se incorporarán **solo cuando un circuito real las necesite**.

## Próximo bloque: Configuración de empresa

El alcance mínimo ya está aprobado.

Primera etapa:

- una sola empresa por instalación;
- Razón social obligatoria;
- Nombre comercial opcional;
- CUIT obligatorio, normalizado y validado;
- Condición fiscal obligatoria;
- Domicilio fiscal obligatorio;
- Localidad obligatoria;
- Provincia obligatoria;
- Código postal opcional;
- Teléfono opcional;
- Email opcional.

No crear todavía maestros separados para localidad, provincia, moneda o condición fiscal. La moneda principal queda fuera de esta primera versión hasta que un circuito monetario real la necesite.

También quedan fuera por ahora IIBB, inicio de actividades, logo, ARCA, CAE, certificados, puntos de venta, talonarios, retenciones, percepciones, SMTP y configuración contable.

Tarea 10.1 completada:

- modelo `Company`;
- tabla `companies` singleton;
- migración `0004_company`;
- permiso `system.company.manage`;
- test de consistencia entre catálogo de permisos y base migrada.

Próxima tarea:

```text
10.2 — Backend + validaciones de Empresa
```

## Modelo mental de acceso

```text
Usuario = cuenta/persona que ingresa al sistema
Rol = conjunto reutilizable de permisos
Permiso = acción concreta habilitada por un rol
Administrador del sistema = acceso total; no es un rol y no depende de roles
```

Flujo normal:

```text
Crear rol → elegir permisos → crear usuario → asignar rol(es) → obtener acceso
```

Nunca mostrar `Administrador del sistema` dentro de una columna o concepto llamado `Roles`.

### Alcance actual del catálogo

Hoy los permisos implementados pertenecen solamente al área **Sistema**:

```text
Sistema
├── Usuarios
└── Roles y permisos
```

No se crean permisos ficticios de Ventas, Compras, Stock, Tesorería u otros módulos antes de que exista su funcionalidad.

Regla de crecimiento:

```text
Cada módulo nuevo define, aplica y prueba sus propios permisos junto con su funcionalidad.
```

## Navegación de Configuración

```text
Configuración
└── Accesos y seguridad
    ├── Usuarios
    └── Roles y permisos
```

`Mi cuenta` es información de la sesión actual y se accede desde el usuario de la barra superior. No forma parte de Gestión de Usuarios.

## Reglas de trabajo

```text
1 tarea → rama → validación → PR → squash merge → main → GitHub Actions → pull local → prueba → siguiente
```

Durante validación local: una sola acción o comando por paso.

No tapar síntomas con CSS/JavaScript ni sumar workarounds innecesarios. Corregir la causa en la capa responsable y retirar cualquier solución temporal previa.

## Reglas UI que no se negocian

- Interfaz sobria, densa y orientada a productividad.
- No agregar niveles de navegación sin necesidad.
- No sobrecargar pantallas con información secundaria.
- Las tablas deben servir para identificar, comparar y actuar rápidamente.
- Mostrar en tablas solo columnas y metadatos necesarios para esa decisión.
- Evitar repetir tipo, estado, roles, permisos, badges o descripciones si no aportan una acción o comparación real.
- El detalle secundario pertenece a la ficha/vista del registro, no a la grilla.
- Mantener patrones reutilizables entre módulos.
- Desktop-first; no diseñar como una interfaz móvil ampliada.

## Stack

```text
Python / FastAPI / SQLAlchemy 2 / SQLite / Alembic
Jinja2 / HTMX / Vanilla JS / CSS propio
Geist / Tabler Icons / Uvicorn / Argon2 / pytest
```

SQLite vive solo en el servidor. Los clientes acceden por HTTP/HTTPS; nunca abren directamente el archivo `.db`.

## Comandos habituales

Desde `D:\NeriSoft`.

Actualizar código:

```powershell
git pull origin main
```

Levantar la aplicación sin depender de la activación de PowerShell:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Aplicar migraciones:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

Tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Base local habitual:

```text
D:\NeriSoft\data\nerisoft.db
```

## Dónde leer más

- Inicio del próximo hilo: [`HANDOFF-ACTUAL.md`](HANDOFF-ACTUAL.md)
- Arquitectura: [`01-arquitectura.md`](01-arquitectura.md)
- Diseño UI: [`02-diseno-ui.md`](02-diseno-ui.md)
- Datos y reglas: [`03-datos-y-reglas.md`](03-datos-y-reglas.md)
- Roadmap: [`04-roadmap.md`](04-roadmap.md)
- Flujo de trabajo: [`05-flujo-trabajo.md`](05-flujo-trabajo.md)
- Contexto consolidado: [`12-resumen-y-contexto.md`](12-resumen-y-contexto.md)

Regla práctica: para un hilo nuevo, empezar por `HANDOFF-ACTUAL.md`; después usar este archivo y abrir documentación específica solo cuando haga falta.
