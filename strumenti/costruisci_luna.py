"""Costruisce le due mappe della Luna in alta risoluzione usate dall'oculare.

Sorgenti (NASA LRO, scaricate a parte perché pesano ~60 MB, non stanno nel repository):
  alb8k.jpg  = lroc_color_poles_8k.jpg  (8192x4096)
      https://media.githubusercontent.com/media/nasa/virgo/master/src/virgo/images/moon/lroc_color_poles_8k.jpg
  dem16.tif  = ldem_16_uint.tif (5760x2880, uint16, 0,5 m per unità)
      https://media.githubusercontent.com/media/AVSLab/vizard/master/VizardUnityProject/Assets/Resources/Textures/CelestialBodies/Moon/ldem_16_uint.tif

Uscite, da mettere accanto a index.html:
  luna_alb_hd.jpg   albedo in grigi, longitudini da -100° a +100° (l'emisfero visibile più le librazioni)
  luna_pend_hd.jpg  pendenze del terreno: R = est-ovest, G = nord-sud, 128 = piano, ±127 = pendenza ±0,6
Uso: python costruisci_luna.py alb8k.jpg dem16.tif
"""
import sys
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
alb, dem = sys.argv[1], sys.argv[2]

A = Image.open(alb).convert('L')
W, H = A.size
x0 = round((-100 + 180) / 360 * W)
x1 = round((100 + 180) / 360 * W)
A.crop((x0, 0, x1 + 1, H)).save('luna_alb_hd.jpg', quality=86, optimize=True)

d = np.array(Image.open(dem)).astype(np.float32) * 0.5 / 1000  # quota in km
h, w = d.shape
X0 = round((-100 + 180) / 360 * w)
X1 = round((100 + 180) / 360 * w)
z = d[:, X0 - 1:X1 + 2]
lat = 90 - (np.arange(h) + 0.5) / h * 180
pk = 1737 * np.pi / 180 / 16  # km per pixel lungo il meridiano (16 pixel per grado)
cl = np.maximum(np.cos(np.radians(lat)), 0.05)[:, None]
gx = (z[:, 2:] - z[:, :-2]) / 2 / (pk * cl)
zz = z[:, 1:-1]
gy = np.zeros_like(zz)
gy[1:-1] = (zz[:-2] - zz[2:]) / 2 / pk
S = 0.6


def enc(g):
    return np.clip(np.round(128 + np.clip(g, -S, S) / S * 127), 0, 255).astype(np.uint8)


rgb = np.stack([enc(gx), enc(gy), np.full(gx.shape, 128, np.uint8)], -1)
Image.fromarray(rgb).save('luna_pend_hd.jpg', quality=90, optimize=True)
print('fatto')
