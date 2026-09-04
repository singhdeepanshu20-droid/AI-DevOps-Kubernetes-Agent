from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from typing import Any, Dict, List, Optional
import json
import asyncio
from app.models.schemas import HealthResponse, InvestigationRequest, InvestigationResponse
from app.services.agent_service import AgentService
from app.services.history_service import AWSDynamoDBHistoryService
from app.kubernetes.executor import KubectlExecutor

router = APIRouter()
agent_service = AgentService()
history_service = AWSDynamoDBHistoryService()


@router.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        service="ai-kubernetes-agent"
    )


@router.get("/clusters")
def get_clusters():
    """Retrieves list of Kubernetes clusters/contexts from local kubeconfig."""
    executor = KubectlExecutor()
    clusters = executor.get_available_contexts()
    current_context = executor.get_current_context()
    return {
        "clusters": clusters,
        "current_context": current_context
    }


@router.post("/investigate", response_model=InvestigationResponse)
def investigate_cluster(request: InvestigationRequest):
    """Executes Kubernetes investigation collecting cluster evidence and performing AI reasoning."""
    res = agent_service.run_investigation(
        namespace=request.namespace,
        cluster_context=request.cluster_context
    )
    return InvestigationResponse(
        status=res.get("status", "success"),
        investigation=res.get("investigation", {}),
        diagnosis=res.get("diagnosis"),
        message=res.get("message", "Kubernetes cluster investigation completed with AWS Bedrock AI diagnosis.")
    )


@router.get("/investigate/stream")
async def investigate_cluster_stream(
    namespace: str = "default",
    cluster_context: Optional[str] = Query(None)
):
    """SSE (Server-Sent Events) stream for realtime investigation progress and AI diagnosis."""
    async def event_generator():
        steps = [
            "Checking Pods",
            "Reading Logs",
            "Analyzing Events",
            "Inspecting Deployments",
            "Checking Networking"
        ]
        try:
            for idx, step_name in enumerate(steps):
                data = json.dumps({"step": idx, "message": step_name, "status": "in_progress"})
                yield f"data: {data}\n\n"
                await asyncio.sleep(0.3)

            # AI Reasoning step notification
            data_ai = json.dumps({"step": 5, "message": "AI Reasoning (AWS Bedrock Qwen)", "status": "in_progress"})
            yield f"data: {data_ai}\n\n"

            # Execute investigation & AI reasoning off the main thread so SSE stream never freezes
            try:
                res = await asyncio.wait_for(
                    asyncio.to_thread(
                        agent_service.run_investigation,
                        namespace=namespace,
                        cluster_context=cluster_context
                    ),
                    timeout=40.0
                )
            except asyncio.TimeoutError:
                res = {
                    "status": "error",
                    "message": "Kubernetes investigation timed out after 40s. Verify cluster accessibility.",
                    "investigation": {},
                    "diagnosis": {
                        "root_cause": "Cluster Timeout",
                        "explanation": "Target cluster did not respond within 40 seconds.",
                        "fix": "Check local cluster state and kubectl connection.",
                        "kubectl_command": "kubectl get nodes",
                        "prevention": "Ensure target cluster control plane is active.",
                        "confidence": 0
                    }
                }

            # Check if execution failed
            if res.get("status") == "error":
                data_error = json.dumps({
                    "step": -1,
                    "message": "Investigation Failed",
                    "status": "error",
                    "error": res.get("message"),
                    "result": res
                })
                yield f"data: {data_error}\n\n"
                return

            # Final completion event
            data_final = json.dumps({
                "step": 6,
                "message": "Root Cause Found",
                "status": "completed",
                "result": res
            })
            yield f"data: {data_final}\n\n"

        except Exception as e:
            data_err = json.dumps({
                "step": -1,
                "message": "Error occurred during investigation stream",
                "status": "error",
                "error": str(e)
            })
            yield f"data: {data_err}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/history", response_model=List[Dict[str, Any]])
def get_investigation_history():
    """Retrieves previous investigation history from AWS DynamoDB (or local cache)."""
    return history_service.get_history()
