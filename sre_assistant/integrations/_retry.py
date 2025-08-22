
# requests.Session 重試與逾時統一設定
from __future__ import annotations
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def session_with_retry(total=3, backoff=0.5, status=(429,500,502,503,504)) -> requests.Session:
    """
    2025-08-22 03:37:34Z
    函式用途：`session_with_retry` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `total`：參數用途請描述。
    - `backoff`：參數用途請描述。
    - `status`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    s = requests.Session()
    r = Retry(total=total, backoff_factor=backoff, status_forcelist=list(status), raise_on_status=False)
    a = HTTPAdapter(max_retries=r)
    s.mount("http://", a); s.mount("https://", a)
    return s