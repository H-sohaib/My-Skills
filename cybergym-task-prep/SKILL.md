---
name: cybergym-task-prep
description: Prepare and download CyberGym tasks from the manifest, extract archives, and configure agent_group.yaml for AutoExploit validation runs.
---

# CyberGym Task Preparation Skill

Use this skill whenever given a CyberGym task ID (e.g., `24633`, `arvo:24633`, `arvo-11173`) to download the task archive from Hugging Face, extract it, and prepare the task workspace along with its `agent_group.yaml`.

## Paths and Context

- **Manifest & Dataset Info**: `/home/sohaib-harraoui/Desktop/workspace/Research/CyberGym/manifest.csv`
- **Task Destination**: `/home/sohaib-harraoui/Desktop/workspace/Research/CyberGym/tasks/arvo-<TASK_ID>`
- **Submission Helper Script**: `/home/sohaib-harraoui/Desktop/workspace/Research/CyberGym/scripts/cybergym_submission.py`
- **Hugging Face Base URL**: `https://huggingface.co/datasets/sunblaze-ucb/cybergym/resolve/main/data/arvo/<TASK_ID>`
- **Default Verifier Endpoint**: `http://35.209.237.7:8666/submit-vul`

---

## Workflow Steps

### 1. Parse and Look Up Task ID
- Normalize the task ID by stripping any `arvo:` or `arvo-` prefix (e.g., `arvo:11173` -> `11173`).
- Retrieve metadata from `manifest.csv`:
  - `project_name`
  - `project_language`
  - `vulnerability_description`
  - `cwe_id` / `cwe_name`

### 2. Download Task Assets
Create directory `$TASK_DIR` at `/home/sohaib-harraoui/Desktop/workspace/Research/CyberGym/tasks/arvo-<TASK_ID>`:
- Download `repo-vul.tar.gz`:
  ```bash
  curl -fL --retry 3 -o "$TASK_DIR/repo-vul.tar.gz" "https://huggingface.co/datasets/sunblaze-ucb/cybergym/resolve/main/data/arvo/<TASK_ID>/repo-vul.tar.gz"
  ```
- Download `description.txt`:
  ```bash
  curl -fL --retry 3 -o "$TASK_DIR/description.txt" "https://huggingface.co/datasets/sunblaze-ucb/cybergym/resolve/main/data/arvo/<TASK_ID>/description.txt"
  ```

### 3. Extract Archive
- Extract `repo-vul.tar.gz` into `$TASK_DIR/repo-vul`:
  ```bash
  mkdir -p "$TASK_DIR/repo-vul"
  tar -xzf "$TASK_DIR/repo-vul.tar.gz" -C "$TASK_DIR/repo-vul"
  ```

### 4. Generate `agent_group.yaml` via Automation Script (Mandatory)
**NEVER construct `agent_group.yaml` or write checksums manually.** Always run the preparation script `prepare_task_agent_group.py` to calculate the exact SHA256 checksum, resolve the masked task ID, identify the target fuzzer, and generate the YAML file:

```bash
python3 /home/sohaib-harraoui/Desktop/workspace/Research/CyberGym/scripts/prepare_task_agent_group.py \
  --task-id "<TASK_ID>" \
  --agent-id "<AGENT_ID>" \
  --version "0.66.1"
```

#### What `prepare_task_agent_group.py` handles automatically:
1. **Masked Task ID**: Resolves `arvo:<TASK_ID>` to its opaque alias (e.g., `1f1c15ecb21a`) from `mask_map.json`.
2. **Target Fuzzer Identification**: Resolves the target fuzzer binary name (e.g., `llvmfuzz`, `simple_compress`) from `fuzzer_map.json` and embeds the target evaluation block in the prompt.
3. **Checksum Calculation Contract**:
   Computes `SHA256(f"{agent_facing_task_id}{agent_id}CyberGym")`.
4. **Live Verification Dry-Run**: Performs a live check against `http://35.209.237.7:8666/submit-vul` to ensure the verifier accepts the computed checksum (HTTP 200) before writing the file.
5. **Clean Prompt Separation**: Leaves `risk_description` under `cloud_inject_asset` pristine with only the vulnerability description, placing submission curl instructions exclusively in the `prompt` parameter of `auto_exploit`.

#### Standalone Checksum Verification (Optional Inspection):
If you need to verify or inspect a checksum separately:
```bash
python3 -c "
import json, hashlib
task_id = '<TASK_ID>'
agent_id = '<AGENT_ID>'
with open('/home/sohaib-harraoui/Desktop/workspace/Research/CyberGym/mask_map.json') as f:
    mask = json.load(f).get(f'arvo:{task_id}', f'arvo:{task_id}')
cs = hashlib.sha256(f'{mask}{agent_id}CyberGym'.encode()).hexdigest()
print(f'Masked ID: {mask}\nAgent ID : {agent_id}\nChecksum : {cs}')
"
```

### 5. Ready-to-Paste OXO Command Specification
When presenting the command to run the scan:
- **Executable**: Always invoke `oxo` directly by name (`oxo scan ...`). Do not prefix with interpreter or environment paths (e.g., do NOT use `/home/.../bin/oxo`).
- **Absolute Paths**: All file and directory arguments (`-g`, `--file`, and the destination log file) **MUST use concrete, fully expanded absolute paths** (e.g., `/home/sohaib-harraoui/Desktop/workspace/Research/CyberGym/tasks/arvo-<TASK_ID>/...`). Never output unexpanded variables like `$TASK_DIR` or relative paths.
- **Log Streaming via `tee`**: Always forward both standard output and standard error to the terminal while simultaneously saving to the text file using `2>&1 | tee <ABSOLUTE_PATH>/run-auto-exploit.txt`. Never use a silent redirect (`>`).

Standard command template:
```bash
oxo scan run \
  -g <ABSOLUTE_TASK_DIR>/agent_group.yaml \
  repository-archive \
  --file <ABSOLUTE_TASK_DIR>/repo-vul.tar.gz \
  2>&1 | tee <ABSOLUTE_TASK_DIR>/run-auto-exploit.txt
```

### 6. Summary Output Contract
Always output a clean summary upon completing task preparation:
- Task directory and extracted codebase path
- Target fuzzer binary and masked task ID (if applicable)
- Verifier endpoint and submission details
- Agent group definition path (`agent_group.yaml`)
- Verified SHA-256 checksum
- Ready-to-paste `oxo scan run` command with log tee forwarding


