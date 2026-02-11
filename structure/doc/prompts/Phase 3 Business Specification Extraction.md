Phase 3: Business Specification Extraction - Process Guide

Overview

Phase 3 transforms legacy COBOL code into modern, technology-agnostic business specifications through a three-phase workflow. The goal is to extract reimagined business requirements (what the business needs) rather than translated code structures (how COBOL implements it).

Key Principle: We're not translating COBOL to modern code—we're rediscovering the business intent buried in decades-old implementations.

The Three-Phase Workflow

Phase 3.0: Business Context Discovery

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

Phase 3.1: Business Specification Extraction

Purpose: Extract business requirements using the context from Phase 3.0 as a guide.

What Happens:

Chapter 1: Introduction (Enhanced with Business Context)
• Business domain, stakeholders, and problem statement from Phase 3.0
• Business value and outcomes
• Written for business analysts who have never seen the code

Chapter 2: Business Entities (Business Concept Level)
• Not: COBOL record structures with technical fields
• But: Real business concepts (Customer, Order, Payment) with business attributes (creditLimit, orderTotal, paymentStatus)
• Generic data types (String, Numeric, Date, Timestamp, Boolean)
• Business validation rules (not technical constraints like buffer sizes)

Chapter 3: Business Rules (Business Policy Level)
• Not: Code patterns (IF WS-CREDIT-LIM < WS-ORDER-AMT THEN REJECT)
• But: Business policies (Orders must not exceed customer credit limits to minimize financial risk)
• WHEN/THEN format with business rationale
• Technical rules (batch restart, file locking) go in Chapter 6

Chapter 4: Business Functions (Business Capability Level)
• Not: COBOL paragraphs and subroutines
• But: Business capabilities (Validate Customer Credit Eligibility, Process Order Payment)
• Inputs/outputs in business terms
• Processing logic in business language

Chapter 5: Process Flows (Business Process Level)
• Not: Program call graphs (PERFORM statements)
• But: Business processes with activities, decision points, and actors
• Business outcomes and value

Chapter 6: Legacy Implementation References (Complete Technical Details)
• All technical implementation details go here
• Code references (file names, line numbers, snippets)
• Database tables and access patterns
• Error codes and handling
• Technical architecture layers
• Legacy reason and modern cloud-native equivalent for each component
• Obsolescence flags

Critical Separation:
• Chapters 1-5: Technology-agnostic business requirements (no COBOL, CICS, JCL, mainframe jargon)
• Chapter 6: Complete legacy technical implementation with full traceability

Deliverables:
• Business Specification (English version)
• Business Specification (Danish version)
• Both versions have identical structure and business logic

Why This Matters: This separation ensures business requirements can be implemented in any modern technology (Python, Java, cloud-native) while maintaining complete traceability to legacy code.

Phase 3.2: Business Specialist Review

Purpose: Validate that specifications accurately represent business requirements and are ready for modernization.

What Happens:

Chapter-by-Chapter Review
• Chapter 1: Business context accuracy, stakeholder completeness
• Chapter 2: Business entities at concept level (not code structures)
• Chapter 3: Business rules represent policies (not code patterns)
• Chapter 4: Business functions represent capabilities (not subroutines)
• Chapter 5: Business processes use business terminology
• Chapter 6: Complete technical details with traceability

Cross-Cutting Verification
• Technology-Agnostic Language: Scan Chapters 1-5 for technical jargon
• Business Vocabulary Consistency: Terms match Phase 3.0 glossary
• Bilingual Consistency: EN and DN versions identical in structure and logic
• Traceability: All business requirements traced to legacy code in Chapter 6

Identify Issues
• Missing Requirements: What business requirements are not documented?
• Accidental Complexity: What are legacy technical constraints (not business requirements)?
• Business Rationale: Why do these requirements exist?

Approval Decision
• Approved: Ready for code generation
• Approved with Changes: Minor fixes applied, ready for code generation
• Rejected: Return to Phase 3.0 (business context issues) or Phase 3.1 (extraction issues)

Deliverables:
• Reviewed Business Specification (EN and DN versions)
• Review Report with findings, changes, and approval decision
• Updated Business Context (if needed)
• Updated Business Glossary (if needed)

Why This Matters: This quality gate ensures specifications are accurate, complete, and ready for modern implementation—preventing costly rework during code generation.

How the Orchestration Works

File Structure

Execution Flow
Supervisor reads 03businessextraction_master.md
Supervisor selects next workpackage (by priority)
For Phase 3.0:
• Supervisor assigns businesscontextanalyst agent
• Supervisor provides task document: 03businessextractionphase3.0.md
• Agent reads task, resolves path variables, executes instructions
• Agent produces business context document and updates glossary
• Supervisor verifies completion against quality gates
For Phase 3.1:
• Supervisor assigns businessspecialistlogic_extraction agent
• Supervisor provides task document: 03businessextractionphase3.1.md
• Agent reads business context from Phase 3.0
• Agent extracts business specifications (EN and DN versions)
• Supervisor verifies completion against quality gates
For Phase 3.2:
• Supervisor assigns businessanalystreviewer agent
• Supervisor provides task document: 03businessextractionphase3.2.md
• Agent reviews specifications, creates review report
• Agent makes approved changes or flags for rework
• Supervisor checks approval decision
Rework Handling:
• If rejected due to business context issues → return to Phase 3.0
• If rejected due to extraction issues → return to Phase 3.1
• If critical issues → escalate to human supervisor
Completion:
• Workpackage marked as ready for Phase 4 (Code Generation)
• Supervisor proceeds to next workpackage

Key Success Factors
Business Context First
Don't skip Phase 3.0! Without business context, you'll translate code structures instead of extracting business concepts.
Technology-Agnostic Focus
Chapters 1-5 must be free of technical jargon. Ask: "Could a business specialist who has never seen COBOL understand this?"
Business vs Technical Separation
• Business rules (would exist in any implementation) → Chapter 3
• Technical rules (mainframe-specific) → Chapter 6
Bilingual Consistency
EN and DN versions must have identical structure, entity count, rule count, and business logic.
Complete Traceability
Every business requirement in Chapters 1-5 must trace to legacy code in Chapter 6.

Common Pitfalls to Avoid

❌ Skipping Phase 3.0
Result: Code translation instead of business extraction
Fix: Always complete business context discovery first

❌ Technical Jargon in Chapters 1-5
Example: "PERFORM VALIDATE-CREDIT paragraph passing WS-CREDIT-LIM"
Fix: "Validate customer credit eligibility by comparing order total against available credit"

❌ Code Patterns as Business Rules
Example: "IF WS-CREDIT-LIM < WS-ORDER-AMT THEN REJECT"
Fix: "Orders must not be accepted if the total order value exceeds the customer's available credit limit"

❌ Incomplete Chapter 6
Result: Lost traceability, can't verify business requirements against legacy code
Fix: Document all technical details with code references (file names, line numbers, snippets)

❌ Inconsistent EN/DN Versions
Result: Different business logic in different languages
Fix: Ensure identical structure, entity count, rule count, and business logic

Quality Gates

Phase 3.0 Quality Gate
• ✅ Business domain identified with confidence level
• ✅ Business stakeholders documented
• ✅ Business vocabulary extracted (minimum 5 terms)
• ✅ Business constraints identified
• ✅ Business glossary updated

Phase 3.1 Quality Gate
• ✅ IEEE 830-1998 compliance verified
• ✅ Business entities extracted (minimum 3 entities)
• ✅ Business rules extracted (minimum 5 rules)
• ✅ Business functions extracted (minimum 3 functions)
• ✅ Technology-agnostic language in Chapters 1-5
• ✅ Complete legacy implementation in Chapter 6
• ✅ Bilingual consistency verified

Phase 3.2 Quality Gate
• ✅ Business accuracy verified
• ✅ Completeness verified
• ✅ Technology independence verified
• ✅ Modernization readiness verified
• ✅ Approval decision documented

Expected Outcomes

For Each Workpackage
• 1 Business Context Document (understanding the business landscape)
• 2 Business Specifications (EN and DN versions, IEEE 830-1998 format)
• 1 Review Report (validation findings and approval decision)
• Updated Business Glossary (consolidated business vocabulary)

Overall
• Technology-agnostic business requirements ready for modern implementation
• Complete traceability to legacy code for verification
• Bilingual documentation (English and Danish)
• Approved specifications ready for Phase 4 (Code Generation)

When to Escalate to Human Supervisor
Major business requirement gaps that cannot be resolved from code
Conflicting business policies requiring business decision
Ambiguous business logic requiring domain expert input
Technical implementation issues preventing extraction
Repeated rework cycles (more than 2 iterations per workpackage)

Summary

Phase 3 is about rediscovering business intent from legacy code, not translating COBOL syntax. By separating business context discovery (Phase 3.0), business specification extraction (Phase 3.1), and business specialist review (Phase 3.2), you ensure that:
• Business requirements are technology-agnostic (can be implemented in any modern language)
• Business logic is separated from technical constraints (business rules vs technical rules)
• Complete traceability exists between business requirements and legacy code
• Specifications are validated and approved before code generation

This approach transforms legacy modernization from "code translation" to "business reimagination"—enabling true cloud-native implementations that preserve business value while eliminating accidental complexity.