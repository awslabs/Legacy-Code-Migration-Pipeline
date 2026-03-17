# Pod-Based Scaling Architecture for Large-Scale Migrations

## Document Control
- **Version:** 1.0
- **Date:** 2026-03-06
- **Status:** Proposal
- **Purpose:** Architecture for scaling the Agentic Code Migrator to handle large engagements (50M+ projects) through parallel pod execution, Git-based artifact management, and relative path resolution.

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Solution Overview](#2-solution-overview)
3. [Pod Model Architecture](#3-pod-model-architecture)
4. [Git Branching Strategy](#4-git-branching-strategy)
5. [Relative Path Migration](#5-relative-path-migration)
6. [Phase 2.5: Pod Partitioning](#6-phase-25-pod-partitioning)
7. [Friction Points and Mitigations](#7-friction-points-and-mitigations)
8. [Staffing Impact](#8-staffing-impact)
9. [Required Changes](#9-required-changes)
10. [Implementation Sequence](#10-implementation-sequence)

---

## 1. Problem Statement

### Current Limitations

The Agentic Code Migrator currently operates as a single-threaded pipeline:

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

## 7. Friction Points and Mitigations

### 7.1 Git Merge Conflicts

**Risk**: Multiple pods writing to the same files.

**Mitigation by design**: Pod partitioning assigns distinct workpackages to each pod. Output paths are namespaced by workpackage ID (`WP-001/`, `WP-002/`), so pods write to different directories. Conflicts are structurally impossible for workpackage-scoped outputs.

**Remaining conflict surfaces and solutions**:

| Shared Artifact | Solution |
|----------------|----------|
| Business glossary (`business-glossary.md`) | Each pod maintains pod-scoped additions (`business-glossary-pod-a.md`). Consolidation step merges them at pod→main merge time. |
| Progress tracking / status JSONs | Pod-scoped status files (`Business_Specification_Status-pod-a.json`). Dashboard reads all of them. |
| Shared domain models | Phase 2.5 partitioning groups workpackages that share entities into the same pod. Cross-pod entity sharing is flagged in `cross_pod_dependencies`. |

A conflict resolution prompt exists as a fallback but should be an exception handler, not a regular part of the flow.

### 7.2 Concurrent Git Operations

**On same machine (worktrees)**: `git worktree` provides separate working directories sharing the same `.git` object store. No concurrent git operation conflicts — each worktree is independent.

**On separate machines**: Each instance has its own clone. Push/pull to shared remote. Standard Git concurrency model applies — no issues as long as pods push to different branches (which they do by design).

### 7.3 Large Repositories

**Legacy input codebase**: Read-only for all pods, never changes after Phase 1. Options:
- If in same repo: committed to `main` before branching, every worktree/clone already has it
- If very large (millions of LOC): keep outside git as a read-only shared mount, referenced via `SOURCE_CODE` path
- Shallow clone (`--depth 1`) if legacy source is in a separate repo

**Generated outputs**: Much smaller than legacy input. Repo size is not a concern on the output side.

### 7.4 Final Merge to Main

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

## 8. Staffing Impact

### 8.1 Why Pods Reduce Headcount

The current framework already automates the specialist→reviewer iteration loop (AI reviews AI). Quality gates have automated confidence thresholds (drift detection at <5% and <10%). Human intervention is exception-based, not checkpoint-based.

With pods, the parallelism multiplier means the same amount of work completes in a fraction of the time, and the AI-driven review loops handle the volume that would otherwise require proportionally more humans.

### 8.2 Estimated Staffing Model

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

## 9. Required Changes

### 9.1 New Files to Create

| File | Purpose |
|------|---------|
| `structure/prompts/02_workpackage/02_pod_partitioning.md` | Phase 2.5 pod partitioning prompt — reads DAG, clusters by domain + dependency, outputs pod assignments |
| `structure/templates/Pod_Assignment.json` | Template for pod assignment output |
| `structure/templates/Pod_Merge_Validation.md` | Template for merge validation task file used by `deployment_reviewer_orchestration` |
| `create_pod_worktrees.py` | Script that reads pod assignment JSON and creates Git branches + worktrees |
| `consolidate_pod_artifacts.py` | Script that merges pod-scoped glossaries, status files, and progress tracking at merge time |

### 9.2 Files to Modify

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
| **`structure/prompts/03-business_extraction/01_business_specification_master-orchestration.md`** | Update `WORKPACKAGE_LOOP` to support pod-scoped execution. Add pod-scoped glossary pattern. Add git commit after deliverable approval. |
| **`structure/web-dashboard/`** | Update dashboard to read from multiple worktrees/branches for cross-pod visibility. |

### 9.3 Git Workflow Additions to Agent Prompts

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

## 10. Implementation Sequence

### Phase 1: Foundation (Relative Paths)
1. Update `config/paths.cfg` — all paths relative
2. Update `create_project.py` — stop absolute resolution
3. Update documentation (orchestration architecture, task file template)
4. Update all agent supervisor prompts — "relative to repo root"
5. Test: create a project, verify all agents work with relative paths

### Phase 2: Pod Partitioning
6. Create Phase 2.5 prompt (`02_pod_partitioning.md`)
7. Create pod assignment template (`Pod_Assignment.json`)
8. Update Migration Supervisor prompt — add Phase 2.5 delegation
9. Update `ReImagine_Main_Prompt.md` — add Phase 2.5 section
10. Test: run Phase 2.5 on existing workpackage output, verify clustering

### Phase 3: Git Branching
11. Create `create_pod_worktrees.py` script
12. Create `consolidate_pod_artifacts.py` script
13. Add git operations to team supervisor prompts
14. Create merge validation task template
15. Test: create branches, run one pod end-to-end, merge to main

### Phase 4: Multi-Pod Execution
16. Update business orchestration for pod-scoped execution
17. Update dashboard for multi-branch visibility
18. Test: run 2-3 pods in parallel on worktrees
19. Test: run pods on separate machines with shared Git remote
20. Validate merge flow and cross-pod integration

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
| Git branches as artifact layer | File-system based (matches existing framework), provides audit trail, enables PRs as quality gates, supports multi-machine execution. |
| Relative paths over late-binding | Simpler, no runtime resolution step, "relative to repo root" is a universal convention. |
| Pod-scoped glossaries over shared writes | Eliminates merge conflicts on shared files. Consolidation at merge time is clean and deterministic. |
| Worktrees for small scale, separate instances for large | Worktrees share object store (efficient), separate instances provide resource isolation (scalable). |
| Phase 2.5 uses domain affinity clustering | Minimizes cross-pod dependencies and merge conflicts by keeping related workpackages together. |
