# Repository Schema Generator (reposchema)
## AI-Optimized Codebase Indexing for KiloCode/UltraRepo

**Transform your codebase into an intelligent, searchable knowledge graph that AI agents can understand and navigate.**

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/UltraRepo/code)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

## 📋 Summary

Repository Schema Generator is a sophisticated Python application that creates AI-optimized knowledge graphs from code repositories. It transforms raw codebases into structured, searchable representations that enhance code discoverability and enable intelligent AI-powered code analysis.

**Two Editions Available:**
- **🆓 Core Edition**: Local vector database, runs on Docker or local machine
- **💎 Premium Edition**: Remote UltraRepo service with enhanced privacy and AI analysis

## 🎯 Vision

To democratize codebase understanding by creating intelligent knowledge graphs that bridge the gap between human developers and AI coding assistants, enabling seamless collaboration and enhanced productivity.

## 🚨 The Problem

Modern codebases are complex, distributed, and difficult to understand:
- **117,363+ files** in large projects become overwhelming
- **Lost context** when switching between projects
- **AI agents struggle** with raw code without proper structure
- **Search limitations** in traditional code editors
- **Knowledge silos** between team members
- **Onboarding challenges** for new developers

## ✅ The Solution

Repository Schema Generator creates **intelligent knowledge graphs** that:
- **Structure raw code** into searchable, AI-friendly formats
- **Preserve context** across file boundaries and project hierarchies
- **Enable semantic search** beyond keyword matching
- **Support multiple AI agents** with consistent, structured data
- **Scale efficiently** while maintaining performance
- **Integrate seamlessly** with existing development workflows

## 🚀 Key Innovations (Features)

### Core Features (Both Editions)
- **🧠 Intelligent File Analysis**: AI-powered metadata extraction
- **📊 Code Structure Mapping**: Functions, classes, imports, dependencies
- **🔍 Smart Ignore Patterns**: `.repoignore` + `.gitignore` integration
- **📈 Size Optimization**: Knowledge graphs under 250KB for AI context windows
- **🔄 Incremental Updates**: Only re-analyze changed files
- **🛡️ Privacy-First**: No sensitive code sent to external services
- **🔗 Dependency Graph Generation**: Visual representation of code relationships

### Premium Features (UltraRepo Service)
- **🤖 AI-Enhanced Analysis**: LLM-powered semantic understanding
- **🔐 Enterprise Security**: SOC2-compliant data handling
- **📊 Advanced Metrics**: Complexity analysis, maintainability scores
- **🌐 API Endpoint Discovery**: Automatic REST/WebSocket detection
- **🛡️ Security Analysis**: Vulnerability pattern recognition
- **📈 Performance Analytics**: Usage tracking and optimization insights

## 🎁 Benefits

### For Developers
- **⚡ Faster Code Navigation**: Find relevant code in seconds
- **🧠 Better Context**: Understand code relationships and dependencies
- **📚 Knowledge Preservation**: Capture tribal knowledge in structured format
- **🤝 Team Collaboration**: Shared understanding across team members
- **🎯 Precise Search**: Find code by intent, not just keywords

### For AI Agents
- **🧠 Enhanced Understanding**: Structured context for better analysis
- **📏 Context Window Optimization**: Efficient use of token limits
- **🔍 Semantic Search**: Find code by meaning and relationships
- **📊 Structured Data**: Consistent format across all codebases
- **🔄 Real-time Updates**: Always current with latest changes

### For Organizations
- **📈 Productivity Gains**: 30-50% faster code discovery
- **🛡️ Knowledge Security**: Controlled access to codebase intelligence
- **📊 Analytics Insights**: Understand development patterns
- **🎯 Onboarding Acceleration**: New developers productive faster
- **🔄 Continuous Learning**: System improves with usage

## 📋 Technical Details

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   VS Code       │    │  Repo Schema    │    │   Vector DB     │
│   Extension     │◄──►│   Generator     │◄──►│   (Qdrant)     │
│                 │    │                 │    │                 │
│ • UI Controls   │    │ • File Analysis │    │ • Collections   │
│ • Settings      │    │ • KG Creation   │    │ • Search        │
│ • Progress      │    │ • AI Enhancement│    │ • Metadata      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Knowledge     │
                    │   Graph Store   │
                    │   (< 250KB)     │
                    └─────────────────┘
```

### Knowledge Graph Structure

```json
{
  "@context": "https://schema.org/",
  "@type": "CodeRepository",
  "name": "my-project",
  "version": "1.0",
  "aiEnhanced": true,
  "files": [
    {
      "@type": "CodeFile",
      "name": "api.py",
      "path": "src/api.py",
      "language": "python",
      "sizeBytes": 15432,
      "codeSummary": "Functions: create_user, get_user, update_user | Imports: fastapi, sqlalchemy",
      "aiAnalysis": {
        "purpose": "REST API endpoints for user management",
        "complexity": "medium",
        "apiEndpoints": ["/users", "/users/{id}"],
        "dependencies": ["fastapi", "sqlalchemy", "pydantic"],
        "securityNotes": ["Input validation present", "Authentication required"]
      }
    }
  ]
}
```

### Performance Specifications

| Metric | Core Edition | Premium Edition |
|--------|-------------|-----------------|
| **Analysis Speed** | < 30 seconds | < 5 minutes |
| **Knowledge Graph Size** | < 100KB | < 250KB |
| **Memory Usage** | < 256MB | < 512MB |
| **Concurrent Users** | 1 (local) | Unlimited |
| **Storage** | Local Qdrant | Cloud UltraRepo |

## 🏗️ Technical Architecture

### Core Components

#### 1. File Analysis Engine
- **Multi-threaded scanning** with intelligent queuing
- **Language detection** and parser selection
- **Binary file exclusion** and size limits
- **Incremental analysis** with change detection

#### 2. Knowledge Graph Generator
- **JSON-LD schema creation** with semantic markup
- **Relationship mapping** between files and modules
- **Metadata enrichment** with AI-generated descriptions
- **Size optimization** through selective inclusion

#### 3. Vector Database Integration
- **Qdrant client** with connection pooling
- **Collection management** with automatic naming
- **Embedding storage** with metadata payloads
- **Search optimization** with filtered queries

#### 4. AI Enhancement Layer (Premium)
- **LLM integration** with multiple provider support
- **Prompt engineering** for consistent analysis
- **Response parsing** and validation
- **Quality assurance** with confidence scoring

### Data Flow Architecture

```
Raw Codebase → File Scanner → Metadata Extractor → Knowledge Graph → Vector DB → Search API
     ↓              ↓              ↓                    ↓              ↓            ↓
  .gitignore    Language        AI Descriptions      JSON-LD       Embeddings   AI Agents
  .repoignore   Detection       Code Summaries       Validation    Indexing     Queries
```

## 🔗 Dependency Graph Feature

Repository Schema Generator now includes advanced dependency graph generation capabilities that create visual representations of code relationships and dependencies.

### What is a Dependency Graph?
A dependency graph shows how different files in your codebase are connected through imports, requires, and other dependency relationships. It helps you understand:

- **Import Relationships**: Which files depend on which other files
- **Circular Dependencies**: Detect potential architectural issues
- **Code Organization**: Visualize the structure of your codebase
- **Impact Analysis**: Understand what files will be affected by changes

### Dependency Graph Output
The dependency graph is saved as `dependency-graph.json` alongside the regular schema files:

```json
{
  "nodes": [
    {
      "file_path": "src/main.py",
      "file_type": ".py",
      "imports": ["os", "utils.helper"],
      "exports": ["function:main"],
      "metadata": {...}
    }
  ],
  "edges": [
    {
      "source_file": "src/main.py",
      "target_file": "src/utils.py",
      "dependency_type": "import",
      "imported_items": ["helper"]
    }
  ],
  "metadata": {
    "total_nodes": 5,
    "total_edges": 8,
    "cycles_detected": 0,
    "generated_at": "2025-01-15T10:30:00"
  }
}
```

### Supported Languages
The dependency analyzer supports multiple programming languages:
- **Python**: `import`, `from ... import` statements
- **JavaScript/TypeScript**: `import`, `require()` statements
- **Java**: `import` statements
- **C#**: `using` statements
- **C/C++**: `#include` directives
- **PHP**: `use`, `require`, `include` statements
- **Go**: `import` statements
- **Rust**: `use` statements

## 🚀 How to Run Repo-Schema within KiloCode/UltraRepo

### Prerequisites

- **Python 3.8+** with virtual environment support
- **Git** for repository access and ignore patterns
- **VS Code** with KiloCode extension installed

### Core Edition Setup (Local)

#### 1. Environment Setup
```bash
# Navigate to the reposchema directory
cd rebrand/reposchema

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Qdrant Setup (Local)
```bash
# Using Docker
docker run -p 6333:6333 qdrant/qdrant

# Or using Docker Compose
docker-compose up qdrant
```

#### 3. Configuration
Create `.env` file:
```env
# Qdrant Configuration
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=  # Optional for local

# Application Settings
LOG_LEVEL=INFO
DEBUG=false
```

#### 4. Basic Usage
```bash
# Analyze current directory
python repo-schema.py

# Analyze specific project
python repo-schema.py --base-dir /path/to/project --project-name myproject

# Custom output location
python repo-schema.py --output-dir ./custom-output
```

#### 5. VS Code Integration
1. Open VS Code with KiloCode extension
2. Go to Settings → Codebase Index
3. Configure Qdrant connection (localhost:6333)
4. Set project name and repository attributes
5. Click "Reindex Now" to generate knowledge graph

### Premium Edition Setup (UltraRepo Service)

#### 1. Account Setup
```bash
# Sign up at UltraRepo.ai
# Get API credentials
ULTRAREPO_API_KEY=your_api_key_here
ULTRAREPO_PROJECT_ID=your_project_id
```

#### 2. Configuration
```env
# UltraRepo Service Configuration
ULTRAREPO_API_URL=https://api.ultrarepo.ai/v1
ULTRAREPO_API_KEY=your_api_key_here
ULTRAREPO_PROJECT_ID=your_project_id

# Enhanced Features
AI_ANALYSIS_ENABLED=true
SECURITY_SCANNING=true
PERFORMANCE_ANALYTICS=true
```

#### 3. Premium Usage
```bash
# Enhanced analysis with AI
python repo-schema.py --edition premium --ai-enhancement

# Security-focused analysis
python repo-schema.py --security-scan --vulnerability-check

# Performance analytics
python repo-schema.py --performance-metrics --complexity-analysis
```

#### 4. VS Code Premium Integration
1. Install UltraRepo VS Code extension
2. Authenticate with UltraRepo account
3. Configure project settings with enhanced options
4. Enable AI analysis and security scanning
5. Access advanced analytics dashboard

## 📊 Feature Comparison

| Feature | Core Edition | Premium Edition |
|---------|-------------|-----------------|
| **File Analysis** | ✅ Basic | ✅ Enhanced + AI |
| **Knowledge Graph** | ✅ < 100KB | ✅ < 250KB |
| **Search Capabilities** | ✅ Basic | ✅ Semantic + AI |
| **Security Analysis** | ❌ | ✅ Vulnerability Scan |
| **Performance Metrics** | ❌ | ✅ Complexity Analysis |
| **API Discovery** | ❌ | ✅ Automatic Detection |
| **Cloud Storage** | ❌ | ✅ UltraRepo Cloud |
| **Team Collaboration** | ❌ | ✅ Shared Analytics |
| **Priority Support** | ❌ | ✅ 24/7 Support |
| **Custom Integrations** | ❌ | ✅ API Access |

## 🔧 Advanced Configuration

### Custom Ignore Patterns
```bash
# Create .repoignore for additional exclusions
echo "node_modules/" >> .repoignore
echo "*.log" >> .repoignore
echo "build/" >> .repoignore
```

### Environment Variables
```env
# Core Settings
REPO_SCHEMA_LOG_LEVEL=DEBUG
REPO_SCHEMA_MAX_FILE_SIZE=1048576  # 1MB
REPO_SCHEMA_TIMEOUT=300  # 5 minutes

# Premium Settings
ULTRAREPO_MODEL=gpt-4
ULTRAREPO_MAX_TOKENS=4000
ULTRAREPO_TEMPERATURE=0.3
```

### Docker Deployment (Core)
```yaml
# docker-compose.yml
version: '3.8'
services:
  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

  reposchema:
    build: .
    environment:
      - QDRANT_URL=http://qdrant:6333
    depends_on:
      - qdrant
```

## 🐛 Troubleshooting

### Common Issues

**VENV Not Found**
```bash
# Ensure virtual environment is activated
source venv/bin/activate
python repo-schema.py
```

**Qdrant Connection Failed**
```bash
# Check Qdrant status
curl http://localhost:6333/health

# Verify configuration
cat .env | grep QDRANT
```

**Large File Processing**
```bash
# Increase file size limit
export MAX_FILE_SIZE=5242880  # 5MB
python repo-schema.py
```

**AI Analysis Timeout (Premium)**
```bash
# Adjust timeout settings
export AI_TIMEOUT=600  # 10 minutes
python repo-schema.py --ai-enhancement
```

## 📈 Performance Optimization

### Core Edition Tips
- Use SSD storage for faster file scanning
- Limit analysis to specific directories when possible
- Schedule regular incremental updates
- Monitor memory usage with large codebases

### Premium Edition Tips
- Batch large codebases into smaller chunks
- Use parallel processing for multiple files
- Cache AI analysis results for unchanged files
- Monitor API usage and costs

## 🤝 Contributing

We welcome contributions to Repository Schema Generator!

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/yourusername/code.git
cd code/rebrand/reposchema

# Set up development environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

### Testing
```bash
# Run unit tests
python -m pytest tests/

# Run integration tests
python -m pytest tests/integration/

# Test with sample data
python repo-schema.py --test-mode --sample-data
```

## 📄 License

**Core Edition**: MIT License - Free for personal and commercial use
**Premium Edition**: UltraRepo Terms of Service - Subscription required

## 🆘 Support

### Documentation
- 📖 [User Guide](docs/user-guide.md)
- 🛠️ [API Reference](docs/api-reference.md)
- 🔧 [Configuration Guide](docs/configuration.md)

### Community Support
- 💬 [Discord Community](https://discord.gg/ultrarepo)
- 📧 [Email Support](mailto:support@ultrarepo.ai)
- 🐛 [Issue Tracker](https://github.com/UltraRepo/code/issues)

### Premium Support
- 🎯 Priority response times
- 📞 Direct technical support
- 🎓 Custom training sessions
- 🔧 White-label solutions

---

**Repository Schema Generator** - Making codebases intelligent and AI-ready.

**Ready to transform your codebase into an AI-powered knowledge graph?**

- **Core Edition**: Start with `python repo-schema.py`
- **Premium Edition**: Visit [UltraRepo.ai](https://ultrarepo.ai) to get started

## Project Structure

```
rebrand/reposchema/
├── README.md                 # This documentation
├── requirements.txt          # Python dependencies
├── repo-schema.py           # Main application script
├── utils/                   # Integration utilities
│   ├── qdrant_client.py     # Qdrant vector database client
│   ├── vscode_integration.py # VS Code extension communication
│   ├── error_handler.py     # Error handling utilities
│   └── venv_manager.py      # Virtual environment management
├── log/                     # Application logs
│   ├── reposchema.log       # Main application log
│   └── error.log            # Error-specific log
├── output/                  # Generated schemas and documentation
│   ├── schemas/             # JSON-LD schema files
│   └── docs/                # Markdown documentation
└── scripts/                 # Utility scripts
    ├── setup_venv.sh        # VENV setup script
    ├── run_schema_gen.sh    # Schema generation runner
    └── validate_setup.sh    # Environment validation
```

## Prerequisites

- **Python 3.8+** with virtual environment support
- **VS Code** with KiloCode extension (for full integration)
- **Qdrant vector database** (local or remote instance)
- **Git** (for .gitignore pattern support)

## Installation

### 1. Clone and Setup
```bash
cd rebrand/reposchema
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file in the project root:
```env
# Qdrant Configuration
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_api_key_here

# VS Code Integration
VSCODE_EXTENSION_PATH=/path/to/kilocode/extension

# Logging
LOG_LEVEL=INFO
LOG_FILE=log/reposchema.log
```

## Usage

### Command Line Interface

```bash
# Basic usage - scan current directory
python repo-schema.py

# Specify custom project directory
python repo-schema.py --base-dir /path/to/project

# Custom output directory
python repo-schema.py --output-dir /path/to/output

# Use custom ignore file
python repo-schema.py --ignore-file /path/to/.customignore

# Generate dependency graph (enabled by default)
python repo-schema.py --generate-dependency-graph

# Disable dependency graph generation
python repo-schema.py --no-dependency-graph
```

### VS Code Integration

The application is designed to be called from the KiloCode VS Code extension:

1. **Project Name Configuration**: Set project name in VS Code settings
2. **Repository Attributes**: Configure which metadata to include
3. **Collection Management**: Automatically creates/finds Qdrant collections
4. **Reindex Now**: Triggers schema generation with vector DB storage

## Configuration Options

### Repository Attributes
- `[Y] Create codebase knowledge graph`: Generate JSON-LD schema
- `[Y] Summary description of each repository file`: AI-generated descriptions
- `[Y] Summarize includes`: Extract import/dependency information
- `[N] Summarize libraries and binary files`: Skip binary analysis

### Qdrant Integration
- **Collection Naming**: `{project_name}_{hash}` format
- **Vector Storage**: Embeddings with metadata payloads
- **Knowledge Graph**: JSON-LD stored in payload metadata
- **Search Enhancement**: Structured data for improved queries

## Output Formats

### JSON Schema (`repo-schema.json`)
```json
{
  "project": "my-project",
  "version": "1.0",
  "taxonomy": [
    {
      "folder": "./",
      "files": [
        {
          "name": "main.py",
          "path": "src/main.py",
          "metadata": {
            "type": ".py",
            "ai_description": "Python source code file",
            "extracted_description": "Main application entry point",
            "modified": "2024-01-15T10:30:00Z"
          }
        }
      ],
      "subfolders": ["src", "tests"]
    }
  ],
  "files_scanned": 150,
  "files_processed": 120
}
```

### Markdown Documentation (`repo-schema.md`)
Generates human-readable documentation with:
- Project structure tree
- File metadata tables
- Dependency summaries
- Navigation aids

### Dependency Graph (`dependency-graph.json`)
Contains structured dependency relationship data:
- **Nodes**: File information with imports/exports
- **Edges**: Dependency relationships between files
- **Metadata**: Graph statistics and generation info
- **Size-optimized**: Automatically truncated if > 250KB

## Integration Architecture

### VS Code Extension Flow
1. **User Configuration**: Set project name and attributes in webview
2. **Collection Discovery**: Search for existing Qdrant collections
3. **VENV Validation**: Ensure Python environment is ready
4. **Schema Generation**: Run Python app with Qdrant integration
5. **Vector Storage**: Store knowledge graph in project collection
6. **Progress Feedback**: Update UI with generation status

### Qdrant Storage Structure
```
Collection: "myproject_a1b2c3d4"
├── Points (Files):
│   ├── ID: "file_hash_1"
│   ├── Vector: [0.1, 0.2, 0.3, ...]
│   └── Payload: {
│       "filePath": "src/main.py",
│       "knowledgeGraph": {
│         "@context": {...},
│         "@type": "CodeFile",
│         "dependencies": ["requests", "json"],
│         "functions": ["main", "process_data"]
│       }
│     }
```

## Error Handling

### VENV Issues
- **Detection**: Automatic VENV validation before execution
- **Recovery**: Clear error messages with setup instructions
- **Fallback**: Option to use system Python (with warnings)

### Qdrant Connection
- **Retry Logic**: Automatic reconnection with exponential backoff
- **Offline Mode**: Cache schemas locally when DB unavailable
- **Sync**: Automatic upload when connection restored

### File Processing
- **Binary Files**: Automatic detection and exclusion
- **Large Files**: Size limits to prevent memory issues
- **Encoding Issues**: UTF-8 fallback with error logging

## Development

### Adding New Features
1. **Utils**: Add utility functions to `utils/` directory
2. **Logging**: Use structured logging with appropriate levels
3. **Error Handling**: Implement try/catch with user-friendly messages
4. **Testing**: Add unit tests for new functionality

### Code Style
- Follow PEP 8 Python style guidelines
- Use type hints for function parameters
- Add docstrings for all public functions
- Log important operations and errors

## Troubleshooting

### Common Issues

**VENV Not Detected**
```bash
# Ensure you're in the correct directory
cd rebrand/reposchema
source venv/bin/activate
python repo-schema.py
```

**Qdrant Connection Failed**
```bash
# Check Qdrant is running
curl http://localhost:6333/health

# Verify API key if using authentication
export QDRANT_API_KEY=your_key_here
```

**Permission Errors**
```bash
# Ensure write permissions for output directory
chmod 755 output/
chmod 644 output/*.json output/*.md
```

### Debug Mode
Enable detailed logging:
```bash
export DEBUG=true
python repo-schema.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is part of the KiloCode VS Code extension ecosystem.

## Support

For issues and questions:
1. Check the logs in `log/` directory
2. Review VS Code extension logs
3. Create an issue with debug information
4. Include your `repo-schema.json` for analysis