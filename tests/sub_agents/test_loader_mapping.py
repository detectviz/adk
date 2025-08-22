
def test_prompts_and_tools_from_yaml():
    from sub_agents.diagnostic.prompts import PROMPT
    from sub_agents.diagnostic.tools import list_tools
    assert "診斷專家" in PROMPT
    assert "rag_search" in list_tools()
