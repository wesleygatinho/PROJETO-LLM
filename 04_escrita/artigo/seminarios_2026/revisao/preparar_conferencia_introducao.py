"""Leitura documental, imagens de conferência e hashes de preservação; sem inferência."""
from pathlib import Path
import json, hashlib, sys, csv
import pypdfium2 as pdfium
from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[4]
REF = ROOT / "02_referencias/verificacao_introducao_seminarios_2026"
OUT = Path(__file__).resolve().parent / "introducao_2026-10-07"
OUT.mkdir(exist_ok=True)

historical = []
for base in ("03_experimentos",):
    for path in sorted((ROOT/base).rglob("*")):
        if path.is_file():
            historical.append({"arquivo":path.relative_to(ROOT).as_posix(),"sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
(OUT/"preservacao_antes.json").write_text(json.dumps(historical,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
records=json.loads((REF/"inventario_pdf.json").read_text(encoding="utf-8"))
selections={"primevul":[2,6],"risse":[2,7],"huang":[2,4,7],"qwen":[1,4],"lora":[1,4],"qlora":[1,4]}
for record in records:
    doc=pdfium.PdfDocument(str(ROOT/record["pdf"]))
    for page in selections[record["id"]]:
        im=doc[page-1].render(scale=1.4).to_pil()
        im.save(REF/f"{record['id']}_p{page:02d}.png")
    doc.close()
print("PDFs renderizados para conferência: ",selections)
for file in ("treinos_etapa3.csv","resultados_etapa3.csv"):
    with (ROOT/"03_experimentos/resultados"/file).open(encoding="utf-8-sig",newline="") as handle:
        rows=[r for r in csv.DictReader(handle) if r.get("depuracao")=="nao"]
    print(file, [{k:r.get(k) for k in ("modelo","seed","variante","benignas_por_vul","epocas","parear_tamanho","max_tokens","log_prefixo")} for r in rows])
print("Preservação:",len(historical),"arquivos; conteúdo histórico apenas lido.")
