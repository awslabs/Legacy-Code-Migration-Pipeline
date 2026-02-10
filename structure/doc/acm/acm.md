# ACM (Agent Configuration Management) Framework

The ACM framework provides quality assurance, validation tools, and agent management for the legacy code migration process. It ensures that all deliverables meet specified standards, maintains consistency across migration projects, and manages the installation and configuration of AI agents.

## Framework Components

### 1. Agent Installation and Management

The ACM framework includes tools for installing and managing the 28 specialized AI agents used in the migration process.

#### install_agents.py

A standalone script for installing or updating agents from the `agents` directory into CAO (CLI Agent Orchestrator).

**Location**: `acm/install_agents.py` (copied to each project during creation)

**Usage**:
```bash
# Install all agents from the agents directory
python acm/install_agents.py

# Install with a specific provider
python acm/install_agents.py --provider kiro_cli

# Install specific agent sources
python acm/install_agents.py --agent-sources agent1.md agent2.md

# Install from a custom agents directory
python acm/install_agents.py --agents-dir /path/to/agents
```

**Options**:
- `--agents-dir PATH`: Path to agents directory (default: ./agents or ../agents)
- `--provider PROVIDER`: CLI provider for agent integration (choices: kiro_cli, q_cli, claude_code; default: kiro_cli)
- `--agent-sources SOURCE [SOURCE ...]`: Specific agent sources to install (built-in names, file paths, or URLs)

**Supported Providers**:

1. **kiro_cli** (default): Kiro CLI integration
   - Requires: `kiro-cli` command available in PATH
   - Installation: https://kiro.ai

2. **q_cli**: Amazon Q CLI integration
   - Requires: `q` command available in PATH
   - Installation: AWS documentation

3. **claude_code**: Claude Code integration
   - No additional CLI installation required

**When to Use**:
- **Initial Setup**: After creating a project with `create_project.py`
- **Agent Updates**: When you modify agent markdown files
- **Adding New Agents**: After adding new agent files to the agents directory
- **Provider Changes**: When switching between different CLI providers
- **Troubleshooting**: If agents are not working correctly, reinstall them

**Examples**:
```bash
# Standard installation with Kiro CLI
cd my_project
python acm/install_agents.py

# Install with Amazon Q CLI
python acm/install_agents.py --provider q_cli

# Install only specific agents
python acm/install_agents.py --agent-sources migration_supervisor.md code_generator.md

# Install from a different directory
python acm/install_agents.py --agents-dir /path/to/custom/agents
```

**Prerequisites**:
- CAO (CLI Agent Orchestrator) must be installed
  - Install using: `python install_cao.py` from the project root
- The selected provider CLI tool should be available (if required)

**Troubleshooting**:

If agent installation fails:

1. **Check CAO Installation**
   ```bash
   cao --help
   ```

2. **Verify Provider Availability**
   ```bash
   # For Kiro CLI
   kiro-cli --version
   
   # For Amazon Q CLI
   q --version
   ```

3. **Kiro CLI Authentication Issues**
   
   If you see `AccessDeniedException` or "bearer token is invalid":
   ```bash
   # Logout and login to refresh authentication
   kiro-cli logout
   kiro-cli login
   ```
   
   This is needed when:
   - Your session has expired
   - You haven't used kiro-cli in a while
   - AWS credentials have been refreshed

4. **Check Agents Directory**
   - Ensure the agents directory exists
   - Verify agent files have `.md` extension
   - Check that agent files have valid YAML frontmatter

5. **View Detailed Logs**
   - Check the script output for specific error messages
   - Verify network connectivity for URL-based agents

6. **Manual Installation**
   ```bash
   # Install a single agent manually
   cao install /path/to/agent.md --provider kiro_cli
   
   # Check installed agents
   ls ~/.kiro/agents/
   ```

For more troubleshooting help, see the [Troubleshooting Guide](../../../TROUBLESHOOTING.md).

### 2. Deliverable Validation

The ACM framework provides comprehensive validation tools for ensuring migration quality and completeness.

## ACM Directory Structure

When the ACM directory is copied to a project, it maintains the following structure:

```
project_name/
├── acm/
│   ├── install_agents.py         # Agent installation script
│   └── deliverable_validator.py  # Deliverable validation tool
├── agents/                       # Agent markdown files
│   ├── migration_supervisor.md
│   ├── analysis_team/
│   ├── business_team/
│   ├── development_team/
│   ├── planning_team/
│   └── deployment_team/
├── templates/                    # Deliverable templates
└── output/                       # Generated deliverables
```

## Workflow Integration

### Agent Management Workflow

1. **Create Project**: `python create_project.py <project_name>`
2. **Install CAO**: `python install_cao.py` (if not already installed)
3. **Install Agents**: `python acm/install_agents.py` (from project directory)
4. **Update Agents**: Modify agent files, then run `python acm/install_agents.py` again
5. **Use Agents**: Launch with CAO or your chosen provider

### Validation Workflow

1. **Generate Deliverables**: Agents produce outputs in the output directory
2. **Run Validation**: Execute `./validate_deliverables.sh` to check quality
3. **Review Results**: Address any validation issues
4. **Iterate**: Repeat until all deliverables pass validation

## Notes

- The `install_agents.py` script is copied to each project during creation
- You can modify agent files at any time and reinstall them
- Different projects can use different providers
- Agent installation is independent of CAO installation
- Validation can be run at any time during the migration process

## Integration with Orchestration Architecture

The ACM framework integrates with the 3-layer orchestration architecture at multiple points:

1. **Specialist Level**: Specialists can self-validate deliverables before reporting completion
2. **Reviewer Level**: Reviewers use ACM validation as part of their quality criteria checks
3. **Team Supervisor Level**: Supervisors can verify deliverables exist and are valid before proceeding
4. **Migration Supervisor Level**: Can validate entire phase outputs before moving to next phase

The iterative review process orchestrated by team supervisors ensures deliverables pass both ACM validation and reviewer quality checks before phase completion.

For more information on the orchestration architecture, see [Orchestration Architecture Documentation](../orchestration_architecture.md)

## Framework Overview

The ACM framework is built around the principle of template-driven validation, where every deliverable in the migration process has a corresponding template that defines its expected structure and content.

### Core Components

#### 1. Agent Installation Script (install_agents.py)
Manages the installation and configuration of AI agents for the migration process. See the Agent Installation and Management section above for detailed usage.

#### 2. Deliverable Validator (deliverable_validator.py)
The primary tool for ensuring migration quality and completeness. See [Deliverable Validator Documentation](deliverable_validator.md) for detailed usage instructions.

**Key Features:**
- **Template Matching**: Ensures every output has a corresponding template
- **Content Validation**: Validates structure and format of JSON, Markdown, and CSV files
- **Comprehensive Reporting**: Detailed validation results with specific error messages
- **Integration Ready**: Designed for CI/CD pipeline integration

#### Validation Framework
The underlying framework that supports:
- **Multi-format Support**: JSON, Markdown, CSV validation with extensible architecture
- **Recursive Validation**: Deep validation of nested structures and hierarchies
- **Error Classification**: Distinguishes between missing templates and content issues
- **Batch Processing**: Validates entire project outputs efficiently

## Quality Assurance Process

### Validation Levels

#### Level 1: Template Existence
- Verifies that every deliverable has a corresponding template
- Ensures no outputs are generated without proper specification
- Identifies missing template definitions

#### Level 2: Structure Validation
- **JSON**: Validates key structure, data types, and nesting
- **Markdown**: Validates header structure and hierarchy
- **CSV**: Validates column headers and structure

#### Level 3: Content Validation
- Ensures content follows expected patterns and formats
- Validates data consistency and completeness
- Checks for required fields and proper formatting

### Integration Points

#### Project Creation
- Templates are automatically copied during project setup
- Path configurations ensure proper template resolution
- Validation scripts are included in every project

#### Orchestration Workflow
- **Specialist Agents**: Can run validation before reporting completion
- **Reviewer Agents**: Include ACM validation in quality criteria
- **Team Supervisors**: Verify deliverables before creating review tasks
- **Iterative Review**: Validation failures trigger remediation cycles
- **Phase Completion**: All deliverables validated before phase approval

#### Migration Workflow
- Validation checkpoints at each migration phase
- Continuous validation during deliverable generation
- Iterative review cycles ensure quality before proceeding
- Final validation before project completion

#### CI/CD Integration
- Command-line interface for automated validation
- Exit codes for build pipeline integration
- Quiet mode for automated processing

## Best Practices

### Template Management
- **Consistency**: Maintain consistent template structures across projects
- **Versioning**: Track template changes and maintain compatibility
- **Documentation**: Document template purposes and usage patterns
- **Validation**: Validate templates themselves for correctness

### Deliverable Generation
- **Template Compliance**: Generate outputs that match template structures
- **Incremental Validation**: Validate deliverables as they're created (specialists can self-check)
- **Error Handling**: Address validation issues promptly
- **Iterative Improvement**: Reviewer feedback + ACM validation = high quality deliverables
- **Documentation**: Document any deviations from standard templates

### Quality Assurance
- **Regular Validation**: Run validation checks frequently during migration
- **Iterative Review**: Team supervisors orchestrate specialist → reviewer → remediation cycles
- **Issue Resolution**: Address validation issues before proceeding to next phase
- **Continuous Improvement**: Update templates based on lessons learned
- **Stakeholder Communication**: Share validation results with project stakeholders

## Framework Extension

### Adding New File Types
The validation framework is designed for extensibility:
1. Implement validation logic for new file formats
2. Add format detection and routing
3. Update error reporting for new validation types
4. Test with representative files

### Custom Validation Rules
- **Business Rules**: Add domain-specific validation logic
- **Quality Metrics**: Implement custom quality measurements
- **Integration Checks**: Validate integration requirements
- **Performance Criteria**: Check performance-related deliverables

### Tool Integration
- **Static Analysis**: Integrate code quality tools
- **Security Scanning**: Add security validation capabilities
- **Performance Testing**: Include performance validation
- **Compliance Checking**: Ensure regulatory compliance