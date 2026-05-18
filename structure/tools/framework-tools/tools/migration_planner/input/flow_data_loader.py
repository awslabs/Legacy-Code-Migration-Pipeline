"""Input module for loading and validating business flow data."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from ..models import BusinessFlow, Program


logger = logging.getLogger(__name__)


class FlowDataLoader:
    """Loads and validates business flow data from JSON files."""
    
    def __init__(self):
        """Initialize the flow data loader."""
        self.classifications: Dict[str, str] = {}
    
    def load_flows(self, flows_path: Path) -> List[BusinessFlow]:
        """
        Load and validate Business_Flows.json.
        
        Args:
            flows_path: Path to Business_Flows.json file
            
        Returns:
            List of validated BusinessFlow objects
            
        Raises:
            FileNotFoundError: If flows file does not exist
            ValueError: If JSON is invalid or required fields are missing
        """
        logger.info(f"Loading flows from {flows_path}")
        
        if not flows_path.exists():
            raise FileNotFoundError(f"Flows file not found: {flows_path}")
        
        try:
            with open(flows_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in flows file: {e}")
        
        if not isinstance(data, dict) or 'flows' not in data:
            raise ValueError("Flows file must contain a 'flows' array")
        
        flows_data = data['flows']
        if not isinstance(flows_data, list):
            raise ValueError("'flows' must be an array")
        
        flows = []
        for flow_data in flows_data:
            try:
                flow = self.validate_flow(flow_data)
                flows.append(flow)
            except ValueError as e:
                flow_id = flow_data.get('flowId', 'UNKNOWN')
                raise ValueError(f"Error validating flow {flow_id}: {e}")
        
        logger.info(f"Successfully loaded {len(flows)} flows")
        return flows
    
    def validate_flow(self, flow_data: dict) -> BusinessFlow:
        """
        Validate a single flow has required fields and create BusinessFlow object.
        
        Args:
            flow_data: Dictionary containing flow data
            
        Returns:
            Validated BusinessFlow object
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Check required fields
        required_fields = ['flowId', 'scope', 'complexity', 'dependencies']
        for field in required_fields:
            if field not in flow_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Extract flowId
        flow_id = flow_data['flowId']
        if not isinstance(flow_id, str) or not flow_id:
            raise ValueError("flowId must be a non-empty string")
        
        # Extract name (optional, default to flowId)
        name = flow_data.get('name', flow_id)
        
        # Extract and validate scope.programs
        scope = flow_data['scope']
        if not isinstance(scope, dict):
            raise ValueError("scope must be an object")
        
        if 'programs' not in scope:
            raise ValueError("Missing required field: scope.programs")
        
        programs_data = scope['programs']
        if not isinstance(programs_data, list):
            raise ValueError("scope.programs must be an array")
        
        programs = []
        for prog_data in programs_data:
            if not isinstance(prog_data, dict):
                raise ValueError("Each program must be an object")
            if 'name' not in prog_data:
                raise ValueError("Each program must have a 'name' field")
            
            prog_name = prog_data['name']
            is_utility = prog_data.get('isUtility', False)
            programs.append(Program(name=prog_name, is_utility=is_utility))
        
        # Extract complexity
        complexity = flow_data['complexity']
        if not isinstance(complexity, dict):
            raise ValueError("complexity must be an object")
        
        # Extract totalPrograms (required)
        if 'totalPrograms' not in complexity:
            raise ValueError("Missing required field: complexity.totalPrograms")
        
        total_programs = complexity['totalPrograms']
        if not isinstance(total_programs, int) or total_programs < 0:
            raise ValueError("complexity.totalPrograms must be a non-negative integer")
        
        # Extract compositeScore (optional, default to 0)
        composite_score = complexity.get('compositeScore', 0.0)
        if not isinstance(composite_score, (int, float)):
            composite_score = 0.0
        
        # Extract dependencies
        dependencies = flow_data['dependencies']
        if not isinstance(dependencies, dict):
            raise ValueError("dependencies must be an object")
        
        # Extract requiredFlows (optional, default to empty list)
        required_flows = dependencies.get('requiredFlows', [])
        if not isinstance(required_flows, list):
            raise ValueError("dependencies.requiredFlows must be an array")
        
        # Extract dependentFlows (optional, default to empty list)
        dependent_flows = dependencies.get('dependentFlows', [])
        if not isinstance(dependent_flows, list):
            raise ValueError("dependencies.dependentFlows must be an array")
        
        # Extract dataOperations.databases (optional, default to empty list)
        databases = []
        if 'dataOperations' in flow_data:
            data_ops = flow_data['dataOperations']
            if isinstance(data_ops, dict) and 'databases' in data_ops:
                databases = data_ops['databases']
                if not isinstance(databases, list):
                    databases = []
        
        # Create and return BusinessFlow object
        return BusinessFlow(
            flow_id=flow_id,
            name=name,
            programs=programs,
            databases=databases,
            total_programs=total_programs,
            composite_score=float(composite_score),
            required_flows=required_flows,
            dependent_flows=dependent_flows
        )
    
    def load_classifications(self, classifications_path: Optional[Path]) -> Dict[str, str]:
        """
        Load Module_Classifications.json if provided.
        
        Args:
            classifications_path: Path to Module_Classifications.json file (optional)
            
        Returns:
            Dictionary mapping program names to classifications
        """
        if classifications_path is None:
            logger.info("No classifications file provided, using empty classifications")
            self.classifications = {}
            return self.classifications
        
        if not classifications_path.exists():
            logger.warning(f"Classifications file not found: {classifications_path}, using empty classifications")
            self.classifications = {}
            return self.classifications
        
        try:
            logger.info(f"Loading classifications from {classifications_path}")
            with open(classifications_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, dict):
                logger.warning("Classifications file must be a JSON object, using empty classifications")
                self.classifications = {}
                return self.classifications
            
            # Extract classifications mapping
            # Expected format: {"programName": "COMMONLY_USED", ...}
            self.classifications = {k: v for k, v in data.items() if isinstance(v, str)}
            
            logger.info(f"Successfully loaded {len(self.classifications)} classifications")
            return self.classifications
            
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON in classifications file: {e}, using empty classifications")
            self.classifications = {}
            return self.classifications
        except Exception as e:
            logger.warning(f"Error loading classifications file: {e}, using empty classifications")
            self.classifications = {}
            return self.classifications

