
# KiloCode to UltraRepo Icon Rebranding Mapping

| KiloCode Icon Name            | Used In File(s) & Line(s)                                   | Purpose/Context                                   | File Type | UltraRepo Replacement Icon (from rebrand/assets/icons) | Replacement Notes |
|-------------------------------|------------------------------------------------------------|---------------------------------------------------|-----------|--------------------------------------------------------|-------------------|
| logo-outline-black.gif        | src/services/ghost/GhostCursorAnimation.ts:10<br>src/dist/extension.js:6312 | Ghost cursor animation (gutter icon, wait state)  | GIF       | logo-outline-black.gif                                 | Copy & overwrite |
| logo-outline-yellow.gif       | src/services/ghost/GhostCursorAnimation.ts:15<br>src/dist/extension.js:6312 | Ghost cursor animation (gutter icon, active state)| GIF       | logo-outline-yellow.gif                                | Copy & overwrite |
| kilo.png                      | src/activate/registerCommands.ts:302<br>src/package.json:113<br>src/dist/extension.js:3845 | Extension icon (light theme, sidebar, etc.)       | PNG       | icon.png                                               | Copy as kilo.png  |
| kilo-dark.png                 | src/activate/registerCommands.ts:303<br>src/package.json:114<br>src/dist/extension.js:3845 | Extension icon (dark theme, sidebar, etc.)        | PNG       | icon.png                                               | Copy as kilo-dark.png |
| kilo-light.svg                | src/package.json:254                                       | Extension icon (light theme, SVG)                 | SVG       | icon-light.svg                                         | Copy as kilo-light.svg |
| kilo-dark.svg                 | src/package.json:255                                       | Extension icon (dark theme, SVG)                  | SVG       | icon-dark.svg                                          | Copy as kilo-dark.svg |
| logo-outline-black.png        | src/package.json:7                                         | Main extension icon (Marketplace, VSIX)           | PNG       | logo-outline-black.png                                 | Copy & overwrite |
| icon.png                      | packages/build/src/__tests__/index.test.ts:14<br>packages/build/dist/__tests__/index.test.js:12 | Test/build icon reference                          | PNG       | icon.png                                               | Copy & overwrite |

**Notes:**
- All new icons are sourced from `rebrand/assets/icons`.
- The rebranding script will copy and rename the new UltraRepo icons to the extension's asset folder, overwriting or replacing the original KiloCode icons as needed.
- This approach avoids the need to change any code references in the extension.
- The script can be run after the extension is built to ensure the correct icons are present in the VSIX.
