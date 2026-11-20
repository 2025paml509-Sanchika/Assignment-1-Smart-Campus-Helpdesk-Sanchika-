"""Shared helpers and result format for the classical agents."""
from typing import Any


def result(agent: str, priority: str, action: str, reasoning: str, **extra: Any) -> dict:
    return {
        "agent": agent,
        "priority": priority,
        "action": action,
        "reasoning": reasoning,
        **extra,
    }


def priority_from_score(score: float) -> str:
    if score >= 75:
        return "P1 - Critical"
    if score >= 45:
        return "P2 - High"
    if score >= 20:
        return "P3 - Normal"
    return "P4 - Low"
