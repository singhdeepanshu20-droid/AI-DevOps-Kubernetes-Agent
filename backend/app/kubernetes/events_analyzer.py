from typing import Any, Dict, List, Optional
from loguru import logger
from app.kubernetes.executor import KubectlExecutor

TARGET_EVENT_REASONS = {
    "FailedScheduling",
    "BackOff",
    "FailedMount",
    "FailedPull",
    "ErrImagePull",
    "Unhealthy",
    "Failed",
    "OOMKilling",
    "FailedCreate",
    "FailedDelete",
    "FailedBinding",
    "FailedPostStartHook",
    "FailedPreStopHook"
}


class EventsAnalyzer:
    """Analyzes Kubernetes cluster events for failures and warnings."""

    def __init__(self, executor: Optional[KubectlExecutor] = None):
        self.executor = executor or KubectlExecutor()

    def analyze(self, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Fetches and summarizes warning/error events in the cluster."""
        args = ["get", "events"]
        if not namespace:
            args.append("-A")

        data, exec_res = self.executor.execute_json(args, namespace=namespace)
        if not exec_res.success or not data:
            logger.warning(f"Failed to fetch events: {exec_res.stderr}")
            return {
                "total_events": 0,
                "warning_count": 0,
                "problematic_events": [],
                "error": exec_res.stderr or "Failed to query events"
            }

        items = data.get("items", [])
        warning_events: List[Dict[str, Any]] = []
        reason_counts: Dict[str, int] = {}

        for item in items:
            event_type = item.get("type", "Normal")
            reason = item.get("reason", "")
            message = item.get("message", "")
            count = item.get("count", 1)
            last_timestamp = item.get("lastTimestamp") or item.get("eventTime") or ""

            involved_obj = item.get("involvedObject", {})
            obj_kind = involved_obj.get("kind", "")
            obj_name = involved_obj.get("name", "")
            obj_ns = involved_obj.get("namespace", "default")

            is_warning = (event_type == "Warning") or (reason in TARGET_EVENT_REASONS)

            if is_warning:
                reason_counts[reason] = reason_counts.get(reason, 0) + count
                warning_events.append({
                    "type": event_type,
                    "reason": reason,
                    "message": message,
                    "count": count,
                    "last_timestamp": last_timestamp,
                    "object": {
                        "kind": obj_kind,
                        "name": obj_name,
                        "namespace": obj_ns
                    }
                })

        return {
            "total_events": len(items),
            "warning_count": len(warning_events),
            "reason_summary": reason_counts,
            "problematic_events": warning_events
        }
