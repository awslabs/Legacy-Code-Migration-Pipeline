# Input Structure Documentation

This directory contains all source materials and specifications needed for the migration process. The input structure is organized to separate legacy materials from target specifications and guidance documents.

## Integration with Orchestration Architecture

Input paths are configured in `config/paths.cfg` and resolved in prompts using `{{PARAMETER}}` placeholders. When team supervisors create task files, they resolve these parameters to absolute paths that specialists can use directly.

For example:
- Phase prompt: `{{LEGACY_SOURCE_CODE}}`
- Task file: `/absolute/path/to/project/input/legacy/source`

This ensures agents receive complete, resolved paths without needing to interpret configuration files.

## Directory Structure

### Legacy Materials (`legacy/`)

Contains all materials from the existing legacy system:

#### `legacy_code/`
- Source code files (COBOL, PL/I, JCL, etc.)
- Include files and copybooks
- Configuration files
- Build scripts and procedures

#### `database/`
- Database schemas (DDL)
- Data definitions
- Stored procedures and functions
- Database configuration files
- Sample data exports

#### `specifications/`
- Original system documentation
- Business requirements documents
- Technical specifications
- User manuals
- System architecture documents

### Target Specifications (`target/`)

Contains specifications and requirements for the target system:

#### `specifications/`
- Target architecture requirements
- Technology stack specifications
- Performance requirements
- Security requirements
- Integration specifications

#### `sample_code/`
- Reference implementations
- Code examples for target platform
- Best practice samples
- Pattern libraries

### Migration Guidance (`guidance/`)

Contains guidance documents and standards for the migration:
- Migration standards and guidelines
- Coding conventions for target platform
- Architecture patterns and principles
- Quality assurance criteria
- Testing strategies

## File Organization Best Practices

### Naming Conventions
- Use descriptive, consistent naming
- Include version information where applicable
- Maintain original file extensions for legacy code
- Use standard extensions for documentation (.md, .pdf, .docx)

### Directory Structure
- Group related files together
- Maintain logical hierarchy
- Separate different types of artifacts
- Use subdirectories for large collections

### Documentation Requirements
- Include README files in major directories
- Document file purposes and relationships
- Maintain change logs for updated materials
- Include contact information for subject matter experts

## Integration with Analysis

The input structure is designed to support the orchestration architecture:
- File paths are configurable via `config/paths.cfg`
- Paths are resolved in phase prompts using `{{PARAMETERS}}`
- Team supervisors resolve paths when creating task files
- Specialists receive absolute paths in task files
- Analysis tools scan these directories systematically
- Results are cross-referenced with input materials
- Traceability is maintained throughout the process

For more information on how paths flow through the orchestration architecture, see [Orchestration Architecture Documentation](../orchestration_architecture.md)