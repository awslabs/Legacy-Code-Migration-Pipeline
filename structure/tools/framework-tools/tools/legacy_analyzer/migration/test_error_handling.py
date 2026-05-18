"""
Tests for Migration Flow Error Handling

This module tests error handling and validation for migration flow export.
Tests cover:
- Custom exception classes
- Flow data validation
- Missing entry point handling
- Missing complexity data handling
- Missing dependency handling
- Incomplete data warnings
"""

import pytest
import sqlite3
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock

from .exceptions import FlowValidationError, MissingDataError, ExportError
from .flow_builder import MigrationFlowBuilder, generate_flow_id
from .flow_exporter import MigrationFlowExporter
from .schema import create_migration_flow_schema


class TestExceptionClasses:
    """Test custom exception classes."""
    
    def test_flow_validation_error_basic(self):
        """Test FlowValidationError with basic message."""
        error = FlowValidationError("Invalid flow data")
        assert str(error) == "Invalid flow data"
        assert error.flow_id is None
        assert error.details == {}
    
    def test_flow_validation_error_with_flow_id(self):
        """Test FlowValidationError with flow ID."""
        error = FlowValidationError("Invalid flow data", flow_id="FLOW_TEST")
        assert "[FLOW_TEST]" in str(error)
        assert error.flow_id == "FLOW_TEST"
    
    def test_flow_validation_error_with_details(self):
        """Test FlowValidationError with details."""
        details = {'field': 'programs', 'expected': 'list', 'actual': 'dict'}
        error = FlowValidationError("Invalid type", flow_id="FLOW_TEST", details=details)
        assert error.details == details
    
    def test_missing_data_error_basic(self):
        """Test MissingDataError with basic message."""
        error = MissingDataError("Data not found")
        assert str(error) == "Data not found"
        assert error.data_type is None
        assert error.artifact_name is None
    
    def test_missing_data_error_with_type(self):
        """Test MissingDataError with data type."""
        error = MissingDataError("Not found", data_type="complexity")
        assert "Missing complexity" in str(error)
        assert error.data_type == "complexity"
    
    def test_missing_data_error_with_artifact(self):
        """Test MissingDataError with artifact name."""
        error = MissingDataError(
            "Not found",
            data_type="complexity",
            artifact_name="PROG1"
        )
        assert "Missing complexity for PROG1" in str(error)
        assert error.artifact_name == "PROG1"
    
    def test_export_error_basic(self):
        """Test ExportError with basic message."""
        error = ExportError("Export failed")
        assert str(error) == "Export failed"
        assert error.operation is None
        assert error.cause is None
    
    def test_export_error_with_operation(self):
        """Test ExportError with operation."""
        error = ExportError("Failed", operation="query")
        assert "Export failed during query" in str(error)
        assert error.operation == "query"
    
    def test_export_error_with_cause(self):
        """Test ExportError with underlying cause."""
        cause = ValueError("Invalid value")
        error = ExportError("Failed", operation="format", cause=cause)
        assert "ValueError" in str(error)
        assert error.cause == cause


class TestFlowIDGeneration:
    """Test flow ID generation with error handling."""
    
    def test_generate_flow_id_empty_program(self):
        """Test that empty program name raises ValueError."""
        with pytest.raises(ValueError, match="program_name cannot be empty"):
            generate_flow_id("")
    
    def test_generate_flow_id_none_program(self):
        """Test that None program name raises ValueError."""
        with pytest.raises(ValueError, match="program_name cannot be empty"):
            generate_flow_id(None)
    
    def test_generate_flow_id_special_chars_only(self):
        """Test that program with only special chars raises ValueError."""
        with pytest.raises(ValueError, match="resulted in empty flow ID"):
            generate_flow_id("###")
    
    def test_generate_flow_id_valid(self):
        """Test valid flow ID generation."""
        flow_id = generate_flow_id("PAYROLL1")
        assert flow_id == "FLOW_PAYROLL1"


class TestFlowDataValidation:
    """Test flow data validation."""
    
    @pytest.fixture
    def db_connection(self):
        """Create in-memory database with schema."""
        conn = sqlite3.connect(':memory:')
        create_migration_flow_schema(conn)
        yield conn
        conn.close()
    
    @pytest.fixture
    def flow_builder(self, db_connection):
        """Create MigrationFlowBuilder instance."""
        with patch.object(MigrationFlowBuilder, '_load_dependencies', return_value=[]):
            builder = MigrationFlowBuilder(db_connection)
            return builder
    
    def test_validate_empty_flow_id(self, flow_builder):
        """Test validation fails for empty flow ID."""
        with pytest.raises(FlowValidationError, match="Flow ID cannot be empty"):
            flow_builder._validate_flow_data(
                flow_id="",
                entry_program="PROG1",
                primary_type="JCL",
                entry_types=[],
                scope={'programs': [], 'copybooks': [], 'datasets': []},
                interfaces={'inbound': [], 'outbound': []},
                data_operations={'databases': [], 'datasets': []},
                complexity={'totalPrograms': 0, 'totalLines': 0, 
                           'cyclomaticComplexity': 0, 'compositeScore': 0.0, 'tier': 'LOW'},
                dependencies={'requiredFlows': [], 'dependentFlows': []}
            )
    
    def test_validate_invalid_flow_id_format(self, flow_builder):
        """Test validation fails for invalid flow ID format."""
        with pytest.raises(FlowValidationError, match="must start with 'FLOW_'"):
            flow_builder._validate_flow_data(
                flow_id="INVALID_ID",
                entry_program="PROG1",
                primary_type="JCL",
                entry_types=[],
                scope={'programs': [], 'copybooks': [], 'datasets': []},
                interfaces={'inbound': [], 'outbound': []},
                data_operations={'databases': [], 'datasets': []},
                complexity={'totalPrograms': 0, 'totalLines': 0,
                           'cyclomaticComplexity': 0, 'compositeScore': 0.0, 'tier': 'LOW'},
                dependencies={'requiredFlows': [], 'dependentFlows': []}
            )
    
    def test_validate_empty_entry_program(self, flow_builder):
        """Test validation fails for empty entry program."""
        with pytest.raises(FlowValidationError, match="Entry program cannot be empty"):
            flow_builder._validate_flow_data(
                flow_id="FLOW_TEST",
                entry_program="",
                primary_type="JCL",
                entry_types=[],
                scope={'programs': [], 'copybooks': [], 'datasets': []},
                interfaces={'inbound': [], 'outbound': []},
                data_operations={'databases': [], 'datasets': []},
                complexity={'totalPrograms': 0, 'totalLines': 0,
                           'cyclomaticComplexity': 0, 'compositeScore': 0.0, 'tier': 'LOW'},
                dependencies={'requiredFlows': [], 'dependentFlows': []}
            )
    
    def test_validate_invalid_entry_types_type(self, flow_builder):
        """Test validation fails for invalid entry types type."""
        with pytest.raises(FlowValidationError, match="Entry types must be a list"):
            flow_builder._validate_flow_data(
                flow_id="FLOW_TEST",
                entry_program="PROG1",
                primary_type="JCL",
                entry_types="not a list",  # Invalid type
                scope={'programs': [], 'copybooks': [], 'datasets': []},
                interfaces={'inbound': [], 'outbound': []},
                data_operations={'databases': [], 'datasets': []},
                complexity={'totalPrograms': 0, 'totalLines': 0,
                           'cyclomaticComplexity': 0, 'compositeScore': 0.0, 'tier': 'LOW'},
                dependencies={'requiredFlows': [], 'dependentFlows': []}
            )
    
    def test_validate_entry_type_missing_type_field(self, flow_builder):
        """Test validation fails for entry type missing 'type' field."""
        with pytest.raises(FlowValidationError, match="missing 'type' field"):
            flow_builder._validate_flow_data(
                flow_id="FLOW_TEST",
                entry_program="PROG1",
                primary_type="JCL",
                entry_types=[{'callers': []}],  # Missing 'type' field
                scope={'programs': [], 'copybooks': [], 'datasets': []},
                interfaces={'inbound': [], 'outbound': []},
                data_operations={'databases': [], 'datasets': []},
                complexity={'totalPrograms': 0, 'totalLines': 0,
                           'cyclomaticComplexity': 0, 'compositeScore': 0.0, 'tier': 'LOW'},
                dependencies={'requiredFlows': [], 'dependentFlows': []}
            )
    
    def test_validate_invalid_scope_type(self, flow_builder):
        """Test validation fails for invalid scope type."""
        with pytest.raises(FlowValidationError, match="Scope must be a dictionary"):
            flow_builder._validate_flow_data(
                flow_id="FLOW_TEST",
                entry_program="PROG1",
                primary_type="JCL",
                entry_types=[],
                scope="not a dict",  # Invalid type
                interfaces={'inbound': [], 'outbound': []},
                data_operations={'databases': [], 'datasets': []},
                complexity={'totalPrograms': 0, 'totalLines': 0,
                           'cyclomaticComplexity': 0, 'compositeScore': 0.0, 'tier': 'LOW'},
                dependencies={'requiredFlows': [], 'dependentFlows': []}
            )
    
    def test_validate_scope_missing_programs(self, flow_builder):
        """Test validation fails for scope missing 'programs' key."""
        with pytest.raises(FlowValidationError, match="Scope missing required key: programs"):
            flow_builder._validate_flow_data(
                flow_id="FLOW_TEST",
                entry_program="PROG1",
                primary_type="JCL",
                entry_types=[],
                scope={'copybooks': [], 'datasets': []},  # Missing 'programs'
                interfaces={'inbound': [], 'outbound': []},
                data_operations={'databases': [], 'datasets': []},
                complexity={'totalPrograms': 0, 'totalLines': 0,
                           'cyclomaticComplexity': 0, 'compositeScore': 0.0, 'tier': 'LOW'},
                dependencies={'requiredFlows': [], 'dependentFlows': []}
            )
    
    def test_validate_invalid_complexity_tier(self, flow_builder):
        """Test validation fails for invalid complexity tier."""
        with pytest.raises(FlowValidationError, match="Invalid complexity tier"):
            flow_builder._validate_flow_data(
                flow_id="FLOW_TEST",
                entry_program="PROG1",
                primary_type="JCL",
                entry_types=[],
                scope={'programs': [], 'copybooks': [], 'datasets': []},
                interfaces={'inbound': [], 'outbound': []},
                data_operations={'databases': [], 'datasets': []},
                complexity={'totalPrograms': 0, 'totalLines': 0,
                           'cyclomaticComplexity': 0, 'compositeScore': 0.0, 
                           'tier': 'INVALID'},  # Invalid tier
                dependencies={'requiredFlows': [], 'dependentFlows': []}
            )
    
    def test_validate_valid_flow_data(self, flow_builder):
        """Test validation passes for valid flow data."""
        # Should not raise any exception
        flow_builder._validate_flow_data(
            flow_id="FLOW_TEST",
            entry_program="PROG1",
            primary_type="JCL",
            entry_types=[
                {'type': 'JCL', 'callers': [{'source': 'JOB1', 'metadata': {}}]}
            ],
            scope={'programs': ['PROG1'], 'copybooks': [], 'datasets': []},
            interfaces={'inbound': [], 'outbound': []},
            data_operations={'databases': [], 'datasets': []},
            complexity={'totalPrograms': 1, 'totalLines': 100,
                       'cyclomaticComplexity': 10, 'compositeScore': 25.0, 'tier': 'LOW'},
            dependencies={'requiredFlows': [], 'dependentFlows': []}
        )


class TestMissingEntryPointHandling:
    """Test handling of missing entry points."""
    
    @pytest.fixture
    def db_connection(self):
        """Create in-memory database with schema."""
        conn = sqlite3.connect(':memory:')
        create_migration_flow_schema(conn)
        yield conn
        conn.close()
    
    def test_build_flow_empty_entry_program(self, db_connection):
        """Test that empty entry program raises ValueError."""
        with patch.object(MigrationFlowBuilder, '_load_dependencies', return_value=[]):
            builder = MigrationFlowBuilder(db_connection)
            
            with pytest.raises(ValueError, match="entry_program cannot be empty"):
                builder.build_flow("")
    
    def test_build_flow_missing_flow_data(self, db_connection):
        """Test that missing flow data raises MissingDataError."""
        with patch.object(MigrationFlowBuilder, '_load_dependencies', return_value=[]):
            builder = MigrationFlowBuilder(db_connection)
            
            # Mock flow_analyzer to raise exception
            builder.flow_analyzer = Mock()
            builder.flow_analyzer.analyze_flow.side_effect = Exception("Flow not found")
            
            with pytest.raises(MissingDataError, match="Failed to analyze flow"):
                builder.build_flow("NONEXISTENT")


class TestMissingComplexityHandling:
    """Test handling of missing complexity data."""
    
    @pytest.fixture
    def db_connection(self):
        """Create in-memory database with schema."""
        conn = sqlite3.connect(':memory:')
        create_migration_flow_schema(conn)
        yield conn
        conn.close()
    
    def test_calculate_complexity_no_data(self, db_connection):
        """Test complexity calculation with no data returns UNKNOWN tier."""
        with patch.object(MigrationFlowBuilder, '_load_dependencies', return_value=[]):
            builder = MigrationFlowBuilder(db_connection)
            
            complexity = builder.calculate_flow_complexity(['PROG1', 'PROG2'])
            
            assert complexity['tier'] == 'UNKNOWN'
            assert complexity['totalPrograms'] == 2
            assert complexity['totalLines'] == 0
            assert complexity['cyclomaticComplexity'] == 0
            assert complexity['compositeScore'] == 0.0


class TestIncompleteDataWarnings:
    """Test warnings for incomplete data."""
    
    @pytest.fixture
    def db_connection(self):
        """Create in-memory database with schema."""
        conn = sqlite3.connect(':memory:')
        create_migration_flow_schema(conn)
        yield conn
        conn.close()
    
    @pytest.fixture
    def exporter(self, db_connection):
        """Create MigrationFlowExporter instance."""
        return MigrationFlowExporter(db_connection)
    
    def test_is_incomplete_flow_no_entry_types(self, exporter):
        """Test flow is incomplete with no entry types."""
        flow_data = {
            'flowId': 'FLOW_TEST',
            'entryPoint': {'types': []},
            'scope': {'programs': ['PROG1']},
            'complexity': {'tier': 'LOW'},
            'dataOperations': {'databases': [], 'datasets': []}
        }
        
        assert exporter._is_incomplete_flow(flow_data) is True
    
    def test_is_incomplete_flow_no_programs(self, exporter):
        """Test flow is incomplete with no programs."""
        flow_data = {
            'flowId': 'FLOW_TEST',
            'entryPoint': {'types': [{'type': 'JCL'}]},
            'scope': {'programs': []},
            'complexity': {'tier': 'LOW'},
            'dataOperations': {'databases': [], 'datasets': []}
        }
        
        assert exporter._is_incomplete_flow(flow_data) is True
    
    def test_is_incomplete_flow_unknown_complexity(self, exporter):
        """Test flow is incomplete with UNKNOWN complexity."""
        flow_data = {
            'flowId': 'FLOW_TEST',
            'entryPoint': {'types': [{'type': 'JCL'}]},
            'scope': {'programs': ['PROG1']},
            'complexity': {'tier': 'UNKNOWN'},
            'dataOperations': {'databases': [], 'datasets': []}
        }
        
        assert exporter._is_incomplete_flow(flow_data) is True
    
    def test_is_incomplete_flow_no_data_operations(self, exporter):
        """Test flow is incomplete with no data operations."""
        flow_data = {
            'flowId': 'FLOW_TEST',
            'entryPoint': {'types': [{'type': 'JCL'}]},
            'scope': {'programs': ['PROG1']},
            'complexity': {'tier': 'LOW'},
            'dataOperations': {'databases': [], 'datasets': []}
        }
        
        assert exporter._is_incomplete_flow(flow_data) is True
    
    def test_is_complete_flow(self, exporter):
        """Test flow is complete with all data."""
        flow_data = {
            'flowId': 'FLOW_TEST',
            'entryPoint': {'types': [{'type': 'JCL'}]},
            'scope': {'programs': ['PROG1']},
            'complexity': {'tier': 'LOW'},
            'dataOperations': {
                'databases': [{'type': 'DB2', 'operation': 'SELECT'}],
                'datasets': []
            }
        }
        
        assert exporter._is_incomplete_flow(flow_data) is False


class TestExportErrorHandling:
    """Test export error handling."""
    
    @pytest.fixture
    def db_connection(self):
        """Create in-memory database with schema."""
        conn = sqlite3.connect(':memory:')
        create_migration_flow_schema(conn)
        yield conn
        conn.close()
    
    @pytest.fixture
    def exporter(self, db_connection):
        """Create MigrationFlowExporter instance."""
        return MigrationFlowExporter(db_connection)
    
    def test_export_flows_file_write_error(self, exporter):
        """Test export raises ExportError on file write failure."""
        # Mock _query_flow to return valid data
        exporter._query_flow = Mock(return_value={
            'flowId': 'FLOW_TEST',
            'entryPoint': {'types': []},
            'scope': {'programs': []},
            'complexity': {'tier': 'UNKNOWN'},
            'dataOperations': {'databases': [], 'datasets': []}
        })
        
        # Try to write to invalid path
        with pytest.raises(ExportError, match="Failed to write to file"):
            exporter.export_flows(['FLOW_TEST'], output_file='/invalid/path/file.json')
    
    def test_export_flows_format_error(self, exporter):
        """Test export raises ExportError on format failure."""
        # Mock _query_flow to return data
        exporter._query_flow = Mock(return_value={'flowId': 'FLOW_TEST'})
        
        # Mock _format_json to raise exception
        exporter._format_json = Mock(side_effect=Exception("Format error"))
        
        with pytest.raises(ExportError, match="Failed to format flows as JSON"):
            exporter.export_flows(['FLOW_TEST'])


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
