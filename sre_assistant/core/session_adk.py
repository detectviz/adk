
def get_session_service():
    """
    Prefer ADK official SessionService. Fallback to in-memory if unavailable.
    """
    try:
        # Expected import path; adjust if project uses different pathing.
        from adk.runtime.session import SessionService  # type: ignore
        return SessionService()
    except Exception:
        # Local fallback to minimal in-memory session service
        class InMemorySessionService:
            def __init__(self):
                self._store = {}
            def get(self, key):
                return self._store.get(key)
            def set(self, key, val):
                self._store[key] = val
                return True
        return InMemorySessionService()
