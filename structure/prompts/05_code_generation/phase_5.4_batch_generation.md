# Phase 5.4: Batch Code Generation

---

## Orchestration Information

**Phase**: Phase 5 - Code Generation
**Step**: Step 5.4 - Batch Code Generation
**Team Supervisor**: development_team_supervisor
**Assigned Agent**: development_specialist_code_generation
**Task File Name**: {{TASKS_BASE_PATH}}/phase_5.4_batch_generation.md

### Expected Deliverables

1. **Workpackage Batch Module**
   - Location: `{{CODE_GENERATION_BATCH_OUTPUT}}/[module-name]/` (e.g., `user-batch/`, `account-batch/`)
   - Description: Complete batch implementation for ONE workpackage
   - Includes: Job configurations, readers, processors, writers, tasklets

2. **Shared Code** (if needed)
   - Location: `{{CODE_GENERATION_BATCH_OUTPUT}}/shared-common/`
   - Description: Cross-cutting batch code used by multiple workpackages
   - Includes: Common readers, writers, listeners, utilities

3. **Progress Tracking Update**
   - File: {{CODE_GENERATION_STATUS}}
   - Description: Updated progress with batch completion for this workpackage

### Success Criteria
- [ ] Batch module created and integrated into existing project structure
- [ ] All batch requirements implemented
- [ ] Code follows tech spec patterns
- [ ] Code compiles without errors
- [ ] TODOs added for integration points and missing information
- [ ] Progress tracking updated

---

## Context

### Workpackage Context (Provided at Runtime)
- **Workpackage ID**: WP-{ID} (e.g., WP-001)
- **Workpackage Name**: [Name from workpackage planning]

### Input Locations
- **Technical Implementation Guide**: `{{TECH_SPEC_BASE_PATH}}/WP-{ID}-tech-implementation-guide-approved.md`
- **Target Specifications**: `{{TARGET_SPECIFICATION}}/` (batch specs)
- **Database Schemas**: `{{DATABASE_GEN_SRC}}/` (generated database schemas)
- **Business Specification**: `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-{ID}-specification.md`
- **Existing Project**: `{{CODE_GENERATION_BATCH_OUTPUT}}/` (skeleton from Phase 5.1)

### Output Locations
- **Batch module**: `{{CODE_GENERATION_BATCH_OUTPUT}}/[module-name]/`
- **Shared code**: `{{CODE_GENERATION_BATCH_OUTPUT}}/shared-common/`
- **Progress tracking**: `{{CODE_GENERATION_STATUS}}`

---

## Objective

Implement ONE workpackage as a batch module in the existing batch project structure. Create all necessary code (jobs, readers, processors, writers) following the tech spec patterns.

**CRITICAL - MODULE PER WORKPACKAGE**:
- Create ONE module for this workpackage (e.g., `user-batch/`, `account-batch/`)
- Integrate into existing Maven/Gradle multi-module structure
- Put shared/common code in `shared-common/` module
- Follow the project structure from Batch Tech Spec Section 2

**CRITICAL - TODO MARKERS**:
- Add `// TODO:` comments for integration points with other workpackages
- Add `// TODO:` comments for external service integration (file systems, databases, APIs)
- Add `// TODO:` comments for missing information or unclear requirements
- Format: `// TODO: [WP-XXX] Description of what's needed`

---

## Instructions

### 1. Read Specifications

1. **Read Technical Implementation Guide** at `{{TECH_SPEC_BASE_PATH}}/WP-{ID}-tech-implementation-guide-approved.md`
   - Section 1: Overview (workpackage context and scope)
   - Section 2: Backend Implementation (may include batch-related entities)
   - Section 3: Data Model (database schema, relationships)
   - Section 5: Business Logic (rules, validations, transformations for batch)
   - Section 6: Integration Points (dependencies on other workpackages)
   - Section 8: Batch Processing (if applicable - job definitions, scheduling)
   - Section 9: Implementation Tasks (step-by-step guidance)

2. **Read Target Batch Specification** at `{{TARGET_SPECIFICATION}}/batch/`
   - Project structure patterns
   - Batch framework and patterns
   - Job configuration standards
   - Scheduling approach

3. **Read Database Schemas** at `{{DATABASE_GEN_SRC}}/`
   - Entity definitions and relationships (from `new_sqlite_ddl.sql` if available)
   - Table structures for batch processing
   - Indexes and performance considerations

4. **Read Business Specification** at `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-{ID}-specification.md`
   - Chapter 2: Business Entities (what data to process)
   - Chapter 3: Business Rules (what transformations to apply)
   - Chapter 4: Business Operations (what batch processes to create)

### 2. Determine Module Structure

Based on Technical Implementation Guide Section 8 and Target Batch Specification, determine the module structure:

**CRITICAL - Module Naming Decision**:

**If this workpackage belongs to an EXISTING business domain** (e.g., WP-002 "User Profile Import" and WP-001 "User Authentication Import" both belong to "User Management"):
- ✅ **Use the SAME module** (e.g., `user-batch`)
- Create separate packages within the module for each workpackage
- Example:
  ```
  user-batch/
  ├── config/
  │   ├── AuthenticationBatchConfig.java    # WP-001
  │   └── ProfileBatchConfig.java           # WP-002
  ├── job/
  │   ├── authentication/                   # WP-001
  │   │   └── UserAuthenticationImportJob.java
  │   └── profile/                          # WP-002
  │       └── UserProfileImportJob.java
  ├── reader/
  │   ├── authentication/                   # WP-001
  │   └── profile/                          # WP-002
  ├── processor/
  │   ├── authentication/                   # WP-001
  │   └── profile/                          # WP-002
  └── writer/
      ├── authentication/                   # WP-001
      └── profile/                          # WP-002
  ```

**If this workpackage is a NEW business domain**:
- ✅ **Create a NEW module** (e.g., `account-batch`, `transaction-batch`)

**How to decide**:
1. Check if a batch module already exists for this business domain
2. If yes: Add to existing module in a new package
3. If no: Create new module

**Example - Maven Multi-Module**:
```
batch/
├── pom.xml (parent)
├── shared-common/          # Shared code
│   ├── reader/
│   ├── writer/
│   ├── listener/
│   └── util/
├── user-batch/             # Domain: User Management
│   ├── pom.xml
│   ├── config/
│   ├── job/
│   │   ├── authentication/ # WP-001: User Authentication Import
│   │   └── profile/        # WP-002: User Profile Import
│   ├── reader/
│   │   ├── authentication/ # WP-001
│   │   └── profile/        # WP-002
│   ├── processor/
│   │   ├── authentication/ # WP-001
│   │   └── profile/        # WP-002
│   └── writer/
│       ├── authentication/ # WP-001
│       └── profile/        # WP-002
├── account-batch/          # Domain: Account Management
│   └── ...                 # WP-003: Account Import
└── application/            # Main app (already exists from Phase 5.1)
```

**Module naming**: Use business domain name + "-batch" (e.g., `user-batch`, `account-batch`, `transaction-batch`), NOT workpackage ID

### 3. Create or Update Module Structure

**If module DOES NOT exist** (new business domain):

1. **Create module directory**: `{{CODE_GENERATION_BATCH_OUTPUT}}/[module-name]/`

2. **Create module build file**: `pom.xml` or `build.gradle` in module directory
   - Add module dependencies (shared-common, spring-boot-starter-batch, etc.)
   - Follow dependency patterns from Technical Implementation Guide Section 8

3. **Create package structure** according to Technical Implementation Guide Section 8:
   - `config/` - Job and step configurations
   - `job/[wp-feature]/` - Job definitions for this WP
   - `reader/[wp-feature]/` - ItemReader implementations for this WP
   - `processor/[wp-feature]/` - ItemProcessor implementations for this WP
   - `writer/[wp-feature]/` - ItemWriter implementations for this WP

4. **Update parent build file**: Add new module to parent pom.xml `<modules>` section

**If module ALREADY EXISTS** (same business domain as previous WP):

1. **Navigate to existing module**: `{{CODE_GENERATION_BATCH_OUTPUT}}/[module-name]/`

2. **Create workpackage-specific packages**:
   - `job/[wp-feature]/` - Job definitions for this WP
   - `reader/[wp-feature]/` - Readers for this WP
   - `processor/[wp-feature]/` - Processors for this WP
   - `writer/[wp-feature]/` - Writers for this WP

3. **Add configuration class** in `config/` directory for this WP's jobs

4. **Update module build file** (if new dependencies needed)

5. **DO NOT update parent build file** (module already registered)

**Example - Adding WP-002 to existing user-batch module**:
```
user-batch/
├── pom.xml (already exists)
├── config/
│   ├── AuthenticationBatchConfig.java  # WP-001 (already exists)
│   └── ProfileBatchConfig.java         # WP-002 (NEW - add this)
├── job/
│   ├── authentication/                 # WP-001 (already exists)
│   │   └── UserAuthImportJob.java
│   └── profile/                        # WP-002 (NEW - add this)
│       └── UserProfileImportJob.java
├── reader/
│   ├── authentication/                 # WP-001 (already exists)
│   └── profile/                        # WP-002 (NEW - add this)
│       └── UserProfileFileReader.java
├── processor/
│   ├── authentication/                 # WP-001 (already exists)
│   └── profile/                        # WP-002 (NEW - add this)
│       └── UserProfileProcessor.java
└── writer/
    ├── authentication/                 # WP-001 (already exists)
    └── profile/                        # WP-002 (NEW - add this)
        └── UserProfileDatabaseWriter.java
```

### 4. Implement Job Configuration

From Technical Implementation Guide Section 8 and Business Specification:

1. **Read job configuration patterns from Technical Implementation Guide and Target Batch Specification**:
   - How to define job configurations
   - How to define step configurations
   - How to wire readers, processors, writers
   - How to configure chunk size, listeners, etc.
   - Where to place configuration classes (package structure)

2. **Read batch requirements**:
   - Business Specification Chapter 4: Batch operations and requirements

3. **Create job configuration** following the tech spec patterns:
   - Place in the location specified by tech spec
   - Define job as specified
   - Define steps as specified
   - Wire readers, processors, writers as specified
   - Configure chunk size, listeners, etc. as specified

4. **Add TODOs for integration with other workpackages**:
   ```
   // Example (syntax will vary by batch framework):
   // TODO: [WP-002] Add account import step when account-batch module exists
   
   // TODO: [MISSING-INFO] Confirm chunk size and retry policy
   ```

### 5. Implement ItemReader

From Technical Implementation Guide Section 8 and Database Schemas:

1. **Read reader patterns from Technical Implementation Guide and Target Batch Specification**:
   - How to create reader classes
   - How to read from file, database, or API
   - How to parse/map input data
   - How to handle errors
   - Where to place reader classes (package structure)

2. **Read data source information**:
   - Technical Implementation Guide Section 3: Data model and sources
   - Database Schemas at `{{DATABASE_GEN_SRC}}/`: Entity definitions (check for `new_sqlite_ddl.sql`)
   - Business Specification: Input data format and location

3. **Create reader class** following the implementation guide patterns:
   - Place in the location specified by tech spec
   - Read from source as specified
   - Parse/map input data as specified
   - Handle errors as specified

4. **Add TODOs for external sources**:
   ```
   // Example (syntax will vary by batch framework):
   // TODO: [CONFIG] Add input file path to application configuration
   
   // TODO: [EXTERNAL] Integrate with S3 for file storage
   // Currently reading from local filesystem
   
   // TODO: [MISSING-INFO] Confirm file format (CSV, JSON, XML?)
   ```

### 6. Implement ItemProcessor

From Technical Implementation Guide Section 5 and Business Specification:

1. **Read processor patterns from Technical Implementation Guide and Target Batch Specification**:
   - How to create processor classes
   - How to apply business logic
   - How to transform data
   - How to validate data
   - How to enrich data
   - Where to place processor classes (package structure)

2. **Read business rules**:
   - Technical Implementation Guide Section 5: Business logic implementation guidance
   - Business Specification Chapter 3: Business rules to apply

3. **Create processor class** following the implementation guide patterns:
   - Place in the location specified by tech spec
   - Apply business logic as specified
   - Transform data as specified
   - Validate data as specified
   - Enrich data as specified

4. **Add TODOs for integration points**:
   ```
   // Example (syntax will vary by batch framework):
   // TODO: [VALIDATION] Add validation rules from business spec
   
   // TODO: [WP-003] Lookup user preferences when preference-batch exists
   
   // TODO: [EXTERNAL] Validate email with external service
   
   // TODO: [MISSING-INFO] Confirm data transformation rules
   ```

### 7. Implement ItemWriter

From Technical Implementation Guide Section 8 and Database Schemas:

1. **Read writer patterns from Technical Implementation Guide and Target Batch Specification**:
   - How to create writer classes
   - How to write to database, file, or API
   - How to handle batch inserts
   - How to handle errors
   - Where to place writer classes (package structure)

2. **Create writer class** following the tech spec patterns:
   - Place in the location specified by tech spec
   - Write to destination as specified
   - Handle batch inserts as specified
   - Handle errors as specified

3. **Add TODOs for integration points**:
   ```
   // Example (syntax will vary by batch framework):
   // TODO: [PERFORMANCE] Consider batch insert optimization
   
   // TODO: [WP-002] Update related accounts when account-batch exists
   
   // TODO: [EXTERNAL] Send notification to external system
   
   // TODO: [MISSING-INFO] Confirm error handling strategy
   ```

### 8. Implement Job Listeners (Optional)

For monitoring and logging:

1. **Read listener patterns from Technical Implementation Guide and Target Batch Specification**:
   - How to create listener classes
   - What listener interfaces to implement
   - Where to place listener classes (package structure)

2. **Create listener classes** following the tech spec patterns (if needed):
   - Place in the location specified by tech spec
   - Implement before/after job logic
   - Implement before/after step logic

3. **Add TODOs for external integrations**:
   ```
   // Example (syntax will vary by batch framework):
   // TODO: [EXTERNAL] Send job start notification
   
   // TODO: [EXTERNAL] Send job completion notification
   
   // TODO: [MISSING-INFO] Confirm reporting requirements
   ```

### 9. Handle Scheduling

From Technical Implementation Guide Section 8 and Target Batch Specification:

1. **Read scheduling patterns from Technical Implementation Guide and Target Batch Specification**:
   - How to configure job scheduling
   - What scheduling mechanism to use
   - Where to place scheduler configuration

2. **Create scheduler configuration** (if needed) following the tech spec patterns:
   - Place in the location specified by tech spec
   - Configure schedule as specified
   - Configure trigger conditions as specified

3. **Add TODOs for configuration**:
   ```
   // Example (syntax will vary by scheduling framework):
   // TODO: [CONFIG] Add cron expression to application configuration
   
   // TODO: [MISSING-INFO] Confirm schedule and trigger conditions
   ```

### 10. Handle Shared Code

If code is needed by multiple batch workpackages:

1. **Identify shared code**:
   - Common readers (CSV reader, JSON reader, etc.)
   - Common writers (Database writer, File writer, etc.)
   - Common listeners
   - Common utilities

2. **Read shared code patterns from Technical Implementation Guide and Target Batch Specification**:
   - Where to place shared code (shared-common module, base package, etc.)
   - How to organize shared code

3. **Create in shared location** as specified by tech spec:
   - Follow the project structure from tech spec
   - Use naming conventions from tech spec

4. **Add TODOs for configuration**:
   ```
   // Example (syntax will vary by batch framework):
   // TODO: [CONFIG] Add CSV parsing configuration
   ```

### 11. Update Progress Tracking

Update `{{CODE_GENERATION_STATUS}}`:

```json
{
  "phase": "Phase 5 - Code Generation",
  "currentStep": "5.4 - Batch Generation",
  "workpackages": {
    "WP-{ID}": {
      "status": "completed",
      "batch": {
        "moduleCreated": true,
        "moduleName": "[batch-module-name]",
        "jobsCount": 1,
        "stepsCount": 1,
        "readersCount": 1,
        "processorsCount": 1,
        "writersCount": 1,
        "todosCount": 12,
        "compiles": true
      }
    }
  }
}
```

---

## TODO Marker Guidelines

**When to add TODOs**:
1. **Integration with other workpackages**: When batch job needs data from other WP batch jobs
2. **External system integration**: When job needs to read from/write to external systems (S3, FTP, APIs)
3. **Missing information**: When business spec is unclear about batch requirements
4. **Configuration needed**: When job parameters, schedules, or settings are needed
5. **Performance optimization**: When batch performance needs tuning

**TODO format**:
```java
// TODO: [CATEGORY] Description
// Categories: WP-XXX, EXTERNAL, MISSING-INFO, CONFIG, PERFORMANCE
```

**Examples**:
```java
// TODO: [WP-002] Process accounts after users when account-batch exists
// TODO: [EXTERNAL] Read files from S3 instead of local filesystem
// TODO: [MISSING-INFO] Confirm chunk size and commit interval
// TODO: [CONFIG] Add database connection pool size for batch
// TODO: [PERFORMANCE] Optimize bulk insert for large datasets
```

---

## Verification

Before marking complete:
1. ✅ Module compiles without errors
2. ✅ Module is integrated into parent build
3. ✅ All batch jobs from business spec are created
4. ✅ All readers, processors, writers are implemented
5. ✅ Job configuration is complete
6. ✅ TODOs are added for all integration points
7. ✅ Code follows naming conventions from tech spec
8. ✅ Job can be executed (even if it processes no data yet)

---

## End of Phase 5.4

The workpackage batch module is now complete and integrated into the project. Move to next workpackage.
