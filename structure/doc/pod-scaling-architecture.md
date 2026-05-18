# Pod-Based Scaling Architecture for Large-Scale Migrations

## Document Control
- **Version:** 1.3
- **Date:** 2026-03-19
- **Status:** Proposal
- **Purpose:** Architecture for scaling the Legacy Code Migration Pipeline to handle large engagements (50M+ projects) through parallel pod execution, Git-based artifact management, and relative path resolution.

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Solution Overview](#2-solution-overview)
3. [Pod Model Architecture](#3-pod-model-architecture)
   - 3.4 [Pod Spawning Mechanics](#34-pod-spawning-mechanics)
   - 3.5 [Single-Machine Scalability Assessment](#35-single-machine-scalability-assessment)
   - 3.6 [Fan-Out / Fan-In Execution Pattern](#36-fan-out--fan-in-execution-pattern)
4. [Git Branching Strategy](#4-git-branching-strategy)
   - 4.5 [Git-Based Document Versioning](#45-git-based-document-versioning-replacing-draftapproved-file-duplication)
5. [Relative Path Migration](#5-relative-path-migration)
6. [Phase 2.5: Pod Partitioning](#6-phase-25-pod-partitioning)
7. [Tracker-Based Work Distribution](#7-tracker-based-work-distribution)
8. [Friction Points and Mitigations](#8-friction-points-and-mitigations)
9. [Staffing Impact](#9-staffing-impact)
10. [Required Changes](#10-required-changes)
11. [Implementation Sequence](#11-implementation-sequence)

---

## 1. Problem Statement

### Current Limitations

The Legacy Code Migration Pipeline currently operates as a single-threaded pipeline:

- **Sequential workpackage processing**: The `WORKPACKAGE_LOOP` in the business orchestration processes one workpackage at a time through Phases 3.0 → 3.0.1 → 3.1 → 3.1.1 → 3.2 → 3.2.1 before moving to the next.
- **Single-machine execution**: All agents, supervisors, and specialists run on one machine with absolute paths resolved by `create_project.py`.
- **Absolute path coupling**: `paths.cfg` resolves `{{PROJECT_BASE_PATH}}` to an absolute path (e.g., `/Users/kerimman/projects/CardDemo_Migration/`), which cascades into every prompt, task file, and deliverable reference. This prevents the same project from running on different machines.
- **No parallelism across workpackages**: Even though workpackages are largely independent after Phase 2 (they write to separate `WP-XXX/` directories), the framework processes them sequentially.

### The Scale Challenge

A $50M engagement implies a legacy codebase with potentially hundreds of workpackages. Running them sequentially through the full Phase 3→4→5→6 pipeline would take an impractical amount of time. The framework needs to:

1. **Parallelize workpackage processing** across multiple machines (pods)
2. **Share a common base** (Phase 1+2 outputs, legacy source, templates) across all pods
3. **Maintain isolation** so pods don't interfere with each other
4. **Provide full audit trail** of what was generated, when, and by which pod
5. **Enable cross-pod integration validation** before final merge
6. **Reduce human headcount** by automating quality gates and leveraging AI review loops

---

## 2. Solution Overview

The solution introduces three changes to the existing framework — no new architectural layers, no new agent types:

### 2.1 Phase 2.5: Pod Partitioning (New Prompt/Task)

A new task after Phase 2 (Workpackage Planning) that reads the workpackage dependency DAG and clusters workpackages into pods based on domain affinity and dependency relationships. The Migration Supervisor then delegates each pod's workpackages to separate team supervisor instances.

### 2.2 Git-Based Artifact Management

Use GitHub (or any Git remote) as the shared artifact layer. Each pod works on its own branch, with the shared base (Phase 1+2 outputs, legacy source, templates) on `main`. Workpackage-level branches provide granular isolation within pods. Merges serve as quality gates.

### 2.3 Relative Path Resolution

Change all paths from absolute to relative (relative to repo root). This allows the same project to be cloned and executed on any machine without path conflicts.

---

## 3. Pod Model Architecture

### 3.1 What Stays Shared (Run Once on Main)

| Phase | Output | Reason |
|-------|--------|--------|
| Phase 1: Source Code Analysis | Analysis reports, business flows, module classifications, database analysis | One-time full codebase analysis — all pods need these as read-only inputs |
| Phase 2: Workpackage Planning | Workpackage definitions, DAG, roadmap | Produces the dependency graph that drives pod assignment |
| Phase 2.5: Pod Partitioning | Pod assignments, shared artifact registry | Determines which workpackages go to which pod |
| Cross-cutting artifacts | Business glossary, domain models, shared schemas | Referenced by all pods |

### 3.2 What Gets Parallelized Per Pod

| Phase | Scope | Notes |
|-------|-------|-------|
| Phase 3: Business Specification | Per workpackage within pod | Already loops per WP — just needs to run in parallel across pods |
| Phase 4: Technical Specification | Per workpackage within pod | Depends on Phase 3 output for same WP |
| Phase 5: Code Generation | Per workpackage within pod | Depends on Phase 3+4 output for same WP |
| Phase 6: Deployment | Per workpackage within pod | With dependency ordering for cross-WP integrations |

### 3.3 Pod Structure

```
                    ┌─────────────────────────────┐
                    │     Migration Supervisor      │
                    │   (Shared — Phase 1, 2, 2.5) │
                    └──────────────┬──────────────┘
                                   │
                ┌──────────────────┼──────────────────┐
                ▼                  ▼                   ▼
       ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
       │     Pod A       │ │     Pod B       │ │     Pod C       │
       │  WP-001,003,007│ │  WP-002,004,008│ │  WP-005,006,009│
       │                 │ │                 │ │                 │
       │ Business Team   │ │ Business Team   │ │ Business Team   │
       │ Tech Spec Team  │ │ Tech Spec Team  │ │ Tech Spec Team  │
       │ Dev Team        │ │ Dev Team        │ │ Dev Team        │
       │ Deploy Team     │ │ Deploy Team     │ │ Deploy Team     │
       └────────────────┘ └────────────────┘ └────────────────┘
```

Each pod is a self-contained migration unit running the full Phase 3→4→5→6 pipeline for its assigned workpackages. The agent definitions are already generic and reusable — each pod just gets its own CAO session with different workpackage assignments pointing to the same shared inputs.

### 3.4 Pod Spawning Mechanics — CAO Capability Assessment

#### CAO Architecture (Source Code Evaluation)

Based on analysis of the [cli-agent-orchestrator](https://github.com/awslabs/cli-agent-orchestrator) source code (v0.1.0), CAO provides a layered architecture that maps directly to the pod scaling model:

```
┌─────────────────────────────────────────────────────────┐
│                    Entry Points                          │
│   CLI (cao launch/shutdown)  │  MCP Server (agent tools) │
└──────────────────────┬───────┴──────────────────────────┘
                       │
                ┌──────▼──────┐
                │  FastAPI    │  ← REST API on localhost:9889
                │  HTTP API   │    All MCP tools call this API internally
                └──────┬──────┘
                       │
                ┌──────▼──────┐
                │  Services   │
                ├─────────────┤
                │ • session   │  ← tmux session lifecycle
                │ • terminal  │  ← agent terminal create/input/output/delete
                │ • inbox     │  ← queued message delivery via watchdog
                │ • flow      │  ← cron-scheduled agent sessions
                │ • cleanup   │  ← 14-day retention, auto-cleanup
                └──────┬──────┘
                       │
          ┌────────────┴────────────┐
          │                         │
     ┌────▼────┐              ┌─────▼─────┐
     │ Clients │              │ Providers │  ← kiro_cli, claude_code, codex,
     │ • tmux  │              │           │    gemini_cli, kimi_cli, copilot_cli,
     │ • sqlite│              │           │    q_cli
     └─────────┘              └───────────┘
```

Key implementation details relevant to pod scaling:

- **Terminal isolation**: Each agent runs in its own tmux window within a session. Terminals are identified by 8-char hex IDs (`CAO_TERMINAL_ID` env var). This provides process-level isolation between pods.
- **Status detection**: Providers detect terminal state (IDLE, PROCESSING, COMPLETED, ERROR, WAITING_USER_ANSWER) by parsing tmux output via provider-specific regex patterns. The inbox service uses a watchdog on terminal log files to detect when agents become idle.
- **Message queuing**: Messages are persisted in SQLite before delivery. The inbox service monitors terminal log files via `PollingObserver` (5-second interval). When an idle pattern is detected in the log tail, pending messages are delivered via `send_input()`.
- **Working directory**: Enabled via `CAO_ENABLE_WORKING_DIRECTORY=true`. Paths are canonicalized via `realpath` and validated against a security policy (blocks system dirs like `/`, `/etc`, `/var`, `/tmp`). When not specified, agents inherit the supervisor's current working directory.
- **Provider inheritance**: Worker agents inherit the supervisor's provider by default. Agent profiles can override this with a `provider` key in frontmatter, enabling cross-provider workflows (e.g., Kiro CLI supervisor delegating to Claude Code workers).

#### CAO's Three Orchestration Modes

1. **`handoff`** — Synchronous/blocking (current framework usage)
   - Creates terminal → waits for IDLE/COMPLETED (120s timeout) → sends message → polls until COMPLETED → extracts last response → sends `/exit` → returns output
   - Default task timeout: 600s (configurable up to 3600s)
   - Implementation: `_handoff_impl()` in `mcp_server/server.py`

2. **`assign`** — Asynchronous/parallel (what pods need)
   - Creates terminal → sends message → returns immediately with `terminal_id`
   - Worker must use `send_message` to return results to the caller
   - Implementation: `_assign_impl()` — notably simpler than handoff (no polling, no output extraction)

3. **`send_message`** — Queued inter-agent communication
   - Posts message to receiver's inbox via REST API
   - Messages persisted in SQLite (survives crashes)
   - Delivered when receiver terminal is IDLE (detected via log file watchdog)
   - Delivery order: oldest first (FIFO)

#### Pod Spawning via `assign` (Recommended — Single Machine)

After Phase 2.5 produces the pod assignment JSON, the Migration Supervisor spawns pods using `assign`. This requires `CAO_ENABLE_WORKING_DIRECTORY=true` so each pod can target its own worktree:

```
MIGRATION SUPERVISOR (after Phase 2.5):

    1. Read Pod_Assignment.json
    2. Get own terminal ID: my_id = CAO_TERMINAL_ID
    3. Create git worktrees for each pod (shell commands)

    4. FOR EACH pod in assignments:
        assign(
            agent_profile = "migration_supervisor",
            message = "You are Pod {pod_id}.
                       Your workpackages: {wp_list}.
                       Start at Phase 3 (Phases 1-2.5 complete on main).
                       When all workpackages complete, send results to
                       terminal {my_id} using send_message.",
            working_directory = "./worktrees/{pod_id}/"
        )
        → Returns immediately with terminal_id

    5. Supervisor becomes IDLE after dispatching all assigns
       → Pod completion messages will be delivered to inbox when they arrive

    6. Receive pod completion messages (send_message from each pod)
       → "Pod {pod_id} complete. All WPs approved. Ready for merge."

    7. When all pods report complete:
       → handoff to deployment_reviewer_orchestration for merge validation
```

**Critical: Message delivery requires supervisor to be IDLE.** After dispatching `assign` calls, the supervisor must finish its turn — not loop or sleep. The CAO inbox watchdog monitors terminal log files and delivers queued messages only when the idle pattern is detected. Running shell commands in a loop keeps the supervisor in PROCESSING state and blocks delivery.

**Productive wait pattern**: The supervisor can use `handoff` for sequential work while pods run (e.g., preparing merge validation templates, consolidating shared artifacts). Pod messages queue in SQLite and deliver after the handoff completes and the supervisor returns to IDLE.

```
Migration Supervisor
    │
    ├── Phase 1 (handoff → analysis_team_supervisor)
    ├── Phase 2 (handoff → planning_team_supervisor)
    ├── Phase 2.5 (handoff → pod partitioning task)
    │
    ├── assign → Pod A supervisor (returns immediately)
    ├── assign → Pod B supervisor (returns immediately)
    ├── assign → Pod C supervisor (returns immediately)
    │
    ├── OPTIONAL: handoff → prepare merge templates (productive wait)
    │
    │   [Pods work in parallel on separate worktrees/tmux windows]
    │
    ├── Pod A ──send_message──→ Supervisor inbox (queued in SQLite)
    ├── Pod B ──send_message──→ Supervisor inbox (queued in SQLite)
    ├── Pod C ──send_message──→ Supervisor inbox (delivered when IDLE)
    │
    └── Merge validation (handoff → deployment_reviewer_orchestration)
```

#### What Each Pod Session Looks Like

Each pod is a Migration Supervisor instance scoped to a subset of workpackages. Internally it uses `handoff` for its sequential pipeline — identical to the current single-session model:

```
Pod A Supervisor (tmux window, worktree: ./worktrees/pod-a/, branch: pod/pod-a)
    │
    ├── Phase 3: WP-001 (handoff → business_team_supervisor)
    ├── Phase 3: WP-003 (handoff → business_team_supervisor)
    ├── Phase 3: WP-007 (handoff → business_team_supervisor)
    ├── Phase 4: WP-001 (handoff → business_team_supervisor)
    ├── ... (full pipeline per WP)
    │
    └── send_message(receiver_id=supervisor_id, message="Pod A complete")
```

The parallelism is between pods, not within them. Each pod's internal orchestration is unchanged.

#### Concrete Example: Mapping the CAO Assign Pattern to Pods

The CAO `examples/assign/` directory provides a working reference implementation. The pattern maps directly to pod spawning:

| Assign Example | Pod Equivalent |
|---------------|----------------|
| `analysis_supervisor` | Migration Supervisor (after Phase 2.5) |
| `data_analyst` (×3, parallel via `assign`) | Pod Supervisor (×N, parallel via `assign`) |
| `report_generator` (sequential via `handoff`) | Merge validation (sequential via `handoff` after all pods complete) |
| `send_message` callback with results | Pod completion notification with status summary |

**Key patterns from the example that must be replicated in pod agent profiles:**

1. **Supervisor "How Message Delivery Works" block** (from `analysis_supervisor.md`):
   The Migration Supervisor prompt must include equivalent instructions:
   ```
   ## How Message Delivery Works
   After you call assign() for each pod, worker pods will send results back
   via send_message(). Messages are delivered to your terminal automatically
   when your turn ends and you become idle. This means:
   - DO NOT run shell commands (sleep, echo, etc.) to wait for results
   - DO finish your turn by stating what you dispatched and what you expect
   - Messages will arrive as your next input automatically
   ```

2. **Worker "ALWAYS use send_message" emphasis** (from `data_analyst.md`):
   Pod supervisor profiles must include explicit instructions to call `send_message` on completion:
   ```
   ## IMPORTANT: Completion Callback
   You HAVE the send_message MCP tool available. When all workpackages in your
   pod are complete (all phases approved), you MUST call:
     send_message(receiver_id="[supervisor_terminal_id]",
                  message="Pod [pod_id] complete. All WPs approved.")
   Do NOT present results to the user. ALWAYS call send_message to notify
   the Migration Supervisor.
   ```

3. **Mixed assign + handoff in same workflow**:
   The supervisor dispatches pods via `assign` (parallel), then can use `handoff` for sequential work (e.g., preparing merge templates) while pods run. This is exactly the analysis_supervisor pattern: assign analysts → handoff report_generator → finish turn → receive analyst results → combine.

#### Cross-Provider Pod Execution

CAO supports cross-provider orchestration via agent profile frontmatter. This means different pods could run on different LLM providers to distribute API rate limits:

```markdown
---
name: migration_supervisor_claude
description: Migration Supervisor (Claude Code provider)
provider: claude_code
mcpServers:
  cao-mcp-server:
    type: stdio
    command: uvx
    args: ["--from", "git+https://github.com/awslabs/cli-agent-orchestrator.git@main", "cao-mcp-server"]
---
```

The supervisor could `assign` Pod A to `migration_supervisor_kiro` and Pod B to `migration_supervisor_claude`, spreading load across providers. This is a natural extension — no code changes needed, just additional agent profile variants.

#### CAO Flow Service — Scheduled Pod Monitoring

CAO includes a flow service (`services/flow_service.py`) that supports cron-scheduled agent sessions. This could be repurposed for pod monitoring:

```markdown
---
name: pod-health-check
schedule: "*/10 * * * *"    # Every 10 minutes
agent_profile: pod_monitor
script: ./check_pod_status.sh
---

Pod status report:
- Pod A: [[pod_a_status]]
- Pod B: [[pod_b_status]]
- Pod C: [[pod_c_status]]

If any pod has stalled (no git commits in 30+ minutes), investigate and report.
```

The flow service:
- Runs a script that checks pod health (git log timestamps, status files)
- If `execute: true`, launches an agent session with the rendered prompt
- If `execute: false`, skips (all pods healthy)

This provides automated monitoring without manual polling. The flow daemon runs as a background task in the CAO server's FastAPI lifespan.

#### CAO REST API for External Monitoring

The CAO server exposes a REST API on `localhost:9889` that enables external monitoring and control:

| Endpoint | Use for Pods |
|----------|-------------|
| `GET /sessions` | List all active sessions (pods) |
| `GET /terminals/{id}` | Check pod terminal status (IDLE/PROCESSING/COMPLETED/ERROR) |
| `GET /terminals/{id}/output?mode=last` | Get pod's last output (completion report) |
| `GET /terminals/{id}/inbox/messages?status=pending` | Check queued messages for a pod |
| `POST /terminals/{id}/input` | Send steering/correction to a running pod |
| `GET /terminals/{id}/working-directory` | Verify pod is in correct worktree |

This API enables:
- A dashboard to show real-time pod status
- Human operators to steer individual pods mid-execution
- External scripts to monitor and alert on pod failures
- Integration with the existing web-dashboard

#### Option B: External Launcher (Multi-Machine / 10+ Pods)

For deployments where pods run on separate machines, each machine runs its own CAO server. An external launcher script coordinates:

```
launch_pods.py
    ↓
    Reads Pod_Assignment.json
    ↓
    FOR EACH pod:
        1. SSH to target machine (or trigger container/EC2)
        2. Clone repo + checkout pod branch
        3. Start CAO server (cao-server on port 9889)
        4. cao launch --agents migration_supervisor --provider kiro_cli
        5. Send pod-scoped prompt via REST API: POST /terminals/{id}/input
    ↓
    Monitor via REST API: GET /terminals/{id} on each machine
    ↓
    On all pods complete: trigger merge validation on main machine
```

Each machine's CAO server is independent — no cross-machine CAO communication needed. Git is the coordination layer (push/pull to shared remote).

#### Spawning Decision Matrix

| Criterion | Option A (`assign` — single machine) | Option B (Launcher — multi-machine) |
|-----------|--------------------------------------|-------------------------------------|
| Parallelism | Yes (tmux sessions, shared CAO server) | Yes (separate machines, separate CAO servers) |
| CAO changes required | None — uses existing `assign` + `working_directory` | None — uses existing REST API |
| External dependencies | `CAO_ENABLE_WORKING_DIRECTORY=true` | Python launcher script |
| Complexity | Low | Medium |
| Multi-machine | No | Yes |
| Cross-provider | Yes (agent profile `provider` key) | Yes (each machine can use different provider) |
| Monitoring | REST API + flow service | REST API per machine |
| Pod limit | 3-5 practical (single machine API rate limits) | Scales with machines |
| Recommended for | Most engagements | Very large engagements (10+ pods) |

### 3.5 Single-Machine Scalability Assessment

A key question: how much can a single machine handle before requiring multi-machine deployment?

**Where the work actually happens**:

| Activity | Runs Where | Resource Impact on Local Machine |
|----------|-----------|--------------------------------|
| LLM inference (prompt processing, generation) | Remote (API call) | Negligible — HTTP request/response |
| File I/O (read inputs, write deliverables) | Local | Low — documents are KB-sized, not GB |
| Prompt assembly (resolve paths, build task files) | Local | Negligible — string operations |
| Git operations (commit, branch, merge) | Local | Low — small repo, fast operations |
| CAO server (FastAPI + SQLite + watchdog) | Local | Low — single process, ~50MB |
| CAO tmux sessions (one per agent terminal) | Local | Moderate — each provider CLI process uses ~200-500MB |
| CAO inbox watchdog (PollingObserver) | Local | Low — 5-second polling interval, checks log file tails |

**The bottleneck is LLM API throughput, not local compute.** Since all heavy processing (understanding code, generating specifications, writing documents) happens on the remote LLM, the local machine is essentially a thin client that assembles prompts and writes files.

**CAO-specific resource considerations**:
- Each pod spawns multiple tmux windows (pod supervisor + team supervisors + specialists/reviewers). With `handoff`, child terminals are created and destroyed per task, so the peak concurrent terminal count per pod is ~3-4 (supervisor + active specialist + active reviewer).
- For 3 pods: ~12 concurrent tmux windows at peak, each running a CLI agent process.
- SQLite handles the inbox and terminal metadata — no scaling concern for this volume.
- The watchdog monitors terminal log files in `~/.aws/cli-agent-orchestrator/logs/terminal/`. With 12 log files, the 5-second polling is negligible.

**Practical limits per machine**:

| Pod Count | Feasibility | Limiting Factor |
|-----------|------------|-----------------|
| 1-3 pods | Comfortable | No issues — ~12 concurrent tmux windows, well within capacity |
| 3-5 pods | Recommended max for single machine | ~20 concurrent tmux windows, ~2-4GB RAM for CLI agent processes |
| 5-10 pods | Possible but watch API rate limits | LLM API rate limits become the constraint; use cross-provider to distribute |
| 10+ pods | Use separate machines | Each machine runs its own CAO server; coordinate via git + REST API |

**Recommendation**: Start with 3-5 pods on a single machine using git worktrees + CAO `assign`. This is sufficient for most engagements. Scale to separate machines only when:
- LLM API rate limits are hit (mitigate first with cross-provider pod profiles)
- The engagement has 20+ pods (rare — implies 60+ workpackages)
- Organizational requirements mandate resource isolation

### 3.6 Fan-Out / Fan-In Execution Pattern

The pod model follows a classic fan-out/fan-in pattern. This is the core execution flow:

```
                         FAN-OUT
                            │
Phase 1 (Analysis)          │  ← shared, sequential
Phase 2 (Workpackage Plan)  │  ← shared, sequential
Phase 2.5 (Pod Partition)   │  ← shared, sequential
                            │
    ┌───────────────────────┼───────────────────────┐
    ▼                       ▼                       ▼
  Pod A                   Pod B                   Pod C
  assign(worker_1,        assign(worker_2,        assign(worker_3,
    "WP-001,003,007         "WP-002,004,008         "WP-005,006,009
     through all phases")    through all phases")    through all phases")
    │                       │                       │
    Phase 3→4→5→6           Phase 3→4→5→6           Phase 3→4→5→6
    (independent)           (independent)           (independent)
    │                       │                       │
    └───────────────────────┼───────────────────────┘
                            │
                         FAN-IN
                            │
              Merge Validation (deployment_reviewer_orchestration)
              Consolidate pod artifacts (glossaries, status)
              Merge pod branches → main
                            │
                     Integrated main
                     (deployment-ready)
```

Each "worker" in the fan-out is a Migration Supervisor instance scoped to a subset of workpackages. Internally, each pod uses the existing 3-layer hierarchy unchanged — the supervisor delegates to team supervisors, who delegate to specialists, who produce deliverables that reviewers validate. The parallelism is between pods, not within them.

The fan-in is where the work recombines:
1. Each pod signals completion via `send_message` (single machine) or REST API (multi-machine)
2. The Migration Supervisor triggers merge validation for `deployment_reviewer_orchestration`
3. The validator checks cross-pod consistency (API contracts, shared entities, glossary alignment)
4. Pod branches merge to `main` in dependency order (if Pod B depends on Pod A's entity, Pod A merges first — defined by `cross_pod_dependencies` from Phase 2.5)
5. Once all pods are merged, `main` has the complete integrated output

---

## 4. Git Branching Strategy

### 4.1 Branch Hierarchy

```
main                              ← shared base (Phase 1+2 outputs, legacy source, templates)
├── pod/pod-a                     ← pod integration branch
│   ├── wp/WP-001                 ← workpackage work branch
│   ├── wp/WP-003                 ← workpackage work branch
│   └── wp/WP-007                 ← workpackage work branch
├── pod/pod-b                     ← pod integration branch
│   ├── wp/WP-002
│   ├── wp/WP-004
│   └── wp/WP-008
└── pod/pod-c
    ├── wp/WP-005
    ├── wp/WP-006
    └── wp/WP-009
```

### 4.2 What Lives Where

```
main branch
├── input/                    (legacy source, specs — read-only shared base)
├── output/
│   ├── analysis/             (Phase 1 output — shared, committed to main)
│   └── analysis/workpackages/ (Phase 2 output — shared, committed to main)
├── templates/                (shared)
├── prompts/                  (shared)
├── agents/                   (shared)
└── config/                   (shared)

pod/pod-a branch (from main)
├── output/
│   ├── specifications/business/specs/WP-001/...
│   ├── specifications/business/specs/WP-003/...
│   ├── specifications/technical/specs/WP-001/...
│   ├── gen_src/backend/WP-001/...
│   └── gen_src/frontend/WP-001/...
```

### 4.3 Merge Flow as Quality Gate

The merge flow replaces the current file-based approval workflow:

1. **Specialist works** on `wp/WP-001` branch
2. **Reviewer reviews** on same branch (iterative specialist→reviewer loop)
3. **Approved** → merge `wp/WP-001` to `pod/pod-a`
4. **All pod WPs done** → cross-pod integration validation
5. **Integration validated** → merge `pod/pod-a` to `main`
6. **Phase 6 (deployment)** runs from `main`

This gives you:
- Full audit trail for free (git log)
- Trivial rollback (git reset)
- Human reviewers can do PRs for quality gates
- Existing path resolution still works (paths are relative to repo root, same in every branch)

### 4.4 Execution Model: Worktrees vs. Separate Instances

**For 3-5 pods on one machine** — use `git worktree`:

```
project-root/
├── .git/                          (shared object store)
├── main/                          (main worktree)
└── worktrees/
    ├── pod-a/                     (git worktree for pod/pod-a branch)
    ├── pod-b/                     (git worktree for pod/pod-b branch)
    └── pod-c/                     (git worktree for pod/pod-c branch)
```

Setup:
```bash
git worktree add worktrees/pod-a pod/pod-a
git worktree add worktrees/pod-b pod/pod-b
```

Each pod's CAO session gets its own worktree path. No cloning overhead, no object duplication.

**For 10+ pods** — separate instances (EC2, containers, etc.):
- Each instance gets a full clone (or shallow clone)
- Runs its pod independently
- Pushes to shared Git remote
- Resource isolation — one pod's heavy LLM usage doesn't starve another

### 4.5 Git-Based Document Versioning (Replacing Draft/Approved File Duplication)

#### The Current Problem

The existing workflow creates separate files for each document state:

```
WP-001-business-context-draft.md      ← specialist creates
WP-001-business-context-approved.md   ← created on approval (near-copy of draft)
```

When a reviewer rejects a draft, the specialist often regenerates the entire document from scratch rather than editing the existing one. This means:
- **Duplicate token cost**: The LLM generates the full document again (output tokens are the expensive/slow ones)
- **Duplicate files**: Draft and approved versions coexist, consuming storage and creating confusion about which is canonical
- **Lost diff visibility**: No easy way to see what changed between iterations

#### The Git-Based Alternative

With git, there is only one file per deliverable. Version history replaces file duplication:

```
WP-001-business-context.md            ← single file, versioned in git
```

The document carries its status in a metadata header:

```markdown
---
status: draft | in_review | approved
workpackage: WP-001
phase: 3.0
last_updated: 2026-03-17
reviewed_by: business_reviewer_requirements
approval_iteration: 2
---
```

#### Lifecycle with Git Versioning

```
1. Specialist CREATES document (status: draft)
   → git add WP-001-business-context.md
   → git commit -m "WP-001: Phase 3.0 business context - draft"

2. Reviewer REVIEWS document (status: in_review)
   → Reviewer reads existing file, produces review report
   → If changes needed: review report lists specific sections to fix

3. Specialist EDITS document in place (status: draft, iteration 2)
   → LLM reads existing document + review feedback
   → LLM produces TARGETED EDITS (not full regeneration)
   → git commit -m "WP-001: Phase 3.0 business context - revision per review"

4. Reviewer RE-REVIEWS (reads doc + git diff from previous version)
   → git diff HEAD~1 shows exactly what changed
   → Reviewer focuses on changed sections, not entire document

5. Approval (status: approved)
   → Specialist updates status header to "approved"
   → git commit -m "WP-001: Phase 3.0 business context - approved"
   → git merge wp/WP-001 → pod/pod-a (merge = quality gate)
```

#### Token Savings Analysis

| Scenario | Current (Regenerate) | Git-Based (Edit in Place) | Savings |
|----------|---------------------|--------------------------|---------|
| 50-page spec, minor revisions | ~50 pages output tokens × N iterations | ~5 pages output tokens × N iterations | ~90% output token reduction per iteration |
| 50-page spec, major revisions | ~50 pages output tokens × N iterations | ~20 pages output tokens × N iterations | ~60% output token reduction per iteration |
| Reviewer re-review | Reads full document each time | Reads full doc + focused diff | Faster review, same input tokens |
| Approval step | Generate new approved file (~50 pages) | Update 1 metadata field (1 line) | ~99% reduction for approval step |

The savings compound across workpackages and phases. For a 50-workpackage engagement with 3 review iterations average, the difference is substantial.

#### Speed Improvement

Editing an existing document is faster than regenerating it because:
- **Fewer output tokens**: The LLM only produces the changed sections, not the entire document
- **Output tokens are the slow/expensive dimension** — input tokens (reading the existing doc) are fast and cheap by comparison
- **Reviewer cycles are faster**: `git diff` gives the reviewer a precise scope of changes, reducing review time

#### Required Prompt Changes

Agent prompts must shift from a "create new" to an "edit existing" model:

| Current Prompt Pattern | New Prompt Pattern |
|----------------------|-------------------|
| "Create the business context document at path X" | "If the document exists at path X, read it and apply the required changes. If it does not exist, create it." |
| "Create approved version at path X-approved.md" | "Update the status field in the document header to 'approved' and commit." |
| "Archive draft to review folder" | Remove — git history serves as the archive |
| "Compare draft against approved" | "Run `git diff HEAD~1` to see changes since last version" |

**Key instruction for specialists**: "When revising a document after reviewer feedback, read the existing document and make targeted edits to the specific sections identified in the review report. Do NOT regenerate the entire document."

**Key instruction for reviewers**: "When re-reviewing a revised document, use `git diff` to identify what changed since your last review. Focus your validation on the changed sections while confirming the unchanged sections remain intact."

#### What This Replaces

| Current Mechanism | Replaced By |
|------------------|-------------|
| `*-draft.md` / `*-approved.md` file pairs | Single file with status header |
| Draft archival to review folder | Git history (`git log --follow <file>`) |
| Separate review report files | Review reports remain (structured feedback), but audit trail is in git |
| Status tracking in separate JSON files | Status in document header + git tags for milestones |
| Manual diff between draft iterations | `git diff` between commits |

#### Backward Compatibility

For single-machine, non-pod projects that don't use git branching, the edit-in-place model still works — the specialist edits the file and the reviewer reviews it. The only difference is the status header convention and the prompt instructions to edit rather than recreate. No git operations are required for the single-machine case (though they're recommended for audit trail).

---

## 5. Relative Path Migration

### 5.1 The Problem

Currently, `create_project.py` resolves `{{PROJECT_BASE_PATH}}` to an absolute path like `/Users/kerimman/projects/CardDemo_Migration/`. This cascades into every other path variable via `paths.cfg`. When a pod runs on a different machine where the project lives at `/home/ec2-user/CardDemo_Migration/`, all paths break.

### 5.2 The Fix

Change `paths.cfg` so all paths are relative to the repository root:

```properties
# BEFORE (absolute — breaks on different machines)
PROJECT_BASE_PATH = /Users/kerimman/projects/CardDemo_Migration
SOURCE_CODE = {{PROJECT_BASE_PATH}}/input/legacy/legacy_code

# AFTER (relative to repo root — works everywhere)
PROJECT_BASE_PATH = .
SOURCE_CODE = ./input/legacy/legacy_code
```

Every agent works from the repo root (which is the worktree root on each machine). The paths resolve correctly regardless of where the repo is cloned.

### 5.3 Files That Need Updating

| File/Area | Change |
|-----------|--------|
| `config/paths.cfg` | Change `PROJECT_BASE_PATH` to `.`, all paths become `./...` relative |
| `create_project.py` | Stop prepending absolute base path; use `./` as root |
| `structure/doc/task_file_template.md` | Update path resolution guidelines: "relative to repo root" instead of "absolute" |
| `structure/doc/orchestration_architecture.md` | Update path resolution rules in Section 6.3 |
| All agent supervisor prompts | Update rule "ALWAYS maintain absolute file paths" → "ALWAYS maintain paths relative to repo root" |
| `development_team_supervisor.md` | Rule 5: change "absolute file paths" to "relative file paths" |
| All existing resolved prompts in created projects | Search-and-replace absolute prefix with `./` |

### 5.4 Backward Compatibility

For existing single-machine projects that don't need pods, relative paths work identically — `./input/legacy/legacy_code` resolves correctly when the agent's working directory is the project root. No behavioral change for the single-machine case.

---

## 6. Phase 2.5: Pod Partitioning

### 6.1 Purpose

A new prompt/task that runs after Phase 2 (Workpackage Planning) and before Phase 3 (Business Specification). It reads the workpackage dependency DAG and clusters workpackages into pods.

### 6.2 Inputs

- Workpackage Planning JSON: `./output/analysis/workpackages/Workpackage_Planning.json`
- Business Flows: `./output/analysis/source_code/flows/Business_Flows.json`
- Module Classifications: `./output/analysis/source_code/Module_Classifications.json`
- Database Analysis: `./output/analysis/database/reports/DB_Source_Analysis_Report.md`

### 6.3 Clustering Criteria

The partitioning must account for:

1. **Dependency DAG**: Workpackages with direct dependencies should be in the same pod to avoid cross-pod blocking.
2. **Domain affinity**: Workpackages that share business entities, DB tables, or COBOL copybooks should be in the same pod. This minimizes cross-pod file overlap and merge conflicts.
3. **Size balancing**: Pods should be roughly equal in estimated effort to avoid one pod finishing far ahead of others.
4. **Configurable pod count**: The number of pods should be a parameter (default: auto-calculated based on total workpackages and available machines).

### 6.4 Outputs

```json
{
  "pod_assignments": {
    "pod-a": {
      "workpackages": ["WP-001", "WP-003", "WP-007"],
      "domain_cluster": "account-management",
      "estimated_effort": "high",
      "shared_entities": ["Account", "Customer"],
      "shared_db_tables": ["ACCTDAT", "CUSTDAT"]
    },
    "pod-b": {
      "workpackages": ["WP-002", "WP-004", "WP-008"],
      "domain_cluster": "transaction-processing",
      "estimated_effort": "high",
      "shared_entities": ["Transaction", "Card"],
      "shared_db_tables": ["TRANSACT", "CARDDAT"]
    }
  },
  "cross_pod_dependencies": [
    {
      "from_pod": "pod-b",
      "to_pod": "pod-a",
      "dependency_type": "shared_entity",
      "entity": "Account",
      "resolution": "pod-a produces first, pod-b consumes via main branch"
    }
  ],
  "shared_artifacts": [
    "business-glossary.md",
    "domain-models/"
  ]
}
```

### 6.5 Integration into Existing Workflow

The Migration Supervisor's workflow becomes:

```
Phase 1 (Analysis)           → run once on main
Phase 2 (Workpackage Planning) → run once on main
Phase 2.5 (Pod Partitioning)   → run once on main, NEW
    ↓
    Create branches + worktrees/instances
    ↓
Phase 3-6 (per pod, parallel)  → each pod on its own branch
    ↓
    Merge validation → merge to main
```

No new orchestration layer needed. The Migration Supervisor reads the pod assignment output and delegates each pod's workpackages to separate team supervisor instances, exactly as it delegates phases today.

---

## 7. Tracker-Based Work Distribution

### 7.1 Motivation

The pod assignment JSON from Phase 2.5 is a static artifact — the supervisor reads it and delegates. But if you push the workpackages and pod assignments to a bug/feature tracker (GitHub Issues, Jira, or a project board), the model becomes dynamic and self-service:

- Pods become claimable: an agent (or a human) picks up an unassigned pod from the board
- Progress is visible without reading git branches or status JSONs
- If a pod fails or stalls, another agent can pick up the remaining workpackages
- Fast pods that finish early can claim more work (natural load balancing)
- Humans and agents use the same interface to see what's done and what's pending

### 7.2 Static Assignment vs. Dynamic Claiming

```
STATIC (current design — supervisor assigns):
  Supervisor → assign(pod-a, WP-001,003,007)
  Supervisor → assign(pod-b, WP-002,004,008)
  Supervisor → assign(pod-c, WP-005,006,009)

DYNAMIC (tracker-based — workers claim):
  Supervisor → publishes pods to tracker (GitHub Issues / Jira board)
  Worker 1 → claims pod-a from tracker → processes it → marks complete
  Worker 2 → claims pod-b from tracker → processes it → marks complete
  Worker 3 → finishes early → claims next available pod from tracker
```

Both models can coexist. Phase 2.5 produces the pod assignment JSON regardless. The question is whether the supervisor pushes assignments to workers (static) or publishes them to a board where workers pull (dynamic).

### 7.3 Tracker Structure

Each pod becomes a tracker item (GitHub Issue, Jira ticket, etc.):

```
┌─────────────────────────────────────────────────────┐
│ Issue: Pod A — Account Management Domain             │
│ Status: Available / Claimed / In Progress / Complete │
│ Assignee: (none until claimed)                       │
│ Labels: pod, domain:account-management, priority:1   │
│                                                      │
│ Workpackages:                                        │
│   - [ ] WP-001: Account CRUD operations              │
│   - [ ] WP-003: Account validation rules             │
│   - [ ] WP-007: Account reporting                    │
│                                                      │
│ Branch: pod/pod-a                                    │
│ Estimated effort: High                               │
│ Dependencies: None (can start immediately)           │
│                                                      │
│ Cross-pod dependencies:                              │
│   - Pod B depends on Account entity from this pod    │
│   - This pod must merge before Pod B                 │
└─────────────────────────────────────────────────────┘
```

Within each pod issue, individual workpackages can be sub-issues or checklist items with their own status:

```
Pod A (Issue #12)
  ├── WP-001 (Sub-issue #13) — Phase 3: In Progress
  ├── WP-003 (Sub-issue #14) — Phase 3: Not Started
  └── WP-007 (Sub-issue #15) — Not Started
```

### 7.4 Agent Self-Assignment Flow

For agents to claim pods autonomously, they need tracker API access. This can be provided via an MCP server for the tracker (GitHub MCP, Jira MCP, etc.):

```
Agent starts up
    → Queries tracker: "List pods with status=Available, sorted by priority"
    → Claims highest-priority available pod: updates status to "Claimed", sets assignee
    → Reads pod details: workpackage list, branch name, dependencies
    → Checks out pod branch, starts Phase 3 pipeline
    → Updates tracker as workpackages complete (checkboxes, status updates)
    → On pod completion: updates status to "Complete", notifies supervisor
    → Queries tracker again: "Any more Available pods?"
    → If yes: claims next pod (load balancing)
    → If no: signals idle to supervisor
```

This requires:
- A tracker MCP server (GitHub Issues MCP already exists)
- A `publish_pods_to_tracker.py` script that reads `Pod_Assignment.json` and creates issues
- Agent prompts that include tracker interaction instructions

### 7.5 Benefits Over Static Assignment

| Aspect | Static Assignment | Tracker-Based Claiming |
|--------|------------------|----------------------|
| Visibility | Git branches + status JSONs | Project board (humans + agents see same view) |
| Load balancing | Fixed at assignment time | Dynamic — fast workers claim more |
| Failure recovery | Manual reassignment | Another agent claims the stalled pod |
| Human oversight | Read git logs | Glance at project board |
| Scalability | Works, but rigid | Scales naturally with more workers |
| Agent autonomy | Supervisor must assign | Agents self-organize |
| Progress tracking | Per-pod status files | Tracker dashboard (built-in) |

### 7.6 Implementation Approach

This is an additive enhancement — it doesn't replace the static assignment model, it layers on top:

1. Phase 2.5 still produces `Pod_Assignment.json` (the source of truth)
2. A `publish_pods_to_tracker.py` script creates tracker items from the JSON
3. Agent prompts include optional tracker interaction (claim/update/complete)
4. If no tracker is configured, the static `assign` model works as before
5. The tracker becomes the single pane of glass for project progress

### 7.7 Future: Fully Autonomous Pod Fleet

The tracker model opens the door to a fully autonomous fleet where:
- A pool of agent instances runs continuously
- Each instance queries the tracker for available work
- Instances claim pods, process them, and return for more
- The supervisor only intervenes for escalations and merge validation
- Humans monitor the project board and handle exceptions

This is the end-state vision. The static assignment model is the starting point, the tracker is the bridge.

---

## 8. Friction Points and Mitigations

### 8.1 Git Merge Conflicts

**Risk**: Multiple pods writing to the same files.

**Mitigation by design**: Pod partitioning assigns distinct workpackages to each pod. Output paths are namespaced by workpackage ID (`WP-001/`, `WP-002/`), so pods write to different directories. Conflicts are structurally impossible for workpackage-scoped outputs.

**Remaining conflict surfaces and solutions**:

| Shared Artifact | Solution |
|----------------|----------|
| Business glossary (`business-glossary.md`) | Each pod maintains pod-scoped additions (`business-glossary-pod-a.md`). Consolidation step merges them at pod→main merge time. |
| Progress tracking / status JSONs | Pod-scoped status files (`Business_Specification_Status-pod-a.json`). Dashboard reads all of them. |
| Shared domain models | Phase 2.5 partitioning groups workpackages that share entities into the same pod. Cross-pod entity sharing is flagged in `cross_pod_dependencies`. |

A conflict resolution prompt exists as a fallback but should be an exception handler, not a regular part of the flow.

### 8.2 Concurrent Git Operations

**On same machine (worktrees)**: `git worktree` provides separate working directories sharing the same `.git` object store. No concurrent git operation conflicts — each worktree is independent.

**On separate machines**: Each instance has its own clone. Push/pull to shared remote. Standard Git concurrency model applies — no issues as long as pods push to different branches (which they do by design).

### 8.3 Large Repositories

**Legacy input codebase**: Read-only for all pods, never changes after Phase 1. Options:
- If in same repo: committed to `main` before branching, every worktree/clone already has it
- If very large (millions of LOC): keep outside git as a read-only shared mount, referenced via `SOURCE_CODE` path
- Shallow clone (`--depth 1`) if legacy source is in a separate repo

**Generated outputs**: Much smaller than legacy input. Repo size is not a concern on the output side.

### 8.4 Final Merge to Main

The most critical integration point. Use the existing `deployment_reviewer_orchestration` agent (already in the deployment team) with a merge validation task file.

**Merge validation flow**:

```
Pod branch complete
    → deployment_reviewer_orchestration runs pre-merge validation task
    → Creates PR with validation report
    → Human reviews PR (focused on validation report, not every file)
    → Approve/reject
    → Merge to main
```

**What the validation task checks**:
- Every workpackage in the pod has approved status
- Cross-pod API contract consistency (do Pod A and Pod B's generated services use compatible interfaces?)
- Consolidated glossary consistency
- No orphaned references to entities from other pods
- Integration test readiness

No new agent needed — `deployment_reviewer_orchestration` already handles orchestration and integration review concerns. This is just a new task file template for it.

---

## 9. Staffing Impact

### 9.1 Why Pods Reduce Headcount

The current framework already automates the specialist→reviewer iteration loop (AI reviews AI). Quality gates have automated confidence thresholds (drift detection at <5% and <10%). Human intervention is exception-based, not checkpoint-based.

With pods, the parallelism multiplier means the same amount of work completes in a fraction of the time, and the AI-driven review loops handle the volume that would otherwise require proportionally more humans.

### 9.2 Estimated Staffing Model

| Role | Without Pods (Sequential) | With Pods (10 Parallel) |
|------|--------------------------|------------------------|
| Migration Architects | 8-10 | 2-3 |
| Business Analysts | 15-20 | 3-5 (exception review only) |
| Developers | 30-40 | 5-8 (integration/fixes) |
| QA Engineers | 10-15 | 3-4 (validation) |
| Project Managers | 5-8 | 2-3 |
| **Total** | **~70-90** | **~15-23** |

Human roles shift from "doing the work" to "supervising the AI doing the work":
- 1-2 domain experts per pod cluster (covering 3-5 pods) instead of per-workpackage
- Developers focus on integration issues and edge cases the AI can't resolve
- QA validates the AI's validation rather than doing primary validation

---

## 10. Required Changes

### 10.1 New Files to Create

| File | Purpose |
|------|---------|
| `structure/prompts/02_workpackage/02_pod_partitioning.md` | Phase 2.5 pod partitioning prompt — reads DAG, clusters by domain + dependency, outputs pod assignments |
| `structure/templates/Pod_Assignment.json` | Template for pod assignment output |
| `structure/templates/Pod_Merge_Validation.md` | Template for merge validation task file used by `deployment_reviewer_orchestration` |
| `create_pod_worktrees.py` | Script that reads pod assignment JSON and creates Git branches + worktrees |
| `consolidate_pod_artifacts.py` | Script that merges pod-scoped glossaries, status files, and progress tracking at merge time |
| `structure/agents/migration_supervisor_pod.md` | Pod-scoped variant of migration supervisor agent profile (same as base but with `assign`/`send_message` instructions for pod completion callback) |
| `scripts/check_pod_status.sh` | Health check script for CAO flow service — checks git commit timestamps and status files per pod |
| `flows/pod-health-check.md` | CAO flow definition for scheduled pod monitoring (see Section 3.4) |
| `launch_pods.py` | External launcher for multi-machine deployments only (Option B) — reads pod assignments, SSHs to machines, starts CAO servers, monitors via REST API |
| `publish_pods_to_tracker.py` | Script that reads `Pod_Assignment.json` and creates tracker items (GitHub Issues / Jira tickets) for each pod and its workpackages (see Section 7) |
| Tracker MCP configuration | Configuration for tracker MCP server (GitHub Issues MCP or Jira MCP) to enable agent self-assignment and status updates |

### 10.2 Files to Modify

| File | Change |
|------|--------|
| **`config/paths.cfg`** | Change `PROJECT_BASE_PATH` from absolute to `.` (relative). All downstream paths become `./...` |
| **`create_project.py`** | Stop resolving `PROJECT_BASE_PATH` to absolute path. Use `.` as root. |
| **`structure/agents/migration_supervisor.md`** | Add Phase 2.5 delegation between Phase 2 and Phase 3. Update path references from "absolute" to "relative to repo root". |
| **`structure/prompts/ReImagine_Main_Prompt.md`** | Add Phase 2.5 section. Update path resolution notes. |
| **`structure/agents/development_team/development_team_supervisor.md`** | Rule 5: change "absolute file paths" to "paths relative to repo root" |
| **`structure/agents/analysis_team/analysis_team_supervisor.md`** | Same path rule update |
| **`structure/agents/business_team/business_team_supervisor.md`** | Same path rule update |
| **`structure/agents/planning_team/planning_team_supervisor.md`** | Same path rule update (if applicable) |
| **`structure/agents/deployment_team/deployment_team_supervisor.md`** | Same path rule update. Add merge validation task delegation. |
| **`structure/doc/orchestration_architecture.md`** | Update Section 6.3 (Path Resolution Rules): relative instead of absolute. Add pod scaling section. |
| **`structure/doc/task_file_template.md`** | Update Section 4 (Path Resolution Guidelines): relative to repo root. Update all examples. |
| **`structure/prompts/03-business_extraction/01_business_specification_master-orchestration.md`** | Update `WORKPACKAGE_LOOP` to support pod-scoped execution. Add pod-scoped glossary pattern. Add git commit after deliverable approval. Change document lifecycle from draft/approved file pairs to single-file edit-in-place with status header (see Section 4.5). |
| **`structure/prompts/05_code_generation/02_code_generation_master_orchestration.md`** | Same document versioning changes as business orchestration — edit-in-place model for all deliverables. |
| **All specialist agent prompts** | Change "create document at path" to "if document exists, edit in place; if not, create". Add instruction: "When revising after review, make targeted edits, do NOT regenerate the entire document." |
| **All reviewer agent prompts** | Add instruction: "Use `git diff` to identify changes since last review. Focus validation on changed sections." Change approval action from "create approved copy" to "update status header to approved". |
| **`structure/web-dashboard/`** | Update dashboard to read from multiple worktrees/branches for cross-pod visibility. |

### 10.3 Git Workflow Additions to Agent Prompts

Team supervisor prompts need these additions for the pod workflow:

**After specialist deliverable approval**:
```
git add <deliverable_paths>
git commit -m "WP-XXX: Phase 3.X deliverable approved"
```

**After all workpackage phases complete on WP branch**:
```
git checkout pod/pod-a
git merge wp/WP-XXX --no-ff -m "WP-XXX: All phases complete, approved"
```

**After all pod workpackages complete**:
```
# Trigger merge validation task for deployment_reviewer_orchestration
# Create PR: pod/pod-a → main
```

These are additions to existing supervisor prompts, not new agents or layers.

---

## 11. Implementation Sequence

### Phase 1: Foundation (Relative Paths)
1. Update `config/paths.cfg` — all paths relative
2. Update `create_project.py` — stop absolute resolution
3. Update documentation (orchestration architecture, task file template)
4. Update all agent supervisor prompts — "relative to repo root"
5. Test: create a project, verify all agents work with relative paths

### Phase 2: Document Versioning (Edit-in-Place)
6. Define document status header convention (draft / in_review / approved)
7. Update specialist prompts — edit existing documents instead of regenerating
8. Update reviewer prompts — use git diff for re-reviews, update status header on approval
9. Remove draft/approved file pair logic from orchestration prompts
10. Test: run one workpackage through Phase 3 with edit-in-place model, verify token reduction

### Phase 3: Pod Partitioning
11. Create Phase 2.5 prompt (`02_pod_partitioning.md`)
12. Create pod assignment template (`Pod_Assignment.json`)
13. Update Migration Supervisor prompt — add Phase 2.5 delegation
14. Update `ReImagine_Main_Prompt.md` — add Phase 2.5 section
15. Test: run Phase 2.5 on existing workpackage output, verify clustering

### Phase 4: Git Branching + CAO Pod Configuration
16. Create `create_pod_worktrees.py` script
17. Create pod-scoped migration supervisor agent profile (`migration_supervisor_pod.md`)
18. Configure `CAO_ENABLE_WORKING_DIRECTORY=true` in CAO server environment
19. Create `consolidate_pod_artifacts.py` script
20. Add git operations to team supervisor prompts
21. Create merge validation task template
22. Test: create branches, run one pod end-to-end via `assign`, merge to main

### Phase 5: Multi-Pod Execution
23. Update Migration Supervisor prompt to use `assign` for pod spawning after Phase 2.5
24. Create CAO flow for pod health monitoring (`pod-health-check.md` + `check_pod_status.sh`)
25. Update dashboard for multi-branch visibility + CAO REST API integration
26. Test: run 2-3 pods in parallel via `assign` on single machine with worktrees
27. Test cross-provider pod execution (e.g., Pod A on Kiro CLI, Pod B on Claude Code)
28. Validate merge flow and cross-pod integration

### Phase 6: Tracker-Based Work Distribution (Optional — Dynamic Claiming)
29. Create `publish_pods_to_tracker.py` script — reads `Pod_Assignment.json`, creates GitHub Issues / Jira tickets per pod
30. Configure tracker MCP server (GitHub Issues MCP or Jira MCP) for agent access
31. Add tracker interaction instructions to pod supervisor prompts (claim/update/complete)
32. Test: publish pods to tracker, verify agent can claim and process a pod via tracker
33. Test: verify fast-finishing agent claims additional available pods (load balancing)

### Phase 7: Multi-Machine Scale (Optional — 10+ Pods)
34. Create `launch_pods.py` for multi-machine orchestration via CAO REST API
35. Test: run pods on separate machines with shared Git remote
36. Validate cross-machine monitoring and merge coordination

---

## Appendix A: Current vs. Target Architecture

```
CURRENT (Sequential, Single Machine):

Phase 1 → Phase 2 → Phase 3 (WP-001 → WP-002 → ... → WP-N) → Phase 4 → Phase 5 → Phase 6
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                     Sequential — one WP at a time

TARGET (Parallel Pods, Multi-Machine):

Phase 1 → Phase 2 → Phase 2.5 (Pod Partitioning)
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
           Pod A       Pod B      Pod C        ← parallel, separate branches
         (WP 1,3,7)  (WP 2,4,8) (WP 5,6,9)
           │           │           │
           Phase 3-6   Phase 3-6   Phase 3-6   ← full pipeline per pod
           │           │           │
           └──────────┼──────────┘
                      ▼
              Merge Validation                  ← deployment_reviewer_orchestration
                      ▼
                    main                        ← integrated, deployment-ready
```

## Appendix B: Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| No new orchestration layer | Migration Supervisor already delegates phases. Pod partitioning is just a new task, not a new layer. |
| No new agent types | `deployment_reviewer_orchestration` already handles integration review. Merge validation is a new task file, not a new agent. |
| CAO `assign` for pod spawning (single machine) | Native CAO capability — no external scripts needed. `assign` creates tmux terminal, sends pod-scoped prompt, returns immediately. `send_message` provides completion callback. See Section 3.4. |
| External launcher only for multi-machine (10+ pods) | Most engagements fit on one machine. External launcher (`launch_pods.py`) only needed when pods must run on separate machines for API rate limit distribution. |
| `CAO_ENABLE_WORKING_DIRECTORY=true` | Required for pod worktree isolation. Each `assign` call targets a different worktree path. Security policy blocks system dirs. |
| Cross-provider pod profiles for rate limit distribution | CAO agent profiles support `provider` key in frontmatter. Different pods can use different LLM providers (Kiro CLI, Claude Code, etc.) to spread API load without separate machines. |
| CAO flow service for pod monitoring | Cron-scheduled health checks via existing flow service. Script checks git commit timestamps; agent investigates stalled pods. No custom monitoring infrastructure needed. |
| CAO REST API for dashboard integration | `GET /terminals/{id}` provides real-time pod status. Dashboard polls API instead of parsing files. Human operators can steer pods via `POST /terminals/{id}/input`. |
| Git branches as artifact layer | File-system based (matches existing framework), provides audit trail, enables PRs as quality gates, supports multi-machine execution. |
| Single-file edit-in-place over draft/approved pairs | Reduces output token cost by ~60-90% per revision iteration. Git history replaces file duplication. Status tracked in document header. See Section 4.5. |
| Relative paths over late-binding | Simpler, no runtime resolution step, "relative to repo root" is a universal convention. |
| Pod-scoped glossaries over shared writes | Eliminates merge conflicts on shared files. Consolidation at merge time is clean and deterministic. |
| Worktrees for small scale, separate instances for large | Worktrees share object store (efficient), separate instances provide resource isolation (scalable). 3-5 pods per machine is the practical sweet spot — LLM API rate limits are the bottleneck, not local compute. See Section 3.5. |
| Phase 2.5 uses domain affinity clustering | Minimizes cross-pod dependencies and merge conflicts by keeping related workpackages together. |
| Tracker-based work distribution as optional layer | Adds dynamic claiming, visible progress, and failure recovery on top of static assignment. Agents and humans share the same project board. Does not replace static `assign` — layers on top. See Section 7. |
