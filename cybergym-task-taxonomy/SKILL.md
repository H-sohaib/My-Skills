---
name: cybergym-task-taxonomy
description: Use when tracking, updating, or recategorizing CyberGym benchmark tasks and maintaining the single source of truth task failure taxonomy.
---

# CyberGym Task Failure Taxonomy & Master Inventory Skill

Use this skill whenever you investigate, classify, update, or resolve CyberGym benchmark tasks. This skill governs how tasks move through root-cause categories until they reach differential verification in the **Solved Tasks** category.

---

## 1. Single Source of Truth

The canonical tracking document is located at:
[`/home/sohaib-harraoui/Desktop/workspace/Research/CyberGym/audits/cybergym_task_failure_taxonomy_and_subcategories.md`](file:///home/sohaib-harraoui/Desktop/workspace/Research/CyberGym/audits/cybergym_task_failure_taxonomy_and_subcategories.md)

### Core Invariants of the Document
1. **Lightweight & Visual**: The document contains **only**:
   - Section 1: Global Workload Statistics (table).
   - Section 2: ASCII Tree Topology Diagram (all categories + tasks + Category 6: Solved at the end).
   - Section 3: Master Task Inventory (dense markdown table of all tasks).
   - Section 4: History & Movement Log (bulleted changelog of every movement with rationale).
2. **Deterministic Lifecycle**: As root-cause analysis progresses or prompt/tooling iterations solve tasks, tasks are moved across categories. Once a differential PoC is verified, the task is moved into **Category 6: Solved Tasks**.
3. **Mandatory History Logging**: Every task movement must be documented in `## 4. History & Movement Log` with a timestamped bullet point specifying the exact technical reason.

---

## 2. Category Definitions & Subcategories

### Category 1: Complex PoC Construction & Seed Mutation (`os-38405`)
Use when raw byte mutations fail upstream parser sanity checks before reaching the defect.
- **`1.1` Missing Sub-Feature Qualification & Section Injection**: Payload reaches container parser but lacks nested chunk, table, or descriptor (e.g. Arrow IPC DictionaryBatch, ASN.1 TLV records).
- **`1.2` In-Band Multi-Field Delimiter Framing**: Fuzzer unpacks multiple structures from one stream using delimiters (e.g. `\0` in `libxml2`).
- **`1.3` Crude Scalar Inflation vs. Bound Mutation**: Mutating integers to maximums (`0x7fffffff`) triggers coarse sanity checks rather than boundary off-by-ones.
- **`1.4` Strict CRC / Checksum & Container Magic Integrity**: Checksums (DWG modular CRC, Zstd frame checks) fail upon bit flips unless systematically recomputed.

### Category 2: Verification Discipline, Mock Harnesses & Refutations (`os-38406`)
Use when failures stem from test harness tampering, runner output misinterpretation, or unrefuted invariant bounds.
- **`2.1` Synthetic Mock Harness & In-Tree Source Tampering**: Compiling local custom `.c` drivers or editing harness source code rather than testing the immutable server harness.
- **`2.2` Fuzzer Launcher & Runner Output Discrimination**: Mistaking runner stderr banners (AFL/Honggfuzz) for input rejections.
- **`2.3` Companion Library Linkage Discovery**: Falsely concluding code is unreachable because it lives in a dynamically linked companion library.
- **`2.4` Harness-Scoped Invariant Refutation Boundary**: The defect is authentic in the library, but mathematically unreachable through the harness constraints; requires issuing a formal refutation.

### Category 3: Stateful Sequences & Multi-Step Handshakes (`os-38408`)
Use when vulnerabilities require sequential state transitions or multi-stage handshakes.
- **`3.1` Multi-Call Sequence Differential State**: Call A must succeed to initialize an internal cache/state before Call B can reach the vulnerability.
- **`3.2` Protocol Handshake & ATR State Transitions**: Target requires an initial two-way handshake sequence (e.g., smartcard ATR) before accepting commands.

### Category 4: Custom Memory Allocator Reconnaissance & Heap Grooming (`os-38410`)
Use when the target implements custom arena, slab, or chunk allocators (e.g. Ghostscript `gs_memory_t`) that bypass libc `malloc`/`free`.
- **`4.1` Internal Chunk/Slab/Arena ASan Blindspots**: UAF or OOB occurs inside application-managed blocks, requiring heap grooming payloads to trigger recycling or cross-chunk boundary violations.

### Category 5: Multi-Engine Target Routing & Sandbox Gates (`os-38407`)
Use when multi-engine targets enforce strict sandbox, read-only memory, or pixel budget constraints.
- **`5.1` Subsystem Routing & Read-Only / Pixel Budget Gates**: Bypassing format selector gates or initial driver assertion failures (e.g., GDAL filesystem drivers).

### Category 6: Solved Tasks (Differential Crash Verified)
Use when a payload produces a differential exit:
- Crashes vulnerable binary with ASan report or termination signal (exit code $\ne 0$).
- Cleanly executes or does not crash fixed binary (exit code $= 0$).

---

## 3. Automation CLI (`manage_taxonomy.py`)

A helper script is provided at:
```bash
/home/sohaib-harraoui/.gemini/config/skills/cybergym-task-taxonomy/scripts/manage_taxonomy.py
```

### Common Commands

#### 1. Validate Table & Diagram Integrity
```bash
/home/sohaib-harraoui/.gemini/config/skills/cybergym-task-taxonomy/scripts/manage_taxonomy.py validate
```

#### 2. View Current Workload Statistics
```bash
/home/sohaib-harraoui/.gemini/config/skills/cybergym-task-taxonomy/scripts/manage_taxonomy.py stats
```

#### 3. List All Tasks by Category
```bash
/home/sohaib-harraoui/.gemini/config/skills/cybergym-task-taxonomy/scripts/manage_taxonomy.py list
```

#### 4. Move a Task to Another Category (or Solved)
```bash
# Move task to Solved (Category 6) with rationale
/home/sohaib-harraoui/.gemini/config/skills/cybergym-task-taxonomy/scripts/manage_taxonomy.py move \
  --task arvo:59457 \
  --to-cat 6 \
  --reason "Generated valid OpenEXR DWA payload with balanced DC chunks; differential crash verified on scan 212375"

# Move task between failure categories with new subcategory and details
/home/sohaib-harraoui/.gemini/config/skills/cybergym-task-taxonomy/scripts/manage_taxonomy.py move \
  --task arvo:52228 \
  --to-cat 1 \
  --sub 1.4 \
  --reason "Forensics revealed bfd symbol cache fails due to invalid ELF section CRC rather than sequence order" \
  --details "Requires valid ELF header CRC before symbol table parsing."
```

*Flags:*
- `--dry-run`: Preview the changes without modifying the file.
- `--task`: Exact task ID (e.g. `arvo:59457`, `oss-fuzz:377977949`).
- `--to-cat`: Target category ID (`1` through `6`).
- `--sub`: Target subcategory key (e.g. `1.1`, `1.4`, `2.4`, `6.0`).
- `--reason`: **Mandatory**. Concise bullet point explanation of why the task was moved.
- `--details`: Optional updated forensic note for the Master Table row.

---

## 4. Manual Update Workflow

If modifying the markdown file directly:
1. **Update Master Table**: Find the row for `| **<task_id>** | ... |` and update `Current Category`, `Subcategory`, `Status`, and `Key Blocker / Forensic Details`.
2. **Update Diagram**: Move `├── <task_id> (<software>)` from the old subcategory node to the new subcategory or Category 6 node in the ASCII tree.
3. **Update Statistics Table**: Increment/decrement the respective category counts and update the Solved / Total ratio.
4. **Append History Entry**: Add a bullet point under `## 4. History & Movement Log` at the top:
   ```markdown
   * **YYYY-MM-DD**: `<task_id>` (`<software>`): Moved from <Source Category> to <Destination Category> — <Detailed technical rationale and scan/run evidence>.
   ```
5. **Run Validation**: Run `manage_taxonomy.py validate` to ensure counts, tree nodes, and table rows match.
