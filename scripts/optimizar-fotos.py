#!/usr/bin/env python3
"""Prepara las fotos del catalogo para la web.

Uso:  python scripts/optimizar-fotos.py            (procesa todo lo de _fuentes/)
      python scripts/optimizar-fotos.py 16 17      (solo esos numeros de prenda)

Entrada : _fuentes/prenda-NN.(jpg|png|webp)  (foto original, cualquier tamano;
          tambien acepta el nombre antiguo render-natural-NN-v2.webp)
Salida  : assets/catalogo/prenda-NN-480.webp, -768.webp, -1000.webp
Hace tres cosas: pasa el fondo durazno a blanco puro (solo el fondo conectado
a los bordes, no toca la prenda), reduce el peso y crea tamanos responsivos.
Requiere: pip install pillow numpy scipy
"""
import sys, re, glob, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUENTES = os.path.join(RAIZ, "_fuentes")
SALIDA = os.path.join(RAIZ, "assets", "catalogo")
TAMANOS = {480: 66, 768: 70, 1000: 72}  # ancho: calidad webp


def blanquear_fondo(img, tol=44, solido=10):
    """Fondo durazno a blanco. Solo toca el fondo conectado a los bordes; las
    sombras suaves se aclaran de forma gradual y la prenda queda intacta."""
    a = np.asarray(img.convert("RGB")).astype(float)
    borde = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]]).mean(0)
    dist = np.sqrt(((a - borde) ** 2).sum(2))
    etiquetas, _ = ndi.label(dist < tol)
    tocan_borde = set(np.unique(np.concatenate(
        [etiquetas[0], etiquetas[-1], etiquetas[:, 0], etiquetas[:, -1]]))) - {0}
    fondo = np.isin(etiquetas, list(tocan_borde))
    t = np.clip((dist - solido) / (tol - solido), 0, 1)
    peso = np.where(fondo, 1 - t * t * (3 - 2 * t), 0)
    peso = ndi.gaussian_filter(peso, 1.0)[..., None]
    return Image.fromarray((a * (1 - peso) + 255 * peso).clip(0, 255).astype("uint8"))


def procesar(numero):
    origen = None
    for patron in (f"prenda-{numero}.*", f"render-natural-{numero}-v2.*"):
        hallados = glob.glob(os.path.join(FUENTES, patron))
        if hallados:
            origen = hallados[0]; break
    if not origen:
        print(f"  no hay foto en _fuentes/ para la prenda {numero} (prenda-{numero}.jpg/png/webp)"); return
    img = blanquear_fondo(Image.open(origen))
    for ancho, calidad in TAMANOS.items():
        alto = round(img.height * ancho / img.width)
        destino = os.path.join(SALIDA, f"prenda-{numero}-{ancho}.webp")
        img.resize((ancho, alto), Image.LANCZOS).save(
            destino, "WEBP", quality=calidad, method=6)
        print(f"  {os.path.basename(destino)}  {os.path.getsize(destino)//1024} KB")


if __name__ == "__main__":
    numeros = sys.argv[1:] or sorted({
        re.search(r"(?:prenda-|render-natural-)(\d+)", os.path.basename(f)).group(1)
        for f in glob.glob(os.path.join(FUENTES, "*"))
        if re.search(r"(?:prenda-|render-natural-)(\d+)", os.path.basename(f))})
    for n in numeros:
        print(f"Prenda {n}"); procesar(n.zfill(2))
