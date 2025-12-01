import * as vscode from "vscode"
import * as dotenvx from "@dotenvx/dotenvx"
import * as path from "path"

// Load environment variables from .env file
try {
	// Specify path to .env file in the project root directory
	const envPath = path.join(__dirname, "..", ".env")
	dotenvx.config({ path: envPath })
} catch (e) {
	// Silently handle environment loading errors
	console.warn("Failed to load environment variables:", e)
}

import { CloudService, ExtensionBridgeService } from "@roo-code/cloud"
import { TelemetryService, PostHogTelemetryClient } from "@roo-code/telemetry"

import "./utils/path" // Necessary to have access to String.prototype.toPosix.
import { createOutputChannelLogger, createDualLogger } from "./utils/outputChannelLogger"

import { Package } from "./shared/package"
import { formatLanguage } from "./shared/language"
import { ContextProxy } from "./core/config/ContextProxy"
import { ClineProvider } from "./core/webview/ClineProvider"
import { DIFF_VIEW_URI_SCHEME } from "./integrations/editor/DiffViewProvider"
import { TerminalRegistry } from "./integrations/terminal/TerminalRegistry"
import { McpServerManager } from "./services/mcp/McpServerManager"
import { CodeIndexManager } from "./services/code-index/manager"
import { registerCommitMessageProvider } from "./services/commit-message"
import { MdmService } from "./services/mdm/MdmService"
import { migrateSettings } from "./utils/migrateSettings"
import { checkAndRunAutoLaunchingTask as checkAndRunAutoLaunchingTask } from "./utils/autoLaunchingTask"
import { autoImportSettings } from "./utils/autoImportSettings"
import { isRemoteControlEnabled } from "./utils/remoteControl"
import { API } from "./extension/api"

import {
	handleUri,
	registerCommands,
	registerCodeActions,
	registerTerminalActions,
	CodeActionProvider,
} from "./activate"
import { initializeI18n } from "./i18n"
import { registerGhostProvider } from "./services/ghost" // kilocode_change
import { TerminalWelcomeService } from "./services/terminal-welcome/TerminalWelcomeService" // kilocode_change

/**
 * Built using https://github.com/microsoft/vscode-webview-ui-toolkit
 *
 * Inspired by:
 *  - https://github.com/microsoft/vscode-webview-ui-toolkit-samples/tree/main/default/weather-webview
 *  - https://github.com/microsoft/vscode-webview-ui-toolkit-samples/tree/main/frameworks/hello-world-react-cra
 */

let outputChannel: vscode.OutputChannel
let extensionContext: vscode.ExtensionContext

// ---- Inline Home Webview (InfraNow-style) ----
const HOME_APP_NAME = "AirVeo App Builder"
const HOME_PRIMARY = "#0B65D8"
const HOME_BG = "#0D1117"

class UltraHomePanel {
	static current: UltraHomePanel | undefined
	private readonly panel: vscode.WebviewPanel
	private disposables: vscode.Disposable[] = []

	static createOrShow(extensionUri: vscode.Uri) {
		const column = vscode.window.activeTextEditor?.viewColumn
		if (UltraHomePanel.current) {
			UltraHomePanel.current.panel.reveal(column)
			return
		}
		const panel = vscode.window.createWebviewPanel(
			'ultrarepoHomePanel',
			'Home',
			column ?? vscode.ViewColumn.One,
			{ enableScripts: true, retainContextWhenHidden: true }
		)
		try {
			// Try to set icon if available
			try {
				panel.iconPath = vscode.Uri.joinPath(extensionUri, 'assets', 'icons', 'icon-home.png')
			} catch {}
		} catch {}
		UltraHomePanel.current = new UltraHomePanel(panel, extensionUri)
	}

	constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
		this.panel = panel
		this.panel.webview.html = this.getHtml(this.panel.webview, extensionUri)
		this.panel.webview.onDidReceiveMessage(async (msg: any) => {
			outputChannel.appendLine(`[Home Webview] Received message: ${JSON.stringify(msg)}`)
			if (!msg || typeof msg.type !== 'string') return

			// Legacy run-cmd message (from some webview code)
			if (msg.type === 'run-cmd' && msg.cmd) {
				outputChannel.appendLine(`[Home Webview] Executing command: ${msg.cmd}`)
				try {
					await vscode.commands.executeCommand(msg.cmd)
					outputChannel.appendLine(`[Home Webview] Command executed successfully: ${msg.cmd}`)
				} catch (error) {
					outputChannel.appendLine(`[Home Webview] Error executing command ${msg.cmd}: ${error}`)
				}
				return
			}

			// Open external links
			if (msg.type === 'open-link' && msg.href) {
				try {
					await vscode.env.openExternal(vscode.Uri.parse(msg.href))
				} catch {}
				return
			}

			// Launch the dependency graph viewer (posted from the React UI)
			if (msg.type === 'launchGraphViewer') {
				outputChannel.appendLine('[Home Webview] Launching graph viewer via launchGraphViewer message')
				// Execute the contributed command which creates the Graph webview panel
				vscode.commands.executeCommand('ultrarepo.showDependencyGraph')
				return
			}

			// Refresh the existing graph viewer by re-opening it
			if (msg.type === 'refreshGraph') {
				outputChannel.appendLine('[Home Webview] Refreshing graph viewer')
				vscode.commands.executeCommand('ultrarepo.showDependencyGraph')
				return
			}
		}, null, this.disposables)
		this.panel.onDidDispose(() => this.dispose(), null, this.disposables)
	}

	dispose() {
		UltraHomePanel.current = undefined
		while (this.disposables.length) {
			const d = this.disposables.pop(); if (d) d.dispose()
		}
	}

	private getHtml(webview: vscode.Webview, extensionUri: vscode.Uri) {
		const nonce = String(Date.now())
		const iconUri = webview.asWebviewUri(vscode.Uri.joinPath(extensionUri, 'assets', 'icons', 'icon-home.png'))
		const iconSrc = `${iconUri.toString()}?v=${nonce}`
		return `<!doctype html>
<html>
<head>
	<meta charset="UTF-8">
	<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src data: ${webview.cspSource}; style-src 'unsafe-inline'; script-src 'nonce-${nonce}';">
	<meta name="viewport" content="width=device-width,initial-scale=1">
	<title>${HOME_APP_NAME}</title>
	<style>
		:root { --primary:${HOME_PRIMARY}; --bg:${HOME_BG}; --pad:16px; --gutter:8px; }
		html,body{margin:0;padding:0;background:var(--bg);color:#fff;font-family:ui-sans-serif,-apple-system,Segoe UI,Roboto,Ubuntu,Cantarell,Noto Sans,Arial}
		header{background:linear-gradient(180deg,var(--primary),#09449a);box-shadow:0 2px 12px rgba(0,0,0,.35)}
		.header-inner{padding:12px var(--pad);display:grid;grid-template-columns:auto 1fr;align-items:center}
		.brand{display:flex;align-items:center;gap:10px}
		.brand img{width:28px;height:28px;border-radius:0}
		.brand h1{font-size:18px;margin:0;font-weight:800}
		nav{display:flex;gap:8px;padding:0 var(--pad) 10px}
		nav a{color:#fff;opacity:.95;text-decoration:none;padding:6px 10px;border-radius:8px;font-size:13px}
		nav a.active,nav a:hover{background:rgba(255,255,255,.12)}
		.wrap{padding:18px}
		.card{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);border-radius:12px;padding:16px}
		.muted{opacity:.85;font-size:13px}
		section{display:none}
		section.active{display:block}
	</style>
</head>
<body>
	<header>
		<div class="header-inner">
			<div class="brand"><img src="${iconSrc}" alt="UR"><h1>${HOME_APP_NAME}</h1></div>
		</div>
		<nav class="nav">
			<a href="#/home" data-route="home">Home</a>
			<a href="#/graph" data-route="graph">Graph</a>
			<a href="#/commands" data-route="commands">Commands</a>
			<a href="#/mcp" data-route="mcp">MCP</a>
			<a href="#/settings" data-route="settings">Settings</a>
		</nav>
	</header>
	<div class="wrap">
		<section id="home" class="active"><div class="card"><h2>Home</h2><p class="muted">Welcome to AirVeo App Builder - your AI coding assistant. Choose a feature from the navigation above to get started.</p><button onclick="vscode.postMessage({type:'run-cmd', cmd:'ultrarepo.showDependencyGraph'})" style="margin-top:16px;padding:10px 20px;background:var(--primary);color:#fff;border:none;border-radius:8px;cursor:pointer;">Open Dependency Graph</button></div></section>
			<section id="graph"><div class="card"><h2>Dependency Graph</h2><p class="muted">Visualize and explore your project dependencies. Click the button below to open the graph.</p><button onclick="vscode.postMessage({type:'run-cmd', cmd:'ultrarepo.showDependencyGraph'})" style="margin-top:16px;padding:10px 20px;background:var(--primary);color:#fff;border:none;border-radius:8px;cursor:pointer;">Open Dependency Graph</button>
			<p class="muted" style="margin-top:10px">Note: make sure to start the Arrows Graph Server before opening the graph. From the repo root run:<br><code>bash rebrand/scripts/start-arrows.sh</code><br>If you already installed dependencies, you can skip install:<br><code>bash rebrand/scripts/start-arrows.sh --skip-install</code></p></div></section>
		<section id="commands"><div class="card"><h2>Commands</h2><p class="muted">Access AirVeo App Builder commands and features. Use the command palette (Ctrl+Shift+P) to explore available commands.</p></div></section>
			<section id="mcp"><div class="card"><h2>MCP Services</h2><p class="muted">Manage and configure Model Context Protocol services for enhanced AI capabilities.</p><button onclick="vscode.postMessage({type:'run-cmd', cmd:'ultrarepo.mcpButtonClicked'})">Open MCP Settings</button></div></section>
			<section id="settings"><div class="card"><h2>Settings</h2><p class="muted">Configure AirVeo App Builder settings and preferences.</p><button onclick="vscode.postMessage({type:'run-cmd', cmd:'ultrarepo.settingsButtonClicked'})">Open Settings</button></div></section>
	</div>
	<script nonce="${nonce}">
		const vscode = acquireVsCodeApi();
		function applyRoute(route){
			document.querySelectorAll('nav a').forEach(a=>a.classList.toggle('active', a.dataset.route===route));
			document.querySelectorAll('section').forEach(s=>s.classList.remove('active'));
			const t=document.getElementById(route); if(t) t.classList.add('active');
			vscode.setState({route}); history.replaceState(null,'','#/'+route);
		}
		document.body.addEventListener('click', (e)=>{
			const a=(e.target instanceof HTMLElement)? e.target.closest('a'):null; if(!a) return;

			// Prefer activating the route so the section/card becomes visible.
			const route = a.dataset.route;
			const cmd = a.getAttribute('data-cmd');

			if(route) {
				e.preventDefault();
				applyRoute(route);
			}

			// If this link also triggers a command (e.g. open graph viewer), run it
			if(cmd) {
				e.preventDefault();
				vscode.postMessage({type:'run-cmd', cmd});
			}

			const href=a.getAttribute('href');
			if(href && href.startsWith('http')){ e.preventDefault(); vscode.postMessage({type:'open-link', href}); }
		});
		const initial=(()=>{ const h=location.hash||''; if(!h) return 'home'; return h.startsWith('#/')? h.slice(2) : (h.startsWith('#')? h.slice(1) : h); })();
		applyRoute(initial);
		window.addEventListener('hashchange', ()=> applyRoute((()=>{ const h=location.hash||''; if(!h) return 'home'; return h.startsWith('#/')? h.slice(2) : (h.startsWith('#')? h.slice(1) : h); })()));
	</script>
</body>
</html>`
	}
}

// This method is called when your extension is activated.
// Your extension is activated the very first time the command is executed.
export async function activate(context: vscode.ExtensionContext) {
	extensionContext = context
	outputChannel = vscode.window.createOutputChannel(Package.outputChannel)
	context.subscriptions.push(outputChannel)
	outputChannel.appendLine(`${Package.name} extension activated - ${JSON.stringify(Package)}`)

	// Migrate old settings to new
	await migrateSettings(context, outputChannel)

	// Initialize telemetry service.
	const telemetryService = TelemetryService.createInstance()

	try {
		telemetryService.register(new PostHogTelemetryClient())
	} catch (error) {
		console.warn("Failed to register PostHogTelemetryClient:", error)
	}

	// Create logger for cloud services.
	const cloudLogger = createDualLogger(createOutputChannelLogger(outputChannel))

	// kilocode_change start: no Roo cloud service
	// Initialize Roo Code Cloud service.
	// const cloudService = await CloudService.createInstance(context, cloudLogger)

	// try {
	// 	if (cloudService.telemetryClient) {
	// 		TelemetryService.instance.register(cloudService.telemetryClient)
	// 	}
	// } catch (error) {
	// 	outputChannel.appendLine(
	// 		`[CloudService] Failed to register TelemetryClient: ${error instanceof Error ? error.message : String(error)}`,
	// 	)
	// }

	// const postStateListener = () => {
	// 	ClineProvider.getVisibleInstance()?.postStateToWebview()
	// }

	// cloudService.on("auth-state-changed", postStateListener)
	// cloudService.on("user-info", postStateListener)
	// cloudService.on("settings-updated", postStateListener)

	// // Add to subscriptions for proper cleanup on deactivate
	// context.subscriptions.push(cloudService)
	// kilocode_change end

	// Initialize MDM service
	const mdmService = await MdmService.createInstance(cloudLogger)

	// Initialize i18n for internationalization support
	initializeI18n(context.globalState.get("language") ?? formatLanguage(vscode.env.language))

	// Initialize terminal shell execution handlers.
	TerminalRegistry.initialize()

	// Get default commands from configuration.
	const defaultCommands = vscode.workspace.getConfiguration(Package.name).get<string[]>("allowedCommands") || []

	// Initialize global state if not already set.
	if (!context.globalState.get("allowedCommands")) {
		context.globalState.update("allowedCommands", defaultCommands)
	}

	// kilocode_change start
	if (!context.globalState.get("firstInstallCompleted")) {
		await context.globalState.update("telemetrySetting", "enabled")
	}
	// kilocode_change end

	const contextProxy = await ContextProxy.getInstance(context)

	// Initialize code index managers for all workspace folders
	const codeIndexManagers: CodeIndexManager[] = []
	if (vscode.workspace.workspaceFolders) {
		for (const folder of vscode.workspace.workspaceFolders) {
			const manager = CodeIndexManager.getInstance(context, folder.uri.fsPath)
			if (manager) {
				codeIndexManagers.push(manager)
				try {
					await manager.initialize(contextProxy)
				} catch (error) {
					outputChannel.appendLine(
						`[CodeIndexManager] Error during background CodeIndexManager configuration/indexing for ${folder.uri.fsPath}: ${error.message || error}`,
					)
				}
				context.subscriptions.push(manager)
			}
		}
	}

	// Initialize Roo Code Cloud service.
	const cloudService = await CloudService.createInstance(context, cloudLogger)

	try {
		if (cloudService.telemetryClient) {
			// TelemetryService.instance.register(cloudService.telemetryClient) kilocode_change
		}
	} catch (error) {
		outputChannel.appendLine(
			`[CloudService] Failed to register TelemetryClient: ${error instanceof Error ? error.message : String(error)}`,
		)
	}

	const postStateListener = () => ClineProvider.getVisibleInstance()?.postStateToWebview()

	cloudService.on("auth-state-changed", postStateListener)
	cloudService.on("settings-updated", postStateListener)

	cloudService.on("user-info", async ({ userInfo }) => {
		postStateListener()

		const bridgeConfig = await cloudService.cloudAPI?.bridgeConfig().catch(() => undefined)

		if (!bridgeConfig) {
			outputChannel.appendLine("[CloudService] Failed to get bridge config")
			return
		}

		ExtensionBridgeService.handleRemoteControlState(
			userInfo,
			contextProxy.getValue("remoteControlEnabled"),
			{ ...bridgeConfig, provider: provider as any, sessionId: vscode.env.sessionId },
			(message: string) => outputChannel.appendLine(message),
		)
	})

	// Add to subscriptions for proper cleanup on deactivate.
	context.subscriptions.push(cloudService)

	const provider = new ClineProvider(context, outputChannel, "sidebar", contextProxy, mdmService)
	TelemetryService.instance.setProvider(provider)

	context.subscriptions.push(
		vscode.window.registerWebviewViewProvider(ClineProvider.sideBarId, provider, {
			webviewOptions: { retainContextWhenHidden: true },
		}),
	)

	// Internal command to open the inline Home panel
	context.subscriptions.push(
		vscode.commands.registerCommand('ultrarepo.__openHomeInline', () => {
			UltraHomePanel.createOrShow(context.extensionUri)
		})
	)

	// kilocode_change start
	if (!context.globalState.get("firstInstallCompleted")) {
		outputChannel.appendLine("First installation detected, opening AirVeo Builder sidebar!")
		try {
			await vscode.commands.executeCommand("ultrarepo.SidebarProvider.focus")

			outputChannel.appendLine("Opening AirVeo Builder walkthrough")

			// this can crash, see:
			// https://discord.com/channels/1349288496988160052/1395865796026040470
			await vscode.commands.executeCommand(
				"workbench.action.openWalkthrough",
				"UltraRepo.ultrarepo#ultrarepoWalkthrough",
				false,
			)
		} catch (error) {
			outputChannel.appendLine(`Error during first-time setup: ${error.message}`)
		} finally {
			await context.globalState.update("firstInstallCompleted", true)
		}
	}
	// kilocode_change end

	// Auto-import configuration if specified in settings
	try {
		await autoImportSettings(outputChannel, {
			providerSettingsManager: provider.providerSettingsManager,
			contextProxy: provider.contextProxy,
			customModesManager: provider.customModesManager,
		})
	} catch (error) {
		outputChannel.appendLine(
			`[AutoImport] Error during auto-import: ${error instanceof Error ? error.message : String(error)}`,
		)
	}

	registerCommands({ context, outputChannel, provider })

	/**
	 * We use the text document content provider API to show the left side for diff
	 * view by creating a virtual document for the original content. This makes it
	 * readonly so users know to edit the right side if they want to keep their changes.
	 *
	 * This API allows you to create readonly documents in VSCode from arbitrary
	 * sources, and works by claiming an uri-scheme for which your provider then
	 * returns text contents. The scheme must be provided when registering a
	 * provider and cannot change afterwards.
	 *
	 * Note how the provider doesn't create uris for virtual documents - its role
	 * is to provide contents given such an uri. In return, content providers are
	 * wired into the open document logic so that providers are always considered.
	 *
	 * https://code.visualstudio.com/api/extension-guides/virtual-documents
	 */
	const diffContentProvider = new (class implements vscode.TextDocumentContentProvider {
		provideTextDocumentContent(uri: vscode.Uri): string {
			return Buffer.from(uri.query, "base64").toString("utf-8")
		}
	})()

	context.subscriptions.push(
		vscode.workspace.registerTextDocumentContentProvider(DIFF_VIEW_URI_SCHEME, diffContentProvider),
	)

	context.subscriptions.push(vscode.window.registerUriHandler({ handleUri }))

	// Register code actions provider.
	context.subscriptions.push(
		vscode.languages.registerCodeActionsProvider({ pattern: "**/*" }, new CodeActionProvider(), {
			providedCodeActionKinds: CodeActionProvider.providedCodeActionKinds,
		}),
	)

	registerGhostProvider(context, provider) // kilocode_change
	registerCommitMessageProvider(context, outputChannel) // kilocode_change
	registerCodeActions(context)
	registerTerminalActions(context)

	// Allows other extensions to activate once Kilo Code is ready.
	vscode.commands.executeCommand(`${Package.name}.activationCompleted`)

	// Implements the `RooCodeAPI` interface.
	const socketPath = process.env.KILO_IPC_SOCKET_PATH ?? process.env.ROO_CODE_IPC_SOCKET_PATH // kilocode_change
	const enableLogging = typeof socketPath === "string"

	// Watch the core files and automatically reload the extension host.
	if (process.env.NODE_ENV === "development") {
		const watchPaths = [
			{ path: context.extensionPath, pattern: "**/*.ts" },
			{ path: path.join(context.extensionPath, "../packages/types"), pattern: "**/*.ts" },
			{ path: path.join(context.extensionPath, "../packages/telemetry"), pattern: "**/*.ts" },
			{ path: path.join(context.extensionPath, "node_modules/@roo-code/cloud"), pattern: "**/*" },
		]

		console.log(
			`♻️♻️♻️ Core auto-reloading: Watching for changes in ${watchPaths.map(({ path }) => path).join(", ")}`,
		)

		// Create a debounced reload function to prevent excessive reloads
		let reloadTimeout: NodeJS.Timeout | undefined
		const DEBOUNCE_DELAY = 1_000

		const debouncedReload = (uri: vscode.Uri) => {
			if (reloadTimeout) {
				clearTimeout(reloadTimeout)
			}

			console.log(`♻️ ${uri.fsPath} changed; scheduling reload...`)

			reloadTimeout = setTimeout(() => {
				console.log(`♻️ Reloading host after debounce delay...`)
				vscode.commands.executeCommand("workbench.action.reloadWindow")
			}, DEBOUNCE_DELAY)
		}

		watchPaths.forEach(({ path: watchPath, pattern }) => {
			const relPattern = new vscode.RelativePattern(vscode.Uri.file(watchPath), pattern)
			const watcher = vscode.workspace.createFileSystemWatcher(relPattern, false, false, false)

			// Listen to all change types to ensure symlinked file updates trigger reloads.
			watcher.onDidChange(debouncedReload)
			watcher.onDidCreate(debouncedReload)
			watcher.onDidDelete(debouncedReload)

			context.subscriptions.push(watcher)
		})

		// Clean up the timeout on deactivation
		context.subscriptions.push({
			dispose: () => {
				if (reloadTimeout) {
					clearTimeout(reloadTimeout)
				}
			},
		})
	}

	await checkAndRunAutoLaunchingTask(context) // kilocode_change

	return new API(outputChannel, provider, socketPath, enableLogging)
}

// This method is called when your extension is deactivated.
export async function deactivate() {
	outputChannel.appendLine(`${Package.name} extension deactivated`)

	const bridgeService = ExtensionBridgeService.getInstance()

	if (bridgeService) {
		await bridgeService.disconnect()
	}

	await McpServerManager.cleanup(extensionContext)
	TelemetryService.instance.shutdown()
	TerminalRegistry.cleanup()
}
