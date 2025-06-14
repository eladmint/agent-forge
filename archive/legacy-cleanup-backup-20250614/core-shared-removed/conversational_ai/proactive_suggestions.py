# Conversational AI Proactive Suggestion Engine
# Intelligent next-step recommendations and user guidance system

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict, Counter

from .state_management import ConversationState
from .pattern_recognition import PatternMatch, ConversationPattern
from .persona_modeling import UserPersona, UserPersonaType, ExperienceLevel, EngagementStyle

class SuggestionType(Enum):
    """Types of proactive suggestions"""
    NEXT_STEP = "next_step"                    # Suggest logical next step
    RELATED_TOPIC = "related_topic"            # Suggest related exploration
    CLARIFICATION = "clarification"            # Suggest clarification needed
    DEEP_DIVE = "deep_dive"                   # Suggest deeper exploration
    COMPARISON = "comparison"                  # Suggest comparing options
    PRACTICAL_APPLICATION = "practical_application"  # Suggest practical use
    LEARNING_PATH = "learning_path"            # Suggest learning progression
    GOAL_REFINEMENT = "goal_refinement"        # Suggest refining goals

class SuggestionPriority(Enum):
    """Priority levels for suggestions"""
    HIGH = "high"      # Immediately relevant and important
    MEDIUM = "medium"  # Relevant and helpful
    LOW = "low"        # Optional but potentially useful

@dataclass
class ProactiveSuggestion:
    """Individual proactive suggestion"""
    suggestion_type: SuggestionType
    priority: SuggestionPriority
    content: str
    reasoning: str
    confidence: float
    
    # Suggestion metadata
    triggers: List[str]  # What triggered this suggestion
    persona_alignment: float  # How well it aligns with user persona
    context_relevance: float  # How relevant to current context
    timing_score: float  # How well-timed the suggestion is
    
    # Action information
    suggested_action: Optional[str] = None
    expected_benefit: str = ""
    estimated_value: float = 0.0  # 0-1 scale of expected value to user
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "suggestion_type": self.suggestion_type.value,
            "priority": self.priority.value,
            "content": self.content,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
            "triggers": self.triggers,
            "persona_alignment": self.persona_alignment,
            "context_relevance": self.context_relevance,
            "timing_score": self.timing_score,
            "suggested_action": self.suggested_action,
            "expected_benefit": self.expected_benefit,
            "estimated_value": self.estimated_value
        }

@dataclass
class SuggestionContext:
    """Context for generating suggestions"""
    conversation_state: ConversationState
    user_persona: UserPersona
    current_pattern: Optional[PatternMatch]
    conversation_history: List[Dict[str, Any]]
    api_context: Dict[str, Any]
    
    # Timing factors
    time_since_last_suggestion: timedelta
    conversation_momentum: str  # "high", "medium", "low"
    user_engagement_level: str  # "high", "medium", "low"

class ProactiveSuggestionEngine:
    """Provides intelligent next-step recommendations and user guidance"""
    
    def __init__(self):
        self.suggestion_templates = self._initialize_suggestion_templates()
        self.persona_suggestion_mapping = self._initialize_persona_mapping()
        self.pattern_suggestion_mapping = self._initialize_pattern_mapping()
        self.suggestion_history: Dict[str, List[ProactiveSuggestion]] = defaultdict(list)
        self.suggestion_effectiveness: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
    
    def _initialize_suggestion_templates(self) -> Dict[SuggestionType, Dict[str, Any]]:
        """Initialize suggestion templates and patterns"""
        return {
            SuggestionType.NEXT_STEP: {
                "templates": [
                    "Based on your interest in {topic}, would you like me to {action}?",
                    "Since you're exploring {topic}, I can help you {action}.",
                    "The next logical step would be to {action}. Shall I help you with that?"
                ],
                "actions": {
                    "event_search": "find specific events in this area",
                    "speaker_lookup": "look up speakers who specialize in this topic",
                    "registration": "help you register for relevant events",
                    "detailed_info": "provide more detailed information"
                },
                "confidence_base": 0.8
            },
            
            SuggestionType.RELATED_TOPIC: {
                "templates": [
                    "Since you're interested in {current_topic}, you might also want to explore {related_topic}.",
                    "People interested in {current_topic} often also look into {related_topic}.",
                    "Would you like to see what's happening in {related_topic} as well?"
                ],
                "related_mappings": {
                    "defi": ["yield farming", "liquidity mining", "protocol governance"],
                    "nft": ["digital art", "gaming", "metaverse"],
                    "blockchain": ["smart contracts", "consensus mechanisms", "scalability"],
                    "crypto": ["trading", "investment strategies", "market analysis"],
                    "conference": ["networking events", "workshops", "meetups"]
                },
                "confidence_base": 0.6
            },
            
            SuggestionType.CLARIFICATION: {
                "templates": [
                    "Would you like me to clarify {unclear_aspect}?",
                    "I can provide more details about {unclear_aspect} if that would help.",
                    "Should I explain {unclear_aspect} in more depth?"
                ],
                "triggers": [
                    "technical_terms_used",
                    "complex_concepts_mentioned",
                    "user_confusion_detected",
                    "incomplete_information_provided"
                ],
                "confidence_base": 0.7
            },
            
            SuggestionType.DEEP_DIVE: {
                "templates": [
                    "Would you like me to dive deeper into {topic}?",
                    "I can provide comprehensive information about {topic} if you're interested.",
                    "There's much more to explore about {topic}. Would you like to learn more?"
                ],
                "triggers": [
                    "sustained_interest_in_topic",
                    "multiple_questions_same_area",
                    "expert_persona_detected"
                ],
                "confidence_base": 0.7
            },
            
            SuggestionType.COMPARISON: {
                "templates": [
                    "Would you like me to compare {option1} with {option2}?",
                    "I can help you see the differences between {option1} and {option2}.",
                    "Comparing {option1} and {option2} might help you decide."
                ],
                "triggers": [
                    "multiple_options_presented",
                    "decision_making_context",
                    "comparison_keywords_used"
                ],
                "confidence_base": 0.6
            },
            
            SuggestionType.PRACTICAL_APPLICATION: {
                "templates": [
                    "Would you like to see how {concept} works in practice?",
                    "I can show you real-world applications of {concept}.",
                    "Here are some practical examples of {concept} you might find useful."
                ],
                "triggers": [
                    "theoretical_discussion",
                    "learning_persona_detected",
                    "how_to_questions"
                ],
                "confidence_base": 0.6
            },
            
            SuggestionType.LEARNING_PATH: {
                "templates": [
                    "Based on your current knowledge, the next step in learning {topic} would be {next_step}.",
                    "To build on what you know about {topic}, I recommend exploring {next_step}.",
                    "Your learning journey in {topic} could continue with {next_step}."
                ],
                "learning_paths": {
                    "blockchain_beginner": ["basic_concepts", "consensus_mechanisms", "smart_contracts", "dapps"],
                    "defi_intermediate": ["advanced_protocols", "yield_strategies", "risk_management", "governance"],
                    "crypto_advanced": ["institutional_trading", "market_making", "derivatives", "regulation"]
                },
                "confidence_base": 0.8
            },
            
            SuggestionType.GOAL_REFINEMENT: {
                "templates": [
                    "To better help you, could you clarify {aspect_to_clarify}?",
                    "It would help if you could be more specific about {aspect_to_clarify}.",
                    "What's most important to you regarding {aspect_to_clarify}?"
                ],
                "refinement_aspects": [
                    "your timeline",
                    "your budget constraints",
                    "your experience level",
                    "your specific goals",
                    "your location preferences"
                ],
                "confidence_base": 0.7
            }
        }
    
    def _initialize_persona_mapping(self) -> Dict[UserPersonaType, Dict[str, Any]]:
        """Initialize persona-specific suggestion preferences"""
        return {
            UserPersonaType.CRYPTO_ENTHUSIAST: {
                "preferred_suggestions": [
                    SuggestionType.RELATED_TOPIC,
                    SuggestionType.DEEP_DIVE,
                    SuggestionType.COMPARISON
                ],
                "engagement_style": "discovery_focused",
                "information_depth": "detailed",
                "suggestion_frequency": "high"
            },
            
            UserPersonaType.DEFI_DEVELOPER: {
                "preferred_suggestions": [
                    SuggestionType.DEEP_DIVE,
                    SuggestionType.PRACTICAL_APPLICATION,
                    SuggestionType.NEXT_STEP
                ],
                "engagement_style": "technical_focused",
                "information_depth": "comprehensive",
                "suggestion_frequency": "medium"
            },
            
            UserPersonaType.INVESTOR: {
                "preferred_suggestions": [
                    SuggestionType.COMPARISON,
                    SuggestionType.NEXT_STEP,
                    SuggestionType.GOAL_REFINEMENT
                ],
                "engagement_style": "decision_focused",
                "information_depth": "targeted",
                "suggestion_frequency": "medium"
            },
            
            UserPersonaType.RESEARCHER: {
                "preferred_suggestions": [
                    SuggestionType.DEEP_DIVE,
                    SuggestionType.RELATED_TOPIC,
                    SuggestionType.COMPARISON
                ],
                "engagement_style": "comprehensive_exploration",
                "information_depth": "exhaustive",
                "suggestion_frequency": "high"
            },
            
            UserPersonaType.STUDENT: {
                "preferred_suggestions": [
                    SuggestionType.LEARNING_PATH,
                    SuggestionType.CLARIFICATION,
                    SuggestionType.PRACTICAL_APPLICATION
                ],
                "engagement_style": "learning_focused",
                "information_depth": "educational",
                "suggestion_frequency": "high"
            },
            
            UserPersonaType.ENTREPRENEUR: {
                "preferred_suggestions": [
                    SuggestionType.NEXT_STEP,
                    SuggestionType.PRACTICAL_APPLICATION,
                    SuggestionType.GOAL_REFINEMENT
                ],
                "engagement_style": "action_focused",
                "information_depth": "actionable",
                "suggestion_frequency": "medium"
            },
            
            UserPersonaType.INDUSTRY_PROFESSIONAL: {
                "preferred_suggestions": [
                    SuggestionType.COMPARISON,
                    SuggestionType.NEXT_STEP,
                    SuggestionType.DEEP_DIVE
                ],
                "engagement_style": "professional_focused",
                "information_depth": "comprehensive",
                "suggestion_frequency": "medium"
            },
            
            UserPersonaType.CASUAL_EXPLORER: {
                "preferred_suggestions": [
                    SuggestionType.RELATED_TOPIC,
                    SuggestionType.CLARIFICATION,
                    SuggestionType.NEXT_STEP
                ],
                "engagement_style": "discovery_focused",
                "information_depth": "accessible",
                "suggestion_frequency": "low"
            }
        }
    
    def _initialize_pattern_mapping(self) -> Dict[ConversationPattern, List[SuggestionType]]:
        """Initialize pattern-based suggestion mappings"""
        return {
            ConversationPattern.DEEP_DIVE: [
                SuggestionType.DEEP_DIVE,
                SuggestionType.PRACTICAL_APPLICATION,
                SuggestionType.RELATED_TOPIC
            ],
            ConversationPattern.EXPLORATION: [
                SuggestionType.RELATED_TOPIC,
                SuggestionType.COMPARISON,
                SuggestionType.NEXT_STEP
            ],
            ConversationPattern.CLARIFICATION_CASCADE: [
                SuggestionType.CLARIFICATION,
                SuggestionType.PRACTICAL_APPLICATION,
                SuggestionType.GOAL_REFINEMENT
            ],
            ConversationPattern.GOAL_ORIENTED: [
                SuggestionType.NEXT_STEP,
                SuggestionType.GOAL_REFINEMENT,
                SuggestionType.COMPARISON
            ],
            ConversationPattern.LEARNING_JOURNEY: [
                SuggestionType.LEARNING_PATH,
                SuggestionType.PRACTICAL_APPLICATION,
                SuggestionType.DEEP_DIVE
            ],
            ConversationPattern.RESEARCH_MODE: [
                SuggestionType.DEEP_DIVE,
                SuggestionType.COMPARISON,
                SuggestionType.RELATED_TOPIC
            ],
            ConversationPattern.COMPARISON_SHOPPING: [
                SuggestionType.COMPARISON,
                SuggestionType.NEXT_STEP,
                SuggestionType.GOAL_REFINEMENT
            ],
            ConversationPattern.TROUBLESHOOTING: [
                SuggestionType.CLARIFICATION,
                SuggestionType.NEXT_STEP,
                SuggestionType.PRACTICAL_APPLICATION
            ]
        }
    
    async def generate_suggestions(
        self,
        conversation_state: ConversationState,
        pattern_data: Optional[PatternMatch],
        persona: UserPersona,
        api_context: Dict[str, Any] = None
    ) -> List[ProactiveSuggestion]:
        """Generate contextual suggestions for user"""
        
        # Create suggestion context
        suggestion_context = await self._create_suggestion_context(
            conversation_state, persona, pattern_data, api_context or {}
        )
        
        # Check if suggestions should be provided
        if not await self.should_provide_suggestions(conversation_state, suggestion_context):
            return []
        
        # Generate suggestions based on different factors
        suggestions = []
        
        # Pattern-based suggestions
        if pattern_data:
            pattern_suggestions = await self._generate_pattern_suggestions(
                pattern_data, suggestion_context
            )
            suggestions.extend(pattern_suggestions)
        
        # Persona-based suggestions
        persona_suggestions = await self._generate_persona_suggestions(
            persona, suggestion_context
        )
        suggestions.extend(persona_suggestions)
        
        # Context-based suggestions
        context_suggestions = await self._generate_context_suggestions(
            conversation_state, suggestion_context
        )
        suggestions.extend(context_suggestions)
        
        # API-based suggestions
        if api_context:
            api_suggestions = await self._generate_api_suggestions(
                api_context, suggestion_context
            )
            suggestions.extend(api_suggestions)
        
        # Deduplicate and rank suggestions
        final_suggestions = await self._rank_and_filter_suggestions(
            suggestions, suggestion_context
        )
        
        # Store suggestions for learning
        user_id = conversation_state.user_id
        self.suggestion_history[user_id].extend(final_suggestions)
        
        return final_suggestions[:3]  # Return top 3 suggestions
    
    async def should_provide_suggestions(
        self,
        conversation_state: ConversationState,
        suggestion_context: SuggestionContext
    ) -> bool:
        """Determine when to offer proactive assistance"""
        
        # Don't suggest too frequently
        if suggestion_context.time_since_last_suggestion < timedelta(minutes=2):
            return False
        
        # Don't suggest if user is highly engaged and moving quickly
        if (suggestion_context.conversation_momentum == "high" and 
            suggestion_context.user_engagement_level == "high"):
            return False
        
        # Always suggest if user seems confused
        if conversation_state.clarification_requests > 2:
            return True
        
        # Suggest based on conversation patterns
        if suggestion_context.current_pattern:
            pattern_confidence = suggestion_context.current_pattern.confidence
            if pattern_confidence > 0.7:
                return True
        
        # Suggest for learning-focused personas
        if suggestion_context.user_persona.primary_persona in [
            UserPersonaType.STUDENT, UserPersonaType.RESEARCHER, UserPersonaType.CASUAL_EXPLORER
        ]:
            return True
        
        # Suggest if conversation has stalled
        if suggestion_context.conversation_momentum == "low":
            return True
        
        # Default to occasional suggestions
        return conversation_state.turn_count % 5 == 0  # Every 5 turns
    
    async def _create_suggestion_context(
        self,
        conversation_state: ConversationState,
        persona: UserPersona,
        pattern_data: Optional[PatternMatch],
        api_context: Dict[str, Any]
    ) -> SuggestionContext:
        """Create comprehensive context for suggestion generation"""
        
        # Calculate time since last suggestion
        last_suggestion_time = self._get_last_suggestion_time(conversation_state.user_id)
        time_since_last = datetime.utcnow() - last_suggestion_time if last_suggestion_time else timedelta(hours=1)
        
        # Assess conversation momentum
        momentum = self._assess_conversation_momentum(conversation_state)
        
        # Assess user engagement
        engagement = self._assess_user_engagement(conversation_state)
        
        return SuggestionContext(
            conversation_state=conversation_state,
            user_persona=persona,
            current_pattern=pattern_data,
            conversation_history=conversation_state.conversation_memory,
            api_context=api_context,
            time_since_last_suggestion=time_since_last,
            conversation_momentum=momentum,
            user_engagement_level=engagement
        )
    
    async def _generate_pattern_suggestions(
        self,
        pattern_match: PatternMatch,
        context: SuggestionContext
    ) -> List[ProactiveSuggestion]:
        """Generate suggestions based on detected conversation pattern"""
        
        suggestions = []
        pattern_type = pattern_match.pattern
        
        # Get suggestion types for this pattern
        suggestion_types = self.pattern_suggestion_mapping.get(pattern_type, [])
        
        for suggestion_type in suggestion_types:
            suggestion = await self._create_pattern_suggestion(
                suggestion_type, pattern_match, context
            )
            if suggestion:
                suggestions.append(suggestion)
        
        return suggestions
    
    async def _generate_persona_suggestions(
        self,
        persona: UserPersona,
        context: SuggestionContext
    ) -> List[ProactiveSuggestion]:
        """Generate suggestions based on user persona"""
        
        suggestions = []
        persona_mapping = self.persona_suggestion_mapping.get(persona.primary_persona, {})
        preferred_types = persona_mapping.get("preferred_suggestions", [])
        
        for suggestion_type in preferred_types:
            suggestion = await self._create_persona_suggestion(
                suggestion_type, persona, context
            )
            if suggestion:
                suggestions.append(suggestion)
        
        return suggestions
    
    async def _generate_context_suggestions(
        self,
        conversation_state: ConversationState,
        context: SuggestionContext
    ) -> List[ProactiveSuggestion]:
        """Generate suggestions based on conversation context"""
        
        suggestions = []
        
        # Suggest clarification if user seems confused
        if conversation_state.clarification_requests > 1:
            clarification_suggestion = await self._create_clarification_suggestion(context)
            if clarification_suggestion:
                suggestions.append(clarification_suggestion)
        
        # Suggest next steps if user has clear goals
        if conversation_state.successful_resolutions > 0:
            next_step_suggestion = await self._create_next_step_suggestion(context)
            if next_step_suggestion:
                suggestions.append(next_step_suggestion)
        
        # Suggest related topics if user is exploring
        if len(conversation_state.get_primary_interests()) > 1:
            related_topic_suggestion = await self._create_related_topic_suggestion(context)
            if related_topic_suggestion:
                suggestions.append(related_topic_suggestion)
        
        return suggestions
    
    async def _generate_api_suggestions(
        self,
        api_context: Dict[str, Any],
        context: SuggestionContext
    ) -> List[ProactiveSuggestion]:
        """Generate suggestions based on API response context"""
        
        suggestions = []
        
        # Suggest deep dive if comprehensive results returned
        if api_context.get("result_count", 0) > 5:
            deep_dive_suggestion = await self._create_api_deep_dive_suggestion(api_context, context)
            if deep_dive_suggestion:
                suggestions.append(deep_dive_suggestion)
        
        # Suggest comparison if multiple similar options
        if api_context.get("similar_results", 0) > 2:
            comparison_suggestion = await self._create_api_comparison_suggestion(api_context, context)
            if comparison_suggestion:
                suggestions.append(comparison_suggestion)
        
        # Suggest refinement if results are too broad
        if api_context.get("result_diversity", 0) > 0.8:
            refinement_suggestion = await self._create_api_refinement_suggestion(api_context, context)
            if refinement_suggestion:
                suggestions.append(refinement_suggestion)
        
        return suggestions
    
    async def _create_pattern_suggestion(
        self,
        suggestion_type: SuggestionType,
        pattern_match: PatternMatch,
        context: SuggestionContext
    ) -> Optional[ProactiveSuggestion]:
        """Create suggestion based on conversation pattern"""
        
        template_config = self.suggestion_templates.get(suggestion_type, {})
        templates = template_config.get("templates", [])
        
        if not templates:
            return None
        
        # Select appropriate template
        template = templates[0]  # Use first template for now
        
        # Extract context for template
        current_topic = self._extract_current_topic(context.conversation_state)
        
        # Generate content based on pattern and suggestion type
        if suggestion_type == SuggestionType.DEEP_DIVE:
            content = f"Since you're showing sustained interest in {current_topic}, would you like me to provide more comprehensive information about this topic?"
            reasoning = f"Pattern detection shows deep dive behavior with {pattern_match.confidence:.1%} confidence"
            suggested_action = "provide_comprehensive_information"
            
        elif suggestion_type == SuggestionType.RELATED_TOPIC:
            related_topics = self._get_related_topics(current_topic)
            if related_topics:
                related_topic = related_topics[0]
                content = f"Since you're exploring {current_topic}, you might also be interested in {related_topic}."
                reasoning = f"Pattern shows exploratory behavior, suggesting related topic expansion"
                suggested_action = "explore_related_topic"
            else:
                return None
        
        elif suggestion_type == SuggestionType.PRACTICAL_APPLICATION:
            content = f"Would you like to see practical examples of how {current_topic} is used in real-world scenarios?"
            reasoning = f"Pattern indicates interest in deeper understanding of {current_topic}"
            suggested_action = "show_practical_examples"
        
        else:
            return None
        
        # Calculate suggestion quality metrics
        persona_alignment = self._calculate_persona_alignment(suggestion_type, context.user_persona)
        context_relevance = pattern_match.confidence
        timing_score = self._calculate_timing_score(context)
        
        return ProactiveSuggestion(
            suggestion_type=suggestion_type,
            priority=SuggestionPriority.MEDIUM,
            content=content,
            reasoning=reasoning,
            confidence=pattern_match.confidence * 0.8,
            triggers=[f"pattern_{pattern_match.pattern.value}"],
            persona_alignment=persona_alignment,
            context_relevance=context_relevance,
            timing_score=timing_score,
            suggested_action=suggested_action,
            expected_benefit=f"Enhanced understanding of {current_topic}",
            estimated_value=0.7
        )
    
    async def _create_persona_suggestion(
        self,
        suggestion_type: SuggestionType,
        persona: UserPersona,
        context: SuggestionContext
    ) -> Optional[ProactiveSuggestion]:
        """Create suggestion based on user persona"""
        
        persona_config = self.persona_suggestion_mapping.get(persona.primary_persona, {})
        
        # Check if this suggestion type is preferred for this persona
        preferred_types = persona_config.get("preferred_suggestions", [])
        if suggestion_type not in preferred_types:
            return None
        
        current_topic = self._extract_current_topic(context.conversation_state)
        
        # Generate persona-specific content
        if suggestion_type == SuggestionType.LEARNING_PATH and persona.primary_persona == UserPersonaType.STUDENT:
            content = f"Based on your current exploration of {current_topic}, the next step in your learning journey could be to explore related fundamentals. Would you like me to guide you through this?"
            reasoning = f"Persona analysis shows learning-focused behavior with {persona.persona_confidence:.1%} confidence"
            suggested_action = "provide_learning_path"
            
        elif suggestion_type == SuggestionType.COMPARISON and persona.primary_persona == UserPersonaType.INVESTOR:
            content = f"As an investor exploring {current_topic}, you might want to compare different options available. Should I help you with a comparative analysis?"
            reasoning = f"Investor persona detected, suggesting decision-support comparison"
            suggested_action = "provide_comparison_analysis"
            
        elif suggestion_type == SuggestionType.DEEP_DIVE and persona.primary_persona == UserPersonaType.DEFI_DEVELOPER:
            content = f"Since you're technically focused, would you like me to dive into the technical specifications and implementation details of {current_topic}?"
            reasoning = f"Developer persona suggests preference for technical depth"
            suggested_action = "provide_technical_details"
            
        else:
            # Generic persona-based suggestion
            engagement_style = persona_config.get("engagement_style", "balanced")
            content = f"Based on your {engagement_style} approach to {current_topic}, would you like me to provide more targeted information?"
            reasoning = f"Suggestion tailored to {persona.primary_persona.value} persona characteristics"
            suggested_action = "provide_targeted_information"
        
        # Calculate suggestion quality metrics
        persona_alignment = 0.9  # High alignment since it's persona-based
        context_relevance = self._calculate_context_relevance(context)
        timing_score = self._calculate_timing_score(context)
        
        return ProactiveSuggestion(
            suggestion_type=suggestion_type,
            priority=SuggestionPriority.MEDIUM,
            content=content,
            reasoning=reasoning,
            confidence=persona.persona_confidence * 0.9,
            triggers=[f"persona_{persona.primary_persona.value}"],
            persona_alignment=persona_alignment,
            context_relevance=context_relevance,
            timing_score=timing_score,
            suggested_action=suggested_action,
            expected_benefit=f"Personalized assistance for {persona.primary_persona.value}",
            estimated_value=0.8
        )
    
    async def _create_clarification_suggestion(self, context: SuggestionContext) -> Optional[ProactiveSuggestion]:
        """Create clarification suggestion when user seems confused"""
        
        current_topic = self._extract_current_topic(context.conversation_state)
        clarification_count = context.conversation_state.clarification_requests
        
        content = f"I notice you've asked for clarification {clarification_count} times. Would you like me to explain {current_topic} in a different way or break it down into simpler concepts?"
        reasoning = f"User confusion detected ({clarification_count} clarification requests)"
        
        return ProactiveSuggestion(
            suggestion_type=SuggestionType.CLARIFICATION,
            priority=SuggestionPriority.HIGH,
            content=content,
            reasoning=reasoning,
            confidence=0.9,
            triggers=["clarification_cascade"],
            persona_alignment=self._calculate_persona_alignment(SuggestionType.CLARIFICATION, context.user_persona),
            context_relevance=0.9,
            timing_score=0.9,
            suggested_action="provide_simplified_explanation",
            expected_benefit="Reduced user confusion and improved understanding",
            estimated_value=0.9
        )
    
    async def _create_next_step_suggestion(self, context: SuggestionContext) -> Optional[ProactiveSuggestion]:
        """Create next step suggestion for goal-oriented users"""
        
        current_topic = self._extract_current_topic(context.conversation_state)
        
        # Determine logical next step based on context
        next_steps = {
            "event": "register for specific events",
            "conference": "explore speaker information or register",
            "defi": "look into specific protocols or yield opportunities",
            "nft": "explore marketplaces or collection details",
            "blockchain": "dive into specific use cases or implementations"
        }
        
        next_step = next_steps.get(current_topic.lower(), "explore related opportunities")
        
        content = f"Based on your exploration of {current_topic}, would you like me to help you {next_step}?"
        reasoning = f"User shows goal-oriented behavior with {context.conversation_state.successful_resolutions} successful resolutions"
        
        return ProactiveSuggestion(
            suggestion_type=SuggestionType.NEXT_STEP,
            priority=SuggestionPriority.MEDIUM,
            content=content,
            reasoning=reasoning,
            confidence=0.7,
            triggers=["goal_oriented_behavior"],
            persona_alignment=self._calculate_persona_alignment(SuggestionType.NEXT_STEP, context.user_persona),
            context_relevance=0.8,
            timing_score=self._calculate_timing_score(context),
            suggested_action="provide_next_step_guidance",
            expected_benefit="Progress toward user goals",
            estimated_value=0.8
        )
    
    async def _create_related_topic_suggestion(self, context: SuggestionContext) -> Optional[ProactiveSuggestion]:
        """Create related topic suggestion for exploratory users"""
        
        interests = context.conversation_state.get_primary_interests()
        if len(interests) < 2:
            return None
        
        current_topic = interests[0]
        related_topics = self._get_related_topics(current_topic)
        
        if not related_topics:
            return None
        
        related_topic = related_topics[0]
        
        content = f"Since you've shown interest in {current_topic}, you might also want to explore {related_topic}. They're closely related in the Web3 ecosystem."
        reasoning = f"User exploring multiple interests: {', '.join(interests[:3])}"
        
        return ProactiveSuggestion(
            suggestion_type=SuggestionType.RELATED_TOPIC,
            priority=SuggestionPriority.LOW,
            content=content,
            reasoning=reasoning,
            confidence=0.6,
            triggers=["exploration_behavior"],
            persona_alignment=self._calculate_persona_alignment(SuggestionType.RELATED_TOPIC, context.user_persona),
            context_relevance=0.6,
            timing_score=self._calculate_timing_score(context),
            suggested_action="explore_related_topic",
            expected_benefit="Broader understanding of related concepts",
            estimated_value=0.6
        )
    
    async def _create_api_deep_dive_suggestion(
        self,
        api_context: Dict[str, Any],
        context: SuggestionContext
    ) -> Optional[ProactiveSuggestion]:
        """Create deep dive suggestion based on API results"""
        
        result_count = api_context.get("result_count", 0)
        current_topic = self._extract_current_topic(context.conversation_state)
        
        content = f"I found {result_count} results for {current_topic}. Would you like me to provide detailed analysis of the most relevant options?"
        reasoning = f"Comprehensive API results ({result_count} items) suggest opportunity for detailed analysis"
        
        return ProactiveSuggestion(
            suggestion_type=SuggestionType.DEEP_DIVE,
            priority=SuggestionPriority.MEDIUM,
            content=content,
            reasoning=reasoning,
            confidence=0.7,
            triggers=["comprehensive_api_results"],
            persona_alignment=self._calculate_persona_alignment(SuggestionType.DEEP_DIVE, context.user_persona),
            context_relevance=0.8,
            timing_score=0.8,
            suggested_action="provide_detailed_analysis",
            expected_benefit="Comprehensive understanding of available options",
            estimated_value=0.7
        )
    
    async def _create_api_comparison_suggestion(
        self,
        api_context: Dict[str, Any],
        context: SuggestionContext
    ) -> Optional[ProactiveSuggestion]:
        """Create comparison suggestion based on API results"""
        
        similar_count = api_context.get("similar_results", 0)
        current_topic = self._extract_current_topic(context.conversation_state)
        
        content = f"I found {similar_count} similar options for {current_topic}. Would you like me to compare them to help you choose the best fit?"
        reasoning = f"Multiple similar options ({similar_count}) suggest comparison would be valuable"
        
        return ProactiveSuggestion(
            suggestion_type=SuggestionType.COMPARISON,
            priority=SuggestionPriority.MEDIUM,
            content=content,
            reasoning=reasoning,
            confidence=0.8,
            triggers=["multiple_similar_results"],
            persona_alignment=self._calculate_persona_alignment(SuggestionType.COMPARISON, context.user_persona),
            context_relevance=0.8,
            timing_score=0.7,
            suggested_action="provide_comparison",
            expected_benefit="Informed decision making",
            estimated_value=0.8
        )
    
    async def _create_api_refinement_suggestion(
        self,
        api_context: Dict[str, Any],
        context: SuggestionContext
    ) -> Optional[ProactiveSuggestion]:
        """Create refinement suggestion for broad API results"""
        
        diversity = api_context.get("result_diversity", 0)
        current_topic = self._extract_current_topic(context.conversation_state)
        
        content = f"The results for {current_topic} are quite diverse. Would you like to refine your search criteria to get more targeted results?"
        reasoning = f"High result diversity ({diversity:.1%}) suggests refinement would improve relevance"
        
        return ProactiveSuggestion(
            suggestion_type=SuggestionType.GOAL_REFINEMENT,
            priority=SuggestionPriority.MEDIUM,
            content=content,
            reasoning=reasoning,
            confidence=0.7,
            triggers=["diverse_api_results"],
            persona_alignment=self._calculate_persona_alignment(SuggestionType.GOAL_REFINEMENT, context.user_persona),
            context_relevance=0.7,
            timing_score=0.6,
            suggested_action="refine_search_criteria",
            expected_benefit="More targeted and relevant results",
            estimated_value=0.7
        )
    
    async def personalize_suggestions(
        self,
        base_suggestions: List[ProactiveSuggestion],
        persona: UserPersona,
        conversation_context: Dict[str, Any]
    ) -> List[ProactiveSuggestion]:
        """Customize suggestions based on user persona and context"""
        
        personalized_suggestions = []
        
        for suggestion in base_suggestions:
            # Adjust content based on persona
            personalized_content = await self._personalize_suggestion_content(
                suggestion, persona, conversation_context
            )
            
            # Adjust priority based on persona preferences
            personalized_priority = self._adjust_suggestion_priority(
                suggestion, persona
            )
            
            # Update persona alignment score
            persona_alignment = self._calculate_persona_alignment(
                suggestion.suggestion_type, persona
            )
            
            # Create personalized suggestion
            personalized_suggestion = ProactiveSuggestion(
                suggestion_type=suggestion.suggestion_type,
                priority=personalized_priority,
                content=personalized_content,
                reasoning=suggestion.reasoning + f" (personalized for {persona.primary_persona.value})",
                confidence=suggestion.confidence,
                triggers=suggestion.triggers + ["personalization"],
                persona_alignment=persona_alignment,
                context_relevance=suggestion.context_relevance,
                timing_score=suggestion.timing_score,
                suggested_action=suggestion.suggested_action,
                expected_benefit=suggestion.expected_benefit,
                estimated_value=suggestion.estimated_value
            )
            
            personalized_suggestions.append(personalized_suggestion)
        
        return personalized_suggestions
    
    async def _rank_and_filter_suggestions(
        self,
        suggestions: List[ProactiveSuggestion],
        context: SuggestionContext
    ) -> List[ProactiveSuggestion]:
        """Rank and filter suggestions based on quality and relevance"""
        
        # Remove duplicates based on suggestion type
        unique_suggestions = {}
        for suggestion in suggestions:
            key = suggestion.suggestion_type
            if key not in unique_suggestions or suggestion.confidence > unique_suggestions[key].confidence:
                unique_suggestions[key] = suggestion
        
        suggestions = list(unique_suggestions.values())
        
        # Calculate overall score for each suggestion
        for suggestion in suggestions:
            suggestion.estimated_value = self._calculate_overall_suggestion_score(suggestion, context)
        
        # Sort by overall score
        suggestions.sort(key=lambda s: s.estimated_value, reverse=True)
        
        # Filter out low-quality suggestions
        filtered_suggestions = [s for s in suggestions if s.estimated_value > 0.5]
        
        return filtered_suggestions
    
    def _calculate_overall_suggestion_score(
        self,
        suggestion: ProactiveSuggestion,
        context: SuggestionContext
    ) -> float:
        """Calculate overall quality score for suggestion"""
        
        # Weighted combination of factors
        score = (
            suggestion.confidence * 0.3 +
            suggestion.persona_alignment * 0.3 +
            suggestion.context_relevance * 0.2 +
            suggestion.timing_score * 0.2
        )
        
        # Priority boost
        priority_boost = {
            SuggestionPriority.HIGH: 0.1,
            SuggestionPriority.MEDIUM: 0.05,
            SuggestionPriority.LOW: 0.0
        }
        score += priority_boost.get(suggestion.priority, 0.0)
        
        return min(1.0, score)
    
    # Helper methods
    
    def _get_last_suggestion_time(self, user_id: str) -> Optional[datetime]:
        """Get timestamp of last suggestion for user"""
        if user_id not in self.suggestion_history:
            return None
        
        suggestions = self.suggestion_history[user_id]
        if not suggestions:
            return None
        
        # Suggestions don't have timestamps in current implementation
        # For now, estimate based on conversation activity
        return datetime.utcnow() - timedelta(minutes=5)
    
    def _assess_conversation_momentum(self, conversation_state: ConversationState) -> str:
        """Assess current conversation momentum"""
        
        if conversation_state.turn_count < 3:
            return "low"
        
        # Calculate time per turn
        duration = conversation_state.last_activity - conversation_state.created_at
        time_per_turn = duration.total_seconds() / conversation_state.turn_count
        
        if time_per_turn < 30:  # Less than 30 seconds per turn
            return "high"
        elif time_per_turn < 120:  # Less than 2 minutes per turn
            return "medium"
        else:
            return "low"
    
    def _assess_user_engagement(self, conversation_state: ConversationState) -> str:
        """Assess user engagement level"""
        
        # Simple heuristic based on conversation activity
        if conversation_state.successful_resolutions > conversation_state.clarification_requests:
            return "high"
        elif conversation_state.turn_count > 5:
            return "medium"
        else:
            return "low"
    
    def _extract_current_topic(self, conversation_state: ConversationState) -> str:
        """Extract current main topic from conversation"""
        interests = conversation_state.get_primary_interests()
        if interests:
            return interests[0]
        
        # Fallback to current intent
        if conversation_state.current_intent:
            return conversation_state.current_intent
        
        return "your current area of interest"
    
    def _get_related_topics(self, topic: str) -> List[str]:
        """Get related topics for given topic"""
        related_mappings = self.suggestion_templates[SuggestionType.RELATED_TOPIC]["related_mappings"]
        return related_mappings.get(topic.lower(), [])
    
    def _calculate_persona_alignment(
        self,
        suggestion_type: SuggestionType,
        persona: UserPersona
    ) -> float:
        """Calculate how well suggestion aligns with user persona"""
        
        persona_config = self.persona_suggestion_mapping.get(persona.primary_persona, {})
        preferred_types = persona_config.get("preferred_suggestions", [])
        
        if suggestion_type in preferred_types:
            return 0.9
        else:
            return 0.5
    
    def _calculate_context_relevance(self, context: SuggestionContext) -> float:
        """Calculate relevance to current conversation context"""
        
        # Simple heuristic based on conversation activity
        base_relevance = 0.7
        
        # Boost for active conversation
        if context.conversation_momentum == "high":
            base_relevance += 0.1
        
        # Boost for engaged user
        if context.user_engagement_level == "high":
            base_relevance += 0.1
        
        return min(1.0, base_relevance)
    
    def _calculate_timing_score(self, context: SuggestionContext) -> float:
        """Calculate timing appropriateness of suggestion"""
        
        # Good timing if not too recent
        if context.time_since_last_suggestion > timedelta(minutes=3):
            return 0.8
        elif context.time_since_last_suggestion > timedelta(minutes=1):
            return 0.6
        else:
            return 0.3
    
    async def _personalize_suggestion_content(
        self,
        suggestion: ProactiveSuggestion,
        persona: UserPersona,
        conversation_context: Dict[str, Any]
    ) -> str:
        """Personalize suggestion content for user persona"""
        
        base_content = suggestion.content
        
        # Adjust language based on experience level
        if persona.experience_level == ExperienceLevel.BEGINNER:
            # Use simpler language
            base_content = base_content.replace("comprehensive", "detailed")
            base_content = base_content.replace("specifications", "information")
        
        elif persona.experience_level == ExperienceLevel.EXPERT:
            # Use more technical language
            base_content = base_content.replace("information", "technical specifications")
            base_content = base_content.replace("details", "comprehensive analysis")
        
        # Adjust based on engagement style
        if persona.engagement_style == EngagementStyle.QUICK_OVERVIEW:
            base_content = base_content.replace("comprehensive", "quick")
            base_content = base_content.replace("detailed", "brief")
        
        return base_content
    
    def _adjust_suggestion_priority(
        self,
        suggestion: ProactiveSuggestion,
        persona: UserPersona
    ) -> SuggestionPriority:
        """Adjust suggestion priority based on persona"""
        
        persona_config = self.persona_suggestion_mapping.get(persona.primary_persona, {})
        preferred_types = persona_config.get("preferred_suggestions", [])
        
        if suggestion.suggestion_type in preferred_types:
            # Boost priority for preferred suggestion types
            if suggestion.priority == SuggestionPriority.LOW:
                return SuggestionPriority.MEDIUM
            elif suggestion.priority == SuggestionPriority.MEDIUM:
                return SuggestionPriority.HIGH
        
        return suggestion.priority
    
    async def learn_from_suggestion_outcome(
        self,
        user_id: str,
        suggestion: ProactiveSuggestion,
        outcome_success: bool,
        user_feedback: Dict[str, Any] = None
    ):
        """Learn from suggestion outcomes to improve future suggestions"""
        
        # Track effectiveness by suggestion type and persona
        suggestion_key = f"{suggestion.suggestion_type.value}_{suggestion.triggers[0] if suggestion.triggers else 'general'}"
        
        current_effectiveness = self.suggestion_effectiveness[user_id].get(suggestion_key, 0.5)
        
        if outcome_success:
            # Increase effectiveness score
            new_effectiveness = min(1.0, current_effectiveness + 0.1)
        else:
            # Decrease effectiveness score
            new_effectiveness = max(0.0, current_effectiveness - 0.05)
        
        self.suggestion_effectiveness[user_id][suggestion_key] = new_effectiveness
    
    async def get_suggestion_analytics(self) -> Dict[str, Any]:
        """Get suggestion generation analytics for monitoring"""
        
        total_suggestions = sum(len(suggestions) for suggestions in self.suggestion_history.values())
        
        if total_suggestions == 0:
            return {"total_suggestions_generated": 0}
        
        # Suggestion type distribution
        type_distribution = defaultdict(int)
        priority_distribution = defaultdict(int)
        confidence_scores = []
        persona_alignment_scores = []
        
        for user_suggestions in self.suggestion_history.values():
            for suggestion in user_suggestions:
                type_distribution[suggestion.suggestion_type.value] += 1
                priority_distribution[suggestion.priority.value] += 1
                confidence_scores.append(suggestion.confidence)
                persona_alignment_scores.append(suggestion.persona_alignment)
        
        return {
            "total_suggestions_generated": total_suggestions,
            "suggestion_type_distribution": dict(type_distribution),
            "priority_distribution": dict(priority_distribution),
            "average_confidence": sum(confidence_scores) / len(confidence_scores),
            "average_persona_alignment": sum(persona_alignment_scores) / len(persona_alignment_scores),
            "high_quality_suggestions": sum(1 for score in confidence_scores if score > 0.7),
            "proactive_assistance_target": 0.4,  # 40% of interactions should include suggestions
            "suggestion_quality_target": 0.7,   # 70% should be high quality
            "quality_target_achieved": (sum(1 for score in confidence_scores if score > 0.7) / len(confidence_scores)) >= 0.7
        }

# Global instance for shared access
proactive_suggestion_engine = ProactiveSuggestionEngine()