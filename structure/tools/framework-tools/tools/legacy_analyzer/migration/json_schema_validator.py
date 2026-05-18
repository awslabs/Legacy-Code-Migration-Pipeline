"""
JSON Schema Validator for Migration Flow Exports

This module provides validation functionality for migration flow JSON exports.
It ensures that exported JSON conforms to the expected schema with proper
field names (camelCase), types, and structure.
"""

import re
from typing import Dict, List, Any, Optional, Tuple


class JSONSchemaValidator:
    """
    Validates migration flow JSON exports against expected schema.
    
    This validator checks:
    1. Field names use camelCase convention
    2. Field types match expected types
    3. Required fields are present
    4. Programs are sorted alphabetically in scope
    """
    
    # Expected field types for different sections
    PROGRAM_FIELDS = {
        'name': str,
        'filePath': (str, type(None)),  # Optional
        'startLine': (int, type(None)),  # Optional
        'endLine': (int, type(None)),  # Optional
        'programType': (str, type(None)),  # Optional
        'language': (str, type(None)),  # Optional
        'is_utility': (bool, type(None))  # Optional, only with extended_scope
    }
    
    COPYBOOK_FIELDS = {
        'name': str,
        'filePath': (str, type(None))  # Optional
    }
    
    ENTRY_TYPE_FIELDS = {
        'entryType': str,
        'callers': list
    }
    
    CALLER_FIELDS = {
        'source': str,
        'filePath': (str, type(None)),  # Optional
        'metadata': (dict, type(None))  # Optional
    }
    
    DEPENDENCY_FIELDS = {
        'flowId': str,
        'entryProgram': str,
        'filePath': (str, type(None))  # Optional
    }
    
    INTERFACE_FIELDS = {
        'direction': str,
        'interfaceType': str,
        'source': str,
        'target': str,
        'external': bool,
        'metadata': (dict, type(None))  # Optional
    }
    
    DATA_OPERATION_FIELDS = {
        'operationCategory': str,
        'operationType': str,
        'dbType': (str, type(None)),  # Optional
        'target': str,
        'program': str,
        'mode': (str, type(None))  # Optional
    }
    
    FLOW_FIELDS = {
        'flowId': str,
        'name': str,
        'entryPoint': dict,  # Contains 'program', 'types', and optionally 'primaryType'
        'scope': dict,
        'interfaces': dict,
        'dataOperations': dict,
        'invokedByJobs': list,
        'dependencies': dict,
        'complexity': dict,
        'priority': (int, type(None)),  # Optional
        'businessDomain': (str, type(None)),  # Optional
    }
    
    @staticmethod
    def is_camel_case(field_name: str) -> bool:
        """
        Check if a field name follows camelCase convention.
        
        Args:
            field_name: Field name to check
            
        Returns:
            True if field name is camelCase, False otherwise
            
        Notes:
            - Allows lowercase start (camelCase)
            - Allows underscores for special cases (is_utility)
            - Does not allow uppercase start (PascalCase)
            - Does not allow snake_case (except is_utility for backward compatibility)
        """
        # Special case: is_utility is allowed for backward compatibility
        if field_name == 'is_utility':
            return True
        
        # Check for snake_case (not allowed except is_utility)
        if '_' in field_name:
            return False
        
        # Check for PascalCase (not allowed)
        if field_name[0].isupper():
            return False
        
        # Must start with lowercase letter
        if not field_name[0].islower():
            return False
        
        # Valid camelCase pattern: starts with lowercase, may contain uppercase
        return True
    
    @staticmethod
    def validate_field_type(
        field_name: str,
        field_value: Any,
        expected_type: Any
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that a field value matches the expected type.
        
        Args:
            field_name: Name of the field being validated
            field_value: Value to validate
            expected_type: Expected type (can be a tuple of types for optional fields)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Handle tuple of types (for optional fields)
        if isinstance(expected_type, tuple):
            if isinstance(field_value, expected_type):
                return True, None
            type_names = ' or '.join(t.__name__ for t in expected_type)
            return False, f"Field '{field_name}' has type {type(field_value).__name__}, expected {type_names}"
        
        # Handle single type
        if isinstance(field_value, expected_type):
            return True, None
        
        return False, f"Field '{field_name}' has type {type(field_value).__name__}, expected {expected_type.__name__}"
    
    def validate_program(self, program: Dict[str, Any]) -> List[str]:
        """
        Validate a program object.
        
        Args:
            program: Program dictionary to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Check required field
        if 'name' not in program:
            errors.append("Program missing required field 'name'")
            return errors
        
        # Validate field names are camelCase
        for field_name in program.keys():
            if not self.is_camel_case(field_name):
                errors.append(f"Program field '{field_name}' is not camelCase")
        
        # Validate field types
        for field_name, field_value in program.items():
            if field_name in self.PROGRAM_FIELDS:
                expected_type = self.PROGRAM_FIELDS[field_name]
                is_valid, error_msg = self.validate_field_type(
                    field_name, field_value, expected_type
                )
                if not is_valid:
                    errors.append(f"Program: {error_msg}")
        
        return errors
    
    def validate_copybook(self, copybook: Dict[str, Any]) -> List[str]:
        """
        Validate a copybook object.
        
        Args:
            copybook: Copybook dictionary to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Check required field
        if 'name' not in copybook:
            errors.append("Copybook missing required field 'name'")
            return errors
        
        # Validate field names are camelCase
        for field_name in copybook.keys():
            if not self.is_camel_case(field_name):
                errors.append(f"Copybook field '{field_name}' is not camelCase")
        
        # Validate field types
        for field_name, field_value in copybook.items():
            if field_name in self.COPYBOOK_FIELDS:
                expected_type = self.COPYBOOK_FIELDS[field_name]
                is_valid, error_msg = self.validate_field_type(
                    field_name, field_value, expected_type
                )
                if not is_valid:
                    errors.append(f"Copybook: {error_msg}")
        
        return errors
    
    def validate_caller(self, caller: Dict[str, Any]) -> List[str]:
        """
        Validate a caller object.
        
        Args:
            caller: Caller dictionary to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Check required field
        if 'source' not in caller:
            errors.append("Caller missing required field 'source'")
            return errors
        
        # Validate field names are camelCase
        for field_name in caller.keys():
            if not self.is_camel_case(field_name):
                errors.append(f"Caller field '{field_name}' is not camelCase")
        
        # Validate field types
        for field_name, field_value in caller.items():
            if field_name in self.CALLER_FIELDS:
                expected_type = self.CALLER_FIELDS[field_name]
                is_valid, error_msg = self.validate_field_type(
                    field_name, field_value, expected_type
                )
                if not is_valid:
                    errors.append(f"Caller: {error_msg}")
        
        return errors
    
    def validate_dependency(self, dependency: Dict[str, Any]) -> List[str]:
        """
        Validate a dependency object.
        
        Args:
            dependency: Dependency dictionary to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Check required fields
        required_fields = ['flowId', 'entryProgram']
        for field in required_fields:
            if field not in dependency:
                errors.append(f"Dependency missing required field '{field}'")
        
        if errors:
            return errors
        
        # Validate field names are camelCase
        for field_name in dependency.keys():
            if not self.is_camel_case(field_name):
                errors.append(f"Dependency field '{field_name}' is not camelCase")
        
        # Validate field types
        for field_name, field_value in dependency.items():
            if field_name in self.DEPENDENCY_FIELDS:
                expected_type = self.DEPENDENCY_FIELDS[field_name]
                is_valid, error_msg = self.validate_field_type(
                    field_name, field_value, expected_type
                )
                if not is_valid:
                    errors.append(f"Dependency: {error_msg}")
        
        return errors
    
    def validate_interface(self, interface: Dict[str, Any]) -> List[str]:
        """
        Validate an interface object.
        
        Args:
            interface: Interface dictionary to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Check required fields
        required_fields = ['direction', 'interfaceType', 'source', 'target', 'external']
        for field in required_fields:
            if field not in interface:
                errors.append(f"Interface missing required field '{field}'")
        
        if errors:
            return errors
        
        # Validate field names are camelCase
        for field_name in interface.keys():
            if not self.is_camel_case(field_name):
                errors.append(f"Interface field '{field_name}' is not camelCase")
        
        # Validate field types
        for field_name, field_value in interface.items():
            if field_name in self.INTERFACE_FIELDS:
                expected_type = self.INTERFACE_FIELDS[field_name]
                is_valid, error_msg = self.validate_field_type(
                    field_name, field_value, expected_type
                )
                if not is_valid:
                    errors.append(f"Interface: {error_msg}")
        
        return errors
    
    def validate_data_operation(self, operation: Dict[str, Any]) -> List[str]:
        """
        Validate a data operation object.
        
        Args:
            operation: Data operation dictionary to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Check required fields
        required_fields = ['operationCategory', 'operationType', 'target', 'program']
        for field in required_fields:
            if field not in operation:
                errors.append(f"Data operation missing required field '{field}'")
        
        if errors:
            return errors
        
        # Validate field names are camelCase
        for field_name in operation.keys():
            if not self.is_camel_case(field_name):
                errors.append(f"Data operation field '{field_name}' is not camelCase")
        
        # Validate field types
        for field_name, field_value in operation.items():
            if field_name in self.DATA_OPERATION_FIELDS:
                expected_type = self.DATA_OPERATION_FIELDS[field_name]
                is_valid, error_msg = self.validate_field_type(
                    field_name, field_value, expected_type
                )
                if not is_valid:
                    errors.append(f"Data operation: {error_msg}")
        
        return errors
    
    def validate_scope(self, scope: Dict[str, Any]) -> List[str]:
        """
        Validate a scope object.
        
        Args:
            scope: Scope dictionary to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Validate field names are camelCase
        for field_name in scope.keys():
            if not self.is_camel_case(field_name):
                errors.append(f"Scope field '{field_name}' is not camelCase")
        
        # Validate programs
        if 'programs' in scope:
            if not isinstance(scope['programs'], list):
                errors.append("Scope 'programs' must be a list")
            else:
                # Validate alphabetical ordering
                order_errors = self.validate_alphabetical_order(
                    scope['programs'], 'Programs'
                )
                errors.extend(order_errors)
                
                # Validate each program
                for i, program in enumerate(scope['programs']):
                    if isinstance(program, dict):
                        prog_errors = self.validate_program(program)
                        errors.extend([f"Program {i}: {e}" for e in prog_errors])
        
        # Validate copybooks
        if 'copybooks' in scope:
            if not isinstance(scope['copybooks'], list):
                errors.append("Scope 'copybooks' must be a list")
            else:
                # Validate alphabetical ordering
                order_errors = self.validate_alphabetical_order(
                    scope['copybooks'], 'Copybooks'
                )
                errors.extend(order_errors)
                
                # Validate each copybook
                for i, copybook in enumerate(scope['copybooks']):
                    if isinstance(copybook, dict):
                        cb_errors = self.validate_copybook(copybook)
                        errors.extend([f"Copybook {i}: {e}" for e in cb_errors])
        
        # Validate datasets (should be list of strings)
        if 'datasets' in scope:
            if not isinstance(scope['datasets'], list):
                errors.append("Scope 'datasets' must be a list")
            else:
                for i, dataset in enumerate(scope['datasets']):
                    if not isinstance(dataset, str):
                        errors.append(f"Dataset {i} must be a string")
        
        return errors
    
    def validate_alphabetical_order(self, items: List[Any], item_type: str) -> List[str]:
        """
        Validate that items are sorted alphabetically by name.
        
        Args:
            items: List of items to check (can be strings or dicts with 'name' field)
            item_type: Type of items for error messages (e.g., 'programs', 'copybooks')
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        if not items:
            return errors
        
        # Extract names
        names = []
        for item in items:
            if isinstance(item, str):
                names.append(item)
            elif isinstance(item, dict) and 'name' in item:
                names.append(item['name'])
            else:
                # Can't validate ordering if we can't extract names
                return errors
        
        # Check if sorted
        sorted_names = sorted(names)
        if names != sorted_names:
            errors.append(f"{item_type} are not sorted alphabetically")
        
        return errors
    
    def validate_flow(self, flow: Dict[str, Any]) -> List[str]:
        """
        Validate a complete flow object.
        
        Args:
            flow: Flow dictionary to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Check required fields
        required_fields = ['flowId', 'name', 'entryPoint']
        for field in required_fields:
            if field not in flow:
                errors.append(f"Flow missing required field '{field}'")
        
        # Validate field names are camelCase
        for field_name in flow.keys():
            if not self.is_camel_case(field_name):
                errors.append(f"Flow field '{field_name}' is not camelCase")
        
        # Validate field types for known fields
        for field_name, field_value in flow.items():
            if field_name in self.FLOW_FIELDS:
                expected_type = self.FLOW_FIELDS[field_name]
                is_valid, error_msg = self.validate_field_type(
                    field_name, field_value, expected_type
                )
                if not is_valid:
                    errors.append(f"Flow: {error_msg}")
        
        # Validate scope
        if 'scope' in flow and isinstance(flow['scope'], dict):
            scope_errors = self.validate_scope(flow['scope'])
            errors.extend(scope_errors)
            
            # Validate alphabetical ordering of programs
            if 'programs' in flow['scope']:
                order_errors = self.validate_alphabetical_order(
                    flow['scope']['programs'], 'Programs'
                )
                errors.extend(order_errors)
            
            # Validate alphabetical ordering of copybooks
            if 'copybooks' in flow['scope']:
                order_errors = self.validate_alphabetical_order(
                    flow['scope']['copybooks'], 'Copybooks'
                )
                errors.extend(order_errors)
        
        # Validate entry types
        if 'entryTypes' in flow and isinstance(flow['entryTypes'], list):
            for i, entry_type in enumerate(flow['entryTypes']):
                if isinstance(entry_type, dict):
                    # Validate callers
                    if 'callers' in entry_type and isinstance(entry_type['callers'], list):
                        for j, caller in enumerate(entry_type['callers']):
                            if isinstance(caller, dict):
                                caller_errors = self.validate_caller(caller)
                                errors.extend([f"Entry type {i}, caller {j}: {e}" for e in caller_errors])
        
        # Validate dependencies
        if 'dependencies' in flow and isinstance(flow['dependencies'], dict):
            for dep_type in ['requiredFlows', 'dependentFlows']:
                if dep_type in flow['dependencies']:
                    deps = flow['dependencies'][dep_type]
                    if isinstance(deps, list):
                        for i, dep in enumerate(deps):
                            if isinstance(dep, dict):
                                dep_errors = self.validate_dependency(dep)
                                errors.extend([f"{dep_type} {i}: {e}" for e in dep_errors])
        
        # Validate interfaces
        if 'interfaces' in flow and isinstance(flow['interfaces'], dict):
            for iface_type in ['inbound', 'outbound']:
                if iface_type in flow['interfaces']:
                    ifaces = flow['interfaces'][iface_type]
                    if isinstance(ifaces, list):
                        for i, iface in enumerate(ifaces):
                            if isinstance(iface, dict):
                                iface_errors = self.validate_interface(iface)
                                errors.extend([f"{iface_type} interface {i}: {e}" for e in iface_errors])
        
        # Validate data operations
        if 'dataOperations' in flow and isinstance(flow['dataOperations'], dict):
            for op_type in ['reads', 'writes', 'updates', 'deletes']:
                if op_type in flow['dataOperations']:
                    ops = flow['dataOperations'][op_type]
                    if isinstance(ops, list):
                        for i, op in enumerate(ops):
                            if isinstance(op, dict):
                                op_errors = self.validate_data_operation(op)
                                errors.extend([f"{op_type} operation {i}: {e}" for e in op_errors])
        
        return errors
    
    def validate_export(self, export_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a complete flow export.
        
        Args:
            export_data: Complete export dictionary with 'flows' key
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check top-level structure
        if not isinstance(export_data, dict):
            return False, ["Export data must be a dictionary"]
        
        if 'flows' not in export_data:
            return False, ["Export data missing 'flows' key"]
        
        if not isinstance(export_data['flows'], list):
            return False, ["'flows' must be a list"]
        
        # Validate each flow
        for i, flow in enumerate(export_data['flows']):
            if isinstance(flow, dict):
                flow_errors = self.validate_flow(flow)
                errors.extend([f"Flow {i}: {e}" for e in flow_errors])
        
        is_valid = len(errors) == 0
        return is_valid, errors
