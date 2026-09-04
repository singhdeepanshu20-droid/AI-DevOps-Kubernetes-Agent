"""Kubernetes inspection layer module re-exports and facade functions."""

from app.kubernetes.executor import KubectlExecutor
from app.kubernetes.pod_inspector import PodInspector
from app.kubernetes.logs_collector import LogsCollector
from app.kubernetes.events_analyzer import EventsAnalyzer
from app.kubernetes.deployment_inspector import DeploymentInspector
from app.kubernetes.network_inspector import NetworkInspector
from app.kubernetes.investigation_service import InvestigationService


def inspect_pods(namespace=None):
    """Facade function for inspecting pods in the cluster."""
    inspector = PodInspector()
    return inspector.inspect(namespace=namespace)


def get_cluster_status(namespace=None):
    """Facade function for retrieving cluster status overview."""
    service = InvestigationService()
    return service.run_investigation(namespace=namespace)


__all__ = [
    "KubectlExecutor",
    "PodInspector",
    "LogsCollector",
    "EventsAnalyzer",
    "DeploymentInspector",
    "NetworkInspector",
    "InvestigationService",
    "inspect_pods",
    "get_cluster_status",
]
