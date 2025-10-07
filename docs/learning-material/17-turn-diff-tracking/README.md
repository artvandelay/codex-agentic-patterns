# Pattern 23: Turn Diff Tracking (Git-Style Unified Diffs)

> **"Track file changes across an agent's turn and compute git-compatible unified diffs"**

## 📖 Pattern Overview

Turn Diff Tracking is the **most complex pattern** in Codex - a sophisticated system for tracking file modifications across an agent's turn and computing git-style unified diffs. This isn't simple file watching; it's production-grade git integration.

## 🎯 Key Concepts

1. **Baseline Snapshots** - Capture file state on FIRST touch
2. **UUID Tracking** - Stable internal IDs survive renames
3. **Incremental Diffs** - Show cumulative changes across turn
4. **Git Integration** - Real blob OIDs, proper diff format
5. **Rename Detection** - Track files across move operations
6. **Performance Optimization** - Cache git roots, efficient computation

## 🔍 How Codex Implements This

### Location in Codebase
- **Primary**: `codex-rs/core/src/turn_diff_tracker.rs` (897 lines!)
- **The most complex single file in Codex**

### The Challenge

During an agent's turn, files might be:
1. Added (new file)
2. Modified (change content)
3. Renamed/moved (change path)
4. Deleted (remove file)
5. **Multiple operations on same file**

Users want to see **what changed overall** in git-style unified diff format.

### Implementation Strategy

```rust
// From codex-rs/core/src/turn_diff_tracker.rs:33-128
pub struct TurnDiffTracker {
    /// Map external path -> internal filename (uuid).
    external_to_temp_name: HashMap<PathBuf, String>,
    /// Internal filename -> baseline file info.
    baseline_file_info: HashMap<String, BaselineFileInfo>,
    /// Internal filename -> current external path (tracks renames).
    temp_name_to_current_path: HashMap<String, PathBuf>,
    /// Cache of known git worktree roots.
    git_root_cache: Vec<PathBuf>,
}

impl TurnDiffTracker {
    /// Front-run apply patch calls to track starting contents.
    pub fn on_patch_begin(&mut self, changes: &HashMap<PathBuf, FileChange>) {
        for (path, change) in changes.iter() {
            // Create stable UUID for this file
            if !self.external_to_temp_name.contains_key(path) {
                let internal = Uuid::new_v4().to_string();
                
                // Snapshot baseline if file exists, else use /dev/null
                if path.exists() {
                    let content = blob_bytes(path, mode).unwrap_or_default();
                    let oid = self.git_blob_oid_for_path(path);
                    // Store baseline...
                }
            }
            
            // Handle renames
            if let FileChange::Update { move_path: Some(dest), .. } = change {
                // Update internal mappings for rename
                self.temp_name_to_current_path.insert(uuid, dest.clone());
            }
        }
    }
}
```

### Key Insights

1. **Baseline on First Touch**: Capture file state before ANY modification
2. **UUID Stability**: Files keep same internal ID across renames
3. **Git-Compatible**: Compute real git blob SHA-1 hashes
4. **Incremental**: Show cumulative diff from baseline to final state

## 💡 Real-World Example from Codex

```
Turn begins:
  hello.txt: "hello world"

Operations:
1. add("new.txt") → baseline: /dev/null
2. update("hello.txt") → baseline: "hello world" 
3. rename("hello.txt" → "greeting.txt")
4. update("greeting.txt") → modify content

Final diff:
```diff
diff --git a/new.txt b/new.txt
new file mode 100644
index 0000000..abc1234
--- /dev/null
+++ b/new.txt
@@ -0,0 +1 @@
+new content

diff --git a/hello.txt b/greeting.txt
index def5678..abc9012
--- a/hello.txt
+++ b/greeting.txt
@@ -1 +1,2 @@
 hello world
+welcome!
```

## 📊 Architecture Diagram

```
File Operations During Turn
    ↓
┌─────────────────────────────┐
│     on_patch_begin()        │
│                             │
│  For each file path:        │
│  1. Generate UUID           │
│  2. Snapshot baseline       │
│  3. Track in mappings       │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│    Internal Tracking        │
│                             │
│ external_path → uuid        │
│ uuid → baseline_info        │
│ uuid → current_path         │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│    get_unified_diff()       │
│                             │
│ For each tracked file:      │
│ 1. Compare baseline vs now  │
│ 2. Generate git-style diff  │
│ 3. Handle renames/modes     │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│      Unified Diff           │
│                             │
│ diff --git a/old b/new      │
│ index abc123..def456        │
│ --- a/old                   │
│ +++ b/new                   │
│ @@ -1,1 +1,2 @@             │
│  existing line              │
│ +new line                   │
└─────────────────────────────┘
```

## 🐍 Python Implementation

See the example file:
- **`pattern_advanced.py`**: Complete 400-line implementation

Key classes:
- `TurnDiffTracker`: Main tracker with UUID mappings
- `BaselineFileInfo`: Snapshot of file at first touch
- `FileMode`: Unix permissions (executable, symlink)

Key methods:
- `on_patch_begin()`: Snapshot files before modification
- `get_unified_diff()`: Compute aggregated diff
- `_compute_git_blob_oid()`: Git-compatible SHA-1

## 🔑 Key Takeaways

1. ✅ **Baseline Snapshots**: Critical to capture state before first touch
2. ✅ **UUID Tracking**: Enables rename detection and stable IDs
3. ✅ **Git Integration**: Real blob OIDs, proper diff format
4. ✅ **Performance**: Cache git roots, efficient diff computation
5. ✅ **Edge Cases**: Binary files, symlinks, permissions, deletions
6. ⚠️ **Extreme Complexity**: 897 lines in Rust, most complex pattern

## 🚀 When to Use

- ✅ Production agent systems that modify files
- ✅ Code generation/editing agents
- ✅ Systems that need change tracking
- ✅ Integration with git workflows
- ❌ Simple file operations
- ❌ Read-only agents
- ❌ Systems without git integration

## ⚠️ Common Pitfalls

### 1. Missing Baseline Snapshots
```python
❌ BAD: Track changes without baseline
✅ GOOD: Snapshot on first touch, then track changes
```

### 2. Ignoring Renames
```python
❌ BAD: Treat rename as delete + add
✅ GOOD: Use stable UUIDs to track across renames
```

### 3. Non-Git-Compatible Diffs
```python
❌ BAD: Custom diff format
✅ GOOD: Use git blob SHA-1 and unified diff format
```

## 📚 Further Reading

- **Codex Source**: `codex-rs/core/src/turn_diff_tracker.rs` (897 lines)
- **Git Internals**: How git computes blob SHA-1 hashes
- **Unified Diff Format**: Standard diff format specification
- **Similar Crate**: Rust library for text diffing
- **SHA-1 Algorithm**: Cryptographic hash function

## 🔗 Related Patterns

- **Pattern 5: Tool Use** - File modification tools
- **Pattern 8: Memory Management** - State tracking
- **Pattern 24: Rollout System** - Change logging
- **Git Integration** - Version control workflows

---

**Next**: [Pattern 18: Rollout System →](../18-rollout-system/README.mdREADME.md)
