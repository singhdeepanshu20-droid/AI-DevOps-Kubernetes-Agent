from typing import Any, Dict, List, Optional
from loguru import logger
from app.kubernetes.executor import KubectlExecutor


class NetworkInspector:
    """Inspects Kubernetes networking, services, and endpoints for anomalies."""

    def __init__(self, executor: Optional[KubectlExecutor] = None):
        self.executor = executor or KubectlExecutor()

    def inspect(self, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Inspects services and endpoints for missing endpoints or misconfigurations."""
        svc_args = ["get", "services"]
        ep_args = ["get", "endpoints"]
        if not namespace:
            svc_args.append("-A")
            ep_args.append("-A")

        services_data, exec_svc = self.executor.execute_json(svc_args, namespace=namespace)
        endpoints_data, exec_ep = self.executor.execute_json(ep_args, namespace=namespace)

        if not exec_svc.success or not services_data:
            logger.warning(f"Failed to fetch services: {exec_svc.stderr}")
            return {
                "healthy": False,
                "total_services": 0,
                "healthy_count": 0,
                "unhealthy_count": 0,
                "problematic_services": [],
                "error": exec_svc.stderr or "Failed to query services"
            }

        # Build lookup table for endpoints: (namespace, name) -> subsets
        endpoints_map: Dict[tuple[str, str], Any] = {}
        if endpoints_data and "items" in endpoints_data:
            for ep_item in endpoints_data["items"]:
                ep_meta = ep_item.get("metadata", {})
                ep_ns = ep_meta.get("namespace", "default")
                ep_name = ep_meta.get("name", "")
                endpoints_map[(ep_ns, ep_name)] = ep_item.get("subsets", [])

        svc_items = services_data.get("items", [])
        total_services = len(svc_items)
        problematic_services: List[Dict[str, Any]] = []

        for svc in svc_items:
            svc_info = self._analyze_service(svc, endpoints_map)
            if svc_info["is_problematic"]:
                del svc_info["is_problematic"]
                problematic_services.append(svc_info)

        unhealthy_count = len(problematic_services)
        healthy_count = total_services - unhealthy_count
        healthy = (unhealthy_count == 0)

        return {
            "healthy": healthy,
            "total_services": total_services,
            "healthy_count": healthy_count,
            "unhealthy_count": unhealthy_count,
            "problematic_services": problematic_services
        }

    def _analyze_service(
        self,
        svc: Dict[str, Any],
        endpoints_map: Dict[tuple[str, str], Any]
    ) -> Dict[str, Any]:
        """Analyzes a single service manifest and its corresponding endpoints."""
        metadata = svc.get("metadata", {})
        spec = svc.get("spec", {})

        name = metadata.get("name", "unknown")
        svc_ns = metadata.get("namespace", "default")
        svc_type = spec.get("type", "ClusterIP")
        selector = spec.get("selector", {})
        ports = spec.get("ports", [])

        is_problematic = False
        issue = "Healthy"
        detail = ""

        # Headless or ExternalName services may not have selectors
        if selector and svc_type != "ExternalName":
            subsets = endpoints_map.get((svc_ns, name))
            if subsets is None:
                is_problematic = True
                issue = "MissingEndpointsObject"
                detail = f"Endpoints resource for service '{name}' in namespace '{svc_ns}' does not exist."
            elif not subsets:
                is_problematic = True
                issue = "NoEndpoints"
                detail = f"Service has selector {selector} but 0 endpoints were found (selector mismatch or pods not running)."
            else:
                has_ready_addresses = False
                not_ready_count = 0
                for subset in subsets:
                    addresses = subset.get("addresses", [])
                    not_ready_addresses = subset.get("notReadyAddresses", [])
                    if addresses:
                        has_ready_addresses = True
                    not_ready_count += len(not_ready_addresses)

                if not has_ready_addresses:
                    is_problematic = True
                    issue = "NoReadyEndpoints"
                    detail = f"Service has {not_ready_count} target pods, but none are in Ready state."

        formatted_ports = []
        for p in ports:
            formatted_ports.append({
                "name": p.get("name"),
                "port": p.get("port"),
                "targetPort": p.get("targetPort"),
                "protocol": p.get("protocol", "TCP")
            })

        return {
            "name": name,
            "namespace": svc_ns,
            "type": svc_type,
            "selector": selector,
            "ports": formatted_ports,
            "issue": issue,
            "detail": detail,
            "is_problematic": is_problematic
        }
