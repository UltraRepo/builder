import React, { useState } from 'react'
import GraphTabs from './GraphTabs'
import ViewTab from './tabs/ViewTab'
import SearchTab from './tabs/SearchTab'
import IndexTab from './tabs/IndexTab'
import ExportTab from './tabs/ExportTab'
import SettingsTab from './tabs/SettingsTab'
import './styles/GraphView.css'

export type GraphTabType = 'view' | 'search' | 'index' | 'export' | 'settings'

declare global {
  interface Window {
    vscode?: any
  }
}

const GraphView: React.FC = () => {
  const [activeTab, setActiveTab] = useState<GraphTabType>('view')

  const handleTabChange = (tab: GraphTabType) => {
    setActiveTab(tab)
    // Persist tab state
    if (window.vscode) {
      window.vscode.setState({ activeGraphTab: tab })
    }
  }

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'view':
        return <ViewTab />
      case 'search':
        return <SearchTab />
      case 'index':
        return <IndexTab />
      case 'export':
        return <ExportTab />
      case 'settings':
        return <SettingsTab />
      default:
        return <ViewTab />
    }
  }

  return (
    <div className="graph-view">
      <div className="graph-header">
        <h1 className="graph-title">Dependency Graph</h1>
        <p className="graph-subtitle">Visualize and manage your project dependencies</p>
      </div>

      <GraphTabs activeTab={activeTab} onTabChange={handleTabChange} />

      <div className="graph-content">
        {renderActiveTab()}
      </div>
    </div>
  )
}

export default GraphView
