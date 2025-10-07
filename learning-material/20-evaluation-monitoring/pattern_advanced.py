"""
Pattern 20: Evaluation and Monitoring
======================================

A production-inspired implementation of agent evaluation and monitoring,
based on Codex's OpenTelemetry and rollout logging architecture.

Key Concepts Demonstrated:
- Multi-dimensional metrics collection (performance, business, system)
- Event-driven monitoring
- Session recording and replay
- Real-time performance tracking
- Error tracking and analysis

Based on: codex-rs/otel/src/lib.rs and codex-rs/core/src/rollout/recorder.rs
"""

import asyncio
import json
import time
import psutil
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from collections import defaultdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics to collect."""
    COUNTER = "counter"
    HISTOGRAM = "histogram"
    GAUGE = "gauge"


class EventType(Enum):
    """Types of events to record."""
    TURN_START = "turn_start"
    TURN_END = "turn_end"
    TOOL_CALL_BEGIN = "tool_call_begin"
    TOOL_CALL_END = "tool_call_end"
    ERROR = "error"
    TOKEN_USAGE = "token_usage"
    RATE_LIMIT = "rate_limit"


@dataclass
class Metric:
    """Represents a single metric data point."""
    name: str
    value: float
    metric_type: MetricType
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class Event:
    """Represents a single event in the session."""
    event_type: EventType
    timestamp: str
    data: Dict[str, Any]
    turn_id: Optional[int] = None


@dataclass
class TokenUsage:
    """Token usage statistics."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    def add(self, other: "TokenUsage"):
        """Add another TokenUsage to this one."""
        self.prompt_tokens += other.prompt_tokens
        self.completion_tokens += other.completion_tokens
        self.total_tokens += other.total_tokens


@dataclass
class PerformanceMetrics:
    """Real-time performance metrics."""
    avg_response_time: float = 0.0
    tool_success_rate: float = 1.0
    tokens_per_minute: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    
    # Internal tracking
    _response_times: List[float] = field(default_factory=list, repr=False)
    _tool_successes: int = field(default=0, repr=False)
    _tool_failures: int = field(default=0, repr=False)

    def update_response_time(self, duration: float):
        """Update average response time."""
        self._response_times.append(duration)
        # Keep only last 100 samples
        if len(self._response_times) > 100:
            self._response_times.pop(0)
        self.avg_response_time = sum(self._response_times) / len(self._response_times)

    def update_tool_stats(self, success: bool):
        """Update tool success rate."""
        if success:
            self._tool_successes += 1
        else:
            self._tool_failures += 1
        
        total = self._tool_successes + self._tool_failures
        if total > 0:
            self.tool_success_rate = self._tool_successes / total

    def update_system_metrics(self):
        """Update system resource metrics."""
        process = psutil.Process()
        self.memory_usage_mb = process.memory_info().rss / 1024 / 1024
        self.cpu_usage_percent = process.cpu_percent(interval=0.1)


class MetricsCollector:
    """
    Collects and aggregates metrics.
    Inspired by: codex-rs/otel/src/lib.rs
    """

    def __init__(self):
        self.metrics: List[Metric] = []
        self.counters: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.gauges: Dict[str, float] = {}

    def record_counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None):
        """Record a counter metric (monotonically increasing)."""
        labels = labels or {}
        key = f"{name}:{json.dumps(labels, sort_keys=True)}"
        self.counters[key] += value
        
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.COUNTER,
            labels=labels,
        )
        self.metrics.append(metric)
        logger.debug(f"Counter {name}: {value} {labels}")

    def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a histogram metric (for distributions)."""
        labels = labels or {}
        key = f"{name}:{json.dumps(labels, sort_keys=True)}"
        self.histograms[key].append(value)
        
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.HISTOGRAM,
            labels=labels,
        )
        self.metrics.append(metric)
        logger.debug(f"Histogram {name}: {value} {labels}")

    def record_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a gauge metric (current value)."""
        labels = labels or {}
        key = f"{name}:{json.dumps(labels, sort_keys=True)}"
        self.gauges[key] = value
        
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.GAUGE,
            labels=labels,
        )
        self.metrics.append(metric)
        logger.debug(f"Gauge {name}: {value} {labels}")

    def get_counter_total(self, name: str, labels: Optional[Dict[str, str]] = None) -> float:
        """Get total value of a counter."""
        labels = labels or {}
        key = f"{name}:{json.dumps(labels, sort_keys=True)}"
        return self.counters.get(key, 0.0)

    def get_histogram_stats(self, name: str, labels: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """Get statistics for a histogram."""
        labels = labels or {}
        key = f"{name}:{json.dumps(labels, sort_keys=True)}"
        values = self.histograms.get(key, [])
        
        if not values:
            return {"count": 0, "min": 0, "max": 0, "avg": 0, "p50": 0, "p95": 0, "p99": 0}
        
        sorted_values = sorted(values)
        count = len(sorted_values)
        
        return {
            "count": count,
            "min": sorted_values[0],
            "max": sorted_values[-1],
            "avg": sum(sorted_values) / count,
            "p50": sorted_values[int(count * 0.50)],
            "p95": sorted_values[int(count * 0.95)] if count > 1 else sorted_values[-1],
            "p99": sorted_values[int(count * 0.99)] if count > 1 else sorted_values[-1],
        }

    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []
        
        # Export counters
        for key, value in self.counters.items():
            name, labels_json = key.split(":", 1)
            labels = json.loads(labels_json)
            labels_str = ",".join([f'{k}="{v}"' for k, v in labels.items()])
            lines.append(f"{name}{{{labels_str}}} {value}")
        
        # Export gauges
        for key, value in self.gauges.items():
            name, labels_json = key.split(":", 1)
            labels = json.loads(labels_json)
            labels_str = ",".join([f'{k}="{v}"' for k, v in labels.items()])
            lines.append(f"{name}{{{labels_str}}} {value}")
        
        return "\n".join(lines)


class SessionRecorder:
    """
    Records session events for replay and analysis.
    Inspired by: codex-rs/core/src/rollout/recorder.rs
    """

    def __init__(self, session_id: str, output_dir: Path):
        self.session_id = session_id
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.file_path = output_dir / f"{session_id}.jsonl"
        self.events: List[Event] = []
        self.file_handle = None

    def open(self):
        """Open the recording file."""
        self.file_handle = open(self.file_path, "a")
        logger.info(f"Recording session {self.session_id} to {self.file_path}")

    def close(self):
        """Close the recording file."""
        if self.file_handle:
            self.file_handle.close()
            logger.info(f"Closed recording for session {self.session_id}")

    def record_event(self, event: Event):
        """Record a single event."""
        self.events.append(event)
        
        if self.file_handle:
            event_dict = {
                "event_type": event.event_type.value,
                "timestamp": event.timestamp,
                "data": event.data,
                "turn_id": event.turn_id,
            }
            self.file_handle.write(json.dumps(event_dict) + "\n")
            self.file_handle.flush()

    def record_turn_start(self, turn_id: int, user_message: str):
        """Record the start of a turn."""
        event = Event(
            event_type=EventType.TURN_START,
            timestamp=datetime.now(timezone.utc).isoformat(),
            data={"user_message": user_message},
            turn_id=turn_id,
        )
        self.record_event(event)

    def record_turn_end(self, turn_id: int, success: bool, duration: float):
        """Record the end of a turn."""
        event = Event(
            event_type=EventType.TURN_END,
            timestamp=datetime.now(timezone.utc).isoformat(),
            data={"success": success, "duration_seconds": duration},
            turn_id=turn_id,
        )
        self.record_event(event)

    def record_tool_call(
        self, turn_id: int, tool_name: str, args: Dict[str, Any], 
        result: Any, duration: float, success: bool
    ):
        """Record a tool call execution."""
        event = Event(
            event_type=EventType.TOOL_CALL_END,
            timestamp=datetime.now(timezone.utc).isoformat(),
            data={
                "tool_name": tool_name,
                "arguments": args,
                "result": str(result)[:500],  # Truncate large results
                "duration_seconds": duration,
                "success": success,
            },
            turn_id=turn_id,
        )
        self.record_event(event)

    def record_error(self, turn_id: int, error_type: str, error_message: str):
        """Record an error."""
        event = Event(
            event_type=EventType.ERROR,
            timestamp=datetime.now(timezone.utc).isoformat(),
            data={"error_type": error_type, "error_message": error_message},
            turn_id=turn_id,
        )
        self.record_event(event)

    def record_token_usage(self, turn_id: int, token_usage: TokenUsage):
        """Record token usage."""
        event = Event(
            event_type=EventType.TOKEN_USAGE,
            timestamp=datetime.now(timezone.utc).isoformat(),
            data=asdict(token_usage),
            turn_id=turn_id,
        )
        self.record_event(event)

    @staticmethod
    def replay_session(file_path: Path) -> List[Event]:
        """Replay a recorded session."""
        events = []
        with open(file_path, "r") as f:
            for line in f:
                event_dict = json.loads(line)
                event = Event(
                    event_type=EventType(event_dict["event_type"]),
                    timestamp=event_dict["timestamp"],
                    data=event_dict["data"],
                    turn_id=event_dict.get("turn_id"),
                )
                events.append(event)
        return events


class AgentMonitor:
    """
    Comprehensive monitoring system for agents.
    Combines metrics collection, event recording, and real-time performance tracking.
    """

    def __init__(self, session_id: str, output_dir: Path = Path("./sessions")):
        self.session_id = session_id
        self.metrics = MetricsCollector()
        self.recorder = SessionRecorder(session_id, output_dir)
        self.performance = PerformanceMetrics()
        self.token_usage = TokenUsage()
        self.start_time = time.time()
        self.current_turn_id = 0

    def start(self):
        """Start monitoring."""
        self.recorder.open()
        logger.info(f"Started monitoring session {self.session_id}")

    def stop(self):
        """Stop monitoring."""
        self.recorder.close()
        duration = time.time() - self.start_time
        logger.info(f"Session {self.session_id} completed in {duration:.2f}s")
        self._print_summary()

    def start_turn(self, user_message: str) -> int:
        """Start a new turn."""
        self.current_turn_id += 1
        self.recorder.record_turn_start(self.current_turn_id, user_message)
        self.metrics.record_counter("turns_total")
        return self.current_turn_id

    def end_turn(self, turn_id: int, success: bool, duration: float):
        """End a turn."""
        self.recorder.record_turn_end(turn_id, success, duration)
        self.performance.update_response_time(duration)
        
        if success:
            self.metrics.record_counter("turns_success")
        else:
            self.metrics.record_counter("turns_failed")
        
        self.metrics.record_histogram("turn_duration_seconds", duration)

    def record_tool_execution(
        self, tool_name: str, args: Dict[str, Any], 
        result: Any, duration: float, success: bool
    ):
        """Record a tool execution."""
        # Record event
        self.recorder.record_tool_call(
            self.current_turn_id, tool_name, args, result, duration, success
        )
        
        # Record metrics
        self.metrics.record_counter(
            "tool_calls_total",
            labels={"tool": tool_name, "success": str(success)}
        )
        self.metrics.record_histogram(
            "tool_duration_seconds",
            duration,
            labels={"tool": tool_name}
        )
        
        # Update performance metrics
        self.performance.update_tool_stats(success)
        
        if not success:
            self.metrics.record_counter("tool_errors_total", labels={"tool": tool_name})

    def record_token_usage(self, prompt_tokens: int, completion_tokens: int):
        """Record token usage."""
        usage = TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        )
        
        self.token_usage.add(usage)
        self.recorder.record_token_usage(self.current_turn_id, usage)
        
        self.metrics.record_counter("tokens_total", value=prompt_tokens, labels={"type": "prompt"})
        self.metrics.record_counter("tokens_total", value=completion_tokens, labels={"type": "completion"})
        
        # Update tokens per minute
        elapsed_minutes = (time.time() - self.start_time) / 60
        if elapsed_minutes > 0:
            self.performance.tokens_per_minute = self.token_usage.total_tokens / elapsed_minutes

    def record_error(self, error_type: str, error_message: str):
        """Record an error."""
        self.recorder.record_error(self.current_turn_id, error_type, error_message)
        self.metrics.record_counter("errors_total", labels={"error_type": error_type})
        logger.error(f"Error in turn {self.current_turn_id}: {error_type} - {error_message}")

    def update_system_metrics(self):
        """Update system resource metrics."""
        self.performance.update_system_metrics()
        self.metrics.record_gauge("memory_usage_mb", self.performance.memory_usage_mb)
        self.metrics.record_gauge("cpu_usage_percent", self.performance.cpu_usage_percent)

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get current performance summary."""
        return {
            "session_id": self.session_id,
            "session_duration": time.time() - self.start_time,
            "turns_completed": self.current_turn_id,
            "performance": asdict(self.performance),
            "token_usage": asdict(self.token_usage),
            "tool_stats": self.metrics.get_histogram_stats("tool_duration_seconds"),
            "turn_stats": self.metrics.get_histogram_stats("turn_duration_seconds"),
        }

    def _print_summary(self):
        """Print monitoring summary."""
        summary = self.get_performance_summary()
        print("\n" + "=" * 60)
        print(f"📊 Session {self.session_id} Summary")
        print("=" * 60)
        print(f"Duration: {summary['session_duration']:.2f}s")
        print(f"Turns: {summary['turns_completed']}")
        print(f"Avg Response Time: {summary['performance']['avg_response_time']:.2f}s")
        print(f"Tool Success Rate: {summary['performance']['tool_success_rate']*100:.1f}%")
        print(f"Tokens Used: {summary['token_usage']['total_tokens']}")
        print(f"Tokens/min: {summary['performance']['tokens_per_minute']:.0f}")
        print(f"Memory: {summary['performance']['memory_usage_mb']:.1f}MB")
        print("=" * 60)


async def demo_evaluation_monitoring():
    """
    Demonstrate evaluation and monitoring patterns.
    """
    print("📊 Evaluation and Monitoring Demo")
    print("=" * 50)

    # Create monitor
    session_id = f"demo-{int(time.time())}"
    monitor = AgentMonitor(session_id)
    monitor.start()

    try:
        # Simulate Turn 1
        print("\n🔄 Turn 1: Processing user request...")
        turn_id = monitor.start_turn("Analyze this document")
        turn_start = time.time()
        
        # Simulate tool calls
        await asyncio.sleep(0.3)
        monitor.record_tool_execution(
            "read_file", {"path": "doc.txt"}, "File content...", 0.3, True
        )
        
        await asyncio.sleep(0.5)
        monitor.record_tool_execution(
            "analyze_text", {"text": "..."}, {"sentiment": "positive"}, 0.5, True
        )
        
        # Record token usage
        monitor.record_token_usage(prompt_tokens=150, completion_tokens=80)
        
        turn_duration = time.time() - turn_start
        monitor.end_turn(turn_id, success=True, duration=turn_duration)
        print(f"✅ Turn 1 completed in {turn_duration:.2f}s")

        # Simulate Turn 2 with error
        print("\n🔄 Turn 2: Processing another request...")
        turn_id = monitor.start_turn("Search the web")
        turn_start = time.time()
        
        await asyncio.sleep(0.2)
        monitor.record_tool_execution(
            "web_search", {"query": "AI agents"}, None, 0.2, False
        )
        monitor.record_error("tool_execution", "Network timeout")
        
        turn_duration = time.time() - turn_start
        monitor.end_turn(turn_id, success=False, duration=turn_duration)
        print(f"❌ Turn 2 failed in {turn_duration:.2f}s")

        # Simulate Turn 3
        print("\n🔄 Turn 3: Retry with different approach...")
        turn_id = monitor.start_turn("Search documentation")
        turn_start = time.time()
        
        await asyncio.sleep(0.4)
        monitor.record_tool_execution(
            "doc_search", {"query": "AI agents"}, {"results": [...]}, 0.4, True
        )
        
        monitor.record_token_usage(prompt_tokens=200, completion_tokens=120)
        
        turn_duration = time.time() - turn_start
        monitor.end_turn(turn_id, success=True, duration=turn_duration)
        print(f"✅ Turn 3 completed in {turn_duration:.2f}s")

        # Update system metrics
        monitor.update_system_metrics()

        # Get performance summary
        print("\n📈 Real-time Performance Metrics:")
        summary = monitor.get_performance_summary()
        print(f"  Avg Response Time: {summary['performance']['avg_response_time']:.2f}s")
        print(f"  Tool Success Rate: {summary['performance']['tool_success_rate']*100:.1f}%")
        print(f"  Total Tokens: {summary['token_usage']['total_tokens']}")
        print(f"  Memory Usage: {summary['performance']['memory_usage_mb']:.1f}MB")

        # Export metrics
        print("\n📊 Prometheus Metrics Sample:")
        prometheus_output = monitor.metrics.export_prometheus()
        for line in prometheus_output.split("\n")[:5]:  # Show first 5 lines
            print(f"  {line}")

        print("\n✅ Monitoring demo completed successfully!")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        monitor.record_error("demo_error", str(e))
        raise
    finally:
        monitor.stop()

    # Demonstrate session replay
    print("\n🔄 Replaying session...")
    events = SessionRecorder.replay_session(monitor.recorder.file_path)
    print(f"  Replayed {len(events)} events")
    
    # Analyze errors
    error_events = [e for e in events if e.event_type == EventType.ERROR]
    print(f"  Found {len(error_events)} errors during session")
    for error in error_events:
        print(f"    - {error.data['error_type']}: {error.data['error_message']}")


async def main():
    """Run the evaluation and monitoring demo."""
    try:
        await demo_evaluation_monitoring()
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"❌ Demo failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())