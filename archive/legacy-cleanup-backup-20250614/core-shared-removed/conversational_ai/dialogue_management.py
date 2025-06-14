# Conversational AI Intelligent Dialogue Manager
# Orchestrates all Phase 2 components for coherent dialogue flow

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import json

from .state_management import ConversationState, ConversationStateManager, conversation_state_manager
from .pattern_recognition import ConversationPatternDetector, PatternMatch, pattern_detector
from .context_switching import ContextSwitchManager, ContextSwitchResult, TransitionPlan, context_switch_manager
from .proactive_suggestions import ProactiveSuggestionEngine, ProactiveSuggestion, proactive_suggestion_engine
from .persona_modeling import PersonaManager, UserPersona, persona_manager

class DialogueFlowResult:
    """Comprehensive result of dialogue flow management"""
    
    def __init__(
        self,
        patterns: List[PatternMatch],
        context_switch: ContextSwitchResult,
        proactive_suggestions: List[ProactiveSuggestion],
        dialogue_recommendations: List[str],
        enhanced_response_context: Dict[str, Any],
        conversation_state: ConversationState,
        user_persona: UserPersona,
        transition_plan: Optional[TransitionPlan] = None
    ):
        self.patterns = patterns
        self.context_switch = context_switch
        self.proactive_suggestions = proactive_suggestions
        self.dialogue_recommendations = dialogue_recommendations
        self.enhanced_response_context = enhanced_response_context
        self.conversation_state = conversation_state
        self.user_persona = user_persona
        self.transition_plan = transition_plan
        
        # Calculate overall dialogue quality metrics
        self.dialogue_quality = self._calculate_dialogue_quality()
        self.proactive_assistance_rate = len(proactive_suggestions) > 0
        self.context_continuity = self._calculate_context_continuity()
        
    def _calculate_dialogue_quality(self) -> float:
        """Calculate overall dialogue quality score"""
        
        # Base quality from pattern detection
        pattern_quality = max([p.confidence for p in self.patterns]) if self.patterns else 0.5
        
        # Context switch handling quality
        switch_quality = 1.0 - (self.context_switch.confidence if self.context_switch.switch_detected else 0.0)
        
        # Suggestion quality
        suggestion_quality = max([s.confidence for s in self.proactive_suggestions]) if self.proactive_suggestions else 0.7
        
        # Persona alignment
        persona_quality = self.user_persona.persona_confidence
        
        return (pattern_quality * 0.3 + switch_quality * 0.2 + suggestion_quality * 0.3 + persona_quality * 0.2)
    
    def _calculate_context_continuity(self) -> float:
        """Calculate context continuity score"""
        
        if not self.context_switch.switch_detected:
            return 1.0  # Perfect continuity when no switch
        
        # Evaluate how well context is preserved during switch
        if self.transition_plan:
            return self.transition_plan.estimated_success_rate
        
        return 1.0 - self.context_switch.confidence  # Inverse of switch disruption
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "patterns": [p.to_dict() for p in self.patterns],
            "context_switch": self.context_switch.to_dict(),
            "proactive_suggestions": [s.to_dict() for s in self.proactive_suggestions],
            "dialogue_recommendations": self.dialogue_recommendations,
            "enhanced_response_context": self.enhanced_response_context,
            "dialogue_quality": self.dialogue_quality,
            "proactive_assistance_rate": self.proactive_assistance_rate,
            "context_continuity": self.context_continuity,
            "transition_plan": self.transition_plan.to_dict() if self.transition_plan else None
        }

class IntelligentDialogueManager:
    """Orchestrates all Phase 2 components for coherent dialogue flow"""
    
    def __init__(self):
        # Component instances
        self.pattern_detector = pattern_detector
        self.context_switcher = context_switch_manager
        self.suggestion_engine = proactive_suggestion_engine
        self.conversation_manager = conversation_state_manager
        self.persona_manager = persona_manager
        
        # Performance tracking
        self.dialogue_metrics: Dict[str, Any] = {
            "total_dialogues_processed": 0,
            "successful_pattern_detections": 0,
            "smooth_context_transitions": 0,
            "proactive_suggestions_provided": 0,
            "average_dialogue_quality": 0.0
        }
        
        # Dialogue flow optimization settings
        self.optimization_settings = {
            "max_suggestions_per_turn": 3,
            "min_confidence_for_pattern": 0.4,
            "context_switch_sensitivity": 0.6,
            "suggestion_frequency_limit": timedelta(minutes=2)
        }
    
    async def manage_dialogue_flow(
        self,
        user_id: str,
        current_message: str,
        conversation_state: Optional[ConversationState] = None,
        api_response_context: Optional[Dict[str, Any]] = None
    ) -> DialogueFlowResult:
        """Comprehensive dialogue flow management"""
        
        try:
            # Get or create conversation state
            if not conversation_state:
                conversation_state = await self.conversation_manager.get_conversation_state(user_id)
            
            # Update conversation with current message
            conversation_state.update_activity()
            
            # Get or update user persona
            user_persona = await self.persona_manager.update_persona_from_conversation(
                user_id, current_message, conversation_state, api_response_context
            )
            
            # 1. Detect conversation patterns
            patterns = await self._detect_conversation_patterns(
                current_message, conversation_state
            )
            
            # 2. Handle context switching
            context_switch_result = await self._handle_context_switching(
                current_message, conversation_state
            )
            
            # 3. Generate proactive suggestions
            proactive_suggestions = await self._generate_proactive_suggestions(
                conversation_state, patterns, user_persona, api_response_context
            )
            
            # 4. Create transition plan if needed
            transition_plan = None
            if context_switch_result.switch_detected:
                transition_plan = await self._create_transition_plan(
                    context_switch_result, conversation_state
                )
            
            # 5. Generate dialogue recommendations
            dialogue_recommendations = await self._generate_dialogue_recommendations(
                patterns, context_switch_result, proactive_suggestions, user_persona
            )
            
            # 6. Create enhanced response context
            enhanced_context = await self._create_enhanced_response_context(
                conversation_state, user_persona, patterns, context_switch_result, api_response_context
            )
            
            # 7. Update conversation state with new context
            await self._update_conversation_context(
                user_id, current_message, enhanced_context, patterns
            )
            
            # Create and return result
            result = DialogueFlowResult(
                patterns=patterns,
                context_switch=context_switch_result,
                proactive_suggestions=proactive_suggestions,
                dialogue_recommendations=dialogue_recommendations,
                enhanced_response_context=enhanced_context,
                conversation_state=conversation_state,
                user_persona=user_persona,
                transition_plan=transition_plan
            )
            
            # Update metrics
            await self._update_dialogue_metrics(result)
            
            return result
            
        except Exception as e:
            # Fallback to basic dialogue management
            return await self._fallback_dialogue_management(
                user_id, current_message, conversation_state, str(e)
            )
    
    async def _detect_conversation_patterns(
        self,
        current_message: str,
        conversation_state: ConversationState
    ) -> List[PatternMatch]:
        """Detect conversation patterns from user behavior"""
        
        try:
            patterns = await self.pattern_detector.detect_patterns(
                conversation_state.conversation_memory,
                current_message,
                conversation_state
            )
            
            # Filter patterns by confidence threshold
            min_confidence = self.optimization_settings["min_confidence_for_pattern"]
            return [p for p in patterns if p.confidence >= min_confidence]
            
        except Exception as e:
            print(f"Pattern detection error: {e}")
            return []
    
    async def _handle_context_switching(
        self,
        current_message: str,
        conversation_state: ConversationState
    ) -> ContextSwitchResult:
        """Handle context switching detection and management"""
        
        try:
            # Detect context switch
            context_switch_result = await self.context_switcher.detect_context_switch(
                current_message,
                conversation_state
            )
            
            return context_switch_result
            
        except Exception as e:
            print(f"Context switching error: {e}")
            # Return no-switch result as fallback
            return ContextSwitchResult(
                switch_detected=False,
                switch_type=None,
                confidence=0.0,
                previous_context={},
                new_context={},
                preserved_elements=[],
                switch_trigger="error_fallback",
                topic_relationship="continuous",
                user_intent_change=False,
                transition_strategy="none",
                context_bridge_needed=False,
                suggested_acknowledgment=""
            )
    
    async def _generate_proactive_suggestions(
        self,
        conversation_state: ConversationState,
        patterns: List[PatternMatch],
        user_persona: UserPersona,
        api_response_context: Optional[Dict[str, Any]]
    ) -> List[ProactiveSuggestion]:
        """Generate proactive suggestions based on dialogue context"""
        
        try:
            # Get the strongest pattern for suggestion generation
            primary_pattern = patterns[0] if patterns else None
            
            # Generate suggestions
            suggestions = await self.suggestion_engine.generate_suggestions(
                conversation_state,
                primary_pattern,
                user_persona,
                api_response_context or {}
            )
            
            # Limit number of suggestions
            max_suggestions = self.optimization_settings["max_suggestions_per_turn"]
            return suggestions[:max_suggestions]
            
        except Exception as e:
            print(f"Suggestion generation error: {e}")
            return []
    
    async def _create_transition_plan(
        self,
        context_switch_result: ContextSwitchResult,
        conversation_state: ConversationState
    ) -> Optional[TransitionPlan]:
        """Create transition plan for context switches"""
        
        try:
            if context_switch_result.switch_detected:
                return await self.context_switcher.manage_smooth_transition(
                    context_switch_result,
                    conversation_state
                )
            return None
            
        except Exception as e:
            print(f"Transition planning error: {e}")
            return None
    
    async def _generate_dialogue_recommendations(
        self,
        patterns: List[PatternMatch],
        context_switch: ContextSwitchResult,
        suggestions: List[ProactiveSuggestion],
        user_persona: UserPersona
    ) -> List[str]:
        """Generate dialogue recommendations for response enhancement"""
        
        recommendations = []
        
        # Pattern-based recommendations
        if patterns:
            primary_pattern = patterns[0]
            pattern_recommendations = self._get_pattern_recommendations(primary_pattern)
            recommendations.extend(pattern_recommendations)
        
        # Context switch recommendations
        if context_switch.switch_detected:
            switch_recommendations = self._get_context_switch_recommendations(context_switch)
            recommendations.extend(switch_recommendations)
        
        # Persona-based recommendations
        persona_recommendations = self._get_persona_recommendations(user_persona)
        recommendations.extend(persona_recommendations)
        
        # Suggestion-based recommendations
        if suggestions:
            suggestion_recommendations = self._get_suggestion_recommendations(suggestions)
            recommendations.extend(suggestion_recommendations)
        
        # Remove duplicates and return top recommendations
        unique_recommendations = list(set(recommendations))
        return unique_recommendations[:5]  # Top 5 recommendations
    
    def _get_pattern_recommendations(self, pattern: PatternMatch) -> List[str]:
        """Get recommendations based on detected pattern"""
        
        pattern_recommendations = {
            "deep_dive": [
                "Provide comprehensive and detailed information",
                "Offer technical specifications and in-depth analysis",
                "Include practical examples and use cases"
            ],
            "exploration": [
                "Suggest related topics and areas of interest",
                "Provide overview information with breadth",
                "Offer discovery paths and exploration options"
            ],
            "clarification_cascade": [
                "Use simpler language and clearer explanations",
                "Break down complex concepts into steps",
                "Provide alternative explanations and examples"
            ],
            "goal_oriented": [
                "Focus on actionable information and next steps",
                "Provide direct answers to specific questions",
                "Offer task completion guidance"
            ],
            "learning_journey": [
                "Structure information as learning progression",
                "Connect concepts to build understanding",
                "Suggest next learning steps"
            ],
            "research_mode": [
                "Provide comprehensive data and analysis",
                "Include detailed specifications and comparisons",
                "Offer thorough research methodology"
            ]
        }
        
        return pattern_recommendations.get(pattern.pattern.value, ["Provide relevant and helpful information"])
    
    def _get_context_switch_recommendations(self, context_switch: ContextSwitchResult) -> List[str]:
        """Get recommendations for handling context switches"""
        
        if not context_switch.switch_detected:
            return ["Maintain conversation continuity"]
        
        recommendations = []
        
        # Add acknowledgment if suggested
        if context_switch.suggested_acknowledgment:
            recommendations.append(f"Acknowledge topic change: '{context_switch.suggested_acknowledgment}'")
        
        # Add bridge recommendations
        if context_switch.context_bridge_needed:
            recommendations.append("Provide context bridge to connect topics")
        
        # Add transition strategy recommendations
        strategy_recommendations = {
            "clean_transition": "Make clear transition to new topic",
            "contextual_connection": "Show connection between topics",
            "context_restoration": "Restore previous context smoothly",
            "show_connection": "Highlight relationship between topics",
            "clarification_focus": "Focus on clarifying user intent",
            "goal_alignment": "Align response with refined goals"
        }
        
        strategy_rec = strategy_recommendations.get(context_switch.transition_strategy)
        if strategy_rec:
            recommendations.append(strategy_rec)
        
        return recommendations
    
    def _get_persona_recommendations(self, persona: UserPersona) -> List[str]:
        """Get recommendations based on user persona"""
        
        persona_recommendations = {
            "crypto_enthusiast": [
                "Use crypto-specific terminology appropriately",
                "Provide community and ecosystem context",
                "Include latest trends and developments"
            ],
            "defi_developer": [
                "Focus on technical implementation details",
                "Provide code examples and technical specifications",
                "Include security and best practices information"
            ],
            "investor": [
                "Emphasize ROI and investment implications",
                "Provide market analysis and comparisons",
                "Focus on risk assessment and opportunities"
            ],
            "researcher": [
                "Provide comprehensive data and sources",
                "Include methodology and analysis details",
                "Offer multiple perspectives and deep insights"
            ],
            "student": [
                "Use educational structure and progression",
                "Provide clear explanations with examples",
                "Suggest learning resources and next steps"
            ],
            "entrepreneur": [
                "Focus on business applications and opportunities",
                "Provide actionable insights and strategies",
                "Include market potential and competitive analysis"
            ],
            "industry_professional": [
                "Use professional language and standards",
                "Provide industry context and best practices",
                "Include regulatory and compliance considerations"
            ],
            "casual_explorer": [
                "Use accessible language and simple explanations",
                "Provide overview information with interesting highlights",
                "Suggest easy next steps for further exploration"
            ]
        }
        
        return persona_recommendations.get(persona.primary_persona.value, ["Provide helpful and relevant information"])
    
    def _get_suggestion_recommendations(self, suggestions: List[ProactiveSuggestion]) -> List[str]:
        """Get recommendations based on proactive suggestions"""
        
        recommendations = []
        
        for suggestion in suggestions:
            if suggestion.suggested_action:
                action_rec = f"Consider {suggestion.suggested_action} based on user behavior"
                recommendations.append(action_rec)
        
        # Add general suggestion recommendation if suggestions were generated
        if suggestions:
            high_priority_count = sum(1 for s in suggestions if s.priority.value == "high")
            if high_priority_count > 0:
                recommendations.append(f"Include {high_priority_count} high-priority proactive suggestions")
            else:
                recommendations.append("Include helpful proactive suggestions for user guidance")
        
        return recommendations
    
    async def _create_enhanced_response_context(
        self,
        conversation_state: ConversationState,
        user_persona: UserPersona,
        patterns: List[PatternMatch],
        context_switch: ContextSwitchResult,
        api_response_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create enhanced context for response generation"""
        
        enhanced_context = {
            # Core conversation context
            "conversation_state": {
                "user_id": conversation_state.user_id,
                "session_id": conversation_state.session_id,
                "turn_count": conversation_state.turn_count,
                "current_state": conversation_state.current_state.value,
                "primary_interests": conversation_state.get_primary_interests(),
                "successful_resolutions": conversation_state.successful_resolutions,
                "clarification_requests": conversation_state.clarification_requests
            },
            
            # User persona context
            "user_persona": {
                "primary_persona": user_persona.primary_persona.value,
                "confidence": user_persona.persona_confidence,
                "experience_level": user_persona.experience_level.value,
                "engagement_style": user_persona.engagement_style.value,
                "personalization_preferences": user_persona.get_personalization_preferences()
            },
            
            # Pattern context
            "conversation_patterns": [
                {
                    "type": pattern.pattern.value,
                    "confidence": pattern.confidence,
                    "duration_minutes": pattern.duration_minutes,
                    "topic_consistency": pattern.topic_consistency
                }
                for pattern in patterns
            ],
            
            # Context switch context
            "context_switch": {
                "switch_detected": context_switch.switch_detected,
                "switch_type": context_switch.switch_type.value if context_switch.switch_type else None,
                "confidence": context_switch.confidence,
                "topic_relationship": context_switch.topic_relationship,
                "transition_strategy": context_switch.transition_strategy,
                "suggested_acknowledgment": context_switch.suggested_acknowledgment
            },
            
            # API context (if provided)
            "api_context": api_response_context or {},
            
            # Dialogue quality metrics
            "dialogue_metrics": {
                "context_preservation_score": conversation_state.calculate_context_preservation_score(),
                "pattern_detection_active": len(patterns) > 0,
                "proactive_assistance_available": True,
                "persona_confidence": user_persona.persona_confidence
            }
        }
        
        return enhanced_context
    
    async def _update_conversation_context(
        self,
        user_id: str,
        current_message: str,
        enhanced_context: Dict[str, Any],
        patterns: List[PatternMatch]
    ):
        """Update conversation context with dialogue flow results"""
        
        try:
            # Extract intent from patterns
            intent = None
            intent_confidence = None
            
            if patterns:
                primary_pattern = patterns[0]
                intent = primary_pattern.pattern.value
                
                # Map confidence to enum
                if primary_pattern.confidence > 0.8:
                    from .state_management import IntentConfidence
                    intent_confidence = IntentConfidence.HIGH
                elif primary_pattern.confidence > 0.5:
                    intent_confidence = IntentConfidence.MEDIUM
                else:
                    intent_confidence = IntentConfidence.LOW
            
            # Update conversation context
            await self.conversation_manager.update_conversation_context(
                user_id,
                enhanced_context,
                intent,
                intent_confidence
            )
            
        except Exception as e:
            print(f"Context update error: {e}")
    
    async def _update_dialogue_metrics(self, result: DialogueFlowResult):
        """Update dialogue management metrics"""
        
        self.dialogue_metrics["total_dialogues_processed"] += 1
        
        if result.patterns:
            self.dialogue_metrics["successful_pattern_detections"] += 1
        
        if result.context_switch.switch_detected and result.context_continuity > 0.8:
            self.dialogue_metrics["smooth_context_transitions"] += 1
        
        if result.proactive_suggestions:
            self.dialogue_metrics["proactive_suggestions_provided"] += 1
        
        # Update running average of dialogue quality
        current_avg = self.dialogue_metrics["average_dialogue_quality"]
        total_processed = self.dialogue_metrics["total_dialogues_processed"]
        
        new_avg = ((current_avg * (total_processed - 1)) + result.dialogue_quality) / total_processed
        self.dialogue_metrics["average_dialogue_quality"] = new_avg
    
    async def _fallback_dialogue_management(
        self,
        user_id: str,
        current_message: str,
        conversation_state: Optional[ConversationState],
        error_message: str
    ) -> DialogueFlowResult:
        """Fallback dialogue management when errors occur"""
        
        print(f"Dialogue management fallback due to error: {error_message}")
        
        # Get basic conversation state
        if not conversation_state:
            conversation_state = await self.conversation_manager.get_conversation_state(user_id)
        
        # Get basic persona
        user_persona = await self.persona_manager.get_or_create_persona(user_id)
        
        # Create minimal context switch result
        context_switch = ContextSwitchResult(
            switch_detected=False,
            switch_type=None,
            confidence=0.0,
            previous_context={},
            new_context={"fallback": True},
            preserved_elements=[],
            switch_trigger="fallback",
            topic_relationship="continuous",
            user_intent_change=False,
            transition_strategy="none",
            context_bridge_needed=False,
            suggested_acknowledgment=""
        )
        
        # Create basic enhanced context
        enhanced_context = {
            "fallback_mode": True,
            "error_occurred": True,
            "user_id": user_id,
            "message": current_message,
            "basic_context": True
        }
        
        return DialogueFlowResult(
            patterns=[],
            context_switch=context_switch,
            proactive_suggestions=[],
            dialogue_recommendations=["Provide helpful response despite technical issues"],
            enhanced_response_context=enhanced_context,
            conversation_state=conversation_state,
            user_persona=user_persona
        )
    
    async def enhance_response_with_dialogue_context(
        self,
        base_response: str,
        dialogue_result: DialogueFlowResult
    ) -> str:
        """Enhance response using dialogue flow context"""
        
        enhanced_response = base_response
        
        # Add context switch acknowledgment if needed
        if (dialogue_result.context_switch.switch_detected and 
            dialogue_result.context_switch.suggested_acknowledgment):
            acknowledgment = dialogue_result.context_switch.suggested_acknowledgment
            enhanced_response = f"{acknowledgment}\n\n{enhanced_response}"
        
        # Add proactive suggestions if available
        if dialogue_result.proactive_suggestions:
            suggestions_text = "\n\n💡 **Suggestions:**\n"
            for i, suggestion in enumerate(dialogue_result.proactive_suggestions[:2], 1):
                suggestions_text += f"{i}. {suggestion.content}\n"
            enhanced_response += suggestions_text
        
        return enhanced_response
    
    async def get_dialogue_flow_metrics(self) -> Dict[str, Any]:
        """Get comprehensive dialogue flow metrics"""
        
        # Get metrics from individual components
        pattern_metrics = await self.pattern_detector.get_pattern_analytics()
        context_switch_metrics = await self.context_switcher.get_context_switch_metrics()
        suggestion_metrics = await self.suggestion_engine.get_suggestion_analytics()
        conversation_metrics = await self.conversation_manager.get_conversation_metrics()
        persona_metrics = await self.persona_manager.get_persona_metrics()
        
        # Calculate Phase 2 success metrics
        total_dialogues = self.dialogue_metrics["total_dialogues_processed"]
        
        if total_dialogues == 0:
            return {"total_dialogues_processed": 0, "phase2_status": "no_activity"}
        
        # Phase 2 success criteria
        proactive_assistance_rate = (
            self.dialogue_metrics["proactive_suggestions_provided"] / total_dialogues
        )
        
        pattern_detection_rate = (
            self.dialogue_metrics["successful_pattern_detections"] / total_dialogues
        )
        
        smooth_transition_rate = (
            self.dialogue_metrics["smooth_context_transitions"] / 
            max(1, context_switch_metrics.get("total_switches_detected", 1))
        )
        
        # Overall Phase 2 performance
        phase2_performance = {
            "proactive_assistance_rate": proactive_assistance_rate,
            "pattern_detection_rate": pattern_detection_rate,
            "smooth_transition_rate": smooth_transition_rate,
            "average_dialogue_quality": self.dialogue_metrics["average_dialogue_quality"]
        }
        
        # Phase 2 targets
        phase2_targets = {
            "proactive_assistance_target": 0.4,     # 40% of interactions
            "pattern_detection_target": 0.6,       # 60% pattern detection
            "smooth_transition_target": 0.9,       # 90% smooth transitions
            "dialogue_quality_target": 0.75        # 75% average quality
        }
        
        # Success evaluation
        targets_met = {
            "proactive_assistance": proactive_assistance_rate >= phase2_targets["proactive_assistance_target"],
            "pattern_detection": pattern_detection_rate >= phase2_targets["pattern_detection_target"],
            "smooth_transitions": smooth_transition_rate >= phase2_targets["smooth_transition_target"],
            "dialogue_quality": self.dialogue_metrics["average_dialogue_quality"] >= phase2_targets["dialogue_quality_target"]
        }
        
        overall_success = sum(targets_met.values()) >= 3  # At least 3 of 4 targets
        
        return {
            # Overall metrics
            "total_dialogues_processed": total_dialogues,
            "phase2_overall_success": overall_success,
            "targets_met_count": sum(targets_met.values()),
            "overall_performance_score": sum(phase2_performance.values()) / len(phase2_performance),
            
            # Phase 2 specific metrics
            "phase2_performance": phase2_performance,
            "phase2_targets": phase2_targets,
            "phase2_targets_met": targets_met,
            
            # Component metrics
            "pattern_recognition": pattern_metrics,
            "context_switching": context_switch_metrics,
            "proactive_suggestions": suggestion_metrics,
            "conversation_management": conversation_metrics,
            "persona_modeling": persona_metrics,
            
            # Individual component metrics
            "dialogue_management_metrics": self.dialogue_metrics
        }

# Global instance for shared access
intelligent_dialogue_manager = IntelligentDialogueManager()