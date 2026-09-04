from typing import Any, Dict, List, Optional
from loguru import logger
from app.kubernetes.executor import KubectlExecutor


class DeploymentInspector:
    """Inspects Kubernetes deployments for replica imbalances and rollout failures."""

    def __init__(self, executor: Optional[KubectlExecutor] = None):
        self.executor = executor or KubectlExecutor()

    def inspect(self, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Fetches deployment status and identifies unhealthy deployments."""
        args = ["get", "deployments"]
        if not namespace:
            args.append("-A")

        data, exec_res = self.executor.execute_json(args, namespace=namespace)
        if not exec_res.success or not data:
            logger.warning(f"Failed to fetch deployments: {exec_res.stderr}")
            return {
                "healthy": False,
                "total_deployments": 0,
                "healthy_count": 0,
                "unhealthy_count": 0,
                "unhealthy_deployments": [],
                "error": exec_res.stderr or "Failed to query deployments"
            }

        items = data.get("items", [])
        total_deployments = len(items)
        unhealthy_deployments: List[Dict[str, Any]] = []

        for item in items:
            deploy_info = self._analyze_deployment(item)
            if deploy_info["is_unhealthy"]:
                del deploy_info["is_unhealthy"]
                unhealthy_deployments.append(deploy_info)

        unhealthy_count = len(unhealthy_deployments)
        healthy_count = total_deployments - unhealthy_count
        healthy = (unhealthy_count == 0)

        return {
            "healthy": healthy,
            "total_deployments": total_deployments,
            "healthy_count": healthy_count,
            "unhealthy_count": unhealthy_count,
            "unhealthy_deployments": unhealthy_deployments
        }

    def _analyze_deployment(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Analyzes single deployment JSON manifest."""
        metadata = item.get("metadata", {})
        spec = item.get("spec", {})
        status = item.get("status", {})

        name = metadata.get("name", "unknown")
        deploy_ns = metadata.get("namespace", "default")

        desired_replicas = spec.get("replicas", 1)
        replicas = status.get("replicas", 0)
        updated_replicas = status.get("updatedReplicas", 0)
        ready_replicas = status.get("readyReplicas", 0)
        available_replicas = status.get("availableReplicas", 0)
        unavailable_replicas = status.get("unavailableReplicas", 0)

        conditions = status.get("conditions", [])
        formatted_conditions = []
        is_unhealthy = False
        status_reason = "Healthy"

        for cond in conditions:
            c_type = cond.get("type", "")
            c_status = cond.get("status", "Unknown")
            c_reason = cond.get("reason", "")
            c_message = cond.get("message", "")

            formatted_conditions.append({
                "type": c_type,
                "status": c_status,
                "reason": c_reason,
                "message": c_message
            })

            # Check rollout failures
            if c_type == "Progressing" and c_status == "False":
                is_unhealthy = True
                status_reason = f"ProgressingFailed ({c_reason})"
            elif c_type == "ReplicaFailure" and c_status == "True":
                is_unhealthy = True
                status_reason = f"ReplicaFailure ({c_reason})"
            elif c_type == "Available" and c_status == "False":
                is_unhealthy = True
                status_reason = "Unavailable"

        # Check replica count mismatches
        if available_replicas < desired_replicas or unavailable_replicas > 0:
            is_unhealthy = True
            if status_reason == "Healthy":
                status_reason = f"ReplicasMismatch (Available {available_replicas}/{desired_replicas})"

        return {
            "name": name,
            "namespace": deploy_ns,
            "status": status_reason,
            "desired_replicas": desired_replicas,
            "current_replicas": replicas,
            "updated_replicas": updated_replicas,
            "ready_replicas": ready_replicas,
            "available_replicas": available_replicas,
            "unavailable_replicas": unavailable_replicas,
            "conditions": formatted_conditions,
            "is_unhealthy": is_unhealthy
        }
