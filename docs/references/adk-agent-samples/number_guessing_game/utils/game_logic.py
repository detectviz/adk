"""utils.game_logic
玩具猜數字遊戲示範共享的遊戲機制。

此模組與傳輸方式無關。它目前包含：
* 愛麗絲代理的數字猜測評估 (`process_guess`)。
* 卡蘿代理的歷史視覺化和洗牌輔助工具
  (`build_visualisation`, `process_history_payload`)。
"""

from __future__ import annotations

import json
import random

from utils.helpers import parse_int_in_range, try_parse_json


__all__ = [
    'build_visualisation',
    'is_sorted_history',
    'process_guess',
    'process_history_payload',
]

# ---------------------------------------------------------------------------
# 猜數字狀態（愛麗絲）
# ---------------------------------------------------------------------------

_target_number: int = random.randint(1, 100)
_attempts: int = 0
_secret_logged: bool = False


# ---------------------------------------------------------------------------
# 猜數字輔助工具
# ---------------------------------------------------------------------------


def process_guess(raw_text: str) -> str:
    """評估單一猜測並傳回愛麗絲代理的回饋。

    Args:
        raw_text: 原始使用者輸入，應表示一個介於 1
            和 100 之間（含）的整數。

    Returns:
        str: 以下回應字串之一：
            * ``"Go higher"`` – 猜測的數字比秘密數字小。
            * ``"Go lower"`` – 猜測的數字比秘密數字大。
            * ``"correct! attempts: <n>"`` – 猜測正確；*n* 是
              到目前為止的嘗試次數。
            * 輸入無效時的錯誤提示。
    """
    global _attempts, _target_number, _secret_logged

    if not _secret_logged:
        print('[遊戲邏輯] 已選擇秘密數字。正在等待猜測…')
        _secret_logged = True

    guess = parse_int_in_range(raw_text, 1, 100)
    if guess is None:
        print(f"[遊戲邏輯] 收到無效輸入 '{raw_text}'。")
        return '請傳送一個介於 1 到 100 之間的數字。'

    _attempts += 1

    if guess < _target_number:
        hint = '再高一點'
    elif guess > _target_number:
        hint = '再低一點'
    else:
        hint = f'正確！嘗試次數：{_attempts}'

    print(f'[遊戲邏輯] 猜測 {guess} -> {hint}')
    return hint


# ---------------------------------------------------------------------------
# 歷史輔助工具（卡蘿和鮑伯）
# ---------------------------------------------------------------------------


def build_visualisation(history: list[dict[str, str]]) -> str:
    """建立一個猜測/回應歷史列表的人類可讀呈現。

    Args:
        history: 字典序列，每個字典至少包含
            ``"guess"`` 和 ``"response"`` 鍵。

    Returns:
        str: 可直接列印到主控台的多行字串。
    """
    if not history:
        return '目前沒有猜測。'

    lines = ['目前的猜測：']
    for idx, entry in enumerate(history, 1):
        guess = entry.get('guess', '?')
        response = entry.get('response', '?')
        lines.append(f' {idx:>2}. {guess:>3} -> {response}')
    print('[遊戲邏輯] 已為鮑伯建立視覺化')
    return '\n'.join(lines)


def is_sorted_history(history: list[dict[str, str]]) -> bool:
    """當 *history* 按猜測的升冪排序時，傳回 ``True``。

    此輔助工具能優雅地處理包含純數字或
    數字字串而非完整字典的歷史記錄。

    Args:
        history: 代表猜測值的字典列表**或**純數字。

    Returns:
        bool: 當值為非遞減順序時為 ``True``；
        否則或解析錯誤時為 ``False``。
    """
    # 歷史列表可以包含字典項目（帶有 'guess' 鍵）
    # 或當其他代理回覆簡化列表時的裸數值。
    try:
        if history and isinstance(history[0], dict):
            guesses = [int(entry['guess']) for entry in history]
        else:
            # 假設是純數字/數字字串的可疊代物件
            guesses = [int(entry) for entry in history]
    except (ValueError, TypeError, KeyError):
        return False
    return guesses == sorted(guesses)


def process_history_payload(raw_text: str) -> str:
    """為提供的酬載傳回卡蘿代理的回應。

    解釋取決於 JSON 結構：

    1. ``{"action": "shuffle", "history": [...]}`` – 歷史列表
       就地洗牌並作為 JSON 字串傳回。
    2. ``[ ... ]`` – 該列表被視為完整歷史，並透過
       :func:`build_visualisation` 格式化。

    任何無法解析為 JSON 的輸入都會產生一個空的視覺化以表示無效輸入。

    Args:
        raw_text: 從鮑伯收到的原始酬載。

    Returns:
        str: 一個 JSON 編碼的列表或一個純文字視覺化。
    """
    success, parsed = try_parse_json(raw_text)
    if not success:
        # 不是 JSON – 傳回一個空的視覺化以表示無效輸入。
        return build_visualisation([])

    # 洗牌請求
    if isinstance(parsed, dict) and parsed.get('action') == 'shuffle':
        history_list = parsed.get('history', [])
        if not isinstance(history_list, list):
            history_list = []
        random.shuffle(history_list)
        print('[遊戲邏輯] 已洗牌歷史並傳回 JSON 列表')
        return json.dumps(history_list)

    # 視覺化請求
    if isinstance(parsed, list):
        return build_visualisation(parsed)

    # 不支援的 JSON 酬載的備用方案
    return build_visualisation([])
