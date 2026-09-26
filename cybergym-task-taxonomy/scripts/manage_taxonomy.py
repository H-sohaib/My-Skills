#!/usr/bin/env python3
"""CyberGym Task Failure Taxonomy & Master Inventory Manager.

Maintains the single source of truth document:
/home/sohaib-harraoui/Desktop/workspace/Research/CyberGym/audits/cybergym_task_failure_taxonomy_and_subcategories.md
"""

from __future__ import annotations

import argparse
import datetime
import pathlib
import re
import sys
from typing import NamedTuple

DEFAULT_DOC_PATH = pathlib.Path(
    "/home/sohaib-harraoui/Desktop/workspace/Research/CyberGym/audits/cybergym_task_failure_taxonomy_and_subcategories.md"
)

CATEGORIES = {
    1: "1. In-Tree Seed Files & Complex PoC Construction",
    2: "2. Verification Discipline, Mock Harnesses & Bounds",
    3: "3. Stateful Sequences & Multi-Step Handshakes",
    4: "4. Custom Memory Allocator Reconnaissance & Grooming",
    5: "5. Multi-Engine Target Routing & Sandbox Gates",
    6: "6. Solved Tasks (Differential Crash Verified)",
}

SUBCATEGORIES = {
    "1.1": "1.1: Missing Sub-Feature Qualification & Section Injection",
    "1.2": "1.2: In-Band Multi-Field Delimiter Framing",
    "1.3": "1.3: Crude Scalar Inflation vs. Bound Mutation",
    "1.4": "1.4: Strict CRC / Checksum & Container Magic Integrity",
    "2.1": "2.1: Synthetic Mock Harness & In-Tree Source Tampering",
    "2.2": "2.2: Fuzzer Launcher & Runner Output Discrimination",
    "2.3": "2.3: Companion Library Linkage Discovery",
    "2.4": "2.4: Harness-Scoped Invariant Refutation Boundary",
    "3.1": "3.1: Multi-Call Sequence Differential State",
    "3.2": "3.2: Protocol Handshake & ATR State Transitions",
    "4.1": "4.1: Internal Chunk/Slab/Arena ASan Blindspots",
    "5.1": "5.1: Subsystem Routing & Read-Only / Pixel Budget Gates",
    "6.0": "Solved Tasks",
}


class TaskRecord(NamedTuple):
    task_id: str
    software: str
    fuzzer: str
    category_id: int
    category_name: str
    subcategory_key: str
    subcategory_name: str
    status: str
    details: str


def parse_doc(content: str) -> tuple[list[TaskRecord], list[str]]:
    """Parse tasks table and history from document content."""
    tasks: list[TaskRecord] = []
    history: list[str] = []

    lines = content.splitlines()
    in_table = False
    in_history = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## 3. Master Task Inventory"):
            in_table = True
            continue
        if stripped.startswith("## 4. History & Movement Log"):
            in_table = False
            in_history = True
            continue

        if in_table and stripped.startswith("|") and not stripped.startswith("| Task ID") and not stripped.startswith("| :---"):
            cols = [c.strip() for c in stripped.split("|")[1:-1]]
            if len(cols) >= 7:
                task_id = re.sub(r"[\*`]", "", cols[0])
                software = re.sub(r"[\*`]", "", cols[1])
                fuzzer = re.sub(r"[\*`]", "", cols[2])
                cat_col = cols[3]
                sub_col = cols[4]
                status = cols[5]
                details = cols[6]

                cat_num_match = re.search(r"(\d+)", cat_col)
                cat_id = int(cat_num_match.group(1)) if cat_num_match else 1
                cat_name = CATEGORIES.get(cat_id, cat_col)

                sub_key_match = re.search(r"(\d+\.\d+)", sub_col)
                if sub_key_match:
                    sub_key = sub_key_match.group(1)
                elif "Solved" in sub_col or cat_id == 6:
                    sub_key = "6.0"
                else:
                    sub_key = "1.1"

                tasks.append(
                    TaskRecord(
                        task_id=task_id,
                        software=software,
                        fuzzer=fuzzer,
                        category_id=cat_id,
                        category_name=cat_name,
                        subcategory_key=sub_key,
                        subcategory_name=sub_col,
                        status=status,
                        details=details,
                    )
                )

        if in_history and stripped.startswith("* **"):
            history.append(stripped)

    return tasks, history


def render_ascii_diagram(tasks: list[TaskRecord]) -> str:
    """Render the ASCII tree topology diagram with accurate grouping."""
    by_sub: dict[str, list[TaskRecord]] = {}
    for t in tasks:
        by_sub.setdefault(t.subcategory_key, []).append(t)

    cat1_tasks = [t for t in tasks if t.category_id == 1]
    cat2_tasks = [t for t in tasks if t.category_id == 2]
    cat3_tasks = [t for t in tasks if t.category_id == 3]
    cat4_tasks = [t for t in tasks if t.category_id == 4]
    cat5_tasks = [t for t in tasks if t.category_id == 5]
    cat6_tasks = [t for t in tasks if t.category_id == 6]

    diagram = [
        "```text",
        "┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐",
        "│                                       CYBERGYM BENCHMARK TASK TAXONOMY TOPOLOGY                                        │",
        "└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘",
        "",
        f"  [Active Benchmark Pool: {len(tasks)} Tasks]",
        "     │",
        f"     ├──► Category 1: Complex PoC Construction & Seed Mutation (os-38405) [{len(cat1_tasks)} Tasks]",
        "     │       │",
    ]

    def render_sub(sub_key: str, sub_title: str, is_last_sub: bool, parent_last: bool):
        sub_list = by_sub.get(sub_key, [])
        pipe = " " if parent_last else "│"
        branch = "└───►" if is_last_sub else "├───►"
        diagram.append(f"     {pipe}       {branch} {sub_title} ({len(sub_list)} Task{'s' if len(sub_list) != 1 else ''})")
        sub_pipe = " " if is_last_sub else "│"
        for i, t in enumerate(sub_list):
            is_last_item = i == len(sub_list) - 1
            item_branch = "└──" if is_last_item else "├──"
            suffix = " [CRASHED BOTH]" if "CRASHED" in t.status else ""
            diagram.append(f"     {pipe}       {sub_pipe}        {item_branch} {t.task_id} ({t.software}){suffix}")
        if not is_last_sub:
            diagram.append(f"     {pipe}       │")

    # Cat 1 subcategories
    render_sub("1.1", "1.1: Missing Sub-Feature Qualification & Section Injection", False, False)
    render_sub("1.2", "1.2: In-Band Multi-Field Delimiter Framing", False, False)
    render_sub("1.3", "1.3: Crude Scalar Inflation vs. Bound Mutation", False, False)
    render_sub("1.4", "1.4: Strict CRC / Checksum & Container Magic Integrity", True, False)

    diagram.append("     │")
    diagram.append(f"     ├──► Category 2: Verification Discipline, Mock Harnesses & Refutations (os-38406) [{len(cat2_tasks)} Tasks]")
    diagram.append("     │       │")
    render_sub("2.1", "2.1: Synthetic Mock Harness & In-Tree Source Tampering", False, False)
    render_sub("2.2", "2.2: Fuzzer Launcher & Runner Output Discrimination", False, False)
    render_sub("2.3", "2.3: Companion Library Linkage Discovery", False, False)
    render_sub("2.4", "2.4: Harness-Scoped Invariant Refutation Boundary", True, False)

    diagram.append("     │")
    diagram.append(f"     ├──► Category 3: Stateful Sequences & Multi-Step Handshakes (os-38408) [{len(cat3_tasks)} Tasks]")
    diagram.append("     │       │")
    render_sub("3.1", "3.1: Multi-Call Sequence Differential State", False, False)
    render_sub("3.2", "3.2: Protocol Handshake & ATR State Transitions", True, False)

    diagram.append("     │")
    diagram.append(f"     ├──► Category 4: Custom Memory Allocators & Heap Grooming (os-38410) [{len(cat4_tasks)} Tasks]")
    diagram.append("     │       │")
    render_sub("4.1", "4.1: Internal Chunk/Slab/Arena ASan Blindspots", True, False)

    diagram.append("     │")
    diagram.append(f"     ├──► Category 5: Multi-Engine Target Routing & Sandbox Gates (os-38407) [{len(cat5_tasks)} Tasks]")
    diagram.append("     │       │")
    render_sub("5.1", "5.1: Subsystem Routing & Read-Only / Pixel Budget Gates", True, False)

    diagram.append("     │")
    diagram.append(f"     └──► Category 6: Solved Tasks [{len(cat6_tasks)} Tasks]")
    for i, t in enumerate(cat6_tasks):
        is_last_item = i == len(cat6_tasks) - 1
        item_branch = "└──" if is_last_item else "├──"
        diagram.append(f"             {item_branch} {t.task_id} ({t.software}) [SOLVED]")

    diagram.append("```")
    return "\n".join(diagram)


def render_stats_table(tasks: list[TaskRecord]) -> str:
    """Render the global workload stats table."""
    total = len(tasks)
    cat_counts: dict[int, int] = {i: 0 for i in range(1, 7)}
    for t in tasks:
        cat_counts[t.category_id] = cat_counts.get(t.category_id, 0) + 1

    solved_count = cat_counts[6]

    def line(name: str, count: int, status: str) -> str:
        pct = (count / total * 100.0) if total else 0.0
        return f"│ {name:<54} │ {count:>2} tasks    │ {pct:>5.1f}%          │ {status:<14} │"

    rows = [
        "```text",
        "┌────────────────────────────────────────────────────────┬─────────────┬────────────────┬────────────────┐",
        "│ Category                                               │ Task Count  │ Share (%)      │ Status         │",
        "├────────────────────────────────────────────────────────┼─────────────┼────────────────┼────────────────┤",
        line("1. In-Tree Seed Files & Complex PoC Construction", cat_counts[1], "Active"),
        line("2. Verification Discipline, Mock Harnesses & Bounds", cat_counts[2], "Active"),
        line("3. Stateful Sequences & Multi-Step Handshakes", cat_counts[3], "Active"),
        line("4. Custom Memory Allocator Reconnaissance & Grooming", cat_counts[4], "Active"),
        line("5. Multi-Engine Target Routing & Sandbox Gates", cat_counts[5], "Active (Both)"),
        line("6. Solved Tasks (Differential Crash Verified)", cat_counts[6], "Solved"),
        "├────────────────────────────────────────────────────────┼─────────────┼────────────────┼────────────────┤",
        f"│ {'Total Distinct Tasks Under Tracking':<54} │ {total:>2} tasks    │ 100.0%         │ {solved_count} / {total} Solved  │",
        "└────────────────────────────────────────────────────────┴─────────────┴────────────────┴────────────────┘",
        "```",
    ]
    return "\n".join(rows)


def render_master_table(tasks: list[TaskRecord]) -> str:
    """Render the master markdown table sorted by task_id."""
    sorted_tasks = sorted(tasks, key=lambda x: x.task_id)
    lines = [
        "| Task ID | Software | Target Fuzzer | Current Category | Subcategory | Status | Key Blocker / Forensic Details |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for t in sorted_tasks:
        lines.append(
            f"| **`{t.task_id}`** | `{t.software}` | `{t.fuzzer}` | {t.category_name.split(':')[0]} | {t.subcategory_name} | {t.status} | {t.details} |"
        )
    return "\n".join(lines)


def render_full_doc(tasks: list[TaskRecord], history: list[str]) -> str:
    """Assemble the complete markdown document."""
    sections = [
        "# CyberGym Benchmark: Task Failure Taxonomy & Master Inventory\n",
        "> **Single Source of Truth** for tracking, classifying, and updating the state of all 19 CyberGym benchmark tasks under active evaluation.\n",
        "---\n",
        "## 1. Global Workload Statistics\n",
        render_stats_table(tasks),
        "\n---\n",
        "## 2. Taxonomy & Task Topology\n",
        render_ascii_diagram(tasks),
        "\n---\n",
        "## 3. Master Task Inventory\n",
        render_master_table(tasks),
        "\n---\n",
        "## 4. History & Movement Log\n",
    ]
    for entry in history:
        sections.append(f"{entry}\n")
    return "\n".join(sections)


def cmd_list(args: argparse.Namespace) -> None:
    doc_path = pathlib.Path(args.file)
    content = doc_path.read_text(encoding="utf-8")
    tasks, _ = parse_doc(content)

    print(f"Loaded {len(tasks)} tasks from {doc_path}:\n")
    for t in sorted(tasks, key=lambda x: (x.category_id, x.subcategory_key, x.task_id)):
        print(f"[{t.category_id}] {t.subcategory_key:<4} | {t.task_id:<20} | {t.software:<12} | {t.status:<14} | {t.details}")


def cmd_stats(args: argparse.Namespace) -> None:
    doc_path = pathlib.Path(args.file)
    content = doc_path.read_text(encoding="utf-8")
    tasks, _ = parse_doc(content)
    print(render_stats_table(tasks))


def cmd_validate(args: argparse.Namespace) -> None:
    doc_path = pathlib.Path(args.file)
    content = doc_path.read_text(encoding="utf-8")
    tasks, history = parse_doc(content)

    print(f"Validation Report for {doc_path}:")
    print(f"- Total tasks parsed: {len(tasks)}")
    print(f"- History entries: {len(history)}")

    task_ids = [t.task_id for t in tasks]
    if len(task_ids) != len(set(task_ids)):
        print("ERROR: Duplicate task IDs detected!")
        sys.exit(1)

    for t in tasks:
        if t.category_id not in CATEGORIES:
            print(f"ERROR: Invalid category {t.category_id} on {t.task_id}")
            sys.exit(1)

    print("SUCCESS: Master inventory integrity verified cleanly!")


def cmd_move(args: argparse.Namespace) -> None:
    doc_path = pathlib.Path(args.file)
    content = doc_path.read_text(encoding="utf-8")
    tasks, history = parse_doc(content)

    target_task = None
    for t in tasks:
        if t.task_id == args.task:
            target_task = t
            break

    if not target_task:
        print(f"ERROR: Task '{args.task}' not found in inventory!")
        sys.exit(1)

    to_cat = int(args.to_cat)
    if to_cat not in CATEGORIES:
        print(f"ERROR: Invalid target category '{to_cat}'! Allowed: 1-6.")
        sys.exit(1)

    to_sub = args.sub or ("6.0" if to_cat == 6 else target_task.subcategory_key)
    sub_name = args.sub_name or SUBCATEGORIES.get(to_sub, to_sub)
    new_status = args.status or ("**SOLVED**" if to_cat == 6 else target_task.status)
    new_details = args.details or target_task.details

    date_str = args.date or datetime.date.today().isoformat()
    old_cat_label = f"Category {target_task.category_id} ({target_task.subcategory_key})"
    new_cat_label = f"Category {to_cat} ({to_sub})"

    history_entry = (
        f"* **{date_str}**: `{target_task.task_id}` (`{target_task.software}`): "
        f"Moved from {old_cat_label} to {new_cat_label} — {args.reason}"
    )

    new_task = TaskRecord(
        task_id=target_task.task_id,
        software=target_task.software,
        fuzzer=target_task.fuzzer,
        category_id=to_cat,
        category_name=CATEGORIES[to_cat],
        subcategory_key=to_sub,
        subcategory_name=sub_name,
        status=new_status,
        details=new_details,
    )

    updated_tasks = [new_task if t.task_id == args.task else t for t in tasks]
    updated_history = [history_entry] + history

    new_doc_content = render_full_doc(updated_tasks, updated_history)

    if args.dry_run:
        print("=== DRY RUN (No changes written) ===")
        print(history_entry)
        print("\nNew Global Statistics:\n")
        print(render_stats_table(updated_tasks))
    else:
        doc_path.write_text(new_doc_content, encoding="utf-8")
        print(f"SUCCESS: Moved {target_task.task_id} to Category {to_cat} ({to_sub})")
        print(f"Appended history entry: {history_entry}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage CyberGym Task Failure Taxonomy")
    parser.add_argument("--file", default=str(DEFAULT_DOC_PATH), help="Path to markdown taxonomy file")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    subparsers.add_parser("list", help="List all tasks and current categories")

    # stats
    subparsers.add_parser("stats", help="Display workload summary statistics")

    # validate
    subparsers.add_parser("validate", help="Validate table formatting and task counts")

    # move
    move_p = subparsers.add_parser("move", help="Move a task to a different category")
    move_p.add_argument("--task", required=True, help="Task ID (e.g. arvo:59457)")
    move_p.add_argument("--to-cat", required=True, type=int, help="Target category (1-6)")
    move_p.add_argument("--sub", help="Subcategory key (e.g. 1.1, 2.4, 6.0)")
    move_p.add_argument("--sub-name", help="Custom subcategory display name")
    move_p.add_argument("--status", help="New status string (e.g. **SOLVED**, Unsolved)")
    move_p.add_argument("--details", help="Updated technical blocker / notes")
    move_p.add_argument("--reason", required=True, help="Mandatory rationale for why task was moved")
    move_p.add_argument("--date", help="Date in YYYY-MM-DD format (defaults to today)")
    move_p.add_argument("--dry-run", action="store_true", help="Preview changes without writing")

    args = parser.parse_args()
    if args.command == "list":
        cmd_list(args)
    elif args.command == "stats":
        cmd_stats(args)
    elif args.command == "validate":
        cmd_validate(args)
    elif args.command == "move":
        cmd_move(args)


if __name__ == "__main__":
    main()
