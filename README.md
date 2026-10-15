# A&O Confecciones · sitio web

Catálogo mayorista de ropa femenina con consultas por WhatsApp. Sitio estático publicado con GitHub Pages:
https://matiasbtt.github.io/ao-confecciones-web/

No hay servidor ni base de datos. Las páginas se generan desde unos pocos archivos de datos y se publican tal cual.

## Agregar una prenda nueva

Hace falta Python 3.10+ y `pip install -r requirements.txt` (una sola vez).

```bash
python scripts/agregar-prenda.py --numero 16 --nombre "Top Rosa" --categoria Tops \
  --descripcion "Top con mangas cortas. Tejido elástico y ligero." \
  --docena 260 --unidad 27 --foto "C:/fotos/top-rosa.jpg" --inicio
```

Eso hace todo junto: optimiza la foto (fondo blanco y tres tamaños), agrega la prenda a `data/prendas.json`,
crea la categoría si es nueva y regenera las páginas, la colección, el sitemap y la portada.
`--inicio` es opcional y la muestra también en la portada.

Después, para ver el resultado antes de publicar:

```bash
python -m http.server 4173 --directory ..
# abrir http://localhost:4173/ao-confecciones-web/
```

Y para publicar: `git add -A`, `git commit` y `git push`. GitHub Pages actualiza el sitio en un par de minutos.

### Fotos

- Sube la foto original (jpg, png o webp, cualquier tamaño). Fondo liso claro, vertical 3:4 funciona mejor.
- `scripts/optimizar-fotos.py` pasa el fondo durazno/crema a blanco puro y genera `prenda-NN-480.webp`,
  `-768.webp` y `-1000.webp`. Una prenda pesa unos 100 KB en total, no varios MB.
- Las fotos originales quedan en `_fuentes/` por si hay que reprocesarlas. No se cargan en la web.

## Cambiar precios, nombres o textos

- Prendas (nombre, precio, descripción, categoría): `data/prendas.json`
- Menú de categorías: `data/categorias.json`
- Páginas sueltas: `paginas/` (inicio, mayoristas, nosotros, contacto, 404)
- Cabecera, pie y bloques repetidos: `plantillas/`
- Colores, tipografía y animaciones: `assets/styles.css` (variables al inicio del bloque "v3")
- Comportamiento (selección de prendas, mensajes de WhatsApp, animaciones al hacer scroll): `assets/app.js`

Después de cualquier cambio en `data/`, `paginas/` o `plantillas/` corre:

```bash
python scripts/build.py          # regenera el sitio
python scripts/build.py --check  # solo avisa si algo está desactualizado (lo usa GitHub Actions)
```

`build.py` valida antes de escribir: avisa si falta una foto, si hay un slug repetido o si una categoría no existe.

## Estructura

```
data/            prendas.json, categorias.json   <- lo que se edita
paginas/         contenido de las páginas sueltas
plantillas/      documento (cabecera/pie), colección, cierre
scripts/         build.py, agregar-prenda.py, optimizar-fotos.py
assets/          styles.css, app.js, logo, fotos optimizadas, tipografías
_fuentes/        fotos originales (no se cargan en la web)
docs/            evaluación de diseño
index.html, coleccion/, prendas/, mayoristas/ ...   <- generado, no editar a mano
```

## Reglas de diseño que conviene mantener

- Fondo blanco puro. Un solo acento (vino `#651f36`); el crema y el rosa solo como tintes muy suaves.
- Tipografía: Cormorant Garamond (títulos) y Space Grotesk (texto). Autoalojadas, licencias OFL en `assets/fonts/`.
- Movimiento: solo `transform` y `opacity`. Todo respeta `prefers-reduced-motion`.
- Sin rayas largas (— –) en ningún texto visible. `build.py` lo revisa en nombres y descripciones.
- Cada prenda nueva necesita sus tres tamaños de foto antes de construir.

Detalle de la revisión de diseño en [docs/EVALUACION-TASTE.md](docs/EVALUACION-TASTE.md).
