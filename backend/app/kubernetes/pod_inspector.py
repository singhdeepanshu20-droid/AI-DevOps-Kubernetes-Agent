from typing import Any, Dict, List, Optional
from loguru import logger
from app.kubernetes.executor import KubectlExecutor


class PodInspector:
    """Inspects Kubernetes pods to identify unhealthy states and failures."""

    def __init__(self, executor: Optional[KubectlExecutor] = None):
        self.executor = executor or KubectlExecutor()

    def inspect(self, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Fetches pod status and filters problematic pods."""
        args = ["get", "pods"]
        if not namespace:
            args.append("-A")

        data, exec_res = self.executor.execute_json(args, namespace=namespace)
        if not exec_res.success or not data:
            logger.warning(f"Failed to fetch pods: {exec_res.stderr}")
            return {
                "healthy": False,
                "total_pods": 0,
                "healthy_count": 0,
                "unhealthy_count": 0,
                "problematic_pods": [],
                "error": exec_res.stderr or "Failed to query pods"
            }

        items = data.get("items", [])
        total_pods = len(items)
        problematic_pods: List[Dict[str, Any]] = []

        for item in items:
            pod_info = self._analyze_pod(item)
            if pod_info["is_problematic"]:
                # Clean internal flag before output
                del pod_info["is_problematic"]
                problematic_pods.append(pod_info)

        unhealthy_count = len(problematic_pods)
        healthy_count = total_pods - unhealthy_count
        healthy = (unhealthy_count == 0)

        return {
            "healthy": healthy,
            "total_pods": total_pods,
            "healthy_count": healthy_count,
            "unhealthy_count": unhealthy_count,
            "problematic_pods": problematic_pods
        }

    def _analyze_pod(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Analyzes single pod item manifest from kubectl JSON."""
        metadata = item.get("metadata", {})
        status = item.get("status", {})
        name = metadata.get("name", "unknown")
        pod_namespace = metadata.get("namespace", "default")
        phase = status.get("phase", "Unknown")

        container_statuses = status.get("containerStatuses", []) + status.get("initContainerStatuses", [])
        total_restarts = 0
        container_details = []
        is_problematic = False
        detected_status = phase
        reason_detail = status.get("reason", "")
        message_detail = status.get("message", "")

        # Check phase
        if phase in ["Pending", "Failed", "Unknown"]:
            is_problematic = True
            detected_status = phase

        # Check container statuses
        for cs in container_statuses:
            c_name = cs.get("name", "")
            c_ready = cs.get("ready", False)
            restarts = cs.get("restartCount", 0)
            total_restarts += restarts

            state = cs.get("state", {})
            last_state = cs.get("lastState", {})
            c_state_str = "running"
            c_reason = ""
            c_msg = ""

            if "waiting" in state:
                c_state_str = "waiting"
                c_reason = state["waiting"].get("reason", "")
                c_msg = state["waiting"].get("message", "")
                if c_reason in [
                    "CrashLoopBackOff", "ImagePullBackOff", "ErrImagePull",
                    "Pending", "ContainerCreating", "CreateContainerConfigError",
                    "CreateContainerError", "OOMKilled", "Error"
                ]:
                    is_problematic = True
                    detected_status = c_reason
                    reason_detail = c_reason
                    message_detail = c_msg
            elif "terminated" in state:
                c_state_str = "terminated"
                c_reason = state["terminated"].get("reason", "")
                c_msg = state["terminated"].get("message", "")
                exit_code = state["terminated"].get("exitCode", 0)
                if exit_code != 0 or c_reason in ["OOMKilled", "Error", "ContainerCannotRun"]:
                    is_problematic = True
                    detected_status = c_reason or f"ExitCode{exit_code}"
                    reason_detail = c_reason
                    message_detail = c_msg

            # Check lastState for OOMKilled or previous crashes
            if "terminated" in last_state:
                last_reason = last_state["terminated"].get("reason", "")
                if last_reason == "OOMKilled":
                    is_problematic = True
                    if not detected_status or detected_status == "Running":
                        detected_status = "OOMKilled"
                        reason_detail = "OOMKilled"

            if not c_ready and phase not in ["Succeeded"]:
                is_problematic = True

            container_details.append({
                "name": c_name,
                "ready": c_ready,
                "restart_count": restarts,
                "state": c_state_str,
                "reason": c_reason,
                "message": c_msg
            })

        # Stuck ContainerCreating check
        if phase == "Pending" and not container_statuses:
            detected_status = "Pending"
            is_problematic = True

        return {
            "name": name,
            "namespace": pod_namespace,
            "status": detected_status,
            "phase": phase,
            "reason": reason_detail,
            "message": message_detail,
            "restarts": total_restarts,
            "containers": container_details,
            "is_problematic": is_problematic
        }
