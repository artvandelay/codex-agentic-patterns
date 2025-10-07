#!/usr/bin/env python3
"""
Advanced Pattern 2: Turn Diff Tracking (Git-Style Unified Diffs)

This is the MOST COMPLEX pattern in Codex - and the most impressive!

The Problem:
During an agent's turn, it might modify multiple files. Users want to see:
- WHAT changed (unified diff format like git)
- Across ALL file operations in the turn
- Handling renames, moves, binary files, permissions
- Computing git-compatible SHA-1 hashes

The Challenge:
- Files might be touched multiple times (add → modify → rename)
- Need baseline snapshot BEFORE first touch
- Track files across renames using stable internal IDs
- Compute incremental diffs efficiently
- Handle edge cases (binary files, symlinks, deletions)

Codex's Solution:
1. Snapshot files on FIRST touch (baseline)
2. Use UUIDs for stable internal file tracking
3. Track current path separately (for renames)
4. Compute git-style unified diffs on demand
5. Cache git roots for performance

Extracted from: codex-rs/core/src/turn_diff_tracker.rs (897 lines!)

This is production-grade git integration in an AI agent.
"""

import hashlib
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Set, Tuple
from uuid import uuid4
from difflib import unified_diff


# ============================================================================
# Types
# ============================================================================

@dataclass
class FileMode:
    """Unix file permissions."""
    is_executable: bool
    is_symlink: bool
    
    def as_git_mode(self) -> str:
        """Return git-style file mode."""
        if self.is_symlink:
            return "120000"
        elif self.is_executable:
            return "100755"
        else:
            return "100644"
    
    def __str__(self) -> str:
        return self.as_git_mode()


@dataclass
class BaselineFileInfo:
    """Snapshot of file at first touch."""
    path: Path
    content: bytes
    mode: FileMode
    oid: str  # Git blob SHA-1


class FileChange:
    """Types of file changes."""
    pass


@dataclass
class FileAdd(FileChange):
    """File addition."""
    content: str


@dataclass
class FileUpdate(FileChange):
    """File update (possibly with rename)."""
    unified_diff: str
    move_path: Optional[Path] = None


@dataclass
class FileDelete(FileChange):
    """File deletion."""
    content: str


# ============================================================================
# Turn Diff Tracker (The Beast!)
# ============================================================================

class TurnDiffTracker:
    """
    Track file changes across an agent's turn and compute unified diffs.
    
    From: codex-rs/core/src/turn_diff_tracker.rs (lines 1-897)
    
    This is THE most complex pattern in Codex. Here's why:
    
    1. **State Management**: Track files across multiple operations
    2. **Baseline Snapshots**: Capture files on FIRST touch
    3. **UUID Tracking**: Stable IDs survive renames
    4. **Git Integration**: Compute real git blob OIDs
    5. **Performance**: Cache git roots, efficient diffs
    6. **Edge Cases**: Binary files, symlinks, permissions
    
    Example Flow:
    ```
    add("a.txt") → baseline: /dev/null, current: "hello"
    update("a.txt") → baseline: "hello", current: "hello world"
    rename("a.txt" → "b.txt") → baseline: "hello", current path: b.txt
    
    Final diff:
      diff --git a/a.txt b/b.txt
      new file mode 100644
      index 0000...abc123
      --- /dev/null
      +++ b/b.txt
      @@ -0,0 +1 @@
      +hello world
    ```
    """
    
    def __init__(self):
        # Map external path → internal UUID
        self.external_to_internal: Dict[Path, str] = {}
        
        # Map internal UUID → baseline snapshot
        self.baseline_snapshots: Dict[str, BaselineFileInfo] = {}
        
        # Map internal UUID → current external path (tracks renames)
        self.internal_to_current_path: Dict[str, Path] = {}
        
        # Cache of known git repository roots
        self.git_root_cache: Set[Path] = set()
    
    def on_patch_begin(self, changes: Dict[Path, FileChange]):
        """
        Called BEFORE applying a patch to snapshot baselines.
        
        This is the key insight: capture file state BEFORE first modification.
        """
        for path, change in changes.items():
            # Ensure stable internal UUID exists
            if path not in self.external_to_internal:
                internal_id = str(uuid4())
                self.external_to_internal[path] = internal_id
                self.internal_to_current_path[internal_id] = path
                
                # Snapshot baseline if file exists
                if path.exists():
                    mode = self._get_file_mode(path)
                    content = self._read_file_bytes(path, mode)
                    oid = self._compute_git_blob_oid(content)
                    
                    self.baseline_snapshots[internal_id] = BaselineFileInfo(
                        path=path,
                        content=content,
                        mode=mode,
                        oid=oid,
                    )
                else:
                    # File doesn't exist → baseline is /dev/null
                    self.baseline_snapshots[internal_id] = BaselineFileInfo(
                        path=path,
                        content=b"",
                        mode=FileMode(is_executable=False, is_symlink=False),
                        oid="0" * 40,  # ZERO_OID
                    )
            
            # Handle renames
            if isinstance(change, FileUpdate) and change.move_path:
                internal_id = self.external_to_internal[path]
                dest = change.move_path
                
                # Update current path mapping
                self.internal_to_current_path[internal_id] = dest
                
                # Update forward mapping
                del self.external_to_internal[path]
                self.external_to_internal[dest] = internal_id
    
    def get_unified_diff(self) -> Optional[str]:
        """
        Compute aggregated unified diff for all tracked files.
        
        Returns git-style unified diff showing all changes in this turn.
        """
        if not self.baseline_snapshots:
            return None
        
        aggregated = []
        
        # Sort by path for stable output (like git)
        internal_ids = sorted(
            self.baseline_snapshots.keys(),
            key=lambda iid: str(self._get_current_path(iid))
        )
        
        for internal_id in internal_ids:
            file_diff = self._compute_file_diff(internal_id)
            if file_diff:
                aggregated.append(file_diff)
        
        if not aggregated:
            return None
        
        return "\n".join(aggregated)
    
    def _compute_file_diff(self, internal_id: str) -> Optional[str]:
        """Compute unified diff for a single file."""
        baseline = self.baseline_snapshots.get(internal_id)
        if not baseline:
            return None
        
        current_path = self._get_current_path(internal_id)
        if not current_path:
            return None
        
        # Get current state
        if current_path.exists():
            current_mode = self._get_file_mode(current_path)
            current_content = self._read_file_bytes(current_path, current_mode)
            current_oid = self._compute_git_blob_oid(current_content)
        else:
            # File was deleted
            current_mode = FileMode(is_executable=False, is_symlink=False)
            current_content = b""
            current_oid = "0" * 40
        
        # Fast path: no change
        if baseline.content == current_content and baseline.path == current_path:
            return None
        
        # Build git-style diff
        lines = []
        
        # Header
        baseline_display = self._relative_to_git_root(baseline.path)
        current_display = self._relative_to_git_root(current_path)
        lines.append(f"diff --git a/{baseline_display} b/{current_display}")
        
        # File mode changes
        is_add = baseline.oid == "0" * 40 and current_oid != "0" * 40
        is_delete = baseline.oid != "0" * 40 and current_oid == "0" * 40
        
        if is_add:
            lines.append(f"new file mode {current_mode}")
        elif is_delete:
            lines.append(f"deleted file mode {baseline.mode}")
        elif baseline.mode.as_git_mode() != current_mode.as_git_mode():
            lines.append(f"old mode {baseline.mode}")
            lines.append(f"new mode {current_mode}")
        
        # Index line
        lines.append(f"index {baseline.oid[:7]}..{current_oid[:7]}")
        
        # Try text diff
        try:
            baseline_text = baseline.content.decode('utf-8')
            current_text = current_content.decode('utf-8')
            
            # Generate unified diff
            baseline_lines = baseline_text.splitlines(keepends=True)
            current_lines = current_text.splitlines(keepends=True)
            
            from_file = "/dev/null" if is_add else f"a/{baseline_display}"
            to_file = "/dev/null" if is_delete else f"b/{current_display}"
            
            diff_lines = list(unified_diff(
                baseline_lines,
                current_lines,
                fromfile=from_file,
                tofile=to_file,
                n=3,  # Context lines
            ))
            
            # Skip first two lines (they're just file headers we already have)
            lines.extend(line.rstrip() for line in diff_lines[2:])
        
        except UnicodeDecodeError:
            # Binary file
            lines.append(f"--- {'/dev/null' if is_add else f'a/{baseline_display}'}")
            lines.append(f"+++ {'/dev/null' if is_delete else f'b/{current_display}'}")
            lines.append("Binary files differ")
        
        return "\n".join(lines)
    
    def _get_current_path(self, internal_id: str) -> Optional[Path]:
        """Get current external path for internal ID."""
        return self.internal_to_current_path.get(internal_id)
    
    def _get_file_mode(self, path: Path) -> FileMode:
        """Determine file mode (executable, symlink, etc.)."""
        if path.is_symlink():
            return FileMode(is_executable=False, is_symlink=True)
        
        # Check if executable (Unix only)
        try:
            stat_info = path.stat()
            is_executable = bool(stat_info.st_mode & 0o111)
            return FileMode(is_executable=is_executable, is_symlink=False)
        except:
            return FileMode(is_executable=False, is_symlink=False)
    
    def _read_file_bytes(self, path: Path, mode: FileMode) -> bytes:
        """Read file content as bytes."""
        if mode.is_symlink:
            # For symlinks, content is the link target
            target = os.readlink(path)
            return str(target).encode('utf-8')
        else:
            return path.read_bytes()
    
    def _compute_git_blob_oid(self, content: bytes) -> str:
        """
        Compute git blob SHA-1.
        
        Git's blob hash is: sha1("blob <size>\0<content>")
        """
        header = f"blob {len(content)}\0".encode('utf-8')
        return hashlib.sha1(header + content).hexdigest()
    
    def _relative_to_git_root(self, path: Path) -> str:
        """Get path relative to git root if in a repo."""
        git_root = self._find_git_root(path)
        if git_root:
            try:
                rel = path.relative_to(git_root)
                return str(rel).replace('\\', '/')
            except ValueError:
                pass
        return str(path).replace('\\', '/')
    
    def _find_git_root(self, path: Path) -> Optional[Path]:
        """Find git repository root for a path."""
        # Check cache first
        for cached_root in self.git_root_cache:
            try:
                if path.is_relative_to(cached_root):
                    return cached_root
            except:
                pass
        
        # Walk up to find .git
        current = path if path.is_dir() else path.parent
        while current:
            git_dir = current / ".git"
            if git_dir.exists():
                self.git_root_cache.add(current)
                return current
            
            # Move to parent
            parent = current.parent
            if parent == current:  # Reached root
                break
            current = parent
        
        return None


# ============================================================================
# Demo
# ============================================================================

def demo():
    """Demonstrate turn diff tracking."""
    import tempfile
    import shutil
    
    print("=" * 80)
    print("TURN DIFF TRACKER DEMO")
    print("=" * 80)
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Initialize tracker
        tracker = TurnDiffTracker()
        
        # Scenario 1: Add a new file
        print("\n📝 Scenario 1: Add new file")
        print("-" * 80)
        
        file_a = tmpdir / "hello.txt"
        
        # Signal we're about to modify (baseline /dev/null)
        tracker.on_patch_begin({file_a: FileAdd(content="hello world\n")})
        
        # Actually create the file
        file_a.write_text("hello world\n")
        
        # Get diff
        diff = tracker.get_unified_diff()
        print(diff)
        
        # Scenario 2: Update existing file
        print("\n\n📝 Scenario 2: Update existing file")
        print("-" * 80)
        
        # Signal we're about to modify again
        tracker.on_patch_begin({file_a: FileUpdate(unified_diff="")})
        
        # Modify the file
        file_a.write_text("hello world\nwelcome!\n")
        
        # Get updated diff (should show entire change from baseline)
        diff = tracker.get_unified_diff()
        print(diff)
        
        # Scenario 3: Rename file
        print("\n\n📝 Scenario 3: Rename file")
        print("-" * 80)
        
        file_b = tmpdir / "greeting.txt"
        
        # Signal rename
        tracker.on_patch_begin({
            file_a: FileUpdate(
                unified_diff="",
                move_path=file_b
            )
        })
        
        # Actually rename
        file_a.rename(file_b)
        file_b.write_text("hello world\nwelcome!\nhow are you?\n")
        
        # Get diff (should show rename + change)
        diff = tracker.get_unified_diff()
        print(diff)
        
        # Scenario 4: Delete file
        print("\n\n📝 Scenario 4: Delete file")
        print("-" * 80)
        
        # Create another file first
        file_c = tmpdir / "temp.txt"
        file_c.write_text("temporary\n")
        
        # Snapshot it
        tracker.on_patch_begin({file_c: FileUpdate(unified_diff="")})
        
        # Now delete
        tracker.on_patch_begin({file_c: FileDelete(content="temporary\n")})
        file_c.unlink()
        
        # Get diff
        diff = tracker.get_unified_diff()
        print(diff)


def main():
    """Run demo."""
    demo()
    
    print("\n\n💡 Key Takeaways:")
    print("=" * 80)
    print("1. ✅ Baseline snapshots: Capture files on FIRST touch")
    print("2. ✅ UUID tracking: Stable IDs survive renames")
    print("3. ✅ Git-compatible: Real blob OIDs, unified diff format")
    print("4. ✅ Incremental: Show cumulative changes across turn")
    print("5. ✅ Performance: Cache git roots, efficient diffs")
    print("\nThis is PRODUCTION-GRADE git integration in an AI agent!")
    print("\n⚡ Complexity: ~900 lines in Rust, simplified to ~400 in Python")


if __name__ == "__main__":
    main()
