# 05 — Flujo de trabajo Git

## Repositorio oficial

```text
https://github.com/Nerpiti86/NeriSoft
```

## Rama oficial

```text
main
```

Todo el trabajo del proyecto se realiza directamente sobre `main`, salvo decisión explícita posterior.

## Carpeta local del usuario

```text
D:\NeriSoft
```

## Regla principal

```text
1 tarea
→ cambio en GitHub
→ validación
→ commit en main
→ aviso de finalización
→ git pull origin main
→ prueba local
→ siguiente tarea
```

## Reglas de commit

- Una tarea debe producir un cambio coherente.
- No mezclar tareas funcionalmente distintas en el mismo commit.
- No publicar trabajo parcial si deja `main` roto.
- Cada commit debe dejar el proyecto ejecutable o, en tareas exclusivamente documentales, la documentación consistente.
- Los mensajes de commit deben describir claramente la tarea realizada.

Ejemplos:

```text
docs: document initial architecture and roadmap
chore: bootstrap FastAPI application
feat: add collapsible application sidebar
feat: add user authentication
fix: correct stock movement rollback
```

## Pull local

Cuando se indique que una tarea está terminada:

```bash
cd D:\NeriSoft
git pull origin main
```

## Exclusividad

El código y la documentación oficiales de NERISOFT se modifican exclusivamente en este repositorio.

No deben crearse copias alternativas como fuente de verdad para el proyecto.

## Validación antes de publicar

Según el tipo de tarea, antes de actualizar `main` se debe comprobar como mínimo:

- sintaxis válida
- imports correctos
- aplicación arrancable cuando exista bootstrap técnico
- migraciones coherentes cuando existan cambios de modelo
- templates sin referencias rotas
- rutas coherentes
- reglas de negocio relevantes verificadas
- documentación actualizada si cambia una decisión arquitectónica

## Documentación como parte del producto

Toda decisión estructural importante debe quedar documentada en `README.md` o `docs/`.

Si una tarea cambia una decisión ya documentada, la misma tarea debe actualizar la documentación correspondiente.
