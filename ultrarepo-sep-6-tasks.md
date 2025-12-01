# UltraRepo Enhancement Tasks - September 6, 2025

## Executive Summary
Critical rebranding and functionality issues identified across the UltraRepo VS Code extension. The build directory has proper command prefixes but several key files still contain old KiloCode references. The rebrand directory is severely incomplete with missing essential components.

## Priority 1: Critical Build-Fixing Issues (Do First)

### 1.1 Fix Extension.ts Command References
**File:** `/Users/jetstart/dev/ultrarepo/code/build/kilocode/src/extension.ts`
**Issue:** Still uses old command references that will break functionality
**Impact:** Extension won't work properly on first install
**Tasks:**
- Line 204: Change `"kilo-code.SidebarProvider.focus"` → `"ultrarepo.SidebarProvider.focus"`
- Line 212: Change `"kilocode.kilo-code#kiloCodeWalkthrough"` → `"UltraRepo.ultrarepo#ultrarepoWalkthrough"`
- Line 202: Change log message from "Kilo Code sidebar" → "UltraRepo sidebar"

### 1.2 Fix Package.json View References
**File:** `/Users/jetstart/dev/ultrarepo/code/build/kilocode/src/package.json`
**Issue:** Activity bar and editor title menus still reference old identifiers
**Impact:** UI elements won't work correctly
**Tasks:**
- Line 113: Change `"kilo-code-ActivityBar"` → `"ultrarepo-ActivityBar"`
- Lines 116-117: Change icon paths from `"kilo.png"` → `"ultrarepo.png"`
- Line 495: Change `"kilo-code.TabPanelProvider"` → `"ultrarepo.TabPanelProvider"`

### 1.3 Fix RegisterCommands Branding Issues
**File:** `/Users/jetstart/dev/ultrarepo/code/build/kilocode/src/activate/registerCommands.ts`
**Issue:** Multiple branding references still point to KiloCode
**Impact:** User-facing text and links are incorrect
**Tasks:**
- Line 168: Change `"https://kilocode.ai"` → `"https://ultrarepo.com"`
- Line 312: Change panel title `"Kilo Code"` → `"UltraRepo"`
- Lines 316-319: Change icon paths from `"kilo.png"` → `"ultrarepo.png"`

### 1.4 Fix Package.ts Output Channel
**File:** `/Users/jetstart/dev/ultrarepo/code/build/kilocode/src/shared/package.ts`
**Issue:** Output channel still shows "Kilo-Code"
**Impact:** Debug logs show wrong extension name
**Tasks:**
- Line 15: Change `outputChannel: "Kilo-Code"` → `outputChannel: "UltraRepo"`

## Priority 2: Keybinding Context Fixes

### 2.1 Fix Keybinding Contexts
**File:** `/Users/jetstart/dev/ultrarepo/code/rebrand/kilocode/src/package.json`
**Issue:** Keybindings still use `kilocode.ghost.*` contexts
**Impact:** Keyboard shortcuts may not work properly
**Tasks:**
- Lines 322-371: Change all `kilocode.ghost.*` → `ultrarepo.ghost.*` in keybinding when conditions

## Priority 3: Webview UI Component Issues

### 3.1 Fix Rebrand Directory Completeness
**Issue:** Rebrand webview-ui is missing essential components
**Impact:** Webview won't build or function
**Tasks:**
- Copy missing components from build to rebrand:
  - `ButtonLink.tsx`, `ButtonSecondary.tsx`
  - `TranslationContext.tsx`
  - `ExtensionStateContext.tsx`
  - `helpers.ts`
  - All other missing UI components

### 3.2 Fix KiloCodeAuth Component
**File:** `/Users/jetstart/dev/ultrarepo/code/rebrand/kilocode/webview-ui/src/components/kilocode/common/KiloCodeAuth.tsx`
**Issue:** Multiple import errors and old references
**Impact:** Authentication UI won't work
**Tasks:**
- Fix missing imports (ButtonLink, ButtonSecondary, etc.)
- Change translation keys from `kilocode:*` → `ultrarepo:*`
- Update `getKiloCodeBackendSignUpUrl` function name and URL

## Priority 4: Content and Documentation Updates

### 4.1 Update Walkthrough Content
**Files:** `/Users/jetstart/dev/ultrarepo/code/build/kilocode/src/walkthrough/*.md`
**Issue:** Content still refers to "Kilo Code"
**Impact:** User onboarding shows wrong product name
**Tasks:**
- Update all walkthrough files to reference "UltraRepo" instead of "Kilo Code"
- Update any hardcoded URLs or references

### 4.2 Update Localization Files
**Files:** `/Users/jetstart/dev/ultrarepo/code/build/kilocode/src/package.nls.*.json`
**Issue:** May contain old references in other languages
**Impact:** Inconsistent branding in non-English locales
**Tasks:**
- Search and replace "Kilo Code" → "UltraRepo" in all localization files
- Update any URLs from kilocode.ai → ultrarepo.com

## Priority 5: Advanced Features (Post-Stability)

### 5.1 Implement Dependency Graph Feature
**Status:** Placeholder implementation exists
**Tasks:**
- Complete the dependency graph visualization
- Integrate with codebase indexing system
- Add graph interaction features

### 5.2 Enhance Codebase Indexing
**Status:** Basic system exists but needs optimization
**Tasks:**
- Implement incremental updates
- Add smart caching mechanisms
- Improve indexing performance for large codebases

## Implementation Strategy

### Phase 1: Critical Fixes (1-2 hours)
1. Fix extension.ts command references
2. Fix package.json view references
3. Fix registerCommands branding
4. Fix package.ts output channel

### Phase 2: Keybindings & UI (1-2 hours)
1. Update keybinding contexts
2. Complete rebrand directory components
3. Fix KiloCodeAuth component

### Phase 3: Content & Polish (1 hour)
1. Update walkthrough content
2. Update localization files
3. Test all functionality

### Phase 4: Advanced Features (Future)
1. Complete dependency graph
2. Enhance indexing system

## Testing Checklist
- [ ] Extension activates without errors
- [ ] Sidebar opens correctly
- [ ] Walkthrough displays proper branding
- [ ] All commands work with ultrarepo.* prefixes
- [ ] Webview UI loads without import errors
- [ ] Keyboard shortcuts function properly
- [ ] Output channel shows "UltraRepo"
- [ ] All UI text shows "UltraRepo" not "Kilo Code"

## Risk Assessment
- **High Risk:** Command reference fixes - could break extension if incorrect
- **Medium Risk:** UI component fixes - may cause build failures if incomplete
- **Low Risk:** Content updates - cosmetic changes only

## Success Criteria
- Extension builds successfully
- All UI elements show "UltraRepo" branding
- All commands use ultrarepo.* prefixes
- No import errors in webview
- Keyboard shortcuts work correctly
- Output logging shows correct extension name</content>
<parameter name="filePath">/Users/jetstart/dev/ultrarepo/code/ultrarepo-sep-6-tasks.md
