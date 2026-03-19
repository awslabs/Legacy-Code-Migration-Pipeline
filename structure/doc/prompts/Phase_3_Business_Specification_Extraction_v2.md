# Phase 3: Business Specification Extraction - Process Guide v2.0

## Overview

Phase 3 transforms legacy COBOL code into modern, technology-agnostic business specifications through a **six-phase workflow**. The goal is to extract reimagined business requirements (what the business needs) rather than translated code structures (how COBOL implements it).

**Key Principle**: We're not translating COBOL to modern code—we're rediscovering the business intent buried in decades-old implementations.

**Drift Prevention**: We use evidence-based abstraction and Chapter 6 traceability to ensure specifications accurately reflect legacy system behavior while providing clean business abstractions.

---

## The Six-Phase Workflow

### Phase 3.0: Business Context Discovery
**Agent**: business_specialist_requirements  
**Purpose**: Understand the business landscape BEFORE diving into code details

**What Happens**:
- **Business Domain Identification**: What business area does this code support? (e.g., Order Management, Customer Service, Billing)
- **Stakeholder Analysis**: Who uses this functionality? Who owns the business process?
- **Business Vocabulary Extraction**: What business terms are used? (Customer, Order, Payment—not CUST-REC, ORD-FILE)
- **Business Problem Statement**: What business problem does this solve? Why does it exist?
- **Business Constraints**: What business policies are enforced? (credit limits, validation rules, approval workflows)

**Deliverables**:
- Business Context Document (one per workpackage)
- Consolidated Business Glossary (shared across all workpackages)

**Why This Matters**: Without business context, you'll translate COBOL structures instead of extracting business concepts. This phase establishes business mindset BEFORE looking at code details.

**Drift Control**: All context must be grounded in Phase 2 analysis - no invented business domains or stakeholders.

---

### Phase 3.0.1: Business Context Review
**Agent**: business_reviewer_requirements  
**Purpose**: Validate context quality before logic extraction begins

**What Happens**:
- Validate business domain identification against Phase 2 module classifications
- Verify stakeholder analysis is reasonable and supported by code usage patterns
- Check business vocabulary appears in code/comments
- Confirm business constraints are evident in code logic
- Assess readiness for Phase 3.1 (logic extraction)

**Deliverables**:
- Business Context Review Report
- Approval decision (APPROVED / REQUIRES_REVISION)

**Quality Gate**:
- ✅ Business domain matches Phase 2 analysis
- ✅ Stakeholders reasonably inferred from code
- ✅ Business vocabulary found in code/comments
- ✅ Business constraints supported by evidence
- ✅ Ready for logic extraction

**Why This Matters**: Validates context before logic extraction begins, preventing context drift from contaminating subsequent phases.

---

### Phase 3.1: Business Logic Extraction
**Agent**: business_specialist_logic_extraction  
**Purpose**: Extract business logic with proper abstraction (NOT code replication)

**What Happens**:

**Evidence-Based Abstraction** - Transform technical implementations to business concepts:

1. **Data Type Abstraction**: PIC X(8) with date validation → Date
2. **Validation Consolidation**: 8 validation steps → "must be a valid date"
3. **Naming Abstraction**: CUST-REC → Customer
4. **Structure Abstraction**: Flat COBOL records → Composite business entities
5. **Logic Simplification**: Complex nested IFs → Business policy
6. **Process Abstraction**: PERFORM statements → Business process steps

**For Each Business Element, Document**:
- **Code Evidence**: File name, line numbers, code snippet
- **Abstraction Type**: DATA_TYPE, CONSOLIDATION, NAMING, STRUCTURE, LOGIC, PROCESS
- **Abstraction Rationale**: Why this preserves business intent
- **Confidence Level**: HIGH, MEDIUM, LOW, SPECULATIVE

**Deliverables**:
- Business Logic Inventory (JSON)
- Business Rules Extraction (Markdown)
- Domain Model Specifications (UML-style)
- Business Process Mappings (Process flows)
- Business Logic Extractor Tool (Python script)

**Example - Proper Abstraction**:
```
Code: startDate PIC X(8) with 8-step YYYYMMDD validation
Abstraction: startDate: Date (mandatory) with validation rules
Evidence: BOOKING.cbl lines 450-520
Type: DATA_TYPE + CONSOLIDATION
Rationale: Business intent is "date field", not "8-character string"
Confidence: HIGH
```

**Forbidden - Drift**:
```
❌ Adding timezone (not in code)
❌ Adding fiscal year validation (not in code)
❌ Adding email field (not in code/database)
❌ Assuming audit fields (not in code)
```

**Why This Matters**: Proper abstractions create clean business specifications while maintaining accuracy. Drift prevention ensures no invented functionality.

---

### Phase 3.1.1: Business Logic Extraction Review
**Agent**: business_reviewer_logic_extraction  
**Purpose**: Validate abstractions are proper (grounded in code), not invented (drift)

**What Happens**:

**For Each Business Element, Validate**:
1. **Evidence Check**: Has code evidence? Reference accurate? Code implements this?
2. **Abstraction Validation**: Preserves business intent? Uses allowed patterns? No forbidden patterns?
3. **Drift Detection**: Any invented functionality? Entities? Rules? Relationships?

**Allowed Patterns** (APPROVE):
- ✅ PIC X(8) → Date (DATA_TYPE)
- ✅ 8 validations → "must be valid date" (CONSOLIDATION)
- ✅ CUST-REC → Customer (NAMING)
- ✅ Flat fields → Composite entity (STRUCTURE)
- ✅ Complex IFs → Business policy (LOGIC)
- ✅ PERFORM → Business steps (PROCESS)

**Forbidden Patterns** (REJECT):
- ❌ Date → DateTime with timezone (timezone not in code)
- ❌ Adding fields not in code/database
- ❌ Adding rules not implemented
- ❌ Assuming standard patterns not proven
- ❌ Over-abstracting (hiding business distinctions)

**Deliverables**:
- Business Logic Extraction Review Report
- Approval decision (APPROVED / REQUIRES_REVISION)
- Drift metrics (if any)

**Quality Gate**:
- ✅ All elements have code evidence
- ✅ All abstractions use allowed patterns
- ✅ No forbidden patterns detected
- ✅ No drift detected (no invented functionality)
- ✅ Ready for specification generation

**Why This Matters**: Catches drift early before it contaminates the final specification. Ensures abstractions are valid.

---

### Phase 3.2: Business Specification Generation
**Agent**: business_specialist_requirements  
**Purpose**: Create IEEE 830-1998 spec with Chapter 6 traceability

**What Happens**:

**Chapters 1-5: Clean Business Abstractions**
- Use business terminology (Customer, not CUST-REC)
- Use modern data types (Date, not PIC X(8))
- Consolidate validations into business rules
- Abstract processes to business level
- Technology-agnostic (no COBOL, CICS, JCL, mainframe terms)

**Chapter 6: Complete Legacy Implementation References**
- Code locations (files, lines) for every element
- Technical implementation details (COBOL records, database tables)
- All validation steps (don't consolidate here)
- Abstraction mapping (how Chapters 1-5 map to code)
- Legacy reason (why implemented this way)
- Modern equivalent (how to implement in cloud-native)

**Example - Chapter 2 (Business)**:
```markdown
## Entity: Booking

### Attributes
- **startDate**: Date (mandatory)
  - Must be a valid date
  - Must be > today
  - Must be <= endDate
```

**Example - Chapter 6 (Technical)**:
```markdown
## Entity: Booking - Legacy Implementation

**Code**: BOOKING.cbl, lines 100-150, 450-520

**Implementation**:
- startDate: PIC X(8) in YYYYMMDD format
- Validation: 8-step date validation logic
  1. Check not empty
  2. Check numeric
  3. Validate year (1900-2100)
  4. Validate month (01-12)
  5. Validate day (01-31)
  6. Validate day for month
  7. Leap year calculation
  8. Date comparison

**Abstraction Mapping**:
- PIC X(8) → Date (DATA_TYPE)
- 8 steps → 3 rules (CONSOLIDATION)

**Legacy Reason**: String dates for mainframe batch compatibility
**Modern Equivalent**: Native Date type with built-in validation
```

**Deliverables**:
- Business Specification - IEEE 830-1998
- Requirements Traceability Matrix

**Why This Matters**: Chapter 6 provides the control mechanism for drift detection. Clean Chapters 1-5 enable modern implementation. Both are essential.

---

### Phase 3.2.1: Business Specification Review
**Agent**: business_reviewer_requirements  
**Purpose**: Final drift check using Chapter 6 backward validation

**What Happens**:

**Standard Quality Review** (Chapters 1-5):
- IEEE 830-1998 compliance
- Technology-agnostic language (no technical jargon)
- Business vocabulary consistency with glossary
- Testability of requirements

**Backward Validation** (Chapters 1-5 vs Chapter 6):
1. **Sample 20% of elements** randomly from Chapters 1-5
2. **For each element**:
   - Read Chapters 1-5: What does spec claim?
   - Read Chapter 6: What does code do?
   - Validate abstraction is proper
   - Check for drift
3. **Calculate drift rate**: (drift elements / sampled elements) × 100%
4. **If drift ≥ 5%**: Validate ALL elements (100%)

**Drift Detection Examples**:

✅ **Valid Abstraction** (NO DRIFT):
```
Spec: startDate: Date
Code (Ch 6): PIC X(8) with YYYYMMDD validation
Assessment: Valid DATA_TYPE abstraction
Decision: PASS
```

❌ **Drift Detected** (INVENTED):
```
Spec: startDate: DateTime with timezone
Code (Ch 6): PIC X(8) with YYYYMMDD validation only
Assessment: Timezone not in code (INVENTED)
Decision: FAIL - Remove timezone
```

**Deliverables**:
- Business Specification Review Report
- Approval decision (APPROVED / REQUIRES_REVISION / REJECTED)
- Drift metrics
- Remediation guidance (if needed)

**Quality Gate**:
- ✅ Standard quality review passed
- ✅ Chapter 6 complete and accurate
- ✅ Backward validation passed (< 5% drift)
- ✅ No invented functionality detected
- ✅ Ready for Phase 4 (Code Generation)

**Rejection Scenarios**:
- **Return to Phase 3.0**: Business context issues
- **Return to Phase 3.1**: Logic extraction issues
- **Return to Phase 3.2**: Specification issues, drift detected

**Why This Matters**: Final quality gate ensures specifications are both high-quality AND accurate to legacy system. Chapter 6 enables drift detection.

---

## Workflow Orchestration

### Sequential Flow
```
Phase 3.0: Business Context Discovery
    ↓ (produces Business Context Document)
Phase 3.0.1: Business Context Review
    ↓ (if APPROVED)
Phase 3.1: Business Logic Extraction
    ↓ (produces Business Logic artifacts with evidence)
Phase 3.1.1: Business Logic Extraction Review
    ↓ (if APPROVED, no drift)
Phase 3.2: Business Specification Generation
    ↓ (produces IEEE 830-1998 spec with Chapter 6)
Phase 3.2.1: Business Specification Review
    ↓ (if APPROVED, < 5% drift)
Phase 4: Code Generation (next phase)
```

### Iterative Review Cycles

Each review phase follows this pattern:
```
1. Specialist completes work → produces deliverables
2. Supervisor creates review task file
3. Supervisor delegates to matching Reviewer
4. Reviewer validates deliverables
5. IF APPROVED:
   - Document approval
   - Proceed to next phase
6. IF REQUIRES_REVISION:
   - Supervisor creates remediation task file
   - Supervisor delegates back to Specialist
   - Specialist addresses issues
   - GOTO step 2 (re-review with iteration++)
7. IF iteration > 3:
   - Escalate to Migration Supervisor
```

---

## Key Success Factors

### 1. Business Context First
Don't skip Phase 3.0! Without business context, you'll translate code structures instead of extracting business concepts.

### 2. Evidence-Based Abstraction
Every business element must have code evidence, but should be abstracted to business intent. Balance: clean abstractions grounded in code.

### 3. Allowed Abstraction Patterns
Use DATA_TYPE, CONSOLIDATION, NAMING, STRUCTURE, LOGIC, PROCESS patterns to transform technical implementations to business concepts.

### 4. Forbidden Abstraction Patterns
Never add functionality, entities, rules, or relationships not present in code. This is drift.

### 5. Chapter 6 as Control Mechanism
Chapter 6 provides complete traceability that enables drift detection. Every element in Chapters 1-5 must have Chapter 6 reference.

### 6. Backward Validation
Use Chapter 6 to validate Chapters 1-5 accuracy. Sample 20%, full validation if drift detected.

### 7. Technology-Agnostic Focus
Chapters 1-5 must be free of technical jargon. Ask: "Could a business specialist who has never seen COBOL understand this?"

### 8. Complete Traceability
Every business requirement in Chapters 1-5 must trace to legacy code in Chapter 6.

---

## Common Pitfalls to Avoid

### ❌ Skipping Phase 3.0
**Result**: Code translation instead of business extraction  
**Fix**: Always complete business context discovery first

### ❌ Technical Jargon in Chapters 1-5
**Example**: "PERFORM VALIDATE-CREDIT paragraph passing WS-CREDIT-LIM"  
**Fix**: "Validate customer credit eligibility by comparing order total against available credit"

### ❌ Code Patterns as Business Rules
**Example**: "IF WS-CREDIT-LIM < WS-ORDER-AMT THEN REJECT"  
**Fix**: "Orders must not be accepted if the total order value exceeds the customer's available credit limit"

### ❌ Inventing Functionality
**Example**: Adding timezone to dates when code only has YYYYMMDD  
**Fix**: Use Date type only, document PIC X(8) in Chapter 6

### ❌ Incomplete Chapter 6
**Result**: Lost traceability, can't verify business requirements against legacy code  
**Fix**: Document all technical details with code references (file names, line numbers, snippets)

### ❌ Inconsistent EN/DN Versions
**Result**: Different business logic in different languages  
**Fix**: Ensure identical structure, entity count, rule count, and business logic

### ❌ Over-Abstraction
**Example**: Consolidating three different credit algorithms into one "validate credit"  
**Fix**: Document all three algorithms separately, preserve business distinctions

### ❌ Assuming Standard Patterns
**Example**: Adding createdAt, updatedAt fields when not in code  
**Fix**: Only document fields that exist in code/database

---

## Quality Gates Summary

### Phase 3.0 Quality Gate (Context Discovery)
- ✅ Business domain identified with confidence level
- ✅ Business stakeholders documented
- ✅ Business vocabulary extracted (minimum 5 terms)
- ✅ Business constraints identified
- ✅ Business glossary updated

### Phase 3.0.1 Quality Gate (Context Review)
- ✅ Business context complete and accurate
- ✅ Stakeholders properly identified
- ✅ Business vocabulary consistent
- ✅ Ready for logic extraction

### Phase 3.1 Quality Gate (Logic Extraction)
- ✅ All business domains covered
- ✅ Business rules extracted with evidence
- ✅ Domain models complete
- ✅ Process flows mapped
- ✅ Evidence documented for all elements
- ✅ Abstractions use allowed patterns

### Phase 3.1.1 Quality Gate (Logic Review)
- ✅ Business logic complete and accurate
- ✅ Abstractions validated (allowed patterns)
- ✅ No drift detected (no invented functionality)
- ✅ Evidence documentation complete
- ✅ Ready for specification generation

### Phase 3.2 Quality Gate (Specification Generation)
- ✅ IEEE 830-1998 compliance verified
- ✅ Business entities extracted (minimum 3)
- ✅ Business rules extracted (minimum 5)
- ✅ Business functions extracted (minimum 3)
- ✅ Technology-agnostic language in Chapters 1-5
- ✅ Complete legacy implementation in Chapter 6

### Phase 3.2.1 Quality Gate (Specification Review)
- ✅ Standard quality review passed
- ✅ Chapter 6 complete and accurate
- ✅ Backward validation passed (< 5% drift)
- ✅ No invented functionality detected
- ✅ Technology independence verified
- ✅ Modernization readiness verified
- ✅ Approval decision documented
- ✅ Ready for Phase 4 (Code Generation)

---

## Expected Outcomes

### For Each Workpackage
- 1 Business Context Document (from Phase 3.0)
- 1 Business Context Review Report (from Phase 3.0.1)
- 1 Business Logic Inventory (from Phase 3.1)
- 1 Business Rules Extraction (from Phase 3.1)
- 1 Domain Model Specification (from Phase 3.1)
- 1 Business Process Mapping (from Phase 3.1)
- 1 Business Logic Extraction Review Report (from Phase 3.1.1)
- 2 Business Specifications - EN and DN (from Phase 3.2)
- 1 Requirements Traceability Matrix (from Phase 3.2)
- 1 Business Specification Review Report (from Phase 3.2.1)
- Updated Business Glossary (throughout all phases)

### Overall
- Technology-agnostic business requirements ready for modern implementation
- Complete traceability to legacy code for verification (Chapter 6)
- Approved specifications ready for Phase 4 (Code Generation)
- Clear audit trail of all reviews and approvals
- Drift metrics documented (< 5% acceptable)

---

## When to Escalate to Human Supervisor

- Major business requirement gaps that cannot be resolved from code
- Conflicting business policies requiring business decision
- Ambiguous business logic requiring domain expert input
- Technical implementation issues preventing extraction
- Repeated rework cycles (more than 3 iterations per phase)
- Drift rate consistently > 5% despite remediation
- Specialist and reviewer disagree on abstraction validity

---

## Summary

Phase 3 is about rediscovering business intent from legacy code, not translating COBOL syntax. By separating:
- **Business context discovery** (Phase 3.0)
- **Context validation** (Phase 3.0.1)
- **Business logic extraction** (Phase 3.1)
- **Logic validation** (Phase 3.1.1)
- **Business specification generation** (Phase 3.2)
- **Specification validation** (Phase 3.2.1)

You ensure that:
- Business requirements are technology-agnostic (can be implemented in any modern language)
- Business logic is separated from technical constraints (business rules vs technical rules)
- Complete traceability exists between business requirements and legacy code (Chapter 6)
- Specifications are validated and approved before code generation
- Drift is detected and prevented through evidence-based abstraction and backward validation
- Quality gates ensure high-quality, accurate specifications

This approach transforms legacy modernization from "code translation" to "business reimagination"—enabling true cloud-native implementations that preserve business value while eliminating accidental complexity.

---

**Document Version**: 2.0  
**Date**: 2024-02-17  
**Changes from v1.0**: 
- Expanded from 3 phases to 6 phases
- Added evidence-based abstraction guidelines
- Added drift prevention mechanisms
- Added Chapter 6 backward validation
- Added detailed quality gates for each phase
- Added abstraction pattern examples
