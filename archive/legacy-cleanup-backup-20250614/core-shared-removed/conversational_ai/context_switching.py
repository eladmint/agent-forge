# Conversational AI Context Switching Management
# Microsoft Bot Framework-inspired context switching for smooth topic transitions

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import re
import json
from collections import defaultdict

from .state_management import ConversationState, ConversationSlot
from .pattern_recognition import ConversationPattern, PatternMatch

class ContextSwitchType(Enum):
    """Types of context switches that can occur in conversation"""
    TOPIC_CHANGE = "topic_change"              # Complete topic change
    SUBTOPIC_SHIFT = "subtopic_shift"          # Shift within same general topic
    RETURN_TO_PREVIOUS = "return_to_previous"  # Return to earlier topic
    BRANCHING = "branching"                    # Explore related but different topic
    CLARIFICATION_SWITCH = "clarification_switch"  # Switch to clarify previous topic
    GOAL_REFINEMENT = "goal_refinement"        # Refine or change stated goal

class SwitchConfidence(Enum):
    """Confidence levels for context switch detection"""
    HIGH = "high"      # >0.8 - Clear switch detected
    MEDIUM = "medium"  # 0.5-0.8 - Probable switch
    LOW = "low"        # <0.5 - Possible switch

@dataclass
class ContextSwitchResult:
    """Result of context switch analysis"""
    switch_detected: bool
    switch_type: Optional[ContextSwitchType]
    confidence: float
    
    # Context information
    previous_context: Dict[str, Any]
    new_context: Dict[str, Any]
    preserved_elements: List[str]
    
    # Switch characteristics
    switch_trigger: str  # What triggered the switch
    topic_relationship: str  # "related", "unrelated", "opposite", "clarifying"
    user_intent_change: bool
    
    # Transition recommendations
    transition_strategy: str
    context_bridge_needed: bool
    suggested_acknowledgment: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "switch_detected": self.switch_detected,
            "switch_type": self.switch_type.value if self.switch_type else None,
            "confidence": self.confidence,
            "previous_context": self.previous_context,
            "new_context": self.new_context,
            "preserved_elements": self.preserved_elements,
            "switch_trigger": self.switch_trigger,
            "topic_relationship": self.topic_relationship,
            "user_intent_change": self.user_intent_change,
            "transition_strategy": self.transition_strategy,
            "context_bridge_needed": self.context_bridge_needed,
            "suggested_acknowledgment": self.suggested_acknowledgment
        }

@dataclass
class TransitionPlan:
    """Plan for managing smooth context transitions"""
    acknowledgment_message: str
    context_bridge: Dict[str, Any]
    preserved_context: Dict[str, Any]
    response_adjustments: List[str]
    proactive_suggestions: List[str]
    
    # Transition metadata
    transition_type: str
    estimated_success_rate: float
    fallback_strategy: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "acknowledgment_message": self.acknowledgment_message,
            "context_bridge": self.context_bridge,
            "preserved_context": self.preserved_context,
            "response_adjustments": self.response_adjustments,
            "proactive_suggestions": self.proactive_suggestions,
            "transition_type": self.transition_type,
            "estimated_success_rate": self.estimated_success_rate,
            "fallback_strategy": self.fallback_strategy
        }

class ContextSwitchManager:
    """Manages smooth topic transitions while preserving relevant context"""
    
    def __init__(self):
        self.switch_patterns = self._initialize_switch_patterns()
        self.preservation_rules = self._initialize_preservation_rules()
        self.transition_strategies = self._initialize_transition_strategies()
        self.switch_history: Dict[str, List[ContextSwitchResult]] = defaultdict(list)
    
    def _initialize_switch_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize patterns that indicate context switches"""
        return {
            "explicit_topic_change": {
                "patterns": [
                    r"let's talk about", r"what about", r"switching to", r"moving on to",
                    r"different topic", r"change of subject", r"by the way", r"actually",
                    r"instead", r"rather than", r"forget about", r"never mind"
                ],
                "confidence_boost": 0.3,
                "switch_type": ContextSwitchType.TOPIC_CHANGE
            },
            
            "question_transition": {
                "patterns": [
                    r"^what", r"^how", r"^when", r"^where", r"^who", r"^why",
                    r"tell me about", r"explain", r"show me", r"find"
                ],
                "confidence_boost": 0.2,
                "switch_type": ContextSwitchType.SUBTOPIC_SHIFT
            },
            
            "return_indicators": {
                "patterns": [
                    r"back to", r"returning to", r"earlier you mentioned", r"you said before",
                    r"going back", r"as we discussed", r"from before"
                ],
                "confidence_boost": 0.4,
                "switch_type": ContextSwitchType.RETURN_TO_PREVIOUS
            },
            
            "branching_indicators": {
                "patterns": [
                    r"related to this", r"similar", r"also", r"what about.*related",
                    r"in the same area", r"connected", r"ties into"
                ],
                "confidence_boost": 0.25,
                "switch_type": ContextSwitchType.BRANCHING
            },
            
            "clarification_switch": {
                "patterns": [
                    r"to clarify", r"what i meant", r"let me be clear", r"specifically",
                    r"more precisely", r"actually i meant", r"correction"
                ],
                "confidence_boost": 0.35,
                "switch_type": ContextSwitchType.CLARIFICATION_SWITCH
            },
            
            "goal_refinement": {
                "patterns": [
                    r"actually i need", r"what i really want", r"more specifically",
                    r"to be more precise", r"i'm looking for", r"let me rephrase"
                ],
                "confidence_boost": 0.3,
                "switch_type": ContextSwitchType.GOAL_REFINEMENT
            }
        }
    
    def _initialize_preservation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize rules for what context to preserve during switches"""
        return {
            "user_preferences": {
                "always_preserve": True,
                "reason": "User preferences should persist across all topics"
            },
            
            "location_constraints": {
                "preserve_condition": "topic_related_to_location",
                "reason": "Location preferences may be relevant to new topic"
            },
            
            "date_constraints": {
                "preserve_condition": "topic_involves_scheduling",
                "reason": "Time constraints often apply across related topics"
            },
            
            "user_goals": {
                "preserve_condition": "goal_not_explicitly_changed",
                "reason": "User goals may span multiple conversation topics"
            },
            
            "persona_context": {
                "always_preserve": True,
                "reason": "User persona informs response style regardless of topic"
            },
            
            "conversation_style": {
                "always_preserve": True,
                "reason": "Conversation style preferences persist"
            },
            
            "previous_search_results": {
                "preserve_condition": "topic_similarity_above_threshold",
                "threshold": 0.3,
                "reason": "Previous results may be relevant to related topics"
            }
        }
    
    def _initialize_transition_strategies(self) -> Dict[ContextSwitchType, Dict[str, Any]]:
        """Initialize strategies for different types of context switches"""
        return {
            ContextSwitchType.TOPIC_CHANGE: {
                "acknowledgment_template": "I understand you'd like to explore {new_topic} now.",
                "bridge_strategy": "clean_transition",
                "context_preservation": "minimal",
                "response_adjustment": "fresh_start"
            },
            
            ContextSwitchType.SUBTOPIC_SHIFT: {
                "acknowledgment_template": "Let me help you with {new_subtopic} within {main_topic}.",
                "bridge_strategy": "contextual_connection",
                "context_preservation": "moderate",
                "response_adjustment": "build_on_previous"
            },
            
            ContextSwitchType.RETURN_TO_PREVIOUS: {
                "acknowledgment_template": "Going back to {previous_topic} as you mentioned.",
                "bridge_strategy": "context_restoration",
                "context_preservation": "full_restoration",
                "response_adjustment": "continue_previous_thread"
            },
            
            ContextSwitchType.BRANCHING: {
                "acknowledgment_template": "That's a great related question about {related_topic}.",
                "bridge_strategy": "show_connection",
                "context_preservation": "selective_related",
                "response_adjustment": "connect_to_previous"
            },
            
            ContextSwitchType.CLARIFICATION_SWITCH: {
                "acknowledgment_template": "Let me clarify that for you.",
                "bridge_strategy": "clarification_focus",
                "context_preservation": "full_context",
                "response_adjustment": "clarify_and_expand"
            },
            
            ContextSwitchType.GOAL_REFINEMENT: {
                "acknowledgment_template": "I see you're refining what you're looking for.",
                "bridge_strategy": "goal_alignment",
                "context_preservation": "update_goals",
                "response_adjustment": "realign_to_new_goal"
            }
        }
    
    async def detect_context_switch(
        self,
        current_message: str,
        conversation_state: ConversationState,
        previous_context: Optional[Dict[str, Any]] = None
    ) -> ContextSwitchResult:
        """Detect when user switches conversation topics"""
        
        if not previous_context:
            previous_context = conversation_state.get_current_context()
        
        # Analyze current message for switch indicators
        switch_indicators = await self._analyze_switch_indicators(current_message)
        
        # Extract new context from current message
        new_context = await self._extract_context_from_message(current_message, conversation_state)
        
        # Calculate topic similarity
        topic_similarity = await self._calculate_topic_similarity(previous_context, new_context)
        
        # Determine if switch occurred
        switch_detected, switch_type, confidence = await self._evaluate_context_switch(
            switch_indicators, topic_similarity, previous_context, new_context
        )
        
        if not switch_detected:
            return ContextSwitchResult(
                switch_detected=False,
                switch_type=None,
                confidence=0.0,
                previous_context=previous_context,
                new_context=new_context,
                preserved_elements=[],
                switch_trigger="no_switch",
                topic_relationship="continuous",
                user_intent_change=False,
                transition_strategy="none",
                context_bridge_needed=False,
                suggested_acknowledgment=""
            )
        
        # Analyze switch characteristics
        switch_trigger = self._identify_switch_trigger(current_message, switch_indicators)
        topic_relationship = self._analyze_topic_relationship(previous_context, new_context, topic_similarity)
        user_intent_change = await self._detect_intent_change(conversation_state, new_context)
        
        # Determine preservation elements
        preserved_elements = await self._determine_preserved_elements(
            previous_context, new_context, switch_type, topic_relationship
        )
        
        # Select transition strategy
        transition_strategy = self._select_transition_strategy(switch_type, topic_relationship)
        context_bridge_needed = self._assess_bridge_necessity(switch_type, topic_similarity)
        
        # Generate acknowledgment
        suggested_acknowledgment = await self._generate_switch_acknowledgment(
            switch_type, previous_context, new_context
        )
        
        # Create result
        result = ContextSwitchResult(
            switch_detected=True,
            switch_type=switch_type,
            confidence=confidence,
            previous_context=previous_context,
            new_context=new_context,
            preserved_elements=preserved_elements,
            switch_trigger=switch_trigger,
            topic_relationship=topic_relationship,
            user_intent_change=user_intent_change,
            transition_strategy=transition_strategy,
            context_bridge_needed=context_bridge_needed,
            suggested_acknowledgment=suggested_acknowledgment
        )
        
        # Store switch for learning
        user_id = conversation_state.user_id
        self.switch_history[user_id].append(result)
        
        return result
    
    async def _analyze_switch_indicators(self, message: str) -> Dict[str, float]:
        """Analyze message for context switch indicators"""
        
        indicators = {}
        message_lower = message.lower()
        
        for pattern_name, pattern_config in self.switch_patterns.items():
            pattern_score = 0.0
            
            for pattern in pattern_config["patterns"]:
                if re.search(pattern, message_lower):
                    pattern_score += pattern_config["confidence_boost"]
            
            indicators[pattern_name] = min(1.0, pattern_score)
        
        # Additional heuristics
        indicators["length_change"] = self._analyze_message_length_change(message)
        indicators["question_to_statement"] = self._analyze_question_statement_change(message)
        indicators["new_keywords"] = await self._analyze_new_keywords(message)
        
        return indicators
    
    async def _extract_context_from_message(
        self,
        message: str,
        conversation_state: ConversationState
    ) -> Dict[str, Any]:
        """Extract context information from current message"""
        
        context = {
            "topics": self._extract_topics_from_message(message),
            "intent": self._infer_intent_from_message(message),
            "entities": await self._extract_entities_from_message(message),
            "question_type": self._classify_question_type(message),
            "urgency": self._assess_message_urgency(message),
            "specificity": self._assess_message_specificity(message)
        }
        
        return context
    
    async def _calculate_topic_similarity(
        self,
        previous_context: Dict[str, Any],
        new_context: Dict[str, Any]
    ) -> float:
        """Calculate similarity between previous and new context topics"""
        
        prev_topics = set(previous_context.get("topics", []))
        new_topics = set(new_context.get("topics", []))
        
        if not prev_topics or not new_topics:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(prev_topics.intersection(new_topics))
        union = len(prev_topics.union(new_topics))
        
        jaccard_similarity = intersection / union if union > 0 else 0.0
        
        # Add semantic similarity bonus for related topics
        semantic_bonus = await self._calculate_semantic_similarity(prev_topics, new_topics)
        
        return min(1.0, jaccard_similarity + semantic_bonus)
    
    async def _evaluate_context_switch(
        self,
        switch_indicators: Dict[str, float],
        topic_similarity: float,
        previous_context: Dict[str, Any],
        new_context: Dict[str, Any]
    ) -> Tuple[bool, Optional[ContextSwitchType], float]:
        """Evaluate if context switch occurred and determine type"""
        
        # Calculate overall switch score
        indicator_scores = list(switch_indicators.values())
        avg_indicator_score = sum(indicator_scores) / len(indicator_scores) if indicator_scores else 0
        
        # Topic dissimilarity contributes to switch likelihood
        dissimilarity_score = 1.0 - topic_similarity
        
        # Combined switch confidence
        switch_confidence = (avg_indicator_score * 0.6) + (dissimilarity_score * 0.4)
        
        # Determine if switch occurred
        switch_detected = switch_confidence > 0.4
        
        if not switch_detected:
            return False, None, switch_confidence
        
        # Determine switch type based on strongest indicator
        switch_type = None
        max_indicator_score = 0.0
        
        for pattern_name, score in switch_indicators.items():
            if score > max_indicator_score and pattern_name in self.switch_patterns:
                max_indicator_score = score
                switch_type = self.switch_patterns[pattern_name]["switch_type"]
        
        # Default to topic change if no specific type identified
        if not switch_type:
            switch_type = ContextSwitchType.TOPIC_CHANGE
        
        return switch_detected, switch_type, switch_confidence
    
    def _identify_switch_trigger(
        self,
        message: str,
        switch_indicators: Dict[str, float]
    ) -> str:
        """Identify what triggered the context switch"""
        
        # Find strongest indicator
        max_indicator = max(switch_indicators.items(), key=lambda x: x[1])
        
        trigger_mapping = {
            "explicit_topic_change": "explicit_user_request",
            "question_transition": "new_question_posed",
            "return_indicators": "user_returned_to_previous_topic",
            "branching_indicators": "user_explored_related_topic",
            "clarification_switch": "user_sought_clarification",
            "goal_refinement": "user_refined_goals"
        }
        
        return trigger_mapping.get(max_indicator[0], "topic_evolution")
    
    def _analyze_topic_relationship(
        self,
        previous_context: Dict[str, Any],
        new_context: Dict[str, Any],
        topic_similarity: float
    ) -> str:
        """Analyze relationship between previous and new topics"""
        
        if topic_similarity > 0.7:
            return "closely_related"
        elif topic_similarity > 0.3:
            return "related"
        elif topic_similarity > 0.1:
            return "loosely_related"
        else:
            return "unrelated"
    
    async def _detect_intent_change(
        self,
        conversation_state: ConversationState,
        new_context: Dict[str, Any]
    ) -> bool:
        """Detect if user intent has changed"""
        
        current_intent = conversation_state.current_intent
        new_intent = new_context.get("intent")
        
        if not current_intent or not new_intent:
            return False
        
        # Simple intent comparison - can be enhanced with semantic analysis
        return current_intent != new_intent
    
    async def _determine_preserved_elements(
        self,
        previous_context: Dict[str, Any],
        new_context: Dict[str, Any],
        switch_type: ContextSwitchType,
        topic_relationship: str
    ) -> List[str]:
        """Determine which context elements should be preserved"""
        
        preserved = []
        
        for element, rule in self.preservation_rules.items():
            should_preserve = False
            
            if rule.get("always_preserve", False):
                should_preserve = True
            elif "preserve_condition" in rule:
                condition = rule["preserve_condition"]
                should_preserve = await self._evaluate_preservation_condition(
                    condition, previous_context, new_context, switch_type, topic_relationship
                )
            
            if should_preserve:
                preserved.append(element)
        
        return preserved
    
    async def _evaluate_preservation_condition(
        self,
        condition: str,
        previous_context: Dict[str, Any],
        new_context: Dict[str, Any],
        switch_type: ContextSwitchType,
        topic_relationship: str
    ) -> bool:
        """Evaluate whether a preservation condition is met"""
        
        if condition == "topic_related_to_location":
            return "location" in new_context.get("entities", {})
        
        elif condition == "topic_involves_scheduling":
            scheduling_keywords = ["event", "meeting", "conference", "date", "time", "schedule"]
            new_topics = new_context.get("topics", [])
            return any(keyword in topic.lower() for topic in new_topics for keyword in scheduling_keywords)
        
        elif condition == "goal_not_explicitly_changed":
            return switch_type != ContextSwitchType.GOAL_REFINEMENT
        
        elif condition == "topic_similarity_above_threshold":
            # This would use the threshold from the rule
            return topic_relationship in ["closely_related", "related"]
        
        return False
    
    def _select_transition_strategy(
        self,
        switch_type: ContextSwitchType,
        topic_relationship: str
    ) -> str:
        """Select appropriate transition strategy"""
        
        strategy_config = self.transition_strategies.get(switch_type, {})
        base_strategy = strategy_config.get("bridge_strategy", "clean_transition")
        
        # Adjust strategy based on topic relationship
        if topic_relationship == "unrelated":
            return "clean_break_transition"
        elif topic_relationship in ["closely_related", "related"]:
            return "contextual_bridge_transition"
        else:
            return base_strategy
    
    def _assess_bridge_necessity(
        self,
        switch_type: ContextSwitchType,
        topic_similarity: float
    ) -> bool:
        """Assess whether a context bridge is needed"""
        
        # Always bridge for returns to previous topics
        if switch_type == ContextSwitchType.RETURN_TO_PREVIOUS:
            return True
        
        # Bridge for related topics
        if topic_similarity > 0.3:
            return True
        
        # Bridge for clarifications
        if switch_type == ContextSwitchType.CLARIFICATION_SWITCH:
            return True
        
        return False
    
    async def _generate_switch_acknowledgment(
        self,
        switch_type: ContextSwitchType,
        previous_context: Dict[str, Any],
        new_context: Dict[str, Any]
    ) -> str:
        """Generate appropriate acknowledgment for context switch"""
        
        strategy_config = self.transition_strategies.get(switch_type, {})
        template = strategy_config.get("acknowledgment_template", "I understand you'd like to explore something different.")
        
        # Extract topic information for template
        previous_topic = self._extract_main_topic(previous_context)
        new_topic = self._extract_main_topic(new_context)
        
        # Fill template
        acknowledgment = template.format(
            new_topic=new_topic,
            previous_topic=previous_topic,
            main_topic=new_topic,  # For subtopic shifts
            new_subtopic=new_topic,
            related_topic=new_topic
        )
        
        return acknowledgment
    
    async def manage_smooth_transition(
        self,
        switch_result: ContextSwitchResult,
        conversation_state: ConversationState
    ) -> TransitionPlan:
        """Plan smooth transition preserving relevant context"""
        
        if not switch_result.switch_detected:
            return TransitionPlan(
                acknowledgment_message="",
                context_bridge={},
                preserved_context={},
                response_adjustments=[],
                proactive_suggestions=[],
                transition_type="no_transition",
                estimated_success_rate=1.0,
                fallback_strategy="continue_normally"
            )
        
        # Generate acknowledgment message
        acknowledgment = switch_result.suggested_acknowledgment
        
        # Create context bridge
        context_bridge = await self._create_context_bridge(switch_result)
        
        # Preserve relevant context
        preserved_context = await self.preserve_context_across_switch(
            switch_result.previous_context,
            switch_result.new_context,
            switch_result.preserved_elements
        )
        
        # Generate response adjustments
        response_adjustments = await self._generate_response_adjustments(switch_result)
        
        # Generate proactive suggestions
        proactive_suggestions = await self._generate_transition_suggestions(switch_result)
        
        # Estimate success rate
        estimated_success_rate = self._estimate_transition_success_rate(switch_result)
        
        # Determine fallback strategy
        fallback_strategy = self._determine_fallback_strategy(switch_result)
        
        return TransitionPlan(
            acknowledgment_message=acknowledgment,
            context_bridge=context_bridge,
            preserved_context=preserved_context,
            response_adjustments=response_adjustments,
            proactive_suggestions=proactive_suggestions,
            transition_type=switch_result.transition_strategy,
            estimated_success_rate=estimated_success_rate,
            fallback_strategy=fallback_strategy
        )
    
    async def preserve_context_across_switch(
        self,
        old_context: Dict[str, Any],
        new_context: Dict[str, Any],
        preserved_elements: List[str] = None
    ) -> Dict[str, Any]:
        """Preserve relevant context elements during topic switch"""
        
        if not preserved_elements:
            preserved_elements = ["user_preferences", "persona_context", "conversation_style"]
        
        preserved_context = {}
        
        for element in preserved_elements:
            if element in old_context:
                preserved_context[element] = old_context[element]
        
        # Merge with new context, prioritizing new information
        merged_context = {**preserved_context, **new_context}
        
        # Add transition metadata
        merged_context["transition_metadata"] = {
            "previous_topic": self._extract_main_topic(old_context),
            "transition_time": datetime.utcnow().isoformat(),
            "preserved_elements": preserved_elements
        }
        
        return merged_context
    
    async def _create_context_bridge(self, switch_result: ContextSwitchResult) -> Dict[str, Any]:
        """Create bridge connecting previous and new context"""
        
        bridge = {
            "connection_type": switch_result.topic_relationship,
            "bridge_elements": [],
            "transition_cues": []
        }
        
        if switch_result.topic_relationship in ["closely_related", "related"]:
            # Find connecting elements
            prev_topics = set(switch_result.previous_context.get("topics", []))
            new_topics = set(switch_result.new_context.get("topics", []))
            common_topics = prev_topics.intersection(new_topics)
            
            bridge["bridge_elements"] = list(common_topics)
            bridge["transition_cues"] = [
                f"Building on our discussion of {topic}" for topic in common_topics
            ]
        
        elif switch_result.switch_type == ContextSwitchType.RETURN_TO_PREVIOUS:
            bridge["bridge_elements"] = ["previous_conversation_reference"]
            bridge["transition_cues"] = ["Returning to your earlier question"]
        
        return bridge
    
    async def _generate_response_adjustments(self, switch_result: ContextSwitchResult) -> List[str]:
        """Generate response adjustments for context switch"""
        
        adjustments = []
        
        if switch_result.switch_type == ContextSwitchType.CLARIFICATION_SWITCH:
            adjustments.extend([
                "use_simpler_language",
                "provide_examples",
                "break_down_complex_concepts"
            ])
        
        elif switch_result.switch_type == ContextSwitchType.GOAL_REFINEMENT:
            adjustments.extend([
                "realign_to_new_goals",
                "acknowledge_refinement",
                "focus_on_specific_needs"
            ])
        
        elif switch_result.topic_relationship == "unrelated":
            adjustments.extend([
                "fresh_start_approach",
                "reset_context_assumptions",
                "new_conversation_thread"
            ])
        
        elif switch_result.topic_relationship in ["related", "closely_related"]:
            adjustments.extend([
                "connect_to_previous_discussion",
                "build_on_established_context",
                "reference_related_information"
            ])
        
        return adjustments
    
    async def _generate_transition_suggestions(self, switch_result: ContextSwitchResult) -> List[str]:
        """Generate proactive suggestions for smooth transition"""
        
        suggestions = []
        
        if switch_result.context_bridge_needed:
            suggestions.append("Explain connection to previous topic")
        
        if switch_result.switch_type == ContextSwitchType.BRANCHING:
            suggestions.append("Offer to explore both topics systematically")
        
        if switch_result.topic_relationship == "related":
            suggestions.append("Suggest comprehensive approach covering related areas")
        
        return suggestions
    
    def _estimate_transition_success_rate(self, switch_result: ContextSwitchResult) -> float:
        """Estimate likelihood of successful transition"""
        
        base_rate = 0.7  # Base success rate
        
        # Adjust based on switch characteristics
        if switch_result.confidence > 0.8:
            base_rate += 0.1  # Clear switches are easier to handle
        
        if switch_result.topic_relationship in ["closely_related", "related"]:
            base_rate += 0.15  # Related topics are easier to transition
        
        if switch_result.context_bridge_needed and switch_result.topic_relationship == "unrelated":
            base_rate -= 0.1  # Unrelated topics with bridges are more challenging
        
        return min(1.0, max(0.0, base_rate))
    
    def _determine_fallback_strategy(self, switch_result: ContextSwitchResult) -> str:
        """Determine fallback strategy if transition fails"""
        
        if switch_result.switch_type == ContextSwitchType.CLARIFICATION_SWITCH:
            return "provide_alternative_explanation"
        
        elif switch_result.topic_relationship == "unrelated":
            return "acknowledge_switch_and_proceed"
        
        else:
            return "ask_for_clarification"
    
    # Helper methods
    
    def _analyze_message_length_change(self, message: str) -> float:
        """Analyze significant changes in message length"""
        # This would compare with previous messages
        # For now, return neutral score
        return 0.0
    
    def _analyze_question_statement_change(self, message: str) -> float:
        """Analyze change from question to statement or vice versa"""
        has_question = "?" in message
        # This would compare with previous message type
        return 0.0
    
    async def _analyze_new_keywords(self, message: str) -> float:
        """Analyze presence of completely new keywords"""
        # This would compare keywords with previous conversation
        # For now, return neutral score
        return 0.0
    
    def _extract_topics_from_message(self, message: str) -> List[str]:
        """Extract topics from message"""
        # Simple keyword extraction - matches pattern_recognition.py
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
    
    def _infer_intent_from_message(self, message: str) -> str:
        """Infer user intent from message"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["find", "search", "look for", "show me"]):
            return "search"
        elif any(word in message_lower for word in ["explain", "what is", "how does"]):
            return "explanation"
        elif any(word in message_lower for word in ["register", "sign up", "book"]):
            return "registration"
        else:
            return "general_inquiry"
    
    async def _extract_entities_from_message(self, message: str) -> Dict[str, Any]:
        """Extract entities from message"""
        # Simple entity extraction
        entities = {}
        
        # Date patterns
        date_patterns = [r"\d{1,2}/\d{1,2}", r"january|february|march|april|may|june|july|august|september|october|november|december"]
        for pattern in date_patterns:
            if re.search(pattern, message.lower()):
                entities["date"] = "date_mentioned"
                break
        
        # Location patterns
        location_keywords = ["in", "at", "near", "around", "city", "country"]
        if any(keyword in message.lower() for keyword in location_keywords):
            entities["location"] = "location_mentioned"
        
        return entities
    
    def _classify_question_type(self, message: str) -> str:
        """Classify type of question"""
        if "?" not in message:
            return "statement"
        
        message_lower = message.lower()
        
        if message_lower.startswith(("what", "which")):
            return "what_question"
        elif message_lower.startswith(("how", "why")):
            return "how_why_question"
        elif message_lower.startswith(("when", "where")):
            return "when_where_question"
        else:
            return "yes_no_question"
    
    def _assess_message_urgency(self, message: str) -> str:
        """Assess urgency level of message"""
        urgent_keywords = ["urgent", "asap", "quickly", "immediately", "soon"]
        if any(keyword in message.lower() for keyword in urgent_keywords):
            return "high"
        
        return "normal"
    
    def _assess_message_specificity(self, message: str) -> str:
        """Assess specificity level of message"""
        specific_indicators = ["specific", "exactly", "precisely", "particular"]
        if any(indicator in message.lower() for indicator in specific_indicators):
            return "high"
        
        general_indicators = ["general", "overview", "anything", "something"]
        if any(indicator in message.lower() for indicator in general_indicators):
            return "low"
        
        return "medium"
    
    async def _calculate_semantic_similarity(self, topics1: set, topics2: set) -> float:
        """Calculate semantic similarity between topic sets"""
        # Simple semantic similarity - can be enhanced with embeddings
        crypto_related_groups = [
            {"defi", "liquidity", "yield", "staking", "protocol"},
            {"nft", "blockchain", "ethereum", "token"},
            {"trading", "investment", "bitcoin", "crypto"},
            {"conference", "event", "meetup"}
        ]
        
        for group in crypto_related_groups:
            if topics1.intersection(group) and topics2.intersection(group):
                return 0.3  # Semantic similarity bonus
        
        return 0.0
    
    def _extract_main_topic(self, context: Dict[str, Any]) -> str:
        """Extract main topic from context"""
        topics = context.get("topics", [])
        if topics:
            return topics[0]  # Return first/primary topic
        
        intent = context.get("intent", "")
        if intent:
            return intent
        
        return "general discussion"
    
    async def get_context_switch_metrics(self) -> Dict[str, Any]:
        """Get context switching metrics for monitoring"""
        
        total_switches = sum(len(switches) for switches in self.switch_history.values())
        
        if total_switches == 0:
            return {"total_switches_detected": 0}
        
        switch_type_distribution = defaultdict(int)
        confidence_scores = []
        successful_transitions = 0
        
        for user_switches in self.switch_history.values():
            for switch in user_switches:
                if switch.switch_type:
                    switch_type_distribution[switch.switch_type.value] += 1
                confidence_scores.append(switch.confidence)
                
                # Estimate success based on confidence and relationship
                if switch.confidence > 0.7 and switch.topic_relationship != "unrelated":
                    successful_transitions += 1
        
        return {
            "total_switches_detected": total_switches,
            "switch_type_distribution": dict(switch_type_distribution),
            "average_switch_confidence": sum(confidence_scores) / len(confidence_scores),
            "high_confidence_switches": sum(1 for score in confidence_scores if score > 0.7),
            "estimated_successful_transitions": successful_transitions,
            "transition_success_rate": successful_transitions / total_switches,
            "smooth_transition_target": 0.9,  # 90% smooth transitions target
            "target_achieved": (successful_transitions / total_switches) >= 0.9
        }

# Global instance for shared access
context_switch_manager = ContextSwitchManager()