# Cleanup Tasks: Strip ATX, Rename ACM → LCMP, Minimize Tooling

**Branch**: Work on `main` directly (or create a new branch `cleanup/rename-and-strip`)
**Status**: Not started on `main` — these changes were done on the now-deleted `pod-based-acm` branch

---

## Task 1: Remove all ATX references

### 1.1 Delete ATX-specific files and directories

```bash
# ATX prompts (all versions)
rm -rf structure/prompts/03-business_extraction/atx/
rm -rf structure/prompts/04_test_case_generation/atx/
rm -rf structure/prompts/05_code_generation/atx/
rm -f  structure/prompts/01_analysis/Database/01_analysis_atx.md

# ATX input data
rm -rf structure/input/legacy/atx/

# ATX evaluation documents
rm -f  structure/doc/proposals/pydantic_ai_evaluation.md
rm -f  structure/doc/proposals/bre_evaluation_for_migration.md
rm -f  structure/doc/proposals/ATX_Podlike_Processing_Requirements.md

# ATX presentation
rm -f  presentation/atx-acm-presentation.html

# ATX tools (in testing/)
rm -rf testing/tools/acm-tools/tools/atx/

# ATX test fixtures
rm -rf test_e2e_integration/input/legacy/atx/
rm -rf test_orchestration/input/legacy/atx/

# ATX-related test files
rm -f  structure/tools/acm-tools/config/atx_transformer.yaml
rm -f  structure/tools/acm-tools/tests/unit/test_atx_error_handling.py
rm -f  structure/tools/acm-tools/tests/property/test_atx_assets_loader_properties.py
rm -f  structure/tools/acm-tools/tests/property/test_atx_dependency_loader_properties.py
rm -f  structure/tools/acm-tools/tests/integration/test_atx_dependency_transformer_integration.py
```

### 1.2 Remove ATX sections from config/paths.cfg

Remove these lines (the "ATX Analysis related" block ~lines 17-25):
```
# ATX Analysis related
ATX_BASE_PATH={{SOURCE_BASE_PATH}}/atx
ATX_DATA_DICTIONARY=...
ATX_DATA_LINEAGE=...
ATX_APP_DOMAIN=...
ATX_DEPENDENCY_ANALYSIS=...
ATX_BRE_OUTPUT=...
ATX_APPLICATION_ANALYSIS=...
ATX_BRE_DOMAINS=...
```

And the "ATX Test Case Generation" block (~lines 232-243):
```
# ATX Test Case Generation related (Phase 4-ATX)
ATX_TEST_GENERATION_ROOT=...
... (all ATX_TEST_GENERATION_* variables)
```

### 1.3 Remove ATX from .gitignore

Remove the line: `structure/input/legacy/atx/*`

### 1.4 Remove ATX fields from pydantic_orchestration_architecture.md

In `structure/doc/proposals/pydantic_orchestration_architecture.md`:
- Remove the `# ATX paths (optional)` section from the ProjectConfig class (~6 fields)
- Remove the ATX path resolution in `from_project_config_json()` method
- Remove the `atx/` line from the project structure diagram
- Remove the reference to `pydantic_ai_evaluation.md`

### 1.5 Remove ATX from docs/ReImagine_Framework_Presentation.md

Remove the "Amazon ATX Integration" section (table + description).

### 1.6 Remove ATX from presentation/acm-vision.html

Remove Slide 2 ("ATX Integration — Where Does It Fit?") and renumber remaining slides.

---

## Task 2: Rename ACM → LCMP

### 2.1 Global text replacements (in all .md, .py, .sh, .cfg, .html, .txt files)

```
"Agentic Code Migrator" → "Legacy Code Migration Pipeline"
"Agentic_Code_Migrator" → "Legacy_Code_Migration_Pipeline"
"ACM tools" → "LCMP tools"
"ACM Tools" → "LCMP Tools"
"ACM Framework" → "LCMP Framework"
"ACM pipeline" → "LCMP pipeline"
"ACM agents" → "LCMP agents"
"ACM web" → "LCMP web"
"ACM documentation" → "LCMP documentation"
"ACM Validation" → "LCMP Validation"
" ACM " → " LCMP " (standalone word)
"acm-migrate" → "lcmp-migrate"
"acm init" → "lcmp init"
"acm watch" → "lcmp watch"
"acm ticket" → "lcmp ticket"
"acm tracker" → "lcmp tracker"
```

### 2.2 Directory renames

```bash
mv structure/acm structure/lcmp
mv structure/doc/acm structure/doc/lcmp
mv structure/doc/lcmp/acm.md structure/doc/lcmp/lcmp.md
mv presentation/acm-vision.html presentation/lcmp-vision.html
```

### 2.3 File renames

```bash
mv install_acm_tools.py install_framework_tools.py
```

### 2.4 Update path references

```
"doc/acm/" → "doc/lcmp/"
"acm.md" → "lcmp.md"
"/acm/" → "/lcmp/"
"install_acm_tools" → "install_framework_tools"
"ACM_BASE_PATH" → "LCMP_BASE_PATH"
"ACM_TEMPLATE_VALIDATOR" → "LCMP_TEMPLATE_VALIDATOR"
```

### 2.5 Update .gitignore

```
"structure/tools/acm-tools/" → "structure/tools/framework-tools/"
```

---

## Task 3: Rename acm-tools → framework-tools

### 3.1 Directory rename

```bash
mv structure/tools/acm-tools structure/tools/framework-tools
```

### 3.2 Global text replacement

```
"acm-tools" → "framework-tools"
"acm_tools" → "framework_tools"
"ACM-Tools" → "Framework-Tools"
```

---

## Task 4: Minimize tooling (delete unused tools)

### 4.1 Delete SMF-related tools (not used by any prompt)

```bash
rm -rf structure/tools/framework-tools/tools/smf_analyzer/
rm -rf structure/tools/framework-tools/tools/smf_dashboard/
rm -rf structure/tools/framework-tools/tools/smf_test_data_generator/
rm -f  structure/tools/framework-tools/shared/database/schemas/smf_schemas.py
rm -f  structure/tools/framework-tools/shared/database/schemas/unified_schema.py
rm -f  structure/tools/framework-tools/shared/database/schemas/registry.py
```

### 4.2 Delete unused scripts

```bash
rm -f structure/tools/framework-tools/scripts/benchmark_analysis.py
rm -f structure/tools/framework-tools/scripts/compare_benchmarks.py
rm -f structure/tools/framework-tools/scripts/complete_analysis.sh
rm -f structure/tools/framework-tools/scripts/copy_inventory_to_test_db.sh
rm -f structure/tools/framework-tools/scripts/load_all_data.sh
rm -f structure/tools/framework-tools/scripts/load_test_data_unified.sh
rm -f structure/tools/framework-tools/scripts/load_test_data.sh
rm -f structure/tools/framework-tools/scripts/merge_smf_files.py
rm -f structure/tools/framework-tools/scripts/regenerate_high_mips_data.sh
rm -f structure/tools/framework-tools/scripts/regenerate_test_data.sh
rm -f structure/tools/framework-tools/scripts/restart_dashboard.sh
rm -f structure/tools/framework-tools/scripts/run_all_projects_analysis.sh
rm -f structure/tools/framework-tools/scripts/run_carddemo_analysis.sh
rm -f structure/tools/framework-tools/scripts/run_smftestdata_inventory.sh
rm -f structure/tools/framework-tools/scripts/startDashboard.sh
rm -f structure/tools/framework-tools/scripts/stopDashboard.sh
rm -f structure/tools/framework-tools/scripts/test_cost_queries.sh
rm -f structure/tools/framework-tools/scripts/test_queries.sh
```

### 4.3 Delete unused infrastructure

```bash
rm -rf structure/tools/framework-tools/docs/
rm -rf structure/tools/framework-tools/tests/
rm -rf structure/tools/framework-tools/config/
rm -f  structure/tools/framework-tools/INDEX.md
rm -f  structure/tools/framework-tools/README_original.md
rm -f  structure/tools/framework-tools/README.md
rm -f  structure/tools/framework-tools/requirements-dev.txt
rm -f  structure/tools/framework-tools/pytest.ini
rm -f  structure/tools/framework-tools/NEW_TOOLS_INTEGRATION_SUMMARY.md
```

### 4.4 Clean SMF references from remaining files

After deletions, run:
```bash
find structure/tools/framework-tools -type f \( -name "*.py" -o -name "*.md" \) \
  -exec sed -i '' '/[Ss][Mm][Ff]/d' {} \;
```

And clean setup.py of SMF entry points and package references.

### 4.5 What REMAINS after cleanup (the minimum toolset)

```
structure/tools/
├── check_pod_status.sh              ← pod monitoring
├── consolidate_pod_artifacts.py     ← pod merge consolidation
├── create_pod_worktrees.py          ← pod worktree creation (used by prompts)
├── publish_pods_to_tracker.py       ← tracker integration
└── framework-tools/
    ├── requirements.txt
    ├── requirements-minimal.txt
    ├── setup.py
    ├── shared/                      ← shared utilities (database adapters, config)
    ├── scripts/
    │   ├── run_configurable_analysis.sh   ← used by prompts
    │   ├── run_migration_planner.sh       ← used by prompts
    │   ├── README_CONFIGURABLE_ANALYSIS.md
    │   └── README_migration_planner.md
    └── tools/
        ├── __init__.py
        ├── database_analyzer/       ← used by prompts
        ├── legacy_analyzer/         ← used by run_configurable_analysis.sh
        └── migration_planner/       ← used by run_migration_planner.sh
```

---

## Task 5: Final verification

After all changes, verify:

```bash
# No ATX references remain
grep -rl "ATX\|atx" --include="*.md" --include="*.py" --include="*.sh" --include="*.cfg" --include="*.html" . | grep -v ".git/"

# No acm-tools references remain
grep -rl "acm-tools\|acm_tools" --include="*.md" --include="*.py" --include="*.sh" . | grep -v ".git/"

# No standalone ACM references remain (excluding test/carddemo dirs)
grep -rl "\bACM\b" --include="*.md" --include="*.py" --include="*.sh" . | grep -v ".git/" | grep -v "testing/" | grep -v "carddemo/" | grep -v "test_"

# No SMF tool references remain
grep -rl "smf\|SMF" --include="*.md" --include="*.py" . | grep -v ".git/" | grep -v "testing/" | grep -v "carddemo/"
```

---

## Task 6: Commit and push

```bash
git add -A
git commit -m "Strip ATX references, rename ACM to LCMP, minimize tooling"
git push origin main
```

---

## Notes

- The `testing/` and `carddemo/` directories contain resolved project files with
  hardcoded paths. These are test fixtures and may still contain old references.
  They can be cleaned separately or regenerated with `create_project.py`.
- The `structure/output/` directory may contain generated deliverables from previous
  runs. These are not part of the framework and can be deleted if needed.
- The `temp/` directory contains sample files for evaluation — can be deleted.
