```markdown
# Business Specification: [Workpackage Name]
 
## Document Control
- **Version:** 1.0
- **Date:** YYYY-MM-DD
- **Standard:** IEEE 830-1998
- **Workpackage ID:** [ID from Phase 2]
- **Entry Point:** [Entry point from Phase 2 for the workpackage ID]
- **Business Domain:** [Domain Name]
 
## Table of Contents
1. Introduction
2. Business Entities
3. Business Rules
4. Business Functions
5. Process Flows
6. Legacy Implementation References
 
## 1. Introduction
[Brief description of the workpackage and its business purpose]
 
## 2. Business Entities
### BE-{workpackageID}-001: [Entity Name]
- **Description:** [Entity description]
- **Attributes:**
 
| Attribute | Data Type | Length | Constraints | Description | Legacy Variable | Suggested Variable |
|-----------|-----------|--------|-------------|-------------|-----------------|-------------------|
| [English Name] | [Data Type] | [Length] | [Constraints] | [Description] | [COBOL-VAR-NAME] | [camelCaseVar] |
 
- **Validation Rules:**
  - [Rule description]
  - [Rule description]
 
### BE-{workpackageID}-002: [Entity Name]
[...]
 
## 3. Business Rules
### BR-001: [Rule Name]
- **Description:** [Rule description]
- **Condition:** WHEN [condition] THEN [action]
- **Related Entities:** [BE-{workpackageID}-XXX, BE-{workpackageID}-XXX]
- **Exceptions:** [Exception conditions and handling]
 
### BR-{workpackageID}-002: [Rule Name]
[...]
 
## 4. Business Functions
### F-{workpackageID}-001: [Function Name]
- **Description:** [Function description]
- **Inputs:**
 
| Input | Data Type | Length | Constraints | Description |
|-----------|-----------|--------|-------------|-------------|
| [English Name] | [Data Type] | [Length] | [Constraints] | [Description] |
 
- **Outputs:**
 
| Output | Data Type | Length | Constraints | Description |
|-----------|-----------|--------|-------------|-------------|
| [English Name] | [Data Type] | [Length] | [Constraints] | [Description] |
 
- **Processing Logic:**
  - [Step-by-step description of business logic]
- **Business Rules Applied:** [BR-{workpackageID}-XXX, BR-{workpackageID}-XXX]
 
### F-{workpackageID}-002: [Function Name]
[...]
 
## 5. Process Flows
[Text-based or ASCII diagram of process flows]
 
## 6. Legacy Implementation References
### Source Files
- [File Name]: [Description]
- [File Name]: [Description]
 
### Business Rule Implementation
- **BR-{workpackageID}-001:** Implemented in [File Name] at lines [XXX-XXX]
  ```cobol
  [Relevant code snippet]
  ```
- **BR-{workpackageID}-002:** Implemented in [File Name] at lines [XXX-XXX]
  [...]
 
### Function Implementation
- **F-{workpackageID}-001:** Implemented in [File Name] at lines [XXX-XXX]
  ```cobol
  [Relevant code snippet showing function logic]
  ```
- **F-{workpackageID}-002:** Implemented in [File Name] at lines [XXX-XXX]
  [...]
 
### Database Tables
- **[TABLE_NAME]**: [Table Name] ([English Description]) - [Usage description]
- **[TABLE_NAME]**: [Table Name] ([English Description]) - [Usage description] // Internal 
- (Common) **[TABLE_NAME]**: [Table Name] ([English Description]) - [Usage description]  // Common Table 
- (External) **[TABLE_NAME]**: [Table Name] ([English Description]) - [Usage description]  // External
 
### Error Codes
- **Error Set [SET_NAME]**:
  - **ERROR_CODE**: [ERROR_CODE] - "[Error Message]"
  - **TREATMENT_CODE**: [TREATMENT_CODE] - "[Treatment Message]"  
  - **CUSTOM_CODE**: [CUSTOM_CODE] - "[Custom Message]" (if applicable)
  - **Usage**: [Usage context and file reference]
 
### Technical Architecture
- **BC Layer**: [Component] - [Business Component description] // Online Only
- **SQLIO Layer**: [Components] - [Database access components description]
- **BATCH Layer**: [Component] - [Batch processing component with JCL job description] // Batch Only
- **Framework**: [Framework details and macro usage]
 
### Data Flow Architecture
1. **Input Flow**: [Component] → [Component] → [Component]
2. **Database Access**: [Component] → [Database Components] → [Database Tables]
3. **Service Calls**: [Component] → [Service Components] → [Service Description]
4. **Output Flow**: [Component] → [Component] → [Component]
5. **Error Handling**: [All layers] → [Framework Error Handling] → [User Messages]
```