# Pattern 20: Evaluation and Monitoring

> **"Tracking agent performance, logging metrics, and evaluating outcomes for continuous improvement"**

## 📖 Overview

Evaluation and Monitoring involves systematically tracking agent performance, collecting metrics, logging events, and analyzing outcomes to ensure reliable operation and continuous improvement. This pattern is essential for production systems where you need visibility into agent behavior, performance bottlenecks, and failure modes.

## 🎯 How Codex Implements Evaluation and Monitoring

Codex implements comprehensive monitoring through multiple layers: OpenTelemetry for metrics, rollout logging for session replay, and real-time performance tracking in the TUI.

### Key Implementation: OpenTelemetry Integration

**File**: [`codex-rs/otel/src/lib.rs`](https://github.com/openai/codex/blob/main/codex-rs/otel/src/lib.rs)

```rust
use opentelemetry::{
    metrics::{Counter, Histogram, Meter},
    trace::{Span, Tracer},
    KeyValue,
};

pub struct CodexTelemetry {
    tracer: Box<dyn Tracer + Send + Sync>,
    meter: Meter,
    
    // Metrics
    pub tool_calls_total: Counter<u64>,
    pub tool_call_duration: Histogram<f64>,
    pub tokens_used_total: Counter<u64>,
    pub errors_total: Counter<u64>,
}

impl CodexTelemetry {
    pub fn record_tool_call(&self, tool_name: &str, duration: f64, success: bool) {
        // Record metrics
        self.tool_calls_total.add(1, &[
            KeyValue::new("tool", tool_name.to_string()),
            KeyValue::new("success", success.to_string()),
        ]);
        
        self.tool_call_duration.record(duration, &[
            KeyValue::new("tool", tool_name.to_string()),
        ]);
        
        if !success {
            self.errors_total.add(1, &[
                KeyValue::new("error_type", "tool_execution"),
                KeyValue::new("tool", tool_name.to_string()),
            ]);
        }
    }
    
    pub fn record_token_usage(&self, prompt_tokens: u64, completion_tokens: u64) {
        self.tokens_used_total.add(prompt_tokens, &[
            KeyValue::new("token_type", "prompt"),
        ]);
        
        self.tokens_used_total.add(completion_tokens, &[
            KeyValue::new("token_type", "completion"),
        ]);
    }
}
```

### Session Recording and Replay

**File**: [`codex-rs/core/src/rollout/recorder.rs`](https://github.com/openai/codex/blob/main/codex-rs/core/src/rollout/recorder.rs)

```rust
pub struct RolloutRecorder {
    session_id: String,
    file: Option<File>,
    sequence_number: AtomicU64,
}

impl RolloutRecorder {
    pub async fn record_turn_start(&mut self, turn_context: &TurnContext) -> Result<()> {
        let item = RolloutItem::TurnStart {
            turn_id: turn_context.turn_id,
            timestamp: Utc::now(),
            user_message: turn_context.user_message.clone(),
        };
        
        self.write_item(&item).await?;
        
        // Also emit telemetry
        telemetry().record_turn_start(turn_context.turn_id);
        Ok(())
    }
    
    pub async fn record_tool_execution(
        &mut self,
        tool_name: &str,
        args: &Value,
        result: &ToolResult,
        duration: Duration,
    ) -> Result<()> {
        let item = RolloutItem::ToolExecution {
            tool_name: tool_name.to_string(),
            arguments: args.clone(),
            result: result.clone(),
            duration_ms: duration.as_millis() as u64,
            timestamp: Utc::now(),
        };
        
        self.write_item(&item).await?;
        
        // Record metrics
        telemetry().record_tool_call(
            tool_name,
            duration.as_secs_f64(),
            result.is_success(),
        );
        
        Ok(())
    }
}
```

### Real-Time Performance Monitoring

**File**: [`codex-rs/tui/src/app.rs`](https://github.com/openai/codex/blob/main/codex-rs/tui/src/app.rs)

```rust
pub struct AppState {
    pub session_stats: SessionStats,
    pub rate_limits: RateLimits,
    pub performance_metrics: PerformanceMetrics,
}

#[derive(Debug, Clone)]
pub struct SessionStats {
    pub turns_completed: u32,
    pub tools_executed: u32,
    pub tokens_used: TokenUsage,
    pub session_duration: Duration,
    pub error_count: u32,
}

#[derive(Debug, Clone)]
pub struct PerformanceMetrics {
    pub avg_response_time: Duration,
    pub tool_success_rate: f64,
    pub tokens_per_minute: f64,
    pub memory_usage: u64,
}

impl AppState {
    pub fn update_metrics(&mut self, event: &ResponseEvent) {
        match event {
            ResponseEvent::Completed { token_usage, .. } => {
                self.session_stats.tokens_used.add(token_usage);
                self.update_performance_metrics();
            }
            ResponseEvent::ToolCallResult { success, duration, .. } => {
                self.session_stats.tools_executed += 1;
                if !success {
                    self.session_stats.error_count += 1;
                }
                self.performance_metrics.update_tool_stats(*duration, *success);
            }
            _ => {}
        }
    }
}
```

### Error Tracking and Analysis

**File**: [`codex-rs/core/src/error.rs`](https://github.com/openai/codex/blob/main/codex-rs/core/src/error.rs)

```rust
#[derive(Debug, thiserror::Error)]
pub enum CodexError {
    #[error("Tool execution failed: {tool_name}")]
    ToolExecutionFailed {
        tool_name: String,
        exit_code: Option<i32>,
        stderr: String,
    },
    
    #[error("Context window exceeded: {tokens_used}/{max_tokens}")]
    ContextWindowExceeded {
        tokens_used: u32,
        max_tokens: u32,
    },
    
    #[error("Rate limit exceeded: {retry_after:?}")]
    RateLimitExceeded {
        retry_after: Option<Duration>,
    },
}

impl CodexError {
    pub fn record_error_metrics(&self) {
        let error_type = match self {
            Self::ToolExecutionFailed { .. } => "tool_execution",
            Self::ContextWindowExceeded { .. } => "context_window",
            Self::RateLimitExceeded { .. } => "rate_limit",
        };
        
        telemetry().errors_total.add(1, &[
            KeyValue::new("error_type", error_type),
        ]);
        
        // Also log for analysis
        tracing::error!(
            error_type = error_type,
            error = %self,
            "Codex error occurred"
        );
    }
}
```

## 🔑 Key Monitoring Patterns in Codex

### 1. **Multi-Layer Metrics Collection**
```rust
// Application metrics
telemetry.record_tool_call("shell", 1.2, true);
telemetry.record_token_usage(150, 80);

// System metrics
telemetry.record_memory_usage(process_memory());
telemetry.record_cpu_usage(cpu_percent());

// Business metrics
telemetry.record_task_completion(task_id, success, duration);
```

### 2. **Event-Driven Monitoring**
```rust
// Events trigger automatic metric collection
match event {
    ResponseEvent::ToolCallBegin { tool_name, .. } => {
        span.record("tool.name", tool_name);
        timer.start();
    }
    ResponseEvent::ToolCallEnd { success, .. } => {
        let duration = timer.elapsed();
        record_tool_metrics(tool_name, duration, success);
    }
}
```

### 3. **Session Replay for Debugging**
```rust
// Every session is recorded for replay
let replayer = RolloutReplayer::new(session_path)?;
let session = replayer.replay_session().await?;

// Analyze session for issues
for turn in session.turns {
    if turn.had_errors() {
        analyze_error_patterns(&turn);
    }
}
```

### 4. **Real-Time Performance Dashboard**
```rust
// TUI displays live metrics
fn render_metrics(frame: &mut Frame, metrics: &PerformanceMetrics) {
    let metrics_text = vec![
        Line::from(format!("Response Time: {:.2}s", metrics.avg_response_time.as_secs_f64())),
        Line::from(format!("Success Rate: {:.1}%", metrics.tool_success_rate * 100.0)),
        Line::from(format!("Tokens/min: {:.0}", metrics.tokens_per_minute)),
        Line::from(format!("Memory: {:.1}MB", metrics.memory_usage as f64 / 1024.0 / 1024.0)),
    ];
    
    let paragraph = Paragraph::new(metrics_text)
        .block(Block::default().title("Performance").borders(Borders::ALL));
    
    frame.render_widget(paragraph, area);
}
```

## 🎯 Key Takeaways

### ✅ **Production Insights**

1. **Multi-Dimensional Metrics**: Codex tracks performance (latency, throughput), business (task success), and system (memory, CPU) metrics.

2. **Event-Driven Collection**: Metrics are collected automatically as events occur, reducing overhead and ensuring completeness.

3. **Session Replay**: Complete session recording enables post-mortem analysis and debugging of complex issues.

4. **Real-Time Visibility**: The TUI provides immediate feedback on system performance and health.

### 🏗️ **Architecture Benefits**

- **Observability**: Full visibility into agent behavior and performance
- **Debugging**: Session replay enables root cause analysis
- **Optimization**: Metrics identify performance bottlenecks
- **Reliability**: Error tracking helps improve system robustness

## 📊 Metrics Categories

### **Performance Metrics**
- Response latency (P50, P95, P99)
- Tool execution duration
- Token processing rate
- Memory and CPU usage

### **Business Metrics**
- Task completion rate
- Tool success rate
- User satisfaction scores
- Session duration

### **Error Metrics**
- Error rate by type
- Failed tool executions
- Context window overflows
- Rate limit hits

### **System Metrics**
- Resource utilization
- Network latency
- Disk I/O
- Thread pool usage

## 🔗 Related Patterns

- **Pattern 18: Rollout System** - Provides data for evaluation
- **Pattern 12: Exception Handling** - Error metrics and tracking
- **Pattern 1: Prompt Chaining** - Turn-level performance metrics
- **Pattern 5: Tool Use** - Tool execution metrics

## 📚 Further Reading

- [OpenTelemetry Documentation](https://opentelemetry.io/)
- [Codex Telemetry Implementation](https://github.com/openai/codex/tree/main/codex-rs/otel)
- [Observability Best Practices](https://sre.google/sre-book/monitoring-distributed-systems/)

---

**Next**: [Complete Agent Example →](../complete-agent-example/README.md)
