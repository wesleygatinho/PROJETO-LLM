"""
Pipeline v2 - revelacao digital de retrato ("homem mais serio").

Correcoes sobre a v1:
  - mascara da pessoa via GrabCut (nao heuristica de cor)
  - bug da luminancia do fundo corrigido (escala so no fundo)
  - exposicao reequilibrada, vinheta suave
  - geometria do rosto refinada por deteccao de olhos
"""

import sys
import numpy as np
import cv2
from pathlib import Path

SRC = Path(sys.argv[1] if len(sys.argv) > 1
           else r"C:\Users\santo\Downloads\foto foto foto.jpeg")
OUTDIR = Path(sys.argv[2] if len(sys.argv) > 2
              else r"D:\UFMA UNIVERSIDADE\MESTRADO - ESTUDO LLM\output\retrato")

RNG = np.random.default_rng(7)


# ------------------------------------------------------------- utilitarios
def luma(img):
    return 0.299 * img[..., 0] + 0.587 * img[..., 1] + 0.114 * img[..., 2]


def smooth(x, sigma):
    k = int(max(3, sigma * 4)) | 1
    return cv2.GaussianBlur(x.astype(np.float32), (k, k), sigma,
                            borderType=cv2.BORDER_REFLECT101)


def load(path):
    data = np.fromfile(str(path), dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if img is None:
        raise SystemExit(f"nao consegui abrir: {path}")
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


# ------------------------------------------------------------- deteccao
def detect_eyes_gray(gray):
    cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_eye.xml")
    eq = cv2.equalizeHist(gray)
    eyes = cascade.detectMultiScale(eq, 1.05, 6, minSize=(28, 28))
    return eyes


def detect_face(img):
    """Retorna (face_box, eye_centers). Usa olhos para refinar a geometria."""
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    eq = cv2.equalizeHist(gray)
    fc = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = fc.detectMultiScale(eq, 1.05, 4, minSize=(150, 150))
    if len(faces) == 0:
        faces = fc.detectMultiScale(eq, 1.01, 2, minSize=(110, 110))
    if len(faces) == 0:
        fb = (int(w * 0.22), int(h * 0.12), int(w * 0.78), int(h * 0.58))
        return fb, []

    fb = max(faces, key=lambda f: f[2] * f[3])
    x, y, fw, fh = fb

    # olhos dentro da face, ordenados por x
    region = eq[max(0, y - 20):y + fh, max(0, x - 20):x + fw + 20]
    eyes = detect_eyes_gray(region)
    centers = []
    for ex, ey, ew, eh in eyes:
        cx = max(0, x - 20) + ex + ew / 2
        cy = max(0, y - 20) + ey + eh / 2
        # linha dos olhos fica na metade superior da face
        if cy < y + fh * 0.62:
            centers.append((cx, cy))
    centers.sort()

    if len(centers) >= 2:
        # escolhe o par mais horizontal
        best = min(combinations(centers, 2),
                   key=lambda p: abs(p[0][1] - p[1][1]))
        (lx, ly), (rx, ry) = best
        eye_dx = abs(rx - lx)
        eye_dy = (ly + ry) / 2
        # caixa refined a partir da distancia entre os olhos
        new_w = eye_dx * 2.05
        new_h = new_w * 1.28
        new_x = (lx + rx) / 2 - new_w / 2
        new_y = eye_dy - new_h * 0.40
        fb2 = (int(max(0, new_x)), int(max(0, new_y)),
               int(min(w, new_x + new_w)), int(min(h, new_y + new_h)))
        # confia no refinado so se nao ficou absurdo
        if new_w > fw * 0.55 and new_w < fw * 1.6:
            fb = fb2
    return fb, centers


def combinations(lst, k=2):
    from itertools import combinations as _c
    return list(_c(lst, k))


# ------------------------------------------------------------- mascara
def grabcut_person(img, face_box):
    """Mascara da pessoa: GrabCut inicializado pela geometria do rosto."""
    h, w = img.shape[:2]
    mask = np.zeros((h, w), np.uint8)

    x0, y0, x1, y1 = face_box
    fw, fh = x1 - x0, y1 - y0

    # GC_FGD: rosto e pescoco (coluna central)
    mask[y0:y1, x0:x1] = cv2.GC_FGD
    neck = int(fh * 0.55)
    mask[y1:y1 + neck, x0 + int(fw * 0.18):x1 - int(fw * 0.18)] = cv2.GC_PR_FGD

    # GC_PR_FGD: ombros/torso abaixo
    body_top = y1 + neck
    mask[body_top:h, int(x0 - fw * 0.35):int(x1 + fw * 0.35)] = cv2.GC_PR_FGD

    # GC_PR_BGD: laterais e topo
    band = int(fw * 0.30)
    mask[:, :max(0, x0 - band)] = cv2.GC_PR_BGD
    mask[:, min(w, x1 + band):] = cv2.GC_PR_BGD
    mask[:max(0, y0 - int(fh * 0.55)), :] = cv2.GC_PR_BGD

    bgd = np.zeros((1, 65), np.float64)
    fgd = np.zeros((1, 65), np.float64)
    try:
        cv2.grabCut(img, mask, None, bgd, fgd, 5, cv2.GC_INIT_WITH_MASK)
    except cv2.error:
        return fallback_person(img, face_box)

    person = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 1.0, 0.0)
    person = cv2.morphologyEx(person.astype(np.uint8), cv2.MORPH_CLOSE,
                              np.ones((15, 15), np.uint8)).astype(np.float32)
    person = smooth(person, 3.0)
    person = np.clip((person - 0.35) / 0.4, 0, 1)
    if person.mean() < 0.06 or person.mean() > 0.92:
        return fallback_person(img, face_box)
    return person


def fallback_person(img, face_box):
    h, w = img.shape[:2]
    x0, y0, x1, y1 = face_box
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    rad = np.sqrt(((xx - cx) / (w * 0.55)) ** 2 + ((yy - cy) / (h * 0.55)) ** 2)
    p = np.clip((1.25 - rad) * 1.6, 0, 1)
    return smooth(p, 6.0)


# ------------------------------------------------------------- pele
def skin_mask(img):
    y = cv2.cvtColor(img, cv2.COLOR_RGB2YCrCb).astype(np.float32)
    m = ((y[..., 1] > 132) & (y[..., 1] < 182) &
         (y[..., 2] > 74) & (y[..., 2] < 132) &
         (y[..., 0] > 35)).astype(np.float32)
    return smooth(m, 4.0)


def matte_skin(img, skin):
    """Rebaixa specular da pele (brilho de testa/bochecha)."""
    L = luma(img)
    local = smooth(L, 14.0)
    hi = np.clip((L - local - 6.0) / 40.0, 0, 1) * skin
    L2 = L * (1 - hi) + np.minimum(L, local - 5.0) * hi
    ratio = (L2 + 1.0) / (L + 1.0)
    return np.clip(img.astype(np.float32) * ratio[..., None], 0, 255)


def even_skin_tone(img, skin, strength=0.32):
    """Suaviza vermelhidor e diferencas de tom, preservando textura."""
    a = img.astype(np.float32)
    for c, (lo, hi) in enumerate([(0, 0), (0, 0), (0, 0)]):
        pass
    blur = cv2.GaussianBlur(img, (0, 0), 22.0).astype(np.float32)
    corr = (blur - a) * 0.45 * strength * skin[..., None]
    # limita correcao por canal para nao criar artefato de cor
    corr = np.clip(corr, -16, 16)
    return np.clip(a + corr, 0, 255)


# ------------------------------------------------------------- luz
def studio_light(img, person, key=(-0.55, -0.62), strength=0.30):
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    nx = (xx / w - 0.5) * 2.0
    ny = (yy / h - 0.5) * 2.0
    kx, ky = key
    field = -(nx * kx + ny * ky)
    field = np.clip(field / 1.15, -1, 1)
    field = smooth(field, 50.0)
    field = (field - field.min()) / (field.max() - field.min() + 1e-6)

    L = luma(img)
    hi = np.clip((L - 105.0) / 125.0, 0, 1)
    lo = np.clip((100.0 - L) / 100.0, 0, 1)
    add = (hi * 0.78 + 0.22) * field * 40.0 * strength * person
    sub = lo * (1.0 - field) * 16.0 * strength * person
    return np.clip(img.astype(np.float32) + (add - sub)[..., None], 0, 255)


def dodge_burn(img, face_box, person):
    h, w = img.shape[:2]
    x0, y0, x1, y1 = face_box
    cx = (x0 + x1) / 2.0
    width = (x1 - x0) * 0.60
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    side = np.clip(np.abs(xx - cx) / width, 0, 1.8)
    brow = y0 + (y1 - y0) * 0.32
    vert = np.clip((yy - brow) / max(1.0, (y1 - brow) * 0.60), 0, 1)
    burn = np.clip((side - 0.90) * 0.85, 0, 1) * vert * person
    return np.clip(img.astype(np.float32) - (burn * 13.0)[..., None], 0, 255)


# ------------------------------------------------------------- cor
def color_grade(img):
    """Contraste em curva S + sombras frias + pele natural."""
    x = img.astype(np.float32) / 255.0
    x = x + 0.13 * (x - 0.5) * (1.0 - np.abs(2.0 * x - 1.0)) / 2.0

    L = luma(img)
    lo = np.clip((0.55 - L / 255.0) / 0.55, 0, 1)
    hi = np.clip((L / 255.0 - 0.45) / 0.55, 0, 1)
    shadow_tint = np.array([0.975, 0.990, 1.035], np.float32)
    high_tint = np.array([1.012, 1.000, 0.988], np.float32)
    x = x * (lo[..., None] * shadow_tint + hi[..., None] * high_tint)

    img8 = np.clip(x * 255, 0, 255).astype(np.uint8)
    hsv = cv2.cvtColor(img8, cv2.COLOR_RGB2HSV).astype(np.float32)
    skin = skin_mask(img8)
    hsv[..., 1] = np.clip(hsv[..., 1] * (0.90 - 0.16 * skin), 0, 255)
    x = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32) / 255.0
    return np.clip(x * 255.0, 0, 255)


# ------------------------------------------------------------- olhos
def eye_enhance(img, face_box, person, eye_centers):
    h, w = img.shape[:2]
    x0, y0, x1, y1 = face_box
    fw, fh = x1 - x0, y1 - y0

    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    m = np.zeros((h, w), np.float32)
    if len(eye_centers) >= 2:
        pts = eye_centers[:2] if len(eye_centers) == 2 else eye_centers
        for cx, cy in pts:
            ell = ((xx - cx) / (fw * 0.135)) ** 2 + ((yy - cy) / (fh * 0.075)) ** 2
            m = np.maximum(m, np.clip(1.0 - ell, 0, 1))
    else:
        eye_y = y0 + fh * 0.46
        for ex in (0.33, 0.67):
            cx = x0 + fw * ex
            ell = ((xx - cx) / (fw * 0.135)) ** 2 + ((yy - eye_y) / (fh * 0.075)) ** 2
            m = np.maximum(m, np.clip(1.0 - ell, 0, 1))
    m = smooth(m, 2.5) * person

    L = luma(img)
    dark = np.clip((1.0 - L / 190.0), 0, 1)
    out = img.astype(np.float32) - (m * dark * 18.0)[..., None]
    out += (m * np.clip((L - 70.0) / 150.0, 0, 1) * 9.0)[..., None]
    return np.clip(out, 0, 255)


# ------------------------------------------------------------- nitidez
def face_sharp_mask(face_box, shape):
    h, w = shape
    x0, y0, x1, y1 = face_box
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    ell = ((xx - cx) / ((x1 - x0) * 0.55)) ** 2 + ((yy - cy) / ((y1 - y0) * 0.62)) ** 2
    return smooth(np.clip(1.0 - ell, 0, 1), 9.0)


def selective_sharpen(img, mask, amount=0.70, radius=1.5):
    blur = cv2.GaussianBlur(img, (0, 0), radius).astype(np.float32)
    a = amount * mask[..., None]
    return np.clip(img.astype(np.float32) * (1 + a) - blur * a, 0, 255)


# ------------------------------------------------------------- fundo
def separate_background(img, person):
    """Fundo: blur de profundidade, escurecido, dessaturado, tom frio.

    A luminancia alvo e aplicada SOMENTE ao fundo (corrige o bug da v1).
    """
    alpha = smooth(np.clip(person, 0, 1), 2.0)[..., None]

    blur = cv2.GaussianBlur(img, (0, 0), 3.2)
    comp = img.astype(np.float32) * alpha + blur.astype(np.float32) * (1 - alpha)

    b = comp.copy()
    bL = luma(b)
    bg_sel = person < 0.5
    med_bg = float(np.median(luma(img)[bg_sel])) if bg_sel.sum() > 500 else 130.0
    target = max(58.0, med_bg * 0.52)
    scale = np.where(bL > 4.0, target / np.maximum(bL, 1.0), 1.0)
    b = b * scale[..., None]

    bL2 = luma(b)
    b = bL2[..., None] * 0.45 + b * 0.55
    b = b * np.array([0.95, 0.985, 1.06], np.float32)

    out = img.astype(np.float32) * alpha + b * (1 - alpha)
    return np.clip(out, 0, 255)


def vignette(img, amount=0.22):
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    nx = (xx / w - 0.5) * 2.0
    ny = (yy / h - 0.5) * 2.0
    r = np.sqrt(nx ** 2 * 0.85 + ny ** 2)
    v = 1.0 - amount * np.clip((r - 0.60) / 0.80, 0, 1) ** 1.8
    return np.clip(img.astype(np.float32) * v[..., None], 0, 255)


def crop_portrait(img, face_box, ratio=4 / 5):
    h, w = img.shape[:2]
    x0, y0, x1, y1 = face_box
    fh = y1 - y0
    target_h = fh * 3.15
    target_w = target_h / ratio
    if target_w > w:
        target_w = w
        target_h = target_w * ratio
    if target_h > h:
        target_h = h
        target_w = target_h * ratio
    cx = (x0 + x1) / 2.0
    cy = y0 + fh * 0.02
    left = max(0, min(cx - target_w / 2.0, w - target_w))
    top = max(0, min(cy - target_h * 0.40, h - target_h))
    out = img[int(top):int(top + target_h), int(left):int(left + target_w)]
    return cv2.resize(out, (int(round(target_w)), int(round(target_h))),
                      interpolation=cv2.INTER_LANCZOS4)


# ------------------------------------------------------------- main
def main():
    img = load(SRC)
    orig = img.copy()
    h, w = img.shape[:2]
    face, eyes = detect_face(img)
    print("rosto:", face, "olhos:", eyes, "img:", (w, h))

    blur = cv2.fastNlMeansDenoisingColored(img, None, 3, 3, 7, 21)
    img = cv2.addWeighted(img, 0.30, blur, 0.70, 0)

    person = grabcut_person(img, face)
    print("cobertura pessoa: %.2f" % person.mean())

    skin = skin_mask(img)
    img = matte_skin(img, skin)
    img = even_skin_tone(img, skin, 0.30)
    img = studio_light(img, person, strength=0.30)
    img = dodge_burn(img, face, person)
    img = color_grade(img)
    img = eye_enhance(img, face, person, eyes)
    fmask = face_sharp_mask(face, img.shape[:2])
    img = selective_sharpen(img, fmask, amount=0.70, radius=1.5)
    img = separate_background(img, person)
    img = vignette(img, 0.22)

    OUTDIR.mkdir(parents=True, exist_ok=True)
    out_full = OUTDIR / "retrato_profissional_full.png"
    out_crop = OUTDIR / "retrato_profissional_4x5.png"
    cv2.imwrite(str(out_full), cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_RGB2BGR))
    crop = crop_portrait(img, face, 4 / 5)
    cv2.imwrite(str(out_crop), cv2.cvtColor(crop.astype(np.uint8), cv2.COLOR_RGB2BGR))

    h2 = 760
    w2 = int(w * h2 / h)
    cmp_img = np.hstack([cv2.resize(orig, (w2, h2)), cv2.resize(img.astype(np.uint8), (w2, h2))])
    cv2.imwrite(str(OUTDIR / "comparativo.png"),
                cv2.cvtColor(cmp_img, cv2.COLOR_RGB2BGR))
    print("gravado:", out_full, "|", out_crop, "| comparativo.png")


if __name__ == "__main__":
    main()
