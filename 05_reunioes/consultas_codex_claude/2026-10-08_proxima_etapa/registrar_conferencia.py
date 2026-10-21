"""Audita identidade das consultas e preservação das seis fontes; somente leitura delas."""
from pathlib import Path
import hashlib, json, datetime

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
sources = json.loads((OUT / "fontes_contexto.json").read_text(encoding="utf-8"))
checks = []
for source in sources:
    current = hashlib.sha256((ROOT / source["arquivo"]).read_bytes()).hexdigest()
    checks.append({**source, "sha256_depois": current, "inalterada": current == source["sha256"]})
calls = []
for name in ("01_resposta.json", "03_resposta_conferencia.json"):
    response = json.loads((OUT / name).read_text(encoding="utf-8"))
    calls.append({"resposta": name, "modelos": list(response.get("modelUsage", {})),
                  "session_id": response.get("session_id"), "is_error": response.get("is_error"),
                  "duration_ms": response.get("duration_ms"), "num_turns": response.get("num_turns"),
                  "custo_estimado_usd_cli": response.get("total_cost_usd")})
models_valid = all(c["modelos"] == ["claude-opus-5-5"] and c["is_error"] is False for c in calls)
session_ids = [c["session_id"] for c in calls]
distinct = all(session_ids) and len(set(session_ids)) == len(session_ids)
costs = [c["custo_estimado_usd_cli"] for c in calls]
total = sum(costs) if all(isinstance(c, (float, int)) for c in costs) else None
record = {"registrado_em_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
          "consultas": calls, "modelo_confirmado_em_ambas": models_valid,
          "sessoes_distintas": distinct, "custo_estimado_total_usd_cli": total,
          "dentro_limite_nominal_usd_3": total is not None and total <= 3,
          "fontes": checks, "seis_fontes_inalteradas": all(c["inalterada"] for c in checks),
          "limite": "Claude analisou textos anexados, sem verificar fontes primárias ou executar ferramentas. Custo CLI não comprova cobrança.",
          "escopo": "Consulta de planejamento; sem execução de P0–P4, treinamento, inferência, RunPod ou edição de históricos."}
(OUT / "auditoria_consultas.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: record[k] for k in ("modelo_confirmado_em_ambas", "sessoes_distintas", "custo_estimado_total_usd_cli", "dentro_limite_nominal_usd_3", "seis_fontes_inalteradas")}, ensure_ascii=False))
if not models_valid or not distinct or not record["seis_fontes_inalteradas"]:
    raise SystemExit("Conferencia operacional falhou.")
