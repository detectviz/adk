class StateStore:
    def __init__(self):
        
        self._store = {}
    def get(self, k, d=None):
        
        return self._store.get(k, d)
    def set(self, k, v):
        
        self._store[k] = v
    def as_dict(self):
        
        return dict(self._store)