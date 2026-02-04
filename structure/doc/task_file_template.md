# Task File Template Documentation

## Document Control
- **Version:** 1.0
- **Date:** 2024-01-15
- **Purpose:** Comprehensive guide for creating task files in the orchestration architecture
- **Audience:** Team Supervisor agents, framework developers

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Task File Structure](#2-task-file-structure)
3. [Field-by-Field Explanation](#3-field-by-field-explanation)
4. [Path Resolution Guidelines](#4-path-resolution-guidelines)
5. [Examples by Agent Type](#5-examples-by-agent-type)
6. [Validation Checklist](#6-validation-checklist)
7. [Common Mistakes and Solutions](#7-common-mistakes-and-solutions)
8. [Troubleshooting Guide](#8-troubleshooting-guide)

---

## 1. Introduction

### 1.1 What is a Task File?

A task file is a runtime-generated document that combines:
- **Generic agent definition** (role, capabilities, responsibilities)
- **Project-specific context** (paths, project name, configuration)
- **Specific instructions** (what to do for this particular task)
- **Expected deliverables** (what to produce and where)
- **Quality criteria** (how to validate success)

Task files are created by **Team Supervisor agents** and given to **Specialist/Reviewer agents** for execution.

### 1.2 Why Task Files?

**Problem:** Agent definitions are generic and reusable across projects. They don't contain project-specific paths or instructions.

**Solution:** Task files bridge the gap by providing project-specific context at runtime without modifying the generic agent definitions.

**Benefits:**
- Agents remain generic and reusable
- Project-specific information provided at runtime
- Clear separation of concerns
- Dynamic task creation based on phase requirements
- Complete context for agent execution

### 1.3 Task File Lifecycle

```
Phase Prompt (with {{PARAMETERS}})
    ↓
Team Supervisor reads phase prompt
    ↓
Team Supervisor extracts relevant instructions
    ↓
Team Supervisor resolves all paths
    ↓
Team Supervisor creates task file
    ↓
Team Supervisor saves to {{TASKS_BASE_PATH}}
    ↓
Team Supervisor delegates to Specialist/Reviewer
    ↓
Agent reads task file and executes work
```


---

## 2. Task File Structure

### 2.1 Complete Template

```markdown
# Task: [Task Name]

## Agent Assignment
**Agent**: [agent_name]
**Agent Definition**: [path to agent definition file or reference]
**Task ID**: [unique_id]
**Created By**: [supervisor_agent_name]
**Created At**: [timestamp]
**Phase**: [phase_name]
**Step**: [step_name]

---

## Project Context

### Project Information
**Project Name**: [project_name]
**Project Base Path**: [absolute_path]

### Input Locations
- **[Input Name]**: [absolute_path]
  - Description: [what it contains]
  - Format: [file format]
- **[Input Name]**: [absolute_path]
  - Description: [what it contains]
  - Format: [file format]

### Output Locations
- **[Output Name]**: [absolute_path]
  - Template: [template_path]
  - Description: [what to produce]
  - Format: [file format]
- **[Output Name]**: [absolute_path]
  - Template: [template_path]
  - Description: [what to produce]
  - Format: [file format]

### Reference Data
- **[Reference Name]**: [absolute_path]
- **[Reference Name]**: [absolute_path]

---

## Task Instructions

### Objective
[Clear statement of what this task accomplishes]

### Detailed Steps

#### Step 1: [Step Name]
[Specific instructions extracted from phase prompt]

**Actions:**
1. [Action 1]
2. [Action 2]
3. [Action 3]

**Technical Specifications:**
- [Spec 1]
- [Spec 2]

#### Step 2: [Step Name]
[Continue with additional steps...]

### Business Rules and Constraints
[Any business rules specific to this task]
- Rule 1: [description]
- Rule 2: [description]

### Error Handling
[Task-specific error scenarios]
- **Scenario 1**: [description]
  - Detection: [how to detect]
  - Recovery: [what to do]
- **Scenario 2**: [description]
  - Detection: [how to detect]
  - Recovery: [what to do]

---

## Expected Deliverables

### 1. [Deliverable Name]
**File**: [absolute_path]
**Template**: [template_path]
**Description**: [What it contains]
**Format**: [File format and structure]

**Content Requirements:**
- Requirement 1
- Requirement 2
- Requirement 3

**Validation:**
- [ ] File exists at specified path
- [ ] File format matches template
- [ ] All required sections present
- [ ] All required fields populated

### 2. [Deliverable Name]
[Repeat structure for each deliverable...]

---

## Quality Criteria

### Completeness
- [ ] All required deliverables produced
- [ ] All required sections/fields populated
- [ ] All inputs processed
- [ ] No missing data or placeholders

### Accuracy
- [ ] Data correctly extracted/transformed
- [ ] Calculations correct
- [ ] References valid
- [ ] Cross-references consistent

### Consistency
- [ ] Naming conventions followed
- [ ] Format matches templates
- [ ] Style consistent throughout
- [ ] Terminology consistent

### Compliance
- [ ] Follows technical specifications
- [ ] Adheres to business rules
- [ ] Meets error handling requirements
- [ ] Satisfies all constraints

---

## Success Criteria

**Task is complete when:**
- [ ] All deliverables produced at specified paths
- [ ] All quality criteria met
- [ ] All validation checks pass
- [ ] No blocking errors remain
- [ ] Ready for review (if applicable)

**Verification Steps:**
1. Check all output files exist
2. Validate file formats
3. Verify content completeness
4. Confirm quality criteria
5. Report completion to supervisor

---

## Notes

### Agent Definition Reference
Your complete role definition and capabilities are in your agent definition file.
This task file provides project-specific context and instructions.

### Escalation
If you encounter issues beyond your capability:
1. Document the issue clearly
2. Report to [supervisor_name]
3. Provide context and attempted solutions

### Additional Resources
[Any additional documentation or resources]
- Resource 1: [path]
- Resource 2: [path]
```

### 2.2 Section Overview

| Section | Purpose | Created By | Source |
|---------|---------|------------|--------|
| Agent Assignment | Identifies agent and task metadata | Supervisor | Supervisor's tracking |
| Project Context | Provides all paths and project info | Supervisor | Phase prompt + paths.cfg |
| Task Instructions | Specific work to perform | Supervisor | Extracted from phase prompt |
| Expected Deliverables | What to produce and where | Supervisor | Phase prompt deliverables |
| Quality Criteria | How to validate quality | Supervisor | Phase prompt quality section |
| Success Criteria | When task is complete | Supervisor | Phase prompt success section |
| Notes | Additional guidance | Supervisor | Context-specific |


---

## 3. Field-by-Field Explanation

### 3.1 Agent Assignment Section

#### **Agent**
- **Type:** String
- **Required:** Yes
- **Format:** Agent name matching agent definition file
- **Example:** `analysis_specialist_legacy_code`
- **Purpose:** Identifies which agent should execute this task
- **Source:** Phase prompt specifies assigned agent for each step

#### **Agent Definition**
- **Type:** String (path or reference)
- **Required:** Yes
- **Format:** Path to agent definition file or reference identifier
- **Example:** `/system/agents/analysis_team/analysis_specialist_legacy_code.md`
- **Purpose:** Points to the agent's complete role definition
- **Note:** Reference only, don't duplicate the agent definition content

#### **Task ID**
- **Type:** String
- **Required:** Yes
- **Format:** `[phase]-[number]` or `[phase]_[step]_[iteration]`
- **Example:** `analysis-001`, `analysis_sourcecode_1`
- **Purpose:** Unique identifier for tracking and auditing
- **Source:** Generated by supervisor (sequential or descriptive)

#### **Created By**
- **Type:** String
- **Required:** Yes
- **Format:** Supervisor agent name
- **Example:** `analysis_team_supervisor`
- **Purpose:** Tracks which supervisor created this task
- **Source:** Supervisor's own identity

#### **Created At**
- **Type:** String (ISO 8601 timestamp)
- **Required:** Yes
- **Format:** `YYYY-MM-DDTHH:MM:SSZ`
- **Example:** `2024-01-15T10:30:00Z`
- **Purpose:** Tracks when task was created for auditing
- **Source:** Current timestamp when supervisor creates task

#### **Phase**
- **Type:** String
- **Required:** Yes
- **Format:** Phase name or identifier
- **Example:** `analysis`, `workpackage`, `business_extraction`
- **Purpose:** Identifies which migration phase this task belongs to
- **Source:** Phase prompt header

#### **Step**
- **Type:** String
- **Required:** Yes
- **Format:** Step name or identifier
- **Example:** `sourcecode`, `database`, `review`
- **Purpose:** Identifies which step within the phase
- **Source:** Phase prompt step identifier

### 3.2 Project Context Section

#### **Project Name**
- **Type:** String
- **Required:** Yes
- **Format:** Project identifier
- **Example:** `MyMigration`, `LegacyApp2024`
- **Purpose:** Identifies the project for context
- **Source:** `{{PROJECT_NAME}}` from phase prompt

#### **Project Base Path**
- **Type:** String (absolute path)
- **Required:** Yes
- **Format:** Absolute filesystem path
- **Example:** `/home/user/projects/mymigration`
- **Purpose:** Root directory for all project files
- **Source:** `{{PROJECT_BASE_PATH}}` from phase prompt

#### **Input Locations**
- **Type:** List of path entries
- **Required:** Yes (at least one)
- **Format:** Each entry has name, path, description, format
- **Example:**
  ```markdown
  - **Legacy Source Code**: /project/input/legacy/source
    - Description: COBOL source files (.cbl, .cob)
    - Format: COBOL source code
  ```
- **Purpose:** Tells agent where to find input data
- **Source:** Extracted from phase prompt context section, paths resolved

#### **Output Locations**
- **Type:** List of path entries
- **Required:** Yes (at least one)
- **Format:** Each entry has name, path, template, description, format
- **Example:**
  ```markdown
  - **Analysis Report**: /project/output/analysis/cobol_analysis.md
    - Template: /project/templates/Cobol_Source_Analysis_Report.md
    - Description: Comprehensive analysis findings
    - Format: Markdown
  ```
- **Purpose:** Tells agent where to write output files
- **Source:** Extracted from phase prompt deliverables section, paths resolved

#### **Reference Data**
- **Type:** List of path entries
- **Required:** No (optional)
- **Format:** Name and path pairs
- **Example:**
  ```markdown
  - **Target Framework Docs**: /project/input/target/spring-boot-docs.pdf
  - **Migration Guidelines**: /project/input/guidance/migration-best-practices.md
  ```
- **Purpose:** Additional context or reference materials
- **Source:** Phase prompt context section if applicable

### 3.3 Task Instructions Section

#### **Objective**
- **Type:** String (paragraph)
- **Required:** Yes
- **Format:** Clear, concise statement of task goal
- **Example:** "Analyze COBOL legacy source code to understand structure, dependencies, and business flows."
- **Purpose:** Provides high-level understanding of task purpose
- **Source:** Extracted from phase prompt objective or step description

#### **Detailed Steps**
- **Type:** Structured list of steps with actions and specifications
- **Required:** Yes
- **Format:** Numbered steps, each with actions and technical specs
- **Example:**
  ```markdown
  #### Step 1: Source Code Discovery
  Scan all source files in /project/input/legacy/source
  
  **Actions:**
  1. Identify all files with extensions: .cbl, .cob
  2. Create inventory with metadata
  
  **Technical Specifications:**
  - Include files from database directory
  - Exclude system utilities
  ```
- **Purpose:** Provides step-by-step execution guidance
- **Source:** Extracted from phase prompt detailed instructions section

#### **Business Rules and Constraints**
- **Type:** List of rules
- **Required:** If applicable
- **Format:** Bullet list with descriptions
- **Example:**
  ```markdown
  - Rule 1: All monetary calculations must preserve precision to 2 decimal places
  - Rule 2: Date formats must be converted to ISO 8601
  ```
- **Purpose:** Ensures agent follows business requirements
- **Source:** Extracted from phase prompt business rules section

#### **Error Handling**
- **Type:** List of scenarios with detection and recovery
- **Required:** Yes
- **Format:** Scenario, detection method, recovery action
- **Example:**
  ```markdown
  - **Scenario 1**: Source file cannot be parsed
    - Detection: Parser throws syntax error
    - Recovery: Log error, mark file as unparseable, continue with next file
  ```
- **Purpose:** Guides agent on handling errors gracefully
- **Source:** Extracted from phase prompt error handling section

### 3.4 Expected Deliverables Section

#### **Deliverable Entry**
Each deliverable must include:

- **File**: Absolute path where deliverable should be created
- **Template**: Path to template file (if applicable)
- **Description**: What the deliverable contains
- **Format**: File format and structure
- **Content Requirements**: List of required content elements
- **Validation**: Checklist for verifying deliverable quality

**Example:**
```markdown
### 1. Source Code Analysis Report
**File**: /project/output/analysis/cobol_analysis.md
**Template**: /project/templates/Cobol_Source_Analysis_Report.md
**Description**: Comprehensive analysis methodology, findings, and recommendations
**Format**: Markdown document following template structure

**Content Requirements:**
- Analysis methodology section
- Findings summary with statistics
- Dependency analysis results
- Module classification results
- Recommendations for migration

**Validation:**
- [ ] File exists at specified path
- [ ] File format matches template structure
- [ ] All required sections present
- [ ] All findings documented with evidence
```

### 3.5 Quality Criteria Section

Quality criteria are organized into categories:

#### **Completeness**
- All required deliverables produced
- All required sections/fields populated
- All inputs processed
- No missing data or placeholders

#### **Accuracy**
- Data correctly extracted/transformed
- Calculations correct
- References valid
- Cross-references consistent

#### **Consistency**
- Naming conventions followed
- Format matches templates
- Style consistent throughout
- Terminology consistent

#### **Compliance**
- Follows technical specifications
- Adheres to business rules
- Meets error handling requirements
- Satisfies all constraints

**Format:** Checkbox list for each criterion
**Purpose:** Provides clear quality standards
**Source:** Extracted from phase prompt quality criteria section

### 3.6 Success Criteria Section

#### **Task is complete when:**
- **Type:** Checkbox list
- **Required:** Yes
- **Format:** Clear, verifiable conditions
- **Example:**
  ```markdown
  - [ ] All deliverables produced at specified paths
  - [ ] All quality criteria met
  - [ ] All validation checks pass
  - [ ] No blocking errors remain
  - [ ] Ready for review (if applicable)
  ```
- **Purpose:** Defines when agent can report completion
- **Source:** Extracted from phase prompt success criteria section

#### **Verification Steps:**
- **Type:** Numbered list
- **Required:** Yes
- **Format:** Sequential verification actions
- **Example:**
  ```markdown
  1. Check all output files exist
  2. Validate file formats
  3. Verify content completeness
  4. Confirm quality criteria
  5. Report completion to supervisor
  ```
- **Purpose:** Guides agent through final verification
- **Source:** Supervisor defines based on deliverables


---

## 4. Path Resolution Guidelines

### 4.1 Path Resolution Rules

**Rule 1: All Paths Must Be Absolute**
- Task files MUST contain absolute paths, not relative paths
- Agents should not need to resolve or construct paths
- Example: `/home/user/projects/mymigration/output/analysis/report.md`
- NOT: `../output/analysis/report.md`

**Rule 2: Paths Must Be Resolved from Parameters**
- Phase prompts contain `{{PARAMETER}}` placeholders
- Supervisor must resolve these to actual paths
- Example: `{{COBOL_SOURCE_ANALYSIS_REPORT}}` → `/project/output/analysis/cobol_analysis.md`

**Rule 3: Input Paths Must Exist**
- Verify input paths exist before creating task file
- If input doesn't exist, escalate to Migration Supervisor
- Don't create task file with invalid input paths

**Rule 4: Output Paths Must Be Creatable**
- Verify output directories exist or can be created
- Check write permissions
- Create directories if needed before delegating

**Rule 5: Template Paths Must Be Valid**
- Verify template files exist
- Provide absolute path to template
- Agent will use template as structure guide

### 4.2 Path Resolution Process

**Step 1: Read Phase Prompt**
```markdown
Input: {{LEGACY_SOURCE_CODE}}
Output: {{COBOL_SOURCE_ANALYSIS_REPORT}}
Template: {{TEMPLATES_BASE_PATH}}/Cobol_Source_Analysis_Report.md
```

**Step 2: Resolve Parameters**
- `{{LEGACY_SOURCE_CODE}}` → `/project/input/legacy/source`
- `{{COBOL_SOURCE_ANALYSIS_REPORT}}` → `/project/output/analysis/cobol_analysis.md`
- `{{TEMPLATES_BASE_PATH}}` → `/project/templates`

**Step 3: Construct Full Paths**
- Input: `/project/input/legacy/source`
- Output: `/project/output/analysis/cobol_analysis.md`
- Template: `/project/templates/Cobol_Source_Analysis_Report.md`

**Step 4: Verify Paths**
- Check input exists: `ls /project/input/legacy/source`
- Check output directory exists: `ls /project/output/analysis` (create if needed)
- Check template exists: `ls /project/templates/Cobol_Source_Analysis_Report.md`

**Step 5: Write to Task File**
```markdown
### Input Locations
- **Legacy Source Code**: /project/input/legacy/source
  - Description: COBOL source files
  - Format: COBOL

### Output Locations
- **Analysis Report**: /project/output/analysis/cobol_analysis.md
  - Template: /project/templates/Cobol_Source_Analysis_Report.md
  - Description: Analysis findings
  - Format: Markdown
```

### 4.3 Common Path Parameters

| Parameter | Typical Resolution | Description |
|-----------|-------------------|-------------|
| `{{PROJECT_BASE_PATH}}` | `/home/user/projects/myproject` | Project root directory |
| `{{TASKS_BASE_PATH}}` | `/home/user/projects/myproject/tasks` | Task files directory |
| `{{TEMPLATES_BASE_PATH}}` | `/home/user/projects/myproject/templates` | Template files directory |
| `{{LEGACY_SOURCE_CODE}}` | `/home/user/projects/myproject/input/legacy/source` | Legacy source code |
| `{{DATABASE_SOURCE_CODE}}` | `/home/user/projects/myproject/input/legacy/database` | Database DDL files |
| `{{ANALYSIS_OUTPUT}}` | `/home/user/projects/myproject/output/analysis` | Analysis outputs |
| `{{WORKPACKAGE_OUTPUT}}` | `/home/user/projects/myproject/output/workpackages` | Workpackage outputs |
| `{{GEN_SRC}}` | `/home/user/projects/myproject/output/generated/src` | Generated source code |

### 4.4 Path Validation Checklist

Before creating task file, verify:
- [ ] All input paths exist and are readable
- [ ] All output directories exist or can be created
- [ ] All output paths are writable
- [ ] All template paths exist and are readable
- [ ] All paths are absolute (start with `/` or drive letter)
- [ ] No `{{PARAMETERS}}` remain unresolved
- [ ] Paths are consistent with paths.cfg definitions


---

## 5. Examples by Agent Type

### 5.1 Specialist Agent Task File Example

**Scenario:** Analysis Team Supervisor creates task for Legacy Code Analyst

```markdown
# Task: Source Code Analysis

## Agent Assignment
**Agent**: analysis_specialist_legacy_code
**Agent Definition**: /system/agents/analysis_team/analysis_specialist_legacy_code.md
**Task ID**: analysis-sourcecode-001
**Created By**: analysis_team_supervisor
**Created At**: 2024-01-15T10:30:00Z
**Phase**: analysis
**Step**: sourcecode

---

## Project Context

### Project Information
**Project Name**: MyMigration
**Project Base Path**: /home/user/projects/mymigration

### Input Locations
- **Legacy Source Code**: /home/user/projects/mymigration/input/legacy/source
  - Description: COBOL source files (.cbl, .cob)
  - Format: COBOL source code
- **Legacy Database**: /home/user/projects/mymigration/input/legacy/database
  - Description: Database DDL files
  - Format: SQL DDL

### Output Locations
- **Analysis Report**: /home/user/projects/mymigration/output/analysis/source_code/reports/cobol_analysis.md
  - Template: /home/user/projects/mymigration/templates/Cobol_Source_Analysis_Report.md
  - Description: Comprehensive analysis findings
  - Format: Markdown
- **Dependency Table**: /home/user/projects/mymigration/output/analysis/source_code/reports/dependency_table.csv
  - Template: /home/user/projects/mymigration/templates/Dependency_Analysis_Table.csv
  - Description: Module dependency relationships
  - Format: CSV
- **Business Flows**: /home/user/projects/mymigration/output/analysis/source_code/progress/business_flows.json
  - Template: /home/user/projects/mymigration/templates/Business_Flows.json
  - Description: Identified business flows
  - Format: JSON

### Reference Data
- **Target Framework Docs**: /home/user/projects/mymigration/input/target/spring-boot-reference.pdf
- **Migration Guidelines**: /home/user/projects/mymigration/input/guidance/cobol-to-java-patterns.md

---

## Task Instructions

### Objective
Analyze COBOL legacy source code to understand structure, dependencies, and business flows for migration planning.

### Detailed Steps

#### Step 1: Source Code Discovery
Scan all source files in the legacy source directory.

**Actions:**
1. Identify all files with extensions: .cbl, .cob, .CBL, .COB
2. Create inventory with metadata (size, last modified, location)
3. Log any files that cannot be accessed or parsed

**Technical Specifications:**
- Include files from database directory for database-related code
- Exclude system utilities: DMBATCH, IDCAMS, IEBCOPY
- Handle both uppercase and lowercase extensions

#### Step 2: Dependency Analysis
Identify all dependencies between modules.

**Actions:**
1. Recognize COBOL call patterns: CALL, CICS LINK, CICS XCTL
2. Map file operations: JCL DD statements, COBOL SELECT
3. Identify database operations: SQL statements, table references
4. Build dependency graph

**Technical Specifications:**
- Mark missing dependencies as TargetFound=False
- Capture call type (static, dynamic, conditional)
- Track file I/O operations (READ, WRITE, REWRITE, DELETE)

#### Step 3: Module Classification
Classify each module by usage and functionality.

**Actions:**
1. Identify entry points (programs called from JCL or CICS)
2. Classify by business domain (based on naming, comments, logic)
3. Determine module type (batch, online, utility, common)
4. Assess complexity (lines of code, cyclomatic complexity)

**Technical Specifications:**
- Use naming conventions to infer business domain
- Analyze PROCEDURE DIVISION for complexity
- Identify reusable components

#### Step 4: Business Flow Identification
Extract business flows from code structure.

**Actions:**
1. Trace execution paths from entry points
2. Identify business transactions
3. Map data transformations
4. Document business rules embedded in code

**Technical Specifications:**
- Focus on main business logic, not technical infrastructure
- Capture conditional logic and decision points
- Note data validation rules

#### Step 5: Generate Analysis Report
Create comprehensive analysis report.

**Actions:**
1. Use template structure from Cobol_Source_Analysis_Report.md
2. Document methodology and approach
3. Summarize findings with statistics
4. Provide recommendations for migration

**Technical Specifications:**
- Follow markdown format
- Include code examples where relevant
- Provide quantitative metrics (module count, dependency count, etc.)

#### Step 6: Generate Dependency Table
Create CSV file with all dependencies.

**Actions:**
1. Use template structure from Dependency_Analysis_Table.csv
2. List all modules and their dependencies
3. Include metadata (call type, frequency if available)

**Technical Specifications:**
- CSV format with headers: SourceModule, TargetModule, CallType, TargetFound
- One row per dependency relationship
- Sort by SourceModule

#### Step 7: Generate Business Flows JSON
Create JSON file with identified business flows.

**Actions:**
1. Use template structure from Business_Flows.json
2. Document each business flow with entry point, steps, outputs
3. Include business rules and constraints

**Technical Specifications:**
- Valid JSON format
- Follow template schema
- Include flow ID, name, description, modules involved

### Business Rules and Constraints
- All monetary calculations must be noted for precision requirements
- Date format conversions must be documented
- Security-sensitive operations must be flagged
- Performance-critical sections must be identified

### Error Handling
- **Scenario 1**: Source file cannot be parsed
  - Detection: Parser throws syntax error
  - Recovery: Log error with file name and line number, mark file as unparseable, continue with next file
- **Scenario 2**: Missing dependency target
  - Detection: CALL target not found in source inventory
  - Recovery: Mark as TargetFound=False in dependency table, note in analysis report
- **Scenario 3**: Template file not found
  - Detection: Template path does not exist
  - Recovery: Escalate to supervisor, do not proceed without template

---

## Expected Deliverables

### 1. Source Code Analysis Report
**File**: /home/user/projects/mymigration/output/analysis/source_code/reports/cobol_analysis.md
**Template**: /home/user/projects/mymigration/templates/Cobol_Source_Analysis_Report.md
**Description**: Comprehensive analysis methodology, findings, and recommendations
**Format**: Markdown document following template structure

**Content Requirements:**
- Analysis methodology section
- Findings summary with statistics
- Dependency analysis results
- Module classification results
- Business flow identification
- Recommendations for migration
- Appendices with detailed data

**Validation:**
- [ ] File exists at specified path
- [ ] File format matches template structure
- [ ] All required sections present
- [ ] All findings documented with evidence
- [ ] Statistics are accurate and complete

### 2. Dependency Analysis Table
**File**: /home/user/projects/mymigration/output/analysis/source_code/reports/dependency_table.csv
**Template**: /home/user/projects/mymigration/templates/Dependency_Analysis_Table.csv
**Description**: Complete module dependency relationships
**Format**: CSV with headers

**Content Requirements:**
- All modules listed
- All dependencies captured
- Call types specified
- Target found status indicated

**Validation:**
- [ ] File exists at specified path
- [ ] CSV format with correct headers
- [ ] All modules accounted for
- [ ] No empty required fields

### 3. Business Flows JSON
**File**: /home/user/projects/mymigration/output/analysis/source_code/progress/business_flows.json
**Template**: /home/user/projects/mymigration/templates/Business_Flows.json
**Description**: Identified business flows with entry points and steps
**Format**: JSON following template schema

**Content Requirements:**
- All business flows identified
- Entry points documented
- Flow steps detailed
- Business rules captured

**Validation:**
- [ ] File exists at specified path
- [ ] Valid JSON format
- [ ] Follows template schema
- [ ] All flows have required fields

---

## Quality Criteria

### Completeness
- [ ] All COBOL source files analyzed
- [ ] All dependency relationships captured
- [ ] All entry points identified
- [ ] All business flows documented
- [ ] All deliverables produced

### Accuracy
- [ ] Module classifications consistent with code structure
- [ ] Dependency relationships verified through code inspection
- [ ] Business domain assignments logical and justified
- [ ] Statistics calculated correctly

### Consistency
- [ ] Output formats match templates exactly
- [ ] Naming conventions followed throughout
- [ ] All required fields populated
- [ ] Terminology consistent across deliverables

### Compliance
- [ ] Follows technical specifications in instructions
- [ ] Adheres to business rules
- [ ] Meets error handling requirements
- [ ] Template structures preserved

---

## Success Criteria

**Task is complete when:**
- [ ] All deliverables produced at specified paths
- [ ] All quality criteria met
- [ ] All validation checks pass
- [ ] No blocking errors remain
- [ ] Ready for review by analysis_reviewer_legacy_code

**Verification Steps:**
1. Check all three output files exist at specified paths
2. Validate file formats (markdown, CSV, JSON)
3. Verify content completeness against requirements
4. Confirm quality criteria met
5. Report completion to analysis_team_supervisor

---

## Notes

### Agent Definition Reference
Your complete role definition and capabilities are in:
/system/agents/analysis_team/analysis_specialist_legacy_code.md

This task file provides project-specific context and instructions.

### Escalation
If you encounter issues beyond your capability:
1. Document the issue clearly (what, when, where, why)
2. Report to analysis_team_supervisor
3. Provide context and attempted solutions
4. Do not proceed if blocking issue

### Additional Resources
- COBOL Language Reference: /home/user/projects/mymigration/input/guidance/cobol-reference.pdf
- Migration Best Practices: /home/user/projects/mymigration/input/guidance/migration-patterns.md
```


### 5.2 Reviewer Agent Task File Example

**Scenario:** Analysis Team Supervisor creates task for Legacy Code Reviewer

```markdown
# Task: Review Source Code Analysis Deliverables

## Agent Assignment
**Agent**: analysis_reviewer_legacy_code
**Agent Definition**: /system/agents/analysis_team/analysis_reviewer_legacy_code.md
**Task ID**: analysis-sourcecode-review-001
**Created By**: analysis_team_supervisor
**Created At**: 2024-01-15T14:30:00Z
**Phase**: analysis
**Step**: sourcecode_review
**Iteration**: 1

---

## Project Context

### Project Information
**Project Name**: MyMigration
**Project Base Path**: /home/user/projects/mymigration

### Deliverables to Review
- **Analysis Report**: /home/user/projects/mymigration/output/analysis/source_code/reports/cobol_analysis.md
  - Template: /home/user/projects/mymigration/templates/Cobol_Source_Analysis_Report.md
  - Created by: analysis_specialist_legacy_code
- **Dependency Table**: /home/user/projects/mymigration/output/analysis/source_code/reports/dependency_table.csv
  - Template: /home/user/projects/mymigration/templates/Dependency_Analysis_Table.csv
  - Created by: analysis_specialist_legacy_code
- **Business Flows**: /home/user/projects/mymigration/output/analysis/source_code/progress/business_flows.json
  - Template: /home/user/projects/mymigration/templates/Business_Flows.json
  - Created by: analysis_specialist_legacy_code

### Reference Data
- **Original Task File**: /home/user/projects/mymigration/tasks/analysis_sourcecode_specialist_task.md
- **Legacy Source Code**: /home/user/projects/mymigration/input/legacy/source

---

## Task Instructions

### Objective
Review all source code analysis deliverables to ensure completeness, accuracy, consistency, and compliance with quality criteria before proceeding to next phase.

### Review Methodology

#### Step 1: Deliverable Existence Check
Verify all expected deliverables exist at specified paths.

**Actions:**
1. Check Analysis Report exists and is readable
2. Check Dependency Table exists and is readable
3. Check Business Flows JSON exists and is readable
4. Verify file sizes are reasonable (not empty, not truncated)

#### Step 2: Format Validation
Verify each deliverable matches its template structure.

**Actions:**
1. Compare Analysis Report structure to template
2. Validate CSV format and headers in Dependency Table
3. Validate JSON format and schema in Business Flows
4. Check for parsing errors or format issues

#### Step 3: Completeness Review
Verify all required content is present.

**Actions:**
1. Check Analysis Report has all required sections
2. Verify all modules are listed in Dependency Table
3. Confirm all business flows are documented
4. Ensure no placeholder text or TODO items remain

#### Step 4: Accuracy Review
Verify content accuracy through sampling.

**Actions:**
1. Sample 10% of modules and verify dependency analysis
2. Cross-check statistics in report against raw data
3. Verify business flow descriptions match code structure
4. Check for logical inconsistencies

#### Step 5: Consistency Review
Verify consistency across deliverables.

**Actions:**
1. Check module names consistent across all deliverables
2. Verify terminology consistent throughout
3. Ensure naming conventions followed
4. Check cross-references are valid

#### Step 6: Compliance Review
Verify compliance with quality criteria.

**Actions:**
1. Check all quality criteria from original task file
2. Verify technical specifications followed
3. Confirm business rules addressed
4. Validate error handling was applied

### Review Outcome Options

#### Option 1: APPROVED
All quality criteria met, no blocking issues, ready to proceed.

**Required for Approval:**
- All deliverables exist and are complete
- All formats match templates
- All quality criteria met
- No blocking issues identified
- Minor issues (if any) documented but non-blocking

**Approval Message Format:**
```
REVIEW OUTCOME: APPROVED

All source code analysis deliverables meet quality criteria.

Summary:
- Analysis Report: Complete and accurate
- Dependency Table: All modules and dependencies captured
- Business Flows: All flows documented

Minor observations (non-blocking):
- [List any minor observations]

Ready to proceed to next phase.
```

#### Option 2: ISSUES FOUND
Quality criteria not met, issues require remediation.

**Issue Reporting Format:**
For each issue, provide:
- Issue ID (for tracking)
- Affected deliverable
- Severity (blocking, major, minor)
- Description (what is wrong)
- Evidence (specific examples)
- Remediation guidance (how to fix)
- Quality criterion violated

**Example Issue:**
```
Issue ID: REV-001
Affected Deliverable: Dependency Table
Severity: Blocking
Description: Missing dependencies for 15 modules
Evidence: Modules CUSTMGMT, ORDPROC, INVUPDT have no dependencies listed
Remediation Guidance: Re-analyze these modules for CALL statements, CICS LINK, file I/O
Quality Criterion Violated: Completeness - "All dependency relationships captured"
```

**Issues Found Message Format:**
```
REVIEW OUTCOME: ISSUES FOUND

The following issues must be addressed before approval:

BLOCKING ISSUES:
[List all blocking issues with full details]

MAJOR ISSUES:
[List all major issues with full details]

MINOR ISSUES:
[List all minor issues with full details]

Remediation required. Please address blocking and major issues.
```

---

## Expected Deliverables

### 1. Review Report
**File**: /home/user/projects/mymigration/tasks/analysis_sourcecode_review_report_001.md
**Description**: Detailed review findings and outcome
**Format**: Markdown

**Content Requirements:**
- Review outcome (APPROVED or ISSUES FOUND)
- Summary of review activities
- Findings for each deliverable
- Issues list (if any) with full details
- Recommendations

**Validation:**
- [ ] Clear outcome stated
- [ ] All deliverables reviewed
- [ ] Issues documented with evidence
- [ ] Remediation guidance provided (if issues)

---

## Quality Criteria

### Thoroughness
- [ ] All deliverables reviewed
- [ ] All quality criteria checked
- [ ] Sampling methodology applied
- [ ] Cross-references validated

### Objectivity
- [ ] Review based on defined criteria
- [ ] Evidence provided for all findings
- [ ] Consistent standards applied
- [ ] No subjective judgments without justification

### Clarity
- [ ] Outcome clearly stated
- [ ] Issues clearly described
- [ ] Remediation guidance actionable
- [ ] Report easy to understand

---

## Success Criteria

**Task is complete when:**
- [ ] All deliverables reviewed
- [ ] Review report produced
- [ ] Clear outcome provided (APPROVED or ISSUES FOUND)
- [ ] If issues found, all issues documented with remediation guidance
- [ ] Report submitted to analysis_team_supervisor

**Verification Steps:**
1. Confirm all deliverables reviewed
2. Validate review report completeness
3. Verify outcome is clear and justified
4. Report completion to analysis_team_supervisor

---

## Notes

### Agent Definition Reference
Your complete role definition and capabilities are in:
/system/agents/analysis_team/analysis_reviewer_legacy_code.md

This task file provides project-specific context and instructions.

### Escalation
If you encounter issues during review:
1. Document the issue clearly
2. Report to analysis_team_supervisor
3. Provide context and recommendations

### Review Standards
Apply consistent standards based on:
- Quality criteria from original task file
- Template requirements
- Industry best practices for analysis documentation
```


### 5.3 Remediation Task File Example

**Scenario:** Analysis Team Supervisor creates remediation task after reviewer finds issues

```markdown
# Task: Remediate Source Code Analysis Issues

## Agent Assignment
**Agent**: analysis_specialist_legacy_code
**Agent Definition**: /system/agents/analysis_team/analysis_specialist_legacy_code.md
**Task ID**: analysis-sourcecode-remediation-001
**Created By**: analysis_team_supervisor
**Created At**: 2024-01-15T16:00:00Z
**Phase**: analysis
**Step**: sourcecode_remediation
**Original Task**: analysis-sourcecode-001
**Review Feedback**: /home/user/projects/mymigration/tasks/analysis_sourcecode_review_report_001.md
**Iteration**: 2

---

## Project Context

### Project Information
**Project Name**: MyMigration
**Project Base Path**: /home/user/projects/mymigration

### Deliverables to Update
- **Dependency Table**: /home/user/projects/mymigration/output/analysis/source_code/reports/dependency_table.csv
  - Template: /home/user/projects/mymigration/templates/Dependency_Analysis_Table.csv
  - Status: Needs remediation
- **Analysis Report**: /home/user/projects/mymigration/output/analysis/source_code/reports/cobol_analysis.md
  - Template: /home/user/projects/mymigration/templates/Cobol_Source_Analysis_Report.md
  - Status: Needs update to reflect corrections

### Reference Data
- **Review Report**: /home/user/projects/mymigration/tasks/analysis_sourcecode_review_report_001.md
- **Original Task**: /home/user/projects/mymigration/tasks/analysis_sourcecode_specialist_task.md
- **Legacy Source Code**: /home/user/projects/mymigration/input/legacy/source

---

## Task Instructions

### Objective
Address all issues identified in review report to bring deliverables to acceptable quality standards.

### Issues to Address

#### Issue REV-001: Missing Dependencies (BLOCKING)
**Affected Deliverable**: Dependency Table
**Severity**: Blocking
**Description**: Missing dependencies for 15 modules
**Evidence**: Modules CUSTMGMT, ORDPROC, INVUPDT, PAYMPROC, ACCTUPDT, RPTGEN01, RPTGEN02, BATCHCTL, FILELOAD, DATACONV, UTILPROG, ERRHAND, LOGMGMT, SECCHECK, AUDITLOG have no dependencies listed
**Remediation Guidance**: 
1. Re-analyze these 15 modules for CALL statements
2. Check for CICS LINK and CICS XCTL commands
3. Identify file I/O operations (SELECT, READ, WRITE)
4. Add all found dependencies to dependency table
5. If truly no dependencies, document why in analysis report

**Quality Criterion Violated**: Completeness - "All dependency relationships captured"

#### Issue REV-002: Inconsistent Module Names (MAJOR)
**Affected Deliverable**: Dependency Table, Analysis Report
**Severity**: Major
**Description**: Module names inconsistent between deliverables
**Evidence**: 
- Dependency Table uses "CUST-MGMT" but Analysis Report uses "CUSTMGMT"
- Dependency Table uses "ORD_PROC" but Analysis Report uses "ORDPROC"
**Remediation Guidance**:
1. Standardize on actual module names from source files
2. Update both Dependency Table and Analysis Report for consistency
3. Use exact names as they appear in PROGRAM-ID

**Quality Criterion Violated**: Consistency - "Module names consistent across all deliverables"

#### Issue REV-003: Missing Statistics (MAJOR)
**Affected Deliverable**: Analysis Report
**Severity**: Major
**Description**: Statistics section incomplete
**Evidence**: Total lines of code not calculated, cyclomatic complexity missing for all modules
**Remediation Guidance**:
1. Calculate total lines of code across all modules
2. Calculate cyclomatic complexity for each module
3. Add summary statistics to report
4. Include distribution charts or tables

**Quality Criterion Violated**: Completeness - "All findings documented with evidence"

### Detailed Steps

#### Step 1: Address Issue REV-001 (Missing Dependencies)
**Actions:**
1. Open each of the 15 modules listed in the issue
2. Scan for CALL statements (static and dynamic)
3. Scan for CICS LINK and CICS XCTL commands
4. Identify file operations (SELECT, FD, READ, WRITE, REWRITE, DELETE)
5. Add all dependencies to dependency table
6. Document in analysis report if any module truly has no dependencies

**Technical Specifications:**
- Use same analysis methodology as original task
- Mark TargetFound=True if target exists, False if not
- Include call type (STATIC, DYNAMIC, CICS-LINK, etc.)

#### Step 2: Address Issue REV-002 (Inconsistent Names)
**Actions:**
1. Create list of all module names from source files (PROGRAM-ID)
2. Update Dependency Table to use exact names
3. Update Analysis Report to use exact names
4. Verify consistency across both deliverables

**Technical Specifications:**
- Use exact PROGRAM-ID as canonical name
- Preserve case as it appears in source
- Update all references in both files

#### Step 3: Address Issue REV-003 (Missing Statistics)
**Actions:**
1. Count lines of code for each module (exclude comments and blank lines)
2. Calculate cyclomatic complexity for each module
3. Add statistics section to analysis report
4. Include summary tables and distributions

**Technical Specifications:**
- LOC = lines in PROCEDURE DIVISION excluding comments/blanks
- Cyclomatic complexity = decision points + 1
- Provide min, max, average, median for both metrics

#### Step 4: Update Analysis Report
**Actions:**
1. Incorporate all corrections from steps 1-3
2. Update findings summary to reflect complete analysis
3. Ensure all sections are complete and accurate
4. Verify report matches template structure

#### Step 5: Verify Corrections
**Actions:**
1. Cross-check all corrections against review feedback
2. Verify all blocking and major issues addressed
3. Ensure quality criteria now met
4. Prepare for re-review

### Business Rules and Constraints
- Same as original task
- Maintain consistency with original analysis methodology
- Preserve all correct information from original deliverables

### Error Handling
- Same as original task
- If unable to resolve an issue, document why and escalate

---

## Expected Deliverables

### 1. Updated Dependency Table
**File**: /home/user/projects/mymigration/output/analysis/source_code/reports/dependency_table.csv
**Description**: Corrected dependency table with all issues addressed
**Format**: CSV

**Content Requirements:**
- All 15 modules now have dependencies listed (or documented as none)
- Module names consistent with source files
- All required fields populated

**Validation:**
- [ ] All modules have dependencies or explanation
- [ ] Module names match PROGRAM-ID exactly
- [ ] No empty required fields
- [ ] Format matches template

### 2. Updated Analysis Report
**File**: /home/user/projects/mymigration/output/analysis/source_code/reports/cobol_analysis.md
**Description**: Corrected analysis report with all issues addressed
**Format**: Markdown

**Content Requirements:**
- Module names consistent with dependency table
- Statistics section complete with LOC and complexity
- Findings updated to reflect complete analysis
- All sections complete

**Validation:**
- [ ] Module names consistent across deliverables
- [ ] Statistics section complete
- [ ] All required sections present
- [ ] Format matches template

### 3. Remediation Summary
**File**: /home/user/projects/mymigration/tasks/analysis_sourcecode_remediation_summary_001.md
**Description**: Summary of changes made to address issues
**Format**: Markdown

**Content Requirements:**
- List of all issues addressed
- Summary of changes made for each issue
- Verification that issues are resolved
- Any remaining concerns or limitations

**Validation:**
- [ ] All issues from review addressed
- [ ] Changes clearly documented
- [ ] Verification provided

---

## Quality Criteria

### Completeness
- [ ] All blocking issues addressed
- [ ] All major issues addressed
- [ ] All deliverables updated
- [ ] Remediation summary provided

### Accuracy
- [ ] Corrections are accurate
- [ ] New data verified against source
- [ ] Statistics calculated correctly
- [ ] No new errors introduced

### Consistency
- [ ] Module names now consistent
- [ ] Terminology consistent
- [ ] Format matches templates
- [ ] Cross-references valid

### Compliance
- [ ] All quality criteria from review now met
- [ ] Original task requirements still satisfied
- [ ] No regression in quality

---

## Success Criteria

**Task is complete when:**
- [ ] All blocking and major issues addressed
- [ ] All deliverables updated
- [ ] Remediation summary provided
- [ ] Ready for re-review
- [ ] Quality criteria met

**Verification Steps:**
1. Verify all issues from review report addressed
2. Check all deliverables updated correctly
3. Validate quality criteria now met
4. Prepare remediation summary
5. Report completion to analysis_team_supervisor for re-review

---

## Notes

### Agent Definition Reference
Your complete role definition and capabilities are in:
/system/agents/analysis_team/analysis_specialist_legacy_code.md

This task file provides project-specific context and instructions.

### Focus on Issues
Focus specifically on addressing the issues identified in the review.
Do not make unnecessary changes to content that was approved.

### Escalation
If you cannot resolve an issue:
1. Document why it cannot be resolved
2. Provide alternatives or workarounds
3. Report to analysis_team_supervisor
4. Do not proceed if blocking issue cannot be resolved
```


---

## 6. Validation Checklist

### 6.1 Pre-Creation Validation

Before creating a task file, verify:

**Phase Prompt Review:**
- [ ] Phase prompt read and understood
- [ ] Step instructions identified
- [ ] Assigned agent identified
- [ ] Expected deliverables listed
- [ ] Quality criteria extracted
- [ ] Success criteria extracted

**Path Resolution:**
- [ ] All `{{PARAMETERS}}` identified
- [ ] All parameters resolved to absolute paths
- [ ] Input paths exist and are readable
- [ ] Output directories exist or can be created
- [ ] Template paths exist and are readable
- [ ] No unresolved parameters remain

**Agent Verification:**
- [ ] Agent definition file exists
- [ ] Agent capabilities match task requirements
- [ ] Agent has necessary permissions

### 6.2 Post-Creation Validation

After creating a task file, verify:

**Structure Completeness:**
- [ ] Agent Assignment section complete
- [ ] Project Context section complete
- [ ] Task Instructions section complete
- [ ] Expected Deliverables section complete
- [ ] Quality Criteria section complete
- [ ] Success Criteria section complete
- [ ] Notes section complete

**Content Quality:**
- [ ] All paths are absolute
- [ ] All paths are valid
- [ ] Instructions are clear and actionable
- [ ] Deliverables are well-defined
- [ ] Quality criteria are measurable
- [ ] Success criteria are verifiable

**Consistency:**
- [ ] Terminology consistent throughout
- [ ] Paths consistent with phase prompt
- [ ] Deliverables match phase prompt expectations
- [ ] Quality criteria align with phase requirements

**Completeness:**
- [ ] No placeholder text (e.g., [TODO], [TBD])
- [ ] No missing sections
- [ ] No empty required fields
- [ ] All instructions extracted from phase prompt

### 6.3 Pre-Delegation Validation

Before delegating task to agent, verify:

**Task File:**
- [ ] Task file saved to correct location ({{TASKS_BASE_PATH}})
- [ ] Task file follows naming convention
- [ ] Task file is readable
- [ ] Task file format is valid markdown

**Environment:**
- [ ] All input paths accessible to agent
- [ ] All output directories writable by agent
- [ ] All templates accessible to agent
- [ ] Agent has necessary permissions

**Readiness:**
- [ ] All dependencies from previous steps complete
- [ ] All prerequisite deliverables exist
- [ ] No blocking issues remain
- [ ] Agent is available for delegation

### 6.4 Post-Execution Validation

After agent completes task, verify:

**Deliverables:**
- [ ] All expected deliverables exist
- [ ] All deliverables at correct paths
- [ ] All deliverables have content (not empty)
- [ ] All deliverables match expected format

**Quality:**
- [ ] All quality criteria met
- [ ] All validation checks pass
- [ ] No errors reported by agent
- [ ] Deliverables ready for review (if applicable)

**Completion:**
- [ ] Agent reported completion
- [ ] Success criteria verified
- [ ] Task marked as complete
- [ ] Ready to proceed to next step


---

## 7. Common Mistakes and Solutions

### 7.1 Path-Related Mistakes

#### Mistake 1: Using Relative Paths
**Problem:**
```markdown
### Input Locations
- **Legacy Source**: ../input/legacy/source
```

**Why It's Wrong:** Agent doesn't know what the relative path is relative to.

**Solution:**
```markdown
### Input Locations
- **Legacy Source**: /home/user/projects/mymigration/input/legacy/source
```

**Rule:** Always use absolute paths in task files.

---

#### Mistake 2: Unresolved Parameters
**Problem:**
```markdown
### Output Locations
- **Analysis Report**: {{COBOL_SOURCE_ANALYSIS_REPORT}}
```

**Why It's Wrong:** Agent cannot resolve parameters; supervisor must resolve them.

**Solution:**
```markdown
### Output Locations
- **Analysis Report**: /home/user/projects/mymigration/output/analysis/cobol_analysis.md
```

**Rule:** Resolve all `{{PARAMETERS}}` before creating task file.

---

#### Mistake 3: Non-Existent Input Paths
**Problem:**
```markdown
### Input Locations
- **Legacy Source**: /home/user/projects/mymigration/input/legacy/source
```
(But this directory doesn't exist)

**Why It's Wrong:** Agent cannot access non-existent inputs.

**Solution:** Verify input paths exist before creating task file. If missing, escalate to Migration Supervisor.

**Rule:** Validate all input paths exist before delegation.

---

### 7.2 Instruction-Related Mistakes

#### Mistake 4: Copying Entire Phase Prompt
**Problem:** Task file contains entire phase prompt verbatim, including instructions for other agents.

**Why It's Wrong:** 
- Task file becomes too large
- Agent sees irrelevant instructions
- Confusion about what to do

**Solution:** Extract only the instructions relevant to this specific agent and task.

**Rule:** Extract and adapt, don't copy entire prompts.

---

#### Mistake 5: Vague Instructions
**Problem:**
```markdown
### Task Instructions
Analyze the source code and produce a report.
```

**Why It's Wrong:** Not specific enough for agent to execute.

**Solution:**
```markdown
### Task Instructions

#### Step 1: Source Code Discovery
Scan all source files in /home/user/projects/mymigration/input/legacy/source

**Actions:**
1. Identify all files with extensions: .cbl, .cob
2. Create inventory with metadata
3. Log any files that cannot be parsed

**Technical Specifications:**
- Include files from database directory
- Exclude system utilities: DMBATCH, IDCAMS
```

**Rule:** Provide detailed, actionable, step-by-step instructions.

---

#### Mistake 6: Missing Error Handling
**Problem:** Task file doesn't specify what to do when errors occur.

**Why It's Wrong:** Agent doesn't know how to handle errors gracefully.

**Solution:** Include error handling section with scenarios, detection, and recovery.

**Rule:** Always include error handling guidance.

---

### 7.3 Deliverable-Related Mistakes

#### Mistake 7: Undefined Deliverables
**Problem:**
```markdown
### Expected Deliverables
Produce an analysis report.
```

**Why It's Wrong:** No path, no template, no format specified.

**Solution:**
```markdown
### Expected Deliverables

### 1. Source Code Analysis Report
**File**: /home/user/projects/mymigration/output/analysis/cobol_analysis.md
**Template**: /home/user/projects/mymigration/templates/Cobol_Source_Analysis_Report.md
**Description**: Comprehensive analysis findings
**Format**: Markdown

**Content Requirements:**
- Analysis methodology section
- Findings summary
- Recommendations

**Validation:**
- [ ] File exists at specified path
- [ ] Format matches template
- [ ] All sections present
```

**Rule:** Fully specify each deliverable with path, template, format, requirements, and validation.

---

#### Mistake 8: Missing Template References
**Problem:** Deliverable specifies output path but no template.

**Why It's Wrong:** Agent doesn't know what structure to follow.

**Solution:** Always provide template path for structured deliverables.

**Rule:** Include template path for all deliverables that have templates.

---

### 7.4 Quality-Related Mistakes

#### Mistake 9: No Quality Criteria
**Problem:** Task file doesn't specify quality standards.

**Why It's Wrong:** Agent doesn't know what quality level is expected.

**Solution:** Include quality criteria section with completeness, accuracy, consistency, and compliance criteria.

**Rule:** Always include measurable quality criteria.

---

#### Mistake 10: Vague Success Criteria
**Problem:**
```markdown
## Success Criteria
Task is complete when work is done.
```

**Why It's Wrong:** Not verifiable or actionable.

**Solution:**
```markdown
## Success Criteria

**Task is complete when:**
- [ ] All deliverables produced at specified paths
- [ ] All quality criteria met
- [ ] All validation checks pass
- [ ] No blocking errors remain
- [ ] Ready for review

**Verification Steps:**
1. Check all output files exist
2. Validate file formats
3. Verify content completeness
4. Confirm quality criteria
5. Report completion to supervisor
```

**Rule:** Provide specific, verifiable success criteria with verification steps.

---

### 7.5 Agent-Related Mistakes

#### Mistake 11: Duplicating Agent Definition
**Problem:** Task file includes entire agent definition content.

**Why It's Wrong:**
- Duplication of information
- Task file becomes too large
- Maintenance burden (two places to update)

**Solution:** Reference agent definition, don't duplicate it.

```markdown
## Agent Assignment
**Agent**: analysis_specialist_legacy_code
**Agent Definition**: /system/agents/analysis_team/analysis_specialist_legacy_code.md

## Notes
### Agent Definition Reference
Your complete role definition and capabilities are in your agent definition file.
This task file provides project-specific context and instructions.
```

**Rule:** Reference agent definitions, never duplicate them.

---

#### Mistake 12: Wrong Agent Assignment
**Problem:** Task assigned to agent without necessary capabilities.

**Why It's Wrong:** Agent cannot complete task successfully.

**Solution:** Verify agent capabilities match task requirements before assignment.

**Rule:** Match agent capabilities to task requirements.

---

### 7.6 Context-Related Mistakes

#### Mistake 13: Missing Project Context
**Problem:** Task file jumps straight to instructions without providing project context.

**Why It's Wrong:** Agent doesn't know project name, base path, or overall context.

**Solution:** Always include complete project context section.

**Rule:** Provide full project context in every task file.

---

#### Mistake 14: Missing Reference Data
**Problem:** Task requires reference materials but they're not listed.

**Why It's Wrong:** Agent doesn't know where to find necessary reference information.

**Solution:** List all reference data with paths in project context section.

**Rule:** Include all necessary reference data locations.

---

### 7.7 Format-Related Mistakes

#### Mistake 15: Inconsistent Formatting
**Problem:** Task file doesn't follow template structure consistently.

**Why It's Wrong:** Harder to read and parse, may confuse agent.

**Solution:** Follow template structure exactly, use consistent markdown formatting.

**Rule:** Maintain consistent structure and formatting throughout.

---

#### Mistake 16: Missing Sections
**Problem:** Task file omits required sections (e.g., no Quality Criteria section).

**Why It's Wrong:** Incomplete information for agent.

**Solution:** Include all required sections from template.

**Rule:** Every task file must have all required sections.


---

## 8. Troubleshooting Guide

### 8.1 Task File Creation Issues

#### Problem: Cannot Resolve Parameter
**Symptoms:** Phase prompt contains `{{PARAMETER}}` but value is unknown.

**Diagnosis:**
1. Check if parameter is defined in paths.cfg
2. Check if create_project.py filled the parameter
3. Check if parameter name is correct (case-sensitive)

**Solutions:**
- If parameter not in paths.cfg: Add it to paths.cfg and regenerate project
- If parameter not filled: Check create_project.py logic
- If parameter name wrong: Correct the parameter name in phase prompt

**Escalation:** If parameter cannot be resolved, escalate to Migration Supervisor.

---

#### Problem: Input Path Does Not Exist
**Symptoms:** Input path specified in phase prompt doesn't exist on filesystem.

**Diagnosis:**
1. Verify path is correct (check for typos)
2. Check if directory should have been created by previous step
3. Check if path is from correct project

**Solutions:**
- If typo: Correct the path
- If missing from previous step: Escalate to Migration Supervisor (dependency issue)
- If wrong project: Verify project context

**Escalation:** Do not create task file with non-existent input paths. Escalate to Migration Supervisor.

---

#### Problem: Template File Not Found
**Symptoms:** Template path specified but file doesn't exist.

**Diagnosis:**
1. Check if templates were copied during project creation
2. Verify template name is correct
3. Check if template is in correct location

**Solutions:**
- If templates not copied: Re-run create_project.py
- If name wrong: Correct template name
- If location wrong: Update template path

**Escalation:** Do not create task file without valid template. Escalate to Migration Supervisor.

---

#### Problem: Unclear Instructions in Phase Prompt
**Symptoms:** Phase prompt instructions are ambiguous or incomplete.

**Diagnosis:**
1. Review phase prompt carefully
2. Check if instructions reference other documents
3. Determine if information is truly missing or just unclear

**Solutions:**
- If reference exists: Include reference in task file
- If truly missing: Escalate to Migration Supervisor for clarification
- If unclear: Interpret based on context and document assumption

**Escalation:** If critical information is missing, escalate before creating task file.

---

### 8.2 Task Execution Issues

#### Problem: Agent Reports Missing Input
**Symptoms:** Agent cannot find input files specified in task file.

**Diagnosis:**
1. Verify input path in task file is correct
2. Check if input path exists on filesystem
3. Verify agent has read permissions

**Solutions:**
- If path wrong in task file: Correct and re-delegate
- If path doesn't exist: Investigate why (dependency issue?)
- If permissions issue: Fix permissions and re-delegate

**Prevention:** Validate input paths exist before creating task file.

---

#### Problem: Agent Cannot Write Output
**Symptoms:** Agent reports cannot create output file.

**Diagnosis:**
1. Check if output directory exists
2. Verify agent has write permissions
3. Check if disk space is available

**Solutions:**
- If directory missing: Create directory and re-delegate
- If permissions issue: Fix permissions and re-delegate
- If disk space issue: Free up space and re-delegate

**Prevention:** Verify output directories exist and are writable before delegation.

---

#### Problem: Agent Produces Wrong Output Format
**Symptoms:** Deliverable doesn't match expected format or template.

**Diagnosis:**
1. Check if template path was provided correctly
2. Verify agent understood format requirements
3. Check if template itself is correct

**Solutions:**
- If template path wrong: Correct task file and re-delegate
- If agent misunderstood: Clarify instructions and re-delegate
- If template wrong: Fix template and re-delegate

**Prevention:** Provide clear format requirements and valid template paths.

---

#### Problem: Agent Reports Task Too Complex
**Symptoms:** Agent cannot complete task due to complexity or scope.

**Diagnosis:**
1. Review task scope and complexity
2. Check if task should be broken into sub-tasks
3. Verify agent has necessary capabilities

**Solutions:**
- If too complex: Break into smaller tasks
- If missing capabilities: Assign to different agent or enhance agent definition
- If unclear scope: Clarify and simplify instructions

**Prevention:** Keep tasks focused and within agent capabilities.

---

### 8.3 Quality Issues

#### Problem: Deliverables Incomplete
**Symptoms:** Agent reports completion but deliverables are missing content.

**Diagnosis:**
1. Check if quality criteria were clear
2. Verify agent understood requirements
3. Check if agent encountered errors

**Solutions:**
- If criteria unclear: Clarify quality criteria and request remediation
- If misunderstood: Provide clearer instructions and request remediation
- If errors occurred: Address errors and request remediation

**Prevention:** Provide clear, measurable quality criteria in task file.

---

#### Problem: Deliverables Don't Match Template
**Symptoms:** Deliverable structure doesn't match template.

**Diagnosis:**
1. Verify template path was correct
2. Check if agent accessed template
3. Verify template is appropriate for task

**Solutions:**
- If template path wrong: Correct and request remediation
- If agent didn't use template: Emphasize template requirement and request remediation
- If template inappropriate: Update template or instructions

**Prevention:** Verify template paths and emphasize template usage in instructions.

---

### 8.4 Review Issues

#### Problem: Reviewer Finds Many Issues
**Symptoms:** Review identifies numerous quality problems.

**Diagnosis:**
1. Check if quality criteria were clear in original task
2. Verify agent had necessary information
3. Determine if issues are systematic or isolated

**Solutions:**
- If criteria unclear: Clarify criteria for remediation task
- If information missing: Provide missing information for remediation
- If systematic: May need to enhance agent definition or instructions

**Prevention:** Provide clear quality criteria and complete information in original task.

---

#### Problem: Specialist and Reviewer Disagree
**Symptoms:** Specialist believes work is correct, reviewer disagrees.

**Diagnosis:**
1. Review quality criteria from original task
2. Check if criteria are objective and measurable
3. Determine if interpretation differs

**Solutions:**
- If criteria subjective: Clarify with objective measures
- If interpretation differs: Provide authoritative interpretation
- If genuine disagreement: Escalate to Migration Supervisor

**Prevention:** Use objective, measurable quality criteria.

---

### 8.5 Iteration Issues

#### Problem: Excessive Iterations
**Symptoms:** Specialist → Reviewer cycle repeats more than 3 times.

**Diagnosis:**
1. Review history of issues and remediations
2. Check if issues are recurring or new each time
3. Determine if fundamental problem exists

**Solutions:**
- If recurring issues: Agent may lack capability, consider reassignment
- If new issues each time: Quality criteria may be unclear or incomplete
- If fundamental problem: Escalate to Migration Supervisor

**Prevention:** Clear quality criteria, capable agents, complete information.

---

### 8.6 Escalation Guidelines

**When to Escalate to Migration Supervisor:**

1. **Missing Critical Information**
   - Phase prompt lacks necessary information
   - Dependencies from previous phases incomplete
   - Cannot resolve required parameters

2. **Resource Issues**
   - Input paths don't exist (dependency problem)
   - Agent lacks necessary capabilities
   - Technical limitations encountered

3. **Quality Issues**
   - Excessive iterations (>3) without resolution
   - Fundamental disagreement on requirements
   - Systematic quality problems

4. **Scope Issues**
   - Task scope too large for single agent
   - Requirements conflict with constraints
   - Unclear or ambiguous requirements

**Escalation Message Format:**
```
TO: Migration Supervisor
FROM: [Team Supervisor Name]
PHASE: [Phase Name]
STEP: [Step Name]
ISSUE: [Brief description]
CONTEXT: [What was attempted, iterations completed, agents involved]
IMPACT: [How this affects project progress]
REQUEST: [What is needed to proceed]
RECOMMENDATION: [Suggested solution if any]
```

---

## 9. Quick Reference

### 9.1 Task File Checklist

**Before Creating Task File:**
- [ ] Read and understand phase prompt
- [ ] Identify assigned agent
- [ ] Extract relevant instructions
- [ ] Resolve all paths
- [ ] Verify inputs exist
- [ ] Verify outputs are creatable
- [ ] Verify templates exist

**Task File Must Include:**
- [ ] Agent Assignment section
- [ ] Project Context section
- [ ] Task Instructions section
- [ ] Expected Deliverables section
- [ ] Quality Criteria section
- [ ] Success Criteria section
- [ ] Notes section

**Before Delegating:**
- [ ] Task file saved to {{TASKS_BASE_PATH}}
- [ ] Task file follows naming convention
- [ ] All paths are absolute
- [ ] No unresolved parameters
- [ ] All sections complete
- [ ] Agent is available

**After Execution:**
- [ ] All deliverables exist
- [ ] Quality criteria met
- [ ] Success criteria verified
- [ ] Ready for next step

### 9.2 Common Parameters

| Parameter | Typical Value | Description |
|-----------|---------------|-------------|
| `{{PROJECT_NAME}}` | MyMigration | Project identifier |
| `{{PROJECT_BASE_PATH}}` | /home/user/projects/myproject | Project root |
| `{{TASKS_BASE_PATH}}` | /home/user/projects/myproject/tasks | Task files location |
| `{{TEMPLATES_BASE_PATH}}` | /home/user/projects/myproject/templates | Templates location |
| `{{LEGACY_SOURCE_CODE}}` | /home/user/projects/myproject/input/legacy/source | Legacy source |
| `{{ANALYSIS_OUTPUT}}` | /home/user/projects/myproject/output/analysis | Analysis outputs |

### 9.3 Task File Naming Convention

**Format:** `[phase]_[step]_[agent-role]_task.md`

**Examples:**
- `analysis_sourcecode_specialist_task.md`
- `analysis_sourcecode_reviewer_task.md`
- `analysis_sourcecode_remediation_task.md`
- `workpackage_planning_specialist_task.md`
- `business_extraction_specialist_task.md`

### 9.4 Key Principles

1. **Absolute Paths Only** - Never use relative paths
2. **Reference, Don't Duplicate** - Reference agent definitions, don't copy them
3. **Extract, Don't Copy** - Extract relevant instructions, don't copy entire prompts
4. **Verify Before Delegate** - Validate all paths and prerequisites before delegation
5. **Clear and Actionable** - Instructions must be specific and executable
6. **Measurable Quality** - Quality criteria must be objective and verifiable
7. **Complete Context** - Provide all necessary information for agent to succeed

---

## 10. Conclusion

Task files are the bridge between generic, reusable agent definitions and project-specific execution. By following this template and guidelines, Team Supervisors can create effective task files that enable agents to execute work successfully.

**Key Takeaways:**

1. **Structure Matters** - Follow the template structure consistently
2. **Paths Must Be Absolute** - Always resolve paths completely
3. **Instructions Must Be Clear** - Provide detailed, actionable steps
4. **Quality Must Be Defined** - Specify measurable quality criteria
5. **Validation Is Essential** - Verify before creation, during execution, after completion

**For Team Supervisors:**
- Use this document as a reference when creating task files
- Follow the validation checklists
- Learn from the examples
- Avoid the common mistakes
- Escalate when necessary

**For Framework Developers:**
- Use this document to understand task file requirements
- Enhance agent definitions to work with this structure
- Improve phase prompts to provide necessary information
- Develop tools to assist with task file creation

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2024-01-15 | System | Initial documentation |

---

**End of Task File Template Documentation**
