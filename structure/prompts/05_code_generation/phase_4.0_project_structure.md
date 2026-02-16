# Phase 4.0: Project Structure Establishment

---

## Orchestration Information

**Phase**: Phase 4 - Code Generation
**Step**: Step 4.0 - Project Structure Establishment
**Team Supervisor**: code_generation_team_supervisor
**Assigned Agent**: code_generation_specialist_infrastructure
**Task File Name**: {{TASKS_BASE_PATH}}/phase_4.0_project_structure.md

### Expected Deliverables

1. **Backend Project Structure**
   - Location: {{CODE_GENERATION_BACKEND_OUTPUT}}/
   - Description: Complete backend project scaffolding with build configuration
   - Includes: Maven/Gradle build files, directory structure, configuration templates

2. **Frontend Project Structure**
   - Location: {{CODE_GENERATION_FRONTEND_OUTPUT}}/
   - Description: Complete frontend project scaffolding with build configuration
   - Includes: package.json, vite.config, directory structure, configuration templates

3. **Batch Project Structure**
   - Location: {{CODE_GENERATION_BATCH_OUTPUT}}/
   - Description: Complete batch project scaffolding with build configuration
   - Includes: Build files, job configuration templates, directory structure

4. **Progress Tracking Initialization**
   - File: {{CODE_GENERATION_STATUS}}
   - Template: {{CODE_GENERATION_STATUS_TEMPLATE}}
   - Description: Initial progress tracking with project structure status

5. **Error Reports** (if applicable)
   - File: {{CODE_GENERATION_ERRORS}}
   - Template: {{CODE_GENERATION_ERRORS_TEMPLATE}}
   - Description: Documentation of issues encountered during setup

### Success Criteria
- [ ] Backend project structure created with valid build configuration
- [ ] Frontend project structure created with valid build configuration
- [ ] Batch project structure created with valid build configuration
- [ ] All directories and subdirectories established
- [ ] Configuration templates in place
- [ ] Build files compile/validate successfully
- [ ] Progress tracking initialized with projectStructureEstablished = true
- [ ] All deliverables produced at specified paths
- [ ] Ready for Phase 4.1/4.2/4.3 (Workpackage Code Generation)

---

## Context

### Input Locations
- **Target backend specification**: `{{TARGET_SPECIFICATION}}/02-BACKEND-SPECIFICATION.md`
- **Target frontend specification**: `{{TARGET_SPECIFICATION}}/01-FRONTEND-SPECIFICATION.md`
- **Target batch specification**: `{{TARGET_SPECIFICATION}}/03-BATCH-SPECIFICATION.md`
- **Backend sample code**: `{{TARGET_SAMPLE_CODE}}/backend/`
- **Frontend sample code**: `{{TARGET_SAMPLE_CODE}}/frontend/`
- **Batch sample code**: `{{TARGET_SAMPLE_CODE}}/batch/`
- **Workpackage planning**: `{{WORKPACKAGE_PLANNING}}`

### Output Locations
- **Backend project**: `{{CODE_GENERATION_BACKEND_OUTPUT}}/`
- **Frontend project**: `{{CODE_GENERATION_FRONTEND_OUTPUT}}/`
- **Batch project**: `{{CODE_GENERATION_BATCH_OUTPUT}}/`
- **Progress tracking**: `{{CODE_GENERATION_STATUS}}`
- **Error reports**: `{{CODE_GENERATION_ERRORS}}`
- **Task files location**: `{{TASKS_BASE_PATH}}`

### Template Locations
- **Status template**: `{{CODE_GENERATION_STATUS_TEMPLATE}}`
- **Errors template**: `{{CODE_GENERATION_ERRORS_TEMPLATE}}`

### Previous Phase Artifacts
- **From Phase 3**: Business specifications, test case definitions
- **From Phase 2**: Workpackage planning with dependencies and tier requirements

---

## Objective

Establish the initial project structure for all three tiers (Backend, Frontend, Batch) BEFORE any workpackage-specific code generation begins. Create a solid foundation with proper build configuration, directory structure, and configuration templates that will support workpackage-by-workpackage code generation in subsequent phases.

**CRITICAL**: This phase creates the scaffolding only. No workpackage-specific business logic is implemented here. Focus on project setup, build configuration, and structural templates that will be used by all workpackages.

---

## Instructions

### 1. Preparation
1. Read target specifications to understand framework requirements:
   - Backend specification for framework choice (Spring Boot, Jakarta EE, etc.)
   - Frontend specification for framework choice (React, Vue, Angular, etc.)
   - Batch specification for framework choice (Spring Batch, etc.)

2. Review sample code to understand:
   - Project structure patterns
   - Build configuration patterns
   - Directory organization
   - Configuration file formats

3. Read workpackage planning to understand:
   - How many workpackages will be implemented
   - Which tiers are needed (backend, frontend, batch)
   - Overall project scope

### 2. Backend Project Structure Setup

#### 2.1 Read Backend Specification
1. Open and read `{{TARGET_SPECIFICATION}}/02-BACKEND-SPECIFICATION.md`
2. Extract key information:
   - **Build Tool**: Maven or Gradle
   - **Framework**: Spring Boot, Jakarta EE, etc.
   - **Java Version**: Required Java version
   - **Dependencies**: Core dependencies and versions
   - **Package Structure**: Recommended package organization
   - **Layer Architecture**: Domain, repository, service, API layers

3. Review sample code at `{{TARGET_SAMPLE_CODE}}/backend/` for:
   - Build file examples (pom.xml or build.gradle)
   - Directory structure patterns
   - Configuration file templates
   - Package naming conventions

#### 2.2 Create Backend Directory Structure
Create the following directory structure at `{{CODE_GENERATION_BACKEND_OUTPUT}}/`:

```
backend/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── [base-package]/
│   │   │       ├── domain/          # Domain entities and value objects
│   │   │       ├── repository/      # Data access layer
│   │   │       ├── service/         # Business logic layer
│   │   │       ├── api/             # REST API controllers
│   │   │       │   ├── controller/
│   │   │       │   └── dto/
│   │   │       ├── config/          # Configuration classes
│   │   │       └── exception/       # Exception handling
│   │   └── resources/
│   │       ├── application.yml      # Application configuration
│   │       ├── application-dev.yml  # Development profile
│   │       ├── application-prod.yml # Production profile
│   │       └── db/
│   │           └── migration/       # Database migration scripts
│   └── test/
│       ├── java/
│       │   └── [base-package]/
│       │       ├── domain/
│       │       ├── repository/
│       │       ├── service/
│       │       └── api/
│       └── resources/
├── docs/                            # Backend documentation
└── [build-file]                     # pom.xml or build.gradle
```

**IMPORTANT**: Use the package structure and naming conventions specified in the backend specification. Do not hardcode package names.

#### 2.3 Create Backend Build Configuration
1. If Maven (pom.xml):
   - Reference backend specification for dependencies and versions
   - Include core framework dependencies (Spring Boot, etc.)
   - Include database dependencies (JPA, database driver)
   - Include testing dependencies (JUnit, Mockito, etc.)
   - Configure build plugins
   - Set Java version from specification

2. If Gradle (build.gradle):
   - Reference backend specification for dependencies and versions
   - Include core framework dependencies
   - Include database dependencies
   - Include testing dependencies
   - Configure build tasks
   - Set Java version from specification

**CRITICAL**: Reference the backend specification for exact dependency versions and configurations. Do not embed hardcoded versions.

#### 2.4 Create Backend Configuration Templates
1. Create `application.yml` with placeholders:
   - Server configuration (port, context-path)
   - Database configuration (url, username, password as placeholders)
   - Logging configuration
   - Framework-specific configuration

2. Create profile-specific configurations:
   - `application-dev.yml` for development
   - `application-prod.yml` for production

3. Create configuration class templates if specified in backend specification

### 3. Frontend Project Structure Setup

#### 3.1 Read Frontend Specification
1. Open and read `{{TARGET_SPECIFICATION}}/01-FRONTEND-SPECIFICATION.md`
2. Extract key information:
   - **Framework**: React, Vue, Angular, etc.
   - **Build Tool**: Vite, Webpack, etc.
   - **Node Version**: Required Node.js version
   - **Dependencies**: Core dependencies and versions
   - **Directory Structure**: Recommended organization
   - **Component Architecture**: Pages, components, services, state management

3. Review sample code at `{{TARGET_SAMPLE_CODE}}/frontend/` for:
   - package.json examples
   - Build configuration (vite.config, webpack.config, etc.)
   - Directory structure patterns
   - Configuration file templates

#### 3.2 Create Frontend Directory Structure
Create the following directory structure at `{{CODE_GENERATION_FRONTEND_OUTPUT}}/`:

```
frontend/
├── src/
│   ├── pages/              # Page components
│   ├── components/         # Reusable UI components
│   │   ├── common/         # Common components
│   │   └── layout/         # Layout components
│   ├── services/           # API integration services
│   ├── store/              # State management
│   ├── hooks/              # Custom React hooks (if React)
│   ├── utils/              # Utility functions
│   ├── types/              # TypeScript types/interfaces
│   ├── styles/             # Global styles
│   ├── assets/             # Static assets
│   ├── config/             # Configuration files
│   ├── App.tsx             # Main app component
│   └── main.tsx            # Entry point
├── public/                 # Public assets
├── tests/                  # Test files
│   ├── unit/
│   └── integration/
├── docs/                   # Frontend documentation
├── package.json            # Dependencies and scripts
├── [build-config]          # vite.config.ts, webpack.config.js, etc.
├── tsconfig.json           # TypeScript configuration
└── .env.example            # Environment variables template
```

**IMPORTANT**: Adjust structure based on framework specified in frontend specification (React, Vue, Angular have different conventions).

#### 3.3 Create Frontend Build Configuration
1. Create `package.json`:
   - Reference frontend specification for dependencies and versions
   - Include framework dependencies (React, Vue, Angular)
   - Include build tool dependencies (Vite, Webpack)
   - Include UI library dependencies (if specified)
   - Include testing dependencies (Vitest, Jest, Testing Library)
   - Define scripts (dev, build, test, lint)
   - Set Node version requirement

2. Create build tool configuration:
   - If Vite: Create `vite.config.ts` with plugins and build settings
   - If Webpack: Create `webpack.config.js` with loaders and plugins
   - Reference frontend specification for configuration details

3. Create TypeScript configuration:
   - Create `tsconfig.json` with compiler options
   - Reference frontend specification for TypeScript settings

**CRITICAL**: Reference the frontend specification for exact dependency versions and configurations. Do not embed hardcoded versions.

#### 3.4 Create Frontend Configuration Templates
1. Create `.env.example` with placeholders:
   - API base URL
   - Environment-specific variables
   - Feature flags

2. Create configuration files if specified:
   - Routing configuration template
   - API client configuration template
   - State management setup template

### 4. Batch Project Structure Setup

#### 4.1 Read Batch Specification
1. Open and read `{{TARGET_SPECIFICATION}}/03-BATCH-SPECIFICATION.md`
2. Extract key information:
   - **Framework**: Spring Batch, etc.
   - **Build Tool**: Maven or Gradle
   - **Java Version**: Required Java version
   - **Dependencies**: Core dependencies and versions
   - **Job Structure**: Recommended job organization
   - **Component Architecture**: Readers, processors, writers, listeners

3. Review sample code at `{{TARGET_SAMPLE_CODE}}/batch/` for:
   - Build file examples
   - Directory structure patterns
   - Job configuration templates
   - Component templates

#### 4.2 Create Batch Directory Structure
Create the following directory structure at `{{CODE_GENERATION_BATCH_OUTPUT}}/`:

```
batch/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── [base-package]/
│   │   │       ├── job/             # Job configurations
│   │   │       ├── reader/          # Item readers
│   │   │       ├── processor/       # Item processors
│   │   │       ├── writer/          # Item writers
│   │   │       ├── listener/        # Job/step listeners
│   │   │       ├── tasklet/         # Tasklets
│   │   │       ├── config/          # Batch configuration
│   │   │       └── exception/       # Exception handling
│   │   └── resources/
│   │       ├── application.yml      # Application configuration
│   │       ├── application-dev.yml  # Development profile
│   │       ├── application-prod.yml # Production profile
│   │       └── jobs/                # Job XML configurations (if XML-based)
│   └── test/
│       ├── java/
│       │   └── [base-package]/
│       │       ├── job/
│       │       ├── reader/
│       │       ├── processor/
│       │       └── writer/
│       └── resources/
├── docs/                            # Batch documentation
└── [build-file]                     # pom.xml or build.gradle
```

**IMPORTANT**: Use the package structure and naming conventions specified in the batch specification.

#### 4.3 Create Batch Build Configuration
1. If Maven (pom.xml):
   - Reference batch specification for dependencies and versions
   - Include batch framework dependencies (Spring Batch, etc.)
   - Include database dependencies
   - Include testing dependencies
   - Configure build plugins
   - Set Java version from specification

2. If Gradle (build.gradle):
   - Reference batch specification for dependencies and versions
   - Include batch framework dependencies
   - Include database dependencies
   - Include testing dependencies
   - Configure build tasks
   - Set Java version from specification

**CRITICAL**: Reference the batch specification for exact dependency versions and configurations.

#### 4.4 Create Batch Configuration Templates
1. Create `application.yml` with placeholders:
   - Batch configuration (job repository, transaction manager)
   - Database configuration
   - Scheduling configuration
   - Logging configuration

2. Create profile-specific configurations:
   - `application-dev.yml` for development
   - `application-prod.yml` for production

3. Create batch configuration class templates if specified

### 5. Verify Build Configurations

#### 5.1 Backend Verification
1. Validate build file syntax:
   - If Maven: Ensure pom.xml is well-formed XML
   - If Gradle: Ensure build.gradle has valid syntax

2. Check for required elements:
   - All dependencies from specification are included
   - Build plugins are configured
   - Java version is set correctly
   - Project metadata is complete

3. Verify directory structure:
   - All required directories exist
   - Package structure follows specification
   - Configuration files are in place

#### 5.2 Frontend Verification
1. Validate package.json:
   - Valid JSON syntax
   - All required dependencies included
   - Scripts are defined
   - Node version requirement set

2. Validate build configuration:
   - Build tool config file exists and is valid
   - TypeScript config exists and is valid
   - Configuration follows specification

3. Verify directory structure:
   - All required directories exist
   - Structure follows framework conventions
   - Configuration files are in place

#### 5.3 Batch Verification
1. Validate build file syntax:
   - If Maven: Ensure pom.xml is well-formed XML
   - If Gradle: Ensure build.gradle has valid syntax

2. Check for required elements:
   - All dependencies from specification are included
   - Build plugins are configured
   - Java version is set correctly
   - Batch framework properly configured

3. Verify directory structure:
   - All required directories exist
   - Package structure follows specification
   - Configuration files are in place

### 6. Initialize Progress Tracking

#### 6.1 Create Progress Tracking File
1. Use template from `{{CODE_GENERATION_STATUS_TEMPLATE}}`
2. Create file at `{{CODE_GENERATION_STATUS}}`
3. Initialize with:
   - phaseId: "04-code-generation"
   - status: "in_progress"
   - projectStructureEstablished: true
   - workpackages: [] (empty array, will be populated in Phase 4.1/4.2/4.3)
   - completedCount: 0
   - totalCount: [from workpackage planning]
   - lastUpdated: [current ISO 8601 timestamp]

#### 6.2 Validate Progress Tracking
1. Ensure file is valid JSON
2. Ensure all required fields are present
3. Ensure projectStructureEstablished is set to true

### 7. Create Documentation Stubs

#### 7.1 Backend Documentation
Create `{{CODE_GENERATION_BACKEND_OUTPUT}}/docs/README.md`:
- Project overview
- Build instructions
- Configuration guide
- Architecture overview
- Development guidelines

#### 7.2 Frontend Documentation
Create `{{CODE_GENERATION_FRONTEND_OUTPUT}}/docs/README.md`:
- Project overview
- Build instructions
- Configuration guide
- Component architecture
- Development guidelines

#### 7.3 Batch Documentation
Create `{{CODE_GENERATION_BATCH_OUTPUT}}/docs/README.md`:
- Project overview
- Build instructions
- Configuration guide
- Job architecture
- Development guidelines

### 8. Final Validation

#### 8.1 Completeness Check
Verify all deliverables are created:
- [ ] Backend project structure exists
- [ ] Backend build configuration exists and is valid
- [ ] Frontend project structure exists
- [ ] Frontend build configuration exists and is valid
- [ ] Batch project structure exists
- [ ] Batch build configuration exists and is valid
- [ ] Progress tracking initialized
- [ ] Documentation stubs created

#### 8.2 Quality Check
Verify quality criteria:
- [ ] All paths use {{PATH_VARIABLES}} correctly
- [ ] All configurations reference specifications (not hardcoded)
- [ ] Directory structures follow specification conventions
- [ ] Build files are syntactically valid
- [ ] Configuration templates have appropriate placeholders
- [ ] No workpackage-specific code is included

#### 8.3 Readiness Check
Verify readiness for next phases:
- [ ] Backend structure ready for Phase 4.1 code generation
- [ ] Frontend structure ready for Phase 4.2 code generation
- [ ] Batch structure ready for Phase 4.3 code generation
- [ ] Progress tracking ready to track workpackage completion

### 9. Error Handling and Recovery

#### 9.1 Common Error Scenarios
1. **Missing Target Specifications**
   - Detection: Specification files not found at {{TARGET_SPECIFICATION}}
   - Recovery: Document error in {{CODE_GENERATION_ERRORS}}
   - Escalation: Cannot proceed without specifications - escalate to supervisor

2. **Invalid Sample Code**
   - Detection: Sample code structure doesn't match specification
   - Recovery: Use specification as primary source, sample code as reference only
   - Escalation: Document discrepancy for review

3. **Build Configuration Errors**
   - Detection: Build file syntax errors or missing dependencies
   - Recovery: Validate against specification and correct
   - Escalation: If specification is ambiguous, escalate for clarification

4. **Directory Creation Failures**
   - Detection: Cannot create directories at output paths
   - Recovery: Check path permissions and retry
   - Escalation: If paths are invalid, escalate to supervisor

#### 9.2 Error Reporting
Document all errors in `{{CODE_GENERATION_ERRORS}}` using template:
```json
{
  "phase": "4.0",
  "timestamp": "[ISO 8601]",
  "errorType": "[Error category]",
  "description": "[What went wrong]",
  "impact": "[How this affects next phases]",
  "recoveryAction": "[What was done]",
  "status": "open|resolved",
  "requiresEscalation": true|false
}
```

### 10. Completion and Handoff

#### 10.1 Completion Checklist
Before marking Phase 4.0 complete:
- [ ] All three tier structures created
- [ ] All build configurations valid
- [ ] All configuration templates in place
- [ ] Progress tracking initialized
- [ ] Documentation stubs created
- [ ] No errors or all errors resolved
- [ ] Ready for workpackage code generation

#### 10.2 Handoff to Phase 4.1/4.2/4.3
Provide to supervisor:
- Confirmation that project structure is established
- Location of all created artifacts
- Any warnings or notes for code generation phases
- Confirmation that progress tracking is initialized

---

## Output Format

### Backend Project Structure
**Location**: `{{CODE_GENERATION_BACKEND_OUTPUT}}/`

**Key Files**:
- Build file (pom.xml or build.gradle)
- application.yml and profile configurations
- Directory structure with all required packages
- Documentation stub

### Frontend Project Structure
**Location**: `{{CODE_GENERATION_FRONTEND_OUTPUT}}/`

**Key Files**:
- package.json
- Build configuration (vite.config.ts, etc.)
- tsconfig.json
- .env.example
- Directory structure with all required folders
- Documentation stub

### Batch Project Structure
**Location**: `{{CODE_GENERATION_BATCH_OUTPUT}}/`

**Key Files**:
- Build file (pom.xml or build.gradle)
- application.yml and profile configurations
- Directory structure with all required packages
- Documentation stub

### Progress Tracking
**File**: `{{CODE_GENERATION_STATUS}}`

**Structure**:
```json
{
  "phaseId": "04-code-generation",
  "status": "in_progress",
  "projectStructureEstablished": true,
  "workpackages": [],
  "completedCount": 0,
  "totalCount": 10,
  "lastUpdated": "2026-02-16T10:00:00Z"
}
```

---

## Quality Criteria

### Build Configuration Validity
- Build files are syntactically correct
- All dependencies from specifications are included
- Versions match specification requirements
- Build plugins/tasks are properly configured
- Java/Node versions are correctly set

### Directory Structure Completeness
- All required directories exist
- Package/folder structure follows specification conventions
- No missing directories that would block code generation
- Structure supports all layers/components from specification

### Configuration Template Appropriateness
- Configuration files have appropriate placeholders
- Profile-specific configurations exist
- No hardcoded values that should be parameterized
- Configuration follows specification patterns

### Specification Adherence
- All structure decisions reference specifications
- No arbitrary choices that contradict specifications
- Framework choices match specification requirements
- Architecture patterns follow specification guidance

### Readiness for Code Generation
- Backend structure ready for domain, repository, service, API code
- Frontend structure ready for pages, components, services code
- Batch structure ready for jobs, readers, processors, writers code
- No structural blockers for workpackage implementation

---

## End of Phase 4.0 Document
