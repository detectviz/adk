from __future__ import annotations
from .intents import Intent

def simple_intent_classifier(text: str) -> Intent:
    
    t = text.lower()
    if any(k in t for k in ["restart","rollout","scale","repair","fix"]):
        return Intent(type="remediation", raw_input=text, confidence=0.8)
    if any(k in t for k in ["postmortem","incident review","timeline"]):
        return Intent(type="postmortem", raw_input=text, confidence=0.8)
    if any(k in t for k in ["provision","dashboard","onboard","monitoring"]):
        return Intent(type="provisioning", raw_input=text, confidence=0.8)
    return Intent(type="diagnostic", raw_input=text, confidence=0.6)