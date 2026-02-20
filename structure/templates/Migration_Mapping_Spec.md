# Migration Mapping Specification

**Document Type**: Technical Specification  
**Document Version**: 1.0  
**Extraction Date**: [Date]  
**Source Documents**: 
- Target Specifications: `{{TARGET_SPECIFICATION}}/`
- Business Specifications: `{{BUSINESS_SPECIFICATION_BASE_PATH}}/`
- Workpackage Planning: `{{WORKPACKAGE_PLANNING}}`

**Status**: Draft

---

## Document Purpose

This document provides the definitive mapping between legacy implementation patterns (documented in Chapter 6 of business specifications) and modern target implementation patterns (documented in target technical specifications). It serves as the primary reference for code generation phases to ensure consistent, correct translation of legacy systems to modern architecture.

**Key Objectives**:
1. Map legacy technologies to modern equivalents
2. Preserve business logic while modernizing implementation
3. Provide reusable patterns across all workpackages
4. Ensure consistency in technology choices
5. Guide code generation with specific implementation details

---

## 1. Cross-Cutting Patterns

These patterns apply to ALL workpackages unless explicitly overridden in workpackage-specific sections.

### 1.1 Authentication & Authorization

**Legacy Pattern**:
- Technology: [e.g., CICS security, RACF, mainframe user validation]
- Implementation: [e.g., User ID validation in COBOL programs]
- Security Model: [e.g., Terminal-based access control]

**Modern Pattern**:
- Technology: [e.g., OAuth 2.0 / OpenID Connect, JWT tokens]
- Implementation: [e.g., Spring Security with OAuth2 Resource Server]
- Security Model: [e.g., Role-Based Access Control (RBAC)]

**🚨 EXTERNAL SERVICE INTEGRATION**: [YES/NO]
- If YES: **DO NOT IMPLEMENT USER STORAGE, PASSWORD HASHING, OR CREDENTIAL MANAGEMENT**
- External Service: [e.g., Keycloak, Auth0, Okta, Azure AD, AWS Cognito]
- Integration Type: [e.g., OAuth2 Resource Server, LDAP client, SAML SP]
- Service Endpoint: [e.g., https://auth.example.com]
- Protocol: [e.g., OAuth 2.0 + OIDC, LDAP, SAML 2.0]

**Implementation Guidance**:
```
Framework: Spring Security 6.x
Dependencies:
  - spring-boot-starter-security
  - spring-boot-starter-oauth2-resource-server  # For OAuth2 integration

Configuration:
  - Configure JWT issuer URI (points to external OAuth2 server)
  - Configure JWK set URI (for token validation)
  - Implement JwtAuthenticationConverter
  - Map JWT claims to Spring Security authorities
  - DO NOT create User entity, UserRepository, or password storage
  - DO NOT implement login/logout endpoints (handled by OAuth2 server)

Authorization:
  - Use @PreAuthorize for method-level security
  - Use hasRole() for role-based checks
  - Use hasAuthority() for permission-based checks

Example:
  @PreAuthorize("hasRole('ACCOUNT_MANAGER')")
  public AccountResponse updateAccount(Long id, AccountRequest request)
  
  # application.yml
  spring:
    security:
      oauth2:
        resourceserver:
          jwt:
            issuer-uri: https://auth.example.com/realms/myapp
            jwk-set-uri: https://auth.example.com/realms/myapp/protocol/openid-connect/certs
```

**Source References**:
- Common Spec: Section 4.3 (Security Standards)
- Backend Spec: Section 10 (Security Standards)
- Target Sample Code: [path if available]

**Traceability**:
- Applies to: All workpackages requiring user authentication
- Business Rules: Preserves access control requirements from business specs

---

### 1.2 Data Persistence

**Legacy Pattern**:
- Technology: [e.g., VSAM KSDS/ESDS/RRDS files]
- Access Method: [e.g., COBOL file I/O, EXEC CICS READ/WRITE]
- Data Format: [e.g., Fixed-length records, COBOL copybooks]

**Modern Pattern**:
- Technology: [e.g., PostgreSQL 15.x, AWS RDS]
- Access Method: [e.g., Spring Data JPA, JpaRepository]
- Data Format: [e.g., Relational tables, JPA entities]

**Implementation Guidance**:
```
Framework: Spring Data JPA 3.x
Dependencies:
  - spring-boot-starter-data-jpa
  - postgresql (JDBC driver)
  - flyway-core (database migrations)

Entity Design:
  - Use @Entity for domain objects
  - Use @Table(name, indexes) for table mapping
  - Use @Id with @GeneratedValue for primary keys
  - Use @Column for column constraints
  - Include audit fields (@CreatedDate, @LastModifiedDate)
  - Use @Version for optimistic locking

Repository Design:
  - Extend JpaRepository<Entity, ID>
  - Use method naming conventions for simple queries
  - Use @Query for complex queries
  - Use @EntityGraph to avoid N+1 queries

Example:
  @Entity
  @Table(name = "accounts", indexes = {
    @Index(name = "idx_account_status", columnList = "status")
  })
  public class Account {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Version
    private Long version;
    
    @CreatedDate
    private Instant createdAt;
  }
```

**Migration Mapping**:
| Legacy File | Modern Table | Key Mapping | Notes |
|-------------|--------------|-------------|-------|
| [VSAM file name] | [table_name] | [legacy key → PK] | [migration notes] |

**Source References**:
- Backend Spec: Section 2.4 (Database), Section 5 (Domain Model), Section 6 (Repository Layer)
- Backend Spec: Section 13 (Database Migrations)
- Target Sample Code: [path if available]

**Traceability**:
- Applies to: All workpackages with data persistence
- Business Rules: Preserves data integrity constraints from business specs

---

### 1.3 Transaction Management

**Legacy Pattern**:
- Technology: [e.g., CICS transaction processing]
- Commands: [e.g., EXEC CICS SYNCPOINT, EXEC CICS SYNCPOINT ROLLBACK]
- Scope: [e.g., Transaction per terminal interaction]

**Modern Pattern**:
- Technology: [e.g., Spring Transaction Management]
- Annotations: [e.g., @Transactional]
- Scope: [e.g., Service method boundaries]

**Implementation Guidance**:
```
Framework: Spring Transaction Management
Dependencies:
  - spring-boot-starter-data-jpa (includes transaction support)

Configuration:
  - Enable transaction management (auto-configured in Spring Boot)
  - Configure transaction manager (auto-configured for JPA)
  - Set default isolation level (READ_COMMITTED)

Service Layer:
  - Apply @Transactional(readOnly = true) at class level
  - Override with @Transactional for write operations
  - Specify isolation level when needed
  - Specify propagation when needed
  - Set timeout for long-running operations

Example:
  @Service
  @Transactional(readOnly = true)
  public class AccountService {
    
    @Transactional(
      isolation = Isolation.READ_COMMITTED,
      propagation = Propagation.REQUIRED,
      timeout = 30
    )
    public AccountResponse updateAccount(Long id, AccountRequest request) {
      // Business logic with automatic transaction management
    }
  }
```

**Transaction Mapping**:
| Legacy Transaction | Modern Transaction Boundary | Isolation Level | Notes |
|-------------------|----------------------------|-----------------|-------|
| [CICS transaction ID] | [Service method] | [isolation level] | [notes] |

**Source References**:
- Backend Spec: Section 7.2 (Transaction Management)
- Target Sample Code: [path if available]

**Traceability**:
- Applies to: All workpackages with data modifications
- Business Rules: Preserves ACID guarantees from legacy system

---

### 1.4 API Design & Endpoints

**Legacy Pattern**:
- Technology: [e.g., CICS transactions, 3270 terminal screens]
- Interface: [e.g., BMS maps, terminal I/O]
- Protocol: [e.g., Terminal emulation, SNA]

**Modern Pattern**:
- Technology: [e.g., RESTful APIs, HTTP/HTTPS]
- Interface: [e.g., JSON request/response]
- Protocol: [e.g., HTTP/1.1, HTTP/2]

**Implementation Guidance**:
```
Framework: Spring Web MVC
Dependencies:
  - spring-boot-starter-web
  - spring-boot-starter-validation
  - springdoc-openapi-starter-webmvc-ui (API documentation)

REST Controller Design:
  - Use @RestController for API controllers
  - Use @RequestMapping for base path
  - Use @GetMapping, @PostMapping, @PutMapping, @DeleteMapping
  - Use @Valid for request validation
  - Use @PathVariable for URL parameters
  - Use @RequestBody for request payload
  - Return ResponseEntity for explicit status codes

URL Structure:
  - /api/v1/{resource}
  - /api/v1/{resource}/{id}
  - /api/v1/{resource}/{id}/{sub-resource}

HTTP Status Codes:
  - 200 OK - Successful GET, PUT, PATCH
  - 201 Created - Successful POST
  - 204 No Content - Successful DELETE
  - 400 Bad Request - Validation error
  - 404 Not Found - Resource not found
  - 409 Conflict - Business rule violation
  - 500 Internal Server Error - Server error

Example:
  @RestController
  @RequestMapping("/api/v1/accounts")
  public class AccountController {
    
    @GetMapping("/{id}")
    public ResponseEntity<AccountResponse> getAccount(@PathVariable Long id) {
      // Implementation
    }
    
    @PutMapping("/{id}")
    public ResponseEntity<AccountResponse> updateAccount(
      @PathVariable Long id,
      @Valid @RequestBody AccountRequest request
    ) {
      // Implementation
    }
  }
```

**Endpoint Mapping Template**:
| Legacy Transaction | HTTP Method | Endpoint | Request | Response | Notes |
|-------------------|-------------|----------|---------|----------|-------|
| [CICS trans ID] | [GET/POST/PUT] | [/api/v1/...] | [DTO] | [DTO] | [notes] |

**Source References**:
- Backend Spec: Section 4 (API Design Standards)
- Backend Spec: Section 8 (DTO Patterns)
- Target Sample Code: [path if available]

**Traceability**:
- Applies to: All workpackages with user interactions
- Business Rules: Preserves business operations from business specs

---

### 1.5 Validation

**Legacy Pattern**:
- Technology: [e.g., COBOL validation paragraphs]
- Implementation: [e.g., IF statements, PERFORM validation routines]
- Error Handling: [e.g., Set error flags, display error messages on screen]

**Modern Pattern**:
- Technology: [e.g., Bean Validation (JSR-380), Custom validators]
- Implementation: [e.g., Annotations, validator components]
- Error Handling: [e.g., MethodArgumentNotValidException, custom exceptions]

**Implementation Guidance**:
```
Framework: Bean Validation (JSR-380)
Dependencies:
  - spring-boot-starter-validation

Request DTO Validation:
  - Use @NotNull, @NotBlank, @NotEmpty
  - Use @Size(min, max) for strings and collections
  - Use @Min, @Max for numbers
  - Use @Pattern(regexp) for format validation
  - Use @Email for email validation
  - Use @Valid for nested objects

Custom Validators:
  - Create @Component validator classes
  - Implement business rule validation
  - Check database constraints (uniqueness, existence)
  - Validate state transitions
  - Throw ValidationException with field errors

Example:
  public class AccountRequest {
    @NotBlank(message = "Account ID is required")
    @Pattern(regexp = "\\d{11}", message = "Account ID must be 11 digits")
    private String accountId;
    
    @NotNull(message = "Credit limit is required")
    @DecimalMin(value = "0.01", message = "Credit limit must be positive")
    private BigDecimal creditLimit;
  }
  
  @Component
  public class AccountValidator {
    public void validateAccountUpdate(AccountRequest request) {
      // Business rule validation
      if (request.getCashLimit().compareTo(request.getCreditLimit()) > 0) {
        throw new ValidationException("Cash limit cannot exceed credit limit");
      }
    }
  }
```

**Validation Mapping Template**:
| Legacy Validation | Modern Validation | Implementation | Error Message | Notes |
|-------------------|-------------------|----------------|---------------|-------|
| [COBOL paragraph] | [Annotation/Validator] | [code pattern] | [message] | [notes] |

**Source References**:
- Backend Spec: Section 9 (Validation Standards)
- Backend Spec: Section 7.4 (Business Validation)
- Target Sample Code: [path if available]

**Traceability**:
- Applies to: All workpackages with input validation
- Business Rules: Implements validation rules from business specs (BR-XXX-XXX)

---

### 1.6 Error Handling

**Legacy Pattern**:
- Technology: [e.g., COBOL error flags, CICS HANDLE CONDITION]
- Implementation: [e.g., 88-level conditions, error paragraphs]
- User Feedback: [e.g., Error messages on terminal screen]

**Modern Pattern**:
- Technology: [e.g., Exception handling, @RestControllerAdvice]
- Implementation: [e.g., Custom exceptions, global exception handler]
- User Feedback: [e.g., JSON error responses with status codes]

**Implementation Guidance**:
```
Framework: Spring Exception Handling
Dependencies:
  - spring-boot-starter-web (includes exception handling)

Custom Exceptions:
  - Create domain-specific exceptions extending RuntimeException
  - Include meaningful error messages
  - Include relevant context (e.g., resource ID)

Exception Types:
  - ResourceNotFoundException (404)
  - BusinessException (409)
  - ValidationException (400)
  - UnauthorizedException (401)

Global Exception Handler:
  - Use @RestControllerAdvice
  - Handle all exception types
  - Return consistent error response structure
  - Log errors appropriately
  - Include correlation ID for tracing

Error Response Structure:
  {
    "timestamp": "2026-02-20T10:30:00Z",
    "status": 400,
    "error": "Bad Request",
    "message": "Validation failed",
    "path": "/api/v1/accounts/123",
    "correlationId": "uuid",
    "errors": [
      {
        "field": "creditLimit",
        "message": "Credit limit must be positive"
      }
    ]
  }

Example:
  @RestControllerAdvice
  public class GlobalExceptionHandler {
    
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(
      ResourceNotFoundException ex,
      HttpServletRequest request
    ) {
      ErrorResponse error = ErrorResponse.builder()
        .timestamp(Instant.now())
        .status(HttpStatus.NOT_FOUND.value())
        .error("Not Found")
        .message(ex.getMessage())
        .path(request.getRequestURI())
        .correlationId(getCorrelationId(request))
        .build();
      return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
    }
  }
```

**Error Mapping Template**:
| Legacy Error Condition | Modern Exception | HTTP Status | Error Message | Notes |
|------------------------|------------------|-------------|---------------|-------|
| [COBOL error flag] | [Exception class] | [status code] | [message] | [notes] |

**Source References**:
- Backend Spec: Section 7.3 (Exception Handling)
- Target Sample Code: [path if available]

**Traceability**:
- Applies to: All workpackages with error conditions
- Business Rules: Preserves error handling logic from business specs

---

### 1.7 Logging & Monitoring

**Legacy Pattern**:
- Technology: [e.g., COBOL DISPLAY statements, CICS logs]
- Implementation: [e.g., Write to SYSOUT, CICS transient data queues]
- Monitoring: [e.g., Mainframe monitoring tools]

**Modern Pattern**:
- Technology: [e.g., SLF4J with Logback, structured logging]
- Implementation: [e.g., Logger instances, MDC for context]
- Monitoring: [e.g., CloudWatch, Prometheus, Grafana]

**Implementation Guidance**:
```
Framework: SLF4J with Logback
Dependencies:
  - spring-boot-starter-logging (included by default)
  - spring-boot-starter-actuator (for metrics)

Logging:
  - Use @Slf4j annotation (Lombok)
  - Use structured logging (JSON format)
  - Include correlation ID in logs (MDC)
  - Log at appropriate levels (ERROR, WARN, INFO, DEBUG)
  - Never log sensitive data (passwords, tokens, PII)

Log Levels:
  - ERROR: Errors requiring immediate attention
  - WARN: Potential issues
  - INFO: Important business events
  - DEBUG: Detailed diagnostic information

Metrics:
  - Expose Actuator endpoints (/actuator/health, /actuator/metrics)
  - Export metrics to Prometheus
  - Track JVM metrics (heap, GC, threads)
  - Track HTTP metrics (requests, errors, duration)
  - Track database metrics (connections, queries)
  - Track custom business metrics

Example:
  @Slf4j
  @Service
  public class AccountService {
    
    public AccountResponse updateAccount(Long id, AccountRequest request) {
      MDC.put("correlationId", getCorrelationId());
      MDC.put("accountId", id.toString());
      
      log.info("Updating account: accountId={}", id);
      
      try {
        // Business logic
        log.info("Account updated successfully: accountId={}", id);
      } catch (Exception e) {
        log.error("Failed to update account: accountId={}", id, e);
        throw e;
      } finally {
        MDC.clear();
      }
    }
  }
```

**Source References**:
- Backend Spec: Section 16.1 (Logging Standards)
- Backend Spec: Section 16.2 (Metrics)
- Common Spec: Section 4.2 (Monitoring and Observability)
- Target Sample Code: [path if available]

**Traceability**:
- Applies to: All workpackages
- Business Rules: Provides audit trail for business operations

---

### 1.8 Concurrency Control

**Legacy Pattern**:
- Technology: [e.g., CICS record locking, EXEC CICS READ UPDATE]
- Implementation: [e.g., Exclusive locks, retry logic]
- Conflict Resolution: [e.g., Last-write-wins, user notification]

**Modern Pattern**:
- Technology: [e.g., JPA optimistic locking, @Version]
- Implementation: [e.g., Version field, OptimisticLockException]
- Conflict Resolution: [e.g., Exception handling, user notification]

**Implementation Guidance**:
```
Framework: JPA Optimistic Locking
Dependencies:
  - spring-boot-starter-data-jpa

Entity Design:
  - Add @Version field to entities
  - Use Long or Integer for version field
  - JPA automatically increments version on update
  - Throws OptimisticLockException on conflict

Exception Handling:
  - Catch OptimisticLockException
  - Return 409 Conflict status
  - Provide meaningful error message
  - Allow client to retry with fresh data

Example:
  @Entity
  public class Account {
    @Id
    private Long id;
    
    @Version
    private Long version;
    
    // Other fields
  }
  
  @Service
  public class AccountService {
    
    @Transactional
    public AccountResponse updateAccount(Long id, Long version, AccountRequest request) {
      Account account = accountRepository.findById(id)
        .orElseThrow(() -> new ResourceNotFoundException("Account not found"));
      
      // Version check happens automatically during save
      // If version doesn't match, OptimisticLockException is thrown
      
      account.updateFrom(request);
      Account saved = accountRepository.save(account);
      return mapper.toResponse(saved);
    }
  }
  
  @RestControllerAdvice
  public class GlobalExceptionHandler {
    
    @ExceptionHandler(OptimisticLockException.class)
    public ResponseEntity<ErrorResponse> handleOptimisticLock(
      OptimisticLockException ex
    ) {
      ErrorResponse error = ErrorResponse.builder()
        .status(HttpStatus.CONFLICT.value())
        .error("Conflict")
        .message("Record was modified by another user. Please refresh and try again.")
        .build();
      return ResponseEntity.status(HttpStatus.CONFLICT).body(error);
    }
  }
```

**Concurrency Mapping Template**:
| Legacy Locking Mechanism | Modern Mechanism | Conflict Detection | Resolution | Notes |
|--------------------------|------------------|-------------------|------------|-------|
| [CICS READ UPDATE] | [@Version field] | [OptimisticLockException] | [409 Conflict] | [notes] |

**Source References**:
- Backend Spec: Section 5.1 (Entity Design Principles)
- Target Sample Code: [path if available]

**Traceability**:
- Applies to: All workpackages with concurrent updates
- Business Rules: Preserves data integrity from business specs

---

## 2. Workpackage-Specific Mappings

This section provides detailed mappings for each workpackage, based on Chapter 6 of the business specifications.

### Template for Each Workpackage

For each workpackage, document:
1. Technology mapping (legacy → modern)
2. Business logic preservation requirements
3. API design (endpoints, methods, DTOs)
4. Data model mapping (files → tables, entities)
5. Security requirements
6. Special considerations

---

### 2.1 WP-{ID}: {Workpackage Name}

**Business Specification**: `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-{ID}-specification.md`  
**Chapter 6 Reference**: Section 6.7 (Migration Considerations)

#### 2.1.1 Technology Mapping

Based on Chapter 6.7 "Technology Dependencies to Remove":

| Legacy Technology | Modern Technology | Implementation Pattern | Source Reference |
|-------------------|-------------------|------------------------|------------------|
| [Legacy tech from Ch 6] | [Modern tech] | [Pattern from target spec] | [Spec section] |
| [e.g., CICS Transaction CAUP] | [REST API] | [Spring Boot REST Controller] | [Backend Spec 4.1] |
| [e.g., BMS Screen COACTUP] | [Web UI] | [React/Angular Component] | [Frontend Spec 3.2] |
| [e.g., VSAM CARDDAT] | [PostgreSQL table] | [JPA Entity + Repository] | [Backend Spec 5.1, 6.1] |

**Notes**: [Any special considerations for this workpackage]

#### 2.1.2 Business Logic Preservation

Based on Chapter 6.7 "Business Logic to Preserve":

**Business Rules** (from Chapter 3):
| Rule ID | Rule Description | Legacy Implementation | Modern Implementation | Notes |
|---------|------------------|----------------------|----------------------|-------|
| BR-{ID}-{NUM} | [Rule description] | [COBOL paragraph/line] | [Validator/Service method] | [notes] |

**Business Functions** (from Chapter 4):
| Function ID | Function Description | Legacy Implementation | Modern Implementation | Notes |
|-------------|---------------------|----------------------|----------------------|-------|
| F-{ID}-{NUM} | [Function description] | [COBOL paragraph/line] | [Service method] | [notes] |

**Process Flows** (from Chapter 5):
| Flow ID | Flow Description | Legacy Implementation | Modern Implementation | Notes |
|---------|------------------|----------------------|----------------------|-------|
| PF-{ID}-{NUM} | [Flow description] | [COBOL logic flow] | [API workflow] | [notes] |

**Critical Preservation Requirements**:
- [List any critical business logic that MUST be preserved exactly]
- [e.g., Validation sequences must execute in same order]
- [e.g., Optimistic locking strategy must be maintained]

#### 2.1.3 API Design

**Endpoint Mapping**:

Based on legacy transactions and business functions:

| Legacy Transaction | HTTP Method | Endpoint | Request DTO | Response DTO | Business Function | Notes |
|-------------------|-------------|----------|-------------|--------------|-------------------|-------|
| [CICS trans ID] | GET | /api/v1/{resource}/{id} | - | [ResponseDTO] | F-{ID}-{NUM} | [notes] |
| [CICS trans ID] | POST | /api/v1/{resource} | [CreateRequestDTO] | [ResponseDTO] | F-{ID}-{NUM} | [notes] |
| [CICS trans ID] | PUT | /api/v1/{resource}/{id} | [UpdateRequestDTO] | [ResponseDTO] | F-{ID}-{NUM} | [notes] |
| [CICS trans ID] | DELETE | /api/v1/{resource}/{id} | - | - | F-{ID}-{NUM} | [notes] |

**Request/Response DTOs**:

List all DTOs needed for this workpackage:

1. **{ResourceName}Response**:
   - Purpose: [e.g., Return account details]
   - Fields: [List key fields from business entities]
   - Source: Business Entity BE-{ID}-{NUM}

2. **{ResourceName}CreateRequest**:
   - Purpose: [e.g., Create new account]
   - Fields: [List required fields]
   - Validation: [Reference business rules]

3. **{ResourceName}UpdateRequest**:
   - Purpose: [e.g., Update existing account]
   - Fields: [List updatable fields]
   - Validation: [Reference business rules]

**Security Requirements**:
- Authentication: [Required/Optional]
- Authorization: [Roles/Permissions required]
- Implementation: `@PreAuthorize("[expression]")`

#### 2.1.4 Data Model Mapping

Based on Chapter 6.2 "Data Files" and Chapter 2 "Business Entities":

**File to Table Mapping**:

| Legacy File | Access Method | Modern Table | Primary Key | Indexes | Notes |
|-------------|---------------|--------------|-------------|---------|-------|
| [VSAM file name] | [KSDS/ESDS/RRDS] | [table_name] | [pk_column] | [index list] | [notes] |

**Entity Mapping**:

For each business entity (from Chapter 2):

**Entity: {EntityName}** (BE-{ID}-{NUM})

- **Legacy Structure**: [COBOL copybook name]
- **Modern Entity**: [Java class name]
- **Table Name**: [database table name]

**Field Mapping**:
| Legacy Field | COBOL Type | Modern Field | Java Type | JPA Annotation | Validation | Notes |
|--------------|------------|--------------|-----------|----------------|------------|-------|
| [COBOL field] | [PIC X(n)] | [javaField] | [String] | [@Column] | [@NotBlank] | [notes] |
| [COBOL field] | [PIC 9(n)V99] | [javaField] | [BigDecimal] | [@Column] | [@DecimalMin] | [notes] |

**Relationships**:
- [Describe entity relationships]
- [e.g., Account has one Customer (many-to-one)]
- [e.g., Account has many Cards (one-to-many)]

**Indexes**:
- [List required indexes based on query patterns]
- [e.g., Index on account_status for filtering]
- [e.g., Index on customer_id for joins]

**Audit Fields**:
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
- created_by (VARCHAR)
- updated_by (VARCHAR)
- version (BIGINT) - for optimistic locking

#### 2.1.5 Service Layer Design

**Service Classes**:

Based on business functions and process flows:

1. **{ResourceName}Service**:
   - Purpose: [e.g., Orchestrate account operations]
   - Methods:
     - `{methodName}()` → Implements F-{ID}-{NUM}
     - `{methodName}()` → Implements F-{ID}-{NUM}
   - Dependencies:
     - {ResourceName}Repository
     - {ResourceName}Validator
     - {OtherService} (if needed)
   - Transaction Boundaries: [Describe transaction scope]

**Validator Classes**:

Based on business rules:

1. **{ResourceName}Validator**:
   - Purpose: [e.g., Validate account business rules]
   - Methods:
     - `validate{Operation}()` → Implements BR-{ID}-{NUM}, BR-{ID}-{NUM}
   - Dependencies:
     - {ResourceName}Repository (for existence checks)

**Mapper Classes**:

For DTO conversions:

1. **{ResourceName}Mapper** (MapStruct):
   - Purpose: [e.g., Convert between Account entity and DTOs]
   - Methods:
     - `toResponse(Entity)` → Entity to Response DTO
     - `toEntity(CreateRequest)` → Request to Entity
     - `updateEntity(UpdateRequest, @MappingTarget Entity)` → Update entity

#### 2.1.6 Special Considerations

**Performance Requirements**:
- [List any specific performance requirements from business spec]
- [e.g., Response time targets]
- [e.g., Throughput requirements]
- [e.g., Caching strategies]

**Data Migration Requirements**:
- [Describe data migration needs from Chapter 6.7]
- [e.g., Account master data (300-byte records)]
- [e.g., Data transformation rules]
- [e.g., Data validation requirements]

**Integration Points**:
- [List any external system integrations]
- [e.g., Legacy system interfaces during transition]
- [e.g., Third-party services]
- [e.g., Event publishing requirements]

**Testing Considerations**:
- [Reference test cases from Phase 4]
- [List critical test scenarios]
- [Describe test data requirements]

**Deployment Considerations**:
- [Describe deployment strategy]
- [e.g., Strangler fig pattern approach]
- [e.g., Feature flags for gradual rollout]
- [e.g., Rollback procedures]

---

### 2.2 WP-{NEXT-ID}: {Next Workpackage Name}

[Repeat structure for each workpackage]

---

## 3. Code Generation Guidance

This section provides specific guidance for code generation phases.

### 3.1 For Backend Code Generation (Phase 5.2)

**Step-by-Step Approach**:

1. **Read This Document**:
   - Review Section 1 (Cross-Cutting Patterns) for general patterns
   - Review Section 2.{WP-ID} for workpackage-specific mappings
   - Extract technology mappings, API design, data model

2. **Read Business Specification**:
   - Chapter 2: Business Entities → JPA Entities
   - Chapter 3: Business Rules → Validators
   - Chapter 4: Business Functions → Service Methods
   - Chapter 5: Process Flows → API Workflows
   - Chapter 6: Legacy References → Traceability

3. **Read Target Technical Specifications**:
   - Backend Spec: Detailed implementation patterns
   - Common Spec: Cross-cutting concerns

4. **Generate Code**:
   - Create JPA entities based on Section 2.{WP-ID}.4 (Data Model Mapping)
   - Create repositories extending JpaRepository
   - Create validators implementing business rules from Chapter 3
   - Create service classes implementing business functions from Chapter 4
   - Create REST controllers based on Section 2.{WP-ID}.3 (API Design)
   - Create DTOs for requests and responses
   - Create MapStruct mappers for conversions
   - Create exception classes for error handling
   - Create Flyway migration scripts for database schema

5. **Apply Cross-Cutting Patterns**:
   - Add @Transactional annotations (Section 1.3)
   - Add @PreAuthorize for security (Section 1.1)
   - Add logging with @Slf4j (Section 1.7)
   - Add @Version for optimistic locking (Section 1.8)
   - Add validation annotations (Section 1.5)
   - Add exception handling (Section 1.6)

6. **Verify Traceability**:
   - Each business rule (BR-XXX-XXX) → Validator method
   - Each business function (F-XXX-XXX) → Service method
   - Each business entity (BE-XXX-XXX) → JPA Entity
   - Each process flow (PF-XXX-XXX) → API workflow

### 3.2 For Frontend Code Generation (Phase 5.3)

**Step-by-Step Approach**:

1. **Read This Document**:
   - Review Section 2.{WP-ID}.3 (API Design) for endpoints and DTOs
   - Understand request/response structures

2. **Read Business Specification**:
   - Chapter 2: Business Entities → UI data models
   - Chapter 5: Process Flows → UI workflows
   - Chapter 6: Legacy screen layouts → Modern UI design

3. **Read Target Technical Specifications**:
   - Frontend Spec: UI framework, component patterns
   - Common Spec: Cross-cutting concerns

4. **Generate Code**:
   - Create API client services for backend endpoints
   - Create UI components for user interactions
   - Create forms with validation matching backend DTOs
   - Create state management for data flow
   - Create routing for navigation
   - Implement error handling and user feedback

### 3.3 For Batch Code Generation (Phase 5.4)

**Step-by-Step Approach**:

1. **Read This Document**:
   - Review Section 1.2 (Data Persistence) for data access patterns
   - Review Section 2.{WP-ID}.4 (Data Model) for entities

2. **Read Business Specification**:
   - Chapter 2: Business Entities → Batch processing entities
   - Chapter 3: Business Rules → Batch validation
   - Chapter 4: Business Functions → Batch operations

3. **Read Target Technical Specifications**:
   - Batch Spec: Spring Batch patterns
   - Common Spec: Cross-cutting concerns

4. **Generate Code**:
   - Create job configuration classes
   - Create ItemReader for data input
   - Create ItemProcessor for business logic
   - Create ItemWriter for data output
   - Configure chunk size and transaction boundaries
   - Implement error handling and retry logic

---

## 4. Quality Assurance Checklist

Use this checklist to verify that code generation correctly implements the migration mapping.

### 4.1 Technology Mapping Verification

- [ ] All legacy technologies identified in Chapter 6.7 have modern equivalents
- [ ] Modern technologies match target technical specifications
- [ ] No legacy-specific code patterns remain (e.g., CICS commands, COBOL syntax)
- [ ] All dependencies declared in pom.xml/package.json match specifications

### 4.2 Business Logic Preservation Verification

- [ ] All business rules (BR-XXX-XXX) implemented in validators or service methods
- [ ] All business functions (F-XXX-XXX) implemented in service methods
- [ ] All process flows (PF-XXX-XXX) implemented in API workflows
- [ ] Validation sequences execute in same order as legacy
- [ ] Error messages match business specification
- [ ] Business logic is technology-agnostic (no infrastructure concerns)

### 4.3 API Design Verification

- [ ] All endpoints follow RESTful conventions from Backend Spec Section 4.1
- [ ] HTTP methods match CRUD operations appropriately
- [ ] Request DTOs include all required fields from business entities
- [ ] Response DTOs include all relevant fields for clients
- [ ] Validation annotations match business rules
- [ ] Security annotations match authorization requirements
- [ ] OpenAPI documentation generated for all endpoints

### 4.4 Data Model Verification

- [ ] All business entities (BE-XXX-XXX) mapped to JPA entities
- [ ] All legacy fields mapped to modern fields with correct types
- [ ] Relationships between entities correctly defined
- [ ] Indexes created for frequently queried columns
- [ ] Audit fields included (created_at, updated_at, created_by, updated_by)
- [ ] Version field included for optimistic locking
- [ ] Flyway migration scripts create correct schema

### 4.5 Cross-Cutting Concerns Verification

- [ ] Authentication implemented per Section 1.1
- [ ] Transaction management implemented per Section 1.3
- [ ] Validation implemented per Section 1.5
- [ ] Error handling implemented per Section 1.6
- [ ] Logging implemented per Section 1.7
- [ ] Concurrency control implemented per Section 1.8
- [ ] All sensitive data properly secured (no logging, encryption at rest)

### 4.6 Traceability Verification

- [ ] Each business rule traceable to validator/service method
- [ ] Each business function traceable to service method
- [ ] Each business entity traceable to JPA entity
- [ ] Each process flow traceable to API workflow
- [ ] Each legacy file traceable to database table
- [ ] Each legacy transaction traceable to REST endpoint

---

## 5. Common Migration Patterns Reference

Quick reference for frequently used migration patterns.

### 5.1 COBOL to Java Type Mapping

| COBOL Type | Example | Java Type | JPA Type | Notes |
|------------|---------|-----------|----------|-------|
| PIC X(n) | PIC X(50) | String | VARCHAR(n) | Character string |
| PIC 9(n) | PIC 9(11) | Long | BIGINT | Integer number |
| PIC 9(n)V99 | PIC 9(13)V99 | BigDecimal | DECIMAL(n,2) | Decimal with 2 places |
| PIC S9(n) | PIC S9(9) | Integer | INTEGER | Signed integer |
| PIC S9(n)V99 | PIC S9(13)V99 | BigDecimal | DECIMAL(n,2) | Signed decimal |
| DATE (YYYYMMDD) | 20260220 | LocalDate | DATE | Date without time |
| TIME (HHMMSS) | 103045 | LocalTime | TIME | Time without date |
| TIMESTAMP | - | Instant | TIMESTAMP | Date and time with timezone |

### 5.2 CICS Command to Spring Pattern Mapping

| CICS Command | Purpose | Spring Pattern | Example |
|--------------|---------|----------------|---------|
| EXEC CICS READ | Read record | repository.findById() | accountRepository.findById(id) |
| EXEC CICS READ UPDATE | Lock and read | @Transactional + findById | @Transactional updateAccount() |
| EXEC CICS WRITE | Create record | repository.save() | accountRepository.save(account) |
| EXEC CICS REWRITE | Update record | repository.save() | accountRepository.save(account) |
| EXEC CICS DELETE | Delete record | repository.deleteById() | accountRepository.deleteById(id) |
| EXEC CICS SYNCPOINT | Commit transaction | @Transactional (auto) | Method completes successfully |
| EXEC CICS SYNCPOINT ROLLBACK | Rollback | throw Exception | throw new BusinessException() |
| EXEC CICS XCTL | Transfer control | service.method() | otherService.process() |
| EXEC CICS RETURN | Return to caller | return | return response |

### 5.3 VSAM to Database Pattern Mapping

| VSAM Type | Access Pattern | Database Pattern | Implementation |
|-----------|----------------|------------------|----------------|
| KSDS (Key Sequenced) | Direct by key | Primary key lookup | findById(key) |
| KSDS (Sequential) | Read all records | Full table scan | findAll() |
| AIX (Alternate Index) | Secondary key lookup | Secondary index | findBySecondaryKey() |
| ESDS (Entry Sequenced) | Sequential only | Append-only table | Insert with auto-increment |
| RRDS (Relative Record) | By record number | Indexed access | findById(recordNumber) |

### 5.4 Screen to API Pattern Mapping

| Screen Operation | User Action | API Pattern | HTTP Method | Endpoint |
|------------------|-------------|-------------|-------------|----------|
| Display record | View details | Read | GET | /api/v1/{resource}/{id} |
| Create new | Submit form | Create | POST | /api/v1/{resource} |
| Update existing | Submit changes | Update | PUT | /api/v1/{resource}/{id} |
| Delete record | Confirm deletion | Delete | DELETE | /api/v1/{resource}/{id} |
| Search records | Enter criteria | Search | GET | /api/v1/{resource}?filter=value |
| List records | View list | List | GET | /api/v1/{resource} |

---

## 6. Assumptions and Gaps

Document any assumptions made during mapping creation and gaps in information.

### 6.1 Assumptions

List assumptions made when creating this mapping:

1. **Authentication**: [e.g., Assumed OAuth2 with JWT tokens based on Common Spec 4.3]
2. **Database**: [e.g., Assumed PostgreSQL based on Backend Spec 2.4]
3. **API Design**: [e.g., Assumed RESTful APIs based on Backend Spec 4.1]
4. **[Other assumptions]**: [Description and rationale]

### 6.2 Information Gaps

List areas where information was not available in source specifications:

1. **[Gap description]**: [What information is missing]
   - **Impact**: [How this affects code generation]
   - **Recommendation**: [How to address this gap]
   - **Source to consult**: [Where to find this information]

2. **[Gap description]**: [What information is missing]
   - **Impact**: [How this affects code generation]
   - **Recommendation**: [How to address this gap]
   - **Source to consult**: [Where to find this information]

### 6.3 Verification Needed

List items that require verification with business stakeholders or technical experts:

1. **[Item to verify]**: [Description]
   - **Stakeholder**: [Who to consult]
   - **Question**: [Specific question to ask]
   - **Impact**: [Why this matters]

---

## 7. Document Control

### 7.1 Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | [Date] | tech_spec_extraction_specialist | Initial creation |
| 1.1 | [Date] | tech_spec_review_specialist | Review feedback incorporated |

### 7.2 Approval

| Role | Name | Status | Date |
|------|------|--------|------|
| Tech Spec Extraction Specialist | [Agent] | Created | [Date] |
| Tech Spec Review Specialist | [Agent] | Reviewed | [Date] |
| Tech Spec Team Supervisor | [Agent] | Approved | [Date] |

### 7.3 Related Documents

- **Target Specifications**: `{{TARGET_SPECIFICATION}}/`
  - 00-COMMON-SPECIFICATION.md
  - 01-FRONTEND-SPECIFICATION.md
  - 02-BACKEND-SPECIFICATION.md
  - 03-BATCH-SPECIFICATION.md

- **Business Specifications**: `{{BUSINESS_SPECIFICATION_BASE_PATH}}/`
  - WP-{ID}-specification.md (for each workpackage)

- **Other Technical Specifications**:
  - Backend Technical Specification
  - Frontend Technical Specification
  - Batch Technical Specification
  - Infrastructure Technical Specification

### 7.4 Usage Instructions

**For Code Generation Agents**:
1. Read this document FIRST before reading business specifications
2. Use Section 1 (Cross-Cutting Patterns) for all workpackages
3. Use Section 2.{WP-ID} for workpackage-specific guidance
4. Use Section 3 for step-by-step code generation approach
5. Use Section 4 for quality verification
6. Use Section 5 for quick pattern reference

**For Review Agents**:
1. Verify all mappings are traceable to source specifications
2. Verify all business logic preservation requirements are clear
3. Verify all technology choices match target specifications
4. Verify all assumptions are documented
5. Verify all gaps are identified

---

## End of Migration Mapping Specification Template
