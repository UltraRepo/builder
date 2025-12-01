import React, { useState, useEffect } from 'react'
import EntityList from '../components/EntityList'
import SearchField from '../components/SearchField'

declare global {
  interface Window {
    vscode?: any
  }
}

interface Entity {
  id: string
  name: string
  type: string
  dependencies: number
  dependents: number
}

const SearchTab: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [entities, setEntities] = useState<Entity[]>([])
  const [filteredEntities, setFilteredEntities] = useState<Entity[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [selectedEntity, setSelectedEntity] = useState<Entity | null>(null)

  useEffect(() => {
    // Load entities on component mount
    loadEntities()
  }, [])

  useEffect(() => {
    // Filter entities based on search query
    if (searchQuery.trim() === '') {
      setFilteredEntities(entities)
    } else {
      const filtered = entities.filter(entity =>
        entity.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        entity.type.toLowerCase().includes(searchQuery.toLowerCase())
      )
      setFilteredEntities(filtered)
    }
  }, [searchQuery, entities])

  const loadEntities = async () => {
    setIsLoading(true)
    try {
      // Request entities from the extension
      if (window.vscode) {
        window.vscode.postMessage({
          type: 'getGraphEntities',
          command: 'search'
        })
      }

      // For now, use mock data
      const mockEntities: Entity[] = [
        { id: '1', name: 'main.py', type: 'file', dependencies: 5, dependents: 2 },
        { id: '2', name: 'utils.py', type: 'file', dependencies: 2, dependents: 8 },
        { id: '3', name: 'config.py', type: 'file', dependencies: 1, dependents: 6 },
        { id: '4', name: 'models/', type: 'directory', dependencies: 3, dependents: 4 },
        { id: '5', name: 'views/', type: 'directory', dependencies: 7, dependents: 1 }
      ]

      setEntities(mockEntities)
      setFilteredEntities(mockEntities)
    } catch (error) {
      console.error('Error loading entities:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSimilaritySearch = async (entityName: string) => {
    setIsLoading(true)
    try {
      if (window.vscode) {
        window.vscode.postMessage({
          type: 'similaritySearch',
          entityName,
          command: 'search'
        })
      }

      // For now, just filter by similar names
      const similar = entities.filter(entity =>
        entity.name.toLowerCase().includes(entityName.toLowerCase().slice(0, 3))
      )
      setFilteredEntities(similar)
    } catch (error) {
      console.error('Error performing similarity search:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleEntitySelect = (entity: Entity) => {
    setSelectedEntity(entity)
    if (window.vscode) {
      window.vscode.postMessage({
        type: 'selectEntity',
        entityId: entity.id,
        command: 'search'
      })
    }
  }

  return (
    <div className="search-tab">
      <div className="search-controls">
        <SearchField
          value={searchQuery}
          onChange={setSearchQuery}
          onSimilaritySearch={handleSimilaritySearch}
          placeholder="Search modules, files, or directories..."
        />
        <button
          className="refresh-button"
          onClick={loadEntities}
          disabled={isLoading}
          title="Refresh entity list"
        >
          <span className="codicon codicon-refresh" aria-hidden="true"></span>
          Refresh
        </button>
      </div>

      <div className="search-content">
        <div className="entity-section">
          <h3>Graph Entities ({filteredEntities.length})</h3>
          <EntityList
            entities={filteredEntities}
            onEntitySelect={handleEntitySelect}
            selectedEntity={selectedEntity}
            isLoading={isLoading}
          />
        </div>

        {selectedEntity && (
          <div className="entity-details">
            <h3>Entity Details</h3>
            <div className="details-content">
              <div className="detail-item">
                <span className="detail-label">Name:</span>
                <span className="detail-value">{selectedEntity.name}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Type:</span>
                <span className="detail-value">{selectedEntity.type}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Dependencies:</span>
                <span className="detail-value">{selectedEntity.dependencies}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Dependents:</span>
                <span className="detail-value">{selectedEntity.dependents}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default SearchTab
