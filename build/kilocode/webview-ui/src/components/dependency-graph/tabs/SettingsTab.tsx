import React, { useState, useEffect } from 'react'

declare global {
  interface Window {
    vscode?: any
  }
}

interface GraphSettings {
  baseUrl: string
  indexingDepth: number
  includeNodeModules: boolean
  excludePatterns: string[]
  visualizationTheme: 'light' | 'dark' | 'auto'
  exportQuality: 'low' | 'medium' | 'high'
}

const SettingsTab: React.FC = () => {
  const [settings, setSettings] = useState<GraphSettings>({
    baseUrl: 'http://localhost:8080',
    indexingDepth: 3,
    includeNodeModules: false,
    excludePatterns: ['node_modules', '.git', 'dist', 'build'],
    visualizationTheme: 'auto',
    exportQuality: 'high'
  })

  const [isSaving, setIsSaving] = useState(false)
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle')

  useEffect(() => {
    // Load settings on mount
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      if (window.vscode) {
        window.vscode.postMessage({
          type: 'getGraphSettings',
          command: 'settings'
        })
      }

      // For now, use default settings
      // In production, this would load from VS Code workspace settings
    } catch (error) {
      console.error('Error loading settings:', error)
    }
  }

  const handleSaveSettings = async () => {
    setIsSaving(true)
    setSaveStatus('saving')

    try {
      if (window.vscode) {
        window.vscode.postMessage({
          type: 'saveGraphSettings',
          settings,
          command: 'settings'
        })
      }

      // Simulate save delay
      await new Promise(resolve => setTimeout(resolve, 1000))

      setSaveStatus('saved')
      setTimeout(() => setSaveStatus('idle'), 2000)
    } catch (error) {
      console.error('Error saving settings:', error)
      setSaveStatus('error')
    } finally {
      setIsSaving(false)
    }
  }

  const updateSetting = <K extends keyof GraphSettings>(
    key: K,
    value: GraphSettings[K]
  ) => {
    setSettings(prev => ({ ...prev, [key]: value }))
    setSaveStatus('idle') // Reset save status when settings change
  }

  const addExcludePattern = () => {
    setSettings(prev => ({
      ...prev,
      excludePatterns: [...prev.excludePatterns, '']
    }))
  }

  const updateExcludePattern = (index: number, value: string) => {
    setSettings(prev => ({
      ...prev,
      excludePatterns: prev.excludePatterns.map((pattern, i) =>
        i === index ? value : pattern
      )
    }))
  }

  const removeExcludePattern = (index: number) => {
    setSettings(prev => ({
      ...prev,
      excludePatterns: prev.excludePatterns.filter((_, i) => i !== index)
    }))
  }

  return (
    <div className="settings-tab">
      <div className="settings-header">
        <h3>Graph Settings</h3>
        <p>Configure dependency graph indexing and visualization settings</p>
      </div>

      <div className="settings-content">
        {/* Database Settings */}
        <div className="settings-section">
          <h4>Database Configuration</h4>
          <div className="setting-item">
            <label htmlFor="baseUrl">Base URL</label>
            <input
              id="baseUrl"
              type="text"
              value={settings.baseUrl}
              onChange={(e) => updateSetting('baseUrl', e.target.value)}
              placeholder="http://localhost:8080"
            />
            <small>URL for the graph database or Arrows server</small>
          </div>
        </div>

        {/* Indexing Settings */}
        <div className="settings-section">
          <h4>Indexing Settings</h4>
          <div className="setting-item">
            <label htmlFor="indexingDepth">Indexing Depth</label>
            <input
              id="indexingDepth"
              type="number"
              min="1"
              max="10"
              value={settings.indexingDepth}
              onChange={(e) => updateSetting('indexingDepth', parseInt(e.target.value))}
            />
            <small>Maximum depth for dependency analysis (1-10)</small>
          </div>

          <div className="setting-item checkbox">
            <input
              id="includeNodeModules"
              type="checkbox"
              checked={settings.includeNodeModules}
              onChange={(e) => updateSetting('includeNodeModules', e.target.checked)}
            />
            <label htmlFor="includeNodeModules">Include node_modules</label>
            <small>Include dependencies from node_modules in analysis</small>
          </div>
        </div>

        {/* Exclude Patterns */}
        <div className="settings-section">
          <h4>Exclude Patterns</h4>
          <div className="exclude-patterns">
            {settings.excludePatterns.map((pattern, index) => (
              <div key={index} className="pattern-item">
                <input
                  type="text"
                  value={pattern}
                  onChange={(e) => updateExcludePattern(index, e.target.value)}
                  placeholder="e.g., node_modules, .git"
                />
                <button
                  type="button"
                  onClick={() => removeExcludePattern(index)}
                  title="Remove pattern"
                  className="remove-pattern"
                >
                  <span className="codicon codicon-close" aria-hidden="true"></span>
                </button>
              </div>
            ))}
            <button
              type="button"
              onClick={addExcludePattern}
              className="add-pattern"
            >
              <span className="codicon codicon-add" aria-hidden="true"></span>
              Add Pattern
            </button>
          </div>
          <small>Patterns to exclude from dependency analysis</small>
        </div>

        {/* Visualization Settings */}
        <div className="settings-section">
          <h4>Visualization Settings</h4>
          <div className="setting-item">
            <label htmlFor="theme">Theme</label>
            <select
              id="theme"
              value={settings.visualizationTheme}
              onChange={(e) => updateSetting('visualizationTheme', e.target.value as GraphSettings['visualizationTheme'])}
            >
              <option value="auto">Auto</option>
              <option value="light">Light</option>
              <option value="dark">Dark</option>
            </select>
            <small>Color theme for graph visualization</small>
          </div>

          <div className="setting-item">
            <label htmlFor="exportQuality">Export Quality</label>
            <select
              id="exportQuality"
              value={settings.exportQuality}
              onChange={(e) => updateSetting('exportQuality', e.target.value as GraphSettings['exportQuality'])}
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
            <small>Quality setting for exported images</small>
          </div>
        </div>

        {/* Save Button */}
        <div className="settings-actions">
          <button
            className={`save-button ${saveStatus}`}
            onClick={handleSaveSettings}
            disabled={isSaving}
          >
            {isSaving ? (
              <>
                <span className="codicon codicon-loading codicon-spin" aria-hidden="true"></span>
                Saving...
              </>
            ) : saveStatus === 'saved' ? (
              <>
                <span className="codicon codicon-check" aria-hidden="true"></span>
                Saved
              </>
            ) : saveStatus === 'error' ? (
              <>
                <span className="codicon codicon-error" aria-hidden="true"></span>
                Error
              </>
            ) : (
              <>
                <span className="codicon codicon-save" aria-hidden="true"></span>
                Save Settings
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

export default SettingsTab
