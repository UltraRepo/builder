# UltraRepo Command Refactoring Plan

## Overview
This document outlines the plan to completely rebrand the VS Code extension from KiloCode to UltraRepo, including command refactoring, proper naming, and icon restoration.

## Current Issues
1. Extension ID is still `kilocode.kilo-code` (works but incorrect branding)
2. App name shows as "Kilo Code" instead of "UltraRepo"
3. Icons reverted to KiloCode icons instead of UltraRepo icons
4. All VS Code commands still use `kilo-code.*` and `kilocode.*` prefixes

## Goals
1. **Proper Extension ID**: Change from `kilocode.kilo-code` to `UltraRepo.ultrarepo`
2. **Display Name**: Show as "UltraRepo AI Coder (KiloCode fork)" by publisher "UltraRepo"
3. **Command Refactoring**: Update all commands from `kilo-code.*` to `ultrarepo.*`
4. **Icon Restoration**: Ensure UltraRepo icons are used consistently
5. **Maintain Functionality**: All features must work after refactoring

## Task List

### Phase 1: Create Command Refactoring Script
- [ ] **Task 1.1**: Create `refactor-kilocode-commands.sh` script
  - Scan all source files for command references
  - Replace `kilo-code.` with `ultrarepo.` 
  - Replace `kilocode.` with `ultrarepo.`
  - Handle special cases and context variables

### Phase 2: Update Package Configuration
- [ ] **Task 2.1**: Update package.json extension ID
  - Change `"name": "kilo-code"` to `"name": "ultrarepo"`
  - Change `"publisher": "kilocode"` to `"publisher": "UltraRepo"`
  
- [ ] **Task 2.2**: Update localization files
  - Set displayName to "UltraRepo AI Coder (KiloCode fork)"
  - Keep description as "Open Source AI coding assistant"

### Phase 3: Fix Icon Issues
- [ ] **Task 3.1**: Debug icon rebranding script
  - Verify UltraRepo icons exist in rebrand/assets/icons
  - Check icon mapping in icon-rebrand.sh
  - Ensure proper icon is set in package.json

- [ ] **Task 3.2**: Test icon replacement
  - Build extension and verify UltraRepo icons appear
  - Check both light and dark theme icons

### Phase 4: Command Reference Updates
- [ ] **Task 4.1**: Update extension.ts command references
  - Line 204: `"kilo-code.SidebarProvider.focus"`
  - Line 212: `"kilocode.kilo-code#kiloCodeWalkthrough"`
  - All other hardcoded command strings

- [ ] **Task 4.2**: Update package.json command definitions
  - All `kilo-code.*` command IDs in contributes.commands
  - All `kilocode.*` context variables
  - Walkthrough ID references

- [ ] **Task 4.3**: Update service files
  - Ghost service commands and context variables
  - Commit message provider commands
  - Any other service command references

### Phase 5: Testing and Validation
- [ ] **Task 5.1**: Build test extension
  - Run build with new command refactoring
  - Verify VSIX is created successfully

- [ ] **Task 5.2**: Functionality testing
  - Install extension and test all commands work
  - Verify sidebar, menus, and context actions
  - Test walkthrough and first-time setup

- [ ] **Task 5.3**: Branding verification
  - Confirm extension shows as "UltraRepo AI Coder (KiloCode fork)"
  - Verify publisher shows as "UltraRepo"
  - Check that UltraRepo icons are displayed

## File Inventory (Files that need command updates)

### Core Extension Files
- `src/extension.ts` - Main extension entry point
- `src/package.json` - Extension manifest
- `src/package.nls*.json` - All localization files

### Service Files with Commands
- `src/services/commit-message/CommitMessageProvider.ts`
- `src/services/ghost/GhostCodeActionProvider.ts`
- `src/services/ghost/GhostProvider.ts`
- `src/services/ghost/index.ts`

### Test Files (may need updates)
- `src/services/ghost/__tests__/GhostModelPerformance.spec.ts`

### Build Scripts to Update
- `rebrand/scripts/patch-nls-ultrarepo.sh` (rename to legacy)
- Create new `rebrand/scripts/patch-nls-ultrarepo-proper.sh`
- Create new `rebrand/scripts/refactor-kilocode-commands.sh`
- Update `rebrand/scripts/build-ultrarepo.sh` to use new scripts

## Command Mapping Reference

### Current Commands → New Commands
- `kilo-code.SidebarProvider.focus` → `ultrarepo.SidebarProvider.focus`
- `kilo-code.plusButtonClicked` → `ultrarepo.plusButtonClicked`
- `kilo-code.newTask` → `ultrarepo.newTask`
- `kilo-code.ghost.*` → `ultrarepo.ghost.*`
- `kilocode.ghost.*` (context) → `ultrarepo.ghost.*`
- All other `kilo-code.*` → `ultrarepo.*`

### Special Cases
- Walkthrough ID: `kilocode.kilo-code#kiloCodeWalkthrough` → `UltraRepo.ultrarepo#ultrarepoWalkthrough`
- Context variables: `kilocode.ghost.*` → `ultrarepo.ghost.*`
- API endpoints: `kilocode.ai` references (may need updates)

## Risk Assessment

### High Risk
- Command ID changes could break existing user workflows
- Extension marketplace conflicts if ID already exists
- Walkthrough and first-time setup flow disruption

### Medium Risk  
- Icon mapping issues causing visual inconsistencies
- Localization file encoding problems
- Build script integration issues

### Low Risk
- Service command registration failures
- Test file reference mismatches

## Success Criteria
1. ✅ Extension installs with ID `UltraRepo.ultrarepo`
2. ✅ Display name shows "UltraRepo AI Coder (KiloCode fork)"
3. ✅ All commands work with `ultrarepo.*` prefix
4. ✅ UltraRepo icons displayed in VS Code
5. ✅ Sidebar, menus, and functionality unchanged
6. ✅ First-time setup and walkthrough work
7. ✅ No broken command references or console errors

## Rollback Plan
- Keep original `patch-nls-ultrarepo.sh` as `patch-nls-ultrarepo-legacy.sh`
- Maintain build flag to switch between kilocode and ultrarepo command sets
- Document command mapping for troubleshooting

## Implementation Order
1. Create and test command refactoring script in isolation
2. Update build process to use proper UltraRepo branding
3. Fix icon issues independently  
4. Apply command refactoring to build directory
5. Test extension functionality thoroughly
6. Deploy and validate complete rebranding
