#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Converte PDFs em Markdown.

Dois modos:
  - page  (padrao): renderiza cada pagina como imagem e usa o Gemini (visao)
                    para gerar o markdown completo -> texto + figuras + tabelas.
  - text  (fallback): usa o markitdown para extrair apenas o texto (sem interpretar
                    imagens embutidas). Nao precisa de chave de API.

Uso:
  python convert.py                 # converte tudo em modo page
  python convert.py --mode text     # so texto, via markitdown
  python convert.py --only "Hu, E"  # filtra pelos PDFs cujo caminho contem o texto
  python convert.py --force         # reconverte mesmo se o .md ja existir
"""

import argparse
import base64
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

# ----------------------------------------------------------------------------
# Configuracao
# ----------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
INPUT_DIR = (HERE.parent / "pdfs das referencias").resolve()
OUTPUT_DIR = (HERE / "markdown_output").resolve()

# Backends disponiveis para o modo "page" (visao).
# ollama = modelo LOCAL (padrao); gemini = API na nuvem.
BACKENDS = {
    "ollama": {
        "base_url": os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        "model": os.environ.get("OLLAMA_MODEL", "qwen2.5vl:7b"),
        "api_key": "ollama",  # dummy; o Ollama nao exige chave
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "model": os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
        "api_key": os.environ.get("GEMINI_API_KEY", ""),
    },
}

# DPI para rasterizar cada pagina. Local (8GB VRAM) vai melhor com ~140-150.
PAGE_DPI = int(os.environ.get("PAGE_DPI", "150"))

# Pausa entre chamadas (util so na nuvem, por limite de taxa).
SLEEP_BETWEEN_CALLS = float(os.environ.get("SLEEP_BETWEEN_CALLS", "0"))

PROMPT_PAGINA = """Voce e um transcritor de artigos cientificos. Converta ESTA pagina do PDF para Markdown fiel e completo, em portugues quando o original estiver em portugues e mantendo o idioma original caso contrario.

Regras:
- Transcreva TODO o texto visivel: titulos (use #, ##, ###), paragrafos, listas, notas de rodape e legendas.
- Equacoes: use LaTeX entre $...$ (inline) ou $$...$$ (bloco).
- Tabelas: reproduza como tabela Markdown, preservando linhas e colunas.
- Para cada FIGURA, GRAFICO ou DIAGRAMA: insira um bloco de citacao iniciado por "> **[Figura]**" com uma descricao objetiva e detalhada do que a imagem mostra (eixos, tendencias, valores, arquitetura etc.). Se houver dados numericos legiveis no grafico, liste-os.
- NAO invente conteudo que nao esteja na pagina. Se algo estiver ilegivel, escreva "[ilegivel]".
- NAO adicione comentarios seus, cercas de codigo ```markdown, nem repita estas instrucoes. Devolva apenas o conteudo da pagina em Markdown.
- Nao repita cabecalhos/rodapes de revista em toda pagina se forem apenas numeracao; mantenha o numero da pagina fora do corpo.
"""


# ----------------------------------------------------------------------------
# Modo TEXT (markitdown)
# ----------------------------------------------------------------------------
def convert_text(pdf_path: Path) -> str:
    from markitdown import MarkItDown

    md = MarkItDown()
    result = md.convert(str(pdf_path))
    return result.text_content or ""


# ----------------------------------------------------------------------------
# Modo PAGE (Gemini visao)
# ----------------------------------------------------------------------------
def get_client(backend: str):
    from openai import OpenAI

    cfg = BACKENDS[backend]
    if backend == "gemini" and not cfg["api_key"]:
        sys.exit(
            "ERRO: defina GEMINI_API_KEY no .env para usar o backend gemini.\n"
            "Pegue a chave em https://aistudio.google.com/apikey"
        )
    # timeout alto: geracao local pode levar dezenas de segundos por pagina
    client = OpenAI(api_key=cfg["api_key"], base_url=cfg["base_url"], timeout=600.0)
    return client, cfg["model"]


def page_to_png_b64(page, dpi: int) -> str:
    import pymupdf  # noqa

    pix = page.get_pixmap(dpi=dpi)
    return base64.b64encode(pix.tobytes("png")).decode("ascii")


def describe_page(client, model: str, png_b64: str) -> str:
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT_PAGINA},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{png_b64}"
                        },
                    },
                ],
            }
        ],
        temperature=0.1,
    )
    return (resp.choices[0].message.content or "").strip()


def convert_page(pdf_path: Path, client, model: str) -> str:
    import pymupdf

    doc = pymupdf.open(str(pdf_path))
    parts = []
    n = doc.page_count
    for i, page in enumerate(doc, start=1):
        t0 = time.time()
        print(f"    pagina {i}/{n} ...", end="", flush=True)
        png_b64 = page_to_png_b64(page, PAGE_DPI)
        try:
            md = describe_page(client, model, png_b64)
        except Exception as e:  # noqa
            md = f"> **[ERRO ao processar a pagina {i}]** {e}"
        # remove cercas ```markdown que o modelo possa devolver
        md = md.removeprefix("```markdown").removeprefix("```").removesuffix("```").strip()
        parts.append(f"<!-- pagina {i} -->\n\n{md}")
        print(f" ok ({time.time() - t0:.0f}s)", flush=True)
        if SLEEP_BETWEEN_CALLS:
            time.sleep(SLEEP_BETWEEN_CALLS)
    doc.close()
    return "\n\n---\n\n".join(parts)


# ----------------------------------------------------------------------------
# Orquestracao
# ----------------------------------------------------------------------------
def main():
    load_dotenv(HERE / ".env")

    ap = argparse.ArgumentParser(description="Converte PDFs em Markdown.")
    ap.add_argument("--mode", choices=["page", "text"], default="page",
                    help="page = visao (padrao); text = markitdown so texto")
    ap.add_argument("--backend", choices=["ollama", "gemini"], default="ollama",
                    help="backend do modo page: ollama (local, padrao) ou gemini")
    ap.add_argument("--only", default=None,
                    help="processa apenas PDFs cujo caminho contenha este texto")
    ap.add_argument("--force", action="store_true",
                    help="reconverte mesmo que o .md ja exista")
    args = ap.parse_args()

    if not INPUT_DIR.exists():
        sys.exit(f"ERRO: pasta de entrada nao encontrada: {INPUT_DIR}")

    pdfs = sorted(INPUT_DIR.rglob("*.pdf"))
    if args.only:
        pdfs = [p for p in pdfs if args.only.lower() in str(p).lower()]
    if not pdfs:
        sys.exit("Nenhum PDF encontrado com esse filtro.")

    client = model = None
    if args.mode == "page":
        client, model = get_client(args.backend)

    tag = f"{args.mode}" + (f"/{args.backend}:{model}" if args.mode == "page" else "")
    print(f"Modo: {tag} | PDFs: {len(pdfs)} | saida: {OUTPUT_DIR}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    ok = skip = fail = 0
    for idx, pdf in enumerate(pdfs, start=1):
        rel = pdf.relative_to(INPUT_DIR).with_suffix(".md")
        out = OUTPUT_DIR / rel
        out.parent.mkdir(parents=True, exist_ok=True)

        print(f"[{idx}/{len(pdfs)}] {rel}")
        if out.exists() and not args.force:
            print("    (ja existe, pulando -- use --force para refazer)")
            skip += 1
            continue

        try:
            if args.mode == "text":
                body = convert_text(pdf)
            else:
                body = convert_page(pdf, client, model)
            header = f"# {pdf.stem}\n\n_Fonte: `{pdf.name}` | conversao: {tag}_\n\n---\n\n"
            out.write_text(header + body, encoding="utf-8")
            print(f"    -> {out}")
            ok += 1
        except Exception as e:  # noqa
            print(f"    FALHOU: {e}")
            fail += 1

    print(f"\nConcluido. Convertidos: {ok} | Pulados: {skip} | Falhas: {fail}")


if __name__ == "__main__":
    main()
