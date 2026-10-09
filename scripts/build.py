#!/usr/bin/env python3
"""Genera todo el sitio a partir de data/ + plantillas/ + paginas/.

    python scripts/build.py            escribe los HTML y el sitemap en la raiz del repo
    python scripts/build.py --check    no escribe nada: avisa si algun archivo cambiaria

Fuentes de verdad (esto es lo unico que se edita a mano):
  data/prendas.json      una entrada por prenda (nombre, categoria, precios, descripcion)
  data/categorias.json   categorias con pagina propia, en el orden del menu
  paginas/*.html         paginas sueltas (inicio, mayoristas, nosotros, contacto, 404)
  plantillas/*.html      cabecera, pie y bloques repetidos
  assets/                css, js, logo, fotos (las fotos las prepara scripts/optimizar-fotos.py)

Los archivos generados (index.html, coleccion/, prendas/, sitemap.xml...) se versionan en git
porque GitHub Pages los publica tal cual. No los edites a mano: se pisan en el proximo build.
"""
import hashlib
import html
import json
import os
import re
import shutil
import sys
from urllib.parse import quote

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "/ao-confecciones-web"
SITIO = "https://matiasbtt.github.io/ao-confecciones-web"
WHATSAPP = "59157736466"
CATALOGO_ORIGINAL = "https://canva.link/dmb9s41cvzbv9yv"
CAT_SIN_PAGINA = "Colección"  # categoria "paraguas": existe en el catalogo general pero no tiene pagina propia

FLECHA = '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M5 12h14m-6-6 6 6-6 6"/></svg>'
ICONO_WA = '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M20 11.5a8.5 8.5 0 0 1-12.8 7.3L3 20l1.2-4.2A8.5 8.5 0 1 1 20 11.5Z"/><path d="M8 8c1 3 2 4 5 5l2-1 1 2c-1 2-5 1-7-1S6 7 8 6l2 1-2 1Z"/></svg>'


def leer(ruta):
    with open(os.path.join(RAIZ, ruta), encoding="utf8", newline="") as f:
        return f.read()


def esc(texto):
    return html.escape(texto, quote=True).replace("&#x27;", "'")


def wa(texto):
    return "https://wa.me/%s?text=%s" % (WHATSAPP, quote(texto, safe="()"))


# ---------------------------------------------------------------- datos
def cargar():
    prendas = json.loads(leer("data/prendas.json"))
    prendas.sort(key=lambda p: p["numero"])
    for p in prendas:
        n = "%02d" % p["numero"]
        p["id"] = "catalogo-" + n
        p["nn"] = n
    categorias = json.loads(leer("data/categorias.json"))
    return prendas, categorias


def validar(prendas, categorias):
    errores, vistos = [], set()
    nombres_cat = {c["nombre"] for c in categorias} | {CAT_SIN_PAGINA}
    for p in prendas:
        for campo in ("numero", "nombre", "slug", "categoria", "descripcion", "precio_docena", "precio_unidad"):
            if campo not in p:
                errores.append("Prenda %s: falta '%s'" % (p.get("numero"), campo))
        if p["slug"] in vistos:
            errores.append("Slug repetido: " + p["slug"])
        vistos.add(p["slug"])
        if p["categoria"] not in nombres_cat:
            errores.append("Prenda %s: la categoria '%s' no esta en data/categorias.json" % (p["numero"], p["categoria"]))
        for t in (480, 768, 1000):
            if not os.path.exists(os.path.join(RAIZ, "assets", "catalogo", "prenda-%s-%d.webp" % (p["nn"], t))):
                errores.append("Prenda %s: falta assets/catalogo/prenda-%s-%d.webp (corre scripts/optimizar-fotos.py)" % (p["numero"], p["nn"], t))
        if re.search(r"[–—]", p["nombre"] + p["descripcion"]):
            errores.append("Prenda %s: evita rayas largas (— –) en los textos; usa coma o punto" % p["numero"])
    return errores


# ---------------------------------------------------------------- piezas
def ruta_categoria(p, categorias):
    for c in categorias:
        if c["nombre"] == p["categoria"]:
            return "%s/coleccion/%s/" % (BASE, c["slug"])
    return BASE + "/coleccion/"


def imagen(p, sizes, extra):
    base = "%s/assets/catalogo/prenda-%s" % (BASE, p["nn"])
    alt = "%s, visualización recreada con IA basada en la página %d del catálogo de A&amp;O" % (p["nombre"], p["numero"])
    return ('<img src="%s-1000.webp" srcset="%s-480.webp 480w, %s-768.webp 768w, %s-1000.webp 1000w" sizes="%s" alt="%s" '
            'width="1000" height="1333" %s decoding="async" data-fallback>') % (base, base, base, base, sizes, alt, extra)


def msg_prenda(p):
    return ("Hola, A&O. Quisiera consultar precio y disponibilidad de %s (catálogo, pág. %d). "
            "¿Cómo se arma la docena y cuáles son las condiciones de compra y envío?") % (p["nombre"], p["numero"])


def tarjeta(p):
    busqueda = esc("%s %s %s %d" % (p["nombre"], p["descripcion"], p["categoria"], p["numero"]))
    url = "%s/prendas/%s/" % (BASE, p["slug"])
    return (
        '<article class="product-card" data-search-text="%s"><a class="product-photo" href="%s" aria-label="Ver %s">%s'
        '<span class="photo-fallback">%s<br>Consulta sus detalles con A&O.</span></a>'
        '<div class="product-meta"><p class="eyebrow">%s · Catálogo %s</p><div class="product-title-row"><h3><a href="%s">%s</a></h3>'
        '<button class="add-button" data-add-product="%s" aria-pressed="false" aria-label="Agregar a la consulta: %s"><span aria-hidden="true">+</span></button></div>'
        '<p class="product-pricing">Bs %d / docena <span class="muted">Bs %d / unidad</span></p>'
        '<a class="text-link" href="%s" target="_blank" rel="noopener" data-product="%s">Consultar esta prenda %s</a></div></article>'
    ) % (busqueda, url, p["nombre"],
         imagen(p, "(max-width: 639px) 48vw, (max-width: 1199px) 32vw, 24vw", 'loading="lazy"'),
         p["nombre"], p["categoria"], p["nn"], url, p["nombre"], p["id"], p["nombre"],
         p["precio_docena"], p["precio_unidad"], wa(msg_prenda(p)), p["id"], FLECHA)


def principal_prenda(p, prendas, categorias):
    cat_url = ruta_categoria(p, categorias)
    relacionadas = [q for q in prendas if q["categoria"] == p["categoria"] and q is not p][:3]
    detalle = (
        '<main id="contenido"><section class="container product-detail"><nav class="breadcrumbs" aria-label="Ruta de navegación">'
        '<a href="%s/">Inicio</a><span aria-hidden="true">/</span><a href="%s/coleccion/">Colección</a><span aria-hidden="true">/</span>'
        '<a href="%s">%s</a><span aria-hidden="true">/</span><span>%s</span></nav>'
        '<div class="product-detail-grid"><div class="detail-image" style="position:relative">%s'
        '<span class="photo-fallback">%s<br>Consulta su fotografía en el catálogo original.</span></div>'
        '<div class="detail-copy"><h1>%s</h1><p class="model-reference">Catálogo, página %d · %s</p>'
        '<p class="detail-description">%s</p>'
        '<div class="detail-prices"><div><strong>Bs %d</strong><span>Precio por docena</span></div>'
        '<div><strong>Bs %d</strong><span>Precio por unidad</span></div></div>'
        '<p class="note">Precios del catálogo. Consulta su vigencia y la disponibilidad de este modelo con A&O.</p>'
        '<div class="detail-actions"><a class="button primary" href="%s" data-product="%s" target="_blank" rel="noopener">%sConsultar precio y disponibilidad</a>'
        '<button class="button" data-add-product="%s" aria-pressed="false">Agregar a mi consulta</button></div>'
        '<div class="detail-links"><button class="clear-filter" data-copy-individual="%s">Copiar consulta</button>'
        '<a href="%s/mayoristas/" class="clear-filter">Cómo comprar</a></div>'
        '<div class="info-list"><div><span>Modelo</span><span>%s</span></div><div><span>Referencia en catálogo</span><span>Página %d</span></div>'
        '<div><span>Tallas y colores</span><span>Consultar con A&O</span></div></div>'
        '<p class="detail-source">Visualización de la prenda recreada con IA a partir del catálogo. Revisa la fotografía de referencia y descripción en el '
        '<a href="%s" target="_blank" rel="noopener">catálogo original de A&O</a>.</p></div></div></section>'
    ) % (BASE, BASE, cat_url, p["categoria"], p["nombre"],
         imagen(p, "(max-width: 959px) 90vw, 48vw", 'fetchpriority="high"'),
         p["nombre"], p["nombre"], p["numero"], p["categoria"], esc(p["descripcion"]),
         p["precio_docena"], p["precio_unidad"], wa(msg_prenda(p)), p["id"], ICONO_WA, p["id"], p["id"], BASE,
         p["nombre"], p["numero"], CATALOGO_ORIGINAL)
    mas = ""
    if relacionadas:
        mas = ('<section class="container section" style="padding-top:15px"><div class="section-heading"><div><h2>Más %s.</h2></div>'
               '<a class="text-link" href="%s/coleccion/">Ver colección completa</a></div><div class="product-grid">%s</div></section>'
               ) % (p["categoria"].lower(), BASE, "".join(tarjeta(q) for q in relacionadas))
    return detalle + mas + leer("plantillas/cierre.html") + "</main>"


def nav_categorias(categorias, actual_slug):
    def enlace(href, texto, actual):
        return '<a href="%s"%s>%s</a>' % (href, ' aria-current="page"' if actual else "", texto)
    partes = [enlace(BASE + "/coleccion/", "Todas", actual_slug is None)]
    for c in categorias:
        partes.append(enlace("%s/coleccion/%s/" % (BASE, c["slug"]), c["nombre"], c["slug"] == actual_slug))
    return '<nav class="category-nav" aria-label="Categorías de prendas">%s</nav>' % "".join(partes)


def conteo(n):
    return "%d prenda%s" % (n, "" if n == 1 else "s")


def principal_coleccion(lista, categorias, categoria):
    m = leer("plantillas/coleccion.html")
    h1 = categoria["nombre"] if categoria else "Prendas <em>para tu negocio.</em>"
    return (m.replace("{{H1}}", h1)
             .replace("{{NAV_CATEGORIAS}}", nav_categorias(categorias, categoria["slug"] if categoria else None))
             .replace("{{CONTEO}}", conteo(len(lista)))
             .replace("{{TARJETAS}}", "".join(tarjeta(p) for p in lista)))


def json_catalogo(prendas):
    datos = [{"id": p["id"], "name": p["nombre"], "category": p["categoria"], "description": p["descripcion"],
              "image": "%s/assets/catalogo/prenda-%s-480.webp" % (BASE, p["nn"]), "slug": p["slug"], "source_page": p["numero"]}
             for p in prendas]
    return json.dumps(datos, ensure_ascii=False, separators=(",", ":"))


def version_assets():
    h = hashlib.md5()
    for ruta in ("assets/styles.css", "assets/app.js"):
        h.update(open(os.path.join(RAIZ, ruta), "rb").read().replace(b"\r\n", b"\n"))
    return h.hexdigest()[:8]


def documento(m, titulo, descripcion, ruta, pagina, actual, producto, catalogo, v):
    d = leer("plantillas/documento.html")
    url = "%s/%s" % (SITIO, ruta)
    d = (d.replace("{{TITULO}}", titulo).replace("{{DESCRIPCION}}", descripcion).replace("{{URL}}", url)
          .replace("{{PAGINA}}", pagina).replace("{{ATRIB_PRODUCTO}}", ' data-product="%s"' % producto if producto else "")
          .replace("{{CATALOGO_JSON}}", catalogo).replace("{{V}}", v).replace("{{MAIN}}", m))
    for clave in ("COLECCION", "MAYORISTAS", "NOSOTROS", "CONTACTO"):
        d = d.replace("{{ACTUAL_%s}}" % clave, ' aria-current="page"' if actual == clave else "")
    return d


def pagina_suelta(nombre, prendas):
    crudo = leer("paginas/%s.html" % nombre)
    meta_txt, cuerpo = crudo.split("-->\n", 1)
    meta = json.loads(meta_txt[4:])
    cuerpo = cuerpo.rstrip("\n")
    destacadas = [p for p in prendas if p.get("destacada_en_inicio")]
    cuerpo = (cuerpo.replace("{{TARJETAS_INICIO}}", "".join(tarjeta(p) for p in destacadas))
                    .replace("{{TOTAL_PRENDAS}}", conteo(len(prendas))))
    return meta, cuerpo


# ---------------------------------------------------------------- build
def construir(forzar_v=None):
    prendas, categorias = cargar()
    errores = validar(prendas, categorias)
    if errores:
        print("No se puede construir:\n  - " + "\n  - ".join(errores))
        sys.exit(1)
    v = forzar_v or version_assets()
    catalogo = json_catalogo(prendas)
    salida = {}

    for nombre in ("inicio", "mayoristas", "nosotros", "contacto", "404"):
        meta, cuerpo = pagina_suelta(nombre, prendas)
        destino = "index.html" if nombre == "inicio" else (meta["ruta"] if meta["ruta"].endswith(".html") else meta["ruta"] + "index.html")
        salida[destino] = documento(cuerpo, meta["titulo"], meta["descripcion"], meta["ruta"], meta["pagina"], meta["actual"], None, catalogo, v)

    n = len(prendas)
    salida["coleccion/index.html"] = documento(
        principal_coleccion(prendas, categorias, None), "Colección | A&O Confecciones",
        "Explora las %d prendas del catálogo de A&amp;O Confecciones. Tops, short falda, vestido y chaquetas para tu negocio." % n,
        "coleccion/", "coleccion", "COLECCION", None, catalogo, v)
    for c in categorias:
        lista = [p for p in prendas if p["categoria"] == c["nombre"]]
        salida["coleccion/%s/index.html" % c["slug"]] = documento(
            principal_coleccion(lista, categorias, c), "%s al por mayor | A&O Confecciones" % c["nombre"],
            "Descubre %s del catálogo de A&amp;O y consulta condiciones mayoristas por WhatsApp." % c["nombre"].lower(),
            "coleccion/%s/" % c["slug"], "coleccion", "", None, catalogo, v)

    for p in prendas:
        salida["prendas/%s/index.html" % p["slug"]] = documento(
            principal_prenda(p, prendas, categorias), "%s | A&O Confecciones" % p["nombre"],
            "%s Consulta este modelo y sus condiciones mayoristas con A&amp;O Confecciones." % esc(p["descripcion"]),
            "prendas/%s/" % p["slug"], "modelo", "", p["id"], catalogo, v)

    rutas = [""] + ["coleccion/"] + ["coleccion/%s/" % c["slug"] for c in categorias] + \
            ["prendas/%s/" % p["slug"] for p in prendas] + ["mayoristas/", "nosotros/", "contacto/"]
    salida["sitemap.xml"] = ('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                             + "".join("<url><loc>%s/%s</loc></url>" % (SITIO, r) for r in rutas) + "</urlset>")
    return salida, prendas


def main():
    solo_revisar = "--check" in sys.argv
    forzar = None
    if "--v" in sys.argv:
        forzar = sys.argv[sys.argv.index("--v") + 1]
    salida, prendas = construir(forzar)
    cambios = []
    for ruta, contenido in salida.items():
        destino = os.path.join(RAIZ, ruta)
        actual = open(destino, encoding="utf8", newline="").read() if os.path.exists(destino) else None
        if actual is None or actual.replace("\r\n", "\n") != contenido:
            cambios.append(ruta)
            if not solo_revisar:
                os.makedirs(os.path.dirname(destino), exist_ok=True)
                with open(destino, "w", encoding="utf8", newline="") as f:
                    f.write(contenido)
    # prendas que ya no existen en data/: borrar su pagina
    carpeta = os.path.join(RAIZ, "prendas")
    vigentes = {p["slug"] for p in prendas}
    if os.path.isdir(carpeta):
        for nombre in os.listdir(carpeta):
            if nombre not in vigentes and os.path.isdir(os.path.join(carpeta, nombre)):
                cambios.append("(borrar) prendas/%s/" % nombre)
                if not solo_revisar:
                    shutil.rmtree(os.path.join(carpeta, nombre))
    print(("%d archivo(s) %s:" % (len(cambios), "cambiarian" if solo_revisar else "actualizados")) if cambios else "Todo al dia: nada que cambiar.")
    for c in cambios:
        print("  -", c)
    if solo_revisar and cambios:
        sys.exit(1)


if __name__ == "__main__":
    main()
