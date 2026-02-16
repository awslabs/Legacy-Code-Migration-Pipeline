# Phase 4.2: Frontend Code Generation

---

## Orchestration Information

**Phase**: Phase 4 - Code Generation
**Step**: Step 4.2 - Frontend Code Generation
**Team Supervisor**: code_generation_team_supervisor
**Assigned Agent**: code_generation_specialist_frontend
**Task File Name**: {{TASKS_BASE_PATH}}/phase_4.2_frontend_generation.md

### Expected Deliverables

1. **UI Components Implementation**
   - Location: {{CODE_GENERATION_FRONTEND_OUTPUT}}/wp-{ID}/components/
   - Description: Reusable UI components for the workpackage
   - Includes: Form components, display components, layout components

2. **Page Components Implementation**
   - Location: {{CODE_GENERATION_FRONTEND_OUTPUT}}/wp-{ID}/pages/
   - Description: Page-level components implementing user flows
   - Includes: List pages, detail pages, form pages

3. **State Management Implementation**
   - Location: {{CODE_GENERATION_FRONTEND_OUTPUT}}/wp-{ID}/store/
   - Description: State management for workpackage data
   - Includes: State slices, actions, selectors

4. **API Integration Implementation**
   - Location: {{CODE_GENERATION_FRONTEND_OUTPUT}}/wp-{ID}/services/
   - Description: API client services for backend integration
   - Includes: API service classes, request/response types

5. **Routing Configuration**
   - Location: {{CODE_GENERATION_FRONTEND_OUTPUT}}/wp-{ID}/routes/
   - Description: Route definitions for workpackage pages
   - Includes: Route configuration, navigation guards

6. **Progress Tracking Update**
   - File: {{CODE_GENERATION_STATUS}}
   - Description: Updated progress with frontend completion for this workpackage

7. **Error Reports** (if applicable)
   - File: {{CODE_GENERATION_ERRORS}}
   - Description: Documentation of issues encountered during generation

### Success Criteria
- [ ] All UI components implemented with proper accessibility
- [ ] All pages implemented matching business requirements
- [ ] State management properly configured
- [ ] API integration working with backend endpoints
- [ ] Routing configured correctly
- [ ] Code compiles without errors
- [ ] All UI requirements traceable to business specification
- [ ] Accessibility requirements met (WCAG 2.1 Level AA)
- [ ] Responsive design implemented
- [ ] Form validation implemented
- [ ] Error handling implemented
- [ ] Progress tracking updated with frontend completion
- [ ] All deliverables produced at specified paths
- [ ] Ready for Phase 4.3 (Batch) or next workpackage

---

## Context

### Workpackage Context (Provided at Runtime)
- **Workpackage ID**: WP-{ID} (e.g., WP-001)
- **Workpackage Name**: [Name from workpackage planning]
- **Workpackage Description**: [Description from business specification]

### Input Locations
- **Business specification**: `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-{ID}-specification.md`
- **Backend API**: `{{CODE_GENERATION_BACKEND_OUTPUT}}/wp-{ID}/` (from Phase 4.1)
- **Target frontend specification**: `{{TARGET_SPECIFICATION}}/01-FRONTEND-SPECIFICATION.md`
- **Frontend sample code**: `{{TARGET_SAMPLE_CODE}}/frontend/`
- **Project structure**: `{{CODE_GENERATION_FRONTEND_OUTPUT}}/` (from Phase 4.0)

### Output Locations
- **Frontend code**: `{{CODE_GENERATION_FRONTEND_OUTPUT}}/wp-{ID}/`
- **Progress tracking**: `{{CODE_GENERATION_STATUS}}`
- **Error reports**: `{{CODE_GENERATION_ERRORS}}`

### Previous Phase Artifacts
- **From Phase 4.0**: Project structure, build configuration, configuration templates
- **From Phase 4.1**: Backend API endpoints, DTOs, domain model
- **From Phase 3**: Business specification with detailed requirements

---

## Objective

Implement the frontend tier for the specified workpackage, translating business requirements from the business specification into working frontend code that follows the target frontend specification's architecture, patterns, and conventions. Integrate with the backend API implemented in Phase 4.1.

**CRITICAL**: This phase implements ONE workpackage only. Focus exclusively on the UI requirements, user flows, and features defined in the workpackage's business specification. Do not implement functionality from other workpackages.

---

## Instructions

### 1. Preparation

#### 1.1 Read Business Specification
1. Open and read `{{BUSINESS_SPECIFICATION_BASE_PATH}}/WP-{ID}-specification.md`
2. Extract key information:
   - **User Interface Requirements**: UI elements, layouts, forms
   - **User Flows**: Navigation paths, user interactions
   - **Data Display Requirements**: Tables, lists, cards, details
   - **Form Requirements**: Input fields, validation, submission
   - **Business Rules**: Client-side validation, business logic
   - **Accessibility Requirements**: ARIA labels, keyboard navigation, screen reader support

3. Identify implementation scope:
   - Which pages need to be created
   - Which components need to be built
   - Which user flows need to be implemented
   - Which API endpoints need to be called
   - Which validations need to be enforced

#### 1.2 Read Target Frontend Specification
1. Open and read `{{TARGET_SPECIFICATION}}/01-FRONTEND-SPECIFICATION.md`
2. Extract implementation guidance:
   - **Framework**: React, Vue, Angular, etc.
   - **UI Library**: Material-UI, Ant Design, Bootstrap, etc.
   - **State Management**: Redux, Zustand, Pinia, NgRx, etc.
   - **Routing**: React Router, Vue Router, Angular Router
   - **API Client**: Axios, Fetch API, etc.
   - **Form Handling**: React Hook Form, Formik, VeeValidate, etc.
   - **Component Patterns**: Functional components, composition patterns
   - **Naming Conventions**: File, component, function naming rules
   - **Styling Approach**: CSS Modules, Styled Components, Tailwind, etc.
   - **Accessibility Standards**: WCAG 2.1 Level AA requirements
   - **Responsive Design**: Breakpoints, mobile-first approach

3. Review sample code at `{{TARGET_SAMPLE_CODE}}/frontend/` for:
   - Component implementation examples
   - Page structure examples
   - State management patterns
   - API integration patterns
   - Form handling examples
   - Routing configuration examples

#### 1.3 Review Backend API
1. Review backend code at `{{CODE_GENERATION_BACKEND_OUTPUT}}/wp-{ID}/`
2. Identify available API endpoints:
   - Controllers and their endpoints
   - Request/response DTOs
   - HTTP methods and status codes
   - Query parameters and path variables

3. Document API endpoints for integration:
   - List all endpoints with methods and paths
   - Note request/response formats
   - Identify authentication requirements

### 2. API Integration Implementation

#### 2.1 Create Type Definitions
1. **Create Type/Interface Definitions**
   - Location: `{{CODE_GENERATION_FRONTEND_OUTPUT}}/wp-{ID}/types/[EntityName].ts`
   - Map backend DTOs to TypeScript interfaces
   - Follow naming conventions from frontend specification

**Example Structure** (React/TypeScript):
```typescript
// types/EntityName.ts
export interface EntityName {
  id: number;
  attribute: string;
  createdAt: string;
}

export interface EntityNameRequest {
  attribute: string;
}

export interface EntityNameResponse {
  id: number;
  attribute: string;
  createdAt: string;
}

export interface EntityNameListResponse {
  items: EntityNameResponse[];
  total: number;
}
```

#### 2.2 Create API Service Classes
1. **Create API Service**
   - Location: `{{CODE_GENERATION_FRONTEND_OUTPUT}}/wp-{ID}/services/[EntityName]Service.ts`
   - Implement methods for each backend endpoint
   - Use API client from frontend specification (Axios, Fetch, etc.)
   - Handle errors appropriately
   - Follow service patterns from frontend specification

**Example Structure** (React/TypeScript with Axios):
```typescript
// services/EntityNameService.ts
import axios from 'axios';
import { EntityName, EntityNameRequest, EntityNameResponse } from '../types/EntityName';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || '/api/v1';

export class EntityNameService {
  
  async getAll(): Promise<EntityNameResponse[]> {
    const response = await axios.get(`${API_BASE_URL}/entity-names`);
    return response.data;
  }
  
  async getById(id: number): Promise<EntityNameResponse> {
    const response = await axios.get(`${API_BASE_URL}/entity-names/${id}`);
    return response.data;
  }
  
  async create(data: EntityNameRequest): Promise<EntityNameResponse> {
    const response = await axios.post(`${API_BASE_URL}/entity-names`, data);
    return response.data;
  }
  
  async update(id: number, data: EntityNameRequest): Promise<EntityNameResponse> {
    const response = await axios.put(`${API_BASE_URL}/entity-names/${id}`, data);
    return response.data;
  }
  
  async delete(id: number): Promise<void> {
    await axios.delete(`${API_BASE_URL}/entity-names/${id}`);
  }
  
  // Business-specific methods
  async performBusinessOperation(id: number, params: BusinessParams): Promise<void> {
    await axios.post(`${API_BASE_URL}/entity-names/${id}/business-operation`, params);
  }
}

export const entityNameService = new EntityNameService();
```

#### 2.3 Validate API Integration
- [ ] All backend endpoints have corresponding service methods
- [ ] Request/response types match backend DTOs
- [ ] Error handling is implemented
- [ ] API base URL is configurable
- [ ] Service follows frontend specification patterns

### 3. State Management Implementation

#### 3.1 Identify State Requirements
From the business specification, identify:
- What data needs to be stored in state
- What operations modify state (create, update, delete)
- What loading/error states are needed
- What derived/computed state is needed

#### 3.2 Implement State Management
Based on the state management solution from frontend specification:

**For Redux/Redux Toolkit** (React):
```typescript
// store/entityNameSlice.ts
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { EntityNameResponse } from '../types/EntityName';
import { entityNameService } from '../services/EntityNameService';

interface EntityNameState {
  items: EntityNameResponse[];
  selectedItem: EntityNameResponse | null;
  loading: boolean;
  error: string | null;
}

const initialState: EntityNameState = {
  items: [],
  selectedItem: null,
  loading: false,
  error: null,
};

export const fetchEntityNames = createAsyncThunk(
  'entityName/fetchAll',
  async () => {
    return await entityNameService.getAll();
  }
);

export const fetchEntityNameById = createAsyncThunk(
  'entityName/fetchById',
  async (id: number) => {
    return await entityNameService.getById(id);
  }
);

export const createEntityName = createAsyncThunk(
  'entityName/create',
  async (data: EntityNameRequest) => {
    return await entityNameService.create(data);
  }
);

const entityNameSlice = createSlice({
  name: 'entityName',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    clearSelected: (state) => {
      state.selectedItem = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchEntityNames.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchEntityNames.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchEntityNames.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch items';
      });
  },
});

export const { clearError, clearSelected } = entityNameSlice.actions;
export default entityNameSlice.reducer;
```

**For Zustand** (React):
```typescript
// store/entityNameStore.ts
import { create } from 'zustand';
import { EntityNameResponse, EntityNameRequest } from '../types/EntityName';
import { entityNameService } from '../services/EntityNameService';

interface EntityNameStore {
  items: EntityNameResponse[];
  selectedItem: EntityNameResponse | null;
  loading: boolean;
  error: string | null;
  
  fetchAll: () => Promise<void>;
  fetchById: (id: number) => Promise<void>;
  create: (data: EntityNameRequest) => Promise<void>;
  update: (id: number, data: EntityNameRequest) => Promise<void>;
  delete: (id: number) => Promise<void>;
  clearError: () => void;
}

export const useEntityNameStore = create<EntityNameStore>((set) => ({
  items: [],
  selectedItem: null,
  loading: false,
  error: null,
  
  fetchAll: async () => {
    set({ loading: true, error: null });
    try {
      const items = await entityNameService.getAll();
      set({ items, loading: false });
    } catch (error) {
      set({ error: 'Failed to fetch items', loading: false });
    }
  },
  
  fetchById: async (id: number) => {
    set({ loading: true, error: null });
    try {
      const selectedItem = await entityNameService.getById(id);
      set({ selectedItem, loading: false });
    } catch (error) {
      set({ error: 'Failed to fetch item', loading: false });
    }
  },
  
  create: async (data: EntityNameRequest) => {
    set({ loading: true, error: null });
    try {
      await entityNameService.create(data);
      set({ loading: false });
    } catch (error) {
      set({ error: 'Failed to create item', loading: false });
    }
  },
  
  clearError: () => set({ error: null }),
}));
```

#### 3.3 Validate State Management
- [ ] State structure matches application needs
- [ ] All CRUD operations are implemented
- [ ] Loading and error states are handled
- [ ] State management follows frontend specification patterns

### 4. UI Components Implementation

#### 4.1 Identify Component Requirements
From the business specification, identify:
- What reusable components are needed
- What forms are needed
- What display components are needed (tables, cards, lists)
- What layout components are needed

#### 4.2 Create Form Components
For each form in the business specification:

1. **Create Form Component**
   - Location: `{{CODE_GENERATION_FRONTEND_OUTPUT}}/wp-{ID}/components/[EntityName]Form.tsx`
   - Implement form fields based on business specification
   - Add validation based on business rules
   - Handle form submission
   - Follow form handling patterns from frontend specification

**Example Structure** (React with React Hook Form):
```typescript
// components/EntityNameForm.tsx
import React from 'react';
import { useForm } from 'react-hook-form';
import { EntityNameRequest } from '../types/EntityName';

interface EntityNameFormProps {
  initialData?: EntityNameRequest;
  onSubmit: (data: EntityNameRequest) => Promise<void>;
  onCancel: () => void;
}

export const EntityNameForm: React.FC<EntityNameFormProps> = ({
  initialData,
  onSubmit,
  onCancel,
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<EntityNameRequest>({
    defaultValues: initialData,
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} aria-label="Entity name form">
      <div className="form-group">
        <label htmlFor="attribute">
          Attribute <span aria-label="required">*</span>
        </label>
        <input
          id="attribute"
          type="text"
          {...register('attribute', {
            required: 'Attribute is required',
            maxLength: {
              value: 100,
              message: 'Attribute must not exceed 100 characters',
            },
          })}
          aria-invalid={errors.attribute ? 'true' : 'false'}
          aria-describedby={errors.attribute ? 'attribute-error' : undefined}
        />
        {errors.attribute && (
          <span id="attribute-error" className="error" role="alert">
            {errors.attribute.message}
          </span>
        )}
      </div>

      <div className="form-actions">
        <button
          type="submit"
          disabled={isSubmitting}
          aria-busy={isSubmitting}
        >
          {isSubmitting ? 'Saving...' : 'Save'}
        </button>
        <button type="button" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </form>
  );
};
```

#### 4.3 Create Display Components
For each data display requirement:

1. **Create List/Table Component**
   - Location: `{{CODE_GENERATION_FRONTEND_OUTPUT}}/wp-{ID}/components/[EntityName]List.tsx`
   - Display data in appropriate format (table, cards, list)
   - Add sorting, filtering if required
   - Add actions (view, edit, delete)
   - Ensure accessibility (proper table markup, ARIA labels)

**Example Structure** (React):
```typescript
// components/EntityNameList.tsx
import React from 'react';
import { EntityNameResponse } from '../types/EntityName';

interface EntityNameListProps {
  items: EntityNameResponse[];
  onView: (id: number) => void;
  onEdit: (id: number) => void;
  onDelete: (id: number) => void;
}

export const EntityNameList: React.FC<EntityNameListProps> = ({
  items,
  onView,
  onEdit,
  onDelete,
}) => {
  return (
    <table role="table" aria-label="Entity names list">
      <thead>
        <tr>
          <th scope="col">ID</th>
          <th scope="col">Attribute</th>
          <th scope="col">Created At</th>
          <th scope="col">Actions</th>
        </tr>
      </thead>
      <tbody>
        {items.map((item) => (
          <tr key={item.id}>
            <td>{item.id}</td>
            <td>{item.attribute}</td>
            <td>{new Date(item.createdAt).toLocaleDateString()}</td>
            <td>
              <button
                onClick={() => onView(item.id)}
                aria-label={`View ${item.attribute}`}
              >
                View
              </button>
              <button
                onClick={() => onEdit(item.id)}
                aria-label={`Edit ${item.attribute}`}
              >
                Edit
              </button>
              <button
                onClick={() => onDelete(item.id)}
                aria-label={`Delete ${item.attribute}`}
              >
                Delete
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};
```

2. **Create Detail Component**
   - Location: `{{CODE_GENERATION_FRONTEND_OUTPUT}}/wp-{ID}/components/[EntityName]Detail.tsx`
   - Display detailed information
   - Add actions if needed
   - Ensure accessibility

#### 4.4 Validate Components
- [ ] All required components are implemented
- [ ] Components follow frontend specification patterns
- [ ] Accessibility requirements met (ARIA labels, keyboard navigation)
- [ ] Form validation matches business rules
- [ ] Components are reusable and well-structured

### 5. Page Components Implementation

#### 5.1 Identify Page Requirements
From the business specification, identify:
- What pages are needed (list, detail, create, edit)
- What user flows connect these pages
- What data each page needs
- What actions are available on each page

#### 5.2 Create List Page
1. **Create List Page Component**
   - Location: `{{CODE_GENERATION_FRONTEND_OUTPUT}}/wp-{ID}/pages/[EntityName]ListPage.tsx`
   - Fetch and display list of items
   - Integrate with state management
   - Add navigation to detail/create/edit pages
   - Handle loading and error states

**Example Structure** (React):
```typescript
// pages/EntityNameListPage.tsx
import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useEntityNameStore } from '../store/entityNameStore';
import { EntityNameList } from '../components/EntityNameList';

export const EntityNameListPage: React.FC = () => {
  const navigate = useNavigate();
  const { items, loading, error, fetchAll, delete: deleteItem } = useEntityNameStore();

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  const handleView = (id: number) => {
    navigate(`/entity-names/${id}`);
  };

  const handleEdit = (id: number) => {
    navigate(`/entity-names/${id}/edit`);
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this item?')) {
      await deleteItem(id);
      await fetchAll();
    }
  };

  const handleCreate = () => {
    navigate('/entity-names/new');
  };

  if (loading) {
    return <div role="status" aria-live="polite">Loading...</div>;
  }

  if (error) {
    return <div role="alert" aria-live="assertive">Error: {error}</div>;
  }

  return (
    <div>
      <h1>Entity Names</h1>
      <button onClick={handleCreate}>Create New</button>
      <EntityNameList
        items={items}
        onView={handleView}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
    </div>
  );
};
```

#### 5.3 Create Detail Page
1. **Create Detail Page Component**
   - Location: `{{CODE_GENERATION_FRONTEND_OUTPUT}}/wp-{ID}/pages/[EntityName]DetailPage.tsx`
   - Fetch and display item details
   - Add actions (edit, delete, back)
   - Handle loading and error states

**Example Structure** (React):
```typescript
// pages/EntityNameDetailPage.tsx
import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useEntityNameStore } from '../store/entityNameStore';
import { EntityNameDetail } from '../components/EntityNameDetail';

export const EntityNameDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { selectedItem, loading, error, fetchById, delete: deleteItem } = useEntityNameStore();

  useEffect(() => {
    if (id) {
      fetchById(parseInt(id));
    }
  }, [id, fetchById]);

  const handleEdit = () => {
    navigate(`/entity-names/${id}/edit`);
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this item?')) {
      await deleteItem(parseInt(id!));
      navigate('/entity-names');
    }
  };

  const handleBack = () => {
    navigate('/entity-names');
  };

  if (loading) {
    return <div role="status" aria-live="polite">Loading...</div>;
  }

  if (error) {
    return <div role="alert" aria-live="assertive">Error: {error}</div>;
  }

  if (!selectedItem) {
    return <div>Item not found</div>;
  }

  return (
    <div>
      <h1>Entity Name Details</h1>
      <EntityNameDetail item={selectedItem} />
      <div>
        <button onClick={handleEdit}>Edit</button>
        <button onClick={handleDelete}>Delete</button>
        <button onClick={handleBack}>Back to List</button>
      </div>
    </div>
  );
};
```

#### 5.4 Create Form Pages (Create/Edit)
1. **Create Form Page Component**
   - Location: `{{CODE_GENERATION_FRONTEND_OUTPUT}}/wp-{ID}/pages/[EntityName]FormPage.tsx`
   - Handle both create and edit modes
   - Fetch existing data for edit mode
   - Submit form data
   - Navigate on success

**Example Structure** (React):
```typescript
// pages/EntityNameFormPage.tsx
import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useEntityNameStore } from '../store/entityNameStore';
import { EntityNameForm } from '../components/EntityNameForm';
import { EntityNameRequest } from '../types/EntityName';

export const EntityNameFormPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { selectedItem, loading, fetchById, create, update } = useEntityNameStore();
  
  const isEditMode = !!id;

  useEffect(() => {
    if (isEditMode && id) {
      fetchById(parseInt(id));
    }
  }, [id, isEditMode, fetchById]);

  const handleSubmit = async (data: EntityNameRequest) => {
    try {
      if (isEditMode && id) {
        await update(parseInt(id), data);
      } else {
        await create(data);
      }
      navigate('/entity-names');
    } catch (error) {
      console.error('Failed to save:', error);
    }
  };

  const handleCancel = () => {
    navigate('/entity-names');
  };

  if (isEditMode && loading) {
    return <div role="status" aria-live="polite">Loading...</div>;
  }

  return (
    <div>
      <h1>{isEditMode ? 'Edit' : 'Create'} Entity Name</h1>
      <EntityNameForm
        initialData={isEditMode ? selectedItem : undefined}
        onSubmit={handleSubmit}
        onCancel={handleCancel}
      />
    </div>
  );
};
```

#### 5.5 Validate Pages
- [ ] All required pages are implemented
- [ ] Pages integrate with state management correctly
- [ ] Navigation between pages works
- [ ] Loading and error states are handled
- [ ] Pages follow frontend specification patterns

### 6. Routing Configuration

#### 6.1 Create Route Definitions
1. **Create Routes Configuration**
   - Location: `{{CODE_GENERATION_FRONTEND_OUTPUT}}/wp-{ID}/routes/index.tsx`
   - Define routes for all pages
   - Follow routing patterns from frontend specification

**Example Structure** (React Router):
```typescript
// routes/index.tsx
import React from 'react';
import { RouteObject } from 'react-router-dom';
import { EntityNameListPage } from '../pages/EntityNameListPage';
import { EntityNameDetailPage } from '../pages/EntityNameDetailPage';
import { EntityNameFormPage } from '../pages/EntityNameFormPage';

export const entityNameRoutes: RouteObject[] = [
  {
    path: '/entity-names',
    children: [
      {
        index: true,
        element: <EntityNameListPage />,
      },
      {
        path: 'new',
        element: <EntityNameFormPage />,
      },
      {
        path: ':id',
        element: <EntityNameDetailPage />,
      },
      {
        path: ':id/edit',
        element: <EntityNameFormPage />,
      },
    ],
  },
];
```

#### 6.2 Validate Routing
- [ ] All pages have routes defined
- [ ] Route paths follow frontend specification conventions
- [ ] Navigation between routes works correctly
- [ ] Route parameters are handled correctly

### 7. Accessibility Implementation

#### 7.1 Semantic HTML
- Use semantic HTML elements (header, nav, main, section, article, footer)
- Use proper heading hierarchy (h1, h2, h3)
- Use lists (ul, ol) for list content
- Use tables for tabular data with proper markup

#### 7.2 ARIA Attributes
- Add ARIA labels to interactive elements
- Add ARIA roles where semantic HTML is insufficient
- Add ARIA live regions for dynamic content
- Add ARIA states (aria-expanded, aria-selected, etc.)

#### 7.3 Keyboard Navigation
- Ensure all interactive elements are keyboard accessible
- Implement proper focus management
- Add keyboard shortcuts where appropriate
- Ensure logical tab order

#### 7.4 Form Accessibility
- Associate labels with form inputs
- Add required field indicators
- Add error messages with aria-describedby
- Add aria-invalid for invalid fields

#### 7.5 Validate Accessibility
- [ ] All interactive elements have accessible names
- [ ] Form inputs have associated labels
- [ ] Error messages are announced to screen readers
- [ ] Keyboard navigation works throughout
- [ ] Focus indicators are visible
- [ ] Color contrast meets WCAG 2.1 Level AA

### 8. Responsive Design Implementation

#### 8.1 Implement Responsive Layouts
- Use responsive units (rem, em, %, vw, vh)
- Implement mobile-first approach
- Use CSS Grid or Flexbox for layouts
- Follow breakpoints from frontend specification

#### 8.2 Implement Media Queries
- Add breakpoints for mobile, tablet, desktop
- Adjust layouts for different screen sizes
- Hide/show elements based on screen size
- Adjust font sizes for readability

#### 8.3 Validate Responsive Design
- [ ] Layout works on mobile devices
- [ ] Layout works on tablets
- [ ] Layout works on desktop
- [ ] No horizontal scrolling on small screens
- [ ] Touch targets are appropriately sized

### 9. Error Handling and Validation

#### 9.1 Client-Side Validation
- Implement validation rules from business specification
- Add real-time validation feedback
- Display validation errors clearly
- Prevent form submission with invalid data

#### 9.2 API Error Handling
- Handle network errors gracefully
- Display user-friendly error messages
- Provide retry mechanisms where appropriate
- Log errors for debugging

#### 9.3 Validate Error Handling
- [ ] All validation rules are implemented
- [ ] Error messages are clear and helpful
- [ ] API errors are handled gracefully
- [ ] Users can recover from errors

### 10. Code Quality and Best Practices

#### 10.1 Code Organization
- [ ] Code is organized by feature (pages, components, services, store)
- [ ] File structure follows frontend specification
- [ ] No circular dependencies
- [ ] Proper separation of concerns

#### 10.2 Naming Conventions
- [ ] Component names follow frontend specification conventions
- [ ] File names match component names
- [ ] Function names are descriptive
- [ ] Variable names are meaningful

#### 10.3 Documentation
- [ ] Components have JSDoc comments
- [ ] Complex logic has comments
- [ ] Props are documented with TypeScript types
- [ ] README includes component usage examples

#### 10.4 Code Style
- [ ] Code follows frontend specification style guide
- [ ] Consistent indentation and formatting
- [ ] No unused imports
- [ ] No console.log statements in production code

### 11. Compilation and Verification

#### 11.1 Compile Code
1. Navigate to frontend project root
2. Run build command:
   - npm: `npm run build`
   - yarn: `yarn build`
3. Verify no compilation errors

#### 11.2 Verify Implementation
- [ ] All components compile
- [ ] All pages compile
- [ ] All services compile
- [ ] No TypeScript errors
- [ ] No linting errors (or acceptable warnings only)

#### 11.3 Verify UI Requirements
- [ ] All UI requirements from specification are implemented
- [ ] User flows work as expected
- [ ] Forms submit correctly
- [ ] Data displays correctly
- [ ] Navigation works correctly

#### 11.4 Verify Integration
- [ ] API calls work correctly
- [ ] Data is fetched and displayed
- [ ] Create/update/delete operations work
- [ ] Error responses are handled

### 12. Update Progress Tracking

#### 12.1 Read Current Progress
1. Read `{{CODE_GENERATION_STATUS}}`
2. Find workpackage entry for WP-{ID}
3. Update frontend status

#### 12.2 Update Frontend Status
Update the workpackage entry:
```json
{
  "workpackageId": "WP-{ID}",
  "workpackageName": "[Name]",
  "status": "in_progress",
  "tiersNeeded": ["backend", "frontend"],
  "tiersCompleted": ["backend", "frontend"],
  "backend": {
    "status": "completed",
    "outputLocation": "{{CODE_GENERATION_BACKEND_OUTPUT}}/wp-{ID}",
    "completedDate": "2026-02-16T14:30:00Z"
  },
  "frontend": {
    "status": "completed",
    "outputLocation": "{{CODE_GENERATION_FRONTEND_OUTPUT}}/wp-{ID}",
    "completedDate": "[ISO 8601 timestamp]",
    "components": {
      "pages": [count],
      "components": [count],
      "services": [count]
    }
  },
  "batch": null,
  "completedDate": "[ISO 8601 timestamp if all tiers complete]"
}
```

#### 12.3 Save Progress
1. Write updated progress to `{{CODE_GENERATION_STATUS}}`
2. Update lastUpdated timestamp
3. Verify file is valid JSON

### 13. Error Handling and Recovery

#### 13.1 Common Error Scenarios

1. **Missing Business Specification**
   - Detection: Business specification file not found
   - Recovery: Cannot proceed without specification
   - Escalation: Escalate to supervisor - critical blocker

2. **Missing Backend API**
   - Detection: Backend code not found at expected location
   - Recovery: Verify Phase 4.1 completed successfully
   - Escalation: If backend is incomplete, escalate

3. **Compilation Errors**
   - Detection: Code doesn't compile
   - Recovery: Fix syntax errors, missing imports, type mismatches
   - Escalation: If errors persist after fixes, escalate

4. **Ambiguous UI Requirements**
   - Detection: UI requirement is unclear or contradictory
   - Recovery: Document ambiguity in {{CODE_GENERATION_ERRORS}}
   - Escalation: Request clarification from supervisor

5. **API Integration Issues**
   - Detection: API endpoints don't match backend implementation
   - Recovery: Review backend code and adjust service calls
   - Escalation: If backend API is incorrect, escalate

#### 13.2 Error Reporting
Document all errors in `{{CODE_GENERATION_ERRORS}}`:
```json
{
  "phase": "4.2",
  "workpackageId": "WP-{ID}",
  "timestamp": "[ISO 8601]",
  "errorType": "[Error category]",
  "description": "[What went wrong]",
  "uiRequirement": "[Related UI requirement if applicable]",
  "impact": "[How this affects implementation]",
  "recoveryAction": "[What was done]",
  "status": "open|resolved",
  "requiresEscalation": true|false
}
```

### 14. Completion and Handoff

#### 14.1 Completion Checklist
Before marking Phase 4.2 complete for this workpackage:
- [ ] All pages implemented
- [ ] All components implemented
- [ ] State management configured
- [ ] API integration working
- [ ] Routing configured
- [ ] Code compiles without errors
- [ ] All UI requirements implemented and traceable
- [ ] Accessibility requirements met
- [ ] Responsive design implemented
- [ ] Progress tracking updated
- [ ] No critical errors or all errors resolved

#### 14.2 Handoff to Phase 4.3 or Next Workpackage
Provide to supervisor:
- Confirmation that frontend tier is complete for WP-{ID}
- Location of generated code
- Component counts (pages, components, services)
- Any warnings or notes for batch implementation or next workpackage
- Confirmation that progress tracking is updated

---

## Output Format

### Frontend Code Structure
**Location**: `{{CODE_GENERATION_FRONTEND_OUTPUT}}/wp-{ID}/`

**Directory Structure**:
```
wp-{ID}/
├── pages/
│   ├── EntityNameListPage.tsx
│   ├── EntityNameDetailPage.tsx
│   └── EntityNameFormPage.tsx
├── components/
│   ├── EntityNameList.tsx
│   ├── EntityNameDetail.tsx
│   └── EntityNameForm.tsx
├── services/
│   └── EntityNameService.ts
├── store/
│   └── entityNameSlice.ts (or entityNameStore.ts)
├── types/
│   └── EntityName.ts
└── routes/
    └── index.tsx
```

### Progress Tracking Update
**File**: `{{CODE_GENERATION_STATUS}}`

**Updated Entry**:
```json
{
  "workpackageId": "WP-{ID}",
  "workpackageName": "[Name]",
  "status": "completed",
  "tiersNeeded": ["backend", "frontend"],
  "tiersCompleted": ["backend", "frontend"],
  "backend": {
    "status": "completed",
    "outputLocation": "{{CODE_GENERATION_BACKEND_OUTPUT}}/wp-{ID}",
    "completedDate": "2026-02-16T14:30:00Z"
  },
  "frontend": {
    "status": "completed",
    "outputLocation": "{{CODE_GENERATION_FRONTEND_OUTPUT}}/wp-{ID}",
    "completedDate": "2026-02-16T16:45:00Z",
    "components": {
      "pages": 3,
      "components": 5,
      "services": 1
    }
  },
  "batch": null,
  "completedDate": "2026-02-16T16:45:00Z"
}
```

---

## Quality Criteria

### UI Requirements Implementation
- All UI requirements from business specification are implemented
- User flows work as expected
- Forms match business requirements
- Data displays correctly
- Navigation is intuitive

### Code Compilation
- Code compiles without errors
- No missing dependencies
- No type errors
- No syntax errors

### Accessibility Compliance
- WCAG 2.1 Level AA requirements met
- All interactive elements keyboard accessible
- Proper ARIA labels and roles
- Form accessibility implemented
- Screen reader compatible

### Responsive Design
- Works on mobile devices
- Works on tablets
- Works on desktop
- No horizontal scrolling
- Touch targets appropriately sized

### API Integration
- All backend endpoints integrated
- Request/response types match backend
- Error handling implemented
- Loading states handled

### Code Quality
- Code follows frontend specification conventions
- Naming conventions followed
- Code is well-documented
- No code smells
- Proper error handling

### Traceability
- All pages traceable to business specification
- All components traceable to UI requirements
- All API calls traceable to backend endpoints
- Clear mapping between requirements and implementation

---

## End of Phase 4.2 Document
