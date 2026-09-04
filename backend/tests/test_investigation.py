import json
import unittest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.kubernetes.executor import KubectlExecutor, ExecResult
from app.kubernetes.pod_inspector import PodInspector
from app.kubernetes.logs_collector import LogsCollector
from app.kubernetes.events_analyzer import EventsAnalyzer
from app.kubernetes.deployment_inspector import DeploymentInspector
from app.kubernetes.network_inspector import NetworkInspector
from app.kubernetes.investigation_service import InvestigationService


class TestKubectlExecutor(unittest.TestCase):

    def test_executor_command_building(self):
        executor = KubectlExecutor(context="my-cluster")
        cmd = executor._build_command(["get", "pods"], namespace="default")
        self.assertEqual(cmd, ["kubectl", "--context", "my-cluster", "--request-timeout", "8s", "-n", "default", "get", "pods"])

    def test_execute_json_parsing(self):
        executor = KubectlExecutor()
        executor.execute = MagicMock(return_value=ExecResult(
            success=True,
            stdout=json.dumps({"items": []}),
            stderr="",
            exit_code=0,
            command=["kubectl", "get", "pods", "-o", "json"]
        ))

        data, res = executor.execute_json(["get", "pods"])
        self.assertIsNotNone(data)
        self.assertEqual(data.get("items"), [])
        self.assertTrue(res.success)


class TestInspectors(unittest.TestCase):

    def test_pod_inspector_detects_problematic_pods(self):
        mock_executor = MagicMock(spec=KubectlExecutor)
        mock_pod_json = {
            "items": [
                {
                    "metadata": {"name": "healthy-pod", "namespace": "default"},
                    "status": {
                        "phase": "Running",
                        "containerStatuses": [{"name": "c1", "ready": True, "restartCount": 0, "state": {"running": {}}}]
                    }
                },
                {
                    "metadata": {"name": "failing-pod", "namespace": "default"},
                    "status": {
                        "phase": "Running",
                        "containerStatuses": [{
                            "name": "c2",
                            "ready": False,
                            "restartCount": 5,
                            "state": {"waiting": {"reason": "CrashLoopBackOff", "message": "Back-off restarting container"}}
                        }]
                    }
                }
            ]
        }
        mock_executor.execute_json.return_value = (mock_pod_json, ExecResult(True, "", "", 0, []))

        inspector = PodInspector(executor=mock_executor)
        result = inspector.inspect()

        self.assertFalse(result["healthy"])
        self.assertEqual(result["total_pods"], 2)
        self.assertEqual(result["unhealthy_count"], 1)
        self.assertEqual(result["problematic_pods"][0]["name"], "failing-pod")
        self.assertEqual(result["problematic_pods"][0]["status"], "CrashLoopBackOff")

    def test_logs_collector_fetches_and_extracts_errors(self):
        mock_executor = MagicMock(spec=KubectlExecutor)
        mock_executor.execute.return_value = ExecResult(
            success=True,
            stdout="2026-09-03 info starting app...\n2026-09-03 ERROR Exception: Database connection refused\n",
            stderr="",
            exit_code=0,
            command=[]
        )

        collector = LogsCollector(executor=mock_executor)
        problematic_pods = [{
            "name": "failing-pod",
            "namespace": "default",
            "containers": [{"name": "c2"}]
        }]
        result = collector.collect(problematic_pods)

        self.assertEqual(result["collected_count"], 1)
        pod_log = result["pod_logs"][0]
        self.assertEqual(pod_log["pod_name"], "failing-pod")
        self.assertTrue(len(pod_log["error_highlights"]) > 0)
        self.assertIn("Database connection refused", pod_log["error_highlights"][0])

    def test_events_analyzer_filters_warnings(self):
        mock_executor = MagicMock(spec=KubectlExecutor)
        mock_events_json = {
            "items": [
                {
                    "type": "Warning",
                    "reason": "FailedScheduling",
                    "message": "0/1 nodes are available: insufficient cpu",
                    "count": 3,
                    "involvedObject": {"kind": "Pod", "name": "unscheduled-pod", "namespace": "default"}
                }
            ]
        }
        mock_executor.execute_json.return_value = (mock_events_json, ExecResult(True, "", "", 0, []))

        analyzer = EventsAnalyzer(executor=mock_executor)
        result = analyzer.analyze()

        self.assertEqual(result["warning_count"], 1)
        self.assertEqual(result["problematic_events"][0]["reason"], "FailedScheduling")

    def test_deployment_inspector_detects_unhealthy(self):
        mock_executor = MagicMock(spec=KubectlExecutor)
        mock_deploy_json = {
            "items": [
                {
                    "metadata": {"name": "web-deploy", "namespace": "default"},
                    "spec": {"replicas": 3},
                    "status": {
                        "replicas": 3,
                        "readyReplicas": 1,
                        "availableReplicas": 1,
                        "unavailableReplicas": 2,
                        "conditions": [
                            {"type": "Available", "status": "False", "reason": "MinimumReplicasUnavailable", "message": "Deployment has minimum availability."}
                        ]
                    }
                }
            ]
        }
        mock_executor.execute_json.return_value = (mock_deploy_json, ExecResult(True, "", "", 0, []))

        inspector = DeploymentInspector(executor=mock_executor)
        result = inspector.inspect()

        self.assertFalse(result["healthy"])
        self.assertEqual(result["unhealthy_count"], 1)
        self.assertEqual(result["unhealthy_deployments"][0]["name"], "web-deploy")

    def test_network_inspector_detects_no_endpoints(self):
        mock_executor = MagicMock(spec=KubectlExecutor)
        mock_svc_json = {
            "items": [
                {
                    "metadata": {"name": "web-svc", "namespace": "default"},
                    "spec": {
                        "type": "ClusterIP",
                        "selector": {"app": "web"},
                        "ports": [{"name": "http", "port": 80, "targetPort": 8080}]
                    }
                }
            ]
        }
        mock_ep_json = {
            "items": [
                {
                    "metadata": {"name": "web-svc", "namespace": "default"},
                    "subsets": []
                }
            ]
        }
        mock_executor.execute_json.side_effect = [
            (mock_svc_json, ExecResult(True, "", "", 0, [])),
            (mock_ep_json, ExecResult(True, "", "", 0, []))
        ]

        inspector = NetworkInspector(executor=mock_executor)
        result = inspector.inspect()

        self.assertFalse(result["healthy"])
        self.assertEqual(result["unhealthy_count"], 1)
        self.assertEqual(result["problematic_services"][0]["issue"], "NoEndpoints")


class TestAPIEndpoints(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")

    def test_investigate_endpoint(self):
        response = self.client.post("/investigate", json={})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("investigation", data)
        inv = data["investigation"]
        self.assertIn("pods", inv)
        self.assertIn("logs", inv)
        self.assertIn("events", inv)
        self.assertIn("deployments", inv)
        self.assertIn("network", inv)


if __name__ == "__main__":
    unittest.main()
