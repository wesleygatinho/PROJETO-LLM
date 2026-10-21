import sys, numpy as np, cv2
sys.path.insert(0, r"D:\UFMA UNIVERSIDADE\MESTRADO - ESTUDO LLM\tmp\retrato")
from retrato_v2 import load, luma, smooth, SRC, OUTDIR

img = load(SRC)
h, w = img.shape[:2]
x0,y0,x1,y1 = 298,406,828,1085   # caixa refinado (olhos)
fh, fw = y1-y0, x1-x0

def show(mask, name):
    vis = img.copy()
    m = mask > 0.5
    vis[m] = (0.45*vis[m] + 0.55*np.array([255,0,0])).astype(np.uint8)
    cv2.imwrite(str(OUTDIR/f"mask_{name}.png"), cv2.cvtColor(vis, cv2.COLOR_RGB2BGR))
    print(name, "cobertura %.3f" % m.mean())

# ---- A: GrabCut init por mascara, ordem corrigida (PR_BGD so nas bordas reais)
mask = np.zeros((h,w), np.uint8)
mask[y0:y1, x0:x1] = cv2.GC_FGD
neck = int(fh*0.55)
mask[y1:y1+neck, x0+int(fw*0.20):x1-int(fw*0.20)] = cv2.GC_FGD     # pescoco = sure FG
body_top = y1+neck
mask[body_top:h, int(x0-fw*0.55):int(x1+fw*0.55)] = cv2.GC_PR_FGD   # torso
# fundo certo: parede (acima da cabeca, fora dos ombros)
mask[:max(0,y0-int(fh*0.45)), :] = cv2.GC_PR_BGD
band = int(fw*0.42)
mask[:, :max(0,x0-band)] = cv2.GC_PR_BGD
mask[:, min(w,x1+band):] = cv2.GC_PR_BGD
bgd=np.zeros((1,65),np.float64); fgd=np.zeros((1,65),np.float64)
cv2.grabCut(img, mask, None, bgd, fgd, 8, cv2.GC_INIT_WITH_MASK)
A = np.where((mask==cv2.GC_FGD)|(mask==cv2.GC_PR_FGD),1.0,0.0)
show(smooth(A,2.0), "A_grabcut_mask")

# ---- B: GrabCut init por retangulo (pessoa inteira)
maskB = np.zeros((h,w), np.uint8)
rect = (int(x0-fw*0.45), int(y0-fh*0.35), int(fw*1.9), int(h-(y0-fh*0.35)))
maskB[:rect[1],:] = cv2.GC_PR_BGD
maskB[rect[1]+rect[3]:,:] = cv2.GC_PR_BGD
maskB[:, :rect[0]] = cv2.GC_PR_BGD
maskB[:, rect[0]+rect[2]:] = cv2.GC_PR_BGD
maskB[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+rect[2]] = cv2.GC_PR_FGD
maskB[rect[1]+int(rect[3]*0.45):rect[1]+rect[3], rect[0]:rect[0]+rect[2]] = cv2.GC_FGD
bgd=np.zeros((1,65),np.float64); fgd=np.zeros((1,65),np.float64)
cv2.grabCut(img, maskB, None, bgd, fgd, 8, cv2.GC_INIT_WITH_MASK)
B = np.where((maskB==cv2.GC_FGD)|(maskB==cv2.GC_PR_FGD),1.0,0.0)
show(smooth(B,2.0), "B_grabcut_rect")

# ---- C: cor da parede (brilho alto, baixa saturacao) + posicao
hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype(np.float32)
wall = ((hsv[...,2] > 150) & (hsv[...,1] < 45)).astype(np.float32)
wall = smooth(wall, 5.0)
person_c = 1.0 - wall
yy,xx = np.mgrid[0:h,0:w].astype(np.float32)
cx,cy = (x0+x1)/2, (y0+y1)/2
rad = np.sqrt(((xx-cx)/(w*0.60))**2 + ((yy-cy)/(h*0.75))**2)
person_c = np.clip(person_c + np.clip((rad-0.55)*0.8,0,1), 0, 1)
person_c = smooth(person_c, 6.0)
person_c = np.clip((person_c-0.35)/0.4,0,1)
show(person_c, "C_cor")

# ---- D: combinacao A com C (onde A diz fundo mas C diz pessoa -> C vence)
D = np.maximum(A, person_c*0.85)
D = smooth(D, 2.0)
D = np.clip((D-0.30)/0.45,0,1)
show(D, "D_combo")
