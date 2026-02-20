# Phase 5.3: Frontend Code Generation

---

## Orchestration Information

**Phase**: Phase 5 - Code Generation
**Step**: Step 5.3 - Frontend Code Generation
**Team Supervisor**: development_team_supervisor
**Assigned Agent**: development_specialist_code_generation
**Task File Name**: {{TASKS_BASE_PATH}}/phase_5.3_frontend_generation.md

### Expected Deliverables

1. **Workpackage Feature Module**
   - Location: `{{CODE_GENERATION_FRONTEND_OUTPUT}}/src/features/[feature-name]/`
   - Description: Complete frontend implementation for ONE workpackage
   - Includes: Components, pages, services, types, store slices

2. **Shared Code** (if needed)
   - Location: `{{CODE_GENERATION_FRONTEND_OUTPUT}}/src/shared/`
   - Description: Cross-cutting code used by multiple workpackages
   - Includes: Common components, utilities, types, hooks

3. **Progress Tracking Update**
   - File: {{CODE_GENERATION_STATUS}}
   - Description: Updated progress with frontend completion for this workpackage

### Success Criteria
- [ ] Feature module created and integrated into existing project structure
- [ ] All UI requirements implemented
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
- **Frontend Tech Spec**: `{{TECH_SPEC_FRONTEND}}`
- **Business Specification**: `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-{ID}-specification.md`
- **Backend API**: `{{CODE_GENERATION_BACKEND_OUTPUT}}/` (for API integration)
- **Existing Project**: `{{CODE_GENERATION_FRONTEND_OUTPUT}}/` (skeleton from Phase 5.1)

### Output Locations
- **Feature module**: `{{CODE_GENERATION_FRONTEND_OUTPUT}}/src/features/[feature-name]/`
- **Shared code**: `{{CODE_GENERATION_FRONTEND_OUTPUT}}/src/shared/`
- **Progress tracking**: `{{CODE_GENERATION_STATUS}}`

---

## Objective

Implement ONE workpackage as a feature module in the existing frontend project structure. Create all necessary code (components, pages, services, state management) following the tech spec patterns.

**CRITICAL - FEATURE MODULE PER WORKPACKAGE**:
- Create ONE feature folder for this workpackage (e.g., `features/users/`, `features/accounts/`)
- Integrate into existing project structure
- Put shared/common code in `src/shared/`
- Follow the project structure from Frontend Tech Spec Section 2

**CRITICAL - TODO MARKERS**:
- Add `// TODO:` comments for integration points with other workpackages
- Add `// TODO:` comments for backend API endpoints not yet implemented
- Add `// TODO:` comments for missing information or unclear requirements
- Format: `// TODO: [WP-XXX] Description of what's needed`

---

## Instructions

### 1. Read Specifications

1. **Read Migration Mapping** at `{{TECH_SPEC_MIGRATION_MAPPING}}`
   - Section 1.4: API Design (endpoints to call)
   - Section 2.{WP-ID}.3: API Design (specific endpoints for this WP)
   - Section 3.2: Frontend Code Generation Guidance

2. **Read Frontend Tech Spec** at `{{TECH_SPEC_FRONTEND}}`
   - Section 2: Project Structure (feature module layout)
   - Section 4: Naming Conventions (how to name components, files)
   - Section 5: Code Organization (where components, pages, services go)

3. **Read Business Specification** at `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-{ID}-specification.md`
   - Chapter 2: Business Entities (what data to display/manage)
   - Chapter 4: Business Operations (what user actions to support)
   - Chapter 5: Business Processes (what workflows to implement)

### 2. Determine Feature Module Structure

Based on Frontend Tech Spec Section 2, determine the feature structure:

**CRITICAL - Feature Naming Decision**:

**If this workpackage belongs to an EXISTING business domain** (e.g., WP-002 "User Profile Management" and WP-001 "User Authentication" both belong to "User Management"):
- ✅ **Use the SAME feature folder** (e.g., `features/users/`)
- Create separate subfolders within the feature for each workpackage
- Example:
  ```
  features/users/
  ├── authentication/        # WP-001
  │   ├── components/
  │   ├── pages/
  │   └── services/
  ├── profile/               # WP-002
  │   ├── components/
  │   ├── pages/
  │   └── services/
  ├── types/                 # Shared types for all user-related features
  └── index.ts
  ```

**If this workpackage is a NEW business domain**:
- ✅ **Create a NEW feature folder** (e.g., `features/accounts/`, `features/transactions/`)

**How to decide**:
1. Check if a feature folder already exists for this business domain
2. If yes: Add to existing feature in a new subfolder
3. If no: Create new feature folder

**Example - Feature-Based Structure**:
```
frontend/
├── src/
│   ├── main.tsx (already exists)
│   ├── shared/              # Shared code
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── utils/
│   │   └── types/
│   └── features/
│       ├── users/           # Domain: User Management
│       │   ├── authentication/  # WP-001: User Authentication
│       │   │   ├── components/
│       │   │   ├── pages/
│       │   │   └── services/
│       │   ├── profile/         # WP-002: User Profile Management
│       │   │   ├── components/
│       │   │   ├── pages/
│       │   │   └── services/
│       │   ├── types/           # Shared types
│       │   └── index.ts
│       └── accounts/        # Domain: Account Management
│           └── ...          # WP-003: Account Creation
```

**Feature naming**: Use business domain name (e.g., `users`, `accounts`, `transactions`), NOT workpackage ID

### 3. Create or Update Feature Structure

**If feature folder DOES NOT exist** (new business domain):

1. **Create feature directory**: `{{CODE_GENERATION_FRONTEND_OUTPUT}}/src/features/[feature-name]/`

2. **Create workpackage subdirectory**: `[feature-name]/[wp-subfolder]/`

3. **Create subdirectories within workpackage folder**:
   - `components/` - UI components for this WP
   - `pages/` - Page-level components for this WP
   - `services/` - API client code for this WP
   - `store/` - State management for this WP (if using Redux/Zustand)
   - `types/` - TypeScript interfaces/types for this WP

4. **Create feature-level files**:
   - `types/index.ts` - Shared types for the entire feature
   - `index.ts` - Export public API of the feature

**If feature folder ALREADY EXISTS** (same business domain as previous WP):

1. **Navigate to existing feature**: `{{CODE_GENERATION_FRONTEND_OUTPUT}}/src/features/[feature-name]/`

2. **Create workpackage subdirectory**: `[feature-name]/[wp-subfolder]/`

3. **Create subdirectories within workpackage folder**:
   - `components/` - UI components for this WP
   - `pages/` - Page-level components for this WP
   - `services/` - API client code for this WP
   - `store/` - State management for this WP

4. **Update feature-level files**:
   - Add new types to `types/index.ts`
   - Export new components/pages from `index.ts`

**Example - Adding WP-002 to existing users feature**:
```
features/users/
├── authentication/          # WP-001 (already exists)
│   ├── components/
│   │   └── LoginForm.tsx
│   ├── pages/
│   │   └── LoginPage.tsx
│   └── services/
│       └── auth.service.ts
├── profile/                 # WP-002 (NEW - add this)
│   ├── components/
│   │   ├── ProfileForm.tsx
│   │   └── ProfileAvatar.tsx
│   ├── pages/
│   │   ├── ProfilePage.tsx
│   │   └── ProfileEditPage.tsx
│   └── services/
│       └── profile.service.ts
├── types/                   # Shared (update with profile types)
│   └── index.ts
└── index.ts                 # Update exports
```

### 4. Implement TypeScript Types

From Business Specification Chapter 2 and Migration Mapping Section 2.{WP-ID}.3:

1. **Read type definition patterns from Frontend Tech Spec**:
   - How to define types/interfaces
   - Where to place type definitions (package/folder structure)
   - Naming conventions for types

2. **Read data structures**:
   - Business Specification Chapter 2: Business entities and attributes
   - Migration Mapping Section 2.{WP-ID}.3: API Design (request/response structures)
   - Backend DTOs (to match backend API)

3. **Create type definitions** following the tech spec patterns:
   - Place in the location specified by tech spec
   - Match backend DTOs
   - Define request/response types
   - Define component prop types

4. **Add TODOs for relationships with other workpackages**:
   ```
   // Example (syntax will vary by language):
   // TODO: [WP-002] Add accounts relationship when accounts feature is implemented
   // accounts?: Account[];
   ```

### 5. Implement API Services

From Migration Mapping Section 2.{WP-ID}.3 (API endpoints):

1. **Read API service patterns from Frontend Tech Spec**:
   - How to create service classes
   - What HTTP client to use
   - How to handle request/response mapping
   - How to handle errors
   - Where to place service classes (folder structure)

2. **Read API endpoints from Migration Mapping**:
   - Section 2.{WP-ID}.3: Exact endpoints, methods, request/response formats
   - Section 1.4: API design patterns

3. **Create service classes** following the tech spec patterns:
   - Place in the location specified by tech spec
   - One service per entity or domain area
   - Use HTTP client from tech spec
   - Handle request/response mapping as specified
   - Handle errors as specified

4. **Add TODOs for missing endpoints**:
   ```
   // Example (syntax will vary by language/framework):
   // TODO: [BACKEND] Verify endpoint is implemented in backend
   
   // TODO: [WP-003] Add getUserNotifications when notification feature is ready
   ```

### 6. Implement State Management

From Frontend Tech Spec Section 6 (State Management):

1. **Read state management patterns from Frontend Tech Spec**:
   - What state management library to use (if any)
   - How to define state shape
   - How to define actions/mutations
   - How to define selectors/getters
   - How to handle async operations
   - Where to place state management code (folder structure)

2. **Create state management code** following the tech spec patterns:
   - Place in the location specified by tech spec
   - Define state shape
   - Define actions/mutations
   - Define selectors/getters
   - Handle async operations as specified

3. **Add TODOs for external integrations**:
   ```
   // Example (syntax will vary by state management library):
   // TODO: [EXTERNAL] Add authentication token to request
   ```

### 7. Implement Components

From Business Specification Chapter 4 (Operations) and Chapter 5 (Processes):

1. **Read component patterns from Frontend Tech Spec**:
   - How to create components
   - Component structure and organization
   - How to handle props/inputs
   - How to handle events/outputs
   - Styling approach
   - Where to place components (folder structure)

2. **Read UI requirements**:
   - Business Specification Chapter 4: Operations (what user actions to support)
   - Business Specification Chapter 5: Processes (what workflows to implement)

3. **Create components** following the tech spec patterns:
   - Place in the location specified by tech spec
   - Reusable UI components for this feature
   - Form components
   - List/table components
   - Detail/view components

4. **Add TODOs for integration points**:
   ```
   // Example (syntax will vary by framework):
   // TODO: [VALIDATION] Add client-side validation rules
   // TODO: [WP-002] Add account selection when accounts feature is ready
   // TODO: [MISSING-INFO] Confirm required fields and validation rules
   ```

### 8. Implement Pages

From Business Specification Chapter 5 (Business Processes):

1. **Read page patterns from Frontend Tech Spec**:
   - How to create page components
   - How to connect to state management
   - How to handle routing
   - Where to place page components (folder structure)

2. **Read workflow requirements**:
   - Business Specification Chapter 5: Business processes and workflows

3. **Create page components** following the tech spec patterns:
   - Place in the location specified by tech spec
   - List/index pages
   - Detail/view pages
   - Create/edit pages
   - Connect to state management as specified
   - Handle routing as specified

4. **Add TODOs for missing information**:
   ```
   // Example (syntax will vary by framework):
   // TODO: [WP-002] Add filter by account when accounts feature is ready
   // TODO: [MISSING-INFO] Confirm pagination requirements
   ```

### 9. Handle Routing

1. **Read routing patterns from Frontend Tech Spec**:
   - How routing is configured
   - Where routing configuration is located
   - How to add authentication guards
   - How to define route parameters

2. **Update routing configuration** following the tech spec patterns:
   - Add routes for this feature
   - Add authentication guards as specified
   - Define route parameters as needed

3. **Add TODOs for security**:
   ```
   // Example (syntax will vary by routing library):
   // TODO: [SECURITY] Add authentication guard
   // TODO: [SECURITY] Add role-based access control
   ```

### 10. Handle Shared Code

If code is needed by multiple workpackages:

1. **Identify shared code**:
   - Common components (buttons, inputs, modals, etc.)
   - Common hooks (authentication, API calls, etc.)
   - Common utilities
   - Common types

2. **Read shared code patterns from Frontend Tech Spec**:
   - Where to place shared code (shared folder, base folder, etc.)
   - How to organize shared code

3. **Create in shared location** as specified by tech spec:
   - Follow the project structure from tech spec
   - Use naming conventions from tech spec

4. **Add TODOs for external integrations**:
   ```
   // Example (syntax will vary by framework):
   // TODO: [EXTERNAL] Integrate with OAuth2 authentication
   ```

### 11. Update Progress Tracking

Update `{{CODE_GENERATION_STATUS}}`:

```json
{
  "phase": "Phase 5 - Code Generation",
  "currentStep": "5.3 - Frontend Generation",
  "workpackages": {
    "WP-{ID}": {
      "status": "completed",
      "frontend": {
        "featureCreated": true,
        "featureName": "[feature-name]",
        "componentsCount": 5,
        "pagesCount": 3,
        "servicesCount": 1,
        "storeSlicesCount": 1,
        "todosCount": 8,
        "compiles": true
      }
    }
  }
}
```

---

## TODO Marker Guidelines

**When to add TODOs**:
1. **Integration with other features**: When code needs to interact with components/services from other WPs
2. **Backend API not ready**: When frontend is ready but backend endpoint doesn't exist yet
3. **External service integration**: When code needs OAuth2, analytics, etc.
4. **Missing information**: When business spec is unclear about UI/UX requirements
5. **Future enhancements**: When spec mentions "future" or "phase 2" features

**TODO format**:
```typescript
// TODO: [CATEGORY] Description
// Categories: WP-XXX, BACKEND, EXTERNAL, MISSING-INFO, VALIDATION, SECURITY, FUTURE
```

**Examples**:
```typescript
// TODO: [WP-002] Add account selector when accounts feature exists
// TODO: [BACKEND] Verify /api/users endpoint is implemented
// TODO: [EXTERNAL] Integrate with Google Analytics
// TODO: [MISSING-INFO] Confirm pagination page size
// TODO: [VALIDATION] Add email format validation
// TODO: [SECURITY] Add role-based access control
// TODO: [FUTURE] Implement export to CSV functionality
```

---

## Verification

Before marking complete:
1. ✅ Feature module compiles without errors
2. ✅ All pages from business spec are created
3. ✅ All components are implemented (or have TODOs)
4. ✅ API services match backend endpoints
5. ✅ State management is configured
6. ✅ Routing is updated
7. ✅ TODOs are added for all integration points
8. ✅ Code follows naming conventions from tech spec

---

## End of Phase 5.3

The workpackage frontend feature is now complete and integrated into the project. Move to next workpackage or next tier.
