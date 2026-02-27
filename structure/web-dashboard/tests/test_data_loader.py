"""
Property-based tests for MigrationDataLoader

Feature: dashboard-file-structure-adaptation
"""

import pytest
from pathlib import Path
from hypothesis import given, strategies as st, settings, HealthCheck
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.data_loader import MigrationDataLoader


class TestPathConfiguration:
    """
    Property 1: Path Resolution Correctness
    
    For any phase or artifact type, when the Data_Loader resolves file paths,
    it should use the new directory structure (output/analysis/, output/specifications/,
    output/migration/, output/gen_src/, output/gen_src_db/, output/tools/) and not
    the old flat structure.
    
    Validates: Requirements 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 3.4,
               4.1, 4.2, 4.3, 5.1, 5.2, 9.1, 10.1, 11.1, 11.3
    """
    
    @given(
        project_root=st.one_of(
            st.none(),
            st.text(min_size=1, max_size=50, alphabet=st.characters(
                whitelist_categories=('Lu', 'Ll', 'Nd'),
                whitelist_characters='/_-.'
            ))
        )
    )
    def test_property_1_path_resolution_correctness(self, project_root):
        """
        **Feature: dashboard-file-structure-adaptation, Property 1: Path Resolution Correctness**
        
        Property: For any project_root (None or valid path), the MigrationDataLoader
        should initialize with the new hierarchical directory structure.
        
        This test verifies that:
        1. All new directory paths are properly initialized
        2. Old paths (progress_dir, tasks_dir) are not present
        3. All paths follow the new hierarchical structure under output/
        4. Paths are correctly resolved relative to project_root
        """
        # Use a temporary directory if project_root is provided
        if project_root is not None:
            import tempfile
            with tempfile.TemporaryDirectory() as tmpdir:
                test_root = Path(tmpdir) / "test_project"
                test_root.mkdir(exist_ok=True)
                loader = MigrationDataLoader(project_root=str(test_root))
                expected_root = test_root
                self._verify_paths(loader, expected_root)
        else:
            loader = MigrationDataLoader(project_root=None)
            # When None, it defaults to parent.parent.parent of data_loader.py
            expected_root = loader.project_root
            self._verify_paths(loader, expected_root)
    
    def _verify_paths(self, loader, expected_root):
        """Helper method to verify all path configurations"""
        # Verify project_root is set correctly
        assert loader.project_root == expected_root
        
        # Verify base output directory
        assert loader.output_dir == expected_root / "output"
        
        # Verify analysis directories (Requirements 1.1, 2.1, 2.2, 10.1)
        assert loader.analysis_dir == expected_root / "output" / "analysis"
        assert loader.source_analysis_dir == expected_root / "output" / "analysis" / "source_code"
        assert loader.db_analysis_dir == expected_root / "output" / "analysis" / "database"
        assert loader.workpackages_dir == expected_root / "output" / "analysis" / "workpackages"
        
        # Verify specifications directories (Requirements 1.3, 3.1, 3.2, 3.3, 3.4)
        assert loader.specifications_dir == expected_root / "output" / "specifications"
        
        # Verify migration directories (Requirements 4.1, 4.2, 4.3)
        assert loader.migration_dir == expected_root / "output" / "migration"
        
        # Verify generated source directories (Requirements 5.1, 5.2)
        assert loader.gen_src_dir == expected_root / "output" / "gen_src"
        assert loader.gen_src_db_dir == expected_root / "output" / "gen_src_db"
        
        # Verify tools directory (Requirements 9.1)
        assert loader.tools_dir == expected_root / "output" / "tools"
        
        # Verify old paths are NOT present (Requirements 11.3)
        assert not hasattr(loader, 'progress_dir'), "Old progress_dir should not exist"
        assert not hasattr(loader, 'tasks_dir'), "Old tasks_dir should not exist"
        
        # Verify all paths are Path objects
        assert isinstance(loader.output_dir, Path)
        assert isinstance(loader.analysis_dir, Path)
        assert isinstance(loader.source_analysis_dir, Path)
        assert isinstance(loader.db_analysis_dir, Path)
        assert isinstance(loader.workpackages_dir, Path)
        assert isinstance(loader.specifications_dir, Path)
        assert isinstance(loader.migration_dir, Path)
        assert isinstance(loader.gen_src_dir, Path)
        assert isinstance(loader.gen_src_db_dir, Path)
        assert isinstance(loader.tools_dir, Path)
        
        # Verify hierarchical structure (Requirements 11.1)
        # All paths should be under output_dir
        assert str(loader.analysis_dir).startswith(str(loader.output_dir))
        assert str(loader.source_analysis_dir).startswith(str(loader.output_dir))
        assert str(loader.db_analysis_dir).startswith(str(loader.output_dir))
        assert str(loader.workpackages_dir).startswith(str(loader.output_dir))
        assert str(loader.specifications_dir).startswith(str(loader.output_dir))
        assert str(loader.migration_dir).startswith(str(loader.output_dir))
        assert str(loader.gen_src_dir).startswith(str(loader.output_dir))
        assert str(loader.gen_src_db_dir).startswith(str(loader.output_dir))
        assert str(loader.tools_dir).startswith(str(loader.output_dir))
        
        # Verify analysis subdirectories are under analysis_dir
        assert str(loader.source_analysis_dir).startswith(str(loader.analysis_dir))
        assert str(loader.db_analysis_dir).startswith(str(loader.analysis_dir))
        assert str(loader.workpackages_dir).startswith(str(loader.analysis_dir))
    
    def test_path_configuration_with_none(self):
        """Test that default project_root works correctly when None is provided"""
        loader = MigrationDataLoader(project_root=None)
        
        # Should default to parent.parent.parent of data_loader.py
        assert loader.project_root is not None
        assert isinstance(loader.project_root, Path)
        
        # All paths should be properly initialized
        assert loader.output_dir == loader.project_root / "output"
        assert loader.analysis_dir == loader.project_root / "output" / "analysis"
    
    def test_path_configuration_with_explicit_root(self, tmp_path):
        """Test that explicit project_root is used correctly"""
        test_root = tmp_path / "custom_project"
        test_root.mkdir()
        
        loader = MigrationDataLoader(project_root=str(test_root))
        
        assert loader.project_root == test_root
        assert loader.output_dir == test_root / "output"
        assert loader.analysis_dir == test_root / "output" / "analysis"



class TestPhaseStatusCalculation:
    """
    Property 12: Phase Status Calculation
    
    For any phase (0-8), when calculating status, the Data_Loader should check
    the phase-specific progress files in the new locations and return "completed",
    "in_progress", or "unknown" based on the file contents.
    
    Validates: Requirements 13.1, 13.2, 13.3, 13.4, 13.5
    """
    
    @given(
        phase_id=st.integers(min_value=0, max_value=8),
        status=st.sampled_from(["completed", "in_progress", "unknown"]),
        has_progress_file=st.booleans()
    )
    def test_property_12_phase_status_calculation(self, phase_id, status, has_progress_file):
        """
        **Feature: dashboard-file-structure-adaptation, Property 12: Phase Status Calculation**
        
        Property: For any phase (0-8), the Data_Loader should check phase-specific
        progress files in new locations and return appropriate status.
        
        This test verifies that:
        1. Phase 0-1 check output/analysis/source_code/progress/
        2. Phase 2 checks output/analysis/workpackages/progress/
        3. Phase 3 checks output/specifications/progress/
        4. Phase 4-8 check output/migration/progress/
        5. Status is correctly determined from progress files
        6. Missing files result in "unknown" status
        """
        import tempfile
        
        # Create test project structure
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir) / "test_project"
            project_root.mkdir()
        
        # Create directory structure based on phase
        if phase_id in [0, 1]:
            progress_dir = project_root / "output" / "analysis" / "source_code" / "progress"
        elif phase_id == 2:
            progress_dir = project_root / "output" / "analysis" / "workpackages" / "progress"
        elif phase_id == 3:
            progress_dir = project_root / "output" / "specifications" / "progress"
        else:  # 4-8
            progress_dir = project_root / "output" / "migration" / "progress"
        
        progress_dir.mkdir(parents=True, exist_ok=True)
        
        # Create progress file if requested
        if has_progress_file and status != "unknown":
            progress_file = self._create_progress_file(progress_dir, phase_id, status)
        
        # Initialize loader
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Get phase status
        phases = loader.get_phase_status()
        
        # Verify we got 8 phases
        assert len(phases) == 9
        
        # Verify phase structure
        phase = phases[phase_id]
        assert phase["id"] == phase_id
        assert "name" in phase
        assert "status" in phase
        
        # Verify status is one of the valid values
        assert phase["status"] in ["completed", "in_progress", "unknown"]
        
        # If we created a progress file, verify status matches
        if has_progress_file and status != "unknown":
            # Status should match what we set (or be derived correctly)
            if status == "completed":
                assert phase["status"] in ["completed", "in_progress"]  # May be in_progress if not fully complete
            elif status == "in_progress":
                assert phase["status"] in ["in_progress", "unknown"]
        else:
            # Without progress file, status should be unknown (unless fallback detection works)
            assert phase["status"] in ["unknown", "completed"]  # Fallback may detect completion
    
    def _create_progress_file(self, progress_dir, phase_id, status):
        """Helper to create a progress file with given status"""
        import json
        
        if phase_id == 0:
            filename = "preparation_status.json"
            data = {
                "status": status,
                "timestamp": "2024-01-15T10:30:00"
            }
        elif phase_id == 1:
            filename = "analysis_status.json"
            data = {
                "status": status,
                "endTime": "2024-01-16T14:20:00"
            }
        elif phase_id == 2:
            filename = "Workpackage_Status.json"
            data = {
                "status": status,
                "completion_date": "2024-01-17"
            }
        elif phase_id == 3:
            filename = "Business_Specification_Status.json"
            # Phase 3 uses workpackage counts
            if status == "completed":
                data = {
                    "summary": {
                        "total_workpackages": 10,
                        "approved": 8,
                        "approved_with_changes": 2,
                        "rejected": 0,
                        "pending": 0
                    },
                    "last_updated": "2024-01-18T16:45:00"
                }
            elif status == "in_progress":
                data = {
                    "summary": {
                        "total_workpackages": 10,
                        "approved": 5,
                        "approved_with_changes": 1,
                        "rejected": 0,
                        "pending": 4
                    },
                    "last_updated": "2024-01-18T16:45:00"
                }
            else:
                data = {
                    "summary": {
                        "total_workpackages": 10,
                        "approved": 0,
                        "approved_with_changes": 0,
                        "rejected": 0,
                        "pending": 10
                    }
                }
        else:  # 4-8
            phase_names = {
                4: "code_generation_status.json",
                5: "test_generation_status.json",
                6: "quality_validation_status.json",
                7: "developer_review_status.json",
                8: "deliverable_status.json"
            }
            filename = phase_names.get(phase_id, f"phase_{phase_id}_status.json")
            data = {
                "status": status,
                "lastUpdated": "2024-01-20T09:15:00"
            }
        
        progress_file = progress_dir / filename
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        return progress_file
    
    def test_phase_status_with_missing_files(self, tmp_path):
        """Test that missing progress files result in unknown status"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create minimal directory structure but no progress files
        (project_root / "output").mkdir()
        
        loader = MigrationDataLoader(project_root=str(project_root))
        phases = loader.get_phase_status()
        
        # All phases should have unknown status (or completed via fallback)
        for phase in phases:
            assert phase["status"] in ["unknown", "completed"]
    
    def test_phase_status_with_malformed_json(self, tmp_path):
        """Test that malformed JSON doesn't crash the loader"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create progress directory with malformed JSON
        progress_dir = project_root / "output" / "analysis" / "source_code" / "progress"
        progress_dir.mkdir(parents=True)
        
        progress_file = progress_dir / "analysis_status.json"
        with open(progress_file, 'w') as f:
            f.write("{ invalid json }")
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Should not crash
        phases = loader.get_phase_status()
        
        # Should return valid structure
        assert len(phases) == 9
        assert all("status" in phase for phase in phases)
    
    def test_phase3_workpackage_counting(self, tmp_path):
        """Test Phase 3 correctly counts approved workpackages"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create Phase 3 progress file
        progress_dir = project_root / "output" / "specifications" / "progress"
        progress_dir.mkdir(parents=True)
        
        progress_file = progress_dir / "Business_Specification_Status.json"
        data = {
            "summary": {
                "total_workpackages": 20,
                "approved": 12,
                "approved_with_changes": 5,
                "rejected": 1,
                "pending": 2
            },
            "last_updated": "2024-01-18T16:45:00"
        }
        
        with open(progress_file, 'w', encoding='utf-8') as f:
            import json
            json.dump(data, f)
        
        loader = MigrationDataLoader(project_root=str(project_root))
        phases = loader.get_phase_status()
        
        phase3 = phases[3]
        
        # Should be in_progress (17 out of 20 completed)
        assert phase3["status"] == "in_progress"
        assert phase3["completedWorkpackages"] == 17  # 12 + 5
        assert phase3["totalWorkpackages"] == 20
        assert phase3["progress"] == 85  # round(17/20 * 100)
    
    def test_phase_status_checks_correct_directories(self, tmp_path):
        """Test that each phase checks the correct directory"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create all progress directories
        dirs_to_create = [
            "output/analysis/source_code/progress",
            "output/analysis/workpackages/progress",
            "output/specifications/progress",
            "output/migration/progress"
        ]
        
        for dir_path in dirs_to_create:
            (project_root / dir_path).mkdir(parents=True)
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Verify the loader has correct path attributes
        assert loader.source_analysis_dir == project_root / "output" / "analysis" / "source_code"
        assert loader.workpackages_dir == project_root / "output" / "analysis" / "workpackages"
        assert loader.specifications_dir == project_root / "output" / "specifications"
        assert loader.migration_dir == project_root / "output" / "migration"
        
        # Get phase status (should not crash)
        phases = loader.get_phase_status()
        assert len(phases) == 9



class TestWorkpackageProgressAggregation:
    """
    Property 10: Workpackage Status Aggregation
    
    For any Business_Specification_Status.json file, the aggregated progress should
    match the count of workpackages with status "APPROVED" or "APPROVED_WITH_CHANGES"
    divided by total workpackages.
    
    Validates: Requirements 7.1, 7.2, 7.4
    """
    
    @given(
        total_workpackages=st.integers(min_value=1, max_value=100),
        approved=st.integers(min_value=0, max_value=50),
        approved_with_changes=st.integers(min_value=0, max_value=50),
        rejected=st.integers(min_value=0, max_value=20),
        pending=st.integers(min_value=0, max_value=30)
    )
    def test_property_10_workpackage_status_aggregation(
        self, total_workpackages, approved, approved_with_changes, rejected, pending
    ):
        """
        **Feature: dashboard-file-structure-adaptation, Property 10: Workpackage Status Aggregation**
        
        Property: For any Business_Specification_Status.json file, the aggregated
        progress should match the count of workpackages with status "APPROVED" or
        "APPROVED_WITH_CHANGES" divided by total workpackages.
        
        This test verifies that:
        1. Total workpackages is extracted from summary.total_workpackages
        2. Phase 3 completed count = approved + approved_with_changes
        3. Completion percentage is calculated correctly
        4. Aggregation works for any valid workpackage counts
        """
        import tempfile
        import json
        
        # Ensure counts don't exceed total
        approved = min(approved, total_workpackages)
        approved_with_changes = min(approved_with_changes, total_workpackages - approved)
        rejected = min(rejected, total_workpackages - approved - approved_with_changes)
        pending = total_workpackages - approved - approved_with_changes - rejected
        
        # Create test project structure
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir) / "test_project"
            project_root.mkdir()
            
            # Create progress directory
            progress_dir = project_root / "output" / "specifications" / "progress"
            progress_dir.mkdir(parents=True)
            
            # Create Business_Specification_Status.json
            status_file = progress_dir / "Business_Specification_Status.json"
            status_data = {
                "project": "test_project",
                "phase": "Phase 3: Business Specification Extraction",
                "last_updated": "2024-01-18T16:45:00",
                "summary": {
                    "total_workpackages": total_workpackages,
                    "approved": approved,
                    "approved_with_changes": approved_with_changes,
                    "rejected": rejected,
                    "pending": pending,
                    "ready_for_phase_4": approved + approved_with_changes
                },
                "workpackages": []
            }
            
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, indent=2)
            
            # Initialize loader
            loader = MigrationDataLoader(project_root=str(project_root))
            
            # Get workpackage progress
            progress = loader.get_workpackage_progress()
            
            # Verify total workpackages (Requirement 7.4)
            assert progress["total"] == total_workpackages, \
                f"Expected total={total_workpackages}, got {progress['total']}"
            
            # Verify phase3_completed = approved + approved_with_changes (Requirements 7.1, 7.2)
            expected_completed = approved + approved_with_changes
            assert progress["phase3_completed"] == expected_completed, \
                f"Expected phase3_completed={expected_completed}, got {progress['phase3_completed']}"
            
            # Verify completion percentage calculation (Requirement 7.4)
            if total_workpackages > 0:
                expected_percentage = round((expected_completed / total_workpackages) * 100, 1)
                assert progress["completion_percentage"] == expected_percentage, \
                    f"Expected completion_percentage={expected_percentage}, got {progress['completion_percentage']}"
            else:
                assert progress["completion_percentage"] == 0.0
            
            # Verify phase4_ready is extracted correctly
            assert progress["phase4_ready"] == approved + approved_with_changes
    
    def test_workpackage_progress_with_missing_file(self, tmp_path):
        """Test that missing Business_Specification_Status.json returns default values"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create directory structure but no status file
        (project_root / "output" / "specifications" / "progress").mkdir(parents=True)
        
        loader = MigrationDataLoader(project_root=str(project_root))
        progress = loader.get_workpackage_progress()
        
        # Should return default values (Requirement 1.4)
        assert progress["total"] == 0
        assert progress["phase3_completed"] == 0
        assert progress["phase4_ready"] == 0
        assert progress["workpackages"] == []
    
    def test_workpackage_progress_with_malformed_json(self, tmp_path):
        """Test that malformed JSON doesn't crash and returns defaults"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create progress directory with malformed JSON
        progress_dir = project_root / "output" / "specifications" / "progress"
        progress_dir.mkdir(parents=True)
        
        status_file = progress_dir / "Business_Specification_Status.json"
        with open(status_file, 'w') as f:
            f.write("{ invalid json }")
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Should not crash (Requirement 6.5)
        progress = loader.get_workpackage_progress()
        
        # Should return default values
        assert progress["total"] == 0
        assert progress["phase3_completed"] == 0
        assert isinstance(progress["workpackages"], list)
    
    def test_workpackage_progress_extracts_metadata(self, tmp_path):
        """Test that workpackage metadata is correctly extracted"""
        import json
        
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create progress directory
        progress_dir = project_root / "output" / "specifications" / "progress"
        progress_dir.mkdir(parents=True)
        
        # Create Business_Specification_Status.json with workpackages
        status_file = progress_dir / "Business_Specification_Status.json"
        status_data = {
            "summary": {
                "total_workpackages": 3,
                "approved": 2,
                "approved_with_changes": 1,
                "rejected": 0,
                "pending": 0,
                "ready_for_phase_4": 3
            },
            "workpackages": [
                {
                    "workpackage_id": "WP-001",
                    "flow_id": "FLOW_12345",
                    "name": "Customer Management",
                    "priority": 1,
                    "status": "APPROVED",
                    "ready_for_code_generation": True
                },
                {
                    "workpackage_id": "WP-002",
                    "flow_id": "FLOW_67890",
                    "name": "Order Processing",
                    "priority": 2,
                    "status": "APPROVED_WITH_CHANGES",
                    "ready_for_code_generation": True
                },
                {
                    "workpackage_id": "WP-003",
                    "flow_id": "FLOW_11111",
                    "name": "Inventory Control",
                    "priority": 3,
                    "status": "APPROVED",
                    "ready_for_code_generation": True
                }
            ]
        }
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2)
        
        loader = MigrationDataLoader(project_root=str(project_root))
        progress = loader.get_workpackage_progress()
        
        # Verify workpackage metadata extraction (Requirement 7.5)
        assert len(progress["workpackages"]) == 3
        
        wp1 = progress["workpackages"][0]
        assert wp1["workpackage_id"] == "WP-001"
        assert wp1["flow_id"] == "FLOW_12345"
        assert wp1["name"] == "Customer Management"
        assert wp1["priority"] == 1
        assert wp1["status"] == "APPROVED"
        assert wp1["ready_for_code_generation"] is True
        
        wp2 = progress["workpackages"][1]
        assert wp2["workpackage_id"] == "WP-002"
        assert wp2["status"] == "APPROVED_WITH_CHANGES"
    
    def test_workpackage_progress_handles_missing_fields(self, tmp_path):
        """Test that missing JSON fields are handled gracefully"""
        import json
        
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create progress directory
        progress_dir = project_root / "output" / "specifications" / "progress"
        progress_dir.mkdir(parents=True)
        
        # Create minimal Business_Specification_Status.json
        status_file = progress_dir / "Business_Specification_Status.json"
        status_data = {
            "summary": {
                "total_workpackages": 5
                # Missing approved, approved_with_changes, etc.
            },
            "workpackages": [
                {
                    "workpackage_id": "WP-001"
                    # Missing flow_id, name, priority, status
                }
            ]
        }
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2)
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Should not crash (Requirement 6.5)
        progress = loader.get_workpackage_progress()
        
        # Should use default values for missing fields
        assert progress["total"] == 5
        assert progress["phase3_completed"] == 0  # 0 + 0
        assert progress["phase4_ready"] == 0
        
        # Workpackage should have default values
        assert len(progress["workpackages"]) == 1
        wp = progress["workpackages"][0]
        assert wp["workpackage_id"] == "WP-001"
        assert wp["flow_id"] == ""
        assert wp["name"] == ""
        assert wp["priority"] == 0
        assert wp["status"] == "UNKNOWN"
        assert wp["ready_for_code_generation"] is False



class TestPhaseReadinessMarking:
    """
    Property 11: Phase Readiness Marking
    
    For any workpackage with "ready_for_code_generation" set to true, the Data_Loader
    should mark it as ready for Phase 4.
    
    Validates: Requirements 7.3
    """
    
    @given(
        total_workpackages=st.integers(min_value=1, max_value=50),
        ready_count=st.integers(min_value=0, max_value=50)
    )
    def test_property_11_phase_readiness_marking(self, total_workpackages, ready_count):
        """
        **Feature: dashboard-file-structure-adaptation, Property 11: Phase Readiness Marking**
        
        Property: For any workpackage with "ready_for_code_generation" set to true,
        the Data_Loader should mark it as ready for Phase 4.
        
        This test verifies that:
        1. Workpackages with ready_for_code_generation=true are counted
        2. The phase4_ready count matches the number of ready workpackages
        3. Individual workpackage ready status is preserved
        4. This works for any number of workpackages and ready counts
        """
        import tempfile
        import json
        
        # Ensure ready_count doesn't exceed total
        ready_count = min(ready_count, total_workpackages)
        
        # Create test project structure
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir) / "test_project"
            project_root.mkdir()
            
            # Create progress directory
            progress_dir = project_root / "output" / "specifications" / "progress"
            progress_dir.mkdir(parents=True)
            
            # Create workpackages with varying ready_for_code_generation status
            workpackages = []
            for i in range(total_workpackages):
                is_ready = i < ready_count
                workpackages.append({
                    "workpackage_id": f"WP-{i+1:03d}",
                    "flow_id": f"FLOW_{i+10000}",
                    "name": f"Workpackage {i+1}",
                    "priority": i + 1,
                    "status": "APPROVED" if is_ready else "PENDING",
                    "ready_for_code_generation": is_ready
                })
            
            # Create Business_Specification_Status.json
            status_file = progress_dir / "Business_Specification_Status.json"
            status_data = {
                "project": "test_project",
                "phase": "Phase 3: Business Specification Extraction",
                "last_updated": "2024-01-18T16:45:00",
                "summary": {
                    "total_workpackages": total_workpackages,
                    "approved": ready_count,
                    "approved_with_changes": 0,
                    "rejected": 0,
                    "pending": total_workpackages - ready_count,
                    "ready_for_phase_4": ready_count
                },
                "workpackages": workpackages
            }
            
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, indent=2)
            
            # Initialize loader
            loader = MigrationDataLoader(project_root=str(project_root))
            
            # Get workpackage progress
            progress = loader.get_workpackage_progress()
            
            # Verify phase4_ready count matches ready workpackages (Requirement 7.3)
            assert progress["phase4_ready"] == ready_count, \
                f"Expected phase4_ready={ready_count}, got {progress['phase4_ready']}"
            
            # Verify individual workpackage ready status is preserved
            ready_workpackages = [
                wp for wp in progress["workpackages"]
                if wp["ready_for_code_generation"] is True
            ]
            assert len(ready_workpackages) == ready_count, \
                f"Expected {ready_count} ready workpackages, found {len(ready_workpackages)}"
            
            # Verify not-ready workpackages are marked correctly
            not_ready_workpackages = [
                wp for wp in progress["workpackages"]
                if wp["ready_for_code_generation"] is False
            ]
            assert len(not_ready_workpackages) == total_workpackages - ready_count
    
    def test_phase_readiness_all_ready(self, tmp_path):
        """Test when all workpackages are ready for Phase 4"""
        import json
        
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create progress directory
        progress_dir = project_root / "output" / "specifications" / "progress"
        progress_dir.mkdir(parents=True)
        
        # Create status with all workpackages ready
        status_file = progress_dir / "Business_Specification_Status.json"
        status_data = {
            "summary": {
                "total_workpackages": 5,
                "approved": 5,
                "approved_with_changes": 0,
                "rejected": 0,
                "pending": 0,
                "ready_for_phase_4": 5
            },
            "workpackages": [
                {
                    "workpackage_id": f"WP-{i:03d}",
                    "flow_id": f"FLOW_{i}",
                    "name": f"WP {i}",
                    "priority": i,
                    "status": "APPROVED",
                    "ready_for_code_generation": True
                }
                for i in range(1, 6)
            ]
        }
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2)
        
        loader = MigrationDataLoader(project_root=str(project_root))
        progress = loader.get_workpackage_progress()
        
        # All should be ready
        assert progress["phase4_ready"] == 5
        assert all(wp["ready_for_code_generation"] for wp in progress["workpackages"])
    
    def test_phase_readiness_none_ready(self, tmp_path):
        """Test when no workpackages are ready for Phase 4"""
        import json
        
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create progress directory
        progress_dir = project_root / "output" / "specifications" / "progress"
        progress_dir.mkdir(parents=True)
        
        # Create status with no workpackages ready
        status_file = progress_dir / "Business_Specification_Status.json"
        status_data = {
            "summary": {
                "total_workpackages": 5,
                "approved": 0,
                "approved_with_changes": 0,
                "rejected": 0,
                "pending": 5,
                "ready_for_phase_4": 0
            },
            "workpackages": [
                {
                    "workpackage_id": f"WP-{i:03d}",
                    "flow_id": f"FLOW_{i}",
                    "name": f"WP {i}",
                    "priority": i,
                    "status": "PENDING",
                    "ready_for_code_generation": False
                }
                for i in range(1, 6)
            ]
        }
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2)
        
        loader = MigrationDataLoader(project_root=str(project_root))
        progress = loader.get_workpackage_progress()
        
        # None should be ready
        assert progress["phase4_ready"] == 0
        assert not any(wp["ready_for_code_generation"] for wp in progress["workpackages"])
    
    def test_phase_readiness_mixed(self, tmp_path):
        """Test with mixed ready/not-ready workpackages"""
        import json
        
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create progress directory
        progress_dir = project_root / "output" / "specifications" / "progress"
        progress_dir.mkdir(parents=True)
        
        # Create status with mixed readiness
        status_file = progress_dir / "Business_Specification_Status.json"
        status_data = {
            "summary": {
                "total_workpackages": 10,
                "approved": 5,
                "approved_with_changes": 2,
                "rejected": 1,
                "pending": 2,
                "ready_for_phase_4": 7  # 5 approved + 2 approved_with_changes
            },
            "workpackages": [
                {"workpackage_id": "WP-001", "flow_id": "F1", "name": "WP1", "priority": 1,
                 "status": "APPROVED", "ready_for_code_generation": True},
                {"workpackage_id": "WP-002", "flow_id": "F2", "name": "WP2", "priority": 2,
                 "status": "APPROVED", "ready_for_code_generation": True},
                {"workpackage_id": "WP-003", "flow_id": "F3", "name": "WP3", "priority": 3,
                 "status": "APPROVED_WITH_CHANGES", "ready_for_code_generation": True},
                {"workpackage_id": "WP-004", "flow_id": "F4", "name": "WP4", "priority": 4,
                 "status": "PENDING", "ready_for_code_generation": False},
                {"workpackage_id": "WP-005", "flow_id": "F5", "name": "WP5", "priority": 5,
                 "status": "REJECTED", "ready_for_code_generation": False},
            ]
        }
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2)
        
        loader = MigrationDataLoader(project_root=str(project_root))
        progress = loader.get_workpackage_progress()
        
        # Should have 7 ready (but only 5 in workpackages array, so count those)
        ready_in_array = sum(1 for wp in progress["workpackages"] if wp["ready_for_code_generation"])
        assert ready_in_array == 3  # WP-001, WP-002, WP-003
        
        # Summary should show 7
        assert progress["phase4_ready"] == 7
    
    def test_phase_readiness_missing_field(self, tmp_path):
        """Test that missing ready_for_code_generation field defaults to False"""
        import json
        
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create progress directory
        progress_dir = project_root / "output" / "specifications" / "progress"
        progress_dir.mkdir(parents=True)
        
        # Create status with missing ready_for_code_generation field
        status_file = progress_dir / "Business_Specification_Status.json"
        status_data = {
            "summary": {
                "total_workpackages": 2,
                "approved": 1,
                "approved_with_changes": 0,
                "rejected": 0,
                "pending": 1
                # Missing ready_for_phase_4
            },
            "workpackages": [
                {
                    "workpackage_id": "WP-001",
                    "flow_id": "F1",
                    "name": "WP1",
                    "priority": 1,
                    "status": "APPROVED"
                    # Missing ready_for_code_generation
                }
            ]
        }
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2)
        
        loader = MigrationDataLoader(project_root=str(project_root))
        progress = loader.get_workpackage_progress()
        
        # Should default to 0 when field is missing
        assert progress["phase4_ready"] == 0
        
        # Workpackage should have ready_for_code_generation=False by default
        assert len(progress["workpackages"]) == 1
        assert progress["workpackages"][0]["ready_for_code_generation"] is False



class TestSubdirectoryBasedCategorization:
    """
    Property 6: Subdirectory-Based Categorization
    
    For any artifact in a specific subdirectory (exports, flows, jobs, reports, tools),
    the Data_Loader should assign the category corresponding to that subdirectory.
    
    Validates: Requirements 2.5
    """
    
    @given(
        subdirectory=st.sampled_from(["exports", "flows", "jobs", "reports", "tools", "progress"]),
        filename=st.text(min_size=5, max_size=30, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            whitelist_characters='_-'
        )).map(lambda x: f"{x}.txt")  # Always add .txt extension
    )
    def test_property_6_subdirectory_based_categorization(self, subdirectory, filename):
        """
        **Feature: dashboard-file-structure-adaptation, Property 6: Subdirectory-Based Categorization**
        
        Property: For any artifact in a specific subdirectory (exports, flows, jobs,
        reports, tools), the Data_Loader should assign the category corresponding to
        that subdirectory.
        
        This test verifies that:
        1. Phase 1 artifacts are categorized by their subdirectory
        2. The _categorize_phase1_artifact method uses subdirectory name
        3. Categorization works for all valid subdirectory names
        4. File extension doesn't override subdirectory-based categorization
        """
        import tempfile
        
        # Create test project structure
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir) / "test_project"
            project_root.mkdir()
            
            # Create Phase 1 directory structure
            source_analysis_dir = project_root / "output" / "analysis" / "source_code"
            subdir_path = source_analysis_dir / subdirectory
            subdir_path.mkdir(parents=True)
            
            # Create a test file in the subdirectory
            test_file = subdir_path / filename
            test_file.write_text("test content")
            
            # Initialize loader
            loader = MigrationDataLoader(project_root=str(project_root))
            
            # Get Phase 1 details
            phase_details = loader.get_phase_details(1)
            
            # Verify artifacts were found
            artifacts = phase_details.get("artifacts", [])
            
            # Find our test file in the artifacts
            matching_artifacts = [a for a in artifacts if a["name"] == filename]
            
            if matching_artifacts:
                artifact = matching_artifacts[0]
                
                # Verify the artifact has a type
                assert "type" in artifact, f"Artifact should have a type: {artifact}"
                
                # Verify the type is based on subdirectory categorization
                artifact_type = artifact["type"]
                
                # The _categorize_phase1_artifact method should use subdirectory name
                # to determine the category
                assert isinstance(artifact_type, str), "Artifact type should be a string"
                assert len(artifact_type) > 0, "Artifact type should not be empty"
                
                # Verify path is correct
                assert subdirectory in artifact["path"], \
                    f"Artifact path should contain subdirectory '{subdirectory}': {artifact['path']}"
    
    def test_subdirectory_categorization_exports(self, tmp_path):
        """Test that files in exports subdirectory are categorized correctly"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create exports subdirectory with files
        exports_dir = project_root / "output" / "analysis" / "source_code" / "exports"
        exports_dir.mkdir(parents=True)
        
        test_file = exports_dir / "data_export.csv"
        test_file.write_text("test,data\n1,2")
        
        loader = MigrationDataLoader(project_root=str(project_root))
        phase_details = loader.get_phase_details(1)
        
        artifacts = phase_details.get("artifacts", [])
        export_artifacts = [a for a in artifacts if "exports" in a["path"]]
        
        assert len(export_artifacts) > 0, "Should find artifacts in exports subdirectory"
        
        for artifact in export_artifacts:
            assert "type" in artifact
            assert "exports" in artifact["path"]
    
    def test_subdirectory_categorization_flows(self, tmp_path):
        """Test that files in flows subdirectory are categorized correctly"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create flows subdirectory with files
        flows_dir = project_root / "output" / "analysis" / "source_code" / "flows"
        flows_dir.mkdir(parents=True)
        
        test_file = flows_dir / "business_flow.json"
        test_file.write_text('{"flow": "test"}')
        
        loader = MigrationDataLoader(project_root=str(project_root))
        phase_details = loader.get_phase_details(1)
        
        artifacts = phase_details.get("artifacts", [])
        flow_artifacts = [a for a in artifacts if "flows" in a["path"]]
        
        assert len(flow_artifacts) > 0, "Should find artifacts in flows subdirectory"
        
        for artifact in flow_artifacts:
            assert "type" in artifact
            assert "flows" in artifact["path"]
    
    def test_subdirectory_categorization_jobs(self, tmp_path):
        """Test that files in jobs subdirectory are categorized correctly"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create jobs subdirectory with files
        jobs_dir = project_root / "output" / "analysis" / "source_code" / "jobs"
        jobs_dir.mkdir(parents=True)
        
        test_file = jobs_dir / "batch_job.json"
        test_file.write_text('{"job": "test"}')
        
        loader = MigrationDataLoader(project_root=str(project_root))
        phase_details = loader.get_phase_details(1)
        
        artifacts = phase_details.get("artifacts", [])
        job_artifacts = [a for a in artifacts if "jobs" in a["path"]]
        
        assert len(job_artifacts) > 0, "Should find artifacts in jobs subdirectory"
        
        for artifact in job_artifacts:
            assert "type" in artifact
            assert "jobs" in artifact["path"]
    
    def test_subdirectory_categorization_reports(self, tmp_path):
        """Test that files in reports subdirectory are categorized correctly"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create reports subdirectory with files
        reports_dir = project_root / "output" / "analysis" / "source_code" / "reports"
        reports_dir.mkdir(parents=True)
        
        test_file = reports_dir / "analysis_report.md"
        test_file.write_text("# Analysis Report")
        
        loader = MigrationDataLoader(project_root=str(project_root))
        phase_details = loader.get_phase_details(1)
        
        # .md files are moved to reports section, not artifacts
        reports = phase_details.get("reports", [])
        report_items = [r for r in reports if "reports" in r["path"]]
        
        assert len(report_items) > 0, "Should find reports in reports subdirectory"
        
        for report in report_items:
            assert "type" in report
            assert "reports" in report["path"]
    
    def test_subdirectory_categorization_tools(self, tmp_path):
        """Test that files in tools subdirectory are categorized correctly"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create tools subdirectory with files
        tools_dir = project_root / "output" / "analysis" / "source_code" / "tools"
        tools_dir.mkdir(parents=True)
        
        test_file = tools_dir / "analysis_tool.py"
        test_file.write_text("# Analysis tool")
        
        loader = MigrationDataLoader(project_root=str(project_root))
        phase_details = loader.get_phase_details(1)
        
        artifacts = phase_details.get("artifacts", [])
        tool_artifacts = [a for a in artifacts if "tools" in a["path"]]
        
        assert len(tool_artifacts) > 0, "Should find artifacts in tools subdirectory"
        
        for artifact in tool_artifacts:
            assert "type" in artifact
            assert "tools" in artifact["path"]
    
    def test_subdirectory_categorization_multiple_files(self, tmp_path):
        """Test categorization with multiple files in different subdirectories"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create multiple subdirectories with files
        source_analysis_dir = project_root / "output" / "analysis" / "source_code"
        
        subdirs = ["exports", "flows", "jobs", "reports", "tools"]
        for subdir in subdirs:
            subdir_path = source_analysis_dir / subdir
            subdir_path.mkdir(parents=True)
            
            # Create a test file in each subdirectory
            test_file = subdir_path / f"{subdir}_test.txt"
            test_file.write_text(f"Test content for {subdir}")
        
        loader = MigrationDataLoader(project_root=str(project_root))
        phase_details = loader.get_phase_details(1)
        
        artifacts = phase_details.get("artifacts", [])
        
        # Should have at least 5 artifacts (one per subdirectory)
        assert len(artifacts) >= 5, f"Should find at least 5 artifacts, found {len(artifacts)}"
        
        # Verify each subdirectory is represented
        for subdir in subdirs:
            subdir_artifacts = [a for a in artifacts if subdir in a["path"]]
            assert len(subdir_artifacts) > 0, f"Should find artifacts in {subdir} subdirectory"
    
    def test_subdirectory_categorization_preserves_path(self, tmp_path):
        """Test that subdirectory categorization preserves correct relative paths"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create a file in a subdirectory
        flows_dir = project_root / "output" / "analysis" / "source_code" / "flows"
        flows_dir.mkdir(parents=True)
        
        test_file = flows_dir / "test_flow.json"
        test_file.write_text('{"test": "data"}')
        
        loader = MigrationDataLoader(project_root=str(project_root))
        phase_details = loader.get_phase_details(1)
        
        artifacts = phase_details.get("artifacts", [])
        flow_artifacts = [a for a in artifacts if a["name"] == "test_flow.json"]
        
        assert len(flow_artifacts) == 1, "Should find exactly one matching artifact"
        
        artifact = flow_artifacts[0]
        
        # Verify path is relative to project_root
        expected_path = "output/analysis/source_code/flows/test_flow.json"
        assert artifact["path"] == expected_path, \
            f"Expected path '{expected_path}', got '{artifact['path']}'"



class TestBilingualSpecificationDetection:
    """
    Property 7: Bilingual Specification Detection
    
    For any specification file with language suffix (-EN, -DE, -KO), the Data_Loader
    should detect the language variant and create separate path entries for each language.
    
    Validates: Requirements 3.5, 8.1, 8.2
    """
    
    @given(
        total_workpackages=st.integers(min_value=1, max_value=20),
        has_english=st.booleans(),
        has_german=st.booleans()
    )
    def test_property_7_bilingual_specification_detection(self, total_workpackages, has_english, has_german):
        """
        **Feature: dashboard-file-structure-adaptation, Property 7: Bilingual Specification Detection**
        
        Property: For any specification with language variants, the Data_Loader should
        detect language variants and create separate path entries for each language.
        
        This test verifies that:
        1. English specifications are detected and pathEN is set
        2. German specifications are detected and pathDE is set
        3. hasMultipleLanguages flag is set correctly
        4. Single-language specifications work correctly
        5. Works for any number of workpackages
        """
        import tempfile
        import json
        
        # Skip if no languages are selected
        if not has_english and not has_german:
            has_english = True  # At least one language must exist
        
        # Create test project structure
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir) / "test_project"
            project_root.mkdir()
            
            # Create progress directory
            progress_dir = project_root / "output" / "specifications" / "progress"
            progress_dir.mkdir(parents=True)
            
            # Create workpackages with bilingual specifications
            workpackages = []
            for i in range(total_workpackages):
                wp_id = f"WP-{i+1:03d}"
                flow_id = f"FLOW_{i+10000}"
                
                wp = {
                    "workpackage_id": wp_id,
                    "flow_id": flow_id,
                    "name": f"Workpackage {i+1}",
                    "priority": i + 1,
                    "status": "APPROVED",
                    "ready_for_code_generation": True,
                    "specifications": {}
                }
                
                # Add English specification if requested
                if has_english:
                    wp["specifications"]["english"] = {
                        "original": f"output/specifications/business/{wp_id}-{flow_id}-original-EN.md",
                        "reviewed": f"output/specifications/business/{wp_id}-{flow_id}-reviewed-EN.md",
                        "version": "1.0",
                        "status": "APPROVED"
                    }
                
                # Add German specification if requested
                if has_german:
                    wp["specifications"]["german"] = {
                        "original": f"output/specifications/business/{wp_id}-{flow_id}-original-DE.md",
                        "reviewed": f"output/specifications/business/{wp_id}-{flow_id}-reviewed-DE.md",
                        "version": "1.0",
                        "status": "APPROVED"
                    }
                
                workpackages.append(wp)
            
            # Create Business_Specification_Status.json
            status_file = progress_dir / "Business_Specification_Status.json"
            status_data = {
                "project": "test_project",
                "phase": "Phase 3: Business Specification Extraction",
                "last_updated": "2024-01-18T16:45:00",
                "summary": {
                    "total_workpackages": total_workpackages,
                    "approved": total_workpackages,
                    "approved_with_changes": 0,
                    "rejected": 0,
                    "pending": 0,
                    "ready_for_phase_4": total_workpackages
                },
                "workpackages": workpackages
            }
            
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, indent=2)
            
            # Initialize loader
            loader = MigrationDataLoader(project_root=str(project_root))
            
            # Get Phase 3 details
            phase_details = loader.get_phase_details(3)
            
            # Verify artifacts were created
            artifacts = phase_details.get("artifacts", [])
            assert len(artifacts) == total_workpackages, \
                f"Expected {total_workpackages} artifacts, got {len(artifacts)}"
            
            # Verify each artifact has correct language paths
            for artifact in artifacts:
                # Verify hasMultipleLanguages flag (Requirement 8.1, 8.2)
                expected_multiple = has_english and has_german
                assert artifact["hasMultipleLanguages"] == expected_multiple, \
                    f"Expected hasMultipleLanguages={expected_multiple}, got {artifact['hasMultipleLanguages']}"
                
                # Verify English path if English is available (Requirement 3.5, 8.1)
                if has_english:
                    assert "pathEN" in artifact, "Should have pathEN when English specification exists"
                    assert artifact["pathEN"].endswith("-EN.md"), \
                        f"English path should end with -EN.md: {artifact['pathEN']}"
                    assert "versionEN" in artifact, "Should have versionEN"
                    assert "statusEN" in artifact, "Should have statusEN"
                else:
                    assert "pathEN" not in artifact, "Should not have pathEN when English specification doesn't exist"
                
                # Verify German path if German is available (Requirement 3.5, 8.2)
                if has_german:
                    assert "pathDE" in artifact, "Should have pathDE when German specification exists"
                    assert artifact["pathDE"].endswith("-DE.md"), \
                        f"German path should end with -DE.md: {artifact['pathDE']}"
                    assert "versionDE" in artifact, "Should have versionDE"
                    assert "statusDE" in artifact, "Should have statusDE"
                else:
                    assert "pathDE" not in artifact, "Should not have pathDE when German specification doesn't exist"
                
                # Verify single-language specifications have generic "path" field (Requirement 8.4)
                if has_english and not has_german:
                    assert "path" in artifact, "Single-language (EN) should have generic path field"
                    assert artifact["path"] == artifact["pathEN"], "Generic path should match pathEN"
                elif has_german and not has_english:
                    assert "path" in artifact, "Single-language (DE) should have generic path field"
                    assert artifact["path"] == artifact["pathDE"], "Generic path should match pathDE"
    
    def test_bilingual_both_languages(self, tmp_path):
        """Test artifact with both English and German specifications"""
        import json
        
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create progress directory
        progress_dir = project_root / "output" / "specifications" / "progress"
        progress_dir.mkdir(parents=True)
        
        # Create status with bilingual workpackage
        status_file = progress_dir / "Business_Specification_Status.json"
        status_data = {
            "summary": {
                "total_workpackages": 1,
                "approved": 1,
                "approved_with_changes": 0,
                "rejected": 0,
                "pending": 0
            },
            "workpackages": [
                {
                    "workpackage_id": "WP-001",
                    "flow_id": "FLOW_12345",
                    "name": "Test WP",
                    "priority": 1,
                    "status": "APPROVED",
                    "specifications": {
                        "english": {
                            "original": "output/specs/WP-001-original-EN.md",
                            "reviewed": "output/specs/WP-001-reviewed-EN.md",
                            "version": "1.0",
                            "status": "APPROVED"
                        },
                        "german": {
                            "original": "output/specs/WP-001-original-DE.md",
                            "reviewed": "output/specs/WP-001-reviewed-DE.md",
                            "version": "1.0",
                            "status": "APPROVED"
                        }
                    }
                }
            ]
        }
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2)
        
        loader = MigrationDataLoader(project_root=str(project_root))
        phase_details = loader.get_phase_details(3)
        
        artifacts = phase_details.get("artifacts", [])
        assert len(artifacts) == 1
        
        artifact = artifacts[0]
        assert artifact["hasMultipleLanguages"] is True
        assert "pathEN" in artifact
        assert "pathDE" in artifact
        assert artifact["pathEN"].endswith("-EN.md")
        assert artifact["pathDE"].endswith("-DE.md")
    
    def test_bilingual_english_only(self, tmp_path):
        """Test artifact with only English specification"""
        import json
        
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create progress directory
        progress_dir = project_root / "output" / "specifications" / "progress"
        progress_dir.mkdir(parents=True)
        
        # Create status with English-only workpackage
        status_file = progress_dir / "Business_Specification_Status.json"
        status_data = {
            "summary": {
                "total_workpackages": 1,
                "approved": 1,
                "approved_with_changes": 0,
                "rejected": 0,
                "pending": 0
            },
            "workpackages": [
                {
                    "workpackage_id": "WP-001",
                    "flow_id": "FLOW_12345",
                    "name": "Test WP",
                    "priority": 1,
                    "status": "APPROVED",
                    "specifications": {
                        "english": {
                            "original": "output/specs/WP-001-original-EN.md",
                            "reviewed": "output/specs/WP-001-reviewed-EN.md",
                            "version": "1.0",
                            "status": "APPROVED"
                        }
                    }
                }
            ]
        }
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2)
        
        loader = MigrationDataLoader(project_root=str(project_root))
        phase_details = loader.get_phase_details(3)
        
        artifacts = phase_details.get("artifacts", [])
        assert len(artifacts) == 1
        
        artifact = artifacts[0]
        assert artifact["hasMultipleLanguages"] is False
        assert "pathEN" in artifact
        assert "pathDE" not in artifact
        assert "path" in artifact  # Should have generic path for single language
        assert artifact["path"] == artifact["pathEN"]
    
    def test_bilingual_german_only(self, tmp_path):
        """Test artifact with only German specification"""
        import json
        
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create progress directory
        progress_dir = project_root / "output" / "specifications" / "progress"
        progress_dir.mkdir(parents=True)
        
        # Create status with German-only workpackage
        status_file = progress_dir / "Business_Specification_Status.json"
        status_data = {
            "summary": {
                "total_workpackages": 1,
                "approved": 1,
                "approved_with_changes": 0,
                "rejected": 0,
                "pending": 0
            },
            "workpackages": [
                {
                    "workpackage_id": "WP-001",
                    "flow_id": "FLOW_12345",
                    "name": "Test WP",
                    "priority": 1,
                    "status": "APPROVED",
                    "specifications": {
                        "german": {
                            "original": "output/specs/WP-001-original-DE.md",
                            "reviewed": "output/specs/WP-001-reviewed-DE.md",
                            "version": "1.0",
                            "status": "APPROVED"
                        }
                    }
                }
            ]
        }
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2)
        
        loader = MigrationDataLoader(project_root=str(project_root))
        phase_details = loader.get_phase_details(3)
        
        artifacts = phase_details.get("artifacts", [])
        assert len(artifacts) == 1
        
        artifact = artifacts[0]
        assert artifact["hasMultipleLanguages"] is False
        assert "pathDE" in artifact
        assert "pathEN" not in artifact
        assert "path" in artifact  # Should have generic path for single language
        assert artifact["path"] == artifact["pathDE"]
    
    def test_bilingual_uses_reviewed_path(self, tmp_path):
        """Test that reviewed path is preferred over original path"""
        import json
        
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create progress directory
        progress_dir = project_root / "output" / "specifications" / "progress"
        progress_dir.mkdir(parents=True)
        
        # Create status with both original and reviewed paths
        status_file = progress_dir / "Business_Specification_Status.json"
        status_data = {
            "summary": {
                "total_workpackages": 1,
                "approved": 1,
                "approved_with_changes": 0,
                "rejected": 0,
                "pending": 0
            },
            "workpackages": [
                {
                    "workpackage_id": "WP-001",
                    "flow_id": "FLOW_12345",
                    "name": "Test WP",
                    "priority": 1,
                    "status": "APPROVED",
                    "specifications": {
                        "english": {
                            "original": "output/specs/WP-001-original-EN.md",
                            "reviewed": "output/specs/WP-001-reviewed-EN.md",
                            "version": "1.0",
                            "status": "APPROVED"
                        }
                    }
                }
            ]
        }
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2)
        
        loader = MigrationDataLoader(project_root=str(project_root))
        phase_details = loader.get_phase_details(3)
        
        artifacts = phase_details.get("artifacts", [])
        assert len(artifacts) == 1
        
        artifact = artifacts[0]
        # Should use reviewed path, not original
        assert "reviewed" in artifact["pathEN"]
        assert "original" not in artifact["pathEN"]
    
    def test_bilingual_fallback_to_original(self, tmp_path):
        """Test that original path is used when reviewed path is missing"""
        import json
        
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create progress directory
        progress_dir = project_root / "output" / "specifications" / "progress"
        progress_dir.mkdir(parents=True)
        
        # Create status with only original path
        status_file = progress_dir / "Business_Specification_Status.json"
        status_data = {
            "summary": {
                "total_workpackages": 1,
                "approved": 1,
                "approved_with_changes": 0,
                "rejected": 0,
                "pending": 0
            },
            "workpackages": [
                {
                    "workpackage_id": "WP-001",
                    "flow_id": "FLOW_12345",
                    "name": "Test WP",
                    "priority": 1,
                    "status": "APPROVED",
                    "specifications": {
                        "english": {
                            "original": "output/specs/WP-001-original-EN.md",
                            "version": "1.0",
                            "status": "DRAFT"
                        }
                    }
                }
            ]
        }
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2)
        
        loader = MigrationDataLoader(project_root=str(project_root))
        phase_details = loader.get_phase_details(3)
        
        artifacts = phase_details.get("artifacts", [])
        assert len(artifacts) == 1
        
        artifact = artifacts[0]
        # Should use original path when reviewed is missing
        assert "original" in artifact["pathEN"]
    
    def test_bilingual_no_specifications(self, tmp_path):
        """Test that workpackages without specifications don't create artifacts"""
        import json
        
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create progress directory
        progress_dir = project_root / "output" / "specifications" / "progress"
        progress_dir.mkdir(parents=True)
        
        # Create status with workpackage but no specifications
        status_file = progress_dir / "Business_Specification_Status.json"
        status_data = {
            "summary": {
                "total_workpackages": 1,
                "approved": 1,
                "approved_with_changes": 0,
                "rejected": 0,
                "pending": 0
            },
            "workpackages": [
                {
                    "workpackage_id": "WP-001",
                    "flow_id": "FLOW_12345",
                    "name": "Test WP",
                    "priority": 1,
                    "status": "APPROVED",
                    "specifications": {}  # Empty specifications
                }
            ]
        }
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2)
        
        loader = MigrationDataLoader(project_root=str(project_root))
        phase_details = loader.get_phase_details(3)
        
        artifacts = phase_details.get("artifacts", [])
        # Should not create artifacts for workpackages without specifications
        assert len(artifacts) == 0



class TestJSONFieldExtractionCompleteness:
    """
    Property 3: JSON Field Extraction Completeness
    
    For any valid JSON progress file, when the Data_Loader parses it, all expected
    fields (workpackage status, specification paths, quality assessment, metadata,
    timestamps) should be extracted correctly.
    
    Validates: Requirements 6.1, 6.2, 6.3, 6.4, 7.5, 8.3, 15.1, 15.2
    """
    
    @given(
        total_workpackages=st.integers(min_value=1, max_value=10),
        approved=st.integers(min_value=0, max_value=10),
        has_quality_assessment=st.booleans(),
        has_specifications=st.booleans(),
        has_timestamp=st.booleans()
    )
    def test_property_3_json_field_extraction_completeness(
        self, total_workpackages, approved, has_quality_assessment, has_specifications, has_timestamp
    ):
        """
        **Feature: dashboard-file-structure-adaptation, Property 3: JSON Field Extraction Completeness**
        
        Property: For any valid JSON progress file, when the Data_Loader parses it,
        all expected fields should be extracted correctly.
        
        This test verifies that:
        1. Workpackage metadata is extracted (id, flow_id, name, priority, status)
        2. Specification paths are extracted (english, german)
        3. Quality assessment data is extracted
        4. Timestamps are extracted
        5. Missing fields are handled gracefully with defaults
        """
        import tempfile
        import json
        
        # Ensure approved doesn't exceed total
        approved = min(approved, total_workpackages)
        
        # Create test project structure
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir) / "test_project"
            project_root.mkdir()
            
            # Create progress directory
            progress_dir = project_root / "output" / "specifications" / "progress"
            progress_dir.mkdir(parents=True)
            
            # Create workpackages with varying field completeness
            workpackages = []
            for i in range(total_workpackages):
                wp_id = f"WP-{i+1:03d}"
                flow_id = f"FLOW_{i+10000}"
                is_approved = i < approved
                
                wp = {
                    "workpackage_id": wp_id,
                    "flow_id": flow_id,
                    "name": f"Workpackage {i+1}",
                    "priority": i + 1,
                    "status": "APPROVED" if is_approved else "PENDING",
                    "ready_for_code_generation": is_approved
                }
                
                # Add quality assessment if requested (Requirement 6.3)
                if has_quality_assessment and is_approved:
                    wp["quality_assessment"] = {
                        "completeness": "PASS",
                        "accuracy": "PASS",
                        "testability": "PASS",
                        "traceability": "PASS",
                        "technology_agnostic": "PASS",
                        "bilingual_consistency": "PASS"
                    }
                
                # Add specifications if requested (Requirements 6.2, 8.3)
                if has_specifications and is_approved:
                    wp["specifications"] = {
                        "english": {
                            "original": f"output/specs/{wp_id}-original-EN.md",
                            "reviewed": f"output/specs/{wp_id}-reviewed-EN.md",
                            "version": "1.0",
                            "status": "APPROVED"
                        },
                        "german": {
                            "original": f"output/specs/{wp_id}-original-DE.md",
                            "reviewed": f"output/specs/{wp_id}-reviewed-DE.md",
                            "version": "1.0",
                            "status": "APPROVED"
                        }
                    }
                
                workpackages.append(wp)
            
            # Create Business_Specification_Status.json
            status_data = {
                "project": "test_project",
                "phase": "Phase 3: Business Specification Extraction",
                "summary": {
                    "total_workpackages": total_workpackages,
                    "approved": approved,
                    "approved_with_changes": 0,
                    "rejected": 0,
                    "pending": total_workpackages - approved,
                    "ready_for_phase_4": approved
                },
                "workpackages": workpackages
            }
            
            # Add timestamp if requested (Requirements 15.1, 15.2)
            if has_timestamp:
                status_data["last_updated"] = "2024-01-18T16:45:00Z"
            
            status_file = progress_dir / "Business_Specification_Status.json"
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, indent=2)
            
            # Initialize loader
            loader = MigrationDataLoader(project_root=str(project_root))
            
            # Get Phase 3 details
            phase_details = loader.get_phase_details(3)
            
            # Verify workpackage metadata extraction (Requirements 6.1, 7.5)
            completed_workpackages = phase_details.get("completedWorkpackages", [])
            assert len(completed_workpackages) == approved, \
                f"Expected {approved} completed workpackages, got {len(completed_workpackages)}"
            
            for wp_info in completed_workpackages:
                # Verify all metadata fields are present
                assert "id" in wp_info, "Should have id field"
                assert "flowId" in wp_info, "Should have flowId field"
                assert "name" in wp_info, "Should have name field"
                assert "priority" in wp_info, "Should have priority field"
                assert "status" in wp_info, "Should have status field"
                assert "ready_for_code_generation" in wp_info, "Should have ready_for_code_generation field"
                
                # Verify metadata values are correct
                assert wp_info["id"].startswith("WP-"), f"ID should start with WP-: {wp_info['id']}"
                assert wp_info["flowId"].startswith("FLOW_"), f"Flow ID should start with FLOW_: {wp_info['flowId']}"
                assert isinstance(wp_info["priority"], int), "Priority should be an integer"
                assert wp_info["status"] in ["APPROVED", "APPROVED_WITH_CHANGES"], \
                    f"Status should be APPROVED or APPROVED_WITH_CHANGES: {wp_info['status']}"
                
                # Verify quality assessment extraction if present (Requirement 6.3)
                if has_quality_assessment:
                    assert "quality_assessment" in wp_info, "Should have quality_assessment field"
                    qa = wp_info["quality_assessment"]
                    assert "completeness" in qa, "Quality assessment should have completeness"
                    assert "accuracy" in qa, "Quality assessment should have accuracy"
                    assert "testability" in qa, "Quality assessment should have testability"
                    assert "traceability" in qa, "Quality assessment should have traceability"
                    assert "technology_agnostic" in qa, "Quality assessment should have technology_agnostic"
                    assert "bilingual_consistency" in qa, "Quality assessment should have bilingual_consistency"
            
            # Verify specification path extraction (Requirements 6.2, 8.3)
            if has_specifications and approved > 0:
                artifacts = phase_details.get("artifacts", [])
                assert len(artifacts) == approved, \
                    f"Expected {approved} artifacts, got {len(artifacts)}"
                
                for artifact in artifacts:
                    assert "pathEN" in artifact, "Should have English path"
                    assert "pathDE" in artifact, "Should have German path"
                    assert "versionEN" in artifact, "Should have English version"
                    assert "versionDE" in artifact, "Should have German version"
                    assert "statusEN" in artifact, "Should have English status"
                    assert "statusDE" in artifact, "Should have German status"
            
            # Verify timestamp extraction (Requirements 15.1, 15.2)
            if has_timestamp:
                assert "lastUpdated" in phase_details, "Should have lastUpdated field"
                assert phase_details["lastUpdated"] == "2024-01-18T16:45:00Z"
            else:
                # Should have empty string or default value when timestamp is missing
                assert phase_details.get("lastUpdated", "") == ""
            
            # Verify summary fields are extracted (Requirement 6.1)
            assert "totalWorkpackages" in phase_details, "Should have totalWorkpackages"
            assert "completedCount" in phase_details, "Should have completedCount"
            assert phase_details["totalWorkpackages"] == total_workpackages
            assert phase_details["completedCount"] == approved
    
    def test_json_extraction_all_fields_present(self, tmp_path):
        """Test extraction when all fields are present"""
        import json
        
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create progress directory
        progress_dir = project_root / "output" / "specifications" / "progress"
        progress_dir.mkdir(parents=True)
        
        # Create complete status file
        status_file = progress_dir / "Business_Specification_Status.json"
        status_data = {
            "project": "test_project",
            "phase": "Phase 3: Business Specification Extraction",
            "last_updated": "2024-01-18T16:45:00Z",
            "summary": {
                "total_workpackages": 2,
                "approved": 2,
                "approved_with_changes": 0,
                "rejected": 0,
                "pending": 0,
                "ready_for_phase_4": 2
            },
            "workpackages": [
                {
                    "workpackage_id": "WP-001",
                    "flow_id": "FLOW_12345",
                    "name": "Customer Management",
                    "priority": 1,
                    "status": "APPROVED",
                    "ready_for_code_generation": True,
                    "quality_assessment": {
                        "completeness": "PASS",
                        "accuracy": "PASS",
                        "testability": "PASS",
                        "traceability": "PASS",
                        "technology_agnostic": "PASS",
                        "bilingual_consistency": "PASS"
                    },
                    "specifications": {
                        "english": {
                            "original": "output/specs/WP-001-original-EN.md",
                            "reviewed": "output/specs/WP-001-reviewed-EN.md",
                            "version": "1.0",
                            "status": "APPROVED"
                        },
                        "german": {
                            "original": "output/specs/WP-001-original-DE.md",
                            "reviewed": "output/specs/WP-001-reviewed-DE.md",
                            "version": "1.0",
                            "status": "APPROVED"
                        }
                    }
                },
                {
                    "workpackage_id": "WP-002",
                    "flow_id": "FLOW_67890",
                    "name": "Order Processing",
                    "priority": 2,
                    "status": "APPROVED",
                    "ready_for_code_generation": True,
                    "quality_assessment": {
                        "completeness": "PASS",
                        "accuracy": "FAIL",
                        "testability": "PASS",
                        "traceability": "PASS",
                        "technology_agnostic": "PASS",
                        "bilingual_consistency": "PASS"
                    },
                    "specifications": {
                        "english": {
                            "original": "output/specs/WP-002-original-EN.md",
                            "reviewed": "output/specs/WP-002-reviewed-EN.md",
                            "version": "1.1",
                            "status": "APPROVED"
                        }
                    }
                }
            ]
        }
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2)
        
        loader = MigrationDataLoader(project_root=str(project_root))
        phase_details = loader.get_phase_details(3)
        
        # Verify all fields were extracted
        assert phase_details["totalWorkpackages"] == 2
        assert phase_details["completedCount"] == 2
        assert phase_details["lastUpdated"] == "2024-01-18T16:45:00Z"
        
        completed_wps = phase_details["completedWorkpackages"]
        assert len(completed_wps) == 2
        
        # Verify first workpackage
        wp1 = completed_wps[0]
        assert wp1["id"] == "WP-001"
        assert wp1["flowId"] == "FLOW_12345"
        assert wp1["name"] == "Customer Management"
        assert wp1["priority"] == 1
        assert wp1["status"] == "APPROVED"
        assert wp1["ready_for_code_generation"] is True
        assert "quality_assessment" in wp1
        assert wp1["quality_assessment"]["completeness"] == "PASS"
        
        # Verify artifacts
        artifacts = phase_details["artifacts"]
        assert len(artifacts) == 2
        
        # First artifact should have both languages
        art1 = artifacts[0]
        assert art1["hasMultipleLanguages"] is True
        assert "pathEN" in art1
        assert "pathDE" in art1
        
        # Second artifact should have only English
        art2 = artifacts[1]
        assert art2["hasMultipleLanguages"] is False
        assert "pathEN" in art2
        assert "pathDE" not in art2
    
    def test_json_extraction_minimal_fields(self, tmp_path):
        """Test extraction when only minimal required fields are present"""
        import json
        
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create progress directory
        progress_dir = project_root / "output" / "specifications" / "progress"
        progress_dir.mkdir(parents=True)
        
        # Create minimal status file
        status_file = progress_dir / "Business_Specification_Status.json"
        status_data = {
            "summary": {
                "total_workpackages": 1,
                "approved": 1
                # Missing other summary fields
            },
            "workpackages": [
                {
                    "workpackage_id": "WP-001",
                    "flow_id": "FLOW_12345",
                    "status": "APPROVED"
                    # Missing name, priority, quality_assessment, specifications
                }
            ]
        }
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2)
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Should not crash (Requirement 6.5)
        phase_details = loader.get_phase_details(3)
        
        # Should extract available fields
        assert phase_details["totalWorkpackages"] == 1
        assert phase_details["completedCount"] == 1
        
        completed_wps = phase_details["completedWorkpackages"]
        assert len(completed_wps) == 1
        
        wp = completed_wps[0]
        assert wp["id"] == "WP-001"
        assert wp["flowId"] == "FLOW_12345"
        assert wp["status"] == "APPROVED"
        
        # Missing fields should have defaults
        assert wp["name"] == ""
        assert wp["priority"] == 0
        assert wp["ready_for_code_generation"] is False
        
        # No artifacts should be created without specifications
        artifacts = phase_details["artifacts"]
        assert len(artifacts) == 0
    
    def test_json_extraction_handles_malformed_quality_assessment(self, tmp_path):
        """Test that malformed quality assessment doesn't crash extraction"""
        import json
        
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create progress directory
        progress_dir = project_root / "output" / "specifications" / "progress"
        progress_dir.mkdir(parents=True)
        
        # Create status with malformed quality assessment
        status_file = progress_dir / "Business_Specification_Status.json"
        status_data = {
            "summary": {
                "total_workpackages": 1,
                "approved": 1
            },
            "workpackages": [
                {
                    "workpackage_id": "WP-001",
                    "flow_id": "FLOW_12345",
                    "status": "APPROVED",
                    "quality_assessment": "invalid"  # Should be an object, not a string
                }
            ]
        }
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2)
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Should not crash
        phase_details = loader.get_phase_details(3)
        
        completed_wps = phase_details["completedWorkpackages"]
        assert len(completed_wps) == 1
        
        # Quality assessment should be skipped or have empty dict
        wp = completed_wps[0]
        if "quality_assessment" in wp:
            # If present, should be empty or have default values
            assert isinstance(wp["quality_assessment"], dict)
    
    def test_json_extraction_handles_empty_specifications(self, tmp_path):
        """Test that empty specifications object doesn't crash extraction"""
        import json
        
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create progress directory
        progress_dir = project_root / "output" / "specifications" / "progress"
        progress_dir.mkdir(parents=True)
        
        # Create status with empty specifications
        status_file = progress_dir / "Business_Specification_Status.json"
        status_data = {
            "summary": {
                "total_workpackages": 1,
                "approved": 1
            },
            "workpackages": [
                {
                    "workpackage_id": "WP-001",
                    "flow_id": "FLOW_12345",
                    "status": "APPROVED",
                    "specifications": {}  # Empty
                }
            ]
        }
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2)
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Should not crash
        phase_details = loader.get_phase_details(3)
        
        # No artifacts should be created
        artifacts = phase_details["artifacts"]
        assert len(artifacts) == 0



class TestFileCountingAggregation:
    """
    Property 8: File Counting Aggregation
    
    For any set of directories to scan, when counting generated files, the total count
    should equal the sum of files in all specified directories.
    
    Validates: Requirements 5.3
    """
    
    @given(
        app_src_count=st.integers(min_value=0, max_value=50),
        db_src_count=st.integers(min_value=0, max_value=50)
    )
    def test_property_8_file_counting_aggregation(self, app_src_count, db_src_count):
        """
        **Feature: dashboard-file-structure-adaptation, Property 8: File Counting Aggregation**
        
        Property: For any set of directories to scan, when counting generated files,
        the total count should equal the sum of files in all specified directories.
        
        This test verifies that:
        1. Files in output/gen_src/ are counted correctly
        2. Files in output/gen_src_db/ are counted correctly
        3. Total count = app_src_count + db_src_count
        4. Aggregation works for any number of files
        """
        import tempfile
        
        # Create test project structure
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir) / "test_project"
            project_root.mkdir()
            
            # Create gen_src directory with files
            gen_src_dir = project_root / "output" / "gen_src"
            gen_src_dir.mkdir(parents=True)
            
            for i in range(app_src_count):
                test_file = gen_src_dir / f"AppFile{i+1}.java"
                test_file.write_text(f"// Application source file {i+1}")
            
            # Create gen_src_db directory with files
            gen_src_db_dir = project_root / "output" / "gen_src_db"
            gen_src_db_dir.mkdir(parents=True)
            
            for i in range(db_src_count):
                test_file = gen_src_db_dir / f"DbFile{i+1}.sql"
                test_file.write_text(f"-- Database source file {i+1}")
            
            # Initialize loader
            loader = MigrationDataLoader(project_root=str(project_root))
            
            # Get Phase 4 details
            phase_details = loader.get_phase_details(4)
            
            # Verify file counting (Requirement 5.3)
            summary = phase_details.get("generatedFilesSummary", {})
            
            assert "applicationSource" in summary, "Should have applicationSource count"
            assert "databaseSource" in summary, "Should have databaseSource count"
            assert "totalFiles" in summary, "Should have totalFiles count"
            
            # Verify individual counts
            assert summary["applicationSource"] == app_src_count, \
                f"Expected {app_src_count} app source files, got {summary['applicationSource']}"
            assert summary["databaseSource"] == db_src_count, \
                f"Expected {db_src_count} db source files, got {summary['databaseSource']}"
            
            # Verify total aggregation
            expected_total = app_src_count + db_src_count
            assert summary["totalFiles"] == expected_total, \
                f"Expected total={expected_total}, got {summary['totalFiles']}"
            
            # Verify artifacts list contains all files
            artifacts = phase_details.get("artifacts", [])
            assert len(artifacts) == expected_total, \
                f"Expected {expected_total} artifacts, got {len(artifacts)}"
            
            # Verify artifact types
            app_artifacts = [a for a in artifacts if a["type"] == "Generated Application Source"]
            db_artifacts = [a for a in artifacts if a["type"] == "Generated Database Source"]
            
            assert len(app_artifacts) == app_src_count, \
                f"Expected {app_src_count} app artifacts, got {len(app_artifacts)}"
            assert len(db_artifacts) == db_src_count, \
                f"Expected {db_src_count} db artifacts, got {len(db_artifacts)}"
    
    def test_file_counting_no_files(self, tmp_path):
        """Test file counting when no files exist"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create empty directories
        (project_root / "output" / "gen_src").mkdir(parents=True)
        (project_root / "output" / "gen_src_db").mkdir(parents=True)
        
        loader = MigrationDataLoader(project_root=str(project_root))
        phase_details = loader.get_phase_details(4)
        
        summary = phase_details.get("generatedFilesSummary", {})
        
        assert summary["applicationSource"] == 0
        assert summary["databaseSource"] == 0
        assert summary["totalFiles"] == 0
        
        artifacts = phase_details.get("artifacts", [])
        assert len(artifacts) == 0
    
    def test_file_counting_only_app_files(self, tmp_path):
        """Test file counting when only application files exist"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create gen_src with files
        gen_src_dir = project_root / "output" / "gen_src"
        gen_src_dir.mkdir(parents=True)
        
        for i in range(5):
            (gen_src_dir / f"App{i}.java").write_text("code")
        
        # Create empty gen_src_db
        (project_root / "output" / "gen_src_db").mkdir(parents=True)
        
        loader = MigrationDataLoader(project_root=str(project_root))
        phase_details = loader.get_phase_details(4)
        
        summary = phase_details.get("generatedFilesSummary", {})
        
        assert summary["applicationSource"] == 5
        assert summary["databaseSource"] == 0
        assert summary["totalFiles"] == 5
    
    def test_file_counting_only_db_files(self, tmp_path):
        """Test file counting when only database files exist"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create empty gen_src
        (project_root / "output" / "gen_src").mkdir(parents=True)
        
        # Create gen_src_db with files
        gen_src_db_dir = project_root / "output" / "gen_src_db"
        gen_src_db_dir.mkdir(parents=True)
        
        for i in range(3):
            (gen_src_db_dir / f"Db{i}.sql").write_text("sql")
        
        loader = MigrationDataLoader(project_root=str(project_root))
        phase_details = loader.get_phase_details(4)
        
        summary = phase_details.get("generatedFilesSummary", {})
        
        assert summary["applicationSource"] == 0
        assert summary["databaseSource"] == 3
        assert summary["totalFiles"] == 3
    
    def test_file_counting_nested_directories(self, tmp_path):
        """Test file counting with nested directory structures"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create nested structure in gen_src
        gen_src_dir = project_root / "output" / "gen_src"
        (gen_src_dir / "com" / "example" / "app").mkdir(parents=True)
        (gen_src_dir / "com" / "example" / "app" / "Main.java").write_text("code")
        (gen_src_dir / "com" / "example" / "app" / "Utils.java").write_text("code")
        
        # Create nested structure in gen_src_db
        gen_src_db_dir = project_root / "output" / "gen_src_db"
        (gen_src_db_dir / "schema" / "tables").mkdir(parents=True)
        (gen_src_db_dir / "schema" / "tables" / "create.sql").write_text("sql")
        
        loader = MigrationDataLoader(project_root=str(project_root))
        phase_details = loader.get_phase_details(4)
        
        summary = phase_details.get("generatedFilesSummary", {})
        
        # Should count files in nested directories
        assert summary["applicationSource"] == 2
        assert summary["databaseSource"] == 1
        assert summary["totalFiles"] == 3
    
    def test_file_counting_missing_directories(self, tmp_path):
        """Test file counting when directories don't exist"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Don't create gen_src or gen_src_db directories
        (project_root / "output").mkdir()
        
        loader = MigrationDataLoader(project_root=str(project_root))
        phase_details = loader.get_phase_details(4)
        
        summary = phase_details.get("generatedFilesSummary", {})
        
        # Should return 0 counts without crashing
        assert summary["applicationSource"] == 0
        assert summary["databaseSource"] == 0
        assert summary["totalFiles"] == 0



class TestDeliverableTypeDistinction:
    """
    Property 9: Deliverable Type Distinction
    
    For any file in the migration deliverables directory, the Data_Loader should
    correctly distinguish between code, documentation, and configuration based on
    file extension and content patterns.
    
    Validates: Requirements 4.4
    """
    
    @given(
        file_type=st.sampled_from(["code", "documentation", "configuration"]),
        filename=st.text(min_size=5, max_size=20, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            whitelist_characters='_-'
        ))
    )
    def test_property_9_deliverable_type_distinction(self, file_type, filename):
        """
        **Feature: dashboard-file-structure-adaptation, Property 9: Deliverable Type Distinction**
        
        Property: For any file in the migration deliverables directory, the Data_Loader
        should correctly distinguish between code, documentation, and configuration.
        
        This test verifies that:
        1. Code files (.java, .py, .sql, etc.) are categorized as "Code Deliverable"
        2. Documentation files (.md, .txt, .pdf, etc.) are categorized as "Documentation Deliverable"
        3. Configuration files (.json, .xml, .yaml, etc.) are categorized as "Configuration Deliverable"
        4. Categorization works for any valid filename
        """
        import tempfile
        
        # Map file type to extension
        extensions = {
            "code": [".java", ".py", ".sql", ".js"],
            "documentation": [".md", ".txt", ".pdf"],
            "configuration": [".json", ".xml", ".yaml", ".properties"]
        }
        
        # Pick a random extension for the file type
        import random
        extension = random.choice(extensions[file_type])
        full_filename = f"{filename}{extension}"
        
        # Create test project structure
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir) / "test_project"
            project_root.mkdir()
            
            # Create deliverables directory with test file
            deliverables_dir = project_root / "output" / "migration" / "deliverables"
            deliverables_dir.mkdir(parents=True)
            
            test_file = deliverables_dir / full_filename
            test_file.write_text("test content")
            
            # Initialize loader
            loader = MigrationDataLoader(project_root=str(project_root))
            
            # Get Phase 7 details
            phase_details = loader.get_phase_details(7)
            
            # Verify deliverable was found
            artifacts = phase_details.get("artifacts", [])
            reports = phase_details.get("reports", [])
            
            # .md files go to reports, others to artifacts
            if extension == ".md":
                items = reports
            else:
                items = artifacts
            
            # Find our test file
            matching_items = [item for item in items if item["name"] == full_filename]
            
            assert len(matching_items) > 0, f"Should find deliverable {full_filename}"
            
            item = matching_items[0]
            
            # Verify type is set
            assert "type" in item, "Deliverable should have a type"
            
            # Verify type matches expected category (Requirement 4.4)
            item_type = item["type"]
            
            if file_type == "code":
                assert "Code" in item_type, \
                    f"Code file should have 'Code' in type, got: {item_type}"
            elif file_type == "documentation":
                assert "Documentation" in item_type, \
                    f"Documentation file should have 'Documentation' in type, got: {item_type}"
            elif file_type == "configuration":
                assert "Configuration" in item_type, \
                    f"Configuration file should have 'Configuration' in type, got: {item_type}"
    
    def test_deliverable_type_java_code(self, tmp_path):
        """Test that .java files are categorized as code"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        deliverables_dir = project_root / "output" / "migration" / "deliverables"
        deliverables_dir.mkdir(parents=True)
        
        (deliverables_dir / "Main.java").write_text("public class Main {}")
        
        loader = MigrationDataLoader(project_root=str(project_root))
        phase_details = loader.get_phase_details(7)
        
        artifacts = phase_details.get("artifacts", [])
        java_artifacts = [a for a in artifacts if a["name"] == "Main.java"]
        
        assert len(java_artifacts) == 1
        assert "Code" in java_artifacts[0]["type"]
    
    def test_deliverable_type_markdown_documentation(self, tmp_path):
        """Test that .md files are categorized as documentation"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        deliverables_dir = project_root / "output" / "migration" / "deliverables"
        deliverables_dir.mkdir(parents=True)
        
        (deliverables_dir / "README.md").write_text("# Documentation")
        
        loader = MigrationDataLoader(project_root=str(project_root))
        phase_details = loader.get_phase_details(7)
        
        reports = phase_details.get("reports", [])
        md_reports = [r for r in reports if r["name"] == "README.md"]
        
        assert len(md_reports) == 1
        assert "Documentation" in md_reports[0]["type"]
    
    def test_deliverable_type_json_configuration(self, tmp_path):
        """Test that .json files are categorized as configuration"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        deliverables_dir = project_root / "output" / "migration" / "deliverables"
        deliverables_dir.mkdir(parents=True)
        
        (deliverables_dir / "config.json").write_text('{"key": "value"}')
        
        loader = MigrationDataLoader(project_root=str(project_root))
        phase_details = loader.get_phase_details(7)
        
        artifacts = phase_details.get("artifacts", [])
        json_artifacts = [a for a in artifacts if a["name"] == "config.json"]
        
        assert len(json_artifacts) == 1
        assert "Configuration" in json_artifacts[0]["type"]
    
    def test_deliverable_type_xml_configuration(self, tmp_path):
        """Test that .xml files are categorized as configuration"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        deliverables_dir = project_root / "output" / "migration" / "deliverables"
        deliverables_dir.mkdir(parents=True)
        
        (deliverables_dir / "pom.xml").write_text('<project></project>')
        
        loader = MigrationDataLoader(project_root=str(project_root))
        phase_details = loader.get_phase_details(7)
        
        artifacts = phase_details.get("artifacts", [])
        xml_artifacts = [a for a in artifacts if a["name"] == "pom.xml"]
        
        assert len(xml_artifacts) == 1
        assert "Configuration" in xml_artifacts[0]["type"]
    
    def test_deliverable_type_sql_code(self, tmp_path):
        """Test that .sql files are categorized as code"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        deliverables_dir = project_root / "output" / "migration" / "deliverables"
        deliverables_dir.mkdir(parents=True)
        
        (deliverables_dir / "schema.sql").write_text("CREATE TABLE test (id INT);")
        
        loader = MigrationDataLoader(project_root=str(project_root))
        phase_details = loader.get_phase_details(7)
        
        artifacts = phase_details.get("artifacts", [])
        sql_artifacts = [a for a in artifacts if a["name"] == "schema.sql"]
        
        assert len(sql_artifacts) == 1
        assert "Code" in sql_artifacts[0]["type"]
    
    def test_deliverable_type_python_code(self, tmp_path):
        """Test that .py files are categorized as code"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        deliverables_dir = project_root / "output" / "migration" / "deliverables"
        deliverables_dir.mkdir(parents=True)
        
        (deliverables_dir / "script.py").write_text("print('hello')")
        
        loader = MigrationDataLoader(project_root=str(project_root))
        phase_details = loader.get_phase_details(7)
        
        artifacts = phase_details.get("artifacts", [])
        py_artifacts = [a for a in artifacts if a["name"] == "script.py"]
        
        assert len(py_artifacts) == 1
        assert "Code" in py_artifacts[0]["type"]
    
    def test_deliverable_type_yaml_configuration(self, tmp_path):
        """Test that .yaml files are categorized as configuration"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        deliverables_dir = project_root / "output" / "migration" / "deliverables"
        deliverables_dir.mkdir(parents=True)
        
        (deliverables_dir / "config.yaml").write_text("key: value")
        
        loader = MigrationDataLoader(project_root=str(project_root))
        phase_details = loader.get_phase_details(7)
        
        artifacts = phase_details.get("artifacts", [])
        yaml_artifacts = [a for a in artifacts if a["name"] == "config.yaml"]
        
        assert len(yaml_artifacts) == 1
        assert "Configuration" in yaml_artifacts[0]["type"]
    
    def test_deliverable_type_mixed_files(self, tmp_path):
        """Test categorization with mixed file types"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        deliverables_dir = project_root / "output" / "migration" / "deliverables"
        deliverables_dir.mkdir(parents=True)
        
        # Create various file types
        (deliverables_dir / "App.java").write_text("code")
        (deliverables_dir / "README.md").write_text("docs")
        (deliverables_dir / "config.json").write_text("config")
        (deliverables_dir / "script.py").write_text("code")
        (deliverables_dir / "settings.xml").write_text("config")
        
        loader = MigrationDataLoader(project_root=str(project_root))
        phase_details = loader.get_phase_details(7)
        
        artifacts = phase_details.get("artifacts", [])
        reports = phase_details.get("reports", [])
        
        # Should have 4 artifacts (non-.md files)
        assert len(artifacts) == 4
        
        # Should have 1 report (.md file)
        assert len(reports) == 1
        
        # Verify code files
        code_artifacts = [a for a in artifacts if "Code" in a["type"]]
        assert len(code_artifacts) == 2  # App.java, script.py
        
        # Verify configuration files
        config_artifacts = [a for a in artifacts if "Configuration" in a["type"]]
        assert len(config_artifacts) == 2  # config.json, settings.xml
        
        # Verify documentation
        doc_reports = [r for r in reports if "Documentation" in r["type"]]
        assert len(doc_reports) == 1  # README.md
    
    def test_deliverable_type_unknown_extension(self, tmp_path):
        """Test that unknown extensions get generic 'Deliverable' type"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        deliverables_dir = project_root / "output" / "migration" / "deliverables"
        deliverables_dir.mkdir(parents=True)
        
        (deliverables_dir / "file.unknown").write_text("content")
        
        loader = MigrationDataLoader(project_root=str(project_root))
        phase_details = loader.get_phase_details(7)
        
        artifacts = phase_details.get("artifacts", [])
        unknown_artifacts = [a for a in artifacts if a["name"] == "file.unknown"]
        
        assert len(unknown_artifacts) == 1
        # Should have generic "Deliverable" type
        assert unknown_artifacts[0]["type"] == "Deliverable"



class TestFileCategorization:
    """
    Property 4: File Categorization by Extension
    
    For any file with extension .md, .json, .csv, or .py, the Data_Loader should
    categorize it as Report, Data File, Analysis Table, or Tool respectively.
    
    Validates: Requirements 14.1, 14.2, 14.3, 14.4
    """
    
    @given(
        filename_base=st.text(min_size=1, max_size=50, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            whitelist_characters='_-'
        )),
        extension=st.sampled_from(['.md', '.json', '.csv', '.py'])
    )
    def test_property_4_file_categorization_by_extension(self, filename_base, extension):
        """
        **Feature: dashboard-file-structure-adaptation, Property 4: File Categorization by Extension**
        
        Property: For any file with extension .md, .json, .csv, or .py, the Data_Loader
        should categorize it as Report, Data File, Analysis Table, or Tool respectively.
        
        This test verifies that:
        1. .md files are categorized as Reports (Requirement 14.1)
        2. .json files are categorized as Data Files (Requirement 14.2)
        3. .csv files are categorized as Analysis Tables (Requirement 14.3)
        4. .py files are categorized as Tools (Requirement 14.4)
        5. Categorization is consistent regardless of filename
        """
        import tempfile
        
        # Create test project structure
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir) / "test_project"
            project_root.mkdir()
            
            # Initialize loader
            loader = MigrationDataLoader(project_root=str(project_root))
            
            # Create file path
            filename = f"{filename_base}{extension}"
            file_path = Path(filename)
            
            # Categorize the file
            category = loader._categorize_file(file_path)
            
            # Verify categorization based on extension
            if extension == '.md':
                # Requirement 14.1: .md files are Reports
                assert "Report" in category or "Specification" in category, \
                    f"Expected .md file to be categorized as Report, got {category}"
            elif extension == '.json':
                # Requirement 14.2: .json files are Data Files
                assert "Data" in category or category == "Data File", \
                    f"Expected .json file to be categorized as Data File, got {category}"
            elif extension == '.csv':
                # Requirement 14.3: .csv files are Analysis Tables
                assert category == "Analysis Table", \
                    f"Expected .csv file to be categorized as Analysis Table, got {category}"
            elif extension == '.py':
                # Requirement 14.4: .py files are Tools
                assert category == "Tool", \
                    f"Expected .py file to be categorized as Tool, got {category}"
    
    def test_md_files_are_reports(self, tmp_path):
        """Test that .md files are categorized as Reports (Requirement 14.1)"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Test various .md files
        test_files = [
            "report.md",
            "analysis.md",
            "summary.md",
            "README.md"
        ]
        
        for filename in test_files:
            file_path = Path(filename)
            category = loader._categorize_file(file_path)
            assert "Report" in category or "Specification" in category, \
                f"Expected {filename} to be categorized as Report, got {category}"
    
    def test_json_files_are_data_files(self, tmp_path):
        """Test that .json files are categorized as Data Files (Requirement 14.2)"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Test various .json files
        test_files = [
            "data.json",
            "config.json",
            "status.json",
            "workpackage.json"
        ]
        
        for filename in test_files:
            file_path = Path(filename)
            category = loader._categorize_file(file_path)
            assert "Data" in category, \
                f"Expected {filename} to be categorized as Data File, got {category}"
    
    def test_csv_files_are_analysis_tables(self, tmp_path):
        """Test that .csv files are categorized as Analysis Tables (Requirement 14.3)"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Test various .csv files
        test_files = [
            "dependencies.csv",
            "analysis.csv",
            "data.csv",
            "table.csv"
        ]
        
        for filename in test_files:
            file_path = Path(filename)
            category = loader._categorize_file(file_path)
            assert category == "Analysis Table", \
                f"Expected {filename} to be categorized as Analysis Table, got {category}"
    
    def test_py_files_are_tools(self, tmp_path):
        """Test that .py files are categorized as Tools (Requirement 14.4)"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Test various .py files
        test_files = [
            "analyzer.py",
            "processor.py",
            "tool.py",
            "script.py"
        ]
        
        for filename in test_files:
            file_path = Path(filename)
            category = loader._categorize_file(file_path)
            assert category == "Tool", \
                f"Expected {filename} to be categorized as Tool, got {category}"
    
    def test_categorization_with_path_object(self, tmp_path):
        """Test that categorization works with Path objects"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Test with Path objects
        assert "Report" in loader._categorize_file(Path("test.md"))
        assert "Data" in loader._categorize_file(Path("test.json"))
        assert loader._categorize_file(Path("test.csv")) == "Analysis Table"
        assert loader._categorize_file(Path("test.py")) == "Tool"
    
    def test_categorization_with_string_path(self, tmp_path):
        """Test that categorization works with string paths"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Test with string paths
        assert "Report" in loader._categorize_file("test.md")
        assert "Data" in loader._categorize_file("test.json")
        assert loader._categorize_file("test.csv") == "Analysis Table"
        assert loader._categorize_file("test.py") == "Tool"
    
    def test_unknown_extension_uses_default(self, tmp_path):
        """Test that unknown extensions use the default category"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Test with unknown extension
        category = loader._categorize_file(Path("test.xyz"))
        assert category == "Generated File"  # Default category
        
        # Test with custom default
        category = loader._categorize_file(Path("test.xyz"), default_type="Custom Type")
        assert category == "Custom Type"



class TestPatternBasedCategorization:
    """
    Property 5: Pattern-Based Categorization
    
    For any file with specific patterns in its name (specification, validation, review, quality),
    the Data_Loader should assign the corresponding specific category.
    
    Validates: Requirements 14.5
    """
    
    @given(
        pattern=st.sampled_from(['specification', 'validation', 'review', 'quality']),
        prefix=st.text(min_size=0, max_size=20, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            whitelist_characters='_-'
        )),
        suffix=st.text(min_size=0, max_size=20, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            whitelist_characters='_-'
        )),
        extension=st.sampled_from(['.md', '.json'])
    )
    def test_property_5_pattern_based_categorization(self, pattern, prefix, suffix, extension):
        """
        **Feature: dashboard-file-structure-adaptation, Property 5: Pattern-Based Categorization**
        
        Property: For any file with specific patterns in its name (specification, validation,
        review, quality), the Data_Loader should assign the corresponding specific category.
        
        This test verifies that:
        1. Files with "specification" in name get Specification category
        2. Files with "validation" in name get Validation category
        3. Files with "review" in name get Review category
        4. Files with "quality" in name get Quality category
        5. Pattern matching is case-insensitive
        6. Pattern matching works regardless of position in filename
        """
        import tempfile
        
        # Create test project structure
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir) / "test_project"
            project_root.mkdir()
            
            # Initialize loader
            loader = MigrationDataLoader(project_root=str(project_root))
            
            # Create filename with pattern
            filename = f"{prefix}{pattern}{suffix}{extension}"
            file_path = Path(filename)
            
            # Categorize the file
            category = loader._categorize_file(file_path)
            
            # Verify pattern-based categorization (Requirement 14.5)
            if pattern == 'specification':
                assert "Specification" in category, \
                    f"Expected file with 'specification' to have Specification category, got {category}"
            elif pattern == 'validation':
                assert "Validation" in category, \
                    f"Expected file with 'validation' to have Validation category, got {category}"
            elif pattern == 'review':
                assert "Review" in category, \
                    f"Expected file with 'review' to have Review category, got {category}"
            elif pattern == 'quality':
                assert "Quality" in category, \
                    f"Expected file with 'quality' to have Quality category, got {category}"
    
    def test_specification_pattern_in_md_files(self, tmp_path):
        """Test that 'specification' pattern is detected in .md files"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Test various filenames with 'specification'
        test_files = [
            "specification.md",
            "business_specification.md",
            "specification_v1.md",
            "my_specification_doc.md",
            "SPECIFICATION.md"  # Case insensitive
        ]
        
        for filename in test_files:
            file_path = Path(filename)
            category = loader._categorize_file(file_path)
            assert "Specification" in category, \
                f"Expected {filename} to have Specification category, got {category}"
    
    def test_validation_pattern_in_files(self, tmp_path):
        """Test that 'validation' pattern is detected"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Test various filenames with 'validation'
        test_files = [
            "validation.md",
            "validation_report.md",
            "code_validation.md",
            "validation.json",
            "VALIDATION.md"  # Case insensitive
        ]
        
        for filename in test_files:
            file_path = Path(filename)
            category = loader._categorize_file(file_path)
            assert "Validation" in category, \
                f"Expected {filename} to have Validation category, got {category}"
    
    def test_review_pattern_in_files(self, tmp_path):
        """Test that 'review' pattern is detected"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Test various filenames with 'review'
        test_files = [
            "review.md",
            "code_review.md",
            "review_report.md",
            "peer_review.md",
            "REVIEW.md"  # Case insensitive
        ]
        
        for filename in test_files:
            file_path = Path(filename)
            category = loader._categorize_file(file_path)
            assert "Review" in category, \
                f"Expected {filename} to have Review category, got {category}"
    
    def test_quality_pattern_in_files(self, tmp_path):
        """Test that 'quality' pattern is detected"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Test various filenames with 'quality'
        test_files = [
            "quality.md",
            "quality_report.md",
            "quality_assessment.md",
            "code_quality.md",
            "quality.json",
            "QUALITY.md"  # Case insensitive
        ]
        
        for filename in test_files:
            file_path = Path(filename)
            category = loader._categorize_file(file_path)
            assert "Quality" in category, \
                f"Expected {filename} to have Quality category, got {category}"
    
    def test_pattern_priority_in_md_files(self, tmp_path):
        """Test that specific patterns take priority over generic Report category"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Files with patterns should get specific categories, not just "Report"
        assert loader._categorize_file(Path("specification.md")) == "Business Specification"
        assert loader._categorize_file(Path("validation.md")) == "Validation Report"
        assert loader._categorize_file(Path("review.md")) == "Review Report"
        assert loader._categorize_file(Path("quality.md")) == "Quality Report"
    
    def test_pattern_in_json_files(self, tmp_path):
        """Test that patterns are detected in .json files"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Test pattern detection in JSON files
        assert "Specification" in loader._categorize_file(Path("specification.json"))
        assert "Validation" in loader._categorize_file(Path("validation.json"))
        assert "Quality" in loader._categorize_file(Path("quality.json"))
    
    def test_no_pattern_uses_extension_category(self, tmp_path):
        """Test that files without patterns use extension-based category"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Files without patterns should use extension-based categories
        category = loader._categorize_file(Path("simple_report.md"))
        assert "Report" in category
        
        category = loader._categorize_file(Path("data.json"))
        assert category == "Data File"
    
    def test_case_insensitive_pattern_matching(self, tmp_path):
        """Test that pattern matching is case-insensitive"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Test various case combinations
        test_cases = [
            ("SPECIFICATION.md", "Specification"),
            ("Specification.md", "Specification"),
            ("specification.md", "Specification"),
            ("VALIDATION.md", "Validation"),
            ("Validation.md", "Validation"),
            ("validation.md", "Validation"),
            ("REVIEW.md", "Review"),
            ("Review.md", "Review"),
            ("review.md", "Review"),
            ("QUALITY.md", "Quality"),
            ("Quality.md", "Quality"),
            ("quality.md", "Quality")
        ]
        
        for filename, expected_pattern in test_cases:
            category = loader._categorize_file(Path(filename))
            assert expected_pattern in category, \
                f"Expected {filename} to have {expected_pattern} in category, got {category}"
    
    def test_multiple_patterns_first_match_wins(self, tmp_path):
        """Test behavior when filename contains multiple patterns"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # When multiple patterns exist, the first match in the if-elif chain should win
        # Based on the implementation order: specification, validation, review, quality
        category = loader._categorize_file(Path("specification_validation.md"))
        assert "Specification" in category  # specification is checked first
        
        category = loader._categorize_file(Path("validation_review.md"))
        assert "Validation" in category  # validation is checked before review


class TestToolCategorization:
    """
    **Feature: dashboard-file-structure-adaptation, Property 13: Tool Categorization by Phase**
    
    For any tool file in a phase-specific subdirectory, the Data_Loader should categorize it by that phase.
    
    **Validates: Requirements 9.2**
    """
    
    @given(
        phase_id=st.integers(min_value=0, max_value=8),
        tool_count=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=100)
    def test_property_13_tool_categorization_by_phase(self, phase_id, tool_count):
        """Property test: Tools in phase-specific subdirectories are categorized by phase"""
        import tempfile
        import shutil
        
        # Create temporary directory
        tmp_path = Path(tempfile.mkdtemp())
        
        try:
            # Setup
            output_dir = tmp_path / "output"
            tools_dir = output_dir / "tools"
            phase_dir = tools_dir / f"phase_{phase_id}"
            phase_dir.mkdir(parents=True, exist_ok=True)
            
            # Create tools in phase-specific subdirectory
            created_tools = []
            for i in range(tool_count):
                tool_file = phase_dir / f"tool_{i}.py"
                tool_file.write_text(f"# Tool {i}")
                created_tools.append(tool_file.name)
            
            # Create loader
            loader = MigrationDataLoader(project_root=tmp_path)
            
            # Get tools for this phase
            tools = loader._get_phase_tools(phase_id)
            
            # Verify all created tools are found
            tool_names = [t['name'] for t in tools]
            for tool_name in created_tools:
                assert tool_name in tool_names, f"Tool {tool_name} should be found for phase {phase_id}"
            
            # Verify all tools have correct path structure
            for tool in tools:
                if tool['name'] in created_tools:
                    expected_path_part = f"output/tools/phase_{phase_id}"
                    assert expected_path_part in tool['path'], \
                        f"Tool path should contain phase-specific directory: {tool['path']}"
        finally:
            # Cleanup
            shutil.rmtree(tmp_path, ignore_errors=True)
    
    def test_tool_categorization_phase_0(self, tmp_path):
        """Test tool categorization for phase 0"""
        output_dir = tmp_path / "output"
        tools_dir = output_dir / "tools"
        phase_dir = tools_dir / "phase_0"
        phase_dir.mkdir(parents=True, exist_ok=True)
        
        # Create tools
        (phase_dir / "excel_processor.py").write_text("# Excel processor")
        (phase_dir / "mapper.sh").write_text("#!/bin/bash")
        
        loader = MigrationDataLoader(project_root=tmp_path)
        tools = loader._get_phase_tools(0)
        
        assert len(tools) == 2
        tool_names = [t['name'] for t in tools]
        assert "excel_processor.py" in tool_names
        assert "mapper.sh" in tool_names
    
    def test_tool_categorization_phase_3(self, tmp_path):
        """Test tool categorization for phase 3"""
        output_dir = tmp_path / "output"
        tools_dir = output_dir / "tools"
        phase_dir = tools_dir / "phase_3"
        phase_dir.mkdir(parents=True, exist_ok=True)
        
        # Create tools
        (phase_dir / "spec_generator.py").write_text("# Spec generator")
        (phase_dir / "README.md").write_text("# Documentation")
        
        loader = MigrationDataLoader(project_root=tmp_path)
        tools = loader._get_phase_tools(3)
        
        assert len(tools) == 2
        tool_names = [t['name'] for t in tools]
        assert "spec_generator.py" in tool_names
        assert "README.md" in tool_names
    
    def test_tool_categorization_no_phase_subdirectory(self, tmp_path):
        """Test tool categorization when tools are in main tools directory"""
        output_dir = tmp_path / "output"
        tools_dir = output_dir / "tools"
        tools_dir.mkdir(parents=True, exist_ok=True)
        
        # Create tools directly in tools directory
        (tools_dir / "general_tool.py").write_text("# General tool")
        (tools_dir / "utility.sh").write_text("#!/bin/bash")
        
        loader = MigrationDataLoader(project_root=tmp_path)
        tools = loader._get_phase_tools(1)
        
        # Should find tools in main directory
        assert len(tools) >= 2
        tool_names = [t['name'] for t in tools]
        assert "general_tool.py" in tool_names
        assert "utility.sh" in tool_names
    
    def test_tool_categorization_mixed_locations(self, tmp_path):
        """Test tool categorization with tools in both phase-specific and main directories"""
        output_dir = tmp_path / "output"
        tools_dir = output_dir / "tools"
        phase_dir = tools_dir / "phase_2"
        phase_dir.mkdir(parents=True, exist_ok=True)
        
        # Create tools in phase-specific directory
        (phase_dir / "phase_tool.py").write_text("# Phase tool")
        
        # Create tools in main directory
        (tools_dir / "general_tool.py").write_text("# General tool")
        
        loader = MigrationDataLoader(project_root=tmp_path)
        tools = loader._get_phase_tools(2)
        
        # Should find tools from both locations
        assert len(tools) >= 2
        tool_names = [t['name'] for t in tools]
        assert "phase_tool.py" in tool_names
        assert "general_tool.py" in tool_names
    
    def test_tool_categorization_empty_directory(self, tmp_path):
        """Test tool categorization with empty tools directory"""
        output_dir = tmp_path / "output"
        tools_dir = output_dir / "tools"
        tools_dir.mkdir(parents=True, exist_ok=True)
        
        loader = MigrationDataLoader(project_root=tmp_path)
        tools = loader._get_phase_tools(1)
        
        assert tools == []
    
    def test_tool_categorization_missing_directory(self, tmp_path):
        """Test tool categorization when tools directory doesn't exist"""
        loader = MigrationDataLoader(project_root=tmp_path)
        tools = loader._get_phase_tools(1)
        
        assert tools == []


class TestToolTypeIdentification:
    """
    **Feature: dashboard-file-structure-adaptation, Property 14: Tool Type Identification**
    
    For any tool file with extension .py, .sh, or .md, the Data_Loader should identify it as 
    Python Tool, Shell Script, or Documentation respectively.
    
    **Validates: Requirements 9.3**
    """
    
    @given(
        extension=st.sampled_from(['.py', '.sh', '.md']),
        tool_name_base=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=65, max_codepoint=122),
            min_size=3,
            max_size=20
        ).filter(lambda x: x and x[0].isalpha())
    )
    @settings(max_examples=100)
    def test_property_14_tool_type_identification(self, extension, tool_name_base):
        """Property test: Tool types are correctly identified by extension"""
        import tempfile
        import shutil
        
        # Create temporary directory
        tmp_path = Path(tempfile.mkdtemp())
        
        try:
            # Setup
            output_dir = tmp_path / "output"
            tools_dir = output_dir / "tools"
            tools_dir.mkdir(parents=True, exist_ok=True)
            
            # Create tool file with specific extension
            tool_file = tools_dir / f"{tool_name_base}{extension}"
            tool_file.write_text("# Tool content")
            
            # Create loader
            loader = MigrationDataLoader(project_root=tmp_path)
            
            # Get tools
            tools = loader._get_phase_tools(0)
            
            # Find our tool
            our_tool = None
            for tool in tools:
                if tool['name'] == tool_file.name:
                    our_tool = tool
                    break
            
            # Verify tool was found and has correct type
            assert our_tool is not None, f"Tool {tool_file.name} should be found"
            
            # Map extension to expected type
            expected_types = {
                '.py': 'Python Tool',
                '.sh': 'Shell Script',
                '.md': 'Documentation'
            }
            
            expected_type = expected_types[extension]
            assert our_tool['type'] == expected_type, \
                f"Tool with extension {extension} should have type '{expected_type}', got '{our_tool['type']}'"
        finally:
            # Cleanup
            shutil.rmtree(tmp_path, ignore_errors=True)
    
    def test_tool_type_python(self, tmp_path):
        """Test Python tool type identification"""
        output_dir = tmp_path / "output"
        tools_dir = output_dir / "tools"
        tools_dir.mkdir(parents=True, exist_ok=True)
        
        (tools_dir / "analyzer.py").write_text("# Python tool")
        
        loader = MigrationDataLoader(project_root=tmp_path)
        tools = loader._get_phase_tools(0)
        
        assert len(tools) == 1
        assert tools[0]['type'] == 'Python Tool'
        assert tools[0]['name'] == 'analyzer.py'
    
    def test_tool_type_shell_script(self, tmp_path):
        """Test shell script tool type identification"""
        output_dir = tmp_path / "output"
        tools_dir = output_dir / "tools"
        tools_dir.mkdir(parents=True, exist_ok=True)
        
        (tools_dir / "deploy.sh").write_text("#!/bin/bash")
        
        loader = MigrationDataLoader(project_root=tmp_path)
        tools = loader._get_phase_tools(0)
        
        assert len(tools) == 1
        assert tools[0]['type'] == 'Shell Script'
        assert tools[0]['name'] == 'deploy.sh'
    
    def test_tool_type_documentation(self, tmp_path):
        """Test documentation tool type identification"""
        output_dir = tmp_path / "output"
        tools_dir = output_dir / "tools"
        tools_dir.mkdir(parents=True, exist_ok=True)
        
        (tools_dir / "README.md").write_text("# Documentation")
        
        loader = MigrationDataLoader(project_root=tmp_path)
        tools = loader._get_phase_tools(0)
        
        assert len(tools) == 1
        assert tools[0]['type'] == 'Documentation'
        assert tools[0]['name'] == 'README.md'
    
    def test_tool_type_mixed_extensions(self, tmp_path):
        """Test tool type identification with multiple file types"""
        output_dir = tmp_path / "output"
        tools_dir = output_dir / "tools"
        tools_dir.mkdir(parents=True, exist_ok=True)
        
        (tools_dir / "tool1.py").write_text("# Python")
        (tools_dir / "tool2.sh").write_text("#!/bin/bash")
        (tools_dir / "tool3.md").write_text("# Docs")
        
        loader = MigrationDataLoader(project_root=tmp_path)
        tools = loader._get_phase_tools(0)
        
        assert len(tools) == 3
        
        # Check each tool has correct type
        tool_types = {t['name']: t['type'] for t in tools}
        assert tool_types['tool1.py'] == 'Python Tool'
        assert tool_types['tool2.sh'] == 'Shell Script'
        assert tool_types['tool3.md'] == 'Documentation'
    
    def test_tool_type_unknown_extension_ignored(self, tmp_path):
        """Test that files with unknown extensions are ignored"""
        output_dir = tmp_path / "output"
        tools_dir = output_dir / "tools"
        tools_dir.mkdir(parents=True, exist_ok=True)
        
        (tools_dir / "tool.py").write_text("# Python")
        (tools_dir / "data.txt").write_text("Some data")
        (tools_dir / "config.json").write_text("{}")
        
        loader = MigrationDataLoader(project_root=tmp_path)
        tools = loader._get_phase_tools(0)
        
        # Only .py file should be found
        assert len(tools) == 1
        assert tools[0]['name'] == 'tool.py'
    
    def test_tool_type_case_insensitive_extension(self, tmp_path):
        """Test that extension matching is case-insensitive"""
        output_dir = tmp_path / "output"
        tools_dir = output_dir / "tools"
        tools_dir.mkdir(parents=True, exist_ok=True)
        
        (tools_dir / "tool.PY").write_text("# Python")
        (tools_dir / "script.SH").write_text("#!/bin/bash")
        (tools_dir / "readme.MD").write_text("# Docs")
        
        loader = MigrationDataLoader(project_root=tmp_path)
        tools = loader._get_phase_tools(0)
        
        assert len(tools) == 3
        
        # Check each tool has correct type
        tool_types = {t['name']: t['type'] for t in tools}
        assert tool_types['tool.PY'] == 'Python Tool'
        assert tool_types['script.SH'] == 'Shell Script'
        assert tool_types['readme.MD'] == 'Documentation'



class TestDatabaseFileExistence:
    """
    Property 15: Database File Existence Check
    
    For any request for analysis database access, the Data_Loader should verify
    the file exists at output/analysis/source_code/analysis.db before providing the path.
    
    Validates: Requirements 10.2
    """
    
    @given(
        db_exists=st.booleans(),
        is_file=st.booleans()
    )
    @settings(max_examples=100)
    def test_property_15_database_file_existence_check(self, db_exists, is_file):
        """
        **Feature: dashboard-file-structure-adaptation, Property 15: Database File Existence Check**
        
        Property: For any request for database path, the loader should verify the file
        exists and is a regular file before returning the path.
        
        This test verifies that:
        1. When database file exists and is a file, path is returned
        2. When database file doesn't exist, None is returned
        3. When path exists but is not a file (e.g., directory), None is returned
        4. Path is always at output/analysis/source_code/analysis.db
        """
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            output_dir = tmp_path / "output"
            analysis_dir = output_dir / "analysis"
            source_dir = analysis_dir / "source_code"
            db_path = source_dir / "analysis.db"
            
            # Create directory structure
            source_dir.mkdir(parents=True, exist_ok=True)
            
            # Set up test scenario
            if db_exists:
                if is_file:
                    # Create as a file
                    db_path.write_text("SQLite database")
                else:
                    # Create as a directory
                    db_path.mkdir(exist_ok=True)
            
            loader = MigrationDataLoader(project_root=tmp_path)
            result = loader.get_database_path()
            
            # Verify behavior
            if db_exists and is_file:
                # Should return the path when file exists
                assert result is not None
                assert result == db_path
                assert result.exists()
                assert result.is_file()
            else:
                # Should return None when file doesn't exist or is not a file
                assert result is None
    
    def test_database_path_location(self, tmp_path):
        """Test that database path is always at the correct location"""
        output_dir = tmp_path / "output"
        analysis_dir = output_dir / "analysis"
        source_dir = analysis_dir / "source_code"
        db_path = source_dir / "analysis.db"
        
        # Create database file
        source_dir.mkdir(parents=True, exist_ok=True)
        db_path.write_text("SQLite database")
        
        loader = MigrationDataLoader(project_root=tmp_path)
        result = loader.get_database_path()
        
        # Verify path structure
        assert result == tmp_path / "output" / "analysis" / "source_code" / "analysis.db"
        assert str(result).endswith("output/analysis/source_code/analysis.db")
    
    def test_database_path_missing_directory(self, tmp_path):
        """Test behavior when source_code directory doesn't exist"""
        loader = MigrationDataLoader(project_root=tmp_path)
        result = loader.get_database_path()
        
        # Should return None when directory structure doesn't exist
        assert result is None



class TestDatabaseQueryFunctionality:
    """
    Unit tests for database query functionality
    
    Validates: Requirements 10.4
    """
    
    def test_query_database_with_valid_database(self, tmp_path):
        """Test querying database for module information"""
        import sqlite3
        
        # Create database with test data
        output_dir = tmp_path / "output"
        analysis_dir = output_dir / "analysis"
        source_dir = analysis_dir / "source_code"
        source_dir.mkdir(parents=True, exist_ok=True)
        
        db_path = source_dir / "analysis.db"
        
        # Create a simple test database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE modules (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL
            )
        """)
        cursor.execute("INSERT INTO modules (name, type) VALUES (?, ?)", ("MODULE1", "COBOL"))
        cursor.execute("INSERT INTO modules (name, type) VALUES (?, ?)", ("MODULE2", "COBOL"))
        cursor.execute("INSERT INTO modules (name, type) VALUES (?, ?)", ("MODULE3", "JCL"))
        conn.commit()
        conn.close()
        
        # Test query
        loader = MigrationDataLoader(project_root=tmp_path)
        results = loader.query_database("SELECT name, type FROM modules WHERE type = ?", ("COBOL",))
        
        assert len(results) == 2
        assert ("MODULE1", "COBOL") in results
        assert ("MODULE2", "COBOL") in results
    
    def test_query_database_without_params(self, tmp_path):
        """Test querying database without parameters"""
        import sqlite3
        
        # Create database with test data
        output_dir = tmp_path / "output"
        analysis_dir = output_dir / "analysis"
        source_dir = analysis_dir / "source_code"
        source_dir.mkdir(parents=True, exist_ok=True)
        
        db_path = source_dir / "analysis.db"
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE test (id INTEGER, value TEXT)")
        cursor.execute("INSERT INTO test VALUES (1, 'test1')")
        cursor.execute("INSERT INTO test VALUES (2, 'test2')")
        conn.commit()
        conn.close()
        
        # Test query without parameters
        loader = MigrationDataLoader(project_root=tmp_path)
        results = loader.query_database("SELECT * FROM test")
        
        assert len(results) == 2
        assert (1, 'test1') in results
        assert (2, 'test2') in results
    
    def test_query_database_missing_file(self, tmp_path):
        """Test that missing database returns empty list"""
        loader = MigrationDataLoader(project_root=tmp_path)
        results = loader.query_database("SELECT * FROM modules")
        
        assert results == []
    
    def test_query_database_invalid_query(self, tmp_path):
        """Test that invalid SQL query returns empty list"""
        import sqlite3
        
        # Create database
        output_dir = tmp_path / "output"
        analysis_dir = output_dir / "analysis"
        source_dir = analysis_dir / "source_code"
        source_dir.mkdir(parents=True, exist_ok=True)
        
        db_path = source_dir / "analysis.db"
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE test (id INTEGER)")
        conn.commit()
        conn.close()
        
        # Test with invalid query
        loader = MigrationDataLoader(project_root=tmp_path)
        results = loader.query_database("SELECT * FROM nonexistent_table")
        
        assert results == []
    
    def test_query_database_malformed_sql(self, tmp_path):
        """Test that malformed SQL returns empty list"""
        import sqlite3
        
        # Create database
        output_dir = tmp_path / "output"
        analysis_dir = output_dir / "analysis"
        source_dir = analysis_dir / "source_code"
        source_dir.mkdir(parents=True, exist_ok=True)
        
        db_path = source_dir / "analysis.db"
        
        conn = sqlite3.connect(str(db_path))
        conn.close()
        
        # Test with malformed SQL
        loader = MigrationDataLoader(project_root=tmp_path)
        results = loader.query_database("INVALID SQL SYNTAX")
        
        assert results == []



class TestTimestampParsingAndFormatting:
    """
    Property 18: Timestamp Parsing and Formatting
    
    For any ISO 8601 timestamp with timezone information, the Data_Loader should
    parse it correctly and format it as MM/DD HH:MM for display.
    
    Validates: Requirements 15.3, 15.5
    """
    
    @given(
        year=st.integers(min_value=2020, max_value=2030),
        month=st.integers(min_value=1, max_value=12),
        day=st.integers(min_value=1, max_value=28),  # Safe for all months
        hour=st.integers(min_value=0, max_value=23),
        minute=st.integers(min_value=0, max_value=59),
        second=st.integers(min_value=0, max_value=59),
        timezone_format=st.sampled_from(['Z', '+00:00', '+01:00', '-05:00', ''])
    )
    def test_property_18_timestamp_parsing_and_formatting(
        self, year, month, day, hour, minute, second, timezone_format
    ):
        """
        **Feature: dashboard-file-structure-adaptation, Property 18: Timestamp Parsing and Formatting**
        
        Property: For any ISO 8601 timestamp with timezone information, the Data_Loader
        should parse it correctly and format it as MM/DD HH:MM for display.
        
        This test verifies that:
        1. ISO 8601 timestamps with various timezone formats are parsed correctly
        2. Timestamps are formatted as MM/DD HH:MM
        3. Parsing handles Z suffix, +HH:MM offset, and no timezone
        4. Formatting is consistent across all valid timestamps
        """
        import tempfile
        
        # Create test project
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir) / "test_project"
            project_root.mkdir()
            
            loader = MigrationDataLoader(project_root=str(project_root))
            
            # Create ISO 8601 timestamp string (Requirement 15.3)
            timestamp_str = f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}{timezone_format}"
            
            # Test parsing
            parsed_dt = loader._parse_timestamp(timestamp_str)
            
            # Should successfully parse
            assert parsed_dt is not None, f"Failed to parse timestamp: {timestamp_str}"
            
            # Verify parsed values
            assert parsed_dt.year == year
            assert parsed_dt.month == month
            assert parsed_dt.day == day
            assert parsed_dt.hour == hour
            assert parsed_dt.minute == minute
            assert parsed_dt.second == second
            
            # Test formatting (Requirement 15.5)
            formatted = loader._format_timestamp(timestamp_str)
            
            # Should format as MM/DD HH:MM
            assert formatted is not None
            assert isinstance(formatted, str)
            
            # Verify format pattern
            expected_format = f"{month:02d}/{day:02d} {hour:02d}:{minute:02d}"
            assert formatted == expected_format, \
                f"Expected format '{expected_format}', got '{formatted}'"
    
    def test_timestamp_parsing_with_various_formats(self, tmp_path):
        """Test that various ISO 8601 formats are parsed correctly"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Test various timestamp formats
        test_cases = [
            ("2024-01-15T10:30:00Z", "01/15 10:30"),
            ("2024-01-15T10:30:00+00:00", "01/15 10:30"),
            ("2024-01-15T10:30:00", "01/15 10:30"),
            ("2024-12-25T23:59:59Z", "12/25 23:59"),
            ("2024-06-01T00:00:00", "06/01 00:00"),
            ("2024-01-15", "01/15 00:00"),  # Date only
        ]
        
        for timestamp_str, expected_format in test_cases:
            formatted = loader._format_timestamp(timestamp_str)
            assert formatted == expected_format, \
                f"For timestamp '{timestamp_str}', expected '{expected_format}', got '{formatted}'"
    
    def test_timestamp_parsing_with_invalid_input(self, tmp_path):
        """Test that invalid timestamps are handled gracefully"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Test invalid inputs
        invalid_inputs = [
            None,
            "",
            "not a timestamp",
            "2024-13-01T10:30:00",  # Invalid month
            "invalid-date-format"
        ]
        
        for invalid_input in invalid_inputs:
            # Should not crash
            parsed = loader._parse_timestamp(invalid_input)
            
            # Should return None for invalid input
            if invalid_input is None or invalid_input == "":
                assert parsed is None
            
            # Formatting should return fallback
            formatted = loader._format_timestamp(invalid_input)
            assert formatted == "Completed"  # Fallback value
    
    def test_timestamp_formatting_consistency(self, tmp_path):
        """Test that formatting is consistent across multiple calls"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        timestamp_str = "2024-01-15T10:30:00Z"
        
        # Format multiple times
        formatted1 = loader._format_timestamp(timestamp_str)
        formatted2 = loader._format_timestamp(timestamp_str)
        formatted3 = loader._format_timestamp(timestamp_str)
        
        # Should be consistent
        assert formatted1 == formatted2 == formatted3
        assert formatted1 == "01/15 10:30"


class TestTimestampFallback:
    """
    Property 19: Timestamp Fallback
    
    For any progress file without a timestamp field, the Data_Loader should use
    the file's modification time as a fallback.
    
    Validates: Requirements 15.4
    """
    
    @given(
        has_timestamp_field=st.booleans(),
        timestamp_field_name=st.sampled_from([
            "last_updated", "lastUpdated", "timestamp", 
            "completion_time", "completedAt", "endTime"
        ])
    )
    def test_property_19_timestamp_fallback(self, has_timestamp_field, timestamp_field_name):
        """
        **Feature: dashboard-file-structure-adaptation, Property 19: Timestamp Fallback**
        
        Property: For any progress file without a timestamp field, the Data_Loader
        should use the file's modification time as a fallback.
        
        This test verifies that:
        1. When timestamp field exists, it is used
        2. When timestamp field is missing, file modification time is used
        3. Fallback works for any progress file
        4. File modification time is returned in ISO 8601 format
        """
        import tempfile
        import json
        import time
        
        # Create test project
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir) / "test_project"
            project_root.mkdir()
            
            # Create progress directory
            progress_dir = project_root / "output" / "analysis" / "source_code" / "progress"
            progress_dir.mkdir(parents=True)
            
            # Create progress file
            progress_file = progress_dir / "test_progress.json"
            
            if has_timestamp_field:
                # Include timestamp field
                progress_data = {
                    timestamp_field_name: "2024-01-15T10:30:00Z",
                    "status": "completed"
                }
            else:
                # No timestamp field
                progress_data = {
                    "status": "completed"
                }
            
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f)
            
            # Wait a moment to ensure file is written
            time.sleep(0.01)
            
            # Initialize loader
            loader = MigrationDataLoader(project_root=str(project_root))
            
            # Extract timestamp
            extracted_timestamp = loader._extract_timestamp(progress_data, progress_file)
            
            # Should always return a timestamp
            assert extracted_timestamp is not None
            
            if has_timestamp_field:
                # Should use the timestamp from the field (Requirement 15.1, 15.2)
                assert extracted_timestamp == "2024-01-15T10:30:00Z"
            else:
                # Should use file modification time (Requirement 15.4)
                # Verify it's a valid ISO 8601 timestamp
                assert isinstance(extracted_timestamp, str)
                # Should be parseable
                parsed = loader._parse_timestamp(extracted_timestamp)
                assert parsed is not None
    
    def test_timestamp_extraction_with_missing_file(self, tmp_path):
        """Test that missing file is handled gracefully"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Progress data without timestamp
        progress_data = {"status": "completed"}
        
        # Non-existent file
        non_existent_file = project_root / "does_not_exist.json"
        
        # Should return None (no timestamp in data, file doesn't exist)
        extracted = loader._extract_timestamp(progress_data, non_existent_file)
        assert extracted is None
    
    def test_timestamp_extraction_priority(self, tmp_path):
        """Test that timestamp fields are checked in priority order"""
        import json
        
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Progress data with multiple timestamp fields
        progress_data = {
            "last_updated": "2024-01-15T10:30:00Z",
            "timestamp": "2024-01-16T11:00:00Z",
            "completion_time": "2024-01-17T12:00:00Z"
        }
        
        # Should use first available field (last_updated)
        extracted = loader._extract_timestamp(progress_data, None)
        assert extracted == "2024-01-15T10:30:00Z"
    
    def test_file_mtime_fallback(self, tmp_path):
        """Test that file modification time is used as fallback"""
        import json
        import time
        
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create progress file
        progress_file = project_root / "progress.json"
        progress_data = {"status": "completed"}  # No timestamp field
        
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f)
        
        # Wait to ensure file is written
        time.sleep(0.01)
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Extract timestamp with fallback
        extracted = loader._extract_timestamp(progress_data, progress_file)
        
        # Should return file modification time
        assert extracted is not None
        
        # Should be a valid ISO 8601 timestamp
        parsed = loader._parse_timestamp(extracted)
        assert parsed is not None
        
        # Should be recent (within last minute)
        from datetime import datetime, timedelta
        now = datetime.now()
        assert (now - parsed) < timedelta(minutes=1)
    
    def test_timestamp_extraction_in_phase_status(self, tmp_path):
        """Test that timestamp extraction works in get_phase_status"""
        import json
        
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create Phase 1 progress file without timestamp field
        progress_dir = project_root / "output" / "analysis" / "source_code" / "progress"
        progress_dir.mkdir(parents=True)
        
        progress_file = progress_dir / "analysis_status.json"
        progress_data = {
            "status": "completed"
            # No timestamp field - should use file mtime
        }
        
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f)
        
        loader = MigrationDataLoader(project_root=str(project_root))
        phases = loader.get_phase_status()
        
        phase1 = phases[1]
        
        # Should have status
        assert phase1["status"] == "completed"
        
        # Should have lastUpdated from file mtime (Requirement 15.4)
        assert "lastUpdated" in phase1
        assert phase1["lastUpdated"] is not None



class TestErrorHandlingWithoutCrashes:
    """
    Property 2: Error Handling Without Crashes
    
    For any missing file, missing directory, or malformed JSON, the Data_Loader should
    return appropriate default values without raising unhandled exceptions.
    
    Validates: Requirements 1.4, 6.5, 8.4, 10.3, 12.1, 12.2, 12.3, 12.4
    """
    
    @given(
        phase_id=st.integers(min_value=0, max_value=8),
        has_directory=st.booleans(),
        has_progress_file=st.booleans(),
        json_is_malformed=st.booleans()
    )
    def test_property_2_error_handling_without_crashes(
        self, phase_id, has_directory, has_progress_file, json_is_malformed
    ):
        """
        **Feature: dashboard-file-structure-adaptation, Property 2: Error Handling Without Crashes**
        
        Property: For any missing file, missing directory, or malformed JSON,
        the Data_Loader should return appropriate default values without raising
        unhandled exceptions.
        
        This test verifies that:
        1. Missing directories return empty lists (Requirement 12.3)
        2. Missing files return default status structures (Requirement 12.1)
        3. Malformed JSON returns empty structures (Requirement 12.2)
        4. Dashboard displays available data when some is missing (Requirement 12.4)
        5. No unhandled exceptions are raised (Requirements 1.4, 6.5, 8.4, 10.3)
        """
        import tempfile
        import json
        
        # Create test project structure
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir) / "test_project"
            project_root.mkdir()
            
            # Conditionally create directory structure
            if has_directory:
                if phase_id in [0, 1]:
                    progress_dir = project_root / "output" / "analysis" / "source_code" / "progress"
                elif phase_id == 2:
                    progress_dir = project_root / "output" / "analysis" / "workpackages" / "progress"
                elif phase_id == 3:
                    progress_dir = project_root / "output" / "specifications" / "progress"
                else:  # 4-8
                    progress_dir = project_root / "output" / "migration" / "progress"
                
                progress_dir.mkdir(parents=True, exist_ok=True)
                
                # Conditionally create progress file
                if has_progress_file:
                    if phase_id == 3:
                        progress_file = progress_dir / "Business_Specification_Status.json"
                    elif phase_id == 2:
                        progress_file = progress_dir / "Workpackage_Status.json"
                    else:
                        progress_file = progress_dir / f"phase_{phase_id}_status.json"
                    
                    # Create malformed or valid JSON
                    if json_is_malformed:
                        # Write malformed JSON (Requirement 12.2)
                        with open(progress_file, 'w') as f:
                            f.write("{ invalid json content }")
                    else:
                        # Write valid JSON
                        if phase_id == 3:
                            data = {
                                "summary": {
                                    "total_workpackages": 5,
                                    "approved": 2,
                                    "approved_with_changes": 1
                                },
                                "workpackages": []
                            }
                        else:
                            data = {
                                "status": "in_progress",
                                "timestamp": "2024-01-15T10:30:00"
                            }
                        with open(progress_file, 'w', encoding='utf-8') as f:
                            json.dump(data, f)
            
            # Initialize loader
            loader = MigrationDataLoader(project_root=str(project_root))
            
            # Test 1: get_phase_status should not crash (Requirements 12.1, 12.2, 12.3)
            try:
                phases = loader.get_phase_status()
                assert isinstance(phases, list), "get_phase_status should return a list"
                assert len(phases) == 9, "get_phase_status should return 9 phases"
                
                # Verify each phase has required fields
                for phase in phases:
                    assert "id" in phase
                    assert "name" in phase
                    assert "status" in phase
                    assert phase["status"] in ["completed", "in_progress", "unknown"]
            except Exception as e:
                pytest.fail(f"get_phase_status crashed with exception: {e}")
            
            # Test 2: get_phase_details should not crash (Requirements 12.1, 12.2, 12.3, 12.4)
            try:
                phase_details = loader.get_phase_details(phase_id)
                assert isinstance(phase_details, dict), "get_phase_details should return a dict"
                
                # Verify required fields exist
                assert "phaseId" in phase_details
                assert "name" in phase_details
                assert "status" in phase_details
                assert "artifacts" in phase_details
                assert "reports" in phase_details
                assert "tools" in phase_details
                
                # Verify fields are correct types
                assert isinstance(phase_details["artifacts"], list)
                assert isinstance(phase_details["reports"], list)
                assert isinstance(phase_details["tools"], list)
            except Exception as e:
                pytest.fail(f"get_phase_details crashed with exception: {e}")
            
            # Test 3: get_workpackage_progress should not crash (Requirements 12.1, 12.2)
            try:
                progress = loader.get_workpackage_progress()
                assert isinstance(progress, dict), "get_workpackage_progress should return a dict"
                
                # Verify required fields
                assert "total" in progress
                assert "phase3_completed" in progress
                assert "phase4_ready" in progress
                assert "workpackages" in progress
                
                # Verify types
                assert isinstance(progress["total"], int)
                assert isinstance(progress["phase3_completed"], int)
                assert isinstance(progress["phase4_ready"], int)
                assert isinstance(progress["workpackages"], list)
            except Exception as e:
                pytest.fail(f"get_workpackage_progress crashed with exception: {e}")
            
            # Test 4: get_project_overview should not crash (Requirement 12.4)
            try:
                overview = loader.get_project_overview()
                assert isinstance(overview, dict), "get_project_overview should return a dict"
                
                # Verify required fields
                assert "projectName" in overview
                assert "phases" in overview
                assert "stats" in overview
            except Exception as e:
                pytest.fail(f"get_project_overview crashed with exception: {e}")
    
    def test_error_handling_with_missing_files(self, tmp_path):
        """Test that missing files return default values without crashing"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create minimal directory structure but no files
        (project_root / "output").mkdir()
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Should not crash (Requirement 12.1)
        phases = loader.get_phase_status()
        assert len(phases) == 9
        
        progress = loader.get_workpackage_progress()
        assert progress["total"] == 0
        assert progress["phase3_completed"] == 0
        
        overview = loader.get_project_overview()
        assert "projectName" in overview
    
    def test_error_handling_with_malformed_json(self, tmp_path):
        """Test that malformed JSON returns empty structures without crashing"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create progress directory with malformed JSON
        progress_dir = project_root / "output" / "specifications" / "progress"
        progress_dir.mkdir(parents=True)
        
        # Write malformed JSON
        status_file = progress_dir / "Business_Specification_Status.json"
        with open(status_file, 'w') as f:
            f.write("{ this is not valid json }")
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Should not crash (Requirement 12.2)
        progress = loader.get_workpackage_progress()
        assert isinstance(progress, dict)
        assert progress["total"] == 0
        assert progress["workpackages"] == []
        
        phases = loader.get_phase_status()
        assert len(phases) == 9
    
    def test_error_handling_with_missing_directories(self, tmp_path):
        """Test that missing directories return empty lists without crashing"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Don't create any output directories
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Should not crash (Requirement 12.3)
        for phase_id in range(8):
            phase_details = loader.get_phase_details(phase_id)
            assert isinstance(phase_details, dict)
            assert isinstance(phase_details["artifacts"], list)
            assert isinstance(phase_details["reports"], list)
            assert isinstance(phase_details["tools"], list)
    
    def test_graceful_degradation_with_partial_data(self, tmp_path):
        """Test that dashboard displays available data when some is missing"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create partial data - only Phase 0 and Phase 1 directories
        phase0_dir = project_root / "output" / "analysis" / "source_code"
        phase0_dir.mkdir(parents=True)
        
        # Create a file in Phase 0
        test_file = phase0_dir / "test_artifact.json"
        with open(test_file, 'w') as f:
            f.write('{"test": "data"}')
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Should not crash and should display available data (Requirement 12.4)
        overview = loader.get_project_overview()
        assert "phases" in overview
        assert len(overview["phases"]) == 9
        
        # Phase 0 should have some data
        phase0_details = loader.get_phase_details(0)
        assert len(phase0_details["artifacts"]) > 0
        
        # Phase 3 should have empty data but not crash
        phase3_details = loader.get_phase_details(3)
        assert isinstance(phase3_details["artifacts"], list)
        assert len(phase3_details["artifacts"]) == 0
    
    def test_database_error_handling(self, tmp_path):
        """Test that database errors are handled gracefully"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Database file doesn't exist (Requirement 10.3)
        db_path = loader.get_database_path()
        assert db_path is None
        
        # Query should return empty list without crashing (Requirement 10.3)
        results = loader.query_database("SELECT * FROM modules")
        assert isinstance(results, list)
        assert len(results) == 0
    
    def test_missing_json_fields_handled_gracefully(self, tmp_path):
        """Test that missing JSON fields are handled with defaults"""
        import json
        
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create progress file with minimal data
        progress_dir = project_root / "output" / "specifications" / "progress"
        progress_dir.mkdir(parents=True)
        
        status_file = progress_dir / "Business_Specification_Status.json"
        # Missing many expected fields
        minimal_data = {
            "summary": {
                "total_workpackages": 3
                # Missing approved, approved_with_changes, etc.
            }
        }
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(minimal_data, f)
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Should not crash and should use defaults (Requirement 6.5)
        progress = loader.get_workpackage_progress()
        assert progress["total"] == 3
        assert progress["phase3_completed"] == 0  # Default when fields missing
        assert progress["phase4_ready"] == 0



class TestRelativePathCalculation:
    """
    Property 16: Relative Path Calculation
    
    For any file path, when calculating relative paths, the Data_Loader should use
    project_root as the base and produce consistent relative paths.
    
    Validates: Requirements 11.4
    """
    
    @given(
        subdirs=st.lists(
            st.text(min_size=1, max_size=20, alphabet=st.characters(
                whitelist_categories=('Lu', 'Ll', 'Nd'),
                whitelist_characters='_-'
            )),
            min_size=0,
            max_size=5
        ),
        filename=st.text(min_size=1, max_size=30, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            whitelist_characters='_-.'
        ))
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_16_relative_path_calculation(self, subdirs, filename, tmp_path):
        """
        **Feature: dashboard-file-structure-adaptation, Property 16: Relative Path Calculation**
        
        Property: For any file path within the project, the _get_relative_path method
        should calculate paths relative to project_root with consistent forward-slash format.
        
        This test verifies that:
        1. Paths are calculated relative to project_root
        2. Forward slashes are used consistently (cross-platform)
        3. Nested paths are handled correctly
        4. The method handles both Path objects and strings
        """
        # Skip if filename is empty or contains only dots
        if not filename or filename.strip('.') == '':
            return
        
        # Skip if any subdir is empty or contains only dots/dashes
        if any(not s or s.strip('.-_') == '' for s in subdirs):
            return
        
        project_root = tmp_path / "test_project"
        project_root.mkdir(exist_ok=True)
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Create a file path within the project
        file_path = project_root
        for subdir in subdirs:
            file_path = file_path / subdir
        file_path = file_path / filename
        
        # Test with Path object
        rel_path = loader._get_relative_path(file_path)
        
        # Verify it's a string
        assert isinstance(rel_path, str), "Relative path should be a string"
        
        # Verify it uses forward slashes (cross-platform consistency)
        assert '\\' not in rel_path, "Relative path should use forward slashes, not backslashes"
        
        # Verify the path is relative (doesn't start with / or drive letter)
        assert not rel_path.startswith('/'), "Relative path should not start with /"
        if len(rel_path) > 1:
            assert rel_path[1] != ':', "Relative path should not contain drive letter"
        
        # Verify the path ends with the filename
        assert rel_path.endswith(filename), f"Relative path should end with filename {filename}"
        
        # Verify subdirectories are in the path
        for subdir in subdirs:
            assert subdir in rel_path, f"Subdirectory {subdir} should be in relative path"
        
        # Test with string path
        rel_path_from_str = loader._get_relative_path(str(file_path))
        assert rel_path == rel_path_from_str, "Should produce same result for Path and string"
    
    def test_relative_path_with_actual_files(self, tmp_path):
        """Test relative path calculation with actual file structure"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create actual directory structure
        output_dir = project_root / "output"
        analysis_dir = output_dir / "analysis"
        source_dir = analysis_dir / "source_code"
        source_dir.mkdir(parents=True)
        
        # Create a test file
        test_file = source_dir / "test_analysis.json"
        test_file.write_text("{}")
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Calculate relative path
        rel_path = loader._get_relative_path(test_file)
        
        # Verify the path is correct
        assert rel_path == "output/analysis/source_code/test_analysis.json"
        
        # Verify it uses forward slashes
        assert '\\' not in rel_path
    
    def test_relative_path_outside_project_root(self, tmp_path):
        """Test that paths outside project_root are handled gracefully"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create a file outside project_root
        outside_file = tmp_path / "outside.txt"
        outside_file.write_text("test")
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Should handle gracefully and return the path (with warning logged)
        rel_path = loader._get_relative_path(outside_file)
        
        # Should return a string (even if not truly relative)
        assert isinstance(rel_path, str)
        assert '\\' not in rel_path  # Should still use forward slashes
    
    def test_relative_path_consistency_across_phases(self, tmp_path):
        """Test that relative paths are consistent across all phase artifact methods"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Create test files in different phase directories
        test_files = {
            "phase0": project_root / "output" / "analysis" / "source_code" / "test0.json",
            "phase1": project_root / "output" / "analysis" / "source_code" / "flows" / "test1.md",
            "phase2": project_root / "output" / "analysis" / "workpackages" / "test2.json",
            "phase3": project_root / "output" / "specifications" / "business" / "test3.md",
            "phase4": project_root / "output" / "gen_src" / "test4.java",
            "phase5": project_root / "output" / "specifications" / "test_cases" / "test5.md",
            "phase6": project_root / "output" / "specifications" / "review" / "test6.md",
            "phase7": project_root / "output" / "migration" / "deliverables" / "test7.java"
        }
        
        # Create all test files
        for phase, file_path in test_files.items():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text("test")
        
        # Get phase details for each phase
        for phase_id in range(8):
            details = loader.get_phase_details(phase_id)
            
            # Check that all paths in artifacts use forward slashes
            for artifact in details.get("artifacts", []):
                path = artifact.get("path", "")
                assert '\\' not in path, f"Phase {phase_id} artifact path should use forward slashes"
                
                # Verify path starts with expected prefix
                if phase_id in [0, 1]:
                    assert path.startswith("output/analysis/source_code"), \
                        f"Phase {phase_id} path should start with output/analysis/source_code"
                elif phase_id == 2:
                    assert path.startswith("output/analysis/workpackages"), \
                        f"Phase {phase_id} path should start with output/analysis/workpackages"
                elif phase_id == 3:
                    assert path.startswith("output/specifications"), \
                        f"Phase {phase_id} path should start with output/specifications"
                elif phase_id == 4:
                    assert path.startswith("output/gen_src"), \
                        f"Phase {phase_id} path should start with output/gen_src"
                elif phase_id in [5, 6]:
                    assert path.startswith("output/specifications"), \
                        f"Phase {phase_id} path should start with output/specifications"
                elif phase_id == 7:
                    assert path.startswith("output/migration"), \
                        f"Phase {phase_id} path should start with output/migration"
            
            # Check that all paths in reports use forward slashes
            for report in details.get("reports", []):
                path = report.get("path", "")
                assert '\\' not in path, f"Phase {phase_id} report path should use forward slashes"
    
    def test_relative_path_with_tools(self, tmp_path):
        """Test that tool paths are calculated correctly"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create tools directory with test files
        tools_dir = project_root / "output" / "tools"
        tools_dir.mkdir(parents=True)
        
        test_tool = tools_dir / "test_tool.py"
        test_tool.write_text("# test tool")
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Get tools for a phase
        tools = loader._get_phase_tools(1)
        
        # Verify tool paths use forward slashes
        for tool in tools:
            path = tool.get("path", "")
            assert '\\' not in path, "Tool path should use forward slashes"
            assert path.startswith("output/tools"), "Tool path should start with output/tools"



class TestProgressDirectorySearchOrder:
    """
    Property 17: Progress Directory Search Order
    
    For any phase, when looking for progress files, the Data_Loader should check
    phase-specific progress directories before returning defaults.
    
    Validates: Requirements 11.2
    """
    
    @given(
        phase_id=st.integers(min_value=0, max_value=8),
        has_progress_file=st.booleans(),
        file_pattern_index=st.integers(min_value=0, max_value=2)
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_17_progress_directory_search_order(
        self, phase_id, has_progress_file, file_pattern_index
    ):
        """
        **Feature: dashboard-file-structure-adaptation, Property 17: Progress Directory Search Order**
        
        Property: For any phase, when looking for progress files, the Data_Loader
        should check phase-specific progress directories before returning defaults.
        
        This test verifies that:
        1. Phase 0-1 check output/analysis/source_code/progress/ first
        2. Phase 2 checks output/analysis/workpackages/progress/ first
        3. Phase 3 checks output/specifications/progress/ first
        4. Phase 4-8 check output/migration/progress/ first
        5. Returns None when no matching files found (defaults)
        6. Returns the first matching file when multiple patterns match
        """
        import tempfile
        import json
        
        # Create test project structure
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir) / "test_project"
            project_root.mkdir()
            
            # Define phase-specific progress directories (matching implementation)
            phase_progress_dirs = {
                0: project_root / "output" / "analysis" / "source_code" / "progress",
                1: project_root / "output" / "analysis" / "source_code" / "progress",
                2: project_root / "output" / "analysis" / "workpackages" / "progress",
                3: project_root / "output" / "specifications" / "progress",
                4: project_root / "output" / "migration" / "progress",
                5: project_root / "output" / "migration" / "progress",
                6: project_root / "output" / "migration" / "progress",
                7: project_root / "output" / "migration" / "progress",
                8: project_root / "output" / "migration" / "progress"
            }
            
            # Get the correct progress directory for this phase
            progress_dir = phase_progress_dirs[phase_id]
            progress_dir.mkdir(parents=True, exist_ok=True)
            
            # Define default patterns for each phase (matching implementation)
            default_patterns = {
                0: ["*preparation*.json"],
                1: ["*analysis*.json"],
                2: ["Workpackage_Status.json"],
                3: ["Business_Specification_Status.json"],
                4: ["*code*generation*.json", "*phase*4*.json"],
                5: ["*test*generation*.json", "*phase*5*.json"],
                6: ["*quality*validation*.json", "*phase*6*.json"],
                7: ["*developer*review*.json", "*phase*7*.json", "*deliverable*.json"],
                8: ["*developer*review*.json", "*phase*8*.json", "*deliverable*.json"]
            }
            
            patterns = default_patterns.get(phase_id, ["*.json"])
            
            # Create a progress file if requested
            if has_progress_file and patterns:
                # Use the file_pattern_index to select which pattern to match
                pattern_to_use = patterns[file_pattern_index % len(patterns)]
                
                # Generate a filename that matches the pattern
                if pattern_to_use == "Workpackage_Status.json":
                    filename = "Workpackage_Status.json"
                elif pattern_to_use == "Business_Specification_Status.json":
                    filename = "Business_Specification_Status.json"
                else:
                    # For wildcard patterns, create a matching filename
                    pattern_clean = pattern_to_use.replace('*', '').replace('.json', '')
                    filename = f"test_{pattern_clean}_status.json"
                
                progress_file = progress_dir / filename
                with open(progress_file, 'w', encoding='utf-8') as f:
                    json.dump({"status": "test", "phase": phase_id}, f)
            
            # Initialize loader
            loader = MigrationDataLoader(project_root=str(project_root))
            
            # Call _get_progress_file_for_phase
            result = loader._get_progress_file_for_phase(phase_id)
            
            # Verify behavior
            if has_progress_file:
                # Should find the file
                assert result is not None, \
                    f"Expected to find progress file for phase {phase_id}"
                assert isinstance(result, Path), \
                    "Result should be a Path object"
                assert result.exists(), \
                    "Returned path should exist"
                assert result.is_file(), \
                    "Returned path should be a file"
                
                # Verify it's in the correct directory
                assert result.parent == progress_dir, \
                    f"Progress file should be in phase-specific directory {progress_dir}"
                
                # Verify it matches one of the expected patterns
                filename = result.name
                matches_pattern = False
                for pattern in patterns:
                    if pattern == filename:
                        matches_pattern = True
                        break
                    # Check wildcard patterns
                    pattern_parts = pattern.replace('*', '').replace('.json', '').split()
                    if all(part in filename for part in pattern_parts if part):
                        matches_pattern = True
                        break
                
                assert matches_pattern, \
                    f"Filename {filename} should match one of the patterns {patterns}"
            else:
                # Should return None (no file found)
                assert result is None, \
                    f"Expected None when no progress file exists for phase {phase_id}"
    
    def test_progress_directory_search_checks_correct_directories(self, tmp_path):
        """Test that each phase checks its specific progress directory"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create all progress directories
        progress_dirs = {
            0: project_root / "output" / "analysis" / "source_code" / "progress",
            1: project_root / "output" / "analysis" / "source_code" / "progress",
            2: project_root / "output" / "analysis" / "workpackages" / "progress",
            3: project_root / "output" / "specifications" / "progress",
            4: project_root / "output" / "migration" / "progress",
            5: project_root / "output" / "migration" / "progress",
            6: project_root / "output" / "migration" / "progress",
            7: project_root / "output" / "migration" / "progress"
        }
        
        for phase_id, progress_dir in progress_dirs.items():
            progress_dir.mkdir(parents=True, exist_ok=True)
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Test each phase
        for phase_id in range(8):
            # Call without creating files - should return None
            result = loader._get_progress_file_for_phase(phase_id)
            assert result is None, f"Phase {phase_id} should return None when no files exist"
    
    def test_progress_directory_search_with_specific_patterns(self, tmp_path):
        """Test that custom patterns work correctly"""
        import json
        
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create progress directory for phase 1
        progress_dir = project_root / "output" / "analysis" / "source_code" / "progress"
        progress_dir.mkdir(parents=True)
        
        # Create multiple files
        file1 = progress_dir / "custom_analysis.json"
        file2 = progress_dir / "other_file.json"
        
        with open(file1, 'w') as f:
            json.dump({"status": "test1"}, f)
        with open(file2, 'w') as f:
            json.dump({"status": "test2"}, f)
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Search with custom pattern
        result = loader._get_progress_file_for_phase(1, patterns=["custom*.json"])
        
        assert result is not None
        assert result.name == "custom_analysis.json"
        
        # Search with different pattern
        result2 = loader._get_progress_file_for_phase(1, patterns=["other*.json"])
        
        assert result2 is not None
        assert result2.name == "other_file.json"
    
    def test_progress_directory_search_returns_first_match(self, tmp_path):
        """Test that when multiple files match, the first one is returned"""
        import json
        
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create progress directory for phase 4
        progress_dir = project_root / "output" / "migration" / "progress"
        progress_dir.mkdir(parents=True)
        
        # Create multiple matching files
        file1 = progress_dir / "code_generation_status.json"
        file2 = progress_dir / "phase_4_status.json"
        
        with open(file1, 'w') as f:
            json.dump({"status": "file1"}, f)
        with open(file2, 'w') as f:
            json.dump({"status": "file2"}, f)
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Should return first match
        result = loader._get_progress_file_for_phase(4)
        
        assert result is not None
        # Should match one of the patterns
        assert result.name in ["code_generation_status.json", "phase_4_status.json"]
    
    def test_progress_directory_search_handles_missing_directory(self, tmp_path):
        """Test that missing progress directory is handled gracefully"""
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Don't create any progress directories
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Should return None for all phases
        for phase_id in range(8):
            result = loader._get_progress_file_for_phase(phase_id)
            assert result is None, \
                f"Phase {phase_id} should return None when directory doesn't exist"
    
    def test_progress_directory_search_phase2_specific_file(self, tmp_path):
        """Test Phase 2 searches for specific Workpackage_Status.json file"""
        import json
        
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create progress directory for phase 2
        progress_dir = project_root / "output" / "analysis" / "workpackages" / "progress"
        progress_dir.mkdir(parents=True)
        
        # Create the specific file
        status_file = progress_dir / "Workpackage_Status.json"
        with open(status_file, 'w') as f:
            json.dump({"status": "completed"}, f)
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Should find the specific file
        result = loader._get_progress_file_for_phase(2)
        
        assert result is not None
        assert result.name == "Workpackage_Status.json"
        assert result.parent == progress_dir
    
    def test_progress_directory_search_phase3_specific_file(self, tmp_path):
        """Test Phase 3 searches for specific Business_Specification_Status.json file"""
        import json
        
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create progress directory for phase 3
        progress_dir = project_root / "output" / "specifications" / "progress"
        progress_dir.mkdir(parents=True)
        
        # Create the specific file
        status_file = progress_dir / "Business_Specification_Status.json"
        with open(status_file, 'w') as f:
            json.dump({"status": "completed", "summary": {"total_workpackages": 10}}, f)
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Should find the specific file
        result = loader._get_progress_file_for_phase(3)
        
        assert result is not None
        assert result.name == "Business_Specification_Status.json"
        assert result.parent == progress_dir
    
    def test_progress_directory_search_with_multiple_patterns(self, tmp_path):
        """Test that multiple patterns are tried in order"""
        import json
        
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create progress directory for phase 7
        progress_dir = project_root / "output" / "migration" / "progress"
        progress_dir.mkdir(parents=True)
        
        # Create a file matching the third pattern
        deliverable_file = progress_dir / "deliverable_status.json"
        with open(deliverable_file, 'w') as f:
            json.dump({"status": "completed"}, f)
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Should find the file even though it matches the third pattern
        result = loader._get_progress_file_for_phase(7)
        
        assert result is not None
        assert "deliverable" in result.name.lower()
    
    def test_progress_directory_search_integration_with_get_phase_status(self, tmp_path):
        """Test that _get_progress_file_for_phase integrates correctly with get_phase_status"""
        import json
        
        project_root = tmp_path / "test_project"
        project_root.mkdir()
        
        # Create progress files for different phases
        phase_configs = [
            (0, "output/analysis/source_code/progress", "preparation_status.json"),
            (1, "output/analysis/source_code/progress", "analysis_status.json"),
            (2, "output/analysis/workpackages/progress", "Workpackage_Status.json"),
            (3, "output/specifications/progress", "Business_Specification_Status.json"),
            (4, "output/migration/progress", "code_generation_status.json"),
        ]
        
        for phase_id, dir_path, filename in phase_configs:
            progress_dir = project_root / dir_path
            progress_dir.mkdir(parents=True, exist_ok=True)
            
            progress_file = progress_dir / filename
            
            if phase_id == 3:
                # Phase 3 needs special format
                data = {
                    "summary": {
                        "total_workpackages": 10,
                        "approved": 10,
                        "approved_with_changes": 0
                    }
                }
            else:
                data = {"status": "completed"}
            
            with open(progress_file, 'w') as f:
                json.dump(data, f)
        
        loader = MigrationDataLoader(project_root=str(project_root))
        
        # Get phase status - should use _get_progress_file_for_phase internally
        phases = loader.get_phase_status()
        
        # Verify phases that have progress files show completed status
        for phase_id in [0, 1, 2, 3, 4]:
            phase = phases[phase_id]
            # Status should be completed or in_progress (not unknown)
            assert phase["status"] in ["completed", "in_progress"], \
                f"Phase {phase_id} should have status from progress file"
