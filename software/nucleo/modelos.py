"""Estructuras de datos compartidas del sistema.

Frontera de módulo (ver AI_OPERATING_SYSTEM/02_ARQUITECTURA.md): este archivo
NO contiene lógica de ningún mueble concreto, solo las clases que todos usan.

Convenciones:
- Todas las medidas en milímetros, enteros.
- Sistema de coordenadas: x = ancho (izquierda→derecha), y = profundidad
  (frente→fondo), z = alto (piso→arriba). El origen (0,0,0) es la esquina
  inferior izquierda delantera del mueble.
"""

from dataclasses import dataclass, field


@dataclass
class Pieza:
    """Una pieza de placa a cortar, con su posición en el mueble armado.

    largo/ancho son las medidas de CORTE (las dos caras grandes de la placa);
    espesor es el grosor de la placa. La caja (pos + dim) ubica la pieza en 3D
    para el generador de SketchUp.
    """

    nombre: str            # ej. "Lateral cajonera izquierdo"
    largo: int             # medida de corte mayor
    ancho: int             # medida de corte menor
    espesor: int           # 18, 25 o 3
    material: str          # ej. "Melamina 18mm Negro" (lo lee OpenCutList)
    pos: tuple             # (x, y, z) esquina de origen de la caja en el mueble
    dim: tuple             # (dx, dy, dz) tamaño de la caja en cada eje
    cantos: str = ""       # qué cantos llevan tapacanto, ej. "1 largo visible"
    notas: str = ""

    def __post_init__(self):
        # El corte siempre se informa largo >= ancho.
        if self.ancho > self.largo:
            self.largo, self.ancho = self.ancho, self.largo


@dataclass
class Herraje:
    """Un ítem de la lista de compras de herrajes/fijaciones."""

    codigo: str            # H-xx de 07_HERRAJES_Y_TORNILLERIA.md
    nombre: str            # ej. "Tornillo confirmat 7×50"
    cantidad: float        # unidades (o metros para tapacanto)
    unidad: str            # "unidades", "pares", "metros"
    para_que: str          # explicación para el usuario


@dataclass
class Perforacion:
    """Una perforación que el usuario debe hacer (o marcar) en una pieza.

    x, y se miden desde la esquina inferior-izquierda de la CARA indicada de
    la pieza, con la pieza apoyada como se corta (largo horizontal).
    """

    pieza: str             # nombre de la Pieza
    cara: str              # "cara", "canto frontal", "canto superior", etc.
    x: int
    y: int
    diametro: float        # mm de broca
    profundidad: str       # "pasante" o mm
    para_que: str          # ej. "confirmat piso cajonera (P-01)"


@dataclass
class Mueble:
    """Resultado completo del motor de despiece: todo lo que los generadores
    de salida necesitan, ya calculado. Los generadores NO recalculan nada."""

    nombre: str
    receta: dict                      # receta normalizada (con defectos aplicados)
    piezas: list = field(default_factory=list)        # [Pieza]
    herrajes: list = field(default_factory=list)      # [Herraje]
    perforaciones: list = field(default_factory=list)  # [Perforacion]
    avisos: list = field(default_factory=list)        # strings para el usuario

    def dimensiones_texto(self):
        d = self.receta["dimensiones"]
        return f"{d['ancho']} × {d['profundidad']} × {d['alto']} mm (ancho × prof. × alto)"
