# Phase: Code Generation - Java

## Context
- Project Structure: Standard migration project folder structure
- Input Location: 
  - `/Users/kerimman/kookminbank/output/specifications/domain/` - Domain specifications from Phase 4
  - `/Users/kerimman/kookminbank/output/specifications/tests/` - Test case definitions from Phase 5
  - `/Users/kerimman/kookminbank/input/target_framework_specifications/java/` - Java framework specifications
  - `/Users/kerimman/kookminbank/input/example_code/src/main/java/` - Java example code to be used as guidance for implementation
- Output Location: 
  - `/Users/kerimman/kookminbank/output/src/` - Generated Java implementation code
  - `/Users/kerimman/kookminbank/progress/06-code-generation-status.json` - Phase completion tracking
- Previous Phase Artifacts:
  - Consolidated domain specifications with business rules, entities, and functions
  - Language-agnostic test case definitions
  - Traceability matrix linking to original specifications

## Objective
Implement modern Java code based on domain specifications and test case definitions while following target architecture patterns. Create a complete, maintainable Java application that preserves all business rules from the original legacy system. Ensure full traceability between generated code and business specifications, and adhere to Java best practices and target framework standards.

## Instructions

### 1. Architecture Setup and Project Structure
1. Review target framework specifications for Java implementation
2. Create standard Maven project structure:
   - Set up `pom.xml` with required dependencies
   - Configure Spring Boot if specified in target framework
   - Create appropriate package structure based on domains
   - Set up configuration files for application properties
   - Configure logging framework
   - Set up database connection configuration if applicable

### 2. Domain Model Implementation
1. For each domain specification:
   - Create Java entity classes for all business entities
   - Implement validation annotations matching business rules
   - Create appropriate relationships between entities
   - Implement value objects for complex types
   - Add JPA annotations if using ORM
   - Ensure proper encapsulation and immutability where appropriate
   - Document entity classes with Javadoc referencing business specifications

### 3. Data Access Layer Implementation
1. For each domain:
   - Create repository interfaces following target architecture pattern
   - Implement data access methods based on business requirements
   - Configure ORM mappings if applicable
   - Implement transaction management
   - Create database migration scripts if required
   - Implement data validation at repository level
   - Document repository classes with traceability to business rules

### 4. Business Logic Implementation
1. For each business rule in domain specifications:
   - Create service classes implementing business logic
   - Ensure all business rules are correctly implemented
   - Implement validation logic matching specifications
   - Create appropriate exception handling
   - Implement transaction boundaries
   - Ensure separation of concerns
   - Document service methods with traceability to business rules
   - Implement complex business workflows as separate components

### 5. API Layer Implementation
1. For each domain:
   - Create REST controllers or service interfaces as specified
   - Implement request/response DTOs
   - Create input validation
   - Implement proper error handling and status codes
   - Document API endpoints with OpenAPI/Swagger annotations
   - Implement security controls if specified
   - Create API documentation with examples

### 6. Cross-Cutting Concerns Implementation
1. Based on target framework specifications:
   - Implement logging throughout the application
   - Configure security framework (Spring Security, etc.)
   - Implement exception handling framework
   - Create custom validators if required
   - Implement audit logging if specified
   - Configure monitoring and metrics if required
   - Implement caching strategy if applicable

### 7. Integration Points
1. For each external system integration:
   - Create client interfaces
   - Implement integration adapters
   - Configure connection parameters
   - Implement error handling and retry logic
   - Create mock implementations for testing
   - Document integration points with traceability

### 8. Configuration Management
1. Based on target framework specifications:
   - Create environment-specific configurations
   - Implement feature toggles if required
   - Configure external property sources
   - Implement configuration validation
   - Document configuration options
   - Create sample configuration files

### 9. Traceability Documentation
1. For all implemented components:
   - Add Javadoc comments linking to business rules
   - Create traceability matrix from code to specifications
   - Document architectural decisions with rationale
   - Create code-to-test mapping documentation
   - Ensure all business rules have corresponding code implementations
   - Document any deviations from specifications with justification

### 10. Progress Tracking
1. Update progress tracking for each completed domain:
   - Record completion status and artifacts
   - Document any issues or exceptions
   - Update phase status in progress tracking system

## Output Format

### Java Project Structure
```
src/
├── main/
│   ├── java/
│   │   └── com/
│   │       └── example/
│   │           └── migration/
│   │               ├── [domain1]/
│   │               │   ├── controller/
│   │               │   ├── service/
│   │               │   ├── repository/
│   │               │   ├── model/
│   │               │   └── dto/
│   │               ├── [domain2]/
│   │               │   ├── controller/
│   │               │   ├── service/
│   │               │   ├── repository/
│   │               │   ├── model/
│   │               │   └── dto/
│   │               └── common/
│   │                   ├── config/
│   │                   ├── exception/
│   │                   ├── security/
│   │                   └── util/
│   └── resources/
│       ├── application.properties
│       ├── application-dev.properties
│       ├── application-prod.properties
│       └── db/
│           └── migration/
└── test/
    └── java/
        └── com/
            └── example/
                └── migration/
                    ├── [domain1]/
                    │   ├── controller/
                    │   ├── service/
                    │   ├── repository/
                    │   └── model/
                    └── [domain2]/
                        ├── controller/
                        ├── service/
                        ├── repository/
                        └── model/
```

### Java Entity Class Format
```java
/**
 * Entity representing [Business Entity Name] from domain specification [Domain-ID].
 * 
 * Business Rules:
 * - [Domain-ID]-BR-001: [Rule description]
 * - [Domain-ID]-BR-002: [Rule description]
 * 
 * @see [Domain Specification Reference]
 */
@Entity
@Table(name = "entity_name")
public class EntityName {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    /**
     * [Attribute description]
     * 
     * Business Rules:
     * - [Domain-ID]-BR-003: [Rule description]
     */
    @Column(name = "attribute_name", nullable = false)
    @NotNull(message = "Attribute cannot be null")
    @Size(min = 1, max = 100, message = "Attribute must be between 1 and 100 characters")
    private String attributeName;
    
    // Additional attributes, getters, setters, etc.
    
    /**
     * Business method implementing rule [Domain-ID]-BR-004
     * 
     * @param parameter Description of parameter
     * @return Description of return value
     * @throws ValidationException if business rule is violated
     */
    public ReturnType businessMethod(ParameterType parameter) {
        // Implementation
    }
}
```

### Java Service Class Format
```java
/**
 * Service implementing business logic for [Domain Name] domain.
 * 
 * Implements business rules from specification [Domain-ID].
 */
@Service
public class DomainService {
    
    private final DomainRepository repository;
    
    @Autowired
    public DomainService(DomainRepository repository) {
        this.repository = repository;
    }
    
    /**
     * Implements business operation [Operation Name].
     * 
     * Business Rules:
     * - [Domain-ID]-BR-005: [Rule description]
     * - [Domain-ID]-BR-006: [Rule description]
     * 
     * @param request Operation request parameters
     * @return Operation result
     * @throws BusinessException if operation violates business rules
     */
    @Transactional
    public ResultType businessOperation(RequestType request) {
        // Implementation with business rule enforcement
    }
}
```

### Java Controller Format
```java
/**
 * REST API controller for [Domain Name] domain.
 */
@RestController
@RequestMapping("/api/v1/domain")
public class DomainController {
    
    private final DomainService service;
    
    @Autowired
    public DomainController(DomainService service) {
        this.service = service;
    }
    
    /**
     * API endpoint for [Operation Name].
     * 
     * @param request Operation request
     * @return Operation response
     */
    @PostMapping("/operation")
    public ResponseEntity<ResponseDTO> operation(@Valid @RequestBody RequestDTO request) {
        // Implementation with service call
    }
}
```

### Traceability Documentation Format
```markdown
# Code Traceability Matrix: [Domain Name]

## Overview
This document maps Java implementation components to business specifications and test cases.

## Entity Mappings

### [Entity Name]
- **Source File:** `src/main/java/com/example/migration/domain/model/EntityName.java`
- **Business Entity:** [Domain-ID]-BE-001
- **Business Rules:**
  - [Domain-ID]-BR-001: [Rule description]
    - Implementation: Field validation annotations
  - [Domain-ID]-BR-002: [Rule description]
    - Implementation: Business method `validateRule()`
- **Test Cases:**
  - [Domain-ID]-TC-001: [Test case description]
  - [Domain-ID]-TC-002: [Test case description]

## Service Mappings

### [Service Name]
- **Source File:** `src/main/java/com/example/migration/domain/service/DomainService.java`
- **Business Functions:**
  - [Domain-ID]-BF-001: [Function description]
    - Implementation: Method `businessOperation()`
- **Business Rules:**
  - [Domain-ID]-BR-003: [Rule description]
    - Implementation: Validation logic in `validateBusinessRule()`
- **Test Cases:**
  - [Domain-ID]-TC-003: [Test case description]
  - [Domain-ID]-TC-004: [Test case description]

## API Mappings

### [API Endpoint]
- **Source File:** `src/main/java/com/example/migration/domain/controller/DomainController.java`
- **Business Functions:**
  - [Domain-ID]-BF-002: [Function description]
    - Implementation: REST endpoint `/api/v1/domain/operation`
- **Test Cases:**
  - [Domain-ID]-TC-005: [Test case description]
```

### Progress Tracking Format
```json
{
  "phaseId": "06-code-generation",
  "status": "in_progress|completed",
  "targetLanguage": "Java",
  "targetFramework": "Spring Boot",
  "domains": [
    {
      "domainId": "D-001",
      "domainName": "Customer Management",
      "status": "completed",
      "components": {
        "entities": 5,
        "repositories": 2,
        "services": 3,
        "controllers": 2,
        "utilities": 1
      },
      "businessRuleImplementation": "100%",
      "sourceLocation": "output/src/main/java/com/example/migration/customer",
      "completedDate": "YYYY-MM-DD"
    },
    {
      "domainId": "D-002",
      "domainName": "Order Processing",
      "status": "in_progress",
      "components": {
        "entities": 0,
        "repositories": 0,
        "services": 0,
        "controllers": 0,
        "utilities": 0
      },
      "businessRuleImplementation": "0%",
      "sourceLocation": null,
      "completedDate": null
    }
  ],
  "completedCount": 1,
  "totalCount": 5,
  "lastUpdated": "YYYY-MM-DD"
}
```

## Quality Criteria

### Code Quality
- Code follows Java best practices and conventions
- Classes have single responsibility
- Methods are small and focused
- Proper exception handling is implemented
- Code is well-documented with Javadoc
- No code smells or anti-patterns
- Consistent naming conventions
- Proper encapsulation and access modifiers

### Business Rule Implementation
- All business rules from specifications are implemented
- Validation logic matches business requirements
- Business workflows are correctly implemented
- Edge cases are handled appropriately
- Error conditions trigger appropriate responses
- Business constraints are enforced

### Architecture Compliance
- Code follows target architecture patterns
- Proper separation of concerns
- Layered architecture is maintained
- Dependencies flow in correct direction
- Framework features are used appropriately
- Configuration follows best practices
- Security controls are properly implemented

### Traceability
- All code components link to business specifications
- Javadoc comments reference business rules
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

## Error Handling

### Common Error Scenarios

1. **Ambiguous Business Rule Implementation**
   - Detection: Business rule with unclear implementation approach
   - Recovery: Document multiple implementation options with pros/cons
   - Escalation: Flag for human review with specific questions

2. **Architecture Pattern Conflicts**
   - Detection: Business requirement conflicts with architecture pattern
   - Recovery: Document conflict and propose adaptation
   - Escalation: Request architecture decision if significant deviation required

3. **Framework Limitation**
   - Detection: Target framework cannot directly support business requirement
   - Recovery: Implement custom solution with framework integration
   - Escalation: Document limitation and proposed workaround

4. **Complex Business Logic**
   - Detection: Business rule requires complex implementation
   - Recovery: Break down into smaller components with clear responsibilities
   - Escalation: Request clarification for ambiguous business logic

### Error Reporting Format
- Log errors to: `progress/06-code-generation-errors.json`
- Include: timestamp, error type, context, attempted resolution
- Update phase status to indicate partial completion or issues

### Fallback Strategies
- Implement simplified version with TODO comments for complex logic
- Use design patterns to handle complex business rules
- Create abstraction layers for problematic framework limitations
- Document technical debt with clear remediation plans
- Implement feature toggles for problematic features