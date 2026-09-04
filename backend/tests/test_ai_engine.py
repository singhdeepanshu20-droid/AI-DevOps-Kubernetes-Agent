import unittest
from unittest.mock import MagicMock, patch
from app.ai.engine import AIReasoningEngine, Diagnosis


class TestAIReasoningEngine(unittest.TestCase):

    def setUp(self):
        self.engine = AIReasoningEngine(aws_region="us-east-1", model_id="anthropic.claude-3-5-sonnet-20240620-v1:0")
        self.mock_evidence = {
            "pods": {
                "healthy": False,
                "total_pods": 2,
                "unhealthy_count": 1,
                "problematic_pods": [{
                    "name": "payment-service-6789-xyz",
                    "namespace": "default",
                    "status": "CrashLoopBackOff",
                    "restart_count": 5
                }]
            },
            "logs": {
                "collected_count": 1,
                "pod_logs": [{
                    "pod_name": "payment-service-6789-xyz",
                    "error_highlights": ["Fatal Error: DATABASE_URL env variable missing"]
                }]
            },
            "events": {"warning_count": 1, "problematic_events": []},
            "deployments": {"healthy": True},
            "network": {"healthy": True}
        }

    @patch("boto3.client")
    def test_bedrock_successful_analysis(self, mock_boto_client):
        mock_bedrock = MagicMock()
        mock_bedrock.converse.return_value = {
            "output": {
                "message": {
                    "content": [{
                        "text": '{"root_cause": "DATABASE_URL missing", "explanation": "App failed to connect to database.", "fix": "Add DATABASE_URL env var", "kubectl_command": "kubectl edit deployment payment-service", "prevention": "Use secret manager", "confidence": 95}'
                    }]
                }
            }
        }
        mock_boto_client.return_value = mock_bedrock

        diagnosis = self.engine.analyze(self.mock_evidence)

        self.assertEqual(diagnosis.root_cause, "DATABASE_URL missing")
        self.assertEqual(diagnosis.confidence, 95)
        self.assertEqual(diagnosis.kubectl_command, "kubectl edit deployment payment-service")

    def test_fallback_analysis_crashloop(self):
        # When AWS Bedrock is offline or unauthenticated, fallback engine takes over
        offline_engine = AIReasoningEngine(aws_region="invalid-region")
        diagnosis = offline_engine.analyze(self.mock_evidence)

        self.assertIn("payment-service-6789-xyz", diagnosis.root_cause)
        self.assertEqual(diagnosis.confidence, 85)
        self.assertIn("kubectl logs", diagnosis.kubectl_command)


if __name__ == "__main__":
    unittest.main()
