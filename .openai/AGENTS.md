# AGENTS.md file for AI Agents

## Dev environment rules
- NEVER modify code in the folder /upstream. Upstream folder is for reference only.  

## Hidden Folders and Files
- The following folders are HIDDEN to AI agents and should NOT be searched:

`.env`
`.gitignore`
`.ultrarepo/*`
`.ultrarepo/upstream/*`

## Dev environment tips
- Use `pnpm dlx turbo run where <project_name>` to jump to a package instead of scanning with `ls`.
- Run `pnpm install --filter <project_name>` to add the package to your workspace so Vite, ESLint, and TypeScript can see it.
- Use `pnpm create vite@latest <project_name> -- --template react-ts` to spin up a new React + Vite package with TypeScript checks ready.
- Check the name field inside each package's package.json to confirm the right name—skip the top-level one.
## UltraRepo Context Indexing, Codebase Search and Context Search 
This project provides a context indexing database with search tools for use by AI agents.  The information below explains how 'codebase_search' works

### codebase_search
The codebase_search tool is that requires additional setup including an embedding provider and vector database.

### How codebase_search works
The codebase_search tool performs semantic searches across your entire codebase using AI embeddings. Unlike traditional text-based search, it understands the meaning of your queries and finds relevant code even when exact keywords don't match. 

### Vector Database for Context Indexing and codebase_search
A vector database is used to index data for codebase search.  The vector database contains project specific data that can be searched.

### Codebase_Search Parameters
The Codebase_Search tool accepts these parameters:

**query** (required): Natural language search query describing what you're looking for

**path** (optional): Directory path to limit search scope to a specific part of your codebase

#### **What Codebase_Search Does**
The <codebase_search> tool is callable by AI agents as a tool or manually by users via the chat window.  The <codebase_search> tool searches through your indexed codebase using semantic similarity rather than exact text matching. It finds code blocks that are conceptually related to your query, even if they don't contain the exact words you searched for. Results include relevant code snippets with file paths, line numbers, and similarity scores.  Examples of the <codebase_search> tool command are below. 

#### When is <codebase_search> tool used?
When Kilo Code / UltraRepo needs to find code related to specific functionality across your project
- When looking for implementation patterns or similar code structures
- When searching for error handling, authentication, or other conceptual code patterns
- When exploring unfamiliar codebases to understand how features are implemented
- When finding related code that might be affected by changes or refactoring

#### Key Features - <codebase_search> tool 
- Semantic Understanding: Finds code by meaning rather than exact keyword matches
- Cross-Project Search: Searches across your entire indexed codebase, not just open files
- Contextual Results: Returns code snippets with file paths and line numbers for easy navigation
- Similarity Scoring: Results ranked by relevance with similarity scores (0-1 scale)
- Scope Filtering: Optional path parameter to limit searches to specific directories
- Intelligent Ranking: Results sorted by semantic relevance to your query
- UI Integration: Results displayed with syntax highlighting and navigation links
- Performance Optimized: Fast vector-based search with configurable result limits

#### Requirements to Use <codebase_search> tool 
This tool is only available when the Codebase Indexing feature is properly configured:

- Feature Enabled: Codebase Indexing must be enabled in experimental settings
- Embedding Provider: OpenAI API key or Ollama configuration required
- Vector Database: Qdrant instance running and accessible
Index Status: Codebase must be indexed (status: "Indexed" or "Indexing")

#### Limitations for <codebase_search> tool 
- Experimental Feature: Part of the experimental codebase indexing system
- Requires Configuration: Depends on external services (embedding provider + Qdrant)
- Index Dependency: Only searches through indexed code blocks
- Result Limits: Maximum of 50 results per search to maintain performance
- Similarity Threshold: Only returns results above 0.4 similarity score
- File Size Limits: Limited to files under 1MB that were successfully indexed
- Language Support: Effectiveness depends on Tree-sitter language support

#### Operation and codebase_search tool process
When the codebase_search tool is invoked, it follows this process:

##### **Availability Validation:**

- Verifies that the CodeIndexManager is available and initialized
- Confirms codebase indexing is enabled in settings
- Checks that indexing is properly configured (API keys, Qdrant URL)
- Validates the current index state allows searching

##### Query Processing:

- Takes your natural language query and generates an embedding vector
- Uses the same embedding provider configured for indexing (OpenAI or Ollama)
- Converts the semantic meaning of your query into a mathematical representation

##### Vector Search Execution:

- Searches the Qdrant vector database for similar code embeddings
- Uses cosine similarity to find the most relevant code blocks
- Applies the minimum similarity threshold (0.4) to filter results
- Limits results to 50 matches for optimal performance

**Path Filtering (if specified):**

- Filters results to only include files within the specified directory path
- Uses normalized path comparison for accurate filtering
- Maintains relevance ranking within the filtered scope

**Result Processing and Formatting:**

- Converts absolute file paths to workspace-relative paths
- Structures results with file paths, line ranges, similarity scores, and code content
- Formats for both AI consumption and UI display with syntax highlighting

**Dual Output Format:**

- AI Output: Structured text format with query, file paths, scores, and code chunks for AI Agent Use

- UI Output: JSON format with syntax highlighting and navigation capabilities for Human Use in UI

##### Search Query Best Practices - <codebase_search> Tool

**Effective Query Patterns** 

Good: Conceptual and specific

<codebase_search>
<query>user authentication and password validation</query>
</codebase_search>

Good: Feature-focused

<codebase_search>
<query>database connection pool setup</query>
</codebase_search>

Good: Problem-oriented

<codebase_search>
<query>error handling for API requests</query>
</codebase_search>

Less effective: Too generic

<codebase_search>
<query>function</query>
</codebase_search>

##### Query Types That Work Well - <codebase_search> Tool
Functional Descriptions: "file upload processing", "email validation logic"
Technical Patterns: "singleton pattern implementation", "factory method usage"
Domain Concepts: "user profile management", "payment processing workflow"
Architecture Components: "middleware configuration", "database migration scripts"
Directory Scoping
Use the optional path parameter to focus searches on specific parts of your codebase:

Search within API modules:

<codebase_search>
<query>endpoint validation middleware</query>
<path>src/api</path>
</codebase_search>

Search in test files:

<codebase_search>
<query>mock data setup patterns</query>
<path>tests</path>
</codebase_search>

Search specific feature directories:

<codebase_search>
<query>component state management</query>
<path>src/components/auth</path>
</codebase_search>

##### Result Interpretation - <codebase_search> Tool

**Similarity Scores** 
- 0.8-1.0: Highly relevant matches, likely exactly what you're looking for
- 0.6-0.8: Good matches with strong conceptual similarity
- 0.4-0.6: Potentially relevant but may require review
- Below 0.4: Filtered out as too dissimilar

**Result Structure**
Each search result includes:

- File Path: Workspace-relative path to the file containing the match
- Score: Similarity score indicating relevance (0.4-1.0)
- Line Range: Start and end line numbers for the code block
- Code Chunk: The actual code content that matched your query

##### <codebase_search> Tool Usage Scenarios
Below are some usage scenarios of how the <codebase_search> Tool can be used in Kilo Code / UltraRepo

- When implementing a new feature, Kilo Code / UltraRepo searches for "authentication middleware" to understand existing patterns before writing new code.

- When debugging an issue, Kilo Code searches for "error handling in API calls" to find related error patterns across the codebase.

- When refactoring code, Kilo Code searches for "database transaction patterns" to ensure consistency across all database operations.

- When onboarding to a new codebase, Kilo Code searches for "configuration loading" to understand how the application bootstraps.

##### <codebase_search> Tool Usage Examples

- Searching for authentication-related code across the entire project:

<codebase_search>
<query>user login and authentication logic</query>
</codebase_search>

- Finding database-related code in a specific directory:

<codebase_search>
<query>database connection and query execution</query>
<path>src/data</path>
</codebase_search>

- Looking for error handling patterns in API code:

<codebase_search>
<query>HTTP error responses and exception handling</query>
<path>src/api</path>
</codebase_search>

- Searching for testing utilities and mock setups:

<codebase_search>
<query>test setup and mock data creation</query>
<path>tests</path>
</codebase_search>

- Finding configuration and environment setup code:

<codebase_search>
<query>environment variables and application configuration</query>
</codebase_search>

## Testing instructions
- Find the CI plan in the .github/workflows folder.
- Run `pnpm turbo run test --filter <project_name>` to run every check defined for that package.
- From the package root you can just call `pnpm test`. The commit should pass all tests before you merge.
- To focus on one step, add the Vitest pattern: `pnpm vitest run -t "<test name>"`.
- Fix any test or type errors until the whole suite is green.
- After moving files or changing imports, run `pnpm lint --filter <project_name>` to be sure ESLint and TypeScript rules still pass.
- Add or update tests for the code you change, even if nobody asked.

## PR instructions
- Title format: [<project_name>] <Title>
- Always run `pnpm lint` and `pnpm test` before committing.