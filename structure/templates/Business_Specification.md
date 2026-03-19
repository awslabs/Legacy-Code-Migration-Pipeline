
# Business Specification: [Workpackage Name]

---

## Document Control

**Document Type**: Business Specification (IEEE 830-1998)
**Workpackage ID**: WP-XXX
**Flow ID**: FLOW_XXX
**Version**: 1.0
**Date**: YYYY-MM-DD
**Status**: [Draft / In Review / Approved / Approved with Changes]
**Confidence Level**: [High / Medium / Low]
**Author**: [Agent/Person Name]
**Reviewer**: [Reviewer Name]
**Review Date**: [YYYY-MM-DD]
**Approval Status**: [Pending / Approved / Approved with Changes / Rejected]

---

## Chapter 1: Introduction

### 1.1 Purpose

**Business Domain**: [Business domain this workpackage supports - e.g., Order Management, Customer Service, Billing]

**Business Problem Statement**: [What business problem does this functionality solve? Why does it exist?]

**Business Value**: [What business value does this provide? What outcomes does it enable?]

**Confidence Level**: [High / Medium / Low] - [Explanation of confidence level]

### 1.2 Scope

**Business Stakeholders**:
- **Primary Users**: [Who uses this functionality?]
- **Business Owners**: [Who owns the business process?]
- **Other Stakeholders**: [Who else is affected?]

**Business Processes Covered**: [What business processes are included?]

**Business Boundaries**:
- **Included**: [What is in scope?]
- **Excluded**: [What is out of scope?]

### 1.3 Business Context

**Why This Functionality Exists**: [Business rationale and context]

**Business Constraints and Policies** (High-Level): [Key business constraints from Phase 3.0]

**Business Vocabulary Reference**: See consolidated business glossary at [path]

---

## Chapter 2: Business Entities

**Note**: Business entities represent real-world business concepts (Customer, Order, Payment), not code structures. Use business-meaningful names from the business glossary. Data types should be generic (String, Numeric, Date, Timestamp, Boolean). Use "N/A" for data lengths on Date, Timestamp, and Boolean types.

**Variable Naming Convention**: Convert COBOL variables to camelCase by:
1. Removing program-specific prefixes (XDIPA501-, WS-, LS-, etc.)
2. Removing direction indicators (I-, O-, IO-)
3. Converting remaining hyphenated parts to camelCase
4. Example: XDIPA501-I-CORP-CLCT-GROUP-CD → corpClctGroupCd

### BE-XXX-001: [Business Entity Name]

**Business Description**: [What business concept does this represent?]

**Attributes**:

| Attribute Name (camelCase) | Data Type | Length | Business Validation Rules | Legacy Variable Name |
|---------------------------|-----------|--------|---------------------------|---------------------|
| [attributeName] | [String/Numeric/Date/Timestamp/Boolean] | [length or N/A] | [Business validation rules - not technical constraints] | [LEGACY-VAR-NAME] |

**Business Relationships**:
- [Relationship to other business entities in business terms]

**Business Constraints**:
- [Business constraints - not technical constraints like buffer sizes]

**Database Alignment**: [Reference to database table if applicable]

---

### BE-XXX-002: [Business Entity Name]

[Repeat structure for each business entity]

---

## Chapter 3: Business Rules

**Note**: Business rules represent business policies that would exist in any implementation. Technical rules (batch restart, file locking, CICS timeouts) belong in Chapter 6. Business rules should be described in business terms using vocabulary from the business glossary.

### BR-XXX-001: [Business Rule Name]

**WHEN**: [Business condition in business terms]

**THEN**: [Business action in business terms]

**RATIONALE**: [Why this rule exists - business reason]

**RELATED ENTITIES**: [Business entities involved - use BE-XXX identifiers]

**EXCEPTION HANDLING**: [Business exceptions and how they're handled in business terms]

**BUSINESS CONSTANTS**: [Credit limits, thresholds, business dates - not technical constants]

---

### BR-XXX-002: [Business Rule Name]

[Repeat structure for each business rule]

---

## Chapter 4: Business Functions

**Note**: Business functions represent business capabilities, not program subroutines. Function names should use business vocabulary. Inputs/outputs should be described in business terms, not technical parameters.

### F-XXX-001: [Business Function Name]

**PURPOSE**: [What business capability this provides]

**BUSINESS INPUTS**: [Business information required - not technical parameters]

**BUSINESS OUTPUTS**: [Business information produced - not technical return codes]

**BUSINESS PROCESSING**: [Business operations performed - in business terms, not code implementation]

**BUSINESS RULES APPLIED**: [List of BR-XXX identifiers that apply to this function]

**RELATED ENTITIES**: [Business entities involved - use BE-XXX identifiers]

**BUSINESS EXCEPTIONS**: [Business error conditions and handling in business terms]

---

### F-XXX-002: [Business Function Name]

[Repeat structure for each business function]

---

## Chapter 5: Process Flows

**Note**: Process flows represent business processes, not program call graphs. Activities should be described in business terms, not program names. Decision points are business decisions, not IF statements. Actors are business roles, not transaction codes.

### Process: [Business Process Name]

**Trigger**: [Business event that starts the process]

**Activities**:

1. **[Business Activity 1]** - Performed by [Business Actor]
   - **Decision Point**: [Business decision if applicable]
     - If [business condition]: [business action]
     - If [business condition]: [business action]

2. **[Business Activity 2]** - Performed by [Business Actor]
   - **Uses**: [Business entities/functions - use BE-XXX, F-XXX identifiers]
   - **Produces**: [Business outputs]

3. **[Business Activity 3]** - Performed by [Business Actor]

**Outcomes**:
- **Success**: [Business outcome when successful]
- **Failure**: [Business outcome when failed]

**Business Value**: [What business value this process delivers]

---

## Chapter 6: Legacy Implementation References

**Note**: This chapter contains ALL technical implementation details. Use technical terminology and code references. Provide complete traceability to source code.

### 6.1 Source Files

| File Name | File Type | Description | Path |
|-----------|-----------|-------------|------|
| [filename] | [COBOL/Copybook/JCL/Map] | [Description] | [path] |

### 6.2 Business Rule Implementation

For each business rule (BR-XXX) from Chapter 3:

#### BR-XXX-001: [Business Rule Name]

**Legacy Technical Approach**: [How the rule is implemented in legacy code - use technical terms]

**Code References**:
- **File**: [filename]
- **Line Numbers**: [start-end]
- **Code Snippet**:
```cobol
[Relevant code snippet]
```

**Legacy Reason**: [Why this technical approach was used - mainframe constraints, performance, etc.]

**Technical Constants**: [Buffer sizes, timeouts, technical thresholds]

**Modern Cloud-Native Equivalent**: [How this would be implemented in modern architecture]

**Migration Guidance**: [Specific guidance for modernizing this rule]

**Obsolescence Flag**: [Obsolete / Still Needed / Requires Review]

---

### 6.3 Function Implementation

For each business function (F-XXX) from Chapter 4:

#### F-XXX-001: [Business Function Name]

**Legacy Technical Approach**: [How the function is implemented - COBOL paragraphs, subroutines]

**Code References**:
- **File**: [filename]
- **Line Numbers**: [start-end]
- **Code Snippet**:
```cobol
[Relevant code snippet]
```

**Technical Parameters**: [COBOL-specific parameters, working storage variables]

**Legacy Reason**: [Why this technical approach was used]

**Modern Cloud-Native Equivalent**: [How this would be implemented as a microservice/function]

**Migration Guidance**: [Specific guidance for modernizing this function]

**Obsolescence Flag**: [Obsolete / Still Needed / Requires Review]

---

### 6.4 Database Tables

| Table Name | Table Type | Columns | Access Patterns | Code References | Modern Equivalent |
|------------|------------|---------|-----------------|-----------------|-------------------|
| [table] | [Internal/Common/External] | [columns] | [SQL/embedded SQL/file I/O] | [file:line] | [DynamoDB/RDS/etc.] |

**Detailed Table Definitions**:

#### [Table Name]

**Columns**:
- [column_name]: [data_type] - [constraints] - [description]

**Access Patterns**: [How the legacy code accesses the table]

**Code References**: [Where table is accessed in source code]

**Modern Equivalent**: [How this would be modeled in modern database]

---

### 6.5 Error Codes

**Error Sets**: [Groupings of related errors]

**Treatment Codes**: [How errors are handled in legacy system]

**Custom Error Codes**:

| Error Code | Description | Raised In | Handled In | Modern Equivalent |
|------------|-------------|-----------|------------|-------------------|
| [code] | [description] | [file:line] | [file:line] | [exception type/logging] |

---

### 6.6 Technical Architecture

**BC Layer**: [Business component layer details]
- **Code References**: [Where implemented]
- **Modern Equivalent**: [Cloud-native equivalent]

**SQLIO Layer**: [Database access layer details]
- **Code References**: [Where implemented]
- **Modern Equivalent**: [Cloud-native equivalent]

**BATCH Layer**: [Batch processing details]
- **Code References**: [Where implemented]
- **Modern Equivalent**: [Cloud-native equivalent]

**Framework**: [Framework components used]
- **Code References**: [Where implemented]
- **Modern Equivalent**: [Cloud-native equivalent]

---

### 6.7 Data Flow Architecture

**Input**: [How data enters the system - screens, files, messages]
- **Code References**: [Where implemented]
- **Modern Equivalent**: [APIs, event streams, etc.]

**Database Access**: [How data is read/written to databases]
- **Code References**: [Where implemented]
- **Modern Equivalent**: [Cloud-native data access]

**Service Calls**: [External system integrations]
- **Code References**: [Where implemented]
- **Modern Equivalent**: [API gateways, service mesh, etc.]

**Output**: [How data exits the system - screens, files, reports]
- **Code References**: [Where implemented]
- **Modern Equivalent**: [APIs, event streams, etc.]

**Error Handling**: [Technical error handling mechanisms]
- **Code References**: [Where implemented]
- **Modern Equivalent**: [Exception handling, logging, monitoring]

---

### 6.8 Technical Rules (Not Business Rules)

**Note**: These are technical rules specific to mainframe implementation that are NOT business requirements.

#### Technical Rule: [Name]

**Description**: [What this technical rule does]

**Code References**: [Where implemented]

**Legacy Reason**: [Why this was needed in mainframe]

**Obsolescence Flag**: [Obsolete / Still Needed / Requires Review]

**Examples**:
- Batch restart logic
- File locking mechanisms
- CICS transaction management
- Buffer management
- Technical workarounds for mainframe constraints

---

## End of Business Specification
