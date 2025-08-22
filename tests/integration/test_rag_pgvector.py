
import os, pytest, tempfile, pathlib
from sre_assistant.tools.knowledge_ingestion import ingest_files
from sre_assistant.tools.rag_retrieve import rag_search

@pytest.mark.integration
def test_rag_flow_smoke(tmp_path):
    
    if not os.getenv("PG_DSN"):
        pytest.skip("PG_DSN 未設定，跳過")
    p = tmp_path / "doc.txt"
    p.write_text("SRE Assistant 利用 PromQL 與 K8s 自動化處置。", encoding="utf-8")
    r = ingest_files([str(p)], title="doc", metadata={"env":"dev"})
    out = rag_search("SRE Assistant 做什麼？", top_k=3)
    assert "citations" in out