import React, { useState, useEffect } from 'react'
import GraphViewer from '../components/GraphViewer'

declare global {
  interface Window {
    vscode?: any
  }
}

const ViewTab: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false)
  const [graphUrl, setGraphUrl] = useState<string | null>(null)

  const handleLaunchGraph = async () => {
    setIsLoading(true)

    try {
      // Request graph data from the extension
      if (window.vscode) {
        window.vscode.postMessage({
          type: 'launchGraphViewer',
          command: 'view'
        })
      }

      // For now, simulate launching Arrows app
      // In production, this would integrate with the actual Arrows server
      setTimeout(() => {
        setGraphUrl('http://localhost:8080') // Placeholder URL
        setIsLoading(false)
      }, 2000)

    } catch (error) {
      console.error('Error launching graph viewer:', error)
      setIsLoading(false)
    }
  }

  const handleRefresh = () => {
    if (window.vscode) {
      window.vscode.postMessage({
        type: 'refreshGraph',
        command: 'view'
      })
    }
  }

  return (
    <div className="view-tab">
      <div className="view-controls">
        <button
          className="launch-button"
          onClick={handleLaunchGraph}
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <span className="codicon codicon-loading codicon-spin" aria-hidden="true"></span>
              Launching Graph...
            </>
          ) : (
            <>
              <span className="codicon codicon-graph" aria-hidden="true"></span>
              Launch Arrows Graph
            </>
          )}
        </button>

        {graphUrl && (
          <button
            className="refresh-button"
            onClick={handleRefresh}
            title="Refresh Graph"
          >
            <span className="codicon codicon-refresh" aria-hidden="true"></span>
            Refresh
          </button>
        )}
      </div>

      <div className="graph-container">
        {graphUrl ? (
          <GraphViewer url={graphUrl} />
        ) : (
          <div className="graph-placeholder">
            <div className="placeholder-icon">
              <span className="codicon codicon-graph" aria-hidden="true"></span>
            </div>
            <h3>Graph Visualization</h3>
            <p>Click "Launch Arrows Graph" to view your dependency graph</p>
            <div className="placeholder-features">
              <div className="feature-item">
                <span className="codicon codicon-zoom-in" aria-hidden="true"></span>
                <span>Interactive zoom and pan</span>
              </div>
              <div className="feature-item">
                <span className="codicon codicon-info" aria-hidden="true"></span>
                <span>Node details on hover</span>
              </div>
              <div className="feature-item">
                <span className="codicon codicon-link" aria-hidden="true"></span>
                <span>Dependency relationships</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default ViewTab
