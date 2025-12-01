import React from 'react'

interface Entity {
  id: string
  name: string
  type: string
  dependencies: number
  dependents: number
}

interface EntityListProps {
  entities: Entity[]
  onEntitySelect: (entity: Entity) => void
  selectedEntity: Entity | null
  isLoading: boolean
}

const EntityList: React.FC<EntityListProps> = ({
  entities,
  onEntitySelect,
  selectedEntity,
  isLoading
}) => {
  if (isLoading) {
    return (
      <div className="entity-list-loading">
        <div className="loading-spinner">
          <span className="codicon codicon-loading codicon-spin" aria-hidden="true"></span>
          Loading entities...
        </div>
      </div>
    )
  }

  if (entities.length === 0) {
    return (
      <div className="entity-list-empty">
        <span className="codicon codicon-search" aria-hidden="true"></span>
        <p>No entities found</p>
      </div>
    )
  }

  return (
    <div className="entity-list">
      {entities.map((entity) => (
        <div
          key={entity.id}
          className={`entity-item ${selectedEntity?.id === entity.id ? 'selected' : ''}`}
          onClick={() => onEntitySelect(entity)}
        >
          <div className="entity-icon">
            <span
              className={`codicon ${
                entity.type === 'file' ? 'codicon-file' :
                entity.type === 'directory' ? 'codicon-folder' :
                'codicon-symbol-class'
              }`}
              aria-hidden="true"
            ></span>
          </div>
          <div className="entity-info">
            <div className="entity-name">{entity.name}</div>
            <div className="entity-meta">
              <span className="entity-type">{entity.type}</span>
              <span className="entity-stats">
                {entity.dependencies} deps • {entity.dependents} deps on
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

export default EntityList
