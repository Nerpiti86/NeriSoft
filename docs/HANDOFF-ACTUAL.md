# HANDOFF ACTUAL — LEER PRIMERO EN EL PRÓXIMO HILO

Fecha de cierre: 22/09/2026

## Objetivo del próximo hilo

**Ejecutar Tarea 10.3 — UI de Configuración de empresa + integración en Configuración + prueba funcional.**

El backend de Empresa ya está implementado. No rediseñarlo salvo que aparezca un problema concreto durante la integración visual.

No continuar con Roles y Permisos salvo problema concreto.

No empezar Auditoría.

## Estado exacto al cerrar

Repositorio:

```text
Nerpiti86/NeriSoft
rama estable: main
local habitual: D:\NeriSoft
```

Última tarea completada:

```text
Tarea 10.2 — Backend + validaciones de Empresa ✅
```

También completadas:

```text
Tarea 10.0 — Normalización documental ✅
Tarea 10.1 — Modelo + migración + permiso de Empresa ✅
```

`9.4 — Validación integral de permisos` sigue pendiente, pero no bloquea Empresa.

## Empresa — alcance vigente

Primera etapa:

```text
una sola empresa por instalación
sin listado de empresas
sin ABM multiempresa
acceso directo desde Configuración
```

Campos:

```text
Razón social        obligatoria
Nombre comercial    opcional
CUIT                 obligatorio
Condición fiscal    obligatoria
Domicilio fiscal    obligatorio
Localidad            obligatoria
Provincia            obligatoria
Código postal        opcional
Teléfono             opcional
Email                opcional
```

Fuera de alcance:

```text
moneda principal
IIBB
inicio de actividades
logo
ARCA / CAE
certificados
puntos de venta
talonarios
retenciones / percepciones
SMTP
contabilidad
maestros separados de Localidad / Provincia / Condición fiscal
multiempresa
```

## Qué quedó implementado en 10.1

Modelo:

```text
app/models/company.py
Company
companies
```

La tabla es singleton mediante:

```text
CHECK (id = 1)
```

Migración:

```text
0004_company
↓
0003_roles_permissions
```

Permiso:

```text
system.company.manage
```

Catálogo actual:

```text
Sistema
├── Usuarios
├── Roles y permisos
└── Empresa
```

Las migraciones históricas no se modifican. El catálogo vigente y la base migrada se comparan mediante tests; no existe sincronizador automático.

## Qué quedó implementado en 10.2

### Ruta

```text
GET  /configuracion/empresa
POST /configuracion/empresa
```

La ruta no está todavía enlazada desde la portada de Configuración. Eso corresponde a 10.3.

### Acceso

Ambas operaciones requieren:

```text
system.company.manage
```

El Administrador del sistema mantiene bypass total.

### Persistencia

Comportamiento:

```text
si companies.id=1 no existe → crear
si companies.id=1 existe    → actualizar
```

Nunca se crea una segunda empresa.

### CSRF

El POST exige token CSRF válido usando el mecanismo existente del proyecto.

### CUIT

El backend:

- elimina espacios y guiones;
- almacena 11 dígitos;
- valida longitud;
- valida que sean dígitos;
- valida dígito verificador mediante checksum.

### Condición fiscal

Se usa una lista controlada dentro del módulo, sin maestro independiente:

```text
IVA RESPONSABLE INSCRITO
IVA EXENTO
NO RESPONSABLE IVA
RESPONSABLE MONOTRIBUTO
MONOTRIBUTO TRABAJADOR INDEPENDIENTE PROMOVIDO
MONOTRIBUTISTA SOCIAL
```

La selección se basó en las leyendas vigentes para el **emisor** contempladas por ARCA en la RG 1415, Anexo II, texto vigente según RG 5866/2026.

No se incorporaron categorías de receptor como Consumidor Final, Cliente del Exterior o Proveedor del Exterior.

Cuando se llegue al módulo fiscal/electrónico deberá revisarse nuevamente la normativa vigente.

### Validaciones

Se validan:

- razón social obligatoria y hasta 160 caracteres;
- nombre comercial opcional y hasta 160;
- CUIT válido;
- condición fiscal perteneciente al conjunto permitido;
- domicilio fiscal obligatorio y hasta 255;
- localidad obligatoria y hasta 120;
- provincia obligatoria y hasta 120;
- código postal opcional y hasta 20;
- teléfono opcional y hasta 50;
- email opcional, formato válido y hasta 254.

Los valores de texto se limpian antes de guardar; el email se normaliza a minúsculas.

### Errores

- validaciones / CSRF → formulario con errores y HTTP 422;
- conflicto de persistencia → HTTP 409;
- éxito → redirect 303 a `/configuracion/empresa?notice=saved`.

### Template actual

Existe:

```text
app/templates/company.html
```

Es un formulario funcional mínimo para sostener el backend. **No es la UI final aprobada.**

No agregar ahora otro formulario paralelo ni otra ruta.

## Tests agregados en 10.2

Cubren:

- normalización de campos;
- checksum de CUIT;
- rechazo de CUIT inválido;
- rechazo de condición fiscal no permitida;
- validación de obligatorios y email;
- bloqueo de acceso sin permiso;
- acceso con permiso delegado;
- bypass de superusuario;
- creación de empresa;
- actualización de la misma empresa;
- conservación de un único registro;
- rechazo de escritura con datos/CSRF inválidos.

## Tarea 10.3 — alcance exacto

Trabajar sobre el backend existente.

Debe implementar:

- sección **Empresa** en la portada de Configuración;
- tarjeta **Datos de la empresa** visible solo con `system.company.manage`;
- formulario visual definitivo para `/configuracion/empresa`;
- organización en:
  - Datos generales;
  - Domicilio fiscal;
  - Contacto;
- mensajes de errores integrados al diseño;
- aviso de guardado correcto;
- consistencia con shell, Geist, Tabler y sistema visual existente;
- comportamiento HTMX/HTML normal coherente con el proyecto;
- prueba local visual y funcional.

No agregar:

- tabs innecesarios;
- listado de empresas;
- botón “Nueva empresa”;
- código de empresa;
- moneda principal;
- maestros auxiliares;
- campos fiscales futuros;
- Auditoría.

## Regla UI

Desktop-first, sobria, densa y orientada a productividad.

```text
Configuración
├── Empresa
│   └── Datos de la empresa
└── Accesos y seguridad
    ├── Usuarios
    └── Roles y permisos
```

## Auditoría

Sigue postergada.

No crear todavía motor genérico de auditoría, event bus, snapshots universales ni historial transversal.

## Holistor

Referencia funcional permanente:

https://holistor.atlassian.net/wiki/spaces/TDADGC/overview?homepageId=566427761

Usarla para descubrir dependencias y casos reales, no para copiar UI ni toda su complejidad.

## Secuencia actual

```text
10.0 Documentación ✅
↓
10.1 Modelo + migración + permiso ✅
↓
10.2 Backend + validaciones ✅
↓
10.3 UI + prueba funcional
↓
Clientes
```

## Forma de trabajo

```text
1 tarea
→ revisar main
→ crear rama
→ implementar
→ validar
→ PR
→ squash merge a main
→ GitHub Actions
→ git pull local
→ prueba visual/funcional
→ siguiente
```

Durante pruebas locales: **una sola acción o comando por mensaje**.

## Primera instrucción sugerida para el próximo hilo

```text
Leé primero docs/HANDOFF-ACTUAL.md y docs/00-lectura-rapida.md.
Después revisá main y ejecutemos únicamente la Tarea 10.3:
integrar Empresa en Configuración, diseñar el formulario final sobre /configuracion/empresa y validar visual/funcionalmente.
No agregar campos ni maestros fuera del alcance aprobado.
```
