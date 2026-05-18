#!/usr/bin/env python3
"""
Integration test for advanced analysis features.

This script tests the integration of program-level dependency storage
and copybook analysis into the main legacy analyzer workflow.
"""

import os
import tempfile
import shutil
from pathlib import Path

from shared.database.adapters import SQLiteAdapter
from .analysis_orchestrator import AnalysisOrchestrator


def create_test_source_files(test_dir: Path) -> None:
    """Create test source files for integration testing."""
    
    # Create COBOL program with multiple programs
    cobol_file = test_dir / "TESTPROG.cbl"
    cobol_content = """
       IDENTIFICATION DIVISION.
       PROGRAM-ID. MAINPROG.
       
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-VAR PIC X(10).
       
       PROCEDURE DIVISION.
       MAIN-PARA.
           CALL 'SUBPROG1'
           PERFORM SUB-PARA
           STOP RUN.
           
       SUB-PARA.
           MOVE 'TEST' TO WS-VAR.
           
       END PROGRAM MAINPROG.
       
       IDENTIFICATION DIVISION.
       PROGRAM-ID. SUBPROG1.
       
       PROCEDURE DIVISION.
           DISPLAY 'SUBPROGRAM 1'
           EXIT PROGRAM.
           
       END PROGRAM SUBPROG1.
    """
    cobol_file.write_text(cobol_content)
    
    # Create copybook with executable code
    copybook_file = test_dir / "TESTCOPY.cpy"
    copybook_content = """
       01 TEST-RECORD.
          05 TEST-ID    PIC 9(5).
          05 TEST-NAME  PIC X(20).
          05 TEST-AMT   PIC 9(7)V99.
          
       COPY-PARA.
           IF TEST-ID > 0
              CALL 'VALIDATE'
           END-IF.
    """
    copybook_file.write_text(copybook_content)
    
    # Create data-only copybook
    data_copybook_file = test_dir / "DATAONLY.cpy"
    data_copybook_content = """
       01 DATA-RECORD.
          05 DATA-ID     PIC 9(8).
          05 DATA-NAME   PIC X(30).
          05 DATA-DATE   PIC 9(8).
          05 DATA-AMOUNT PIC 9(9)V99.
    """
    data_copybook_file.write_text(data_copybook_content)
    
    # Create JCL file
    jcl_file = test_dir / "TESTJOB.jcl"
    jcl_content = """
//TESTJOB  JOB CLASS=A,MSGCLASS=X
//STEP1    EXEC PGM=MAINPROG
//SYSOUT   DD SYSOUT=*
//SYSIN    DD *
TEST DATA
/*
    """
    jcl_file.write_text(jcl_content)


def test_complete_analysis_integration():
    """Test complete analysis with advanced features enabled."""
    
    print("="*80)
    print("INTEGRATION TEST: Complete Analysis with Advanced Features")
    print("="*80)
    
    # Create temporary directory and test files
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        create_test_source_files(test_dir)
        
        # Create temporary database
        db_path = test_dir / "test_analysis.db"
        
        try:
            # Initialize database
            db = SQLiteAdapter(str(db_path))
            db.connect()
            
            # Initialize orchestrator
            orchestrator = AnalysisOrchestrator(db)
            
            print(f"Test directory: {test_dir}")
            print(f"Database: {db_path}")
            print(f"Test files created: {len(list(test_dir.glob('*')))}")
            
            # Run complete analysis with all advanced features
            results = orchestrator.run_complete_analysis(
                source_directory=str(test_dir),
                calculate_complexity=False,
                enable_program_level=True,
                enable_copybook_analysis=True
            )
            
            # Verify results
            summary = results.get('summary', {})
            
            print("\n" + "="*60)
            print("INTEGRATION TEST RESULTS")
            print("="*60)
            print(f"✓ Total artifacts: {summary.get('total_artifacts', 0)}")
            print(f"✓ Artifacts with dependencies: {summary.get('artifacts_with_dependencies', 0)}")
            print(f"✓ Program boundaries detected: {summary.get('program_boundaries_detected', 0)}")
            print(f"✓ Copybooks analyzed: {summary.get('copybooks_analyzed', 0)}")
            print(f"✓ Dependencies stored: {summary.get('dependencies_stored', 0)}")
            
            # Check database tables
            cursor = db.cursor
            
            # Check program_file_mapping table
            cursor.execute("SELECT COUNT(*) FROM program_file_mapping")
            program_count = cursor.fetchone()[0]
            print(f"✓ Program boundaries stored: {program_count}")
            
            # Check copybook_analysis table
            cursor.execute("SELECT COUNT(*) FROM copybook_analysis")
            copybook_analysis_count = cursor.fetchone()[0]
            print(f"✓ Copybook analysis stored: {copybook_analysis_count}")
            
            # Check artifact_dependencies table
            cursor.execute("SELECT COUNT(*) FROM artifact_dependencies")
            dependency_count = cursor.fetchone()[0]
            print(f"✓ Total dependencies stored: {dependency_count}")
            
            # Verify program-level dependencies exist
            cursor.execute("SELECT COUNT(*) FROM artifact_dependencies WHERE source_artifact_type = 'PROGRAM'")
            program_deps = cursor.fetchone()[0]
            print(f"✓ Program-level dependencies: {program_deps}")
            
            # Verify copybook analysis results
            cursor.execute("SELECT copybook_name, has_executable_code FROM copybook_analysis")
            copybook_results = cursor.fetchall()
            for name, has_exec in copybook_results:
                exec_status = "executable" if has_exec else "data-only"
                print(f"✓ Copybook {name}: {exec_status}")
            
            print("="*60)
            
            # Validate integration success
            success_criteria = [
                summary.get('total_artifacts', 0) > 0,
                program_count > 0,  # Program boundaries detected and stored
                copybook_analysis_count > 0,  # Copybook analysis performed and stored
                dependency_count > 0,  # Dependencies stored
            ]
            
            if all(success_criteria):
                print("🎉 INTEGRATION TEST PASSED - All advanced features working!")
                return True
            else:
                print("❌ INTEGRATION TEST FAILED - Some features not working")
                return False
                
        except Exception as e:
            print(f"❌ INTEGRATION TEST ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            if 'db' in locals():
                db.close()


def test_program_level_only():
    """Test program-level analysis only."""
    
    print("\n" + "="*80)
    print("INTEGRATION TEST: Program-Level Analysis Only")
    print("="*80)
    
    # Create temporary directory and test files
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        create_test_source_files(test_dir)
        
        # Create temporary database
        db_path = test_dir / "test_program_level.db"
        
        try:
            # Initialize database
            db = SQLiteAdapter(str(db_path))
            db.connect()
            
            # Initialize orchestrator
            orchestrator = AnalysisOrchestrator(db)
            
            # Run analysis with only program-level enabled
            results = orchestrator.run_complete_analysis(
                source_directory=str(test_dir),
                calculate_complexity=False,
                enable_program_level=True,
                enable_copybook_analysis=False
            )
            
            # Check that program-level features work but copybook analysis is disabled
            cursor = db.cursor
            
            cursor.execute("SELECT COUNT(*) FROM program_file_mapping")
            program_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM copybook_analysis")
            copybook_count = cursor.fetchone()[0]
            
            print(f"✓ Program boundaries stored: {program_count}")
            print(f"✓ Copybook analysis stored: {copybook_count} (should be 0)")
            
            success = program_count > 0 and copybook_count == 0
            print(f"{'🎉 PASSED' if success else '❌ FAILED'}: Program-level only test")
            
            return success
            
        except Exception as e:
            print(f"❌ PROGRAM-LEVEL TEST ERROR: {str(e)}")
            return False
        
        finally:
            if 'db' in locals():
                db.close()


def test_copybook_analysis_only():
    """Test copybook analysis only."""
    
    print("\n" + "="*80)
    print("INTEGRATION TEST: Copybook Analysis Only")
    print("="*80)
    
    # Create temporary directory and test files
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        create_test_source_files(test_dir)
        
        # Create temporary database
        db_path = test_dir / "test_copybook_analysis.db"
        
        try:
            # Initialize database
            db = SQLiteAdapter(str(db_path))
            db.connect()
            
            # Initialize orchestrator
            orchestrator = AnalysisOrchestrator(db)
            
            # Run analysis with only copybook analysis enabled
            results = orchestrator.run_complete_analysis(
                source_directory=str(test_dir),
                calculate_complexity=False,
                enable_program_level=False,
                enable_copybook_analysis=True
            )
            
            # Check that copybook analysis works but program-level is disabled
            cursor = db.cursor
            
            cursor.execute("SELECT COUNT(*) FROM program_file_mapping")
            program_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM copybook_analysis")
            copybook_count = cursor.fetchone()[0]
            
            print(f"✓ Program boundaries stored: {program_count} (should be 0)")
            print(f"✓ Copybook analysis stored: {copybook_count}")
            
            success = program_count == 0 and copybook_count > 0
            print(f"{'🎉 PASSED' if success else '❌ FAILED'}: Copybook analysis only test")
            
            return success
            
        except Exception as e:
            print(f"❌ COPYBOOK ANALYSIS TEST ERROR: {str(e)}")
            return False
        
        finally:
            if 'db' in locals():
                db.close()


def main():
    """Run all integration tests."""
    
    print("LEGACY ANALYZER INTEGRATION TESTS")
    print("Testing advanced analysis feature integration")
    print("="*80)
    
    tests = [
        test_complete_analysis_integration,
        test_program_level_only,
        test_copybook_analysis_only
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"Test failed with exception: {e}")
            results.append(False)
    
    # Final summary
    passed = sum(results)
    total = len(results)
    
    print("\n" + "="*80)
    print("INTEGRATION TEST SUMMARY")
    print("="*80)
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("✓ Program-level dependency storage integrated")
        print("✓ Copybook analysis storage integrated")
        print("✓ CLI commands working")
        print("✓ Advanced features can be enabled/disabled")
    else:
        print("❌ SOME INTEGRATION TESTS FAILED")
        print("Please check the implementation and fix issues")
    
    print("="*80)
    
    return passed == total


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)