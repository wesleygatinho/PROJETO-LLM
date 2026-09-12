# PDFs → Markdown (local, com interpretação de imagens)

Converte os artigos de `../pdfs das referencias/` para Markdown, espelhando a
estrutura de subpastas em `markdown_output/`.

## Como funciona

- **Modo `page` (padrão) + backend `ollama` (padrão):** cada página do PDF é
  rasterizada em imagem e enviada a um **modelo de visão LOCAL** (Qwen2.5-VL via
  Ollama). Ele devolve o Markdown completo da página — texto, equações em LaTeX,
  tabelas e uma **descrição de cada figura/gráfico**. Roda offline, sem cota, sem
  custo.
- **Backend `gemini`:** mesmo modo, mas usando a API na nuvem (precisa de chave e
  respeita cota). Use `--backend gemini`.
- **Modo `text`:** usa o **markitdown** para extrair só o texto (sem interpretar
  imagens, sem modelo). Rápido e sem dependências externas.

## Pré-requisitos

1. Dependências Python:
   ```bash
   pip install -r requirements.txt
   ```
2. **Ollama** instalado e rodando (o instalador já sobe o servidor em segundo plano).
3. Modelo de visão baixado:
   ```bash
   ollama pull qwen2.5vl:7b
   ```
   Se faltar VRAM ou quiser mais velocidade, use `qwen2.5vl:3b` e ajuste o `.env`.

## Uso

```bash
python convert.py                       # tudo, local (ollama + qwen2.5vl:7b)
python convert.py --only "Hu, E"        # só PDFs cujo caminho contém o texto
python convert.py --force               # reconverte mesmo se o .md já existir
python convert.py --backend gemini      # usa a nuvem (precisa GEMINI_API_KEY no .env)
python convert.py --mode text           # só texto, via markitdown
```

A conversão é **retomável**: PDFs que já têm `.md` são pulados (use `--force`).
O console mostra o tempo de cada página.

## Ajustes (`.env`, opcional)

| Variável | Padrão | Efeito |
|---|---|---|
| `OLLAMA_MODEL` | `qwen2.5vl:7b` | modelo local. `qwen2.5vl:3b` = mais rápido, menos VRAM |
| `PAGE_DPI` | `150` | resolução da página; maior = mais nítido, mais VRAM/tempo |
| `OLLAMA_BASE_URL` | `http://localhost:11434/v1` | endpoint do Ollama |

## Dicas de desempenho (RTX 4060, 8 GB)

- `qwen2.5vl:7b` cabe justo em 8 GB. Se o Ollama jogar camadas na CPU (fica lento),
  baixe o `PAGE_DPI` para 130 ou troque para `qwen2.5vl:3b`.
- Rode um teste com `--only` antes de processar os 41 PDFs.
- Para ver a VRAM em uso: `ollama ps`.
