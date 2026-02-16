
# Frontend Specification for Java Legacy Migration Projects

**Version:** 1.0  
**Last Updated:** February 16, 2026  
**Scope:** Frontend/UI tier standards and requirements

---

## 1. Overview

### 1.1 Purpose

Establish consistent, maintainable, and modern frontend standards for web applications migrating from mainframe environments, with emphasis on user experience, accessibility, and cloud-native architecture.

### 1.2 Related Specifications

- `00-COMMON-SPECIFICATION.md` - Cross-cutting standards (MUST be followed)
- `02-BACKEND-SPECIFICATION.md` - Backend tier requirements
- `03-BATCH-SPECIFICATION.md` - Batch processing tier requirements

### 1.3 Architecture Context

**Modern Web Application:**
- Single Page Application (SPA) architecture
- Component-based design
- Responsive and accessible UI
- Progressive Web App (PWA) capabilities
- Cloud-native deployment

---

## 2. Technology Stack

### 2.1 Core Framework

**Recommended:** React 18.x or higher

**Rationale:**
- Industry standard with large ecosystem
- Strong community support
- Excellent tooling and developer experience
- Component reusability
- Virtual DOM for performance
- Hooks for state management

**Alternative Frameworks:**
- Angular 17.x (for teams with Angular expertise)
- Vue.js 3.x (for simpler applications)

### 2.2 Build Tool

**Required:** Vite 5.x

**Rationale:**
- Fast development server with HMR
- Optimized production builds
- Modern ES modules support
- Plugin ecosystem
- TypeScript support out of the box

### 2.3 Language

**Required:** TypeScript 5.x

**Rationale:**
- Type safety reduces runtime errors
- Better IDE support and autocomplete
- Self-documenting code
- Easier refactoring
- Industry standard for modern web apps

### 2.4 UI Component Library

**Recommended:** Material-UI (MUI) 5.x

**Rationale:**
- Comprehensive component library
- Follows Material Design principles
- Accessible by default
- Customizable theming
- Good documentation

**Alternative:**
- Ant Design (for enterprise applications)
- Chakra UI (for simpler styling)

### 2.5 State Management

**Recommended:** React Query (TanStack Query) 5.x

**Rationale:**
- Server state management
- Automatic caching and refetching
- Optimistic updates
- Background synchronization
- Reduces boilerplate

**For Complex Client State:**
- Zustand (lightweight, simple API)
- Redux Toolkit (for complex state requirements)

---

## 3. Project Structure

### 3.1 Directory Structure

```
frontend/
├── public/                 # Static assets
│   ├── favicon.ico
│   └── manifest.json
├── src/
│   ├── assets/            # Images, fonts, etc.
│   ├── components/        # Reusable components
│   │   ├── common/        # Generic components
│   │   └── features/      # Feature-specific components
│   ├── pages/             # Page components
│   ├── services/          # API services
│   ├── hooks/             # Custom React hooks
│   ├── utils/             # Utility functions
│   ├── types/             # TypeScript types
│   ├── config/            # Configuration
│   ├── styles/            # Global styles
│   ├── App.tsx            # Root component
│   ├── main.tsx           # Entry point
│   └── vite-env.d.ts      # Vite types
├── tests/                 # Test files
├── .env.example           # Environment variables template
├── .eslintrc.json         # ESLint configuration
├── .prettierrc            # Prettier configuration
├── tsconfig.json          # TypeScript configuration
├── vite.config.ts         # Vite configuration
└── package.json           # Dependencies
```

### 3.2 Component Organization

**Requirements:**
- One component per file
- Co-locate component-specific styles
- Use index.ts for clean imports
- Separate presentational and container components
- Keep components small and focused (<200 lines)

**Component Structure:**
```
components/
├── common/
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.test.tsx
│   │   ├── Button.styles.ts
│   │   └── index.ts
│   └── Input/
└── features/
    └── ResourceList/
        ├── ResourceList.tsx
        ├── ResourceListItem.tsx
        ├── ResourceList.test.tsx
        └── index.ts
```

### 3.3 Naming Conventions

**Files:**
- Components: PascalCase (e.g., `ResourceList.tsx`)
- Utilities: camelCase (e.g., `formatDate.ts`)
- Types: PascalCase (e.g., `ResourceTypes.ts`)
- Constants: UPPER_SNAKE_CASE (e.g., `API_ENDPOINTS.ts`)

**Components:**
- PascalCase for component names
- camelCase for props and variables
- Prefix custom hooks with `use` (e.g., `useResource`)
- Prefix boolean props with `is`, `has`, `should` (e.g., `isLoading`)

---

## 4. Component Design Patterns

### 4.1 Functional Components

**Requirements:**
- Use functional components (not class components)
- Use React Hooks for state and lifecycle
- Use TypeScript for props typing
- Export component as default
- Define prop types interface

**Component Template:**
```typescript
interface ResourceListProps {
  resources: Resource[];
  onSelect: (id: string) => void;
  isLoading?: boolean;
}

export default function ResourceList({ 
  resources, 
  onSelect, 
  isLoading = false 
}: ResourceListProps) {
  // Component logic
  return (
    // JSX
  );
}
```

### 4.2 Custom Hooks

**Requirements:**
- Extract reusable logic into custom hooks
- Prefix hook names with `use`
- Return object or array based on complexity
- Include TypeScript types
- Document hook purpose and usage

**Use Cases:**
- API calls
- Form handling
- Local storage
- Authentication state
- Window dimensions

### 4.3 Component Composition

**Requirements:**
- Prefer composition over inheritance
- Use children prop for flexible layouts
- Create compound components for related functionality
- Use render props for advanced patterns
- Keep component hierarchy shallow

### 4.4 Error Boundaries

**Requirements:**
- Implement error boundaries for error handling
- Display user-friendly error messages
- Log errors for monitoring
- Provide fallback UI
- Allow error recovery when possible

---

## 5. State Management

### 5.1 Server State (React Query)

**Requirements:**
- Use React Query for all API calls
- Configure query keys consistently
- Set appropriate stale times
- Enable automatic refetching
- Implement optimistic updates
- Handle loading and error states

**Query Configuration:**
- Stale time: 5 minutes (default)
- Cache time: 10 minutes
- Retry: 3 attempts with exponential backoff
- Refetch on window focus: enabled

### 5.2 Client State (Zustand)

**Requirements:**
- Use Zustand for complex client state
- Keep stores small and focused
- Use TypeScript for store typing
- Implement actions as store methods
- Avoid storing server data in client state

**Use Cases:**
- UI state (modals, sidebars)
- User preferences
- Form state (complex forms)
- Application settings

### 5.3 Form State

**Recommended:** React Hook Form

**Requirements:**
- Use React Hook Form for form handling
- Integrate with validation library (Zod)
- Handle form submission errors
- Implement field-level validation
- Support async validation

### 5.4 URL State

**Requirements:**
- Store navigation state in URL
- Use query parameters for filters
- Use path parameters for resource IDs
- Sync URL with application state
- Support browser back/forward

---

## 6. API Integration

### 6.1 API Client Configuration

**Requirements:**
- Use Axios for HTTP requests
- Configure base URL from environment
- Add request/response interceptors
- Handle authentication tokens
- Implement retry logic
- Add correlation ID to requests

**Interceptors:**
- Request: Add auth token, correlation ID
- Response: Handle errors, refresh tokens
- Error: Transform error responses

### 6.2 API Service Layer

**Requirements:**
- Create service modules per domain
- Define TypeScript types for requests/responses
- Use consistent naming conventions
- Handle errors appropriately
- Return typed responses

**Service Structure:**
```typescript
// services/resourceService.ts
export const resourceService = {
  getAll: (params: GetResourcesParams): Promise<ResourceResponse[]> => {},
  getById: (id: string): Promise<ResourceResponse> => {},
  create: (data: CreateResourceRequest): Promise<ResourceResponse> => {},
  update: (id: string, data: UpdateResourceRequest): Promise<ResourceResponse> => {},
  delete: (id: string): Promise<void> => {}
};
```

### 6.3 Error Handling

**Requirements:**
- Create custom error types
- Display user-friendly error messages
- Log errors for monitoring
- Provide error recovery options
- Handle network errors gracefully

**Error Types:**
- Validation errors (400)
- Authentication errors (401)
- Authorization errors (403)
- Not found errors (404)
- Server errors (500)

### 6.4 Loading States

**Requirements:**
- Show loading indicators for async operations
- Use skeleton screens for initial loads
- Disable actions during loading
- Provide feedback for long operations
- Handle concurrent requests

---

## 7. Routing

### 7.1 React Router Configuration

**Requirements:**
- Use React Router v6
- Define routes in centralized configuration
- Use nested routes for layouts
- Implement protected routes
- Handle 404 pages

**Route Structure:**
```typescript
const routes = [
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <Home /> },
      { path: 'resources', element: <ResourceList /> },
      { path: 'resources/:id', element: <ResourceDetail /> },
      { path: 'resources/new', element: <ResourceCreate /> }
    ]
  },
  { path: '/login', element: <Login /> },
  { path: '*', element: <NotFound /> }
];
```

### 7.2 Navigation

**Requirements:**
- Use Link component for internal navigation
- Use programmatic navigation for actions
- Preserve scroll position appropriately
- Support browser back/forward
- Handle navigation guards

### 7.3 Protected Routes

**Requirements:**
- Implement authentication check
- Redirect to login if unauthenticated
- Preserve intended destination
- Check authorization for routes
- Handle token expiration

---

## 8. Styling

### 8.1 Styling Approach

**Recommended:** CSS-in-JS with MUI's styled API

**Requirements:**
- Use theme for consistent styling
- Define design tokens (colors, spacing, typography)
- Support light/dark mode
- Use responsive design
- Follow accessibility guidelines

### 8.2 Theme Configuration

**Requirements:**
- Define color palette
- Define typography scale
- Define spacing scale
- Define breakpoints
- Define component overrides

### 8.3 Responsive Design

**Requirements:**
- Mobile-first approach
- Support common breakpoints (xs, sm, md, lg, xl)
- Test on multiple devices
- Use flexible layouts (flexbox, grid)
- Optimize images for different sizes

### 8.4 Accessibility

**Requirements:**
- Use semantic HTML
- Provide alt text for images
- Support keyboard navigation
- Use ARIA attributes appropriately
- Maintain color contrast ratios (WCAG AA)
- Test with screen readers

---

## 9. Forms and Validation

### 9.1 Form Handling

**Requirements:**
- Use React Hook Form
- Implement controlled components
- Handle form submission
- Display validation errors
- Support field-level validation
- Support async validation

### 9.2 Validation

**Recommended:** Zod for schema validation

**Requirements:**
- Define validation schemas
- Validate on blur and submit
- Display inline error messages
- Prevent invalid submissions
- Support custom validation rules

### 9.3 Form Components

**Requirements:**
- Create reusable form components
- Support different input types
- Handle disabled and readonly states
- Show loading states
- Support error states

---

## 10. Authentication and Authorization

### 10.1 Authentication

**Requirements:**
- Implement JWT-based authentication
- Store tokens securely (httpOnly cookies or secure storage)
- Refresh tokens before expiration
- Handle token expiration gracefully
- Implement logout functionality

### 10.2 Authorization

**Requirements:**
- Check user permissions
- Hide unauthorized UI elements
- Protect routes based on roles
- Handle authorization errors
- Support role-based access control

### 10.3 Security Best Practices

**Requirements:**
- Never store sensitive data in localStorage
- Sanitize user input
- Implement CSRF protection
- Use HTTPS only
- Implement Content Security Policy
- Validate all data from backend

---

## 11. Performance Optimization

### 11.1 Code Splitting

**Requirements:**
- Use lazy loading for routes
- Use dynamic imports for large components
- Split vendor bundles
- Optimize bundle size
- Monitor bundle size in CI/CD

### 11.2 Rendering Optimization

**Requirements:**
- Use React.memo for expensive components
- Use useMemo for expensive calculations
- Use useCallback for event handlers
- Avoid unnecessary re-renders
- Use virtualization for long lists

### 11.3 Asset Optimization

**Requirements:**
- Optimize images (WebP, lazy loading)
- Minimize CSS and JavaScript
- Use CDN for static assets
- Implement caching strategies
- Compress assets (gzip, brotli)

### 11.4 Performance Monitoring

**Requirements:**
- Monitor Core Web Vitals
- Track page load times
- Monitor API response times
- Use performance profiling tools
- Set performance budgets

---

## 12. Testing

### 12.1 Testing Strategy

**Test Pyramid:**
- Unit Tests: 70% (components, hooks, utils)
- Integration Tests: 20% (user flows)
- E2E Tests: 10% (critical paths)

**Coverage Requirements:**
- Minimum 80% code coverage
- 100% coverage for critical components
- All user interactions tested

### 12.2 Unit Testing

**Requirements:**
- Use Vitest for unit tests
- Use React Testing Library
- Test component behavior, not implementation
- Mock external dependencies
- Test error scenarios

**Test Structure:**
- Arrange - Setup component and props
- Act - Trigger user interactions
- Assert - Verify expected behavior

### 12.3 Integration Testing

**Requirements:**
- Test user flows
- Mock API calls
- Test form submissions
- Test navigation
- Test error handling

### 12.4 E2E Testing

**Recommended:** Playwright

**Requirements:**
- Test critical user journeys
- Test across browsers
- Test responsive design
- Test accessibility
- Run in CI/CD pipeline

---

## 13. Internationalization (i18n)

### 13.1 i18n Configuration

**Recommended:** react-i18next

**Requirements:**
- Support multiple languages
- Store translations in JSON files
- Use translation keys consistently
- Support pluralization
- Support date/number formatting

### 13.2 Translation Management

**Requirements:**
- Organize translations by feature
- Use namespaces for large applications
- Provide fallback language
- Handle missing translations
- Support RTL languages

---

## 14. Error Handling and Logging

### 14.1 Error Handling

**Requirements:**
- Implement global error boundary
- Display user-friendly error messages
- Provide error recovery options
- Log errors to monitoring service
- Handle network errors

### 14.2 Logging

**Requirements:**
- Log errors with context
- Log user actions for debugging
- Include correlation IDs
- Never log sensitive data
- Use appropriate log levels

---

## 15. Build and Deployment

### 15.1 Build Configuration

**Requirements:**
- Separate dev and prod builds
- Use environment variables
- Optimize production builds
- Generate source maps
- Implement cache busting

### 15.2 Environment Variables

**Requirements:**
- Use .env files for configuration
- Never commit secrets
- Validate required variables
- Document all variables
- Use different values per environment

### 15.3 Docker Configuration

**Requirements:**
- Use multi-stage Dockerfile
- Use nginx for serving static files
- Minimize image size
- Include health check
- Run as non-root user

### 15.4 CI/CD Pipeline

**Requirements:**
- Run linting and tests
- Build production bundle
- Run security scans
- Deploy to environments
- Run smoke tests

---

## 16. Code Quality

### 16.1 Linting

**Requirements:**
- Use ESLint with TypeScript support
- Use Prettier for formatting
- Configure pre-commit hooks
- Enforce consistent code style
- Fix linting errors before commit

### 16.2 Code Review

**Requirements:**
- Review all code changes
- Check for security issues
- Verify test coverage
- Ensure accessibility
- Verify performance impact

### 16.3 Documentation

**Requirements:**
- Document complex components
- Document custom hooks
- Document API integration
- Maintain README
- Document deployment process

---

## 17. Accessibility (a11y)

### 17.1 WCAG Compliance

**Requirements:**
- Meet WCAG 2.1 Level AA
- Support keyboard navigation
- Provide text alternatives
- Maintain color contrast
- Support screen readers

### 17.2 Semantic HTML

**Requirements:**
- Use semantic elements
- Use proper heading hierarchy
- Use ARIA attributes appropriately
- Label form inputs
- Provide skip links

### 17.3 Testing

**Requirements:**
- Use automated accessibility testing
- Test with screen readers
- Test keyboard navigation
- Test color contrast
- Test with browser extensions

---

## 18. Progressive Web App (PWA)

### 18.1 PWA Features

**Requirements:**
- Implement service worker
- Create web app manifest
- Support offline functionality
- Enable install prompt
- Implement push notifications (optional)

### 18.2 Offline Support

**Requirements:**
- Cache static assets
- Cache API responses
- Handle offline state
- Sync when online
- Show offline indicator

---

## 19. Monitoring and Analytics

### 19.1 Error Monitoring

**Requirements:**
- Integrate error tracking service
- Track JavaScript errors
- Track API errors
- Include user context
- Set up alerts

### 19.2 Analytics

**Requirements:**
- Track page views
- Track user interactions
- Track conversion events
- Respect user privacy
- Comply with GDPR

---

## 20. Prohibited Practices

### 20.1 Code Anti-Patterns

**Prohibited:**
- Prop drilling (use context or state management)
- Inline styles (use styled components or CSS-in-JS)
- Direct DOM manipulation (use React refs)
- Mutating state directly
- Using index as key in lists
- Storing derived state

### 20.2 Performance Anti-Patterns

**Prohibited:**
- Creating components inside render
- Creating functions inside render
- Not memoizing expensive calculations
- Not using code splitting
- Loading all data upfront
- Not implementing pagination

### 20.3 Security Anti-Patterns

**Prohibited:**
- Using dangerouslySetInnerHTML without sanitization
- Storing tokens in localStorage
- Trusting user input
- Exposing API keys in frontend
- Not validating data from backend
- Using eval() or Function()

---

## 21. Document Control

### 21.1 Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-16 | Architecture Team | Initial version |

### 21.2 Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Technical Lead | | | |
| Architecture Lead | | | |
| UX Lead | | | |

### 21.3 Review Schedule

This document should be reviewed and updated:
- Quarterly for minor updates
- Annually for major revisions
- When new technologies are adopted
- When design patterns change

### 21.4 Related Documents

- Common Specification
- Backend Specification
- Batch Specification
- Design System Guide
- Accessibility Guidelines

---

**End of Frontend Specification**
