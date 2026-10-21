import sys, numpy as np, cv2
sys.path.insert(0, r"D:\UFMA UNIVERSIDADE\MESTRADO - ESTUDO LLM\tmp\retrato")
from retrato_v2 import load, detect_face, SRC, OUTDIR

img = load(SRC)
face, eyes = detect_face(img)
vis = img.copy()
x0,y0,x1,y1 = face
cv2.rectangle(vis,(x0,y0),(x1,y1),(0,255,0),4)
for (cx,cy) in eyes:
    cv2.circle(vis,(int(cx),int(cy)),16,(255,0,0),4)
cv2.imwrite(str(OUTDIR/"debug_boxes.png"), cv2.cvtColor(vis, cv2.COLOR_RGB2BGR))
print("box refinado", face, "eyes", eyes)

# haar puro
gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY); eq = cv2.equalizeHist(gray)
fc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
faces = fc.detectMultiScale(eq, 1.05, 4, minSize=(150,150))
vis2 = img.copy()
for f in faces:
    x,y,fw,fh = [int(v) for v in f]
    cv2.rectangle(vis2,(x,y),(x+fw,y+fh),(255,255,0),4)
cv2.imwrite(str(OUTDIR/"debug_haar.png"), cv2.cvtColor(vis2, cv2.COLOR_RGB2BGR))
print("haar", [tuple(int(v) for v in f) for f in faces])
