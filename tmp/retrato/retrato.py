"""
Pipeline de revelacao digital para retrato profissional ("homem mais serio").
Entrada: foto original (Downloads). Saida: PNG em output/retrato.

Etapas:
  1. leitura + orientacao + limpeza leve de artefatos
  2. estimativa de fundo (moldura) e mascara de fundo
  3. matte de pele (supressao de specular highlight -> remove brilho de testa/bochecha)
  4. luz de estudio simulada (key light diagonal + fill)
  5. grade de cor (contraste em curva S, neutro frio nas sombras, pele natural)
  6. nitidez seletiva (olhos, sobrancelha, contorno do rosto)
  7. separacao de fundo (dessaturar + escurecer + blur de profundidade)
  8. vinheta e recorte 4:5
"""

import sys
import numpy as np
import cv2
from pathlib import Path

SRC = Path(sys.argv[1] if len(sys.argv) > 1
           else r"C:\Users\santo\Downloads\foto foto foto.jpeg")
OUTDIR = Path(sys.argv[2] if len(sys.argv) > 2
              else r"D:\UFMA UNIVERSIDADE\MESTRADO - ESTUDO LLM\output\retrato")


# ---------------------------------------------------------------- utilidades
def luma(img):
    return 0.299 * img[..., 0] + 0.587 * img[..., 1] + 0.114 * img[..., 2]


def smooth(x, sigma):
    """Blur gaussiano com borda refletida (sigma em px)."""
    k = int(max(3, sigma * 4)) | 1
    return cv2.GaussianBlur(x, (k, k), sigma, borderType=cv2.BORDER_REFLECT101)


def s_curve(x, amount):
    """Curva S suave. amount=0 -> identidade."""
    y = x / 255.0
    y = y + amount * (y - 0.5) * (1.0 - np.abs(2.0 * y - 1.0)) / 2.0
    return np.clip(y, 0, 1) * 255.0


def luma_of(img):
    return luma(img)


# ---------------------------------------------------------------- 1. leitura
def load(path):
    data = np.fromfile(str(path), dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if img is None:
        raise SystemExit(f"nao consegui abrir: {path}")
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def denoise_light(img, amount=0.35):
    """Denoise suave preservando textura da pele."""
    blur = cv2.fastNlMeansDenoisingColored(img, None, 3, 3, 7, 21)
    return cv2.addWeighted(img, amount, blur, 1 - amount, 0)


# ---------------------------------------------------------------- 2. fundo
def estimate_background(img, face_box, frame_frac=0.10):
    """Estima cor do fundo pela moldura, excluindo a area do rosto."""
    h, w = img.shape[:2]
    m = np.zeros((h, w), np.float32)
    fh = int(h * frame_frac)
    fw = int(w * frame_frac)
    m[:fh, :] = 1
    m[-fh:, :] = 1
    m[:, :fw] = 1
    m[:, -fw:] = 1
    x0, y0, x1, y1 = face_box
    pad = int((x1 - x0) * 0.35)
    m[max(0, y0 - pad):min(h, y1 + pad), max(0, x0 - pad):min(w, x1 + pad)] = 0
    if m.sum() < 100:
        m = np.ones((h, w), np.float32)
    bg_mean = np.array([img[..., c][m > 0].mean() for c in range(3)], np.float32)
    return bg_mean, m


def background_mask(img, face_box):
    """Mascara de fundo: 0 = fundo, 1 = pessoa.

    Combina (a) diferenca de cor do fundo estimado, (b) distancia ao centro
    do rosto, (c) skin-tone, e aplica retangularizacao suave.
    """
    h, w = img.shape[:2]
    bg_mean, frame = estimate_background(img, face_box)
    diff = np.linalg.norm(img.astype(np.float32) - bg_mean[None, None, :], axis=2)
    diff_n = np.clip(diff / max(20.0, np.percentile(diff, 92)), 0, 1)

    x0, y0, x1, y1 = face_box
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    rad = np.sqrt(((xx - cx) / (w * 0.62)) ** 2 + ((yy - cy) / (h * 0.62)) ** 2)
    center_n = np.clip(1.0 - rad, 0, 1)

    # skin tone (YCrCb) reforca o centro/pessoa
    ycrcb = cv2.cvtColor(img, cv2.COLOR_RGB2YCrCb).astype(np.float32)
    skin = ((ycrcb[..., 1] > 133) & (ycrcb[..., 1] < 180) &
            (ycrcb[..., 2] > 77) & (ycrcb[..., 2] < 130)).astype(np.float32)
    skin = smooth(skin, 3.0)

    person = np.clip(0.55 * diff_n + 0.25 * center_n + 0.20 * skin, 0, 1)
    person = smooth(person, 6.0)
    person = np.clip((person - 0.32) / 0.5, 0, 1)
    person = smooth(person, 4.0)
    return person


# ---------------------------------------------------------------- 3. pele
def skin_mask(img):
    ycrcb = cv2.cvtColor(img, cv2.COLOR_RGB2YCrCb).astype(np.float32)
    m = ((ycrcb[..., 1] > 132) & (ycrcb[..., 1] < 182) &
         (ycrcb[..., 2] > 74) & (ycrcb[..., 2] < 132) &
         (ycrcb[..., 0] > 40)).astype(np.float32)
    return smooth(m, 4.0)


def matte_skin(img, skin):
    """Clamp de specular: rebaixa pixels de pele muito claros rumo a media local.

    Reduz o brilho de testa/bochechas e o aspecto 'sudado', que e o que mais
    denuncia uma foto casual em leitura de retrato.
    """
    L = luma(img)
    local = smooth(L, 12.0)
    hi = np.clip((L - local - 8.0) / 45.0, 0, 1) * skin
    # preserva um pouco de brilho (nao deixa a pele plastica)
    target = local - 6.0
    L2 = L * (1 - hi) + np.minimum(L, target) * hi
    ratio = (L2 + 1.0) / (L + 1.0)
    out = img.astype(np.float32) * ratio[..., None]
    return np.clip(out, 0, 255)


def even_skin_tone(img, skin, strength=0.35):
    """Suaviza variacao de tom (vermelhidor/olheiras) mantendo textura."""
    L = luma(img)
    local = smooth(L, 25.0)
    corr = np.clip((local - L) * 0.5 * strength * skin, -18, 18)
    out = img.astype(np.float32) + corr[..., None]
    return np.clip(out, 0, 255)


# ---------------------------------------------------------------- 4. luz
def studio_light(img, person, key=(-0.55, -0.62), strength=0.30):
    """Simula key light diagonal + fill suave, limitado a area da pessoa."""
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    nx = (xx / w - 0.5) * 2.0
    ny = (yy / h - 0.5) * 2.0
    kx, ky = key
    field = -(nx * kx + ny * ky)          # luz vem da diagonal
    field = np.clip(field / 1.15, -1, 1)
    field = smooth(field, 45.0)
    field = (field - field.min()) / (field.max() - field.min() + 1e-6)

    L = luma(img)
    # luz aditiva nas altas luzes, sombra nas baixas (key light de verdade)
    hi = np.clip((L - 110.0) / 120.0, 0, 1)
    lo = np.clip((105.0 - L) / 105.0, 0, 1)
    add = (hi * 0.75 + 0.25) * field * 46.0 * strength * person
    sub = lo * (1.0 - field) * 20.0 * strength * person
    out = img.astype(np.float32) + (add - sub)[..., None]
    return np.clip(out, 0, 255)


def dodge_burn(img, face_box, person):
    """Escurece laterais do rosto e Harmoniza contorno mandibular."""
    h, w = img.shape[:2]
    x0, y0, x1, y1 = face_box
    cx = (x0 + x1) / 2.0
    width = (x1 - x0) * 0.62
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    side = np.clip(np.abs(xx - cx) / width, 0, 1.6)
    # sobe ate a altura dos olhos
    brow = y0 + (y1 - y0) * 0.30
    vert = np.clip((yy - brow) / max(1.0, (y1 - brow) * 0.55), 0, 1)
    burn = np.clip((side - 0.85) * 0.9, 0, 1) * vert * person
    out = img.astype(np.float32) - (burn * 16.0)[..., None]
    return np.clip(out, 0, 255)


# ---------------------------------------------------------------- 5. cor
def color_grade(img, person):
    """Neutro frio nas sombras, pele natural, contraste em curva S."""
    x = img.astype(np.float32) / 255.0

    # curva S de contraste (leve, para nao estourar pele)
    x = x + 0.16 * (x - 0.5) * (1.0 - np.abs(2.0 * x - 1.0)) / 2.0

    L = luma(img)
    lo = np.clip((0.55 - L / 255.0) / 0.55, 0, 1)     # peso das sombras
    hi = np.clip((L / 255.0 - 0.45) / 0.55, 0, 1)     # peso das altas luzes

    # sombras puxam para o azul (ar/seriedade), altas luzes ficam neutras quentes
    shadow_tint = np.array([0.965, 0.985, 1.045], np.float32)
    high_tint = np.array([1.015, 1.000, 0.985], np.float32)
    tint = (lo[..., None] * shadow_tint + hi[..., None] * high_tint)
    x = x * tint

    # dessatura global leve + skin natural (retira vermelho/orange do relogio)
    hsv = cv2.cvtColor(np.clip(x * 255, 0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
    sat_scale = np.ones(hsv.shape[:2], np.float32) * 0.86
    # pele: reduzir saturação excessiva sem matar cor natural
    skin = skin_mask(np.clip(x * 255, 0, 255).astype(np.uint8))
    sat_scale = sat_scale * (1 - 0.22 * skin)
    hsv[..., 1] = np.clip(hsv[..., 1] * sat_scale, 0, 255)
    x = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32) / 255.0

    return np.clip(x * 255.0, 0, 255)


# ---------------------------------------------------------------- 6. nitidez
def face_sharp_mask(img, face_box):
    h, w = img.shape[:2]
    x0, y0, x1, y1 = face_box
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    ell = ((xx - cx) / ((x1 - x0) * 0.52)) ** 2 + ((yy - cy) / ((y1 - y0) * 0.60)) ** 2
    m = np.clip(1.0 - ell, 0, 1).astype(np.float32)
    return smooth(m, 8.0)


def selective_sharpen(img, mask, amount=0.85, radius=1.6):
    blur = cv2.GaussianBlur(img, (0, 0), radius)
    out = img.astype(np.float32) * (1 + amount * mask[..., None]) - \
        blur.astype(np.float32) * (amount * mask[..., None])
    return np.clip(out, 0, 255)


def eye_enhance(img, face_box, person):
    """Escurece levemente linha ciliares/cavidade dos olhos -> olhar mais firme."""
    h, w = img.shape[:2]
    x0, y0, x1, y1 = face_box
    fw, fh = x1 - x0, y1 - y0
    eye_y = y0 + fh * 0.455
    eye_h = fh * 0.105

    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    m = np.zeros((h, w), np.float32)
    for ex in (0.325, 0.675):
        cx = x0 + fw * ex
        ell = ((xx - cx) / (fw * 0.135)) ** 2 + ((yy - eye_y) / eye_h) ** 2
        m = np.maximum(m, np.clip(1.0 - ell, 0, 1))
    m = smooth(m, 3.0) * person

    L = luma(img)
    dark = np.clip((1.0 - L / 200.0), 0, 1)
    out = img.astype(np.float32) - (m * dark * 22.0)[..., None]
    out += (m * np.clip((L - 60.0) / 150.0, 0, 1) * 8.0)[..., None]
    return np.clip(out, 0, 255)


# ---------------------------------------------------------------- 7. fundo
def separate_background(img, person):
    """Escurece e dessatura o fundo, com leve desfoque (profundidade)."""
    alpha = person[..., None]
    blur = cv2.GaussianBlur(img, (0, 0), 2.2)
    img = img * alpha + blur * (1 - alpha)

    bg = 1.0 - person
    L = luma(img)
    b = img.astype(np.float32) * 0.62 + np.array([16, 18, 24], np.float32) * (1 - bg)[..., None]
    # ajusta luminancia do fundo
    target = 74.0
    bL = luma(b)
    scale = np.where(bL > 1, target / np.maximum(bL, 1.0), 1.0)
    b = b * scale[..., None]
    # dessatura o fundo
    bL = luma(b)
    b = bL[..., None] * 0.72 + b * 0.28
    # leve tom frio no fundo, para separar do sujeito
    b = b * np.array([0.93, 0.97, 1.06], np.float32)

    out = img * alpha + b * (1 - alpha)
    return np.clip(out, 0, 255)


# ---------------------------------------------------------------- 8. final
def vignette(img, amount=0.30):
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    nx = (xx / w - 0.5) * 2.0
    ny = (yy / h - 0.5) * 2.0
    r = np.sqrt(nx ** 2 * 0.9 + ny ** 2)
    v = 1.0 - amount * np.clip((r - 0.55) / 0.85, 0, 1) ** 1.7
    return np.clip(img.astype(np.float32) * v[..., None], 0, 255)


def crop_portrait(img, face_box, ratio=4/5):
    """Recorte vertical de retrato, com rosto no terco superior."""
    h, w = img.shape[:2]
    x0, y0, x1, y1 = face_box
    fh = y1 - y0

    # altura desejada a partir da posicao do rosto
    target_h = fh * 3.05
    target_w = target_h / ratio
    if target_w > w:
        target_w = w
        target_h = target_w * ratio

    # centro: rosto ligeiramente acima do centro geometrico
    cx = (x0 + x1) / 2.0
    cy = y0 + fh * 0.06
    left = cx - target_w / 2.0
    top = cy - target_h * 0.42
    left = max(0, min(left, w - target_w))
    top = max(0, min(top, h - target_h))
    out = img[int(top):int(top + target_h), int(left):int(left + target_w)]
    return cv2.resize(out, (int(round(target_w)), int(round(target_h))),
                      interpolation=cv2.INTER_LANCZOS4)


def detect_face(img):
    cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray = cv2.equalizeHist(gray)
    faces = cascade.detectMultiScale(gray, 1.08, 5, minSize=(120, 120))
    if len(faces) == 0:
        faces = cascade.detectMultiScale(gray, 1.03, 3, minSize=(100, 100))
    if len(faces) == 0:
        h, w = img.shape[:2]
        return (int(w * 0.25), int(h * 0.15), int(w * 0.75), int(h * 0.60))
    return max(faces, key=lambda f: f[2] * f[3])


# ---------------------------------------------------------------- main
def main():
    img = load(SRC)
    orig = img.copy()
    h, w = img.shape[:2]
    face = detect_face(img)
    print("rosto:", face, " imagem:", (w, h))

    img = denoise_light(img, 0.30)
    person = background_mask(img, face)
    skin = skin_mask(img)

    img = matte_skin(img, skin)
    img = even_skin_tone(img, skin, 0.30)
    img = studio_light(img, person, strength=0.32)
    img = dodge_burn(img, face, person)
    img = color_grade(img, person)
    img = eye_enhance(img, face, person)
    fmask = face_sharp_mask(img, face)
    img = selective_sharpen(img, fmask, amount=0.75, radius=1.5)
    img = separate_background(img, person)
    img = vignette(img, 0.32)

    # a cor precisa ser recalculada sobre a imagem final
    img = color_grade(img, person)
    img = selective_sharpen(img, fmask, amount=0.40, radius=1.2)
    img = vignette(img, 0.20)

    OUTDIR.mkdir(parents=True, exist_ok=True)
    out_full = OUTDIR / "retrato_profissional_full.png"
    out_crop = OUTDIR / "retrato_profissional_4x5.png"
    cv2.imwrite(str(out_full), cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_RGB2BGR))
    crop = crop_portrait(img, face, 4 / 5)
    cv2.imwrite(str(out_crop), cv2.cvtColor(crop.astype(np.uint8), cv2.COLOR_RGB2BGR))
    print("gravado:", out_full)
    print("gravado:", out_crop)

    # comparativo lado a lado para conferencia
    h2 = 700
    w2 = int(w * h2 / h)
    small_o = cv2.resize(orig, (w2, h2))
    small_n = cv2.resize(img.astype(np.uint8), (w2, h2))
    cv2.imwrite(str(OUTDIR / "comparativo.png"),
                cv2.cvtColor(np.hstack([small_o, small_n]), cv2.COLOR_RGB2BGR))
    print("gravado:", OUTDIR / "comparativo.png")


if __name__ == "__main__":
    main()
