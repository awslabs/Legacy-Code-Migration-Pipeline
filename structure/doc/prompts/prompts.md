# Prompts Documentation

This directory contains AI prompts organized by migration phases. These prompts guide AI agents through systematic analysis and migration tasks, ensuring consistent and thorough processing of legacy systems.

## Prompt Structure

Prompts are organized into sequential phases that build upon each other:

### Phase 00: Preparation
**Directory: `00_preparation/`**

Initial setup and preparation prompts that establish the foundation for migration analysis:
- Environment setup validation
- Source code inventory and cataloging
- Initial assessment and scoping
- Prerequisite verification

### Phase 01: Analysis
**Directory: `01_analysis/`**

Deep analysis prompts for understanding the legacy system:
- Source code structure analysis
- Business logic extraction
- Data flow analysis
- Dependency mapping
- Technology stack assessment
- Performance characteristics analysis

### Phase 02: Workpackage Definition
**Directory: `02_workpackage/`**

Prompts for breaking down the migration into manageable workpackages:
- Functional decomposition
- Dependency analysis
- Risk assessment
- Effort estimation
- Priority assignment
- Resource allocation planning

### Phase 03: Specification
**Directory: `03_specification/`**

Detailed specification prompts for target system design:
- Architecture specification
- API design
- Data model design
- Integration requirements
- Non-functional requirements
- Migration strategy definition

### Phase 04: Code Generation
**Directory: `04_code_generation/`**

Prompts for generating modern code from legacy systems:
- Code transformation rules
- Pattern mapping
- Quality assurance checks
- Testing strategy
- Deployment planning
- Rollback procedures

## Usage Guidelines

### Sequential Processing
Prompts should generally be executed in phase order, as later phases depend on outputs from earlier phases.

### Customization
Prompts can be customized for specific:
- Legacy technologies (COBOL, PL/I, etc.)
- Target platforms (.NET, Java, Python, etc.)
- Business domains
- Organizational requirements

### Integration with Templates
Prompts are designed to work with the template system, generating outputs that populate the standardized templates in the `templates/` directory.

### AI Agent Configuration
Each prompt includes:
- Context requirements
- Expected input formats
- Output specifications
- Quality criteria
- Validation checkpoints