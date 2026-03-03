# Phase: Code Generation - Java Spring Boot

## Context
- Project Structure: Standard migration project folder structure
- Input Location: 
  - {{BUSINESS_SPECIFICATION_BASE_PATH}} - Workpackage-based business specifications
  - {{TECH_SPEC_SPECS_PATH}} - Technical specifications and architecture
  - {{TEST_GENERATION_SERVICE_BASE_PATH}} - Test case definitions
  - {{SOURCE_CODE_ANALYSIS_OUTPUT}} - Legacy code analysis and dependencies
  - {{SOURCE_CODE}} - Original legacy source code
  - {{LEGACY_SPECIFICATION}} - Legacy documentation (Chapter 6)
  - {{TARGET_SPECIFICATION}} - Target framework specifications (Spring Boot, Spring Modulith)
  - {{TARGET_SAMPLE_CODE}} - Java example code for guidance
- Output Location: 
  - {{CODE_GENERATION_BACKEND_OUTPUT}} - Generated Java implementation code
  - {{CODE_GENERATION_BASE_PATH}}/progress - Phase completion tracking

## Objective
Implement modern Java Spring Boot code based on workpackage specifications while following Spring Modulith architecture. Create a complete, maintainable, production-ready Java application that preserves all business rules from the original legacy system. Process workpackages sequentially but organize code by domain modules. Ensure full traceability between generated code and business specifications, and adhere to Java best practices and modern development standards.

## Instructions

### 1. Workpackage Processing Strategy

**CRITICAL - Process by Migration Sequence, Not Workpackage ID**

1. **Process workpackages in migration sequence order** (Seq 1, Seq 2, Seq 3, etc.)
   - Read `migrationSequence` array from {{WORKPACKAGE_PLANNING}}
   - Process by `sequenceNumber`, NOT by `workpackageId`
   - Example: Seq 1 might be WP-001, Seq 19 might be WP-013 (different order)

2. **Check coordination dependencies before starting**:
   - Read `softPrerequisites` for the current sequence entry
   - Verify all prerequisite workpackages are completed
   - Check `sharedModuleContext` to identify modules that should already exist
   - If prerequisites not met, skip and process next in sequence

3. **Organize code by domain modules** (auth, user, transaction, common, etc.)
   - Each workpackage may contribute to multiple domain modules
   - Track progress by both workpackageId (traceability) and sequenceNumber (execution order)

4. **Add workpackage and sequence references** in file headers:
   - `@workpackage WP-001: User Authentication`
   - `@sequence Seq 1 (Wave 1, Phase 1)`

5. **Before generating code**:
   - Check which modules already exist from previous workpackages
   - Check `sharedModuleContext` for modules that should be reused vs. created
   - Verify soft prerequisites are complete

6. **Preserve existing code** - see Section 11 for critical preservation rules

**Migration Sequence Structure** (from {{WORKPACKAGE_PLANNING}}):
```json
{
  "sequenceNumber": 1,
  "workpackageId": 12,
  "flowId": "FLOW_CBACT02C",
  "phase": 1,
  "wave": 1,
  "prerequisites": [],
  "softPrerequisites": [],
  "sharedModuleContext": {
    "sharesModulesWith": ["FLOW_CBACT03C", "FLOW_CBCUS01C"],
    "sharedModules": {
      "FLOW_CBACT03C": ["CEE3ABD"],
      "FLOW_CBCUS01C": ["CEE3ABD"]
    },
    "coordinationReason": "Highest priority flow for shared modules"
  }
}
```

### 2. Architecture: Spring Modulith Package-Based Modules
1. Use Spring Modulith for modular monolith architecture
2. Each top-level package under base package is a module:
   - `com.carddemo.auth` - Authentication module
   - `com.carddemo.user` - User management module
   - `com.carddemo.transaction` - Transaction processing module
   - `com.carddemo.common` - Shared utilities and cross-cutting concerns
3. Add Spring Modulith dependency to pom.xml:
   ```xml
   <dependency>
       <groupId>org.springframework.modulith</groupId>
       <artifactId>spring-modulith-starter-core</artifactId>
   </dependency>
   ```
4. Module boundaries:
   - Each module has internal and API packages
   - Use `@ApplicationModuleListener` for cross-module events
   - Verify no circular dependencies between modules
5. Package structure within each module:
   ```
   com.carddemo.[module]/
   ├── api/          # Public API (controllers, DTOs)
   ├── domain/       # Domain entities
   ├── service/      # Service layer (business logic)
   ├── repository/   # Data access layer
   └── internal/     # Internal implementation (validators, mappers, adapters)
   ```

### 3. Project Structure Setup
1. Create standard Maven project structure with Spring Boot 3.x
2. Configure pom.xml with:
   - Spring Boot 3.x
   - Spring Modulith
   - Spring Data JPA
   - PostgreSQL driver
   - Spring Security
   - Validation API
   - Lombok
   - SLF4J logging
3. Set Java version to 21
4. Configure application.yml for database, security, logging
5. Create main application class with `@SpringBootApplication`

### 4. Domain Model Implementation (Production-Ready Entities)
1. For each business entity in specifications:
   - Create JPA entity classes in `[module]/domain/`
   - **Use surrogate keys** (`Long id` with `@GeneratedValue`) + business keys
   - **Add audit fields**: `createdAt`, `updatedAt`, `createdBy`, `updatedBy`
   - **Add optimistic locking**: `@Version` field
   - **Define database indexes** in `@Table` annotation
   - **Use enums** for type fields (not strings)
   - **Use Lombok** (`@Getter`, `@Setter`) for boilerplate reduction
   - **Add JPA Auditing**: `@EntityListeners(AuditingEntityListener.class)`
   - Implement validation annotations matching business rules
   - Create appropriate relationships between entities
   - Ensure proper encapsulation
   - Add comprehensive Javadoc with traceability (see section 9)

### 5. Data Access Layer Implementation
1. For each domain module:
   - Create Spring Data JPA repository interfaces in `[module]/repository/`
   - Use standard repository methods where possible
   - Implement custom queries using @Query for complex operations
   - Configure transaction management with @Transactional
   - Implement data validation at repository level
   - Document repository classes with traceability to business rules

### 6. Business Logic Implementation (Service Layer with Separation of Concerns)
1. For each business rule in specifications:
   - Create service classes in `[module]/service/`
   - **Create dedicated validator classes** in `[module]/internal/` for validation logic
   - **Create dedicated mapper classes** in `[module]/internal/` for DTO/Entity mapping
   - Implement all business rules correctly
   - Use `@Transactional(readOnly = true)` at class level for read operations
   - Use `@Transactional` on individual write methods
   - Create appropriate exception handling with custom exceptions
   - **Add comprehensive logging** with SLF4J (`@Slf4j`)
   - Ensure separation of concerns (service, validator, mapper)
   - Document service methods with traceability (see section 9)
   - Implement complex business workflows as separate components
   - **Use constructor injection** for dependencies (immutable)

### 7. API Layer Implementation
1. For each domain module:
   - Create REST controllers in `[module]/api/`
   - Implement request/response DTOs in `[module]/api/dto/`
   - Create input validation using @Valid
   - Implement proper error handling and HTTP status codes
   - Document API endpoints with OpenAPI/Swagger annotations
   - Implement security controls (authentication, authorization)
   - Follow RESTful conventions
   - Add comprehensive logging for API calls

### 8. Cross-Cutting Concerns (common module)
1. Implement in `com.carddemo.common`:
   - **Configuration** (`config/`): Application configuration, beans, JPA auditing config
   - **Security** (`security/`): Spring Security configuration, JWT handling
   - **Exception Handling** (`exception/`): Global exception handler, custom exceptions
   - **Utilities** (`util/`): Helper classes, converters, validators
   - **Logging**: Use SLF4J throughout the application
   - **Audit**: Implement audit logging with JPA auditing
   - **Monitoring**: Configure actuator endpoints

### 9. Documentation and Traceability (Comprehensive Javadoc Style)

**CRITICAL: Follow gen_src copy documentation style - comprehensive, detailed, production-ready**

1. **Class-Level Javadoc Structure**:
   ```java
   /**
    * [One-line description]
    * 
    * <p><b>Business Context:</b> [Detailed explanation of business purpose]</p>
    * 
    * <p><b>Business Functions:</b></p>
    * <ul>
    *   <li>F-XXX-YYY: [Function description]</li>
    *   <li>F-XXX-ZZZ: [Function description]</li>
    * </ul>
    * 
    * <p><b>Business Rules Applied:</b></p>
    * <ul>
    *   <li>BR-XXX-YYY: [Rule description]</li>
    *   <li>BR-XXX-ZZZ: [Rule description]</li>
    * </ul>
    * 
    * <p><b>Legacy Mapping:</b></p>
    * <ul>
    *   <li>Legacy Program: [PROGRAM.cbl] lines [X-Y]</li>
    *   <li>Legacy Function: [Description]</li>
    * </ul>
    * 
    * <p><b>Migration Notes:</b></p>
    * <ul>
    *   <li>[Important migration considerations]</li>
    *   <li>[External dependencies]</li>
    * </ul>
    * 
    * @see [Related classes]
    * @since [Version]
    * @version [Version]
    * @author CardDemo Migration Team
    * 
    * @workpackage WP-XXX: [Workpackage name]
    * @specref [Spec file]#[Section]
    * @legacyref [PROGRAM.cbl]:[lines]
    * @docref Chapter6-[Module].md#[section]
    */
   ```

2. **Method-Level Javadoc Structure**:
   ```java
   /**
    * [Method description]
    * 
    * <p><b>Business Function:</b> F-XXX-YYY - [Function name]</p>
    * 
    * <p><b>Business Rules Applied:</b></p>
    * <ul>
    *   <li>BR-XXX-YYY: [Rule description]</li>
    * </ul>
    * 
    * <p><b>Process Flow:</b></p>
    * <ol>
    *   <li>[Step 1]</li>
    *   <li>[Step 2]</li>
    *   <li>[Step 3]</li>
    * </ol>
    * 
    * <p><b>Legacy Equivalent:</b> [PROGRAM.cbl] lines [X-Y] ([paragraph name])</p>
    * 
    * @param [parameter] [description]
    * @return [description]
    * @throws [exception] [condition]
    * 
    * @specref WP-XXX#F-XXX-YYY
    * @specref WP-XXX#BR-XXX-YYY
    */
   ```

3. **Entity Field Documentation**:
   ```java
   /**
    * [Field description]
    * 
    * <p><b>Business Rule:</b> BR-XXX-YYY ([Rule description])</p>
    * <p><b>Validation:</b> [Validation rules]</p>
    * <p><b>Legacy Field:</b> [FIELD-NAME] (PIC [format])</p>
    */
   ```

4. **Inline Code Comments**:
   - Add inline comments referencing business rules: `// BR-XXX-YYY: [Rule description]`
   - Explain complex logic with business context
   - Reference legacy code for equivalent operations

5. **Traceability Matrix**:
   - Create markdown file per workpackage: `TRACEABILITY-WP-[NUM].md`
   - Map each generated class/method to:
     - Business specification reference
     - Legacy code reference
     - Test case reference

### 10. Strict No-Hallucination Policy

**CRITICAL: Do not invent anything not in specifications**

1. **NEVER invent business rules** not in specifications
2. **NEVER create entities** not defined in domain model
3. **NEVER add functionality** beyond specifications
4. **NEVER create hard-coded mock data** in production code
5. **NEVER invent external system integrations** not specified
6. **NEVER add fields to entities** not in specifications
7. **NEVER create methods** not required by business specifications
8. If uncertain about implementation, mark with TODO (see section 12)

9. **Verification checklist** for each component:
   - [ ] All functionality comes from specifications
   - [ ] No invented business rules
   - [ ] No hard-coded test data
   - [ ] All entities match domain model exactly
   - [ ] All integrations are specified
   - [ ] All fields are from specifications
   - [ ] All methods serve specified business functions

### 11. Code Preservation Rules - Do Not Delete Existing Code

**CRITICAL: When implementing a workpackage, preserve all existing code from previous workpackages.**

1. **NEVER delete existing code** from other workpackages
2. **NEVER delete existing files** created by previous workpackages
3. **NEVER modify code in other domain modules** unless the current workpackage explicitly requires changes to that domain
4. **Exception - Common module**: The `common` module may be modified by any workpackage as it contains shared utilities

**Modification Rules by Domain:**
- **Same domain as current workpackage**: ✅ Can modify/extend existing code
- **Different domain**: ❌ Do not modify (unless explicitly required by business spec)
- **Common module**: ✅ Can modify/extend (shared across all workpackages)

**Examples:**
- ✅ WP-002 working on `user` module → Can modify existing `user` module code
- ✅ WP-002 working on `user` module → Can add utilities to `common` module
- ❌ WP-002 working on `user` module → Cannot modify `auth` module (created by WP-001)
- ❌ WP-003 → Cannot delete classes created by WP-001 or WP-002

**Implementation Strategy:**
1. Before generating code, check which modules already exist
2. Only add new files or extend existing files in the current workpackage's domain
3. If cross-module integration is needed, use module APIs (public interfaces)
4. Document any necessary cross-module changes with clear justification

**Verification Checklist:**
- [ ] No files deleted from previous workpackages
- [ ] No code removed from other domain modules
- [ ] Modifications to other domains are justified in business spec
- [ ] Common module changes are additive (not destructive)
- [ ] Cross-module integration uses public APIs

### 12. TODO Comments for Incomplete Implementations

**Use TODO when implementation details are missing or uncertain**

1. **Use TODO when**:
   - External system integration details are missing
   - Business rule details are unclear or ambiguous
   - Validation rules are not fully specified
   - Database schema details are uncertain
   - Security implementation details are missing
   - Configuration requirements are not specified
   - Legacy logic cannot be mapped to modern patterns
   - Business rules require clarification

2. **TODO Format**:
   ```java
   // TODO: [CATEGORY] - [Description] - Refer to: [Source]
   ```

3. **TODO Categories**:
   - `EXTERNAL_INTEGRATION` - Missing external system details
   - `BUSINESS_RULE` - Unclear or missing business rule
   - `VALIDATION` - Unspecified validation logic
   - `DATABASE` - Database schema uncertainties
   - `SECURITY` - Security implementation details
   - `CONFIG` - Configuration requirements
   - `UNMAPPABLE` - Legacy logic requiring manual review
   - `CLARIFICATION` - Business rules requiring clarification

4. **TODO Examples**:
   ```java
   // TODO: EXTERNAL_INTEGRATION - OAuth2 provider configuration not specified - Refer to: Business Spec WP-001 Section 3.2
   
   // TODO: BUSINESS_RULE - Interest calculation formula unclear for edge case - Refer to: COBOL CALCINT.cbl:234-267
   
   // TODO: UNMAPPABLE - Complex COBOL PERFORM logic with multiple exits - Refer to: LEGACY.cbl:456-523 - Requires manual review
   
   // TODO: CLARIFICATION - Validation rule for account status transition needs business confirmation - Refer to: Business Spec WP-002-BR-015
   ```

### 13. Integration Points
1. For each external system integration:
   - Create client interfaces in `[module]/api/client/`
   - Implement integration adapters in `[module]/internal/adapter/`
   - Configure connection parameters in application.yml
   - Implement error handling and retry logic
   - Create mock implementations for testing
   - **Mark with TODO if details are missing**
   - Add comprehensive logging for integration calls

### 14. Configuration Management
1. Use Spring Boot configuration:
   - `application.yml` - Common configuration
   - `application-dev.yml` - Development environment
   - `application-prod.yml` - Production environment
2. Externalize all environment-specific values
3. Use `@ConfigurationProperties` for type-safe configuration
4. Document all configuration options
5. **Mark with TODO if configuration details are missing**
6. Never hard-code values in production code

### 15. Quality Assurance Verification

**Verify each generated component meets production standards**

For each generated component, verify:
- [ ] Package structure follows Spring Modulith conventions
- [ ] No circular dependencies between modules
- [ ] All business rules from specifications are implemented
- [ ] No invented functionality beyond specifications
- [ ] TODOs mark all incomplete/uncertain implementations
- [ ] Javadoc includes comprehensive documentation (business context, process flow, legacy mapping)
- [ ] Javadoc includes @workpackage, @specref, @legacyref, @docref tags
- [ ] Code compiles without errors
- [ ] Integration points are clearly marked
- [ ] No hard-coded values (use configuration)
- [ ] Proper exception handling with custom exceptions
- [ ] Input validation on all API endpoints
- [ ] Transaction boundaries are correct (@Transactional annotations)
- [ ] Security controls are implemented
- [ ] Logging is comprehensive (SLF4J)
- [ ] Entities have audit fields (createdAt, updatedAt, createdBy, updatedBy)
- [ ] Entities have optimistic locking (@Version)
- [ ] Entities use surrogate keys + business keys
- [ ] Entities use enums for type fields
- [ ] Entities use Lombok for boilerplate
- [ ] Services use validator and mapper classes
- [ ] No code deleted from previous workpackages

### 16. Testing Strategy
1. **Unit Tests**:
   - Test business logic in service layer
   - Mock dependencies
   - Cover edge cases and error conditions
   - Test validation logic
2. **Integration Tests**:
   - Test API endpoints
   - Test database interactions
   - Use test containers for database
   - Test cross-module integration
3. **Test Coverage**:
   - Aim for 80%+ coverage of business logic
   - Focus on critical business rules
4. **Test Documentation**:
   - Link tests to business specifications
   - Reference test case definitions from Phase 4

### 17. Progress Tracking
1. Update progress file after each workpackage: {{CODE_GENERATION_STATUS}}
2. Track by both workpackageId (traceability) and sequenceNumber (execution order)
3. Format:
   ```json
   {
     "phaseId": "05-code-generation",
     "status": "in_progress|completed",
     "targetLanguage": "Java",
     "targetFramework": "Spring Boot + Spring Modulith",
     "currentSequence": 5,
     "workpackages": [
       {
         "sequenceNumber": 1,
         "workpackageId": "WP-001",
         "workpackageName": "User Authentication",
         "flowId": "FLOW_COSGN00C",
         "phase": 1,
         "wave": 1,
         "status": "completed",
         "softPrerequisites": [],
         "sharedModules": [],
         "modulesAffected": ["auth", "common"],
         "components": {
           "entities": 3,
           "repositories": 2,
           "services": 2,
           "validators": 1,
           "mappers": 1,
           "controllers": 1,
           "utilities": 1
         },
         "businessRulesImplemented": 15,
         "todosCreated": 3,
         "completedDate": "2026-02-21"
       }
     ],
     "completedCount": 1,
     "totalCount": 26,
     "lastUpdated": "2026-02-21"
   }
   ```

## Output Format and Code Examples

### Entity Class Example (Production-Ready Style)
```java
package com.carddemo.user.domain;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import org.springframework.data.annotation.CreatedBy;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedBy;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.Instant;

/**
 * User entity representing system users in the credit card management system.
 * 
 * <p><b>Business Entity:</b> BE-002-001 (User)</p>
 * <p><b>Business Description:</b> Represents a system user who can access the credit card 
 * management system. Each user has a unique identifier, personal information, and a role 
 * classification that determines their access level.</p>
 * 
 * <p><b>Business Rules Applied:</b></p>
 * <ul>
 *   <li>BR-002-001: Required Field Validation - All fields are mandatory</li>
 *   <li>BR-002-002: Unique User ID Constraint - userId must be unique</li>
 *   <li>BR-002-003: Admin-Only Access Control - userType determines access level</li>
 * </ul>
 * 
 * <p><b>Legacy Mapping:</b></p>
 * <ul>
 *   <li>Legacy File: USRSEC (VSAM KSDS)</li>
 *   <li>Legacy Copybook: CSUSR01Y.cpy (SEC-USER-DATA)</li>
 *   <li>Migration: Fixed-length COBOL records to relational table</li>
 * </ul>
 * 
 * @see com.carddemo.user.repository.UserRepository
 * @see com.carddemo.user.service.UserService
 * @workpackage WP-002: User Management
 * @since WP-002 (User Addition Functionality)
 */
@Entity
@Table(name = "users", indexes = {
    @Index(name = "idx_user_id", columnList = "user_id", unique = true),
    @Index(name = "idx_user_type", columnList = "user_type")
})
@EntityListeners(AuditingEntityListener.class)
@Getter
@Setter
public class User {

    /**
     * Surrogate primary key for internal database use.
     * Auto-generated sequence value.
     */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * Business key: Unique user identifier (8 characters).
     * 
     * <p><b>Business Rule:</b> BR-002-002 (Unique User ID Constraint)</p>
     * <p><b>Validation:</b> Required, unique, max 8 characters, alphanumeric</p>
     * <p><b>Legacy Field:</b> SEC-USR-ID (PIC X(8))</p>
     */
    @Column(name = "user_id", nullable = false, unique = true, length = 8)
    private String userId;

    /**
     * User's first name (20 characters).
     * 
     * <p><b>Business Rule:</b> BR-002-001 (Required Field Validation)</p>
     * <p><b>Legacy Field:</b> SEC-USR-FNAME (PIC X(20))</p>
     */
    @Column(name = "first_name", nullable = false, length = 20)
    private String firstName;

    /**
     * User type classification: ADMIN or REGULAR.
     * 
     * <p><b>Business Rule:</b> BR-002-003 (Admin-Only Access Control)</p>
     * <p><b>Legacy Field:</b> SEC-USR-TYPE (PIC X(1))</p>
     */
    @Column(name = "user_type", nullable = false, length = 1)
    @Enumerated(EnumType.STRING)
    private UserType userType;

    @Version
    private Long version;

    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt;

    @LastModifiedDate
    @Column(name = "updated_at", nullable = false)
    private Instant updatedAt;

    @CreatedBy
    @Column(name = "created_by", nullable = false, updatable = false, length = 8)
    private String createdBy;

    @LastModifiedBy
    @Column(name = "updated_by", nullable = false, length = 8)
    private String updatedBy;
}
```

### Service Class Example (With Validator and Mapper)
```java
package com.carddemo.user.service;

import com.carddemo.user.api.dto.UserCreateRequest;
import com.carddemo.user.api.dto.UserResponse;
import com.carddemo.user.domain.User;
import com.carddemo.user.repository.UserRepository;
import com.carddemo.user.internal.UserValidator;
import com.carddemo.user.internal.UserMapper;
import com.carddemo.common.exception.ResourceNotFoundException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * Service layer for user management operations.
 * 
 * <p><b>Business Functions Implemented:</b></p>
 * <ul>
 *   <li>F-002-004: Create User Account</li>
 *   <li>User retrieval and listing</li>
 * </ul>
 * 
 * <p><b>Business Process:</b> User Account Creation (Chapter 5)</p>
 * 
 * <p><b>Transaction Management:</b></p>
 * <ul>
 *   <li>Read operations: @Transactional(readOnly = true)</li>
 *   <li>Write operations: @Transactional</li>
 *   <li>Isolation: READ_COMMITTED (default)</li>
 *   <li>Propagation: REQUIRED (default)</li>
 * </ul>
 * 
 * <p><b>Legacy Mapping:</b></p>
 * <ul>
 *   <li>Legacy Program: COUSR01C.cbl</li>
 *   <li>EXEC CICS WRITE → save()</li>
 *   <li>EXEC CICS READ → findById()</li>
 *   <li>EXEC CICS SYNCPOINT → Transaction commit</li>
 * </ul>
 * 
 * @see com.carddemo.user.api.UserController
 * @see com.carddemo.user.repository.UserRepository
 * @workpackage WP-002: User Management
 * @since WP-002 (User Addition Functionality)
 */
@Slf4j
@Service
@Transactional(readOnly = true)
public class UserService {

    private final UserRepository userRepository;
    private final UserValidator userValidator;
    private final UserMapper userMapper;

    public UserService(UserRepository userRepository,
                      UserValidator userValidator,
                      UserMapper userMapper) {
        this.userRepository = userRepository;
        this.userValidator = userValidator;
        this.userMapper = userMapper;
    }

    /**
     * Creates a new user account.
     * 
     * <p><b>Business Function:</b> F-002-004 (Create User Account)</p>
     * <p><b>Business Process:</b> User Account Creation - Activity 4</p>
     * 
     * <p><b>Business Rules Applied:</b></p>
     * <ul>
     *   <li>BR-002-001: Required Field Validation (DTO validation)</li>
     *   <li>BR-002-002: Unique User ID Constraint (validator)</li>
     *   <li>BR-002-003: Admin-Only Access Control (controller security)</li>
     * </ul>
     * 
     * <p><b>Process Flow:</b></p>
     * <ol>
     *   <li>Validate user input (BR-002-001, BR-002-002)</li>
     *   <li>Map DTO to entity</li>
     *   <li>Save entity to database</li>
     *   <li>Map entity to response DTO</li>
     *   <li>Return success response</li>
     * </ol>
     * 
     * <p><b>Success Message:</b> "User [USER-ID] has been added ..."</p>
     * <p><b>Error Messages:</b></p>
     * <ul>
     *   <li>"User ID already exist..." - Duplicate user ID</li>
     *   <li>"Unable to Add User..." - System error</li>
     * </ul>
     * 
     * <p><b>Legacy Implementation:</b></p>
     * <ul>
     *   <li>Program: COUSR01C.cbl</li>
     *   <li>Operation: EXEC CICS WRITE USRSEC</li>
     * </ul>
     * 
     * @param request User creation request with validated data
     * @return UserResponse with created user data
     * @throws BusinessException if user ID already exists
     * 
     * @specref WP-002#F-002-004
     * @specref WP-002#BR-002-001
     * @specref WP-002#BR-002-002
     * @legacyref COUSR01C.cbl:WRITE-USER-SEC-RECORD
     */
    @Transactional
    public UserResponse createUser(UserCreateRequest request) {
        log.info("Creating user: userId={}", request.getUserId());

        // F-002-003: Validate User Input (BR-002-002)
        userValidator.validateUserCreate(request);

        // F-002-004: Create User Account
        User user = userMapper.toEntity(request);
        User savedUser = userRepository.save(user);

        log.info("User created successfully: userId={}, id={}", 
                savedUser.getUserId(), savedUser.getId());

        return userMapper.toResponse(savedUser);
    }

    /**
     * Retrieves user by user ID (business key).
     * 
     * <p><b>Business Rule:</b> BR-001-003 (Case-Insensitive User ID)</p>
     * 
     * @param userId User ID (case-insensitive)
     * @return UserResponse with user data
     * @throws ResourceNotFoundException if user not found
     */
    public UserResponse getUserByUserId(String userId) {
        log.debug("Retrieving user by userId: userId={}", userId);

        User user = userRepository.findByUserIdIgnoreCase(userId)
            .orElseThrow(() -> new ResourceNotFoundException("User with userId: " + userId));

        return userMapper.toResponse(user);
    }
}
```

### Controller Class Example
```java
package com.carddemo.user.api;

import com.carddemo.user.api.dto.UserCreateRequest;
import com.carddemo.user.api.dto.UserResponse;
import com.carddemo.user.service.UserService;
import jakarta.validation.Valid;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

/**
 * REST API controller for user management operations.
 * 
 * <p><b>Business Functions:</b></p>
 * <ul>
 *   <li>F-002-004: Create User Account</li>
 * </ul>
 * 
 * <p><b>Security:</b> Admin-only access (BR-002-003)</p>
 * 
 * @workpackage WP-002: User Management
 */
@Slf4j
@RestController
@RequestMapping("/api/v1/users")
public class UserController {
    
    private final UserService userService;
    
    public UserController(UserService userService) {
        this.userService = userService;
    }
    
    /**
     * Creates a new user account.
     * 
     * <p><b>Business Function:</b> F-002-004 (Create User Account)</p>
     * <p><b>Business Rule:</b> BR-002-003 (Admin-Only Access Control)</p>
     * 
     * @param request User creation request
     * @return UserResponse with created user data
     * 
     * @specref WP-002#F-002-004
     */
    @PostMapping
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<UserResponse> createUser(@Valid @RequestBody UserCreateRequest request) {
        log.info("POST /api/v1/users - Creating user: userId={}", request.getUserId());
        
        UserResponse response = userService.createUser(request);
        
        log.info("User created successfully: userId={}", response.getUserId());
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }
    
    /**
     * Retrieves user by user ID.
     * 
     * @param userId User ID
     * @return UserResponse with user data
     */
    @GetMapping("/{userId}")
    public ResponseEntity<UserResponse> getUserByUserId(@PathVariable String userId) {
        log.info("GET /api/v1/users/{} - Retrieving user", userId);
        
        UserResponse response = userService.getUserByUserId(userId);
        
        return ResponseEntity.ok(response);
    }
}
```

### Validator Class Example
```java
package com.carddemo.user.internal;

import com.carddemo.user.api.dto.UserCreateRequest;
import com.carddemo.user.repository.UserRepository;
import com.carddemo.common.exception.BusinessException;
import org.springframework.stereotype.Component;

/**
 * Validator for user-related business rules.
 * 
 * @workpackage WP-002: User Management
 */
@Component
public class UserValidator {
    
    private final UserRepository userRepository;
    
    public UserValidator(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
    
    /**
     * Validates user creation request.
     * 
     * <p><b>Business Rule:</b> BR-002-002 (Unique User ID Constraint)</p>
     * 
     * @param request User creation request
     * @throws BusinessException if user ID already exists
     * 
     * @specref WP-002#BR-002-002
     */
    public void validateUserCreate(UserCreateRequest request) {
        // BR-002-002: Unique User ID Constraint
        if (userRepository.existsByUserIdIgnoreCase(request.getUserId())) {
            throw new BusinessException("User ID already exist");
        }
    }
}
```

### Mapper Class Example
```java
package com.carddemo.user.internal;

import com.carddemo.user.api.dto.UserCreateRequest;
import com.carddemo.user.api.dto.UserResponse;
import com.carddemo.user.domain.User;
import org.springframework.stereotype.Component;

/**
 * Mapper for converting between User entities and DTOs.
 * 
 * @workpackage WP-002: User Management
 */
@Component
public class UserMapper {
    
    /**
     * Converts UserCreateRequest to User entity.
     * 
     * @param request User creation request
     * @return User entity
     */
    public User toEntity(UserCreateRequest request) {
        User user = new User();
        user.setUserId(request.getUserId().toUpperCase()); // BR-001-003: Case-insensitive
        user.setFirstName(request.getFirstName());
        user.setLastName(request.getLastName());
        user.setUserType(request.getUserType());
        return user;
    }
    
    /**
     * Converts User entity to UserResponse DTO.
     * 
     * @param user User entity
     * @return UserResponse DTO
     */
    public UserResponse toResponse(User user) {
        return UserResponse.builder()
            .id(user.getId())
            .userId(user.getUserId())
            .firstName(user.getFirstName())
            .lastName(user.getLastName())
            .userType(user.getUserType())
            .createdAt(user.getCreatedAt())
            .updatedAt(user.getUpdatedAt())
            .build();
    }
}
```

## Quality Criteria

### Code Quality
- Code follows Java best practices and Spring conventions
- Classes have single responsibility
- Methods are small and focused (< 30 lines preferred)
- Proper exception handling is implemented
- Code is well-documented with comprehensive Javadoc
- No code smells or anti-patterns
- Consistent naming conventions
- Proper encapsulation and access modifiers
- Use of dependency injection (constructor injection)
- Lombok used for boilerplate reduction
- SLF4J logging throughout

### Business Rule Implementation
- All business rules from specifications are implemented
- Validation logic matches business requirements exactly
- Business workflows are correctly implemented
- Edge cases are handled appropriately
- Error conditions trigger appropriate responses
- Business constraints are enforced
- No invented business rules

### Architecture Compliance
- Code follows Spring Modulith patterns
- Proper module boundaries are maintained
- No circular dependencies between modules
- Layered architecture within modules (api/domain/service/repository/internal)
- Dependencies flow in correct direction
- Framework features are used appropriately
- Configuration follows Spring Boot best practices
- Security controls are properly implemented
- Separation of concerns (service, validator, mapper)

### Traceability
- All code components link to business specifications
- Javadoc comments include comprehensive documentation
- Javadoc includes @workpackage, @specref, @legacyref, @docref tags
- Business context explained in class-level Javadoc
- Process flows documented in method-level Javadoc
- Inline comments reference business rules
- Traceability matrix is complete and accurate
- Test coverage maps to business requirements
- Any deviations are documented with rationale

### Technical Requirements
- Code compiles without errors
- Maven build configuration is correct
- Required dependencies are properly configured
- Application can be started and initialized
- Database schema matches entity definitions
- Configuration is environment-aware
- Logging is properly implemented
- No hard-coded values in production code
- Entities have audit fields
- Entities have optimistic locking
- Entities use surrogate keys + business keys
- Entities use enums for type fields

### Production Readiness
- Comprehensive logging for debugging
- Audit trail in entities (createdAt, updatedAt, createdBy, updatedBy)
- Optimistic locking for concurrent updates
- Proper transaction management
- Custom exceptions with meaningful messages
- Input validation on all API endpoints
- Security controls implemented
- Configuration externalized
- No code deleted from previous workpackages

## Error Handling

### Common Error Scenarios

1. **Ambiguous Business Rule Implementation**
   - Detection: Business rule with unclear implementation approach
   - Recovery: Add TODO with CLARIFICATION category
   - Document multiple implementation options if possible
   - Reference specific business specification section

2. **Missing External System Details**
   - Detection: Integration point without configuration details
   - Recovery: Add TODO with EXTERNAL_INTEGRATION category
   - Create interface but leave implementation incomplete
   - Document expected integration contract

3. **Unmappable Legacy Logic**
   - Detection: Complex legacy code that doesn't map to modern patterns
   - Recovery: Add TODO with UNMAPPABLE category
   - Reference specific legacy code lines
   - Flag for manual review
   - Document the complexity and why it's unmappable

4. **Framework Limitation**
   - Detection: Business requirement conflicts with framework capabilities
   - Recovery: Document limitation and propose workaround
   - Add TODO if workaround is uncertain
   - Escalate for architecture decision if significant

5. **Missing Business Specification Details**
   - Detection: Required information not in specifications
   - Recovery: Add TODO with BUSINESS_RULE category
   - Reference specification section that should contain the information
   - Continue with reasonable default if safe

### Error Reporting
- Log all issues to progress tracking file
- Include: timestamp, workpackage, error type, context, resolution
- Update workpackage status to indicate issues
- Create separate issue log if multiple issues found

## Execution Strategy

1. **Read Migration Sequence** from {{WORKPACKAGE_PLANNING}}
   - Load `migrationSequence` array
   - Sort by `sequenceNumber` (ascending)
   - Note: sequenceNumber ≠ workpackageId (different ordering)

2. **For each sequence entry** (Seq 1, Seq 2, Seq 3, ...):
   - Extract `workpackageId`, `flowId`, `phase`, `wave`
   - Check `softPrerequisites` - verify all are completed
   - Check `sharedModuleContext` - identify modules to reuse
   - If prerequisites not met, skip to next sequence

3. **Before starting each workpackage**:
   - Check which modules already exist from previous workpackages
   - Identify which modules this workpackage will affect
   - Review `sharedModuleContext` for coordination requirements
   - Plan code preservation strategy

4. **For each workpackage**:
   - Read business specification thoroughly
   - Identify affected domain modules
   - Check for shared modules that should be reused (from `sharedModuleContext`)
   - Generate/update entities in domain modules (with audit fields, versioning, indexes)
   - Generate/update repositories
   - Generate/update validators (in internal package)
   - Generate/update mappers (in internal package)
   - Generate/update services (with logging, transaction management)
   - Generate/update controllers (with security, validation)
   - Create traceability documentation
   - Update progress tracking (both sequenceNumber and workpackageId)
   - Verify quality criteria
   - Verify no code deleted from other workpackages

5. **Stop after each workpackage** for review

6. **Continue with next sequence** after approval

**Wave-Based Parallelization** (Optional):
- Workpackages in the same wave can be generated in parallel
- Wave 1 workpackages have no soft dependencies
- Later waves depend on earlier waves completing first

## Success Criteria

- [ ] Application compiles successfully with Maven
- [ ] All business rules from specifications are preserved
- [ ] Spring Modulith structure is correct (no circular dependencies)
- [ ] All TODOs are properly documented with categories and references
- [ ] Full traceability (workpackage + business spec + legacy + Chapter 6)
- [ ] No invented functionality beyond specifications
- [ ] Code follows Spring Boot and Java best practices
- [ ] Configuration is externalized
- [ ] Security is implemented
- [ ] Tests are created for business logic
- [ ] Documentation is comprehensive (business context, process flows, legacy mapping)
- [ ] Entities have audit fields and optimistic locking
- [ ] Services use validator and mapper classes
- [ ] Comprehensive logging throughout
- [ ] No code deleted from previous workpackages
- [ ] Code style matches gen_src copy (production-ready)

---

**Execute this implementation systematically, processing one workpackage at a time, ensuring all original business functionality is preserved in the modernized Spring Boot application with production-ready code quality.**
