import React, { useState } from 'react'

interface SearchFieldProps {
  value: string
  onChange: (value: string) => void
  onSimilaritySearch: (query: string) => void
  placeholder?: string
}

const SearchField: React.FC<SearchFieldProps> = ({
  value,
  onChange,
  onSimilaritySearch,
  placeholder = "Search..."
}) => {
  const [isSimilarityMode, setIsSimilarityMode] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (isSimilarityMode && value.trim()) {
      onSimilaritySearch(value.trim())
    }
  }

  const toggleSimilarityMode = () => {
    setIsSimilarityMode(!isSimilarityMode)
  }

  return (
    <div className="search-field-container">
      <form onSubmit={handleSubmit} className="search-form">
        <div className="search-input-wrapper">
          <span className="search-icon codicon codicon-search" aria-hidden="true"></span>
          <input
            type="text"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={placeholder}
            className="search-input"
          />
          <button
            type="button"
            onClick={toggleSimilarityMode}
            className={`similarity-toggle ${isSimilarityMode ? 'active' : ''}`}
            title={isSimilarityMode ? "Switch to regular search" : "Switch to similarity search"}
          >
            <span className="codicon codicon-lightbulb" aria-hidden="true"></span>
          </button>
        </div>

        {isSimilarityMode && (
          <button type="submit" className="similarity-search-button">
            <span className="codicon codicon-search-view-icon" aria-hidden="true"></span>
            Similarity Search
          </button>
        )}
      </form>

      {isSimilarityMode && (
        <div className="similarity-help">
          <small>
            Similarity search finds entities with similar names or relationships.
            Enter a partial name to find related modules.
          </small>
        </div>
      )}
    </div>
  )
}

export default SearchField
