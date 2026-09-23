# 05 — Flujo de trabajo Git

## Repositorio oficial

```text
https://github.com/Nerpiti86/NeriSoft
```

## Rama estable

```text
main
```

`main` es la rama estable y debe quedar ejecutable y verificable.

Cada tarea se desarrolla en una rama propia creada desde `main`. Una vez validada, se integra mediante Pull Request con **squash merge**. No se desarrolla trabajo parcial directamente sobre `main`.

## Carpeta local del usuario

```text
D:\NeriSoft
```

## Regla principal

```text
1 tarea
→ revisar main
→ crear rama de tarea
→ implementar
→ validar
→ Pull Request
→ squash merge a main
→ GitHub Actions
→ git pull origin main
→ prueba local
→ siguiente tarea
```

Durante las pruebas locales se avanza con una sola acción o comando por mensaje.

## Reglas de commit y PR

- Una tarea debe producir un cambio coherente.
- No mezclar tareas funcionalmente distintas en el mismo PR.
- La rama de trabajo puede contener los commits intermedios necesarios.
- No mergear trabajo parcial si deja `main` roto.
- El squash merge debe dejar un único commit coherente de la tarea en `main`.
- En tareas exclusivamente documentales, el resultado mergeado debe dejar la documentación vigente consistente.
- Los mensajes finales deben describir claramente la tarea realizada.

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
