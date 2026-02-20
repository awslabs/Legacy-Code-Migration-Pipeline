# Migration Mapping Specification - Usage Guide

## Overview

The Migration Mapping Specification is a critical bridge document that connects:
- **Business Specifications** (WHAT to build, technology-agnostic)
- **Chapter 6 Legacy References** (WHERE it came from, legacy patterns)
- **Target Technical Specifications** (HOW to build, modern patterns)

This document is created during **Phase 5.0 (Technical Specification Extraction)** and used by all code generation phases (5.2, 5.3, 5.4).

## Purpose

### The Problem It Solves

Without this document, code generation agents might:
- Generate simple implementations without considering enterprise patterns
- Miss authentication/authorization requirements
- Ignore cross-cutting concerns like logging, monitoring, security
- Fail to map legacy patterns to modern equivalents correctly

### The Solution

The Migration Mapping Specification provides:
1. **Cross-Cutting Patterns** (Section 1): Reusable patterns for all workpackages
2. **Workpackage-Specific Mappings** (Section 2): Detailed mappings per workpackage
3. **Code Generation Guidance** (Section 3): Step-by-step instructions for agents
4. **Quality Checklists** (Section 4): Verification criteria
5. **Pattern Reference** (Section 5): Quick lookup tables

## Document Structure

```
Migration Mapping Specification
├── Section 1: Cross-Cutting Patterns (applies to ALL workpackages)
│   ├── 1.1 Authentication & Authorization
│   ├── 1.2 Data Persistence
│   ├── 1.3 Transaction Management
│   ├── 1.4 API Design & Endpoints
│   ├── 1.5 Validation
│   ├── 1.6 Error Handling
│   ├── 1.7 Logging & Monitoring
│   └── 1.8 Concurrency Control
│
├── Section 2: Workpackage-Specific Mappings (one per WP)
│   └── 2.{WP-ID}: {Workpackage Name}
│       ├── 2.{WP-ID}.1 Technology Mapping
│       ├── 2.{WP-ID}.2 Business Logic Preservation
│       ├── 2.{WP-ID}.3 API Design
│       ├── 2.{WP-ID}.4 Data Model Mapping
│       ├── 2.{WP-ID}.5 Service Layer Design
│       └── 2.{WP-ID}.6 Special Considerations
│
├── Section 3: Code Generation Guidance
│   ├── 3.1 For Backend Code Generation
│   ├── 3.2 For Frontend Code Generation
│   └── 3.3 For Batch Code Generation
│
├── Section 4: Quality Assurance Checklist
├── Section 5: Common Migration Patterns Reference
├── Section 6: Assumptions and Gaps
└── Section 7: Document Control
```

## How to Create This Document (Phase 5.0)

### Phase 5.0.0: Tech Spec Extraction Specialist

The `tech_spec_extraction_specialist` agent creates this document by:

1. **Reading Source Documents**:
   - Target specifications (`{{TARGET_SPECIFICATION}}/`)
   - All business specifications with Chapter 6
   - Workpackage planning

2. **Populating Section 1 (Cross-Cutting Patterns)**:
   - Extract patterns from target specifications
   - Document authentication approach (Common Spec 4.3)
   - Document data persistence approach (Backend Spec 2.4, 5, 6)
   - Document transaction management (Backend Spec 7.2)
   - Document API design standards (Backend Spec 4)
   - Document validation approach (Backend Spec 9)
   - Document error handling (Backend Spec 7.3)
   - Document logging/monitoring (Backend Spec 16, Common Spec 4.2)
   - Document concurrency control (Backend Spec 5.1)

3. **Populating Section 2 (Workpackage Mappings)**:
   For each workpackage:
   - Read business specification Chapter 6.7 (Migration Considerations)
   - Extract "Technology Dependencies to Remove"
   - Extract "Business Logic to Preserve"
   - Map legacy technologies to modern equivalents using Section 1 patterns
   - Create technology mapping table
   - Create business logic preservation table
   - Design API endpoints based on business functions
   - Map data files to database tables
   - Design service layer based on business functions
   - Document special considerations

4. **Populating Section 3 (Code Generation Guidance)**:
   - Provide step-by-step instructions for backend generation
   - Provide step-by-step instructions for frontend generation
   - Provide step-by-step instructions for batch generation

5. **Populating Section 4 (Quality Checklist)**:
   - Create verification checklist based on requirements

6. **Populating Section 5 (Pattern Reference)**:
   - Create quick reference tables for common patterns

7. **Documenting Section 6 (Assumptions & Gaps)**:
   - Document any assumptions made
   - Document any information gaps
   - Document items needing verification

### Phase 5.0.1: Tech Spec Review Specialist

The `tech_spec_review_specialist` agent reviews this document by:

1. **Completeness Verification**:
   - All sections populated
   - All workpackages have mappings
   - All cross-cutting patterns documented

2. **Accuracy Verification**:
   - Technology mappings match target specifications
   - Business logic preservation requirements are clear
   - API designs follow RESTful conventions
   - Data models preserve business entities

3. **Consistency Verification**:
   - Patterns consistent across workpackages
   - Terminology consistent throughout
   - No contradictions between sections

4. **Traceability Verification**:
   - All mappings traceable to source specifications
   - All business rules accounted for
   - All business functions mapped

5. **Implementation Readiness**:
   - Sufficient detail for code generation
   - Clear guidance for agents
   - Quality checklist comprehensive

## How to Use This Document (Code Generation Phases)

### Phase 5.2: Backend Code Generation

The `development_specialist_code_generation` agent uses this document by:

1. **Reading Order**:
   - FIRST: Read this Migration Mapping Specification
   - SECOND: Read business specification for workpackage
   - THIRD: Read target technical specifications for details

2. **Using Section 1 (Cross-Cutting Patterns)**:
   - Apply authentication pattern to all endpoints
   - Apply data persistence pattern to all entities
   - Apply transaction management to all service methods
   - Apply validation pattern to all DTOs
   - Apply error handling to all controllers
   - Apply logging to all services
   - Apply concurrency control to all entities

3. **Using Section 2.{WP-ID} (Workpackage Mapping)**:
   - Use 2.{WP-ID}.1 for technology choices
   - Use 2.{WP-ID}.2 to ensure business logic preservation
   - Use 2.{WP-ID}.3 to create REST controllers and DTOs
   - Use 2.{WP-ID}.4 to create JPA entities and repositories
   - Use 2.{WP-ID}.5 to create service layer
   - Use 2.{WP-ID}.6 for special considerations

4. **Using Section 3.1 (Backend Guidance)**:
   - Follow step-by-step approach
   - Verify traceability at each step

5. **Using Section 4 (Quality Checklist)**:
   - Verify all items before completion

### Phase 5.3: Frontend Code Generation

The `development_specialist_code_generation` agent uses this document by:

1. **Reading Order**:
   - FIRST: Read Section 2.{WP-ID}.3 (API Design) for endpoints
   - SECOND: Read business specification for UI requirements
   - THIRD: Read frontend technical specification for patterns

2. **Using the Mapping**:
   - Use API endpoint definitions to create API client services
   - Use DTO definitions to create TypeScript interfaces
   - Use business entities to design UI data models
   - Use process flows to design UI workflows

3. **Using Section 3.2 (Frontend Guidance)**:
   - Follow step-by-step approach

### Phase 5.4: Batch Code Generation

The `development_specialist_code_generation` agent uses this document by:

1. **Reading Order**:
   - FIRST: Read Section 1.2 (Data Persistence) for data access
   - SECOND: Read Section 2.{WP-ID}.4 (Data Model) for entities
   - THIRD: Read business specification for batch requirements

2. **Using the Mapping**:
   - Use entity definitions for ItemReader/ItemWriter
   - Use business rules for ItemProcessor
   - Use data model for database access

3. **Using Section 3.3 (Batch Guidance)**:
   - Follow step-by-step approach

## Example: WP-001 Authentication Scenario

### The Problem (Without Migration Mapping)

**Business Spec Chapter 5** says:
- "User is authenticated and authorized"

**Chapter 6.7** says:
- "CICS transaction processing → REST API or microservice"
- "Platform-agnostic validation"

**Code Generator** without mapping might create:
```java
@RestController
public class AccountController {
    @GetMapping("/accounts/{id}")
    public Account getAccount(@PathVariable Long id) {
        // Simple implementation, no authentication!
        return accountService.getAccount(id);
    }
}
```

### The Solution (With Migration Mapping)

**Migration Mapping Section 1.1** says:
- Technology: OAuth 2.0 / OpenID Connect, JWT tokens
- Implementation: Spring Security with OAuth2 Resource Server
- Authorization: Use @PreAuthorize for method-level security

**Migration Mapping Section 2.1.3** says:
- Endpoint: GET /api/v1/accounts/{id}
- Security: @PreAuthorize("hasAnyRole('ACCOUNT_MANAGER', 'CUSTOMER_SERVICE')")

**Code Generator** with mapping creates:
```java
@RestController
@RequestMapping("/api/v1/accounts")
public class AccountController {
    
    @GetMapping("/{id}")
    @PreAuthorize("hasAnyRole('ACCOUNT_MANAGER', 'CUSTOMER_SERVICE')")
    public ResponseEntity<AccountResponse> getAccount(@PathVariable Long id) {
        AccountResponse response = accountService.getAccount(id);
        return ResponseEntity.ok(response);
    }
}
```

With Spring Security configuration:
```java
@Configuration
@EnableMethodSecurity
public class SecurityConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .oauth2ResourceServer(oauth2 -> oauth2.jwt())
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/actuator/health").permitAll()
                .anyRequest().authenticated()
            );
        return http.build();
    }
}
```

## Benefits

### 1. Consistency
All workpackages use the same authentication pattern, same data persistence pattern, etc.

### 2. Completeness
Code generators don't miss cross-cutting concerns like security, logging, monitoring.

### 3. Traceability
Clear mapping from legacy patterns to modern patterns, from business rules to code.

### 4. Quality
Quality checklist ensures all requirements are met.

### 5. Maintainability
Single source of truth for migration patterns, easy to update if patterns change.

## File Locations

**Template**: `structure/templates/Migration_Mapping_Spec.md`

**Generated Document**: `{{TECH_SPEC_BASE_PATH}}/specs/migration-mapping-spec.md`

**Referenced By**:
- Phase 5.2: Backend Code Generation
- Phase 5.3: Frontend Code Generation
- Phase 5.4: Batch Code Generation

## Next Steps

1. Update `phase_5.0.0_tech_spec_creation.md` to include creating this document
2. Update `phase_5.0.1_tech_spec_review.md` to include reviewing this document
3. Update `phase_5.2_backend_generation.md` to reference this document
4. Update `phase_5.3_frontend_generation.md` to reference this document
5. Update `phase_5.4_batch_generation.md` to reference this document
6. Update tech spec team agent profiles to include this document in their workflows

---

**End of Usage Guide**
