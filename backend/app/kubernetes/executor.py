import json
import subprocess
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from loguru import logger


@dataclass
class ExecResult:
    """Dataclass holding command execution results."""
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    command: List[str]


class KubectlExecutor:
    """Safely executes kubectl commands using subprocess with fast request timeout."""

    def __init__(self, context: Optional[str] = None):
        self.context = context

    def get_available_contexts(self) -> List[str]:
        """Returns list of all cluster contexts configured in local kubeconfig."""
        res = self.execute(["config", "get-contexts", "-o", "name"], timeout=5)
        if res.success and res.stdout.strip():
            return [ctx.strip() for ctx in res.stdout.strip().split("\n") if ctx.strip()]
        return []

    def get_current_context(self) -> Optional[str]:
        """Returns the currently active cluster context in local kubeconfig."""
        res = self.execute(["config", "current-context"], timeout=5)
        if res.success and res.stdout.strip():
            return res.stdout.strip()
        return None

    def _build_command(
        self,
        args: List[str],
        namespace: Optional[str] = None
    ) -> List[str]:
        """Builds full kubectl command with context, request-timeout, and namespace flags."""
        cmd = ["kubectl"]
        if self.context:
            cmd.extend(["--context", self.context])
        cmd.extend(["--request-timeout", "8s"])
        if namespace:
            cmd.extend(["-n", namespace])
        cmd.extend(args)
        return cmd

    def execute(
        self,
        args: List[str],
        namespace: Optional[str] = None,
        timeout: int = 12
    ) -> ExecResult:
        """Executes a kubectl command safely and returns structured result."""
        cmd = self._build_command(args, namespace=namespace)
        cmd_str = " ".join(cmd)
        logger.debug(f"Executing kubectl command: {cmd_str}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            success = (result.returncode == 0)
            if not success:
                logger.warning(
                    f"kubectl command failed with exit code {result.returncode}: {cmd_str}\n"
                    f"stderr: {result.stderr.strip()}"
                )
            return ExecResult(
                success=success,
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode,
                command=cmd
            )
        except FileNotFoundError:
            logger.error("kubectl CLI binary was not found on PATH.")
            return ExecResult(
                success=False,
                stdout="",
                stderr="kubectl executable not found. Ensure kubectl is installed and in PATH.",
                exit_code=127,
                command=cmd
            )
        except subprocess.TimeoutExpired:
            logger.error(f"kubectl command timed out after {timeout} seconds: {cmd_str}")
            return ExecResult(
                success=False,
                stdout="",
                stderr=f"Command execution timed out after {timeout} seconds.",
                exit_code=124,
                command=cmd
            )
        except Exception as exc:
            logger.error(f"Unexpected error executing kubectl command '{cmd_str}': {exc}")
            return ExecResult(
                success=False,
                stdout="",
                stderr=str(exc),
                exit_code=1,
                command=cmd
            )

    def execute_json(
        self,
        args: List[str],
        namespace: Optional[str] = None,
        timeout: int = 12
    ) -> tuple[Optional[Dict[str, Any]], ExecResult]:
        """Executes a kubectl command expecting JSON output, parsing the result."""
        json_args = list(args)
        if "-o" not in json_args and "--output" not in json_args:
            json_args.extend(["-o", "json"])

        exec_res = self.execute(json_args, namespace=namespace, timeout=timeout)
        if not exec_res.success or not exec_res.stdout.strip():
            return None, exec_res

        try:
            parsed_data = json.loads(exec_res.stdout)
            return parsed_data, exec_res
        except json.JSONDecodeError as err:
            logger.error(f"Failed to parse kubectl JSON output: {err}")
            return None, exec_res
