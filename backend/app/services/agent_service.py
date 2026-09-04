"""Agent service orchestrating Kubernetes cluster investigation, AWS Bedrock AI reasoning, and DynamoDB persistence."""

from typing import Any, Dict, Optional
from loguru import logger
from app.kubernetes.investigation_service import InvestigationService
from app.ai.engine import AIReasoningEngine
from app.services.history_service import AWSDynamoDBHistoryService


class AgentService:
    def __init__(
        self,
        investigation_service: Optional[InvestigationService] = None,
        ai_engine: Optional[AIReasoningEngine] = None,
        history_service: Optional[AWSDynamoDBHistoryService] = None
    ):
        self.investigation_service = investigation_service or InvestigationService()
        self.ai_engine = ai_engine or AIReasoningEngine()
        self.history_service = history_service or AWSDynamoDBHistoryService()

    def run_investigation(
        self,
        namespace: Optional[str] = None,
        cluster_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Orchestrates cluster evidence collection, AWS Bedrock AI reasoning, and DynamoDB logging."""
        try:
            investigation_data = self.investigation_service.run_investigation(
                namespace=namespace,
                cluster_context=cluster_context
            )

            diagnosis = self.ai_engine.analyze(investigation_data)

            # Save to AWS DynamoDB / History Service
            try:
                self.history_service.save_investigation(
                    root_cause=diagnosis.root_cause,
                    namespace=namespace or "default",
                    confidence=diagnosis.confidence,
                    status="success",
                    fix=diagnosis.fix,
                    kubectl_command=diagnosis.kubectl_command
                )
            except Exception as hist_err:
                logger.warning(f"Failed to persist history to DynamoDB: {hist_err}")

            return {
                "status": "success",
                "investigation": investigation_data,
                "diagnosis": diagnosis.model_dump()
            }
        except Exception as exc:
            logger.error(f"Investigation execution failed: {exc}")
            error_details = (
                "Unable to connect to Kubernetes cluster or AWS Bedrock.\n\n"
                "Please verify:\n"
                "- kubeconfig path\n"
                "- cluster access\n"
                "- AWS credentials / IAM policies\n"
                "- kubectl permissions"
            )
            return {
                "status": "error",
                "message": error_details,
                "error": str(exc),
                "investigation": {},
                "diagnosis": {
                    "root_cause": "Cluster Connection or AWS Bedrock Failure",
                    "explanation": f"Failed to execute Kubernetes investigation: {str(exc)}",
                    "fix": "Verify kubeconfig path, kubectl cluster access, and AWS Bedrock credentials.",
                    "kubectl_command": "kubectl get nodes",
                    "prevention": "Ensure valid Kubeconfig and AWS credentials are set up.",
                    "confidence": 0
                }
            }
