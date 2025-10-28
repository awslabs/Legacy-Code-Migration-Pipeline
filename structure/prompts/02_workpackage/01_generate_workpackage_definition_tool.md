# Phase 2: Workpackage Definition

## Context
- Input Location
-- Dependency graphs and module classifications: `{{SOURCE_CODE_ANALYSIS_DEPENDENCY_TABLE}}` 
-- Extracted business flows: `{{SOURCE_CODE_ANALYSIS_BUSINESS_FLOW}}`

- Output Location
-- Prioritized migration roadmap: `{{PROJECT_BASE_PATH}}/output/migration/workpackage_definition/` 
-- Progress Tracking: `{{PROJECT_BASE_PATH}}/output/migration/progress/02-workpackage-status.json` 

## Objective
Define and prioritize migration workpackages based on complexity analysis of end-to-end flows. Create a comprehensive migration roadmap that minimizes risk by prioritizing flows with the least complexity and fewest dependencies on commonly used modules.

## Instructions

### Step 1: Flow Complexity Analysis
1. Load the end-to-end flow data from Phase 1 analysis
2. For each flow, calculate complexity metrics:
   - **Module Count**: Total number of modules in the flow
   - **Common Module Count**: Number of commonly used modules in the flow
   - **Complexity Score**: Sum of individual module complexity scores
   - **Pre-existent Count**: Number of modules already included in higher priority workpackages
   - **Flow Type**: Complete (entry point to database) or partial

### Step 2: Flow Prioritization
Calculate priority scores for each flow using the following formula:

**Priority Score Formula** (lower = higher priority):
```
Priority = (Modules × 2) + (Common Modules × 3) + (Complexity × 0.5) + (Pre-existent × 1) + Complete Flow Bonus (-5) + Simple Flow Bonus (-3 for ≤3 modules, -1 for ≤5 modules)
```

Where:
- **Modules**: Total number of modules in the flow
- **Common Modules**: Number of modules used by multiple flows
- **Complexity**: Sum of complexity scores for all modules in the flow
- **Pre-existent**: Number of modules already included in higher priority workpackages
- **Complete Flow Bonus**: -5 points for flows that are complete (entry point to database)
- **Simple Flow Bonus**: -3 points for flows with ≤3 modules, -1 point for flows with ≤5 modules

### Step 3: Workpackage Definition
1. Sort flows by priority score (lowest to highest)
2. For each flow, create a workpackage that includes:
   - The flow's entry point module
   - All dependent modules in the flow
   - Clear identification of pre-existent modules (already in previous workpackages)
3. Ensure each workpackage contains exactly one end-to-end flow
4. Update pre-existent module counts for remaining flows after each workpackage is defined

### Step 4: Dependency Resolution
1. Identify dependencies between workpackages
2. Create a directed acyclic graph (DAG) of workpackage dependencies
3. Validate that the workpackage order respects all dependencies
4. Adjust priorities if necessary to resolve circular dependencies

### Step 5: Migration Roadmap Creation
1. Organize workpackages into migration phases based on dependencies
2. Create a visual representation of the migration roadmap
3. Document rationale for workpackage priorities and phase assignments
4. Ensure all flows from Phase 1 are included in the roadmap

### Step 6: Workpackage Analysis Tool Development
1. Create a Python tool that automates the workpackage definition process
2. Implement the priority formula and sorting algorithm
3. Generate all required output formats
4. Include validation to ensure all flows are accounted for

## Output Format

### Primary Outputs

#### 1. Workpackage Definition Report
**File**: `{{WORKPACKAGE_REPORT}}`
**Template for the file**: `{{WORKPACKAGE_REPORT_TEMPLATE}}`

#### 2. Workpackage Analysis Table
**File**: `{{WORKPACKAGE_ANALYSIS_TABLE}}`
**Template for the file**: `{{WORKPACKAGE_ANALYSIS_TABLE_TEMPLATE}}`

Where:
- **Workpackage**: Sequential workpackage number
- **Flow_ID**: Identifier from Phase 1 analysis
- **Flow_Type**: Batch|Online|Both
- **Flow_Path**: Comma-separated list of modules in the flow
- **Priority_Score**: Calculated priority score
- **Pre_Existent_Modules**: Comma-separated list of modules already in previous workpackages
- **Business_Domain**: Primary business domain for the flow
- **Complexity**: Overall complexity score

#### 3. Workpackage Dependencies
**File**: `{{WORKPACKAGE_ANALYSIS_DEPENDENCIES}}`
**Template for the file**: `{{WORKPACKAGE_ANALYSIS_DEPENDENCIES_TEMPLATE}}`


#### 4. Migration Roadmap
**File**: `{{WORKPACKAGE_ROADMAP}}`
**Template for the file**: `{{WORKPACKAGE_ROADMAP_TEMPLATE}}`


#### 5. Workpackage Analysis Tool
**File**: `{{WORKPACKAGE_ANALYZER_TOOL}}`
- Python tool that performs workpackage definition and prioritization
- Should be reusable for similar migration projects
- Include comprehensive error handling and logging

#### 6. Progress Tracking
**File**: `{{WORKPACKAGE_PROGRESS}}`
**Template for the file**: `{{WORKPACKAGE_PROGRESS}}`


## Quality Criteria

### Completeness
- All flows from Phase 1 must be assigned to workpackages
- All modules must be accounted for in the workpackage definitions
- All dependencies between workpackages must be identified
- The migration roadmap must include all workpackages

### Accuracy
- Priority scores must be calculated correctly using the specified formula
- Pre-existent module counts must be accurate for each workpackage
- Dependency relationships between workpackages must be valid
- Phase assignments must respect all dependencies

### Consistency
- All output formats must match specified schemas
- Naming conventions must be followed consistently
- All required fields must be populated
- Cross-references between outputs must be accurate

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
**File**: `{{SOURCE_CODE_ANALYSIS_ERRORS}}`
**Template for the file**: `{{SOURCE_CODE_ANALYSIS_ERRORS_TEMPLATE}}`


### Fallback Strategies
- **Simplified Prioritization**: If complex formula fails, use simpler module count-based prioritization
- **Partial Processing**: Continue with successfully analyzed flows
- **Manual Intervention**: Provide clear documentation for human review
- **Alternative Approaches**: Use different dependency resolution strategies for problematic cases

## Success Validation
- Verify all output files are created with valid content
- Validate JSON outputs against specified schemas
- Ensure CSV files have proper headers and data formatting
- Confirm all flows are assigned to workpackages
- Verify workpackage dependencies form a valid directed acyclic graph
- Check that the migration roadmap includes all workpackages in a valid sequence