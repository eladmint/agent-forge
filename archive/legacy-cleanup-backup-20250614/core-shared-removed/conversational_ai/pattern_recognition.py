# Conversational AI Pattern Recognition System
# Microsoft Bot Framework-inspired conversation pattern detection and learning

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import re
import json
from collections import defaultdict, Counter

from .state_management import ConversationState, IntentHistory, IntentConfidence

class ConversationPattern(Enum):
    """Types of conversation patterns that can be detected"""
    DEEP_DIVE = "deep_dive"                    # User asks follow-up questions about same topic
    EXPLORATION = "exploration"                 # User switches between multiple related topics
    CLARIFICATION_CASCADE = "clarification_cascade"  # User needs multiple clarifications
    GOAL_ORIENTED = "goal_oriented"            # User has specific objective and direct questions
    LEARNING_JOURNEY = "learning_journey"      # User progresses from basic to advanced questions
    RESEARCH_MODE = "research_mode"            # User systematically gathering information
    COMPARISON_SHOPPING = "comparison_shopping" # User comparing multiple options
    TROUBLESHOOTING = "troubleshooting"        # User seeking solution to specific problem

class PatternConfidence(Enum):
    """Confidence levels for pattern detection"""
    HIGH = "high"      # >0.8
    MEDIUM = "medium"  # 0.5-0.8
    LOW = "low"        # <0.5

@dataclass
class PatternMatch:
    """Represents a detected conversation pattern"""
    pattern: ConversationPattern
    confidence: float
    evidence: List[str]
    detected_at: datetime
    context: Dict[str, Any]
    user_turns: List[int]  # Turn numbers where pattern was observed
    
    # Pattern characteristics
    duration_minutes: float = 0.0
    topic_consistency: float = 0.0
    question_complexity_trend: str = "stable"  # "increasing", "decreasing", "stable"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern": self.pattern.value,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "detected_at": self.detected_at.isoformat(),
            "context": self.context,
            "user_turns": self.user_turns,
            "duration_minutes": self.duration_minutes,
            "topic_consistency": self.topic_consistency,
            "question_complexity_trend": self.question_complexity_trend
        }

@dataclass
class PatternPrediction:
    """Predicted next user intents based on pattern"""
    predicted_intents: List[str]
    confidence_scores: Dict[str, float]
    suggested_responses: List[str]
    proactive_actions: List[str]
    expected_pattern_continuation: bool

class ConversationPatternDetector:
    """Detects and learns from conversation patterns for intelligent dialogue management"""
    
    def __init__(self):
        self.pattern_definitions = self._initialize_pattern_definitions()
        self.pattern_history: Dict[str, List[PatternMatch]] = defaultdict(list)
        self.learning_weights = self._initialize_learning_weights()
        
    def _initialize_pattern_definitions(self) -> Dict[ConversationPattern, Dict[str, Any]]:
        """Initialize pattern detection rules and characteristics"""
        return {
            ConversationPattern.DEEP_DIVE: {
                "description": "User asks follow-up questions about same topic",
                "min_turns": 3,
                "topic_consistency_threshold": 0.7,
                "indicators": [
                    "follow_up_questions_same_topic",
                    "increasing_question_complexity",
                    "reference_to_previous_response"
                ],
                "typical_duration_minutes": 10,
                "next_intent_probability": {
                    "detailed_explanation": 0.8,
                    "technical_details": 0.6,
                    "examples_request": 0.7,
                    "related_topic_exploration": 0.4
                }
            },
            
            ConversationPattern.EXPLORATION: {
                "description": "User switches between multiple related topics",
                "min_turns": 4,
                "topic_consistency_threshold": 0.3,  # Low consistency indicates exploration
                "indicators": [
                    "topic_switching",
                    "broad_questions",
                    "discovery_language"
                ],
                "typical_duration_minutes": 15,
                "next_intent_probability": {
                    "new_topic_search": 0.7,
                    "overview_request": 0.8,
                    "comparison_request": 0.5,
                    "category_browsing": 0.6
                }
            },
            
            ConversationPattern.CLARIFICATION_CASCADE: {
                "description": "User needs multiple clarifications",
                "min_turns": 3,
                "topic_consistency_threshold": 0.8,
                "indicators": [
                    "repeated_clarification_requests",
                    "confusion_signals",
                    "reformulation_requests"
                ],
                "typical_duration_minutes": 8,
                "next_intent_probability": {
                    "simplified_explanation": 0.9,
                    "example_request": 0.8,
                    "alternative_approach": 0.6,
                    "escalation_request": 0.3
                }
            },
            
            ConversationPattern.GOAL_ORIENTED: {
                "description": "User has specific objective and direct questions",
                "min_turns": 2,
                "topic_consistency_threshold": 0.9,
                "indicators": [
                    "specific_goals",
                    "direct_questions",
                    "task_completion_focus"
                ],
                "typical_duration_minutes": 5,
                "next_intent_probability": {
                    "action_request": 0.8,
                    "specific_information": 0.9,
                    "completion_verification": 0.6,
                    "next_step_request": 0.7
                }
            },
            
            ConversationPattern.LEARNING_JOURNEY: {
                "description": "User progresses from basic to advanced questions",
                "min_turns": 5,
                "topic_consistency_threshold": 0.6,
                "indicators": [
                    "progressive_complexity",
                    "building_knowledge",
                    "concept_connection"
                ],
                "typical_duration_minutes": 20,
                "next_intent_probability": {
                    "advanced_concepts": 0.7,
                    "practical_application": 0.8,
                    "knowledge_verification": 0.6,
                    "related_advanced_topics": 0.5
                }
            },
            
            ConversationPattern.RESEARCH_MODE: {
                "description": "User systematically gathering information",
                "min_turns": 4,
                "topic_consistency_threshold": 0.5,
                "indicators": [
                    "systematic_information_gathering",
                    "comprehensive_questions",
                    "data_collection_focus"
                ],
                "typical_duration_minutes": 25,
                "next_intent_probability": {
                    "comprehensive_data": 0.8,
                    "comparative_analysis": 0.7,
                    "detailed_specifications": 0.9,
                    "research_continuation": 0.6
                }
            },
            
            ConversationPattern.COMPARISON_SHOPPING: {
                "description": "User comparing multiple options",
                "min_turns": 3,
                "topic_consistency_threshold": 0.6,
                "indicators": [
                    "comparison_requests",
                    "option_evaluation",
                    "decision_making_context"
                ],
                "typical_duration_minutes": 12,
                "next_intent_probability": {
                    "detailed_comparison": 0.8,
                    "option_details": 0.7,
                    "decision_support": 0.9,
                    "additional_options": 0.5
                }
            },
            
            ConversationPattern.TROUBLESHOOTING: {
                "description": "User seeking solution to specific problem",
                "min_turns": 2,
                "topic_consistency_threshold": 0.8,
                "indicators": [
                    "problem_description",
                    "solution_seeking",
                    "error_reporting"
                ],
                "typical_duration_minutes": 8,
                "next_intent_probability": {
                    "solution_steps": 0.9,
                    "alternative_solutions": 0.6,
                    "problem_clarification": 0.7,
                    "escalation": 0.3
                }
            }
        }
    
    def _initialize_learning_weights(self) -> Dict[str, float]:
        """Initialize weights for pattern learning"""
        return {
            "temporal_weight": 0.3,      # How much time patterns matter
            "frequency_weight": 0.4,     # How much pattern frequency matters
            "recency_weight": 0.3,       # How much recent patterns matter
            "success_weight": 0.5        # How much successful patterns matter
        }
    
    async def detect_patterns(
        self,
        conversation_history: List[Dict[str, Any]],
        current_message: str,
        conversation_state: ConversationState
    ) -> List[PatternMatch]:
        """Identify conversation patterns from user behavior"""
        
        if len(conversation_history) < 2:
            return []
        
        detected_patterns = []
        
        # Analyze each potential pattern
        for pattern_type in ConversationPattern:
            pattern_match = await self._analyze_pattern(
                pattern_type,
                conversation_history,
                current_message,
                conversation_state
            )
            
            if pattern_match and pattern_match.confidence > 0.3:
                detected_patterns.append(pattern_match)
        
        # Sort by confidence and return top patterns
        detected_patterns.sort(key=lambda x: x.confidence, reverse=True)
        
        # Store patterns for learning
        user_id = conversation_state.user_id
        for pattern in detected_patterns:
            self.pattern_history[user_id].append(pattern)
        
        return detected_patterns[:3]  # Return top 3 patterns
    
    async def _analyze_pattern(
        self,
        pattern_type: ConversationPattern,
        conversation_history: List[Dict[str, Any]],
        current_message: str,
        conversation_state: ConversationState
    ) -> Optional[PatternMatch]:
        """Analyze conversation for specific pattern type"""
        
        pattern_def = self.pattern_definitions[pattern_type]
        
        # Check minimum turn requirement
        if len(conversation_history) < pattern_def["min_turns"]:
            return None
        
        # Extract recent conversation window
        analysis_window = conversation_history[-10:]  # Analyze last 10 turns
        
        # Calculate pattern indicators
        indicators = await self._calculate_pattern_indicators(
            pattern_type, analysis_window, current_message, conversation_state
        )
        
        # Calculate confidence score
        confidence = await self._calculate_pattern_confidence(
            pattern_type, indicators, analysis_window
        )
        
        if confidence < 0.3:
            return None
        
        # Extract evidence
        evidence = self._extract_pattern_evidence(pattern_type, indicators, analysis_window)
        
        # Calculate pattern characteristics
        duration = self._calculate_pattern_duration(analysis_window)
        topic_consistency = await self._calculate_topic_consistency(analysis_window)
        complexity_trend = self._analyze_complexity_trend(analysis_window)
        
        return PatternMatch(
            pattern=pattern_type,
            confidence=confidence,
            evidence=evidence,
            detected_at=datetime.utcnow(),
            context=self._extract_pattern_context(analysis_window),
            user_turns=[i for i, turn in enumerate(analysis_window) if turn.get("user_message")],
            duration_minutes=duration,
            topic_consistency=topic_consistency,
            question_complexity_trend=complexity_trend
        )
    
    async def _calculate_pattern_indicators(
        self,
        pattern_type: ConversationPattern,
        conversation_window: List[Dict[str, Any]],
        current_message: str,
        conversation_state: ConversationState
    ) -> Dict[str, float]:
        """Calculate specific indicators for pattern type"""
        
        indicators = {}
        
        if pattern_type == ConversationPattern.DEEP_DIVE:
            indicators.update(await self._analyze_deep_dive_indicators(
                conversation_window, current_message, conversation_state
            ))
        
        elif pattern_type == ConversationPattern.EXPLORATION:
            indicators.update(await self._analyze_exploration_indicators(
                conversation_window, current_message, conversation_state
            ))
        
        elif pattern_type == ConversationPattern.CLARIFICATION_CASCADE:
            indicators.update(await self._analyze_clarification_indicators(
                conversation_window, current_message, conversation_state
            ))
        
        elif pattern_type == ConversationPattern.GOAL_ORIENTED:
            indicators.update(await self._analyze_goal_oriented_indicators(
                conversation_window, current_message, conversation_state
            ))
        
        elif pattern_type == ConversationPattern.LEARNING_JOURNEY:
            indicators.update(await self._analyze_learning_journey_indicators(
                conversation_window, current_message, conversation_state
            ))
        
        elif pattern_type == ConversationPattern.RESEARCH_MODE:
            indicators.update(await self._analyze_research_mode_indicators(
                conversation_window, current_message, conversation_state
            ))
        
        return indicators
    
    async def _analyze_deep_dive_indicators(
        self,
        conversation_window: List[Dict[str, Any]],
        current_message: str,
        conversation_state: ConversationState
    ) -> Dict[str, float]:
        """Analyze indicators for deep dive pattern"""
        
        indicators = {}
        
        # Check for follow-up questions on same topic
        topic_continuity = 0.0
        if len(conversation_window) >= 3:
            recent_topics = []
            for turn in conversation_window[-3:]:
                if turn.get("user_message"):
                    topics = self._extract_topics_from_message(turn["user_message"])
                    recent_topics.extend(topics)
            
            if recent_topics:
                most_common_topic = Counter(recent_topics).most_common(1)[0]
                topic_continuity = most_common_topic[1] / len(recent_topics)
        
        indicators["follow_up_questions_same_topic"] = topic_continuity
        
        # Check for increasing question complexity
        complexity_trend = 0.0
        if len(conversation_window) >= 3:
            complexities = []
            for turn in conversation_window[-3:]:
                if turn.get("user_message"):
                    complexity = self._calculate_message_complexity(turn["user_message"])
                    complexities.append(complexity)
            
            if len(complexities) >= 2:
                if complexities[-1] > complexities[0]:
                    complexity_trend = min(1.0, (complexities[-1] - complexities[0]) / complexities[0])
        
        indicators["increasing_question_complexity"] = complexity_trend
        
        # Check for references to previous responses
        reference_score = 0.0
        reference_patterns = [
            r"you mentioned", r"you said", r"as you explained", r"from what you told me",
            r"building on that", r"following up", r"more about", r"tell me more"
        ]
        
        for pattern in reference_patterns:
            if re.search(pattern, current_message.lower()):
                reference_score += 0.3
        
        indicators["reference_to_previous_response"] = min(1.0, reference_score)
        
        return indicators
    
    async def _analyze_exploration_indicators(
        self,
        conversation_window: List[Dict[str, Any]],
        current_message: str,
        conversation_state: ConversationState
    ) -> Dict[str, float]:
        """Analyze indicators for exploration pattern"""
        
        indicators = {}
        
        # Check for topic switching
        topic_switches = 0
        if len(conversation_window) >= 3:
            previous_topics = set()
            for i, turn in enumerate(conversation_window[-3:]):
                if turn.get("user_message"):
                    current_topics = set(self._extract_topics_from_message(turn["user_message"]))
                    if i > 0 and not current_topics.intersection(previous_topics):
                        topic_switches += 1
                    previous_topics = current_topics
        
        indicators["topic_switching"] = min(1.0, topic_switches / 3)
        
        # Check for broad questions
        broad_question_patterns = [
            r"what.*about", r"tell me about", r"how.*work", r"what.*types",
            r"what.*options", r"show me", r"find.*events", r"any.*related"
        ]
        
        broad_score = 0.0
        for pattern in broad_question_patterns:
            if re.search(pattern, current_message.lower()):
                broad_score += 0.2
        
        indicators["broad_questions"] = min(1.0, broad_score)
        
        # Check for discovery language
        discovery_patterns = [
            r"discover", r"explore", r"browse", r"look around", r"see what",
            r"anything else", r"what else", r"other.*options"
        ]
        
        discovery_score = 0.0
        for pattern in discovery_patterns:
            if re.search(pattern, current_message.lower()):
                discovery_score += 0.3
        
        indicators["discovery_language"] = min(1.0, discovery_score)
        
        return indicators
    
    async def _analyze_clarification_indicators(
        self,
        conversation_window: List[Dict[str, Any]],
        current_message: str,
        conversation_state: ConversationState
    ) -> Dict[str, float]:
        """Analyze indicators for clarification cascade pattern"""
        
        indicators = {}
        
        # Count clarification requests
        clarification_count = conversation_state.clarification_requests
        recent_clarifications = 0
        
        clarification_patterns = [
            r"i don't understand", r"what do you mean", r"can you explain",
            r"i'm confused", r"clarify", r"not clear", r"what.*that mean"
        ]
        
        for turn in conversation_window[-5:]:
            if turn.get("user_message"):
                for pattern in clarification_patterns:
                    if re.search(pattern, turn["user_message"].lower()):
                        recent_clarifications += 1
                        break
        
        indicators["repeated_clarification_requests"] = min(1.0, recent_clarifications / 3)
        
        # Check for confusion signals
        confusion_patterns = [
            r"confused", r"lost", r"don't get it", r"makes no sense",
            r"not following", r"unclear", r"complicated"
        ]
        
        confusion_score = 0.0
        for pattern in confusion_patterns:
            if re.search(pattern, current_message.lower()):
                confusion_score += 0.4
        
        indicators["confusion_signals"] = min(1.0, confusion_score)
        
        # Check for reformulation requests
        reformulation_patterns = [
            r"different way", r"simpler", r"easier", r"other words",
            r"rephrase", r"explain again", r"try again"
        ]
        
        reformulation_score = 0.0
        for pattern in reformulation_patterns:
            if re.search(pattern, current_message.lower()):
                reformulation_score += 0.3
        
        indicators["reformulation_requests"] = min(1.0, reformulation_score)
        
        return indicators
    
    async def _analyze_goal_oriented_indicators(
        self,
        conversation_window: List[Dict[str, Any]],
        current_message: str,
        conversation_state: ConversationState
    ) -> Dict[str, float]:
        """Analyze indicators for goal-oriented pattern"""
        
        indicators = {}
        
        # Check for specific goals
        goal_patterns = [
            r"i need to", r"i want to", r"help me", r"how can i",
            r"i'm looking for", r"find.*specific", r"register for"
        ]
        
        goal_score = 0.0
        for pattern in goal_patterns:
            if re.search(pattern, current_message.lower()):
                goal_score += 0.3
        
        indicators["specific_goals"] = min(1.0, goal_score)
        
        # Check for direct questions
        direct_question_patterns = [
            r"^(what|when|where|how|who|which)", r"\?$", r"tell me",
            r"show me", r"give me", r"can you"
        ]
        
        direct_score = 0.0
        for pattern in direct_question_patterns:
            if re.search(pattern, current_message.lower()):
                direct_score += 0.2
        
        indicators["direct_questions"] = min(1.0, direct_score)
        
        # Check for task completion focus
        task_patterns = [
            r"complete", r"finish", r"done", r"next step", r"proceed",
            r"register", r"book", r"sign up", r"submit"
        ]
        
        task_score = 0.0
        for pattern in task_patterns:
            if re.search(pattern, current_message.lower()):
                task_score += 0.4
        
        indicators["task_completion_focus"] = min(1.0, task_score)
        
        return indicators
    
    async def _analyze_learning_journey_indicators(
        self,
        conversation_window: List[Dict[str, Any]],
        current_message: str,
        conversation_state: ConversationState
    ) -> Dict[str, float]:
        """Analyze indicators for learning journey pattern"""
        
        indicators = {}
        
        # Check for progressive complexity
        if len(conversation_window) >= 4:
            complexities = []
            for turn in conversation_window[-4:]:
                if turn.get("user_message"):
                    complexity = self._calculate_message_complexity(turn["user_message"])
                    complexities.append(complexity)
            
            if len(complexities) >= 3:
                # Check if complexity generally increases
                increases = sum(1 for i in range(1, len(complexities)) 
                              if complexities[i] > complexities[i-1])
                progression_score = increases / (len(complexities) - 1)
                indicators["progressive_complexity"] = progression_score
            else:
                indicators["progressive_complexity"] = 0.0
        else:
            indicators["progressive_complexity"] = 0.0
        
        # Check for building knowledge
        building_patterns = [
            r"now i understand", r"that makes sense", r"i see", r"got it",
            r"so if", r"then", r"building on", r"next level"
        ]
        
        building_score = 0.0
        for pattern in building_patterns:
            if re.search(pattern, current_message.lower()):
                building_score += 0.3
        
        indicators["building_knowledge"] = min(1.0, building_score)
        
        # Check for concept connections
        connection_patterns = [
            r"related to", r"similar to", r"different from", r"compared to",
            r"like.*but", r"connects to", r"ties into"
        ]
        
        connection_score = 0.0
        for pattern in connection_patterns:
            if re.search(pattern, current_message.lower()):
                connection_score += 0.4
        
        indicators["concept_connection"] = min(1.0, connection_score)
        
        return indicators
    
    async def _analyze_research_mode_indicators(
        self,
        conversation_window: List[Dict[str, Any]],
        current_message: str,
        conversation_state: ConversationState
    ) -> Dict[str, float]:
        """Analyze indicators for research mode pattern"""
        
        indicators = {}
        
        # Check for systematic information gathering
        systematic_patterns = [
            r"comprehensive", r"detailed", r"thorough", r"complete",
            r"all.*information", r"everything about", r"full.*details"
        ]
        
        systematic_score = 0.0
        for pattern in systematic_patterns:
            if re.search(pattern, current_message.lower()):
                systematic_score += 0.3
        
        indicators["systematic_information_gathering"] = min(1.0, systematic_score)
        
        # Check for comprehensive questions
        comprehensive_patterns = [
            r"what.*all", r"list.*all", r"show.*all", r"every.*option",
            r"complete.*list", r"all.*available", r"entire.*range"
        ]
        
        comprehensive_score = 0.0
        for pattern in comprehensive_patterns:
            if re.search(pattern, current_message.lower()):
                comprehensive_score += 0.4
        
        indicators["comprehensive_questions"] = min(1.0, comprehensive_score)
        
        # Check for data collection focus
        data_patterns = [
            r"data", r"statistics", r"numbers", r"metrics", r"analysis",
            r"research", r"study", r"report", r"findings"
        ]
        
        data_score = 0.0
        for pattern in data_patterns:
            if re.search(pattern, current_message.lower()):
                data_score += 0.2
        
        indicators["data_collection_focus"] = min(1.0, data_score)
        
        return indicators
    
    async def _calculate_pattern_confidence(
        self,
        pattern_type: ConversationPattern,
        indicators: Dict[str, float],
        conversation_window: List[Dict[str, Any]]
    ) -> float:
        """Calculate confidence score for pattern detection"""
        
        pattern_def = self.pattern_definitions[pattern_type]
        
        # Calculate weighted indicator score
        indicator_sum = sum(indicators.values())
        indicator_count = len(indicators)
        indicator_score = indicator_sum / indicator_count if indicator_count > 0 else 0
        
        # Apply pattern-specific weights
        base_confidence = indicator_score * 0.7
        
        # Bonus for meeting pattern requirements
        if len(conversation_window) >= pattern_def["min_turns"]:
            base_confidence += 0.1
        
        # Topic consistency bonus/penalty
        topic_consistency = await self._calculate_topic_consistency(conversation_window)
        consistency_threshold = pattern_def["topic_consistency_threshold"]
        
        if pattern_type in [ConversationPattern.DEEP_DIVE, ConversationPattern.GOAL_ORIENTED]:
            # Patterns that benefit from high consistency
            if topic_consistency >= consistency_threshold:
                base_confidence += 0.1
            else:
                base_confidence -= 0.1
        else:
            # Patterns that benefit from low consistency (exploration)
            if topic_consistency <= consistency_threshold:
                base_confidence += 0.1
        
        # Historical pattern bonus
        base_confidence += self._get_historical_pattern_bonus(pattern_type)
        
        return max(0.0, min(1.0, base_confidence))
    
    def _extract_pattern_evidence(
        self,
        pattern_type: ConversationPattern,
        indicators: Dict[str, float],
        conversation_window: List[Dict[str, Any]]
    ) -> List[str]:
        """Extract evidence supporting pattern detection"""
        
        evidence = []
        
        # Add high-scoring indicators as evidence
        for indicator, score in indicators.items():
            if score > 0.5:
                evidence.append(f"{indicator}: {score:.2f}")
        
        # Add conversation characteristics
        if len(conversation_window) >= 3:
            evidence.append(f"Conversation length: {len(conversation_window)} turns")
        
        # Add pattern-specific evidence
        if pattern_type == ConversationPattern.DEEP_DIVE:
            evidence.append("Sustained focus on single topic with increasing detail")
        elif pattern_type == ConversationPattern.EXPLORATION:
            evidence.append("Topic switching behavior with broad questions")
        elif pattern_type == ConversationPattern.CLARIFICATION_CASCADE:
            evidence.append("Multiple clarification requests detected")
        
        return evidence
    
    def _calculate_pattern_duration(self, conversation_window: List[Dict[str, Any]]) -> float:
        """Calculate pattern duration in minutes"""
        
        if len(conversation_window) < 2:
            return 0.0
        
        # Use timestamps if available
        start_time = None
        end_time = None
        
        for turn in conversation_window:
            if "timestamp" in turn:
                if start_time is None:
                    start_time = datetime.fromisoformat(turn["timestamp"])
                end_time = datetime.fromisoformat(turn["timestamp"])
        
        if start_time and end_time:
            duration = (end_time - start_time).total_seconds() / 60
            return duration
        
        # Estimate based on turn count (assume 1-2 minutes per turn)
        return len(conversation_window) * 1.5
    
    async def _calculate_topic_consistency(self, conversation_window: List[Dict[str, Any]]) -> float:
        """Calculate topic consistency across conversation window"""
        
        if len(conversation_window) < 2:
            return 1.0
        
        all_topics = []
        for turn in conversation_window:
            if turn.get("user_message"):
                topics = self._extract_topics_from_message(turn["user_message"])
                all_topics.extend(topics)
        
        if not all_topics:
            return 0.0
        
        # Calculate topic distribution
        topic_counts = Counter(all_topics)
        most_common_count = topic_counts.most_common(1)[0][1]
        
        return most_common_count / len(all_topics)
    
    def _analyze_complexity_trend(self, conversation_window: List[Dict[str, Any]]) -> str:
        """Analyze question complexity trend"""
        
        if len(conversation_window) < 3:
            return "stable"
        
        complexities = []
        for turn in conversation_window[-5:]:  # Analyze last 5 turns
            if turn.get("user_message"):
                complexity = self._calculate_message_complexity(turn["user_message"])
                complexities.append(complexity)
        
        if len(complexities) < 3:
            return "stable"
        
        # Calculate trend
        increases = sum(1 for i in range(1, len(complexities)) 
                       if complexities[i] > complexities[i-1])
        decreases = sum(1 for i in range(1, len(complexities)) 
                       if complexities[i] < complexities[i-1])
        
        if increases > decreases:
            return "increasing"
        elif decreases > increases:
            return "decreasing"
        else:
            return "stable"
    
    def _extract_pattern_context(self, conversation_window: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract context information for pattern"""
        
        context = {
            "turn_count": len(conversation_window),
            "user_turns": sum(1 for turn in conversation_window if turn.get("user_message")),
            "bot_turns": sum(1 for turn in conversation_window if turn.get("bot_response")),
            "topics_mentioned": [],
            "question_types": []
        }
        
        # Extract topics and question types
        for turn in conversation_window:
            if turn.get("user_message"):
                topics = self._extract_topics_from_message(turn["user_message"])
                context["topics_mentioned"].extend(topics)
                
                if "?" in turn["user_message"]:
                    context["question_types"].append("question")
                else:
                    context["question_types"].append("statement")
        
        # Remove duplicates
        context["topics_mentioned"] = list(set(context["topics_mentioned"]))
        
        return context
    
    def _extract_topics_from_message(self, message: str) -> List[str]:
        """Extract topics/keywords from message"""
        
        # Simple keyword extraction - can be enhanced with NLP
        crypto_keywords = [
            "defi", "nft", "blockchain", "ethereum", "bitcoin", "crypto",
            "token", "smart contract", "dapp", "protocol", "yield", "staking",
            "liquidity", "trading", "investment", "conference", "event", "meetup"
        ]
        
        topics = []
        message_lower = message.lower()
        
        for keyword in crypto_keywords:
            if keyword in message_lower:
                topics.append(keyword)
        
        return topics
    
    def _calculate_message_complexity(self, message: str) -> float:
        """Calculate message complexity score (0-1)"""
        
        complexity_factors = {
            "word_count": len(message.split()),
            "technical_terms": sum(1 for term in ["protocol", "smart contract", "defi", "blockchain"] 
                                 if term in message.lower()),
            "question_marks": message.count("?"),
            "complex_sentences": message.count(",") + message.count(";"),
            "specific_details": sum(1 for term in ["specific", "detail", "exactly", "precisely"] 
                                  if term in message.lower())
        }
        
        # Normalize and weight factors
        word_score = min(1.0, complexity_factors["word_count"] / 50)
        tech_score = min(1.0, complexity_factors["technical_terms"] / 5)
        structure_score = min(1.0, (complexity_factors["complex_sentences"] + 
                                   complexity_factors["question_marks"]) / 10)
        detail_score = min(1.0, complexity_factors["specific_details"] / 3)
        
        return (word_score * 0.3 + tech_score * 0.4 + structure_score * 0.2 + detail_score * 0.1)
    
    def _get_historical_pattern_bonus(self, pattern_type: ConversationPattern) -> float:
        """Get bonus based on historical pattern success"""
        
        # This would use actual historical data
        # For now, return small positive bonus for established patterns
        return 0.05
    
    async def predict_user_intent_flow(
        self,
        pattern_match: PatternMatch,
        conversation_state: ConversationState
    ) -> PatternPrediction:
        """Predict likely next user intents based on detected pattern"""
        
        pattern_def = self.pattern_definitions[pattern_match.pattern]
        next_intent_probs = pattern_def["next_intent_probability"]
        
        # Sort intents by probability
        sorted_intents = sorted(next_intent_probs.items(), key=lambda x: x[1], reverse=True)
        
        predicted_intents = [intent for intent, prob in sorted_intents[:3]]
        confidence_scores = {intent: prob for intent, prob in sorted_intents[:3]}
        
        # Generate suggested responses based on pattern
        suggested_responses = await self._generate_pattern_responses(pattern_match)
        
        # Generate proactive actions
        proactive_actions = await self._generate_proactive_actions(pattern_match)
        
        # Predict pattern continuation
        continuation_probability = pattern_match.confidence * 0.8
        expected_continuation = continuation_probability > 0.6
        
        return PatternPrediction(
            predicted_intents=predicted_intents,
            confidence_scores=confidence_scores,
            suggested_responses=suggested_responses,
            proactive_actions=proactive_actions,
            expected_pattern_continuation=expected_continuation
        )
    
    async def _generate_pattern_responses(self, pattern_match: PatternMatch) -> List[str]:
        """Generate suggested responses based on pattern"""
        
        responses = []
        
        if pattern_match.pattern == ConversationPattern.DEEP_DIVE:
            responses.extend([
                "Let me provide more detailed information about this topic.",
                "I can give you technical specifications if you're interested.",
                "Would you like me to explain the underlying concepts?",
                "I can show you practical examples of this in action."
            ])
        
        elif pattern_match.pattern == ConversationPattern.EXPLORATION:
            responses.extend([
                "I can show you related topics that might interest you.",
                "Would you like to explore different categories?",
                "Let me suggest some other areas you might want to discover.",
                "I can help you browse through various options."
            ])
        
        elif pattern_match.pattern == ConversationPattern.CLARIFICATION_CASCADE:
            responses.extend([
                "Let me explain this in simpler terms.",
                "I'll break this down step by step.",
                "Would you prefer a different approach to this explanation?",
                "I can provide a practical example to clarify."
            ])
        
        elif pattern_match.pattern == ConversationPattern.GOAL_ORIENTED:
            responses.extend([
                "I can help you complete this task efficiently.",
                "Let me guide you through the specific steps.",
                "Would you like me to find exactly what you need?",
                "I can provide direct answers to help you proceed."
            ])
        
        elif pattern_match.pattern == ConversationPattern.LEARNING_JOURNEY:
            responses.extend([
                "Ready to explore more advanced concepts?",
                "I can show you how this applies in practice.",
                "Would you like to see how these concepts connect?",
                "Let me introduce some related advanced topics."
            ])
        
        elif pattern_match.pattern == ConversationPattern.RESEARCH_MODE:
            responses.extend([
                "I can provide comprehensive data and analysis.",
                "Would you like detailed specifications and comparisons?",
                "I can compile thorough research information for you.",
                "Let me gather all relevant data on this topic."
            ])
        
        return responses[:2]  # Return top 2 suggestions
    
    async def _generate_proactive_actions(self, pattern_match: PatternMatch) -> List[str]:
        """Generate proactive actions based on pattern"""
        
        actions = []
        
        if pattern_match.pattern == ConversationPattern.DEEP_DIVE:
            actions.extend([
                "prepare_detailed_explanation",
                "gather_technical_specifications",
                "find_practical_examples"
            ])
        
        elif pattern_match.pattern == ConversationPattern.EXPLORATION:
            actions.extend([
                "suggest_related_topics",
                "prepare_category_overview",
                "compile_discovery_options"
            ])
        
        elif pattern_match.pattern == ConversationPattern.CLARIFICATION_CASCADE:
            actions.extend([
                "simplify_explanation_approach",
                "prepare_step_by_step_guide",
                "find_alternative_explanations"
            ])
        
        elif pattern_match.pattern == ConversationPattern.GOAL_ORIENTED:
            actions.extend([
                "optimize_task_completion_path",
                "prepare_direct_solutions",
                "gather_specific_information"
            ])
        
        elif pattern_match.pattern == ConversationPattern.LEARNING_JOURNEY:
            actions.extend([
                "prepare_advanced_concepts",
                "compile_practical_applications",
                "map_concept_connections"
            ])
        
        elif pattern_match.pattern == ConversationPattern.RESEARCH_MODE:
            actions.extend([
                "compile_comprehensive_data",
                "prepare_detailed_analysis",
                "gather_comparative_information"
            ])
        
        return actions[:3]  # Return top 3 actions
    
    async def learn_from_pattern_outcome(
        self,
        user_id: str,
        pattern_match: PatternMatch,
        outcome_success: bool,
        user_feedback: Dict[str, Any] = None
    ):
        """Learn from pattern detection outcomes to improve future detection"""
        
        # Update pattern learning weights based on success
        if outcome_success:
            self.learning_weights["success_weight"] *= 1.05  # Increase successful pattern weight
        else:
            self.learning_weights["success_weight"] *= 0.95  # Decrease unsuccessful pattern weight
        
        # Store outcome for future learning
        if user_id in self.pattern_history:
            for stored_pattern in self.pattern_history[user_id]:
                if (stored_pattern.pattern == pattern_match.pattern and
                    stored_pattern.detected_at == pattern_match.detected_at):
                    stored_pattern.context["outcome_success"] = outcome_success
                    if user_feedback:
                        stored_pattern.context["user_feedback"] = user_feedback
                    break
    
    async def get_pattern_analytics(self) -> Dict[str, Any]:
        """Get pattern detection analytics for monitoring"""
        
        total_patterns = sum(len(patterns) for patterns in self.pattern_history.values())
        
        if total_patterns == 0:
            return {"total_patterns_detected": 0}
        
        # Pattern distribution
        pattern_distribution = defaultdict(int)
        confidence_scores = []
        successful_patterns = 0
        
        for user_patterns in self.pattern_history.values():
            for pattern in user_patterns:
                pattern_distribution[pattern.pattern.value] += 1
                confidence_scores.append(pattern.confidence)
                
                if pattern.context.get("outcome_success", False):
                    successful_patterns += 1
        
        return {
            "total_patterns_detected": total_patterns,
            "pattern_distribution": dict(pattern_distribution),
            "average_confidence": sum(confidence_scores) / len(confidence_scores),
            "high_confidence_patterns": sum(1 for score in confidence_scores if score > 0.7),
            "pattern_success_rate": successful_patterns / total_patterns,
            "pattern_detection_target": 0.6,  # 60% of conversations should have detectable patterns
            "detection_threshold_met": len(confidence_scores) > 0 and 
                                     sum(1 for score in confidence_scores if score > 0.5) / len(confidence_scores) > 0.6
        }

# Global instance for shared access
pattern_detector = ConversationPatternDetector()