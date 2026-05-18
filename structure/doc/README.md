# ReImagine Framework Documentation

This directory contains comprehensive documentation for the ReImagine Framework, a multi-agent system for legacy application migration.

## Documentation Structure

### Core Architecture
- **[Orchestration Architecture](orchestration_architecture.md)** - Complete guide to the 3-layer orchestration architecture
- **[Task File Template](task_file_template.md)** - Detailed guide for creating task files

### Component Documentation
- **[Agents](agents/agents.md)** - AI agent configurations and specifications
- **[Prompts](prompts/prompts.md)** - AI prompts organized by migration phases
- **[Templates](templates/templates.md)** - Standardized templates for deliverables
- **[LCMP Framework](lcmp/lcmp.md)** - Quality assurance and validation tools
- **[Deliverable Validator](lcmp/deliverable_validator.md)** - Validation tool usage guide

### Directory Structure
- **[Input Structure](input/input.md)** - Source materials and specifications organization
- **[Output Structure](output/output.md)** - Generated artifacts and deliverables organization

## Quick Start

### Understanding the Architecture

The ReImagine Framework uses a **3-layer orchestration architecture**:

1. **Layer 1 - Migration Supervisor**: Receives main prompt, delegates phases to team supervisors
2. **Layer 2 - Team Supervisors**: Receive phase prompts, create task files, orchestrate iterative review
3. **Layer 3 - Specialists & Reviewers**: Receive task files, execute work or validate deliverables

**Key Principle:** Agents are generic and reusable. Project-specific context is provided through task files created at runtime.

### Getting Started

1. **Read the Orchestration Architecture**: Start with [orchestration_architecture.md](orchestration_architecture.md) to understand the overall system
2. **Understand Agents**: Review [agents/agents.md](agents/agents.md) to learn about the 28 agents and their roles
3. **Learn About Prompts**: Read [prompts/prompts.md](prompts/prompts.md) to understand how prompts guide the workflow
4. **Explore Task Files**: Study [task_file_template.md](task_file_template.md) to learn how supervisors create task files
5. **Set Up Validation**: Review [lcmp/lcmp.md](lcmp/lcmp.md) to understand quality assurance

### Key Concepts

#### Separation of Concerns
- **Agents**: Generic, reusable across projects (no project-specific paths)
- **Prompts**: Project-specific, contain resolved paths and instructions
- **Task Files**: Runtime-specific, created by supervisors for each task

#### Information Flow
```
Main Prompt (all phases + paths)
    ↓
Migration Supervisor (delegates phases)
    ↓
Phase Prompt (phase-specific paths + instructions)
    ↓
Team Supervisor (creates task files)
    ↓
Task File (agent-specific paths + instructions)
    ↓
Specialist/Reviewer Agent (executes work)
```

#### Iterative Quality Assurance
- Team supervisors orchestrate review within each phase
- Specialist produces deliverables → Reviewer validates → (if issues) → Remediation → Repeat
- Phase completes only after reviewer approval
- No separate sequential review step

### Documentation Navigation

#### For Framework Users
1. Start with [Orchestration Architecture](orchestration_architecture.md)
2. Review [Agents Documentation](agents/agents.md) for agent capabilities
3. Check [Prompts Documentation](prompts/prompts.md) for workflow guidance
4. Use [Deliverable Validator](lcmp/deliverable_validator.md) for quality checks

#### For Framework Developers
1. Study [Orchestration Architecture](orchestration_architecture.md) for design principles
2. Review [Task File Template](task_file_template.md) for task file structure
3. Understand [LCMP Framework](lcmp/lcmp.md) for validation integration
4. Check component docs for extension points

#### For Team Supervisors (AI Agents)
1. Read [Orchestration Architecture](orchestration_architecture.md) section 6 on task file creation
2. Study [Task File Template](task_file_template.md) for detailed guidance
3. Review [Prompts Documentation](prompts/prompts.md) for phase prompt structure
4. Understand iterative review orchestration in [Orchestration Architecture](orchestration_architecture.md) section 5

#### For Specialists/Reviewers (AI Agents)
1. Understand your role in [Agents Documentation](agents/agents.md)
2. Learn about task files in [Task File Template](task_file_template.md)
3. Review [Templates Documentation](templates/templates.md) for deliverable structure
4. Check [Deliverable Validator](lcmp/deliverable_validator.md) for self-validation

## Additional Resources

### Project Setup
- Use `create_project.py` to create new migration projects
- Use `install_cao.py` to install all agents with CAO
- Configure paths in `config/paths.cfg`

### Validation
- Run `./validate_deliverables.sh` to validate all deliverables
- Use LCMP framework for continuous quality assurance
- Integrate validation into CI/CD pipelines

### Templates
- All templates are in `structure/templates/`
- Templates are automatically copied to new projects
- Customize templates for specific project needs

## Contributing

When updating documentation:
1. Maintain consistency with orchestration architecture
2. Update all related documents when making changes
3. Include examples and diagrams where helpful
4. Keep documentation synchronized with code changes
5. Follow the established documentation structure

## Version History

- **Version 1.0** (2024-01-15): Initial documentation with orchestration architecture
  - 3-layer orchestration model
  - Task file creation protocol
  - Iterative review orchestration
  - Complete component documentation
