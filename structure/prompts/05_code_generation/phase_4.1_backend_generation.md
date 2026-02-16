# Phase 4.1: Backend Code Generation

---

## Orchestration Information

**Phase**: Phase 4 - Code Generation
**Step**: Step 4.1 - Backend Code Generation
**Team Supervisor**: code_generation_team_supervisor
**Assigned Agent**: code_generation_specialist_backend
**Task File Name**: {{TASKS_BASE_PATH}}/phase_4.1_backend_generation.md

### Expected Deliverables

1. **Domain Model Implementation**
   - Location: {{CODE_GENERATION_BACKEND_OUTPUT}}/wp-{ID}/domain/
   - Description: Entities, value objects, domain events for the workpackage
   - Includes: JPA entities, domain logic, validation rules

2. **Repository Layer Implementation**
   - Location: {{CODE_GENERATION_BACKEND_OUTPUT}}/wp-{ID}/repository/
   - Description: Data access layer with repository interfaces and implementations
   - Includes: JPA repositories, custom queries, specifications

3. **Service Layer Implementation**
   - Location: {{CODE_GENERATION_BACKEND_OUTPUT}}/wp-{ID}/service/
   - Description: Business logic layer implementing all business rules
   - Includes: Service interfaces, implementations, transaction management

4. **API Layer Implementation**
   - Location: {{CODE_GENERATION_BACKEND_OUTPUT}}/wp-{ID}/api/
   - Description: REST API controllers and DTOs
   - Includes: Controllers, request/response DTOs, API documentation

5. **Progress Tracking Update**
   - File: {{CODE_GENERATION_STATUS}}
   - Description: Updated progress with backend completion for this workpackage

6. **Error Reports** (if applicable)
   - File: {{CODE_GENERATION_ERRORS}}
   - Description: Documentation of issues encountered during generation

### Success Criteria
- [ ] All domain entities implemented with proper JPA annotations
- [ ] All repository interfaces created with required queries
- [ ] All business rules from specification implemented in service layer
- [ ] All API endpoints implemented with proper DTOs
- [ ] Code compiles without errors
- [ ] All business rules traceable to business specification
- [ ] Proper layering maintained (no layer violations)
- [ ] Exception handling implemented
- [ ] Validation implemented at appropriate layers
- [ ] Progress tracking updated with backend completion
- [ ] All deliverables produced at specified paths
- [ ] Ready for Phase 4.2 (Frontend) or next workpackage

---

## Context

### Workpackage Context (Provided at Runtime)
- **Workpackage ID**: WP-{ID} (e.g., WP-001)
- **Workpackage Name**: [Name from workpackage planning]
- **Workpackage Description**: [Description from business specification]

### Input Locations
- **Business specification**: `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-{ID}-specification.md`
- **Test case specification**: `{{TEST_GENERATION_DOMAIN_BASE_PATH}}/WP-{ID}-tests.md`
- **Target backend specification**: `{{TARGET_SPECIFICATION}}/02-BACKEND-SPECIFICATION.md`
- **Backend sample code**: `{{TARGET_SAMPLE_CODE}}/backend/`
- **Project structure**: `{{CODE_GENERATION_BACKEND_OUTPUT}}/` (from Phase 4.0)

### Output Locations
- **Backend code**: `{{CODE_GENERATION_BACKEND_OUTPUT}}/wp-{ID}/`
- **Progress tracking**: `{{CODE_GENERATION_STATUS}}`
- **Error reports**: `{{CODE_GENERATION_ERRORS}}`

### Previous Phase Artifacts
- **From Phase 4.0**: Project structure, build configuration, configuration templates
- **From Phase 3**: Business specification with detailed requirements
- **From Phase 3**: Test case definitions

---

## Objective

Implement the backend tier for the specified workpackage, translating business requirements from the business specification into working backend code that follows the target backend specification's architecture, patterns, and conventions.

**CRITICAL**: This phase implements ONE workpackage only. Focus exclusively on the business rules, entities, and API endpoints defined in the workpackage's business specification. Do not implement functionality from other workpackages.

---

## Instructions

### 1. Preparation

#### 1.1 Read Business Specification
1. Open and read `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-{ID}-specification.md`
2. Extract key information:
   - **Business Rules**: All business logic that must be implemented
   - **Domain Entities**: Entities and their attributes
   - **Relationships**: Entity relationships and cardinality
   - **Validation Rules**: Data validation requirements
   - **Business Processes**: Workflows and process flows
   - **API Requirements**: Required endpoints and operations

3. Identify implementation scope:
   - Which entities need to be created
   - Which business rules need to be implemented
   - Which API endpoints need to be exposed
   - Which validations need to be enforced

#### 1.2 Read Target Backend Specification
1. Open and read `{{TARGET_SPECIFICATION}}/02-BACKEND-SPECIFICATION.md`
2. Extract implementation guidance:
   - **Framework**: Spring Boot, Jakarta EE, etc.
   - **Architecture Pattern**: Layered architecture details
   - **Naming Conventions**: Class, method, package naming rules
   - **Annotation Usage**: JPA, validation, transaction annotations
   - **Error Handling**: Exception handling patterns
   - **API Design**: REST API conventions (URL patterns, HTTP methods, status codes)
   - **DTO Patterns**: Request/response DTO conventions
   - **Repository Patterns**: JPA repository patterns
   - **Service Patterns**: Service layer patterns
   - **Transaction Management**: Transaction boundaries and propagation

3. Review sample code at `{{TARGET_SAMPLE_CODE}}/backend/` for:
   - Entity implementation examples
   - Repository implementation examples
   - Service implementation examples
   - Controller implementation examples
   - DTO mapping patterns
   - Exception handling examples

#### 1.3 Read Test Case Specification
1. Open and read `{{TEST_GENERATION_DOMAIN_BASE_PATH}}/WP-{ID}-tests.md`
2. Extract test requirements:
   - Test scenarios that must be supported
   - Edge cases that must be handled
   - Validation scenarios
   - Error scenarios

### 2. Domain Model Implementation

#### 2.1 Identify Domain Entities
From the business specification, identify:
- **Entities**: Main domain objects with identity
- **Value Objects**: Objects defined by their attributes
- **Aggregates**: Entity clusters with consistency boundaries
- **Domain Events**: Events that occur in the domain

#### 2.2 Implement Domain Entities
For each entity in the business specification:

1. **Create Entity Class**
   - Location: `{{CODE_GENERATION_BACKEND_OUTPUT}}/wp-{ID}/domain/[EntityName].java`
   - Follow naming conventions from backend specification
   - Add JPA annotations (@Entity, @Table, @Id, etc.)
   - Reference backend specification for annotation patterns

2. **Define Attributes**
   - Map business specification attributes to Java fields
   - Use appropriate Java types
   - Add JPA column annotations (@Column, @Temporal, etc.)
   - Add validation annotations (@NotNull, @Size, @Pattern, etc.)
   - Reference backend specification for type mappings

3. **Define Relationships**
   - Map business specification relationships to JPA relationships
   - Use @OneToMany, @ManyToOne, @ManyToMany, @OneToOne as appropriate
   - Define cascade types based on business rules
   - Define fetch types (LAZY vs EAGER) per backend specification
   - Set up bidirectional relationships correctly

4. **Implement Domain Logic**
   - Add business methods that enforce business rules
   - Implement validation logic
   - Implement calculated fields
   - Keep domain logic in domain layer (not in services)

5. **Add Constructors and Builders**
   - Create appropriate constructors
   - Consider builder pattern for complex entities
   - Follow patterns from backend specification

**Example Structure**:
```java
@Entity
@Table(name = "entity_name")
public class EntityName {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, length = 100)
    @NotBlank
    private String attribute;
    
    @OneToMany(mappedBy = "parent", cascade = CascadeType.ALL)
    private List<ChildEntity> children;
    
    // Domain logic methods
    public void businessMethod() {
        // Enforce business rules
    }
    
    // Getters, setters, equals, hashCode
}
```

#### 2.3 Implement Value Objects
For value objects in the business specification:
- Create immutable classes
- Use @Embeddable annotation if embedded in entities
- Implement equals() and hashCode() based on all attributes
- Reference backend specification for value object patterns

#### 2.4 Validate Domain Model
- [ ] All entities from business specification are implemented
- [ ] All attributes are mapped correctly
- [ ] All relationships are defined correctly
- [ ] All validation rules are applied
- [ ] Domain logic is in domain layer
- [ ] Code follows backend specification conventions

### 3. Repository Layer Implementation

#### 3.1 Identify Repository Requirements
From the business specification, identify:
- Which entities need repositories
- What queries are needed (find by criteria, custom queries)
- What operations are needed (CRUD, bulk operations)

#### 3.2 Implement Repository Interfaces
For each entity that needs data access:

1. **Create Repository Interface**
   - Location: `{{CODE_GENERATION_BACKEND_OUTPUT}}/wp-{ID}/repository/[EntityName]Repository.java`
   - Extend JpaRepository or appropriate base interface
   - Follow naming conventions from backend specification

2. **Define Query Methods**
   - Add finder methods using Spring Data JPA naming conventions
   - Add custom query methods with @Query annotation if needed
   - Reference backend specification for query patterns

3. **Add Specifications (if needed)**
   - Create Specification classes for complex queries
   - Follow backend specification patterns

**Example Structure**:
```java
@Repository
public interface EntityNameRepository extends JpaRepository<EntityName, Long> {
    
    // Query methods derived from method name
    List<EntityName> findByAttribute(String attribute);
    
    Optional<EntityName> findByAttributeAndStatus(String attribute, Status status);
    
    // Custom query
    @Query("SELECT e FROM EntityName e WHERE e.attribute LIKE %:search%")
    List<EntityName> searchByAttribute(@Param("search") String search);
    
    // Native query (if needed)
    @Query(value = "SELECT * FROM entity_name WHERE ...", nativeQuery = true)
    List<EntityName> customNativeQuery();
}
```

#### 3.3 Validate Repository Layer
- [ ] All entities have repositories
- [ ] All required queries are defined
- [ ] Query methods follow naming conventions
- [ ] Custom queries are correct
- [ ] Code follows backend specification patterns

### 4. Service Layer Implementation

#### 4.1 Identify Service Requirements
From the business specification, identify:
- Business processes that need to be implemented
- Business rules that need to be enforced
- Transaction boundaries
- Service operations (create, update, delete, query)

#### 4.2 Implement Service Interfaces
For each business capability:

1. **Create Service Interface**
   - Location: `{{CODE_GENERATION_BACKEND_OUTPUT}}/wp-{ID}/service/[ServiceName]Service.java`
   - Define business operations
   - Use business-oriented method names
   - Follow naming conventions from backend specification

**Example Structure**:
```java
public interface EntityNameService {
    
    EntityName create(EntityName entity);
    
    EntityName update(Long id, EntityName entity);
    
    void delete(Long id);
    
    Optional<EntityName> findById(Long id);
    
    List<EntityName> findAll();
    
    // Business-specific methods
    void performBusinessOperation(Long id, BusinessParams params);
}
```

#### 4.3 Implement Service Classes
For each service interface:

1. **Create Service Implementation**
   - Location: `{{CODE_GENERATION_BACKEND_OUTPUT}}/wp-{ID}/service/impl/[ServiceName]ServiceImpl.java`
   - Implement service interface
   - Add @Service annotation
   - Inject repositories via constructor injection
   - Reference backend specification for service patterns

2. **Implement Business Logic**
   - Translate business rules from business specification to code
   - Enforce validation rules
   - Implement business processes
   - Handle business exceptions
   - Maintain traceability to business specification (comments with rule IDs)

3. **Add Transaction Management**
   - Add @Transactional annotations
   - Set transaction boundaries per backend specification
   - Configure propagation and isolation levels if needed

4. **Implement Error Handling**
   - Throw business exceptions for business rule violations
   - Follow exception handling patterns from backend specification
   - Provide meaningful error messages

**Example Structure**:
```java
@Service
@Transactional
public class EntityNameServiceImpl implements EntityNameService {
    
    private final EntityNameRepository repository;
    
    public EntityNameServiceImpl(EntityNameRepository repository) {
        this.repository = repository;
    }
    
    @Override
    public EntityName create(EntityName entity) {
        // Business rule: BR-001 - Validate entity before creation
        validateEntity(entity);
        
        // Business rule: BR-002 - Check uniqueness
        if (repository.findByAttribute(entity.getAttribute()).isPresent()) {
            throw new BusinessException("Entity already exists");
        }
        
        return repository.save(entity);
    }
    
    @Override
    public EntityName update(Long id, EntityName entity) {
        // Business rule: BR-003 - Entity must exist
        EntityName existing = repository.findById(id)
            .orElseThrow(() -> new EntityNotFoundException("Entity not found"));
        
        // Business rule: BR-004 - Update logic
        existing.setAttribute(entity.getAttribute());
        
        return repository.save(existing);
    }
    
    // Other methods...
    
    private void validateEntity(EntityName entity) {
        // Implement validation logic from business specification
    }
}
```

#### 4.4 Validate Service Layer
- [ ] All business processes are implemented
- [ ] All business rules are enforced
- [ ] Transaction boundaries are correct
- [ ] Error handling is implemented
- [ ] Code is traceable to business specification
- [ ] Code follows backend specification patterns

### 5. API Layer Implementation

#### 5.1 Identify API Requirements
From the business specification, identify:
- Required API endpoints
- HTTP methods for each endpoint
- Request/response formats
- Query parameters
- Path variables
- Status codes for different scenarios

#### 5.2 Implement DTOs

1. **Create Request DTOs**
   - Location: `{{CODE_GENERATION_BACKEND_OUTPUT}}/wp-{ID}/api/dto/[EntityName]RequestDTO.java`
   - Define fields for API requests
   - Add validation annotations
   - Follow DTO patterns from backend specification

2. **Create Response DTOs**
   - Location: `{{CODE_GENERATION_BACKEND_OUTPUT}}/wp-{ID}/api/dto/[EntityName]ResponseDTO.java`
   - Define fields for API responses
   - Include only necessary data (no sensitive information)
   - Follow DTO patterns from backend specification

3. **Create Mapper Classes**
   - Location: `{{CODE_GENERATION_BACKEND_OUTPUT}}/wp-{ID}/api/mapper/[EntityName]Mapper.java`
   - Implement mapping between entities and DTOs
   - Use MapStruct or manual mapping per backend specification

**Example DTO Structure**:
```java
// Request DTO
public class EntityNameRequestDTO {
    
    @NotBlank(message = "Attribute is required")
    @Size(max = 100, message = "Attribute must not exceed 100 characters")
    private String attribute;
    
    // Getters and setters
}

// Response DTO
public class EntityNameResponseDTO {
    
    private Long id;
    private String attribute;
    private LocalDateTime createdAt;
    
    // Getters and setters
}

// Mapper
@Component
public class EntityNameMapper {
    
    public EntityName toEntity(EntityNameRequestDTO dto) {
        // Map DTO to entity
    }
    
    public EntityNameResponseDTO toResponseDTO(EntityName entity) {
        // Map entity to response DTO
    }
}
```

#### 5.3 Implement Controllers

1. **Create Controller Class**
   - Location: `{{CODE_GENERATION_BACKEND_OUTPUT}}/wp-{ID}/api/controller/[EntityName]Controller.java`
   - Add @RestController annotation
   - Add @RequestMapping for base path
   - Inject service and mapper via constructor injection
   - Follow REST conventions from backend specification

2. **Implement API Endpoints**
   - Create endpoint for each operation in business specification
   - Use appropriate HTTP methods (GET, POST, PUT, DELETE, PATCH)
   - Use appropriate status codes (200, 201, 204, 400, 404, 500)
   - Add validation (@Valid annotation)
   - Add API documentation annotations (Swagger/OpenAPI)
   - Follow URL patterns from backend specification

3. **Implement Error Handling**
   - Handle validation errors
   - Handle business exceptions
   - Return appropriate error responses
   - Follow error response format from backend specification

**Example Controller Structure**:
```java
@RestController
@RequestMapping("/api/v1/entity-names")
public class EntityNameController {
    
    private final EntityNameService service;
    private final EntityNameMapper mapper;
    
    public EntityNameController(EntityNameService service, EntityNameMapper mapper) {
        this.service = service;
        this.mapper = mapper;
    }
    
    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public EntityNameResponseDTO create(@Valid @RequestBody EntityNameRequestDTO request) {
        EntityName entity = mapper.toEntity(request);
        EntityName created = service.create(entity);
        return mapper.toResponseDTO(created);
    }
    
    @GetMapping("/{id}")
    public EntityNameResponseDTO findById(@PathVariable Long id) {
        EntityName entity = service.findById(id)
            .orElseThrow(() -> new EntityNotFoundException("Entity not found"));
        return mapper.toResponseDTO(entity);
    }
    
    @GetMapping
    public List<EntityNameResponseDTO> findAll() {
        return service.findAll().stream()
            .map(mapper::toResponseDTO)
            .collect(Collectors.toList());
    }
    
    @PutMapping("/{id}")
    public EntityNameResponseDTO update(
            @PathVariable Long id,
            @Valid @RequestBody EntityNameRequestDTO request) {
        EntityName entity = mapper.toEntity(request);
        EntityName updated = service.update(id, entity);
        return mapper.toResponseDTO(updated);
    }
    
    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@PathVariable Long id) {
        service.delete(id);
    }
    
    // Business-specific endpoints
    @PostMapping("/{id}/business-operation")
    public void performBusinessOperation(
            @PathVariable Long id,
            @Valid @RequestBody BusinessParamsDTO params) {
        service.performBusinessOperation(id, mapper.toBusinessParams(params));
    }
}
```

#### 5.4 Validate API Layer
- [ ] All required endpoints are implemented
- [ ] HTTP methods are correct
- [ ] Status codes are appropriate
- [ ] Request/response DTOs are defined
- [ ] Validation is implemented
- [ ] Error handling is implemented
- [ ] API follows backend specification conventions

### 6. Exception Handling Implementation

#### 6.1 Create Custom Exceptions
Create business-specific exceptions:
- Location: `{{CODE_GENERATION_BACKEND_OUTPUT}}/wp-{ID}/exception/`
- Create exception classes for business rule violations
- Follow exception patterns from backend specification

**Example**:
```java
public class BusinessException extends RuntimeException {
    public BusinessException(String message) {
        super(message);
    }
}

public class EntityNotFoundException extends RuntimeException {
    public EntityNotFoundException(String message) {
        super(message);
    }
}
```

#### 6.2 Create Global Exception Handler
Create controller advice for global exception handling:
- Location: `{{CODE_GENERATION_BACKEND_OUTPUT}}/wp-{ID}/exception/GlobalExceptionHandler.java`
- Handle all custom exceptions
- Return appropriate error responses
- Follow error response format from backend specification

**Example**:
```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(EntityNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ErrorResponse handleEntityNotFound(EntityNotFoundException ex) {
        return new ErrorResponse(HttpStatus.NOT_FOUND.value(), ex.getMessage());
    }
    
    @ExceptionHandler(BusinessException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ErrorResponse handleBusinessException(BusinessException ex) {
        return new ErrorResponse(HttpStatus.BAD_REQUEST.value(), ex.getMessage());
    }
    
    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ErrorResponse handleValidationException(MethodArgumentNotValidException ex) {
        // Extract validation errors
        Map<String, String> errors = new HashMap<>();
        ex.getBindingResult().getFieldErrors().forEach(error ->
            errors.put(error.getField(), error.getDefaultMessage())
        );
        return new ErrorResponse(HttpStatus.BAD_REQUEST.value(), "Validation failed", errors);
    }
}
```

### 7. Code Quality and Best Practices

#### 7.1 Code Organization
- [ ] Code is organized by layer (domain, repository, service, api)
- [ ] Package structure follows backend specification
- [ ] No circular dependencies between layers
- [ ] Proper separation of concerns

#### 7.2 Naming Conventions
- [ ] Class names follow backend specification conventions
- [ ] Method names are descriptive and follow conventions
- [ ] Variable names are meaningful
- [ ] Constants are properly named (UPPER_SNAKE_CASE)

#### 7.3 Documentation
- [ ] Classes have JavaDoc comments
- [ ] Complex methods have comments
- [ ] Business rules are documented with rule IDs
- [ ] API endpoints have Swagger/OpenAPI annotations

#### 7.4 Code Style
- [ ] Code follows backend specification style guide
- [ ] Consistent indentation and formatting
- [ ] No unused imports
- [ ] No commented-out code

### 8. Compilation and Verification

#### 8.1 Compile Code
1. Navigate to backend project root
2. Run build command:
   - Maven: `mvn clean compile`
   - Gradle: `gradle clean build`
3. Verify no compilation errors

#### 8.2 Verify Implementation
- [ ] All entities compile
- [ ] All repositories compile
- [ ] All services compile
- [ ] All controllers compile
- [ ] No compilation errors
- [ ] No warnings (or acceptable warnings only)

#### 8.3 Verify Business Rules
- [ ] All business rules from specification are implemented
- [ ] Business rules are traceable (comments with rule IDs)
- [ ] Validation rules are enforced
- [ ] Error scenarios are handled

#### 8.4 Verify API Completeness
- [ ] All required endpoints are implemented
- [ ] All endpoints match business specification requirements
- [ ] Request/response formats are correct
- [ ] Status codes are appropriate

### 9. Update Progress Tracking

#### 9.1 Read Current Progress
1. Read `{{CODE_GENERATION_STATUS}}`
2. Find workpackage entry for WP-{ID}
3. If workpackage doesn't exist, create new entry

#### 9.2 Update Backend Status
Update the workpackage entry:
```json
{
  "workpackageId": "WP-{ID}",
  "workpackageName": "[Name]",
  "status": "in_progress",
  "tiersNeeded": ["backend", ...],
  "tiersCompleted": ["backend"],
  "backend": {
    "status": "completed",
    "outputLocation": "{{CODE_GENERATION_BACKEND_OUTPUT}}/wp-{ID}",
    "completedDate": "[ISO 8601 timestamp]",
    "components": {
      "entities": [count],
      "repositories": [count],
      "services": [count],
      "controllers": [count]
    }
  },
  "completedDate": null  // Will be set when all tiers complete
}
```

#### 9.3 Save Progress
1. Write updated progress to `{{CODE_GENERATION_STATUS}}`
2. Update lastUpdated timestamp
3. Verify file is valid JSON

### 10. Error Handling and Recovery

#### 10.1 Common Error Scenarios

1. **Missing Business Specification**
   - Detection: Business specification file not found
   - Recovery: Cannot proceed without specification
   - Escalation: Escalate to supervisor - critical blocker

2. **Ambiguous Business Rules**
   - Detection: Business rule is unclear or contradictory
   - Recovery: Document ambiguity in {{CODE_GENERATION_ERRORS}}
   - Escalation: Request clarification from supervisor

3. **Compilation Errors**
   - Detection: Code doesn't compile
   - Recovery: Fix syntax errors, missing imports, type mismatches
   - Escalation: If errors persist after fixes, escalate

4. **Missing Dependencies**
   - Detection: Required classes/libraries not available
   - Recovery: Check if Phase 4.0 completed successfully
   - Escalation: If project structure is incomplete, escalate

5. **Business Rule Conflicts**
   - Detection: Business rules contradict each other
   - Recovery: Document conflict in {{CODE_GENERATION_ERRORS}}
   - Escalation: Request clarification from supervisor

#### 10.2 Error Reporting
Document all errors in `{{CODE_GENERATION_ERRORS}}`:
```json
{
  "phase": "4.1",
  "workpackageId": "WP-{ID}",
  "timestamp": "[ISO 8601]",
  "errorType": "[Error category]",
  "description": "[What went wrong]",
  "businessRule": "[Related business rule ID if applicable]",
  "impact": "[How this affects implementation]",
  "recoveryAction": "[What was done]",
  "status": "open|resolved",
  "requiresEscalation": true|false
}
```

### 11. Completion and Handoff

#### 11.1 Completion Checklist
Before marking Phase 4.1 complete for this workpackage:
- [ ] All domain entities implemented
- [ ] All repositories implemented
- [ ] All services implemented with business logic
- [ ] All API endpoints implemented
- [ ] All exception handling implemented
- [ ] Code compiles without errors
- [ ] All business rules implemented and traceable
- [ ] Progress tracking updated
- [ ] No critical errors or all errors resolved

#### 11.2 Handoff to Phase 4.2 or Next Workpackage
Provide to supervisor:
- Confirmation that backend tier is complete for WP-{ID}
- Location of generated code
- Component counts (entities, repositories, services, controllers)
- Any warnings or notes for frontend implementation
- Confirmation that progress tracking is updated

---

## Output Format

### Backend Code Structure
**Location**: `{{CODE_GENERATION_BACKEND_OUTPUT}}/wp-{ID}/`

**Directory Structure**:
```
wp-{ID}/
├── domain/
│   ├── EntityName1.java
│   ├── EntityName2.java
│   └── ValueObject.java
├── repository/
│   ├── EntityName1Repository.java
│   └── EntityName2Repository.java
├── service/
│   ├── EntityName1Service.java
│   ├── EntityName2Service.java
│   └── impl/
│       ├── EntityName1ServiceImpl.java
│       └── EntityName2ServiceImpl.java
├── api/
│   ├── controller/
│   │   ├── EntityName1Controller.java
│   │   └── EntityName2Controller.java
│   ├── dto/
│   │   ├── EntityName1RequestDTO.java
│   │   ├── EntityName1ResponseDTO.java
│   │   ├── EntityName2RequestDTO.java
│   │   └── EntityName2ResponseDTO.java
│   └── mapper/
│       ├── EntityName1Mapper.java
│       └── EntityName2Mapper.java
└── exception/
    ├── BusinessException.java
    ├── EntityNotFoundException.java
    └── GlobalExceptionHandler.java
```

### Progress Tracking Update
**File**: `{{CODE_GENERATION_STATUS}}`

**Updated Entry**:
```json
{
  "workpackageId": "WP-{ID}",
  "workpackageName": "[Name]",
  "status": "in_progress",
  "tiersNeeded": ["backend", "frontend"],
  "tiersCompleted": ["backend"],
  "backend": {
    "status": "completed",
    "outputLocation": "{{CODE_GENERATION_BACKEND_OUTPUT}}/wp-{ID}",
    "completedDate": "2026-02-16T14:30:00Z",
    "components": {
      "entities": 5,
      "repositories": 3,
      "services": 4,
      "controllers": 3
    }
  },
  "frontend": null,
  "batch": null,
  "completedDate": null
}
```

---

## Quality Criteria

### Business Rule Implementation
- All business rules from business specification are implemented
- Business rules are enforced in appropriate layers
- Business rules are traceable (comments with rule IDs)
- Validation rules are applied correctly
- Error scenarios are handled per business rules

### Code Compilation
- Code compiles without errors
- No missing dependencies
- No type mismatches
- No syntax errors

### Layered Architecture
- Domain logic is in domain layer
- Data access is in repository layer
- Business logic is in service layer
- API logic is in API layer
- No layer violations (e.g., controllers calling repositories directly)

### API Design
- REST conventions followed
- Appropriate HTTP methods used
- Appropriate status codes returned
- Request/response DTOs properly defined
- Validation implemented
- Error responses follow specification format

### Code Quality
- Code follows backend specification conventions
- Naming conventions followed
- Code is well-documented
- No code smells
- Proper exception handling

### Traceability
- All entities traceable to business specification
- All business rules traceable to business specification
- All API endpoints traceable to business specification
- Clear mapping between requirements and implementation

---

## End of Phase 4.1 Document
