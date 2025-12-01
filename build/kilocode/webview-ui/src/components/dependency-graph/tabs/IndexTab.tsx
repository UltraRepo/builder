import React, { useState, useEffect } from 'react'
import IndexStatus from '../components/IndexStatus'

declare global {
  interface Window {
    vscode?: any
  }
}

interface IndexStatus {
  projectName: string
  databaseName: string
  status: 'idle' | 'indexing' | 'completed' | 'error'
  progress: number
  message: string
  lastIndexed?: string
}

const IndexTab: React.FC = () => {
  const [indexStatus, setIndexStatus] = useState<IndexStatus>({
    projectName: 'UltraRepo',
    databaseName: 'dependency_graph',
    status: 'idle',
    progress: 0,
    message: 'Ready to index'
  })

  const [isIndexing, setIsIndexing] = useState(false)

  useEffect(() => {
    // Load current index status on mount
    loadIndexStatus()
  }, [])

  const loadIndexStatus = async () => {
    try {
      if (window.vscode) {
        window.vscode.postMessage({
          type: 'getIndexStatus',
          command: 'index'
        })
      }

      // For now, use mock status
      setIndexStatus(prev => ({
        ...prev,
        lastIndexed: new Date().toLocaleString()
      }))
    } catch (error) {
      console.error('Error loading index status:', error)
    }
  }

  const handleIndexNow = async () => {
    if (isIndexing) return

    setIsIndexing(true)
    setIndexStatus(prev => ({
      ...prev,
      status: 'indexing',
      progress: 0,
      message: 'Starting indexing process...'
    }))

    try {
      if (window.vscode) {
        window.vscode.postMessage({
          type: 'startIndexing',
          command: 'index'
        })
      }

      // Simulate indexing progress
      const progressInterval = setInterval(() => {
        setIndexStatus(prev => {
          const newProgress = Math.min(prev.progress + Math.random() * 15, 95)
          let message = 'Indexing in progress...'

          if (newProgress > 30) message = 'Analyzing dependencies...'
          if (newProgress > 60) message = 'Building graph relationships...'
          if (newProgress > 80) message = 'Finalizing index...'

          return {
            ...prev,
            progress: newProgress,
            message
          }
        })
      }, 1000)

      // Complete indexing after some time
      setTimeout(() => {
        clearInterval(progressInterval)
        setIndexStatus(prev => ({
          ...prev,
          status: 'completed',
          progress: 100,
          message: 'Indexing completed successfully',
          lastIndexed: new Date().toLocaleString()
        }))
        setIsIndexing(false)
      }, 8000)

    } catch (error) {
      console.error('Error during indexing:', error)
      setIndexStatus(prev => ({
        ...prev,
        status: 'error',
        message: 'Indexing failed: ' + (error as Error).message
      }))
      setIsIndexing(false)
    }
  }

  const handleStopIndexing = () => {
    setIsIndexing(false)
    setIndexStatus(prev => ({
      ...prev,
      status: 'idle',
      message: 'Indexing stopped by user'
    }))

    if (window.vscode) {
      window.vscode.postMessage({
        type: 'stopIndexing',
        command: 'index'
      })
    }
  }

  return (
    <div className="index-tab">
      <div className="index-header">
        <h3>Project Indexing</h3>
        <p>Index your project dependencies for graph visualization</p>
      </div>

      <div className="index-content">
        <div className="project-info">
          <div className="info-item">
            <span className="info-label">Project:</span>
            <span className="info-value">{indexStatus.projectName}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Database:</span>
            <span className="info-value">{indexStatus.databaseName}</span>
          </div>
          {indexStatus.lastIndexed && (
            <div className="info-item">
              <span className="info-label">Last Indexed:</span>
              <span className="info-value">{indexStatus.lastIndexed}</span>
            </div>
          )}
        </div>

        <IndexStatus
          status={indexStatus.status}
          progress={indexStatus.progress}
          message={indexStatus.message}
        />

        <div className="index-controls">
          {!isIndexing ? (
            <button
              className="index-button primary"
              onClick={handleIndexNow}
            >
              <span className="codicon codicon-play" aria-hidden="true"></span>
              Index Now
            </button>
          ) : (
            <button
              className="index-button secondary"
              onClick={handleStopIndexing}
            >
              <span className="codicon codicon-stop" aria-hidden="true"></span>
              Stop Indexing
            </button>
          )}

          <button
            className="index-button secondary"
            onClick={loadIndexStatus}
            title="Refresh status"
          >
            <span className="codicon codicon-refresh" aria-hidden="true"></span>
            Refresh Status
          </button>
        </div>

        <div className="index-help">
          <h4>Indexing Process</h4>
          <ul>
            <li>Analyzes all source files in your project</li>
            <li>Identifies import/export relationships</li>
            <li>Builds dependency graph data structure</li>
            <li>Stores data in local database for fast access</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default IndexTab
