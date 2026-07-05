# Escritorio Gamer Demo — generado automáticamente por MUEBLES-MELAMINA
# Mueble: 1600 × 700 × 750 mm (ancho × prof. × alto)
#
# CÓMO USAR (detalle en el README del proyecto):
#   1. Abrí SketchUp con un modelo nuevo (plantilla en milímetros).
#   2. Ventana → Consola Ruby.
#   3. Escribí:  load "RUTA/COMPLETA/a/este/archivo.rb"   y Enter.
#   4. Para la lista de cortes: Extensiones → OpenCutList → Cortes.
#
# Cada pieza es un componente con material asignado: OpenCutList los lee tal cual.

PIEZAS = [
  { nombre: "Tapa capa inferior (oculta)", pos: [0, 0, 714], dim: [1600, 700, 18], material: "Aglomerado crudo 18mm", color: [198, 180, 150] },
  { nombre: "Tapa capa superior (visible)", pos: [0, 0, 732], dim: [1600, 700, 18], material: "Melamina 18mm Negro", color: [45, 45, 48] },
  { nombre: "Lateral izquierdo (pata panel)", pos: [0, 50, 0], dim: [18, 650, 714], material: "Melamina 18mm Negro", color: [45, 45, 48] },
  { nombre: "Parante soporte CPU", pos: [268, 50, 0], dim: [18, 650, 714], material: "Melamina 18mm Negro", color: [45, 45, 48] },
  { nombre: "Bandeja CPU", pos: [18, 50, 100], dim: [250, 650, 18], material: "Melamina 18mm Negro", color: [45, 45, 48] },
  { nombre: "Lateral cajonera interno", pos: [1200, 50, 0], dim: [18, 600, 714], material: "Melamina 18mm Negro", color: [45, 45, 48] },
  { nombre: "Lateral cajonera externo", pos: [1582, 50, 0], dim: [18, 600, 714], material: "Melamina 18mm Negro", color: [45, 45, 48] },
  { nombre: "Piso cajonera", pos: [1218, 50, 0], dim: [364, 600, 18], material: "Melamina 18mm Negro", color: [45, 45, 48] },
  { nombre: "Fondo cajonera", pos: [1202, 650, 2], dim: [396, 3, 710], material: "Fibrofácil 3mm", color: [170, 140, 105] },
  { nombre: "Frente cajón 1", pos: [1202, 32, 18], dim: [396, 18, 229], material: "Melamina 18mm Negro", color: [45, 45, 48] },
  { nombre: "Lateral caja cajón 1 (izq)", pos: [1231, 50, 33], dim: [18, 550, 199], material: "Melamina 18mm Negro", color: [45, 45, 48] },
  { nombre: "Lateral caja cajón 1 (der)", pos: [1551, 50, 33], dim: [18, 550, 199], material: "Melamina 18mm Negro", color: [45, 45, 48] },
  { nombre: "Frente interno cajón 1", pos: [1249, 50, 33], dim: [302, 18, 199], material: "Melamina 18mm Negro", color: [45, 45, 48] },
  { nombre: "Contrafrente cajón 1", pos: [1249, 582, 33], dim: [302, 18, 199], material: "Melamina 18mm Negro", color: [45, 45, 48] },
  { nombre: "Fondo cajón 1", pos: [1232, 51, 30], dim: [336, 548, 3], material: "Fibrofácil 3mm", color: [170, 140, 105] },
  { nombre: "Frente cajón 2", pos: [1202, 32, 250], dim: [396, 18, 229], material: "Melamina 18mm Negro", color: [45, 45, 48] },
  { nombre: "Lateral caja cajón 2 (izq)", pos: [1231, 50, 265], dim: [18, 550, 199], material: "Melamina 18mm Negro", color: [45, 45, 48] },
  { nombre: "Lateral caja cajón 2 (der)", pos: [1551, 50, 265], dim: [18, 550, 199], material: "Melamina 18mm Negro", color: [45, 45, 48] },
  { nombre: "Frente interno cajón 2", pos: [1249, 50, 265], dim: [302, 18, 199], material: "Melamina 18mm Negro", color: [45, 45, 48] },
  { nombre: "Contrafrente cajón 2", pos: [1249, 582, 265], dim: [302, 18, 199], material: "Melamina 18mm Negro", color: [45, 45, 48] },
  { nombre: "Fondo cajón 2", pos: [1232, 51, 262], dim: [336, 548, 3], material: "Fibrofácil 3mm", color: [170, 140, 105] },
  { nombre: "Frente cajón 3", pos: [1202, 32, 482], dim: [396, 18, 229], material: "Melamina 18mm Negro", color: [45, 45, 48] },
  { nombre: "Lateral caja cajón 3 (izq)", pos: [1231, 50, 497], dim: [18, 550, 199], material: "Melamina 18mm Negro", color: [45, 45, 48] },
  { nombre: "Lateral caja cajón 3 (der)", pos: [1551, 50, 497], dim: [18, 550, 199], material: "Melamina 18mm Negro", color: [45, 45, 48] },
  { nombre: "Frente interno cajón 3", pos: [1249, 50, 497], dim: [302, 18, 199], material: "Melamina 18mm Negro", color: [45, 45, 48] },
  { nombre: "Contrafrente cajón 3", pos: [1249, 582, 497], dim: [302, 18, 199], material: "Melamina 18mm Negro", color: [45, 45, 48] },
  { nombre: "Fondo cajón 3", pos: [1232, 51, 494], dim: [336, 548, 3], material: "Fibrofácil 3mm", color: [170, 140, 105] },
]

PASACABLES = [
  { x: 590, y: 640, z: 750, d: 60 },
  { x: 894, y: 640, z: 750, d: 60 },
]

model = Sketchup.active_model
model.start_operation("Escritorio Gamer Demo", true)

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
puts "✔ Escritorio Gamer Demo: #{PIEZAS.length} piezas dibujadas. " \
     "Abrí OpenCutList (Extensiones) para la lista de cortes."
