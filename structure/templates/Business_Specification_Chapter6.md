# Chapter 6: Legacy Implementation References - WP-XXX

---

## Document Control

**Document Type**: Legacy Implementation References (Chapter 6)
**Workpackage ID**: WP-XXX
**Flow ID**: FLOW_XXX
**Version**: 1.0
**Date**: YYYY-MM-DD
**Status**: [Draft / In Review / Approved / Approved with Changes]
**Author**: [Agent/Person Name]
**Reviewer**: [Reviewer Name]
**Review Date**: [YYYY-MM-DD]

---

**Note**: This chapter contains ALL technical implementation details. Use technical terminology and code references. Provide complete traceability to source code.

---

## 6.1 Source Files

| File Name | File Type | Description | Path |
|-----------|-----------|-------------|------|
| [filename] | [COBOL Program/Copybook/JCL/Map/BMS] | [Description] | [path] |

---

## 6.2 Business Rule Implementation

For each business rule pattern identified in legacy code:

### BR-XXX-001: [Business Rule Name]

**Legacy Technical Approach**: [How the rule is implemented in legacy code - use technical terms]

**Code References**:
- **File**: [filename]
- **Line Numbers**: [start-end]
- **Code Snippet**:
```cobol
[Relevant code snippet]
```

**Legacy Reason**: [Why this technical approach was used - mainframe constraints, performance, etc.]

**Technical Constants**: [Buffer sizes, timeouts, technical thresholds, COBOL data types]

**Modern Cloud-Native Equivalent**: [How this would be implemented in modern architecture]

**Migration Guidance**: [Specific guidance for modernizing this rule]

**Obsolescence Flag**: [Obsolete / Still Needed / Requires Review]

---

## 6.3 Function Implementation

For each function/paragraph identified in legacy code:

### F-XXX-001: [Business Function Name]

**Legacy Technical Approach**: [How the function is implemented - COBOL paragraphs, subroutines]

**Code References**:
- **File**: [filename]
- **Line Numbers**: [start-end]
- **Code Snippet**:
```cobol
[Relevant code snippet]
```

**Technical Parameters**: [COBOL-specific parameters, working storage variables with data types]
- Input: [variable] ([PIC clause])
- Output: [variable] ([PIC clause])

**Legacy Reason**: [Why this technical approach was used]

**Modern Cloud-Native Equivalent**: [How this would be implemented as a microservice/function]

**Migration Guidance**: [Specific guidance for modernizing this function]

**Obsolescence Flag**: [Obsolete / Still Needed / Requires Review]

---

## 6.4 Database Tables

| Table Name | Table Type | Columns | Access Patterns | Code References | Modern Equivalent |
|------------|------------|---------|-----------------|-----------------|-------------------|
| [table] | [Internal/Common/External] | [columns] | [SQL/embedded SQL/file I/O] | [file:line] | [DynamoDB/RDS/etc.] |

### Detailed Table Definitions

#### [Table Name]

**Columns**:
- [column_name]: [data_type] [constraints] - [description]

**Access Patterns**: [How the legacy code accesses the table - SELECT, INSERT, UPDATE, DELETE]

**Code References**: [Where table is accessed in source code - file:lines]

**Modern Equivalent**: [How this would be modeled in modern database]

---

## 6.5 Error Codes

**Error Sets**: [Groupings of related errors - e.g., Validation Errors, Database Errors, Business Logic Errors]

**Treatment Codes**: [How errors are handled in legacy system - ABEND, WARN, REJECT]

**Custom Error Codes**:

| Error Code | Description | Raised In | Handled In | Modern Equivalent |
|------------|-------------|-----------|------------|-------------------|
| [code] | [description] | [file:line] | [file:line] | [HTTP status/exception type] |

---

## 6.6 Technical Architecture

**BC Layer** (Business Component):
- Purpose: [Layer purpose]
- Components: [List of components]
- Code References: [paths]
- Modern Equivalent: [Cloud-native equivalent]

**SQLIO Layer** (Database Access):
- Purpose: [Layer purpose]
- Components: [List of components]
- Code References: [paths]
- Modern Equivalent: [Cloud-native equivalent]

**BATCH Layer** (Batch Processing):
- Purpose: [Layer purpose]
- Components: [List of components]
- Code References: [paths]
- Modern Equivalent: [Cloud-native equivalent]

**Framework** (Common Utilities):
- Purpose: [Layer purpose]
- Components: [List of components]
- Code References: [paths]
- Modern Equivalent: [Cloud-native equivalent]

---

## 6.7 Data Flow Architecture

**Input**: [How data enters the system - screens, files, messages]
- Entry Point: [program/transaction]
- Input Data: [description]
- Code References: [file:lines]
- Modern Equivalent: [APIs, event streams, etc.]

**Database Access**: [How data is read/written to databases]
- Read: [tables/operations]
- Write: [tables/operations]
- Code References: [file:lines]
- Modern Equivalent: [Cloud-native data access]

**Service Calls**: [External system integrations]
- External Call: [description]
- Purpose: [why called]
- Code References: [file:lines]
- Modern Equivalent: [API gateways, service mesh, etc.]

**Output**: [How data exits the system - screens, files, reports]
- Success: [description]
- Failure: [description]
- Code References: [file:lines]
- Modern Equivalent: [APIs, event streams, etc.]

**Error Handling**: [Technical error handling mechanisms]
- Error Handler: [program/paragraph]
- Logging: [mechanism]
- Code References: [file:lines]
- Modern Equivalent: [Exception handling, logging, monitoring]

---

## 6.8 Technical Rules (Not Business Rules)

**Note**: These are technical rules specific to mainframe implementation that are NOT business requirements. They represent technical workarounds and constraints.

### Technical Rule: [Name]

**Description**: [What this technical rule does]

**Code References**:
- File: [filename]
- Lines: [start-end]

**Legacy Reason**: [Why this was needed in mainframe]

**Obsolescence Flag**: [Obsolete / Still Needed / Requires Review]

---

**Examples of Technical Rules**:
- Batch restart/checkpoint logic
- File locking mechanisms
- CICS transaction management
- Buffer management
- Technical workarounds for mainframe constraints

---

## End of Chapter 6

