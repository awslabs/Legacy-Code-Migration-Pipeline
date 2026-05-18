"""Data models for pod partitioning."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class CrossPodDependency:
    """A dependency that crosses pod boundaries."""
    from_pod: str
    to_pod: str
    dependency_type: str  # shared_entity | shared_table | data_flow
    entity: str
    resolution: str = ""


@dataclass
class Pod:
    """A pod containing workpackages for parallel execution."""
    pod_id: str
    workpackages: List[str] = field(default_factory=list)
    domain_cluster: str = ""
    estimated_effort: str = "medium"  # low | medium | high
    shared_entities: List[str] = field(default_factory=list)
    shared_db_tables: List[str] = field(default_factory=list)
    # Internal tracking
    effort_score: float = 0.0

    def to_dict(self) -> dict:
        return {
            "workpackages": self.workpackages,
            "domain_cluster": self.domain_cluster,
            "estimated_effort": self.estimated_effort,
            "shared_entities": self.shared_entities,
            "shared_db_tables": self.shared_db_tables,
        }


@dataclass
class PodAssignment:
    """Complete pod assignment output."""
    version: str = "1.0"
    created: str = ""
    pod_count: int = 0
    pods: Dict[str, Pod] = field(default_factory=dict)
    cross_pod_dependencies: List[CrossPodDependency] = field(default_factory=list)
    shared_artifacts: List[str] = field(default_factory=list)
    # Metadata for LLM refinement
    quality_report: Dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.created:
            self.created = datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "created": self.created,
            "pod_count": self.pod_count,
            "pod_assignments": {
                pod_id: pod.to_dict() for pod_id, pod in self.pods.items()
            },
            "cross_pod_dependencies": [
                {
                    "from_pod": d.from_pod,
                    "to_pod": d.to_pod,
                    "dependency_type": d.dependency_type,
                    "entity": d.entity,
                    "resolution": d.resolution,
                }
                for d in self.cross_pod_dependencies
            ],
            "shared_artifacts": self.shared_artifacts,
        }

    def validate(self) -> Dict[str, any]:
        """Run quality checks and return report."""
        issues = []
        all_wps = []
        for pod in self.pods.values():
            all_wps.extend(pod.workpackages)

        # Check duplicates
        if len(all_wps) != len(set(all_wps)):
            seen = set()
            dupes = [w for w in all_wps if w in seen or seen.add(w)]
            issues.append(f"Duplicate workpackage assignments: {dupes}")

        # Check pod count
        if self.pod_count != len(self.pods):
            issues.append(
                f"pod_count ({self.pod_count}) != actual pods ({len(self.pods)})"
            )

        # Check effort balance
        efforts = [p.effort_score for p in self.pods.values() if p.effort_score > 0]
        if efforts:
            avg = sum(efforts) / len(efforts)
            for pod_id, pod in self.pods.items():
                if avg > 0 and abs(pod.effort_score - avg) / avg > 0.30:
                    issues.append(
                        f"Pod {pod_id} effort ({pod.effort_score:.1f}) "
                        f"deviates >30% from average ({avg:.1f})"
                    )

        self.quality_report = {
            "total_workpackages_assigned": len(all_wps),
            "unique_workpackages": len(set(all_wps)),
            "pod_count": len(self.pods),
            "cross_pod_dependency_count": len(self.cross_pod_dependencies),
            "issues": issues,
            "passed": len(issues) == 0,
        }
        return self.quality_report
