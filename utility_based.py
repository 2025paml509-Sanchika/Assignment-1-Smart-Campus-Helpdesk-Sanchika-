"""Utility-Based Agent: scores response options using a transparent utility model."""
from .common import result, priority_from_score


class UtilityBasedAgent:
    def _score(self, ticket: dict) -> float:
        impact = {"low": 10, "medium": 25, "potentially_high": 35, "high": 40}.get(ticket.get("impact"), 10)
        urgency = {"normal": 5, "high": 20, "critical": 35}.get(ticket.get("urgency"), 5)
        users = int(ticket.get("affected_users", 1))
        user_score = min(20, users * 0.25)
        time_score = 20 if ticket.get("minutes_to_event") is not None and ticket["minutes_to_event"] <= 15 else 0
        uncertainty_penalty = 8 if not ticket.get("reports_complete", True) else 0
        return max(0, min(100, impact + urgency + user_score + time_score - uncertainty_penalty))

    def decide(self, ticket: dict) -> dict:
        score = self._score(ticket)
        priority = priority_from_score(score)

        if ticket.get("category") == "network" and not ticket.get("reports_complete", True):
            action = "Perform rapid network diagnostics and validate scope before full incident escalation"
        elif score >= 75:
            action = "Prioritize immediate dispatch of the relevant support team"
        elif score >= 45:
            action = "Assign to the high-priority IT queue and investigate promptly"
        else:
            action = "Use standard support workflow and known troubleshooting steps"

        reasoning = (
            f"Utility score={score:.1f}/100. Components: impact, urgency, affected-user count "
            "and imminent-event time; incomplete reports incur an uncertainty penalty. "
            "The score ranks response options, while uncertain network evidence still requires verification."
        )
        return result("Utility-Based", priority, action, reasoning, utility_score=round(score, 1))
