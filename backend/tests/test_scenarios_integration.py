import unittest
from unittest.mock import MagicMock
from app.ai.engine import AIReasoningEngine
from app.kubernetes.investigation_service import InvestigationService
from app.kubernetes.executor import KubectlExecutor, ExecResult
from app.services.agent_service import AgentService


class TestEndToEndFailureScenarios(unittest.TestCase):

    def setUp(self):
        self.ai_engine = AIReasoningEngine()

    def test_scenario_1_crashloopbackoff(self):
        evidence = {
            "pods": {
                "healthy": False,
                "total_pods": 1,
                "unhealthy_count": 1,
                "problematic_pods": [{
                    "name": "test-crashloop-7489-xyz",
                    "namespace": "default",
                    "status": "CrashLoopBackOff",
                    "restart_count": 8
                }]
            },
            "logs": {
                "collected_count": 1,
                "pod_logs": [{
                    "pod_name": "test-crashloop-7489-xyz",
                    "error_highlights": ["FATAL ERROR: REQUIRED_DB_URL environment variable is missing!"]
                }]
            },
            "events": {"warning_count": 1, "problematic_events": []},
            "deployments": {"healthy": True},
            "network": {"healthy": True}
        }

        diagnosis = self.ai_engine.analyze(evidence)
        combined_text = (diagnosis.root_cause + " " + diagnosis.explanation).lower()
        self.assertTrue(
            "crashloop" in combined_text or "environment" in combined_text or "required_db_url" in combined_text,
            f"Expected crashloop or env var error in diagnosis, got: {diagnosis.root_cause}"
        )
        self.assertTrue(diagnosis.confidence >= 50)

    def test_scenario_2_imagepullbackoff(self):
        evidence = {
            "pods": {
                "healthy": False,
                "total_pods": 1,
                "unhealthy_count": 1,
                "problematic_pods": [{
                    "name": "test-imagepull-9876-abc",
                    "namespace": "default",
                    "status": "ImagePullBackOff",
                    "restart_count": 0
                }]
            },
            "logs": {"collected_count": 0, "pod_logs": []},
            "events": {
                "warning_count": 1,
                "problematic_events": [{
                    "reason": "Failed",
                    "message": "Failed to pull image 'nginx:nonexistent-tag-v9999': rpc error: code = NotFound",
                    "kind": "Pod",
                    "name": "test-imagepull-9876-abc"
                }]
            },
            "deployments": {"healthy": True},
            "network": {"healthy": True}
        }

        diagnosis = self.ai_engine.analyze(evidence)
        combined_text = (diagnosis.root_cause + " " + diagnosis.explanation).lower()
        self.assertIn("image", combined_text)
        self.assertTrue(diagnosis.confidence >= 50)

    def test_scenario_3_oomkilled(self):
        evidence = {
            "pods": {
                "healthy": False,
                "total_pods": 1,
                "unhealthy_count": 1,
                "problematic_pods": [{
                    "name": "test-oomkilled-5432-def",
                    "namespace": "default",
                    "status": "OOMKilled",
                    "restart_count": 3
                }]
            },
            "logs": {"collected_count": 0, "pod_logs": []},
            "events": {"warning_count": 0, "problematic_events": []},
            "deployments": {"healthy": True},
            "network": {"healthy": True}
        }

        diagnosis = self.ai_engine.analyze(evidence)
        combined_text = (diagnosis.root_cause + " " + diagnosis.explanation).lower()
        self.assertTrue(
            "oom" in combined_text or "memory" in combined_text,
            f"Expected OOM/memory in diagnosis, got: {diagnosis.root_cause}"
        )
        self.assertTrue(diagnosis.confidence >= 50)

    def test_scenario_4_service_selector_mismatch(self):
        evidence = {
            "pods": {
                "healthy": True,
                "total_pods": 1,
                "unhealthy_count": 0,
                "problematic_pods": []
            },
            "logs": {"collected_count": 0, "pod_logs": []},
            "events": {"warning_count": 0, "problematic_events": []},
            "deployments": {"healthy": True},
            "network": {
                "healthy": False,
                "unhealthy_count": 1,
                "problematic_services": [{
                    "name": "test-mismatched-service",
                    "namespace": "default",
                    "issue": "NoEndpoints",
                    "selector": {"app": "wrong-app-label-name"}
                }]
            }
        }

        diagnosis = self.ai_engine.analyze(evidence)
        self.assertTrue(len(diagnosis.root_cause) > 0)
        self.assertTrue(diagnosis.confidence > 0)

    def test_healthy_cluster_scenario(self):
        evidence = {
            "pods": {"healthy": True, "total_pods": 5, "unhealthy_count": 0, "problematic_pods": []},
            "logs": {"collected_count": 0, "pod_logs": []},
            "events": {"warning_count": 0, "problematic_events": []},
            "deployments": {"healthy": True, "unhealthy_count": 0, "unhealthy_deployments": []},
            "network": {"healthy": True, "unhealthy_count": 0, "problematic_services": []}
        }

        diagnosis = self.ai_engine.analyze(evidence)
        combined_text = (diagnosis.root_cause + " " + diagnosis.explanation).lower()
        self.assertTrue(
            "no" in combined_text or "healthy" in combined_text or "normal" in combined_text,
            f"Expected healthy indication, got: {diagnosis.root_cause}"
        )
        self.assertTrue(diagnosis.confidence >= 50)

    def test_agent_service_error_resilience(self):
        mock_inv = MagicMock()
        mock_inv.run_investigation.side_effect = Exception("kubectl executable not found in PATH")
        agent_svc = AgentService(investigation_service=mock_inv)

        res = agent_svc.run_investigation()
        self.assertEqual(res["status"], "error")
        self.assertIn("Unable to connect to Kubernetes cluster", res["message"])


if __name__ == "__main__":
    unittest.main()
