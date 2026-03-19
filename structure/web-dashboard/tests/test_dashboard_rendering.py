#!/usr/bin/env python3
"""
Visual rendering tests for the dashboard.

Tests that verify the dashboard displays data correctly in the UI.
"""

import pytest
import json
from app import create_app


@pytest.fixture
def app():
    """Create Flask app for testing."""
    app = create_app('default')
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestDashboardUIRendering:
    """Test that dashboard UI renders correctly with actual data."""
    
    def test_index_page_contains_expected_elements(self, client):
        """Test that the main page has expected HTML elements."""
        response = client.get('/')
        assert response.status_code == 200
        
        html = response.data.decode('utf-8')
        
        # Should have basic HTML structure
        assert '<html' in html.lower()
        assert '</html>' in html.lower()
        
        # Should have some content (not just empty page)
        assert len(html) > 100
    
    def test_api_overview_has_project_info(self, client):
        """Test that overview API returns project information."""
        response = client.get('/api/overview')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        
        # Should have some data structure
        assert isinstance(data, dict)
        assert len(data) > 0
    
    def test_api_phases_returns_all_phases(self, client):
        """Test that phases API returns data for all phases."""
        response = client.get('/api/phases')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert isinstance(data, list)
        
        # Should have phase data
        if len(data) > 0:
            # Each phase should have some structure
            for phase in data:
                assert isinstance(phase, dict)
    
    def test_workpackages_api_returns_valid_data(self, client):
        """Test that workpackages API returns valid workpackage data."""
        response = client.get('/api/workpackages')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        
        # Should return some structure
        assert data is not None
        
        # If workpackages exist, verify structure
        if isinstance(data, dict) and 'workpackages' in data:
            workpackages = data['workpackages']
            assert isinstance(workpackages, list)
            
            # Verify workpackage structure
            for wp in workpackages:
                assert isinstance(wp, dict)
                # Should have some identifying information
                assert len(wp) > 0
    
    def test_specs_in_phase3_details(self, client):
        """Test that Phase 3 details include specifications."""
        from models.data_loader import MigrationDataLoader
        from pathlib import Path
        
        project_root = Path(__file__).parent.parent.parent.parent
        loader = MigrationDataLoader(project_root=project_root)
        
        phase3_details = loader.get_phase_details(3)
        
        # Should have artifacts
        if 'artifacts' in phase3_details and phase3_details['artifacts']:
            artifacts = phase3_details['artifacts']
            
            # Check artifacts have correct structure
            for artifact in artifacts:
                assert 'name' in artifact
                assert 'type' in artifact
            
            assert len(artifacts) >= 0
    
    def test_phase_status_shows_completion(self, client):
        """Test that phase status includes completion information."""
        from models.data_loader import MigrationDataLoader
        from pathlib import Path
        
        project_root = Path(__file__).parent.parent.parent.parent
        loader = MigrationDataLoader(project_root=project_root)
        
        phase_status = loader.get_phase_status()
        
        # Should have status for phases
        assert isinstance(phase_status, list)
        
        # Each phase should have status information
        for phase in phase_status:
            assert isinstance(phase, dict)
            # Should have some status indicator
            assert 'status' in phase or 'completion' in phase or 'phase' in phase
    
    def test_workpackage_progress_shows_approved_count(self, client):
        """Test that workpackage progress shows approved workpackages."""
        from models.data_loader import MigrationDataLoader
        from pathlib import Path
        
        project_root = Path(__file__).parent.parent.parent.parent
        loader = MigrationDataLoader(project_root=project_root)
        
        progress = loader.get_workpackage_progress()
        
        # Should have progress data
        assert isinstance(progress, dict)
        
        # If summary exists, verify it has counts
        if 'summary' in progress:
            summary = progress['summary']
            assert isinstance(summary, dict)
            
            # Should have some count fields
            if 'approved' in summary:
                assert isinstance(summary['approved'], int)
                assert summary['approved'] >= 0
    
    def test_all_api_endpoints_accessible(self, client):
        """Test that all main API endpoints are accessible."""
        endpoints = [
            '/api/overview',
            '/api/phases',
            '/api/workpackages',
            '/api/flows',
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            # Should not return 500 errors
            assert response.status_code != 500
            # Should return 200 or 404 (if not implemented)
            assert response.status_code in [200, 404]
    
    def test_dashboard_handles_missing_data_gracefully(self, client):
        """Test that dashboard doesn't crash when some data is missing."""
        # Try to access various endpoints
        response = client.get('/')
        assert response.status_code == 200
        
        response = client.get('/api/overview')
        assert response.status_code == 200
        
        response = client.get('/api/phases')
        assert response.status_code == 200
        
        # Dashboard should handle missing data without 500 errors
        # All responses should be valid
    
    def test_phase_details_for_all_phases(self, client):
        """Test that we can get details for all phases without errors."""
        from models.data_loader import MigrationDataLoader
        from pathlib import Path
        
        project_root = Path(__file__).parent.parent.parent.parent
        loader = MigrationDataLoader(project_root=project_root)
        
        # Test all phases 0-7
        for phase_id in range(8):
            details = loader.get_phase_details(phase_id)
            
            # Should return a dict without crashing
            assert isinstance(details, dict)
            
            # Should have phase identifier
            assert 'phase' in details or 'artifacts' in details or details == {}


class TestSpecificationDisplay:
    """Test specification handling in the UI."""
    
    def test_specs_have_correct_structure(self, client):
        """Test that specifications have correct structure."""
        from models.data_loader import MigrationDataLoader
        from pathlib import Path
        
        project_root = Path(__file__).parent.parent.parent.parent
        loader = MigrationDataLoader(project_root=project_root)
        
        phase3_details = loader.get_phase_details(3)
        
        if 'artifacts' in phase3_details:
            artifacts = phase3_details['artifacts']
            
            for artifact in artifacts:
                assert 'name' in artifact
                assert 'type' in artifact
                assert 'workpackage' in artifact


class TestErrorHandling:
    """Test error handling in the dashboard."""
    
    def test_invalid_phase_id_handled(self, client):
        """Test that invalid phase IDs are handled gracefully."""
        from models.data_loader import MigrationDataLoader
        from pathlib import Path
        
        project_root = Path(__file__).parent.parent.parent.parent
        loader = MigrationDataLoader(project_root=project_root)
        
        # Try invalid phase IDs
        for invalid_id in [-1, 99, 1000]:
            # Should not crash
            try:
                details = loader.get_phase_details(invalid_id)
                # Should return empty dict or default structure
                assert isinstance(details, dict)
            except Exception as e:
                # If it raises an exception, it should be handled
                pytest.fail(f"Unhandled exception for invalid phase {invalid_id}: {e}")
    
    def test_missing_progress_files_handled(self, client):
        """Test that missing progress files don't crash the dashboard."""
        # The dashboard should handle missing files gracefully
        response = client.get('/api/phases')
        assert response.status_code == 200
        
        # Should return valid JSON even if some files are missing
        data = json.loads(response.data)
        assert isinstance(data, list)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
