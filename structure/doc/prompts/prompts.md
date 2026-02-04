# Prompts Documentation

This directory contains AI prompts organized by migration phases. These prompts guide AI agents through systematic analysis and migration tasks within the **3-layer orchestration architecture**, ensuring consistent and thorough processing of legacy systems.

## Orchestration Architecture Integration

Prompts are designed to work within the orchestration architecture:

1. **Main Migration Prompt** (`ReImagine_Main_Prompt.md`): Given to Migration Supervisor, contains all phases with delegation instructions
2. **Phase Prompts**: Given to Team Supervisors, contain phase-specific instructions and task file creation guidance
3. **Task Files**: Created by Team Supervisors from phase prompts, given to Specialist/Reviewer agents

**Key Principle:** Prompts contain project-specific context (paths resolved from `paths.cfg`), while agents remain generic and reusable.

For detailed information about the orchestration architecture, see [Orchestration Architecture Documentation](../orchestration_architecture.md)

## Prompt Structure

Prompts are organized into sequential phases that build upon each other. Each prompt includes orchestration information for supervisor-based delegation:

### Main Migration Prompt
**File: `ReImagine_Main_Prompt.md`**

The top-level prompt given to the Migration Supervisor containing:
- Complete project context with all resolved paths
- All migration phases in sequence
- Team supervisor assignments for each phase
- Expected deliverables for each phase
- Delegation instructions and success criteria

### Phase 00: Preparation
**Directory: `00_preparation/`**

Initial setup and preparation prompts that establish the foundation for migration analysis:
- Environment setup validation
- Source code inventory and cataloging
- Initial assessment and scoping
- Prerequisite verification

### Phase 01: Analysis
**Directory: `01_analysis/`**

Deep analysis prompts for understanding the legacy system. Each prompt includes:
- Orchestration header with team supervisor and assigned agent
- Task file creation guidance for supervisors
- Complete phase context with resolved paths
- Detailed instructions for specialists
- Quality criteria and success metrics
- Expected deliverables with templates

**Prompts:**
- Database analysis
- Source code structure analysis
- Business logic extraction
- Data flow analysis
- Dependency mapping
- Technology stack assessment

### Phase 02: Workpackage Definition
**Directory: `02_workpackage/`**

Prompts for breaking down the migration into manageable workpackages:
- Functional decomposition
- Dependency analysis
- Risk assessment
- Effort estimation
- Priority assignment
- Resource allocation planning

Each prompt includes orchestration information for the planning team supervisor.

### Phase 03: Business Extraction
**Directory: `03-business_extraction/`**

Detailed specification prompts for target system design:
- Business logic extraction
- Domain consolidation
- Requirements specification
- Test case generation (service-based and domain-based)

Each prompt includes orchestration information for the business team supervisor.

### Phase 04: Code Generation
**Directory: `04_code_generation/`**

Prompts for generating modern code from legacy systems:
- Code transformation rules
- Pattern mapping
- Quality assurance checks
- Testing strategy
- Deployment planning
- Rollback procedures

Each prompt includes orchestration information for the development team supervisor.

## Usage Guidelines

### Orchestration-Based Execution

**Migration Supervisor Level:**
1. Receives `ReImagine_Main_Prompt.md` with all phases
2. Delegates entire phases to team supervisors
3. Provides phase prompt files to team supervisors
4. Verifies deliverables before proceeding to next phase

**Team Supervisor Level:**
1. Receives phase prompt from Migration Supervisor
2. Reads phase prompt to understand objectives and instructions
3. Creates task files for specialists and reviewers
4. Extracts relevant instructions from phase prompt
5. Resolves all paths from `{{PARAMETERS}}`
6. Delegates task files to specialists/reviewers
7. Orchestrates iterative review cycles
8. Reports completion only after review approval

**Specialist/Reviewer Level:**
1. Receives task file from team supervisor
2. Executes work according to task instructions
3. Produces deliverables (specialists) or validates deliverables (reviewers)
4. Reports completion or feedback to team supervisor

### Sequential Processing
Prompts should generally be executed in phase order, as later phases depend on outputs from earlier phases. The Migration Supervisor enforces this sequential execution.

### Customization
Prompts can be customized for specific:
- Legacy technologies (COBOL, PL/I, etc.)
- Target platforms (.NET, Java, Python, etc.)
- Business domains
- Organizational requirements

All customizations should maintain the orchestration structure (header sections, task file creation guidance, etc.).

### Integration with Templates
Prompts are designed to work with the template system, generating outputs that populate the standardized templates in the `templates/` directory. Task files created by supervisors include template paths for specialists to use.

### Path Resolution
All prompts use `{{PARAMETER}}` placeholders that are resolved by `create_project.py` during project creation. Team supervisors must resolve these parameters when creating task files.

### AI Agent Configuration
Each phase prompt includes:
- Orchestration header with team supervisor and assigned agent
- Context requirements with resolved paths
- Expected input formats and locations
- Output specifications with templates
- Quality criteria and validation checkpoints
- Task file creation protocol for supervisors

For detailed information on task file creation, see [Task File Template Documentation](../task_file_template.md)