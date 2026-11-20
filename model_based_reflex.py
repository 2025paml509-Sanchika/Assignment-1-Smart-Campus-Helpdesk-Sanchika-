"""Model-Based Reflex Agent: combines the current percept with remembered state."""
from .common import result


class ModelBasedReflexAgent:
    def __init__(self):
        # State is keyed by service/building to avoid unrelated tickets contaminating one another.
        self.service_state = {}

    def decide(self, ticket: dict) -> dict:
        key = ticket.get("service") or ticket.get("building") or "unknown"
        previous = self.service_state.get(key, {
            "outage_suspected": False, "consecutive_reports": 0, "last_ticket_id": None
        })

        is_network = ticket.get("category") == "network"
        incomplete = not ticket.get("reports_complete", True)
        multiple = int(ticket.get("affected_users", 1)) > 1

        current_outage_signal = is_network and multiple
        remembered_signal = previous["outage_suspected"]
        outage_suspected = current_outage_signal or remembered_signal
        report_count = previous["consecutive_reports"] + 1 if current_outage_signal else 0

        # Update the internal model only for this service key.
        self.service_state[key] = {
            "outage_suspected": outage_suspected,
            "consecutive_reports": report_count,
            "last_ticket_id": ticket.get("ticket_id"),
        }

        if ticket.get("urgency") == "critical":
            priority, action = "P1 - Critical", "Dispatch support immediately; verify the classroom AV path"
        elif outage_suspected and (incomplete or report_count >= 1):
            priority, action = "P1 - Critical", "Open a suspected building network incident; verify access-point and service status"
        elif ticket.get("impact") == "low":
            priority, action = "P3 - Normal", "Use standard individual-device troubleshooting"
        else:
            priority, action = "P2 - High", "Assign support and continue monitoring the service"

        reasoning = (
            f"Current ticket plus internal service model: suspected_outage={outage_suspected}, "
            f"reports_seen_for_service={report_count}. "
            "The remembered state is scoped to this service, not applied to unrelated tickets."
        )
        return result("Model-Based Reflex", priority, action, reasoning,
                      internal_state=dict(self.service_state[key]))
