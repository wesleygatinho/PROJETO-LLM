"""Extração direta dos PDFs primários locais; nenhuma chamada de modelo ou experimento."""
from pathlib import Path
from hashlib import sha256
import json
import sys
from pypdf import PdfReader
sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
PDFS = {
    "primevul": "Datasets e benchmarks/Ding, Y - 2024.pdf",
    "risse": "Ref Adicionadas/Niklas Risse - 2024.pdf",
    "huang": "Deteccao de vulnerabilidade métodos e modelos/Feiyang Huang - 2026.pdf",
    "qwen": "Modelos de código/Hui, B - 2024.pdf",
    "lora": "Eficiência quantizacao PEFT e destilacao/Hu, E - 2021.pdf",
    "qlora": "Eficiência quantizacao PEFT e destilacao/Dettmers, T - 2023.pdf",
}
records = []
for key, relative in PDFS.items():
    path = ROOT / "02_referencias/pdfs das referencias" / relative
    reader = PdfReader(path)
    text = "\n\n".join(f"=== PÁGINA FÍSICA {i} ===\n{page.extract_text(extraction_mode='layout')}" for i, page in enumerate(reader.pages, 1))
    target = OUT / f"{key}_pdf.txt"
    target.write_text(text, encoding="utf-8")
    records.append({"id":key,"pdf":path.relative_to(ROOT).as_posix(),"sha256_pdf":sha256(path.read_bytes()).hexdigest(),"paginas":len(reader.pages),"extracao":target.relative_to(ROOT).as_posix(),"sha256_extracao":sha256(target.read_bytes()).hexdigest(),"metadados_pdf":{str(k):str(v) for k,v in (reader.metadata or {}).items()}})
    print(key, len(reader.pages), text[:900].replace("\n", " "))
(OUT / "inventario_pdf.json").write_text(json.dumps(records, ensure_ascii=False, indent=2)+"\n",encoding="utf-8")
