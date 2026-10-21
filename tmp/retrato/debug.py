import sys, numpy as np, cv2
sys.path.insert(0, r"D:\UFMA UNIVERSIDADE\MESTRADO - ESTUDO LLM\tmp\retrato")
from retrato_v2 import load, detect_face, luma, grabcut_person, fallback_person, SRC, OUTDIR

img = load(SRC)
h, w = img.shape[:2]

# haar puro, sem refino
gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
eq = cv2.equalizeHist(gray)
fc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
for sf in (1.05, 1.01):
    faces = fc.detectMultiScale(eq, sf, 4, minSize=(150,150))
    print("haar scale", sf, "->", [tuple(int(v) for v in f) for f in faces])
    if len(faces): break

face, eyes = detect_face(img)
print("refinado:", face, "olhos:", eyes)

# captura a excecao do grabcut
mask = np.zeros((h,w), np.uint8)
x0,y0,x1,y1 = face
fw,fh = x1-x0, y1-y0
mask[y0:y1, x0:x1] = cv2.GC_FGD
neck = int(fh*0.55)
mask[y1:y1+neck, x0+int(fw*0.18):x1-int(fw*0.18)] = cv2.GC_PR_FGD
body_top = y1+neck
mask[body_top:h, int(x0-fw*0.35):int(x1+fw*0.35)] = cv2.GC_PR_FGD
band = int(fw*0.30)
mask[:, :max(0,x0-band)] = cv2.GC_PR_BGD
mask[:, min(w,x1+band):] = cv2.GC_PR_BGD
mask[:max(0,y0-int(fh*0.55)),:] = cv2.GC_PR_BGD
print("init hist:", {int(k): int((mask==k).sum()) for k in [0,1,2,3]})
bgd = np.zeros((1,65), np.float64); fgd = np.zeros((1,65), np.float64)
try:
    cv2.grabCut(img, mask, None, bgd, fgd, 5, cv2.GC_INIT_WITH_MASK)
    print("grabcut OK")
except cv2.error as e:
    print("grabcut EXC:", e)

person = np.where((mask==cv2.GC_FGD)|(mask==cv2.GC_PR_FGD),1.0,0.0)
print("cobertura grabcut: %.3f" % person.mean())
bg_sel = person < 0.5
print("mediana luma fundo (por grabcut):", float(np.median(luma(img)[bg_sel])))

# mascara
vis = img.copy()
vis[person>0.5] = (0.5*vis[person>0.5] + 0.5*np.array([255,0,0])).astype(np.uint8)
cv2.imwrite(str(OUTDIR/"debug_grabcut.png"), cv2.cvtColor(vis, cv2.COLOR_RGB2BGR))

# com haar puro (sem refino)
faces = fc.detectMultiScale(eq, 1.05, 4, minSize=(150,150))
if len(faces):
    fb = max(faces, key=lambda f: f[2]*f[3])
    fb = (int(fb[0]),int(fb[1]),int(fb[0]+fb[2]),int(fb[1]+fb[3]))
    p2 = grabcut_person(img, fb)
    print("cobertura com haar puro:", p2.mean(), "box", fb)
    vis2 = img.copy()
    vis2[p2>0.5] = (0.5*vis2[p2>0.5] + 0.5*np.array([0,255,0])).astype(np.uint8)
    cv2.imwrite(str(OUTDIR/"debug_grabcut_haar.png"), cv2.cvtColor(vis2, cv2.COLOR_RGB2BGR))

print("luma stats imagem:", luma(img).min(), luma(img).mean(), luma(img).max())
