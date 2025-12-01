#!/usr/bin/env python3
"""
Qdrant Client for Repository Schema Generator

Provides utilities for interacting with Qdrant vector database,
including collection management, knowledge graph storage, and search operations.
"""

import os
import json
import hashlib
import logging
from typing import Optional, Dict, List, Any, Tuple
from pathlib import Path

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    QdrantClient = None
    models = None

logger = logging.getLogger(__name__)

class QdrantManager:
    """Manages Qdrant vector database operations for repository schemas"""

    def __init__(self, url: str = "http://localhost:6333", api_key: Optional[str] = None):
        if not QDRANT_AVAILABLE:
            raise ImportError("qdrant-client not installed. Run: pip install qdrant-client")

        self.url = url
        self.api_key = api_key
        self.client = QdrantClient(url=url, api_key=api_key)

    def generate_collection_name(self, project_name: str, workspace_path: str) -> str:
        """Generate unique collection name for CIR project"""
        if project_name and project_name.strip():
            # Use first 8 chars of hash for uniqueness
            hash_suffix = hashlib.sha256(workspace_path.encode()).hexdigest()[:8]
            return f"cir_{project_name.strip()}_{hash_suffix}"
        else:
            # Fallback to workspace-based naming
            return f"cir_ws_{hashlib.sha256(workspace_path.encode()).hexdigest()[:16]}"

    def collection_exists(self, collection_name: str) -> bool:
        """Check if collection exists"""
        try:
            self.client.get_collection(collection_name)
            return True
        except Exception:
            return False

    def find_collections_by_project(self, project_name: str) -> List[str]:
        """Find collections that match a project name pattern"""
        try:
            collections = self.client.get_collections()
            matching = []

            for collection in collections.collections:
                if collection.name.startswith(f"{project_name}_"):
                    matching.append(collection.name)

            return matching
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            return []

    def create_collection(self, collection_name: str, vector_size: int = 1536) -> bool:
        """Create a new collection with specified vector size"""
        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance.COSINE
                )
            )
            logger.info(f"Created collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create collection {collection_name}: {e}")
            return False

    def store_knowledge_graph(self, collection_name: str, file_path: str,
                             vector: List[float], knowledge_graph: Dict[str, Any],
                             metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Store knowledge graph data in Qdrant collection"""
        try:
            # Generate unique ID for the point
            point_id = hashlib.sha256(file_path.encode()).hexdigest()

            # Prepare payload with knowledge graph
            payload = {
                "filePath": file_path,
                "knowledgeGraph": knowledge_graph,
                **(metadata or {})
            }

            # Upsert point
            self.client.upsert(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=payload
                    )
                ]
            )

            logger.info(f"Stored knowledge graph for: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to store knowledge graph for {file_path}: {e}")
            return False

    def store_enhanced_knowledge_graph(self, collection_name: str, file_path: str,
                                      vector: List[float], metadata: Dict[str, Any],
                                      ai_analysis: Optional[Dict[str, Any]] = None) -> bool:
        """Store enhanced knowledge graph with AI metadata"""
        try:
            from .ai_service import get_schema
            schema = get_schema()

            # Generate unique ID for the point
            point_id = hashlib.sha256(file_path.encode()).hexdigest()

            # Create enhanced payload
            payload = schema.create_enhanced_payload(file_path, metadata, ai_analysis)

            # Validate payload before storing
            if not schema.validate_payload(payload):
                logger.error(f"Invalid payload structure for {file_path}")
                return False

            # Upsert point
            self.client.upsert(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=payload
                    )
                ]
            )

            logger.info(f"Stored enhanced knowledge graph for: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to store enhanced knowledge graph for {file_path}: {e}")
            return False

    def search_similar(self, collection_name: str, query_vector: List[float],
                      limit: int = 10, score_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Search for similar vectors in collection"""
        try:
            results = self.client.query_points(
                collection_name=collection_name,
                query=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                with_payload=True
            )

            return [
                {
                    "id": point.id,
                    "score": point.score,
                    "payload": point.payload
                }
                for point in results.points
            ]

        except Exception as e:
            logger.error(f"Search failed in collection {collection_name}: {e}")
            return []

    def search_enhanced(self, collection_name: str, query_vector: List[float],
                       filters: Optional[Dict[str, Any]] = None,
                       limit: int = 10, score_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Enhanced search with filters for AI metadata"""
        try:
            from .ai_service import get_schema
            schema = get_schema()

            # Convert filters to Qdrant format if provided
            query_filter = None
            if filters:
                query_filter = self._convert_filters_to_qdrant(filters)

            results = self.client.query_points(
                collection_name=collection_name,
                query=query_vector,
                query_filter=query_filter,
                limit=limit,
                score_threshold=score_threshold,
                with_payload=True
            )

            return [
                {
                    "id": point.id,
                    "score": point.score,
                    "payload": point.payload
                }
                for point in results.points
            ]

        except Exception as e:
            logger.error(f"Enhanced search failed in collection {collection_name}: {e}")
            return []

    def search_by_metadata(self, collection_name: str, filters: Dict[str, Any],
                          limit: int = 50) -> List[Dict[str, Any]]:
        """Search by metadata filters without vector similarity"""
        try:
            query_filter = self._convert_filters_to_qdrant(filters)

            results = self.client.query_points(
                collection_name=collection_name,
                query_filter=query_filter,
                limit=limit,
                with_payload=True
            )

            return [
                {
                    "id": point.id,
                    "score": point.score,
                    "payload": point.payload
                }
                for point in results.points
            ]

        except Exception as e:
            logger.error(f"Metadata search failed in collection {collection_name}: {e}")
            return []

    def _convert_filters_to_qdrant(self, filters: Dict[str, Any]) -> models.Filter:
        """Convert filter dict to Qdrant Filter object"""
        conditions = []

        for key, value in filters.items():
            if isinstance(value, dict):
                # Handle operators like $eq, $in, etc.
                for op, val in value.items():
                    if op == "$eq":
                        conditions.append(models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=val)
                        ))
                    elif op == "$in":
                        conditions.append(models.FieldCondition(
                            key=key,
                            match=models.MatchAny(any=val)
                        ))
            else:
                # Default to exact match
                conditions.append(models.FieldCondition(
                    key=key,
                    match=models.MatchValue(value=value)
                ))

        return models.Filter(must=conditions)

    def get_collection_info(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a collection"""
        try:
            info = self.client.get_collection(collection_name)
            return {
                "name": info.collection_name,
                "vector_size": info.config.params.vectors.size if info.config.params.vectors else None,
                "distance": str(info.config.params.vectors.distance) if info.config.params.vectors else None,
                "points_count": info.points_count,
                "status": str(info.status)
            }
        except Exception as e:
            logger.error(f"Failed to get collection info for {collection_name}: {e}")
            return None

    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection"""
        try:
            self.client.delete_collection(collection_name)
            logger.info(f"Deleted collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection {collection_name}: {e}")
            return False

    def list_all_collections(self) -> List[str]:
        """List all collections in the database"""
        try:
            collections = self.client.get_collections()
            return [col.name for col in collections.collections]
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            return []

    def validate_connection(self) -> Dict[str, Any]:
        """Validate connection to Qdrant database"""
        result = {
            "connected": False,
            "version": None,
            "collections_count": 0,
            "error": None
        }

        try:
            # Try to get collections as a connection test
            collections = self.client.get_collections()
            result["connected"] = True
            result["collections_count"] = len(collections.collections)

            # Try to get version info if available
            try:
                # This might not be available in all Qdrant versions
                health = self.client.get_health()
                result["version"] = getattr(health, 'version', None)
            except:
                pass

        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Qdrant connection validation failed: {e}")

        return result

def main():
    """CLI interface for Qdrant operations"""
    import argparse

    parser = argparse.ArgumentParser(description="Qdrant Client for Repository Schema")
    parser.add_argument("--url", default="http://localhost:6333", help="Qdrant URL")
    parser.add_argument("--api-key", help="Qdrant API key")
    parser.add_argument("--list-collections", action="store_true", help="List all collections")
    parser.add_argument("--validate", action="store_true", help="Validate connection")
    parser.add_argument("--find-project", help="Find collections for project name")

    args = parser.parse_args()

    try:
        manager = QdrantManager(args.url, args.api_key)

        if args.validate:
            result = manager.validate_connection()
            print("Connection Validation:")
            print(f"  Connected: {result['connected']}")
            print(f"  Collections: {result['collections_count']}")
            if result['version']:
                print(f"  Version: {result['version']}")
            if result['error']:
                print(f"  Error: {result['error']}")

        elif args.list_collections:
            collections = manager.list_all_collections()
            print("Collections:")
            for col in collections:
                print(f"  - {col}")

        elif args.find_project:
            collections = manager.find_collections_by_project(args.find_project)
            print(f"Collections for project '{args.find_project}':")
            for col in collections:
                print(f"  - {col}")

        else:
            print("Use --validate, --list-collections, or --find-project")

    except ImportError as e:
        print(f"Error: {e}")
        print("Install with: pip install qdrant-client")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()