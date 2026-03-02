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
- **Technical Implementation Guide**: `{{TECH_SPEC_BASE_PATH}}/WP-{ID}-tech-implementation-guide-approved.md`
- **Target Specifications**: `{{TARGET_SPECIFICATION}}/` (frontend specs)
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

1. **Read Technical Implementation Guide** at `{{TECH_SPEC_BASE_PATH}}/WP-{ID}-tech-implementation-guide-approved.md`
   - Section 1: Overview (workpackage context and scope)
   - Section 3: Frontend Implementation (components, pages, state management)
   - Section 4: API Design (endpoints to call, request/response formats)
   - Section 6: Integration Points (dependencies on other workpackages)
   - Section 9: Implementation Tasks (step-by-step guidance)

2. **Read Target Frontend Specification** at `{{TARGET_SPECIFICATION}}/frontend/`
   - Project structure patterns
   - Technology stack and frameworks
   - Component patterns and conventions
   - State management approach

3. **Read Business Specification** at `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-{ID}-specification.md`
   - Chapter 2: Business Entities (what data to display/manage)
   - Chapter 4: Business Operations (what user actions to support)
   - Chapter 5: Business Processes (what workflows to implement)

### 2. Determine Feature Module Structure

Based on Technical Implementation Guide Section 3 and Target Frontend Specification, determine the feature structure:

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

From Technical Implementation Guide Section 3 and Section 4:

1. **Read type definition patterns from Technical Implementation Guide and Target Frontend Specification**:
   - How to define types/interfaces
   - Where to place type definitions (package/folder structure)
   - Naming conventions for types

2. **Read data structures**:
   - Technical Implementation Guide Section 4: API Design (request/response structures)
   - Business Specification Chapter 2: Business entities and attributes
   - Backend DTOs (to match backend API)

3. **CRITICAL - Verify API Contract Alignment**:
   
   **Before creating frontend types, verify they match the backend API response**:
   
   a. **Check Backend DTO Field Names**:
      - Read the backend DTO classes in `/Users/kerimman/carddemo_migration/output/gen_src/backend/src/main/java/com/carddemo/[domain]/web/dto/`
      - Note the exact field names (e.g., `transactionAmount` vs `amount`)
      - Note the exact nested object field names (e.g., `merchant.merchantId` vs `merchant.id`)
   
   b. **Test API Response Structure** (if backend is running):
      - Make a sample API call to verify actual response structure
      - Compare response field names with backend DTO
      - Document any discrepancies
   
   c. **Ensure Exact Field Name Match**:
      ```typescript
      // ✅ CORRECT - Matches backend DTO field names exactly
      export interface TransactionDetailResponse {
        transactionId: string;              // Backend: getTransactionId()
        transactionAmount: number;          // Backend: getTransactionAmount()
        transactionTypeCode: string;        // Backend: getTransactionTypeCode()
        merchant: {
          merchantId: string;               // Backend: getMerchantId()
          merchantName: string;             // Backend: getMerchantName()
        };
      }
      
      // ❌ WRONG - Field names don't match backend
      export interface TransactionDetailResponse {
        transactionId: string;
        amount: number;                     // Backend has transactionAmount
        typeCode: string;                   // Backend has transactionTypeCode
        merchant: {
          id: string;                       // Backend has merchantId
          name: string;                     // Backend has merchantName
        };
      }
      ```
   
   d. **Add Verification Comment**:
      ```typescript
      /**
       * Transaction Detail Response
       * 
       * VERIFIED: Field names match backend DTO
       * Backend: com.carddemo.transaction.web.dto.TransactionDetailResponse
       * Last verified: [Date]
       * 
       * @workpackage WP-003: Transaction Display
       */
      export interface TransactionDetailResponse {
        // ...
      }
      ```

4. **Create type definitions** following the implementation guide patterns:
   - Place in the location specified by tech spec
   - Match backend DTOs EXACTLY (field names, nesting structure, types)
   - Define request/response types
   - Define component prop types

5. **Add TODOs for relationships with other workpackages**:
   ```
   // Example (syntax will vary by language):
   // TODO: [WP-002] Add accounts relationship when accounts feature is implemented
   // accounts?: Account[];
   ```

**API Contract Verification Checklist**:
- [ ] Backend DTO classes reviewed for exact field names
- [ ] Frontend types match backend field names exactly
- [ ] Nested object field names match (e.g., merchant.merchantId)
- [ ] Array field names match
- [ ] Optional fields marked correctly (? in TypeScript)
- [ ] Date/timestamp field names match
- [ ] Enum field names match
- [ ] Verification comment added to type definition

### 5. Implement API Services

From Technical Implementation Guide Section 4:

1. **Read API service patterns from Technical Implementation Guide and Target Frontend Specification**:
   - How to create service classes
   - What HTTP client to use
   - How to handle request/response mapping
   - How to handle errors
   - Where to place service classes (folder structure)

2. **Read API endpoints from Technical Implementation Guide**:
   - Section 4: Exact endpoints, methods, request/response formats
   - URL structure, HTTP methods, headers

3. **Create service classes** following the implementation guide patterns:
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

From Technical Implementation Guide Section 3 and Target Frontend Specification:

1. **Read state management patterns from Technical Implementation Guide and Target Frontend Specification**:
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

From Technical Implementation Guide Section 3 and Business Specification:

1. **Read component patterns from Technical Implementation Guide and Target Frontend Specification**:
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

From Technical Implementation Guide Section 3 and Business Specification:

1. **Read page patterns from Technical Implementation Guide and Target Frontend Specification**:
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

1. **Read routing patterns from Technical Implementation Guide and Target Frontend Specification**:
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

2. **Read shared code patterns from Technical Implementation Guide and Target Frontend Specification**:
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

## Documentation and Traceability

**CRITICAL: Follow comprehensive documentation style - detailed, production-ready comments**

### Component/Class Documentation
```typescript
/**
 * [One-line description]
 * 
 * Business Context: [Detailed explanation of business purpose]
 * 
 * Business Functions:
 * - F-XXX-YYY: [Function description]
 * - F-XXX-ZZZ: [Function description]
 * 
 * Business Rules Applied:
 * - BR-XXX-YYY: [Rule description]
 * - BR-XXX-ZZZ: [Rule description]
 * 
 * Legacy Mapping:
 * - Legacy Screen: [SCREEN-NAME]
 * - Legacy Function: [Description]
 * 
 * @workpackage WP-XXX: [Workpackage name]
 * @specref [Spec file]#[Section]
 * @legacyref [SCREEN]:[section]
 */
```

### Function/Method Documentation
```typescript
/**
 * [Function description]
 * 
 * Business Function: F-XXX-YYY - [Function name]
 * 
 * Business Rules Applied:
 * - BR-XXX-YYY: [Rule description]
 * 
 * Process Flow:
 * 1. [Step 1]
 * 2. [Step 2]
 * 3. [Step 3]
 * 
 * Legacy Equivalent: [SCREEN] [section]
 * 
 * @param [parameter] [description]
 * @returns [description]
 * 
 * @specref WP-XXX#F-XXX-YYY
 * @specref WP-XXX#BR-XXX-YYY
 */
```

### Inline Code Comments
- Add inline comments referencing business rules: `// BR-XXX-YYY: [Rule description]`
- Explain complex logic with business context
- Reference legacy screens for equivalent operations

---

## Strict No-Hallucination Policy

**CRITICAL: Do not invent anything not in specifications**

1. **NEVER invent business rules** not in specifications
2. **NEVER create UI components** not defined in specifications
3. **NEVER add functionality** beyond specifications
4. **NEVER create hard-coded mock data** in production code
5. **NEVER invent external system integrations** not specified
6. **NEVER add fields to forms** not in specifications
7. **NEVER create pages** not required by business specifications
8. If uncertain about implementation, mark with TODO (see next section)

**Verification checklist** for each component:
- [ ] All functionality comes from specifications
- [ ] No invented business rules
- [ ] No hard-coded test data
- [ ] All UI components match specifications exactly
- [ ] All integrations are specified
- [ ] All form fields are from specifications
- [ ] All pages serve specified business functions

---

## Code Preservation Rules

**CRITICAL: When implementing a workpackage, preserve all existing code from previous workpackages.**

1. **NEVER delete existing code** from other workpackages
2. **NEVER delete existing files** created by previous workpackages
3. **NEVER modify code in other feature modules** unless the current workpackage explicitly requires changes to that feature
4. **Exception - Shared module**: The shared module may be modified by any workpackage as it contains shared utilities

**Modification Rules by Feature:**
- **Same feature as current workpackage**: ✅ Can modify/extend existing code
- **Different feature**: ❌ Do not modify (unless explicitly required by business spec)
- **Shared module**: ✅ Can modify/extend (shared across all workpackages)

**Examples:**
- ✅ WP-002 working on `users` feature → Can modify existing `users` feature code
- ✅ WP-002 working on `users` feature → Can add utilities to `shared` module
- ❌ WP-002 working on `users` feature → Cannot modify `authentication` feature (created by WP-001)
- ❌ WP-003 → Cannot delete components created by WP-001 or WP-002

**Implementation Strategy:**
1. Before generating code, check which features already exist
2. Only add new files or extend existing files in the current workpackage's feature
3. If cross-feature integration is needed, use feature APIs (public interfaces)
4. Document any necessary cross-feature changes with clear justification

**Verification Checklist:**
- [ ] No files deleted from previous workpackages
- [ ] No code removed from other feature modules
- [ ] Modifications to other features are justified in business spec
- [ ] Shared module changes are additive (not destructive)
- [ ] Cross-feature integration uses public APIs

---

## TODO Comments for Incomplete Implementations

**Use TODO when implementation details are missing or uncertain**

### When to Use TODO
- External system integration details are missing
- Business rule details are unclear or ambiguous
- Validation rules are not fully specified
- UI/UX requirements are uncertain
- Security implementation details are missing
- Configuration requirements are not specified
- Legacy screen logic cannot be mapped to modern patterns
- Business rules require clarification

### TODO Format
```typescript
// TODO: [CATEGORY] - [Description] - Refer to: [Source]
```

### TODO Categories
- `EXTERNAL_INTEGRATION` - Missing external system details
- `BUSINESS_RULE` - Unclear or missing business rule
- `VALIDATION` - Unspecified validation logic
- `UI_UX` - UI/UX requirements uncertainties
- `SECURITY` - Security implementation details
- `CONFIG` - Configuration requirements
- `UNMAPPABLE` - Legacy logic requiring manual review
- `CLARIFICATION` - Business rules requiring clarification

### TODO Examples
```typescript
// TODO: EXTERNAL_INTEGRATION - OAuth2 provider configuration not specified - Refer to: Business Spec WP-001 Section 3.2

// TODO: BUSINESS_RULE - Interest calculation formula unclear for edge case - Refer to: Legacy Screen CALC01

// TODO: UNMAPPABLE - Complex screen navigation logic - Refer to: LEGACY-SCREEN:456-523 - Requires manual review

// TODO: CLARIFICATION - Validation rule for account status transition needs business confirmation - Refer to: Business Spec WP-002-BR-015
```

---

### 12. Integration with Existing Application

**CRITICAL: Each workpackage must integrate seamlessly with the existing application structure**

This section ensures that new features don't exist in isolation but are properly connected to the application's navigation, layout, and user experience.

#### 12.1 Navigation Integration

**Add to Appropriate Menu**

Based on user role and feature type, add navigation links to existing menus:

**Admin Menu** (`src/pages/AdminMenuPage.tsx` or similar):
```typescript
// Add menu item for admin-only features
<MenuItem onClick={() => navigate('/admin/users/create')}>
  <PersonAddIcon />
  <span>Create User</span>
</MenuItem>
```

**User Menu** (`src/pages/MainMenuPage.tsx` or similar):
```typescript
// Add menu item for regular user features
<MenuItem onClick={() => navigate('/transactions')}>
  <ReceiptIcon />
  <span>View Transactions</span>
</MenuItem>
```

**Checklist**:
- [ ] Menu item added to appropriate menu (Admin/User)
- [ ] Icon selected (use Material-UI icons or similar)
- [ ] Navigation path matches route definition
- [ ] Menu item label is clear and action-oriented
- [ ] Menu item follows existing menu structure

#### 12.2 Routing Integration

**Update Main Router** (`src/App.tsx` or `src/routes/index.tsx`):

```typescript
// Add routes for new feature
import { CreateUserPage } from './features/users/profile/pages/CreateUserPage';
import { UpdateUserPage } from './features/users/profile/pages/UpdateUserPage';

// In router configuration
<Route path="/admin/users/create" element={<CreateUserPage />} />
<Route path="/admin/users/:userId/edit" element={<UpdateUserPage />} />
```

**Route Naming Conventions**:
- Admin routes: `/admin/[resource]/[action]`
- User routes: `/[resource]/[action]`
- Detail routes: `/[resource]/:id`
- Edit routes: `/[resource]/:id/edit`

**Checklist**:
- [ ] Routes added to main router
- [ ] Route paths follow naming conventions
- [ ] Protected routes have auth guards (if applicable)
- [ ] Route parameters defined correctly
- [ ] Lazy loading configured (if applicable)

#### 12.3 Layout Integration

**Use Consistent Page Layout**

All pages should use the same layout structure for consistency:

```typescript
import { PageLayout } from '@/shared/components/PageLayout';

export const CreateUserPage = () => {
  return (
    <PageLayout
      title="Create User"
      breadcrumbs={[
        { label: 'Admin', path: '/admin' },
        { label: 'Users', path: '/admin/users' },
        { label: 'Create', path: '/admin/users/create' }
      ]}
    >
      {/* Page content */}
    </PageLayout>
  );
};
```

**If PageLayout doesn't exist, create it in shared**:
```typescript
// src/shared/components/PageLayout.tsx
export const PageLayout = ({ title, breadcrumbs, children }) => {
  return (
    <div className="page-container">
      <header className="page-header">
        <Breadcrumbs items={breadcrumbs} />
        <h1>{title}</h1>
      </header>
      <main className="page-content">
        {children}
      </main>
    </div>
  );
};
```

**Checklist**:
- [ ] Page uses consistent layout component
- [ ] Page title is clear and descriptive
- [ ] Breadcrumbs show navigation path
- [ ] Layout matches existing pages

#### 12.4 UI/UX Consistency

**Follow UI/UX Design Guide**

Reference: `/Users/kerimman/carddemo_migration/input/target/specifications/01-FRONTEND-UIUX-GUIDE.md`

**Key Consistency Points**:

1. **Colors**: Use design system colors
   ```typescript
   // Use theme colors, not hardcoded values
   <Button color="primary">Save</Button>  // ✅ Good
   <Button style={{backgroundColor: '#1976d2'}}>Save</Button>  // ❌ Bad
   ```

2. **Spacing**: Use consistent spacing scale (8px base)
   ```typescript
   // Use spacing utilities
   <Box sx={{ p: 3, mb: 2 }}>  // ✅ Good (24px padding, 16px margin)
   <Box style={{padding: '25px'}}>  // ❌ Bad (arbitrary value)
   ```

3. **Typography**: Use theme typography
   ```typescript
   <Typography variant="h4">Title</Typography>  // ✅ Good
   <h4 style={{fontSize: '20px'}}>Title</h4>  // ❌ Bad
   ```

4. **Buttons**: Follow button hierarchy
   ```typescript
   // Primary action
   <Button variant="contained" color="primary">Save</Button>
   
   // Secondary action
   <Button variant="outlined" color="primary">Cancel</Button>
   
   // Tertiary action
   <Button variant="text">Skip</Button>
   ```

5. **Forms**: Consistent form layout
   ```typescript
   // Single column, labels above inputs
   <FormControl fullWidth sx={{ mb: 2 }}>
     <FormLabel required>User ID</FormLabel>
     <TextField {...} />
     <FormHelperText>Max 8 characters</FormHelperText>
   </FormControl>
   ```

**Checklist**:
- [ ] Uses design system colors (no hardcoded colors)
- [ ] Uses consistent spacing (8px scale)
- [ ] Uses theme typography (no inline font styles)
- [ ] Follows button hierarchy (primary/secondary/tertiary)
- [ ] Forms use consistent layout (labels above, full width)
- [ ] Error states use standard error styling
- [ ] Loading states use standard spinners
- [ ] Success feedback uses standard toasts/alerts

#### 12.5 Component Reuse

**Check for Existing Components Before Creating New Ones**

Before implementing a component, check if similar functionality exists:

**Common Reusable Components** (should be in `src/shared/components/`):
- `Button` - Standard button with variants
- `Input` / `TextField` - Form inputs
- `Select` / `Dropdown` - Dropdowns
- `Modal` / `Dialog` - Modals and dialogs
- `Alert` / `Toast` - Notifications
- `Card` - Content cards
- `Table` - Data tables
- `Pagination` - Pagination controls
- `Breadcrumbs` - Navigation breadcrumbs
- `ErrorMessage` - Error display
- `LoadingSpinner` - Loading indicators
- `ConfirmDialog` - Confirmation dialogs

**When to Create New Component**:
- ✅ Component is specific to this feature (e.g., `UserProfileCard`)
- ✅ Component is complex and reusable (e.g., `DataTable`)
- ❌ Component is a simple wrapper around existing component
- ❌ Component duplicates existing shared component

**When to Update Shared Component**:
- ✅ Adding a new variant to existing component
- ✅ Adding optional prop to existing component
- ✅ Fixing bug in existing component
- ❌ Changing behavior that breaks other features

**Checklist**:
- [ ] Checked `src/shared/components/` for existing components
- [ ] Reused existing components where possible
- [ ] Created new shared components for reusable functionality
- [ ] Feature-specific components in feature folder
- [ ] Shared components properly exported from shared module

#### 12.6 State Management Integration

**Connect to Global State (if applicable)**

If using global state management (Redux, Zustand, Context):

```typescript
// Use existing auth state
import { useAuth } from '@/shared/hooks/useAuth';

export const CreateUserPage = () => {
  const { user, isAdmin } = useAuth();
  
  if (!isAdmin) {
    return <Navigate to="/unauthorized" />;
  }
  
  // ...
};
```

**Checklist**:
- [ ] Uses existing auth state for user info
- [ ] Uses existing global state where applicable
- [ ] Doesn't duplicate state that exists globally
- [ ] Feature state is local to feature (not global)

#### 12.7 API Integration

**Use Consistent API Client**

All API calls should use the same HTTP client configuration:

```typescript
// Use shared API client
import { apiClient } from '@/shared/services/apiClient';

export const userService = {
  createUser: async (data: CreateUserRequest) => {
    return apiClient.post<CreateUserResponse>('/api/v1/users', data);
  }
};
```

**If apiClient doesn't exist, create it**:
```typescript
// src/shared/services/apiClient.ts
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8080',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add interceptors for auth, error handling, etc.
apiClient.interceptors.request.use(/* ... */);
apiClient.interceptors.response.use(/* ... */);
```

**Checklist**:
- [ ] Uses shared API client (not raw axios/fetch)
- [ ] API base URL from environment variable
- [ ] Error handling consistent across all API calls
- [ ] Loading states handled consistently
- [ ] Auth tokens added via interceptor (if applicable)

#### 12.8 Error Handling Integration

**Use Consistent Error Display**

All errors should be displayed consistently:

```typescript
import { useToast } from '@/shared/hooks/useToast';

export const CreateUserForm = () => {
  const { showError, showSuccess } = useToast();
  
  const handleSubmit = async (data) => {
    try {
      await userService.createUser(data);
      showSuccess('User created successfully');
    } catch (error) {
      showError(error.message || 'Failed to create user');
    }
  };
};
```

**Checklist**:
- [ ] Uses shared toast/notification system
- [ ] Error messages are user-friendly
- [ ] Success messages confirm action
- [ ] Form validation errors shown inline
- [ ] API errors shown as toasts/alerts

#### 12.9 Accessibility Integration

**Maintain Accessibility Standards**

Ensure new features maintain the same accessibility level as existing features:

```typescript
// Keyboard navigation
<Button onClick={handleSave} onKeyDown={(e) => e.key === 'Enter' && handleSave()}>
  Save
</Button>

// Screen reader labels
<IconButton aria-label="Delete user" onClick={handleDelete}>
  <DeleteIcon />
</IconButton>

// Focus management
useEffect(() => {
  if (error) {
    errorRef.current?.focus();
  }
}, [error]);
```

**Checklist**:
- [ ] All interactive elements keyboard accessible
- [ ] All icons have aria-labels
- [ ] Form inputs have labels (visible or aria-label)
- [ ] Error messages announced to screen readers
- [ ] Focus management for modals/dialogs
- [ ] Color contrast meets WCAG AA standards

#### 12.10 Testing Integration

**Ensure Feature is Testable**

While unit tests are in Phase 5.5, ensure code is structured for testing:

```typescript
// Separate business logic from UI
export const validateUserId = (userId: string): ValidationResult => {
  if (!userId) return { valid: false, error: 'User ID required' };
  if (userId.length > 8) return { valid: false, error: 'Max 8 characters' };
  return { valid: true };
};

// Use in component
const handleChange = (value: string) => {
  const result = validateUserId(value);
  setError(result.error);
};
```

**Checklist**:
- [ ] Business logic separated from UI components
- [ ] Components accept props (not hardcoded data)
- [ ] API calls in separate service layer
- [ ] Validation logic is pure functions
- [ ] State management is testable

#### 12.11 Documentation Integration

**Update Application Documentation**

Add feature documentation to help other developers:

**Update README** (if feature-level README exists):
```markdown
## Features

### User Management (WP-001, WP-002, WP-004, WP-005)
- **Create User** (WP-002): Admin can create new users
  - Route: `/admin/users/create`
  - Component: `CreateUserPage`
  - API: `POST /api/v1/users`
```

**Add Feature README** (in feature folder):
```markdown
# User Management Feature

## Overview
User management functionality including create, update, delete operations.

## Workpackages
- WP-001: Authentication
- WP-002: Create User
- WP-004: Delete User
- WP-005: Update User

## Routes
- `/login` - Login page
- `/admin/users/create` - Create user
- `/admin/users/:id/edit` - Update user
- `/admin/users/:id/delete` - Delete user

## Components
- `LoginForm` - User login
- `CreateUserForm` - Create user form
- `UpdateUserForm` - Update user form
- `DeleteUserDialog` - Delete confirmation

## API Services
- `authService` - Authentication operations
- `userManagementService` - User CRUD operations
```

**Checklist**:
- [ ] Feature documented in README
- [ ] Routes documented
- [ ] Components documented
- [ ] API services documented
- [ ] Integration points documented

#### 12.12 Integration Verification Checklist

Before marking workpackage complete, verify all integration points:

**Navigation**:
- [ ] Menu items added to appropriate menus
- [ ] Navigation paths work correctly
- [ ] Breadcrumbs show correct path
- [ ] Back buttons work correctly

**Routing**:
- [ ] Routes added to main router
- [ ] Route paths follow conventions
- [ ] Protected routes have auth guards
- [ ] Route parameters work correctly

**UI/UX**:
- [ ] Follows design system colors
- [ ] Uses consistent spacing
- [ ] Uses theme typography
- [ ] Follows button hierarchy
- [ ] Forms use consistent layout
- [ ] Matches look & feel of existing pages

**Components**:
- [ ] Reuses existing shared components
- [ ] New shared components properly exported
- [ ] Feature-specific components in feature folder
- [ ] No duplicate components

**State Management**:
- [ ] Uses existing global state
- [ ] Doesn't duplicate state
- [ ] Feature state is local

**API Integration**:
- [ ] Uses shared API client
- [ ] Error handling consistent
- [ ] Loading states consistent
- [ ] Auth tokens handled correctly

**Accessibility**:
- [ ] Keyboard accessible
- [ ] Screen reader compatible
- [ ] Focus management correct
- [ ] Color contrast sufficient

**Documentation**:
- [ ] Feature documented
- [ ] Routes documented
- [ ] Integration points documented

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
