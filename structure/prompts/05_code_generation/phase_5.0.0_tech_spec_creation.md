# Phase 5.0.0: Technical Specification Creation

---

## Orchestration Information

**Phase**: Phase 5.0.0 - Technical Specification Creation  
**Team Supervisor**: tech_spec_extraction_supervisor  
**Assigned Agent**: tech_spec_extraction_specialist  
**Task File Name**: {{TASKS_BASE_PATH}}/phase_5.0.0_tech_spec_creation.md

### Expected Deliverables

1. **Migration Mapping Specification** (NEW - CRITICAL)
   - Location: {{TECH_SPEC_MIGRATION_MAPPING}}
   - Template: {{TECH_SPEC_MIGRATION_MAPPING_TEMPLATE}}
   - Description: Bridge document mapping Chapter 6 legacy patterns to modern implementations
   - Priority: CREATE THIS FIRST - all other specs depend on it

2. **Backend Technical Specification**
   - Location: {{TECH_SPEC_BACKEND}}
   - Template: {{TECH_SPEC_BACKEND_TEMPLATE}}
   - Description: Complete backend technical specification with all discoverable details

3. **Frontend Technical Specification**
   - Location: {{TECH_SPEC_FRONTEND}}
   - Template: {{TECH_SPEC_FRONTEND_TEMPLATE}}
   - Description: Complete frontend technical specification with all discoverable details

4. **Batch Technical Specification**
   - Location: {{TECH_SPEC_BATCH}}
   - Template: {{TECH_SPEC_BATCH_TEMPLATE}}
   - Description: Complete batch technical specification with all discoverable details

5. **Infrastructure Technical Specification**
   - Location: {{TECH_SPEC_INFRASTRUCTURE}}
   - Template: {{TECH_SPEC_INFRASTRUCTURE_TEMPLATE}}
   - Description: Complete infrastructure technical specification with all discoverable details

6. **Progress Tracking**
   - File: {{TECH_SPEC_STATUS}}
   - Template: {{TECH_SPEC_STATUS_TEMPLATE}}
   - Description: Progress tracking with extraction status

7. **Progress Report**
   - File: {{TECH_SPEC_PROGRESS}}
   - Template: {{TECH_SPEC_PROGRESS_TEMPLATE}}
   - Description: Human-readable progress report

8. **Error Log** (if applicable)
   - File: {{TECH_SPEC_ERRORS}}
   - Template: {{TECH_SPEC_ERRORS_TEMPLATE}}
   - Description: Documentation of issues encountered

### Success Criteria
- [ ] Migration Mapping Specification created FIRST
- [ ] All cross-cutting patterns documented in Migration Mapping
- [ ] All workpackage-specific mappings documented in Migration Mapping
- [ ] All four technical specifications created
- [ ] All required sections populated with discovered information
- [ ] Source references documented for all information
- [ ] Assumptions documented where specifications unclear
- [ ] Code examples included from sample code
- [ ] No critical errors
- [ ] Progress tracking updated
- [ ] Ready for Phase 5.0.1 (Review)

---

## Context

### Input Locations
- **Target backend specification**: `{{TARGET_SPECIFICATION}}/02-BACKEND-SPECIFICATION.md`
- **Target frontend specification**: `{{TARGET_SPECIFICATION}}/01-FRONTEND-SPECIFICATION.md`
- **Target batch specification**: `{{TARGET_SPECIFICATION}}/03-BATCH-SPECIFICATION.md`
- **Target common specification**: `{{TARGET_SPECIFICATION}}/00-COMMON-SPECIFICATION.md`
- **Business specifications**: `{{BUSINESS_SPECIFICATION_BASE_PATH}}/` (for Chapter 6 references)
- **Workpackage planning**: `{{WORKPACKAGE_PLANNING}}`
- **Backend sample code**: `{{TARGET_SAMPLE_CODE}}/backend/`
- **Frontend sample code**: `{{TARGET_SAMPLE_CODE}}/frontend/`
- **Batch sample code**: `{{TARGET_SAMPLE_CODE}}/batch/`

### Output Locations
- **Migration Mapping spec**: `{{TECH_SPEC_MIGRATION_MAPPING}}`
- **Backend tech spec**: `{{TECH_SPEC_BACKEND}}`
- **Frontend tech spec**: `{{TECH_SPEC_FRONTEND}}`
- **Batch tech spec**: `{{TECH_SPEC_BATCH}}`
- **Infrastructure tech spec**: `{{TECH_SPEC_INFRASTRUCTURE}}`
- **Progress tracking**: `{{TECH_SPEC_STATUS}}`
- **Progress report**: `{{TECH_SPEC_PROGRESS}}`
- **Error log**: `{{TECH_SPEC_ERRORS}}`

### Template Locations
- **Migration Mapping template**: `{{TECH_SPEC_MIGRATION_MAPPING_TEMPLATE}}`
- **Backend template**: `{{TECH_SPEC_BACKEND_TEMPLATE}}`
- **Frontend template**: `{{TECH_SPEC_FRONTEND_TEMPLATE}}`
- **Batch template**: `{{TECH_SPEC_BATCH_TEMPLATE}}`
- **Infrastructure template**: `{{TECH_SPEC_INFRASTRUCTURE_TEMPLATE}}`
- **Status template**: `{{TECH_SPEC_STATUS_TEMPLATE}}`
- **Progress template**: `{{TECH_SPEC_PROGRESS_TEMPLATE}}`
- **Errors template**: `{{TECH_SPEC_ERRORS_TEMPLATE}}`

---

## Objective

Extract and document ALL technical implementation details from customer specifications and sample code. Create structured, implementation-ready technical specifications that will be the single source of truth for all code generation phases.

**CRITICAL PRINCIPLES**:
1. **Discovery-Based**: Do NOT assume or hardcode any details - discover everything
2. **Keyword-Based Search**: Use keyword search to find information (no section number assumptions)
3. **Flexible**: Work with ANY specification structure
4. **Traceable**: Document source of every piece of information
5. **Assumption Documentation**: Document all assumptions when specifications unclear
6. **Sample Code Fallback**: Use sample code when specifications insufficient

---

## Instructions

### CRITICAL: CREATE MIGRATION MAPPING SPECIFICATION FIRST

The Migration Mapping Specification is the MOST IMPORTANT deliverable. It bridges Chapter 6 of business specifications (legacy patterns) with target technical specifications (modern patterns). All code generation phases depend on this document.

**Creation Order**:
1. Migration Mapping Specification (FIRST - highest priority)
2. Backend Technical Specification
3. Frontend Technical Specification
4. Batch Technical Specification
5. Infrastructure Technical Specification

---

### DISCOVERY-BASED APPROACH

You will discover ALL technical details through keyword-based search. Do NOT assume any specification structure or section numbering.

### 1. Initialize Progress Tracking

1. Copy {{TECH_SPEC_STATUS_TEMPLATE}} to {{TECH_SPEC_STATUS}}
2. Copy {{TECH_SPEC_PROGRESS_TEMPLATE}} to {{TECH_SPEC_PROGRESS}}
3. Copy {{TECH_SPEC_ERRORS_TEMPLATE}} to {{TECH_SPEC_ERRORS}}
4. Update timestamps and set status to "in_progress"

---

### 2. Create Migration Mapping Specification (PRIORITY 1)

**Purpose**: This document maps legacy implementation patterns from Chapter 6 of business specifications to modern implementation patterns from target specifications. It is the PRIMARY reference for all code generation.

#### 2.1 Read Source Materials

**Read ALL target specifications**:
- Common Spec: `{{TARGET_SPECIFICATION}}/00-COMMON-SPECIFICATION.md`
- Backend Spec: `{{TARGET_SPECIFICATION}}/02-BACKEND-SPECIFICATION.md`
- Frontend Spec: `{{TARGET_SPECIFICATION}}/01-FRONTEND-SPECIFICATION.md`
- Batch Spec: `{{TARGET_SPECIFICATION}}/03-BATCH-SPECIFICATION.md`

**Read ALL business specifications**:
- Directory: `{{BUSINESS_SPECIFICATION_BASE_PATH}}/`
- Focus on: Chapter 6 (Legacy Implementation References), especially Section 6.7 (Migration Considerations)

**Read workpackage planning**:
- File: `{{WORKPACKAGE_PLANNING}}`
- Extract: List of all workpackages to map

#### 2.2 Copy and Populate Template

1. Copy `{{TECH_SPEC_MIGRATION_MAPPING_TEMPLATE}}` to `{{TECH_SPEC_MIGRATION_MAPPING}}`

2. **Populate Section 1: Cross-Cutting Patterns**

These patterns apply to ALL workpackages. Extract from target specifications:

**1.1 Authentication & Authorization**:
- Search Common Spec for: "authentication", "authorization", "OAuth", "OAuth2", "OIDC", "JWT", "LDAP", "SSO", "SAML", "security", "token", "identity provider", "Keycloak", "Auth0", "Okta"
- Search Backend Spec for: "Spring Security", "security", "authentication", "authorization"
- **CRITICAL**: Identify if this is EXTERNAL service integration (OAuth2, LDAP, SSO) or LOCAL implementation (user table, password storage)
- Document: Technology, implementation approach (integration vs local), configuration, example code, external service details if applicable
- **If external service**: Clearly state "EXTERNAL SERVICE - DO NOT IMPLEMENT USER STORAGE" and document integration approach
- Source references: Exact section numbers and quotes

**1.2 Data Persistence**:
- Search Backend Spec for: "database", "persistence", "JPA", "repository", "entity", "ORM"
- Document: Technology, framework, entity design, repository pattern, transaction management
- Source references: Exact section numbers and quotes

**1.3 Transaction Management**:
- Search Backend Spec for: "transaction", "@Transactional", "ACID", "isolation", "propagation"
- Document: Framework, annotations, configuration, patterns
- Source references: Exact section numbers and quotes

**1.4 API Design & Endpoints**:
- Search Backend Spec for: "REST", "API", "endpoint", "HTTP", "controller", "request", "response"
- Document: URL structure, HTTP methods, status codes, request/response format
- Source references: Exact section numbers and quotes

**1.5 Validation**:
- Search Backend Spec for: "validation", "Bean Validation", "JSR-380", "@Valid", "validator"
- Document: Framework, annotations, custom validators, error handling
- Source references: Exact section numbers and quotes

**1.6 Error Handling**:
- Search Backend Spec for: "exception", "error", "error handling", "@RestControllerAdvice"
- Document: Exception types, global handler, error response structure
- Source references: Exact section numbers and quotes

**1.7 Logging & Monitoring**:
- Search Backend Spec for: "logging", "log", "SLF4J", "monitoring", "metrics", "actuator"
- Search Common Spec for: "observability", "monitoring", "logging"
- Document: Framework, log levels, structured logging, metrics
- Source references: Exact section numbers and quotes

**1.8 Concurrency Control**:
- Search Backend Spec for: "concurrency", "locking", "optimistic", "@Version", "concurrent"
- Document: Locking strategy, implementation, conflict resolution
- Source references: Exact section numbers and quotes

3. **Populate Section 2: Workpackage-Specific Mappings**

For EACH workpackage in `{{WORKPACKAGE_PLANNING}}`:

**2.{WP-ID}.1 Technology Mapping**:
- Read business spec: `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-{ID}-specification.md`
- Navigate to Chapter 6.7 "Migration Considerations"
- Extract "Technology Dependencies to Remove" list
- For each legacy technology, map to modern equivalent using Section 1 patterns
- Create technology mapping table
- Document source references

**2.{WP-ID}.2 Business Logic Preservation**:
- From Chapter 3 (Business Rules): List all BR-XXX-XXX rules
- From Chapter 4 (Business Functions): List all F-XXX-XXX functions
- From Chapter 5 (Process Flows): List all PF-XXX-XXX flows
- From Chapter 6: Extract legacy implementation locations
- Map each to modern implementation pattern (validator, service method, API workflow)
- Create business logic preservation tables

**2.{WP-ID}.3 API Design**:
- From Chapter 4 (Business Functions): Identify operations
- From Chapter 6: Identify legacy transactions
- Design REST endpoints using Section 1.4 patterns
- Define request/response DTOs based on Chapter 2 (Business Entities)
- Define security requirements based on Section 1.1 patterns
- Create API design table

**2.{WP-ID}.4 Data Model Mapping**:
- From Chapter 2 (Business Entities): List all BE-XXX-XXX entities
- From Chapter 6.2 (Data Files): List all legacy files
- Map legacy files to modern database tables
- Map legacy fields to modern entity fields
- Define relationships, indexes, audit fields
- Create data model mapping tables

**2.{WP-ID}.5 Service Layer Design**:
- Based on business functions, design service classes
- Based on business rules, design validator classes
- Define mapper classes for DTO conversions
- Document dependencies and transaction boundaries

**2.{WP-ID}.6 Special Considerations**:
- Extract performance requirements
- Extract data migration requirements
- Identify integration points
- Note testing considerations
- Note deployment considerations

4. **Populate Section 3: Code Generation Guidance**

Provide step-by-step instructions for:
- 3.1 Backend Code Generation (how to use this document)
- 3.2 Frontend Code Generation (how to use this document)
- 3.3 Batch Code Generation (how to use this document)

5. **Populate Section 4: Quality Assurance Checklist**

Create comprehensive checklist for verifying:
- Technology mapping completeness
- Business logic preservation
- API design compliance
- Data model correctness
- Cross-cutting concerns implementation
- Traceability

6. **Populate Section 5: Common Migration Patterns Reference**

Create quick reference tables:
- COBOL to Java type mapping
- CICS command to Spring pattern mapping
- VSAM to database pattern mapping
- Screen to API pattern mapping

7. **Populate Section 6: Assumptions and Gaps**

Document:
- All assumptions made during mapping
- Information gaps found
- Items requiring verification

8. **Complete Section 7: Document Control**

Update:
- Version history
- Approval status
- Related documents
- Usage instructions

#### 2.3 Verification

Verify Migration Mapping Specification:
- [ ] All cross-cutting patterns documented with source references
- [ ] All workpackages have complete mappings
- [ ] All Chapter 6.7 items mapped to modern patterns
- [ ] All business rules, functions, flows mapped
- [ ] API design complete for all workpackages
- [ ] Data model mapping complete for all workpackages
- [ ] Code generation guidance clear and actionable
- [ ] Quality checklist comprehensive
- [ ] Pattern reference tables complete
- [ ] Assumptions and gaps documented

---

### 3. Extract Backend Technical Specification

#### 2.1 Read Source Materials

**Read the backend specification**:
- File: `{{TARGET_SPECIFICATION}}/02-BACKEND-SPECIFICATION.md`
- Read the ENTIRE file - do not assume structure

**Review sample code**:
- Directory: `{{TARGET_SAMPLE_CODE}}/backend/`
- Look for: Build files, configuration files, code examples

#### 2.2 Discovery Process

For EACH section in the backend template, use keyword-based search:

**Section 1: Build System**
- Search for keywords: "maven", "gradle", "build", "pom.xml", "build.gradle", "build tool"
- Extract: Tool name, version, build file name
- Document source: Where you found this information
- If not found: Check sample code for build files
- If still not found: Document assumption

**Section 2: Framework**
- Search for keywords: "framework", "spring boot", "jakarta", "quarkus", "micronaut", "version"
- Extract: Framework name, version, parent/BOM
- Document source: Where you found this information
- If not found: Check sample code for framework indicators
- If still not found: Document assumption

**Section 3: Language**
- Search for keywords: "java", "kotlin", "language", "version", "jdk", "compiler"
- Extract: Language, version, compiler target
- Document source: Where you found this information
- If not found: Check build file for language version
- If still not found: Document assumption

**Section 4: Project Structure**
- Search for keywords: "structure", "directory", "folder", "organization", "layout", "package", "module"
- Extract: EXACT directory structure as documented
- Document source: Where you found this information
- If not found: Check sample code for structure
- **CRITICAL**: Copy the EXACT structure - do not invent your own

**Section 5: Dependencies**
- Search for keywords: "dependencies", "dependency", "libraries", "library", "artifact"
- Extract: All dependencies with versions
- Document source: Where you found this information
- If not found: Check build file in sample code
- Group by: Core, Persistence, Testing, Other

**Section 6: Code Organization**
- Search for keywords: "architecture", "pattern", "layer", "layered", "hexagonal", "clean", "organization"
- Extract: Architecture pattern, package strategy, layer descriptions
- Document source: Where you found this information
- If not found: Infer from sample code structure
- If still not found: Document assumption

**Section 7: Naming Conventions**
- Search for keywords: "naming", "convention", "pattern", "name", "suffix", "prefix"
- Extract: Package, class, method, variable naming patterns
- Document source: Where you found this information
- If not found: Infer from sample code
- If still not found: Document assumption

**Section 8: Persistence Approach**
- Search for keywords: "persistence", "jpa", "jdbc", "orm", "database", "entity", "repository"
- Extract: ORM/data access approach, database type, transaction management
- Document source: Where you found this information
- If not found: Check sample code for persistence patterns
- If still not found: Document assumption

**Section 9: API Patterns**
- Search for keywords: "api", "rest", "graphql", "endpoint", "controller", "resource"
- Extract: API style, versioning, endpoint patterns, request/response format
- Document source: Where you found this information
- If not found: Check sample code for API patterns
- If still not found: Document assumption

**Section 10: Security Approach**
- Search for keywords: "security", "authentication", "authorization", "jwt", "oauth", "session"
- Extract: Authentication mechanism, authorization approach, security configuration
- Document source: Where you found this information
- If not found: Check sample code for security configuration
- If still not found: Document assumption

**Section 11: Testing Approach**
- Search for keywords: "test", "testing", "junit", "mockito", "integration test", "unit test"
- Extract: Testing frameworks, test organization, coverage targets
- Document source: Where you found this information
- If not found: Check sample code for test examples
- If still not found: Document assumption

**Section 12: Error Handling**
- Search for keywords: "error", "exception", "handling", "global handler", "error response"
- Extract: Exception strategy, exception hierarchy, error response format
- Document source: Where you found this information
- If not found: Check sample code for error handling
- If still not found: Document assumption

**Section 13: Logging**
- Search for keywords: "log", "logging", "slf4j", "logback", "log4j"
- Extract: Logging framework, log levels, log format
- Document source: Where you found this information
- If not found: Check sample code for logging configuration
- If still not found: Document assumption

**Section 14: Configuration**
- Search for keywords: "configuration", "config", "properties", "yaml", "profile", "environment"
- Extract: Configuration format, profiles, externalized configuration
- Document source: Where you found this information
- If not found: Check sample code for configuration files
- If still not found: Document assumption

**Section 15-17: Additional Patterns and Code Examples**
- Search for: validation, caching, async, scheduling patterns
- Extract code examples from sample code
- Document source for each example

#### 2.3 Create Backend Technical Specification

1. Copy {{TECH_SPEC_BACKEND_TEMPLATE}} to {{TECH_SPEC_BACKEND}}
2. Fill in ALL sections with discovered information
3. For each section, add a note indicating source:
   - "Source: [Specification file, line/section]"
   - "Source: [Sample code file]"
   - "Assumption: [Reason for assumption]"
4. Include code examples from sample code
5. Document all assumptions in Section 17 (Notes and Assumptions)

#### 2.4 Update Progress

Update {{TECH_SPEC_STATUS}}:
- Set backend.status = "completed"
- Set backend.completionDate = current timestamp
- Mark all extracted sections as true
- Update overallProgress

### 3. Extract Frontend Technical Specification

#### 3.1 Read Source Materials

**Read the frontend specification**:
- File: `{{TARGET_SPECIFICATION}}/01-FRONTEND-SPECIFICATION.md`
- Read the ENTIRE file - do not assume structure

**Review sample code**:
- Directory: `{{TARGET_SAMPLE_CODE}}/frontend/`
- Look for: package.json, build config, code examples

#### 3.2 Discovery Process

For EACH section in the frontend template, use keyword-based search:

**Section 1: Framework**
- Search for keywords: "framework", "react", "vue", "angular", "svelte", "version"
- Extract: Framework name, version, type (SPA/SSR/SSG)
- Document source

**Section 2: Build Tool**
- Search for keywords: "build", "vite", "webpack", "rollup", "parcel", "bundler"
- Extract: Build tool, version, configuration file
- Document source

**Section 3: Language**
- Search for keywords: "typescript", "javascript", "language", "version", "compiler"
- Extract: Language, version, compiler
- Document source

**Section 4: Project Structure**
- Search for keywords: "structure", "directory", "folder", "organization", "component"
- Extract: EXACT directory structure
- Document source
- **CRITICAL**: Copy EXACT structure

**Section 5: Dependencies**
- Search for keywords: "dependencies", "package", "library", "npm", "yarn"
- Extract: All dependencies with versions
- Document source
- Group by: Core, UI Library, State Management, Routing, Testing, Other

**Section 6: Component Organization**
- Search for keywords: "component", "organization", "pattern", "atomic", "feature"
- Extract: Component pattern, component structure, component types
- Document source

**Section 7: Naming Conventions**
- Search for keywords: "naming", "convention", "pattern", "file name", "component name"
- Extract: File, component, function, variable naming patterns
- Document source

**Section 8: State Management**
- Search for keywords: "state", "redux", "zustand", "pinia", "ngrx", "context"
- Extract: State management solution, state organization, state structure
- Document source

**Section 9: Routing**
- Search for keywords: "routing", "router", "route", "navigation"
- Extract: Routing library, routing mode, route structure
- Document source

**Section 10: API Integration**
- Search for keywords: "api", "http", "axios", "fetch", "client"
- Extract: HTTP client, API service pattern, request/response handling
- Document source

**Section 11: Styling Approach**
- Search for keywords: "style", "css", "scss", "tailwind", "styled components", "css modules"
- Extract: Styling solution, CSS framework, responsive design approach
- Document source

**Section 12: Accessibility**
- Search for keywords: "accessibility", "a11y", "wcag", "aria", "screen reader"
- Extract: WCAG level, accessibility requirements, accessibility patterns
- Document source

**Section 13: Testing Approach**
- Search for keywords: "test", "testing", "jest", "vitest", "cypress", "playwright"
- Extract: Testing frameworks, test organization, test patterns
- Document source

**Section 14-19: Additional Sections**
- Continue keyword-based discovery for remaining sections
- Extract code examples from sample code
- Document all sources

#### 3.3 Create Frontend Technical Specification

1. Copy {{TECH_SPEC_FRONTEND_TEMPLATE}} to {{TECH_SPEC_FRONTEND}}
2. Fill in ALL sections with discovered information
3. Add source notes for each section
4. Include code examples from sample code
5. Document all assumptions

#### 3.4 Update Progress

Update {{TECH_SPEC_STATUS}}:
- Set frontend.status = "completed"
- Set frontend.completionDate = current timestamp
- Mark all extracted sections as true
- Update overallProgress

### 4. Extract Batch Technical Specification

#### 4.1 Read Source Materials

**Read the batch specification**:
- File: `{{TARGET_SPECIFICATION}}/03-BATCH-SPECIFICATION.md`
- Read the ENTIRE file

**Review sample code**:
- Directory: `{{TARGET_SAMPLE_CODE}}/batch/`
- Look for: Build files, job configurations, code examples

#### 4.2 Discovery Process

For EACH section in the batch template, use keyword-based search:

**Section 1: Framework**
- Search for keywords: "batch", "spring batch", "jakarta batch", "framework", "version"
- Extract: Batch framework, version, parent/BOM
- Document source

**Section 2: Build System**
- Search for keywords: "maven", "gradle", "build", "pom.xml", "build.gradle"
- Extract: Build tool, version, build file
- Document source

**Section 3: Language**
- Search for keywords: "java", "kotlin", "language", "version"
- Extract: Language, version, compiler target
- Document source

**Section 4: Project Structure**
- Search for keywords: "structure", "directory", "folder", "job", "organization"
- Extract: EXACT directory structure
- Document source
- **CRITICAL**: Copy EXACT structure

**Section 5: Dependencies**
- Search for keywords: "dependencies", "dependency", "batch", "library"
- Extract: All dependencies with versions
- Document source
- Group by: Core, Batch, Database, Testing

**Section 6: Job Organization**
- Search for keywords: "job", "organization", "pattern", "configuration", "step"
- Extract: Job organization pattern, job configuration approach, job structure
- Document source

**Section 7: Naming Conventions**
- Search for keywords: "naming", "convention", "job name", "step name", "bean name"
- Extract: Package, class, method naming patterns
- Document source

**Section 8: Chunk Processing**
- Search for keywords: "chunk", "commit", "transaction", "batch size"
- Extract: Chunk size, commit interval, transaction management
- Document source

**Section 9: Error Handling**
- Search for keywords: "error", "skip", "retry", "exception", "fault tolerant"
- Extract: Skip policy, retry policy, error listeners
- Document source

**Section 10: Restart and Recovery**
- Search for keywords: "restart", "recovery", "job repository", "state"
- Extract: Restart capability, job repository, state management
- Document source

**Section 11-21: Additional Sections**
- Continue keyword-based discovery
- Extract code examples from sample code
- Document all sources

#### 4.3 Create Batch Technical Specification

1. Copy {{TECH_SPEC_BATCH_TEMPLATE}} to {{TECH_SPEC_BATCH}}
2. Fill in ALL sections with discovered information
3. Add source notes for each section
4. Include code examples from sample code
5. Document all assumptions

#### 4.4 Update Progress

Update {{TECH_SPEC_STATUS}}:
- Set batch.status = "completed"
- Set batch.completionDate = current timestamp
- Mark all extracted sections as true
- Update overallProgress

### 5. Extract Infrastructure Technical Specification

#### 5.1 Read Source Materials

**Search ALL specifications** for infrastructure information:
- Backend specification
- Frontend specification
- Batch specification
- Any deployment/infrastructure documents

**Review sample code** for infrastructure indicators:
- Dockerfiles
- Kubernetes manifests
- CI/CD configurations
- Deployment scripts

#### 5.2 Discovery Process

For EACH section in the infrastructure template, use keyword-based search:

**Section 1: Deployment Approach**
- Search for keywords: "deployment", "cloud", "on-premise", "aws", "azure", "gcp"
- Extract: Deployment model, cloud provider, deployment strategy
- Document source

**Section 2: Containerization**
- Search for keywords: "docker", "container", "image", "registry"
- Extract: Container runtime, container registry, Dockerfile patterns
- Document source

**Section 3: Orchestration**
- Search for keywords: "kubernetes", "k8s", "docker compose", "orchestration"
- Extract: Orchestration platform, configuration patterns
- Document source

**Section 4: CI/CD Pipeline**
- Search for keywords: "ci/cd", "pipeline", "jenkins", "gitlab", "github actions"
- Extract: CI/CD platform, pipeline stages, deployment automation
- Document source

**Section 5-15: Additional Sections**
- Continue keyword-based discovery
- Extract configuration examples
- Document all sources

#### 5.3 Create Infrastructure Technical Specification

1. Copy {{TECH_SPEC_INFRASTRUCTURE_TEMPLATE}} to {{TECH_SPEC_INFRASTRUCTURE}}
2. Fill in ALL sections with discovered information
3. Add source notes for each section
4. Include configuration examples
5. Document all assumptions
6. **Note**: This specification may have more assumptions than others due to limited infrastructure details in source specifications

#### 5.4 Update Progress

Update {{TECH_SPEC_STATUS}}:
- Set infrastructure.status = "completed"
- Set infrastructure.completionDate = current timestamp
- Mark all extracted sections as true
- Update overallProgress to 100%

### 6. Final Validation

#### 6.1 Completeness Check

For EACH specification:
- [ ] All required sections populated
- [ ] Source references documented
- [ ] Assumptions documented
- [ ] Code examples included
- [ ] No placeholder text remaining

#### 6.2 Consistency Check

Across ALL specifications:
- [ ] Consistent naming conventions
- [ ] Consistent version numbers
- [ ] No conflicting information
- [ ] Consistent terminology

#### 6.3 Quality Check

For ALL specifications:
- [ ] Clear and unambiguous
- [ ] Sufficient detail for code generation
- [ ] Traceable to source specifications
- [ ] Assumptions clearly marked

### 7. Update Final Progress

1. Update {{TECH_SPEC_STATUS}}:
   - Set status = "completed"
   - Set completionDate = current timestamp
   - Verify all specifications marked as completed
   - Verify overallProgress.percentComplete = 100

2. Update {{TECH_SPEC_PROGRESS}}:
   - Update all status indicators
   - Mark all sections as complete
   - Update timestamps

3. If errors occurred, update {{TECH_SPEC_ERRORS}}:
   - Document all errors encountered
   - Categorize by severity
   - Indicate resolution status

### 8. Error Handling

#### 8.1 Missing Source Specifications

If source specification file not found:
1. Document error in {{TECH_SPEC_ERRORS}}
2. Mark specification as "failed" in {{TECH_SPEC_STATUS}}
3. Continue with other specifications
4. Report to supervisor

#### 8.2 Insufficient Information

If information cannot be discovered:
1. Check sample code for indicators
2. If still not found, document assumption
3. Mark assumption clearly in specification
4. Add to assumptions section
5. Continue with extraction

#### 8.3 Conflicting Information

If conflicting information found:
1. Document conflict in {{TECH_SPEC_ERRORS}}
2. Use most recent or most detailed source
3. Document decision in specification
4. Add warning to {{TECH_SPEC_STATUS}}

---

## Output Format

### Technical Specifications

All specifications follow their respective templates with:
- All sections populated
- Source references: "Source: [file/location]"
- Assumptions marked: "Assumption: [reason]"
- Code examples included
- Notes and assumptions section completed

### Progress Tracking

**{{TECH_SPEC_STATUS}}**: JSON with complete status
**{{TECH_SPEC_PROGRESS}}**: Markdown with human-readable progress
**{{TECH_SPEC_ERRORS}}**: JSON with any errors encountered

---

## Quality Criteria

### Completeness
- All required sections populated
- No placeholder text remaining
- All discoverable information extracted

### Traceability
- Every piece of information has source reference
- All assumptions documented
- Clear lineage from source to specification

### Clarity
- Clear and unambiguous language
- Sufficient detail for implementation
- Well-organized and structured

### Consistency
- Consistent across all specifications
- No conflicting information
- Consistent terminology and naming

### Usability
- Directly usable by code generation phases
- No additional discovery needed
- Complete and self-contained

---

## End of Phase 5.0.0 Document
