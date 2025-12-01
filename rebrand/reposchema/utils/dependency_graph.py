#!/usr/bin/env python3
"""
Dependency Graph Generator for Repository Schema

Creates and manages dependency relationships between files in a codebase,
enabling visualization and analysis of import/export relationships.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque

# Optional import for NetworkX
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    nx = None
    NETWORKX_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class DependencyNode:
    """Represents a file node in the dependency graph"""
    file_path: str
    file_type: str
    imports: List[str] = None
    exports: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.imports is None:
            self.imports = []
        if self.exports is None:
            self.exports = []
        if self.metadata is None:
            self.metadata = {}

@dataclass
class DependencyEdge:
    """Represents a dependency relationship between files"""
    source_file: str
    target_file: str
    dependency_type: str  # 'import', 'require', 'include', etc.
    imported_items: List[str] = None
    line_number: Optional[int] = None

    def __post_init__(self):
        if self.imported_items is None:
            self.imported_items = []

class DependencyGraph:
    """Manages the dependency graph structure and operations"""

    def __init__(self):
        self.nodes: Dict[str, DependencyNode] = {}
        self.edges: List[DependencyEdge] = []
        self.file_to_module_map: Dict[str, str] = {}
        self.module_to_files_map: Dict[str, List[str]] = defaultdict(list)

    def add_node(self, node: DependencyNode) -> None:
        """Add a node to the graph"""
        self.nodes[node.file_path] = node

        # Update module mappings
        module_name = self._extract_module_name(node.file_path, node.file_type)
        if module_name:
            self.file_to_module_map[node.file_path] = module_name
            self.module_to_files_map[module_name].append(node.file_path)

    def add_edge(self, edge: DependencyEdge) -> None:
        """Add an edge to the graph"""
        self.edges.append(edge)

    def get_dependencies(self, file_path: str) -> List[DependencyEdge]:
        """Get all dependencies for a specific file"""
        return [edge for edge in self.edges if edge.source_file == file_path]

    def get_dependents(self, file_path: str) -> List[DependencyEdge]:
        """Get all files that depend on the specified file"""
        return [edge for edge in self.edges if edge.target_file == file_path]

    def detect_cycles(self) -> List[List[str]]:
        """Detect circular dependencies in the graph"""
        if not NETWORKX_AVAILABLE:
            logger.warning("NetworkX not available, skipping cycle detection")
            return []

        # Create NetworkX graph for cycle detection
        G = nx.DiGraph()

        for edge in self.edges:
            G.add_edge(edge.source_file, edge.target_file)

        try:
            cycles = list(nx.simple_cycles(G))
            return cycles
        except Exception as e:
            logger.error(f"Error detecting cycles: {e}")
            return []

    def get_subgraph(self, file_paths: List[str]) -> 'DependencyGraph':
        """Extract a subgraph containing only specified files"""
        subgraph = DependencyGraph()

        # Add nodes
        for file_path in file_paths:
            if file_path in self.nodes:
                subgraph.add_node(self.nodes[file_path])

        # Add relevant edges
        for edge in self.edges:
            if edge.source_file in file_paths and edge.target_file in file_paths:
                subgraph.add_edge(edge)

        return subgraph

    def topological_sort(self) -> List[str]:
        """Perform topological sort of the dependency graph"""
        if not NETWORKX_AVAILABLE:
            logger.warning("NetworkX not available, returning unsorted file list")
            return list(self.nodes.keys())

        G = nx.DiGraph()

        for edge in self.edges:
            G.add_edge(edge.source_file, edge.target_file)

        try:
            return list(nx.topological_sort(G))
        except Exception as e:
            # Graph has cycles or other issues, return partial ordering
            logger.warning(f"Topological sort failed: {e}")
            return list(self.nodes.keys())

    def _extract_module_name(self, file_path: str, file_type: str) -> Optional[str]:
        """Extract module name from file path based on file type"""
        if file_type == '.py':
            # Python: convert path to module name
            path_parts = file_path.replace('.py', '').split(os.sep)
            if path_parts[-1] == '__init__':
                return '.'.join(path_parts[:-1])
            return '.'.join(path_parts)
        elif file_type in ['.js', '.jsx', '.ts', '.tsx']:
            # JavaScript/TypeScript: use file name without extension
            return os.path.splitext(os.path.basename(file_path))[0]
        elif file_type == '.java':
            # Java: package.class format
            return file_path.replace('.java', '').replace(os.sep, '.')
        else:
            return None

class DependencyAnalyzer:
    """Analyzes code files to extract dependency relationships"""

    def __init__(self):
        self.supported_extensions = {
            '.py': self._analyze_python_file,
            '.js': self._analyze_javascript_file,
            '.jsx': self._analyze_javascript_file,
            '.ts': self._analyze_javascript_file,
            '.tsx': self._analyze_javascript_file,
            '.java': self._analyze_java_file,
            '.cs': self._analyze_csharp_file,
            '.cpp': self._analyze_cpp_file,
            '.c': self._analyze_cpp_file,
            '.php': self._analyze_php_file,
            '.go': self._analyze_go_file,
            '.rs': self._analyze_rust_file
        }

    def analyze_file(self, file_path: str, content: str) -> DependencyNode:
        """Analyze a file and extract its dependencies"""
        file_type = os.path.splitext(file_path)[1].lower()

        node = DependencyNode(
            file_path=file_path,
            file_type=file_type,
            imports=[],
            exports=[],
            metadata={}
        )

        if file_type in self.supported_extensions:
            analyzer_func = self.supported_extensions[file_type]
            analyzer_func(content, node)

        return node

    def _analyze_python_file(self, content: str, node: DependencyNode) -> None:
        """Analyze Python file for imports and dependencies"""
        lines = content.split('\n')
        imports = []
        exports = []

        # Python standard library modules (common ones) - reduced set for better internal dep detection
        stdlib_modules = {
            'os', 'sys', 'json', 're', 'time', 'datetime', 'pathlib', 'collections',
            'itertools', 'functools', 'math', 'random', 'string', 'argparse', 'logging',
            'subprocess', 'threading', 'asyncio', 'typing', 'tempfile', 'shutil', 'glob',
            'pickle', 'copy', 'enum', 'abc', 'warnings', 'io', 'codecs', 'urllib',
            'urllib.request', 'urllib.parse', 'xml', 'html', 'email', 'base64',
            'struct', 'hashlib', 'ssl', 'socket', 'sqlite3', 'zlib', 'gzip', 'csv',
            'configparser', 'plistlib', 'mmap', 'cgi', 'wsgiref', 'calendar', 'zoneinfo'
        }

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Extract imports
            if line.startswith('from '):
                # Handle: from pathlib import Path
                module = line.split('from ')[1].split(' import ')[0]
                if module and not module.startswith('_'):
                    # For dependency graphs, we want the module name, not individual imports
                    # Only include non-stdlib modules and relative imports
                    if module not in stdlib_modules and not module.startswith('.'):
                        imports.append(module)
            elif line.startswith('import '):
                # Handle multi-import: import os, sys
                parts = line.split('import ')[1].split(',')
                for part in parts[:3]:  # Limit per line
                    module = part.strip().split()[0]
                    if module and not module.startswith('_'):
                        # Only include non-stdlib modules and relative imports
                        if module not in stdlib_modules and not module.startswith('.'):
                            imports.append(module)

            # Extract exports (simplified - could be enhanced)
            elif line.startswith(('def ', 'class ')) and not line.startswith('    '):
                if 'def ' in line:
                    func_name = line.split('def ')[1].split('(')[0].strip()
                    if not func_name.startswith('_'):
                        exports.append(f"function:{func_name}")
                elif 'class ' in line:
                    class_name = line.split('class ')[1].split('(')[0].split(':')[0].strip()
                    if not class_name.startswith('_'):
                        exports.append(f"class:{class_name}")

        node.imports = imports
        node.exports = exports

    def _analyze_javascript_file(self, content: str, node: DependencyNode) -> None:
        """Analyze JavaScript/TypeScript file for imports and dependencies"""
        lines = content.split('\n')
        imports = []
        exports = []

        # Common external packages that should be filtered out
        external_packages = {
            'react', 'react-dom', 'vue', 'angular', 'jquery', 'lodash', 'underscore',
            'axios', 'fetch', 'express', 'mongoose', 'mongodb', 'mysql', 'postgres',
            'redis', 'socket.io', 'webpack', 'babel', 'typescript', 'eslint',
            'prettier', 'jest', 'mocha', 'chai', 'sinon', 'enzyme', 'testing-library',
            'redux', 'mobx', 'rxjs', 'rxjs/operators', 'immutable', 'moment',
            'date-fns', 'ramda', 'bluebird', 'q', 'async', 'co', 'thunkify',
            'fs', 'path', 'os', 'crypto', 'http', 'https', 'url', 'querystring',
            'events', 'stream', 'buffer', 'util', 'child_process', 'cluster',
            'zlib', 'readline', 'repl', 'vm', 'v8', 'webassembly'
        }

        for line in lines:
            line = line.strip()
            if not line or line.startswith('//') or line.startswith('/*'):
                continue

            # Extract imports
            if line.startswith('import '):
                if 'from ' in line:
                    module = line.split('from ')[1].strip().strip("';\"")
                    # Only include non-relative imports that are not common external packages
                    if (module and not module.startswith('./') and not module.startswith('../')
                        and module not in external_packages and not module.startswith('@types/')):
                        imports.append(module)
                elif '{' in line and '}' in line:
                    # Named imports: import { useState, useEffect } from 'react'
                    module_part = line.split('} from ')[-1] if '} from ' in line else ""
                    if module_part:
                        module = module_part.strip().strip("';\"")
                        # Only include non-relative imports that are not common external packages
                        if (module and not module.startswith('./') and not module.startswith('../')
                            and module not in external_packages and not module.startswith('@types/')):
                            imports.append(module)

            # Extract exports
            elif line.startswith(('export ', 'module.exports')):
                if 'export ' in line:
                    if 'function ' in line:
                        func_name = line.split('function ')[1].split('(')[0].strip()
                        exports.append(f"function:{func_name}")
                    elif 'class ' in line:
                        class_name = line.split('class ')[1].split()[0]
                        exports.append(f"class:{class_name}")
                    elif 'const ' in line or 'let ' in line or 'var ' in line:
                        var_name = line.split()[1].split('=')[0].strip()
                        exports.append(f"variable:{var_name}")

        node.imports = imports
        node.exports = exports

    def _analyze_java_file(self, content: str, node: DependencyNode) -> None:
        """Analyze Java file for imports and dependencies"""
        lines = content.split('\n')
        imports = []
        exports = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith('//') or line.startswith('/*'):
                continue

            # Extract imports
            if line.startswith('import '):
                package = line.split('import ')[1].split(';')[0]
                if not package.startswith('java.') and not package.startswith('javax.'):
                    imports.append(package)

            # Extract class declarations
            elif line.startswith('public class ') or line.startswith('class '):
                class_name = line.split('class ')[1].split()[0]
                exports.append(f"class:{class_name}")

        node.imports = imports
        node.exports = exports

    def _analyze_csharp_file(self, content: str, node: DependencyNode) -> None:
        """Analyze C# file for imports and dependencies"""
        lines = content.split('\n')
        imports = []
        exports = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith('//') or line.startswith('/*'):
                continue

            # Extract using statements
            if line.startswith('using '):
                namespace = line.split('using ')[1].split(';')[0]
                if not namespace.startswith('System.'):
                    imports.append(namespace)

            # Extract class declarations
            elif line.startswith(('public class ', 'class ')):
                class_name = line.split('class ')[1].split()[0]
                exports.append(f"class:{class_name}")

        node.imports = imports
        node.exports = exports

    def _analyze_cpp_file(self, content: str, node: DependencyNode) -> None:
        """Analyze C/C++ file for includes and dependencies"""
        lines = content.split('\n')
        imports = []
        exports = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith('//') or line.startswith('/*'):
                continue

            # Extract includes
            if line.startswith('#include '):
                if '<' in line and '>' in line:
                    header = line.split('<')[1].split('>')[0]
                    imports.append(header)
                elif '"' in line:
                    header = line.split('"')[1]
                    imports.append(header)

        node.imports = imports
        node.exports = exports

    def _analyze_php_file(self, content: str, node: DependencyNode) -> None:
        """Analyze PHP file for imports and dependencies"""
        lines = content.split('\n')
        imports = []
        exports = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith('//') or line.startswith('#'):
                continue

            # Extract use statements
            if line.startswith('use '):
                use_path = line.split('use ')[1].split(';')[0]
                imports.append(use_path)

            # Extract class/function declarations
            elif line.startswith(('class ', 'function ', 'public function ')):
                if 'class ' in line:
                    class_name = line.split('class ')[1].split()[0]
                    exports.append(f"class:{class_name}")
                elif 'function ' in line:
                    func_name = line.split('function ')[1].split('(')[0].strip()
                    exports.append(f"function:{func_name}")

        node.imports = imports
        node.exports = exports

    def _analyze_go_file(self, content: str, node: DependencyNode) -> None:
        """Analyze Go file for imports and dependencies"""
        lines = content.split('\n')
        imports = []
        exports = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith('//'):
                continue

            # Extract imports
            if line.startswith('import '):
                if '(' in line:  # Multi-line imports
                    # Handle multi-line imports
                    j = lines.index(line) + 1
                    while j < len(lines) and not lines[j].strip().startswith(')'):
                        imp_line = lines[j].strip().strip('"')
                        if imp_line and not imp_line.startswith('//'):
                            imports.append(imp_line)
                        j += 1
                else:
                    imp = line.split('"')[1] if '"' in line else ""
                    if imp:
                        imports.append(imp)

            # Extract function/type declarations
            elif line.startswith(('func ', 'type ')):
                if 'func ' in line:
                    func_name = line.split('func ')[1].split('(')[0].strip()
                    if func_name[0].isupper():  # Exported in Go
                        exports.append(f"function:{func_name}")
                elif 'type ' in line:
                    type_name = line.split('type ')[1].split()[0]
                    if type_name[0].isupper():
                        exports.append(f"type:{type_name}")

        node.imports = imports
        node.exports = exports

    def _analyze_rust_file(self, content: str, node: DependencyNode) -> None:
        """Analyze Rust file for imports and dependencies"""
        lines = content.split('\n')
        imports = []
        exports = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith('//'):
                continue

            # Extract use statements
            if line.startswith('use '):
                use_path = line.split('use ')[1].split(';')[0]
                imports.append(use_path)

            # Extract function/struct declarations
            elif line.startswith(('fn ', 'struct ', 'pub fn ', 'pub struct ')):
                if 'fn ' in line:
                    fn_line = line.replace('pub ', '').split('fn ')[1]
                    fn_name = fn_line.split('(')[0].strip()
                    exports.append(f"function:{fn_name}")
                elif 'struct ' in line:
                    struct_line = line.replace('pub ', '').split('struct ')[1]
                    struct_name = struct_line.split()[0]
                    exports.append(f"struct:{struct_name}")

        node.imports = imports
        node.exports = exports

class DependencyGraphGenerator:
    """Main class for generating dependency graphs from codebase"""

    def __init__(self):
        self.analyzer = DependencyAnalyzer()
        self.graph = DependencyGraph()

    def generate_from_schema(self, schema_data: Dict[str, Any]) -> DependencyGraph:
        """Generate dependency graph from existing schema data"""
        logger.info("Generating dependency graph from schema data")

        # Process each file in the schema
        for entry in schema_data.get('taxonomy', []):
            for file_info in entry.get('files', []):
                file_path = file_info.get('path', '')
                metadata = file_info.get('metadata', {})

                # Read file content if available
                content = ""
                try:
                    if os.path.exists(file_path):
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                except Exception as e:
                    logger.warning(f"Could not read file {file_path}: {e}")

                # Analyze file
                node = self.analyzer.analyze_file(file_path, content)
                node.metadata = metadata
                self.graph.add_node(node)

        # Create edges based on import relationships
        self._create_dependency_edges()

        logger.info(f"Generated dependency graph with {len(self.graph.nodes)} nodes and {len(self.graph.edges)} edges")
        return self.graph

    def _create_dependency_edges(self) -> None:
        """Create dependency edges based on import relationships"""
        for file_path, node in self.graph.nodes.items():
            for import_module in node.imports:
                # Try to find matching files for this import
                target_files = self._resolve_import_to_files(import_module, file_path)

                for target_file in target_files:
                    if target_file in self.graph.nodes:
                        edge = DependencyEdge(
                            source_file=file_path,
                            target_file=target_file,
                            dependency_type='import',
                            imported_items=[import_module]
                        )
                        self.graph.add_edge(edge)

    def _resolve_import_to_files(self, import_module: str, source_file: str) -> List[str]:
        """Resolve an import module name to actual file paths"""
        matching_files = []

        # Get source file directory for relative path resolution
        source_dir = os.path.dirname(source_file)

        for file_path in self.graph.nodes.keys():
            # Check if this file could satisfy the import
            if self._module_matches_file(import_module, file_path, source_dir):
                matching_files.append(file_path)

        return matching_files

    def _module_matches_file(self, import_module: str, file_path: str, source_dir: str) -> bool:
        """Check if an import module could match a file"""
        file_type = os.path.splitext(file_path)[1].lower()

        if file_type == '.py':
            # Python module matching
            # Convert file path to module name
            if file_path.endswith('__init__.py'):
                module_name = file_path[:-12].replace(os.sep, '.')  # Remove __init__.py
            else:
                module_name = file_path[:-3].replace(os.sep, '.')  # Remove .py

            # Check exact match
            if module_name == import_module:
                return True

            # Check if import_module ends with this module name (handles partial matches)
            if import_module.endswith(module_name):
                return True

            # Check relative path matching
            try:
                rel_path = os.path.relpath(file_path, source_dir)
                if rel_path.endswith('__init__.py'):
                    rel_module = rel_path[:-12].replace(os.sep, '.')
                else:
                    rel_module = rel_path[:-3].replace(os.sep, '.')

                if rel_module == import_module:
                    return True

                # Handle case where import is just the module name
                if os.path.basename(file_path) == f"{import_module}.py":
                    return True

            except ValueError:
                pass

        elif file_type in ['.js', '.jsx', '.ts', '.tsx']:
            # JavaScript/TypeScript module matching
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            if file_name == import_module:
                return True

        # Add more language-specific matching logic as needed
        return False

    def serialize_graph(self, max_size_kb: int = 250) -> str:
        """Serialize the dependency graph to JSON with size constraints"""
        graph_data = {
            'nodes': [asdict(node) for node in self.graph.nodes.values()],
            'edges': [asdict(edge) for edge in self.graph.edges],
            'metadata': {
                'total_nodes': len(self.graph.nodes),
                'total_edges': len(self.graph.edges),
                'cycles_detected': len(self.graph.detect_cycles()),
                'generated_at': str(datetime.now())
            }
        }

        json_str = json.dumps(graph_data, indent=2)
        size_kb = len(json_str.encode('utf-8')) / 1024

        if size_kb > max_size_kb:
            logger.warning(f"Graph size ({size_kb:.1f}KB) exceeds limit ({max_size_kb}KB), truncating")
            # Truncate by removing some edges if needed
            max_edges = int(len(self.graph.edges) * (max_size_kb / size_kb) * 0.9)
            graph_data['edges'] = graph_data['edges'][:max_edges]
            graph_data['metadata']['truncated'] = True
            json_str = json.dumps(graph_data, indent=2)

        return json_str

    def save_graph(self, output_path: str, max_size_kb: int = 250) -> None:
        """Save the dependency graph to a file"""
        json_str = self.serialize_graph(max_size_kb)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(json_str)

        logger.info(f"Saved dependency graph to {output_path}")

    def export_to_arrows_app(self, output_path: str, max_size_kb: int = 250) -> None:
        """Export dependency graph in Arrows.app compatible format"""
        arrows_data = self._convert_to_arrows_format()

        # Apply size constraints
        json_str = json.dumps(arrows_data, indent=2)
        size_kb = len(json_str.encode('utf-8')) / 1024

        if size_kb > max_size_kb:
            logger.warning(f"Arrows export size ({size_kb:.1f}KB) exceeds limit ({max_size_kb}KB), truncating")
            # Truncate edges to fit within size limit
            max_edges = int(len(arrows_data['relationships']) * (max_size_kb / size_kb) * 0.9)
            arrows_data['relationships'] = arrows_data['relationships'][:max_edges]
            json_str = json.dumps(arrows_data, indent=2)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(json_str)

        logger.info(f"Exported dependency graph to Arrows.app format: {output_path}")

    def _convert_to_arrows_format(self) -> Dict[str, Any]:
        """Convert dependency graph to Arrows.app compatible format"""
        arrows_data = {
            "nodes": [],
            "relationships": [],
            "style": {
                "node": {
                    "color": "#4A90E2",
                    "borderColor": "#357ABD",
                    "borderWidth": 2,
                    "fontSize": 12,
                    "fontColor": "#FFFFFF"
                },
                "relationship": {
                    "color": "#7F7F7F",
                    "fontSize": 10,
                    "fontColor": "#2E2E2E"
                }
            },
            "metadata": {
                "total_nodes": len(self.graph.nodes),
                "total_edges": len(self.graph.edges),
                "cycles_detected": len(self.graph.detect_cycles()),
                "generated_at": str(datetime.now()),
                "exported_for": "arrows.app"
            }
        }

        # Create node ID mapping
        node_id_map = {}
        node_counter = 1

        # Add nodes
        for file_path, node in self.graph.nodes.items():
            node_id = f"n{node_counter}"
            node_id_map[file_path] = node_id

            # Determine node color based on file type
            node_color = self._get_node_color(node.file_type)

            arrows_node = {
                "id": node_id,
                "labels": [node.file_type[1:].upper() if node.file_type.startswith('.') else node.file_type.upper()],
                "properties": {
                    "file_path": file_path,
                    "file_name": os.path.basename(file_path),
                    "file_type": node.file_type,
                    "imports_count": len(node.imports),
                    "exports_count": len(node.exports)
                },
                "position": {
                    "x": (node_counter % 10) * 150,  # Simple grid layout
                    "y": (node_counter // 10) * 100
                },
                "style": {
                    "nodeColor": node_color,
                    "borderColor": "#357ABD"
                }
            }

            arrows_data["nodes"].append(arrows_node)
            node_counter += 1

        # Add relationships
        for edge in self.graph.edges:
            if edge.source_file in node_id_map and edge.target_file in node_id_map:
                arrows_relationship = {
                    "id": f"r{len(arrows_data['relationships']) + 1}",
                    "type": edge.dependency_type.upper(),
                    "startNodeId": node_id_map[edge.source_file],
                    "endNodeId": node_id_map[edge.target_file],
                    "properties": {
                        "source_file": edge.source_file,
                        "target_file": edge.target_file,
                        "imported_items": edge.imported_items
                    }
                }

                arrows_data["relationships"].append(arrows_relationship)

        return arrows_data

    def _get_node_color(self, file_type: str) -> str:
        """Get appropriate color for different file types"""
        color_map = {
            '.py': '#3776AB',      # Python blue
            '.js': '#F7DF1E',      # JavaScript yellow
            '.jsx': '#61DAFB',     # React blue
            '.ts': '#3178C6',      # TypeScript blue
            '.tsx': '#3178C6',     # TypeScript blue
            '.java': '#ED8B00',    # Java orange
            '.cs': '#239120',      # C# green
            '.cpp': '#00599C',     # C++ blue
            '.c': '#A8B9CC',       # C gray
            '.php': '#777BB4',     # PHP purple
            '.go': '#00ADD8',      # Go cyan
            '.rs': '#000000',      # Rust black
            '.html': '#E34F26',    # HTML orange
            '.css': '#1572B6',     # CSS blue
            '.json': '#000000',    # JSON black
            '.md': '#083FA1',      # Markdown blue
        }

        return color_map.get(file_type.lower(), '#CCCCCC')  # Default gray

def generate_dependency_graph(schema_file: str, output_file: str) -> None:
    """Generate dependency graph from schema file"""
    logger.info(f"Generating dependency graph from {schema_file}")

    # Load schema data
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_data = json.load(f)

    # Generate dependency graph
    generator = DependencyGraphGenerator()
    graph = generator.generate_from_schema(schema_data)

    # Save graph
    generator.save_graph(output_file)

    # Log statistics
    cycles = graph.detect_cycles()
    logger.info(f"Dependency graph generated: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
    if cycles:
        logger.warning(f"Detected {len(cycles)} circular dependencies")

if __name__ == "__main__":
    # CLI interface for testing
    import argparse

    parser = argparse.ArgumentParser(description="Generate dependency graph from schema")
    parser.add_argument("schema_file", help="Path to repo-schema.json file")
    parser.add_argument("output_file", help="Path to output dependency graph file")
    parser.add_argument("--max-size-kb", type=int, default=250, help="Maximum graph size in KB")

    args = parser.parse_args()
    generate_dependency_graph(args.schema_file, args.output_file)