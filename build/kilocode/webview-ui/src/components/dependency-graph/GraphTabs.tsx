import React from 'react'
import { GraphTabType } from './GraphView'
import './styles/tabs.css'

interface GraphTabsProps {
  activeTab: GraphTabType
  onTabChange: (tab: GraphTabType) => void
}

const GraphTabs: React.FC<GraphTabsProps> = ({ activeTab, onTabChange }) => {
  const tabs: { id: GraphTabType; label: string; icon: string }[] = [
    { id: 'view', label: 'View', icon: 'eye' },
    { id: 'search', label: 'Search', icon: 'search' },
    { id: 'index', label: 'Index', icon: 'database' },
    { id: 'export', label: 'Export', icon: 'export' },
    { id: 'settings', label: 'Settings', icon: 'settings-gear' }
  ]

  return (
    <div className="graph-tabs">
      <div className="tabs-container">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => onTabChange(tab.id)}
            aria-label={tab.label}
          >
            <span className={`codicon codicon-${tab.icon}`} aria-hidden="true"></span>
            <span className="tab-label">{tab.label}</span>
          </button>
        ))}
      </div>
    </div>
  )
}

export default GraphTabs
