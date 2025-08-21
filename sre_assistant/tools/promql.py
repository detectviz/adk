
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Dict, Any

def promql_query_tool(query: str, range: str) -> Dict[str, Any]:
    return {"series":[{"metric":{"job":"demo"},"values":[[0,1],[60,1]]}],"stats":{"sample_count":2}}
