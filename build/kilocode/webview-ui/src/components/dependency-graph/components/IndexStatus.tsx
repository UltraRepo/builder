import React from 'react'

interface IndexStatusProps {
  status: 'idle' | 'indexing' | 'completed' | 'error'
  progress: number
  message: string
}

const IndexStatus: React.FC<IndexStatusProps> = ({ status, progress, message }) => {
  const getStatusIcon = () => {
    switch (status) {
      case 'idle':
        return 'circle-outline'
      case 'indexing':
        return 'loading'
      case 'completed':
        return 'check'
      case 'error':
        return 'error'
      default:
        return 'circle-outline'
    }
  }

  const getStatusColor = () => {
    switch (status) {
      case 'idle':
        return 'neutral'
      case 'indexing':
        return 'info'
      case 'completed':
        return 'success'
      case 'error':
        return 'error'
      default:
        return 'neutral'
    }
  }

  return (
    <div className={`index-status status-${getStatusColor()}`}>
      <div className="status-header">
        <span className={`status-icon codicon codicon-${getStatusIcon()} ${
          status === 'indexing' ? 'codicon-spin' : ''
        }`} aria-hidden="true"></span>
        <span className="status-text">
          {status === 'idle' && 'Ready'}
          {status === 'indexing' && 'Indexing'}
          {status === 'completed' && 'Completed'}
          {status === 'error' && 'Error'}
        </span>
      </div>

      <div className="status-message">{message}</div>

      {status === 'indexing' && (
        <div className="progress-container">
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <span className="progress-text">{Math.round(progress)}%</span>
        </div>
      )}

      {status === 'completed' && (
        <div className="status-success">
          <span className="codicon codicon-check-all" aria-hidden="true"></span>
          Project indexing completed successfully
        </div>
      )}

      {status === 'error' && (
        <div className="status-error">
          <span className="codicon codicon-error" aria-hidden="true"></span>
          An error occurred during indexing. Please check the logs.
        </div>
      )}
    </div>
  )
}

export default IndexStatus
