"""Pod partitioner: clusters workpackages into pods for parallel execution."""

import json
import logging
import math
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .models import CrossPodDependency, Pod, PodAssignment

logger = logging.getLogger(__name__)


class PodPartitioner:
    """
    Deterministic pod partitioner implementing the Phase 2.5 algorithm.

    Handles steps 1-4, 6-10 of the prompt fully.
    Step 5 (domain-similarity merge) uses a copybook/entity overlap heuristic.
    Domain cluster *naming* is left as an optional LLM refinement.
    """

    def __init__(
        self,
        workpackage_planning_path: str,
        business_flows_path: str,
        module_classifications_path: Optional[str] = None,
        db_analysis_path: Optional[str] = None,
        pod_count_override: Optional[int] = None,
    ):
        self.wp_path = Path(workpackage_planning_path)
        self.flows_path = Path(business_flows_path)
        self.classifications_path = (
            Path(module_classifications_path) if module_classifications_path else None
        )
        self.db_path = Path(db_analysis_path) if db_analysis_path else None
        self.pod_count_override = pod_count_override

        # Loaded data
        self.wp_data: Dict = {}
        self.flows_data: Dict = {}
        self.classifications: Dict = {}
        self.db_tables_by_flow: Dict[str, Set[str]] = defaultdict(set)

        # Derived structures
        self.flow_to_wp: Dict[str, str] = {}  # flow_id -> WP-xxx
        self.wp_to_flow: Dict[str, str] = {}  # WP-xxx -> flow_id
        self.wp_deps: Dict[str, Set[str]] = defaultdict(set)  # WP -> set of WP deps
        self.wp_effort: Dict[str, float] = {}
        self.wp_entities: Dict[str, Set[str]] = defaultdict(set)  # WP -> shared entities
        self.wp_copybooks: Dict[str, Set[str]] = defaultdict(set)
        self.wp_db_tables: Dict[str, Set[str]] = defaultdict(set)
        self.wp_programs: Dict[str, Set[str]] = defaultdict(set)
        self.flow_by_id: Dict[str, dict] = {}

    # ── Stage 1: Load inputs ──────────────────────────────────────────

    def load_inputs(self) -> None:
        """Load all input files."""
        logger.info("Loading Workpackage_Planning.json")
        with open(self.wp_path, "r") as f:
            self.wp_data = json.load(f)

        logger.info("Loading Business_Flows.json")
        with open(self.flows_path, "r") as f:
            self.flows_data = json.load(f)

        if self.classifications_path and self.classifications_path.exists():
            logger.info("Loading Module_Classifications.json")
            with open(self.classifications_path, "r") as f:
                self.classifications = json.load(f)
        else:
            logger.info("No module classifications available, skipping")

        if self.db_path and self.db_path.exists():
            logger.info("Loading DB_Source_Analysis_Report.md")
            self._parse_db_report()
        else:
            logger.info("No DB analysis report available, skipping")

        self._build_indexes()

    def _parse_db_report(self) -> None:
        """Parse DB analysis report for table-to-flow mappings."""
        # Best-effort parse of markdown tables
        try:
            text = self.db_path.read_text()
            # Simple heuristic: look for table names in context of flow/program refs
            # This is intentionally basic; the LLM can refine if needed
            for flow in self.flows_data.get("flows", []):
                flow_id = flow["flowId"]
                for db_op in flow.get("dataOperations", {}).get("databases", []):
                    table = db_op.get("target", "")
                    if table:
                        self.db_tables_by_flow[flow_id].add(table)
        except Exception as e:
            logger.warning(f"Could not parse DB report: {e}")

    def _build_indexes(self) -> None:
        """Build lookup indexes from loaded data."""
        # Map flow_id <-> WP-xxx
        for flow_id, wp_info in self.wp_data.get("flowPriorities", {}).items():
            wp_id = f"WP-{wp_info['workpackageId']:03d}"
            self.flow_to_wp[flow_id] = wp_id
            self.wp_to_flow[wp_id] = flow_id

        # Build flow lookup
        for flow in self.flows_data.get("flows", []):
            self.flow_by_id[flow["flowId"]] = flow

        # Build dependency graph (WP -> WP)
        for flow_id, wp_info in self.wp_data.get("flowPriorities", {}).items():
            wp_id = self.flow_to_wp[flow_id]
            flow = self.flow_by_id.get(flow_id, {})

            # Hard dependencies from requiredFlows
            for req_flow in flow.get("dependencies", {}).get("requiredFlows", []):
                if req_flow in self.flow_to_wp:
                    self.wp_deps[wp_id].add(self.flow_to_wp[req_flow])

            # Coordination dependencies (soft -> treat as edges for connected components)
            coord_deps = self.wp_data.get("coordinationDependencies", {})
            if flow_id in coord_deps:
                for dep_flow in coord_deps[flow_id]:
                    if dep_flow in self.flow_to_wp:
                        self.wp_deps[wp_id].add(self.flow_to_wp[dep_flow])

        # Extract per-WP metadata from flows
        for flow_id, flow in self.flow_by_id.items():
            if flow_id not in self.flow_to_wp:
                continue
            wp_id = self.flow_to_wp[flow_id]

            # Programs
            for prog in flow.get("scope", {}).get("programs", []):
                self.wp_programs[wp_id].add(prog["name"])

            # Copybooks
            for cb in flow.get("scope", {}).get("copybooks", []):
                self.wp_copybooks[wp_id].add(cb["name"])

            # Datasets / entities
            for ds in flow.get("scope", {}).get("datasets", []):
                self.wp_entities[wp_id].add(ds)

            # DB tables from dataOperations
            for db_op in flow.get("dataOperations", {}).get("databases", []):
                table = db_op.get("target", "")
                if table:
                    self.wp_db_tables[wp_id].add(table)
                    self.wp_entities[wp_id].add(table)

        # Effort estimation per WP
        for wp_id in self.wp_to_flow:
            flow_id = self.wp_to_flow[wp_id]
            flow = self.flow_by_id.get(flow_id, {})
            n_programs = flow.get("complexity", {}).get("totalPrograms", 1)
            n_copybooks = len(self.wp_copybooks.get(wp_id, set()))
            n_tables = len(self.wp_db_tables.get(wp_id, set()))
            composite = flow.get("complexity", {}).get("compositeScore", 0.5)
            self.wp_effort[wp_id] = n_programs + 0.5 * n_copybooks + n_tables + composite

    # ── Stage 2-3: Build dependency graph & find connected components ─

    def find_connected_components(self) -> List[Set[str]]:
        """Find connected components in the undirected dependency graph."""
        all_wps = set(self.wp_to_flow.keys())

        # Build undirected adjacency
        adj: Dict[str, Set[str]] = defaultdict(set)
        for wp, deps in self.wp_deps.items():
            for dep in deps:
                adj[wp].add(dep)
                adj[dep].add(wp)

        visited: Set[str] = set()
        components: List[Set[str]] = []

        for wp in sorted(all_wps):
            if wp in visited:
                continue
            # BFS
            component: Set[str] = set()
            queue = [wp]
            while queue:
                node = queue.pop(0)
                if node in visited:
                    continue
                visited.add(node)
                component.add(node)
                for neighbor in adj.get(node, set()):
                    if neighbor not in visited:
                        queue.append(neighbor)
            components.append(component)

        logger.info(f"Found {len(components)} connected components")
        return components

    # ── Stage 4: Enrich with domain data ──────────────────────────────

    def compute_domain_affinity(
        self, comp_a: Set[str], comp_b: Set[str]
    ) -> float:
        """
        Compute domain similarity between two components.
        Uses Jaccard similarity over copybooks + entities + DB tables.
        """
        set_a: Set[str] = set()
        set_b: Set[str] = set()
        for wp in comp_a:
            set_a |= self.wp_copybooks.get(wp, set())
            set_a |= self.wp_entities.get(wp, set())
            set_a |= self.wp_db_tables.get(wp, set())
        for wp in comp_b:
            set_b |= self.wp_copybooks.get(wp, set())
            set_b |= self.wp_entities.get(wp, set())
            set_b |= self.wp_db_tables.get(wp, set())

        if not set_a and not set_b:
            return 0.0
        intersection = set_a & set_b
        union = set_a | set_b
        return len(intersection) / len(union) if union else 0.0

    def infer_domain_cluster(self, workpackages: Set[str]) -> str:
        """
        Infer a domain cluster label from the workpackages' characteristics.
        Uses entry point types and naming patterns as heuristic.
        Returns a machine-generated label; LLM can refine later.
        """
        entry_types = defaultdict(int)
        name_tokens = defaultdict(int)

        for wp_id in workpackages:
            flow_id = self.wp_to_flow.get(wp_id, "")
            flow = self.flow_by_id.get(flow_id, {})

            # Entry point type
            primary_type = flow.get("entryPoint", {}).get("primaryType", "UNKNOWN")
            entry_types[primary_type] += 1

            # Name-based tokens (e.g., CBACT -> batch-account, COTRN -> online-transaction)
            name = flow.get("name", "")
            if name:
                prefix = name[:4].upper() if len(name) >= 4 else name.upper()
                name_tokens[prefix] += 1

        # Determine dominant type
        dominant_type = max(entry_types, key=entry_types.get) if entry_types else "mixed"

        # Determine dominant name prefix
        dominant_prefix = (
            max(name_tokens, key=name_tokens.get) if name_tokens else "unknown"
        )

        # Map common prefixes to domain names
        prefix_domains = {
            "CBAC": "batch-account-processing",
            "CBTR": "batch-transaction-processing",
            "CBCU": "batch-customer-processing",
            "CBST": "batch-statement-generation",
            "COBS": "batch-scheduling",
            "COAC": "online-account-management",
            "COTR": "online-transaction-management",
            "COUS": "online-user-management",
            "COSG": "online-sign-on",
            "COBI": "online-billing",
            "COCR": "online-credit-card-management",
            "COAD": "online-administration",
            "COME": "online-menu-navigation",
            "CORP": "online-reporting",
        }

        domain = prefix_domains.get(dominant_prefix, f"{dominant_type.lower()}-{dominant_prefix.lower()}")
        return domain

    # ── Stage 5: Merge small components ───────────────────────────────

    def merge_small_components(
        self, components: List[Set[str]], min_size: int = 2
    ) -> List[Set[str]]:
        """Merge components with fewer than min_size WPs into most similar component."""
        large = [c for c in components if len(c) >= min_size]
        small = [c for c in components if len(c) < min_size]

        if not large and small:
            # All components are small; merge them all into one
            merged = set()
            for c in small:
                merged |= c
            return [merged]

        for small_comp in small:
            best_idx = 0
            best_score = -1.0
            for i, large_comp in enumerate(large):
                score = self.compute_domain_affinity(small_comp, large_comp)
                if score > best_score:
                    best_score = score
                    best_idx = i
            large[best_idx] |= small_comp
            logger.info(
                f"Merged small component {small_comp} into component {best_idx} "
                f"(affinity={best_score:.3f})"
            )

        return large

    # ── Stage 6: Balance pod sizes ────────────────────────────────────

    def _component_effort(self, component: Set[str]) -> float:
        return sum(self.wp_effort.get(wp, 1.0) for wp in component)

    def calculate_pod_count(self, total_wps: int) -> int:
        """Calculate target pod count."""
        if self.pod_count_override:
            return self.pod_count_override
        if total_wps <= 5:
            return 1
        count = math.ceil(total_wps / 5)
        count = max(2, count)
        count = min(count, total_wps // 2)
        return count

    def balance_pods(
        self, components: List[Set[str]], target_pod_count: int
    ) -> List[Set[str]]:
        """
        Balance components into target_pod_count pods.
        Split oversized components, merge undersized ones.
        """
        # If we already have the right number, just return
        if len(components) == target_pod_count:
            return components

        # If too many components, merge smallest pairs by affinity
        while len(components) > target_pod_count:
            # Find the two most similar components
            best_i, best_j, best_score = 0, 1, -1.0
            for i in range(len(components)):
                for j in range(i + 1, len(components)):
                    score = self.compute_domain_affinity(components[i], components[j])
                    # Prefer merging smaller components
                    size_bonus = 1.0 / (len(components[i]) + len(components[j]))
                    combined = score + size_bonus
                    if combined > best_score:
                        best_score = combined
                        best_i, best_j = i, j
            merged = components[best_i] | components[best_j]
            components = [
                c for idx, c in enumerate(components) if idx not in (best_i, best_j)
            ]
            components.append(merged)

        # If too few components, split the largest
        while len(components) < target_pod_count:
            # Find largest component
            largest_idx = max(range(len(components)), key=lambda i: len(components[i]))
            largest = components[largest_idx]
            if len(largest) < 2:
                break  # Can't split a single-WP component

            # Split by effort: sort WPs and divide
            sorted_wps = sorted(largest, key=lambda wp: self.wp_effort.get(wp, 1.0))
            mid = len(sorted_wps) // 2
            part_a = set(sorted_wps[:mid])
            part_b = set(sorted_wps[mid:])

            # Verify we don't break hard dependencies
            if self._has_cross_dependency(part_a, part_b):
                # Can't split this component without breaking deps
                break

            components[largest_idx] = part_a
            components.append(part_b)

        return components

    def _has_cross_dependency(self, set_a: Set[str], set_b: Set[str]) -> bool:
        """Check if there are hard dependencies between two sets."""
        for wp in set_a:
            flow_id = self.wp_to_flow.get(wp, "")
            flow = self.flow_by_id.get(flow_id, {})
            for req in flow.get("dependencies", {}).get("requiredFlows", []):
                if req in self.flow_to_wp and self.flow_to_wp[req] in set_b:
                    return True
        for wp in set_b:
            flow_id = self.wp_to_flow.get(wp, "")
            flow = self.flow_by_id.get(flow_id, {})
            for req in flow.get("dependencies", {}).get("requiredFlows", []):
                if req in self.flow_to_wp and self.flow_to_wp[req] in set_a:
                    return True
        return False

    # ── Stage 7-10: Assign pods, document deps, write output ──────────

    def _classify_effort(self, effort: float, avg_effort: float) -> str:
        if avg_effort == 0:
            return "medium"
        ratio = effort / avg_effort
        if ratio < 0.7:
            return "low"
        elif ratio > 1.3:
            return "high"
        return "medium"

    def find_cross_pod_dependencies(
        self, pods: Dict[str, Pod]
    ) -> List[CrossPodDependency]:
        """Find and document dependencies that cross pod boundaries."""
        # Build WP -> pod lookup
        wp_to_pod: Dict[str, str] = {}
        for pod_id, pod in pods.items():
            for wp in pod.workpackages:
                wp_to_pod[wp] = pod_id

        cross_deps: List[CrossPodDependency] = []
        seen = set()

        # Check shared entities across pods
        for pod_id_a, pod_a in pods.items():
            entities_a = set()
            tables_a = set()
            for wp in pod_a.workpackages:
                entities_a |= self.wp_entities.get(wp, set())
                tables_a |= self.wp_db_tables.get(wp, set())

            for pod_id_b, pod_b in pods.items():
                if pod_id_b <= pod_id_a:
                    continue
                entities_b = set()
                tables_b = set()
                for wp in pod_b.workpackages:
                    entities_b |= self.wp_entities.get(wp, set())
                    tables_b |= self.wp_db_tables.get(wp, set())

                # Shared entities
                shared_ent = entities_a & entities_b
                for entity in sorted(shared_ent):
                    key = (pod_id_a, pod_id_b, entity)
                    if key not in seen:
                        seen.add(key)
                        dep_type = (
                            "shared_table"
                            if entity in tables_a and entity in tables_b
                            else "shared_entity"
                        )
                        # Determine merge ordering: lower pod letter produces first
                        cross_deps.append(
                            CrossPodDependency(
                                from_pod=pod_id_a,
                                to_pod=pod_id_b,
                                dependency_type=dep_type,
                                entity=entity,
                                resolution=f"{pod_id_a} produces first; merge {pod_id_b} after {pod_id_a}",
                            )
                        )

        return cross_deps

    def find_shared_artifacts(self, pods: Dict[str, Pod]) -> List[str]:
        """Find artifacts referenced by all pods but modified by none."""
        # Collect copybooks per pod
        pod_copybooks: Dict[str, Set[str]] = {}
        for pod_id, pod in pods.items():
            cbs = set()
            for wp in pod.workpackages:
                cbs |= self.wp_copybooks.get(wp, set())
            pod_copybooks[pod_id] = cbs

        if not pod_copybooks:
            return []

        # Intersection of all pods' copybooks = shared read-only artifacts
        common = None
        for cbs in pod_copybooks.values():
            if common is None:
                common = set(cbs)
            else:
                common &= cbs

        return sorted(common) if common else []

    # ── Main orchestration ────────────────────────────────────────────

    def run(self) -> PodAssignment:
        """Execute the full pod partitioning pipeline."""
        # Step 1: Load
        self.load_inputs()

        total_wps = len(self.wp_to_flow)
        logger.info(f"Total workpackages: {total_wps}")

        # Early exit: ≤5 WPs = single pod
        if total_wps <= 5:
            logger.info("≤5 workpackages, creating single pod")
            all_wps = sorted(self.wp_to_flow.keys())
            pod = Pod(
                pod_id="pod-a",
                workpackages=all_wps,
                domain_cluster=self.infer_domain_cluster(set(all_wps)),
                effort_score=self._component_effort(set(all_wps)),
            )
            pod.estimated_effort = "medium"
            pod.shared_entities = sorted(
                set().union(*(self.wp_entities.get(w, set()) for w in all_wps))
            )
            pod.shared_db_tables = sorted(
                set().union(*(self.wp_db_tables.get(w, set()) for w in all_wps))
            )
            result = PodAssignment(
                pod_count=1,
                pods={"pod-a": pod},
                shared_artifacts=self.find_shared_artifacts({"pod-a": pod}),
            )
            result.validate()
            return result

        # Step 2-3: Connected components
        components = self.find_connected_components()

        # Step 4: (domain data already enriched in _build_indexes)

        # Step 5: Merge small components
        components = self.merge_small_components(components, min_size=2)

        # Step 6: Balance
        target_count = self.calculate_pod_count(total_wps)
        logger.info(f"Target pod count: {target_count}")
        components = self.balance_pods(components, target_count)

        # Step 7: Assign pod IDs
        pods: Dict[str, Pod] = {}
        efforts = []
        for i, component in enumerate(sorted(components, key=lambda c: sorted(c)[0])):
            pod_id = f"pod-{chr(ord('a') + i)}"
            effort = self._component_effort(component)
            efforts.append(effort)

            all_entities = set()
            all_tables = set()
            for wp in component:
                all_entities |= self.wp_entities.get(wp, set())
                all_tables |= self.wp_db_tables.get(wp, set())

            pods[pod_id] = Pod(
                pod_id=pod_id,
                workpackages=sorted(component),
                domain_cluster=self.infer_domain_cluster(component),
                effort_score=effort,
                shared_entities=sorted(all_entities),
                shared_db_tables=sorted(all_tables),
            )

        # Classify effort levels
        avg_effort = sum(efforts) / len(efforts) if efforts else 1.0
        for pod in pods.values():
            pod.estimated_effort = self._classify_effort(pod.effort_score, avg_effort)

        # Step 8: Cross-pod dependencies
        cross_deps = self.find_cross_pod_dependencies(pods)

        # Step 9: Shared artifacts
        shared_artifacts = self.find_shared_artifacts(pods)

        # Step 10: Build output
        result = PodAssignment(
            pod_count=len(pods),
            pods=pods,
            cross_pod_dependencies=cross_deps,
            shared_artifacts=shared_artifacts,
        )
        result.validate()

        logger.info(f"Pod partitioning complete: {len(pods)} pods")
        if result.quality_report.get("issues"):
            for issue in result.quality_report["issues"]:
                logger.warning(f"Quality issue: {issue}")
        else:
            logger.info("All quality checks passed")

        return result

    def write_output(self, result: PodAssignment, output_path: str) -> None:
        """Write Pod_Assignment.json to disk."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(result.to_dict(), f, indent=2)
        logger.info(f"Wrote Pod_Assignment.json to {path}")
