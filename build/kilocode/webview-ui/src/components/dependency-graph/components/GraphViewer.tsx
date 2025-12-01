import React, { useEffect, useRef } from 'react'

interface GraphViewerProps {
  url: string
}

const GraphViewer: React.FC<GraphViewerProps> = ({ url }) => {
  const iframeRef = useRef<HTMLIFrameElement>(null)

  useEffect(() => {
    // Handle iframe communication if needed
    const handleMessage = (event: MessageEvent) => {
      // Handle messages from the iframe if necessary
      if (event.origin === new URL(url).origin) {
        console.log('Message from graph viewer:', event.data)
      }
    }

    window.addEventListener('message', handleMessage)
    return () => window.removeEventListener('message', handleMessage)
  }, [url])

  return (
    <div className="graph-viewer">
      <iframe
        ref={iframeRef}
        src={url}
        title="Dependency Graph Viewer"
        className="graph-iframe"
        sandbox="allow-scripts allow-same-origin allow-popups"
      />
    </div>
  )
}

export default GraphViewer
