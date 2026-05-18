"""Shared module analyzer for detecting coordination dependencies."""

from typing import Dict, List, Set, Tuple
from collections import defaultdict
from .models.business_flow import BusinessFlow


class SharedModuleAnalyzer:
    """
    Analyzes shared modules across flows to identify coordination dependencies.
    
    This analyzer detects when multiple flows use the same utility modules
    and determines which flow should be migrated first based on priority scores.
    """
    
    def __init__(self, flows: List[BusinessFlow], priority_scores: Dict[str, float]):
        """
        Initialize shared module analyzer.
        
        Args:
            flows: List of BusinessFlow objects
            priority_scores: Dictionary mapping flow_id to priority score
        """
        self.flows = flows
        self.priority_scores = priority_scores
        self._module_to_flows: Dict[str, List[str]] = defaultdict(list)
        self._build_module_index()
    
    def _build_module_index(self) -> None:
        """Build index of which flows use which modules."""
        for flow in self.flows:
            for program in flow.programs:
                if not program.is_utility:
                    # Only track non-utility programs as potential shared modules
                    self._module_to_flows[program.name].append(flow.flow_id)
    
    def find_shared_modules(self, min_usage_count: int = 2) -> Dict[str, List[str]]:
        """
        Find modules that are shared across multiple flows.
        
        Args:
            min_usage_count: Minimum number of flows that must use a module
                           for it to be considered "shared" (default: 2)
        
        Returns:
            Dictionary mapping module name to list of flow IDs that use it
        """
        shared = {}
        for module_name, flow_ids in self._module_to_flows.items():
            if len(flow_ids) >= min_usage_count:
                shared[module_name] = flow_ids
        return shared
    
    def calculate_coordination_dependencies(
        self,
        strategy: str = "priority_first"
    ) -> tuple[Dict[str, List[str]], Dict[str, Dict]]:
        """
        Calculate coordination dependencies and shared module context.
        
        This creates "soft dependencies" where flows sharing modules should
        coordinate their migration order. The strategy determines which flow
        should be migrated first.
        
        Args:
            strategy: Strategy for determining migration order:
                     - "priority_first": Migrate higher-priority (lower score) flows first
                     - "complexity_first": Migrate simpler flows first
                     - "none": No coordination dependencies
        
        Returns:
            Tuple of:
            - Dictionary mapping flow_id to list of flow_ids it should coordinate with
              (flows that should ideally be migrated before it)
            - Dictionary mapping flow_id to shared module context (bidirectional info)
        """
        if strategy == "none":
            return {flow.flow_id: [] for flow in self.flows}, {}
        
        coordination_deps: Dict[str, Set[str]] = defaultdict(set)
        shared_context: Dict[str, Dict] = {}
        shared_modules = self.find_shared_modules()
        
        for module_name, flow_ids in shared_modules.items():
            # Sort flows by priority score (lower = higher priority)
            sorted_flows = sorted(
                flow_ids,
                key=lambda fid: self.priority_scores.get(fid, float('inf'))
            )
            
            # Each flow should coordinate with all higher-priority flows
            # that share the same module
            for i, flow_id in enumerate(sorted_flows):
                # Add all flows with higher priority (earlier in sorted list)
                for higher_priority_flow in sorted_flows[:i]:
                    coordination_deps[flow_id].add(higher_priority_flow)
                
                # Build shared module context (bidirectional)
                if flow_id not in shared_context:
                    shared_context[flow_id] = {
                        'sharesModulesWith': [],
                        'sharedModules': {},
                        'coordinationReason': ''
                    }
                
                # Add all other flows that share this module
                other_flows = [f for f in flow_ids if f != flow_id]
                for other_flow in other_flows:
                    if other_flow not in shared_context[flow_id]['sharesModulesWith']:
                        shared_context[flow_id]['sharesModulesWith'].append(other_flow)
                
                # Track which modules are shared with which flows
                for other_flow in other_flows:
                    if other_flow not in shared_context[flow_id]['sharedModules']:
                        shared_context[flow_id]['sharedModules'][other_flow] = []
                    shared_context[flow_id]['sharedModules'][other_flow].append(module_name)
                
                # Set coordination reason
                if coordination_deps[flow_id]:
                    higher_priority_list = sorted(list(coordination_deps[flow_id]))
                    shared_context[flow_id]['coordinationReason'] = (
                        f"Should migrate after {', '.join(higher_priority_list[:3])}"
                        f"{' and others' if len(higher_priority_list) > 3 else ''} "
                        f"(higher priority flows sharing modules)"
                    )
                else:
                    shared_context[flow_id]['coordinationReason'] = (
                        "Highest priority flow for shared modules - can migrate first"
                    )
        
        # Convert sets to sorted lists
        coordination_deps_final = {
            flow_id: sorted(list(deps))
            for flow_id, deps in coordination_deps.items()
        }
        
        return coordination_deps_final, shared_context
    
    def get_shared_module_report(self) -> Dict[str, any]:
        """
        Generate a report on shared module usage.
        
        Returns:
            Dictionary containing:
            - total_shared_modules: Count of modules used by multiple flows
            - shared_modules: List of shared module details
            - flows_with_shared_modules: Count of flows using shared modules
        """
        shared = self.find_shared_modules()
        
        shared_module_details = []
        for module_name, flow_ids in shared.items():
            shared_module_details.append({
                'moduleName': module_name,
                'usedByFlows': flow_ids,
                'usageCount': len(flow_ids)
            })
        
        # Sort by usage count (most shared first)
        shared_module_details.sort(key=lambda x: x['usageCount'], reverse=True)
        
        flows_with_shared = set()
        for flow_ids in shared.values():
            flows_with_shared.update(flow_ids)
        
        return {
            'totalSharedModules': len(shared),
            'sharedModules': shared_module_details,
            'flowsWithSharedModules': len(flows_with_shared),
            'totalFlows': len(self.flows)
        }
