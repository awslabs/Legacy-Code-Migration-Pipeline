Phase 3: Business Specification Extraction - Process Guide (v2.0)

Overview

Phase 3 transforms legacy COBOL code into modern, technology-agnostic business specifications through a six-phase workflow. The goal is to extract reimagined business requirements (what the business needs) rather than translated code structures (how COBOL implements it).

Key Principle: We're not translating COBOL to modern code—we're rediscovering the business intent buried in decades-old implementations.

Critical Quality Control: Chapter 6 (Legacy Implementation References) serves as the evidence base and drift detection mechanism. All business abstractions in Chapters 1-5 must be traceable to code evidence in Chapter 6.

The Six-Phase Workflow

Phase 3.0: Business Context Discovery

Agent: business_specialist_requirements
Purpose: Understand the business landscape BEFORE diving into code details.

What Happens:
• Business Domain Identification: What business area does this code support? (e.g., Order Management, Customer Service, Billing)
• Stakeholder Analysis: Who uses this functionality? Who owns the business process?
• Business Vocabulary Extraction: What business terms are used? (Customer, Order, Payment—not CUST-REC, ORD-FILE)
• Business Problem Statement: What business problem does this solve? Why does it exist?
• Business Constraints: What business policies are enforced? (credit limits, validation rules, approval workflows)

Deliverables:
• Business Context Document (one per workpackage)
• Consolidated Business Glossary (shared across all workpackages)

Why This Matters: Without business context, you'll translate COBOL structures instead of extracting business concepts. This phase ensures you understand the "why" before documenting the "what."

Phase 3.0.1: Business Context Review

Agent: business_reviewer_requirements
Purpose: Validate business context accuracy before proceeding to logic extraction.

What Happens:
• Verify business domain identification accuracy
• Validate stakeholder completeness
• Check business vocabulary consistency
• Confirm business problem statement clarity
• Assess confidence levels

Deliverables:
• Business Context Review Report
• Approved or revised Business Context Document

Why This Matters: Ensures the foundation for logic extraction is solid, preventing cascading errors in subsequent phases.

Phase 3.1: Business Logic Extraction

Agent: business_specialist_logic_extraction
Purpose: Extract business logic patterns and create Chapter 6 evidence base.

What Happens:

Evidence-Based Extraction:
• Extract business logic patterns from code with full traceability
• Document ALL technical implementation details in Chapter 6
• Create evidence base for business abstractions
• Apply allowed abstraction patterns only:
  - DATA_TYPE: PIC X(8) date → Date type
  - CONSOLIDATION: 8 validation steps → "must be valid date"
  - NAMING: CUST-REC → Customer
  - STRUCTURE: Flat records → normalized entities
  - LOGIC: Code patterns → business intent
  - PROCESS: Call graphs → business workflows

Forbidden Patterns (Analysis Drift):
• Adding functionality not in code (e.g., timezone handling if not present)
• Inventing entities not in database (e.g., email if not in schema)
• Assuming standard patterns (e.g., fiscal year if not implemented)
• Extrapolating beyond code evidence

Chapter 6 Creation:
• Complete technical implementation details
• Code references (file names, line numbers, snippets)
• Database tables and access patterns
• Error codes and handling
• Technical architecture layers
• Legacy reason and modern equivalent for each component

Deliverables:
• Chapter 6: Legacy Implementation References (complete evidence base)
• Logic Extraction Notes (patterns identified, abstractions applied)

Why This Matters: Chapter 6 becomes the control mechanism for drift detection. Every business abstraction must trace to code evidence documented here.

Phase 3.1.1: Business Logic Extraction Review

Agent: business_reviewer_logic_extraction
Purpose: Validate logic extraction accuracy and abstraction appropriateness.

What Happens:

Abstraction Validation:
• Verify all abstractions follow allowed patterns
• Check for forbidden patterns (drift indicators)
• Validate evidence completeness in Chapter 6
• Confirm traceability from code to abstractions

Drift Detection:
• Scan for added functionality not in code
• Check for invented entities not in database
• Verify no assumptions beyond code evidence
• Flag any extrapolations

Deliverables:
• Logic Extraction Review Report
• Drift Detection Report (if issues found)
• Approved or revised Chapter 6

Why This Matters: Prevents analysis drift early, before it propagates to the business specification.

Phase 3.2: Business Specification Generation

Agent: business_specialist_requirements
Purpose: Create business specification (Chapters 1-5) using approved Chapter 6 as evidence base.

What Happens:

Chapter 1: Introduction (Enhanced with Business Context)
• Business domain, stakeholders, and problem statement from Phase 3.0
• Business value and outcomes
• Written for business analysts who have never seen the code

Chapter 2: Business Entities (Business Concept Level)
• Real business concepts (Customer, Order, Payment) with business attributes
• Generic data types (String, Numeric, Date, Timestamp, Boolean)
• Business validation rules (not technical constraints)
• Every entity must trace to Chapter 6 evidence

Chapter 3: Business Rules (Business Policy Level)
• Business policies (Orders must not exceed customer credit limits)
• WHEN/THEN format with business rationale
• Every rule must trace to Chapter 6 code references
• Technical rules (batch restart, file locking) remain in Chapter 6

Chapter 4: Business Functions (Business Capability Level)
• Business capabilities (Validate Customer Credit Eligibility)
• Inputs/outputs in business terms
• Every function must trace to Chapter 6 implementation

Chapter 5: Process Flows (Business Process Level)
• Business processes with activities, decision points, and actors
• Business outcomes and value
• Every process must trace to Chapter 6 code flow

Evidence-Based Specification:
• All business elements must reference Chapter 6 evidence
• Use approved abstractions from Phase 3.1.1
• Apply business vocabulary from Phase 3.0.1
• Maintain traceability throughout

Critical Separation:
• Chapters 1-5: Technology-agnostic business requirements
• Chapter 6: Complete legacy technical implementation (already created in Phase 3.1)

Deliverables:
• Business Specification Chapters 1-5
• Traceability Matrix (business elements → Chapter 6 references)

Why This Matters: Evidence-based specification prevents drift by requiring explicit traceability to Chapter 6 for every business element.

Phase 3.2.1: Business Specification Review

Agent: business_reviewer_requirements
Purpose: Validate specifications against Chapter 6 evidence and detect drift.

What Happens:

Backward Validation Protocol:
• Sample 20% of business elements (entities, rules, functions)
• For each sampled element, validate against Chapter 6:
  - Does Chapter 6 evidence support this business element?
  - Is the abstraction appropriate (allowed patterns only)?
  - Are there any drift indicators (forbidden patterns)?
• Calculate drift percentage: (drift_count / sample_count) × 100
• If drift ≥ 5%, perform full validation of all elements

Chapter-by-Chapter Review:
• Chapter 1: Business context accuracy, stakeholder completeness
• Chapter 2: Business entities trace to Chapter 6, appropriate abstractions
• Chapter 3: Business rules trace to Chapter 6 code, no invented policies
• Chapter 4: Business functions trace to Chapter 6 implementation
• Chapter 5: Business processes trace to Chapter 6 code flow
• Chapter 6: Already validated in Phase 3.1.1

Cross-Cutting Verification:
• Technology-Agnostic Language: Scan Chapters 1-5 for technical jargon
• Business Vocabulary Consistency: Terms match Phase 3.0.1 glossary
• Traceability: All business requirements traced to Chapter 6

Drift Detection Metrics:
• Added functionality count (forbidden)
• Invented entities count (forbidden)
• Assumed patterns count (forbidden)
• Appropriate abstractions count (allowed)
• Drift percentage: (forbidden / total) × 100

Approval Decision:
• Approved: Drift < 5%, ready for code generation
• Approved with Changes: Minor fixes applied, drift < 5%
• Rejected: Drift ≥ 5%, return to Phase 3.2 with specific corrections

Deliverables:
• Reviewed Business Specification (EN and DN versions)
• Review Report with drift metrics and approval decision
• Traceability Validation Report
• Updated Business Specification (if changes needed)

Why This Matters: Backward validation against Chapter 6 ensures specifications remain grounded in code evidence, preventing analysis drift.

How the Orchestration Works

File Structure

Execution Flow

Supervisor reads 03businessextraction_master.md
Supervisor selects next workpackage (by priority)

For Phase 3.0 (Business Context Discovery):
• Supervisor assigns business_specialist_requirements agent
• Supervisor provides task document: 03businessextractionphase3.0.md
• Agent reads task, resolves path variables, executes instructions
• Agent produces business context document and updates glossary
• Supervisor verifies completion against quality gates

For Phase 3.0.1 (Business Context Review):
• Supervisor assigns business_reviewer_requirements agent
• Supervisor provides task document: 03businessextractionphase3.0.1.md
• Agent reviews business context for accuracy
• Agent approves or requests revisions
• Supervisor verifies approval decision

For Phase 3.1 (Business Logic Extraction):
• Supervisor assigns business_specialist_logic_extraction agent
• Supervisor provides task document: 03businessextractionphase3.1.md
• Agent reads approved business context from Phase 3.0.1
• Agent extracts logic patterns and creates Chapter 6
• Supervisor verifies completion against quality gates

For Phase 3.1.1 (Business Logic Extraction Review):
• Supervisor assigns business_reviewer_logic_extraction agent
• Supervisor provides task document: 03businessextractionphase3.1.1.md
• Agent reviews Chapter 6 and logic abstractions
• Agent performs drift detection
• Agent approves or requests revisions
• Supervisor verifies approval decision

For Phase 3.2 (Business Specification Generation):
• Supervisor assigns business_specialist_requirements agent
• Supervisor provides task document: 03businessextractionphase3.2.md
• Agent reads approved Chapter 6 from Phase 3.1.1
• Agent creates Chapters 1-5 (EN and DN versions)
• Supervisor verifies completion against quality gates

For Phase 3.2.1 (Business Specification Review):
• Supervisor assigns business_reviewer_requirements agent
• Supervisor provides task document: 03businessextractionphase3.2.1.md
• Agent performs backward validation against Chapter 6
• Agent calculates drift metrics
• Agent approves, approves with changes, or rejects
• Supervisor checks approval decision

Rework Handling:
• If Phase 3.0.1 rejects → return to Phase 3.0
• If Phase 3.1.1 rejects → return to Phase 3.1
• If Phase 3.2.1 rejects → return to Phase 3.2 with specific corrections
• If critical issues → escalate to human supervisor

Completion:
• Workpackage marked as ready for Phase 4 (Code Generation)
• Supervisor proceeds to next workpackage

Key Success Factors

Business Context First
Don't skip Phase 3.0! Without business context, you'll translate code structures instead of extracting business concepts.

Evidence-Based Abstraction
Chapter 6 is the foundation. All business abstractions must trace to code evidence documented in Chapter 6.

Allowed Abstraction Patterns Only
Apply only DATA_TYPE, CONSOLIDATION, NAMING, STRUCTURE, LOGIC, PROCESS patterns. Forbidden: adding functionality, inventing entities, assuming patterns.

Backward Validation
Sample 20% of business elements and validate against Chapter 6. Full validation if drift ≥ 5%.

Technology-Agnostic Focus
Chapters 1-5 must be free of technical jargon. Ask: "Could a business specialist who has never seen COBOL understand this?"

Business vs Technical Separation
• Business rules (would exist in any implementation) → Chapter 3
• Technical rules (mainframe-specific) → Chapter 6

Complete Traceability
Every business requirement in Chapters 1-5 must trace to Chapter 6 evidence.

Common Pitfalls to Avoid

❌ Skipping Phase 3.0
Result: Code translation instead of business extraction
Fix: Always complete business context discovery first

❌ Skipping Phase 3.0.1 or 3.1.1 Reviews
Result: Errors propagate to later phases, causing rework
Fix: Always complete reviews before proceeding

❌ Creating Chapters 1-5 Before Chapter 6
Result: No evidence base for drift detection
Fix: Always create Chapter 6 first (Phase 3.1), then Chapters 1-5 (Phase 3.2)

❌ Analysis Drift - Adding Functionality
Example: Adding timezone handling when code only validates date format
Fix: Only abstract what exists in code (Chapter 6 evidence)

❌ Analysis Drift - Inventing Entities
Example: Adding email field when database has no email column
Fix: Only include entities/attributes present in database (Chapter 6 evidence)

❌ Analysis Drift - Assuming Patterns
Example: Assuming fiscal year logic when code only uses calendar dates
Fix: Only document logic actually implemented (Chapter 6 evidence)

❌ Technical Jargon in Chapters 1-5
Example: "PERFORM VALIDATE-CREDIT paragraph passing WS-CREDIT-LIM"
Fix: "Validate customer credit eligibility by comparing order total against available credit"

❌ Code Patterns as Business Rules
Example: "IF WS-CREDIT-LIM < WS-ORDER-AMT THEN REJECT"
Fix: "Orders must not be accepted if the total order value exceeds the customer's available credit limit"

❌ Incomplete Chapter 6
Result: Lost traceability, can't detect drift
Fix: Document all technical details with code references (file names, line numbers, snippets)

❌ Inconsistent EN/DN Versions
Result: Different business logic in different languages
Fix: Ensure identical structure, entity count, rule count, and business logic

❌ Skipping Backward Validation
Result: Drift goes undetected until code generation
Fix: Always perform 20% sample validation against Chapter 6

Quality Gates

Phase 3.0 Quality Gate (Business Context Discovery)
• ✅ Business domain identified with confidence level
• ✅ Business stakeholders documented
• ✅ Business vocabulary extracted (minimum 5 terms)
• ✅ Business constraints identified
• ✅ Business glossary updated

Phase 3.0.1 Quality Gate (Business Context Review)
• ✅ Business domain accuracy verified
• ✅ Stakeholder completeness verified
• ✅ Business vocabulary consistency verified
• ✅ Confidence levels acceptable
• ✅ Approval decision documented

Phase 3.1 Quality Gate (Business Logic Extraction)
• ✅ Chapter 6 created with complete technical details
• ✅ All code references documented (file names, line numbers, snippets)
• ✅ Database tables and access patterns documented
• ✅ Error codes and handling documented
• ✅ Technical architecture documented
• ✅ Logic patterns identified with evidence

Phase 3.1.1 Quality Gate (Business Logic Extraction Review)
• ✅ Abstraction patterns validated (allowed patterns only)
• ✅ Drift detection performed (forbidden patterns flagged)
• ✅ Chapter 6 completeness verified
• ✅ Traceability verified
• ✅ Approval decision documented

Phase 3.2 Quality Gate (Business Specification Generation)
• ✅ IEEE 830-1998 compliance verified
• ✅ Business entities extracted (minimum 3 entities)
• ✅ Business rules extracted (minimum 5 rules)
• ✅ Business functions extracted (minimum 3 functions)
• ✅ Technology-agnostic language in Chapters 1-5
• ✅ All elements trace to Chapter 6

Phase 3.2.1 Quality Gate (Business Specification Review)
• ✅ Backward validation performed (20% sample)
• ✅ Drift metrics calculated
• ✅ Business accuracy verified
• ✅ Completeness verified
• ✅ Technology independence verified
• ✅ Modernization readiness verified
• ✅ Approval decision documented

Expected Outcomes

For Each Workpackage
• 1 Business Context Document (understanding the business landscape)
• 1 Business Context Review Report (validation of business context)
• 1 Chapter 6 Document (complete technical implementation with evidence)
• 1 Logic Extraction Review Report (validation of abstractions and drift detection)
• 2 Business Specifications (EN and DN versions, IEEE 830-1998 format, Chapters 1-5)
• 1 Specification Review Report (backward validation findings and approval decision)
• 1 Traceability Matrix (business elements → Chapter 6 references)
• Updated Business Glossary (consolidated business vocabulary)

Overall
• Technology-agnostic business requirements ready for modern implementation
• Complete traceability to legacy code for verification
• Drift-controlled abstractions (evidence-based)
• Approved specifications ready for Phase 4 (Code Generation)

When to Escalate to Human Supervisor

Major business requirement gaps that cannot be resolved from code
Conflicting business policies requiring business decision
Ambiguous business logic requiring domain expert input
Technical implementation issues preventing extraction
Repeated rework cycles (more than 2 iterations per phase)
Drift percentage ≥ 10% (indicates systematic issues)
Critical traceability gaps (business elements without Chapter 6 evidence)

Summary

Phase 3 is about rediscovering business intent from legacy code, not translating COBOL syntax. By separating business context discovery (Phase 3.0), business context review (Phase 3.0.1), business logic extraction (Phase 3.1), business logic extraction review (Phase 3.1.1), business specification generation (Phase 3.2), and business specification review (Phase 3.2.1), you ensure that:

• Business requirements are technology-agnostic (can be implemented in any modern language)
• Business logic is separated from technical constraints (business rules vs technical rules)
• Complete traceability exists between business requirements and legacy code (via Chapter 6)
• Abstractions are evidence-based and drift-controlled (allowed patterns only)
• Specifications are validated at multiple checkpoints before code generation
• Quality is built in through reviews and backward validation

The six-phase approach manages cognitive load by separating concerns:
• Phases 3.0/3.0.1: Understand business context
• Phases 3.1/3.1.1: Extract and validate technical evidence
• Phases 3.2/3.2.1: Generate and validate business specification

Chapter 6 serves as the control mechanism for drift detection, ensuring all business abstractions remain grounded in code evidence.

This approach transforms legacy modernization from "code translation" to "business reimagination"—enabling true cloud-native implementations that preserve business value while eliminating accidental complexity.