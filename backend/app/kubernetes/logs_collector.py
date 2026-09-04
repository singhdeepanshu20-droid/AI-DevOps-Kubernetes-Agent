import re
from typing import Any, Dict, List, Optional
from loguru import logger
from app.kubernetes.executor import KubectlExecutor

ERROR_PATTERNS = [
    re.compile(p, re.IGNORECASE) for p in [
        r"exception",
        r"fatal",
        r"error",
        r"failed",
        r"failure",
        r"connection refused",
        r"connect failure",
        r"timeout",
        r"missing",
        r"not found",
        r"panic",
        r"unhandled",
        r"denied",
        r"unauthorized",
        r"invalid"
    ]
]


class LogsCollector:
    """Collects and filters logs for problematic pods."""

    def __init__(self, executor: Optional[KubectlExecutor] = None):
        self.executor = executor or KubectlExecutor()

    def collect(
        self,
        problematic_pods: List[Dict[str, Any]],
        tail_lines: int = 50,
        max_error_highlights: int = 10
    ) -> Dict[str, Any]:
        """Fetches logs for problematic pods and extracts error highlights."""
        collected_logs: List[Dict[str, Any]] = []

        for pod in problematic_pods:
            pod_name = pod.get("name")
            pod_namespace = pod.get("namespace", "default")
            containers = pod.get("containers", [])

            if not pod_name:
                continue

            # Target specific container or all containers in pod
            container_names = [c["name"] for c in containers if c.get("name")]
            if not container_names:
                container_names = [None]  # type: ignore

            for container_name in container_names:
                log_entry = self._fetch_pod_container_log(
                    pod_name=pod_name,
                    namespace=pod_namespace,
                    container_name=container_name,
                    tail_lines=tail_lines,
                    max_error_highlights=max_error_highlights
                )
                collected_logs.append(log_entry)

        return {
            "collected_count": len(collected_logs),
            "pod_logs": collected_logs
        }

    def _fetch_pod_container_log(
        self,
        pod_name: str,
        namespace: str,
        container_name: Optional[str],
        tail_lines: int,
        max_error_highlights: int
    ) -> Dict[str, Any]:
        """Fetches logs for a single pod/container combination."""
        args = ["logs", pod_name, f"--tail={tail_lines}"]
        if container_name:
            args.extend(["-c", container_name])

        exec_res = self.executor.execute(args, namespace=namespace)
        stdout = exec_res.stdout.strip()
        stderr = exec_res.stderr.strip()

        # If current container log is empty or failed, try --previous
        if not exec_res.success or not stdout:
            prev_args = list(args) + ["--previous"]
            prev_res = self.executor.execute(prev_args, namespace=namespace)
            if prev_res.success and prev_res.stdout.strip():
                stdout = f"[PREVIOUS CONTAINER LOGS]\n{prev_res.stdout.strip()}"

        log_content = stdout or stderr or "No log output recorded."
        highlights = self._extract_error_highlights(log_content, max_error_highlights)

        return {
            "pod_name": pod_name,
            "namespace": namespace,
            "container": container_name or "default",
            "tail_lines": tail_lines,
            "error_highlights": highlights,
            "logs_preview": log_content[:2000]  # Cap length for concise output
        }

    def _extract_error_highlights(self, log_content: str, max_highlights: int) -> List[str]:
        """Extracts lines containing failure patterns."""
        lines = log_content.splitlines()
        highlights: List[str] = []

        for line in lines:
            line_clean = line.strip()
            if not line_clean:
                continue
            if any(pattern.search(line_clean) for pattern in ERROR_PATTERNS):
                highlights.append(line_clean)
                if len(highlights) >= max_highlights:
                    break

        return highlights
