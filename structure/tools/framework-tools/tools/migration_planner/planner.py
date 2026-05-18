"""Migration planner orchestrator."""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List

from .models import (
    PlannerConfig,
    PlanningData,
    Metadata,
    Statistics,
)
from .input import FlowDataLoader
from .priority import PriorityCalculator
from .workpackage import WorkpackageAssigner
from .phase import PhaseAssigner, ValidationError
from .output import OutputGenerator
from .logging_config import get_logger
from datetime import datetime


logger = get_logger(__name__)


@dataclass
class PlanningResult:
    """Result of the planning pipeline."""
    
    planning_data: PlanningData
    output_files: List[Path]
    success: bool
    error_message: str = ""


class MigrationPlanner:
    """Orchestrates the migration workpackage planning pipeline."""
    
    def __init__(self, config: PlannerConfig):
        """
        Initialize the migration planner.
        
        Args:
            config: Planner configuration
        """
        self.config = config
        self.logger = get_logger(__name__)
    
    def run(self) -> PlanningResult:
        """
        Execute the planning pipeline.
        
        Pipeline stages:
        1. Load input files (flows and classifications)
        2. Calculate priority scores
        3. Assign workpackage IDs
        4. Determine migration phases
        5. Generate output files
        
        Returns:
            PlanningResult with planning data and output file paths
            
        Raises:
            FileNotFoundError: If required input files are missing
            ValueError: If validation fails
            ValidationError: If dependency validation fails
        """
        try:
            # Stage 1: Load input files
            self.logger.info("=" * 60)
            self.logger.info("STAGE 1: Loading input files")
            self.logger.info("=" * 60)
            
            loader = FlowDataLoader()
            
            # Load flows
            flows = loader.load_flows(self.config.flows_file)
            self.logger.info(f"Loaded {len(flows)} business flows")
            
            # Load classifications (optional)
            classifications = loader.load_classifications(self.config.classifications_file)
            if classifications:
                self.logger.info(f"Loaded {len(classifications)} module classifications")
            else:
                self.logger.warning("No module classifications loaded")
            
            # Stage 2: Calculate priority scores
            self.logger.info("")
            self.logger.info("=" * 60)
            self.logger.info("STAGE 2: Calculating priority scores")
            self.logger.info("=" * 60)
            
            calculator = PriorityCalculator(classifications)
            priorities = calculator.calculate_all_priorities(flows)
            self.logger.info(f"Calculated priorities for {len(priorities)} flows")
            
            # Log priority range
            if priorities:
                scores = [p.priority_score for p in priorities.values()]
                min_score = min(scores)
                max_score = max(scores)
                avg_score = sum(scores) / len(scores)
                self.logger.info(
                    f"Priority score range: {min_score:.2f} to {max_score:.2f} "
                    f"(avg: {avg_score:.2f})"
                )
            
            # Stage 2.5: Analyze shared modules
            self.logger.info("")
            self.logger.info("=" * 60)
            self.logger.info("STAGE 2.5: Analyzing shared modules")
            self.logger.info("=" * 60)
            
            from .shared_module_analyzer import SharedModuleAnalyzer
            
            priority_scores = {fid: p.priority_score for fid, p in priorities.items()}
            shared_analyzer = SharedModuleAnalyzer(flows, priority_scores)
            shared_report = shared_analyzer.get_shared_module_report()
            
            self.logger.info(
                f"Found {shared_report['totalSharedModules']} shared modules "
                f"across {shared_report['flowsWithSharedModules']} flows"
            )
            
            # Calculate coordination dependencies
            coordination_deps, shared_context = shared_analyzer.calculate_coordination_dependencies(
                strategy="priority_first"
            )
            
            # Count flows with coordination dependencies
            flows_with_coordination = sum(1 for deps in coordination_deps.values() if deps)
            if flows_with_coordination > 0:
                self.logger.info(
                    f"Identified coordination dependencies for {flows_with_coordination} flows"
                )
            
            # Stage 3: Assign workpackage IDs
            self.logger.info("")
            self.logger.info("=" * 60)
            self.logger.info("STAGE 3: Assigning workpackage IDs")
            self.logger.info("=" * 60)
            
            assigner = WorkpackageAssigner()
            workpackages = assigner.assign_workpackages(priorities, flows)
            self.logger.info(f"Assigned {len(workpackages)} workpackages")
            
            # Log pre-existent module statistics
            total_preexistent = sum(
                len(wp.preexistent_modules) for wp in workpackages
            )
            if total_preexistent > 0:
                self.logger.info(
                    f"Identified {total_preexistent} pre-existent module references"
                )
            
            # Stage 4: Determine migration phases
            self.logger.info("")
            self.logger.info("=" * 60)
            self.logger.info("STAGE 4: Determining migration phases")
            self.logger.info("=" * 60)
            
            phase_assigner = PhaseAssigner()
            
            try:
                phases, migration_sequence = phase_assigner.assign_phases(
                    workpackages, flows, coordination_deps, shared_context
                )
                self.logger.info(f"Assigned {len(phases)} migration phases")
                self.logger.info(f"Generated migration sequence with {len(migration_sequence)} items")
                
                # Log wave statistics
                wave_counts = {}
                for item in migration_sequence:
                    wave_key = f"Phase {item.phase}, Wave {item.wave}"
                    wave_counts[wave_key] = wave_counts.get(wave_key, 0) + 1
                
                if wave_counts:
                    self.logger.info("Wave distribution:")
                    for wave_key in sorted(wave_counts.keys()):
                        self.logger.info(f"  {wave_key}: {wave_counts[wave_key]} workpackages")
            except ValidationError as e:
                self.logger.error(f"Dependency validation failed: {e}")
                raise
            
            # Stage 5: Generate output files
            self.logger.info("")
            self.logger.info("=" * 60)
            self.logger.info("STAGE 5: Generating output files")
            self.logger.info("=" * 60)
            
            # Calculate statistics
            statistics = self._calculate_statistics(workpackages, phases, priorities)
            
            # Create metadata
            metadata = Metadata(
                project_name=self.config.project_name,
                created_date=datetime.utcnow().isoformat() + 'Z',
                phase="WORKPACKAGE_PLANNING",
                version="1.0"
            )
            
            # Build planning data
            flow_priorities_dict = {wp.flow_id: wp for wp in workpackages}
            
            planning_data = PlanningData(
                metadata=metadata,
                flow_priorities=flow_priorities_dict,
                phases=phases,
                migration_sequence=migration_sequence,
                statistics=statistics,
                shared_module_report=shared_report,
                coordination_dependencies=coordination_deps,
                shared_module_context=shared_context
            )
            
            # Generate output files
            generator = OutputGenerator(
                self.config.output_base,
                self.config.project_name
            )
            
            output_files = []
            
            # Generate planning JSON
            planning_json = generator.generate_planning_json(
                planning_data, priorities, flows
            )
            output_files.append(planning_json)
            
            # Generate status JSON
            status_json = generator.generate_status_json(workpackages, phases)
            output_files.append(status_json)
            
            # Generate roadmap markdown
            roadmap_md = generator.generate_roadmap_markdown(planning_data, flows)
            output_files.append(roadmap_md)
            
            self.logger.info("")
            self.logger.info("=" * 60)
            self.logger.info("PLANNING COMPLETE")
            self.logger.info("=" * 60)
            self.logger.info(f"Output directory: {self.config.output_base}")
            self.logger.info("Generated files:")
            for output_file in output_files:
                self.logger.info(f"  - {output_file.name}")
            
            return PlanningResult(
                planning_data=planning_data,
                output_files=output_files,
                success=True
            )
            
        except FileNotFoundError as e:
            error_msg = f"File not found: {e}"
            self.logger.error(error_msg)
            return PlanningResult(
                planning_data=None,
                output_files=[],
                success=False,
                error_message=error_msg
            )
        
        except ValueError as e:
            error_msg = f"Validation error: {e}"
            self.logger.error(error_msg)
            return PlanningResult(
                planning_data=None,
                output_files=[],
                success=False,
                error_message=error_msg
            )
        
        except ValidationError as e:
            error_msg = f"Dependency validation error: {e}"
            self.logger.error(error_msg)
            return PlanningResult(
                planning_data=None,
                output_files=[],
                success=False,
                error_message=error_msg
            )
        
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            self.logger.error(error_msg, exc_info=True)
            return PlanningResult(
                planning_data=None,
                output_files=[],
                success=False,
                error_message=error_msg
            )
    
    def _calculate_statistics(
        self,
        workpackages,
        phases,
        priorities
    ) -> Statistics:
        """
        Calculate statistics for the planning data.
        
        Args:
            workpackages: List of workpackage assignments
            phases: List of phase assignments
            priorities: Dictionary of priority results
            
        Returns:
            Statistics object
        """
        total_flows = len(workpackages)
        total_phases = len(phases)
        
        # Calculate average priority score
        if priorities:
            scores = [p.priority_score for p in priorities.values()]
            average_priority_score = sum(scores) / len(scores)
        else:
            average_priority_score = 0.0
        
        # Calculate flows per phase
        flows_per_phase = {}
        for phase in phases:
            flows_per_phase[phase.phase_id] = len(phase.workpackages)
        
        return Statistics(
            total_flows=total_flows,
            total_phases=total_phases,
            average_priority_score=average_priority_score,
            flows_per_phase=flows_per_phase
        )
