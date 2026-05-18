"""
Inventory Manager - Handles complete inventory lifecycle.

This class is responsible for:
1. Discovering all source files
2. Extracting metadata (PROGRAM-IDs, etc.)
3. Creating and populating inventory tables
4. Providing complete artifact context for dependency analysis
"""

import os
import glob
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path
from collections import defaultdict

from .language_detector import LanguageDetector
from .models.artifact import Artifact, ArtifactType
from .analysis.mixed_content_detector import MixedContentDetector


class InventoryManager:
    """Manages complete inventory discovery and population."""
    
    # Language to file extension mapping
    LANGUAGE_EXTENSIONS = {
        'COBOL': ['.cbl', '.cob', '.cobol', '.cpy', '.CBL', '.COB', '.COBOL', '.CPY'],
        'PLI': ['.pli', '.pl1', '.inc', '.PLI', '.PL1', '.INC'],
        'JCL': ['.jcl', '.JCL'],
        'REXX': ['.rexx', '.rex', '.txt', '.REXX', '.REX', '.TXT'],
        'NATURAL': ['.nsp', '.nsn', '.nsc', '.nsl', '.nsg', '.nsd', '.nsa', '.ns8',
                    '.NSP', '.NSN', '.NSC', '.NSL', '.NSG', '.NSD', '.NSA', '.NS8'],
        'RPG': ['.rpg', '.rpgle', '.sqlrpgle', '.rpg38', '.mbr',
                '.RPG', '.RPGLE', '.SQLRPGLE', '.RPG38', '.MBR'],
        'ASM': ['.asm', '.s', '.mac', '.ASM', '.S', '.MAC']
    }
    
    def __init__(self, database: BaseDatabase):
        """Initialize inventory manager."""
        self.database = database
        self.language_detector = LanguageDetector()
        self.mixed_content_detector = MixedContentDetector()
        self.discovered_artifacts: List[Artifact] = []
        self.stats = defaultdict(int)
    
    def discover_all_files(self, directory: str) -> List[Artifact]:
        """
        Phase 1: Discover all source files in directory.
        
        Args:
            directory: Root directory to scan
            
        Returns:
            List of discovered artifacts (without metadata)
        """
        print(f"\n=== Phase 1: Discovering Files ===")
        print(f"Scanning directory: {directory}")
        
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        # Get all known extensions
        all_extensions = []
        for exts in self.LANGUAGE_EXTENSIONS.values():
            all_extensions.extend(exts)
        
        # Scan for all files
        discovered_files = []
        for ext in set(all_extensions):
            pattern = f"**/*{ext}"
            full_pattern = os.path.join(directory, pattern)
            matched_files = glob.glob(full_pattern, recursive=True)
            discovered_files.extend(matched_files)
        
        # Remove duplicates
        discovered_files = list(set(discovered_files))
        
        print(f"Found {len(discovered_files)} source files")
        
        # Create basic artifacts
        artifacts = []
        for file_path in discovered_files:
            try:
                artifact = self._create_basic_artifact(file_path)
                if artifact:
                    artifacts.append(artifact)
                    self.stats['files_discovered'] += 1
            except Exception as e:
                print(f"  ⚠ Warning: Error processing {file_path}: {str(e)}")
                self.stats['discovery_errors'] += 1
        
        self.discovered_artifacts = artifacts
        
        print(f"✓ Discovered {len(artifacts)} artifacts")
        if self.stats['discovery_errors'] > 0:
            print(f"⚠ Discovery errors: {self.stats['discovery_errors']}")
        
        return artifacts
    
    def extract_all_metadata(self) -> None:
        """
        Phase 2: Extract metadata from all discovered files.
        
        This includes:
        - PROGRAM-ID extraction
        - Program boundary detection
        - File size and modification dates
        - Language confirmation via content analysis
        """
        print(f"\n=== Phase 2: Extracting Metadata ===")
        print(f"Processing {len(self.discovered_artifacts)} artifacts...")
        
        processed = 0
        for artifact in self.discovered_artifacts:
            try:
                self._extract_artifact_metadata(artifact)
                processed += 1
                
                if processed % 100 == 0:
                    print(f"  Processed {processed}/{len(self.discovered_artifacts)} artifacts...")
                    
            except Exception as e:
                print(f"  ⚠ Warning: Error extracting metadata for {artifact.file_path}: {str(e)}")
                self.stats['metadata_errors'] += 1
        
        print(f"✓ Extracted metadata for {processed} artifacts")
        if self.stats['metadata_errors'] > 0:
            print(f"⚠ Metadata errors: {self.stats['metadata_errors']}")
    
    def create_inventory_schema(self) -> None:
        """
        Phase 3: Create inventory database schema.
        """
        print(f"\n=== Phase 3: Creating Inventory Schema ===")
        
        from shared.database.schemas import InventorySchema
        
        schema = InventorySchema()
        table_defs = schema.get_table_definitions()
        
        for table_name, table_def in table_defs.items():
            if self.database.table_exists(table_name):
                print(f"  ✓ Table {table_name} already exists")
            else:
                self.database.create_table(table_name, table_def)
                print(f"  ✓ Created table {table_name}")
        
        self.database.commit()
        print("✓ Inventory schema ready")
    
    def populate_complete_inventory(self, source_directory: str = None) -> None:
        """
        Phase 4: Populate inventory with complete artifact information.
        
        Args:
            source_directory: Optional source directory for specialized artifact parsing
        """
        print(f"\n=== Phase 4: Populating Inventory ===")
        
        # Filter out documentation artifacts
        code_artifacts = [artifact for artifact in self.discovered_artifacts 
                         if artifact.language != 'DOCUMENTATION']
        
        print(f"Storing {len(code_artifacts)} artifacts...")
        if len(code_artifacts) < len(self.discovered_artifacts):
            excluded = len(self.discovered_artifacts) - len(code_artifacts)
            print(f"  Excluded {excluded} documentation files")
        
        # Group artifacts by type for batch insertion
        artifacts_by_type = defaultdict(list)
        for artifact in code_artifacts:
            artifacts_by_type[artifact.artifact_type].append(artifact)
        
        # Insert each type
        total_inserted = 0
        for artifact_type, artifacts in artifacts_by_type.items():
            inserted = self._insert_artifacts_batch(artifact_type, artifacts)
            total_inserted += inserted
            print(f"  ✓ Inserted {inserted} {artifact_type.value} artifacts")
        
        self.database.commit()
        print(f"✓ Populated inventory with {total_inserted} artifacts")
        
        # Update stats
        self.stats['artifacts_stored'] = total_inserted
        
        # Phase 4b: Populate specialized tables if source directory provided
        if source_directory:
            self._populate_specialized_tables(source_directory)
    
    def get_complete_inventory(self) -> Dict[str, Artifact]:
        """
        Get complete inventory as a lookup dictionary.
        
        If discovered_artifacts is empty (e.g., when loading existing database),
        loads artifacts from the database.
        
        Returns:
            Dictionary mapping artifact names to Artifact objects
        """
        # If we have in-memory artifacts, use them
        if self.discovered_artifacts:
            artifact_map = {}
            for artifact in self.discovered_artifacts:
                # Use program_id as primary key if available, otherwise filename
                key = artifact.program_id if artifact.program_id else artifact.filename
                artifact_map[key] = artifact
            return artifact_map
        
        # Otherwise, load from database
        artifact_map = {}
        try:
            cursor = self.database.cursor()
            
            # Load basic inventory
            cursor.execute("""
                SELECT id, artifact_name, filename, artifact_type, language,
                       file_path, file_size, analyzed, last_modified
                FROM inventory
            """)
            
            # Create a map of file_id to artifact for program mapping
            file_id_to_artifact = {}
            
            for row in cursor.fetchall():
                file_id, artifact_name, filename, artifact_type_str, language, \
                file_path, file_size, analyzed, last_modified = row
                
                # Convert string artifact_type to enum
                # Handle legacy types that aren't in the enum
                if artifact_type_str in ['CSECT', 'MAIN']:
                    artifact_type = ArtifactType.PROGRAM
                else:
                    try:
                        artifact_type = ArtifactType(artifact_type_str)
                    except ValueError:
                        # Unknown type, skip it
                        print(f"⚠ Warning: Unknown artifact type '{artifact_type_str}' for {artifact_name}, skipping")
                        continue
                
                # Determine file extension from filename
                file_extension = ''
                if filename:
                    import os
                    file_extension = os.path.splitext(filename)[1]
                
                # Create artifact object
                artifact = Artifact(
                    artifact_name=artifact_name,
                    filename=filename,
                    artifact_type=artifact_type,
                    language=language,
                    file_extension=file_extension,
                    file_path=file_path,
                    file_size=file_size,
                    analyzed=bool(analyzed),
                    last_modified=last_modified
                )
                
                # Store by artifact_name for now
                artifact_map[artifact_name] = artifact
                file_id_to_artifact[file_id] = artifact
            
            # Load program names from program_file_mapping
            cursor.execute("""
                SELECT file_id, program_name
                FROM program_file_mapping
            """)
            
            for file_id, program_name in cursor.fetchall():
                if file_id in file_id_to_artifact:
                    artifact = file_id_to_artifact[file_id]
                    # Set program_id
                    artifact.program_id = program_name
                    # Also add to map by program_name
                    artifact_map[program_name] = artifact
        
        except Exception as e:
            print(f"⚠ Warning: Could not load inventory from database: {e}")
            import traceback
            traceback.print_exc()
            return {}
        
        return artifact_map
    
    def get_inventory_stats(self) -> Dict[str, int]:
        """Get inventory statistics with file-level and program-level counts."""
        stats = dict(self.stats)
        
        # Add artifact type counts
        type_counts = defaultdict(int)
        language_counts = defaultdict(int)
        
        for artifact in self.discovered_artifacts:
            type_counts[artifact.artifact_type.value] += 1
            language_counts[artifact.language] += 1
        
        stats.update(type_counts)
        stats.update(language_counts)
        
        # Calculate file-level statistics from database if available
        try:
            cursor = self.database.cursor()
            
            # Count multi-program files
            cursor.execute("SELECT COUNT(*) FROM inventory WHERE program_count > 1")
            stats['multi_program_files'] = cursor.fetchone()[0]
            
            # Count single-program files
            cursor.execute("SELECT COUNT(*) FROM inventory WHERE program_count = 1")
            stats['single_program_files'] = cursor.fetchone()[0]
            
            # Count mixed content files (where dominant_language or dominant_type is NULL but program_count > 1)
            cursor.execute("""
                SELECT COUNT(*) FROM inventory 
                WHERE program_count > 1 AND (dominant_language IS NULL OR dominant_type IS NULL)
            """)
            stats['mixed_content_files'] = cursor.fetchone()[0]
            
            # Count total programs from program_file_mapping
            cursor.execute("SELECT COUNT(*) FROM program_file_mapping")
            stats['total_programs'] = cursor.fetchone()[0]
            
        except Exception:
            # Database might not be populated yet
            pass
        
        return stats
    
    def _create_basic_artifact(self, file_path: str) -> Optional[Artifact]:
        """Create basic artifact from file path."""
        try:
            path_obj = Path(file_path)
            filename = path_obj.stem.upper()
            file_ext = path_obj.suffix.lower()
            
            # Detect language
            language = self._detect_language_from_extension(file_ext)
            if not language:
                return None
            
            # Determine artifact type
            artifact_type = self._determine_artifact_type(file_ext, language)
            
            # Get file size
            file_size = None
            try:
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
            except:
                pass
            
            return Artifact(
                artifact_name=filename,  # Will be updated with PROGRAM-ID if found
                filename=filename,
                artifact_type=artifact_type,
                language=language,
                file_extension=file_ext,
                file_path=file_path,
                file_size=file_size,
                analyzed=False  # Not analyzed yet
            )
            
        except Exception as e:
            print(f"  ⚠ Error creating artifact for {file_path}: {str(e)}")
            return None
    
    def _extract_artifact_metadata(self, artifact: Artifact) -> None:
        """Extract detailed metadata for an artifact."""
        try:
            # Read source code
            with open(artifact.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                source_code = f.read()
        except:
            return
        
        # Check for mixed content first
        if self.mixed_content_detector.is_mixed_content_file(source_code):
            # Handle mixed content file
            self._extract_mixed_content_metadata(artifact, source_code)
            return
        
        # Confirm language via content analysis for single-language files
        detected_language = self.language_detector.detect_language(
            artifact.file_path, source_code
        )
        if detected_language:
            artifact.language = detected_language
        elif detected_language is None and artifact.file_extension in ['.txt', '.TXT']:
            # If content analysis returns None for .txt files, it means it's likely documentation
            # Mark it for removal by setting a special flag
            artifact.language = 'DOCUMENTATION'
            return
        
        # Extract PROGRAM-ID for applicable languages
        if artifact.language in ['COBOL', 'PLI', 'NATURAL']:
            program_id = self._extract_program_id(source_code, artifact.language)
            if program_id:
                artifact.program_id = program_id
                # Use PROGRAM-ID as primary artifact name
                artifact.artifact_name = program_id
        
        # Get file modification time
        try:
            stat = os.stat(artifact.file_path)
            artifact.last_modified = stat.st_mtime
        except:
            pass
    
    def _detect_language_from_extension(self, file_ext: str) -> Optional[str]:
        """Detect language from file extension."""
        for language, extensions in self.LANGUAGE_EXTENSIONS.items():
            if file_ext in extensions:
                return language
        return None
    
    def _determine_artifact_type(self, file_ext: str, language: str) -> ArtifactType:
        """Determine artifact type from extension and language."""
        if file_ext in ['.cpy', '.copy', '.inc']:
            return ArtifactType.COPYBOOK
        elif language == 'JCL':
            return ArtifactType.JCL
        else:
            return ArtifactType.PROGRAM
    
    def _extract_program_id(self, source_code: str, language: str) -> Optional[str]:
        """Extract PROGRAM-ID from source code."""
        import re
        
        if language == 'COBOL':
            # Look for PROGRAM-ID
            pattern = r'PROGRAM-ID\.\s+([A-Z0-9\-]+)'
            match = re.search(pattern, source_code, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        
        elif language == 'PLI':
            # Look for procedure name
            pattern = r'^\s*([A-Z0-9_]+)\s*:\s*PROC'
            match = re.search(pattern, source_code, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1).upper()
        
        elif language == 'NATURAL':
            # Natural programs are identified by filename, not by a PROGRAM-ID statement.
            # Do not attempt to extract a program name from source content, as single-word
            # lines (LOCAL, INIT, END, etc.) are Natural keywords, not program identifiers.
            return None
        
        return None
    
    def _extract_mixed_content_metadata(self, artifact: Artifact, source_code: str) -> None:
        """Extract metadata for mixed content files (e.g., PDS format)."""
        # Detect program boundaries in mixed content
        boundaries = self.mixed_content_detector.detect_boundaries(artifact.file_path, source_code)
        
        if not boundaries:
            # No programs detected, treat as regular file
            return
        
        # Get content summary
        summary = self.mixed_content_detector.get_content_summary(boundaries)
        
        # Update artifact with mixed content information
        artifact.language = summary.get('overall_language', 'MIXED')
        artifact.program_count = summary.get('total_programs', len(boundaries))
        artifact.is_mixed_content = True
        
        # Store mixed content metadata
        artifact.mixed_content_summary = summary
        artifact.program_boundaries = boundaries
        
        # Set artifact name to filename for mixed content files
        artifact.artifact_name = artifact.filename
        
        # Get file modification time
        try:
            import os
            stat = os.stat(artifact.file_path)
            artifact.last_modified = stat.st_mtime
        except:
            pass
        
        # Update stats
        self.stats['mixed_content_files_detected'] += 1
    
    def _insert_artifacts_batch(self, artifact_type: ArtifactType, artifacts: List[Artifact]) -> int:
        """Insert artifacts in batch by type using file-level approach."""
        if not artifacts:
            return 0
        
        # Group artifacts by file path to handle multi-program files
        files_by_path = {}
        for artifact in artifacts:
            if artifact.file_path not in files_by_path:
                files_by_path[artifact.file_path] = []
            files_by_path[artifact.file_path].append(artifact)
        
        # Convert to file-level inventory entries
        unified_rows = []
        
        for file_path, file_artifacts in files_by_path.items():
            # Use the first artifact as the base for file-level data
            base_artifact = file_artifacts[0]
            
            # Calculate program count and determine dominant language/type
            # For mixed content files, use the detected program count
            if hasattr(base_artifact, 'is_mixed_content') and base_artifact.is_mixed_content:
                program_count = getattr(base_artifact, 'program_count', len(file_artifacts))
            else:
                program_count = len(file_artifacts) if artifact_type == ArtifactType.PROGRAM else 0
            
            dominant_language, dominant_type = self._determine_dominant_attributes(file_artifacts)
            
            # Determine final language and artifact_type based on dominance rules
            final_language = dominant_language if dominant_language else base_artifact.language
            final_artifact_type = dominant_type if dominant_type else artifact_type.value
            
            unified_row = {
                'artifact_name': base_artifact.filename,  # Use filename for file-level entry
                'filename': base_artifact.filename,
                'artifact_type': final_artifact_type,
                'language': final_language,
                'file_path': file_path,
                'file_size': base_artifact.file_size,
                'program_count': program_count,
                'dominant_language': dominant_language,
                'dominant_type': dominant_type,
                'analyzed': 0,  # Not analyzed yet
                'last_modified': base_artifact.last_modified
            }
            unified_rows.append(unified_row)
        
        # Insert into unified inventory table (file-level entries)
        self.database.insert_rows('inventory', unified_rows)
        
        return len(unified_rows)
    
    def _determine_dominant_attributes(self, artifacts: List[Artifact]) -> Tuple[Optional[str], Optional[str]]:
        """
        Determine dominant language and type for a file with multiple programs.
        
        Decision Rules:
        1. Single language/type: Use actual values
        2. Dominant (>50%): Use dominant values  
        3. No dominant: Use 'MIXED'
        
        Returns:
            Tuple of (dominant_language, dominant_type) or (None, None) if mixed
        """
        if len(artifacts) <= 1:
            return None, None  # Single program files don't need dominance
        
        # Count languages and types
        language_counts = {}
        type_counts = {}
        
        for artifact in artifacts:
            language_counts[artifact.language] = language_counts.get(artifact.language, 0) + 1
            type_counts[artifact.artifact_type.value] = type_counts.get(artifact.artifact_type.value, 0) + 1
        
        total_count = len(artifacts)
        
        # Determine dominant language
        dominant_language = None
        if len(language_counts) == 1:
            # Single language
            dominant_language = list(language_counts.keys())[0]
        else:
            # Check for >50% dominance
            for lang, count in language_counts.items():
                if count > total_count / 2:
                    dominant_language = lang
                    break
        
        # Determine dominant type
        dominant_type = None
        if len(type_counts) == 1:
            # Single type
            dominant_type = list(type_counts.keys())[0]
        else:
            # Check for >50% dominance
            for typ, count in type_counts.items():
                if count > total_count / 2:
                    dominant_type = typ
                    break
        
        return dominant_language, dominant_type
    
    def _populate_specialized_tables(self, source_directory: str) -> None:
        """
        Populate specialized inventory tables from artifacts and source files.
        
        This method:
        1. Populates inventory_programs and inventory_copybooks from main inventory
        2. Scans for and parses CSD files to populate inventory_cics
        3. Scans for JCL files to populate inventory_jcl
        4. Optionally scans for dataset catalogs (future enhancement)
        
        Args:
            source_directory: Root directory containing source code and artifacts
        """
        print(f"\n=== Phase 4b: Populating Specialized Tables ===")
        
        # 1. Populate programs and copybooks from main inventory
        self._populate_programs_from_inventory()
        self._populate_copybooks_from_inventory()
        
        # 2. Scan for and parse CSD files
        self._scan_and_parse_csd_files(source_directory)
        
        # 3. Scan for JCL files
        self._scan_and_parse_jcl_files(source_directory)
        
        self.database.commit()
        print("✓ Specialized tables populated")
    
    def _populate_programs_from_inventory(self) -> None:
        """Populate inventory_programs from main inventory table."""
        print("  Populating programs from inventory...")
        
        # Get programs from main inventory
        cursor = self.database.cursor()
        cursor.execute("""
            SELECT artifact_name, file_path, file_size, language
            FROM inventory
            WHERE artifact_type = 'PROGRAM'
        """)
        
        programs = cursor.fetchall()
        if not programs:
            print("    No programs found in inventory")
            return
        
        # Clear existing program inventory
        cursor.execute("DELETE FROM inventory_programs")
        
        # Insert programs
        program_rows = []
        for program in programs:
            program_name = program[0]
            file_path = program[1]
            size_bytes = program[2] or 0
            
            # Extract library name from path
            library_name = Path(file_path).parent.name.upper()
            
            program_rows.append({
                'program_name': program_name,
                'library_name': library_name,
                'size_bytes': size_bytes
            })
        
        if program_rows:
            self.database.insert_rows('inventory_programs', program_rows)
            print(f"    ✓ Inserted {len(program_rows)} programs")
        
        self.stats['programs_populated'] = len(program_rows)
    
    def _populate_copybooks_from_inventory(self) -> None:
        """Populate inventory_copybooks from main inventory table."""
        print("  Populating copybooks from inventory...")
        
        # Get copybooks from main inventory
        cursor = self.database.cursor()
        cursor.execute("""
            SELECT artifact_name, file_path
            FROM inventory
            WHERE artifact_type = 'COPYBOOK'
        """)
        
        copybooks = cursor.fetchall()
        if not copybooks:
            print("    No copybooks found in inventory")
            return
        
        # Clear existing copybook inventory
        cursor.execute("DELETE FROM inventory_copybooks")
        
        # Insert copybooks
        copybook_rows = []
        for copybook in copybooks:
            copybook_name = copybook[0]
            file_path = copybook[1]
            
            # Extract library name from path
            library_name = Path(file_path).parent.name.upper()
            
            copybook_rows.append({
                'copybook_name': copybook_name,
                'library_name': library_name
            })
        
        if copybook_rows:
            self.database.insert_rows('inventory_copybooks', copybook_rows)
            print(f"    ✓ Inserted {len(copybook_rows)} copybooks")
        
        self.stats['copybooks_populated'] = len(copybook_rows)
    
    def _scan_and_parse_csd_files(self, source_directory: str) -> int:
        """Scan for CSD files and populate inventory_cics table."""
        print("  Scanning for CSD files...")
        
        # Find CSD files
        csd_files = []
        source_path = Path(source_directory)
        
        for csd_file in source_path.rglob("*.csd"):
            csd_files.append(csd_file)
        for csd_file in source_path.rglob("*.CSD"):
            csd_files.append(csd_file)
        
        if not csd_files:
            print("    No CSD files found")
            return
        
        print(f"    Found {len(csd_files)} CSD files")
        
        # Clear existing CICS inventory
        cursor = self.database.cursor()
        cursor.execute("DELETE FROM inventory_cics")
        
        # Parse each CSD file
        total_resources = 0
        for csd_file in csd_files:
            try:
                resources = self._parse_csd_file(str(csd_file))
                if resources:
                    # Convert to database rows
                    cics_rows = []
                    for resource in resources:
                        cics_rows.append({
                            'resource_name': resource['resource_name'],
                            'resource_type': resource['resource_type'],
                            'group_name': resource.get('group_name'),
                            'status': resource.get('status', 'ENABLED'),
                            'program_name': resource.get('program_name'),
                            'dataset_name': resource.get('dataset_name'),
                            'description': resource.get('description'),
                            'language': resource.get('language')
                        })
                    
                    if cics_rows:
                        self.database.insert_rows('inventory_cics', cics_rows)
                        total_resources += len(cics_rows)
                        print(f"    ✓ Parsed {len(cics_rows)} resources from {csd_file.name}")
                
            except Exception as e:
                print(f"    ⚠ Error parsing {csd_file}: {str(e)}")
                self.stats['csd_parse_errors'] = self.stats.get('csd_parse_errors', 0) + 1
        
        if total_resources > 0:
            print(f"    ✓ Total CICS resources: {total_resources}")
            
            # Extract and populate datasets from CICS FILE resources
            self._populate_datasets_from_cics()
        
        self.stats['cics_resources_populated'] = total_resources
        return total_resources
    
    def _populate_datasets_from_cics(self) -> int:
        """Extract dataset names from CICS FILE resources and populate inventory_datasets table."""
        print("    Extracting datasets from CICS resources...")
        
        cursor = self.database.cursor()
        
        # Get all CICS FILE resources with dataset names
        cursor.execute("""
            SELECT DISTINCT dataset_name, resource_name, description
            FROM inventory_cics 
            WHERE resource_type = 'FILE' 
            AND dataset_name IS NOT NULL 
            AND dataset_name != ''
        """)
        
        cics_datasets = cursor.fetchall()
        
        if not cics_datasets:
            print("    No datasets found in CICS FILE resources")
            return 0
        
        # Clear existing dataset inventory
        cursor.execute("DELETE FROM inventory_datasets")
        
        # Prepare dataset rows for insertion
        dataset_rows = []
        for dataset_name, file_name, description in cics_datasets:
            dataset_rows.append({
                'dataset_name': dataset_name,
                'dataset_type': self._determine_dataset_type(dataset_name),
                'creation_date': None,
                'last_referenced': None,
                'size_mb': None,
                'volume': None
            })
        
        # Insert dataset records
        if dataset_rows:
            self.database.insert_rows('inventory_datasets', dataset_rows)
            self.database.commit()
            print(f"    ✓ Populated {len(dataset_rows)} datasets from CICS resources")
            self.stats['datasets_from_cics'] = len(dataset_rows)
        
        return len(dataset_rows)
    
    def _determine_dataset_type(self, dataset_name: str) -> str:
        """Determine dataset type from dataset name patterns."""
        dataset_upper = dataset_name.upper()
        
        if '.VSAM.KSDS' in dataset_upper:
            return 'KSDS'
        elif '.VSAM.ESDS' in dataset_upper:
            return 'ESDS'
        elif '.VSAM.RRDS' in dataset_upper:
            return 'RRDS'
        elif '.VSAM.AIX' in dataset_upper or '.AIX.' in dataset_upper:
            return 'AIX'
        elif '.VSAM.' in dataset_upper:
            return 'VSAM'
        elif '.PS' in dataset_upper or '.SEQ' in dataset_upper:
            return 'PS'
        elif '.PDS' in dataset_upper:
            return 'PDS'
        elif '.PDSE' in dataset_upper:
            return 'PDSE'
        else:
            return 'VSAM'  # Default for CICS datasets

    def _scan_and_parse_jcl_files(self, source_directory: str) -> int:
        """Scan for JCL files and populate inventory_jcl table."""
        print("  Scanning for JCL files...")
        
        # Find JCL files (not already in main inventory to avoid duplicates)
        jcl_files = []
        source_path = Path(source_directory)
        
        for jcl_file in source_path.rglob("*.jcl"):
            jcl_files.append(jcl_file)
        for jcl_file in source_path.rglob("*.JCL"):
            jcl_files.append(jcl_file)
        
        if not jcl_files:
            print("    No additional JCL files found")
            return
        
        print(f"    Found {len(jcl_files)} JCL files")
        
        # Clear existing JCL inventory
        cursor = self.database.cursor()
        cursor.execute("DELETE FROM inventory_jcl")
        
        # Process each JCL file
        jcl_rows = []
        for jcl_file in jcl_files:
            try:
                member_name = jcl_file.stem
                library_name = jcl_file.parent.name.upper()
                size_lines = 0
                
                # Count lines in JCL file
                try:
                    with open(jcl_file, 'r', encoding='utf-8', errors='ignore') as f:
                        size_lines = sum(1 for line in f if line.strip())
                except:
                    size_lines = 0
                
                jcl_rows.append({
                    'member_name': member_name,
                    'library_name': library_name,
                    'size_lines': size_lines
                })
                
            except Exception as e:
                print(f"    ⚠ Error processing {jcl_file}: {str(e)}")
                self.stats['jcl_parse_errors'] = self.stats.get('jcl_parse_errors', 0) + 1
        
        if jcl_rows:
            self.database.insert_rows('inventory_jcl', jcl_rows)
            print(f"    ✓ Inserted {len(jcl_rows)} JCL jobs")
        
        self.stats['jcl_jobs_populated'] = len(jcl_rows)
        return len(jcl_rows)
    
    def _parse_csd_file(self, csd_path: str) -> List[Dict[str, str]]:
        """
        Parse CSD file and extract CICS resource definitions.
        
        This is a simplified version of the CSD parser from populate_cics_inventory.py
        integrated into the inventory manager.
        
        Args:
            csd_path: Path to CSD file
            
        Returns:
            List of resource dictionaries
        """
        try:
            with open(csd_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            raise Exception(f"Could not read CSD file: {str(e)}")
        
        resources = []
        
        # Split content into individual DEFINE statements
        lines = content.split('\n')
        current_block = []
        
        for line in lines:
            if line.strip().startswith('DEFINE '):
                # Process previous block if it exists
                if current_block:
                    resource = self._process_csd_define_block('\n'.join(current_block))
                    if resource:
                        resources.append(resource)
                # Start new block
                current_block = [line]
            elif current_block:
                # Continue current block
                current_block.append(line)
        
        # Process the last block
        if current_block:
            resource = self._process_csd_define_block('\n'.join(current_block))
            if resource:
                resources.append(resource)
        
        return resources
    
    def _process_csd_define_block(self, block: str) -> Optional[Dict[str, str]]:
        """Process a single DEFINE block from CSD file."""
        import re
        
        # Extract resource type and name from first line
        first_line = block.split('\n')[0].strip()
        match = re.match(r'DEFINE\s+(\w+)\(([^)]+)\)', first_line)
        if not match:
            return None
            
        resource_type = match.group(1)
        resource_name = match.group(2)
        
        # Extract GROUP
        group_match = re.search(r'GROUP\(([^)]+)\)', block)
        group_name = group_match.group(1) if group_match else None
        
        # Extract DESCRIPTION
        desc_match = re.search(r'DESCRIPTION\(([^)]+)\)', block)
        description = desc_match.group(1) if desc_match else None
        
        # Extract STATUS
        status_match = re.search(r'STATUS\(([^)]+)\)', block)
        status = status_match.group(1) if status_match else 'ENABLED'
        
        resource_info = {
            'resource_name': resource_name,
            'resource_type': resource_type,
            'group_name': group_name,
            'status': status,
            'description': description,
            'program_name': None,
            'dataset_name': None,
            'language': None
        }
        
        # Add type-specific parsing
        if resource_type == 'FILE':
            dsname_match = re.search(r'DSNAME\(([^)]+)\)', block)
            resource_info['dataset_name'] = dsname_match.group(1) if dsname_match else None
            
        elif resource_type == 'PROGRAM':
            lang_match = re.search(r'LANGUAGE\(([^)]+)\)', block)
            resource_info['language'] = lang_match.group(1) if lang_match else None
            
        elif resource_type == 'TRANSACTION':
            prog_match = re.search(r'PROGRAM\(([^)]+)\)', block)
            resource_info['program_name'] = prog_match.group(1) if prog_match else None
            
        elif resource_type == 'LIBRARY':
            dsname_match = re.search(r'DSNAME01\(([^)]+)\)', block)
            resource_info['dataset_name'] = dsname_match.group(1) if dsname_match else None
        
        return resource_info

    def _create_cics_transaction_dependencies(self) -> None:
        """
        Create CICS_TRANSACTION dependencies from inventory_cics table.
        
        The migration flow builder expects entry points to be stored as dependencies
        in the artifact_dependencies table. This method creates dependencies linking
        CICS transactions to their associated programs.
        """
        cursor = self.database.cursor()
        
        # Get CICS transactions with programs
        cursor.execute("""
            SELECT resource_name, program_name
            FROM inventory_cics
            WHERE resource_type = 'TRANSACTION' AND program_name IS NOT NULL
        """)
        
        transactions = cursor.fetchall()
        if not transactions:
            return
        
        created = 0
        for trans_id, program_name in transactions:
            # Check if dependency already exists
            cursor.execute("""
                SELECT COUNT(*) FROM artifact_dependencies
                WHERE source_artifact_name = ?
                  AND target_artifact_name = ?
                  AND dependency_type = 'CICS_TRANSACTION'
            """, (trans_id, program_name))
            
            if cursor.fetchone()[0] > 0:
                continue
            
            # Create dependency
            cursor.execute("""
                INSERT INTO artifact_dependencies (
                    source_artifact_name,
                    source_artifact_type,
                    target_artifact_name,
                    target_artifact_type,
                    dependency_type,
                    line_number
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                trans_id,
                'TRANSACTION',
                program_name,
                'PROGRAM',
                'CICS_TRANSACTION',
                None
            ))
            
            created += 1
        
        if created > 0:
            self.database.commit()
            print(f"    ℹ Created {created} CICS transaction dependencies")
