#!/usr/bin/env python3
"""
AI Service Architecture for Repository Schema Generator

This module provides a modular AI service layer that supports:
- Multiple LLM providers (OpenAI, Anthropic, local models)
- Knowledge graph size optimization (< 250KB)
- Enhanced Qdrant schema with AI metadata
- Async processing for scalability
"""

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class AIServiceConfig:
    """Configuration for AI service operations"""
    provider: str = "openai"
    model: str = "gpt-3.5-turbo"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: int = 4000
    temperature: float = 0.3
    timeout: int = 30
    max_retries: int = 3
    rate_limit_delay: float = 1.0

@dataclass
class CodeAnalysisRequest:
    """Request structure for code analysis"""
    file_path: str
    content: str
    language: str
    metadata: Dict[str, Any]
    analysis_type: str = "comprehensive"  # basic, comprehensive, security

@dataclass
class CodeAnalysisResponse:
    """Response structure for code analysis"""
    file_path: str
    success: bool
    analysis: Dict[str, Any]
    tokens_used: int = 0
    processing_time: float = 0.0
    error: Optional[str] = None

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    @abstractmethod
    async def analyze_code(self, request: CodeAnalysisRequest, config: AIServiceConfig) -> CodeAnalysisResponse:
        """Analyze code using the LLM provider"""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get provider name"""
        pass

    @abstractmethod
    def validate_config(self, config: AIServiceConfig) -> bool:
        """Validate provider-specific configuration"""
        pass

class OpenAIProvider(LLMProvider):
    """OpenAI-compatible LLM provider"""

    def get_provider_name(self) -> str:
        return "openai"

    def validate_config(self, config: AIServiceConfig) -> bool:
        return bool(config.api_key)

    async def analyze_code(self, request: CodeAnalysisRequest, config: AIServiceConfig) -> CodeAnalysisResponse:
        """Analyze code using OpenAI-compatible API"""
        start_time = time.time()

        try:
            # Import here to avoid dependency issues
            import aiohttp

            headers = {
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json"
            }

            # Build prompt based on analysis type
            prompt = self._build_analysis_prompt(request)

            payload = {
                "model": config.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": config.max_tokens,
                "temperature": config.temperature
            }

            base_url = config.base_url or "https://api.openai.com/v1"
            url = f"{base_url}/chat/completions"

            async with aiohttp.ClientSession() as session:
                for attempt in range(config.max_retries):
                    try:
                        async with session.post(url, headers=headers, json=payload, timeout=config.timeout) as response:
                            if response.status == 200:
                                result = await response.json()
                                analysis = self._parse_response(result, request.analysis_type)
                                processing_time = time.time() - start_time

                                return CodeAnalysisResponse(
                                    file_path=request.file_path,
                                    success=True,
                                    analysis=analysis,
                                    tokens_used=result.get("usage", {}).get("total_tokens", 0),
                                    processing_time=processing_time
                                )
                            else:
                                error_text = await response.text()
                                logger.warning(f"API error (attempt {attempt + 1}): {response.status} - {error_text}")

                    except asyncio.TimeoutError:
                        logger.warning(f"Timeout on attempt {attempt + 1}")

                    if attempt < config.max_retries - 1:
                        await asyncio.sleep(config.rate_limit_delay * (attempt + 1))

                return CodeAnalysisResponse(
                    file_path=request.file_path,
                    success=False,
                    analysis={},
                    error="Max retries exceeded"
                )

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Analysis failed for {request.file_path}: {e}")
            return CodeAnalysisResponse(
                file_path=request.file_path,
                success=False,
                analysis={},
                processing_time=processing_time,
                error=str(e)
            )

class AnthropicProvider(LLMProvider):
    """Anthropic Claude LLM provider"""

    def get_provider_name(self) -> str:
        return "anthropic"

    def validate_config(self, config: AIServiceConfig) -> bool:
        return bool(config.api_key)

    async def analyze_code(self, request: CodeAnalysisRequest, config: AIServiceConfig) -> CodeAnalysisResponse:
        """Analyze code using Anthropic Claude API"""
        start_time = time.time()

        try:
            import aiohttp

            headers = {
                "x-api-key": config.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }

            prompt = self._build_analysis_prompt(request)

            payload = {
                "model": config.model,
                "max_tokens": config.max_tokens,
                "temperature": config.temperature,
                "messages": [{"role": "user", "content": prompt}]
            }

            base_url = config.base_url or "https://api.anthropic.com"
            url = f"{base_url}/v1/messages"

            async with aiohttp.ClientSession() as session:
                for attempt in range(config.max_retries):
                    try:
                        async with session.post(url, headers=headers, json=payload, timeout=config.timeout) as response:
                            if response.status == 200:
                                result = await response.json()
                                analysis = self._parse_response(result, request.analysis_type)
                                processing_time = time.time() - start_time

                                return CodeAnalysisResponse(
                                    file_path=request.file_path,
                                    success=True,
                                    analysis=analysis,
                                    tokens_used=result.get("usage", {}).get("input_tokens", 0) + result.get("usage", {}).get("output_tokens", 0),
                                    processing_time=processing_time
                                )
                            else:
                                error_text = await response.text()
                                logger.warning(f"Anthropic API error (attempt {attempt + 1}): {response.status} - {error_text}")

                    except asyncio.TimeoutError:
                        logger.warning(f"Timeout on attempt {attempt + 1}")

                    if attempt < config.max_retries - 1:
                        await asyncio.sleep(config.rate_limit_delay * (attempt + 1))

                return CodeAnalysisResponse(
                    file_path=request.file_path,
                    success=False,
                    analysis={},
                    error="Max retries exceeded"
                )

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Anthropic analysis failed for {request.file_path}: {e}")
            return CodeAnalysisResponse(
                file_path=request.file_path,
                success=False,
                analysis={},
                processing_time=processing_time,
                error=str(e)
            )

    def _build_analysis_prompt(self, request: CodeAnalysisRequest) -> str:
        """Build Anthropic-specific analysis prompt"""
        return OpenAIProvider()._build_analysis_prompt(request)  # Reuse OpenAI prompt structure

    def _parse_response(self, api_response: Dict, analysis_type: str) -> Dict[str, Any]:
        """Parse Anthropic response"""
        try:
            content = api_response["content"][0]["text"]
            # Extract JSON from response (similar to OpenAI)
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_content = content[json_start:json_end]
                return json.loads(json_content)
            else:
                return {"purpose": content[:200], "complexity": "unknown"}
        except Exception as e:
            logger.warning(f"Failed to parse Anthropic response: {e}")
            return {"purpose": "Analysis failed", "complexity": "unknown"}

class LocalProvider(LLMProvider):
    """Local LLM provider for offline analysis"""

    def get_provider_name(self) -> str:
        return "local"

    def validate_config(self, config: AIServiceConfig) -> bool:
        # Local models might not need API keys
        return True

    async def analyze_code(self, request: CodeAnalysisRequest, config: AIServiceConfig) -> CodeAnalysisResponse:
        """Analyze code using local LLM (placeholder for future implementation)"""
        start_time = time.time()

        # For now, return basic analysis without external API calls
        # Future: Integrate with local models like Ollama, LM Studio, etc.

        try:
            # Basic fallback analysis
            analysis = {
                "purpose": f"Local analysis of {request.language} file",
                "complexity": "unknown",
                "main_function": "Not determined",
                "dependencies": [],
                "patterns": [],
                "quality_score": 5
            }

            processing_time = time.time() - start_time

            return CodeAnalysisResponse(
                file_path=request.file_path,
                success=True,
                analysis=analysis,
                tokens_used=0,  # Local, no token counting
                processing_time=processing_time
            )

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Local analysis failed for {request.file_path}: {e}")
            return CodeAnalysisResponse(
                file_path=request.file_path,
                success=False,
                analysis={},
                processing_time=processing_time,
                error=str(e)
            )

    def _build_analysis_prompt(self, request: CodeAnalysisRequest) -> str:
        """Build analysis prompt based on request type"""
        base_prompt = f"""
Analyze the following {request.language} code file and provide a structured analysis:

File: {request.file_path}
Language: {request.language}

Code:
{request.content[:4000]}  # Limit content for token efficiency

Please provide analysis in the following JSON format:
{{
    "purpose": "Brief description of what this code does",
    "complexity": "low|medium|high",
    "main_function": "Primary function or entry point",
    "dependencies": ["list", "of", "imports"],
    "patterns": ["architectural", "patterns", "used"],
    "quality_score": 1-10
}}

Focus on being concise while providing actionable insights.
"""

        if request.analysis_type == "security":
            base_prompt += """
Additional security analysis:
{
    "security_issues": ["potential", "issues"],
    "input_validation": "present|missing|partial",
    "authentication": "required|optional|none",
    "data_sensitivity": "low|medium|high"
}
"""

        return base_prompt

    def _parse_response(self, api_response: Dict, analysis_type: str) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        try:
            content = api_response["choices"][0]["message"]["content"]
            # Extract JSON from response
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_content = content[json_start:json_end]
                return json.loads(json_content)
            else:
                return {"purpose": content[:200], "complexity": "unknown"}
        except Exception as e:
            logger.warning(f"Failed to parse response: {e}")
            return {"purpose": "Analysis failed", "complexity": "unknown"}

class ProviderFactory:
    """Factory for creating LLM providers"""

    @staticmethod
    def create_provider(provider_name: str) -> Optional[LLMProvider]:
        """Create provider instance by name"""
        providers = {
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider,
            "local": LocalProvider
        }

        provider_class = providers.get(provider_name.lower())
        if provider_class:
            return provider_class()
        return None

    @staticmethod
    def get_available_providers() -> List[str]:
        """Get list of available provider names"""
        return ["openai", "anthropic", "local"]

    @staticmethod
    def get_provider_config_template(provider_name: str) -> Dict[str, Any]:
        """Get configuration template for a provider"""
        templates = {
            "openai": {
                "model": "gpt-3.5-turbo",
                "base_url": "https://api.openai.com/v1",
                "max_tokens": 4000,
                "temperature": 0.3
            },
            "anthropic": {
                "model": "claude-3-sonnet-20240229",
                "base_url": "https://api.anthropic.com",
                "max_tokens": 4000,
                "temperature": 0.3
            },
            "local": {
                "model": "local-model",
                "base_url": None,
                "max_tokens": 4000,
                "temperature": 0.3
            }
        }
        return templates.get(provider_name.lower(), {})

class AIService:
    """Main AI service orchestrator"""

    def __init__(self, config: AIServiceConfig):
        self.config = config
        self.providers: Dict[str, LLMProvider] = {}
        self._register_providers()

    def _register_providers(self):
        """Register available LLM providers"""
        self.providers["openai"] = OpenAIProvider()
        self.providers["anthropic"] = AnthropicProvider()
        self.providers["local"] = LocalProvider()
        # Future: Add more providers as needed

    def get_provider(self, provider_name: str) -> Optional[LLMProvider]:
        """Get LLM provider by name"""
        return self.providers.get(provider_name)

    async def analyze_file(self, request: CodeAnalysisRequest) -> CodeAnalysisResponse:
        """Analyze a single file"""
        provider = self.get_provider(self.config.provider)
        if not provider:
            return CodeAnalysisResponse(
                file_path=request.file_path,
                success=False,
                analysis={},
                error=f"Provider {self.config.provider} not available"
            )

        if not provider.validate_config(self.config):
            return CodeAnalysisResponse(
                file_path=request.file_path,
                success=False,
                analysis={},
                error=f"Invalid configuration for provider {self.config.provider}"
            )

        return await provider.analyze_code(request, self.config)

    async def analyze_batch(self, requests: List[CodeAnalysisRequest],
                          concurrency: int = 3) -> List[CodeAnalysisResponse]:
        """Analyze multiple files concurrently"""
        semaphore = asyncio.Semaphore(concurrency)

        async def analyze_with_semaphore(request):
            async with semaphore:
                return await self.analyze_file(request)

        tasks = [analyze_with_semaphore(req) for req in requests]
        return await asyncio.gather(*tasks, return_exceptions=True)

class KnowledgeGraphOptimizer:
    """Optimizes knowledge graphs for size and efficiency"""

    def __init__(self, max_size_kb: int = 250):
        self.max_size_kb = max_size_kb

    def optimize_graph(self, graph: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize knowledge graph size"""
        # Remove unnecessary fields
        optimized = self._remove_redundant_fields(graph)

        # Compress text fields
        optimized = self._compress_text_fields(optimized)

        # Prioritize important information
        optimized = self._prioritize_content(optimized)

        # Final size check and truncation if needed
        optimized = self._ensure_size_limit(optimized)

        return optimized

    def _remove_redundant_fields(self, graph: Dict[str, Any]) -> Dict[str, Any]:
        """Remove fields that don't add value"""
        optimized = json.loads(json.dumps(graph))  # Deep copy

        # Remove empty or null values
        def clean_dict(d):
            if not isinstance(d, dict):
                return d
            return {k: clean_dict(v) for k, v in d.items()
                   if v is not None and v != "" and v != []}

        optimized = clean_dict(optimized)

        # Remove redundant metadata that's already in file system
        if "files" in optimized:
            for file_info in optimized["files"]:
                if "metadata" in file_info:
                    metadata = file_info["metadata"]
                    # Remove redundant size info if we have file stats
                    if "size_bytes" in metadata and metadata.get("size_bytes") == 0:
                        del metadata["size_bytes"]

        return optimized

    def _compress_text_fields(self, graph: Dict[str, Any]) -> Dict[str, Any]:
        """Compress long text fields"""
        optimized = json.loads(json.dumps(graph))  # Deep copy

        def compress_text(obj, max_length: int = 500):
            if isinstance(obj, str) and len(obj) > max_length:
                # Truncate and add ellipsis
                return obj[:max_length - 3] + "..."
            elif isinstance(obj, dict):
                return {k: compress_text(v, max_length) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [compress_text(item, max_length) for item in obj]
            return obj

        return compress_text(optimized)

    def _prioritize_content(self, graph: Dict[str, Any]) -> Dict[str, Any]:
        """Prioritize most important content"""
        optimized = json.loads(json.dumps(graph))  # Deep copy

        if "files" in optimized:
            # Sort files by importance (code files first, then docs, then others)
            def get_file_priority(file_info):
                path = file_info.get("path", "").lower()
                if any(ext in path for ext in [".py", ".js", ".ts", ".java", ".cpp", ".c"]):
                    return 0  # Highest priority
                elif any(ext in path for ext in [".md", ".txt", ".rst"]):
                    return 1  # Documentation
                elif any(ext in path for ext in [".json", ".yaml", ".yml", ".xml"]):
                    return 2  # Config files
                else:
                    return 3  # Other files

            optimized["files"].sort(key=get_file_priority)

            # Limit the number of files if still too large
            max_files = 1000  # Reasonable limit
            if len(optimized["files"]) > max_files:
                optimized["files"] = optimized["files"][:max_files]

        return optimized

    def _ensure_size_limit(self, graph: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure final graph is within size limits"""
        current_size = len(json.dumps(graph).encode('utf-8')) / 1024  # KB

        if current_size <= self.max_size_kb:
            return graph

        # If still too large, progressively remove less important data
        optimized = json.loads(json.dumps(graph))  # Deep copy

        # Remove code summaries first (can be regenerated)
        if "files" in optimized:
            for file_info in optimized["files"]:
                if "metadata" in file_info and "code_summary" in file_info["metadata"]:
                    del file_info["metadata"]["code_summary"]

        # Check size again
        current_size = len(json.dumps(optimized).encode('utf-8')) / 1024
        if current_size <= self.max_size_kb:
            return optimized

        # If still too large, remove extracted descriptions
        if "files" in optimized:
            for file_info in optimized["files"]:
                if "metadata" in file_info and "extracted_description" in file_info["metadata"]:
                    del file_info["metadata"]["extracted_description"]

        return optimized

    def validate_size(self, graph: Dict[str, Any]) -> bool:
        """Validate that graph size is within limits"""
        size_bytes = len(json.dumps(graph).encode('utf-8'))
        size_kb = size_bytes / 1024
        return size_kb <= self.max_size_kb

    def get_size_stats(self, graph: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed size statistics"""
        size_bytes = len(json.dumps(graph).encode('utf-8'))
        size_kb = size_bytes / 1024

        stats = {
            "total_size_kb": round(size_kb, 2),
            "within_limit": size_kb <= self.max_size_kb,
            "limit_kb": self.max_size_kb
        }

        if "files" in graph:
            stats["file_count"] = len(graph["files"])

        return stats

class EnhancedQdrantSchema:
    """Enhanced Qdrant schema with AI metadata support"""

    def __init__(self):
        self.schema_version = "2.0"
        self.ai_metadata_fields = [
            "semantic_purpose",
            "complexity_score",
            "security_analysis",
            "api_endpoints",
            "dependency_graph",
            "maintainability_index",
            "code_patterns",
            "error_patterns",
            "test_coverage"
        ]

    def create_enhanced_payload(self, file_path: str, metadata: Dict[str, Any],
                              ai_analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create enhanced payload with AI metadata"""
        payload = {
            "filePath": file_path,
            "schemaVersion": self.schema_version,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata,
            "aiEnhanced": ai_analysis is not None,
            "indexable": True  # Flag for search indexing
        }

        if ai_analysis:
            # Structure AI analysis for better searchability
            payload["aiAnalysis"] = self._structure_ai_analysis(ai_analysis)

        # Add searchable tags
        payload["tags"] = self._generate_search_tags(metadata, ai_analysis)

        return payload

    def _structure_ai_analysis(self, ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Structure AI analysis for optimal storage and search"""
        structured = {}

        # Core analysis fields
        structured["purpose"] = ai_analysis.get("purpose", "")
        structured["complexity"] = ai_analysis.get("complexity", "unknown")
        structured["quality_score"] = ai_analysis.get("quality_score", 5)

        # Dependencies and relationships
        structured["dependencies"] = ai_analysis.get("dependencies", [])
        structured["imports"] = ai_analysis.get("imports", [])

        # Advanced analysis
        if "api_endpoints" in ai_analysis:
            structured["api_endpoints"] = ai_analysis["api_endpoints"]
        if "security_issues" in ai_analysis:
            structured["security_issues"] = ai_analysis["security_issues"]
        if "patterns" in ai_analysis:
            structured["patterns"] = ai_analysis["patterns"]

        return structured

    def _generate_search_tags(self, metadata: Dict[str, Any],
                            ai_analysis: Optional[Dict[str, Any]] = None) -> List[str]:
        """Generate searchable tags for the file"""
        tags = []

        # Basic metadata tags
        if metadata.get("type"):
            tags.append(f"type:{metadata['type']}")
        if metadata.get("ai_description"):
            # Extract key terms from description
            desc = metadata["ai_description"].lower()
            if "python" in desc:
                tags.append("language:python")
            if "javascript" in desc:
                tags.append("language:javascript")
            if "config" in desc:
                tags.append("category:config")

        # AI analysis tags
        if ai_analysis:
            if ai_analysis.get("complexity"):
                tags.append(f"complexity:{ai_analysis['complexity']}")
            if ai_analysis.get("purpose"):
                purpose = ai_analysis["purpose"].lower()
                if "api" in purpose:
                    tags.append("category:api")
                if "test" in purpose:
                    tags.append("category:test")
                if "util" in purpose or "helper" in purpose:
                    tags.append("category:utility")

        return tags

    def get_vector_size(self) -> int:
        """Get recommended vector size for AI-enhanced content"""
        return 1536  # Standard for OpenAI embeddings

    def get_collection_config(self) -> Dict[str, Any]:
        """Get Qdrant collection configuration with enhanced indexing"""
        return {
            "vectors": {
                "size": self.get_vector_size(),
                "distance": "Cosine"
            },
            "optimizers_config": {
                "default_segment_number": 2,
                "indexing_threshold": 10000
            },
            "quantization_config": {
                "scalar": {
                    "type": "int8",
                    "quantile": 0.99,
                    "always_ram": True
                }
            }
        }

    def create_search_filters(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """Create Qdrant search filters from query parameters"""
        filters = {}

        if "language" in query_params:
            filters["metadata.type"] = {"$eq": query_params["language"]}

        if "complexity" in query_params:
            filters["aiAnalysis.complexity"] = {"$eq": query_params["complexity"]}

        if "tags" in query_params:
            # Search for files with specific tags
            tag_filters = []
            for tag in query_params["tags"]:
                tag_filters.append({"tags": {"$in": [tag]}})
            if tag_filters:
                filters["$or"] = tag_filters

        return filters

    def validate_payload(self, payload: Dict[str, Any]) -> bool:
        """Validate payload structure"""
        required_fields = ["filePath", "schemaVersion", "metadata"]
        for field in required_fields:
            if field not in payload:
                return False

        # Validate AI analysis structure if present
        if payload.get("aiEnhanced") and "aiAnalysis" in payload:
            ai_analysis = payload["aiAnalysis"]
            if not isinstance(ai_analysis, dict):
                return False

        return True

# Global service instances
_ai_service: Optional[AIService] = None
_optimizer: Optional[KnowledgeGraphOptimizer] = None
_schema: Optional[EnhancedQdrantSchema] = None

def get_ai_service(config: Optional[AIServiceConfig] = None) -> AIService:
    """Get or create AI service instance"""
    global _ai_service
    if _ai_service is None:
        if config is None:
            config = AIServiceConfig()
        _ai_service = AIService(config)
    return _ai_service

def get_optimizer() -> KnowledgeGraphOptimizer:
    """Get or create optimizer instance"""
    global _optimizer
    if _optimizer is None:
        _optimizer = KnowledgeGraphOptimizer()
    return _optimizer

def get_schema() -> EnhancedQdrantSchema:
    """Get or create schema instance"""
    global _schema
    if _schema is None:
        _schema = EnhancedQdrantSchema()
    return _schema

# CLI interface for testing
async def main():
    """Test the AI service"""
    import argparse

    parser = argparse.ArgumentParser(description="AI Service for Code Analysis")
    parser.add_argument("--provider", default="openai",
                       choices=ProviderFactory.get_available_providers(),
                       help="LLM provider")
    parser.add_argument("--model", help="Model name (auto-detected if not provided)")
    parser.add_argument("--api-key", help="API key")
    parser.add_argument("--list-providers", action="store_true", help="List available providers")
    parser.add_argument("--test-file", help="Test file to analyze")

    args = parser.parse_args()

    if args.list_providers:
        print("Available LLM Providers:")
        for provider in ProviderFactory.get_available_providers():
            template = ProviderFactory.get_provider_config_template(provider)
            print(f"  - {provider}: {template.get('model', 'default model')}")
        return

    # Auto-detect model if not provided
    if not args.model:
        template = ProviderFactory.get_provider_config_template(args.provider)
        args.model = template.get("model", "gpt-3.5-turbo")

    config = AIServiceConfig(
        provider=args.provider,
        model=args.model,
        api_key=args.api_key
    )

    service = get_ai_service(config)

    if args.test_file and Path(args.test_file).exists():
        content = Path(args.test_file).read_text()
        language = "python"  # Basic detection, could be enhanced
        if args.test_file.endswith(('.js', '.jsx', '.ts', '.tsx')):
            language = "javascript"
        elif args.test_file.endswith(('.java', '.cs', '.cpp', '.c')):
            language = "compiled"

        request = CodeAnalysisRequest(
            file_path=args.test_file,
            content=content,
            language=language,
            metadata={}
        )

        print(f"Analyzing {args.test_file} with {args.provider} ({args.model})...")
        response = await service.analyze_file(request)

        print(f"\nAnalysis Results for {args.test_file}:")
        print(f"Success: {response.success}")
        print(f"Processing Time: {response.processing_time:.2f}s")
        print(f"Tokens Used: {response.tokens_used}")

        if response.success:
            print("\nAnalysis:")
            for key, value in response.analysis.items():
                print(f"  {key}: {value}")
        else:
            print(f"Error: {response.error}")
    else:
        print(f"AI service initialized with {args.provider} provider.")
        print("Use --test-file to analyze a file, or --list-providers to see options.")

if __name__ == "__main__":
    asyncio.run(main())