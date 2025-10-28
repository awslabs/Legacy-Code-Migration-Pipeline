# Agents Documentation

This directory contains AI agent configurations and specifications for automated migration tasks. Agents are specialized AI components that handle specific aspects of the legacy code migration process.

## Agent Architecture

### Agent Types

#### Analysis Agents
Specialized agents for different types of analysis:
- **Source Code Analyzer**: Analyzes legacy source code structure, dependencies, and business logic
- **Database Analyzer**: Processes database schemas, stored procedures, and data relationships
- **Business Flow Analyzer**: Extracts and documents business processes and workflows
- **Dependency Analyzer**: Maps relationships between system components

#### Transformation Agents
Agents responsible for code and data transformation:
- **Code Generator**: Converts legacy code to modern programming languages
- **Database Migrator**: Transforms database schemas and data structures
- **Configuration Generator**: Creates target system configuration files
- **Test Generator**: Generates test cases and validation scripts

#### Quality Assurance Agents
Agents focused on validation and quality control:
- **Code Reviewer**: Validates generated code quality and standards compliance
- **Migration Validator**: Ensures migration completeness and accuracy
- **Performance Analyzer**: Assesses performance implications of migrations
- **Security Auditor**: Reviews security aspects of migrated systems

### Agent Configuration

#### Configuration Files
Each agent type has associated configuration files that define:
- **Capabilities**: What the agent can analyze or generate
- **Input Requirements**: Expected input formats and structures
- **Output Specifications**: Generated artifact formats and locations
- **Quality Criteria**: Validation rules and success metrics
- **Integration Points**: How the agent connects with other framework components

#### Prompt Integration
Agents use prompts from the `prompts/` directory to:
- Understand context and requirements
- Process inputs systematically
- Generate consistent outputs
- Maintain quality standards

## Agent Workflows

### Sequential Processing
Agents typically work in coordinated sequences:
1. **Preparation Agents**: Set up analysis environment and validate inputs
2. **Analysis Agents**: Process legacy systems and extract information
3. **Planning Agents**: Create workpackages and migration strategies
4. **Transformation Agents**: Generate target system artifacts
5. **Validation Agents**: Ensure quality and completeness

### Parallel Processing
Some agents can work in parallel for efficiency:
- Multiple analysis agents processing different code modules
- Parallel transformation of independent components
- Concurrent validation of different deliverable types

### Feedback Loops
Agents incorporate feedback mechanisms:
- **Error Correction**: Automatic retry with refined approaches
- **Quality Improvement**: Iterative refinement based on validation results
- **Learning Integration**: Incorporation of lessons learned from previous migrations

## Agent Integration

### Framework Integration
Agents integrate with the migration framework through:
- **Template System**: Use standardized templates for consistent outputs
- **Configuration Management**: Respect project-specific path configurations
- **Validation Framework**: Submit outputs for ACM validation
- **Progress Tracking**: Update status and metrics throughout processing

### Tool Integration
Agents can invoke and integrate with:
- **Static Analysis Tools**: For code quality and complexity analysis
- **Migration Utilities**: For data transformation and validation
- **Testing Frameworks**: For automated testing of migrated components
- **Deployment Tools**: For target system deployment and configuration

## Best Practices

### Agent Development
- **Modularity**: Design agents for specific, well-defined tasks
- **Reusability**: Create agents that can work across different migration projects
- **Configurability**: Allow customization for different legacy technologies and target platforms
- **Observability**: Include comprehensive logging and progress reporting

### Agent Deployment
- **Resource Management**: Consider computational requirements and constraints
- **Scalability**: Design for processing large legacy systems
- **Reliability**: Include error handling and recovery mechanisms
- **Security**: Ensure secure handling of sensitive legacy system information