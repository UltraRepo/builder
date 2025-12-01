**AI Agent Prompt:**

You are an expert AI coding assistant tasked with updating a rebranded fork of the KiloCode extension (from https://github.com/Kilo-Org/kilocode) to the v4.124.0 release. The project is structured as follows:

- **Project Overview**: This is a rebrand/assembly of KiloCode, enhanced with AirVeo-specific features. The repo uses upstream submodules for reference, rebranded assets/code in `rebrand/`, and a build process to create the final AirVeo Builder extension.
- **Key Folders**:

  | Folder Name | Path | Purpose |
  |-------------|------|---------|
  | Upstream Reference | `.ultrarepo/upstream/*` and `upstream/*` | Read-only reference copies/submodules of the original KiloCode source code. Used for comparison and as the base for rebranding. Never edit these directly. |
  | Rebrand Source | `rebrand/` | Contains assets, code, and scripts to transform upstream KiloCode into AirVeo-branded versions. This is the source for all rebrand changes (e.g., rebranded from KiloCode → AirVeo). Changes here are applied to the build folder during the build process. |
  | Build Output | `build/kilocode/` | Working build folder where upstream code is copied, modified with rebrand changes, and packaged. This is where the final AirVeo Builder extension is built and the VSIX is generated. |
- **Rebrand Strategy**: Any visible UI elements in KiloCode (e.g., extension name, icons, webviews, command titles, localization strings) must be rebranded to AirVeo branding. This includes:
  - Extension ID: `AirVeo.builder`
  - Display Name: "AirVeo App Builder"
  - Publisher: "AirVeo"
  - Icons: AirVeo-themed versions (e.g., replacing KiloCode logos with AirVeo ones).
  - Commands: Prefixed with `builder.*` instead of `kilo.*` or `ultrarepo.*`.
  - Webviews and UI: Updated to reflect AirVeo branding (e.g., logos, text, themes).
  - Localization: Replace any "KiloCode" or "UltraRepo" references with "AirVeo" in NLS files.
- **Build Scripts**: Located in `rebrand/scripts/`. Key ones include `build-airveo-complete.sh` (main orchestrator), `patch-nls-builder.sh` (branding patches), `icon-rebrand-builder.sh` (icon replacements), `rebrand-webviews-builder.sh` (file copies), and `refactor-commands-builder.sh` (command updates). These must be retained and updated if needed to work with v4.124.0. Do not delete or replace them—only modify for compatibility.
- **Current State**: The upstream submodule is at v4.83.1. Syncing to v4.124.0 (~41 versions ahead) may introduce new features, dependencies, or structural changes that could break the rebrand process.
- **Constraints**:
  - Never edit files in `upstream/` or `.ultrarepo/upstream/`.
  - All rebrand changes must go in `rebrand/` and be applied via scripts.
  - Preserve the rebrand strategy: Ensure the final extension appears fully AirVeo-branded, with no KiloCode visible UI.
  - Use pnpm + turbo for builds.
  - After changes, validate by running the build script and testing the VSIX.

**Goal**: Sync the `upstream` submodule to the v4.124.0 release of KiloCode. Update the rebrand process to ensure compatibility, while retaining all existing rebrand scripts and the AirVeo branding strategy. The final output should be a fully functional, AirVeo-branded extension built from v4.124.0.

**Steps to Follow**:
1. **Sync the Submodule**: Update the `upstream` Git submodule to point to the v4.124.0 tag/commit from https://github.com/Kilo-Org/kilocode. Ensure it's pulled correctly without modifying local files.
2. **Analyze Changes**: Review the changelog/diffs between v4.83.1 and v4.124.0. Identify potential impacts on:
   - Dependencies (e.g., new packages in `package.json`).
   - File structure (e.g., new/removed files in `src/`, `webview-ui/`, or assets).
   - Build process (e.g., changes to Turbo configs or VSIX generation).
   - UI elements (e.g., new webviews, icons, or localization keys that need rebranding).
3. **Update Rebrand Folder**: If upstream changes affect rebrand targets (e.g., new files need copying or new NLS keys need patching), update `rebrand/kilocode/` accordingly. Do not alter upstream directly.
4. **Modify Rebrand Scripts**: Update scripts in `rebrand/scripts/` for compatibility (e.g., add new icon mappings in `icon-rebrand-builder.sh` or handle new file paths in `rebrand-webviews-builder.sh`). Ensure they still apply AirVeo branding correctly.
5. **Test the Build**: Run `bash rebrand/scripts/build-airveo-complete.sh` to build the extension. Fix any errors (e.g., missing dependencies, script failures). Validate the VSIX output.
6. **Verify Branding**: Install the built VSIX locally and check that all visible UI is AirVeo-branded (e.g., extension name, icons, webviews, commands). Ensure no KiloCode references remain.
7. **Document Changes**: Provide a summary of what was updated, any new features from v4.124.0 that are now included, and any remaining issues.

**Expected Outcome**: The project builds successfully to v4.124.0 with full AirVeo branding intact. The rebrand scripts are preserved and functional. If blockers arise (e.g., major upstream changes), suggest incremental updates or additional rebrand adjustments.

Proceed step-by-step, and ask for clarification if needed. Focus on correctness, safety, and maintaining the rebrand integrity.