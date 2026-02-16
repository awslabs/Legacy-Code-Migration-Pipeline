
# Backend Specification for Java Legacy Migration Projects

**Version:** 1.0  
**Last Updated:** February 16, 2026  
**Scope:** Backend/API tier standards and requirements

---

## 1. Overview

### 1.1 Purpose

Establish consistent, maintainable, and cloud-native backend standards for transaction-heavy applications migrating from mainframe environments, with emphasis on ACID transaction guarantees and high-throughput processing.

### 1.2 Related Specifications

- `00-COMMON-SPECIFICATION.md` - Cross-cutting standards (MUST be followed)
- `01-FRONTEND-SPECIFICATION.md` - Frontend tier requirements
- `03-BATCH-SPECIFICATION.md` - Batch processing tier requirements

### 1.3 Architecture Context

**Core Transaction Macroservice (Modular Monolith):**
- Handles core business transactions requiring ACID guarantees
- Maintains strong consistency within shared database
- Clear internal module boundaries with enforced dependencies
- Single deployment unit for simplified operations

**Strategic Microservices:**
- Integration services (legacy system connectors)
- External API adapters
- Services with different scaling requirements
- Services requiring independent deployment cycles

**When to Use Each Pattern:**

| Use Modular Monolith When | Use Microservices When |
|---------------------------|------------------------|
| Strong transactional consistency required | Independent scaling needed |
| Shared data model across features | Different technology stacks required |
| Team works on related features | Independent deployment cycles critical |
| Operational simplicity preferred | Service isolation required |

---

## 2. Technology Stack

### 2.1 Core Framework

**Required:** Spring Boot 3.2.x or higher

**Required Spring Modules:**
- Spring Boot Starter Web
- Spring Boot Starter Data JPA
- Spring Boot Starter Security
- Spring Boot Starter Validation
- Spring Boot Starter Actuator
- Spring Cloud (for microservices patterns)
- Spring Modulith (for modular monolith structure)

### 2.2 Java Version

**Required:** Java 17 LTS or Java 21 LTS  
**Prohibited:** Java 8, Java 11

### 2.3 Build Tool

**Recommended:** Maven 3.9.x

**Multi-Module Structure:**
- Parent POM with shared dependencies and versions
- Shared-common module for cross-cutting concerns
- Business domain modules (module-a, module-b, etc.)
- Application module for configuration and startup

### 2.4 Database

**Relational Database (Required for Core Transactions):**
- **Recommended:** AWS RDS PostgreSQL 15.x
- **Alternative:** AWS Aurora PostgreSQL, AWS RDS MySQL 8.x

**Connection Pooling:**
- Use HikariCP (included with Spring Boot)
- Pool size: 20-50 connections per instance

**NoSQL (Optional for Specific Use Cases):**
- AWS DynamoDB (high-throughput, key-value access)
- Redis (caching, session storage)

### 2.5 Messaging

**AWS SQS:** Asynchronous processing, reliable message delivery  
**AWS SNS:** Pub/sub messaging, event broadcasting  
**AWS EventBridge:** Event-driven architecture, event routing

---

## 3. Project Structure

### 3.1 Modular Monolith Structure

```
core-service/
├── shared-common/          # Cross-cutting concerns
│   ├── exception/
│   ├── util/
│   ├── config/
│   └── dto/
├── module-a/               # Business domain module
│   ├── api/                # Public interfaces (exposed to other modules)
│   ├── domain/             # Business logic (internal only)
│   ├── data/               # Persistence (internal only)
│   ├── integration/        # External calls (internal only)
│   └── web/                # REST controllers
├── module-b/               # Another business domain module
├── application/            # Application configuration and startup
│   ├── config/
│   └── resources/
│       ├── application.yml
│       └── db/migration/
└── pom.xml (parent)
```

### 3.2 Module Dependency Rules

**Allowed:**
- All modules can depend on `shared-common`
- Modules can depend on other module's `api` package only
- No circular dependencies

**Prohibited:**
- Direct access to another module's `domain`, `data`, or `integration` packages
- Shared mutable state between modules
- Direct database access across module boundaries

**Enforcement:**
- Use ArchUnit tests to validate dependencies
- Configure Maven Enforcer Plugin

### 3.3 Microservice Structure

```
integration-service/
├── config/
├── controller/
├── service/
├── client/
├── model/
└── resources/
    └── application.yml
```

---

## 4. API Design Standards

### 4.1 RESTful API Conventions

**URL Structure:**
- `/api/v1/{resource}`
- `/api/v1/{resource}/{id}`
- `/api/v1/{resource}/{id}/{sub-resource}`

**HTTP Methods:**
- `GET` - Retrieve resources (idempotent, safe)
- `POST` - Create resources
- `PUT` - Update entire resource (idempotent)
- `PATCH` - Partial update
- `DELETE` - Remove resource (idempotent)

**HTTP Status Codes:**
- `200 OK` - Successful GET, PUT, PATCH
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Business rule violation
- `422 Unprocessable Entity` - Semantic validation error
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service temporarily unavailable

### 4.2 Request/Response Format

**Standard Request Headers:**
- `Content-Type: application/json`
- `Authorization: Bearer {token}`
- `X-Correlation-ID: {uuid}`

**Success Response Structure:**
- Include resource ID and status
- Include timestamps (createdAt, updatedAt)
- Use ISO 8601 format for dates

**Error Response Structure:**
- Include timestamp, status code, error type
- Include descriptive message
- Include request path and correlation ID
- Include field-level errors for validation failures

### 4.3 OpenAPI Specification

**Requirements:**
- All APIs must have OpenAPI documentation
- Use springdoc-openapi-starter-webmvc-ui
- Document all endpoints with @Operation annotations
- Document all response codes with @ApiResponses
- Include request/response examples

**Access Points:**
- Swagger UI: `/swagger-ui.html`
- OpenAPI JSON: `/v3/api-docs`

### 4.4 Pagination Standards

**Query Parameters:**
- `page` - Page number (0-indexed)
- `size` - Page size (default: 20, max: 100)
- `sort` - Sort field and direction (e.g., `createdAt,desc`)

**Response Structure:**
- Include content array
- Include pagination metadata (page number, size, total elements, total pages)
- Include navigation flags (first, last)

### 4.5 Filtering and Searching

**Requirements:**
- Use query parameters for filtering
- Support multiple filter criteria
- Use ISO 8601 format for date filters
- Combine filtering with pagination

---

## 5. Domain Model Patterns

### 5.1 Entity Design Principles

**Requirements:**
- All entities must have audit fields (createdAt, updatedAt, createdBy, updatedBy)
- Use optimistic locking with `@Version` for concurrent updates
- Index frequently queried columns
- Use LAZY fetch strategy by default
- Include business logic in entity methods (not just getters/setters)
- Use `@EntityListeners(AuditingEntityListener.class)` for auditing

**Annotations:**
- `@Entity` - Mark as JPA entity
- `@Table(name, indexes)` - Define table name and indexes
- `@Id` with `@GeneratedValue` - Primary key
- `@Column` - Column constraints (nullable, unique, length)
- `@Enumerated(EnumType.STRING)` - Enum storage
- `@CreatedDate`, `@LastModifiedDate` - Audit timestamps
- `@Version` - Optimistic locking

### 5.2 Value Objects

**Requirements:**
- Use `@Embeddable` for value objects
- Make value objects immutable (no setters)
- Implement equals() and hashCode()
- Use `@Embedded` in entities to include value objects

**Use Cases:**
- Address, Money, DateRange
- Any concept that has no identity but has attributes

### 5.3 Enumerations

**Requirements:**
- Use `@Enumerated(EnumType.STRING)` (never ORDINAL)
- Include description field in enum
- Include business logic methods (e.g., isTerminal(), canTransitionTo())
- Store as string for database readability and migration safety

### 5.4 Auditing

**Requirements:**
- Enable JPA auditing with `@EnableJpaAuditing`
- Implement `AuditorAware<String>` to provide current user
- Use `@CreatedBy`, `@LastModifiedBy` for user tracking
- Use `@CreatedDate`, `@LastModifiedDate` for timestamp tracking
- Create base auditable entity class for reuse

---

## 6. Repository Layer Patterns

### 6.1 Spring Data JPA Repository

**Requirements:**
- Extend `JpaRepository<Entity, ID>`
- Use method naming conventions for simple queries
- Use `@Query` for complex queries
- Use `@EntityGraph` to avoid N+1 queries
- Use `@Modifying` for update/delete queries
- Use projections for read-only queries

**Method Naming Conventions:**
- `findBy{Property}` - Find by single property
- `findBy{Property}And{Property}` - Find by multiple properties
- `findBy{Property}OrderBy{Property}` - Find with sorting
- `existsBy{Property}` - Check existence
- `countBy{Property}` - Count results

### 6.2 Custom Repository Implementation

**Requirements:**
- Create custom interface for complex queries
- Implement using `@PersistenceContext EntityManager`
- Use Criteria API for dynamic queries
- Build predicates based on search criteria
- Support pagination in custom queries
- Separate count query for total elements

**Use Cases:**
- Dynamic search with multiple optional criteria
- Complex joins not expressible in method names
- Database-specific optimizations

### 6.3 Query Optimization

**Best Practices:**
- Use `@EntityGraph` to fetch associations eagerly when needed
- Use projections (interfaces) for read-only queries
- Index frequently queried columns
- Use pagination for large result sets
- Monitor slow queries (>100ms)
- Use query hints for caching

### 6.4 Native Queries

**When to Use:**
- Complex queries not expressible in JPQL
- Database-specific features (window functions, CTEs)
- Performance optimization

**Requirements:**
- Use `@Query(nativeQuery = true)`
- Use named parameters
- Document why native query is necessary
- Consider portability implications

---

## 7. Service Layer Patterns

### 7.1 Service Design

**Requirements:**
- Define service interface
- Implement with `@Service` annotation
- Use constructor injection for dependencies
- Apply `@Transactional(readOnly = true)` at class level
- Override with `@Transactional` for write operations
- Use `@Slf4j` for logging

**Service Responsibilities:**
- Business logic orchestration
- Transaction management
- Validation coordination
- Event publishing
- Error handling

### 7.2 Transaction Management

**Declarative Transactions:**
- Use `@Transactional` annotation
- Specify isolation level (default: READ_COMMITTED)
- Specify propagation (default: REQUIRED)
- Set timeout for long-running operations
- Specify rollback rules

**Transaction Propagation:**
- `REQUIRED` - Join existing or create new (default)
- `REQUIRES_NEW` - Always create new transaction
- `MANDATORY` - Must be called within transaction
- `SUPPORTS` - Optional transaction
- `NOT_SUPPORTED` - Execute without transaction
- `NEVER` - Fail if transaction exists

**Read-Only Optimization:**
- Use `@Transactional(readOnly = true)` for read operations
- Provides optimization hint to database
- Prevents accidental modifications

### 7.3 Exception Handling

**Custom Exceptions:**
- Create domain-specific exceptions
- Extend RuntimeException (unchecked)
- Include meaningful error messages
- Include relevant context (e.g., resource ID)

**Exception Types:**
- `ResourceNotFoundException` - Resource not found (404)
- `BusinessException` - Business rule violation (409)
- `ValidationException` - Validation failure (400)
- `UnauthorizedException` - Authentication failure (401)

**Global Exception Handler:**
- Use `@RestControllerAdvice`
- Handle all exception types
- Return consistent error response structure
- Log errors appropriately
- Include correlation ID for tracing

### 7.4 Business Validation

**Requirements:**
- Create validator components with `@Component`
- Separate validation from service logic
- Throw ValidationException with field errors
- Validate business rules (not just format)
- Check cross-entity constraints

**Validation Types:**
- Existence checks (e.g., customer exists)
- Uniqueness checks (e.g., code not duplicate)
- Business rule checks (e.g., value within limits)
- State transition checks (e.g., can cancel order)
- Reference integrity checks (e.g., no active dependencies)

---

## 8. DTO Patterns

### 8.1 Request DTOs

**Requirements:**
- Use Bean Validation annotations
- Separate DTOs for create and update operations
- Use `@Valid` for nested objects
- Include meaningful validation messages
- Use appropriate validation annotations

**Validation Annotations:**
- `@NotNull`, `@NotBlank`, `@NotEmpty`
- `@Size(min, max)` for strings and collections
- `@Min`, `@Max` for numbers
- `@DecimalMin`, `@DecimalMax` for decimals
- `@Digits(integer, fraction)` for precision
- `@Pattern(regexp)` for format validation
- `@Email` for email validation
- `@Past`, `@Future` for dates

### 8.2 Response DTOs

**Requirements:**
- Include all relevant data for client
- Use consistent naming conventions
- Include timestamps (createdAt, updatedAt)
- Include audit information when relevant
- Create summary DTOs for list operations

**Response Types:**
- Full response - All entity details
- Summary response - Key fields only
- Nested response - Include related entities

### 8.3 Mapping with MapStruct

**Requirements:**
- Use MapStruct for entity-DTO mapping
- Define mapper interface with `@Mapper(componentModel = "spring")`
- Use `@Mapping` to customize field mapping
- Use `@MappingTarget` for update operations
- Ignore audit fields in mapping

**Mapper Methods:**
- `toResponse(Entity)` - Entity to response DTO
- `toEntity(CreateRequest)` - Request to entity
- `updateEntity(UpdateRequest, @MappingTarget Entity)` - Update entity
- `toResponseList(List<Entity>)` - List mapping

---

## 9. Validation Standards

### 9.1 Bean Validation (JSR-380)

**Requirements:**
- Use spring-boot-starter-validation dependency
- Apply validation annotations to request DTOs
- Use `@Valid` in controller methods
- Use `@Validated` at class level for method validation
- Handle MethodArgumentNotValidException globally

### 9.2 Custom Validators

**Requirements:**
- Create custom annotation with `@Constraint`
- Implement `ConstraintValidator<Annotation, Type>`
- Return true for valid values
- Use ConstraintValidatorContext for custom messages
- Register validator in annotation

### 9.3 Business Validation

**Requirements:**
- Create validator components
- Validate business rules not expressible in annotations
- Check database constraints (uniqueness, existence)
- Validate state transitions
- Throw ValidationException with field errors

### 9.4 Validation Groups

**Use Cases:**
- Different validation rules for create vs update
- Conditional validation based on operation type
- Partial validation for specific scenarios

**Requirements:**
- Define group interfaces
- Apply groups to validation annotations
- Use `@Validated(Group.class)` in controllers

---

## 10. Security Standards

### 10.1 Spring Security Configuration

**Requirements:**
- Use spring-boot-starter-security
- Use spring-boot-starter-oauth2-resource-server
- Configure SecurityFilterChain bean
- Disable CSRF for stateless APIs
- Configure CORS appropriately
- Use stateless session management

**Security Rules:**
- Permit public endpoints (health, swagger)
- Require authentication for all other endpoints
- Use role-based authorization
- Configure OAuth2 resource server with JWT

### 10.2 JWT Token Configuration

**Requirements:**
- Configure issuer URI
- Configure JWK set URI
- Implement JwtAuthenticationConverter
- Map JWT claims to authorities
- Use "ROLE_" prefix for roles

### 10.3 Method-Level Security

**Requirements:**
- Enable method security with `@EnableMethodSecurity`
- Use `@PreAuthorize` for authorization checks
- Use SpEL expressions for complex rules
- Create custom security expressions for reusable logic

**Authorization Patterns:**
- Role-based: `@PreAuthorize("hasRole('ADMIN')")`
- Combined: `@PreAuthorize("hasRole('ADMIN') or @security.isOwner(#id)")`
- Custom expressions for business logic

### 10.4 Security Best Practices

**Requirements:**
- Use BCryptPasswordEncoder for password hashing
- Never log sensitive data (passwords, tokens, PII)
- Encrypt sensitive data at rest
- Use HTTPS for all communications
- Implement proper session timeout
- Use secure random for token generation
- Configure security headers (CSP, X-Frame-Options, etc.)

---

## 11. Caching Strategy

### 11.1 Spring Cache Configuration

**Requirements:**
- Use spring-boot-starter-cache
- Enable caching with `@EnableCaching`
- Configure cache manager (Caffeine or Redis)
- Define cache names
- Configure cache properties (size, TTL)

**Cache Manager Options:**
- Caffeine - In-memory, single instance
- Redis - Distributed, multi-instance

### 11.2 Cache Annotations

**Cacheable:**
- Use `@Cacheable(value, key)` for read operations
- Result cached by specified key
- Cache hit returns cached value without method execution

**Cache Eviction:**
- Use `@CacheEvict(value, key)` to remove cache entry
- Use `allEntries = true` to clear entire cache
- Use `@Caching` for multiple cache operations

**Cache Put:**
- Use `@CachePut(value, key)` to update cache
- Method always executed, result cached

### 11.3 Distributed Caching with Redis

**Requirements:**
- Use spring-boot-starter-data-redis
- Configure RedisConnectionFactory
- Configure RedisCacheManager
- Set appropriate TTL
- Configure serialization (JSON recommended)

### 11.4 Caching Best Practices

**When to Cache:**
- Frequently accessed data
- Expensive computations
- Slow database queries
- External API responses
- Reference/lookup data

**When NOT to Cache:**
- Frequently changing data
- User-specific sensitive data
- Large objects (>1MB)
- Data requiring strong consistency

**Cache Key Design:**
- Use meaningful, unique keys
- Include version in key for invalidation
- Consider key length limits
- Use consistent key format

---

## 12. Messaging Patterns

### 12.1 AWS SQS Integration

**Requirements:**
- Use spring-cloud-aws-starter-sqs
- Configure SqsTemplate bean
- Use `@SqsListener` for consumers
- Include correlation ID in messages
- Implement idempotent message processing

**Message Producer:**
- Send messages using SqsTemplate
- Include message attributes
- Set appropriate visibility timeout

**Message Consumer:**
- Use `@SqsListener` annotation
- Handle exceptions appropriately
- Implement retry logic
- Use dead-letter queues for failed messages

### 12.2 AWS SNS Integration

**Requirements:**
- Use spring-cloud-aws-starter-sns
- Configure SnsTemplate bean
- Publish events to topics
- Include message attributes

### 12.3 Spring Events (Internal)

**Requirements:**
- Extend ApplicationEvent for custom events
- Use ApplicationEventPublisher to publish
- Use `@EventListener` for synchronous handling
- Use `@Async` for asynchronous handling
- Use `@TransactionalEventListener` for transactional events

**Event Phases:**
- BEFORE_COMMIT - Before transaction commits
- AFTER_COMMIT - After successful commit (default)
- AFTER_ROLLBACK - After rollback
- AFTER_COMPLETION - After commit or rollback

### 12.4 Messaging Best Practices

**Message Design:**
- Keep messages small and focused
- Include correlation ID for tracing
- Use idempotent message processing
- Implement retry logic with exponential backoff
- Use dead-letter queues for failed messages

**Error Handling:**
- Distinguish retryable vs non-retryable errors
- Log failures appropriately
- Move to DLQ after max retries
- Monitor DLQ for issues

---

## 13. Database Migrations

### 13.1 Flyway Configuration

**Requirements:**
- Use flyway-core dependency
- Use flyway-database-postgresql (or appropriate driver)
- Enable Flyway in application properties
- Configure migration locations
- Enable validation on migrate

### 13.2 Migration File Structure

**Naming Convention:**
- `V{version}__{description}.sql` - Versioned migration
- `R__{description}.sql` - Repeatable migration
- Version format: V1, V1.1, V1.1.1

**Directory Structure:**
- Store in `src/main/resources/db/migration/`
- Organize by version number
- Use descriptive names

### 13.3 Migration Types

**Create Table:**
- Define all columns with appropriate types
- Define primary key
- Define constraints (NOT NULL, UNIQUE)
- Create indexes for frequently queried columns

**Alter Table:**
- Add columns
- Modify columns (with caution)
- Add constraints
- Create indexes

**Data Migration:**
- Insert reference data
- Transform existing data
- Migrate from legacy tables
- Use WHERE NOT EXISTS to avoid duplicates

### 13.4 Migration Best Practices

**Guidelines:**
- Never modify existing migrations
- Test migrations on copy of production data
- Keep migrations small and focused
- Use transactions (default in Flyway)
- Include rollback scripts for critical changes
- Version control all migration files
- Document complex migrations

**Rollback Strategy:**
- Create separate rollback scripts
- Test rollback procedures
- Document rollback steps
- Consider data loss implications

---

## 14. Performance Standards

### 14.1 Database Performance

**Connection Pool Configuration:**
- Maximum pool size: 50
- Minimum idle: 10
- Connection timeout: 30 seconds
- Idle timeout: 10 minutes
- Max lifetime: 30 minutes
- Leak detection threshold: 60 seconds

**Query Optimization:**
- Use indexes on frequently queried columns
- Avoid N+1 queries (use @EntityGraph or JOIN FETCH)
- Use pagination for large result sets
- Use projections for read-only queries
- Monitor slow queries (>100ms)

**Slow Query Logging:**
- Enable SQL logging in development
- Log slow queries in production
- Monitor query execution times
- Analyze and optimize slow queries

### 14.2 API Performance

**Response Time Targets:**
- GET requests: <200ms (p95)
- POST/PUT requests: <500ms (p95)
- Complex queries: <1000ms (p95)

**Performance Optimization:**
- Use caching for frequently accessed data
- Implement pagination for list endpoints
- Use async processing for long-running operations
- Compress responses (gzip)
- Use CDN for static content

**Async Processing:**
- Enable async with `@EnableAsync`
- Configure thread pool executor
- Use `@Async` for long-running operations
- Return CompletableFuture for async methods

### 14.3 Memory Management

**JVM Configuration:**
- Set appropriate heap size (-Xms, -Xmx)
- Use G1GC garbage collector
- Set max GC pause time
- Enable heap dump on OutOfMemoryError

**Memory Best Practices:**
- Close resources properly (use try-with-resources)
- Avoid memory leaks (unsubscribed listeners, static collections)
- Use pagination to avoid loading large datasets
- Monitor heap usage and GC metrics

### 14.4 Performance Monitoring

**Actuator Metrics:**
- Expose health, info, metrics, prometheus endpoints
- Enable Prometheus metrics export
- Monitor JVM metrics
- Monitor HTTP metrics
- Monitor database metrics

**Custom Metrics:**
- Use MeterRegistry to create custom metrics
- Track business metrics (e.g., orders created)
- Track performance metrics (e.g., operation duration)
- Use tags for metric dimensions

---

## 15. Testing Standards

### 15.1 Testing Strategy

**Test Pyramid:**
- Unit Tests: 70% (fast, isolated)
- Integration Tests: 20% (database, external services)
- End-to-End Tests: 10% (full application flow)

**Coverage Requirements:**
- Minimum 80% code coverage for new code
- 100% coverage for critical business logic
- All API error scenarios tested
- All validation rules tested

### 15.2 Unit Testing

**Requirements:**
- Use JUnit 5 (Jupiter)
- Use Mockito for mocking
- Use AssertJ for assertions
- Test service layer in isolation
- Mock repository and external dependencies

**Test Structure:**
- Given - Setup test data and mocks
- When - Execute method under test
- Then - Assert results and verify interactions

### 15.3 Integration Testing

**Requirements:**
- Use `@SpringBootTest` for full context
- Use Testcontainers for database
- Use `@AutoConfigureTestDatabase(replace = NONE)`
- Test with real database
- Test transaction behavior

**Testcontainers:**
- Use PostgreSQLContainer for PostgreSQL
- Configure dynamic properties
- Reuse containers across tests
- Clean up test data

### 15.4 API Testing

**Requirements:**
- Use `@WebMvcTest` for controller tests
- Use MockMvc for HTTP testing
- Mock service layer
- Test all endpoints
- Test all status codes
- Test validation
- Test error handling

**Test Scenarios:**
- Happy path (successful operations)
- Validation failures
- Business rule violations
- Resource not found
- Unauthorized access
- Server errors

### 15.5 Test Data Management

**Requirements:**
- Use test data builders
- Use meaningful test data
- Clean up test data after tests
- Use `@Transactional` for automatic rollback
- Avoid test interdependencies

---

## 16. Monitoring and Observability

### 16.1 Logging Standards

**Requirements:**
- Use SLF4J with Logback
- Use structured logging (JSON format)
- Include correlation ID in logs
- Log at appropriate levels
- Never log sensitive data

**Log Levels:**
- ERROR - Errors requiring immediate attention
- WARN - Potential issues
- INFO - Important business events
- DEBUG - Detailed diagnostic information
- TRACE - Very detailed diagnostic information

### 16.2 Metrics

**Requirements:**
- Expose Actuator metrics endpoint
- Export metrics to Prometheus
- Track JVM metrics (heap, GC, threads)
- Track HTTP metrics (requests, errors, duration)
- Track database metrics (connections, queries)
- Track custom business metrics

### 16.3 Health Checks

**Requirements:**
- Implement health endpoint
- Check database connectivity
- Check external service connectivity
- Return appropriate status (UP, DOWN, OUT_OF_SERVICE)
- Include details in response

### 16.4 Distributed Tracing

**Requirements:**
- Use correlation ID for request tracing
- Include correlation ID in all logs
- Include correlation ID in error responses
- Propagate correlation ID to downstream services
- Generate correlation ID if not provided

---

## 17. Deployment Standards

### 17.1 Docker Configuration

**Requirements:**
- Use multi-stage Dockerfile
- Use official base images
- Minimize image size
- Run as non-root user
- Include health check
- Set appropriate resource limits

**Dockerfile Structure:**
- Build stage - Compile application
- Runtime stage - Run application
- Copy only necessary files
- Use .dockerignore

### 17.2 Kubernetes Deployment

**Requirements:**
- Define Deployment resource
- Define Service resource
- Configure resource requests and limits
- Configure liveness and readiness probes
- Configure environment variables
- Use ConfigMaps for configuration
- Use Secrets for sensitive data

**Resource Limits:**
- Memory request: 512Mi
- Memory limit: 1Gi
- CPU request: 250m
- CPU limit: 500m

### 17.3 Environment Configuration

**Requirements:**
- Use Spring profiles (dev, staging, prod)
- Externalize configuration
- Use environment variables for secrets
- Never commit secrets to version control
- Use different configurations per environment

### 17.4 CI/CD Pipeline

**Requirements:**
- Build on every commit
- Run tests in pipeline
- Run security scans
- Build Docker image
- Push to container registry
- Deploy to environments
- Run smoke tests after deployment

---

## 18. Migration Patterns

### 18.1 Strangler Fig Pattern

**Approach:**
- Gradually replace legacy functionality
- Route traffic to new service
- Keep legacy system running
- Migrate incrementally
- Decommission legacy when complete

### 18.2 Data Migration

**Requirements:**
- Analyze legacy data structures
- Map legacy to new schema
- Create migration scripts
- Validate migrated data
- Handle data quality issues
- Maintain data lineage

**Migration Steps:**
1. Extract data from legacy system
2. Transform to new format
3. Validate transformed data
4. Load into new system
5. Verify data integrity
6. Reconcile with legacy

### 18.3 API Compatibility

**Requirements:**
- Maintain backward compatibility
- Version APIs appropriately
- Deprecate old versions gradually
- Provide migration guides
- Support multiple versions during transition

---

## 19. Prohibited Practices

### 19.1 Code Anti-Patterns

**Prohibited:**
- God classes (>500 lines)
- Circular dependencies
- Tight coupling to specific implementations
- Hardcoded values (use configuration)
- Commented-out code
- TODO comments in production code

### 19.2 Security Anti-Patterns

**Prohibited:**
- Storing passwords in plain text
- Using weak encryption algorithms
- Exposing sensitive data in logs
- Disabling security features
- Using default credentials
- Trusting user input without validation

### 19.3 Performance Anti-Patterns

**Prohibited:**
- N+1 query problems
- Loading entire tables without pagination
- Synchronous processing of long-running operations
- Unbounded caches
- Missing database indexes
- Inefficient algorithms

### 19.4 Database Anti-Patterns

**Prohibited:**
- Using ORDINAL for enums
- Missing foreign key constraints
- Missing indexes on foreign keys
- Using SELECT * in production code
- Modifying existing migrations
- Storing large BLOBs in database

---

## 20. Document Control

### 20.1 Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-16 | Architecture Team | Initial version |

### 20.2 Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Technical Lead | | | |
| Architecture Lead | | | |
| Security Lead | | | |

### 20.3 Review Schedule

This document should be reviewed and updated:
- Quarterly for minor updates
- Annually for major revisions
- When new technologies are adopted
- When architectural patterns change

### 20.4 Related Documents

- Common Specification
- Frontend Specification
- Batch Specification
- Security Standards
- Deployment Guide
- Migration Playbook

---

**End of Backend Specification**
