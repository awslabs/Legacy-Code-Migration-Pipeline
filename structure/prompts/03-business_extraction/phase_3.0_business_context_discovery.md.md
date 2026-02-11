
# Phase 3.0: Business Context Discovery

---

## Orchestration Information

**Phase**: Phase 3 - Business Specification
**Step**: Step 3.0 - Business Context Discovery
**Team Supervisor**: business_team_supervisor
**Assigned Agent**: business_specialist_logic_extraction
**Task File Name**: {{TASKS_BASE_PATH}}/phase_3.0_business_context_discovery.md

### Expected Deliverables

1. **Business Context Documents**
   - File: {{BUSINESS_CONTEXT_BASE_PATH}}/WP-XXX-business-context.md
   - Template: {{BUSINESS_CONTEXT_TEMPLATE}}
   - Description: Business domain, stakeholders, vocabulary, and constraints for each workpackage

2. **Business Glossary**
   - File: {{BUSINESS_CONTEXT_BASE_PATH}}/business-glossary.md
   - Description: Consolidated business vocabulary across all workpackages

3. **Progress Tracking**
   - File: {{BUSINESS_CONTEXT_STATUS}}
   - Template: {{BUSINESS_CONTEXT_STATUS_TEMPLATE}}
   - Description: Context discovery progress tracking

4. **Error Reports** (if applicable)
   - File: {{BUSINESS_CONTEXT_ERRORS}}
   - Template: {{BUSINESS_CONTEXT_ERRORS_TEMPLATE}}
   - Description: Documentation of issues encountered during discovery

### Success Criteria
- [ ] Business domain identified for each workpackage
- [ ] Business stakeholders documented
- [ ] Business vocabulary extracted and glossary created
- [ ] Business constraints and policies identified
- [ ] Business outcomes and value documented
- [ ] Legacy implementation pointers captured (not detailed analysis)
- [ ] All deliverables produced at specified paths
- [ ] Ready for Phase 3.1 (Business Specification Extraction)

---

## Context

### Input Locations
- **Workpackage definitions**: `{{PROJECT_BASE_PATH}}/output/migration/workpackage_definition/`
- **Source code files**: `{{SOURCE_CODE}}`
- **Database source code**: `{{DATABASE_SOURCE_CODE}}`
- **Legacy specifications**: `{{PROJECT_BASE_PATH}}/input/legacy_specifications/`
- **Legacy documentation**: `{{PROJECT_BASE_PATH}}/input/legacy_documentation/`
- **Business documentation**: `{{PROJECT_BASE_PATH}}/input/business_documentation/`
- **Module dependency table**: `{{DEPENDENCY_ANALYSIS_TABLE}}`

### Output Locations
- **Business context documents**: `{{BUSINESS_CONTEXT_BASE_PATH}}/WP-XXX-business-context.md`
- **Business glossary**: `{{BUSINESS_CONTEXT_BASE_PATH}}/business-glossary.md`
- **Progress tracking**: `{{BUSINESS_CONTEXT_STATUS}}`
- **Error reports**: `{{BUSINESS_CONTEXT_ERRORS}}`
- **Task files location**: `{{TASKS_BASE_PATH}}`

### Template Locations
- **Business context template**: `{{BUSINESS_CONTEXT_TEMPLATE}}`
- **Status template**: `{{BUSINESS_CONTEXT_STATUS_TEMPLATE}}`
- **Errors template**: `{{BUSINESS_CONTEXT_ERRORS_TEMPLATE}}`

### Previous Phase Artifacts
- **From Phase 1**: Source code analysis, dependency analysis table, module classifications, business flows
- **From Phase 2**: Workpackage definitions with prioritized flows

---

## Objective

Discover and document the business context for each workpackage BEFORE extracting technical details. Understand what business problem the code solves, who the stakeholders are, what business vocabulary exists, and what business constraints apply. This context will guide the subsequent business specification extraction in Phase 3.1.

**CRITICAL**: This phase is about understanding the business landscape, NOT extracting detailed business rules or entities. Focus on the "why" and "who" before the "what" and "how".

---

## Instructions

### 1. Preparation
1. Review the workpackage definitions from Phase 2
2. For each workpackage, in priority order:
   - Identify all relevant source files (programs, copybooks, includes, JCL, maps, etc.)
   - Review any available legacy documentation
   - Review any available business documentation
   - Examine code comments, variable names, and program descriptions for business clues

### 2. Business Domain Identification
1. For each workpackage, determine:
   - **Primary Business Domain**: What major business area does this support? (e.g., Order Management, Customer Service, Billing, Inventory Management, Financial Reporting)
   - **Sub-Domain**: What specific area within the primary domain? (e.g., Credit Risk Management within Order Management)
   - **Business Capability**: What specific business capability is being implemented? (e.g., Customer Credit Validation, Order Fulfillment, Invoice Generation)

2. Evidence sources for domain identification:
   - Program names and descriptions
   - Module naming conventions
   - Database table names and relationships
   - Transaction codes and screen names
   - Code comments and documentation headers
   - File and dataset naming patterns

3. Document confidence level:
   - **High**: Clear evidence from multiple sources
   - **Medium**: Evidence from code patterns and naming
   - **Low**: Inferred from technical implementation only

### 3. Business Stakeholder Identification
1. For each workpackage, identify:
   - **Primary Users**: Who directly interacts with this functionality? (e.g., Sales Representatives, Customer Service Agents, Finance Analysts)
   - **Business Owners**: Who owns the business process? (e.g., Finance Department, Sales Operations, Customer Service Management)
   - **Impacted Parties**: Who is affected by this functionality? (e.g., Customers, Vendors, Partners, Internal Teams)
   - **Decision Makers**: Who makes decisions about business rules? (e.g., Credit Risk Team, Pricing Committee, Compliance Officer)

2. Evidence sources for stakeholder identification:
   - User interface screens and transaction codes
   - Report recipients and distribution lists
   - Authorization and security profiles
   - Workflow and approval chains
   - Documentation and training materials
   - Code comments mentioning departments or roles

3. If stakeholders cannot be determined from available evidence:
   - Document as "Unknown - requires business specialist input"
   - Flag for human review in Phase 3.2

### 4. Business Problem Statement
1. For each workpackage, articulate:
   - **The Business Problem**: What business challenge or need does this code address?
   - **Business Context**: Why does this functionality exist?
   - **Business Value**: What value does this deliver to the organization?
   - **Business Impact**: What happens if this functionality fails?

2. Frame the problem statement from a business perspective:
   - **Good**: "The business needs to prevent order fulfillment for customers who exceed their credit limits to minimize financial risk exposure while maintaining customer relationships"
   - **Bad**: "The program validates credit limits before processing orders"

3. Focus on business outcomes, not technical implementation:
   - Ask: "If I were explaining this to a business executive who has never seen the code, what problem would I say it solves?"
   - Avoid technical jargon and implementation details
   - Emphasize business benefits and risks

### 5. Business Vocabulary Extraction
1. For each workpackage, extract business terms:
   - **Business Entities**: Real-world business concepts (Customer, Order, Payment, Product, Invoice)
   - **Business Attributes**: Business-meaningful properties (Credit Limit, Order Total, Payment Status, Product Category)
   - **Business Actions**: Business operations (Validate, Approve, Reject, Process, Calculate, Notify)
   - **Business States**: Business status values (Pending, Approved, Rejected, Completed, Cancelled)
   - **Business Rules Terms**: Terms used in business policies (Threshold, Limit, Deadline, Priority, Exception)

2. Sources for vocabulary extraction:
   - Variable names (after removing technical prefixes)
   - Code comments and documentation
   - Screen labels and field names
   - Report headers and column names
   - Database table and column names
   - Error messages and user notifications

3. Create business term definitions:
   - **Term**: The business vocabulary word
   - **Definition**: What it means in business context
   - **Technical Mapping**: How it appears in legacy code (for traceability)
   - **Example**: Concrete example of the term in use

4. Build a consolidated business glossary:
   - Merge vocabulary across all workpackages
   - Identify synonyms and resolve conflicts
   - Create a single source of truth for business terminology

### 6. Business Constraints and Policies Identification
1. For each workpackage, identify high-level business constraints:
   - **Business Rules**: What business policies are being enforced? (e.g., "Orders cannot exceed credit limits")
   - **Regulatory Requirements**: What compliance or regulatory constraints exist? (e.g., "Must comply with SOX financial controls")
   - **Business Policies**: What organizational policies apply? (e.g., "VIP customers have manual override capability")
   - **Service Level Agreements**: What performance or availability commitments exist? (e.g., "Order validation must complete within 2 seconds")

2. **IMPORTANT**: At this phase, identify WHAT constraints exist, not HOW they are implemented:
   - **Good**: "Credit limits are enforced to minimize financial risk"
   - **Bad**: "IF WS-CREDIT-LIM < WS-ORDER-AMT THEN REJECT"

3. Distinguish between business constraints and technical constraints:
   - **Business Constraint**: Would exist regardless of technology (credit limits, validation rules, approval workflows)
   - **Technical Constraint**: Specific to mainframe implementation (batch restart logic, file locking, CICS transaction timeouts)
   - Document business constraints in this phase
   - Note technical constraints as "legacy implementation details" for Chapter 6 in Phase 3.1

### 7. Business Outcomes and Success Criteria
1. For each workpackage, document:
   - **Success Outcomes**: What happens when the functionality works correctly? (e.g., "Order is validated and proceeds to fulfillment")
   - **Failure Outcomes**: What happens when business rules are violated? (e.g., "Order is rejected with clear reason provided to customer")
   - **Business Metrics**: How is success measured? (e.g., "Reduces bad debt by $X annually", "Maintains 99.9% order accuracy")
   - **Business Value**: What tangible benefit does this deliver? (e.g., "Minimizes credit risk exposure", "Improves customer satisfaction")

2. Frame outcomes from business perspective:
   - Focus on business impact, not technical success
   - Quantify value where possible (cost savings, revenue impact, risk reduction)
   - Consider both positive outcomes (value delivered) and negative outcomes (risks mitigated)

### 8. Legacy Implementation Pointers
1. For each workpackage, document high-level technical context:
   - **Primary Programs**: Main COBOL programs involved
   - **Key Data Sources**: Databases, files, or external systems accessed
   - **Integration Points**: CICS transactions, batch jobs, APIs, message queues
   - **Technology Stack**: COBOL, DB2, CICS, JCL, etc.

2. **IMPORTANT**: This is NOT detailed technical analysis:
   - Provide just enough context to understand the legacy landscape
   - Detailed technical extraction happens in Phase 3.1
   - Focus on "what technologies are involved" not "how they work"

### 9. Business Context Document Creation
1. For each workpackage, create a business context document using the template
2. Document structure:
   - **Section 1**: Business Domain (Primary domain, sub-domain, capability)
   - **Section 2**: Business Stakeholders (Users, owners, impacted parties, decision makers)
   - **Section 3**: Business Problem Statement (Problem, context, value, impact)
   - **Section 4**: Business Vocabulary (Terms, definitions, technical mappings, examples)
   - **Section 5**: Business Constraints and Policies (Rules, regulations, policies, SLAs)
   - **Section 6**: Business Outcomes (Success, failure, metrics, value)
   - **Section 7**: Legacy Implementation Pointers (Programs, data sources, integrations, technology stack)

3. Ensure all sections are written from business perspective:
   - Use business terminology, not technical jargon
   - Focus on "why" and "what" not "how"
   - Make it readable by business specialists who have never seen the code

### 10. Business Glossary Consolidation
1. After completing all workpackage context documents:
   - Extract all business terms from individual documents
   - Merge into a single consolidated business glossary
   - Resolve conflicts and synonyms
   - Organize alphabetically or by business domain
   - Cross-reference terms used across multiple workpackages

### 11. Progress Tracking and Validation
1. Update progress tracking for each completed workpackage:
   - Record completion status and artifacts
   - Document confidence levels for domain identification
   - Flag areas requiring business specialist input
   - Note any missing documentation or ambiguous business context

2. Validate completeness before proceeding to Phase 3.1:
   - All workpackages have business context documents
   - Business glossary is consolidated
   - High-confidence business domains identified
   - Stakeholders documented (or flagged for BA input)
   - Business problem statements articulated

### 12. Pause Before Progressing to Phase 3.1
- Do not proceed to business specification extraction until all business context documents are complete and validated

---

## Output Format

### Business Context Document
**File**: `{{BUSINESS_CONTEXT_BASE_PATH}}/WP-XXX-business-context.md`
**Template**: `{{BUSINESS_CONTEXT_TEMPLATE}}`

**Structure**:
```markdown
# Business Context Document: WP-XXX (Workpackage Name)

## Document Control
- **Version**: 1.0
- **Date**: YYYY-MM-DD
- **Author**: [Agent/Team Name]
- **Workpackage ID**: WP-XXX
- **Confidence Level**: High/Medium/Low

## 1. Business Domain
### 1.1 Primary Business Domain
[e.g., Order Management, Customer Service, Financial Reporting]

### 1.2 Sub-Domain
[e.g., Credit Risk Management, Order Fulfillment, Invoice Processing]

### 1.3 Business Capability
[e.g., Customer Credit Validation, Inventory Reservation, Payment Processing]

### 1.4 Evidence and Confidence
- **Evidence Sources**: [List sources used to identify domain]
- **Confidence Level**: High/Medium/Low
- **Rationale**: [Why this confidence level]

## 2. Business Stakeholders
### 2.1 Primary Users
[Who directly interacts with this functionality]
- Role 1: [Description]
- Role 2: [Description]

### 2.2 Business Owners
[Who owns the business process]
- Department/Team: [Description]

### 2.3 Impacted Parties
[Who is affected by this functionality]
- Party 1: [Description]
- Party 2: [Description]

### 2.4 Decision Makers
[Who makes decisions about business rules]
- Role/Team: [Description]

### 2.5 Evidence and Confidence
- **Evidence Sources**: [List sources]
- **Confidence Level**: High/Medium/Low
- **Requires BA Input**: Yes/No

## 3. Business Problem Statement
### 3.1 The Business Problem
[What business challenge or need does this address]

### 3.2 Business Context
[Why does this functionality exist]

### 3.3 Business Value
[What value does this deliver to the organization]

### 3.4 Business Impact
[What happens if this functionality fails]

## 4. Business Vocabulary
### 4.1 Business Entities
| Term | Definition | Technical Mapping | Example |
|------|------------|-------------------|---------|
| Customer | [Business definition] | CUST-REC, CUSTOMER-FILE | [Example] |
| Order | [Business definition] | ORD-REC, ORDER-FILE | [Example] |

### 4.2 Business Attributes
| Term | Definition | Technical Mapping | Example |
|------|------------|-------------------|---------|
| Credit Limit | [Business definition] | WS-CREDIT-LIM | [Example] |
| Order Total | [Business definition] | WS-ORDER-AMT | [Example] |

### 4.3 Business Actions
| Term | Definition | Technical Mapping | Example |
|------|------------|-------------------|---------|
| Validate | [Business definition] | PERFORM VALIDATE-CREDIT | [Example] |
| Approve | [Business definition] | PERFORM APPROVE-ORDER | [Example] |

### 4.4 Business States
| Term | Definition | Technical Mapping | Example |
|------|------------|-------------------|---------|
| Pending | [Business definition] | STATUS-CD = 'P' | [Example] |
| Approved | [Business definition] | STATUS-CD = 'A' | [Example] |

## 5. Business Constraints and Policies
### 5.1 Business Rules (High-Level)
- **Rule 1**: [What business policy is enforced]
- **Rule 2**: [What business policy is enforced]

### 5.2 Regulatory Requirements
- **Requirement 1**: [What compliance constraint exists]
- **Requirement 2**: [What compliance constraint exists]

### 5.3 Business Policies
- **Policy 1**: [What organizational policy applies]
- **Policy 2**: [What organizational policy applies]

### 5.4 Service Level Agreements
- **SLA 1**: [What performance/availability commitment exists]
- **SLA 2**: [What performance/availability commitment exists]

### 5.5 Business vs Technical Constraints
**Business Constraints** (would exist in any implementation):
- [List business constraints]

**Technical Constraints** (specific to legacy implementation):
- [List technical constraints - for Chapter 6 in Phase 3.1]

## 6. Business Outcomes and Success Criteria
### 6.1 Success Outcomes
[What happens when functionality works correctly]

### 6.2 Failure Outcomes
[What happens when business rules are violated]

### 6.3 Business Metrics
- **Metric 1**: [How success is measured]
- **Metric 2**: [How success is measured]

### 6.4 Business Value
- **Value 1**: [Tangible benefit delivered]
- **Value 2**: [Tangible benefit delivered]

## 7. Legacy Implementation Pointers
### 7.1 Primary Programs
- Program 1: [Brief description]
- Program 2: [Brief description]

### 7.2 Key Data Sources
- Database/File 1: [Brief description]
- Database/File 2: [Brief description]

### 7.3 Integration Points
- Integration 1: [Brief description]
- Integration 2: [Brief description]

### 7.4 Technology Stack
- COBOL, DB2, CICS, JCL, etc.

## 8. Notes and Flags
### 8.1 Areas Requiring Specialist Input
- [List areas where business specialist input is needed]

### 8.2 Ambiguities and Uncertainties
- [List any ambiguous or uncertain aspects]

### 8.3 Missing Documentation
- [List any missing documentation that would help]
```

### Business Glossary
**File**: `{{BUSINESS_CONTEXT_BASE_PATH}}/business-glossary.md`

**Structure**:
```markdown
# Business Glossary - Consolidated

## Document Control
- **Version**: 1.0
- **Date**: YYYY-MM-DD
- **Author**: [Agent/Team Name]
- **Scope**: All Workpackages

## Business Entities
| Term | Definition | Used in Workpackages | Technical Mappings | Examples |
|------|------------|----------------------|--------------------|----------|
| Customer | [Definition] | WP-001, WP-003 | CUST-REC, CUSTOMER-FILE | [Example] |
| Order | [Definition] | WP-001, WP-002 | ORD-REC, ORDER-FILE | [Example] |

## Business Attributes
| Term | Definition | Used in Workpackages | Technical Mappings | Examples |
|------|------------|----------------------|--------------------|----------|
| Credit Limit | [Definition] | WP-001 | WS-CREDIT-LIM | [Example] |
| Order Total | [Definition] | WP-001, WP-002 | WS-ORDER-AMT | [Example] |

## Business Actions
| Term | Definition | Used in Workpackages | Technical Mappings | Examples |
|------|------------|----------------------|--------------------|----------|
| Validate | [Definition] | WP-001, WP-003 | PERFORM VALIDATE-* | [Example] |
| Approve | [Definition] | WP-001, WP-002 | PERFORM APPROVE-* | [Example] |

## Business States
| Term | Definition | Used in Workpackages | Technical Mappings | Examples |
|------|------------|----------------------|--------------------|----------|
| Pending | [Definition] | WP-001, WP-002 | STATUS-CD = 'P' | [Example] |
| Approved | [Definition] | WP-001, WP-002 | STATUS-CD = 'A' | [Example] |

## Cross-References
### Synonyms
- [Term 1] = [Term 2] (used in different workpackages for same concept)

### Related Terms
- [Term 1] relates to [Term 2] via [relationship]
```

### Progress Tracking
**File**: `{{BUSINESS_CONTEXT_STATUS}}`
**Template**: `{{BUSINESS_CONTEXT_STATUS_TEMPLATE}}`

### Error Reports
**File**: `{{BUSINESS_CONTEXT_ERRORS}}`
**Template**: `{{BUSINESS_CONTEXT_ERRORS_TEMPLATE}}`

---

## Quality Criteria

### Business Domain Clarity
- Business domain is clearly identified and articulated
- Domain assignment is supported by evidence from multiple sources
- Confidence level is documented and justified
- Sub-domain and business capability are specific and meaningful

### Stakeholder Completeness
- All relevant stakeholder categories are identified
- Stakeholder roles are described in business terms
- Evidence sources for stakeholder identification are documented
- Areas requiring BA input are clearly flagged

### Business Problem Articulation
- Problem statement is written from business perspective
- Business context and rationale are clear
- Business value and impact are quantified where possible
- Statement is understandable by non-technical business specialists

### Vocabulary Accuracy
- Business terms are extracted from code and documentation
- Definitions are business-focused, not technical
- Technical mappings provide traceability to legacy code
- Examples illustrate term usage in business context
- Consolidated glossary resolves conflicts and synonyms

### Constraint Identification
- Business constraints are distinguished from technical constraints
- High-level business policies are identified (not detailed rules)
- Regulatory and compliance requirements are noted
- SLAs and performance requirements are documented

### Business Outcome Focus
- Success and failure outcomes are described in business terms
- Business metrics and value are quantified where possible
- Outcomes focus on business impact, not technical success

### Legacy Context Appropriateness
- Legacy implementation pointers provide sufficient context
- Technical details are high-level, not exhaustive
- Focus is on "what technologies" not "how they work"
- Detailed technical analysis is deferred to Phase 3.1

---

## Error Handling

### Common Error Scenarios

1. **Missing Business Documentation**
   - Detection: No legacy specifications or business documentation available
   - Recovery: Extract business context from code comments, variable names, and patterns
   - Escalation: Document confidence level as "Low" and flag for BA review

2. **Ambiguous Business Domain**
   - Detection: Code spans multiple business domains or domain is unclear
   - Recovery: Document all possible domains with evidence and confidence levels
   - Escalation: Flag for BA input to clarify primary domain

3. **Unknown Stakeholders**
   - Detection: No evidence of who uses or owns the functionality
   - Recovery: Document as "Unknown - requires BA input"
   - Escalation: Flag as high-priority item for Phase 3.2 review

4. **Conflicting Business Vocabulary**
   - Detection: Same term used differently across workpackages
   - Recovery: Document all usages and flag conflict in glossary
   - Escalation: Request BA clarification on preferred terminology

5. **Technical-Only Documentation**
   - Detection: All available documentation is technical, no business context
   - Recovery: Infer business context from code patterns and naming
   - Escalation: Document confidence level as "Low" and flag for BA validation

### Error Reporting Format
**File**: `{{BUSINESS_CONTEXT_ERRORS}}`
**Template**: `{{BUSINESS_CONTEXT_ERRORS_TEMPLATE}}`

**Structure**:
```markdown
# Business Context Discovery Errors - WP-XXX

## Error 1: [Error Type]
- **Workpackage**: WP-XXX
- **Severity**: High/Medium/Low
- **Description**: [What went wrong]
- **Impact**: [How this affects Phase 3.1]
- **Recovery Action**: [What was done]
- **Requires BA Input**: Yes/No
- **Status**: Open/Resolved
```

### Fallback Strategies
- When business documentation is missing, extract context from code patterns
- When stakeholders are unknown, document as "requires BA input"
- When domain is ambiguous, document all possibilities with confidence levels
- When vocabulary conflicts exist, flag for BA resolution
- Prioritize completing context documents over perfect accuracy
- Flag all uncertainties for Phase 3.2 review

---

## End of Phase 3.0 Document
