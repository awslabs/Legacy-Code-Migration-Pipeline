# Phase 5.2: Backend Code Generation

---

## Orchestration Information

**Phase**: Phase 5 - Code Generation
**Step**: Step 5.2 - Backend Code Generation
**Team Supervisor**: development_team_supervisor
**Assigned Agent**: development_specialist_code_generation
**Task File Name**: {{TASKS_BASE_PATH}}/phase_5.2_backend_generation.md

### Expected Deliverables

1. **Workpackage Module**
   - Location: `{{CODE_GENERATION_BACKEND_OUTPUT}}/[wp-module-name]/` (e.g., `user-module/`, `account-module/`)
   - Description: Complete backend implementation for ONE workpackage
   - Includes: Entities, repositories, services, controllers, DTOs, mappers

2. **Shared Code** (if needed)
   - Location: `{{CODE_GENERATION_BACKEND_OUTPUT}}/shared-common/`
   - Description: Cross-cutting code used by multiple workpackages
   - Includes: Common utilities, exceptions, base classes

3. **Progress Tracking Update**
   - File: {{CODE_GENERATION_STATUS}}
   - Description: Updated progress with backend completion for this workpackage

### Success Criteria
- [ ] Workpackage module created and integrated into existing project structure
- [ ] All business requirements implemented
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
- **Migration Mapping Spec**: `{{TECH_SPEC_MIGRATION_MAPPING}}`
- **Backend Tech Spec**: `{{TECH_SPEC_BACKEND}}`
- **Business Specification**: `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-{ID}-specification.md`
- **Existing Project**: `{{CODE_GENERATION_BACKEND_OUTPUT}}/` (skeleton from Phase 5.1)

### Output Locations
- **Workpackage module**: `{{CODE_GENERATION_BACKEND_OUTPUT}}/[wp-module-name]/`
- **Shared code**: `{{CODE_GENERATION_BACKEND_OUTPUT}}/shared-common/`
- **Progress tracking**: `{{CODE_GENERATION_STATUS}}`

---

## Objective

Implement ONE workpackage as a module in the existing backend project structure. Create all necessary code (entities, repositories, services, controllers) following the tech spec patterns.

**CRITICAL - MODULE PER WORKPACKAGE**:
- Create ONE module for this workpackage (e.g., `user-module/`, `account-module/`)
- Integrate into existing multi-module structure and build system.
- Put shared/common code in `shared-common/` module
- Follow the project structure from Backend Tech Spec Section 2

**CRITICAL - TODO MARKERS**:
- Add `// TODO:` comments for integration points with other workpackages
- Add `// TODO:` comments for external service integration (OAuth2, logging, etc.)
- Add `// TODO:` comments for missing information or unclear requirements
- Format: `// TODO: [WP-XXX] Description of what's needed`

---

## Instructions

### 1. Read Specifications

1. **Read Migration Mapping** at `{{TECH_SPEC_MIGRATION_MAPPING}}`
   - Section 1: Cross-Cutting Patterns (authentication, persistence, API design, etc.)
   - Section 2.{WP-ID}: Workpackage-Specific Mapping (entities, APIs, business logic)

2. **Read Backend Tech Spec** at `{{TECH_SPEC_BACKEND}}`
   - Section 2: Project Structure (module layout, package structure)
   - Section 4: Naming Conventions (how to name classes, packages, methods)
   - Section 5: Code Organization (where entities, services, controllers go)

3. **Read Business Specification** at `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-{ID}-specification.md`
   - Chapter 2: Business Entities (what domain objects to create)
   - Chapter 3: Business Rules (what logic to implement)
   - Chapter 4: Business Operations (what endpoints/services to create)

### 2. Determine Module Structure

Based on Backend Tech Spec Section 2, determine the module structure:

**CRITICAL - Module Naming Decision**:

**If this workpackage belongs to an EXISTING business domain** (e.g., WP-002 "User Profile Management" and WP-001 "User Authentication" both belong to "User Management"):
- ✅ **Use the SAME module** (e.g., `user-module`)
- Create separate packages within the module for each workpackage
- Example:
  ```
  user-module/
  ├── domain/
  │   ├── authentication/    # WP-001
  │   │   └── User.java
  │   └── profile/           # WP-002
  │       └── UserProfile.java
  ├── service/
  │   ├── authentication/    # WP-001
  │   └── profile/           # WP-002
  └── web/
      ├── authentication/    # WP-001
      └── profile/           # WP-002
  ```
### 3. Create or Update Module Structure

**If module DOES NOT exist** (new business domain):

1. **Create module directory**: `{{CODE_GENERATION_BACKEND_OUTPUT}}/[module-name]/`

2. **Create module build file**: `pom.xml` or `build.gradle` in module directory
   - Add module dependencies (shared-common, spring-boot-starter-web, etc.)
   - Follow dependency patterns from Backend Tech Spec Section 3

3. **Create package structure** according to Backend Tech Spec Section 2:
   - `api/` - Public interfaces and DTOs
   - `domain/[wp-feature]/` - Entities and domain logic for this WP
   - `data/` - Repositories
   - `service/[wp-feature]/` - Business services for this WP
   - `web/[wp-feature]/` - REST controllers for this WP

4. **Update parent build file**: Add new module to parent pom.xml `<modules>` section

**If module ALREADY EXISTS** (same business domain as previous WP):

1. **Navigate to existing module**: `{{CODE_GENERATION_BACKEND_OUTPUT}}/[module-name]/`

2. **Create workpackage-specific packages**:
   - `domain/[wp-feature]/` - Entities for this WP
   - `service/[wp-feature]/` - Services for this WP
   - `web/[wp-feature]/` - Controllers for this WP

3. **Update module build file** (if new dependencies needed)

4. **DO NOT update parent build file** (module already registered)

**Example - Adding WP-002 to existing user-module**:
```
user-module/
├── pom.xml (already exists)
├── domain/
│   ├── authentication/     # WP-001 (already exists)
│   │   └── User.java
│   └── profile/            # WP-002 (NEW - add this)
│       ├── UserProfile.java
│       └── UserPreference.java
├── service/
│   ├── authentication/     # WP-001 (already exists)
│   └── profile/            # WP-002 (NEW - add this)
│       └── UserProfileService.java
└── web/
    ├── authentication/     # WP-001 (already exists)
    └── profile/            # WP-002 (NEW - add this)
        └── UserProfileController.java
```
│   └── dto/
├── user-module/            # Domain: User Management
│   ├── pom.xml
│   ├── api/
│   ├── domain/
│   │   ├── authentication/ # WP-001: User Authentication
│   │   └── profile/        # WP-002: User Profile Management
│   ├── data/
│   ├── service/
│   │   ├── authentication/ # WP-001
│   │   └── profile/        # WP-002
│   └── web/
│       ├── authentication/ # WP-001
│       └── profile/        # WP-002
├── account-module/         # Domain: Account Management
│   └── ...                 # WP-003: Account Creation
└── application/            # Main app (already exists from Phase 5.1)
```

**Module naming**: Use business domain name (e.g., `user-module`, `account-module`, `transaction-module`), NOT workpackage ID

### 3. Create Module Structure

1. **Create module directory**: `{{CODE_GENERATION_BACKEND_OUTPUT}}/[wp-module-name]/`

2. **Create module build file**: `pom.xml` or `build.gradle` in module directory
   - Add module dependencies (shared-common, spring-boot-starter-web, etc.)
   - Follow dependency patterns from Backend Tech Spec Section 3

3. **Create package structure** according to Backend Tech Spec Section 2:
   - `api/` - Public interfaces and DTOs
   - `domain/` - Entities and domain logic
   - `data/` - Repositories
   - `service/` - Business services
   - `web/` - REST controllers

4. **Update parent build file**: Add new module to parent pom.xml `<modules>` section

### 4. Implement Business Entities

From Business Specification Chapter 2 and Migration Mapping Section 2.{WP-ID}.4:

1. **Read entity definitions**:
   - Business Specification Chapter 2: Business entities and their attributes
   - Migration Mapping Section 2.{WP-ID}.4: Data model mapping (legacy → modern)
   - Migration Mapping Section 1.2: Data persistence patterns

2. **Read implementation guidance from Backend Tech Spec**:
   - How to define entities (annotations, base classes, etc.)
   - How to map attributes (types, constraints, etc.)
   - How to define relationships (one-to-many, many-to-one, etc.)
   - How to add validation (validation framework, rules, etc.)
   - Where to place entity classes (package structure)

3. **Create entity classes** following the tech spec patterns:
   - Place in the package specified by tech spec
   - Use the entity definition approach from tech spec
   - Map all attributes from business specification
   - Define relationships as specified in tech spec
   - Add validation as specified in tech spec

4. **Add TODOs for relationships with other workpackages**:
   ```
   // Example (syntax will vary by tech stack):
   // TODO: [WP-002] Add relationship to Account entity when account-module is implemented
   // Relationship definition commented out until WP-002 is complete
   ```

### 5. Implement Repositories

From Migration Mapping Section 1.2 (Data Persistence):

1. **Read repository patterns from Backend Tech Spec**:
   - How to create repository classes/interfaces
   - What base classes or interfaces to extend
   - How to define query methods
   - Naming conventions for repositories
   - Where to place repository classes (package structure)

2. **Create repository classes** following the tech spec patterns:
   - Place in the package specified by tech spec
   - Use the repository pattern from tech spec
   - Add custom query methods as needed
   - Follow naming conventions from tech spec

3. **Add TODOs for integration points**:
   ```
   // Example (syntax will vary by tech stack):
   // TODO: [EXTERNAL] Integrate with caching service when available
   // Caching configuration commented out until external service is ready
   ```

### 6. Implement Services

From Business Specification Chapter 3 (Business Rules) and Chapter 4 (Operations):

1. **Read service patterns from Backend Tech Spec**:
   - How to create service classes
   - How to implement business logic
   - How to enforce business rules
   - How to handle transactions
   - How to add validation
   - Where to place service classes (package structure)

2. **Read business logic from specifications**:
   - Business Specification Chapter 3: Business rules to enforce
   - Business Specification Chapter 4: Operations to implement
   - Migration Mapping Section 2.{WP-ID}.2: Business logic preservation
   - Migration Mapping Section 2.{WP-ID}.5: Service layer design

3. **Create service classes** following the tech spec patterns:
   - Place in the package specified by tech spec
   - Implement business logic as specified
   - Enforce business rules as specified
   - Handle transactions as specified in tech spec
   - Add validation as specified in tech spec

4. **Add TODOs for integration points**:
   ```
   // Example (syntax will vary by tech stack):
   // TODO: [EXTERNAL] Integrate with OAuth2 server for user provisioning
   // Call external auth service to create user there first
   
   // TODO: [WP-003] Send notification when notification-module is implemented
   // notificationService.sendWelcomeEmail(user);
   ```

### 7. Implement Controllers

From Migration Mapping Section 2.{WP-ID}.3 (API Design):

1. **Read controller patterns from Backend Tech Spec**:
   - How to create controller classes
   - How to define API endpoints
   - How to add security/authorization
   - How to add validation
   - How to handle request/response mapping
   - Where to place controller classes (package structure)

2. **Read API design from Migration Mapping**:
   - Section 2.{WP-ID}.3: Exact endpoints, DTOs, security requirements
   - Section 1.4: API design patterns (URL structure, HTTP methods, status codes)

3. **Create controller classes** following the tech spec patterns:
   - Place in the package specified by tech spec
   - Define REST endpoints as specified in migration mapping
   - Add security as specified in tech spec
   - Add validation as specified in tech spec
   - Handle request/response mapping as specified

4. **Add TODOs for missing information**:
   ```
   // Example (syntax will vary by tech stack):
   // TODO: [SECURITY] Verify correct role for this endpoint
   // Security annotation to be confirmed
   
   // TODO: [MISSING-INFO] Confirm if email verification is required before user creation
   ```

### 8. Implement DTOs and Mappers

1. **Read DTO patterns from Backend Tech Spec**:
   - How to create DTOs (request/response objects)
   - Where to place DTOs (package structure)
   - How to add validation to DTOs
   - How to create mappers (entity ↔ DTO conversion)

2. **Read data structures from Migration Mapping**:
   - Section 2.{WP-ID}.3: API Design (request/response structures)
   - Section 2.{WP-ID}.4: Data Model (entity structures)

3. **Create DTOs** following the tech spec patterns:
   - Request DTOs (for incoming data)
   - Response DTOs (for outgoing data)
   - Add validation as specified in tech spec

4. **Create mappers** following the tech spec patterns:
   - Convert between entities and DTOs
   - Use mapping approach from tech spec (library, manual, etc.)

### 9. Handle External Service Integration

From Migration Mapping Section 1.1 (Authentication) and other external services:

1. **Identify external services** from Migration Mapping Section 1:
   - Section 1.1: Authentication & Authorization (OAuth2, LDAP, etc.)
   - Section 1.7: Logging & Monitoring (external logging services)
   - Other sections mentioning external services

2. **Read integration patterns from Backend Tech Spec**:
   - How to configure external service clients
   - How to add security configuration
   - Where to place configuration classes

3. **DO NOT implement external service functionality**

4. **DO add integration code with TODOs**:
   ```
   // Example (syntax will vary by tech stack):
   // TODO: [EXTERNAL] Configure OAuth2 Resource Server
   // Replace with actual OAuth2 server URL from environment config
   
   // TODO: [CONFIG] Add issuer-uri and jwk-set-uri to application configuration
   ```

### 10. Handle Shared Code

If code is needed by multiple workpackages:

1. **Identify shared code**:
   - Common exceptions
   - Base classes
   - Utility classes
   - Common DTOs

2. **Read shared code patterns from Backend Tech Spec**:
   - Where to place shared code (shared-common module, base package, etc.)
   - How to organize shared code

3. **Create in shared location** as specified by tech spec:
   - Follow the project structure from tech spec
   - Use naming conventions from tech spec

### 11. Update Progress Tracking

Update `{{CODE_GENERATION_STATUS}}`:

```json
{
  "phase": "Phase 5 - Code Generation",
  "currentStep": "5.2 - Backend Generation",
  "workpackages": {
    "WP-{ID}": {
      "status": "completed",
      "backend": {
        "moduleCreated": true,
        "moduleName": "[wp-module-name]",
        "entitiesCount": 3,
        "repositoriesCount": 3,
        "servicesCount": 2,
        "controllersCount": 2,
        "todosCount": 5,
        "compiles": true
      }
    }
  }
}
```

---

## TODO Marker Guidelines

**When to add TODOs**:
1. **Integration with other workpackages**: When code needs to interact with entities/services from other WPs
2. **External service integration**: When code needs to integrate with OAuth2, logging, messaging, etc.
3. **Missing information**: When business spec is unclear or incomplete
4. **Configuration needed**: When environment-specific config is required
5. **Future enhancements**: When spec mentions "future" or "phase 2" features

**TODO format**:
```java
// TODO: [CATEGORY] Description
// Categories: WP-XXX, EXTERNAL, MISSING-INFO, CONFIG, FUTURE
```

**Examples**:
```java
// TODO: [WP-002] Add relationship to Account when account-module exists
// TODO: [EXTERNAL] Integrate with Keycloak OAuth2 server
// TODO: [MISSING-INFO] Confirm validation rules for email format
// TODO: [CONFIG] Add database connection pool size to application.yml
// TODO: [FUTURE] Implement audit logging when audit-module is ready
```

---

## Verification

Before marking complete:
1. ✅ Module compiles without errors
2. ✅ Module is integrated into parent build
3. ✅ All entities from business spec are created
4. ✅ All business rules are implemented (or have TODOs)
5. ✅ All API endpoints from migration mapping are created
6. ✅ TODOs are added for all integration points
7. ✅ Code follows naming conventions from tech spec
8. ✅ No external service functionality is implemented (only integration code)

---

## End of Phase 5.2

The workpackage backend module is now complete and integrated into the project. Move to next workpackage or next tier.
