# KiloCode Extension: Icon Usage Reference

| Icon File Name                | Used In File(s) & Line(s)                                   | Purpose/Context                                   | File Type |
|-------------------------------|------------------------------------------------------------|---------------------------------------------------|-----------|
| logo-outline-black.gif        | src/services/ghost/GhostCursorAnimation.ts:10<br>src/dist/extension.js:6312 | Ghost cursor animation (gutter icon, wait state)  | GIF       |
| logo-outline-yellow.gif       | src/services/ghost/GhostCursorAnimation.ts:15<br>src/dist/extension.js:6312 | Ghost cursor animation (gutter icon, active state)| GIF       |
| kilo.png                      | src/activate/registerCommands.ts:302<br>src/package.json:113<br>src/dist/extension.js:3845 | Extension icon (light theme, sidebar, etc.)       | PNG       |
| kilo-dark.png                 | src/activate/registerCommands.ts:303<br>src/package.json:114<br>src/dist/extension.js:3845 | Extension icon (dark theme, sidebar, etc.)        | PNG       |
| kilo-light.svg                | src/package.json:254                                       | Extension icon (light theme, SVG)                 | SVG       |
| kilo-dark.svg                 | src/package.json:255                                       | Extension icon (dark theme, SVG)                  | SVG       |
| logo-outline-black.png        | src/package.json:7                                         | Main extension icon (Marketplace, VSIX)           | PNG       |
| icon.png                      | packages/build/src/__tests__/index.test.ts:14<br>packages/build/dist/__tests__/index.test.js:12 | Test/build icon reference                          | PNG       |

**Notes:**
- Line numbers are approximate and may change with code edits.
- Some icons are referenced in minified/bundled files (e.g., `dist/extension.js`) as a result of the build process.
- The main extension icon for VS Code Marketplace and VSIX is typically set in `package.json` as `logo-outline-black.png`.
- Test/build icons may not appear in the user interface.
