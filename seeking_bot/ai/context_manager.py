"""
Context Manager - Intelligent conversation context management
Implements sliding window and multi-agent strategies for coherent conversations
"""

import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import deque
import hashlib
from enum import Enum
from loguru import logger
import re


class ContextStrategy(Enum):
    """Context management strategies"""
    SLIDING_WINDOW = "sliding_window"
    MULTI_AGENT = "multi_agent"
    HIERARCHICAL = "hierarchical"
    GRAPH_BASED = "graph_based"


@dataclass
class Message:
    """Individual message in conversation"""
    content: str
    sender: str  # 'user' or 'bot'
    timestamp: datetime
    metadata: Dict = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    sentiment: Optional[float] = None
    topics: List[str] = field(default_factory=list)


@dataclass
class ConversationContext:
    """Complete conversation context"""
    conversation_id: str
    user_id: str
    user_profile: Dict = field(default_factory=dict)
    messages: List[Message] = field(default_factory=list)
    topics_discussed: List[str] = field(default_factory=list)
    relationship_stage: str = "initial"
    sentiment_history: List[float] = field(default_factory=list)
    key_facts: Dict = field(default_factory=dict)
    conversation_goals: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)


class ContextManager:
    """
    Advanced context management for AI conversations
    Maintains conversation coherence and personality consistency
    """
    
    def __init__(self, strategy: str = "sliding_window", window_size: int = 10):
        """
        Initialize context manager
        
        Args:
            strategy: Context management strategy
            window_size: Size of context window
        """
        self.strategy = ContextStrategy(strategy)
        self.window_size = window_size
        
        # Conversation storage
        self.conversations: Dict[str, ConversationContext] = {}
        
        # Topic extraction patterns
        self.topic_patterns = {
            'interests': r'(?:i like|i love|i enjoy|interested in|passion for)\s+(\w+)',
            'work': r'(?:i work|my job|career|profession)\s+(?:as|in|at)\s+(\w+)',
            'location': r'(?:i live|i\'m from|based in|located in)\s+(\w+)',
            'hobbies': r'(?:hobby|free time|weekend)\s+(\w+)',
            'preferences': r'(?:prefer|favorite|best)\s+(\w+)'
        }
        
        # Relationship stage markers
        self.relationship_stages = {
            'initial': ['hello', 'hi', 'hey', 'nice to meet'],
            'getting_to_know': ['tell me about', 'what do you', 'how about you'],
            'comfortable': ['haha', 'lol', 'that\'s funny', 'i feel'],
            'interested': ['meet', 'coffee', 'dinner', 'phone', 'number'],
            'established': ['miss you', 'thinking of you', 'can\'t wait']
        }
        
        # Memory importance scoring
        self.importance_keywords = [
            'birthday', 'anniversary', 'job', 'family', 'favorite',
            'hate', 'love', 'important', 'never', 'always'
        ]
        
        logger.info(f"Context manager initialized with {strategy} strategy")
    
    def get_context(self, session: Any) -> Dict[str, Any]:
        """
        Get conversation context for a session
        
        Args:
            session: Chat session object
            
        Returns:
            Context dictionary for AI prompting
        """
        conversation_id = session.chat_id
        
        # Get or create conversation context
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = ConversationContext(
                conversation_id=conversation_id,
                user_id=session.user_name
            )
        
        context = self.conversations[conversation_id]
        
        # Update context with recent messages
        for msg in session.messages:
            self._add_message_to_context(context, msg)
        
        # Apply context strategy
        if self.strategy == ContextStrategy.SLIDING_WINDOW:
            return self._get_sliding_window_context(context)
        elif self.strategy == ContextStrategy.MULTI_AGENT:
            return self._get_multi_agent_context(context)
        elif self.strategy == ContextStrategy.HIERARCHICAL:
            return self._get_hierarchical_context(context)
        else:
            return self._get_sliding_window_context(context)
    
    def _add_message_to_context(self, context: ConversationContext, message: Dict):
        """Add a message to conversation context"""
        # Create Message object
        msg = Message(
            content=message['text'],
            sender='user' if message['type'] == 'received' else 'bot',
            timestamp=message['timestamp']
        )
        
        # Extract topics
        msg.topics = self._extract_topics(message['text'])
        
        # Analyze sentiment
        msg.sentiment = self._analyze_sentiment(message['text'])
        
        # Check if message already exists
        if not any(m.content == msg.content and 
                  m.timestamp == msg.timestamp for m in context.messages):
            context.messages.append(msg)
            
            # Update context metadata
            self._update_context_metadata(context, msg)
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from message text"""
        topics = []
        text_lower = text.lower()
        
        for category, pattern in self.topic_patterns.items():
            matches = re.findall(pattern, text_lower)
            topics.extend(matches)
        
        # Extract general topics
        # Simple keyword extraction (can be enhanced with NLP)
        keywords = ['coffee', 'dinner', 'movie', 'travel', 'music', 
                   'sports', 'reading', 'cooking', 'fitness', 'art']
        
        for keyword in keywords:
            if keyword in text_lower:
                topics.append(keyword)
        
        return list(set(topics))  # Remove duplicates
    
    def _analyze_sentiment(self, text: str) -> float:
        """
        Simple sentiment analysis
        
        Returns:
            Sentiment score between -1 (negative) and 1 (positive)
        """
        positive_words = ['good', 'great', 'love', 'wonderful', 'amazing',
                         'excellent', 'happy', 'joy', 'beautiful', 'fantastic']
        negative_words = ['bad', 'terrible', 'hate', 'awful', 'horrible',
                         'sad', 'angry', 'disappointed', 'worst', 'ugly']
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count + negative_count == 0:
            return 0.0
        
        sentiment = (positive_count - negative_count) / (positive_count + negative_count)
        return max(-1, min(1, sentiment))
    
    def _update_context_metadata(self, context: ConversationContext, message: Message):
        """Update conversation metadata based on new message"""
        # Update topics
        context.topics_discussed.extend(message.topics)
        context.topics_discussed = list(set(context.topics_discussed))
        
        # Update sentiment history
        if message.sentiment is not None:
            context.sentiment_history.append(message.sentiment)
            # Keep only recent sentiment
            context.sentiment_history = context.sentiment_history[-20:]
        
        # Update relationship stage
        self._update_relationship_stage(context, message)
        
        # Extract key facts
        self._extract_key_facts(context, message)
        
        # Update timestamp
        context.last_updated = datetime.now()
    
    def _update_relationship_stage(self, context: ConversationContext, message: Message):
        """Update relationship stage based on conversation progress"""
        text_lower = message.content.lower()
        
        for stage, markers in self.relationship_stages.items():
            if any(marker in text_lower for marker in markers):
                # Progress to next stage if appropriate
                current_stage_index = list(self.relationship_stages.keys()).index(
                    context.relationship_stage
                )
                new_stage_index = list(self.relationship_stages.keys()).index(stage)
                
                if new_stage_index >= current_stage_index:
                    context.relationship_stage = stage
                    logger.debug(f"Relationship stage updated to: {stage}")
    
    def _extract_key_facts(self, context: ConversationContext, message: Message):
        """Extract and store important facts from messages"""
        if message.sender != 'user':
            return
        
        text = message.content
        
        # Extract name
        name_pattern = r"(?:my name is|i'm|i am|call me)\s+(\w+)"
        name_match = re.search(name_pattern, text, re.IGNORECASE)
        if name_match:
            context.key_facts['name'] = name_match.group(1)
        
        # Extract age
        age_pattern = r"(?:i'm|i am)\s+(\d+)\s+(?:years old|yo)"
        age_match = re.search(age_pattern, text, re.IGNORECASE)
        if age_match:
            context.key_facts['age'] = age_match.group(1)
        
        # Extract location
        location_pattern = r"(?:i live in|i'm from|based in)\s+([A-Z]\w+(?:\s+[A-Z]\w+)*)"
        location_match = re.search(location_pattern, text, re.IGNORECASE)
        if location_match:
            context.key_facts['location'] = location_match.group(1)
        
        # Check for important information
        for keyword in self.importance_keywords:
            if keyword in text.lower():
                # Store the entire message as important
                if 'important_messages' not in context.key_facts:
                    context.key_facts['important_messages'] = []
                context.key_facts['important_messages'].append({
                    'content': text,
                    'timestamp': message.timestamp.isoformat()
                })
    
    def _get_sliding_window_context(self, context: ConversationContext) -> Dict:
        """Get context using sliding window strategy"""
        # Get recent messages
        recent_messages = context.messages[-self.window_size:]
        
        # Format conversation history
        conversation_history = []
        for msg in recent_messages:
            role = "User" if msg.sender == "user" else "Assistant"
            conversation_history.append(f"{role}: {msg.content}")
        
        return {
            'strategy': 'sliding_window',
            'conversation_history': "\n".join(conversation_history),
            'user_profile': context.user_profile,
            'topics_discussed': context.topics_discussed[:10],
            'relationship_stage': context.relationship_stage,
            'key_facts': context.key_facts,
            'recent_sentiment': sum(context.sentiment_history[-5:]) / max(len(context.sentiment_history[-5:]), 1)
        }
    
    def _get_multi_agent_context(self, context: ConversationContext) -> Dict:
        """Get context using multi-agent strategy"""
        # Different agents focus on different aspects
        agents = {
            'personality_agent': self._get_personality_context(context),
            'topic_agent': self._get_topic_context(context),
            'relationship_agent': self._get_relationship_context(context),
            'memory_agent': self._get_memory_context(context)
        }
        
        # Combine agent contexts
        combined_context = {
            'strategy': 'multi_agent',
            'agents': agents,
            'conversation_history': self._get_recent_history(context, 5),
            'synthesis': self._synthesize_agent_contexts(agents)
        }
        
        return combined_context
    
    def _get_personality_context(self, context: ConversationContext) -> Dict:
        """Agent focused on maintaining personality consistency"""
        return {
            'user_communication_style': self._analyze_communication_style(context),
            'preferred_topics': context.topics_discussed[:5],
            'sentiment_profile': 'positive' if sum(context.sentiment_history) > 0 else 'neutral'
        }
    
    def _get_topic_context(self, context: ConversationContext) -> Dict:
        """Agent focused on topic management"""
        return {
            'current_topics': self._get_current_topics(context),
            'topic_transitions': self._suggest_topic_transitions(context),
            'avoided_topics': []  # Can be configured
        }
    
    def _get_relationship_context(self, context: ConversationContext) -> Dict:
        """Agent focused on relationship progression"""
        return {
            'current_stage': context.relationship_stage,
            'next_stage_suggestions': self._get_next_stage_suggestions(context),
            'relationship_goals': context.conversation_goals
        }
    
    def _get_memory_context(self, context: ConversationContext) -> Dict:
        """Agent focused on important information recall"""
        important_facts = []
        
        # Get important messages
        if 'important_messages' in context.key_facts:
            important_facts = context.key_facts['important_messages'][-3:]
        
        return {
            'key_facts': context.key_facts,
            'important_memories': important_facts,
            'user_preferences': self._extract_preferences(context)
        }
    
    def _get_hierarchical_context(self, context: ConversationContext) -> Dict:
        """Get context using hierarchical strategy"""
        # Organize context in hierarchy: immediate → recent → historical
        return {
            'strategy': 'hierarchical',
            'immediate': {
                'last_message': context.messages[-1].content if context.messages else "",
                'last_topics': context.messages[-1].topics if context.messages else []
            },
            'recent': {
                'conversation': self._get_recent_history(context, 5),
                'topics': list(set(topic for msg in context.messages[-5:] 
                                  for topic in msg.topics))
            },
            'historical': {
                'key_facts': context.key_facts,
                'relationship_stage': context.relationship_stage,
                'all_topics': context.topics_discussed
            }
        }
    
    def _get_recent_history(self, context: ConversationContext, count: int) -> str:
        """Get recent conversation history"""
        recent = context.messages[-count:] if len(context.messages) > count else context.messages
        history = []
        
        for msg in recent:
            role = "User" if msg.sender == "user" else "Assistant"
            history.append(f"{role}: {msg.content}")
        
        return "\n".join(history)
    
    def _analyze_communication_style(self, context: ConversationContext) -> str:
        """Analyze user's communication style"""
        if not context.messages:
            return "unknown"
        
        user_messages = [msg for msg in context.messages if msg.sender == "user"]
        
        if not user_messages:
            return "unknown"
        
        # Analyze message length
        avg_length = sum(len(msg.content) for msg in user_messages) / len(user_messages)
        
        if avg_length < 20:
            style = "brief"
        elif avg_length < 50:
            style = "moderate"
        else:
            style = "detailed"
        
        # Check for emojis
        emoji_pattern = r'[😀-🙏🌀-🗿🚀-🛿🏀-🏿]'
        uses_emojis = any(re.search(emoji_pattern, msg.content) for msg in user_messages)
        
        if uses_emojis:
            style += "_emoji_user"
        
        return style
    
    def _get_current_topics(self, context: ConversationContext) -> List[str]:
        """Get currently active topics"""
        if not context.messages:
            return []
        
        # Get topics from last 3 messages
        recent_topics = []
        for msg in context.messages[-3:]:
            recent_topics.extend(msg.topics)
        
        return list(set(recent_topics))
    
    def _suggest_topic_transitions(self, context: ConversationContext) -> List[str]:
        """Suggest natural topic transitions"""
        current_topics = self._get_current_topics(context)
        
        topic_transitions = {
            'coffee': ['favorite coffee shop', 'morning routine', 'weekend plans'],
            'work': ['work-life balance', 'hobbies', 'weekend activities'],
            'travel': ['favorite destinations', 'bucket list', 'adventures'],
            'music': ['concerts', 'favorite artists', 'dancing'],
            'fitness': ['healthy lifestyle', 'outdoor activities', 'sports']
        }
        
        suggestions = []
        for topic in current_topics:
            if topic in topic_transitions:
                suggestions.extend(topic_transitions[topic])
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def _get_next_stage_suggestions(self, context: ConversationContext) -> List[str]:
        """Suggest actions for relationship progression"""
        stage_suggestions = {
            'initial': ['Ask about interests', 'Share something about yourself'],
            'getting_to_know': ['Find common interests', 'Ask deeper questions'],
            'comfortable': ['Suggest a casual meeting', 'Share contact information'],
            'interested': ['Plan a specific date', 'Express genuine interest'],
            'established': ['Maintain regular contact', 'Plan future activities']
        }
        
        return stage_suggestions.get(context.relationship_stage, [])
    
    def _extract_preferences(self, context: ConversationContext) -> Dict:
        """Extract user preferences from conversation"""
        preferences = {}
        
        for msg in context.messages:
            if msg.sender == "user":
                text = msg.content.lower()
                
                # Extract likes
                like_pattern = r"(?:i like|i love|i enjoy)\s+(\w+(?:\s+\w+)?)"
                likes = re.findall(like_pattern, text)
                if likes:
                    preferences['likes'] = preferences.get('likes', []) + likes
                
                # Extract dislikes
                dislike_pattern = r"(?:i don't like|i hate|not a fan of)\s+(\w+(?:\s+\w+)?)"
                dislikes = re.findall(dislike_pattern, text)
                if dislikes:
                    preferences['dislikes'] = preferences.get('dislikes', []) + dislikes
        
        # Remove duplicates
        for key in preferences:
            preferences[key] = list(set(preferences[key]))[:5]
        
        return preferences
    
    def _synthesize_agent_contexts(self, agents: Dict) -> str:
        """Synthesize multiple agent contexts into guidance"""
        synthesis = []
        
        # Personality guidance
        personality = agents['personality_agent']
        synthesis.append(f"Communication style: {personality['user_communication_style']}")
        
        # Topic guidance
        topics = agents['topic_agent']
        if topics['current_topics']:
            synthesis.append(f"Current topics: {', '.join(topics['current_topics'][:3])}")
        
        # Relationship guidance
        relationship = agents['relationship_agent']
        synthesis.append(f"Relationship stage: {relationship['current_stage']}")
        
        # Memory guidance
        memory = agents['memory_agent']
        if memory['key_facts']:
            synthesis.append(f"Remember: {list(memory['key_facts'].keys())[:3]}")
        
        return " | ".join(synthesis)
    
    def clear_old_contexts(self, days: int = 7):
        """Clear old conversation contexts"""
        cutoff = datetime.now() - timedelta(days=days)
        
        to_remove = []
        for conv_id, context in self.conversations.items():
            if context.last_updated < cutoff:
                to_remove.append(conv_id)
        
        for conv_id in to_remove:
            del self.conversations[conv_id]
        
        if to_remove:
            logger.info(f"Cleared {len(to_remove)} old conversation contexts")
    
    def export_context(self, conversation_id: str) -> Dict:
        """Export conversation context for analysis or backup"""
        if conversation_id not in self.conversations:
            return {}
        
        context = self.conversations[conversation_id]
        
        return {
            'conversation_id': context.conversation_id,
            'user_id': context.user_id,
            'message_count': len(context.messages),
            'topics': context.topics_discussed,
            'relationship_stage': context.relationship_stage,
            'key_facts': context.key_facts,
            'sentiment_average': sum(context.sentiment_history) / max(len(context.sentiment_history), 1),
            'last_updated': context.last_updated.isoformat()
        }