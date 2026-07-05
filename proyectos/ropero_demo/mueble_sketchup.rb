# Ropero Demo — generado automáticamente por MUEBLES-MELAMINA
# Mueble: 900 × 580 × 2400 mm (ancho × prof. × alto)
#
# CÓMO USAR (detalle en el README del proyecto):
#   1. Abrí SketchUp con un modelo nuevo (plantilla en milímetros).
#   2. Ventana → Consola Ruby.
#   3. Escribí:  load "RUTA/COMPLETA/a/este/archivo.rb"   y Enter.
#   4. Para la lista de cortes: Extensiones → OpenCutList → Cortes.
#
# Cada pieza es un componente con material asignado: OpenCutList los lee tal cual.

PIEZAS = [
  { nombre: "Lateral izquierdo", pos: [0, 0, 100], dim: [18, 580, 2300], material: "Melamina 18mm Blanco", color: [245, 245, 240] },
  { nombre: "Lateral derecho", pos: [882, 0, 100], dim: [18, 580, 2300], material: "Melamina 18mm Blanco", color: [245, 245, 240] },
  { nombre: "Piso", pos: [18, 0, 100], dim: [864, 580, 18], material: "Melamina 18mm Blanco", color: [245, 245, 240] },
  { nombre: "Techo (estante superior)", pos: [18, 0, 2382], dim: [864, 580, 18], material: "Melamina 18mm Blanco", color: [245, 245, 240] },
  { nombre: "Fondo", pos: [2, 577, 102], dim: [896, 3, 2296], material: "Fibrofácil 3mm", color: [170, 140, 105] },
  { nombre: "Zócalo frontal", pos: [18, 30, 0], dim: [864, 18, 100], material: "Melamina 18mm Blanco", color: [245, 245, 240] },
  { nombre: "Divisor cajones", pos: [500, 0, 118], dim: [18, 580, 2264], material: "Melamina 18mm Blanco", color: [245, 245, 240] },
  { nombre: "Tapa de cajonera", pos: [518, 0, 880], dim: [364, 580, 18], material: "Melamina 18mm Blanco", color: [245, 245, 240] },
  { nombre: "Frente cajón 1", pos: [502, 0, 118], dim: [396, 18, 250], material: "Melamina 18mm Blanco", color: [245, 245, 240] },
  { nombre: "Lateral caja cajón 1 (izq)", pos: [531, 0, 133], dim: [18, 500, 220], material: "Melamina 18mm Blanco", color: [245, 245, 240] },
  { nombre: "Lateral caja cajón 1 (der)", pos: [851, 0, 133], dim: [18, 500, 220], material: "Melamina 18mm Blanco", color: [245, 245, 240] },
  { nombre: "Frente interno cajón 1", pos: [549, 0, 133], dim: [302, 18, 220], material: "Melamina 18mm Blanco", color: [245, 245, 240] },
  { nombre: "Contrafrente cajón 1", pos: [549, 482, 133], dim: [302, 18, 220], material: "Melamina 18mm Blanco", color: [245, 245, 240] },
  { nombre: "Fondo cajón 1", pos: [532, 1, 130], dim: [336, 498, 3], material: "Fibrofácil 3mm", color: [170, 140, 105] },
  { nombre: "Frente cajón 2", pos: [502, 0, 371], dim: [396, 18, 250], material: "Melamina 18mm Blanco", color: [245, 245, 240] },
  { nombre: "Lateral caja cajón 2 (izq)", pos: [531, 0, 386], dim: [18, 500, 220], material: "Melamina 18mm Blanco", color: [245, 245, 240] },
  { nombre: "Lateral caja cajón 2 (der)", pos: [851, 0, 386], dim: [18, 500, 220], material: "Melamina 18mm Blanco", color: [245, 245, 240] },
  { nombre: "Frente interno cajón 2", pos: [549, 0, 386], dim: [302, 18, 220], material: "Melamina 18mm Blanco", color: [245, 245, 240] },
  { nombre: "Contrafrente cajón 2", pos: [549, 482, 386], dim: [302, 18, 220], material: "Melamina 18mm Blanco", color: [245, 245, 240] },
  { nombre: "Fondo cajón 2", pos: [532, 1, 383], dim: [336, 498, 3], material: "Fibrofácil 3mm", color: [170, 140, 105] },
  { nombre: "Frente cajón 3", pos: [502, 0, 624], dim: [396, 18, 250], material: "Melamina 18mm Blanco", color: [245, 245, 240] },
  { nombre: "Lateral caja cajón 3 (izq)", pos: [531, 0, 639], dim: [18, 500, 220], material: "Melamina 18mm Blanco", color: [245, 245, 240] },
  { nombre: "Lateral caja cajón 3 (der)", pos: [851, 0, 639], dim: [18, 500, 220], material: "Melamina 18mm Blanco", color: [245, 245, 240] },
  { nombre: "Frente interno cajón 3", pos: [549, 0, 639], dim: [302, 18, 220], material: "Melamina 18mm Blanco", color: [245, 245, 240] },
  { nombre: "Contrafrente cajón 3", pos: [549, 482, 639], dim: [302, 18, 220], material: "Melamina 18mm Blanco", color: [245, 245, 240] },
  { nombre: "Fondo cajón 3", pos: [532, 1, 636], dim: [336, 498, 3], material: "Fibrofácil 3mm", color: [170, 140, 105] },
  { nombre: "Barral colgador", pos: [68, 278, 1750], dim: [364, 25, 25], material: "Tubo cromado", color: [190, 195, 200] },
  { nombre: "Puerta batiente 1", pos: [21, -18, 103], dim: [427, 18, 2294], material: "Melamina 18mm Blanco", color: [245, 245, 240] },
  { nombre: "Puerta batiente 2", pos: [451, -18, 103], dim: [427, 18, 2294], material: "Melamina 18mm Blanco", color: [245, 245, 240] },
]

PASACABLES = [

]

model = Sketchup.active_model
model.start_operation("Ropero Demo", true)

materiales = {}

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
    grp.name = "PERFORACIÓN pasacables Ø#{pf[:d]}"
  end
end

model.commit_operation
Sketchup.active_model.active_view.zoom_extents
puts "✔ Ropero Demo: #{PIEZAS.length} piezas dibujadas. " \
     "Abrí OpenCutList (Extensiones) para la lista de cortes."
