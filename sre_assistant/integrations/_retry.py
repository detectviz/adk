
# -*- coding: utf-8 -*-
# requests.Session 重試與逾時統一設定
from __future__ import annotations
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def session_with_retry(total=3, backoff=0.5, status=(429,500,502,503,504)) -> requests.Session:
    s = requests.Session()
    r = Retry(total=total, backoff_factor=backoff, status_forcelist=list(status), raise_on_status=False)
    a = HTTPAdapter(max_retries=r)
    s.mount("http://", a); s.mount("https://", a)
    return s
