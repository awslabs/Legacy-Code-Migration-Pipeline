# Agents Documentation

This directory contains AI agent configurations and specifications for automated legacy code migration tasks. The agents follow the [CLI Agent Orchestrator (CAO)](https://github.com/awslabs/cli-agent-orchestrator) structure and format, but can be used with any multi-agent system that supports the CAO agent profile format.

## Agent Architecture Overview

The migration framework implements a hierarchical multi-agent system with specialized teams coordinated by supervisors. Each agent is designed as a markdown file with YAML frontmatter following the CAO agent profile specification.

### Hierarchical Structure

```
Migration Supervisor (Top Level)
├── Analysis Team Supervisor
│   ├── Legacy Code Analyst
│   ├── Database Analyst
│   └── Analysis Reviewer
├── Planning Team Supervisor
│   ├── Workpackage Planner
│   └── Planning Reviewer
├── Business Team Supervisor (Future Phase 3)
│   ├── Business Logic Analyst*
│   ├── Requirements Extractor*
│   ├── Test Case Designer*
│   └── Business Reviewer*
├── Development Team Supervisor (Enhanced)
│   ├── Code Developer
│   ├── Test Generator
│   └── Code Reviewer
└── Deployment Team Supervisor (Future Phase 5)
    ├── Migration Script Generator*
    ├── Database Migration Specialist*
    ├── Deployment Orchestrator*
    └── Deployment Reviewer*
```

*Agents marked with asterisk are defined in supervisors but individual agent files await prompt development.

## Agent Categories

### Supervisor Agents
Coordinate teams and manage workflow phases:
- **Migration Supervisor**: Top-level orchestrator ensuring sequential phase completion
- **Analysis Team Supervisor**: Coordinates legacy system analysis activities
- **Planning Team Supervisor**: Manages workpackage definition and migration roadmap creation
- **Business Team Supervisor**: Orchestrates business logic extraction and requirements specification
- **Development Team Supervisor**: Manages code generation and testing (existing code_supervisor)
- **Deployment Team Supervisor**: Coordinates deployment scripts and production rollout

### Analysis Agents
Specialized agents for legacy system analysis:
- **Legacy Code Analyst**: Analyzes COBOL source code, dependencies, and business flows
- **Database Analyst**: Processes database schemas and creates migration assessments
- **Analysis Reviewer**: Validates all analysis outputs for completeness and accuracy

### Planning Agents
Agents responsible for migration planning and prioritization:
- **Workpackage Planner**: Creates prioritized migration workpackages based on complexity analysis
- **Planning Reviewer**: Validates workpackage definitions and migration roadmaps

### Development Agents
Agents focused on code generation and testing:
- **Code Developer**: Generates target language code from business specifications (existing)
- **Test Generator**: Creates automated test code and comprehensive test data
- **Code Reviewer**: Validates generated code quality and standards compliance (existing)

### Quality Assurance Agents
Specialized reviewers ensuring deliverable quality:
- **Analysis Reviewer**: Reviews and approves all analysis phase outputs
- **Planning Reviewer**: Reviews and approves all planning phase outputs
- **Business Reviewer**: Reviews and approves business specifications and test definitions
- **Code Reviewer**: Reviews and approves all generated code and tests
- **Deployment Reviewer**: Reviews and approves deployment scripts and procedures

## Agent Configuration and Structure

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

#### Individual Agent Installation
You can install and use individual agents for specific tasks:

```bash
# Install a single agent (using CAO)
cao install ./structure/agents/legacy_code_analyst.md

# Run the agent directly
cao run legacy_code_analyst
```

#### Team Installation
Install an entire team starting with the supervisor:

```bash
# Install analysis team
cao install ./structure/agents/analysis_team_supervisor.md
cao install ./structure/agents/legacy_code_analyst.md
cao install ./structure/agents/database_analyst.md
cao install ./structure/agents/analysis_reviewer.md

# Run the team supervisor
cao run analysis_team_supervisor
```

#### Complete Migration System Installation
Install the full hierarchical system:

```bash
# Install all agents starting with the migration supervisor
cao install ./structure/agents/migration_supervisor.md
# ... install all team supervisors and their agents

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
# Just analyze legacy COBOL code
cao run analysis_team_supervisor
# or directly
cao run legacy_code_analyst
```

#### Workpackage Planning Only
```bash
# Create migration workpackages from existing analysis
cao run planning_team_supervisor
# or directly  
cao run workpackage_planner
```

#### Code Generation Only
```bash
# Generate code from existing specifications
cao run code_supervisor  # existing development team supervisor
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

### Currently Implemented Agents
The following agents are fully implemented and ready for use:

#### Analysis Team
- **`migration_supervisor.md`**: Top-level migration orchestrator
- **`analysis_team_supervisor.md`**: Coordinates analysis activities
- **`legacy_code_analyst.md`**: Analyzes COBOL source code (implements sourcecode analysis prompt)
- **`database_analyst.md`**: Analyzes database schemas (implements database analysis prompt)
- **`analysis_reviewer.md`**: Reviews and validates analysis outputs

#### Planning Team
- **`planning_team_supervisor.md`**: Coordinates workpackage planning
- **`workpackage_planner.md`**: Creates migration workpackages (implements workpackage prompts)
- **`planning_reviewer.md`**: Reviews and validates planning outputs

#### Development Team (Enhanced)
- **`code_supervisor.md`**: Development team supervisor (existing)
- **`code_developer.md`**: Generates target code (existing)
- **`test_generator.md`**: Creates automated tests and test data
- **`code_reviewer.md`**: Reviews generated code (existing)

#### Future Teams (Structured but Awaiting Prompts)
- **`business_team_supervisor.md`**: Coordinates business specification (Phase 3)
- **`deployment_team_supervisor.md`**: Coordinates deployment activities (Phase 5)

### Agent Status by Implementation Phase

#### Phase 1 & 2 - Ready for Production
- ✅ Analysis Team: Complete with existing prompts
- ✅ Planning Team: Complete with existing prompts
- ✅ Enhanced Development Team: Test Generator added

#### Phase 3 & 5 - Awaiting Prompt Development
- 🔄 Business Team: Supervisor ready, individual agents await prompts
- 🔄 Deployment Team: Supervisor ready, individual agents await prompts

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