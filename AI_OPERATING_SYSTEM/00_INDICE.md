# 00 — ÍNDICE DEL SISTEMA OPERATIVO DE CONOCIMIENTO

> **Para la IA que lee esto:** este directorio es tu memoria permanente. Antes de responder
> cualquier consulta sobre este proyecto, ubicá el documento relevante en esta tabla y leelo.
> Nunca respondas desde conocimiento genérico si existe un documento que cubre el tema.

## Qué es este proyecto (en una frase)

Software que convierte un pedido en lenguaje natural ("quiero un escritorio gamer") en:
modelo 3D en SketchUp + posiciones de tornillos y herrajes + lista de cortes optimizada
(OpenCutList) + lista de compras + presupuesto. La IA genera **recetas JSON**; un motor
determinista en Python hace todo lo demás.

## Documentos

| Nº | Archivo | Contenido | Consultar cuando… |
|----|---------|-----------|-------------------|
| 01 | [01_IDENTIDAD_Y_VISION.md](01_IDENTIDAD_Y_VISION.md) | Qué construimos, por qué, rol de cada IA, quién es el usuario | dudes del propósito o del rol que te toca |
| 02 | [02_ARQUITECTURA.md](02_ARQUITECTURA.md) | Flujo completo del sistema, el JSON como contrato, límites de cada módulo | vayas a tocar código o proponer cambios estructurales |
| 03 | [03_STACK_TECNOLOGICO.md](03_STACK_TECNOLOGICO.md) | Python, SketchUp + Ruby, OpenCutList, LM Studio, Git — y por qué cada uno | alguien proponga agregar/cambiar una herramienta |
| 04 | [04_ESQUEMA_RECETA_JSON.md](04_ESQUEMA_RECETA_JSON.md) | Especificación completa del formato de receta (el contrato central) | generes o valides una receta |
| 05 | [05_REGLAS_DE_CARPINTERIA.md](05_REGLAS_DE_CARPINTERIA.md) | Melamina, espesores, holguras, uniones, cantos, tornillería | calcules piezas, valides medidas o dudes de una regla física |
| 06 | [06_MEDIDAS_ESTANDAR.md](06_MEDIDAS_ESTANDAR.md) | Ergonomía, medidas por defecto, formatos de placa comerciales | propongas dimensiones por defecto o valides límites |
| 07 | [07_HERRAJES_Y_TORNILLERIA.md](07_HERRAJES_Y_TORNILLERIA.md) | Correderas, tornillos, tarugos, pasacables: cuál, cuándo, cuántos | armes la lista de compras o posiciones de perforado |
| 08 | [08_REGLAS_PARA_IAS.md](08_REGLAS_PARA_IAS.md) | System prompt y protocolo para LM Studio / ChatGPT / Claude | configures un modelo o depures una receta mal generada |
| 09 | [09_DECISIONES_TECNICAS.md](09_DECISIONES_TECNICAS.md) | Registro de decisiones (ADR): qué se decidió, por qué, qué se descartó | quieras cambiar algo ya decidido — leé primero si ya se discutió |
| 10 | [10_HOJA_DE_RUTA.md](10_HOJA_DE_RUTA.md) | Fases futuras: más muebles, UI, planos 2D, CNC, docs pendientes | planifiques trabajo nuevo |
| 11 | [11_REGLAS_Y_MEDIDAS_ROPERO.md](11_REGLAS_Y_MEDIDAS_ROPERO.md) | Reglas y medidas propias del ropero/placard (barral, puertas, zócalo) | calcules o valides un ropero |

## Reglas de mantenimiento de esta memoria

1. **Toda decisión nueva se registra en 09** antes de implementarse. Sin excepción.
2. **Ningún documento contradice a otro.** Si detectás una contradicción, es un bug de la
   memoria: señalalo y proponé la corrección, no elijas silenciosamente una versión.
3. Los documentos se **actualizan junto con el código** en el mismo commit cuando una regla cambia.
4. Documentos futuros (materiales ampliados, más tipos de muebles, glosario, bitácora, etc.)
   se agregan con numeración correlativa (11, 12, …) y se registran en esta tabla.
5. El idioma de toda la documentación y los mensajes al usuario es **español**. El código usa
   nombres en español para el dominio de carpintería (pieza, despiece, tapacanto) porque el
   usuario es carpintero hispanohablante y debe poder leerlo.
