"""agent_Bob.py
鮑伯代理 (AgentBob) – 玩具 A2A 猜數字遊戲的命令列前端。

鮑伯在人類玩家和兩個對等代理之間進行協調：

* **愛麗絲代理 (AgentAlice)** – 持有秘密數字並對猜測進行評分。
* **卡蘿代理 (AgentCarol)** – 產生鮑伯累積的猜測歷史的文字視覺化（以及可選的洗牌）。
"""

from __future__ import annotations

import json
import time

from typing import Any

from a2a.types import Task, TaskState
from config import AGENT_ALICE_PORT, AGENT_CAROL_PORT
from utils.game_logic import is_sorted_history
from utils.protocol_wrappers import (
    cancel_task,
    extract_text,
    send_followup,
    send_text,
)


# ---------------------------------------------------------------------------
# 本地記憶體中的遊戲狀態
# ---------------------------------------------------------------------------

game_history: list[dict[str, str]] = []

MAX_NEGOTIATION_ATTEMPTS = 400  # 避免無盡迴圈的上限


def _start_shuffle_request() -> Task | None:
    """向卡蘿代理發送初始洗牌請求，並確保我們取回一個任務。"""
    payload = json.dumps({'action': 'shuffle', 'history': game_history})
    resp_obj = send_text(AGENT_CAROL_PORT, payload)  # type: ignore[arg-type]
    return resp_obj if isinstance(resp_obj, Task) else None


def _extract_history_from_task(resp_task: Task) -> list[Any]:
    """從 *resp_task* 中傳回 JSON 解碼的歷史列表。

    Args:
        resp_task: 由卡蘿代理產生的任務物件，預期在其最新的成品中包含一個單一的 JSON 列表。

    Returns:
        list: 解析後的歷史列表，如果解析失敗或成品缺失/無效，則為空列表。
    """
    parts_text = extract_text(resp_task)
    try:
        return json.loads(parts_text)
    except json.JSONDecodeError:
        return []


def _negotiate_sorted_history(
    max_attempts: int = MAX_NEGOTIATION_ATTEMPTS,
) -> int:
    """要求卡蘿洗牌，直到歷史列表被排序。

    此函式啟動一個新的 *shuffle* 任務，然後進入一個請求/回應迴圈，
    根據傳回的列表是否已排序，發送「再試一次」或「做得好！」的後續訊息。

    Args:
        max_attempts: 在為避免無限迴圈而取消任務之前，重新洗牌嘗試的次數上限。

    Returns:
        int: 在協商期間發送給卡蘿的訊息數量。
    """
    attempts = 0
    resp_task = _start_shuffle_request()
    if resp_task is None:
        return attempts

    print(
        f'[鮑伯] 已收到任務 {resp_task.id}，狀態為 {resp_task.status.state}'
    )

    while (
        resp_task.status.state == TaskState.input_required
        and attempts < max_attempts
    ):
        # 在決定發送哪個後續訊息之前評估列表
        maybe_hist = _extract_history_from_task(resp_task)
        if isinstance(maybe_hist, list):
            print(f'[鮑伯] 候選歷史：{maybe_hist}')
            print(f'[鮑伯] 是否已排序？{is_sorted_history(maybe_hist)}')

        if isinstance(maybe_hist, list) and is_sorted_history(maybe_hist):
            attempts += 1
            game_history.clear()
            game_history.extend(maybe_hist)
            print(f'[鮑伯] 歷史在 {attempts} 次嘗試後已排序')
            print(
                '（我們透過隨機排序來說明多輪通訊）'
            )
            resp_task = send_followup(AGENT_CAROL_PORT, resp_task, '做得好！')  # type: ignore[assignment]
            break

        # 未排序 → 要求卡蘿再次洗牌
        attempts += 1
        print(f"[鮑伯] 第 {attempts} 次嘗試：發送 '再試一次'")
        resp_obj = send_followup(AGENT_CAROL_PORT, resp_task, '再試一次')
        if not isinstance(resp_obj, Task):
            print(
                '[鮑伯] 未在回應中收到任務；中止協商'
            )
            break
        resp_task = resp_obj
        print(f'[鮑伯] 卡蘿以狀態 {resp_task.status.state} 回應')

    if (
        resp_task.status.state == TaskState.input_required
        and attempts >= max_attempts
    ):
        print(
            f'[鮑伯] 已達最大嘗試次數 ({max_attempts})。正在取消任務。'
        )
        cancel_task(AGENT_CAROL_PORT, resp_task.id)

    return attempts


def _handle_guess(guess: str) -> str:
    """將 *guess* 轉發給愛麗絲代理並傳回她的文字回饋。"""
    resp_obj = send_text(AGENT_ALICE_PORT, guess)
    feedback = extract_text(resp_obj)
    print(f'愛麗絲說：{feedback}')
    return feedback


def _visualise_history() -> None:
    """請求並列印 *game_history* 的格式化視覺化。"""
    vis_obj = send_text(AGENT_CAROL_PORT, json.dumps(game_history))
    vis_text = extract_text(vis_obj)
    print("\n=== 卡蘿的視覺化（已排序） ===")
    print(vis_text)
    print('============================\n')


def play_game() -> None:
    """為猜數字遊戲執行互動式 CLI 迴圈。"""
    print('猜猜愛麗絲代理選擇的數字 (1-100)！')

    while True:
        user_input = input('您的猜測：').strip()
        if not user_input:
            continue

        feedback = _handle_guess(user_input)
        game_history.append({'guess': user_input, 'response': feedback})

        total_attempts = _negotiate_sorted_history()
        if total_attempts:
            print(
                f'已要求卡蘿重做視覺化 {total_attempts} 次'
            )

        _visualise_history()

        if feedback.startswith('correct'):
            break

    print('您贏了！正在結束…')
    time.sleep(0.5)


def main() -> None:  # pragma: no cover
    print("提示：別忘了也要啟動愛麗絲和卡蘿！")
    play_game()


if __name__ == '__main__':
    main()
