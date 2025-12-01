import React from 'react'

interface ExportOptionsProps {
  onExport: (format: 'svg' | 'pdf' | 'png') => void
  isExporting: boolean
}

const ExportOptions: React.FC<ExportOptionsProps> = ({ onExport, isExporting }) => {
  const exportFormats = [
    {
      format: 'svg' as const,
      title: 'SVG Export',
      description: 'Scalable vector graphics for web and print',
      icon: 'file-code',
      recommended: true
    },
    {
      format: 'pdf' as const,
      title: 'PDF Export',
      description: 'Portable document format for sharing',
      icon: 'file-pdf',
      recommended: false
    },
    {
      format: 'png' as const,
      title: 'PNG Export',
      description: 'High-quality raster image',
      icon: 'file-image',
      recommended: false
    }
  ]

  return (
    <div className="export-options">
      <h4>Choose Export Format</h4>
      <div className="format-grid">
        {exportFormats.map(({ format, title, description, icon, recommended }) => (
          <div key={format} className={`format-card ${recommended ? 'recommended' : ''}`}>
            {recommended && (
              <div className="recommended-badge">
                <span className="codicon codicon-star" aria-hidden="true"></span>
                Recommended
              </div>
            )}
            <div className="format-icon">
              <span className={`codicon codicon-${icon}`} aria-hidden="true"></span>
            </div>
            <div className="format-content">
              <h5>{title}</h5>
              <p>{description}</p>
            </div>
            <button
              className="export-format-button"
              onClick={() => onExport(format)}
              disabled={isExporting}
              title={`Export as ${format.toUpperCase()}`}
            >
              {isExporting ? (
                <>
                  <span className="codicon codicon-loading codicon-spin" aria-hidden="true"></span>
                  Exporting...
                </>
              ) : (
                <>
                  <span className="codicon codicon-export" aria-hidden="true"></span>
                  Export {format.toUpperCase()}
                </>
              )}
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}

export default ExportOptions
