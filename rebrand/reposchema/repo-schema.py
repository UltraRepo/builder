#!/usr/bin/env python3
import os
import json
import re
import sys
import time
import mimetypes
import logging
import signal
from datetime import datetime
from pathspec import PathSpec
import argparse

# Import Qdrant utilities
try:
    from utils.qdrant_client import QdrantManager
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    QdrantManager = None

# Import dependency graph utilities
try:
    from utils.dependency_graph import DependencyGraphGenerator, generate_dependency_graph
    DEPENDENCY_GRAPH_AVAILABLE = True
except ImportError:
    DEPENDENCY_GRAPH_AVAILABLE = False
    DependencyGraphGenerator = None
    generate_dependency_graph = None

# Configuration Constants
# ----------------------

# Debug mode flag (set to False to disable debug messages)
DEBUG = False

# Define the DEFAULT base directory and output files (used if args not provided, or for defaults)
DEFAULT_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# File processing limits and exclusions
FILE_SIZE_LIMIT = 1 * 1024 * 1024  # 1MB in bytes - prevents processing of large files

# Known binary file extensions to exclude from processing
BINARY_EXTENSIONS = {
    '.exe', '.dll', '.so', '.dylib', '.bin',
    '.zip', '.tar', '.gz', '.7z', '.rar',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.webp',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.pyc', '.pyo', '.class', '.o', '.a', '.lib',
    '.mp3', '.mp4', '.wav', '.avi', '.mov',
    '.db', '.sqlite', '.mdb'
}

# Common file type descriptions
FILE_TYPE_DESCRIPTIONS = {
    '.py': 'Python source code file',
    '.js': 'JavaScript source code file',
    '.jsx': 'React JavaScript component file',
    '.ts': 'TypeScript source code file',
    '.tsx': 'React TypeScript component file',
    '.json': 'JSON configuration or data file',
    '.md': 'Markdown documentation file',
    '.txt': 'Plain text file',
    '.html': 'HTML web page file',
    '.css': 'CSS stylesheet file',
    '.scss': 'SASS stylesheet file',
    '.yaml': 'YAML configuration file',
    '.yml': 'YAML configuration file',
    '.sh': 'Shell script file',
    '.bat': 'Windows batch script file',
    '.gitignore': 'Git ignore rules file',
    '.env': 'Environment variables file',
    'package.json': 'Node.js package configuration and dependencies',
    'requirements.txt': 'Python package dependencies file',
    'Dockerfile': 'Docker container build instructions',
    'README.md': 'Project documentation and overview',
    'LICENSE': 'Project license terms',
    '.prettierrc': 'Prettier code formatter configuration',
    '.eslintrc': 'ESLint code linter configuration',
    'tsconfig.json': 'TypeScript compiler configuration',
    'next.config.js': 'Next.js framework configuration',
    'webpack.config.js': 'Webpack bundler configuration'
}

def debug_print(*args, **kwargs):
    """Print debug messages only when DEBUG is True"""
    if DEBUG:
        print(*args, **kwargs)

def load_gitignore_patterns(target_base_dir, custom_ignore_file=None):
    """Load and parse ignore patterns from default .repoignore and optional custom ignore file."""
    patterns = []

    # 1. Load from default .repoignore in script directory (ALWAYS loaded)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repoignore_path = os.path.join(script_dir, ".repoignore")
    if os.path.exists(repoignore_path):
        try:
            with open(repoignore_path, "r", encoding="utf-8") as f:
                debug_print(f"\nDEBUG: Loading default patterns from: {repoignore_path}")
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line)
        except Exception as e:
            print(f"Warning: Error reading default .repoignore: {e}")
    else:
        print(f"Warning: Default .repoignore not found at: {repoignore_path}")

    # 2. Load from standard .gitignore in target_base_dir (optional)
    gitignore_path = os.path.join(target_base_dir, ".gitignore")
    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, "r", encoding="utf-8") as f:
                debug_print(f"\nDEBUG: Loading patterns from: {gitignore_path}")
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line)
        except Exception as e:
            print(f"Warning: Error reading standard .gitignore: {e}")

    # 3. Load from custom ignore file if provided
    if custom_ignore_file and os.path.exists(custom_ignore_file):
        try:
            with open(custom_ignore_file, "r", encoding="utf-8") as f:
                debug_print(f"\nDEBUG: Loading patterns from custom file: {custom_ignore_file}")
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Add custom patterns, potentially overriding standard ones if needed later
                        patterns.append(line)
        except Exception as e:
            print(f"Warning: Error reading custom ignore file '{custom_ignore_file}': {e}")

    if not patterns:
        return None

    # Debug print loaded patterns
    debug_print("nDEBUG: Combined ignore patterns loaded:")
    for pattern in patterns:
        debug_print(f"  - {pattern}")

    # Create PathSpec object (handles precedence internally if patterns overlap)
    # Using gitwildmatch style
    return PathSpec.from_lines("gitwildmatch", patterns)

def is_git_path(path):
    """Check if a path contains a .git component"""
    # Check relative path parts for '.git'
    return '.git' in path.split(os.sep)

def is_ignored(file_path, base_dir, gitignore_spec):
    if gitignore_spec is None:
        return False

    try:
        relative_path = os.path.relpath(file_path, base_dir)
    except ValueError:
        if DEBUG: print(f"DEBUG: Cannot get relative path for {file_path} against {base_dir}")
        return False 

    relative_path_normalized = relative_path.replace(os.sep, '/')
    is_dir_flag_for_debug_only = os.path.isdir(file_path)

    # Specific debug for 'vendor' directory check
    if relative_path_normalized == "vendor" and is_dir_flag_for_debug_only:
        if DEBUG:
            print(f"DEBUG_VENDOR_CHECK: Checking relative path 'vendor' (is_dir={is_dir_flag_for_debug_only}). file_path='{file_path}'. base_dir='{base_dir}'")
            match_against_vendor_slash = False
            if gitignore_spec:
                for pattern_obj in gitignore_spec.patterns:
                    if 'vendor/' in pattern_obj.pattern: 
                        temp_spec = PathSpec.from_lines('gitwildmatch', [pattern_obj.pattern])
                        if temp_spec.match_file(relative_path_normalized):
                            match_against_vendor_slash = True
                            print(f"DEBUG_VENDOR_CHECK: Pattern '{pattern_obj.pattern}' matches '{relative_path_normalized}' (is_dir={is_dir_flag_for_debug_only})")
            print(f"DEBUG_VENDOR_CHECK: Preliminary match for 'vendor' (dir) against a 'vendor/' like pattern: {match_against_vendor_slash}")

    match_result = gitignore_spec.match_file(relative_path_normalized)

    if match_result:
        if DEBUG: print(f"DEBUG_IS_IGNORED: Path '{relative_path_normalized}' (is_dir={is_dir_flag_for_debug_only}, from file_path '{file_path}') MATCHED by gitignore_spec. RESULT: IGNORED")
        return True
    
    # if DEBUG: print(f"DEBUG_IS_IGNORED: Path '{relative_path_normalized}' (is_dir={is_dir_flag_for_debug_only}, from file_path '{file_path}') NOT matched by gitignore_spec. RESULT: NOT IGNORED")
    return False

# File Analysis Functions
# ----------------------

def is_text_file(file_path):
    try:
        ext = os.path.splitext(file_path)[1].lower()
        if ext in BINARY_EXTENSIONS:
            return False
        if os.path.getsize(file_path) > FILE_SIZE_LIMIT:
            return False
        mime_type = mimetypes.guess_type(file_path)[0]
        if mime_type and not mime_type.startswith('text/'):
            return False
        with open(file_path, 'rb') as f:
            chunk = f.read(512)
            try:
                chunk.decode('utf-8')
                return True
            except UnicodeDecodeError:
                return False
    except Exception:
        return False

def get_ai_description(file_path, file_name, content=None):
    """Generate an AI-like description based on file type and name"""
    # First check for exact filename matches
    if file_name in FILE_TYPE_DESCRIPTIONS:
        return FILE_TYPE_DESCRIPTIONS[file_name]

    # Then check file extension
    ext = os.path.splitext(file_name)[1].lower()
    if ext in FILE_TYPE_DESCRIPTIONS:
        return FILE_TYPE_DESCRIPTIONS[ext]

    # For unknown files, try to make an educated guess
    if not ext:  # No extension
        if file_name.lower().startswith('readme'):
            return 'Project documentation file'
        if file_name.lower().startswith('license'):
            return 'Project license file'
        if file_name.lower().startswith('dockerfile'):
            return 'Docker container configuration'
        return 'Configuration or data file'

    return f'File with {ext} extension'

def extract_python_summary(content):
    """Extract enhanced Python code summary for AI agents"""
    summary_parts = []

    try:
        lines = content.split('\n')
        imports = []
        functions = []
        classes = []
        decorators = []
        constants = []

        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Extract imports with better parsing
            if line.startswith(('import ', 'from ')):
                if len(imports) < 5:  # Increased limit
                    if 'import ' in line:
                        # Handle multi-import: import os, sys
                        parts = line.split('import ')[1].split(',')
                        for part in parts[:2]:  # Limit per line
                            imports.append(part.strip().split()[0])
                    elif 'from ' in line:
                        # Handle: from pathlib import Path
                        module = line.split('from ')[1].split(' import ')[0]
                        imports.append(module)

            # Extract decorators
            elif line.startswith('@') and len(decorators) < 3:
                decorators.append(line[1:].strip())

            # Extract function definitions with parameters
            elif line.startswith('def ') and len(functions) < 4:
                func_line = line.split('def ')[1]
                func_name = func_line.split('(')[0].strip()
                # Extract parameter count
                params_part = func_line.split('(')[1].split(')')[0] if '(' in func_line else ""
                param_count = len([p for p in params_part.split(',') if p.strip() and p.strip() != 'self'])
                functions.append(f"{func_name}({param_count}p)")

            # Extract class definitions with inheritance
            elif line.startswith('class ') and len(classes) < 3:
                class_line = line.split('class ')[1]
                class_name = class_line.split('(')[0].split(':')[0].strip()
                # Check for inheritance
                if '(' in class_line and ')' in class_line:
                    inheritance = class_line.split('(')[1].split(')')[0]
                    classes.append(f"{class_name}({inheritance})")
                else:
                    classes.append(class_name)

            # Extract constants (uppercase variables)
            elif '=' in line and len(constants) < 3:
                var_part = line.split('=')[0].strip()
                if var_part.isupper() and not var_part.startswith('_'):
                    constants.append(var_part)

        # Build summary with priorities
        if imports:
            summary_parts.append(f"Imports: {', '.join(imports[:5])}")
        if classes:
            summary_parts.append(f"Classes: {', '.join(classes)}")
        if functions:
            summary_parts.append(f"Functions: {', '.join(functions[:4])}")
        if decorators:
            summary_parts.append(f"Decorators: {', '.join(decorators)}")
        if constants:
            summary_parts.append(f"Constants: {', '.join(constants)}")

        # Add file type indicators
        if any('async def' in l for l in lines):
            summary_parts.append("Async support")
        if any('__main__' in l for l in lines):
            summary_parts.append("Executable")
        if any('if __name__' in l for l in lines):
            summary_parts.append("Script entry point")

    except Exception as e:
        return f"Python file (parsing error: {str(e)[:30]})"

    return ' | '.join(summary_parts) if summary_parts else "Python module"

def extract_javascript_summary(content):
    """Extract enhanced JavaScript/TypeScript code summary"""
    summary_parts = []

    try:
        lines = content.split('\n')
        imports = []
        functions = []
        classes = []
        interfaces = []
        types = []
        components = []

        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith('//') or line.startswith('/*'):
                continue

            # Extract imports with better parsing
            if line.startswith('import ') and len(imports) < 5:
                if 'from ' in line:
                    module = line.split('from ')[1].strip().strip("';\"")
                    imports.append(module)
                elif '{' in line and '}' in line:
                    # Named imports: import { useState, useEffect } from 'react'
                    module_part = line.split('} from ')[-1] if '} from ' in line else ""
                    if module_part:
                        imports.append(module_part.strip().strip("';\""))

            # Extract type definitions
            elif line.startswith(('type ', 'interface ')) and len(types) < 3:
                if line.startswith('interface '):
                    interface_name = line.split('interface ')[1].split()[0]
                    interfaces.append(interface_name)
                elif line.startswith('type '):
                    type_name = line.split('type ')[1].split('=')[0].strip()
                    types.append(type_name)

            # Extract function definitions
            elif ('function ' in line or '=> ' in line or 'const ' in line) and len(functions) < 4:
                if 'function ' in line:
                    func_name = line.split('function ')[1].split('(')[0].strip()
                    functions.append(f"{func_name}()")
                elif '=> ' in line and 'const ' in line:
                    # Arrow function: const funcName = () => {}
                    func_name = line.split('const ')[1].split('=')[0].strip()
                    functions.append(f"{func_name}=>")
                elif 'const ' in line and '=>' in line:
                    # Alternative arrow function pattern
                    func_name = line.split('const ')[1].split('=')[0].strip()
                    functions.append(f"{func_name}=>")

            # Extract class definitions
            elif line.startswith('class ') and len(classes) < 3:
                class_name = line.split('class ')[1].split()[0]
                classes.append(class_name)

            # Detect React components
            elif ('function ' in line or 'const ' in line) and len(components) < 2:
                if any(keyword in line.upper() for keyword in ['COMPONENT', 'JSX', 'REACT']):
                    if 'function ' in line:
                        comp_name = line.split('function ')[1].split('(')[0].strip()
                        components.append(f"FC:{comp_name}")
                    elif 'const ' in line and ('(' in line or '<' in line):
                        comp_name = line.split('const ')[1].split('=')[0].strip()
                        components.append(f"Comp:{comp_name}")

        # Build summary with priorities
        if imports:
            summary_parts.append(f"Imports: {', '.join(imports[:5])}")
        if components:
            summary_parts.append(f"Components: {', '.join(components)}")
        if classes:
            summary_parts.append(f"Classes: {', '.join(classes)}")
        if functions:
            summary_parts.append(f"Functions: {', '.join(functions[:4])}")
        if interfaces:
            summary_parts.append(f"Interfaces: {', '.join(interfaces)}")
        if types:
            summary_parts.append(f"Types: {', '.join(types)}")

        # Add framework indicators
        if any('react' in imp.lower() for imp in imports):
            summary_parts.append("React")
        if any('vue' in imp.lower() for imp in imports):
            summary_parts.append("Vue")
        if any('angular' in imp.lower() for imp in imports):
            summary_parts.append("Angular")
        if any('express' in imp.lower() for imp in imports):
            summary_parts.append("Express")
        if any('typescript' in l.lower() for l in lines):
            summary_parts.append("TypeScript")

    except Exception as e:
        return f"JavaScript/TypeScript file (parsing error: {str(e)[:30]})"

    return ' | '.join(summary_parts) if summary_parts else "JavaScript/TypeScript module"

def extract_compiled_summary(content):
    """Extract enhanced summary for compiled languages (Java, C++, C#, etc.)"""
    summary_parts = []

    try:
        lines = content.split('\n')
        includes = []
        usings = []
        imports = []
        classes = []
        functions = []
        namespaces = []

        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith('//') or line.startswith('/*'):
                continue

            # Extract includes (C/C++)
            if line.startswith('#include ') and len(includes) < 4:
                if '<' in line and '>' in line:
                    header = line.split('<')[1].split('>')[0]
                    includes.append(header)
                elif '"' in line:
                    header = line.split('"')[1]
                    includes.append(header)

            # Extract using statements (C#)
            elif line.startswith('using ') and len(usings) < 4:
                namespace = line.split('using ')[1].split(';')[0]
                usings.append(namespace)

            # Extract imports (Java)
            elif line.startswith('import ') and len(imports) < 4:
                package = line.split('import ')[1].split(';')[0]
                imports.append(package)

            # Extract namespace/package declarations
            elif line.startswith(('namespace ', 'package ')) and len(namespaces) < 2:
                ns = line.split()[1].split(';')[0]
                namespaces.append(ns)

            # Extract class definitions with modifiers
            elif ('class ' in line or 'interface ' in line) and len(classes) < 3:
                # Look for access modifiers
                modifiers = []
                if 'public ' in line:
                    modifiers.append('public')
                if 'private ' in line:
                    modifiers.append('private')
                if 'protected ' in line:
                    modifiers.append('protected')
                if 'static ' in line:
                    modifiers.append('static')

                if 'class ' in line:
                    class_name = line.split('class ')[1].split()[0]
                    classes.append(f"{' '.join(modifiers)} class {class_name}")
                elif 'interface ' in line:
                    interface_name = line.split('interface ')[1].split()[0]
                    classes.append(f"{' '.join(modifiers)} interface {interface_name}")

            # Extract function/method definitions
            elif ('(' in line and ')' in line and '{' in line) and len(functions) < 4:
                # Skip control structures
                if any(keyword in line for keyword in ['if ', 'for ', 'while ', 'switch ']):
                    continue

                # Extract function name
                func_part = line.split('(')[0].strip()
                func_name = func_part.split()[-1]

                # Extract return type and modifiers
                remaining = func_part.split()
                return_type = remaining[-2] if len(remaining) > 1 else "void"
                modifiers = remaining[:-2] if len(remaining) > 2 else []

                if func_name and not func_name.startswith(('if', 'for', 'while')):
                    functions.append(f"{' '.join(modifiers)} {return_type} {func_name}()")

        # Build summary based on language patterns
        all_deps = includes + usings + imports
        if all_deps:
            summary_parts.append(f"Dependencies: {', '.join(all_deps[:5])}")

        if namespaces:
            summary_parts.append(f"Namespaces: {', '.join(namespaces)}")

        if classes:
            summary_parts.append(f"Types: {', '.join(classes)}")

        if functions:
            summary_parts.append(f"Functions: {', '.join(functions[:4])}")

        # Language-specific indicators
        if includes:
            summary_parts.append("C/C++")
        if usings:
            summary_parts.append("C#")
        if any('System.' in str(imports) for imp in imports):
            summary_parts.append(".NET")
        if any('java.' in str(imports) for imp in imports):
            summary_parts.append("Java")

    except Exception as e:
        return f"Compiled language file (parsing error: {str(e)[:30]})"

    return ' | '.join(summary_parts) if summary_parts else "Compiled language module"

def extract_config_summary(content):
    """Extract concise summary for config files (JSON, YAML)"""
    try:
        if content.strip().startswith('{'):  # JSON
            import json
            data = json.loads(content)
            keys = list(data.keys())[:5]
            return f"Config keys: {', '.join(keys)}"
        else:  # YAML or other
            lines = content.split('\n')
            top_keys = []
            for line in lines:
                if line.startswith(('  ', '\t')):  # Skip nested keys for brevity
                    continue
                if ':' in line and not line.startswith('#'):
                    key = line.split(':')[0].strip()
                    if key and len(top_keys) < 5:
                        top_keys.append(key)
            return f"Config sections: {', '.join(top_keys)}" if top_keys else ""
    except:
        return "Configuration file"

def extract_docs_summary(content):
    """Extract concise summary for documentation files"""
    lines = content.split('\n')
    headers = []
    for line in lines:
        if line.startswith('#') and len(headers) < 3:
            header = line.strip('#').strip()
            if header:
                headers.append(header[:30])  # Limit header length
    return f"Sections: {', '.join(headers)}" if headers else "Documentation"

def extract_go_summary(content):
    """Extract summary for Go language files"""
    summary_parts = []

    try:
        lines = content.split('\n')
        imports = []
        functions = []
        structs = []
        interfaces = []
        packages = []

        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith('//'):
                continue

            # Extract package declaration
            if line.startswith('package ') and len(packages) < 1:
                pkg = line.split('package ')[1]
                packages.append(pkg)

            # Extract imports
            elif line.startswith('import ') and len(imports) < 4:
                if '(' in line:  # Multi-line imports
                    # Handle multi-line imports
                    j = i + 1
                    while j < len(lines) and not lines[j].strip().startswith(')'):
                        imp_line = lines[j].strip().strip('"')
                        if imp_line and not imp_line.startswith('//'):
                            imports.append(imp_line)
                        j += 1
                else:
                    imp = line.split('"')[1] if '"' in line else ""
                    if imp:
                        imports.append(imp)

            # Extract function definitions
            elif line.startswith('func ') and len(functions) < 4:
                func_line = line.split('func ')[1]
                if '(' in func_line:  # Method or function with receiver
                    func_name = func_line.split('(')[0].strip()
                    functions.append(f"func {func_name}")
                else:
                    func_name = func_line.split('(')[0].strip()
                    functions.append(f"func {func_name}")

            # Extract type definitions
            elif line.startswith('type ') and len(structs) < 3:
                type_line = line.split('type ')[1]
                type_name = type_line.split()[0]
                type_kind = type_line.split()[1] if len(type_line.split()) > 1 else ""

                if 'struct' in type_kind:
                    structs.append(f"struct {type_name}")
                elif 'interface' in type_kind:
                    interfaces.append(f"interface {type_name}")

        # Build summary
        if packages:
            summary_parts.append(f"Package: {packages[0]}")
        if imports:
            summary_parts.append(f"Imports: {', '.join(imports[:4])}")
        if functions:
            summary_parts.append(f"Functions: {', '.join(functions[:4])}")
        if structs:
            summary_parts.append(f"Structs: {', '.join(structs)}")
        if interfaces:
            summary_parts.append(f"Interfaces: {', '.join(interfaces)}")

        summary_parts.append("Go")

    except Exception as e:
        return f"Go file (parsing error: {str(e)[:30]})"

    return ' | '.join(summary_parts) if summary_parts else "Go module"

def extract_rust_summary(content):
    """Extract summary for Rust language files"""
    summary_parts = []

    try:
        lines = content.split('\n')
        mods = []
        functions = []
        structs = []
        enums = []
        traits = []
        uses = []

        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith('//'):
                continue

            # Extract use statements
            if line.startswith('use ') and len(uses) < 4:
                use_path = line.split('use ')[1].split(';')[0]
                uses.append(use_path)

            # Extract module declarations
            elif line.startswith('mod ') and len(mods) < 3:
                mod_name = line.split('mod ')[1].split(';')[0].split()[0]
                mods.append(mod_name)

            # Extract function definitions
            elif line.startswith(('fn ', 'pub fn ')) and len(functions) < 4:
                fn_line = line.replace('pub ', '').split('fn ')[1]
                fn_name = fn_line.split('(')[0].strip()
                functions.append(f"fn {fn_name}")

            # Extract struct definitions
            elif line.startswith(('struct ', 'pub struct ')) and len(structs) < 3:
                struct_line = line.replace('pub ', '').split('struct ')[1]
                struct_name = struct_line.split()[0]
                structs.append(f"struct {struct_name}")

            # Extract enum definitions
            elif line.startswith(('enum ', 'pub enum ')) and len(enums) < 3:
                enum_line = line.replace('pub ', '').split('enum ')[1]
                enum_name = enum_line.split()[0]
                enums.append(f"enum {enum_name}")

            # Extract trait definitions
            elif line.startswith(('trait ', 'pub trait ')) and len(traits) < 2:
                trait_line = line.replace('pub ', '').split('trait ')[1]
                trait_name = trait_line.split()[0]
                traits.append(f"trait {trait_name}")

        # Build summary
        if uses:
            summary_parts.append(f"Uses: {', '.join(uses[:4])}")
        if mods:
            summary_parts.append(f"Modules: {', '.join(mods)}")
        if functions:
            summary_parts.append(f"Functions: {', '.join(functions[:4])}")
        if structs:
            summary_parts.append(f"Structs: {', '.join(structs)}")
        if enums:
            summary_parts.append(f"Enums: {', '.join(enums)}")
        if traits:
            summary_parts.append(f"Traits: {', '.join(traits)}")

        summary_parts.append("Rust")

    except Exception as e:
        return f"Rust file (parsing error: {str(e)[:30]})"

    return ' | '.join(summary_parts) if summary_parts else "Rust module"

def extract_php_summary(content):
    """Extract summary for PHP language files"""
    summary_parts = []

    try:
        lines = content.split('\n')
        namespaces = []
        uses = []
        classes = []
        functions = []
        interfaces = []

        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith('//') or line.startswith('#'):
                continue

            # Extract namespace
            if line.startswith('namespace ') and len(namespaces) < 1:
                ns = line.split('namespace ')[1].split(';')[0]
                namespaces.append(ns)

            # Extract use statements
            elif line.startswith('use ') and len(uses) < 4:
                use_path = line.split('use ')[1].split(';')[0]
                uses.append(use_path)

            # Extract class definitions
            elif line.startswith(('class ', 'abstract class ', 'final class ')) and len(classes) < 3:
                class_line = line.replace('abstract ', '').replace('final ', '').split('class ')[1]
                class_name = class_line.split()[0]
                classes.append(f"class {class_name}")

            # Extract function definitions
            elif line.startswith(('function ', 'public function ', 'private function ', 'protected function ')) and len(functions) < 4:
                func_line = line.replace('public ', '').replace('private ', '').replace('protected ', '').split('function ')[1]
                func_name = func_line.split('(')[0].strip()
                functions.append(f"function {func_name}")

            # Extract interface definitions
            elif line.startswith('interface ') and len(interfaces) < 2:
                interface_name = line.split('interface ')[1].split()[0]
                interfaces.append(f"interface {interface_name}")

        # Build summary
        if namespaces:
            summary_parts.append(f"Namespace: {namespaces[0]}")
        if uses:
            summary_parts.append(f"Uses: {', '.join(uses[:4])}")
        if classes:
            summary_parts.append(f"Classes: {', '.join(classes)}")
        if functions:
            summary_parts.append(f"Functions: {', '.join(functions[:4])}")
        if interfaces:
            summary_parts.append(f"Interfaces: {', '.join(interfaces)}")

        summary_parts.append("PHP")

    except Exception as e:
        return f"PHP file (parsing error: {str(e)[:30]})"

    return ' | '.join(summary_parts) if summary_parts else "PHP module"

def get_file_metadata(file_path):
    """Get lightweight file metadata optimized for AI context windows (~500 chars max additional)"""
    try:
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_path)[-1].lower()

        metadata = {
            "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
            "type": file_ext,
            "ai_description": get_ai_description(file_path, file_name),
            "extracted_description": "",
            "size_bytes": 0,
            "code_summary": ""  # New field: concise code symbols and relationships (~300 chars max)
        }

        # Get file size
        try:
            size = os.path.getsize(file_path)
            metadata["size_bytes"] = size
            if size == 0:
                metadata["extracted_description"] = "(Empty file)"
                return metadata
        except:
            metadata["extracted_description"] = "(Error reading file)"
            return metadata

        if is_text_file(file_path):
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                    # Extract first meaningful line for description
                    lines = content.split('\n')
                    for line in lines[:5]:  # Check first 5 lines
                        line = line.strip()
                        if line and not line.startswith('#') and not line.startswith('//'):
                            metadata["extracted_description"] = line[:80]  # Shorter preview
                            break

                    # Generate concise code summary for AI agents
                    if file_ext == '.py':
                        metadata["code_summary"] = extract_python_summary(content)
                    elif file_ext in ['.js', '.jsx', '.ts', '.tsx']:
                        metadata["code_summary"] = extract_javascript_summary(content)
                    elif file_ext in ['.java', '.cs', '.cpp', '.c']:
                        metadata["code_summary"] = extract_compiled_summary(content)
                    elif file_ext == '.go':
                        metadata["code_summary"] = extract_go_summary(content)
                    elif file_ext == '.rs':
                        metadata["code_summary"] = extract_rust_summary(content)
                    elif file_ext == '.php':
                        metadata["code_summary"] = extract_php_summary(content)
                    elif file_ext in ['.json', '.yaml', '.yml']:
                        metadata["code_summary"] = extract_config_summary(content)
                    elif file_ext in ['.md', '.txt']:
                        metadata["code_summary"] = extract_docs_summary(content)

                    # Ensure summary stays within ~300 character limit
                    if len(metadata["code_summary"]) > 300:
                        metadata["code_summary"] = metadata["code_summary"][:297] + "..."

            except Exception as e:
                metadata["extracted_description"] = f"(Error reading: {str(e)[:50]})"
        else:
            metadata["extracted_description"] = "(Binary file)"

        return metadata
    except Exception as e:
        return {
            "modified": "",
            "type": "",
            "ai_description": "Unknown file type",
            "extracted_description": f"(Error: {str(e)[:50]})",
            "size_bytes": 0,
            "code_summary": ""
        }

def generate_repo_schema(base_dir, gitignore_spec):
    schema = {
        "project": os.path.basename(os.path.abspath(base_dir)),
        "version": "1.0",
        "taxonomy": [],
        "files_scanned": 0,
        "files_processed": 0
    }
    
    print(f"Scanning directory: {os.path.abspath(base_dir)}")

    total_files_scanned = 0
    total_files_processed = 0

    try:
        for root, dirs, files_in_dir in os.walk(base_dir, topdown=True):
            if DEBUG: print(f"DEBUG_OS_WALK: Processing directory (root): {root}")

            # Prune ignored directories from os.walk's list for future traversal
            dirs_to_prune_from_walk = []
            if DEBUG: print(f"DEBUG_PRUNING: Checking subdirectories for pruning in '{os.path.relpath(root, base_dir) or '.'}'. Original subdirs for os.walk: {dirs}")
            for d_name in list(dirs): # Iterate over a copy of dirs
                dir_path_to_check = os.path.join(root, d_name)
                if is_ignored(dir_path_to_check, base_dir, gitignore_spec):
                    if DEBUG: print(f"DEBUG_PRUNING: Subdirectory '{d_name}' in '{os.path.relpath(root, base_dir) or '.'}' IS marked as ignored. Adding to os.walk prune list.")
                    dirs_to_prune_from_walk.append(d_name)
                elif DEBUG and d_name == "vendor" and root == base_dir:
                     print(f"DEBUG_PRUNING_VENDOR_NOT_IGNORED: Top-level 'vendor' subdir was NOT marked as ignored by is_ignored() for os.walk pruning.")
                # elif DEBUG: # Too verbose otherwise
                    # print(f"DEBUG_PRUNING: Subdirectory '{d_name}' in '{os.path.relpath(root, base_dir) or '.'}' is NOT ignored.")

            if dirs_to_prune_from_walk:
                for d_remove in dirs_to_prune_from_walk:
                    if d_remove in dirs: # Ensure it's still in the list to avoid error
                        dirs.remove(d_remove) # Modifies dirs IN PLACE, affecting os.walk
                if DEBUG: print(f"DEBUG_PRUNING: Pruned {len(dirs_to_prune_from_walk)} subdir(s) ({dirs_to_prune_from_walk}) from os.walk list in '{os.path.relpath(root, base_dir) or '.'}'. Subdirs remaining for os.walk: {dirs}")
            elif DEBUG:
                print(f"DEBUG_PRUNING: No subdirs were pruned from os.walk list in '{os.path.relpath(root, base_dir) or '.'}'. Subdirs for os.walk processing: {dirs}")

            current_dir_relative = os.path.relpath(root, base_dir)
            if current_dir_relative == ".":
                entry = {
                    "folder": "./",
                    "files": [],
                    "subfolders": sorted([d for d in dirs])
                }
            else:
                entry = {
                    "folder": current_dir_relative,
                    "files": [],
                    "subfolders": sorted([d for d in dirs])
                }

            files_in_current_dir = 0
            for file in files_in_dir:
                file_path = os.path.join(root, file)
                schema["files_scanned"] += 1
                total_files_scanned += 1

                if is_ignored(file_path, base_dir, gitignore_spec):
                    continue

                schema["files_processed"] += 1
                total_files_processed += 1
                files_in_current_dir += 1

                if schema["files_processed"] % 10 == 0:
                    sys.stdout.write(f"\rFiles Scanned: {schema['files_scanned']} | Files Processed: {schema['files_processed']}...")
                    sys.stdout.flush()

                rel_path = os.path.relpath(file_path, base_dir)
                entry["files"].append({
                    "name": file,
                    "path": rel_path.replace('\\\\', '/'),
                    "metadata": get_file_metadata(file_path)
                })

            if files_in_current_dir > 0 or (current_dir_relative == '.' and entry["subfolders"]):
                entry["files"].sort(key=lambda x: x['name'].lower())
                schema["taxonomy"].append(entry)
    except KeyboardInterrupt:
        print("\nFile scanning interrupted by user")
        logging.warning("File scanning interrupted by user during os.walk")
        # Continue with partial results
    except Exception as e:
        print(f"Error during file scanning: {e}")
        logging.error(f"Error during file scanning: {e}", exc_info=True)
        # Continue with partial results
    
    print("\n")
    return schema

def format_metadata(file, file_prefix):
    """Helper function to format file metadata"""
    metadata = file['metadata']
    # Use the same prefix as the file node plus additional indentation
    indent = file_prefix + "    "  # Four spaces for alignment
    meta_str = ""
    if metadata.get('type'):
        meta_str += f"{indent}Type: {metadata['type']}\n"
    if metadata.get('modified'):
        meta_str += f"{indent}Modified: {metadata['modified']}\n"
    if metadata.get('ai_description'):
        meta_str += f"{indent}Description: {metadata['ai_description']}\n"
    if metadata.get('extracted_description'):
        meta_str += f"{indent}Content: {metadata['extracted_description']}\n"
    return meta_str

def format_tree(entries, prefix="", base_dir=None, gitignore_spec=None):
    tree = ""
    base_indent = "    "  # Base indentation for all items

    # Separate root files and folder entries
    folder_map = {entry['folder']: entry for entry in entries if entry['folder'] != './'}
    root_files_entry = next((entry for entry in entries if entry['folder'] == './'), None)

    # Sort folder paths for deterministic order
    sorted_folder_paths = sorted(folder_map.keys(), key=lambda x: x.lower())

    # Helper function to build the tree recursively
    def build_tree_recursive(folder_path, current_prefix=""):
        if not folder_path: # Should be './' for root
            return ""

        # Get the entry for the current folder
        folder_entry = folder_map.get(folder_path) if folder_path != './' else root_files_entry
        if not folder_entry:
            return "" # Should not happen if logic is correct

        display_name = os.path.basename(folder_path) if folder_path != './' else './'
        branch = "└── " if not folder_entry.get("subfolders") else "├── " # Placeholder, needs adjustment based on siblings

        # Indentation based on depth
        depth = folder_path.count(os.sep) if folder_path != './' else 0
        indent = base_indent * depth
        node_prefix = current_prefix + indent

        line = f"{node_prefix}📁 {display_name}\n"

        # Process files within this folder
        files = sorted(folder_entry.get('files', []), key=lambda x: x['name'].lower())
        file_indent = base_indent * (depth + 1)
        file_node_prefix = current_prefix + file_indent

        num_files = len(files)
        for i, file in enumerate(files):
            is_last_file = i == num_files - 1
            file_branch = "└── " if is_last_file else "├── "
            line += f"{file_node_prefix}{file_branch}📄 {file['name']}\n"
            # Use the helper function for metadata formatting
            try:
                line += format_metadata(file, file_node_prefix) # Pass the correct prefix
            except KeyboardInterrupt:
                print("\nMetadata formatting interrupted by user")
                logging.warning("Metadata formatting interrupted by user")
                break
            except Exception as e:
                logging.error(f"Error formatting metadata for {file['name']}: {e}")
                line += f"{file_node_prefix}    Error: {str(e)}\n"

        # Recursively process subfolders
        subfolders = sorted(folder_entry.get("subfolders", []), key=str.lower)
        num_subfolders = len(subfolders)
        for i, subfolder_name in enumerate(subfolders):
            subfolder_rel_path = os.path.join(folder_path, subfolder_name) if folder_path != './' else subfolder_name
            # Check if subfolder is ignored (using correct base_dir and spec)
            if base_dir and gitignore_spec and is_ignored(os.path.join(base_dir, subfolder_rel_path), base_dir, gitignore_spec):
                continue

            # Determine the prefix for the recursive call (handling tree lines)
            # This part is complex to get right visually, might need refinement
            # is_last_sub = i == num_subfolders - 1
            # pipe_prefix = "|   " if not is_last_sub else "    "
            # line += build_tree_recursive(subfolder_rel_path, current_prefix + pipe_prefix)
            try:
                line += build_tree_recursive(subfolder_rel_path, current_prefix) # Simpler recursion for now
            except KeyboardInterrupt:
                print("\nTree building interrupted by user")
                logging.warning("Tree building interrupted by user")
                break
            except Exception as e:
                logging.error(f"Error building tree for {subfolder_rel_path}: {e}")
                line += f"{current_prefix}    Error processing {subfolder_name}\n"

        return line

    # Start building the tree from the root
    # tree += build_tree_recursive('./') # Start with root

    # Simpler iterative approach based on sorted paths for now, rebuild format_tree if needed
    processed_folders = set()

    def add_folder_entry(entry, depth):
        nonlocal tree
        folder_rel_path = entry['folder']
        if folder_rel_path in processed_folders: return
        processed_folders.add(folder_rel_path)

        display_name = os.path.basename(folder_rel_path) if folder_rel_path != './' else './'
        indent = base_indent * depth
        tree += f"{prefix}{indent}📁 {display_name}\n"

        files = sorted(entry.get('files', []), key=lambda x: x['name'].lower())
        file_prefix = prefix + base_indent * (depth + 1)
        num_files = len(files)
        for i, file in enumerate(files):
            is_last_file = i == num_files - 1
            file_branch = "└── " if is_last_file else "├── "
            tree += f"{file_prefix}{file_branch}📄 {file['name']}\n"
            try:
                tree += format_metadata(file, file_prefix)
            except KeyboardInterrupt:
                print("\nMetadata formatting interrupted by user")
                logging.warning("Metadata formatting interrupted by user in add_folder_entry")
                break
            except Exception as e:
                logging.error(f"Error formatting metadata for {file['name']}: {e}")
                tree += f"{file_prefix}    Error: {str(e)}\n"

    # Process root first if it exists
    if root_files_entry:
        try:
            add_folder_entry(root_files_entry, 0)
        except KeyboardInterrupt:
            print("\nRoot folder processing interrupted by user")
            logging.warning("Root folder processing interrupted by user")
        except Exception as e:
            logging.error(f"Error processing root folder: {e}")

    # Process other folders based on depth
    for folder_rel_path in sorted_folder_paths:
         depth = folder_rel_path.count(os.sep)
         entry = folder_map[folder_rel_path]
         # Basic check - ensure parent was processed (simplistic, assumes top-down iteration)
         parent = os.path.dirname(folder_rel_path) if folder_rel_path != '.' else '.'
         parent_key = parent if parent != '.' else './'
         # This check is flawed, os.walk guarantees parent first. Add entry directly.
         try:
             add_folder_entry(entry, depth + 1) # +1 because root is depth 0
         except KeyboardInterrupt:
             print("\nFolder processing interrupted by user")
             logging.warning("Folder processing interrupted by user")
             break
         except Exception as e:
             logging.error(f"Error processing folder {folder_rel_path}: {e}")

    return tree

def generate_markdown(schema, base_dir, gitignore_spec):
    markdown = f"# {schema['project']} v{schema['version']}\n\n"
    markdown += f"Scanned Path: {os.path.abspath(base_dir)}\n"
    markdown += f"Files Scanned: {schema.get('files_scanned', 0)}\n"
    markdown += f"Files Processed (after ignores): {schema.get('files_processed', 0)}\n\n"
    markdown += "## Project Structure with Details\n\n```\n"

    # Generate the tree structure with embedded metadata
    markdown += format_tree(schema['taxonomy'], base_dir=base_dir, gitignore_spec=gitignore_spec)
    markdown += "\n```\n"

    return markdown

def run_schema_generation(base_dir, output_dir, ignore_file_path=None, qdrant_url=None, qdrant_api_key=None, project_name=None, store_qdrant=False, generate_dependency_graph_flag=True):
    """Core logic to generate schema, callable as a function."""
    logging.info(f"Starting schema generation for base_dir: {base_dir}, output_dir: {output_dir}, ignore_file: {ignore_file_path}")

    results = {
        "success": False,
        "message": "",
        "json_output_path": None,
        "md_output_path": None,
        "files_scanned": 0,
        "files_processed": 0
    }

    try:
        # Ensure base_dir and output_dir are absolute paths
        base_dir = os.path.abspath(base_dir)
        output_dir = os.path.abspath(output_dir)
        ignore_file_path = os.path.abspath(ignore_file_path) if ignore_file_path else None

        # Validate base_dir exists
        if not os.path.isdir(base_dir):
            results["message"] = f"Error: Base directory not found or is not a directory: {base_dir}"
            return results

        # Create output subdirectories if they don't exist
        output_schema_dir = output_dir # Use the provided output_dir directly
        os.makedirs(output_schema_dir, exist_ok=True)

        # Define output file paths based on output_dir
        output_json_path = os.path.join(output_schema_dir, "repo-schema.json")
        output_md_path = os.path.join(output_schema_dir, "repo-schema.md")
        results["json_output_path"] = output_json_path
        results["md_output_path"] = output_md_path

        logging.info(f"JSON output path: {output_json_path}")
        logging.info(f"Markdown output path: {output_md_path}")

        print(f"\nStarting repository analysis for: {base_dir}")
        print(f"Output will be saved to: {output_dir}")
        if ignore_file_path:
            print(f"Using custom ignore file: {ignore_file_path}")

        # Load ignore patterns using the correct base_dir and optional custom file
        gitignore_spec = load_gitignore_patterns(base_dir, ignore_file_path)
        logging.info(f"Loaded ignore patterns from .repoignore and optional .gitignore")

        # Generate schema using the correct base_dir and ignore spec
        schema = generate_repo_schema(base_dir, gitignore_spec)
        results["files_scanned"] = schema.get('files_scanned', 0)
        results["files_processed"] = schema.get('files_processed', 0)

        # Store in Qdrant if requested
        if store_qdrant and QDRANT_AVAILABLE:
            try:
                logging.info("Initializing Qdrant client...")
                qdrant_manager = QdrantManager(url=qdrant_url, api_key=qdrant_api_key)

                # Determine project name
                if not project_name:
                    project_name = schema.get('project', 'unknown_project')

                # Generate collection name
                collection_name = qdrant_manager.generate_collection_name(project_name, base_dir)
                logging.info(f"Using collection name: {collection_name}")

                # Create collection if it doesn't exist
                if not qdrant_manager.collection_exists(collection_name):
                    if qdrant_manager.create_collection(collection_name):
                        logging.info(f"Created new collection: {collection_name}")
                    else:
                        logging.error("Failed to create collection")
                        results["message"] += " Warning: Failed to create Qdrant collection."

                # Store schema data in Qdrant (without vectors for now)
                stored_count = 0
                for entry in schema.get('taxonomy', []):
                    for file_info in entry.get('files', []):
                        file_path = file_info.get('path', '')
                        metadata = file_info.get('metadata', {})

                        # Create knowledge graph payload
                        knowledge_graph = {
                            "fileType": metadata.get('type', ''),
                            "aiDescription": metadata.get('ai_description', ''),
                            "extractedDescription": metadata.get('extracted_description', ''),
                            "modified": metadata.get('modified', ''),
                            "folder": entry.get('folder', '')
                        }

                        # Use dummy vector for now (since we don't have embeddings)
                        dummy_vector = [0.0] * 1536  # Standard embedding size

                        if qdrant_manager.store_knowledge_graph(
                            collection_name=collection_name,
                            file_path=file_path,
                            vector=dummy_vector,
                            knowledge_graph=knowledge_graph
                        ):
                            stored_count += 1

                logging.info(f"Stored {stored_count} files in Qdrant collection: {collection_name}")
                results["qdrant_collection"] = collection_name
                results["qdrant_stored_count"] = stored_count

            except Exception as e:
                logging.error(f"Qdrant storage failed: {e}")
                results["message"] += f" Warning: Qdrant storage failed: {e}"
        elif store_qdrant and not QDRANT_AVAILABLE:
            logging.warning("Qdrant storage requested but qdrant-client not available")
            results["message"] += " Warning: Qdrant client not available."

        # Generate JSON output to the specified path
        print(f"\nWriting JSON output to: {output_json_path}")
        try:
            with open(output_json_path, "w", encoding="utf-8") as f:
                json.dump(schema, f, indent=2)
        except Exception as e:
            results["message"] = f"Error writing JSON file: {e}"
            return results

        # Generate Markdown output to the specified path
        print(f"Writing Markdown output to: {output_md_path}")
        try:
            # Pass base_dir and spec needed for formatting/checking within generate_markdown/format_tree
            markdown_content = generate_markdown(schema, base_dir, gitignore_spec)
            with open(output_md_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)
        except KeyboardInterrupt:
            print("\nMarkdown generation interrupted by user")
            logging.warning("Markdown generation interrupted by user")
            results["message"] = "Schema generation partially completed (interrupted during markdown generation)"
            results["success"] = False
            return results
        except Exception as e:
            results["message"] = f"Error writing Markdown file: {e}"
            logging.error(f"Error writing Markdown file: {e}", exc_info=True)
            return results

        # Generate dependency graph if requested and available
        if generate_dependency_graph_flag and DEPENDENCY_GRAPH_AVAILABLE:
            print("Generating dependency graph...")
            try:
                dependency_graph_path = os.path.join(output_schema_dir, "dependency-graph.json")
                results["dependency_graph_path"] = dependency_graph_path

                # Generate dependency graph from the schema
                graph_generator = DependencyGraphGenerator()
                dependency_graph = graph_generator.generate_from_schema(schema)

                # Save the dependency graph
                graph_generator.save_graph(dependency_graph_path)

                # Add dependency graph statistics to results
                cycles = dependency_graph.detect_cycles()
                results["dependency_graph_stats"] = {
                    "nodes": len(dependency_graph.nodes),
                    "edges": len(dependency_graph.edges),
                    "cycles": len(cycles)
                }

                if cycles:
                    logging.warning(f"Detected {len(cycles)} circular dependencies in dependency graph")
                    results["message"] += f" Warning: {len(cycles)} circular dependencies detected."

                print(f"Dependency graph generated: {len(dependency_graph.nodes)} nodes, {len(dependency_graph.edges)} edges")

            except Exception as e:
                logging.error(f"Error generating dependency graph: {e}")
                results["message"] += f" Warning: Dependency graph generation failed: {e}"
        elif generate_dependency_graph_flag and not DEPENDENCY_GRAPH_AVAILABLE:
            logging.warning("Dependency graph generation requested but module not available")
            results["message"] += " Warning: Dependency graph module not available."

        results["success"] = True
        results["message"] = "Schema generation completed successfully."
        logging.info("Schema generation completed successfully.")

    except KeyboardInterrupt:
        print("\nOperation interrupted by user (Ctrl+C)")
        results["message"] = "Schema generation was interrupted by user"
        logging.warning("Schema generation interrupted by user (KeyboardInterrupt)")
        # Don't mark as success but don't exit with error code for interrupts
        results["success"] = False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        results["message"] = f"An unexpected error occurred during schema generation: {e}"
        logging.error(f"Unexpected error during schema generation: {e}", exc_info=True)

    print(f"\n\nTask completed:")
    print(f"  Base Directory: {base_dir}")
    print(f"  Files Scanned: {results['files_scanned']}")
    print(f"  Files Processed (after ignores): {results['files_processed']}")
    print(f"  Output Schema Dir: {output_schema_dir}")
    print(f"    - {os.path.basename(output_json_path)}")
    print(f"    - {os.path.basename(output_md_path)}")

    if 'dependency_graph_path' in results:
        print(f"    - {os.path.basename(results['dependency_graph_path'])}")
        if 'dependency_graph_stats' in results:
            stats = results['dependency_graph_stats']
            print(f"  Dependency Graph: {stats['nodes']} nodes, {stats['edges']} edges")
            if stats['cycles'] > 0:
                print(f"  Circular Dependencies: {stats['cycles']} detected")

    logging.info(f"Task completed: {results['message']}")

    return results

def signal_handler(signum, frame):
    """Handle interrupt signals gracefully"""
    print("\nOperation interrupted by user")
    logging.warning("Operation interrupted by user (signal)")
    sys.exit(1)

def main():
    """Main execution function when run as script"""
    # Setup signal handler for graceful interruption
    signal.signal(signal.SIGINT, signal_handler)

    # Setup logging
    os.makedirs('log', exist_ok=True)
    logging.basicConfig(filename='log/repo-schema.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Job started: Repository schema generation")

    parser = argparse.ArgumentParser(description="Generate repository schema.")
    # Add arguments but make them not required for now, we'll handle prompting
    parser.add_argument('--base-dir', help='(Optional) The root directory of the repository to scan. Overrides interactive prompt.')
    parser.add_argument('--output-dir', help='(Optional) The directory where output files will be created. Overrides interactive prompt.')
    parser.add_argument('--ignore-file', help='(Optional) Path to a custom file containing gitignore-style patterns. Overrides automatic detection.')
    parser.add_argument('--qdrant-url', default='http://localhost:6333', help='Qdrant server URL')
    parser.add_argument('--qdrant-api-key', help='Qdrant API key')
    parser.add_argument('--project-name', help='Project name for collection naming')
    parser.add_argument('--store-qdrant', action='store_true', help='Store schema data in Qdrant vector database')
    parser.add_argument('--generate-dependency-graph', action='store_true', default=True, help='Generate dependency graph (default: True)')
    parser.add_argument('--no-dependency-graph', action='store_true', help='Disable dependency graph generation')
    args = parser.parse_args()

    base_dir_to_use = args.base_dir
    output_dir_to_use = args.output_dir
    ignore_file_to_use = args.ignore_file
    qdrant_url = args.qdrant_url
    qdrant_api_key = args.qdrant_api_key
    project_name = args.project_name
    store_qdrant = args.store_qdrant
    generate_dependency_graph_flag = args.generate_dependency_graph and not args.no_dependency_graph

    logging.info(f"Base directory: {base_dir_to_use}")
    logging.info(f"Output directory: {output_dir_to_use}")
    logging.info(f"Ignore file: {ignore_file_to_use}")
    logging.info(f"Qdrant URL: {qdrant_url}")
    logging.info(f"Qdrant API key: {'***' if qdrant_api_key else 'None'}")
    logging.info(f"Project name: {project_name}")
    logging.info(f"Store in Qdrant: {store_qdrant}")
    logging.info(f"Generate dependency graph: {generate_dependency_graph_flag}")

    # Determine script's directory and suggested project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    suggested_project_root = os.path.dirname(script_dir)

    # 1. Determine Base Directory (Project Root)
    if not base_dir_to_use:
        try:
            response = input(f"'Project Root': [{suggested_project_root}] - Use this directory? (Y/N/Cancel): ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            print("Operation cancelled by user.")
            logging.info("Operation cancelled by user during base directory prompt")
            sys.exit(1)

        if response == 'Y':
            base_dir_to_use = suggested_project_root
            print(f"Using Project Root: {os.path.abspath(base_dir_to_use)}")
        elif response == 'N':
            try:
                base_dir_to_use = input("Please enter the full path to the Project Root: ").strip()
                if not os.path.isdir(base_dir_to_use):
                    print(f"Error: Provided path '{base_dir_to_use}' is not a valid directory.")
                    logging.error(f"Invalid directory provided: {base_dir_to_use}")
                    sys.exit(1)
                print(f"Using Project Root: {os.path.abspath(base_dir_to_use)}")
            except (EOFError, KeyboardInterrupt):
                print("Operation cancelled.")
                logging.info("Operation cancelled by user during directory input")
                sys.exit(1)
        else:
            print("Operation cancelled by user or invalid input.")
            logging.info("Operation cancelled by user or invalid input")
            sys.exit(1)
    else:
        print(f"Using Project Root (from command line): {os.path.abspath(base_dir_to_use)}")

    # 2. Determine Output Directory (will be Project Root, schema subfolder created by run_schema_generation)
    if not output_dir_to_use:
        output_dir_to_use = base_dir_to_use # Output will be in [Project Root]/schema/
        print(f"Output will be generated in: {os.path.abspath(output_dir_to_use)}")
    else:
        print(f"Using Output Directory (from command line): {os.path.abspath(output_dir_to_use)}")
        print(f"Output will be generated in: {os.path.abspath(output_dir_to_use)}")

    # 3. Determine Gitignore File
    if not ignore_file_to_use: # Only try to auto-detect if not specified via CLI
        potential_gitignore_path = os.path.join(base_dir_to_use, ".gitignore")
        if os.path.exists(potential_gitignore_path):
            ignore_file_to_use = potential_gitignore_path
            print(f"Using .gitignore found at: {ignore_file_to_use}")
        else:
            print(f".gitignore not found in {base_dir_to_use}. Proceeding without gitignore rules.")
            ignore_file_to_use = None # Explicitly set to None if not found and not provided
    else:
        if os.path.exists(ignore_file_to_use):
            print(f"Using .gitignore (from command line): {os.path.abspath(ignore_file_to_use)}")
        else:
            print(f"Warning: Custom ignore file specified via command line not found: {ignore_file_to_use}. Proceeding without it.")
            ignore_file_to_use = None

    # Call the core logic function
    results = run_schema_generation(
        base_dir_to_use,
        output_dir_to_use,
        ignore_file_to_use,
        qdrant_url,
        qdrant_api_key,
        project_name,
        store_qdrant,
        generate_dependency_graph_flag
    )

    # Exit with error code if failed
    if not results["success"]:
        print(f"\nError: {results['message']}")
        sys.exit(1)
    else:
        print(f"\n{results['message']}")
        sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation interrupted by user")
        logging.warning("Main execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {e}")
        logging.error(f"Fatal error in main execution: {e}", exc_info=True)
        sys.exit(1)
