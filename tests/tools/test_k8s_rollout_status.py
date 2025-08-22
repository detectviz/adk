from sre_assistant.tools.k8s_long_running import _eval_rollout, RolloutStatus

def test_all_ready():
    pods = [{"ready": True, "phase": "Running", "reason": None} for _ in range(3)]
    assert _eval_rollout(pods, deadline_seconds=300) == RolloutStatus.SUCCESS

def test_backoff_detected():
    pods = [{"ready": False, "phase": "CrashLoopBackOff", "reason": "BackOff"}]
    assert _eval_rollout(pods, deadline_seconds=300) == RolloutStatus.BACKOFF

def test_timeout():
    pods = [{"ready": False, "phase": "Pending", "reason": None}]
    assert _eval_rollout(pods, deadline_seconds=0) == RolloutStatus.TIMEOUT
