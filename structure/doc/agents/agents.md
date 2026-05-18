# Agents Documentation

This directory contains AI agent configurations and specifications for automated legacy code migration tasks. The agents follow the [CLI Agent Orchestrator (CAO)](https://github.com/awslabs/cli-agent-orchestrator) structure and format, but can be used with any multi-agent system that supports the CAO agent profile format.

## Agent Architecture Overview

The migration framework implements a **3-layer orchestration architecture** with hierarchical multi-agent teams coordinated by supervisors. Each agent is designed as a markdown file with YAML frontmatter following the CAO agent profile specification.

### Orchestration Architecture

The framework uses a supervisor-based delegation model where:

1. **Layer 1 - Migration Supervisor**: Receives the main migration prompt and delegates entire phases to team supervisors
2. **Layer 2 - Team Supervisors**: Receive phase prompts, create task files, and delegate to specialists/reviewers
3. **Layer 3 - Specialists & Reviewers**: Receive task files and execute technical work or validate deliverables

**Key Principle:** Agents are generic and reusable. Project-specific context is provided through task files created at runtime by team supervisors.

For detailed information about the orchestration architecture, see [Orchestration Architecture Documentation](../orchestration_architecture.md).

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
Coordinate teams and manage workflow phases using the orchestration architecture:
- **Migration Supervisor**: Top-level orchestrator ensuring sequential phase completion, delegates phases to team supervisors
- **Analysis Team Supervisor**: Coordinates analysis activities, creates task files for specialists/reviewers, orchestrates iterative review
- **Planning Team Supervisor**: Manages workpackage definition, creates task files, orchestrates review within phase
- **Business Team Supervisor**: Orchestrates business logic extraction, creates task files, manages iterative quality assurance
- **Development Team Supervisor**: Manages code generation and testing, creates task files, coordinates review cycles
- **Deployment Team Supervisor**: Coordinates deployment scripts and production rollout, creates task files, ensures quality gates

**Key Responsibilities:**
- Receive phase prompts from Migration Supervisor (or main prompt for Migration Supervisor)
- Create task files for specialists and reviewers with project-specific context
- Delegate tasks to team members
- Orchestrate iterative review (specialist → reviewer → remediation → repeat until approved)
- Report phase completion only after review approval

### Specialist Agents (11 agents)
Domain experts performing technical work based on task files:

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

**Key Responsibilities:**
- Receive task files from team supervisors
- Execute technical work according to task instructions
- Produce deliverables at specified paths using provided templates
- Report completion to team supervisor
- Remediate issues when reviewer finds problems

### Reviewer Agents (11 agents)
Quality assurance specialists with 1:1 pairing to specialists, working within iterative review cycles:

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

**Key Responsibilities:**
- Receive review task files from team supervisors
- Validate deliverables against quality criteria
- Provide detailed feedback on issues found (or approval if quality criteria met)
- Support iterative improvement through multiple review cycles

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

### Orchestration-Based Workflow

The migration follows the 3-layer orchestration architecture:

**Layer 1 - Migration Supervisor:**
1. Receives main migration prompt with all phases
2. Understands phase dependencies and execution order
3. Delegates entire phases to team supervisors
4. Monitors phase completion and verifies deliverables
5. Enforces sequential phase execution

**Layer 2 - Team Supervisors:**
1. Receive phase prompts from Migration Supervisor
2. Create task files for specialists with project-specific context
3. Delegate tasks to specialists
4. Orchestrate iterative review within the phase:
   - Delegate to reviewer after specialist completes
   - Handle feedback (approved or issues found)
   - Create remediation tasks if issues found
   - Iterate until reviewer approves
5. Report phase completion only after review approval

**Layer 3 - Specialists & Reviewers:**
1. Receive task files from team supervisors
2. Execute work according to task instructions
3. Produce deliverables (specialists) or validate deliverables (reviewers)
4. Report completion or feedback to team supervisor

### Sequential Phase Processing
The migration follows a strict sequential workflow managed by the Migration Supervisor:

1. **Phase 1 - Analysis**: Legacy Code Analyst and Database Analyst work in parallel, validated by reviewers through iterative cycles
2. **Phase 2 - Planning**: Workpackage Planner creates migration roadmap, validated by reviewer through iterative cycles
3. **Phase 3 - Business Specification**: Business team extracts requirements and defines test cases, validated through iterative review
4. **Phase 4 - Development**: Code Developer and Test Generator create code and tests, validated through iterative review
5. **Phase 5 - Deployment**: Deployment team creates migration scripts and deployment procedures, validated through iterative review

### Quality Gate Enforcement
Each phase has mandatory quality gates enforced through iterative review:
- **No phase starts** until the previous phase is approved by its reviewer
- **All deliverables** must pass review before proceeding to the next phase
- **Iterative review cycles** orchestrated by team supervisors: specialist → reviewer → (if issues) → remediation → reviewer → ... → approved
- **Migration Supervisor** enforces sequential execution and quality standards
- **Team Supervisors** track iteration count and escalate if excessive (>3 iterations)

### Parallel Execution Within Teams
Within each team, agents can work in parallel:
- **Analysis Team**: Legacy Code Analyst and Database Analyst work simultaneously
- **Development Team**: Code Developer and Test Generator coordinate but work on different aspects
- **Future Teams**: Business and Deployment teams will have parallel workflows

### Task Assignment Protocol
Supervisors follow the orchestration architecture's task assignment protocol:
1. **Verify Prerequisites**: Ensure previous phase completion and input availability
2. **Read Phase Prompt**: Understand phase objectives, instructions, and deliverables
3. **Create Task Files**: Write detailed task files with:
   - Agent assignment information
   - Project-specific context (all resolved paths)
   - Extracted instructions relevant to the agent
   - Expected deliverables with templates
   - Quality and success criteria
4. **Assign to Agents**: Provide task file path when delegating
5. **Monitor Progress**: Track deliverable production and quality
6. **Orchestrate Review**: Create review task files and delegate to reviewers
7. **Handle Feedback**: Create remediation tasks if issues found, iterate until approved
8. **Report Completion**: Notify Migration Supervisor only after review approval

For detailed task file creation guidance, see [Task File Template Documentation](../task_file_template.md)

## Agent Installation and Usage

### Installation Options

#### Automated Installation (Recommended)
Use the framework's installation script to install all 28 agents automatically with provider selection:

```bash
# Create project and install all agents with K-CLI (default provider)
python create_project.py my_project
python install_cao.py my_project

# Install with specific provider
python install_cao.py my_project --provider k_cli     # K-CLI (default)
python install_cao.py my_project --provider q_cli     # Amazon Q CLI
python install_cao.py my_project --provider claude_code  # Claude Code

# The script will discover and install all agents from subdirectories
```

#### Individual Agent Installation
You can install and use individual agents for specific tasks using the new CAO command syntax:

```bash
# Install a single agent from local file with default provider (K-CLI)
cao agent install ./structure/agents/analysis_team/analysis_specialist_legacy_code.md

# Install with specific provider
cao agent install ./structure/agents/analysis_team/analysis_specialist_legacy_code.md --provider q_cli

# Install built-in agents (if available in CAO)
cao agent install developer --provider k_cli

# Install from URL
cao agent install https://example.com/custom-agent.md --provider k_cli

# List installed agents
cao agent list
```

#### Team Installation
Install an entire team starting with the supervisor:

```bash
# Install analysis team with K-CLI provider
cao agent install ./structure/agents/analysis_team/analysis_team_supervisor.md --provider k_cli
cao agent install ./structure/agents/analysis_team/analysis_specialist_legacy_code.md --provider k_cli
cao agent install ./structure/agents/analysis_team/analysis_reviewer_legacy_code.md --provider k_cli
cao agent install ./structure/agents/analysis_team/analysis_specialist_database.md --provider k_cli
cao agent install ./structure/agents/analysis_team/analysis_reviewer_database.md --provider k_cli

# Verify installation
cao agent list
```

#### Complete Migration System Installation
Install the full hierarchical system:

```bash
# Install all 28 agents with provider selection
python install_cao.py my_project --provider k_cli

# Or install manually starting with the migration supervisor
cao agent install ./structure/agents/migration_supervisor.md --provider k_cli

# Install all team directories
find ./structure/agents -name "*.md" -exec cao agent install {} --provider k_cli \;

# Verify complete installation
cao agent list
```

### Provider Selection

#### Supported Providers

| Provider | Display Name | Description | CLI Required |
|----------|--------------|-------------|--------------|
| `k_cli` | K-CLI (Kiro) | **Default provider** - Best integration with Kiro development environment | Yes (kiro command) |
| `q_cli` | Amazon Q CLI | AWS-native AI assistant integration | Yes (q command) |
| `claude_code` | Claude Code | Anthropic Claude integration | No |

#### K-CLI Setup (Default Provider)

K-CLI is the recommended default provider for the best integration experience:

1. **Install Kiro**: Follow the [Kiro installation guide](https://kiro.ai/docs/installation)
2. **Verify Installation**: Run `kiro --version` to confirm K-CLI is available
3. **Configure Workspace**: Ensure your project is in a Kiro workspace

```bash
# Verify K-CLI availability
kiro --version

# Install agents with K-CLI (default)
python install_cao.py my_project

# Or explicitly specify K-CLI
python install_cao.py my_project --provider k_cli
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
# Install and coordinate complete analysis with team supervisor
cao agent install ./structure/agents/analysis_team/analysis_team_supervisor.md --provider k_cli
# Use CAO session management to run the supervisor

# Or install and run individual specialists
cao agent install ./structure/agents/analysis_team/analysis_specialist_legacy_code.md --provider k_cli
cao agent install ./structure/agents/analysis_team/analysis_specialist_database.md --provider k_cli
```

#### Workpackage Planning Only
```bash
# Install and create migration workpackages from existing analysis
cao agent install ./structure/agents/planning_team/planning_team_supervisor.md --provider k_cli

# Or install and run specialist directly
cao agent install ./structure/agents/planning_team/planning_specialist_workpackage.md --provider k_cli
```

#### Business Requirements Extraction
```bash
# Install and coordinate business specification activities
cao agent install ./structure/agents/business_team/business_team_supervisor.md --provider k_cli

# Or install and run individual specialists
cao agent install ./structure/agents/business_team/business_specialist_logic_extraction.md --provider k_cli
cao agent install ./structure/agents/business_team/business_specialist_requirements.md --provider k_cli
cao agent install ./structure/agents/business_team/business_specialist_test_design.md --provider k_cli
```

#### Code Generation Only
```bash
# Install and coordinate development activities
cao agent install ./structure/agents/development_team/development_team_supervisor.md --provider k_cli

# Or install and run individual specialists
cao agent install ./structure/agents/development_team/development_specialist_code_generation.md --provider k_cli
cao agent install ./structure/agents/development_team/development_specialist_test_generation.md --provider k_cli
```

#### Deployment Preparation
```bash
# Install and coordinate deployment activities
cao agent install ./structure/agents/deployment_team/deployment_team_supervisor.md --provider k_cli

# Or install and run individual specialists
cao agent install ./structure/agents/deployment_team/deployment_specialist_migration_scripts.md --provider k_cli
cao agent install ./structure/agents/deployment_team/deployment_specialist_orchestration.md --provider k_cli
```

## Framework Integration

### Template System Integration
Agents integrate with the migration framework through:
- **Standardized Templates**: All outputs use templates from `structure/templates/`
- **Path Configuration**: Agents respect project-specific path configurations
- **LCMP Validation**: Outputs are validated against framework templates
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
# Install Team Supervisors with K-CLI (default provider)
cao agent install ./structure/agents/migration_supervisor.md --provider k_cli
cao agent install ./structure/agents/analysis_team/analysis_team_supervisor.md --provider k_cli
cao agent install ./structure/agents/planning_team/planning_team_supervisor.md --provider k_cli
cao agent install ./structure/agents/business_team/business_team_supervisor.md --provider k_cli
cao agent install ./structure/agents/development_team/development_team_supervisor.md --provider k_cli
cao agent install ./structure/agents/deployment_team/deployment_team_supervisor.md --provider k_cli

# Install Key Specialists
cao agent install ./structure/agents/analysis_team/analysis_specialist_legacy_code.md --provider k_cli
cao agent install ./structure/agents/business_team/business_specialist_requirements.md --provider k_cli
cao agent install ./structure/agents/development_team/development_specialist_code_generation.md --provider k_cli
cao agent install ./structure/agents/deployment_team/deployment_specialist_orchestration.md --provider k_cli

# Verify installations
cao agent list
```

### Installation Commands
```bash
# Complete setup with K-CLI provider (default)
python create_project.py my_project
python install_cao.py my_project

# Complete setup with specific provider
python install_cao.py my_project --provider q_cli

# Verify installation
find my_project/structure/agents -name "*.md" | wc -l  # Should show 28
cao agent list  # Should show installed agents with providers
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