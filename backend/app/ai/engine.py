import json
import logging
import httpx
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from app.core.config import settings

logger = logging.getLogger(__name__)


class Diagnosis(BaseModel):
    root_cause: str = Field(..., description="Root cause of the failure")
    explanation: str = Field(..., description="Clear explanation of the root cause")
    fix: str = Field(..., description="Suggested fix recommendation")
    kubectl_command: str = Field(..., description="Exact kubectl command to resolve or inspect")
    prevention: str = Field(default="Monitor pod health and resource limits.", description="Prevention recommendation")
    confidence: int = Field(..., ge=0, le=100, description="Confidence score percentage (0-100)")


SYSTEM_PROMPT = """You are a Senior Kubernetes Site Reliability Engineer (SRE).
Your task is to analyze Kubernetes investigation evidence (Pods, Logs, Events, Deployments, Networking) and determine the exact root cause of any failure.

You MUST respond strictly with a valid JSON object with NO additional text or markdown formatting outside the JSON object.

The JSON schema MUST be:
{
  "root_cause": "Concise summary of the root cause",
  "explanation": "Detailed explanation of why the application or component failed",
  "fix": "Actionable, beginner-friendly step-by-step fix suggestion",
  "kubectl_command": "Exact kubectl command to apply the fix or inspect further",
  "prevention": "Recommendation to prevent this issue in the future",
  "confidence": 92
}

Rules:
1. Correlate evidence across Pod state, error logs, Warning events, deployment conditions, and service endpoints.
2. Avoid generic advice; give specific Kubernetes-native recommendations.
3. Provide exact, working kubectl commands.
4. Set confidence score between 0 and 100 based on strength of evidence.
5. If cluster is completely healthy, set root_cause to 'No Issues Detected', fix to 'Cluster is operating normally', and confidence to 100.
6. If multiple pods are failing, synthesize all problematic pods into the root_cause summary (e.g. 'Multiple Failing Pods: nginx-crash (Error), nginx-imagepullbackoff (ImagePullBackOff)') and provide combined fix instructions.
"""


class AIReasoningEngine:
    def __init__(
        self,
        aws_region: str = None,
        model_id: str = None,
        access_key: str = None,
        secret_key: str = None
    ):
        self.aws_region = aws_region or settings.AWS_REGION
        self.model_id = model_id or settings.AWS_BEDROCK_MODEL_ID
        self.access_key = access_key or settings.AWS_ACCESS_KEY_ID
        self.secret_key = secret_key or settings.AWS_SECRET_ACCESS_KEY

    def build_prompt(self, evidence: Dict[str, Any]) -> str:
        """Builds a structured troubleshooting prompt from investigation evidence."""
        return f"Kubernetes Investigation Payload:\n{json.dumps(evidence, indent=2)}\n\nAnalyze the payload and produce the JSON diagnosis:"

    def analyze(self, evidence: Dict[str, Any]) -> Diagnosis:
        """Sends investigation payload to AWS Bedrock Qwen LLM (with fast timeouts & fallback)."""
        user_prompt = self.build_prompt(evidence)

        # 1. Try AWS Bedrock Runtime via boto3 with fast connection timeout
        try:
            import boto3
            from botocore.config import Config
            boto_config = Config(connect_timeout=3, read_timeout=8, retries={"max_attempts": 1})
            session_kwargs = {"region_name": self.aws_region, "config": boto_config}
            if self.access_key and self.secret_key:
                session_kwargs["aws_access_key_id"] = self.access_key
                session_kwargs["aws_secret_access_key"] = self.secret_key

            bedrock_client = boto3.client("bedrock-runtime", **session_kwargs)

            # Use Bedrock Converse API for Qwen3 Coder Next model
            response = bedrock_client.converse(
                modelId=self.model_id,
                messages=[{
                    "role": "user",
                    "content": [{"text": user_prompt}]
                }],
                system=[{"text": SYSTEM_PROMPT}],
                inferenceConfig={"temperature": 0.2, "maxTokens": 2000}
            )

            content = response["output"]["message"]["content"][0]["text"]
            diagnosis = self._parse_json_response(content)
            if diagnosis:
                return diagnosis
        except Exception as e:
            logger.info(f"AWS Bedrock call did not execute ({e}). Trying secondary endpoint/fallback...")

        # 2. Try OpenRouter HTTP fallback if key present with fast timeout
        if settings.OPENROUTER_API_KEY:
            try:
                diagnosis = self._analyze_openrouter(user_prompt)
                if diagnosis:
                    return diagnosis
            except Exception as e:
                logger.warning(f"OpenRouter fallback failed: {e}")

        # 3. Rule-based fallback analyzer
        return self._generate_fallback_diagnosis(evidence, "AWS Bedrock & secondary endpoints offline")

    def _analyze_openrouter(self, user_prompt: str) -> Optional[Diagnosis]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}"
        }
        payload = {
            "model": settings.OPENROUTER_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2
        }
        url = f"{settings.OPENROUTER_BASE_URL.rstrip('/')}/chat/completions"
        with httpx.Client(timeout=8.0) as client:
            res = client.post(url, headers=headers, json=payload)
            res.raise_for_status()
            text = res.json()["choices"][0]["message"]["content"]
            return self._parse_json_response(text)

    def _parse_json_response(self, text: str) -> Optional[Diagnosis]:
        clean_content = text.strip()
        if clean_content.startswith("```json"):
            clean_content = clean_content[7:]
        if clean_content.startswith("```"):
            clean_content = clean_content[3:]
        if clean_content.endswith("```"):
            clean_content = clean_content[:-3]
        clean_content = clean_content.strip()

        parsed = json.loads(clean_content)
        return Diagnosis(
            root_cause=str(parsed.get("root_cause", "Unknown Root Cause")),
            explanation=str(parsed.get("explanation", "Unable to determine detailed explanation.")),
            fix=str(parsed.get("fix", "Inspect container logs and pod status.")),
            kubectl_command=str(parsed.get("kubectl_command", "kubectl get pods -A")),
            prevention=str(parsed.get("prevention", "Implement liveness and readiness probes.")),
            confidence=int(parsed.get("confidence", 80))
        )

    def _generate_fallback_diagnosis(self, evidence: Dict[str, Any], error_msg: str) -> Diagnosis:
        """Rule-based fallback analyzer when AI endpoint is offline or credentials are not supplied."""
        pods = evidence.get("pods", {})
        logs = evidence.get("logs", {})
        events = evidence.get("events", {})
        deployments = evidence.get("deployments", {})

        problematic_pods = pods.get("problematic_pods", [])
        if problematic_pods:
            if len(problematic_pods) > 1:
                summaries = [f"{p.get('name')} ({p.get('status')})" for p in problematic_pods]
                fixes = []
                commands = []
                for p in problematic_pods:
                    p_name = p.get("name")
                    p_status = str(p.get("status", ""))
                    if "ImagePull" in p_status or "ErrImagePull" in p_status:
                        fixes.append(f"Verify container image tag/registry for {p_name}")
                        commands.append(f"kubectl describe pod {p_name}")
                    elif "Crash" in p_status or "Error" in p_status:
                        fixes.append(f"Inspect container logs for {p_name}")
                        commands.append(f"kubectl logs {p_name} --previous")
                    else:
                        fixes.append(f"Inspect pod status for {p_name}")
                        commands.append(f"kubectl describe pod {p_name}")

                return Diagnosis(
                    root_cause=f"Multiple Unhealthy Pods: {', '.join(summaries)}",
                    explanation=f"Found {len(problematic_pods)} failing pods in target namespace: {', '.join(summaries)}.",
                    fix="; ".join(fixes),
                    kubectl_command="; ".join(commands),
                    prevention="Configure container health probes, image tag verification, and resource limits.",
                    confidence=90
                )

            pod = problematic_pods[0]
            pod_name = pod.get("name", "pod")
            pod_status = pod.get("status", "Unknown")

            if "CrashLoopBackOff" in pod_status or "Error" in pod_status:
                return Diagnosis(
                    root_cause=f"Pod {pod_name} is in {pod_status}",
                    explanation=f"Container in pod {pod_name} crashed repeatedly on startup. Check environment variables or configuration.",
                    fix=f"Inspect error logs for {pod_name} and verify environment variables.",
                    kubectl_command=f"kubectl logs {pod_name} --previous",
                    prevention="Add configuration validation checks during container startup.",
                    confidence=85
                )
            elif "ImagePullBackOff" in pod_status or "ErrImagePull" in pod_status:
                return Diagnosis(
                    root_cause=f"Pod {pod_name} failed to pull container image ({pod_status})",
                    explanation=f"Kubernetes node could not download the container image specified in deployment for {pod_name}.",
                    fix="Verify image tag exists in container registry and imagePullSecrets are configured.",
                    kubectl_command=f"kubectl describe pod {pod_name}",
                    prevention="Use immutable image tags and verify registry permissions in CI/CD pipeline.",
                    confidence=90
                )
            elif "OOMKilled" in pod_status:
                return Diagnosis(
                    root_cause=f"Pod {pod_name} exceeded memory limit (OOMKilled)",
                    explanation="The container exceeded its configured memory request/limit and was terminated by the Linux kernel OOM killer.",
                    fix=f"Increase memory limits for pod {pod_name} in deployment manifest.",
                    kubectl_command=f"kubectl top pod {pod_name}",
                    prevention="Conduct load testing to determine baseline memory utilization and set appropriate memory limits.",
                    confidence=95
                )

        if not pods.get("healthy", True) or not deployments.get("healthy", True):
            return Diagnosis(
                root_cause="Kubernetes Workload Unhealthy",
                explanation="One or more pods or deployments are not in a Ready or Running state.",
                fix="Review deployment status and events to locate failing resources.",
                kubectl_command="kubectl get pods,deployments -A",
                prevention="Configure readiness probes to prevent routing traffic to unready pods.",
                confidence=75
            )

        return Diagnosis(
            root_cause="No Major Issues Detected",
            explanation="All inspected pods, deployments, and services appear healthy in the target namespace.",
            fix="No action required. Cluster operating within normal parameters.",
            kubectl_command="kubectl get pods -n default",
            prevention="Set up Prometheus/Grafana alerts for proactive monitoring.",
            confidence=95
        )
