# Conversational AI Persona Modeling System
# Advanced user persona detection and modeling for personalized experiences

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import json
import math

from .state_management import ConversationState, IntentConfidence

class UserPersonaType(Enum):
    """Types of user personas based on behavior and preferences"""
    CRYPTO_ENTHUSIAST = "crypto_enthusiast"
    DEFI_DEVELOPER = "defi_developer"
    INVESTOR = "investor"
    RESEARCHER = "researcher"
    ENTREPRENEUR = "entrepreneur"
    STUDENT = "student"
    INDUSTRY_PROFESSIONAL = "industry_professional"
    CASUAL_EXPLORER = "casual_explorer"

class ExperienceLevel(Enum):
    """User experience levels in Web3/crypto space"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class EngagementStyle(Enum):
    """How users prefer to engage with content"""
    DETAILED = "detailed"          # Wants comprehensive information
    QUICK_OVERVIEW = "quick"       # Prefers summaries and highlights
    INTERACTIVE = "interactive"    # Likes Q&A and back-and-forth
    RESEARCH_FOCUSED = "research"  # Deep dives and technical details

@dataclass
class PersonaSignal:
    """Individual signal contributing to persona detection"""
    signal_type: str
    value: Any
    confidence: float
    timestamp: datetime
    source: str
    weight: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "signal_type": self.signal_type,
            "value": self.value,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "weight": self.weight
        }

@dataclass
class UserPersona:
    """Comprehensive user persona model"""
    user_id: str
    primary_persona: UserPersonaType
    persona_confidence: float
    experience_level: ExperienceLevel
    engagement_style: EngagementStyle
    
    # Persona attributes
    interests: List[str] = field(default_factory=list)
    expertise_areas: List[str] = field(default_factory=list)
    preferred_content_types: List[str] = field(default_factory=list)
    activity_patterns: Dict[str, Any] = field(default_factory=dict)
    
    # Behavioral signals
    signals: List[PersonaSignal] = field(default_factory=list)
    
    # Temporal tracking
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    update_count: int = 0
    
    # Persona metrics
    prediction_accuracy: float = 0.0
    adaptation_rate: float = 0.1  # How quickly persona adapts to new signals
    
    def update_persona(self, new_signals: List[PersonaSignal]):
        """Update persona based on new behavioral signals"""
        self.signals.extend(new_signals)
        self.last_updated = datetime.utcnow()
        self.update_count += 1
        
        # Recalculate persona based on all signals
        self._recalculate_persona()
    
    def _recalculate_persona(self):
        """Recalculate persona type based on current signals"""
        persona_scores = {persona_type: 0.0 for persona_type in UserPersonaType}
        
        # Weight recent signals more heavily
        current_time = datetime.utcnow()
        
        for signal in self.signals:
            # Time decay factor (more recent = higher weight)
            days_old = (current_time - signal.timestamp).days
            time_weight = math.exp(-days_old * 0.1)  # Exponential decay
            
            # Calculate signal contribution
            signal_weight = signal.confidence * signal.weight * time_weight
            
            # Add to relevant persona scores
            relevant_personas = self._get_relevant_personas_for_signal(signal)
            for persona_type in relevant_personas:
                persona_scores[persona_type] += signal_weight
        
        # Determine primary persona
        if persona_scores:
            max_score = max(persona_scores.values())
            if max_score > 0:
                self.primary_persona = max(persona_scores, key=persona_scores.get)
                # Normalize confidence (0-1 range)
                total_score = sum(persona_scores.values())
                self.persona_confidence = max_score / total_score if total_score > 0 else 0.0
    
    def _get_relevant_personas_for_signal(self, signal: PersonaSignal) -> List[UserPersonaType]:
        """Map signals to relevant persona types"""
        signal_persona_mapping = {
            "technical_query": [UserPersonaType.DEFI_DEVELOPER, UserPersonaType.RESEARCHER],
            "investment_interest": [UserPersonaType.INVESTOR, UserPersonaType.ENTREPRENEUR],
            "learning_focus": [UserPersonaType.STUDENT, UserPersonaType.CASUAL_EXPLORER],
            "industry_terminology": [UserPersonaType.INDUSTRY_PROFESSIONAL, UserPersonaType.DEFI_DEVELOPER],
            "protocol_questions": [UserPersonaType.DEFI_DEVELOPER, UserPersonaType.CRYPTO_ENTHUSIAST],
            "market_analysis": [UserPersonaType.INVESTOR, UserPersonaType.RESEARCHER],
            "networking_interest": [UserPersonaType.ENTREPRENEUR, UserPersonaType.INDUSTRY_PROFESSIONAL],
            "basic_questions": [UserPersonaType.STUDENT, UserPersonaType.CASUAL_EXPLORER]
        }
        
        return signal_persona_mapping.get(signal.signal_type, [])
    
    def get_personalization_preferences(self) -> Dict[str, Any]:
        """Get preferences for personalizing responses"""
        return {
            "detail_level": self._get_preferred_detail_level(),
            "technical_depth": self._get_preferred_technical_depth(),
            "content_focus": self._get_preferred_content_focus(),
            "interaction_style": self._get_preferred_interaction_style(),
            "priority_topics": self.interests[:5],  # Top 5 interests
            "expertise_areas": self.expertise_areas
        }
    
    def _get_preferred_detail_level(self) -> str:
        """Determine preferred level of detail based on persona"""
        detail_preferences = {
            UserPersonaType.RESEARCHER: "comprehensive",
            UserPersonaType.DEFI_DEVELOPER: "technical",
            UserPersonaType.STUDENT: "educational",
            UserPersonaType.CASUAL_EXPLORER: "overview",
            UserPersonaType.INVESTOR: "focused",
            UserPersonaType.ENTREPRENEUR: "actionable",
            UserPersonaType.INDUSTRY_PROFESSIONAL: "professional",
            UserPersonaType.CRYPTO_ENTHUSIAST: "detailed"
        }
        return detail_preferences.get(self.primary_persona, "balanced")
    
    def _get_preferred_technical_depth(self) -> str:
        """Determine preferred technical depth"""
        if self.experience_level == ExperienceLevel.EXPERT:
            return "deep"
        elif self.experience_level == ExperienceLevel.ADVANCED:
            return "moderate"
        elif self.experience_level == ExperienceLevel.INTERMEDIATE:
            return "basic"
        else:
            return "minimal"
    
    def _get_preferred_content_focus(self) -> List[str]:
        """Get preferred content focus areas"""
        focus_mapping = {
            UserPersonaType.CRYPTO_ENTHUSIAST: ["protocols", "technology", "community"],
            UserPersonaType.DEFI_DEVELOPER: ["technical", "development", "tools"],
            UserPersonaType.INVESTOR: ["market", "opportunities", "roi"],
            UserPersonaType.RESEARCHER: ["analysis", "trends", "data"],
            UserPersonaType.ENTREPRENEUR: ["business", "networking", "partnerships"],
            UserPersonaType.STUDENT: ["education", "fundamentals", "learning"],
            UserPersonaType.INDUSTRY_PROFESSIONAL: ["industry", "professional", "standards"],
            UserPersonaType.CASUAL_EXPLORER: ["overview", "introduction", "accessible"]
        }
        return focus_mapping.get(self.primary_persona, ["general"])
    
    def _get_preferred_interaction_style(self) -> str:
        """Get preferred interaction style"""
        style_mapping = {
            EngagementStyle.DETAILED: "comprehensive_responses",
            EngagementStyle.QUICK_OVERVIEW: "concise_summaries",
            EngagementStyle.INTERACTIVE: "question_driven",
            EngagementStyle.RESEARCH_FOCUSED: "data_heavy"
        }
        return style_mapping.get(self.engagement_style, "balanced")
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize persona to dictionary"""
        return {
            "user_id": self.user_id,
            "primary_persona": self.primary_persona.value,
            "persona_confidence": self.persona_confidence,
            "experience_level": self.experience_level.value,
            "engagement_style": self.engagement_style.value,
            "interests": self.interests,
            "expertise_areas": self.expertise_areas,
            "preferred_content_types": self.preferred_content_types,
            "activity_patterns": self.activity_patterns,
            "signals": [signal.to_dict() for signal in self.signals],
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "update_count": self.update_count,
            "prediction_accuracy": self.prediction_accuracy,
            "adaptation_rate": self.adaptation_rate
        }

class PersonaDetector:
    """Detects and analyzes user personas from conversation patterns"""
    
    def __init__(self):
        self.signal_extractors = self._initialize_signal_extractors()
        self.persona_thresholds = self._initialize_persona_thresholds()
    
    def _initialize_signal_extractors(self) -> Dict[str, Any]:
        """Initialize signal extraction patterns"""
        return {
            "technical_terminology": {
                "patterns": [
                    r"(?:smart contract|solidity|web3|defi|protocol|dapp|gas|liquidity|yield|staking)",
                    r"(?:consensus|proof of stake|proof of work|merkle|hash|nonce)",
                    r"(?:evm|ethereum|polygon|arbitrum|optimism|layer 2)"
                ],
                "weight": 0.8,
                "persona_signals": ["technical_query", "protocol_questions"]
            },
            
            "investment_language": {
                "patterns": [
                    r"(?:investment|portfolio|roi|returns|market cap|tokenomics)",
                    r"(?:price|valuation|funding|venture|capital|vc)",
                    r"(?:apy|yield|farming|staking rewards|liquidity mining)"
                ],
                "weight": 0.7,
                "persona_signals": ["investment_interest", "market_analysis"]
            },
            
            "learning_indicators": {
                "patterns": [
                    r"(?:what is|how does|can you explain|i don't understand)",
                    r"(?:learn|study|beginner|new to|getting started)",
                    r"(?:tutorial|guide|introduction|basics|fundamentals)"
                ],
                "weight": 0.6,
                "persona_signals": ["learning_focus", "basic_questions"]
            },
            
            "professional_context": {
                "patterns": [
                    r"(?:company|enterprise|business|industry|professional)",
                    r"(?:compliance|regulation|legal|institutional)",
                    r"(?:corporate|enterprise|b2b|saas|platform)"
                ],
                "weight": 0.7,
                "persona_signals": ["industry_terminology"]
            },
            
            "networking_interest": {
                "patterns": [
                    r"(?:networking|meet|connect|partnership|collaboration)",
                    r"(?:team|founder|ceo|cto|developer|engineer)",
                    r"(?:conference|meetup|event|workshop|summit)"
                ],
                "weight": 0.6,
                "persona_signals": ["networking_interest"]
            }
        }
    
    def _initialize_persona_thresholds(self) -> Dict[str, float]:
        """Initialize confidence thresholds for persona detection"""
        return {
            "minimum_confidence": 0.3,      # Minimum confidence to assign persona
            "high_confidence": 0.7,         # High confidence threshold
            "adaptation_threshold": 0.1,    # Minimum change to trigger adaptation
            "signal_decay_days": 30         # Days after which signals start decaying
        }
    
    async def analyze_conversation_for_signals(
        self,
        user_message: str,
        conversation_state: ConversationState,
        context: Dict[str, Any] = None
    ) -> List[PersonaSignal]:
        """Analyze conversation for persona signals"""
        signals = []
        message_lower = user_message.lower()
        
        # Extract technical signals
        tech_signals = await self._extract_technical_signals(message_lower)
        signals.extend(tech_signals)
        
        # Extract behavioral signals
        behavioral_signals = await self._extract_behavioral_signals(
            user_message, conversation_state
        )
        signals.extend(behavioral_signals)
        
        # Extract interaction pattern signals
        interaction_signals = await self._extract_interaction_signals(
            conversation_state, context or {}
        )
        signals.extend(interaction_signals)
        
        # Extract temporal pattern signals
        temporal_signals = await self._extract_temporal_signals(conversation_state)
        signals.extend(temporal_signals)
        
        return signals
    
    async def _extract_technical_signals(self, message: str) -> List[PersonaSignal]:
        """Extract technical knowledge signals"""
        signals = []
        
        for signal_type, config in self.signal_extractors.items():
            for pattern in config["patterns"]:
                if any(term in message for term in pattern.split("|")):
                    for persona_signal in config["persona_signals"]:
                        signals.append(PersonaSignal(
                            signal_type=persona_signal,
                            value=signal_type,
                            confidence=config["weight"],
                            timestamp=datetime.utcnow(),
                            source="technical_analysis",
                            weight=config["weight"]
                        ))
        
        return signals
    
    async def _extract_behavioral_signals(
        self,
        user_message: str,
        conversation_state: ConversationState
    ) -> List[PersonaSignal]:
        """Extract behavioral pattern signals"""
        signals = []
        
        # Analyze question complexity
        question_complexity = self._analyze_question_complexity(user_message)
        if question_complexity:
            signals.append(PersonaSignal(
                signal_type="question_complexity",
                value=question_complexity,
                confidence=0.6,
                timestamp=datetime.utcnow(),
                source="behavioral_analysis"
            ))
        
        # Analyze follow-up patterns
        if conversation_state.turn_count > 3:
            follow_up_pattern = self._analyze_follow_up_pattern(conversation_state)
            if follow_up_pattern:
                signals.append(PersonaSignal(
                    signal_type="follow_up_pattern",
                    value=follow_up_pattern,
                    confidence=0.5,
                    timestamp=datetime.utcnow(),
                    source="behavioral_analysis"
                ))
        
        return signals
    
    async def _extract_interaction_signals(
        self,
        conversation_state: ConversationState,
        context: Dict[str, Any]
    ) -> List[PersonaSignal]:
        """Extract interaction style signals"""
        signals = []
        
        # Analyze response preferences
        if context.get("api_response"):
            response_engagement = self._analyze_response_engagement(
                context["api_response"], conversation_state
            )
            if response_engagement:
                signals.append(PersonaSignal(
                    signal_type="response_engagement",
                    value=response_engagement,
                    confidence=0.4,
                    timestamp=datetime.utcnow(),
                    source="interaction_analysis"
                ))
        
        return signals
    
    async def _extract_temporal_signals(
        self,
        conversation_state: ConversationState
    ) -> List[PersonaSignal]:
        """Extract temporal pattern signals"""
        signals = []
        
        # Analyze session patterns
        if conversation_state.turn_count >= 5:
            session_intensity = self._calculate_session_intensity(conversation_state)
            signals.append(PersonaSignal(
                signal_type="session_intensity",
                value=session_intensity,
                confidence=0.3,
                timestamp=datetime.utcnow(),
                source="temporal_analysis"
            ))
        
        return signals
    
    def _analyze_question_complexity(self, message: str) -> Optional[str]:
        """Analyze the complexity level of user questions"""
        # Simple heuristics for question complexity
        word_count = len(message.split())
        technical_terms = sum(1 for term in ["protocol", "smart contract", "defi", "liquidity", "yield", "gas", "consensus"] if term in message.lower())
        
        if technical_terms >= 3 or word_count > 30:
            return "complex"
        elif technical_terms >= 1 or word_count > 15:
            return "moderate"
        else:
            return "simple"
    
    def _analyze_follow_up_pattern(self, conversation_state: ConversationState) -> Optional[str]:
        """Analyze user's follow-up question patterns"""
        recent_intents = conversation_state.get_recent_intents(5)
        
        if len(recent_intents) >= 3:
            # Check for deep-diving pattern
            if all(intent.intent == recent_intents[0].intent for intent in recent_intents[:3]):
                return "deep_dive"
            
            # Check for broad exploration pattern
            unique_intents = len(set(intent.intent for intent in recent_intents))
            if unique_intents >= 3:
                return "broad_exploration"
        
        return None
    
    def _analyze_response_engagement(
        self,
        api_response: Dict[str, Any],
        conversation_state: ConversationState
    ) -> Optional[str]:
        """Analyze how user engages with responses"""
        # This would be enhanced with actual user interaction data
        tools_used = api_response.get("tools_used", [])
        
        if len(tools_used) > 1:
            return "thorough_researcher"
        elif tools_used:
            return "focused_searcher"
        else:
            return "quick_browser"
    
    def _calculate_session_intensity(self, conversation_state: ConversationState) -> str:
        """Calculate conversation session intensity"""
        time_span = conversation_state.last_activity - conversation_state.created_at
        turns_per_minute = conversation_state.turn_count / (time_span.total_seconds() / 60) if time_span.total_seconds() > 0 else 0
        
        if turns_per_minute > 2:
            return "high"
        elif turns_per_minute > 1:
            return "moderate"
        else:
            return "low"

class PersonaManager:
    """Manages user personas across the application"""
    
    def __init__(self):
        self.detector = PersonaDetector()
        self.active_personas: Dict[str, UserPersona] = {}
        self.persona_persistence = None  # Will be injected
    
    async def get_or_create_persona(self, user_id: str) -> UserPersona:
        """Get existing persona or create new one"""
        if user_id not in self.active_personas:
            # Try to load from persistence
            if self.persona_persistence and hasattr(self.persona_persistence, 'load_user_persona'):
                persona = await self.persona_persistence.load_user_persona(user_id)
                if persona:
                    self.active_personas[user_id] = persona
                else:
                    self.active_personas[user_id] = UserPersona(
                        user_id=user_id,
                        primary_persona=UserPersonaType.CASUAL_EXPLORER,
                        persona_confidence=0.1,
                        experience_level=ExperienceLevel.BEGINNER,
                        engagement_style=EngagementStyle.QUICK_OVERVIEW
                    )
            else:
                self.active_personas[user_id] = UserPersona(
                    user_id=user_id,
                    primary_persona=UserPersonaType.CASUAL_EXPLORER,
                    persona_confidence=0.1,
                    experience_level=ExperienceLevel.BEGINNER,
                    engagement_style=EngagementStyle.QUICK_OVERVIEW
                )
        
        return self.active_personas[user_id]
    
    async def update_persona_from_conversation(
        self,
        user_id: str,
        user_message: str,
        conversation_state: ConversationState,
        context: Dict[str, Any] = None
    ) -> UserPersona:
        """Update user persona based on conversation"""
        persona = await self.get_or_create_persona(user_id)
        
        # Extract new signals
        new_signals = await self.detector.analyze_conversation_for_signals(
            user_message, conversation_state, context
        )
        
        # Update persona with new signals
        if new_signals:
            persona.update_persona(new_signals)
            
            # Persist updated persona
            if self.persona_persistence and hasattr(self.persona_persistence, 'save_user_persona'):
                await self.persona_persistence.save_user_persona(user_id, persona)
        
        return persona
    
    async def get_personalization_context(self, user_id: str) -> Dict[str, Any]:
        """Get personalization context for response customization"""
        persona = await self.get_or_create_persona(user_id)
        
        return {
            "persona_type": persona.primary_persona.value,
            "confidence": persona.persona_confidence,
            "experience_level": persona.experience_level.value,
            "preferences": persona.get_personalization_preferences(),
            "interests": persona.interests,
            "expertise_areas": persona.expertise_areas
        }
    
    async def get_persona_metrics(self) -> Dict[str, Any]:
        """Get persona analysis metrics for monitoring"""
        if not self.active_personas:
            return {"total_personas": 0}
        
        persona_distribution = {}
        experience_distribution = {}
        confidence_scores = []
        
        for persona in self.active_personas.values():
            # Persona type distribution
            persona_type = persona.primary_persona.value
            persona_distribution[persona_type] = persona_distribution.get(persona_type, 0) + 1
            
            # Experience level distribution
            exp_level = persona.experience_level.value
            experience_distribution[exp_level] = experience_distribution.get(exp_level, 0) + 1
            
            # Confidence scores
            confidence_scores.append(persona.persona_confidence)
        
        return {
            "total_personas": len(self.active_personas),
            "persona_distribution": persona_distribution,
            "experience_distribution": experience_distribution,
            "average_confidence": sum(confidence_scores) / len(confidence_scores),
            "high_confidence_personas": sum(1 for score in confidence_scores if score > 0.7),
            "persona_adaptation_target": 0.4,  # 40% of users should have personalized experience
            "personalization_achieved": sum(1 for score in confidence_scores if score > 0.4) / len(confidence_scores)
        }

# Global instance for shared access
persona_manager = PersonaManager()