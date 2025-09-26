"""
Grok API Client - Handles AI response generation with context awareness
Supports multiple AI providers (Grok, OpenAI, Anthropic) with fallback
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import hashlib
from datetime import datetime, timedelta

import aiohttp
from loguru import logger
import tiktoken


class AIProvider(Enum):
    """Supported AI providers"""
    GROK = "grok"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUGGINGFACE = "huggingface"


@dataclass
class PromptTemplate:
    """Prompt template with versioning and A/B testing support"""
    id: str
    version: str
    template: str
    performance_score: float = 0.0
    usage_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)


@dataclass
class AIResponse:
    """Structured AI response with metadata"""
    text: str
    provider: AIProvider
    model: str
    tokens_used: int
    latency: float
    confidence: float = 1.0
    metadata: Dict = field(default_factory=dict)


class GrokClient:
    """
    Advanced AI client with support for multiple providers,
    context management, and prompt optimization
    """
    
    def __init__(self, api_key: str, model: str = "grok-1", provider: AIProvider = AIProvider.GROK):
        """
        Initialize AI client
        
        Args:
            api_key: API key for the provider
            model: Model name to use
            provider: AI provider enum
        """
        self.api_key = api_key
        self.model = model
        self.provider = provider
        self.session = None
        
        # Prompt templates with A/B testing
        self.prompt_templates: Dict[str, List[PromptTemplate]] = {
            'greeting': [],
            'response': [],
            'question': [],
            'closing': []
        }
        
        # Response cache for efficiency
        self.response_cache: Dict[str, AIResponse] = {}
        self.cache_ttl = 3600  # 1 hour
        
        # Token counting
        self.tokenizer = None
        self._init_tokenizer()
        
        # Performance metrics
        self.metrics = {
            'total_requests': 0,
            'total_tokens': 0,
            'total_cost': 0.0,
            'average_latency': 0.0,
            'cache_hits': 0
        }
        
        # Initialize default prompt templates
        self._init_default_templates()
    
    def _init_tokenizer(self):
        """Initialize tokenizer for token counting"""
        try:
            # Use tiktoken for accurate token counting
            self.tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")
        except:
            logger.warning("Failed to initialize tokenizer, token counts will be estimates")
    
    def _init_default_templates(self):
        """Initialize default prompt templates"""
        default_templates = {
            'greeting': [
                PromptTemplate(
                    id="greet_v1",
                    version="1.0",
                    template="You are having a friendly conversation on a dating platform. The user just said: '{message}'. Respond with a warm, engaging greeting that shows interest."
                ),
                PromptTemplate(
                    id="greet_v2",
                    version="2.0",
                    template="As a friendly conversationalist on a dating app, respond to '{message}' with enthusiasm and curiosity about the person."
                )
            ],
            'response': [
                PromptTemplate(
                    id="resp_v1",
                    version="1.0",
                    template="""Previous context: {context}
User: {message}

Generate a natural, engaging response that:
- Shows genuine interest
- Asks a follow-up question
- Keeps the conversation flowing
- Is concise (under 50 words)"""
                ),
                PromptTemplate(
                    id="resp_v2",
                    version="2.0",
                    template="""Chat history:
{context}

Latest message: {message}

Your response should be friendly, authentic, and encourage further conversation. Keep it brief and engaging."""
                )
            ]
        }
        
        for category, templates in default_templates.items():
            self.prompt_templates[category] = templates
    
    async def generate_response(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 150,
        context: Optional[Dict] = None,
        use_cache: bool = True
    ) -> Optional[str]:
        """
        Generate AI response with context awareness
        
        Args:
            prompt: Input prompt
            temperature: Response randomness (0-1)
            max_tokens: Maximum response length
            context: Additional context dictionary
            use_cache: Whether to use response cache
            
        Returns:
            Generated response text
        """
        try:
            # Check cache first
            if use_cache:
                cache_key = self._generate_cache_key(prompt, temperature, max_tokens)
                if cache_key in self.response_cache:
                    cached = self.response_cache[cache_key]
                    if self._is_cache_valid(cached):
                        self.metrics['cache_hits'] += 1
                        logger.debug("Using cached response")
                        return cached.text
            
            # Select provider and generate response
            start_time = time.time()
            
            if self.provider == AIProvider.GROK:
                response = await self._grok_request(prompt, temperature, max_tokens)
            elif self.provider == AIProvider.OPENAI:
                response = await self._openai_request(prompt, temperature, max_tokens)
            elif self.provider == AIProvider.ANTHROPIC:
                response = await self._anthropic_request(prompt, temperature, max_tokens)
            else:
                response = await self._huggingface_request(prompt, temperature, max_tokens)
            
            # Calculate metrics
            latency = time.time() - start_time
            tokens_used = self._count_tokens(prompt + (response or ""))
            
            # Update metrics
            self.metrics['total_requests'] += 1
            self.metrics['total_tokens'] += tokens_used
            self.metrics['average_latency'] = (
                (self.metrics['average_latency'] * (self.metrics['total_requests'] - 1) + latency) /
                self.metrics['total_requests']
            )
            
            # Cache response
            if response and use_cache:
                ai_response = AIResponse(
                    text=response,
                    provider=self.provider,
                    model=self.model,
                    tokens_used=tokens_used,
                    latency=latency,
                    metadata={'timestamp': datetime.now().isoformat()}
                )
                self.response_cache[cache_key] = ai_response
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate AI response: {e}")
            return None
    
    async def _grok_request(self, prompt: str, temperature: float, max_tokens: int) -> Optional[str]:
        """
        Make request to Grok API
        
        Note: Grok API details are hypothetical as it's not publicly available yet.
        This uses OpenAI-compatible format as a placeholder.
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            # Hypothetical Grok API endpoint
            url = "https://api.grok.ai/v1/chat/completions"
            
            async with self.session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.error(f"Grok API error: {response.status}")
                    # Fallback to OpenAI
                    return await self._openai_request(prompt, temperature, max_tokens)
                    
        except Exception as e:
            logger.error(f"Grok request failed: {e}")
            return None
    
    async def _openai_request(self, prompt: str, temperature: float, max_tokens: int) -> Optional[str]:
        """Make request to OpenAI API"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            url = "https://api.openai.com/v1/chat/completions"
            
            async with self.session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.error(f"OpenAI API error: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"OpenAI request failed: {e}")
            return None
    
    async def _anthropic_request(self, prompt: str, temperature: float, max_tokens: int) -> Optional[str]:
        """Make request to Anthropic API"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": "claude-3-sonnet-20240229",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            url = "https://api.anthropic.com/v1/messages"
            
            async with self.session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["content"][0]["text"]
                else:
                    logger.error(f"Anthropic API error: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Anthropic request failed: {e}")
            return None
    
    async def _huggingface_request(self, prompt: str, temperature: float, max_tokens: int) -> Optional[str]:
        """Make request to HuggingFace API (free tier)"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "temperature": temperature,
                "max_new_tokens": max_tokens,
                "return_full_text": False
            }
        }
        
        try:
            # Using a free model like Mistral
            url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
            
            async with self.session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data[0]["generated_text"]
                else:
                    logger.error(f"HuggingFace API error: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"HuggingFace request failed: {e}")
            return None
    
    def select_prompt_template(self, category: str, ab_test: bool = True) -> PromptTemplate:
        """
        Select prompt template with A/B testing support
        
        Args:
            category: Template category
            ab_test: Whether to use A/B testing
            
        Returns:
            Selected prompt template
        """
        templates = self.prompt_templates.get(category, [])
        
        if not templates:
            # Return a default template
            return PromptTemplate(
                id="default",
                version="1.0",
                template="{message}"
            )
        
        if ab_test and len(templates) > 1:
            # A/B testing: select based on performance scores
            import random
            
            # Calculate selection probabilities based on performance
            total_score = sum(t.performance_score + 1 for t in templates)
            probabilities = [(t.performance_score + 1) / total_score for t in templates]
            
            # Weighted random selection
            selected = random.choices(templates, weights=probabilities)[0]
        else:
            # Select best performing template
            selected = max(templates, key=lambda t: t.performance_score)
        
        # Update usage count
        selected.usage_count += 1
        
        return selected
    
    def update_template_performance(self, template_id: str, score: float):
        """
        Update template performance score for A/B testing
        
        Args:
            template_id: Template identifier
            score: Performance score (0-1)
        """
        for templates in self.prompt_templates.values():
            for template in templates:
                if template.id == template_id:
                    # Exponential moving average
                    alpha = 0.1
                    template.performance_score = (
                        alpha * score + (1 - alpha) * template.performance_score
                    )
                    logger.debug(f"Updated template {template_id} score to {template.performance_score:.2f}")
                    return
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # Rough estimate: 1 token ≈ 4 characters
            return len(text) // 4
    
    def _generate_cache_key(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """Generate cache key for response"""
        key_data = f"{prompt}:{temperature}:{max_tokens}:{self.provider.value}:{self.model}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _is_cache_valid(self, response: AIResponse) -> bool:
        """Check if cached response is still valid"""
        if 'timestamp' not in response.metadata:
            return False
        
        timestamp = datetime.fromisoformat(response.metadata['timestamp'])
        age = (datetime.now() - timestamp).total_seconds()
        
        return age < self.cache_ttl
    
    def get_metrics(self) -> Dict:
        """Get AI client metrics"""
        return {
            **self.metrics,
            'cache_size': len(self.response_cache),
            'estimated_cost': self._estimate_cost()
        }
    
    def _estimate_cost(self) -> float:
        """Estimate API costs based on token usage"""
        # Rough cost estimates per 1K tokens
        cost_per_1k = {
            AIProvider.GROK: 0.002,  # Hypothetical
            AIProvider.OPENAI: 0.002,
            AIProvider.ANTHROPIC: 0.003,
            AIProvider.HUGGINGFACE: 0.0  # Free tier
        }
        
        rate = cost_per_1k.get(self.provider, 0.002)
        return (self.metrics['total_tokens'] / 1000) * rate
    
    async def close(self):
        """Close AI client and cleanup"""
        if self.session:
            await self.session.close()
            self.session = None