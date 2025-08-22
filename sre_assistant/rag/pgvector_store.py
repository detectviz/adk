
class PgVectorError(Exception):
    code = "E_VECTOR_BACKEND"
    def __init__(self, message, code=None):
        super().__init__(message)
        if code:
            self.code = code

class DuplicateKey(PgVectorError):
    def __init__(self, message="duplicate key"):
        super().__init__(message, code="E_DUP_KEY")

class TxnAbort(PgVectorError):
    def __init__(self, message="transaction aborted"):
        super().__init__(message, code="E_TXN_ABORT")

class PgVectorStore:
    def __init__(self, conn):
        self.conn = conn

    def upsert(self, items):
        # explicit transaction with error mapping
        tx = self.conn.begin()
        try:
            for it in items:
                self._insert_or_update(it)
            tx.commit()
        except Exception as e:
            tx.rollback()
            msg = str(e).lower()
            if "duplicate key" in msg or "unique constraint" in msg:
                raise DuplicateKey()
            if "abort" in msg or "serialization" in msg:
                raise TxnAbort()
            raise PgVectorError(str(e))

    def _insert_or_update(self, it):
        # Placeholder sql runner to keep decoupled for tests
        cur = self.conn.cursor()
        cur.execute("/* upsert vector */", it)

    def search(self, query, top_k=5):
        try:
            cur = self.conn.cursor()
            cur.execute("/* vector search */", {"q": query, "k": top_k})
            return cur.fetchall()
        except Exception as e:
            raise PgVectorError(str(e))
