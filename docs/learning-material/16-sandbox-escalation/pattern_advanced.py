#!/usr/bin/env python3
"""
Advanced Pattern 1: Sandbox Escalation with Automatic Retry

This pattern demonstrates a sophisticated multi-stage command execution system
that Codex uses in production. It's NOT just "run command and handle errors" -
it's a complete decision tree with:

1. Safety assessment (auto-approve, ask user, reject)
2. Sandbox selection (none, seatbelt, seccomp)
3. Execution with escalation on failure
4. User approval workflow
5. Session-scoped approval caching
6. Telemetry and decision tracking

Extracted from: codex-rs/core/src/executor/runner.rs (lines 76-218)
                codex-rs/core/src/executor/sandbox.rs (lines 87-160)

This is what separates production systems from demos.
"""

import asyncio
import subprocess
import hashlib
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Set, Dict, Any
from datetime import datetime


# ============================================================================
# Types and Enums
# ============================================================================

class SandboxType(Enum):
    """Different sandbox isolation levels."""
    NONE = "none"  # No isolation
    DOCKER = "docker"  # Container isolation
    RESTRICTED_SHELL = "restricted"  # Limited shell access


class AskForApproval(Enum):
    """When to request user approval."""
    NEVER = "never"  # Auto-deny dangerous commands
    UNLESS_TRUSTED = "unless_trusted"  # Ask if command not in approved list
    ON_FAILURE = "on_failure"  # Run sandboxed, ask if fails
    ALWAYS = "always"  # Always ask user


class ReviewDecision(Enum):
    """User's decision after approval request."""
    APPROVED = "approved"  # Approve this once
    APPROVED_FOR_SESSION = "approved_for_session"  # Approve for this session
    DENIED = "denied"  # Deny this command
    ABORT = "abort"  # Abort entire task


class SafetyCheck(Enum):
    """Safety assessment result."""
    AUTO_APPROVE = "auto_approve"
    ASK_USER = "ask_user"
    REJECT = "reject"


@dataclass
class ExecResult:
    """Result of command execution."""
    exit_code: int
    stdout: str
    stderr: str
    duration: float
    sandbox_used: SandboxType
    timed_out: bool = False


@dataclass
class SandboxDecision:
    """Sandbox placement decision."""
    initial_sandbox: SandboxType
    escalate_on_failure: bool
    record_session_approval: bool


class SandboxError(Exception):
    """Sandbox-specific error."""
    def __init__(self, message: str, output: Optional[ExecResult] = None):
        super().__init__(message)
        self.output = output


# ============================================================================
# Safety Assessment (Pattern Core)
# ============================================================================

DANGEROUS_COMMANDS = {
    "rm", "mv", "dd", "mkfs", "fdisk",
    "sudo", "su", "chmod", "chown",
    "curl", "wget", "nc", "netcat",
}

DANGEROUS_PATTERNS = [
    "-rf",  # Recursive force delete
    ">/dev/",  # Writing to devices
    ":(){ :|:&",  # Fork bomb
]


def assess_command_safety(
    command: list[str],
    approval_policy: AskForApproval,
    approved_cache: Set[str],
) -> tuple[SafetyCheck, Optional[SandboxType]]:
    """
    Assess command safety and determine if approval is needed.
    
    This mirrors Codex's safety assessment logic:
    - Check against dangerous command list
    - Check for dangerous patterns
    - Consider approval policy
    - Check approval cache
    """
    cmd_hash = command_hash(command)
    
    # Already approved for this session?
    if cmd_hash in approved_cache:
        return (SafetyCheck.AUTO_APPROVE, SandboxType.NONE)
    
    # Check if command looks dangerous
    is_dangerous = False
    cmd_str = " ".join(command)
    
    # Check first word (command name)
    if command and command[0] in DANGEROUS_COMMANDS:
        is_dangerous = True
    
    # Check for dangerous patterns
    for pattern in DANGEROUS_PATTERNS:
        if pattern in cmd_str:
            is_dangerous = True
            break
    
    if is_dangerous:
        if approval_policy == AskForApproval.NEVER:
            return (SafetyCheck.REJECT, None)
        else:
            return (SafetyCheck.ASK_USER, SandboxType.NONE)
    
    # Not dangerous - run with appropriate sandbox
    if approval_policy == AskForApproval.ON_FAILURE:
        # Run sandboxed first, escalate if fails
        return (SafetyCheck.AUTO_APPROVE, SandboxType.RESTRICTED_SHELL)
    else:
        # Run without sandbox
        return (SafetyCheck.AUTO_APPROVE, SandboxType.NONE)


def command_hash(command: list[str]) -> str:
    """Hash command for cache key."""
    cmd_str = " ".join(command)
    return hashlib.sha256(cmd_str.encode()).hexdigest()[:16]


# ============================================================================
# Sandbox Selection Logic
# ============================================================================

async def select_sandbox(
    command: list[str],
    approval_policy: AskForApproval,
    approved_cache: Set[str],
    user_approval_callback,
) -> SandboxDecision:
    """
    Determine sandbox placement with approval workflow.
    
    This is the core decision tree from Codex:
    1. Assess safety
    2. If auto-approve → return sandbox decision
    3. If ask user → request approval
    4. If reject → raise error
    
    From: codex-rs/core/src/executor/sandbox.rs:87-160
    """
    safety, sandbox = assess_command_safety(command, approval_policy, approved_cache)
    
    if safety == SafetyCheck.AUTO_APPROVE:
        escalate = (
            approval_policy == AskForApproval.ON_FAILURE
            and sandbox in [SandboxType.DOCKER, SandboxType.RESTRICTED_SHELL]
        )
        return SandboxDecision(
            initial_sandbox=sandbox,
            escalate_on_failure=escalate,
            record_session_approval=False,
        )
    
    elif safety == SafetyCheck.ASK_USER:
        # Request user approval
        decision = await user_approval_callback(command)
        
        if decision == ReviewDecision.APPROVED:
            return SandboxDecision(
                initial_sandbox=SandboxType.NONE,
                escalate_on_failure=False,
                record_session_approval=False,
            )
        elif decision == ReviewDecision.APPROVED_FOR_SESSION:
            return SandboxDecision(
                initial_sandbox=SandboxType.NONE,
                escalate_on_failure=False,
                record_session_approval=True,
            )
        else:
            raise PermissionError(f"Command rejected by user: {' '.join(command)}")
    
    else:  # REJECT
        raise PermissionError(f"Dangerous command blocked: {' '.join(command)}")


# ============================================================================
# Command Execution
# ============================================================================

async def execute_in_sandbox(
    command: list[str],
    sandbox: SandboxType,
    timeout: float = 30.0,
) -> ExecResult:
    """
    Execute command in specified sandbox.
    
    In production Codex uses:
    - macOS: Seatbelt profiles
    - Linux: Landlock/Seccomp
    
    This demo uses simpler sandboxing.
    """
    start = datetime.now()
    
    try:
        if sandbox == SandboxType.NONE:
            # No sandboxing
            proc = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        
        elif sandbox == SandboxType.RESTRICTED_SHELL:
            # Simulate restricted shell (in production this would use Seatbelt/Seccomp)
            # For demo: prepend with 'env -i' to clear environment
            proc = await asyncio.create_subprocess_exec(
                "env", "-i", "PATH=/usr/bin:/bin", *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        
        elif sandbox == SandboxType.DOCKER:
            # Run in Docker container
            docker_cmd = ["docker", "run", "--rm", "--network=none", "alpine"] + command
            proc = await asyncio.create_subprocess_exec(
                *docker_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        
        # Wait with timeout
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=timeout
            )
            timed_out = False
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            timed_out = True
            stdout, stderr = b"", b"Command timed out"
        
        duration = (datetime.now() - start).total_seconds()
        
        result = ExecResult(
            exit_code=proc.returncode or -1,
            stdout=stdout.decode('utf-8', errors='replace'),
            stderr=stderr.decode('utf-8', errors='replace'),
            duration=duration,
            sandbox_used=sandbox,
            timed_out=timed_out,
        )
        
        # Check if sandbox denied the command
        if result.exit_code == 126 or result.exit_code == 127:
            # Command not found or permission denied
            raise SandboxError("Command denied by sandbox", result)
        
        return result
    
    except FileNotFoundError as e:
        duration = (datetime.now() - start).total_seconds()
        raise SandboxError(f"Command not found: {e}", ExecResult(
            exit_code=127,
            stdout="",
            stderr=str(e),
            duration=duration,
            sandbox_used=sandbox,
        ))


# ============================================================================
# Main Execution Pipeline (The Magic!)
# ============================================================================

class CommandExecutor:
    """
    Sophisticated command executor with sandbox escalation.
    
    This is the production pattern from Codex - NOT a toy example!
    
    Execution flow:
    1. Assess command safety
    2. Select appropriate sandbox
    3. Execute in sandbox
    4. If sandbox fails AND escalation enabled:
       a. Notify user of failure
       b. Request approval to retry without sandbox
       c. If approved, retry without sandbox
    5. Cache approvals for session
    """
    
    def __init__(self):
        self.approval_cache: Set[str] = set()
        self.execution_log: list[Dict[str, Any]] = []
    
    async def run(
        self,
        command: list[str],
        approval_policy: AskForApproval = AskForApproval.ON_FAILURE,
        user_approval_callback=None,
    ) -> ExecResult:
        """
        Execute command with full sandbox escalation workflow.
        
        From: codex-rs/core/src/executor/runner.rs:77-157
        """
        if user_approval_callback is None:
            user_approval_callback = self._default_approval_callback
        
        print(f"\n🔧 Executing: {' '.join(command)}")
        
        # Step 1: Decide sandbox placement
        decision = await select_sandbox(
            command,
            approval_policy,
            self.approval_cache,
            user_approval_callback,
        )
        
        if decision.record_session_approval:
            cmd_hash = command_hash(command)
            self.approval_cache.add(cmd_hash)
            print(f"✅ Approved for session (cached)")
        
        print(f"📦 Sandbox: {decision.initial_sandbox.value}")
        print(f"⚡ Escalate on failure: {decision.escalate_on_failure}")
        
        # Step 2: Execute in chosen sandbox
        try:
            result = await execute_in_sandbox(
                command,
                decision.initial_sandbox,
            )
            
            self._log_execution(command, result, "success")
            print(f"✓ Exit code: {result.exit_code} ({result.duration:.2f}s)")
            
            return result
        
        except SandboxError as err:
            # Step 3: Handle sandbox failure with escalation
            if decision.escalate_on_failure:
                print(f"⚠️  Sandbox failure: {err}")
                print(f"🔄 Attempting escalation...")
                
                return await self._retry_without_sandbox(
                    command,
                    err,
                    user_approval_callback,
                )
            else:
                self._log_execution(command, err.output, "sandbox_denied")
                raise
    
    async def _retry_without_sandbox(
        self,
        command: list[str],
        sandbox_error: SandboxError,
        user_approval_callback,
    ) -> ExecResult:
        """
        Fallback: retry command without sandbox after user approval.
        
        From: codex-rs/core/src/executor/runner.rs:159-216
        """
        print(f"\n⚠️  Command failed in sandbox:")
        if sandbox_error.output:
            print(f"   Exit code: {sandbox_error.output.exit_code}")
            if sandbox_error.output.stderr:
                print(f"   Error: {sandbox_error.output.stderr[:200]}")
        
        # Ask user if they want to retry without sandbox
        print(f"\n❓ Retry without sandbox protection?")
        decision = await user_approval_callback(
            command,
            prompt="Command failed; retry without sandbox?"
        )
        
        if decision in [ReviewDecision.APPROVED, ReviewDecision.APPROVED_FOR_SESSION]:
            if decision == ReviewDecision.APPROVED_FOR_SESSION:
                cmd_hash = command_hash(command)
                self.approval_cache.add(cmd_hash)
            
            print(f"🔓 Retrying without sandbox...")
            result = await execute_in_sandbox(command, SandboxType.NONE)
            self._log_execution(command, result, "escalated_success")
            return result
        else:
            raise PermissionError("User denied escalation")
    
    async def _default_approval_callback(
        self,
        command: list[str],
        prompt: Optional[str] = None
    ) -> ReviewDecision:
        """Default interactive approval."""
        print(f"\n🔐 APPROVAL REQUIRED")
        print(f"Command: {' '.join(command)}")
        if prompt:
            print(f"Reason: {prompt}")
        print(f"\nOptions:")
        print(f"  1. Approve once")
        print(f"  2. Approve for session")
        print(f"  3. Deny")
        
        choice = input("Choice (1/2/3): ").strip()
        
        if choice == "1":
            return ReviewDecision.APPROVED
        elif choice == "2":
            return ReviewDecision.APPROVED_FOR_SESSION
        else:
            return ReviewDecision.DENIED
    
    def _log_execution(
        self,
        command: list[str],
        result: Optional[ExecResult],
        status: str,
    ):
        """Log execution for telemetry."""
        self.execution_log.append({
            "timestamp": datetime.now().isoformat(),
            "command": " ".join(command),
            "status": status,
            "exit_code": result.exit_code if result else None,
            "sandbox": result.sandbox_used.value if result else None,
            "duration": result.duration if result else None,
        })


# ============================================================================
# Demo
# ============================================================================

async def demo():
    """Demonstrate sandbox escalation pattern."""
    print("=" * 80)
    print("SANDBOX ESCALATION PATTERN DEMO")
    print("=" * 80)
    
    executor = CommandExecutor()
    
    # Test 1: Safe command (auto-approved)
    print("\n\n📝 Test 1: Safe command")
    print("-" * 80)
    result = await executor.run(
        ["echo", "Hello, World!"],
        approval_policy=AskForApproval.ON_FAILURE,
    )
    print(f"Output: {result.stdout.strip()}")
    
    # Test 2: Command that might fail in sandbox
    print("\n\n📝 Test 2: Network command (may fail in sandbox)")
    print("-" * 80)
    try:
        result = await executor.run(
            ["curl", "--version"],
            approval_policy=AskForApproval.ON_FAILURE,
        )
        print(f"Success! curl version: {result.stdout.split()[0]}")
    except Exception as e:
        print(f"Failed: {e}")
    
    # Test 3: Dangerous command (requires approval)
    print("\n\n📝 Test 3: Dangerous command (requires explicit approval)")
    print("-" * 80)
    
    # Auto-deny for demo
    async def auto_deny(*args, **kwargs):
        return ReviewDecision.DENIED
    
    try:
        result = await executor.run(
            ["rm", "-rf", "/tmp/test"],
            approval_policy=AskForApproval.UNLESS_TRUSTED,
            user_approval_callback=auto_deny,
        )
    except PermissionError as e:
        print(f"✓ Correctly blocked: {e}")
    
    # Show execution log
    print("\n\n📊 Execution Log:")
    print("-" * 80)
    for entry in executor.execution_log:
        print(f"{entry['timestamp']}: {entry['command']}")
        print(f"  Status: {entry['status']}, Exit: {entry['exit_code']}, "
              f"Sandbox: {entry['sandbox']}, Duration: {entry['duration']:.2f}s")


async def main():
    """Run demonstrations."""
    await demo()
    
    print("\n\n💡 Key Takeaways:")
    print("=" * 80)
    print("1. ✅ Multi-stage execution with intelligent fallbacks")
    print("2. ✅ User approval workflows with session caching")
    print("3. ✅ Safety assessment before execution")
    print("4. ✅ Automatic sandbox escalation on failure")
    print("5. ✅ Telemetry and decision tracking")
    print("\nThis is what PRODUCTION agentic systems look like!")


if __name__ == "__main__":
    asyncio.run(main())
