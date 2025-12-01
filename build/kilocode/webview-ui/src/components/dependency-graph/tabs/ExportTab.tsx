import React, { useState } from 'react'
import ExportOptions from '../components/ExportOptions'

declare global {
  interface Window {
    vscode?: any
  }
}

interface ExportJob {
  id: string
  format: 'svg' | 'pdf' | 'png'
  status: 'pending' | 'processing' | 'completed' | 'error'
  progress: number
  filename?: string
  error?: string
}

const ExportTab: React.FC = () => {
  const [exportJobs, setExportJobs] = useState<ExportJob[]>([])
  const [isExporting, setIsExporting] = useState(false)

  const handleExport = async (format: 'svg' | 'pdf' | 'png') => {
    if (isExporting) return

    const jobId = Date.now().toString()
    const newJob: ExportJob = {
      id: jobId,
      format,
      status: 'pending',
      progress: 0
    }

    setExportJobs(prev => [...prev, newJob])
    setIsExporting(true)

    try {
      if (window.vscode) {
        window.vscode.postMessage({
          type: 'exportGraph',
          format,
          jobId,
          command: 'export'
        })
      }

      // Simulate export progress
      const progressInterval = setInterval(() => {
        setExportJobs(prev => prev.map(job => {
          if (job.id === jobId) {
            const newProgress = Math.min(job.progress + Math.random() * 20, 95)
            let status: ExportJob['status'] = 'processing'

            if (newProgress >= 95) {
              status = 'completed'
              clearInterval(progressInterval)
              setIsExporting(false)
            }

            return {
              ...job,
              progress: newProgress,
              status,
              filename: status === 'completed' ? `dependency-graph.${format}` : undefined
            }
          }
          return job
        }))
      }, 800)

    } catch (error) {
      console.error('Export error:', error)
      setExportJobs(prev => prev.map(job =>
        job.id === jobId
          ? { ...job, status: 'error', error: (error as Error).message }
          : job
      ))
      setIsExporting(false)
    }
  }

  const handleDownload = (job: ExportJob) => {
    if (job.filename && window.vscode) {
      window.vscode.postMessage({
        type: 'downloadExport',
        filename: job.filename,
        jobId: job.id,
        command: 'export'
      })
    }
  }

  const clearCompletedJobs = () => {
    setExportJobs(prev => prev.filter(job => job.status !== 'completed'))
  }

  return (
    <div className="export-tab">
      <div className="export-header">
        <h3>Export Graph</h3>
        <p>Export your dependency graph in various formats</p>
      </div>

      <div className="export-content">
        <ExportOptions
          onExport={handleExport}
          isExporting={isExporting}
        />

        {exportJobs.length > 0 && (
          <div className="export-jobs">
            <div className="jobs-header">
              <h4>Export Jobs</h4>
              <button
                className="clear-button"
                onClick={clearCompletedJobs}
                title="Clear completed jobs"
              >
                <span className="codicon codicon-clear-all" aria-hidden="true"></span>
                Clear Completed
              </button>
            </div>

            <div className="jobs-list">
              {exportJobs.map((job) => (
                <div key={job.id} className={`job-item status-${job.status}`}>
                  <div className="job-info">
                    <div className="job-format">
                      <span className={`format-icon codicon codicon-file-${
                        job.format === 'svg' ? 'code' :
                        job.format === 'pdf' ? 'pdf' :
                        'image'
                      }`} aria-hidden="true"></span>
                      <span className="format-text">{job.format.toUpperCase()}</span>
                    </div>
                    <div className="job-status">
                      {job.status === 'pending' && (
                        <span className="status-text">Queued</span>
                      )}
                      {job.status === 'processing' && (
                        <>
                          <span className="status-text">Processing</span>
                          <div className="job-progress">
                            <div
                              className="progress-fill"
                              style={{ width: `${job.progress}%` }}
                            ></div>
                          </div>
                          <span className="progress-text">{Math.round(job.progress)}%</span>
                        </>
                      )}
                      {job.status === 'completed' && (
                        <>
                          <span className="status-text success">Completed</span>
                          <button
                            className="download-button"
                            onClick={() => handleDownload(job)}
                            title="Download file"
                          >
                            <span className="codicon codicon-cloud-download" aria-hidden="true"></span>
                            Download
                          </button>
                        </>
                      )}
                      {job.status === 'error' && (
                        <>
                          <span className="status-text error">Error</span>
                          <span className="error-message">{job.error}</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="export-help">
          <h4>Supported Formats</h4>
          <div className="format-info">
            <div className="format-item">
              <span className="codicon codicon-file-code" aria-hidden="true"></span>
              <div className="format-details">
                <strong>SVG</strong>
                <p>Scalable vector format, perfect for web and print</p>
              </div>
            </div>
            <div className="format-item">
              <span className="codicon codicon-file-pdf" aria-hidden="true"></span>
              <div className="format-details">
                <strong>PDF</strong>
                <p>Portable document format for sharing and printing</p>
              </div>
            </div>
            <div className="format-item">
              <span className="codicon codicon-file-image" aria-hidden="true"></span>
              <div className="format-details">
                <strong>PNG</strong>
                <p>Raster image format for presentations and documentation</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ExportTab
