from typing import Any, Dict, Optional
from loguru import logger
from app.kubernetes.executor import KubectlExecutor
from app.kubernetes.pod_inspector import PodInspector
from app.kubernetes.logs_collector import LogsCollector
from app.kubernetes.events_analyzer import EventsAnalyzer
from app.kubernetes.deployment_inspector import DeploymentInspector
from app.kubernetes.network_inspector import NetworkInspector


class InvestigationService:
    """Orchestrates Kubernetes investigation across pods, logs, events, deployments, and networking."""

    def __init__(
        self,
        executor: Optional[KubectlExecutor] = None,
        pod_inspector: Optional[PodInspector] = None,
        logs_collector: Optional[LogsCollector] = None,
        events_analyzer: Optional[EventsAnalyzer] = None,
        deployment_inspector: Optional[DeploymentInspector] = None,
        network_inspector: Optional[NetworkInspector] = None
    ):
        self.executor = executor or KubectlExecutor()
        self.pod_inspector = pod_inspector or PodInspector(self.executor)
        self.logs_collector = logs_collector or LogsCollector(self.executor)
        self.events_analyzer = events_analyzer or EventsAnalyzer(self.executor)
        self.deployment_inspector = deployment_inspector or DeploymentInspector(self.executor)
        self.network_inspector = network_inspector or NetworkInspector(self.executor)

    def run_investigation(
        self,
        namespace: Optional[str] = None,
        cluster_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Runs complete Kubernetes evidence gathering pipeline."""
        logger.info(f"Starting Kubernetes cluster investigation (context: {cluster_context or 'default'}, namespace: {namespace or 'all'})...")

        if cluster_context:
            self.executor.context = cluster_context

        # 1. Check Pods
        logger.info("Step 1/5: Inspecting Pods...")
        pods_result = self.pod_inspector.inspect(namespace=namespace)
        if pods_result.get("error"):
            logger.warning(f"Pod inspection failed: {pods_result.get('error')}")

        # 2. Collect Logs for problematic pods
        logger.info("Step 2/5: Collecting Logs for unhealthy pods...")
        problematic_pods = pods_result.get("problematic_pods", [])
        logs_result = self.logs_collector.collect(problematic_pods)

        # 3. Analyze Events
        logger.info("Step 3/5: Analyzing Cluster Events...")
        events_result = self.events_analyzer.analyze(namespace=namespace)

        # 4. Inspect Deployments
        logger.info("Step 4/5: Inspecting Deployments...")
        deployments_result = self.deployment_inspector.inspect(namespace=namespace)

        # 5. Check Networking
        logger.info("Step 5/5: Inspecting Network Services & Endpoints...")
        network_result = self.network_inspector.inspect(namespace=namespace)

        logger.info("Kubernetes cluster investigation completed.")

        return {
            "pods": pods_result,
            "logs": logs_result,
            "events": events_result,
            "deployments": deployments_result,
            "network": network_result
        }
