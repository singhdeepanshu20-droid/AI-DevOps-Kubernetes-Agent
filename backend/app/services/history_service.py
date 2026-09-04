import time
import logging
from typing import Any, Dict, List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

# In-memory history cache fallback
_LOCAL_HISTORY_CACHE: List[Dict[str, Any]] = [
    {
        "id": "inv-sample-aws-1",
        "timestamp": "14:22:10",
        "root_cause": "CrashLoopBackOff (DATABASE_URL missing)",
        "namespace": "default",
        "confidence": 92,
        "status": "success",
        "fix": "Add missing environment variable",
        "kubectl_command": "kubectl edit deployment payment-service"
    },
    {
        "id": "inv-sample-aws-2",
        "timestamp": "11:05:40",
        "root_cause": "ImagePullBackOff (Invalid tag)",
        "namespace": "kube-system",
        "confidence": 90,
        "status": "success",
        "fix": "Fix image tag in manifest",
        "kubectl_command": "kubectl set image deployment/web nginx=nginx:1.25"
    }
]


class AWSDynamoDBHistoryService:
    def __init__(self, table_name: Optional[str] = None, region_name: Optional[str] = None):
        self.table_name = table_name or settings.AWS_DYNAMODB_TABLE
        self.region_name = region_name or settings.AWS_REGION

    def save_investigation(
        self,
        root_cause: str,
        namespace: str,
        confidence: int,
        status: str = "success",
        fix: Optional[str] = None,
        kubectl_command: Optional[str] = None
    ) -> Dict[str, Any]:
        """Saves investigation item to AWS DynamoDB Table (or fallback in-memory cache)."""
        item_id = f"inv-{int(time.time() * 1000)}"
        timestamp_str = time.strftime("%H:%M:%S")

        record = {
            "id": item_id,
            "timestamp": timestamp_str,
            "root_cause": root_cause,
            "namespace": namespace or "default",
            "confidence": confidence,
            "status": status,
            "fix": fix or "",
            "kubectl_command": kubectl_command or ""
        }

        # Try AWS DynamoDB PutItem via boto3
        try:
            import boto3
            session_kwargs = {"region_name": self.region_name}
            if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
                session_kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
                session_kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY

            dynamodb = boto3.resource("dynamodb", **session_kwargs)
            table = dynamodb.Table(self.table_name)
            table.put_item(Item=record)
            logger.info(f"Successfully saved investigation {item_id} to AWS DynamoDB table {self.table_name}")
        except Exception as e:
            logger.info(f"AWS DynamoDB put_item bypassed ({e}). Saved to local session cache.")

        # Always update local cache for instant retrieval
        _LOCAL_HISTORY_CACHE.insert(0, record)
        if len(_LOCAL_HISTORY_CACHE) > 20:
            _LOCAL_HISTORY_CACHE.pop()

        return record

    def get_history(self) -> List[Dict[str, Any]]:
        """Fetches investigation history from AWS DynamoDB Table (or fallback in-memory cache)."""
        try:
            import boto3
            session_kwargs = {"region_name": self.region_name}
            if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
                session_kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
                session_kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY

            dynamodb = boto3.resource("dynamodb", **session_kwargs)
            table = dynamodb.Table(self.table_name)
            response = table.scan(Limit=10)
            items = response.get("Items", [])
            if items:
                return items
        except Exception as e:
            logger.info(f"AWS DynamoDB scan bypassed ({e}). Returning local session history.")

        return _LOCAL_HISTORY_CACHE
