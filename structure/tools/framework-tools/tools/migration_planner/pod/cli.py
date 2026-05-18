"""CLI for pod partitioning."""

import argparse
import json
import logging
import sys
from pathlib import Path

from .pod_partitioner import PodPartitioner


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        prog="pod-partitioner",
        description="Partition workpackages into pods for parallel migration execution",
    )
    parser.add_argument(
        "--workpackage-planning",
        required=True,
        help="Path to Workpackage_Planning.json",
    )
    parser.add_argument(
        "--business-flows",
        required=True,
        help="Path to Business_Flows.json",
    )
    parser.add_argument(
        "--module-classifications",
        default=None,
        help="Path to Module_Classifications.json (optional)",
    )
    parser.add_argument(
        "--db-analysis",
        default=None,
        help="Path to DB_Source_Analysis_Report.md (optional)",
    )
    parser.add_argument(
        "--output",
        default="./output/analysis/workpackages/Pod_Assignment.json",
        help="Output path for Pod_Assignment.json",
    )
    parser.add_argument(
        "--pod-count",
        type=int,
        default=None,
        help="Override pod count (default: auto-calculated)",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
    )
    return parser.parse_args(args)


def main(args=None) -> int:
    parsed = parse_args(args)
    logging.basicConfig(
        level=getattr(logging, parsed.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        partitioner = PodPartitioner(
            workpackage_planning_path=parsed.workpackage_planning,
            business_flows_path=parsed.business_flows,
            module_classifications_path=parsed.module_classifications,
            db_analysis_path=parsed.db_analysis,
            pod_count_override=parsed.pod_count,
        )
        result = partitioner.run()
        partitioner.write_output(result, parsed.output)

        # Print summary
        report = result.quality_report
        print(f"\nPod Partitioning Complete")
        print(f"  Pods: {result.pod_count}")
        print(f"  Workpackages assigned: {report.get('total_workpackages_assigned', 0)}")
        print(f"  Cross-pod dependencies: {report.get('cross_pod_dependency_count', 0)}")
        print(f"  Quality: {'PASSED' if report.get('passed') else 'ISSUES FOUND'}")
        if not report.get("passed"):
            for issue in report.get("issues", []):
                print(f"    ⚠ {issue}")
        print(f"\nOutput: {parsed.output}")
        return 0

    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
