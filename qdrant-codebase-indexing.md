# Qdrant Codebase Indexing Documentation

## Overview

This document provides comprehensive documentation for the Qdrant-based codebase indexing system used in AirVeo App Builder (formerly KiloCode). The system provides semantic code search capabilities by creating vector embeddings of code blocks and storing them in a Qdrant vector database.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Components](#core-components)
3. [Configuration](#configuration)
4. [Indexing Process](#indexing-process)
5. [Search Functionality](#search-functionality)
6. [Vector Database Integration](#vector-database-integration)
7. [Embedder Providers](#embedder-providers)
8. [File Processing Pipeline](#file-processing-pipeline)
9. [Cache Management](#cache-management)
10. [User Interface](#user-interface)
11. [API Reference](#api-reference)

---

## Architecture Overview

The codebase indexing system uses a **modular architecture** with the following key principles:

- **Singleton Pattern**: One `CodeIndexManager` instance per workspace
- **Service-Oriented**: Specialized services for configuration, state, search, and orchestration
- **Event-Driven**: Progress updates and state changes communicated via events
- **Async Processing**: Parallel file processing with concurrency limits
- **Cache-First**: Efficient re-indexing by tracking file hashes

### System Flow

```
User Enables Indexing
    ↓
CodeIndexManager.initialize()
    ↓
Load Configuration (Qdrant URL, API Key, Embedder Settings)
    ↓
Create Services (Embedder, VectorStore, Parser, Scanner)
    ↓
Start Indexing Process
    ↓
Scan Workspace → Parse Files → Generate Embeddings → Store in Qdrant
    ↓
Start File Watcher → Monitor Changes → Re-index Modified Files
    ↓
Ready for Search
```

---

## Core Components

### 1. CodeIndexManager (`manager.ts`)

**Purpose**: Central coordinator for all indexing operations

**Key Responsibilities**:
- Manages singleton instances per workspace
- Initializes and coordinates all services
- Handles start/stop of indexing and file watching
- Provides public API for search operations
- Manages error recovery

**Key Methods**:
```typescript
// Get singleton instance for a workspace
static getInstance(context: vscode.ExtensionContext, workspacePath?: string): CodeIndexManager

// Initialize with configuration
async initialize(contextProxy: ContextProxy): Promise<{ requiresRestart: boolean }>

// Start indexing process
async startIndexing(): Promise<void>

// Stop file watcher
stopWatcher(): void

// Search the index
async search(query: string, directoryPrefix?: string): Promise<VectorStoreSearchResult[]>

// Get current status
getCurrentStatus(): SystemStatus

// Dispose and cleanup
dispose(): void
```

### 2. CodeIndexConfigManager (`config-manager.ts`)

**Purpose**: Manages all configuration settings for codebase indexing

**Configuration Properties**:
- `codebaseIndexEnabled`: Feature on/off toggle
- `embedderProvider`: Selected embedding provider (OpenAI, Ollama, Gemini, etc.)
- `modelId`: Embedding model identifier
- `modelDimension`: Vector dimension size
- `qdrantUrl`: Qdrant server URL (default: `http://localhost:6333`)
- `qdrantApiKey`: API key for Qdrant authentication
- `qdrantCollection`: Custom collection name (optional)
- `searchMinScore`: Minimum similarity score for search results
- `searchMaxResults`: Maximum number of search results

**Key Methods**:
```typescript
async loadConfiguration(): Promise<{ requiresRestart: boolean }>
isFeatureEnabled: boolean
isFeatureConfigured: boolean
getCurrentConfig(): CodeIndexConfig
```

### 3. QdrantVectorStore (`vector-store/qdrant-client.ts`)

**Purpose**: Qdrant database client for vector operations

**Key Features**:
- Collection creation and management
- Vector upsert (insert/update) operations
- Similarity search with filtering
- Point deletion
- Dimension validation and migration
- Custom collection naming support

**Key Methods**:
```typescript
async initialize(): Promise<boolean>
async upsert(points: { id: string; vector: number[]; payload: Payload }[]): Promise<void>
async search(queryVector: number[], directoryPrefix?: string, minScore?: number, limit?: number): Promise<VectorStoreSearchResult[]>
async deletePoints(pointIds: string[]): Promise<void>
async healthCheck(): Promise<boolean>
```

**Collection Naming**:
- Default: `ws-{hash}` where hash is first 16 chars of SHA256(workspacePath)
- Custom: User-specified collection name from configuration

### 4. CodeIndexOrchestrator (`orchestrator.ts`)

**Purpose**: Orchestrates the complete indexing workflow

**Key Responsibilities**:
- Coordinates initial workspace scan
- Manages file watcher lifecycle
- Handles batch processing of file changes
- Reports progress and errors
- Manages state transitions

**Workflow**:
```typescript
startIndexing()
  → Initialize vector store (create collection if needed)
  → Clear cache if collection was recreated
  → Start workspace scan
  → Process files in batches
  → Start file watcher
  → Monitor for file changes
```

### 5. DirectoryScanner (`processors/scanner.ts`)

**Purpose**: Scans workspace directories and processes files

**Key Features**:
- Recursive directory traversal
- File filtering (extensions, .gitignore, .rooignore)
- Parallel file processing with concurrency limits
- Batch embedding generation
- Cache-based change detection
- Progress reporting

**Processing Constants**:
```typescript
PARSING_CONCURRENCY = 10          // Concurrent file parsing
BATCH_PROCESSING_CONCURRENCY = 3  // Concurrent batch processing
BATCH_SEGMENT_THRESHOLD = 100     // Blocks per batch
MAX_FILE_SIZE_BYTES = 1MB         // Skip files larger than 1MB
```

### 6. CodeParser (`processors/parser.ts`)

**Purpose**: Parses source files into semantic code blocks

**Supported Languages**: Via Tree-sitter
- JavaScript, TypeScript, Python, Java, C, C++, C#, Go, Rust, Ruby, PHP, Swift, Kotlin, and more
- Markdown (special handling for headers and sections)

**Parsing Strategy**:
- **Tree-sitter**: Primary method for structured code parsing
- **Fallback Chunking**: For unsupported or problematic files
- **Markdown**: Custom parser for semantic section extraction

**Code Block Structure**:
```typescript
interface CodeBlock {
  content: string        // The actual code or text
  filePath: string      // Absolute file path
  fileHash: string      // SHA256 hash of file content
  startLine: number     // Starting line in file
  endLine: number       // Ending line in file
  type: string          // Block type (function, class, section, etc.)
}
```

### 7. CodeIndexSearchService (`search-service.ts`)

**Purpose**: Provides semantic search capabilities

**Search Process**:
1. Validate feature is enabled and configured
2. Generate embedding for search query
3. Perform vector similarity search in Qdrant
4. Apply directory filtering (optional)
5. Return ranked results

**Search Parameters**:
- `query`: Natural language search query
- `directoryPrefix`: Optional path filter
- `minScore`: Minimum similarity threshold (default from config)
- `maxResults`: Maximum results (default from config)

---

## Configuration

### Setup Requirements

1. **Qdrant Server**: Running instance (local or remote)
2. **Embedding Provider**: API key for OpenAI, Ollama, or other provider
3. **VS Code Extension**: Codebase Indexing feature enabled

### Configuration Storage

**Global State** (VS Code extension context):
```json
{
  "codebaseIndexConfig": {
    "codebaseIndexEnabled": true,
    "codebaseIndexQdrantUrl": "http://localhost:6333",
    "codebaseIndexQdrantCollection": "",
    "codebaseIndexEmbedderProvider": "openai",
    "codebaseIndexEmbedderModelId": "text-embedding-3-small",
    "codebaseIndexEmbedderModelDimension": 1536,
    "codebaseIndexSearchMinScore": 0.4,
    "codebaseIndexSearchMaxResults": 50
  }
}
```

**Secrets** (VS Code SecretStorage):
- `codeIndexOpenAiKey`: OpenAI API key
- `codeIndexQdrantApiKey`: Qdrant API key
- `codebaseIndexOpenAiCompatibleApiKey`: OpenAI-compatible API key
- `codebaseIndexGeminiApiKey`: Google Gemini API key
- `codebaseIndexMistralApiKey`: Mistral API key

### Qdrant Connection

**URL Formats Supported**:
```
http://localhost:6333
https://api.qdrant.tech
https://qdrant.example.com:6333
http://192.168.1.100:6334
https://cloud.qdrant.io/my-cluster
```

**URL Parsing**:
- Automatically detects HTTP vs HTTPS
- Handles explicit ports or uses protocol defaults (80/443)
- Supports URL prefixes for reverse proxies
- Validates and normalizes all URL formats

---

## Indexing Process

### Initial Index Creation

**Phase 1: Initialization**
```
1. Load configuration from VS Code settings
2. Validate Qdrant connection
3. Initialize embedder with API keys
4. Create or verify Qdrant collection
5. Check vector dimensions match configuration
```

**Phase 2: Workspace Scanning**
```
1. List all files in workspace (respects .gitignore)
2. Filter by supported extensions
3. Apply .rooignore rules
4. Check file sizes (skip > 1MB)
5. Calculate file hashes
6. Compare with cache to detect changes
```

**Phase 3: File Processing**
```
For each new/changed file:
  1. Read file content
  2. Parse into code blocks using Tree-sitter
  3. Filter blocks by size (min/max chars)
  4. Accumulate blocks into batches (100 blocks per batch)
  5. Generate embeddings for batch
  6. Store in Qdrant with metadata
  7. Update cache with new file hash
  8. Report progress
```

**Phase 4: File Watching**
```
1. Start VS Code file watcher
2. Monitor for file create/change/delete events
3. Queue changed files for re-indexing
4. Process queue in batches
5. Keep index synchronized with workspace
```

### Incremental Updates

When files change:
1. **File Watcher** detects change
2. **Queue Management**: Add to batch queue
3. **Batch Processing**: Process when threshold reached or timer expires
4. **Delete Old Vectors**: Remove old embeddings for changed file
5. **Re-parse and Re-index**: Generate new embeddings
6. **Update Cache**: Store new file hash

### Cache Strategy

**File Hash Cache** (`cache-manager.ts`):
- Stores SHA256 hash for each indexed file
- Persisted to disk in workspace storage
- Enables efficient change detection
- Cleared when collection is recreated

**Cache Format**:
```json
{
  "/workspace/src/file1.ts": "abc123...",
  "/workspace/src/file2.ts": "def456...",
  ...
}
```

---

## Search Functionality

### Semantic Search

The search system uses **vector similarity** to find relevant code:

```typescript
// User query
const results = await codeIndexManager.search("authentication middleware");

// Behind the scenes:
// 1. Generate embedding for "authentication middleware"
// 2. Search Qdrant for similar vectors
// 3. Return code blocks ranked by similarity
```

### Search Results

**Result Structure**:
```typescript
interface VectorStoreSearchResult {
  id: string           // Unique point ID in Qdrant
  score: number       // Similarity score (0-1)
  payload: {
    filePath: string  // Absolute file path
    content: string   // Code block content
    startLine: number // Line number in file
    endLine: number   // End line in file
    type: string      // Block type
  }
}
```

### Filtering and Ranking

**Directory Filtering**:
```typescript
// Search only in specific directory
const results = await codeIndexManager.search(
  "user authentication",
  "/workspace/src/auth"
);
```

**Similarity Threshold**:
- Configurable minimum score (default: 0.4)
- Results below threshold are excluded
- Higher scores = better matches

**Result Limits**:
- Configurable max results (default: 50)
- Prevents overwhelming users with too many results

---

## Vector Database Integration

### Qdrant Schema

**Collection Configuration**:
```typescript
{
  vectors: {
    size: 1536,              // Dimension (model-dependent)
    distance: "Cosine"       // Similarity metric
  }
}
```

**Point Structure**:
```typescript
{
  id: "uuid-v5-based-on-file-and-block",
  vector: [0.123, -0.456, ...],  // 1536 dimensions
  payload: {
    filePath: "/absolute/path/to/file.ts",
    content: "function authenticate() { ... }",
    startLine: 42,
    endLine: 58,
    type: "function_declaration"
  }
}
```

### Collection Management

**Automatic Collection Creation**:
- Creates collection on first index
- Validates vector dimensions
- Recreates if dimensions change (model switch)

**Collection Naming Strategy**:
1. **Default**: Workspace-based hash
   - Format: `ws-{first-16-chars-of-sha256(workspace-path)}`
   - Example: `ws-a1b2c3d4e5f6g7h8`

2. **Custom**: User-specified name
   - Set via `qdrantCollection` configuration
   - Allows shared collections across workspaces
   - Useful for project-based organization

### Dimension Handling

**Automatic Migration**:
```typescript
// Detects dimension mismatch
const collectionInfo = await qdrantClient.getCollection(collectionName);
if (collectionInfo.config.params.vectors.size !== expectedDimension) {
  // Delete old collection
  await qdrantClient.deleteCollection(collectionName);
  // Create new collection with correct dimensions
  await qdrantClient.createCollection(collectionName, {
    vectors: { size: expectedDimension, distance: "Cosine" }
  });
}
```

---

## Embedder Providers

### Supported Providers

1. **OpenAI** (`embedders/openai.ts`)
   - Models: `text-embedding-3-small` (1536d), `text-embedding-3-large` (3072d)
   - Batching: Up to 8000 tokens per batch
   - Rate limiting: Automatic retry with exponential backoff

2. **Ollama** (`embedders/ollama.ts`)
   - Local embedding models
   - No API costs
   - Models: nomic-embed-text, mxbai-embed-large, etc.

3. **Google Gemini** (`embedders/gemini.ts`)
   - Models: text-embedding-004 (768d)
   - Requires Gemini API key

4. **OpenAI Compatible** (Custom endpoints)
   - Any API compatible with OpenAI format
   - Custom base URL support

5. **Mistral AI**
   - Mistral embedding models
   - Requires Mistral API key

### Embedding Generation

**Batch Processing**:
```typescript
// Accumulate blocks until batch threshold
const batchSize = 100;
const blocks: CodeBlock[] = [...];

// Generate embeddings in batch
const embeddings = await embedder.createEmbeddings(
  blocks.map(b => b.content),
  "text-embedding-3-small"
);

// Store in Qdrant
await vectorStore.upsert(
  embeddings.map((vector, i) => ({
    id: generateUUID(blocks[i]),
    vector: vector,
    payload: { ...blocks[i] }
  }))
);
```

**Error Handling**:
- Automatic retry for transient failures
- Exponential backoff (100ms → 200ms → 400ms)
- Max 3 retries per batch
- Detailed error telemetry

---

## File Processing Pipeline

### Supported File Extensions

**Programming Languages**:
```typescript
const scannerExtensions = [
  '.js', '.jsx', '.ts', '.tsx',      // JavaScript/TypeScript
  '.py',                              // Python
  '.java', '.kt', '.kts',            // Java/Kotlin
  '.c', '.cpp', '.h', '.hpp',        // C/C++
  '.cs',                              // C#
  '.go',                              // Go
  '.rs',                              // Rust
  '.rb',                              // Ruby
  '.php',                             // PHP
  '.swift',                           // Swift
  '.md', '.markdown',                 // Markdown
  // ... and more
];
```

### Parsing Strategies

**1. Tree-sitter Parsing** (Primary)
- Structural code understanding
- Extracts semantic blocks (functions, classes, methods)
- Preserves context and hierarchy

**2. Fallback Chunking**
- For unsupported languages or parsing errors
- Fixed-size chunks with overlap
- Maintains code continuity

**3. Markdown Parsing** (Special)
- Header-based section extraction
- Semantic document structure
- Code blocks and text sections

### Code Block Sizing

**Constraints**:
```typescript
MIN_BLOCK_CHARS = 50          // Skip very small blocks
MAX_BLOCK_CHARS = 8000        // Split large blocks
MIN_CHUNK_REMAINDER = 200     // Minimum chunk after split
MAX_TOLERANCE_FACTOR = 1.2    // Allow 20% over limit
```

**Splitting Strategy**:
```
If block > MAX_BLOCK_CHARS:
  1. Try to split at natural boundaries (newlines)
  2. Ensure chunks >= MIN_CHUNK_REMAINDER
  3. Allow up to 20% over limit to avoid tiny remainders
  4. Create multiple code blocks from single parse node
```

---

## Cache Management

### CacheManager (`cache-manager.ts`)

**Purpose**: Tracks file hashes to enable incremental indexing

**Storage Location**:
```
<workspace>/.vscode/code-index-cache.json
```

**Cache Operations**:
```typescript
// Initialize (load from disk)
await cacheManager.initialize();

// Get cached hash
const hash = cacheManager.getHash('/path/to/file.ts');

// Set hash
cacheManager.setHash('/path/to/file.ts', 'abc123...');

// Remove file from cache
cacheManager.removeHash('/path/to/file.ts');

// Clear all cache
await cacheManager.clearCacheFile();

// Save to disk
await cacheManager.saveCacheToDisk();
```

**Auto-Save**:
- Saves after each batch of updates
- Ensures cache persistence across restarts

---

## User Interface

### Settings UI (`webview-ui/src/components/settings/ApiOptions.tsx`)

**Codebase Indexing Section**:

1. **Enable Codebase Indexing** (Checkbox)
   - Toggle feature on/off
   - Shows/hides configuration fields

2. **Embedder Provider** (Dropdown)
   - OpenAI
   - Ollama
   - Google Gemini
   - OpenAI Compatible
   - Mistral AI

3. **Model Selection** (Dropdown)
   - Provider-specific models
   - Auto-updates dimension

4. **Qdrant URL** (Text Input)
   - Default: `http://localhost:6333`
   - Supports HTTP/HTTPS

5. **Qdrant API Key** (Password Input)
   - Optional for local instances
   - Required for cloud Qdrant

6. **Collection Name** (Text Input)
   - Optional custom collection name
   - Auto-generates if empty

7. **Get Collections** (Button)
   - Lists existing collections
   - Helps with collection discovery

**Status Indicator**:
```
● Indexed - File watcher started.
● Indexing - Processing files...
● Error - Configuration invalid
○ Standby - Feature disabled
```

### Localization

**Supported Languages**:
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Japanese (ja)
- Chinese (zh-CN, zh-TW)
- And many more...

**Translation Files**:
```
webview-ui/src/i18n/locales/{lang}/settings.json
```

---

## API Reference

### CodeIndexManager Public API

```typescript
class CodeIndexManager {
  // Singleton instance
  static getInstance(
    context: vscode.ExtensionContext, 
    workspacePath?: string
  ): CodeIndexManager | undefined
  
  // Initialize with configuration
  async initialize(contextProxy: ContextProxy): Promise<{ requiresRestart: boolean }>
  
  // Start indexing process
  async startIndexing(): Promise<void>
  
  // Stop file watcher
  stopWatcher(): void
  
  // Search the index
  async search(
    query: string, 
    directoryPrefix?: string
  ): Promise<VectorStoreSearchResult[]>
  
  // Get current status
  getCurrentStatus(): {
    systemStatus: IndexingState
    statusMessage: string
    progress: ProgressInfo
  }
  
  // Event listeners
  onProgressUpdate: Event<ProgressUpdate>
  
  // State getters
  get state(): IndexingState
  get isFeatureEnabled(): boolean
  get isFeatureConfigured(): boolean
  get isInitialized(): boolean
  
  // Cleanup
  dispose(): void
}
```

### Search Usage Example

```typescript
const manager = CodeIndexManager.getInstance(context, workspacePath);

// Initialize
await manager.initialize(contextProxy);

// Start indexing
await manager.startIndexing();

// Wait for indexing to complete
manager.onProgressUpdate((update) => {
  if (update.state === 'Indexed') {
    console.log('Indexing complete!');
  }
});

// Search
const results = await manager.search('user authentication');

results.forEach(result => {
  console.log(`Score: ${result.score}`);
  console.log(`File: ${result.payload.filePath}`);
  console.log(`Lines: ${result.payload.startLine}-${result.payload.endLine}`);
  console.log(`Code: ${result.payload.content}`);
});
```

---

## Performance Characteristics

### Concurrency Limits

```typescript
PARSING_CONCURRENCY = 10          // Files parsed in parallel
BATCH_PROCESSING_CONCURRENCY = 3  // Embedding batches processed in parallel
MAX_PENDING_BATCHES = 5           // Queue limit
```

### Batch Sizes

```typescript
BATCH_SEGMENT_THRESHOLD = 100     // Code blocks per embedding batch
MAX_BATCH_TOKENS = 8000          // OpenAI token limit per batch
```

### Retry Configuration

```typescript
MAX_BATCH_RETRIES = 3            // Retry attempts for failed batches
INITIAL_RETRY_DELAY_MS = 100     // Initial retry delay
// Exponential backoff: 100ms → 200ms → 400ms
```

### File Limits

```typescript
MAX_FILE_SIZE_BYTES = 1048576    // 1MB file size limit
MAX_LIST_FILES_LIMIT = 10000     // Max files to scan
```

---

## Error Handling

### Error Recovery

**Automatic Recovery**:
```typescript
// If indexing fails, attempt recovery
if (currentState === 'Error') {
  await manager.recoverFromError();
  // Re-initializes services
  // Clears error state
  // Ready to retry
}
```

### Error Telemetry

All errors are captured for diagnostics:
```typescript
TelemetryService.instance.captureEvent(
  TelemetryEventName.CODE_INDEX_ERROR,
  {
    error: errorMessage,
    stack: errorStack,
    location: 'functionName'
  }
);
```

### Common Error Scenarios

1. **Qdrant Connection Failure**
   - Check Qdrant server is running
   - Verify URL and port
   - Check network connectivity

2. **API Key Invalid**
   - Verify embedder API key
   - Check key permissions
   - Ensure sufficient quota

3. **Dimension Mismatch**
   - System auto-recreates collection
   - Cache is cleared
   - Re-indexing triggered

4. **Out of Memory**
   - Reduce concurrency limits
   - Increase batch processing delay
   - Filter large files

---

## Best Practices

### Configuration

1. **Use Local Qdrant for Development**
   ```bash
   docker run -p 6333:6333 qdrant/qdrant
   ```

2. **Choose Appropriate Model**
   - Small projects: `text-embedding-3-small` (1536d)
   - Large projects: Consider local Ollama models
   - Cost-sensitive: Ollama (free, local)

3. **Set Reasonable Limits**
   - `searchMinScore`: 0.4-0.6 for precision
   - `searchMaxResults`: 20-50 for usability

### Performance

1. **Enable .rooignore**
   - Exclude `node_modules`, `dist`, etc.
   - Reduces indexing time significantly

2. **Monitor Progress**
   - Use status indicator
   - Watch for error states
   - Check telemetry logs

3. **Incremental Updates**
   - File watcher keeps index current
   - Only changed files re-indexed
   - Cache ensures efficiency

---

## Troubleshooting

### Issue: "Qdrant connection failed"
**Solution**: 
- Check Qdrant is running: `curl http://localhost:6333/health`
- Verify URL in settings
- Check firewall rules

### Issue: "No results found"
**Solution**:
- Verify indexing completed (status = "Indexed")
- Check search query is meaningful
- Lower `searchMinScore` threshold
- Increase `searchMaxResults`

### Issue: "Indexing stuck at X%"
**Solution**:
- Check logs for errors
- Verify API key is valid
- Check rate limits
- Restart indexing

### Issue: "Collection dimension mismatch"
**Solution**:
- System auto-fixes on next index
- Or manually delete collection in Qdrant
- Re-index will create correct collection

---

## Future Enhancements

### Planned Features

1. **Collection Management UI**
   - List all collections
   - Switch between collections
   - Delete/rename collections

2. **Enhanced Metadata**
   - File modification dates
   - Author information
   - Dependency tracking
   - Symbol references

3. **JSON-LD Knowledge Graphs**
   - Export index schema
   - Cross-project discovery
   - AI-readable metadata

4. **Advanced Filtering**
   - File type filters
   - Date range filters
   - Author filters
   - Tag-based organization

5. **Performance Optimizations**
   - Streaming embeddings
   - Progressive indexing
   - Smart batch sizing
   - Adaptive concurrency

---

## Conclusion

The Qdrant-based codebase indexing system provides powerful semantic search capabilities for code understanding and navigation. By combining vector embeddings with efficient caching and incremental updates, it enables fast, accurate code discovery across large codebases.

For questions or issues, consult the project documentation or open an issue on GitHub.

---

**Document Version**: 1.0  
**Last Updated**: November 26, 2025  
**Author**: AI Documentation Generator
