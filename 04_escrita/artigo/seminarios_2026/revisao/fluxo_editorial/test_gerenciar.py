import importlib.util
import json
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from contextlib import redirect_stdout

SCRIPT = Path(__file__).with_name("gerenciar.py")
spec = importlib.util.spec_from_file_location("editorial", SCRIPT)
flow = importlib.util.module_from_spec(spec)
spec.loader.exec_module(flow)


class WorkflowTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="teste_fluxo_", dir=flow.PROJECT)
        self.addCleanup(self.tmp.cleanup)
        project = Path(self.tmp.name)
        # Caminhos curtos no Windows e dentro da raiz gravável do projeto.
        article = project / "artigo"
        here = article / "revisao" / "fluxo_editorial"
        (here / "prompts").mkdir(parents=True)
        for guide in flow.GUIDES:
            (article / guide).write_text("Guia fixo", encoding="utf-8")
        for role in ("redigir", "revisar", "corrigir"):
            (here / "prompts" / f"{role}.md").write_text("Prompt de teste", encoding="utf-8")
        self.patcher = patch.multiple(flow, HERE=here, ARTICLE=article, PROJECT=project, ROUNDS=here / "rodadas")
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.project = project
        self.brief = article / "brief.md"
        self.brief.write_text("Escopo da seção", encoding="utf-8")
        self.text = article / "texto_origem.md"
        self.text.write_text("Este trabalho analisa a configuração.", encoding="utf-8")
        flow.start("teste", self.brief, "artigo", [])
        flow.draft("teste", self.text, "Codex — redator")

    def input(self, value):
        path = self.project / "entrada.json"
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        return path

    def review_payload(self, decision="corrigir", kind="editorial", scope="editorial"):
        directory, manifest = flow.load("teste")
        version = flow.current(manifest)
        items = [] if decision == "aprovar" else [{"id": f"V{version['numero']}-R1", "tipo": kind,
            "gravidade": "maior", "trecho": "Este trabalho", "problema": "Precisar a afirmação", "acao": "Reescrever"}]
        checks = [{"id": x["id"], "estado": "resolvido", "justificativa": "Conferido no texto"}
                  for x in version["respostas"]]
        return {"versao": version["numero"], "sha256": version["texto"]["sha256"],
            "contexto_sha256": flow.context_hash(manifest), "abrangencia": "texto_integral_da_versao",
            "revisor": "Claude — revisor", "escopo": scope, "decisao": decision,
            "itens": items, "verificacoes_anteriores": checks, "limites": ["Revisão limitada às fontes fornecidas"]}

    def correction_payload(self):
        directory, manifest = flow.load("teste")
        version = flow.current(manifest)
        previous = flow.latest_review(directory, version)
        return {"versao_base": version["numero"], "sha256_base": version["texto"]["sha256"],
            "contexto_sha256": flow.context_hash(manifest), "parecer_sha256": version["pareceres"][-1]["sha256"],
            "corretor": "Codex — corretor", "texto": "Este trabalho analisa somente esta configuração.",
            "respostas": [{"id": x["id"], "situacao": "corrigido", "justificativa": "Precisado o escopo",
                          "evidencias": []} for x in previous["itens"]]}

    def verification(self):
        directory, manifest = flow.load("teste")
        version = flow.current(manifest)
        return {"versao": version["numero"], "sha256": version["texto"]["sha256"],
            "verificador": "Codex — conferência de integração", "pendencias": [], "checagens": [{
                "alegacao": "Escopo restrito", "fonte": self.brief.relative_to(self.project).as_posix(),
                "localizador": "briefing inteiro", "verificacao": "Texto mantém o escopo solicitado"}]}

    def test_full_cycle_requires_new_review_before_integration(self):
        flow.review("teste", self.input(self.review_payload()))
        flow.correction("teste", self.input(self.correction_payload()))
        self.assertEqual(flow.status("teste")["estado"], "aguarda_nova_revisao")
        with self.assertRaises(flow.FlowError):
            flow.integrate("teste", self.input(self.verification()))
        flow.review("teste", self.input(self.review_payload("aprovar", scope="cientifico_editorial")))
        target = flow.integrate("teste", self.input(self.verification()))
        self.assertIn("somente", target.read_text(encoding="utf-8"))
        with self.assertRaises(flow.FlowError):
            flow.integrate("teste", self.input(self.verification()))

    def test_rejects_review_from_wrong_version_or_context(self):
        for key, value in (("versao", 2), ("sha256", "outro"), ("contexto_sha256", "outro")):
            payload = self.review_payload()
            payload[key] = value
            with self.subTest(key=key), self.assertRaises(flow.FlowError):
                flow.review("teste", self.input(payload))

    def test_rejects_nonliteral_quote(self):
        payload = self.review_payload()
        payload["itens"][0]["trecho"] = "Texto que nunca existiu"
        with self.assertRaises(flow.FlowError):
            flow.review("teste", self.input(payload))

    def test_rejects_duplicate_review_ids(self):
        payload = self.review_payload()
        payload["itens"].append(payload["itens"][0].copy())
        with self.assertRaises(flow.FlowError):
            flow.review("teste", self.input(payload))

    def test_rejects_missing_extra_and_duplicate_responses(self):
        flow.review("teste", self.input(self.review_payload()))
        for mutation in ("missing", "extra", "duplicate"):
            payload = self.correction_payload()
            if mutation == "missing":
                payload["respostas"] = []
            else:
                extra = payload["respostas"][0].copy()
                if mutation == "extra":
                    extra["id"] = "V1-R2"
                payload["respostas"].append(extra)
            with self.subTest(mutation=mutation), self.assertRaises(flow.FlowError):
                flow.correction("teste", self.input(payload))

    def test_scientific_correction_requires_evidence(self):
        flow.review("teste", self.input(self.review_payload("bloqueado", "evidencia", "cientifico_editorial")))
        with self.assertRaises(flow.FlowError):
            flow.correction("teste", self.input(self.correction_payload()))
        payload = self.correction_payload()
        payload["respostas"][0]["situacao"] = "retirado"
        flow.correction("teste", self.input(payload))
        self.assertEqual(flow.status("teste")["estado"], "aguarda_nova_revisao")

    def test_reviewer_must_verify_previous_ids(self):
        flow.review("teste", self.input(self.review_payload()))
        flow.correction("teste", self.input(self.correction_payload()))
        payload = self.review_payload("aprovar")
        payload["verificacoes_anteriores"] = []
        with self.assertRaises(flow.FlowError):
            flow.review("teste", self.input(payload))
        payload = self.review_payload("aprovar")
        payload["verificacoes_anteriores"][0]["estado"] = "nao_resolvido"
        with self.assertRaises(flow.FlowError):
            flow.review("teste", self.input(payload))

    def test_editorial_approval_cannot_integrate(self):
        flow.review("teste", self.input(self.review_payload("aprovar")))
        with self.assertRaises(flow.FlowError):
            flow.integrate("teste", self.input(self.verification()))

    def test_demonstration_cannot_integrate(self):
        flow.start("demo", self.brief, "demonstracao", [])
        flow.draft("demo", self.text, "Codex")
        with self.assertRaises(flow.FlowError):
            flow.integrate("demo", self.input({}))

    def test_hash_detects_text_and_source_tampering(self):
        directory, manifest = flow.load("teste")
        path = directory / flow.current(manifest)["texto"]["arquivo"]
        original = path.read_bytes()
        path.write_bytes(original + b"alterado")
        with self.assertRaises(flow.FlowError):
            flow.status("teste")
        path.write_bytes(original)
        self.brief.write_text("Novo contexto", encoding="utf-8")
        with self.assertRaises(flow.FlowError):
            flow.status("teste")

    def test_paths_cannot_escape(self):
        with self.assertRaises(flow.FlowError):
            flow.start("../fora", self.brief, "artigo", [])
        with self.assertRaises(flow.FlowError):
            flow.artifact(flow.round_path("teste"), "../../escape.md", b"x")
        with self.assertRaises(flow.FlowError):
            flow.within(self.project.parent / "escape.md", self.project)

    def test_real_cli_envelope_and_model_metadata(self):
        payload = self.review_payload("aprovar")
        wrapped = {"is_error": False, "result": json.dumps(payload), "modelUsage": {"claude-opus-5-5": {}},
                   "session_id": "sessao-teste", "total_cost_usd": 0.1}
        flow.review("teste", self.input(wrapped))
        directory, manifest = flow.load("teste")
        saved = flow.latest_review(directory, flow.current(manifest))
        self.assertEqual(saved["proveniencia"]["modelos"], ["claude-opus-5-5"])

    def test_approval_with_open_item_rejected(self):
        payload = self.review_payload()
        payload["decisao"] = "aprovar"
        with self.assertRaises(flow.FlowError):
            flow.review("teste", self.input(payload))

    def load_consultation_module(self):
        spec = importlib.util.spec_from_file_location("consultation", SCRIPT.with_name("consultar_claude.py"))
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"gerenciar": flow}):
            spec.loader.exec_module(module)
        return module

    def test_declared_writer_pending_does_not_disappear_with_approval(self):
        flow.start("pendente", self.brief, "artigo", [])
        flow.import_draft("pendente", self.input({"autor": "Claude — redator", "texto": "Rascunho preliminar",
                                                "pendencias": ["Recuperar fonte da afirmação"]}))
        with self.assertRaisesRegex(flow.FlowError, "Redator declarou pendências"):
            flow.integrate("pendente", self.input({}))

    def test_consultation_records_response_without_importing_or_retrying(self):
        consultation = self.load_consultation_module()
        wrapped = {"is_error": False, "result": json.dumps(self.review_payload("aprovar")),
                   "modelUsage": {"claude-opus-5-5": {}}, "duration_ms": 1}
        result = subprocess.CompletedProcess([], 0, json.dumps(wrapped), "")
        args = ["consultar", "teste", "revisar", "--executavel", str(SCRIPT)]
        with patch.object(sys, "argv", args), patch.object(consultation.subprocess, "run", return_value=result) as call, redirect_stdout(io.StringIO()):
            self.assertEqual(consultation.main(), 0)
        self.assertEqual(call.call_count, 1)
        self.assertEqual(flow.status("teste")["estado"], "rascunho")
        directory, manifest = flow.load("teste")
        self.assertTrue((directory / "consultas/001_revisar.json").is_file())
        self.assertEqual(flow.current(manifest)["pareceres"], [])

    def test_consultation_timeout_preserves_failure_without_retry(self):
        consultation = self.load_consultation_module()
        args = ["consultar", "teste", "revisar", "--executavel", str(SCRIPT)]
        error = subprocess.TimeoutExpired("claude", 900)
        with patch.object(sys, "argv", args), patch.object(consultation.subprocess, "run", side_effect=error) as call, redirect_stdout(io.StringIO()):
            self.assertEqual(consultation.main(), 2)
        self.assertEqual(call.call_count, 1)
        directory, manifest = flow.load("teste")
        self.assertTrue((directory / "consultas/001_revisar_stderr.txt").is_file())
        self.assertEqual(flow.current(manifest)["pareceres"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
