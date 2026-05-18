"""Database operations for program flow analysis."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from ..models.flow import ProgramFlow
from ..models.dependency import CircularDependency


class FlowDatabase:
    """Manages database operations for program flows."""
    
    def __init__(self, db_connection):
        """
        Initialize flow database manager.
        
        Args:
            db_connection: Database connection object (e.g., sqlite3.Connection)
        """
        self.conn = db_connection
        self.cursor = db_connection.cursor()
    
    def create_schema(self) -> None:
        """Create database tables for program flows."""
        
        # Create program_flows table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS program_flows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_program VARCHAR(44) NOT NULL,
                depth INTEGER NOT NULL,
                total_programs INTEGER NOT NULL,
                total_copybooks INTEGER DEFAULT 0,
                total_datasets INTEGER DEFAULT 0,
                has_circular_deps BOOLEAN DEFAULT 0,
                analyzed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(start_program)
            )
        """)
        
        # Create flow_programs table (programs in each flow)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS flow_programs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                flow_id INTEGER NOT NULL,
                program_name VARCHAR(44) NOT NULL,
                depth_level INTEGER,
                FOREIGN KEY (flow_id) REFERENCES program_flows(id) ON DELETE CASCADE
            )
        """)
        
        # Create flow_circular_deps table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS flow_circular_deps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                flow_id INTEGER NOT NULL,
                cycle_artifacts TEXT NOT NULL,
                cycle_dep_types TEXT NOT NULL,
                FOREIGN KEY (flow_id) REFERENCES program_flows(id) ON DELETE CASCADE
            )
        """)
        
        # Create indexes for performance
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_flow_start_program 
            ON program_flows(start_program)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_flow_programs_flow_id 
            ON flow_programs(flow_id)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_flow_programs_name 
            ON flow_programs(program_name)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_flow_circular_flow_id 
            ON flow_circular_deps(flow_id)
        """)
        
        self.conn.commit()
    
    def save_flow(self, flow: ProgramFlow) -> int:
        """
        Save a program flow to the database.
        
        Args:
            flow: ProgramFlow object to save
            
        Returns:
            Flow ID
        """
        # Check if flow already exists
        self.cursor.execute(
            "SELECT id FROM program_flows WHERE start_program = ?",
            (flow.start_program,)
        )
        existing = self.cursor.fetchone()
        
        if existing:
            # Update existing flow
            flow_id = existing[0]
            self.cursor.execute("""
                UPDATE program_flows
                SET depth = ?,
                    total_programs = ?,
                    total_copybooks = ?,
                    total_datasets = ?,
                    has_circular_deps = ?,
                    analyzed_date = ?
                WHERE id = ?
            """, (
                flow.depth,
                flow.total_programs,
                flow.total_copybooks,
                flow.total_datasets,
                1 if flow.has_circular_dependencies() else 0,
                datetime.now(),
                flow_id
            ))
            
            # Delete old flow_programs and circular_deps
            self.cursor.execute("DELETE FROM flow_programs WHERE flow_id = ?", (flow_id,))
            self.cursor.execute("DELETE FROM flow_circular_deps WHERE flow_id = ?", (flow_id,))
        else:
            # Insert new flow
            self.cursor.execute("""
                INSERT INTO program_flows (
                    start_program, depth, total_programs, total_copybooks,
                    total_datasets, has_circular_deps, analyzed_date
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                flow.start_program,
                flow.depth,
                flow.total_programs,
                flow.total_copybooks,
                flow.total_datasets,
                1 if flow.has_circular_dependencies() else 0,
                datetime.now()
            ))
            flow_id = self.cursor.lastrowid
        
        # Insert flow programs
        for program in flow.programs:
            self.cursor.execute("""
                INSERT INTO flow_programs (flow_id, program_name, depth_level)
                VALUES (?, ?, ?)
            """, (flow_id, program, None))  # depth_level can be calculated later
        
        # Insert circular dependencies
        for cycle in flow.circular_dependencies:
            artifacts_str = ','.join(cycle.artifacts)
            dep_types_str = ','.join(cycle.dependency_types)
            
            self.cursor.execute("""
                INSERT INTO flow_circular_deps (flow_id, cycle_artifacts, cycle_dep_types)
                VALUES (?, ?, ?)
            """, (flow_id, artifacts_str, dep_types_str))
        
        self.conn.commit()
        return flow_id
    
    def load_flow(self, start_program: str) -> Optional[ProgramFlow]:
        """
        Load a program flow from the database.
        
        Args:
            start_program: Starting program name
            
        Returns:
            ProgramFlow object or None if not found
        """
        # Get flow record
        self.cursor.execute("""
            SELECT id, start_program, depth, total_programs, 
                   total_copybooks, total_datasets, has_circular_deps
            FROM program_flows
            WHERE start_program = ?
        """, (start_program,))
        
        row = self.cursor.fetchone()
        if not row:
            return None
        
        flow_id, start_prog, depth, total_progs, total_copy, total_ds, has_circular = row
        
        # Get programs in flow
        self.cursor.execute("""
            SELECT program_name
            FROM flow_programs
            WHERE flow_id = ?
            ORDER BY id
        """, (flow_id,))
        
        programs = [row[0] for row in self.cursor.fetchall()]
        
        # Get circular dependencies
        self.cursor.execute("""
            SELECT cycle_artifacts, cycle_dep_types
            FROM flow_circular_deps
            WHERE flow_id = ?
        """, (flow_id,))
        
        circular_deps = []
        for artifacts_str, dep_types_str in self.cursor.fetchall():
            artifacts = artifacts_str.split(',')
            dep_types = dep_types_str.split(',')
            circular_deps.append(CircularDependency(
                artifacts=artifacts,
                dependency_types=dep_types
            ))
        
        # Create ProgramFlow object (without dependencies - those need to be loaded separately)
        flow = ProgramFlow(
            start_program=start_prog,
            depth=depth,
            programs=programs,
            dependencies=[],  # Dependencies not stored in flow tables
            circular_dependencies=circular_deps,
            total_programs=total_progs,
            total_copybooks=total_copy,
            total_datasets=total_ds
        )
        
        return flow
    
    def delete_flow(self, start_program: str) -> bool:
        """
        Delete a program flow from the database.
        
        Args:
            start_program: Starting program name
            
        Returns:
            True if deleted, False if not found
        """
        self.cursor.execute(
            "DELETE FROM program_flows WHERE start_program = ?",
            (start_program,)
        )
        self.conn.commit()
        
        return self.cursor.rowcount > 0
    
    def get_all_flows(self) -> List[Dict[str, Any]]:
        """
        Get summary of all flows in the database.
        
        Returns:
            List of flow summary dictionaries
        """
        self.cursor.execute("""
            SELECT start_program, depth, total_programs, 
                   total_copybooks, total_datasets, has_circular_deps, analyzed_date
            FROM program_flows
            ORDER BY start_program
        """)
        
        flows = []
        for row in self.cursor.fetchall():
            flows.append({
                'start_program': row[0],
                'depth': row[1],
                'total_programs': row[2],
                'total_copybooks': row[3],
                'total_datasets': row[4],
                'has_circular_deps': bool(row[5]),
                'analyzed_date': row[6]
            })
        
        return flows
    
    def get_flows_with_circular_deps(self) -> List[str]:
        """
        Get all flows that have circular dependencies.
        
        Returns:
            List of start program names
        """
        self.cursor.execute("""
            SELECT start_program
            FROM program_flows
            WHERE has_circular_deps = 1
            ORDER BY start_program
        """)
        
        return [row[0] for row in self.cursor.fetchall()]
    
    def get_programs_in_flows(self, program_name: str) -> List[str]:
        """
        Get all flows that include a specific program.
        
        Args:
            program_name: Program to search for
            
        Returns:
            List of start program names
        """
        self.cursor.execute("""
            SELECT DISTINCT pf.start_program
            FROM program_flows pf
            JOIN flow_programs fp ON pf.id = fp.flow_id
            WHERE fp.program_name = ?
            ORDER BY pf.start_program
        """, (program_name,))
        
        return [row[0] for row in self.cursor.fetchall()]
    
    def get_flow_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about all flows in the database.
        
        Returns:
            Dictionary with statistics
        """
        self.cursor.execute("""
            SELECT 
                COUNT(*) as total_flows,
                AVG(depth) as avg_depth,
                MAX(depth) as max_depth,
                AVG(total_programs) as avg_programs,
                MAX(total_programs) as max_programs,
                SUM(CASE WHEN has_circular_deps = 1 THEN 1 ELSE 0 END) as flows_with_cycles
            FROM program_flows
        """)
        
        row = self.cursor.fetchone()
        
        return {
            'total_flows': row[0] or 0,
            'avg_depth': round(row[1], 2) if row[1] else 0,
            'max_depth': row[2] or 0,
            'avg_programs': round(row[3], 2) if row[3] else 0,
            'max_programs': row[4] or 0,
            'flows_with_cycles': row[5] or 0
        }
