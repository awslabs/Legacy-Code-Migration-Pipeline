I'll now provide the complete Phase 3.1 and Phase 3.2 prompts that work with your exact template structure.

Phase 3.1: Business Specification Extraction (COMPLETE)

Orchestration Information

Phase: Phase 3 - Business Specification
Step: Step 3.1 - Business Specification Extraction
Team Supervisor: businessteamsupervisor
Assigned Agent: businessspecialistlogic_extraction
Task File Name: {{TASKSBASEPATH}}/businessspecificationextraction_task.md

Expected Deliverables
Business Specification Documents
• File: {{BUSINESSSPECIFICATIONBASEPATH}}/WP-XXX-FLOWXXX-specification-EN.md
• File: {{BUSINESSSPECIFICATIONBASEPATH}}/WP-XXX-FLOWXXX-specification-DN.md
• Template: {{BUSINESSSPECIFICATIONTEMPLATE}}
• Description: IEEE 830-1998 formatted business specifications for each workpackage flow (English and Danish versions)
Progress Tracking
• File: {{BUSINESSSPECIFICATIONSTATUS}}
• Template: {{BUSINESSSPECIFICATIONSTATUS_TEMPLATE}}
• Description: Business extraction progress and status tracking
Review Files
• File: {{BUSINESSSPECIFICATIONREVIEW}}/business-extraction-WP-XXX-review.md
• Description: Review documentation for each workpackage (created by reviewer)
Error Reports (if applicable)
• File: {{BUSINESSSPECIFICATIONERRORS}}
• Template: {{BUSINESSSPECIFICATIONERRORS_TEMPLATE}}
• Description: Documentation of errors and issues encountered

Success Criteria
• [ ] All workpackage flows have business specifications created (EN and DN versions)
• [ ] All business entities extracted at business concept level (not just cleaned code structures)
• [ ] All business rules identified and cataloged (business policies separated from technical rules)
• [ ] All business functions and processes specified
• [ ] IEEE 830-1998 standard compliance verified
• [ ] Technology-agnostic documentation achieved (Chapters 1-5)
• [ ] Legacy implementation references complete (Chapter 6)
• [ ] Business context from Phase 3.0 incorporated throughout
• [ ] EN and DN versions have identical structure and content
• [ ] All deliverables produced at specified paths
• [ ] Quality criteria met
• [ ] Ready for Phase 3.2 review

For Team Supervisor: Task File Creation

When creating the task file for this step:
Extract from this prompt:
• Objective section: Extract business specifications using business context from Phase 3.0
• Detailed instructions: All Steps 1-13 below
• Technical specifications: IEEE 830-1998 format, generic data types, camelCase naming conventions
• Business rules and constraints: Technology-agnostic documentation, business vs technical rule distinction, business context integration
• Error handling guidance: Incomplete legacy code, ambiguous business logic, complex technical implementation
• Output format requirements: Business specification documents (EN and DN), progress tracking
• Quality criteria: IEEE compliance, business rule quality, entity completeness, technology independence, traceability, business context alignment
Add project context:
• Project name: {{PROJECT_NAME}}
• Project base path: {{PROJECTBASEPATH}}
• All input locations (resolved paths):
• Business context documents: {{BUSINESSCONTEXTBASE_PATH}}
• Business glossary: {{BUSINESSCONTEXTBASE_PATH}}/business-glossary.md
• Workpackage definitions: {{PROJECTBASEPATH}}/output/migration/workpackage_definition/
• Source code files: {{SOURCE_CODE}}
• Database source code: {{DATABASESOURCECODE}}
• Legacy specifications: {{PROJECTBASEPATH}}/input/legacy_specifications/
• Module dependency table: {{DEPENDENCYANALYSISTABLE}}
• All output locations (resolved paths):
• Business specifications: {{BUSINESSSPECIFICATIONBASE_PATH}}
• Review files: {{BUSINESSSPECIFICATIONREVIEW}}
• Reporting: {{BUSINESSSPECIFICATIONREPORTING}}
• Progress tracking: {{BUSINESSSPECIFICATIONSTATUS}}
• Error reports: {{BUSINESSSPECIFICATIONERRORS}}
• Task files location: {{TASKSBASEPATH}}
• All template locations (resolved paths):
• Business specification template: {{BUSINESSSPECIFICATIONTEMPLATE}}
• Status template: {{BUSINESSSPECIFICATIONSTATUS_TEMPLATE}}
• Errors template: {{BUSINESSSPECIFICATIONERRORS_TEMPLATE}}
Reference agent definition:
• Agent name: businessspecialistlogic_extraction
• Agent definition file: structure/agents/businessteam/businessspecialistlogicextraction.md
• Note: Don't duplicate agent definition, just reference it
Dependencies from previous phases:
This step requires outputs from Phase 3.0 (Business Context Discovery):
• From Phase 3.0: Business context documents, business glossary
• From Phase 1: Source code analysis, dependency analysis table, module classifications, business flows
• From Phase 2: Workpackage definitions with prioritized flows
• Verify these artifacts exist before creating the task file

Context
• Input Locations:
• Business context documents: {{BUSINESSCONTEXTBASE_PATH}}/WP-XXX-business-context.md
• Business glossary: {{BUSINESSCONTEXTBASE_PATH}}/business-glossary.md
• Prioritized migration roadmap: {{PROJECTBASEPATH}}/output/migration/workpackage_definition/
• Source code files: {{SOURCE_CODE}}
• Database source code: {{DATABASESOURCECODE}}
• Database table definitions (if available)
• Legacy framework documentation: {{PROJECTBASEPATH}}/input/legacy_specifications/
• Module dependency table: {{DEPENDENCYANALYSISTABLE}}
• Output Locations:
• IEEE-formatted business specifications: {{BUSINESSSPECIFICATIONBASE_PATH}}
• English versions: WP-XXX-FLOW_XXX-specification-EN.md
• Danish versions: WP-XXX-FLOW_XXX-specification-DN.md
• Review: {{BUSINESSSPECIFICATIONREVIEW}}/business-extraction-WP-XXX-review.md
• (IMPORTANT: Reviewer must create review files, NOT output to STDOUT)
• Reporting: {{BUSINESSSPECIFICATIONREPORTING}}
• Progress Tracking: {{BUSINESSSPECIFICATIONSTATUS}}
• Error Reports: {{BUSINESSSPECIFICATIONERRORS}}
• Task files location: {{TASKSBASEPATH}}
• Previous Phase Artifacts:
• Business context documents with business domain, stakeholders, vocabulary, constraints
• Business glossary with consolidated terminology
• Workpackage definitions with prioritized flows
• Source code analysis with module classifications
• Dependency graphs and business domain assignments

Objective

Extract business specifications from legacy code using the business context established in Phase 3.0. Create comprehensive IEEE 830-1998 formatted specifications that document business requirements (Chapters 1-5) separately from legacy implementation details (Chapter 6). Focus on extracting business concepts, policies, and processes rather than translating code structures.

CRITICAL PRINCIPLES:
Use business context to guide extraction - Reference Phase 3.0 business context throughout
Extract business concepts, not code structures - Ask "What business concept does this represent?" not "What are the fields?"
Distinguish business rules from technical rules - Business rules would exist in any implementation; technical rules are mainframe-specific
Focus on business intent, not implementation patterns - Document what the business requires, not how the code implements it
Maintain technology-agnostic language in Chapters 1-5 - No COBOL, mainframe, or technical jargon
Preserve full traceability in Chapter 6 - Complete legacy implementation details with code references

Instructions
Preparation and Context Review
Review the workpackage definitions from Phase 2
CRITICAL: For each workpackage, review the business context document from Phase 3.0:
• Business domain and capability
• Business stakeholders
• Business problem statement
• Business vocabulary and glossary
• Business constraints and policies
• Business outcomes and value
Review the consolidated business glossary
For each workpackage, in priority order:
• Identify all relevant source files (programs, copybooks, includes, JCL, maps, etc.)
• Locate the entry points and end-to-end flows
• Prepare to extract business specifications using business context as the lens
Chapter 1: Introduction (Enhanced with Business Context)
Use Phase 3.0 business context to populate Chapter 1:
• Section 1.1 - Purpose:
• Business domain and capability (from Phase 3.0)
• Business problem statement (from Phase 3.0)
• Business value and outcomes (from Phase 3.0)
• Section 1.2 - Scope:
• Business stakeholders (from Phase 3.0)
• Business processes covered
• Business boundaries (what's included/excluded)
• Section 1.3 - Business Context:
• Why this functionality exists (from Phase 3.0)
• Business constraints and policies (high-level from Phase 3.0)
• Business vocabulary reference (link to glossary)
Write Chapter 1 from business perspective:
• Use business terminology from Phase 3.0 glossary
• Focus on business needs and value
• Avoid technical implementation details
• Make it readable by business specialists who have never seen the code
Chapter 2: Business Entity Extraction (Business Concept Level)
CRITICAL: Extract business entities at the business concept level, not code structure level:
• Ask: "What real-world business concept does this data structure represent?"
• Not: "What are the fields in this COBOL record?"
For each identified business entity:
• Use business vocabulary from Phase 3.0 glossary
• Identify business entity name: Use business terms (Customer, Order, Payment) not technical terms (CUST-REC, ORD-FILE)
• Extract business attributes: Use business attribute names from glossary (creditLimit, orderTotal, paymentStatus)
• Convert variable names to camelCase following these rules:
Remove program-specific prefixes (e.g., XDIPA501-, WS-, LS-, etc.)
Remove direction indicators (I-, O-, IO-)
Convert remaining hyphenated parts to camelCase
Examples: XDIPA501-I-CORP-CLCT-GROUP-CD → corpClctGroupCd, WS-CUSTOMER-NAME → customerName
• Use generic data types: String, Numeric, Date, Timestamp, Boolean (not COBOL-specific types)
• Provide "N/A" as data length for data objects (Date, Timestamp, Boolean), but keep the length for concrete data types (String, Numeric)
• Intelligently convert data types to the most appropriate ones for the task (e.g., use Date with Length "N/A" instead of a String for 'YYYYMMDD')
• Document business validation rules (not technical constraints like buffer sizes)
• Align with database table definitions when available
• Assign unique identifiers using BE-{workpackageID}-XXX numbering system (e.g., BE-001-001)
Business entity relationships:
• Document business relationships (Customer HAS-MANY Orders, Order HAS-ONE Payment)
• Use business terms to describe relationships
• Focus on business meaning, not technical foreign keys
Distinguish business attributes from technical attributes:
• Business attributes: Represent business concepts (creditLimit, orderDate, customerName)
• Technical attributes: Implementation details (recordLength, bufferSize, lockFlag)
• Document business attributes in Chapter 2
• Document technical attributes in Chapter 6 (Legacy Implementation)
Chapter 3: Business Rule Extraction (Business Policy Level)
CRITICAL: Extract business rules that represent business policies, not code patterns:
• Ask: "What business decision or policy is being enforced and why?"
• Not: "What conditional logic exists in the code?"
Use business context from Phase 3.0 to interpret rule intent:
• Reference business constraints and policies from Phase 3.0
• Use business vocabulary from glossary
• Focus on business rationale, not technical implementation
For each flow in the workpackage:
• Identify business decisions: What business decision is being made?
• Extract business constraints: What business policy is being enforced?
• Document business conditions: When does this rule apply? (in business terms)
• Document business actions: What happens when the rule is triggered? (in business terms)
• Document business rationale: Why does this rule exist? (if discernible from context or comments)
• Include business constants: Credit limits, thresholds, business dates (not technical constants like buffer sizes, timeouts)
Business rule format (WHEN/THEN structure):
Distinguish business rules from technical rules:
• Business rules: Would exist in any implementation (credit limits, validation rules, approval workflows)
• Example: "Orders must not be accepted if the total order value exceeds the customer's available credit limit"
• Technical rules: Specific to mainframe implementation (batch restart logic, file locking, CICS transaction timeouts)
• Example: "If CICS transaction times out after 30 seconds, rollback and retry"
• Document business rules in Chapter 3
• Document technical rules in Chapter 6 (Legacy Implementation)
Business rule abstraction level:
• Too concrete (code-level): "If customer credit limit field is less than order amount field, reject transaction"
• Too abstract (useless): "System must validate customer eligibility"
• Right level (business requirement): "Orders must not be accepted if the total order value exceeds the customer's available credit limit. Available credit = Credit Limit - Outstanding Balance."
Assign unique identifiers using BR-{workpackageID}-XXX numbering system (e.g., BR-001-001)
Chapter 4: Business Function Identification (Business Capability Level)
CRITICAL: Extract business functions that represent business capabilities, not program subroutines:
• Ask: "What business capability or operation does this perform?"
• Not: "What does this PERFORM paragraph do?"
For each flow in the workpackage:
• Identify business functions: Cohesive units of business functionality
• Use business vocabulary: Function names should use business terms from glossary
• Document business inputs: What business information is required? (not technical parameters)
• Document business outputs: What business information is produced? (not technical return codes)
• Document business processing logic: What business operations are performed? (in business terms)
• Map relationships to business rules: Which business rules apply to this function?
• Assign unique identifiers using F-{workpackageID}-XXX numbering system (e.g., F-001-001)
Business function format:
Focus on business operations, not technical implementation:
• Good: "Validate customer credit eligibility by comparing order total against available credit"
• Bad: "Call VALIDATE-CREDIT subroutine passing WS-CREDIT-LIM and WS-ORDER-AMT"
Chapter 5: Process Flow Extraction (Business Process Level)
CRITICAL: Extract business process flows, not program call graphs:
• Ask: "What business process is being executed and what are the business activities?"
• Not: "What is the sequence of PERFORM statements?"
For each flow in the workpackage:
• Identify business process: What business process is being implemented? (from Phase 3.0 context)
• Extract business activities: What business operations occur? (not program calls)
• Identify business decision points: Where are business decisions made? (not IF statements)
• Document business actors: Who performs each activity? (from Phase 3.0 stakeholders)
• Describe business events: What triggers the process? What are the outcomes?
Business process flow format (text-based):
Use business vocabulary throughout:
• Business activities (not program names)
• Business decision points (not conditional statements)
• Business actors (not transaction codes)
• Business outcomes (not return codes)
Chapter 6: Legacy Implementation References (Comprehensive Technical Details)
CRITICAL: Chapter 6 contains ALL technical implementation details:
• This is where you document HOW the legacy system implements the business requirements
• Use technical terminology and code references
• Provide complete traceability to source code
Section 6.1: Source Files
• List all source files involved (programs, copybooks, includes, JCL, maps)
• Provide file paths and descriptions
• Note file types and purposes
Section 6.2: Business Rule Implementation
• For each business rule (BR-XXX) from Chapter 3:
• Legacy Technical Approach: How the rule is implemented in legacy code
• Code References: Specific source files, line numbers, and code snippets
• Legacy Reason: Why this technical approach was used (mainframe constraints, performance, etc.)
• Technical Constants: Buffer sizes, timeouts, technical thresholds
• Modern Cloud-Native Equivalent: How this would be implemented in modern architecture
• Migration Guidance: Specific guidance for modernizing this rule
• Obsolescence Flag: Is this rule obsolete or still needed?
Section 6.3: Function Implementation
• For each business function (F-XXX) from Chapter 4:
• Legacy Technical Approach: How the function is implemented (COBOL paragraphs, subroutines)
• Code References: Specific source files, line numbers, and code snippets
• Technical Parameters: COBOL-specific parameters, working storage variables
• Legacy Reason: Why this technical approach was used
• Modern Cloud-Native Equivalent: How this would be implemented as a microservice/function
• Migration Guidance: Specific guidance for modernizing this function
• Obsolescence Flag: Is this function obsolete or still needed?
Section 6.4: Database Tables
• For each database table accessed:
• Table Name: Physical table name
• Table Type: Internal, Common, or External
• Columns: Column names, data types, constraints
• Access Patterns: How the legacy code accesses the table (SQL, embedded SQL, file I/O)
• Code References: Where table is accessed in source code
• Modern Equivalent: How this would be modeled in modern database (DynamoDB, RDS, etc.)
Section 6.5: Error Codes
• Error Sets: Groupings of related errors
• Treatment Codes: How errors are handled in legacy system
• Custom Error Codes: Application-specific error codes
• Code References: Where errors are raised and handled
• Modern Equivalent: How errors would be handled in modern architecture (exceptions, logging, monitoring)
Section 6.6: Technical Architecture
• BC Layer: Business component layer details
• SQLIO Layer: Database access layer details
• BATCH Layer: Batch processing details
• Framework: Framework components used
• Code References: Where each layer is implemented
• Modern Equivalent: How this would be architected in cloud-native design
Section 6.7: Data Flow Architecture
• Input: How data enters the system (screens, files, messages)
• Database Access: How data is read/written to databases
• Service Calls: External system integrations
• Output: How data exits the system (screens, files, reports)
• Error Handling: Technical error handling mechanisms
• Code References: Where each data flow is implemented
• Modern Equivalent: How data would flow in modern architecture (APIs, event streams, etc.)
Technical rule documentation (rules that are NOT business rules):
• Batch restart logic
• File locking mechanisms
• CICS transaction management
• Buffer management
• Technical workarounds for mainframe constraints
• Code References: Where implemented
• Obsolescence Flag: Mark as obsolete if not needed in modern architecture
Technology-Agnostic Documentation (Chapters 1-5)
CRITICAL: Ensure Chapters 1-5 are completely technology-agnostic:
• No references to: COBOL, CICS, JCL, DB2, mainframe, batch, online, transaction, file, record, paragraph, PERFORM, MOVE, etc.
• Use instead: Business terms from Phase 3.0 glossary
• Focus on: Business requirements, business policies, business processes, business entities, business rules
Test for technology-agnosticism:
• Could a business specialist who has never seen COBOL understand Chapters 1-5?
• Could these requirements be implemented in Python, Java, or any other language?
• Are all business concepts described in business terms?
Preserve business logic without technical constraints:
• Document what the business requires, not how mainframe implements it
• Remove technical workarounds and constraints from business requirements
• Focus on business intent and outcomes
Bilingual Documentation (English and Danish)
Create both EN and DN versions for each workpackage:
• WP-XXX-FLOW_XXX-specification-EN.md (English)
• WP-XXX-FLOW_XXX-specification-DN.md (Danish)
Ensure identical structure and content:
• Same number of business entities (BE-XXX)
• Same number of business rules (BR-XXX)
• Same number of business functions (F-XXX)
• Same business logic and requirements
• Same Chapter 6 technical details
Danish terminology alongside English:
• Use format: "English Term (DANISH TERM)"
• Example: "Creation Initials (SKABELSESINITIALER)"
• Maintain consistency with existing Danish business vocabulary
Translate business concepts, not technical terms:
• Business terms should be translated
• Technical terms in Chapter 6 can remain in English (COBOL, CICS, etc.)
• Code snippets remain in original language
Validation and Completeness Check
For each completed business specification:
• Chapter 1: Business context from Phase 3.0 incorporated
• Chapter 2: Business entities at business concept level (not code structures)
• Chapter 3: Business rules represent business policies (technical rules in Chapter 6)
• Chapter 4: Business functions represent business capabilities
• Chapter 5: Business process flows use business terminology
• Chapter 6: Complete legacy implementation details with code references
• Technology-agnostic: Chapters 1-5 have no technical jargon
• Traceability: All business requirements traced to legacy code in Chapter 6
• Bilingual: EN and DN versions have identical structure and content
Cross-reference with Phase 3.0 business context:
• Business domain matches Phase 3.0
• Business stakeholders documented in Chapter 1
• Business vocabulary from glossary used throughout
• Business constraints from Phase 3.0 reflected in business rules
• Business outcomes from Phase 3.0 reflected in process flows
Verify business vs technical separation:
• All business requirements in Chapters 1-5
• All technical implementation in Chapter 6
• No technical jargon in Chapters 1-5
• Complete technical details in Chapter 6
Progress Tracking
Update progress tracking for each completed workpackage:
• Record completion status and artifacts (EN and DN versions)
• Document any issues or exceptions
• ENSURE reviewer creates review file in {{BUSINESSSPECIFICATIONREVIEW}} directory
• Update phase status in progress tracking system
• Note confidence levels and areas requiring BA input
Quality Assurance
Before marking workpackage as complete:
• Run technology-agnostic test on Chapters 1-5
• Verify all business entities use business vocabulary from Phase 3.0
• Verify all business rules represent business policies (not code patterns)
• Verify all business functions represent business capabilities (not subroutines)
• Verify Chapter 6 has complete technical details with code references
• Verify EN and DN versions are identical in structure and content
• Verify all BE-XXX, BR-XXX, F-XXX identifiers are unique and sequential
Pause Before Progressing to Next Workpackage
• Do not proceed to next workpackage until current workpackage is complete and validated
• Ensure both EN and DN versions are created
• Ensure review file is ready for Phase 3.2

Output Format

Business Specification Document (English)
File: {{BUSINESSSPECIFICATIONBASEPATH}}/WP-XXX-FLOWXXX-specification-EN.md
Template: {{BUSINESSSPECIFICATIONTEMPLATE}}

Structure (6 Chapters):
Introduction (Enhanced with Phase 3.0 business context)
Business Entities (Business concept level with BE-XXX identifiers)
Business Rules (Business policy level with BR-XXX identifiers)
Business Functions (Business capability level with F-XXX identifiers)
Process Flows (Business process level in text format)
Legacy Implementation References (Comprehensive technical details)

Business Specification Document (Danish)
File: {{BUSINESSSPECIFICATIONBASEPATH}}/WP-XXX-FLOWXXX-specification-DN.md
Template: {{BUSINESSSPECIFICATIONTEMPLATE}}

Structure: Identical to English version with Danish translations

Progress Tracking
File: {{BUSINESSSPECIFICATIONSTATUS}}
Template: {{BUSINESSSPECIFICATIONSTATUS_TEMPLATE}}

Error Reports
File: {{BUSINESSSPECIFICATIONERRORS}}
Template: {{BUSINESSSPECIFICATIONERRORS_TEMPLATE}}

Quality Criteria

IEEE Standard Compliance
• Document follows IEEE 830-1998 Software Requirements Specification format
• All sections are properly numbered and structured
• Document control information is complete and accurate
• Requirements are uniquely identified and traceable (BE-XXX, BR-XXX, F-XXX)

Business Context Integration
• Chapter 1 incorporates business context from Phase 3.0
• Business domain, stakeholders, and problem statement clearly documented
• Business vocabulary from Phase 3.0 glossary used throughout
• Business constraints and policies from Phase 3.0 reflected in business rules

Business Entity Quality
• Entities represent business concepts (not code structures)
• Entity names use business vocabulary from Phase 3.0 glossary
• Attributes are business-meaningful (not technical fields)
• Generic data types used (String, Numeric, Date, Timestamp, Boolean)
• Variable names converted to camelCase (removing prefixes: XDIPA501-, WS-, LS-, I-, O-, IO-)
• Business validation rules documented (not technical constraints)
• Unique BE-XXX identifiers assigned

Business Rule Quality
• Rules represent business policies (not code patterns)
• Rules are described in business terms using Phase 3.0 vocabulary
• Each rule has clear WHEN/THEN format with business rationale
• Business rules distinguished from technical rules (technical rules in Chapter 6)
• Business constants included (credit limits, thresholds) not technical constants (buffer sizes)
• Unique BR-XXX identifiers assigned
• Rules are specific enough to be testable but abstract enough to be implementation-independent

Business Function Quality
• Functions represent business capabilities (not program subroutines)
• Function names use business vocabulary from Phase 3.0 glossary
• Inputs/outputs described in business terms (not technical parameters)
• Processing logic described in business terms (not code implementation)
• Relationships to business rules clearly mapped
• Unique F-XXX identifiers assigned

Business Process Quality
• Process flows represent business processes (not program call graphs)
• Activities described in business terms (not program names)
• Decision points are business decisions (not IF statements)
• Actors are business roles from Phase 3.0 stakeholders (not transaction codes)
• Outcomes described in business terms (not return codes)
• Business value clearly articulated

Technology Independence (Chapters 1-5)
• No references to COBOL, CICS, JCL, DB2, mainframe, or technical jargon
• Business logic described without implementation details
• Generic business terminology used throughout
• Business intent clearly separated from implementation approach
• Readable by business specialists who have never seen the code

Legacy Implementation Completeness (Chapter 6)
• All technical implementation details documented
• Code references include specific file names and line numbers
• Code snippets provided for key implementations
• Database tables documented with access patterns
• Error codes and handling documented
• Technical architecture layers documented
• Data flow architecture documented
• Legacy reason and modern equivalent provided for each component
• Obsolescence flags assigned
• Technical rules (not business rules) documented

Traceability
• Each business entity traced to legacy data structures in Chapter 6
• Each business rule traced to legacy implementation in Chapter 6
• Each business function traced to legacy code in Chapter 6
• Source file references include specific line numbers
• All legacy functionality accounted for in business specifications
• Clear mapping between business requirements (Chapters 1-5) and legacy implementation (Chapter 6)

Bilingual Consistency
• EN and DN versions have identical structure
• Same number of BE-XXX, BR-XXX, F-XXX identifiers
• Same business logic and requirements
• Danish terminology alongside English where appropriate
• Both versions complete and validated

Error Handling

Common Error Scenarios
Incomplete Legacy Code
• Detection: Missing files or incomplete code sections
• Recovery: Document the gap in Chapter 6 and proceed with available information
• Escalation: Flag for human review if critical business functionality is affected
Ambiguous Business Logic
• Detection: Multiple interpretations of code logic possible
• Recovery: Use Phase 3.0 business context to guide interpretation; document all possible interpretations with confidence levels
• Escalation: Request human clarification for critical business rules
Complex Technical Implementation
• Detection: Highly technical code with unclear business intent
• Recovery: Focus on observable behavior and inputs/outputs; use Phase 3.0 business context to infer intent
• Escalation: Flag for expert review if business intent cannot be determined
Missing Database Definitions
• Detection: Unable to align with database table definitions
• Recovery: Create entity definitions based on code usage patterns and Phase 3.0 business vocabulary
• Escalation: Document assumptions made and flag for validation
Business vs Technical Rule Ambiguity
• Detection: Unclear whether a rule is business policy or technical constraint
• Recovery: Use Phase 3.0 business context to determine; if still unclear, document in both Chapter 3 and Chapter 6 with note
• Escalation: Flag for BA review in Phase 3.2
Missing Business Context
• Detection: Phase 3.0 business context document incomplete or missing
• Recovery: Proceed with code analysis but document lower confidence level
• Escalation: Flag for BA review and request Phase 3.0 completion
Bilingual Translation Issues
• Detection: Difficulty translating business concepts to Danish
• Recovery: Use English term with Danish equivalent in parentheses
• Escalation: Flag for native Danish speaker review

Error Reporting Format
File: {{BUSINESSSPECIFICATIONERRORS}}
Template: {{BUSINESSSPECIFICATIONERRORS_TEMPLATE}}

Structure:

Fallback Strategies
• When business context is incomplete, use code patterns and naming to infer business intent
• When business vs technical distinction is unclear, document in both locations with cross-reference
• When business vocabulary is missing, create reasonable business terms and flag for BA validation
• Focus on completing specifications over perfect accuracy
• Flag all uncertainties for Phase 3.2 review
• Prioritize business requirements extraction over technical details
• Use Phase 3.0 business context as primary guide for all extraction decisions