# Agents Documentation

This directory contains AI agent configurations and specifications for automated legacy code migration tasks. The agents follow the [CLI Agent Orchestrator (CAO)](https://github.com/awslabs/cli-agent-orchestrator) structure and format, but can be used with any multi-agent system that supports the CAO agent profile format.

## Agent Architecture Overview

The migration framework implements a hierarchical multi-agent system with specialized teams coordinated by supervisors. Each agent is designed as a markdown file with YAML frontmatter following the CAO agent profile specification.

### Hierarchical Structure

```
Migration Supervisor (Top Level)
├── Analysis Team Supervisor
│   ├── Legacy Code Specialist ↔ Legacy Code Reviewer
│   └── Database Specialist ↔ Database Reviewer
├── Planning Team Supervisor
│   └── Workpackage Specialist ↔ Workpackage Reviewer
├── Business Team Supervisor
│   ├── Logic Extraction Specialist ↔ Logic Extraction Reviewer
│   ├── Requirements Specialist ↔ Requirements Reviewer
│   └── Test Design Specialist ↔ Test Design Reviewer
├── Development Team Supervisor
│   ├── Code Generation Specialist ↔ Code Generation Reviewer
│   └── Test Generation Specialist ↔ Test Generation Reviewer
└── Deployment Team Supervisor
    ├── Migration Scripts Specialist ↔ Migration Scripts Reviewer
    ├── Database Migration Specialist ↔ Database Migration Reviewer
    └── Orchestration Specialist ↔ Orchestration Reviewer
```

**Total: 28 Agents** organized in 6 teams with 1:1 specialist-reviewer pairing for granular quality control.

## Agent Categories

### Supervisor Agents (6 agents)
Coordinate teams and manage workflow phases:
- **Migration Supervisor**: Top-level orchestrator ensuring sequential phase completion
- **Analysis Team Supervisor**: Coordinates legacy system analysis activities  
- **Planning Team Supervisor**: Manages workpackage definition and migration roadmap creation
- **Business Team Supervisor**: Orchestrates business logic extraction and requirements specification
- **Development Team Supervisor**: Manages code generation and testing
- **Deployment Team Supervisor**: Coordinates deployment scripts and production rollout

### Specialist Agents (11 agents)
Domain experts performing technical work:

**Analysis Specialists:**
- **Legacy Code Specialist**: Analyzes COBOL source code, dependencies, and business flows
- **Database Specialist**: Processes database schemas and creates migration assessments

**Planning Specialists:**
- **Workpackage Specialist**: Creates prioritized migration workpackages based on complexity analysis

**Business Specialists:**
- **Logic Extraction Specialist**: Extracts business rules and logic from legacy code analysis
- **Requirements Specialist**: Converts business logic into modern requirements specifications
- **Test Design Specialist**: Creates comprehensive test case definitions

**Development Specialists:**
- **Code Generation Specialist**: Generates modern application code from business specifications
- **Test Generation Specialist**: Implements comprehensive test suites and test data

**Deployment Specialists:**
- **Migration Scripts Specialist**: Creates database migration and data transfer scripts
- **Database Migration Specialist**: Plans and executes database migration procedures
- **Orchestration Specialist**: Coordinates deployment automation and production rollout

### Reviewer Agents (11 agents)
Quality assurance specialists with 1:1 pairing to specialists:

**Analysis Reviewers:**
- **Legacy Code Reviewer**: Reviews and validates legacy code analysis outputs
- **Database Reviewer**: Reviews and validates database analysis outputs

**Planning Reviewers:**
- **Workpackage Reviewer**: Reviews and validates workpackage definitions and migration roadmaps

**Business Reviewers:**
- **Logic Extraction Reviewer**: Reviews and validates business logic extraction deliverables
- **Requirements Reviewer**: Reviews and validates requirements specification deliverables  
- **Test Design Reviewer**: Reviews and validates test case design deliverables

**Development Reviewers:**
- **Code Generation Reviewer**: Reviews and validates generated application code
- **Test Generation Reviewer**: Reviews and validates generated test implementations

**Deployment Reviewers:**
- **Migration Scripts Reviewer**: Reviews and validates migration script deliverables
- **Database Migration Reviewer**: Reviews and validates database migration plans
- **Orchestration Reviewer**: Reviews and validates deployment orchestration deliverables

## Agent Configuration and Structure

### Naming Convention
All agents follow a consistent naming pattern: `{team}_{role}_{specialization}.md`

**Examples:**
- `analysis_specialist_legacy_code.md` - Analysis team's legacy code specialist
- `business_reviewer_requirements.md` - Business team's requirements reviewer  
- `development_team_supervisor.md` - Development team supervisor

This naming convention ensures:
- **Self-documenting filenames** when flattened in CAO installation
- **Clear team identification** for easy organization
- **Role clarity** (supervisor/specialist/reviewer)
- **Specialization visibility** for specific domain expertise

### CAO Agent Profile Format
All agents follow the CLI Agent Orchestrator (CAO) agent profile format:

```markdown
---
name: agent-name
description: Brief description of the agent
mcpServers:
  cao-mcp-server:
    type: stdio
    command: uvx
    args:
      - "--from"
      - "git+https://github.com/awslabs/cli-agent-orchestrator.git@main"
      - "cao-mcp-server"
---

# AGENT NAME

## Role and Identity
[Agent's role and responsibilities]

## Core Responsibilities
[Detailed list of what the agent does]

## Critical Rules
[Important rules the agent must follow]
```

### Agent Capabilities
Each agent defines specific capabilities:
- **Input Requirements**: Expected input formats, file locations, and prerequisites
- **Output Specifications**: Generated artifact formats, templates, and file locations
- **Quality Criteria**: Validation rules, success metrics, and approval requirements
- **Integration Points**: How the agent connects with supervisors and other agents

### Prompt Integration
Agents integrate with the framework's prompt system:
- **Analysis Agents**: Execute prompts from `prompts/01_analysis/` directory
- **Planning Agents**: Execute prompts from `prompts/02_workpackage/` directory
- **Future Agents**: Will execute prompts from `prompts/03_specification/`, `prompts/04_code_generation/`, etc.
- **Task Files**: Supervisors create detailed task files referencing specific prompts

## Agent Workflows and Execution

### Sequential Phase Processing
The migration follows a strict sequential workflow managed by the Migration Supervisor:

1. **Phase 1 - Analysis**: Legacy Code Analyst and Database Analyst work in parallel, validated by Analysis Reviewer
2. **Phase 2 - Planning**: Workpackage Planner creates migration roadmap, validated by Planning Reviewer
3. **Phase 3 - Business Specification**: Business team extracts requirements and defines test cases
4. **Phase 4 - Development**: Code Developer and Test Generator create code and tests, validated by Code Reviewer
5. **Phase 5 - Deployment**: Deployment team creates migration scripts and deployment procedures

### Quality Gate Enforcement
Each phase has mandatory quality gates:
- **No phase starts** until the previous phase is approved by its reviewer
- **All deliverables** must pass review before proceeding to the next phase
- **Iterative review cycles** continue until all quality criteria are met
- **Migration Supervisor** enforces sequential execution and quality standards

### Parallel Execution Within Teams
Within each team, agents can work in parallel:
- **Analysis Team**: Legacy Code Analyst and Database Analyst work simultaneously
- **Development Team**: Code Developer and Test Generator coordinate but work on different aspects
- **Future Teams**: Business and Deployment teams will have parallel workflows

### Task Assignment Protocol
Supervisors follow a consistent task assignment protocol:
1. **Verify Prerequisites**: Ensure previous phase completion and input availability
2. **Create Task Files**: Write detailed task descriptions with absolute paths
3. **Assign to Agents**: Reference task files for agent execution
4. **Monitor Progress**: Track deliverable production and quality
5. **Coordinate Review**: Send all outputs to appropriate reviewer agents

## Agent Installation and Usage

### Installation Options

#### Automated Installation (Recommended)
Use the framework's installation script to install all 28 agents automatically:

```bash
# Create project and install all agents
python create_project.py my_project
python install_cao.py my_project

# The script will discover and install all agents from subdirectories
```

#### Individual Agent Installation
You can install and use individual agents for specific tasks:

```bash
# Install a single agent (using CAO)
cao install ./agents/analysis_team/analysis_specialist_legacy_code.md

# Run the agent directly
cao run analysis_specialist_legacy_code
```

#### Team Installation
Install an entire team starting with the supervisor:

```bash
# Install analysis team
cao install ./agents/analysis_team/analysis_team_supervisor.md
cao install ./agents/analysis_team/analysis_specialist_legacy_code.md
cao install ./agents/analysis_team/analysis_reviewer_legacy_code.md
cao install ./agents/analysis_team/analysis_specialist_database.md
cao install ./agents/analysis_team/analysis_reviewer_database.md

# Run the team supervisor
cao run analysis_team_supervisor
```

#### Complete Migration System Installation
Install the full hierarchical system:

```bash
# Install all 28 agents starting with the migration supervisor
cao install ./agents/migration_supervisor.md

# Install all team directories
find ./agents -name "*.md" -exec cao install {} \;

# Run the complete migration
cao run migration_supervisor
```

### Flexible Entry Points
You can start at any level of the hierarchy depending on your needs:

- **Complete Migration**: Start with `migration_supervisor` for full end-to-end migration
- **Analysis Only**: Start with `analysis_team_supervisor` for legacy system analysis
- **Planning Only**: Start with `planning_team_supervisor` if you have analysis results
- **Development Only**: Start with `development_team_supervisor` (existing `code_supervisor`) if you have specifications
- **Individual Tasks**: Run specific agents like `legacy_code_analyst` for targeted analysis

### Usage Examples

#### Legacy Code Analysis Only
```bash
# Coordinate complete analysis with team supervisor
cao run analysis_team_supervisor

# Or run individual specialists
cao run analysis_specialist_legacy_code
cao run analysis_specialist_database
```

#### Workpackage Planning Only
```bash
# Create migration workpackages from existing analysis
cao run planning_team_supervisor

# Or run specialist directly
cao run planning_specialist_workpackage
```

#### Business Requirements Extraction
```bash
# Coordinate business specification activities
cao run business_team_supervisor

# Or run individual specialists
cao run business_specialist_logic_extraction
cao run business_specialist_requirements
cao run business_specialist_test_design
```

#### Code Generation Only
```bash
# Coordinate development activities
cao run development_team_supervisor

# Or run individual specialists
cao run development_specialist_code_generation
cao run development_specialist_test_generation
```

#### Deployment Preparation
```bash
# Coordinate deployment activities
cao run deployment_team_supervisor

# Or run individual specialists
cao run deployment_specialist_migration_scripts
cao run deployment_specialist_orchestration
```

## Framework Integration

### Template System Integration
Agents integrate with the migration framework through:
- **Standardized Templates**: All outputs use templates from `structure/templates/`
- **Path Configuration**: Agents respect project-specific path configurations
- **ACM Validation**: Outputs are validated against framework templates
- **Progress Tracking**: Status updates follow standardized progress tracking formats

### Tool Generation and Integration
Many agents create reusable tools:
- **Analysis Tools**: Legacy Code Analyst and Database Analyst create Python analysis tools
- **Planning Tools**: Workpackage Planner creates workpackage analysis tools
- **Test Tools**: Test Generator creates test automation frameworks
- **Migration Tools**: Deployment agents create migration and deployment automation

## Available Agents

### Complete Agent Implementation (28 agents)
All agents are fully implemented and organized in team directories:

#### Root Level (1 agent)
- **`migration_supervisor.md`**: Top-level migration orchestrator

#### Analysis Team (5 agents)
- **`analysis_team/analysis_team_supervisor.md`**: Coordinates analysis activities
- **`analysis_team/analysis_specialist_legacy_code.md`**: Analyzes COBOL source code
- **`analysis_team/analysis_reviewer_legacy_code.md`**: Reviews legacy code analysis
- **`analysis_team/analysis_specialist_database.md`**: Analyzes database schemas  
- **`analysis_team/analysis_reviewer_database.md`**: Reviews database analysis

#### Planning Team (3 agents)
- **`planning_team/planning_team_supervisor.md`**: Coordinates workpackage planning
- **`planning_team/planning_specialist_workpackage.md`**: Creates migration workpackages
- **`planning_team/planning_reviewer_workpackage.md`**: Reviews workpackage planning

#### Business Team (7 agents)
- **`business_team/business_team_supervisor.md`**: Coordinates business specification
- **`business_team/business_specialist_logic_extraction.md`**: Extracts business logic
- **`business_team/business_reviewer_logic_extraction.md`**: Reviews logic extraction
- **`business_team/business_specialist_requirements.md`**: Creates requirements specifications
- **`business_team/business_reviewer_requirements.md`**: Reviews requirements
- **`business_team/business_specialist_test_design.md`**: Designs test cases
- **`business_team/business_reviewer_test_design.md`**: Reviews test design

#### Development Team (5 agents)
- **`development_team/development_team_supervisor.md`**: Coordinates code generation
- **`development_team/development_specialist_code_generation.md`**: Generates application code
- **`development_team/development_reviewer_code_generation.md`**: Reviews generated code
- **`development_team/development_specialist_test_generation.md`**: Implements test suites
- **`development_team/development_reviewer_test_generation.md`**: Reviews test implementation

#### Deployment Team (7 agents)
- **`deployment_team/deployment_team_supervisor.md`**: Coordinates deployment activities
- **`deployment_team/deployment_specialist_migration_scripts.md`**: Creates migration scripts
- **`deployment_team/deployment_reviewer_migration_scripts.md`**: Reviews migration scripts
- **`deployment_team/deployment_specialist_database_migration.md`**: Plans database migration
- **`deployment_team/deployment_reviewer_database_migration.md`**: Reviews database migration
- **`deployment_team/deployment_specialist_orchestration.md`**: Coordinates deployment
- **`deployment_team/deployment_reviewer_orchestration.md`**: Reviews deployment orchestration

### Agent Status by Implementation Phase

#### All Phases - Production Ready ✅
- ✅ **Analysis Team**: Complete with 1:1 specialist-reviewer pairing
- ✅ **Planning Team**: Complete with 1:1 specialist-reviewer pairing  
- ✅ **Business Team**: Complete with comprehensive business logic extraction and requirements
- ✅ **Development Team**: Complete with code generation and test implementation
- ✅ **Deployment Team**: Complete with migration scripts and deployment orchestration

### Agent File Organization

The agents are organized in a hierarchical directory structure for development convenience, but when installed via `install_cao.py`, all agents are flattened into the CAO system with self-documenting filenames:

```
structure/agents/
├── migration_supervisor.md
├── analysis_team/
│   ├── analysis_team_supervisor.md
│   ├── analysis_specialist_legacy_code.md
│   ├── analysis_reviewer_legacy_code.md
│   ├── analysis_specialist_database.md
│   └── analysis_reviewer_database.md
├── planning_team/
│   ├── planning_team_supervisor.md
│   ├── planning_specialist_workpackage.md
│   └── planning_reviewer_workpackage.md
├── business_team/
│   ├── business_team_supervisor.md
│   ├── business_specialist_logic_extraction.md
│   ├── business_reviewer_logic_extraction.md
│   ├── business_specialist_requirements.md
│   ├── business_reviewer_requirements.md
│   ├── business_specialist_test_design.md
│   └── business_reviewer_test_design.md
├── development_team/
│   ├── development_team_supervisor.md
│   ├── development_specialist_code_generation.md
│   ├── development_reviewer_code_generation.md
│   ├── development_specialist_test_generation.md
│   └── development_reviewer_test_generation.md
└── deployment_team/
    ├── deployment_team_supervisor.md
    ├── deployment_specialist_migration_scripts.md
    ├── deployment_reviewer_migration_scripts.md
    ├── deployment_specialist_database_migration.md
    ├── deployment_reviewer_database_migration.md
    ├── deployment_specialist_orchestration.md
    └── deployment_reviewer_orchestration.md
```

## Best Practices

### Agent Usage Guidelines
- **Start Small**: Begin with individual agents or teams for specific tasks
- **Validate Inputs**: Ensure all required input files and directories exist before running agents
- **Monitor Progress**: Use progress tracking files to monitor agent execution
- **Review Outputs**: Always run reviewer agents to validate deliverable quality
- **Maintain Paths**: Use absolute file paths consistently across all agent interactions

### Agent Development Guidelines
- **Follow CAO Format**: All new agents must follow the CAO agent profile specification
- **Implement Quality Gates**: Include comprehensive review and validation processes
- **Maintain Traceability**: Ensure clear links between inputs, processing, and outputs
- **Document Thoroughly**: Provide clear documentation for agent capabilities and usage
- **Handle Errors Gracefully**: Implement robust error handling and recovery mechanisms

### Integration Guidelines
- **Respect Hierarchy**: Use supervisors to coordinate team activities
- **Maintain Sequential Flow**: Ensure proper phase sequencing and quality gates
- **Use Standard Templates**: All outputs must conform to framework templates
- **Preserve File Paths**: Maintain absolute path references throughout the workflow
- **Enable Flexibility**: Support both complete migration and individual task execution

## Quick Reference

### Agent Count by Team
- **Total Agents**: 28
- **Analysis Team**: 5 agents (1 supervisor + 2 specialists + 2 reviewers)
- **Planning Team**: 3 agents (1 supervisor + 1 specialist + 1 reviewer)  
- **Business Team**: 7 agents (1 supervisor + 3 specialists + 3 reviewers)
- **Development Team**: 5 agents (1 supervisor + 2 specialists + 2 reviewers)
- **Deployment Team**: 7 agents (1 supervisor + 3 specialists + 3 reviewers)
- **Migration Supervisor**: 1 agent (top-level orchestrator)

### Key Agent Names for CAO
```bash
# Team Supervisors
cao run migration_supervisor
cao run analysis_team_supervisor
cao run planning_team_supervisor
cao run business_team_supervisor
cao run development_team_supervisor
cao run deployment_team_supervisor

# Key Specialists
cao run analysis_specialist_legacy_code
cao run business_specialist_requirements
cao run development_specialist_code_generation
cao run deployment_specialist_orchestration
```

### Installation Commands
```bash
# Complete setup
python create_project.py my_project
python install_cao.py my_project

# Verify installation
find my_project/agents -name "*.md" | wc -l  # Should show 28
```

## Compatibility and Extensibility

### Multi-Agent System Compatibility
While designed for CAO, these agents can be adapted for other multi-agent systems:
- **Agent Profiles**: The markdown format with YAML frontmatter is widely supported
- **Task Descriptions**: The task file approach can be adapted to other orchestration systems
- **Quality Gates**: The review and approval workflow can be implemented in various frameworks
- **Hierarchical Structure**: The supervisor-worker pattern is applicable across different systems

### Extension Points
The framework is designed for easy extension:
- **New Agent Types**: Add specialized agents following the established patterns
- **Additional Phases**: Extend the workflow with new migration phases
- **Technology Support**: Adapt agents for different legacy and target technologies
- **Quality Criteria**: Customize review criteria for specific migration requirements