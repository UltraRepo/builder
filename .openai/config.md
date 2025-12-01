<!--
  UltraRepo: Copilot instructions
  Purpose: short, targeted guidance so AI coding agents understand the repo layout,
  workflows, and constraints before making code changes.
-->

# UltraRepo AI Repository- Instructions

Follow these concise rules when analyzing or modifying this repository. They prioritize correctness, local workflow conventions, and safety (do not modify upstream sources).

- Big picture: this repo is a rebrand/assembly around a third‑party extension (KiloCode), enhanced with UltraRepo-specific features for AI-assisted code intelligence, discovery and accuracy and code generation. The repo structure utilizes upstream submodules, rebranded assets, modified code as needed for UltraRepo, and a build process to create the final packaged extension:
  - `.ultrarepo/upstream/*` (reference) — original source git submodules referencing paths in the upstream repo. Use it for read-only inspection only. DO NOT EDIT.  If you need to propose changes to upstream, do so in the `rebrand/` folder, as code in the rebrand folder is applied to the `build/` folder during the build process by running the rebrand/script/build script at `rebrand/scripts/build-ultrarepo-complete.sh` 
  - `build/` — working build folder where changes are applied, compiled, and packaged. `build/` contains a full copy of the upstream code, plus any modifications applied during the build process. This is the folder that is actually built and packaged as the VS Code extension.
  - `rebrand/` — assets, code, and configuration used to transform `upstream` into an UltraRepo build. For consistency, files and folders under `rebrand/` are organized in a way that mostly mirrors the `build/` (and `upstream`) structures, with the exception of repo-specific modifications. Rebrand changes are applied to `build/` during the build process by the build script at `rebrand/scripts/build-ultrarepo-complete.sh`
- `rebrand/scripts/*` — directory containing all UltraRepo-specific scripts and modifications, including rebranded assets and configuration files.

- Developer workflows (explicit)
  - Use pnpm + turbo for workspace tasks. Typical commands:
    - Install: `pnpm install`
    - Run package tasks: `pnpm dlx turbo run --filter <package>` or `pnpm --filter <package> <script>`
    - Build the branded extension (automated): `bash rebrand/scripts/build-ultrarepo-complete.sh`
  - Test: `pnpm turbo run test --filter <project_name>` or from package root `pnpm test`.

- Safety rules (must follow)
  - NEVER modify files under `upstream/` (or `.ultrarepo/upstream` if present). Those are reference copies or submodules.
  - Do not change `.gitmodules` location — leave it at repo root. If submodule paths moved locally, prefer creating runtime symlink or updating local config; do not move `.gitmodules`.
  - Respect `.gitignore` entries (this repo ignores `upstream/*` and `.ultrarepo/*`). Avoid proposing edits that re-track these files.

- Key integration and architecture notes (read these before code changes)
 - Key integration and architecture notes (read these before code changes)
  - Entry point / activation
    - Primary bootstrap: `rebrand/kilocode/src/extension.ts` (and the built copy at `build/kilocode/src/extension.ts`). `activate(context)` wires long‑running services and registers disposables on `context.subscriptions`.
    - Services to inspect: `CloudService`, `TelemetryService`, `ClineProvider` (sidebar), `McpServerManager`, `CodeIndexManager`.
    - Pattern: `CodeIndexManager` instances are created per workspace folder inside the activate() loop and initialized asynchronously (avoid blocking activate()). When adding services follow the same lifecycle: instantiate, call initialize, push to `context.subscriptions`.
  - Telemetry (how to opt-out)
    - Telemetry clients are registered conditionally in `extension.ts` (PostHog via `PostHogTelemetryClient` and CloudService telemetry clients). By default UltraRepo registers PostHog unless disabled.
    - Quick opt-outs (recommended order):
      1. Follow `/disable_kilo_telemetry.md` in the repo — it documents options: VS Code telemetry off, hosts-file/DNS block for PostHog, extension setting toggle (if exposed), or code-level opt-out via env var `KILO_DISABLE_TELEMETRY=1` / `POSTHOG_DISABLED=1` that calls `client.disable()`.
      2. For local builds, prefer the environment toggle (set `KILO_DISABLE_TELEMETRY=1` before launching VS Code) or edit `PostHogTelemetryClient` per the doc.
    - Code note: Telemetry registration points to check: the `telemetryService.register(new PostHogTelemetryClient())` call near the top of `extension.ts` and places where `cloudService.telemetryClient` would be registered.
  - Home webview & inline Home panel
    - Inline Home is implemented in `rebrand/kilocode/src/extension.ts` as the `UltraHomePanel` class. It creates a `vscode.WebviewPanel` (id `ultrarepoHomePanel`) with `enableScripts: true` and `retainContextWhenHidden: true`.
    - Creation: `UltraHomePanel.createOrShow(context.extensionUri)` is invoked on activation and also registered as the command `ultrarepo.__openHomeInline`.
    - Messaging: the Home webview uses `acquireVsCodeApi()` in the client and posts messages back with `{type, ...}`; the panel listens via `webview.onDidReceiveMessage` and routes actions (commands, open links, launch graph viewer) by calling `vscode.commands.executeCommand` or `vscode.env.openExternal` on the extension side.
    - If you change the Home UI, update both the HTML template in `UltraHomePanel.getHtml()` and any command IDs it calls (e.g., `ultrarepo.showDependencyGraph`).
    - Editing the UltraRepo Home webview (practical steps)
      - Source files to edit:
        - Primary source: `rebrand/kilocode/src/extension.ts` (class `UltraHomePanel`).
        - Built copy: `build/kilocode/src/extension.ts` (generated; do not edit directly unless experimenting). Always change `rebrand/` and run the build.
      - What to change when updating the Home UI:
        - Update `UltraHomePanel.getHtml()` to modify the webview HTML/JS/CSS. The method returns the full HTML string used for the panel. Keep the `acquireVsCodeApi()` contract stable.
        - If the webview triggers extension commands, ensure the command ids (`ultrarepo.*`) are present in the commands map (see `activate/registerCommands.ts`) and in `build/kilocode/src/package.json` under `contributes.commands` using the localized title keys (e.g. `%command.showDependencyGraph.title%`).
        - If the webview uses `postMessage({type:'run-cmd', cmd:'<commandId>'})` or posts `{type:'launchGraphViewer'}`, update the `webview.onDidReceiveMessage` handler in `extension.ts` to map those messages to `vscode.commands.executeCommand()` calls.
      - Quick dev cycle:
        1. Edit `rebrand/kilocode/src/extension.ts` (or webview assets under `rebrand/kilocode/src/webview-ui`).
        2. Run the automated rebrand/build: `bash rebrand/scripts/build-ultrarepo-complete.sh` (this copies/merges `rebrand/` into `build/` and runs the bundle).
        3. Verify the VSIX in `build/kilocode/dist/` (see below) and install the VSIX for local testing.

    - VSIX output / build artifact location
      - The packaged VSIX is emitted into the build dist folder. Example output from the smoke build used here:
        - `build/kilocode/dist/ultrarepo-4.83.1.vsix` (also available at `build/kilocode/src/dist/ultrarepo-4.83.1.vsix` depending on build scripts). Use that path to install locally with `code --install-extension <path>`.

    - Modifying VS Code commands and localization (NLS)
      - Commands:
        - Add/modify command implementations in `rebrand/kilocode/src/activate/registerCommands.ts` (and the built copy in `build/kilocode/src/activate/registerCommands.ts` after running the build). The `registerCommands` helper registers commands centrally; follow the existing pattern to add new handlers.
        - After adding a new command id (for example `ultrarepo.showDependencyGraph`), add the metadata entry to `rebrand/kilocode/src/package.json` (preferred) or `build/kilocode/src/package.json` if you are directly experimenting. The command entry must include the `command` id and `title` field which should reference an NLS key: `"title": "%command.showDependencyGraph.title%"`.
      - Localization (NLS) and i18n:
        - Default localized strings live in `rebrand/kilocode/src/package.nls.json`. Update or add keys there, for example:
          - `"command.showDependencyGraph.title": "UltraRepo: Graph Viewer"`
        - The built copy is at `build/kilocode/src/package.nls.json` after the rebrand/build. The runtime code frequently uses the i18n helper `t('key')` from `../i18n` in TypeScript; webview HTML may reference localized keys via the package metadata when necessary.
        - If you add NLS keys, update `rebrand/kilocode/src/package.nls.json` and then run the build script so the keys propagate into `build/` and into any webview bundles.
      - i18n usage notes:
        - In code use the `t()` function (imported from `../i18n`) for runtime localized strings. For command titles and other package metadata use `%key%` references in `package.json` and define the keys in `package.nls.json`.
        - Keep message contracts stable between webview and extension; prefer sending small, typed payloads and validate in the `onDidReceiveMessage` handler.

    - Other useful tips
      - Always edit `rebrand/` first. `build/` is generated and will be overwritten by the build script.
      - Keep webview HTML/JS minimal and avoid embedding secrets or absolute filesystem paths. Use `webview.asWebviewUri()` where you need to reference extension resources.
      - When changing command ids or NLS keys, update any webview clients (HTML/JS) that call them and the `package.nls.json` keys in `rebrand/`.
  - Webviews and messaging
    - Sidebar/webview provider: `ClineProvider` supplies sidebar HTML and state; look for `postMessage` usage on the provider and `handleUri` registered via `vscode.window.registerUriHandler`.
    - Keep message contracts stable (types/payload shape). Validate messages in `onDidReceiveMessage` handlers.
  - Virtual documents for diffs
    - The extension registers a `TextDocumentContentProvider` for `DIFF_VIEW_URI_SCHEME` which decodes base64 query payloads into readonly document contents (see the anonymous provider in `extension.ts`). Use `vscode.workspace.registerTextDocumentContentProvider(scheme, provider)` to register.
    - Avoid including secrets in URIs/queries since they may be logged or leaked.
  - Commands: central registration
    - Commands are centrally wired via `activate/registerCommands.ts` (called from `extension.ts`). Add new commands there and implement handlers in `services/` or `core/`. Register disposables on activation and add command metadata to `build/kilocode/src/package.json` (not upstream files).

- Project-specific conventions
  - Rebranding flow: do not change upstream files; implement edits in `rebrand/` and use the build script to apply patches into `build/`.
  - Telemetry: Telemetry clients are registered conditionally; be careful when modifying registration (PostHog, CloudService). Look for `TelemetryService.register` usage.
  - First-install flow: the extension may auto-open sidebars/walkthroughs on first install (search `firstInstallCompleted`). Avoid unexpected UX changes.

- Examples of safe edits
  - To add a new command: add registration in `activate/registerCommands.ts`, add implementation under `services/` or `core/`, and update `package.json` in `build/kilocode/src` (do not edit upstream package.json directly).
  - To add a webview route: modify `ClineProvider` and the webview HTML bundle; prefer editing files under `build/kilocode/src/webview-ui` or `rebrand/webview-ui`.

- Testing and verification (must run before proposing changes)
  - Lint and type-check: `pnpm lint --filter <project>` and `pnpm -w -s turbo run build` where applicable.
  - Smoke build: run `bash rebrand/scripts/build-ultrarepo-complete.sh` locally to verify packaging and assets.
  - Run VS Code dev host if changing extension activation logic: `pnpm --filter build/kilocode run watch` or use the VS Code extension debug launch in the `build` project.

- AI Tools and Search Capabilities

  - **codebase_search Tool**: Semantic search tool for finding functionally relevant code across the entire codebase, even without exact keywords or file names. Useful for understanding feature implementations, discovering API usages, and finding code examples.

    **Usage Guidelines:**
    - Use for ANY exploration of code you haven't examined yet in the conversation
    - Must be used FIRST before other search tools when exploring new code areas
    - For project-specific queries: Reuse the user's exact wording/question format (e.g., search for 'user authentication flow' or 'dependency injection pattern')
    - Retrieving file information: Results include file paths and relevant code snippets; use returned file paths with read_file tool for detailed examination

    **Parameters:**
    - `query` (required): The search query in natural language. Reuse user's exact wording unless there's a clear reason not to.
    - `path` (optional): Limit search to specific subdirectory relative to workspace root. Leave empty for entire workspace.

    **Examples:**
    - Search entire codebase: `<codebase_search><query>user login and password hashing</query></codebase_search>`
    - Search specific directory: `<codebase_search><query>API endpoints</query><path>src/api</path></codebase_search>`

    **Best Practices:**
    - Always use semantic search first when exploring unfamiliar code
    - Use natural language queries that describe functionality rather than exact code terms
    - Follow up search results with read_file for detailed code examination
    - Limit scope with path parameter when searching large codebases

- Where to look for examples
  - Command wiring: `build/kilocode/src/activate/registerCommands.ts`
  - Extension activation & services: `build/kilocode/src/extension.ts`
  - Ghost AI provider: `build/kilocode/src/services/ghost/` (example of AI integration)
  - Rebrand scripts: `rebrand/scripts/` (show how changes are mass-applied)

- When in doubt
  - If an edit touches `upstream/`, stop and propose a patch in `rebrand/` instead.
  - Ask for a reproducible local test (build script + smoke run) before creating a PR.

If any of these instructions are unclear or incomplete, ask a concise question listing which file(s) you plan to change and I will provide exact local verification steps.
