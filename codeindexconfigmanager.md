# Unified Codebase Indexing Strategy: Qdrant & NeoCoder

This document outlines the architectural plan to extend the "Codebase Indexing" feature to support both the local Qdrant vector store and the MCP-based NeoCoder indexer (Neo4j) seamlessly.

## 1. Unified Vision

The goal is to provide a single "Codebase Indexing" experience for the user, where enabling indexing activates both systems if configured.

- **Unified Settings**: A single configuration section in the UI for all indexing settings.
- **Unified Control**: The "Start Indexing" button triggers indexing for both Qdrant and NeoCoder.
- **Unified Updates**: The file watcher propagates changes to both indexers simultaneously.

## 2. Configuration Management (`CodeIndexConfigManager`)

We will extend the existing configuration system to include NeoCoder-specific settings.

### Data Structure Updates
The `CodeIndexConfig` interface will be updated to include:
- `neoCoderUrl`: The URL of the NeoCoder MCP server (if applicable, or connection details).
- `neoCoderApiKey`: The API key for NeoCoder (stored securely via `SecretStorage`).
- `enableNeoCoder`: A boolean flag to toggle this specific indexer.

### UI Updates (`ApiOptions.tsx` / `CodeIndexPopover.tsx`)
The settings UI will be expanded to include a "NeoCoder Configuration" section:
- **NeoCoder URL**: Input field.
- **NeoCoder API Key**: Password input field.
- **Status Indicator**: Shows connection status to the NeoCoder MCP server.

## 3. Orchestration (`CodeIndexOrchestrator`)

The `CodeIndexOrchestrator` is the central hub that currently coordinates the `DirectoryScanner` and the `VectorStore`. It will be refactored to manage multiple indexers.

### Architecture Change
Instead of tightly coupling with `VectorStore`, the orchestrator will manage a list of `Indexer` adapters.

```typescript
interface Indexer {
  initialize(): Promise<void>;
  indexFile(path: string, content: string): Promise<void>;
  deleteFile(path: string): Promise<void>;
  syncCodebase(files: FileInfo[]): Promise<void>;
}
```

### Workflow
1.  **Start Indexing**:
    - The Orchestrator scans the codebase using `DirectoryScanner`.
    - It calls `syncCodebase()` on the `QdrantIndexer`.
    - It calls `syncCodebase()` on the `NeoCoderIndexer` (MCP adapter).

2.  **File Watcher**:
    - When a file changes, the Orchestrator receives the event.
    - It calls `indexFile()` on both indexers.
    - When a file is deleted, it calls `deleteFile()` on both.

## 4. NeoCoder Integration (MCP Adapter)

Since NeoCoder is an MCP server, we cannot call library functions directly. We will create a `NeoCoderService` (or `NeoCoderIndexer`) that acts as an adapter.

### Assumptions on NeoCoder MCP Tools
We assume the NeoCoder MCP server exposes tools similar to:
- `ingest_file(path, content)`: To index a single file.
- `remove_file(path)`: To remove a file from the graph.
- `sync_project(path)`: To trigger a full scan (optional, if supported).

### Implementation Details
- The `NeoCoderService` will use the extension's `McpHub` or `McpClient` to communicate with the NeoCoder server.
- It will translate the Orchestrator's standard calls into specific MCP tool executions.

## 5. Implementation Plan

1.  **Settings**: Update `CodeIndexConfigManager` and UI to store/retrieve NeoCoder credentials.
2.  **Adapter**: Create `NeoCoderService` implementing a standard Indexer interface.
3.  **Orchestrator**: Refactor `CodeIndexOrchestrator` to broadcast events to all registered indexers.
4.  **Testing**: Verify that clicking "Start Indexing" results in data being present in both Qdrant and NeoCoder.