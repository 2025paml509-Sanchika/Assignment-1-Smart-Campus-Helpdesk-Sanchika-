"""Learning Agent: uses persistent category-level outcome experience.

Feedback is simulated analyst feedback; it does not modify any real service.
"""
import json
from pathlib import Path
from .common import result

DEFAULT_EXPERIENCE = {
    "hardware": {"success": 7, "failure": 2},
    "software": {"success": 8, "failure": 2},
    "network": {"success": 3, "failure": 4},
}


class LearningAgent:
    def __init__(self, experience_path="data/learning_data.json"):
        self.path = Path(experience_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.save(DEFAULT_EXPERIENCE)

    def load(self):
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return json.loads(json.dumps(DEFAULT_EXPERIENCE))

    def save(self, data):
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def decide(self, ticket: dict) -> dict:
        history = self.load()
        category = ticket.get("category", "other")
        counts = history.get(category, {"success": 0, "failure": 0})
        success, failure = int(counts["success"]), int(counts["failure"])
        # Laplace smoothing prevents a zero-history category from producing 0 or 1 confidence.
        confidence = (success + 1) / (success + failure + 2)

        if ticket.get("urgency") == "critical":
            priority = "P1 - Critical"
            action = "Dispatch immediately; use the historically reliable hardware response playbook"
        elif category == "network" and not ticket.get("reports_complete", True):
            priority = "P2 - High"
            action = "Verify outage scope first; network history has lower resolution confidence"
        elif confidence >= 0.75:
            priority = "P3 - Normal" if ticket.get("impact") == "low" else "P2 - High"
            action = "Use the category's historically successful troubleshooting playbook"
        else:
            priority = "P2 - High"
            action = "Assign experienced support staff and verify the outcome closely"

        reasoning = (
            f"Experience for '{category}': {success} successes and {failure} failures. "
            f"Smoothed success rate={(confidence * 100):.1f}%. "
            "This history influences the recommended playbook/verification level; current critical urgency "
            "still overrides historical success."
        )
        return result("Learning Agent", priority, action, reasoning,
                      experience=dict(counts), estimated_success_rate=round(confidence, 3))

    def update(self, category: str, resolved: bool):
        history = self.load()
        history.setdefault(category, {"success": 0, "failure": 0})
        key = "success" if resolved else "failure"
        history[category][key] += 1
        self.save(history)
        return history[category]
