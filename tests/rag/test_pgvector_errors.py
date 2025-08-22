import pytest
from sre_assistant.rag.pgvector_store import PgVectorStore, PgVectorError, DuplicateKey, TxnAbort

class DummyCursor:
    def __init__(self, behavior=None, results=None):
        self.behavior = behavior or "ok"
        self.results = results or []

    def execute(self, sql, params=None):
        if self.behavior == "dup":
            raise Exception("duplicate key value violates unique constraint")
        if self.behavior == "abort":
            raise Exception("Transaction aborted due to serialization failure")
        if self.behavior == "fail":
            raise Exception("backend error")

    def fetchall(self):
        return self.results

class DummyTx:
    def __init__(self, conn):
        self.conn = conn
        self.committed = False
        self.rolled = False
    def commit(self):
        self.committed = True
    def rollback(self):
        self.rolled = True

class DummyConn:
    def __init__(self, cursor_behavior="ok", results=None):
        self.cursor_behavior = cursor_behavior
        self.results = results or [("id1", 0.1)]
    def cursor(self):
        return DummyCursor(self.cursor_behavior, self.results)
    def begin(self):
        return DummyTx(self)

def test_upsert_duplicate_key_maps_error():
    store = PgVectorStore(DummyConn(cursor_behavior="dup"))
    with pytest.raises(DuplicateKey):
        store.upsert([{"id":"a"}])

def test_upsert_txn_abort_maps_error():
    store = PgVectorStore(DummyConn(cursor_behavior="abort"))
    with pytest.raises(TxnAbort):
        store.upsert([{"id":"a"}])

def test_search_success():
    store = PgVectorStore(DummyConn(cursor_behavior="ok", results=[("x", 0.9)]))
    rows = store.search("q", top_k=1)
    assert rows == [("x", 0.9)]
