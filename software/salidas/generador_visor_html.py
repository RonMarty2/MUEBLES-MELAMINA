"""Genera un visor 3D del mueble en un archivo HTML único.

Alternativa 100% GRATUITA a SketchUp (Decisión D-009): el usuario abre el
archivo con doble clic en cualquier navegador y ve el mueble en 3D — girar
con el mouse, zoom con la rueda, lista de piezas con resaltado al pasar.

La biblioteca three.js (gratis, licencia MIT) viene INCRUSTADA en el archivo
desde salidas/recursos/three.min.js: el visor funciona sin internet, siempre.
"""

import json
from pathlib import Path

from .generador_sketchup import _color_para

RUTA_THREE = Path(__file__).parent / "recursos" / "three.min.js"


def generar_visor_html(mueble, ruta_html):
    piezas = []
    for p in mueble.piezas:
        r, g, b = _color_para(p.material)
        piezas.append({
            "nombre": p.nombre,
            "pos": list(p.pos),
            "dim": list(p.dim),
            "color": [r, g, b],
            "corte": f"{p.largo} × {p.ancho} × {p.espesor} mm",
            "material": p.material,
        })
    perfs = [
        {"x": pf.x, "y": pf.y, "d": pf.diametro}
        for pf in mueble.perforaciones if "pasacables" in pf.para_que
    ]
    d = mueble.receta["dimensiones"]
    datos = json.dumps({
        "nombre": mueble.nombre,
        "dims": [d["ancho"], d["profundidad"], d["alto"]],
        "piezas": piezas,
        "pasacables": perfs,
    }, ensure_ascii=False)

    html = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>__TITULO__ — Visor 3D</title>
<style>
  body { margin: 0; font-family: system-ui, sans-serif; overflow: hidden; }
  #panel { position: fixed; top: 0; left: 0; width: 290px; height: 100vh;
           overflow-y: auto; background: #ffffffee; border-right: 1px solid #ccc;
           padding: 12px; box-sizing: border-box; font-size: 13px; }
  #panel h1 { font-size: 16px; margin: 0 0 4px; }
  #panel .sub { color: #666; margin-bottom: 10px; }
  .pieza { padding: 5px 6px; border-radius: 5px; cursor: pointer; }
  .pieza:hover, .pieza.activa { background: #ffe9a8; }
  .pieza .medida { color: #777; font-size: 12px; }
  #ayuda { position: fixed; bottom: 8px; right: 12px; color: #555;
           background: #ffffffcc; padding: 4px 10px; border-radius: 6px; font-size: 12px; }
  #sin-internet { display: none; position: fixed; inset: 0; background: #fff;
           padding: 40px; font-size: 16px; }
  canvas { display: block; }
</style>
</head>
<body>
<div id="panel">
  <h1 id="titulo"></h1>
  <div class="sub" id="subtitulo"></div>
  <div id="lista"></div>
</div>
<div id="ayuda">Arrastrar: girar · Rueda: zoom · Clic en la lista: resaltar pieza</div>
<div id="sin-internet">
  <h2>No se pudo cargar el motor 3D</h2>
  <p>Regenerá este archivo con el software (falta three.js incrustado).</p>
</div>
<script>__THREE_JS__</script>
<script>
const DATOS = __DATOS__;

if (typeof THREE === "undefined") {
  document.getElementById("sin-internet").style.display = "block";
} else {
  const esc = 0.001; // mm -> metros de escena
  const [A, P, H] = DATOS.dims;
  document.getElementById("titulo").textContent = DATOS.nombre;
  document.getElementById("subtitulo").textContent =
    A + " × " + P + " × " + H + " mm (ancho × prof. × alto)";

  const escena = new THREE.Scene();
  escena.background = new THREE.Color(0xf2f2f0);
  const camara = new THREE.PerspectiveCamera(50, 1, 0.01, 100);
  const render = new THREE.WebGLRenderer({ antialias: true });
  document.body.appendChild(render.domElement);

  escena.add(new THREE.AmbientLight(0xffffff, 0.65));
  const sol = new THREE.DirectionalLight(0xffffff, 0.7);
  sol.position.set(2, 3, 4);
  escena.add(sol);
  const piso = new THREE.Mesh(
    new THREE.PlaneGeometry(8, 8),
    new THREE.MeshLambertMaterial({ color: 0xe0ddd8 }));
  piso.rotation.x = -Math.PI / 2;
  piso.position.y = -0.001;
  escena.add(piso);
  escena.add(new THREE.GridHelper(8, 32, 0xcccccc, 0xe5e5e5));

  // Coordenadas del proyecto: x=ancho, y=prof, z=alto -> three.js: x, z, y
  const centro = new THREE.Vector3(A * esc / 2, H * esc / 2, P * esc / 2);
  const mallas = [];
  const lista = document.getElementById("lista");

  DATOS.piezas.forEach((p, i) => {
    const [dx, dy, dz] = p.dim, [x, y, z] = p.pos;
    const geo = new THREE.BoxGeometry(dx * esc, dz * esc, dy * esc);
    const mat = new THREE.MeshLambertMaterial({
      color: new THREE.Color(p.color[0] / 255, p.color[1] / 255, p.color[2] / 255) });
    const m = new THREE.Mesh(geo, mat);
    m.position.set((x + dx / 2) * esc, (z + dz / 2) * esc, (y + dy / 2) * esc);
    escena.add(m);
    const borde = new THREE.LineSegments(
      new THREE.EdgesGeometry(geo),
      new THREE.LineBasicMaterial({ color: 0x555555 }));
    borde.position.copy(m.position);
    escena.add(borde);
    mallas.push(m);

    const fila = document.createElement("div");
    fila.className = "pieza";
    fila.innerHTML = "<b>" + p.nombre + "</b><div class='medida'>" +
                     p.corte + " · " + p.material + "</div>";
    fila.onclick = () => {
      document.querySelectorAll(".pieza").forEach(e => e.classList.remove("activa"));
      fila.classList.add("activa");
      mallas.forEach(mm => { mm.material.transparent = true; mm.material.opacity = 0.25; });
      m.material.opacity = 1;
    };
    lista.appendChild(fila);
  });
  document.body.ondblclick = () =>
    mallas.forEach(mm => { mm.material.opacity = 1; mm.material.transparent = false; });

  DATOS.pasacables.forEach(pf => {
    const marca = new THREE.Mesh(
      new THREE.CylinderGeometry(pf.d / 2 * esc, pf.d / 2 * esc, 0.006, 24),
      new THREE.MeshLambertMaterial({ color: 0xdc2828 }));
    marca.position.set(pf.x * esc, H * esc + 0.003, pf.y * esc);
    escena.add(marca);
  });

  // Controles de órbita propios (sin más dependencias)
  // Arranque mirando el FRENTE del mueble, levemente desde arriba-derecha
  let rotY = 2.55, rotX = 0.4, dist = Math.max(A, P, H) * esc * 2.2;
  let arrastrando = false, px = 0, py = 0;
  function ubicarCamara() {
    camara.position.set(
      centro.x + dist * Math.sin(rotY) * Math.cos(rotX),
      centro.y + dist * Math.sin(rotX),
      centro.z + dist * Math.cos(rotY) * Math.cos(rotX));
    camara.lookAt(centro);
  }
  render.domElement.addEventListener("mousedown", e => {
    arrastrando = true; px = e.clientX; py = e.clientY; });
  window.addEventListener("mouseup", () => arrastrando = false);
  window.addEventListener("mousemove", e => {
    if (!arrastrando) return;
    rotY -= (e.clientX - px) * 0.008;
    rotX = Math.min(1.5, Math.max(-0.2, rotX + (e.clientY - py) * 0.008));
    px = e.clientX; py = e.clientY; ubicarCamara(); });
  window.addEventListener("wheel", e => {
    dist = Math.min(15, Math.max(0.4, dist * (e.deltaY > 0 ? 1.1 : 0.9)));
    ubicarCamara(); });

  function ajustar() {
    const w = window.innerWidth, h = window.innerHeight;
    render.setSize(w, h);
    camara.aspect = w / h;
    camara.updateProjectionMatrix();
  }
  window.addEventListener("resize", ajustar);
  ajustar(); ubicarCamara();
  (function animar() { requestAnimationFrame(animar); render.render(escena, camara); })();
}
</script>
</body>
</html>
"""
    three_js = RUTA_THREE.read_text(encoding="utf-8")
    html = (html.replace("__TITULO__", mueble.nombre)
                .replace("__THREE_JS__", three_js)
                .replace("__DATOS__", datos))
    with open(ruta_html, "w", encoding="utf-8") as f:
        f.write(html)
    return ruta_html
