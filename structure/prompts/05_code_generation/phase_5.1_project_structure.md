# Phase 5.1: Project Structure Establishment

---

## Orchestration Information

**Phase**: Phase 5 - Code Generation
**Step**: Step 5.1 - Project Structure Establishment
**Team Supervisor**: development_team_supervisor
**Assigned Agent**: development_specialist_code_generation
**Task File Name**: {{TASKS_BASE_PATH}}/phase_5.1_project_structure.md

### Expected Deliverables

1. **Backend Project Skeleton**
   - Location: {{CODE_GENERATION_BACKEND_OUTPUT}}/
   - Description: Bare minimum backend project structure with build configuration

2. **Frontend Project Skeleton**
   - Location: {{CODE_GENERATION_FRONTEND_OUTPUT}}/
   - Description: Bare minimum frontend project structure with build configuration

3. **Batch Project Skeleton**
   - Location: {{CODE_GENERATION_BATCH_OUTPUT}}/
   - Description: Bare minimum batch project structure with build configuration

4. **Progress Tracking**
   - File: {{CODE_GENERATION_STATUS}}
   - Description: Initial progress tracking with project structure status

### Success Criteria
- [ ] Backend skeleton created with valid build configuration
- [ ] Frontend skeleton created with valid build configuration
- [ ] Batch skeleton created with valid build configuration
- [ ] Build files compile/validate successfully
- [ ] Applications can start (but do nothing)
- [ ] Progress tracking initialized
- [ ] Ready for workpackage code generation

---

## Context

### Input Locations
- **Backend Tech Spec**: `{{TECH_SPEC_BACKEND}}`
- **Frontend Tech Spec**: `{{TECH_SPEC_FRONTEND}}`
- **Batch Tech Spec**: `{{TECH_SPEC_BATCH}}`
- **Infrastructure Tech Spec**: `{{TECH_SPEC_INFRASTRUCTURE}}`

### Output Locations
- **Backend project**: `{{CODE_GENERATION_BACKEND_OUTPUT}}/`
- **Frontend project**: `{{CODE_GENERATION_FRONTEND_OUTPUT}}/`
- **Batch project**: `{{CODE_GENERATION_BATCH_OUTPUT}}/`
- **Progress tracking**: `{{CODE_GENERATION_STATUS}}`

---

## Objective

Create ONLY the bare skeleton project structure for backend, frontend, and batch tiers. This is the absolute minimum needed to have compilable, runnable (but empty) applications.

**CRITICAL - SKELETON ONLY**:
- ✅ Create: Root folders, build files, base config, main entry point
- ❌ Don't create: Business modules, domain packages, feature folders, any business code

**Think of it as**: Creating a brand new project with `spring initializr`, `create-react-app`, or `npm create vite@latest` - you get the basic structure, but no features yet.

**Business modules and packages will be added incrementally in Phase 5.2/5.3/5.4 as each workpackage is implemented.**

---

## Instructions

### 1. Backend Project Skeleton

1. **Read the Backend Tech Spec** at `{{TECH_SPEC_BACKEND}}`

2. **Extract key information**:
   - Section 1: Technology Stack (framework, language, build tool, database)
   - Section 3: Dependencies (what to include in build file)
   - Section 4: Configuration (application.yml structure)

3. **Create the skeleton**:
   - Create ROOT directory structure only:
     ```
     backend/
     ├── pom.xml (or build.gradle)
     ├── src/
     │   ├── main/
     │   │   ├── java/
     │   │   │   └── com/company/app/
     │   │   │       └── Application.java
     │   │   └── resources/
     │   │       └── application.yml
     │   └── test/
     │       └── java/
     ```
   - Create build file with ALL dependencies from Section 3
   - Create Application.java with @SpringBootApplication (or equivalent main class)
   - Create application.yml with base configuration from Section 4
   - **DO NOT create**: Business module directories, domain packages, entities, repositories, services, controllers

4. **Verify**:
   - Build file is valid (mvn validate or gradle build --dry-run)
   - Application can compile
   - Application can start (and immediately stop - no endpoints yet)

### 2. Frontend Project Skeleton

1. **Read the Frontend Tech Spec** at `{{TECH_SPEC_FRONTEND}}`

2. **Extract key information**:
   - Section 1: Technology Stack (framework, language, build tool)
   - Section 3: Dependencies (package.json dependencies)
   - Section 4: Configuration (config files)

3. **Create the skeleton**:
   - Create ROOT directory structure only:
     ```
     frontend/
     ├── package.json
     ├── vite.config.ts (or equivalent)
     ├── tsconfig.json
     ├── index.html
     └── src/
         └── main.tsx (or main.js)
     ```
   - Create package.json with ALL dependencies from Section 3
   - Create build configuration files from Section 4
   - Create index.html with root div
   - Create main.tsx with minimal app initialization (renders "Hello World" or empty div)
   - **DO NOT create**: components/, pages/, services/, store/, any feature folders

4. **Verify**:
   - package.json is valid JSON
   - npm install (or yarn install) works
   - Application can build (npm run build)
   - Application can start in dev mode (npm run dev)

### 3. Batch Project Skeleton

1. **Read the Batch Tech Spec** at `{{TECH_SPEC_BATCH}}`

2. **Extract key information**:
   - Section 1: Technology Stack (framework, language, build tool)
   - Section 3: Dependencies (what to include in build file)
   - Section 4: Configuration (batch configuration structure)

3. **Create the skeleton**:
   - Create ROOT directory structure only:
     ```
     batch/
     ├── pom.xml (or build.gradle)
     ├── src/
     │   ├── main/
     │   │   ├── java/
     │   │   │   └── com/company/batch/
     │   │   │       └── BatchApplication.java
     │   │   └── resources/
     │   │       └── application.yml
     │   └── test/
     │       └── java/
     ```
   - Create build file with ALL dependencies from Section 3
   - Create BatchApplication.java with @SpringBootApplication @EnableBatchProcessing (or equivalent)
   - Create application.yml with base batch configuration from Section 4
   - **DO NOT create**: Job directories, reader/writer/processor packages, any job definitions

4. **Verify**:
   - Build file is valid
   - Application can compile
   - Application can start (no jobs defined yet)

### 4. Update Progress Tracking

Create `{{CODE_GENERATION_STATUS}}` with:

```json
{
  "phase": "Phase 5 - Code Generation",
  "currentStep": "5.1 - Project Structure",
  "status": "completed",
  "projectStructureEstablished": true,
  "timestamp": "[ISO 8601 timestamp]",
  "tiers": {
    "backend": {
      "skeletonCreated": true,
      "buildFileValid": true,
      "canCompile": true,
      "canStart": true,
      "location": "{{CODE_GENERATION_BACKEND_OUTPUT}}"
    },
    "frontend": {
      "skeletonCreated": true,
      "buildFileValid": true,
      "canBuild": true,
      "canStart": true,
      "location": "{{CODE_GENERATION_FRONTEND_OUTPUT}}"
    },
    "batch": {
      "skeletonCreated": true,
      "buildFileValid": true,
      "canCompile": true,
      "canStart": true,
      "location": "{{CODE_GENERATION_BATCH_OUTPUT}}"
    }
  }
}
```

---

## Important Notes - SKELETON ONLY

**What to create**:
- Root directory structure (src/main/java, src/main/resources, src/test/java, etc.)
- Build files (pom.xml, package.json, etc.) with ALL dependencies
- Base configuration files (application.yml, vite.config.ts, tsconfig.json, etc.)
- Main application entry point (Application.java, main.tsx, etc.)
- Minimal code to make the project compile and start (but do nothing)

**What NOT to create**:
- Business module directories (user-module, account-module, etc.)
- Domain packages (domain/, data/, api/, service/, repository/)
- Feature folders (components/, pages/, services/, store/)
- Business-specific packages or folders
- Any entities, repositories, services, controllers, components
- Any batch jobs, readers, writers, processors
- Any tests (except maybe one smoke test to verify skeleton works)

**Why**: Business modules and packages will be created incrementally in Phase 5.2/5.3/5.4 as each workpackage is implemented. This phase creates only the foundation that all workpackages will build upon.

**Example - Backend**:
```
✅ Create:
backend/
├── pom.xml                          # With ALL dependencies
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/company/app/
│   │   │       └── Application.java # Main class only
│   │   └── resources/
│   │       └── application.yml      # Base config
│   └── test/
│       └── java/

❌ Don't create:
backend/
├── user-module/                     # NO business modules yet
├── account-module/                  # NO business modules yet
└── src/main/java/com/company/app/
    ├── domain/                      # NO domain packages yet
    ├── repository/                  # NO repository packages yet
    └── service/                     # NO service packages yet
```

**Example - Frontend**:
```
✅ Create:
frontend/
├── package.json                     # With ALL dependencies
├── vite.config.ts                   # Build config
├── tsconfig.json                    # TypeScript config
├── index.html                       # Entry HTML
└── src/
    └── main.tsx                     # Entry point only (Hello World)

❌ Don't create:
frontend/
└── src/
    ├── components/                  # NO feature folders yet
    ├── pages/                       # NO feature folders yet
    ├── services/                    # NO feature folders yet
    └── store/                       # NO feature folders yet
```

---

## Error Handling

If information is missing from tech specs:
1. Document the missing information in `{{CODE_GENERATION_ERRORS}}`
2. Use reasonable defaults based on the framework
3. Continue with skeleton setup
4. Flag for review

Example error entry:
```json
{
  "phase": "5.1",
  "tier": "backend",
  "issue": "Database connection pool size not specified",
  "resolution": "Used default HikariCP settings",
  "requiresReview": false
}
```

---

## End of Phase 5.1

Once complete, the skeleton is ready for workpackage-by-workpackage code generation in phases 5.2, 5.3, and 5.4.
