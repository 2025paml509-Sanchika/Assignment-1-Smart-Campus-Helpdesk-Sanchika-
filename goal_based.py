"""Goal-Based Agent: chooses an action according to explicit service goals."""
from .common import result


class GoalBasedAgent:
    GOALS = [
        "Restore or preserve teaching activity",
        "Minimize the number of users affected",
        "Avoid unnecessary escalation when evidence is incomplete",
    ]

    def decide(self, ticket: dict) -> dict:
        category = ticket.get("category")
        if category == "hardware" and ticket.get("minutes_to_event") is not None:
            action = "Send an AV technician now and prepare a spare projector/room fallback"
            priority = "P1 - Critical"
            reason = "This action best protects the imminent lecture goal and provides a fallback."
        elif category == "network" and not ticket.get("reports_complete", True):
            action = "Run a rapid building-wide connectivity check, collect AP/location details, then escalate if confirmed"
            priority = "P2 - High"
            reason = "The goal is to restore multi-user access while avoiding an unsupported claim that an outage is confirmed."
        elif category == "software":
            action = "Guide the student through the approved prerequisite installation; assign desktop support if it fails"
            priority = "P3 - Normal"
            reason = "A standard fix is likely to resolve the single-user issue without diverting emergency resources."
        else:
            action = "Collect missing facts and route to the relevant support team"
            priority = "P3 - Normal"
            reason = "The available facts do not identify a more urgent goal-directed action."

        return result("Goal-Based", priority, action, reason,
                      goals_considered=self.GOALS)
