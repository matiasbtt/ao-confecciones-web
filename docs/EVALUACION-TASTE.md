# Evaluación de diseño con Taste Skill y Emil Kowalski

Fecha: 8 de octubre de 2026. Revisión del sitio antes y después de los cambios.

**Lectura del encargo:** rediseño de un catálogo mayorista de ropa femenina para comerciantes de Cochabamba,
con lenguaje editorial de e-commerce de moda. Se conserva la estructura, los textos y las URL; se rehace el
lenguaje visual y el movimiento. Diales: variación 7, movimiento 7, densidad 3.

## Qué marcaba la skill en la versión anterior

| Regla | Antes | Ahora |
| --- | --- | --- |
| Serif prohibida por defecto (Fraunces) | Fraunces en títulos y navegación, 293 KB de fuentes | Cormorant Garamond (está en la lista permitida), 93 KB con Space Grotesk |
| Paleta beige + espresso, la más repetida de la IA | Crema `#f0dec8` en cabecera, hero, bloques y pie; fondo `#faf4eb` | Blanco `#fff` como base. Crema y rosa solo como tintes suaves en 2 bloques |
| Un solo acento | Rosa en botones, vino en la cabecera, dorado suelto | Un acento: vino `#651f36`, en todos los botones primarios |
| Cabecera máx. 80 px | 174 px con el logo a 168 px | 96 px con el logo a 80 px (se mantiene algo sobre el tope para que el sello siga legible) |
| Entradas con movimiento motivado | Ninguna entrada, solo zoom del cursor en 3 enlaces | Entrada desde los lados hacia el centro, revelado al hacer scroll y salida entre páginas |
| Estados táctiles en botones | `scale(.97)` al presionar | Salto al pasar el cursor, relleno que barre, presión con resorte y rebote al agregar |
| Raya larga (—) prohibida | 1 en el mensaje de WhatsApp de la consulta | Ninguna en el sitio |
| Fotos reales y pesadas | 1,4 MB solo en la portada | 350 KB en la portada (ver "Peso") |
| Nombre de las imágenes y fallbacks | Con fallback de texto si falla la foto | Se mantiene |

## Lo que se cambió, con la razón de cada cosa

**Fondo blanco puro.** Pedido expreso. Las fotos traían el fondo durazno pintado dentro de la imagen, así que no
bastaba con cambiar el CSS: `scripts/optimizar-fotos.py` pasa ese fondo a blanco sin tocar la prenda (solo el fondo
conectado a los bordes, con las sombras suaves aclaradas). La skill recomienda evitar `#fff` puro; se respetó el pedido.

**Entrada desde los lados.** Lo de la izquierda (menú izquierdo, título, texto, botones) entra desde la izquierda; lo
de la derecha (menú derecho, las dos fotos) desde la derecha; el logo cae al centro. Todo se acerca al centro con
escala de 0,94 a 1, para que se sienta que "se acercan". Primera visita de la sesión: 900 ms con escalonado.
Visitas siguientes: 520 ms, para que navegar no se vuelva lento. Usa CSS (no JS) para que no haya parpadeo.

**Revelado al hacer scroll.** Las tarjetas de las columnas izquierdas entran desde la izquierda y las de las derechas
desde la derecha; lo del centro sube. Se decide midiendo la posición real del elemento, así que en móvil (2 columnas)
también funciona. Solo anima lo que todavía no se ve al cargar, para no causar parpadeo.

**Salida.** Al tocar un enlace interno, cada lado se aleja hacia su borde durante 230 ms y recién entonces cambia la
página. Se ignoran clics con Ctrl o Cmd, enlaces a otra pestaña y a otro dominio (WhatsApp), y se limpia al volver con
el botón atrás.

**Botones.** Cada control que se puede presionar tiene su microanimación:

| Elemento | Al pasar el cursor | Al presionar |
| --- | --- | --- |
| Botones (`.button`) | Salta 9 px y se asienta en 4 px (rebote real, no solo subir), el color se rellena de izquierda a derecha, sombra teñida de vino, la flecha se corre 5 px | Escala 0,96 en 90 ms |
| Botón "+" de cada prenda | Crece 10 % y se llena de vino | Rebote "pop" (0,8 a 1,2 a 1) y el contador del menú también rebota |
| Menú, selección, cerrar | Salto corto de 5 px | Escala 0,96 |
| Enlaces con flecha | Salto de 2 px y flecha corrida | |
| Botón flotante de WhatsApp | Salto y el ícono se mueve | Además da 4 saltos suaves al empezar la visita (uno cada 8 s, desde los 5 s) para llamar la atención sobre el contacto |
| Tarjeta de prenda | La foto sube 6 px con sombra | |

Criterios de Emil Kowalski aplicados: curvas con `ease-out` fuerte, nada de `ease-in`; solo se anima `transform`
y `opacity` (con las propiedades individuales `translate` y `scale`, que no chocan con el zoom del cursor del menú);
los efectos de hover van dentro de `@media (hover: hover) and (pointer: fine)` para que no se disparen en táctil;
las transiciones (no keyframes) donde puede haber interrupción; ninguna animación pasa de 460 ms en un control.
Todo se apaga con `prefers-reduced-motion`.

**Peso.** Medido en Chrome con la caché desactivada, servidor local sin compresión (GitHub Pages comprime el CSS,
el JS y el HTML, así que en línea será un poco menos):

| Página | Antes | Ahora |
| --- | --- | --- |
| Portada, escritorio | 1.417 KB | 351 KB |
| Portada, móvil con red 3G rápida | 939 KB, 4,5 s | 341 KB, 1,8 s |
| Colección | 1.052 KB | 376 KB |
| Ficha de prenda | 646 KB | 252 KB |

Qué lo bajó: cada foto pasa de 1 MB a ~100 KB en tres tamaños (480, 768 y 1000 px) y el navegador elige el que
corresponde; `sizes` estaba mal calculado (pedía el doble de lo necesario en la portada); el logo se sirve como WebP
de 16 KB en la cabecera en vez del SVG de 200 KB; el ícono de pestaña es un PNG de 11 KB; las fuentes pasaron de
293 KB a 93 KB. Total de `assets/`: de 8,4 MB a 2,2 MB.

## Referencias visuales externas

No pude revisar sitios en vivo con detalle: Sézane puso un muro de cookies y país, y aceptar consentimientos no es
algo que haga por ti. Por eso estas referencias son **patrones de diseño conocidos del e-commerce de moda editorial**
(p. ej. Sézane, COS, Aritzia), no capturas ni copias:

- **Marcos en arco** para las dos fotos principales: eco del círculo del logo y un recurso habitual en moda editorial.
- **Cuadrícula escalonada** (las columnas pares bajan 40 px): rompe la rejilla de tarjetas iguales que la skill llama genérica.
- **Pareja tipográfica** de serif cursiva grande con sans pequeña y limpia, con mucho aire.
- **Todo sobre blanco con líneas finas** en lugar de bloques de color.
- **Botones en pastilla con relleno que barre**, el gesto de interfaz más común en tiendas de moda actuales.

## Lo que sigue pendiente (decisiones tuyas)

1. **Fotografía real.** Las prendas son visualizaciones recreadas con IA (el sitio lo avisa). Es lo que más pesa
   en la sensación de "diseño genérico": con 3 a 5 fotos reales de las prendas puestas (portada, historia, una por
   categoría) el sitio cambia de nivel. En este entorno no puedo generar imágenes.
2. **Modo oscuro.** La skill lo pide en páginas de consumo. No se hizo: el sitio es de fondo blanco por decisión de
   marca. Si lo quieres, es un bloque de variables en el CSS.
3. **Numeración "01 02 03"** en los pasos de la portada: la skill la marca como etiqueta genérica. Se dejó porque
   ayuda a leer el orden; se puede quitar.
4. **Prenda 6** ("Top Canela", categoría "Colección"): la foto muestra una prenda de tirantes a cuadros y el nombre
   del catálogo no coincide. La ficha ya avisa que se confirme con A&O. Conviene corregir nombre y categoría en
   `data/prendas.json`.
5. **Prueba en celulares reales**, sobre todo el rebote de botones al tocar (en táctil no hay hover, así que ahí
   solo se ve la presión y el pop).
