# Phase 1.3: Analysis Review

---

## Orchestration Information

**Phase**: Phase 1 - Source Code Analysis
**Step**: Step 1.3 - Analysis Review
**Team Supervisor**: analysis_team_supervisor
**Assigned Agents**: 
- analysis_reviewer_legacy_code (for source code analysis review)
- analysis_reviewer_database (for database analysis review)
**Task File Names**: 
- {{TASKS_BASE_PATH}}/analysis_sourcecode_review_task.md
- {{TASKS_BASE_PATH}}/analysis_database_review_task.md

### Expected Deliverables

1. **Analysis Review Feedback Report**
   - File: {{ANALYSIS_REVIEW_FEEDBACK}}
   - Description: Comprehensive review findings with specific issues and recommendations

2. **Analysis Phase Approval Document**
   - File: {{ANALYSIS_PHASE_APPROVAL}}
   - Description: Formal approval decision with quality assessment

3. **Remediation Tracking** (if issues found)
   - File: {{ANALYSIS_REMEDIATION_TRACKING}}
   - Description: Issue tracking and remediation progress

### Success Criteria
- [ ] All analysis deliverables reviewed and validated
- [ ] All quality criteria assessed (completeness, accuracy, consistency)
- [ ] Cross-references between outputs verified
- [ ] Approval decision documented with clear rationale
- [ ] If issues found: detailed feedback provided with remediation guidance
- [ ] If approved: confirmation that migration planning can proceed
- [ ] Ready to proceed to Phase 2 (Workpackage Planning)

---

## For Team Supervisor: Task File Creation

When creating the task files for this step:

### 1. Extract from this prompt:
- **Objective section**: The goal of reviewing and validating all analysis outputs
- **Review scope**: All deliverables from Steps 1.1 and 1.2
- **Review methodology**: Completeness, accuracy, consistency validation steps
- **Quality assessment categories**: Functionality, documentation, maintainability, etc.
- **Approval/rejection workflow**: Decision criteria and feedback process
- **Remediation instructions**: How to handle issues and coordinate fixes

### 2. Add project context:
- **Project name**: {{PROJECT_NAME}}
- **Project base path**: {{PROJECT_BASE_PATH}}
- **All input locations** (deliverables to review - resolved paths):
  - Source code analysis report: {{COBOL_SOURCE_ANALYSIS_REPORT}}
  - Dependency analysis table: {{DEPENDENCY_ANALYSIS_TABLE}}
  - Business flows: {{BUSINESS_FLOWS}}
  - Module classifications: {{MODULE_CLASSIFICATIONS}}
  - Source code analyzer tool: {{COBOL_SOURCE_CODE_ANALYSIS_ANALYZER_TOOL}}
  - Source code progress tracking: {{ANALYSIS_STATUS}}
  - Database analysis report: {{DATABASE_ANALYSIS_REPORT}}
  - Target system DDL scripts: {{DATABASE_GEN_SRC}}/
  - Migration scripts: {{DATABASE_GEN_SRC}}/migration/
  - Database analyzer tool: {{DATABASE_ANALYZER_TOOL}}
  - Database progress tracking: {{DATABASE_PROGRESS_TRACKING}}
- **All output locations** (resolved paths):
  - Review feedback: {{ANALYSIS_REVIEW_FEEDBACK}}
  - Phase approval: {{ANALYSIS_PHASE_APPROVAL}}
  - Remediation tracking: {{ANALYSIS_REMEDIATION_TRACKING}}
  - Task files location: {{TASKS_BASE_PATH}}
- **All template locations** (resolved paths):
  - Templates used by analysis phase (for validation)

### 3. Reference agent definitions:
- **Agent names**: analysis_reviewer_legacy_code, analysis_reviewer_database
- **Agent definition files**: 
  - structure/agents/analysis_team/analysis_reviewer_legacy_code.md
  - structure/agents/analysis_team/analysis_reviewer_database.md
- **Note**: Don't duplicate agent definitions, just reference them

### 4. Task file structure:
Create TWO separate task files (one for each reviewer):

**For Source Code Review** (analysis_sourcecode_review_task.md):
- **Agent Assignment**: analysis_reviewer_legacy_code
- **Project Context**: All source code analysis deliverables to review
- **Task Instructions**: Review methodology for source code outputs
- **Expected Deliverables**: Review feedback and approval decision
- **Quality Criteria**: Completeness, accuracy, consistency checks

**For Database Review** (analysis_database_review_task.md):
- **Agent Assignment**: analysis_reviewer_database
- **Project Context**: All database analysis deliverables to review
- **Task Instructions**: Review methodology for database outputs
- **Expected Deliverables**: Review feedback and approval decision
- **Quality Criteria**: Schema integrity, migration safety checks

### 5. Path resolution:
Ensure all {{PARAMETERS}} are replaced with actual absolute paths before creating the task files.

---

## Context

### Project Information
**Project Name**: {{PROJECT_NAME}}
**Project Base Path**: {{PROJECT_BASE_PATH}}

### Deliverables to Review (from Steps 1.1 and 1.2)

#### Source Code Analysis Deliverables
- **Source Code Analysis Report**: {{COBOL_SOURCE_ANALYSIS_REPORT}}
  - Template: {{COBOL_SOURCE_ANALYSIS_REPORT_TEMPLATE}}
  - Description: Comprehensive analysis methodology, findings, and recommendations
  
- **Dependency Analysis Table**: {{DEPENDENCY_ANALYSIS_TABLE}}
  - Template: {{DEPENDENCY_ANALYSIS_TABLE_TEMPLATE}}
  - Description: Complete module dependency relationships
  
- **Business Flow Specifications**: {{BUSINESS_FLOWS}}
  - Template: {{BUSINESS_FLOWS_TEMPLATE}}
  - Description: End-to-end flow identification and mapping
  
- **Module Classification Report**: {{MODULE_CLASSIFICATIONS}}
  - Template: {{MODULE_CLASSIFICATIONS_TEMPLATE}}
  - Description: Module type and functionality classifications
  
- **Dependency Analysis Tool**: {{COBOL_SOURCE_CODE_ANALYSIS_ANALYZER_TOOL}}
  - Description: Python tool that performs the analysis
  
- **Progress Tracking**: {{ANALYSIS_STATUS}}
  - Template: {{ANALYSIS_STATUS_TEMPLATE}}
  - Description: Analysis progress and status tracking

#### Database Analysis Deliverables
- **Database Analysis Report**: {{DATABASE_ANALYSIS_REPORT}}
  - Template: {{DATABASE_REPORTING_TEMPLATE}}
  - Description: Comprehensive database analysis findings and compatibility assessment
  
- **Target System DDL Scripts**: {{DATABASE_GEN_SRC}}/
  - Description: Functionally equivalent database DDL for each target system (DB2 LUW, PostgreSQL)
  
- **Migration Scripts**: {{DATABASE_GEN_SRC}}/migration/
  - Description: Data migration scripts for each target system
  
- **Database Analyzer Tool**: {{DATABASE_ANALYZER_TOOL}}
  - Description: Python tool that performs the database analysis
  
- **Progress Tracking**: {{DATABASE_PROGRESS_TRACKING}}
  - Template: {{ANALYSIS_STATUS_TEMPLATE}}
  - Description: Database analysis progress and status tracking

### Review Output Locations
- **Review Feedback Report**: {{ANALYSIS_REVIEW_FEEDBACK}}
  - Description: Comprehensive review findings with specific issues and recommendations
  
- **Phase Approval Document**: {{ANALYSIS_PHASE_APPROVAL}}
  - Description: Formal approval decision with quality assessment
  
- **Remediation Tracking**: {{ANALYSIS_REMEDIATION_TRACKING}}
  - Description: Issue tracking and remediation progress (if issues found)

---

## Objective

Perform comprehensive review and validation of all analysis phase deliverables from Steps 1.1 (Database Analysis) and 1.2 (Source Code Analysis). Ensure all outputs meet quality standards, are complete and accurate, and provide a solid foundation for migration planning. Make final approval decision for analysis phase completion.

---

## Instructions

### Step 1: Deliverable Inventory and Initial Validation

**Actions:**
1. Verify all required deliverables from Steps 1.1 and 1.2 are present
2. Check that all files exist at specified paths
3. Verify file sizes are reasonable (not empty or corrupted)
4. Validate file formats match expected types (Markdown, CSV, JSON, Python, SQL)
5. Create initial inventory checklist

**Deliverables Checklist:**
- [ ] Source Code Analysis Report exists
- [ ] Dependency Analysis Table exists
- [ ] Business Flow Specifications exist
- [ ] Module Classification Report exists
- [ ] Source Code Analyzer Tool exists
- [ ] Source Code Progress Tracking exists
- [ ] Database Analysis Report exists
- [ ] Target System DDL Scripts exist (for all target systems)
- [ ] Migration Scripts exist (for all target systems)
- [ ] Database Analyzer Tool exists
- [ ] Database Progress Tracking exists

**If any deliverables are missing:**
- Document missing items with specific file paths
- Report to analysis_team_supervisor
- Request completion before proceeding with detailed review

### Step 2: Template and Format Compliance Validation

**Actions:**
1. Validate all outputs against their specified templates
2. Check JSON files validate against schemas
3. Verify CSV files have correct column headers
4. Confirm Markdown files include all required sections
5. Ensure file naming conventions are followed

**Format Validation Checks:**

**For JSON Files** (Business Flows, Module Classifications, Progress Tracking):
- [ ] Valid JSON syntax (no parsing errors)
- [ ] All required fields present
- [ ] Field types match schema specifications
- [ ] No empty required fields (unless specified)
- [ ] Consistent structure across all entries

**For CSV Files** (Dependency Analysis Table):
- [ ] Correct column headers match template exactly
- [ ] All required columns present
- [ ] Data types appropriate for each column
- [ ] No missing values in required fields
- [ ] Consistent formatting throughout

**For Markdown Files** (Analysis Reports):
- [ ] All required sections present
- [ ] Section order matches template
- [ ] Proper markdown formatting
- [ ] Complete content in all sections
- [ ] Professional documentation quality

**For SQL Files** (DDL and Migration Scripts):
- [ ] Valid SQL syntax
- [ ] Proper formatting and indentation
- [ ] Comments documenting transformations
- [ ] Execution instructions included

**For Python Files** (Analyzer Tools):
- [ ] Valid Python syntax
- [ ] Proper code structure and organization
- [ ] Documentation and comments present
- [ ] Error handling implemented

### Step 3: Completeness Validation

**Source Code Analysis Completeness:**
- [ ] All legacy source files analyzed and documented
- [ ] All dependency relationships captured in dependency table
- [ ] All entry points identified and mapped to business flows
- [ ] All modules classified by type (ENTRY_POINT, COMMONLY_USED, SINGLE_USE)
- [ ] All modules classified by functionality (FUNCTIONAL, UTILITY)
- [ ] All business domains assigned with documented rationale
- [ ] All business flows traced from entry to data persistence
- [ ] Analysis tool created and functional
- [ ] Progress tracking shows "Complete" status

**Database Analysis Completeness:**
- [ ] All database source files analyzed and documented
- [ ] Compatibility assessment completed for all target systems (DB2 LUW, PostgreSQL)
- [ ] Equivalent DDL scripts created for each target system
- [ ] Target systems contain SAME number of tables as source database
- [ ] All columns included in target DDL
- [ ] All constraints and indexes migrated
- [ ] Migration scripts generated with integrity preservation
- [ ] Migration scripts cover all tables
- [ ] Database analyzer tool created and functional
- [ ] Progress tracking shows "Complete" status

### Step 4: Accuracy Validation

**Source Code Analysis Accuracy:**
- [ ] Module classifications are consistent and well-documented
- [ ] Business domain assignments are logical with clear rationale
- [ ] Dependency relationships are verified and complete
- [ ] Flow complexity calculations are consistent across all flows
- [ ] Database operations include actual queries (SELECT, UPDATE, etc.) and table information
- [ ] Cross-references between outputs are accurate
- [ ] System utilities properly excluded from analysis
- [ ] Dynamic calls properly identified and documented

**Database Analysis Accuracy:**
- [ ] Target database schemas have same/equivalent datatypes
- [ ] Datatype mappings are correct and preserve data integrity
- [ ] Column names preserved exactly (no changes)
- [ ] Referential integrity maintained in target schemas
- [ ] Constraints correctly translated for each target system
- [ ] SQL dialect differences properly addressed
- [ ] Compatibility assessments are thorough and accurate
- [ ] Migration strategies are appropriate for each incompatibility

### Step 5: Consistency Validation

**Cross-Reference Validation:**
- [ ] Module names consistent between dependency table and classification report
- [ ] Flow IDs consistent between business flows and dependency analysis
- [ ] Database table references match between code analysis and database analysis
- [ ] Business domains align between code modules and database schemas
- [ ] File operations reference valid database entities
- [ ] Entry points in code analysis match transaction definitions

**Format Consistency:**
- [ ] Naming conventions followed consistently throughout
- [ ] Documentation format consistent across all deliverables
- [ ] Terminology consistent (same terms used for same concepts)
- [ ] After migration, referential integrity remains same as source database
- [ ] Foreign key relationships preserved
- [ ] Data relationships maintained

### Step 6: Quality Assessment

**Functionality Review:**
- **Code Analysis**: Does the analysis correctly identify all legacy code call patterns, file operations, and database access?
- **Database Analysis**: Do the target schemas support the same business operations as the source?
- **Tool Quality**: Are the analysis tools robust, reusable, and well-documented?

**Readability and Documentation:**
- **Report Clarity**: Are analysis reports clear, comprehensive, and well-structured?
- **Code Documentation**: Are analysis tools properly documented with clear usage instructions?
- **Rationale Documentation**: Are all classification and domain assignment decisions well-documented?

**Maintainability and Reusability:**
- **Tool Design**: Are analysis tools designed for reuse with similar legacy systems?
- **Script Organization**: Are database migration scripts well-organized and maintainable?
- **Documentation Standards**: Is all documentation consistent and professional?

**Performance and Scalability:**
- **Analysis Efficiency**: Do analysis tools handle large codebases efficiently?
- **Migration Performance**: Are database migration scripts optimized for performance?
- **Resource Usage**: Are tools designed to handle enterprise-scale legacy systems?

**Security and Risk Management:**
- **Data Security**: Are migration scripts designed to preserve data security?
- **Error Handling**: Is error handling comprehensive and appropriate?
- **Risk Mitigation**: Are potential migration risks identified and addressed?

### Step 7: Tool Verification (Optional but Recommended)

**If time and resources permit:**
1. Execute source code analyzer tool on sample legacy code
2. Verify tool produces expected outputs
3. Check error handling and logging functionality
4. Execute database analyzer tool on sample database files
5. Verify DDL generation is correct
6. Test migration scripts in safe environment (if possible)

### Step 8: Approval Decision and Documentation

**Decision Criteria:**

**APPROVE if:**
- [ ] All deliverables present and complete
- [ ] All quality criteria met (completeness, accuracy, consistency)
- [ ] All templates and formats compliant
- [ ] Cross-references validated
- [ ] Tools functional and well-documented
- [ ] No blocking issues identified
- [ ] Ready for migration planning phase

**REQUIRE REVISION if:**
- [ ] Missing deliverables
- [ ] Quality criteria not met
- [ ] Template violations
- [ ] Inconsistencies between outputs
- [ ] Blocking issues identified
- [ ] Tools non-functional or poorly documented

**Document Decision:**
Create formal approval document at {{ANALYSIS_PHASE_APPROVAL}} with:
- Approval status (APPROVED / REQUIRES_REVISION)
- Review date and reviewer identification
- List of all validated deliverables with paths
- Quality assessment summary
- Next phase readiness confirmation
- Any notes or observations

### Step 9: Feedback Generation (if issues found)

**If REQUIRES_REVISION:**

1. **Create Detailed Feedback Report** at {{ANALYSIS_REVIEW_FEEDBACK}}:
   - Review summary with overall status
   - Specific issues identified with file paths and line numbers
   - Recommended remediation actions for each issue
   - Priority classification (Critical, High, Medium, Low)
   - Quality assessment breakdown

2. **Create Remediation Tracking** at {{ANALYSIS_REMEDIATION_TRACKING}}:
   - List of all issues requiring remediation
   - Assigned to (specialist agent)
   - Status tracking (Open, In Progress, Resolved)
   - Resolution verification checklist

3. **Communicate with Analysis Team Supervisor**:
   - Provide clear, actionable feedback
   - Specify which deliverables need revision
   - Indicate expected timeline for remediation
   - Offer to answer questions or provide clarification

### Step 10: Remediation Cycle Management (if applicable)

**If issues were found and remediation is in progress:**

1. **Monitor Remediation Progress**:
   - Track issue resolution status
   - Verify updated deliverables are submitted
   - Check that all feedback has been addressed

2. **Re-Review Updated Deliverables**:
   - Validate all issues have been properly resolved
   - Ensure no new issues were introduced
   - Confirm quality criteria are now met

3. **Final Approval**:
   - Once all issues resolved, update approval document
   - Change status to APPROVED
   - Confirm readiness for Phase 2

---

## Output Format

### Primary Outputs

#### 1. Analysis Review Feedback Report
**File**: {{ANALYSIS_REVIEW_FEEDBACK}}

**Required Sections:**
```markdown
# Analysis Review Feedback

## Review Summary
- Review Date: [Date]
- Reviewers: analysis_reviewer_legacy_code, analysis_reviewer_database
- Overall Status: [APPROVED / REQUIRES_REVISION]

## Source Code Analysis Review
### Deliverables Reviewed
- [List all source code deliverables with paths]

### Issues Identified
- [Specific issue with file path and line number]
- [Recommended remediation action]
- [Priority: Critical/High/Medium/Low]

### Quality Assessment
- Completeness: [PASS / FAIL - with details]
- Accuracy: [PASS / FAIL - with details]
- Consistency: [PASS / FAIL - with details]

## Database Analysis Review
### Deliverables Reviewed
- [List all database deliverables with paths]

### Issues Identified
- [Specific issue with file path and details]
- [Recommended remediation action]
- [Priority: Critical/High/Medium/Low]

### Quality Assessment
- Completeness: [PASS / FAIL - with details]
- Accuracy: [PASS / FAIL - with details]
- Consistency: [PASS / FAIL - with details]

## Cross-Reference Validation
### Issues Identified
- [Any inconsistencies between code and database analysis]
- [Recommended remediation action]

## Approval Decision
- [Detailed rationale for approval or revision requirements]
- [Next steps]
```

#### 2. Analysis Phase Approval Document
**File**: {{ANALYSIS_PHASE_APPROVAL}}

**Required Format (JSON):**
```json
{
  "approval_status": "APPROVED",
  "approval_date": "YYYY-MM-DD",
  "reviewers": ["analysis_reviewer_legacy_code", "analysis_reviewer_database"],
  "deliverables_validated": [
    "absolute path to deliverable 1",
    "absolute path to deliverable 2",
    "..."
  ],
  "quality_assessment": {
    "completeness": "PASS",
    "accuracy": "PASS",
    "consistency": "PASS"
  },
  "next_phase_readiness": "CONFIRMED",
  "notes": "Any additional comments or observations"
}
```

#### 3. Remediation Tracking (if issues found)
**File**: {{ANALYSIS_REMEDIATION_TRACKING}}

**Required Format (JSON):**
```json
{
  "remediation_cycle": 1,
  "issues": [
    {
      "issue_id": "ISSUE-001",
      "description": "Specific issue description",
      "file_path": "absolute path to file",
      "priority": "Critical",
      "assigned_to": "analysis_specialist_legacy_code",
      "status": "Open",
      "remediation_action": "Specific action required",
      "resolution_notes": ""
    }
  ],
  "overall_status": "In Progress",
  "next_review_date": "YYYY-MM-DD"
}
```

---

## Quality Criteria

### Review Process Quality
- [ ] All deliverables inventoried and checked
- [ ] All validation steps completed systematically
- [ ] All issues documented with specific details
- [ ] All feedback is actionable and clear
- [ ] Approval decision is well-documented with rationale

### Feedback Quality (if issues found)
- [ ] Issues include specific file paths and line numbers
- [ ] Remediation actions are clear and actionable
- [ ] Priority levels are appropriate
- [ ] Feedback is constructive and professional
- [ ] Timeline expectations are reasonable

### Approval Documentation Quality
- [ ] Approval status is clear and unambiguous
- [ ] All validated deliverables are listed with paths
- [ ] Quality assessment is comprehensive
- [ ] Next phase readiness is confirmed
- [ ] Documentation is professional and complete

---

## Error Handling

### Common Review Scenarios

#### 1. **Missing Deliverables**
- **Detection**: Required files not found at specified paths
- **Recovery**: Document missing items, report to supervisor, request completion
- **Escalation**: If deliverables remain missing after 2 requests, escalate to Migration Supervisor

#### 2. **Template Violations**
- **Detection**: Outputs don't match specified templates
- **Recovery**: Document specific violations, provide template reference, request correction
- **Escalation**: If violations persist after 2 remediation cycles, escalate to supervisor

#### 3. **Quality Criteria Not Met**
- **Detection**: Completeness, accuracy, or consistency checks fail
- **Recovery**: Provide detailed feedback with specific examples, request remediation
- **Escalation**: If quality issues persist after 2 cycles, escalate with recommendation

#### 4. **Inconsistencies Between Outputs**
- **Detection**: Cross-reference validation reveals mismatches
- **Recovery**: Document inconsistencies, coordinate resolution between specialists
- **Escalation**: If inconsistencies cannot be resolved, escalate to supervisor for guidance

#### 5. **Tool Failures**
- **Detection**: Analysis tools fail to execute or produce unreliable results
- **Recovery**: Document tool issues, request debugging and fixes
- **Escalation**: If tools remain non-functional after 2 attempts, escalate as blocking issue

### Escalation Triggers
- Analysis deliverables fail review more than 2 times
- Critical analysis gaps that impact migration feasibility
- Inconsistencies between code and database analysis that cannot be resolved
- Analysis tools fail to function properly or produce unreliable results
- Timeline constraints threaten overall migration schedule

---

## Success Validation

**Review is complete when:**
- [ ] All deliverables inventoried and validated
- [ ] All quality criteria assessed
- [ ] Approval decision documented
- [ ] If APPROVED: Phase approval document created, ready for Phase 2
- [ ] If REQUIRES_REVISION: Feedback report created, remediation tracking established
- [ ] Analysis Team Supervisor notified of review completion
- [ ] All review outputs exist at specified paths

**Verification Steps:**
1. Check all review output files exist at specified locations
2. Validate approval document format and content
3. If issues found: verify feedback report is comprehensive and actionable
4. Confirm decision rationale is clear and well-documented
5. Report review completion to analysis_team_supervisor

---

## Notes

### Agent Definition References
Complete role definitions and capabilities are in:
- structure/agents/analysis_team/analysis_reviewer_legacy_code.md
- structure/agents/analysis_team/analysis_reviewer_database.md

This prompt provides project-specific context and review instructions.

### Coordination
- Both reviewers should coordinate to ensure consistent quality standards
- Cross-reference validation requires collaboration between reviewers
- Final approval decision should reflect consensus between both reviewers

### Escalation
If you encounter issues beyond your capability:
1. Document the issue clearly with specific details
2. Report to analysis_team_supervisor
3. Provide context, attempted solutions, and recommendations

### Quality Gate Importance
Your approval is the quality gate that ensures the migration project proceeds on a solid foundation. Maintain high standards while providing constructive feedback that enables the analysis team to deliver excellent results.
