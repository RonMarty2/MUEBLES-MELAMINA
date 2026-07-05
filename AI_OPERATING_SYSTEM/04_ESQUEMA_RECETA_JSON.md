# 04 — ESQUEMA DE LA RECETA JSON

## Objetivo de este documento

Especificar el **contrato central** del sistema: el formato de receta que toda IA genera y
que el motor consume. Cualquier cambio aquí impacta todo el sistema, por lo que requiere
una decisión registrada en `09_DECISIONES_TECNICAS.md` y un aumento del campo `version`.

El esquema formal (validable por máquina) vive en `software/recetas/schema_receta.json`.
Este documento es su explicación para humanos e IAs.

## Principios del formato

1. **Todas las medidas en milímetros, números enteros.** Nunca cm, nunca decimales.
2. **La receta describe intención, no piezas.** Dice "cajonera de 400 de ancho con 3
   cajones"; NUNCA dice "cortar lateral de 682×550". Las piezas las calcula el motor.
3. **Todo campo opcional tiene un valor por defecto documentado aquí** y aplicado por el
   motor. Una receta mínima válida puede tener 3 campos.
4. **`version` obligatoria.** Hoy `"1.0"`. El motor rechaza versiones que no conoce.

## Receta completa de referencia (tipo `escritorio_gamer`)

```json
{
  "version": "1.0",
  "tipo_mueble": "escritorio_gamer",
  "nombre": "Escritorio gamer de Ron",
  "dimensiones": {
    "ancho": 1600,
    "profundidad": 700,
    "alto": 750
  },
  "tapa": {
    "tipo": "doble_18"
  },
  "material": {
    "color": "Negro texturado",
    "espesor": 18,
    "espesor_fondo": 3
  },
  "cajonera": {
    "posicion": "derecha",
    "ancho": 400,
    "cantidad_cajones": 3
  },
  "soporte_cpu": {
    "incluir": true,
    "ancho": 250
  },
  "pasacables": {
    "cantidad": 2,
    "diametro": 60
  }
}
```

## Campos, límites y valores por defecto

| Campo | Tipo | Obligatorio | Defecto | Límites (los aplica el validador citando la regla) |
|---|---|---|---|---|
| `version` | string | Sí | — | Debe ser `"1.0"` |
| `tipo_mueble` | string | Sí | — | Hoy solo `"escritorio_gamer"` |
| `nombre` | string | No | `"Mueble sin nombre"` | Libre; se usa en archivos y títulos |
| `dimensiones.ancho` | entero | No | 1600 | 900–2400 (R-15: debe caber en placa) |
| `dimensiones.profundidad` | entero | No | 700 | 500–900; ≥600 recomendado gamer (M-02) |
| `dimensiones.alto` | entero | No | 750 | 700–800 (M-01 ergonomía) |
| `tapa.tipo` | string | No | ver R-04 | `"simple_18"`, `"doble_18"` o `"simple_25"` |
| `material.color` | string | No | `"Blanco"` | Libre (texto para compras y SketchUp) |
| `material.espesor` | entero | No | 18 | 15 o 18 (R-01); estructura del prototipo usa 18 |
| `material.espesor_fondo` | entero | No | 3 | 3 o 5,5 |
| `cajonera.posicion` | string | No | `"derecha"` | `"derecha"`, `"izquierda"`, `"ninguna"` |
| `cajonera.ancho` | entero | No | 400 | 300–600 (R-05: debe permitir cajón útil) |
| `cajonera.cantidad_cajones` | entero | No | 3 | 1–4 (R-06/R-07: alturas de frente resultantes) |
| `soporte_cpu.incluir` | bool | No | true | — |
| `soporte_cpu.ancho` | entero | No | 250 | 200–350 (M-05: gabinetes ATX) |
| `pasacables.cantidad` | entero | No | 2 | 0–4 |
| `pasacables.diametro` | entero | No | 60 | 60 u 80 (medidas comerciales de grommet, H-06) |

**Defecto de `tapa.tipo` (regla R-04):** si el vano libre de la tapa supera 800 mm — que en
un escritorio gamer típico siempre pasa — el defecto es `"doble_18"`. Si el usuario fuerza
`"simple_18"` con vano > 800, el validador rechaza la receta explicando el riesgo de pandeo.

## Qué debe hacer la IA con este esquema

- Generar **solo JSON válido**, sin texto alrededor (el protocolo exacto está en
  `08_REGLAS_PARA_IAS.md`).
- Ante un pedido de ajuste ("hacelo más ancho"), **modificar la receta anterior**, no crear
  una nueva desde cero, y cambiar únicamente los campos afectados.
- Si el usuario pide algo fuera de límites, la IA puede acercarse al límite válido **pero
  debe avisar** en el campo `nombre` NO — los avisos van fuera del JSON, en la conversación.
  La receta emitida siempre respeta los límites.
- Si el usuario pide algo que el esquema no soporta (p. ej. "con puertas corredizas"),
  responder que ese parámetro aún no existe y registrar el pedido como idea para
  `10_HOJA_DE_RUTA.md`. Nunca inventar campos.

## Evolución del esquema

- **Agregar un campo opcional con defecto** → versión menor (1.0 → 1.1). Las recetas viejas
  siguen siendo válidas.
- **Cambiar significado o quitar campos** → versión mayor (2.0) + migrador de recetas viejas.
  Evitarlo salvo necesidad real.
- Nuevos `tipo_mueble` agregan su propia sección de campos sin tocar los existentes
  (procedimiento en `02_ARQUITECTURA.md`).

## Ejemplos

**Receta mínima válida** (el motor completa todo lo demás con defectos):
```json
{ "version": "1.0", "tipo_mueble": "escritorio_gamer" }
```

**Ajuste conversacional.** Usuario: *"sacale el soporte de CPU y hacelo de 1,80"* →
la IA reemite la receta anterior cambiando solo:
```json
"dimensiones": { "ancho": 1800, "profundidad": 700, "alto": 750 },
"soporte_cpu": { "incluir": false }
```

**Receta inválida y su error esperado:**
```json
"cajonera": { "ancho": 250, "cantidad_cajones": 4 }
```
→ `"cajonera.ancho = 250 mm es menor al mínimo de 300 mm (R-05): con correderas no
quedaría cajón útil. Usá 300 mm o más."`

## Documentos relacionados

- Reglas que valida el motor: `05_REGLAS_DE_CARPINTERIA.md`
- Medidas por defecto y su justificación: `06_MEDIDAS_ESTANDAR.md`
- Protocolo de generación por IA: `08_REGLAS_PARA_IAS.md`
- Esquema formal: `software/recetas/schema_receta.json`
