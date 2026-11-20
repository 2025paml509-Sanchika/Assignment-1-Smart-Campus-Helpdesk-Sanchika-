"""Simple Reflex Agent: maps only the current percept to fixed rules."""
from .common import result


class SimpleReflexAgent:
    def decide(self, ticket: dict) -> dict:
        impact = ticket.get("impact", "low")
        urgency = ticket.get("urgency", "normal")
        users = int(ticket.get("affected_users", 1))

        if urgency == "critical" or (impact == "high" and users >= 20):
            priority, action = "P1 - Critical", "Dispatch on-call IT support immediately"
            why = "Current ticket percept matches the critical-urgency/high-impact rule."
        elif impact in {"high", "potentially_high"} or urgency == "high" or users >= 5:
            priority, action = "P2 - High", "Assign to the relevant IT support queue promptly"
            why = "Current ticket percept matches the high-impact or high-urgency rule."
        elif impact == "low" and urgency == "normal":
            priority, action = "P3 - Normal", "Provide standard troubleshooting or queue assignment"
            why = "A single-user, low-impact issue with normal urgency matches the standard-support rule."
        else:
            priority, action = "P3 - Normal", "Request missing information and triage"
            why = "No specific rule matched; use a conservative standard triage action."

        return result("Simple Reflex", priority, action, why,
                      mechanism="Current percept only")
