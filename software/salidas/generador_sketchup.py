"""Genera el script Ruby (.rb) que dibuja el mueble en SketchUp.

Frontera de módulo (02_ARQUITECTURA.md): no recalcula nada, solo traduce las
piezas del Mueble a la API Ruby de SketchUp (Decisión D-003).

Cada pieza se crea como COMPONENTE con nombre y material asignado: eso es
exactamente lo que OpenCutList necesita para armar la lista de cortes y el
diagrama de placa (ver README, sección OpenCutList).

Cómo lo usa el usuario (guiado en el README):
  SketchUp → Ventana → Consola Ruby → pegar:  load "C:/ruta/al/archivo.rb"
"""

COLORES = {
    # nombre de color de melamina (en minúsculas) -> RGB para SketchUp
    "blanco": (245, 245, 240),
    "negro": (45, 45, 48),
    "negro texturado": (45, 45, 48),
    "gris": (150, 150, 150),
    "grafito": (90, 90, 95),
    "roble": (190, 155, 100),
    "nogal": (120, 85, 60),
    "cedro": (165, 115, 80),
    "wengue": (75, 55, 45),
}
COLOR_DEFECTO = (200, 190, 170)
COLOR_FONDO = (170, 140, 105)


def _color_para(material):
    m = material.lower()
    if "fibrof" in m:
        return COLOR_FONDO
    for nombre, rgb in COLORES.items():
        if nombre in m:
            return rgb
    return COLOR_DEFECTO


def generar_script_sketchup(mueble, ruta_rb):
    """Escribe el .rb autocontenido y devuelve la ruta."""
    filas = []
    for p in mueble.piezas:
        x, y, z = p.pos
        dx, dy, dz = p.dim
        r, g, b = _color_para(p.material)
        nombre = p.nombre.replace('"', "'")
        material = p.material.replace('"', "'")
        filas.append(
            f'  {{ nombre: "{nombre}", pos: [{x}, {y}, {z}], '
            f"dim: [{dx}, {dy}, {dz}], material: \"{material}\", color: [{r}, {g}, {b}] }},"
        )

    pasacables = []
    for pf in mueble.perforaciones:
        if "pasacables" in pf.para_que:
            d = mueble.receta["dimensiones"]
            pasacables.append(
                f"  {{ x: {pf.x}, y: {pf.y}, z: {d['alto']}, d: {pf.diametro} }},"
            )

    script = f'''# {mueble.nombre} — generado automáticamente por MUEBLES-MELAMINA
# Mueble: {mueble.dimensiones_texto()}
#
# CÓMO USAR (detalle en el README del proyecto):
#   1. Abrí SketchUp con un modelo nuevo (plantilla en milímetros).
#   2. Ventana → Consola Ruby.
#   3. Escribí:  load "RUTA/COMPLETA/a/este/archivo.rb"   y Enter.
#   4. Para la lista de cortes: Extensiones → OpenCutList → Cortes.
#
# Cada pieza es un componente con material asignado: OpenCutList los lee tal cual.

PIEZAS = [
{chr(10).join(filas)}
]

PASACABLES = [
{chr(10).join(pasacables)}
]

model = Sketchup.active_model
model.start_operation("{mueble.nombre.replace('"', "'")}", true)

materiales = {{}}

PIEZAS.each do |pza|
  mat_nombre = pza[:material]
  unless materiales[mat_nombre]
    m = model.materials[mat_nombre] || model.materials.add(mat_nombre)
    m.color = Sketchup::Color.new(*pza[:color])
    materiales[mat_nombre] = m
  end

  defn = model.definitions.add(pza[:nombre])
  dx, dy, dz = pza[:dim]
  cara = defn.entities.add_face(
    [0, 0, 0], [dx.mm, 0, 0], [dx.mm, dy.mm, 0], [0, dy.mm, 0]
  )
  cara.reverse! if cara.normal.z < 0
  cara.pushpull(dz.mm)

  x, y, z = pza[:pos]
  t = Geom::Transformation.new(Geom::Point3d.new(x.mm, y.mm, z.mm))
  inst = model.active_entities.add_instance(defn, t)
  inst.material = materiales[mat_nombre]
end

# Marcadores rojos de pasacables (posición de la broca copa, R-16)
unless PASACABLES.empty?
  rojo = model.materials["Marcador perforación"] || model.materials.add("Marcador perforación")
  rojo.color = Sketchup::Color.new(220, 40, 40)
  PASACABLES.each do |pf|
    grp = model.active_entities.add_group
    centro = Geom::Point3d.new(pf[:x].mm, pf[:y].mm, pf[:z].mm)
    circulo = grp.entities.add_circle(centro, Z_AXIS, (pf[:d] / 2.0).mm)
    cara = grp.entities.add_face(circulo)
    cara.pushpull(3.mm) if cara
    grp.material = rojo
    grp.name = "PERFORACIÓN pasacables Ø#{{pf[:d]}}"
  end
end

model.commit_operation
Sketchup.active_model.active_view.zoom_extents
puts "✔ {mueble.nombre}: #{{PIEZAS.length}} piezas dibujadas. " \\
     "Abrí OpenCutList (Extensiones) para la lista de cortes."
'''

    with open(ruta_rb, "w", encoding="utf-8") as f:
        f.write(script)
    return ruta_rb
