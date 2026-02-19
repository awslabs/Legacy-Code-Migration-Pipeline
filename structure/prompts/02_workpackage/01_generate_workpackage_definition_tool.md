# Phase 2: Workpackage Definition and Prioritization

---

## Orchestration Information

**Phase**: Phase 2 - Migration Wave Planning
**Step**: Step 2.1 - Workpackage Definition
**Team Supervisor**: planning_team_supervisor
**Assigned Agent**: planning_specialist_workpackage
**Task File Name**: {{TASKS_BASE_PATH}}/workpackage_planning_specialist_task.md

### Expected Deliverables

1. **Workpackage Planning File**
   - File: {{WORKPACKAGE_PLANNING}}
   - Template: {{WORKPACKAGE_PLANNING_TEMPLATE}}
   - Description: Priority scores, workpackage assignments, phase groupings, and migration sequence

2. **Migration Roadmap**
   - File: {{WORKPACKAGE_ROADMAP}}
   - Template: {{WORKPACKAGE_ROADMAP_TEMPLATE}}
   - Description: Comprehensive migration roadmap with phase-by-phase breakdown and dependency visualization

3. **Workpackage Prioritization Tool**
   - File: {{WORKPACKAGE_ANALYZER_TOOL}}
   - Description: Python tool that reads Business_Flows.json and Module_Classifications.json to calculate priorities and generate planning outputs

4. **Progress Tracking**
   - File: {{WORKPACKAGE_STATUS}}
   - Template: {{ANALYSIS_STATUS_TEMPLATE}}
   - Description: Workpackage planning progress and status tracking

### Success Criteria
- [ ] All flows from Phase 1 assigned to workpackages
- [ ] Priority scores calculated correctly using specified formula
- [ ] Dependencies between workpackages identified and validated
- [ ] Migration roadmap created with phase-by-phase breakdown
- [ ] All deliverables produced at specified paths
- [ ] Quality criteria met
- [ ] Ready for review

---

## For Team Supervisor: Task File Creation

When creating the task file for this step:

### 1. Extract from this prompt:
- **Objective section**: The goal of prioritizing business flows and creating workpackages
- **Detailed instructions**: All Steps 1-7 below
- **Technical specifications**: Priority score formula, phase assignment algorithm, dependency validation
- **Business rules and constraints**: Priority calculation rules, pre-existent module tracking, DAG validation
- **Error handling guidance**: Missing flow data, circular dependencies, inconsistent module references
- **Output format requirements**: All primary outputs and their specifications
- **Quality criteria**: Completeness, accuracy, consistency requirements

### 2. Add project context:
- **Project name**: {{PROJECT_NAME}}
- **Project base path**: {{PROJECT_BASE_PATH}}
- **All input locations** (resolved paths):
  - Module classifications: {{MODULE_CLASSIFICATIONS}}
  - Phase 1 analysis outputs: {{ANALYSIS_OUTPUT}}
- **All output locations** (resolved paths):
  - Migration roadmap: {{WORKPACKAGE_ROADMAP}}
  - Workpackage analyzer tool: {{WORKPACKAGE_ANALYZER_TOOL}}
  - Progress tracking: {{WORKPACKAGE_STATUS}}
  - Error reporting: {{ANALYSIS_ERRORS}}
  - Task files location: {{TASKS_BASE_PATH}}
- **All template locations** (resolved paths):
  - Migration roadmap template: {{WORKPACKAGE_ROADMAP_TEMPLATE}}
  - Analysis status template: {{ANALYSIS_STATUS_TEMPLATE}}
  - Analysis errors template: {{ANALYSIS_ERRORS_TEMPLATE}}

### 3. Reference agent definition:
- **Agent name**: planning_specialist_workpackage
- **Agent definition file**: structure/agents/planning_team/planning_specialist_workpackage.md
- **Note**: Don't duplicate agent definition, just reference it

### 4. Task file structure:
Use the standard task file template with these sections:
- **Agent Assignment**: Agent name, task ID, created by, timestamp, phase, step
- **Project Context**: Project info, input locations, output locations, reference data
- **Task Instructions**: Objective, detailed steps (1-7), business rules, error handling
- **Expected Deliverables**: All 4 deliverables with paths, templates, descriptions, validation checklists
- **Quality Criteria**: Completeness, accuracy, consistency (from this prompt)
- **Success Criteria**: Task completion verification steps

### 5. Path resolution:
Ensure all {{PARAMETERS}} are replaced with actual absolute paths before creating the task file.

---

## For Team Supervisor: Dependencies Verification

Before creating the task file, verify that all Phase 1 outputs are available:

**Required Phase 1 Deliverables:**
- [ ] Module_Classifications.json exists at {{MODULE_CLASSIFICATIONS}}
- [ ] Phase 1 analysis completed and approved

If any dependencies are missing, coordinate with analysis_team_supervisor before proceeding.

---

## Context

### Project Information
**Project Name**: {{PROJECT_NAME}}
**Project Base Path**: {{PROJECT_BASE_PATH}}

### Input Locations
  - Description: Business flows identified in Phase 1 with complexity metrics
  - Format: JSON (Business_Flows.json)
- Module classifications: {{MODULE_CLASSIFICATIONS}}
  - Description: Module classifications from Phase 1 (COMMONLY_USED, etc.)
  - Format: JSON (Module_Classifications.json)

### Output Locations
  - Description: All flow data plus workpackage fields
  - Format: JSON (Workpackage_Dependencies.json)
- Migration roadmap: {{WORKPACKAGE_ROADMAP}}
  - Template: {{WORKPACKAGE_ROADMAP_TEMPLATE}}
  - Description: Comprehensive migration roadmap document
  - Format: Markdown
- Workpackage analyzer tool: {{WORKPACKAGE_ANALYZER_TOOL}}
  - Description: Python tool for workpackage prioritization
  - Format: Python script
- Progress Tracking: {{WORKPACKAGE_STATUS}}
  - Template: {{ANALYSIS_STATUS_TEMPLATE}}
  - Description: Status tracking for workpackage planning
  - Format: JSON

### Dependencies from Phase 1
- Module classifications: {{MODULE_CLASSIFICATIONS}}
- Source code analysis reports: {{ANALYSIS_OUTPUT}} 

## Objective
Prioritize business flows for migration based on complexity, dependencies, and business value. Create Workpackage_Planning.json that contains priority scores, workpackage assignments, phase groupings, and migration sequence. Business_Flows.json remains unchanged as the source of truth for flow analysis. Generate a comprehensive migration roadmap that minimizes risk by prioritizing flows with the least complexity and fewest dependencies on commonly used modules.

## Instructions

### Step 1: Load and Validate Input Data
1. Load the Business_Flows.json file from Phase 1
2. Load the Module_Classifications.json file from Phase 1
3. Validate that all flows have required complexity metrics
4. Validate that all module references are consistent
5. Prepare to create Workpackage_Planning.json output (do NOT copy flow data)

### Step 2: Calculate Priority Scores
For each flow, calculate a priority score using the following formula:

**Priority Score Formula** (lower = higher priority):
```
Priority = (TotalPrograms × 2) + (CommonModules × 3) + (CompositeScore × 0.5) + CompleteFlowBonus + SimpleFlowBonus
```

Where:
- **TotalPrograms**: From `complexity.totalPrograms`
- **CommonModules**: Count of programs in `scope.programs` that are classified as "COMMONLY_USED" in Module_Classifications.json
- **CompositeScore**: From `complexity.compositeScore`
- **CompleteFlowBonus**: -5 points if flow has database operations (complete flow from entry to data)
- **SimpleFlowBonus**: -3 points if totalPrograms ≤ 3, -1 point if totalPrograms ≤ 5

Add `workpackage.priorityScore` field to each flow with the calculated value.

### Step 3: Sort and Assign Workpackage IDs
1. Sort flows by priority score (lowest to highest)
2. Assign sequential workpackage IDs starting from 1
3. Add `workpackage.workpackageId` field to each flow

### Step 4: Calculate Pre-existent Modules
For each flow (in priority order):
1. Identify which programs in `scope.programs` were already included in higher priority flows
2. Add `workpackage.preExistentModules` array with these program names
3. This helps identify module reuse across workpackages

### Step 5: Identify Flow Dependencies
For each flow:
1. Check if any programs in `scope.programs` are entry points for other flows
2. Add to `dependencies.dependentFlows` with flowIds of flows that depend on this flow's modules
3. Validate that dependencies form a directed acyclic graph (DAG)
4. Flag any circular dependencies for manual review

### Step 6: Assign Migration Phases
1. Create phases based on dependency relationships
2. Phase 1: Flows with no dependencies on other flows
3. Phase N: Flows that depend only on flows in phases 1 through N-1
4. Add `workpackage.phase` field to each flow
5. Ensure all flows are assigned to a phase
6. Create the `phases` array with phase metadata

### Step 7: Generate Migration Roadmap
Create a comprehensive migration roadmap document that includes:
1. Executive summary of migration approach
2. Phase-by-phase breakdown with flow lists
3. Dependency visualization (textual representation)
4. Risk assessment for each phase
5. Recommended execution order within each phase

## Output Format

### Primary Outputs

#### 1. Workpackage Planning File
**File**: `{{WORKPACKAGE_PLANNING}}`
**Template**: `{{WORKPACKAGE_PLANNING_TEMPLATE}}`
- Contains priority scores, workpackage IDs, phase assignments, and migration sequence
- References flows by flowId (data remains in Business_Flows.json)
- Business_Flows.json remains unchanged (Phase 1 output preserved)
- New file for Phase 2 with prioritization and planning metadata only

#### 2. Migration Roadmap
**File**: `{{WORKPACKAGE_ROADMAP}}`
**Template**: `{{WORKPACKAGE_ROADMAP_TEMPLATE}}`

#### 3. Workpackage Prioritization Tool
**File**: `{{WORKPACKAGE_ANALYZER_TOOL}}`
- Python tool that performs workpackage prioritization
- Reads Business_Flows.json and Module_Classifications.json
- Calculates priorities and creates Workpackage_Planning.json
- Generates all required output formats
- Include comprehensive error handling and logging

#### 4. Progress Tracking
**File**: `{{WORKPACKAGE_STATUS}}`
**Template**: `{{ANALYSIS_STATUS_TEMPLATE}}`

## Quality Criteria

### Completeness
- [ ] All flows from Phase 1 must be assigned to workpackages
- [ ] All modules must be accounted for in the workpackage definitions
- [ ] All dependencies between workpackages must be identified
- [ ] The migration roadmap must include all workpackages
- [ ] All required output files must be generated

### Accuracy
- [ ] Priority scores must be calculated correctly using the specified formula
- [ ] Pre-existent module counts must be accurate for each workpackage
- [ ] Dependency relationships between workpackages must be valid
- [ ] Phase assignments must respect all dependencies
- [ ] All calculations and data transformations must be correct

### Consistency
- [ ] All output formats must match specified schemas
- [ ] Naming conventions must be followed consistently
- [ ] All required fields must be populated
- [ ] Cross-references between outputs must be accurate
- [ ] Terminology and formatting must be consistent throughout

## Error Handling

### Common Error Scenarios

#### 1. **Missing Flow Data**
- Detection: Flow referenced in Phase 1 not found in input data
- Recovery: Log error, continue with available flows
- Escalation: If >10% of flows are missing, request human intervention

#### 2. **Circular Dependencies**
- Detection: Circular references between workpackages
- Recovery: Break circular dependencies by adjusting priorities
- Escalation: Document complex circular dependencies for manual review

#### 3. **Inconsistent Module References**
- Detection: Module referenced in flow not found in module list
- Recovery: Log inconsistency, continue with available data
- Escalation: Flag for manual review if critical modules are affected

#### 4. **Priority Calculation Errors**
- Detection: Invalid input data for priority formula
- Recovery: Use default values for missing metrics, document assumption
- Escalation: Flag workpackages with estimated priorities for review

### Error Reporting Format
**File**: `{{ANALYSIS_ERRORS}}`
**Template for the file**: `{{ANALYSIS_ERRORS_TEMPLATE}}`

### Fallback Strategies
- **Simplified Prioritization**: If complex formula fails, use simpler module count-based prioritization
- **Partial Processing**: Continue with successfully analyzed flows
- **Manual Intervention**: Provide clear documentation for human review
- **Alternative Approaches**: Use different dependency resolution strategies for problematic cases

## Success Validation

### Deliverable Verification
- [ ] Verify all output files are created with valid content
- [ ] Validate JSON outputs against specified schemas
- [ ] Confirm all flows are assigned to workpackages
- [ ] Verify workpackage dependencies form a valid directed acyclic graph
- [ ] Check that the migration roadmap includes all workpackages in a valid sequence

### Quality Verification
- [ ] All quality criteria met (completeness, accuracy, consistency)
- [ ] All priority scores calculated correctly
- [ ] All dependencies validated
- [ ] No circular dependencies detected
- [ ] All error scenarios handled appropriately

### Readiness for Next Phase
- [ ] All deliverables exist at specified paths
- [ ] All files have valid content (file size > 0)
- [ ] Progress tracking updated
- [ ] Ready for review by planning_reviewer_workpackage
- [ ] Ready to proceed to Phase 3 (Business Specification) upon approval