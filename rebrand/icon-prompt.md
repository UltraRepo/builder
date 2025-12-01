# AI Prompt: Debugging VS Code Extension Icon Replacement

You are tasked with ensuring that the UltraRepo (or KiloCode) VS Code extension displays the correct rebranded icon on the VS Code extension description page. If the old KiloCode icon still appears, follow these steps to debug and fix the issue:

## Debugging Steps
1. **Check the Main Icon Reference:**
   - Open `src/package.json` in your extension source.
   - Ensure the `"icon"` field points to the correct rebranded icon file (e.g., `assets/icons/icon.png` or `logo-outline-black.png`).

2. **Verify Icon File Exists:**
   - Confirm the icon file exists in the built extension's `assets/icons` directory.

3. **Check the Rebrand Script:**
   - Review `rebrand/scripts/icon-rebrand.sh` to ensure it copies the correct icon file to the right location.
   - Run the script manually if needed:
     ```sh
     bash rebrand/scripts/icon-rebrand.sh build/kilocode/assets/icons
     ```

4. **Rebuild the Extension:**
   - Run the build script to ensure all changes are included:
     ```sh
     bash rebrand/scripts/build-ultrarepo.sh
     ```

5. **Uninstall Old Extension:**
   - Remove any previously installed versions of the extension from VS Code.
   - Delete the extension folder from `~/.vscode/extensions/` if necessary.

6. **Install the New VSIX:**
   - Install the newly built VSIX file in VS Code.

7. **Restart VS Code:**
   - Sometimes VS Code caches extension metadata. Restart VS Code to ensure the new icon is loaded.

## If the Icon Still Does Not Change
- Double-check that the `icon` field in `package.json` matches the file you want to display.
- Make sure the VSIX you are installing is the one you just built.
- Check for other icon references in `package.json` (e.g., activity bar, dark/light icons) and update as needed.
- If the extension name or publisher matches a Marketplace extension, VS Code may show Marketplace branding. Consider changing both to unique values.

---

**Prompt for AI:**
> "The VS Code extension icon is not updating after rebranding. What steps should I take to ensure the new icon appears on the extension description page?"
