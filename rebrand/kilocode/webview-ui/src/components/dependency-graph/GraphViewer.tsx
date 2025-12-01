import React, { useMemo } from "react"

type GraphViewerProps = {
  // Fully-qualified URL to the Arrows viewer html (recommended)
  // e.g. https://localhost:3000/arrows/index.html?data=/path/to/schema.json
  graphUrl?: string
  // Optional CSS class for outer container
  className?: string
  // Minimum height for the iframe area
  minHeight?: string
}

// Small, resilient GraphViewer component that shows the Arrows graph in an iframe.
// The webview environment usually injects some base URIs (e.g. window.IMAGES_BASE_URI);
// so this component attempts to build a sensible fallback URL when `graphUrl` is not provided.
export default function GraphViewer({ graphUrl, className, minHeight = "560px" }: GraphViewerProps) {
  const src = useMemo(() => {
    if (graphUrl && graphUrl.length > 0) return graphUrl

    // Try common globals injected by the extension (set in the webview HTML).
    const anyWin = window as any

    // ARROWS_BASE_URL can be set by the extension to point at the arrows viewer build.
    if (anyWin.ARROWS_BASE_URL) {
      return `${anyWin.ARROWS_BASE_URL}`
    }

    // Some webviews set IMAGES_BASE_URI or MATERIAL_ICONS_BASE_URI - use as best-effort base.
    if (anyWin.IMAGES_BASE_URI) {
      return `${anyWin.IMAGES_BASE_URI}/arrows/index.html`
    }

    // As a last resort try relative path that may work when the arrows build is copied to the extension assets.
    return `./arrows/index.html`
  }, [graphUrl])

  return (
    <div className={className} style={{ width: "100%", height: "100%", minHeight }}>
      <iframe
        title="UltraRepo Dependency Graph"
        src={src}
        style={{ width: "100%", height: "100%", border: "0", minHeight }}
        sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
      />
    </div>
  )
}
