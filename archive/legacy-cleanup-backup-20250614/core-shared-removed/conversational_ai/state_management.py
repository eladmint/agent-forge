# Conversational AI State Management
# Rasa-inspired conversation state tracking for Nuru AI

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import asyncio
from contextlib import asynccontextmanager

class ConversationStateType(Enum):
    """Types of conversation states"""
    INITIAL = "initial"
    EVENT_SEARCH = "event_search"
    SPEAKER_LOOKUP = "speaker_lookup"
    PREFERENCE_SETTING = "preference_setting"
    REGISTRATION = "registration"
    CLARIFICATION = "clarification"
    FOLLOW_UP = "follow_up"

class IntentConfidence(Enum):
    """Intent recognition confidence levels"""
    HIGH = "high"      # >0.8
    MEDIUM = "medium"  # 0.5-0.8
    LOW = "low"        # <0.5

@dataclass
class ConversationSlot:
    """Individual conversation slot following Rasa patterns"""
    name: str
    value: Any
    confidence: float
    timestamp: datetime
    source: str  # "user_input", "api_response", "inferred"
    
    def is_valid(self) -> bool:
        """Check if slot value is still valid"""
        # Slots expire after 1 hour for dynamic data
        if self.source == "api_response":
            return datetime.utcnow() - self.timestamp < timedelta(hours=1)
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source
        }

@dataclass
class IntentHistory:
    """Track conversation intent history"""
    intent: str
    confidence: IntentConfidence
    timestamp: datetime
    context: Dict[str, Any]
    resolved: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent": self.intent,
            "confidence": self.confidence.value,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
            "resolved": self.resolved
        }

@dataclass
class ConversationState:
    """Core conversation state following Rasa-inspired patterns"""
    user_id: str
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    current_state: ConversationStateType = ConversationStateType.INITIAL
    
    # Rasa-inspired slot management
    slots: Dict[str, ConversationSlot] = field(default_factory=dict)
    
    # Intent tracking
    intent_history: List[IntentHistory] = field(default_factory=list)
    current_intent: Optional[str] = None
    intent_confidence: IntentConfidence = IntentConfidence.LOW
    
    # Context management
    context_stack: List[Dict[str, Any]] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    conversation_memory: List[Dict[str, Any]] = field(default_factory=list)
    
    # Session tracking
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    turn_count: int = 0
    
    # Proactive assistance tracking
    proactive_suggestions_given: List[str] = field(default_factory=list)
    clarification_requests: int = 0
    successful_resolutions: int = 0
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()
        self.turn_count += 1
    
    def set_slot(self, name: str, value: Any, confidence: float = 1.0, source: str = "user_input"):
        """Set conversation slot with Rasa-style slot management"""
        self.slots[name] = ConversationSlot(
            name=name,
            value=value,
            confidence=confidence,
            timestamp=datetime.utcnow(),
            source=source
        )
        self.update_activity()
    
    def get_slot(self, name: str) -> Optional[Any]:
        """Get slot value if valid"""
        slot = self.slots.get(name)
        if slot and slot.is_valid():
            return slot.value
        return None
    
    def add_intent(self, intent: str, confidence: IntentConfidence, context: Dict[str, Any]):
        """Add intent to history"""
        intent_entry = IntentHistory(
            intent=intent,
            confidence=confidence,
            timestamp=datetime.utcnow(),
            context=context
        )
        self.intent_history.append(intent_entry)
        self.current_intent = intent
        self.intent_confidence = confidence
        self.update_activity()
    
    def push_context(self, context: Dict[str, Any]):
        """Push new context to stack"""
        self.context_stack.append({
            **context,
            "timestamp": datetime.utcnow().isoformat(),
            "turn": self.turn_count
        })
        # Keep only last 10 contexts to prevent memory bloat
        if len(self.context_stack) > 10:
            self.context_stack = self.context_stack[-10:]
    
    def get_current_context(self) -> Dict[str, Any]:
        """Get current conversation context"""
        return self.context_stack[-1] if self.context_stack else {}
    
    def add_conversation_turn(self, user_message: str, bot_response: str, metadata: Dict[str, Any] = None):
        """Add conversation turn to memory"""
        turn = {
            "turn_id": self.turn_count,
            "timestamp": datetime.utcnow().isoformat(),
            "user_message": user_message,
            "bot_response": bot_response,
            "metadata": metadata or {}
        }
        self.conversation_memory.append(turn)
        
        # Keep only last 50 turns to manage memory
        if len(self.conversation_memory) > 50:
            self.conversation_memory = self.conversation_memory[-50:]
    
    def get_recent_intents(self, limit: int = 5) -> List[IntentHistory]:
        """Get recent intent history"""
        return self.intent_history[-limit:] if self.intent_history else []
    
    def has_previous_searches(self) -> bool:
        """Check if user has previous search history"""
        search_intents = ["event_search", "speaker_lookup", "topic_search"]
        return any(intent.intent in search_intents for intent in self.intent_history)
    
    def get_primary_interests(self) -> List[str]:
        """Extract primary interests from conversation history"""
        interests = []
        for slot in self.slots.values():
            if slot.name in ["topic", "interest", "category"] and slot.is_valid():
                if isinstance(slot.value, list):
                    interests.extend(slot.value)
                else:
                    interests.append(str(slot.value))
        return list(set(interests))
    
    def matches_user_interests(self, event_data: Dict[str, Any]) -> bool:
        """Check if event matches user interests from conversation"""
        user_interests = self.get_primary_interests()
        event_topics = event_data.get("topics", [])
        
        if not user_interests or not event_topics:
            return False
        
        # Simple keyword matching - can be enhanced with semantic similarity
        for interest in user_interests:
            for topic in event_topics:
                if interest.lower() in topic.lower() or topic.lower() in interest.lower():
                    return True
        return False
    
    def calculate_context_preservation_score(self) -> float:
        """Calculate how well context is preserved (target: 95%)"""
        if not self.conversation_memory:
            return 1.0
        
        preserved_contexts = 0
        total_contexts = len(self.conversation_memory) - 1
        
        if total_contexts == 0:
            return 1.0
        
        for i in range(1, len(self.conversation_memory)):
            current_turn = self.conversation_memory[i]
            previous_turn = self.conversation_memory[i-1]
            
            # Check if current turn references previous context
            if self._has_context_reference(current_turn, previous_turn):
                preserved_contexts += 1
        
        return preserved_contexts / total_contexts
    
    def _has_context_reference(self, current_turn: Dict[str, Any], previous_turn: Dict[str, Any]) -> bool:
        """Check if current turn maintains context from previous turn"""
        # Simple heuristic - can be enhanced with NLP
        current_message = current_turn.get("user_message", "").lower()
        previous_response = previous_turn.get("bot_response", "").lower()
        
        # Check for pronouns, references, continuations
        context_indicators = ["this", "that", "these", "those", "it", "them", "also", "too", "and"]
        
        return any(indicator in current_message for indicator in context_indicators)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize conversation state"""
        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "current_state": self.current_state.value,
            "slots": {name: slot.to_dict() for name, slot in self.slots.items()},
            "intent_history": [intent.to_dict() for intent in self.intent_history],
            "current_intent": self.current_intent,
            "intent_confidence": self.intent_confidence.value,
            "context_stack": self.context_stack,
            "user_preferences": self.user_preferences,
            "conversation_memory": self.conversation_memory,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "turn_count": self.turn_count,
            "proactive_suggestions_given": self.proactive_suggestions_given,
            "clarification_requests": self.clarification_requests,
            "successful_resolutions": self.successful_resolutions
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationState":
        """Deserialize conversation state"""
        state = cls(user_id=data["user_id"])
        state.session_id = data.get("session_id", state.session_id)
        state.current_state = ConversationStateType(data.get("current_state", "initial"))
        
        # Restore slots
        for name, slot_data in data.get("slots", {}).items():
            state.slots[name] = ConversationSlot(
                name=slot_data["name"],
                value=slot_data["value"],
                confidence=slot_data["confidence"],
                timestamp=datetime.fromisoformat(slot_data["timestamp"]),
                source=slot_data["source"]
            )
        
        # Restore intent history
        for intent_data in data.get("intent_history", []):
            state.intent_history.append(IntentHistory(
                intent=intent_data["intent"],
                confidence=IntentConfidence(intent_data["confidence"]),
                timestamp=datetime.fromisoformat(intent_data["timestamp"]),
                context=intent_data["context"],
                resolved=intent_data.get("resolved", False)
            ))
        
        state.current_intent = data.get("current_intent")
        state.intent_confidence = IntentConfidence(data.get("intent_confidence", "low"))
        state.context_stack = data.get("context_stack", [])
        state.user_preferences = data.get("user_preferences", {})
        state.conversation_memory = data.get("conversation_memory", [])
        state.created_at = datetime.fromisoformat(data.get("created_at", datetime.utcnow().isoformat()))
        state.last_activity = datetime.fromisoformat(data.get("last_activity", datetime.utcnow().isoformat()))
        state.turn_count = data.get("turn_count", 0)
        state.proactive_suggestions_given = data.get("proactive_suggestions_given", [])
        state.clarification_requests = data.get("clarification_requests", 0)
        state.successful_resolutions = data.get("successful_resolutions", 0)
        
        return state

class ConversationStateManager:
    """Manages conversation states across the application"""
    
    def __init__(self):
        self.active_conversations: Dict[str, ConversationState] = {}
        self.state_persistence = None  # Will be injected
        self._cleanup_interval = 3600  # 1 hour cleanup interval
        self._max_inactive_time = timedelta(hours=24)  # 24 hour session timeout
    
    async def get_conversation_state(self, user_id: str) -> ConversationState:
        """Get or create conversation state for user"""
        if user_id not in self.active_conversations:
            # Try to load from persistence
            if self.state_persistence and hasattr(self.state_persistence, 'load_conversation_state'):
                state = await self.state_persistence.load_conversation_state(user_id)
                if state:
                    self.active_conversations[user_id] = state
                else:
                    self.active_conversations[user_id] = ConversationState(user_id=user_id)
            else:
                self.active_conversations[user_id] = ConversationState(user_id=user_id)
        
        return self.active_conversations[user_id]
    
    async def update_conversation_context(
        self, 
        user_id: str, 
        new_context: Dict[str, Any],
        intent: str = None,
        confidence: IntentConfidence = IntentConfidence.MEDIUM
    ):
        """Update conversation context across services"""
        state = await self.get_conversation_state(user_id)
        
        # Update context stack
        state.push_context(new_context)
        
        # Track intent if provided
        if intent:
            state.add_intent(intent, confidence, new_context)
        
        # Extract and set slots from context
        await self._extract_slots_from_context(state, new_context)
        
        # Persist state changes
        if self.state_persistence and hasattr(self.state_persistence, 'save_conversation_state'):
            await self.state_persistence.save_conversation_state(user_id, state)
        
        # Notify interested services of state change
        await self._broadcast_state_change(user_id, state)
    
    async def _extract_slots_from_context(self, state: ConversationState, context: Dict[str, Any]):
        """Extract slots from context automatically"""
        # Extract common slots
        if "query" in context:
            state.set_slot("last_query", context["query"], source="user_input")
        
        if "topic" in context:
            state.set_slot("topic", context["topic"], source="user_input")
        
        if "date_range" in context:
            state.set_slot("date_range", context["date_range"], source="user_input")
        
        if "location" in context:
            state.set_slot("location", context["location"], source="user_input")
        
        if "speaker" in context:
            state.set_slot("speaker", context["speaker"], source="user_input")
    
    async def _broadcast_state_change(self, user_id: str, state: ConversationState):
        """Notify interested services of state change"""
        # This would integrate with the event bus system
        # For now, we'll just log the change
        print(f"State change for user {user_id}: {state.current_state.value}")
    
    async def add_conversation_turn(
        self, 
        user_id: str, 
        user_message: str, 
        bot_response: str, 
        metadata: Dict[str, Any] = None
    ):
        """Add conversation turn to user's conversation memory"""
        state = await self.get_conversation_state(user_id)
        state.add_conversation_turn(user_message, bot_response, metadata)
        
        # Persist the updated state
        if self.state_persistence and hasattr(self.state_persistence, 'save_conversation_state'):
            await self.state_persistence.save_conversation_state(user_id, state)
    
    async def cleanup_inactive_sessions(self):
        """Clean up inactive conversation sessions"""
        current_time = datetime.utcnow()
        inactive_users = []
        
        for user_id, state in self.active_conversations.items():
            if current_time - state.last_activity > self._max_inactive_time:
                inactive_users.append(user_id)
        
        for user_id in inactive_users:
            # Save final state before cleanup
            if self.state_persistence and hasattr(self.state_persistence, 'save_conversation_state'):
                await self.state_persistence.save_conversation_state(user_id, self.active_conversations[user_id])
            del self.active_conversations[user_id]
        
        print(f"Cleaned up {len(inactive_users)} inactive conversation sessions")
    
    async def get_conversation_metrics(self) -> Dict[str, Any]:
        """Get conversation state metrics for monitoring"""
        total_conversations = len(self.active_conversations)
        context_preservation_scores = []
        
        for state in self.active_conversations.values():
            context_preservation_scores.append(state.calculate_context_preservation_score())
        
        avg_context_preservation = sum(context_preservation_scores) / len(context_preservation_scores) if context_preservation_scores else 0
        
        return {
            "total_active_conversations": total_conversations,
            "average_context_preservation": avg_context_preservation,
            "target_context_preservation": 0.95,  # 95% target
            "context_preservation_achieved": avg_context_preservation >= 0.95
        }

# Global instance for shared access
conversation_state_manager = ConversationStateManager()