from sre_assistant.core.hitl_provider import load_providers, get_provider
def test_load_and_get_provider():
    
    data = load_providers()
    assert isinstance(data.get("providers"), list)
    _ = get_provider("hitl-approval")