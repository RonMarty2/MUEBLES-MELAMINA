# 10 — HOJA DE RUTA

## Objetivo de este documento

Ordenar la evolución del proyecto en fases, para que cada trabajo nuevo tenga un lugar y
la IA no proponga saltos de fase sin señalarlo. Las ideas sueltas también se anotan acá
(sección Ideas) hasta que maduren a una fase.

## Fase 0 — Prototipo escritorio gamer ✅ (este trabajo)

- Documentación base 00–10 del AI_OPERATING_SYSTEM.
- Receta JSON v1.0 + validador + motor de despiece del escritorio gamer.
- Salidas: script SketchUp (.rb), lista de cortes CSV, compras y presupuesto en Markdown.
- Cliente de IA (LM Studio / OpenAI / Anthropic) opcional al flujo.
- Proyecto demo generado y commiteado como referencia.

**Criterio de éxito:** Ron ejecuta el script en su SketchUp, ve el escritorio en 3D,
obtiene el diagrama de cortes con OpenCutList y una lista de compras utilizable.

## Fase 1 — Endurecer el prototipo con uso real

- Ron diseña SU escritorio real con el sistema y anota todo lo que falte o falle.
- Ajustar defectos y reglas con lo aprendido (cada ajuste = commit de doc + código juntos).
- Sumar plano de perforaciones legible en taller (hoy las posiciones están en el CSV/MD;
  falta un formato "para pegar en la pared del taller").
- Probar 2–3 modelos en LM Studio y registrar en 09 cuál genera mejores recetas.

## Fase 2 — Segundo y tercer tipo de mueble

- Candidatos en orden: **placard/ropero** (cubre bisagras, barral, módulos apilables) y
  **bajo mesada de cocina** (zócalos, bisagras cazoleta 35 mm, patas plásticas).
- Cada tipo sigue el procedimiento de `02_ARQUITECTURA.md` y agrega sus reglas R-xx / M-xx.
- Extraer utilidades comunes que aparezcan repetidas (cajones ya es común).

## Fase 3 — Experiencia de uso

- Interfaz conversacional continua (hoy: comando por comando) — chat en terminal o interfaz
  web mínima local.
- Vista previa 3D en el navegador (Three.js) para iterar sin abrir SketchUp; SketchUp queda
  para el resultado final y OpenCutList.
- Planos 2D acotados por pieza (SVG/PDF) para el taller.

## Fase 4 — Taller y negocio

- Histórico de precios y proveedores → entra SQLite (reabre D-006).
- Gestión de pedidos/clientes; presupuestos con margen de ganancia configurable.
- Exportación CNC (DXF por pieza con perforaciones) si se accede a router CNC.
- Completar el AI_OPERATING_SYSTEM hacia los 40 documentos del plan original (glosario,
  bitácora, checklists de armado, guía de compra de herramientas, etc.) a medida que cada
  documento tenga contenido real que documentar.

## Fase 5 — Plataforma (visión lejana)

- Multiusuario / web / comercial. Recién acá se justifica PostgreSQL, cuentas, pagos.
- Nada del código actual se tira: el contrato JSON y el motor son el núcleo reutilizable.

## Ideas sueltas (aún sin fase)

- Canaleta portacables integrada al mueble (M-15).
- Puertas corredizas y batientes como parámetros de receta.
- Cálculo de tiempo de armado estimado.
- Modo "optimizar precio": la IA propone variantes más baratas del mismo mueble.
- Biblioteca de setups gamer predefinidos (streaming, doble PC, simracing).

**Regla:** una idea se implementa solo cuando se promueve a una fase y se registra la
decisión en `09_DECISIONES_TECNICAS.md`.

## Documentos relacionados

- Procedimiento para agregar muebles: `02_ARQUITECTURA.md`
- Cuándo pagar por herramientas/IA: `03_STACK_TECNOLOGICO.md`
- Decisiones que estas fases reabrirían: `09_DECISIONES_TECNICAS.md` (D-003, D-006)
