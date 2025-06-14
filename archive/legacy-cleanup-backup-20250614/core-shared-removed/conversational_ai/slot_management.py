# Conversational AI Slot Management System
# Advanced slot extraction and management for conversation memory

from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
import re
import json
from dataclasses import dataclass

from .state_management import ConversationSlot, ConversationState

class SlotType(Enum):
    """Types of conversation slots"""
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    TIME = "time"
    LOCATION = "location"
    TOPIC = "topic"
    SPEAKER = "speaker"
    EVENT = "event"
    PREFERENCE = "preference"
    BOOLEAN = "boolean"
    LIST = "list"

class SlotExtractionMethod(Enum):
    """Methods for extracting slot values"""
    REGEX = "regex"
    KEYWORD = "keyword"
    NLP = "nlp"
    API_RESPONSE = "api_response"
    USER_CONFIRMATION = "user_confirmation"
    INFERRED = "inferred"

@dataclass
class SlotDefinition:
    """Definition of a conversation slot"""
    name: str
    slot_type: SlotType
    required: bool = False
    default_value: Any = None
    validation_pattern: Optional[str] = None
    extraction_patterns: List[str] = None
    synonyms: List[str] = None
    description: str = ""
    
    def __post_init__(self):
        if self.extraction_patterns is None:
            self.extraction_patterns = []
        if self.synonyms is None:
            self.synonyms = []

class SlotExtractor:
    """Intelligent slot extraction from user messages"""
    
    def __init__(self):
        self.slot_definitions = self._initialize_slot_definitions()
        self.extraction_patterns = self._initialize_extraction_patterns()
    
    def _initialize_slot_definitions(self) -> Dict[str, SlotDefinition]:
        """Initialize predefined slot definitions"""
        return {
            "topic": SlotDefinition(
                name="topic",
                slot_type=SlotType.TOPIC,
                extraction_patterns=[
                    r"(?:about|regarding|on|for)\s+([a-zA-Z\s]+)",
                    r"(?:interested in|looking for)\s+([a-zA-Z\s]+)",
                    r"(?:defi|web3|ai|blockchain|crypto|nft|metaverse|dao)"
                ],
                synonyms=["subject", "theme", "category", "area"],
                description="Event topic or area of interest"
            ),
            
            "date_range": SlotDefinition(
                name="date_range",
                slot_type=SlotType.DATE,
                extraction_patterns=[
                    r"(?:today|tomorrow|this week|next week|this month|next month)",
                    r"(?:january|february|march|april|may|june|july|august|september|october|november|december)\s*\d{1,2}",
                    r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}",
                    r"(?:in\s+)?(\d+)\s+(?:days?|weeks?|months?)"
                ],
                synonyms=["date", "when", "time", "schedule"],
                description="Date or time range for events"
            ),
            
            "location": SlotDefinition(
                name="location",
                slot_type=SlotType.LOCATION,
                extraction_patterns=[
                    r"(?:in|at|near)\s+([a-zA-Z\s,]+)",
                    r"(?:san francisco|new york|london|berlin|singapore|tokyo|dubai|miami)",
                    r"(?:online|virtual|remote)"
                ],
                synonyms=["place", "venue", "city", "where"],
                description="Event location or venue"
            ),
            
            "speaker": SlotDefinition(
                name="speaker",
                slot_type=SlotType.SPEAKER,
                extraction_patterns=[
                    r"(?:speaker|presenter|talk by|by)\s+([a-zA-Z\s]+)",
                    r"([A-Z][a-z]+\s+[A-Z][a-z]+)",  # Person names
                    r"(?:vitalik|balaji|naval|chris dixon|andreessen)"
                ],
                synonyms=["presenter", "host", "keynote", "who"],
                description="Event speaker or presenter"
            ),
            
            "event_type": SlotDefinition(
                name="event_type",
                slot_type=SlotType.TEXT,
                extraction_patterns=[
                    r"(?:conference|workshop|meetup|summit|hackathon|webinar|panel|demo|networking)",
                    r"(?:talk|presentation|discussion|session)"
                ],
                synonyms=["type", "format", "kind"],
                description="Type or format of event"
            ),
            
            "preference": SlotDefinition(
                name="preference",
                slot_type=SlotType.PREFERENCE,
                extraction_patterns=[
                    r"(?:prefer|like|want|need)\s+([a-zA-Z\s]+)",
                    r"(?:interested in|looking for)\s+([a-zA-Z\s]+)"
                ],
                synonyms=["like", "want", "need", "prefer"],
                description="User preferences and interests"
            ),
            
            "budget": SlotDefinition(
                name="budget",
                slot_type=SlotType.NUMBER,
                extraction_patterns=[
                    r"(?:\$|budget|cost|price)\s*(\d+)",
                    r"(?:free|paid|premium)"
                ],
                synonyms=["cost", "price", "fee"],
                description="Budget constraints for events"
            ),
            
            "urgency": SlotDefinition(
                name="urgency",
                slot_type=SlotType.TEXT,
                extraction_patterns=[
                    r"(?:urgent|asap|soon|quickly|immediately)",
                    r"(?:not urgent|whenever|no rush)"
                ],
                synonyms=["priority", "rush", "speed"],
                description="Urgency of the request"
            )
        }
    
    def _initialize_extraction_patterns(self) -> Dict[str, List[str]]:
        """Initialize extraction patterns for different contexts"""
        return {
            "question_words": [
                r"(?:what|when|where|who|why|how)\s+(.*?)(?:\?|$)",
                r"(?:tell me about|show me|find|search for)\s+(.*?)(?:\?|$)"
            ],
            "preferences": [
                r"(?:i (?:want|need|like|prefer|am interested in))\s+(.*?)(?:\.|$)",
                r"(?:looking for|searching for)\s+(.*?)(?:\.|$)"
            ],
            "negations": [
                r"(?:not|don't|doesn't|won't|can't|isn't|aren't)\s+(.*?)(?:\.|$)",
                r"(?:no|none|nothing|never)\s+(.*?)(?:\.|$)"
            ]
        }
    
    async def extract_slots(
        self, 
        user_message: str, 
        conversation_state: ConversationState,
        context: Dict[str, Any] = None
    ) -> Dict[str, ConversationSlot]:
        """Extract slots from user message using multiple methods"""
        extracted_slots = {}
        message_lower = user_message.lower()
        
        # Extract slots using regex patterns
        for slot_name, slot_def in self.slot_definitions.items():
            value = await self._extract_slot_with_patterns(
                message_lower, slot_def, conversation_state
            )
            if value:
                extracted_slots[slot_name] = ConversationSlot(
                    name=slot_name,
                    value=value,
                    confidence=0.8,  # High confidence for pattern matching
                    timestamp=datetime.utcnow(),
                    source="regex_extraction"
                )
        
        # Extract slots using keyword matching
        keyword_slots = await self._extract_slots_with_keywords(
            message_lower, conversation_state
        )
        extracted_slots.update(keyword_slots)
        
        # Extract slots using context inference
        context_slots = await self._extract_slots_from_context(
            user_message, conversation_state, context or {}
        )
        extracted_slots.update(context_slots)
        
        # Validate and refine extracted slots
        validated_slots = await self._validate_extracted_slots(
            extracted_slots, conversation_state
        )
        
        return validated_slots
    
    async def _extract_slot_with_patterns(
        self,
        message: str,
        slot_def: SlotDefinition,
        conversation_state: ConversationState
    ) -> Optional[Any]:
        """Extract slot value using regex patterns"""
        for pattern in slot_def.extraction_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                if match.groups():
                    return match.group(1).strip()
                else:
                    return match.group(0).strip()
        
        # Check for synonyms
        for synonym in slot_def.synonyms:
            if synonym.lower() in message:
                # Look for value after synonym
                synonym_pattern = rf"{synonym}\s+(?:is|:|=)?\s*([a-zA-Z0-9\s]+)"
                match = re.search(synonym_pattern, message, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
        
        return None
    
    async def _extract_slots_with_keywords(
        self,
        message: str,
        conversation_state: ConversationState
    ) -> Dict[str, ConversationSlot]:
        """Extract slots using keyword matching"""
        extracted = {}
        
        # Topic keywords
        topic_keywords = {
            "defi": ["defi", "decentralized finance", "liquidity", "yield", "dex"],
            "ai": ["ai", "artificial intelligence", "machine learning", "ml", "neural"],
            "web3": ["web3", "web 3", "decentralized", "blockchain", "crypto"],
            "nft": ["nft", "non-fungible", "digital art", "collectibles"],
            "dao": ["dao", "decentralized autonomous", "governance", "voting"],
            "metaverse": ["metaverse", "virtual world", "vr", "augmented reality"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in message for keyword in keywords):
                extracted["topic"] = ConversationSlot(
                    name="topic",
                    value=topic,
                    confidence=0.7,
                    timestamp=datetime.utcnow(),
                    source="keyword_matching"
                )
                break
        
        # Location keywords
        location_keywords = {
            "san francisco": ["san francisco", "sf", "bay area"],
            "new york": ["new york", "nyc", "ny"],
            "london": ["london", "uk", "england"],
            "singapore": ["singapore", "sg"],
            "online": ["online", "virtual", "remote", "digital"]
        }
        
        for location, keywords in location_keywords.items():
            if any(keyword in message for keyword in keywords):
                extracted["location"] = ConversationSlot(
                    name="location",
                    value=location,
                    confidence=0.7,
                    timestamp=datetime.utcnow(),
                    source="keyword_matching"
                )
                break
        
        return extracted
    
    async def _extract_slots_from_context(
        self,
        user_message: str,
        conversation_state: ConversationState,
        context: Dict[str, Any]
    ) -> Dict[str, ConversationSlot]:
        """Extract slots using conversation context and inference"""
        extracted = {}
        
        # Infer from previous conversation turns
        recent_intents = conversation_state.get_recent_intents(3)
        
        # If user continues a topic without mentioning it explicitly
        if not any("topic" in slot for slot in extracted.keys()):
            previous_topic = conversation_state.get_slot("topic")
            if previous_topic and self._is_continuation(user_message):
                extracted["topic"] = ConversationSlot(
                    name="topic",
                    value=previous_topic,
                    confidence=0.6,
                    timestamp=datetime.utcnow(),
                    source="context_inference"
                )
        
        # Infer location from context if not specified
        if "here" in user_message.lower() or "local" in user_message.lower():
            # Could infer from user's previous location mentions
            previous_location = conversation_state.get_slot("location")
            if previous_location:
                extracted["location"] = ConversationSlot(
                    name="location",
                    value=previous_location,
                    confidence=0.5,
                    timestamp=datetime.utcnow(),
                    source="context_inference"
                )
        
        # Infer preferences from context
        if context.get("api_response"):
            # Extract successful search terms as preferences
            api_response = context["api_response"]
            if api_response.get("tools_used"):
                for tool in api_response["tools_used"]:
                    if "search" in tool:
                        # Infer user liked the search results
                        extracted["preference"] = ConversationSlot(
                            name="preference",
                            value="successful_search_context",
                            confidence=0.4,
                            timestamp=datetime.utcnow(),
                            source="api_inference"
                        )
        
        return extracted
    
    def _is_continuation(self, message: str) -> bool:
        """Detect if message is a continuation of previous topic"""
        continuation_indicators = [
            "also", "too", "and", "plus", "additionally", "furthermore",
            "what about", "how about", "any other", "more", "else"
        ]
        return any(indicator in message.lower() for indicator in continuation_indicators)
    
    async def _validate_extracted_slots(
        self,
        extracted_slots: Dict[str, ConversationSlot],
        conversation_state: ConversationState
    ) -> Dict[str, ConversationSlot]:
        """Validate and refine extracted slots"""
        validated = {}
        
        for slot_name, slot in extracted_slots.items():
            slot_def = self.slot_definitions.get(slot_name)
            if not slot_def:
                continue
            
            # Validate against pattern if defined
            if slot_def.validation_pattern:
                if re.match(slot_def.validation_pattern, str(slot.value)):
                    validated[slot_name] = slot
            else:
                # Basic validation based on type
                if await self._validate_slot_type(slot, slot_def):
                    validated[slot_name] = slot
        
        return validated
    
    async def _validate_slot_type(self, slot: ConversationSlot, slot_def: SlotDefinition) -> bool:
        """Validate slot value against its type definition"""
        try:
            if slot_def.slot_type == SlotType.NUMBER:
                float(slot.value)
                return True
            elif slot_def.slot_type == SlotType.BOOLEAN:
                return str(slot.value).lower() in ["true", "false", "yes", "no", "1", "0"]
            elif slot_def.slot_type == SlotType.TEXT:
                return isinstance(slot.value, str) and len(slot.value.strip()) > 0
            else:
                return True  # Other types pass through for now
        except (ValueError, TypeError):
            return False

class SlotManager:
    """Manages slot operations and memory"""
    
    def __init__(self):
        self.extractor = SlotExtractor()
        self.slot_memory = {}  # In-memory slot storage
    
    async def process_user_message(
        self,
        user_id: str,
        user_message: str,
        conversation_state: ConversationState,
        context: Dict[str, Any] = None
    ) -> Tuple[Dict[str, ConversationSlot], Dict[str, Any]]:
        """Process user message and extract/update slots"""
        
        # Extract new slots from message
        extracted_slots = await self.extractor.extract_slots(
            user_message, conversation_state, context
        )
        
        # Update conversation state with new slots
        for slot_name, slot in extracted_slots.items():
            conversation_state.set_slot(
                slot_name, 
                slot.value, 
                slot.confidence, 
                slot.source
            )
        
        # Generate slot filling suggestions
        missing_slots = await self._identify_missing_slots(
            conversation_state, extracted_slots
        )
        
        # Calculate slot filling progress
        progress = await self._calculate_slot_filling_progress(conversation_state)
        
        return extracted_slots, {
            "missing_slots": missing_slots,
            "slot_filling_progress": progress,
            "extracted_count": len(extracted_slots),
            "total_slots": len(conversation_state.slots)
        }
    
    async def _identify_missing_slots(
        self,
        conversation_state: ConversationState,
        current_extraction: Dict[str, ConversationSlot]
    ) -> List[str]:
        """Identify important missing slots for proactive slot filling"""
        
        # Define slot dependencies and importance
        slot_importance = {
            "topic": 0.9,       # Very important for event search
            "date_range": 0.7,  # Important for filtering
            "location": 0.6,    # Important for relevance
            "speaker": 0.5,     # Moderately important
            "event_type": 0.4   # Nice to have
        }
        
        missing_important_slots = []
        
        for slot_name, importance in slot_importance.items():
            if importance > 0.6:  # Only suggest high-importance slots
                if not conversation_state.get_slot(slot_name):
                    missing_important_slots.append(slot_name)
        
        return missing_important_slots
    
    async def _calculate_slot_filling_progress(
        self,
        conversation_state: ConversationState
    ) -> Dict[str, Any]:
        """Calculate slot filling progress for UX optimization"""
        
        total_important_slots = ["topic", "date_range", "location"]
        filled_important_slots = [
            slot for slot in total_important_slots 
            if conversation_state.get_slot(slot)
        ]
        
        progress_percentage = len(filled_important_slots) / len(total_important_slots)
        
        return {
            "percentage": progress_percentage,
            "filled_slots": len(filled_important_slots),
            "total_important_slots": len(total_important_slots),
            "is_sufficient": progress_percentage >= 0.6,  # 60% threshold
            "next_suggestion": total_important_slots[len(filled_important_slots)] if len(filled_important_slots) < len(total_important_slots) else None
        }
    
    async def generate_slot_filling_question(
        self,
        missing_slot: str,
        conversation_state: ConversationState
    ) -> str:
        """Generate natural questions to fill missing slots"""
        
        questions = {
            "topic": [
                "What kind of events are you most interested in?",
                "Are you looking for events about any specific topic?",
                "What areas would you like to explore?"
            ],
            "date_range": [
                "Are you looking for events happening at a specific time?",
                "When would you like to attend these events?",
                "Do you have a particular date range in mind?"
            ],
            "location": [
                "Are you interested in events in a specific location?",
                "Would you prefer online or in-person events?",
                "What city or area are you considering?"
            ],
            "speaker": [
                "Are you interested in hearing from any particular speakers?",
                "Do you have favorite speakers or thought leaders?",
                "Any specific people you'd like to learn from?"
            ],
            "event_type": [
                "What type of events do you prefer - conferences, workshops, or networking?",
                "Are you looking for any specific event format?",
                "Do you prefer large conferences or smaller meetups?"
            ]
        }
        
        slot_questions = questions.get(missing_slot, ["Could you provide more details?"])
        
        # Select question based on conversation context
        return slot_questions[0]  # For now, use first question
    
    async def get_slot_summary(self, conversation_state: ConversationState) -> Dict[str, Any]:
        """Get summary of current slot state for monitoring"""
        
        active_slots = {
            name: {
                "value": slot.value,
                "confidence": slot.confidence,
                "age_minutes": (datetime.utcnow() - slot.timestamp).total_seconds() / 60,
                "source": slot.source
            }
            for name, slot in conversation_state.slots.items()
            if slot.is_valid()
        }
        
        return {
            "active_slots": active_slots,
            "total_slots": len(active_slots),
            "average_confidence": sum(slot["confidence"] for slot in active_slots.values()) / len(active_slots) if active_slots else 0,
            "slot_filling_target": 0.6,  # 60% of important slots should be filled
            "context_preservation_score": conversation_state.calculate_context_preservation_score()
        }

# Global instance for shared access
slot_manager = SlotManager()