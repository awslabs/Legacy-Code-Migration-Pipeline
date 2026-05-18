"""Output generation for migration workpackage planning."""

import json
import logging
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from collections import defaultdict

from ..models import (
    BusinessFlow,
    PlanningData,
    Metadata,
    Statistics,
    WorkpackageAssignment,
    PhaseAssignment,
    MigrationSequenceItem,
    PriorityResult,
)


logger = logging.getLogger(__name__)


class OutputGenerator:
    """Generates JSON and Markdown outputs for migration planning."""
    
    def __init__(self, output_base: Path, project_name: str):
        """
        Initialize the output generator.
        
        Args:
            output_base: Base directory for output files
            project_name: Project name for metadata
        """
        self.output_base = Path(output_base)
        self.project_name = project_name
        
        # Ensure output directory and subfolders exist
        self.output_base.mkdir(parents=True, exist_ok=True)
        self.progress_dir = self.output_base / "progress"
        self.reports_dir = self.output_base / "reports"
        self.progress_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory: {self.output_base}")
    
    def generate_planning_json(
        self,
        data: PlanningData,
        priorities: Dict[str, PriorityResult],
        flows: List[BusinessFlow]
    ) -> Path:
        """
        Generate Workpackage_Planning.json.
        
        Args:
            data: Planning data with metadata, phases, sequence, statistics
            priorities: Dictionary mapping flow_id to PriorityResult
            flows: List of business flows
            
        Returns:
            Path to generated file
        """
        logger.info("Generating Workpackage_Planning.json")
        
        # Build flow map for lookups
        flow_map = {flow.flow_id: flow for flow in flows}
        
        # Build flowPriorities section
        flow_priorities = {}
        for flow_id, wp_assignment in data.flow_priorities.items():
            flow = flow_map[flow_id]
            priority_result = priorities[flow_id]
            
            # Find phase for this flow
            phase_num = None
            for phase in data.phases:
                if wp_assignment.workpackage_id in phase.workpackages:
                    phase_num = phase.phase_id
                    break
            
            flow_priorities[flow_id] = {
                "workpackageId": wp_assignment.workpackage_id,
                "priorityScore": wp_assignment.priority_score,
                "phase": phase_num,
                "preExistentModules": wp_assignment.preexistent_modules,
                "priorityFactors": {
                    "totalPrograms": priority_result.factors.total_programs,
                    "commonModules": priority_result.factors.common_modules,
                    "compositeScore": priority_result.factors.composite_score,
                    "completeFlowBonus": priority_result.factors.complete_flow_bonus,
                    "simpleFlowBonus": priority_result.factors.simple_flow_bonus
                }
            }
        
        # Build phases section
        phases_list = []
        for phase in data.phases:
            phases_list.append({
                "phaseId": phase.phase_id,
                "name": f"Phase {phase.phase_id}",
                "workpackages": phase.workpackages,
                "dependencies": phase.dependencies
            })
        
        # Build migrationSequence section (sorted by sequenceNumber)
        migration_sequence = []
        sorted_sequence = sorted(data.migration_sequence, key=lambda x: x.sequence_number)
        for item in sorted_sequence:
            seq_item = {
                "sequenceNumber": item.sequence_number,
                "workpackageId": item.workpackage_id,
                "flowId": item.flow_id,
                "phase": item.phase,
                "wave": item.wave,
                "prerequisites": item.prerequisites
            }
            
            # Add soft prerequisites if present
            if item.soft_prerequisites:
                seq_item["softPrerequisites"] = item.soft_prerequisites
            
            # Add shared module context if present
            if item.shared_module_context:
                seq_item["sharedModuleContext"] = item.shared_module_context
            
            migration_sequence.append(seq_item)
        
        # Build complete output structure
        output = {
            "metadata": {
                "projectName": data.metadata.project_name,
                "createdDate": data.metadata.created_date,
                "phase": data.metadata.phase,
                "version": data.metadata.version
            },
            "flowPriorities": flow_priorities,
            "phases": phases_list,
            "migrationSequence": migration_sequence,
            "statistics": {
                "totalFlows": data.statistics.total_flows,
                "totalPhases": data.statistics.total_phases,
                "averagePriorityScore": data.statistics.average_priority_score,
                "flowsPerPhase": data.statistics.flows_per_phase
            },
            "sharedModuleAnalysis": data.shared_module_report,
            "coordinationDependencies": data.coordination_dependencies
        }
        
        # Write to file
        output_path = self.output_base / "Workpackage_Planning.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Generated: {output_path}")
        return output_path
    
    def generate_status_json(
        self,
        workpackages: List[WorkpackageAssignment],
        phases: List[PhaseAssignment]
    ) -> Path:
        """
        Generate Workpackage_Status.json with initial status.
        
        Args:
            workpackages: List of workpackage assignments
            phases: List of phase assignments
            
        Returns:
            Path to generated file
        """
        logger.info("Generating Workpackage_Status.json")
        
        # Build phase map for lookup
        phase_map = {}
        for phase in phases:
            for wp_id in phase.workpackages:
                phase_map[wp_id] = phase.phase_id
        
        # Build status entries
        status_entries = []
        for wp in workpackages:
            phase_num = phase_map.get(wp.workpackage_id, 1)
            
            entry = {
                "workpackageId": wp.workpackage_id,
                "flowId": wp.flow_id,
                "phase": phase_num,
                "status": "NOT_STARTED",
                "startDate": None,
                "endDate": None,
                "notes": ""
            }
            status_entries.append(entry)
        
        # Build complete output structure
        output = {
            "metadata": {
                "projectName": self.project_name,
                "lastUpdated": datetime.utcnow().isoformat() + 'Z',
                "version": "1.0"
            },
            "status": "completed",
            "workpackages": status_entries
        }
        
        # Write to file
        output_path = self.progress_dir / "Workpackage_Status.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Generated: {output_path}")
        return output_path
    
    def generate_roadmap_markdown(
        self,
        data: PlanningData,
        flows: List[BusinessFlow]
    ) -> Path:
        """
        Generate Workpackage_Definition_Roadmap.md.
        
        Args:
            data: Planning data
            flows: List of business flows
            
        Returns:
            Path to generated file
        """
        logger.info("Generating Workpackage_Definition_Roadmap.md")
        
        # Build flow map for lookups
        flow_map = {flow.flow_id: flow for flow in flows}
        
        lines = []
        
        # Header with metadata
        lines.append(f"# Migration Workpackage Roadmap: {data.metadata.project_name}")
        lines.append("")
        lines.append(f"**Generated:** {data.metadata.created_date}")
        lines.append(f"**Version:** {data.metadata.version}")
        lines.append(f"**Phase:** {data.metadata.phase}")
        lines.append(f"**Status:** completed")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Executive Summary
        lines.append("## Executive Summary")
        lines.append("")
        lines.append(f"- **Total Flows:** {data.statistics.total_flows}")
        lines.append(f"- **Total Phases:** {data.statistics.total_phases}")
        lines.append(f"- **Average Priority Score:** {data.statistics.average_priority_score:.2f}")
        lines.append("")
        
        # Flows per phase
        lines.append("### Flows per Phase")
        lines.append("")
        for phase_id in sorted(data.statistics.flows_per_phase.keys()):
            count = data.statistics.flows_per_phase[phase_id]
            lines.append(f"- **Phase {phase_id}:** {count} workpackages")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Phase Breakdown
        lines.append("## Phase Breakdown")
        lines.append("")
        
        for phase in data.phases:
            lines.append(f"### Phase {phase.phase_id}")
            lines.append("")
            
            if phase.dependencies:
                dep_str = ", ".join([f"Phase {d}" for d in phase.dependencies])
                lines.append(f"**Dependencies:** {dep_str}")
                lines.append("")
            
            lines.append(f"**Workpackages:** {len(phase.workpackages)}")
            lines.append("")
            
            # List workpackages in this phase
            for wp_id in sorted(phase.workpackages):
                # Find the workpackage assignment
                wp_assignment = None
                for flow_id, wp in data.flow_priorities.items():
                    if wp.workpackage_id == wp_id:
                        wp_assignment = wp
                        break
                
                if wp_assignment:
                    flow = flow_map.get(wp_assignment.flow_id)
                    program_count = len(flow.programs) if flow else 0
                    
                    lines.append(
                        f"- **WP{wp_id}:** {wp_assignment.flow_id} "
                        f"(Priority: {wp_assignment.priority_score:.2f}, "
                        f"Programs: {program_count})"
                    )
                    
                    if wp_assignment.preexistent_modules:
                        lines.append(
                            f"  - Pre-existent modules: "
                            f"{len(wp_assignment.preexistent_modules)}"
                        )
            
            lines.append("")
        
        lines.append("---")
        lines.append("")
        
        # Shared Module Analysis
        if data.shared_module_report and data.shared_module_report.get('totalSharedModules', 0) > 0:
            lines.append("## Shared Module Analysis")
            lines.append("")
            lines.append(f"- **Total Shared Modules:** {data.shared_module_report['totalSharedModules']}")
            lines.append(f"- **Flows with Shared Modules:** {data.shared_module_report['flowsWithSharedModules']} of {data.shared_module_report['totalFlows']}")
            lines.append("")
            
            # List top shared modules
            lines.append("### Most Shared Modules")
            lines.append("")
            shared_modules = data.shared_module_report.get('sharedModules', [])
            for module in shared_modules[:10]:  # Top 10
                lines.append(f"- **{module['moduleName']}**: Used by {module['usageCount']} flows")
                flow_list = ", ".join(module['usedByFlows'][:5])
                if len(module['usedByFlows']) > 5:
                    flow_list += f", ... and {len(module['usedByFlows']) - 5} more"
                lines.append(f"  - Flows: {flow_list}")
            
            lines.append("")
            
            # Coordination dependencies
            if data.coordination_dependencies:
                flows_with_coord = sum(1 for deps in data.coordination_dependencies.values() if deps)
                if flows_with_coord > 0:
                    lines.append("### Coordination Dependencies")
                    lines.append("")
                    lines.append(f"**Note:** {flows_with_coord} flows have coordination dependencies based on shared modules.")
                    lines.append("These flows should ideally be migrated after the flows they coordinate with.")
                    lines.append("")
                    
                    # Show flows with coordination dependencies
                    for flow_id, coord_flows in sorted(data.coordination_dependencies.items()):
                        if coord_flows:
                            coord_str = ", ".join(coord_flows)
                            lines.append(f"- **{flow_id}** should coordinate with: {coord_str}")
                    
                    lines.append("")
            
            lines.append("---")
            lines.append("")
        
        # Dependency Visualization
        lines.append("## Dependency Visualization")
        lines.append("")
        lines.append("### Flow Dependencies")
        lines.append("")
        
        # Show flows with dependencies
        has_dependencies = False
        for flow in flows:
            if flow.required_flows:
                has_dependencies = True
                req_str = ", ".join(flow.required_flows)
                lines.append(f"- **{flow.flow_id}** depends on: {req_str}")
        
        if not has_dependencies:
            lines.append("*No dependencies between flows*")
        
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Migration Sequence Table
        lines.append("## Migration Sequence")
        lines.append("")
        lines.append("The migration sequence shows the recommended order for implementing workpackages.")
        lines.append("Workpackages are organized into phases and waves:")
        lines.append("")
        lines.append("- **Phase**: Hard dependencies - must complete previous phases first")
        lines.append("- **Wave**: Soft dependencies - workpackages in the same wave can be migrated in parallel")
        lines.append("- **Prerequisites**: Hard dependencies that must be completed first")
        lines.append("- **Soft Prerequisites**: Recommended to complete first (shared modules)")
        lines.append("")
        lines.append("| Seq | Workpackage | Flow ID | Phase | Wave | Prerequisites | Soft Prerequisites |")
        lines.append("|-----|-------------|---------|-------|------|---------------|-------------------|")
        
        for item in data.migration_sequence:
            prereq_str = ", ".join([f"WP{p}" for p in item.prerequisites]) if item.prerequisites else "None"
            soft_prereq_str = ", ".join([f"WP{p}" for p in item.soft_prerequisites]) if item.soft_prerequisites else "None"
            lines.append(
                f"| {item.sequence_number} | "
                f"WP{item.workpackage_id} | "
                f"{item.flow_id} | "
                f"{item.phase} | "
                f"{item.wave} | "
                f"{prereq_str} | "
                f"{soft_prereq_str} |"
            )
        
        lines.append("")
        
        # Add wave explanation if there are multiple waves
        max_wave = max((item.wave for item in data.migration_sequence), default=1)
        if max_wave > 1:
            lines.append("### Wave-Based Migration")
            lines.append("")
            lines.append("Workpackages in the same phase and wave can be migrated in parallel.")
            lines.append("This allows for efficient resource allocation and faster overall migration.")
            lines.append("")
            
            # Group by phase and wave
            by_phase_wave = defaultdict(list)
            for item in data.migration_sequence:
                by_phase_wave[(item.phase, item.wave)].append(item)
            
            for (phase, wave) in sorted(by_phase_wave.keys()):
                items = by_phase_wave[(phase, wave)]
                lines.append(f"**Phase {phase}, Wave {wave}:** {len(items)} workpackages can be migrated in parallel")
            
            lines.append("")
        
        lines.append("---")
        lines.append("")
        lines.append("*End of Roadmap*")
        lines.append("")
        
        # Write to file
        output_path = self.reports_dir / "Workpackage_Definition_Roadmap.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        logger.info(f"Generated: {output_path}")
        return output_path
