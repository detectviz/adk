
# -*- coding: utf-8 -*-
def test_official_a2a_wrappers_exist():
    from sre_assistant.adk_app.a2a_expose import to_a2a_app
    from sre_assistant.adk_app.a2a_consume import remote_agent
    assert callable(to_a2a_app) and callable(remote_agent)
