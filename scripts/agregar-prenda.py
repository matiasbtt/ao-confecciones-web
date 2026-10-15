#!/usr/bin/env python3
"""Agrega una prenda nueva al catalogo en un solo paso.

Ejemplo:
  python scripts/agregar-prenda.py --numero 16 --nombre "Top Rosa" --categoria Tops \
      --descripcion "Top con mangas cortas. Tejido elastico." --docena 260 --unidad 27 \
      --foto "C:/fotos/top-rosa.jpg" [--inicio]

Que hace: copia la foto a _fuentes/, la optimiza (fondo blanco + 3 tamanos), suma la prenda a
data/prendas.json (y la categoria a data/categorias.json si es nueva) y regenera el sitio.
Despues solo falta revisar con "python -m http.server" y hacer commit.
"""
import argparse, json, os, re, shutil, subprocess, sys, unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable


def slug(texto):
    t = unicodedata.normalize("NFD", texto).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--numero", type=int, required=True, help="numero de pagina en el catalogo (tambien ordena la lista)")
    a.add_argument("--nombre", required=True)
    a.add_argument("--categoria", required=True, help="Tops, Vestidos, Chaquetas, Shorts y faldas o una nueva")
    a.add_argument("--descripcion", required=True)
    a.add_argument("--docena", type=int, required=True, help="precio por docena en Bs")
    a.add_argument("--unidad", type=int, required=True, help="precio por unidad en Bs")
    a.add_argument("--foto", required=True, help="ruta de la foto original (jpg, png o webp)")
    a.add_argument("--inicio", action="store_true", help="mostrarla tambien en la portada")
    a = a.parse_args()
    nn = "%02d" % a.numero

    ruta_datos = os.path.join(RAIZ, "data", "prendas.json")
    prendas = json.load(open(ruta_datos, encoding="utf8"))
    if any(p["numero"] == a.numero for p in prendas):
        sys.exit("Ya existe la prenda %d. Elige otro numero o editala en data/prendas.json." % a.numero)
    if not os.path.exists(a.foto):
        sys.exit("No encuentro la foto: " + a.foto)

    ext = os.path.splitext(a.foto)[1].lower() or ".jpg"
    os.makedirs(os.path.join(RAIZ, "_fuentes"), exist_ok=True)
    shutil.copy(a.foto, os.path.join(RAIZ, "_fuentes", "prenda-%s%s" % (nn, ext)))

    prendas.append({"numero": a.numero, "nombre": a.nombre, "slug": "%s-p%s" % (slug(a.nombre), nn),
                    "categoria": a.categoria, "descripcion": a.descripcion,
                    "precio_docena": a.docena, "precio_unidad": a.unidad, "destacada_en_inicio": a.inicio})
    prendas.sort(key=lambda p: p["numero"])
    json.dump(prendas, open(ruta_datos, "w", encoding="utf8", newline="\n"), ensure_ascii=False, indent=2)
    open(ruta_datos, "a", encoding="utf8", newline="\n").write("\n")

    ruta_cat = os.path.join(RAIZ, "data", "categorias.json")
    cats = json.load(open(ruta_cat, encoding="utf8"))
    if a.categoria not in {c["nombre"] for c in cats}:
        cats.append({"nombre": a.categoria, "slug": slug(a.categoria)})
        json.dump(cats, open(ruta_cat, "w", encoding="utf8", newline="\n"), ensure_ascii=False, indent=2)
        open(ruta_cat, "a", encoding="utf8", newline="\n").write("\n")
        print("Categoria nueva '%s': se creo su pagina y su lugar en el menu." % a.categoria)

    subprocess.check_call([PY, os.path.join(RAIZ, "scripts", "optimizar-fotos.py"), nn])
    subprocess.check_call([PY, os.path.join(RAIZ, "scripts", "build.py")])
    print("\nListo: %s. Revisa en http://localhost:4173/ao-confecciones-web/prendas/%s-p%s/" % (a.nombre, slug(a.nombre), nn))


if __name__ == "__main__":
    main()
