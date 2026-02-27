# Phase: Technical Design (TD) - Workpackage Implementation Guidance

## Context
- Project Structure: Standard migration project folder structure
- Input Location: 
  - {{BUSINESS_SPECIFICATION_BASE_PATH}} - Workpackage-based business specifications
  - {{TEST_GENERATION_DOMAIN_BASE_PATH}} - Test cases per workpackage
  - {{DATABASE_GEN_SRC}} - Database schemas (DDL) for the new target system
  - {{TARGET_SPECIFICATION}} - Target framework specifications (architecture, patterns, technologies)
  - {{TARGET_SAMPLE_CODE}} - Sample code examples for reference
  - {{WORKPACKAGE_PLANNING}} - Workpackage definitions and dependencies
  - {{SOURCE_CODE_ANALYSIS_OUTPUT}} - Legacy code analysis and dependencies
  - {{TECH_SPEC_BASE_PATH}} - Cross-cutting technical specifications (if available)
  - {{TECHNICAL_DESIGN_OUTPUT}} - Previously created technical designs for other workpackages

- Output Location: 
  - {{TECHNICAL_DESIGN_OUTPUT}} - Technical design documents per workpackage
  - {{TECHNICAL_DESIGN_PROGRESS}} - Phase completion tracking
  - {{TECHNICAL_DESIGN_ERRORS}} - Error tracking

## Objective

Create detailed, implementation-ready technical design documents for each workpackage that provide comprehensive guidance for code generation agents. Each document should specify the exact implementation approach including APIs, methods, classes, package structure, layering, and detailed function implementations.

The technical design serves as the PRIMARY implementation reference that code generators will use alongside business specifications, target specifications, and database schemas.

**CRITICAL**: All implementation patterns, structures, and conventions MUST be derived from the target specifications and existing technical designs. Do NOT hardcode or assume any specific framework, pattern, or structure.

---

## Key Principles

1. **Specification-Driven**: Derive ALL patterns, structures, and conventions from target specifications
2. **Consistency**: Follow patterns established in existing technical designs for other workpackages
3. **Implementation-Ready**: Provide sufficient detail that a code generator can implement without ambiguity
4. **Non-Redundant**: Reference business specs, target specs, and DB schemas - don't duplicate their content
5. **Workpackage-Focused**: One technical design per workpackage
6. **Traceable**: Link all design decisions to business requirements and target specifications
7. **Adaptable**: Work with any target technology stack or architectural pattern

---

## Instructions

### Step 1: Initialize Progress Tracking

1. Create progress tracking file at {{TECHNICAL_DESIGN_PROGRESS}} using template
2. List all workpackages from {{WORKPACKAGE_PLANNING}}
3. Set initial status to "not_started" for all workpackages
4. Create error log at {{TECHNICAL_DESIGN_ERRORS}} using template

### Step 2: Read and Understand Target Specifications

**CRITICAL FIRST STEP**: Before creating any technical design, thoroughly read and understand the target specifications to extract:

#### 2.1 Read All Target Specification Files

Read the following files completely (do NOT assume structure or content):
- {{TARGET_SPECIFICATION}}/00-COMMON-SPECIFICATION.md
- {{TARGET_SPECIFICATION}}/01-FRONTEND-SPECIFICATION.md
- {{TARGET_SPECIFICATION}}/02-BACKEND-SPECIFICATION.md
- {{TARGET_SPECIFICATION}}/03-BATCH-SPECIFICATION.md

#### 2.2 Extract Key Patterns from Target Specifications

Use keyword-based search to discover (do NOT assume):

**Architecture Patterns**:
- Search for: "architecture", "layering", "layers", "structure", "organization", "modules", "components"
- Extract: How the application is structured (e.g., layered, hexagonal, clean architecture, microservices, monolith)
- Document: The specific layers/modules and their responsibilities

**Package/Directory Structure**:
- Search for: "package", "directory", "folder", "structure", "organization", "naming"
- Extract: How code should be organized (package naming conventions, directory structure)
- Document: The exact structure pattern to follow

**Backend Patterns** (if applicable):
- Search for: "controller", "service", "repository", "entity", "DTO", "mapper", "REST", "API", "endpoint"
- Extract: What components are used and how they interact
- Document: The specific pattern (e.g., Controller-Service-Repository, CQRS, etc.)

**Frontend Patterns** (if applicable):
- Search for: "component", "page", "view", "state", "routing", "hooks", "services"
- Extract: How frontend code is organized
- Document: The specific pattern and structure

**Data Access Patterns**:
- Search for: "database", "persistence", "ORM", "query", "transaction", "entity", "model"
- Extract: How data access is implemented
- Document: The specific approach and patterns

**API Design Patterns**:
- Search for: "REST", "GraphQL", "API", "endpoint", "HTTP", "request", "response", "status code"
- Extract: How APIs are designed and structured
- Document: URL patterns, HTTP methods, request/response formats

**Validation Patterns**:
- Search for: "validation", "validator", "constraint", "error", "exception"
- Extract: How validation is implemented
- Document: The specific validation approach

**Error Handling Patterns**:
- Search for: "error", "exception", "handling", "response", "status"
- Extract: How errors are handled and communicated
- Document: Error response formats and handling strategies

**Security Patterns**:
- Search for: "security", "authentication", "authorization", "token", "session", "permission"
- Extract: How security is implemented
- Document: Authentication/authorization approach

**Testing Patterns**:
- Search for: "test", "testing", "unit", "integration", "mock"
- Extract: Testing conventions and patterns
- Document: Test structure and naming

**Naming Conventions**:
- Search for: "naming", "convention", "name", "identifier"
- Extract: How to name classes, methods, files, variables
- Document: All naming rules

#### 2.3 Review Sample Code

Read sample code from {{TARGET_SAMPLE_CODE}}/ to see patterns in action:
- Identify actual implementations of patterns described in specifications
- Note any conventions not explicitly documented in specifications
- Extract code templates and examples

#### 2.4 Review Existing Technical Designs

If other workpackages have already been designed, read their technical designs from {{TECHNICAL_DESIGN_OUTPUT}}/:
- Identify established patterns and conventions
- Ensure consistency with previous designs
- Reuse common structures and approaches

#### 2.5 Review Cross-Cutting Technical Specifications

If available, read technical specifications from {{TECH_SPEC_BASE_PATH}}/:
- Migration mapping specifications
- Backend/Frontend/Batch technical specifications
- Infrastructure specifications

### Step 3: Read Additional Reference Materials

**Database Schema**:
- Read: {{DATABASE_GEN_SRC}}/new_sqlite_ddl.sql (or equivalent)
- Extract: Table structures, relationships, constraints
- Note: Data types, indexes, foreign keys

**Workpackage Planning**:
- Read: {{WORKPACKAGE_PLANNING}}
- Extract: Workpackage list, dependencies, priorities

### Step 4: Process Each Workpackage

For each workpackage in {{WORKPACKAGE_PLANNING}}, create a technical design document.

#### 4.1 Read Workpackage-Specific Inputs

**For workpackage WP-XXX:**
- Business specification: {{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-specification.md
  - Focus on: Functional requirements, business rules, data models, API requirements
  - Reference Chapter 6 for legacy implementation context
- Test cases: {{TEST_GENERATION_DOMAIN_BASE_PATH}}/WP-XXX-tests.md
  - Use to understand expected behavior and edge cases

#### 4.2 Create Technical Design Document

**Output file**: {{TECHNICAL_DESIGN_OUTPUT}}/WP-XXX-technical-design.md

**Document Structure** (adapt based on target specifications):

```markdown
# Technical Design: WP-XXX - [Workpackage Name]

## 1. Overview

### 1.1 Workpackage Summary
- **ID**: WP-XXX
- **Name**: [From business spec]
- **Business Specification**: Reference to {{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-specification.md
- **Test Cases**: Reference to {{TEST_GENERATION_DOMAIN_BASE_PATH}}/WP-XXX-tests.md
- **Dependencies**: [List dependent workpackages from planning]

### 1.2 Implementation Scope
Based on business requirements, identify what needs to be implemented:
- **Frontend Components**: [Yes/No - list if yes]
- **Backend Services**: [Yes/No - list if yes]
- **Batch Jobs**: [Yes/No - list if yes]
- **Database Changes**: [Yes/No - reference DB schema sections if yes]
- **Infrastructure**: [Any infrastructure components needed]

### 1.3 Architecture Layer Assignment
Based on the architecture pattern from target specifications, identify which layers this workpackage touches:
- [List layers as defined in target specification]
- [For each layer, list what components/modules are needed]

**Reference**: [Cite specific section from target specification that defines the architecture]

---

## 2. Implementation Structure

### 2.1 Code Organization

**Package/Directory Structure**:
Based on the structure pattern from target specifications, define the complete organization for this workpackage:

```
[Root structure from target specification]
├── [module/package name following target spec conventions]
│   ├── [substructure as defined in target spec]
│   │   └── [files following naming conventions from target spec]
```

**Rationale**: [Reference specific section from target specification]
**Consistency**: [Reference similar structure from other workpackage technical designs if available]

### 2.2 Component Identification

Based on business requirements and target specification patterns, identify all components needed:

**[Component Type 1 from target spec]**:
- Component Name: [Following naming convention from target spec]
- Responsibility: [What this component does]
- Location: [Where it goes in the structure]
- Dependencies: [What it depends on]

**[Component Type 2 from target spec]**:
- Component Name: [Following naming convention from target spec]
- Responsibility: [What this component does]
- Location: [Where it goes in the structure]
- Dependencies: [What it depends on]

[Continue for all component types defined in target specification]

---

## 3. API/Interface Design

### 3.1 API Endpoints (if applicable)

Based on API design patterns from target specifications:

For each API endpoint required by business specification:

#### 3.1.1 [Endpoint Name]

**Business Requirement**: [Reference specific requirement from business spec]

**Endpoint Details** (following target specification patterns):
- **HTTP Method**: [As defined in target spec API patterns]
- **URL Path**: [Following URL pattern from target spec]
- **Handler/Controller**: [Component name following target spec naming]
- **Method Name**: [Following naming convention from target spec]

**Request Structure**:
[Define based on request format specified in target spec]
- Include validation rules from business spec
- Follow data structure patterns from target spec

**Response Structure**:
[Define based on response format specified in target spec]
- Include all fields needed by consumers
- Follow data structure patterns from target spec

**Status Codes**:
[Use status codes as defined in target specification]
- [Code]: [When - from target spec]
- [Code]: [When - from target spec]

**Implementation Guidance**:
[Provide implementation steps following patterns from target specification and sample code]

**Validation Rules**: [List all validation rules from business spec]
**Error Handling**: [Follow error handling pattern from target spec]
**Security**: [Follow security pattern from target spec]

**Reference**: [Cite specific sections from target specification]

---

## 4. Business Logic Implementation

### 4.1 Business Logic Components

Based on business logic patterns from target specifications:

For each business logic component:

#### 4.1.1 [Component Name]

**Responsibility**: [What business logic this handles]

**Interface/Contract**:
[Define interface following patterns from target specification]

**Implementation Guidance**:

**Method: [methodName]**
[Provide step-by-step implementation guidance]

**Business Rules Implementation**:
[Detail each business rule from business spec and how to implement it]
- Rule 1: [Description and implementation approach following target spec patterns]
- Rule 2: [Description and implementation approach following target spec patterns]

**Transaction Management**: [Follow transaction pattern from target spec]
**Error Handling**: [Follow error handling pattern from target spec]
**Logging**: [Follow logging pattern from target spec]

**Reference**: [Cite specific sections from target specification]

---

## 5. Data Access Implementation

### 5.1 Data Model Mapping

**Database Tables Used**: [From {{DATABASE_GEN_SRC}}]

For each entity:

#### 5.1.1 [Entity Name]

**Database Table**: [Table name from database schema]

**Entity Structure**:
[Define entity structure following data access patterns from target specification]

**Field Mappings**:
[Map business spec fields to database columns to code fields]
- Business Field → Database Column → Code Field
- [field1] → [column1] → [codeField1]

**Relationships**:
[Define relationships following patterns from target specification]

**Reference**: [Cite specific sections from target specification and database schema]

### 5.2 Data Access Components

Based on data access patterns from target specifications:

**[Data Access Component Type from target spec]**:
[Define following patterns from target specification]

**Query Methods**:
[List all required queries from business spec and test cases]
[Follow query patterns from target specification]

**Reference**: [Cite specific sections from target specification]

---

## 6. Frontend Implementation (if applicable)

### 6.1 Frontend Structure

Based on frontend patterns from target specifications:

**Component Organization**:
[Define structure following frontend specification]

**State Management**:
[Follow state management pattern from target specification]

**Routing**:
[Follow routing pattern from target specification]

### 6.2 User Interface Components

For each UI component:

#### 6.2.1 [Component Name]

**Business Requirement**: [Reference from business spec]
**Component Type**: [From target specification]
**Location**: [Following structure from target spec]

**Responsibilities**:
- Display: [What data to show]
- Actions: [What user actions are supported]
- Navigation: [Where users can navigate]

**Implementation Guidance**:
[Provide guidance following patterns from target specification and sample code]

**State Management**: [Follow pattern from target spec]
**API Integration**: [Follow pattern from target spec]
**Validation**: [Follow pattern from target spec]

**Reference**: [Cite specific sections from target specification]

---

## 7. Batch Processing Implementation (if applicable)

### 7.1 Batch Job Definition

Based on batch patterns from target specifications:

**Job Name**: [Following naming convention from target spec]
**Purpose**: [What this batch job does]
**Schedule**: [When it runs]
**Trigger**: [How it's triggered - from target spec patterns]

### 7.2 Job Implementation

**Structure**:
[Define following batch patterns from target specification]

**Processing Logic**:
[Provide implementation guidance following target spec patterns]

**Error Handling**: [Follow error handling pattern from target spec]
**Monitoring**: [Follow monitoring pattern from target spec]

**Reference**: [Cite specific sections from target specification]

---

## 8. Cross-Cutting Concerns

### 8.1 Security Implementation

Based on security patterns from target specifications:

**Authentication**: [Follow authentication pattern from target spec]
**Authorization**: [Follow authorization pattern from target spec]
- Roles: [List required roles]
- Permissions: [List required permissions]
- Enforcement: [Follow enforcement pattern from target spec]

**Reference**: [Cite specific sections from target specification]

### 8.2 Validation Implementation

Based on validation patterns from target specifications:

**Input Validation**:
[Follow validation pattern from target spec]
- [List all validations from business spec]

**Business Rule Validation**:
[Follow validation pattern from target spec]
- [List all business rules from business spec]

**Reference**: [Cite specific sections from target specification]

### 8.3 Error Handling Implementation

Based on error handling patterns from target specifications:

**Error Scenarios**: [List all error scenarios from test cases]
**Error Responses**: [Follow error response format from target spec]
**Logging**: [Follow logging pattern from target spec]

**Reference**: [Cite specific sections from target specification]

### 8.4 Logging and Monitoring

Based on logging patterns from target specifications:

**Log Points**: [Follow logging pattern from target spec]
**Metrics**: [Follow metrics pattern from target spec]

**Reference**: [Cite specific sections from target specification]

### 8.5 Testing Guidance

Based on testing patterns from target specifications:

**Unit Tests**: [Follow unit test pattern from target spec]
**Integration Tests**: [Follow integration test pattern from target spec]
**Test Data**: [Reference test cases document]

**Reference**: [Cite specific sections from target specification]

---

## 9. Data Flow

### 9.1 Request Flow

Diagram the complete flow for key operations following the architecture from target specifications:

```
[Layer 1 from target spec]
    ↓
[Layer 2 from target spec]
    ↓
[Layer 3 from target spec]
    ↓
[Continue following architecture layers from target spec]
```

### 9.2 Data Transformations

Document all data transformations following patterns from target specifications:
- [Transformation 1]: [Following pattern from target spec]
- [Transformation 2]: [Following pattern from target spec]

---

## 10. Integration Points

### 10.1 Internal Dependencies

**Depends On** (other workpackages):
- WP-XXX: [What functionality is needed and how to integrate following target spec patterns]

**Depended Upon By** (other workpackages):
- WP-YYY: [What functionality this provides following target spec patterns]

### 10.2 External Dependencies

**External Services**:
[List any external services and how to integrate following target spec patterns]

**Third-Party Libraries**:
[List any libraries and their usage following target spec patterns]

---

## 11. Implementation Notes

### 11.1 Design Decisions

Document key design decisions:
- **Decision**: [What was decided]
- **Rationale**: [Why this approach - reference target spec]
- **Alternatives Considered**: [What else was considered]
- **Trade-offs**: [Pros and cons]
- **Target Spec Reference**: [Cite relevant sections]

### 11.2 Assumptions

List all assumptions made:
- [Assumption 1]: [What is assumed and why]
- [Assumption 2]: [What is assumed and why]

### 11.3 Open Questions

List any unresolved questions:
- [Question 1]: [What needs clarification]
- [Question 2]: [What needs clarification]

### 11.4 Migration Considerations

**Legacy System Mapping**:
- Legacy Component → Modern Component (following target spec patterns)
- [Legacy program] → [Modern component]

**Data Migration**:
- [What data needs to be migrated]
- [How to handle data transformation]

---

## 12. Code Generation Guidance

### 12.1 Generation Order

Recommended order for code generation (adapt based on target spec patterns):
1. [Component type 1 from target spec]
2. [Component type 2 from target spec]
3. [Continue following logical order based on dependencies]

### 12.2 Naming Conventions

**All naming conventions MUST follow target specification**:
- [Component Type 1]: [Naming pattern from target spec]
- [Component Type 2]: [Naming pattern from target spec]
- [Continue for all component types]

**Reference**: [Cite naming convention sections from target specification]

### 12.3 Code Templates

Reference sample code from {{TARGET_SAMPLE_CODE}} for:
- [Template 1 from sample code]
- [Template 2 from sample code]
- [Continue for all relevant templates]

---

## 13. References

### 13.1 Business Requirements
- Business Specification: {{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-specification.md
- Test Cases: {{TEST_GENERATION_DOMAIN_BASE_PATH}}/WP-XXX-tests.md

### 13.2 Technical Specifications
- Target Common Spec: {{TARGET_SPECIFICATION}}/00-COMMON-SPECIFICATION.md
- Target Backend Spec: {{TARGET_SPECIFICATION}}/02-BACKEND-SPECIFICATION.md
- Target Frontend Spec: {{TARGET_SPECIFICATION}}/01-FRONTEND-SPECIFICATION.md
- Target Batch Spec: {{TARGET_SPECIFICATION}}/03-BATCH-SPECIFICATION.md
- Database Schema: {{DATABASE_GEN_SRC}}/[schema file]
- Cross-Cutting Tech Specs: {{TECH_SPEC_BASE_PATH}}/

### 13.3 Sample Code
- Sample Code: {{TARGET_SAMPLE_CODE}}/

### 13.4 Related Technical Designs
- [List other workpackage technical designs referenced for consistency]

---

## Appendix: Quick Reference

### Implementation Summary
[Provide a quick reference table summarizing key implementation details]

| Aspect | Implementation | Reference |
|--------|----------------|-----------|
| Architecture Pattern | [From target spec] | [Section] |
| Package Structure | [From target spec] | [Section] |
| API Pattern | [From target spec] | [Section] |
| Data Access Pattern | [From target spec] | [Section] |
| Validation Pattern | [From target spec] | [Section] |
| Error Handling Pattern | [From target spec] | [Section] |

### Component Inventory
[List all components to be generated with their types and locations]

| Component Name | Type | Location | Purpose |
|----------------|------|----------|---------|
| [Name] | [Type from target spec] | [Path] | [Purpose] |

```

---

### Step 5: Quality Checks

For each technical design document, verify:

- [ ] All patterns and structures are derived from target specifications (not hardcoded)
- [ ] All references to target specification sections are included
- [ ] Consistency with other workpackage technical designs is maintained
- [ ] All API endpoints from business spec are documented
- [ ] All database tables referenced exist in the DB schema
- [ ] All business rules have implementation guidance
- [ ] Package/directory structure follows target specification exactly
- [ ] Naming conventions follow target specification exactly
- [ ] Frontend components (if any) follow target specification patterns
- [ ] Batch jobs (if any) follow target specification patterns
- [ ] Security requirements follow target specification patterns
- [ ] Error handling follows target specification patterns
- [ ] Integration points are documented
- [ ] Code generation guidance is clear and specification-driven

### Step 6: Update Progress Tracking

After completing each workpackage:
1. Update {{TECHNICAL_DESIGN_PROGRESS}}
2. Mark workpackage as "completed"
3. Document any issues or blockers in {{TECHNICAL_DESIGN_ERRORS}}
4. Note dependencies on other workpackages

---

## Success Criteria

- [ ] Technical design created for ALL workpackages
- [ ] Each design is implementation-ready (sufficient detail for code generation)
- [ ] All designs reference (not duplicate) business specs, target specs, and DB schemas
- [ ] All patterns and structures are derived from target specifications
- [ ] Consistency maintained across all workpackage designs
- [ ] All target specification sections are properly referenced
- [ ] Layering follows target specification architecture
- [ ] API contracts follow target specification patterns
- [ ] Package structures follow target specification conventions
- [ ] Naming conventions follow target specification rules
- [ ] Integration points between workpackages are documented
- [ ] Security and error handling follow target specification patterns
- [ ] Code generation guidance is specification-driven
- [ ] Progress tracking is complete
- [ ] No hardcoded assumptions about frameworks or patterns

---

## Critical Rules

1. **NEVER hardcode specific frameworks** (e.g., Spring Boot, React, JPA) - derive from target specifications
2. **NEVER assume package structures** - extract from target specifications
3. **NEVER assume naming conventions** - extract from target specifications
4. **NEVER assume architectural patterns** - extract from target specifications
5. **ALWAYS reference target specification sections** for every pattern used
6. **ALWAYS check existing technical designs** for consistency
7. **ALWAYS use keyword-based search** to discover patterns in target specifications
8. **ALWAYS cite sources** for every design decision

---

## Notes

**For Code Generators**: When implementing code from these technical designs:
1. Read the technical design for the workpackage
2. Reference the business specification for business rules and requirements
3. Reference the target specification for framework patterns and conventions (as cited in the technical design)
4. Reference the database schema for data structures
5. Use the technical design as the PRIMARY implementation guide
6. Follow the package structure and naming conventions exactly as specified (derived from target spec)
7. Implement all specified methods and classes
8. Include all validation, error handling, and logging as specified (following target spec patterns)

**Design Philosophy**: These technical designs bridge the gap between "what to build" (business specs) and "how to build it" (target specs). They provide the concrete implementation roadmap that makes code generation deterministic and consistent, while remaining adaptable to any target technology stack or architectural pattern.
- **Batch Processing Layer**: [Jobs, schedulers, processors]
- **Infrastructure Layer**: [Configuration, security, monitoring]

---

## 2. Backend Implementation

### 2.1 Package Structure
Define the complete package structure for this workpackage:

```
com.example.project
├── [domain-module]/              # Domain module name (e.g., customer, account, transaction)
│   ├── api/                      # REST controllers
│   │   ├── [Entity]Controller.java
│   │   ├── dto/                  # Request/Response DTOs
│   │   │   ├── [Entity]Request.java
│   │   │   ├── [Entity]Response.java
│   │   │   └── [Entity]UpdateRequest.java
│   │   └── mapper/               # DTO mappers
│   │       └── [Entity]Mapper.java
│   ├── domain/                   # Domain model
│   │   ├── model/                # Domain entities
│   │   │   └── [Entity].java
│   │   ├── repository/           # Data access
│   │   │   └── [Entity]Repository.java
│   │   └── service/              # Business logic
│   │       ├── [Entity]Service.java
│   │       └── impl/
│   │           └── [Entity]ServiceImpl.java
│   ├── exception/                # Domain-specific exceptions
│   │   └── [Entity]NotFoundException.java
│   └── validation/               # Custom validators
│       └── [Entity]Validator.java
```

**Rationale**: [Explain why this structure - reference target specification patterns]

### 2.2 API Endpoints

For each API endpoint required by the business specification:

#### 2.2.1 [Endpoint Name] - [HTTP Method] [URL Path]

**Business Requirement**: [Reference specific requirement from business spec]

**Endpoint Details:**
- **HTTP Method**: GET/POST/PUT/DELETE/PATCH
- **URL Path**: `/api/v1/[resource]/[path]`
- **Controller**: `[Entity]Controller.java`
- **Method Name**: `[methodName]`

**Request:**
```java
// Request DTO structure
public class [Entity]Request {
    // Field definitions with validation annotations
    @NotNull
    @Size(min = 1, max = 100)
    private String fieldName;
    
    // Include all required fields from business spec
}
```

**Response:**
```java
// Response DTO structure
public class [Entity]Response {
    private Long id;
    private String fieldName;
    // Include all fields needed by frontend/consumers
}
```

**HTTP Status Codes:**
- 200 OK: [When]
- 201 Created: [When]
- 400 Bad Request: [When - validation failures]
- 404 Not Found: [When - resource not found]
- 500 Internal Server Error: [When - unexpected errors]

**Controller Implementation Guidance:**
```java
@RestController
@RequestMapping("/api/v1/[resource]")
public class [Entity]Controller {
    
    @PostMapping
    public ResponseEntity<[Entity]Response> create[Entity](
        @Valid @RequestBody [Entity]Request request) {
        // 1. Validate request (Bean Validation handles this)
        // 2. Call service layer
        // 3. Map result to response DTO
        // 4. Return appropriate HTTP status
    }
}
```

**Validation Rules**: [List all validation rules from business spec]
**Error Handling**: [Specify error responses and messages]
**Security**: [Authentication/authorization requirements]

### 2.3 Service Layer

For each service class:

#### 2.3.1 [Entity]Service

**Responsibility**: [What business logic this service handles]

**Interface:**
```java
public interface [Entity]Service {
    [Entity] create[Entity]([Entity]CreateCommand command);
    [Entity] update[Entity](Long id, [Entity]UpdateCommand command);
    [Entity] get[Entity]ById(Long id);
    List<[Entity]> findAll[Entity]s([Entity]SearchCriteria criteria);
    void delete[Entity](Long id);
}
```

**Implementation Guidance:**

**Method: create[Entity]**
```java
public [Entity] create[Entity]([Entity]CreateCommand command) {
    // Step 1: Validate business rules
    //   - [List specific business rules from business spec]
    //   - Example: Check if entity already exists
    //   - Example: Validate relationships with other entities
    
    // Step 2: Create domain entity
    //   - Map command to entity
    //   - Set default values
    //   - Generate IDs if needed
    
    // Step 3: Persist entity
    //   - Use repository.save()
    //   - Handle database constraints
    
    // Step 4: Trigger domain events (if applicable)
    //   - Example: EntityCreatedEvent
    
    // Step 5: Return created entity
}
```

**Business Rules Implementation**: [Detail each business rule from business spec]
- Rule 1: [Description and implementation approach]
- Rule 2: [Description and implementation approach]

**Transaction Management**: [@Transactional configuration and isolation level]
**Error Handling**: [What exceptions to throw and when]
**Logging**: [What to log at each step]

### 2.4 Data Access Layer

#### 2.4.1 Entity Mapping

**Database Table**: [Table name from {{DATABASE_GEN_SRC}}/new_sqlite_ddl.sql]

**JPA Entity:**
```java
@Entity
@Table(name = "[table_name]")
public class [Entity] {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "[column_name]", nullable = false, length = 100)
    private String fieldName;
    
    // Map all columns from database schema
    // Include relationships (@OneToMany, @ManyToOne, etc.)
    // Include audit fields (createdAt, updatedAt, createdBy, updatedBy)
}
```

**Field Mappings**: [Map each business spec field to database column]
- Business Field → Database Column → Java Field
- [field1] → [column1] → [javaField1]

#### 2.4.2 Repository

**Repository Interface:**
```java
public interface [Entity]Repository extends JpaRepository<[Entity], Long> {
    
    // Custom query methods based on business requirements
    Optional<[Entity]> findBy[UniqueField](String value);
    List<[Entity]> findBy[Criteria](String criteria);
    
    // Complex queries using @Query if needed
    @Query("SELECT e FROM [Entity] e WHERE ...")
    List<[Entity]> findByComplexCriteria(...);
}
```

**Query Methods**: [List all required queries from business spec and test cases]

### 2.5 Exception Handling

**Domain Exceptions:**
```java
// Define custom exceptions for this workpackage
public class [Entity]NotFoundException extends RuntimeException {
    public [Entity]NotFoundException(Long id) {
        super("Entity not found with id: " + id);
    }
}

public class [Entity]ValidationException extends RuntimeException {
    // For business rule violations
}
```

**Global Exception Handler**: [Reference target specification for error response format]

---

## 3. Frontend Implementation

### 3.1 Component Structure

Define the React/Angular/Vue component structure:

```
src/
├── features/
│   └── [feature-name]/
│       ├── components/
│       │   ├── [Entity]List.tsx
│       │   ├── [Entity]Detail.tsx
│       │   ├── [Entity]Form.tsx
│       │   └── [Entity]Card.tsx
│       ├── hooks/
│       │   ├── use[Entity].ts
│       │   └── use[Entity]List.ts
│       ├── services/
│       │   └── [entity]Service.ts
│       ├── types/
│       │   └── [entity].types.ts
│       └── pages/
│           ├── [Entity]ListPage.tsx
│           └── [Entity]DetailPage.tsx
```

### 3.2 Pages and Routes

For each user-facing page:

#### 3.2.1 [Page Name]

**Business Requirement**: [Reference from business spec]
**Route**: `/[path]`
**Component**: `[Page]Component`

**Page Responsibilities:**
- Display: [What data to show]
- Actions: [What user actions are supported]
- Navigation: [Where users can navigate from this page]

**Component Structure:**
```typescript
export const [Page]Component: React.FC = () => {
    // State management
    const [entities, setEntities] = useState<Entity[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    
    // API calls
    useEffect(() => {
        // Fetch data on mount
    }, []);
    
    // Event handlers
    const handleCreate = async (data: EntityRequest) => {
        // Call backend API
        // Handle success/error
        // Update UI
    };
    
    // Render
    return (
        // JSX structure
    );
};
```

### 3.3 API Integration

**Service Layer:**
```typescript
// [entity]Service.ts
export class [Entity]Service {
    private baseUrl = '/api/v1/[resource]';
    
    async create[Entity](request: [Entity]Request): Promise<[Entity]Response> {
        // HTTP POST to backend
        // Error handling
        // Response mapping
    }
    
    async get[Entity](id: number): Promise<[Entity]Response> {
        // HTTP GET
    }
    
    // All CRUD operations
}
```

### 3.4 State Management

**State Structure**: [Redux/Context/Zustand approach from target spec]
**Actions**: [List all state actions needed]
**Selectors**: [List all data selectors needed]

### 3.5 Form Handling

For each form:

**Form: [Form Name]**
- **Purpose**: [What this form does]
- **Fields**: [List all fields from business spec]
- **Validation**: [Client-side validation rules]
- **Submission**: [What happens on submit]

**Form Implementation:**
```typescript
interface [Entity]FormData {
    // Form field types
}

const [Entity]Form: React.FC = () => {
    const { register, handleSubmit, formState: { errors } } = useForm<[Entity]FormData>();
    
    const onSubmit = async (data: [Entity]FormData) => {
        // Validate
        // Call API
        // Handle response
    };
    
    return (
        <form onSubmit={handleSubmit(onSubmit)}>
            {/* Form fields with validation */}
        </form>
    );
};
```

---

## 4. Batch Processing Implementation

### 4.1 Batch Job Definition

**Job Name**: [Job name from business spec]
**Purpose**: [What this batch job does]
**Schedule**: [When it runs - cron expression]
**Trigger**: [Scheduled/Manual/Event-driven]

### 4.2 Job Structure

```java
@Component
public class [Job]BatchJob {
    
    @Scheduled(cron = "[cron-expression]")
    public void execute() {
        // Step 1: Read data
        // Step 2: Process data
        // Step 3: Write results
        // Step 4: Handle errors
        // Step 5: Log completion
    }
}
```

### 4.3 Processing Logic

**Input**: [Where data comes from]
**Processing Steps**:
1. [Step 1 description and implementation approach]
2. [Step 2 description and implementation approach]
3. [Step 3 description and implementation approach]

**Output**: [Where results go]
**Error Handling**: [How to handle failures]
**Monitoring**: [What metrics to track]

---

## 5. Cross-Cutting Concerns

### 5.1 Security

**Authentication**: [How this workpackage handles authentication]
- Reference: [Target specification section]
- Implementation: [Specific approach for this workpackage]

**Authorization**: [What permissions are required]
- Roles: [List required roles]
- Permissions: [List required permissions]
- Enforcement: [Where and how to enforce]

### 5.2 Validation

**Input Validation**:
- Bean Validation annotations: [List all validations]
- Custom validators: [List any custom validation logic]

**Business Rule Validation**:
- [Rule 1]: [How to validate]
- [Rule 2]: [How to validate]

### 5.3 Error Handling

**Error Scenarios**: [List all error scenarios from test cases]
**Error Responses**: [Format and content of error responses]
**Logging**: [What to log for each error type]

### 5.4 Logging and Monitoring

**Log Points**:
- Entry/exit of service methods
- Business rule validations
- External API calls
- Error conditions

**Metrics to Track**:
- API response times
- Success/failure rates
- Business metrics (e.g., transactions processed)

### 5.5 Testing Guidance

**Unit Tests**: [What to unit test]
- Service layer business logic
- Validation logic
- Utility methods

**Integration Tests**: [What to integration test]
- API endpoints
- Database operations
- External service integrations

**Test Data**: [Reference test cases document for test scenarios]

---

## 6. Data Flow

### 6.1 Request Flow

Diagram the complete flow for key operations:

```
[Frontend Component]
    ↓ (HTTP Request)
[Backend Controller]
    ↓ (DTO Validation)
[Service Layer]
    ↓ (Business Logic)
[Repository Layer]
    ↓ (SQL Query)
[Database]
    ↓ (Result)
[Service Layer]
    ↓ (DTO Mapping)
[Controller]
    ↓ (HTTP Response)
[Frontend Component]
```

### 6.2 Data Transformations

Document all data transformations:
- **Frontend → Backend**: [Request DTO mapping]
- **Backend → Database**: [Entity mapping]
- **Database → Backend**: [Entity to DTO mapping]
- **Backend → Frontend**: [Response DTO mapping]

---

## 7. Integration Points

### 7.1 Internal Dependencies

**Depends On** (other workpackages):
- WP-XXX: [What functionality is needed and how to integrate]

**Depended Upon By** (other workpackages):
- WP-YYY: [What functionality this provides]

### 7.2 External Dependencies

**External Services**:
- Service Name: [Purpose, API endpoints, authentication]

**Third-Party Libraries**:
- Library Name: [Purpose, version, usage]

---

## 8. Implementation Notes

### 8.1 Design Decisions

Document key design decisions:
- **Decision**: [What was decided]
- **Rationale**: [Why this approach]
- **Alternatives Considered**: [What else was considered]
- **Trade-offs**: [Pros and cons]

### 8.2 Assumptions

List all assumptions made:
- [Assumption 1]: [What is assumed and why]
- [Assumption 2]: [What is assumed and why]

### 8.3 Open Questions

List any unresolved questions:
- [Question 1]: [What needs clarification]
- [Question 2]: [What needs clarification]

### 8.4 Migration Considerations

**Legacy System Mapping**:
- Legacy Component → Modern Component
- [Legacy program] → [Modern service/API]

**Data Migration**:
- [What data needs to be migrated]
- [How to handle data transformation]

---

## 9. Code Generation Guidance

### 9.1 Generation Order

Recommended order for code generation:
1. Database entities (JPA)
2. Repository interfaces
3. Service interfaces and implementations
4. DTOs (Request/Response)
5. Controllers
6. Frontend services
7. Frontend components
8. Batch jobs (if applicable)

### 9.2 Naming Conventions

**Backend**:
- Entities: `[Entity].java` (e.g., `Customer.java`)
- Services: `[Entity]Service.java`, `[Entity]ServiceImpl.java`
- Controllers: `[Entity]Controller.java`
- DTOs: `[Entity]Request.java`, `[Entity]Response.java`
- Repositories: `[Entity]Repository.java`

**Frontend**:
- Components: `[Entity][Type].tsx` (e.g., `CustomerList.tsx`)
- Services: `[entity]Service.ts` (camelCase)
- Types: `[entity].types.ts`

### 9.3 Code Templates

Reference sample code from {{TARGET_SAMPLE_CODE}} for:
- Controller template
- Service template
- Repository template
- Component template

---

## 10. References

### 10.1 Business Requirements
- Business Specification: {{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-XXX-specification.md
- Test Cases: {{TEST_GENERATION_DOMAIN_BASE_PATH}}/WP-XXX-tests.md

### 10.2 Technical Specifications
- Target Backend Spec: {{TARGET_SPECIFICATION}}/02-BACKEND-SPECIFICATION.md
- Target Frontend Spec: {{TARGET_SPECIFICATION}}/01-FRONTEND-SPECIFICATION.md
- Target Batch Spec: {{TARGET_SPECIFICATION}}/03-BATCH-SPECIFICATION.md
- Database Schema: {{DATABASE_GEN_SRC}}/new_sqlite_ddl.sql

### 10.3 Sample Code
- Backend Samples: {{TARGET_SAMPLE_CODE}}/backend/
- Frontend Samples: {{TARGET_SAMPLE_CODE}}/frontend/
- Batch Samples: {{TARGET_SAMPLE_CODE}}/batch/

---

## Appendix: Quick Reference

### API Endpoints Summary
| Method | Path | Purpose | Request | Response |
|--------|------|---------|---------|----------|
| POST | /api/v1/[resource] | Create | [Entity]Request | [Entity]Response |
| GET | /api/v1/[resource]/{id} | Get by ID | - | [Entity]Response |
| PUT | /api/v1/[resource]/{id} | Update | [Entity]UpdateRequest | [Entity]Response |
| DELETE | /api/v1/[resource]/{id} | Delete | - | 204 No Content |
| GET | /api/v1/[resource] | List all | Query params | List<[Entity]Response> |

### Database Tables Used
| Table | Purpose | Key Columns |
|-------|---------|-------------|
| [table1] | [purpose] | [columns] |

### Frontend Routes
| Route | Component | Purpose |
|-------|-----------|---------|
| /[path] | [Component] | [Purpose] |

```

---

### Step 4: Quality Checks

For each technical design document, verify:

- [ ] All API endpoints from business spec are documented
- [ ] All database tables referenced are in the DB schema
- [ ] All business rules have implementation guidance
- [ ] Package structure follows target specification patterns
- [ ] Frontend components map to user requirements
- [ ] Batch jobs (if any) are fully specified
- [ ] Security requirements are addressed
- [ ] Error handling is comprehensive
- [ ] Integration points are documented
- [ ] Code generation guidance is clear

### Step 5: Update Progress Tracking

After completing each workpackage:
1. Update {{TECHNICAL_DESIGN_PROGRESS}}
2. Mark workpackage as "completed"
3. Document any issues or blockers
4. Note dependencies on other workpackages

---

## Success Criteria

- [ ] Technical design created for ALL workpackages
- [ ] Each design is implementation-ready (sufficient detail for code generation)
- [ ] All designs reference (not duplicate) business specs, target specs, and DB schemas
- [ ] Layering is clear (frontend/backend/batch separation)
- [ ] API contracts are fully specified
- [ ] Package structures follow target specification patterns
- [ ] Integration points between workpackages are documented
- [ ] Security and error handling are addressed
- [ ] Code generation guidance is provided
- [ ] Progress tracking is complete

---

## Notes

**For Code Generators**: When implementing code from these technical designs:
1. Read the technical design for the workpackage
2. Reference the business specification for business rules and requirements
3. Reference the target specification for framework patterns and conventions
4. Reference the database schema for data structures
5. Use the technical design as the PRIMARY implementation guide
6. Follow the package structure and naming conventions exactly
7. Implement all specified methods and classes
8. Include all validation, error handling, and logging as specified

**Design Philosophy**: These technical designs bridge the gap between "what to build" (business specs) and "how to build it" (target specs). They provide the concrete implementation roadmap that makes code generation deterministic and consistent.

