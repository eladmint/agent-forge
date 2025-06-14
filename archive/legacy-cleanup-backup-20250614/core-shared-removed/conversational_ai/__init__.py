# Conversational AI Package
# Phase 1: Enhanced State Management Implementation
# Phase 2: Intelligent Dialogue Flows Implementation

# Phase 1 Components
from .state_management import (
    ConversationState,
    ConversationStateType,
    ConversationSlot,
    IntentHistory,
    IntentConfidence,
    ConversationStateManager,
    conversation_state_manager
)

from .slot_management import (
    SlotType,
    SlotExtractionMethod,
    SlotDefinition,
    SlotExtractor,
    SlotManager,
    slot_manager
)

from .persona_modeling import (
    UserPersonaType,
    ExperienceLevel,
    EngagementStyle,
    PersonaSignal,
    UserPersona,
    PersonaDetector,
    PersonaManager,
    persona_manager
)

from .persistence import (
    ConversationPersistenceInterface,
    PersonaPersistenceInterface,
    DatabaseConversationPersistence,
    DatabasePersonaPersistence,
    RedisConversationPersistence,
    HybridPersistence,
    ConversationPersistenceManager,
    persistence_manager,
    create_conversation_tables
)

# Phase 2 Components
from .pattern_recognition import (
    ConversationPatternDetector,
    PatternMatch,
    ConversationPattern,
    PatternConfidence,
    PatternPrediction,
    pattern_detector
)

from .context_switching import (
    ContextSwitchManager,
    ContextSwitchResult,
    TransitionPlan,
    ContextSwitchType,
    SwitchConfidence,
    context_switch_manager
)

from .proactive_suggestions import (
    ProactiveSuggestionEngine,
    ProactiveSuggestion,
    SuggestionType,
    SuggestionPriority,
    SuggestionContext,
    proactive_suggestion_engine
)

from .dialogue_management import (
    IntelligentDialogueManager,
    DialogueFlowResult,
    intelligent_dialogue_manager
)

__version__ = "2.0.0"
__phase__ = "Phase 2: Intelligent Dialogue Flows"

# Global initialization function
async def initialize_conversational_ai(
    db_client=None,
    redis_client=None,
    config: dict = None
):
    """Initialize the conversational AI system"""
    
    config = config or {}
    
    # Set up persistence layers
    if db_client:
        # Create database tables
        await create_conversation_tables(db_client)
        
        # Set up database persistence
        db_conv_persistence = DatabaseConversationPersistence(db_client)
        db_persona_persistence = DatabasePersonaPersistence(db_client)
        
        if redis_client:
            # Set up hybrid persistence (Redis + Database)
            redis_conv_persistence = RedisConversationPersistence(redis_client)
            hybrid_persistence = HybridPersistence(redis_conv_persistence, db_conv_persistence)
            persistence_manager.set_conversation_persistence(hybrid_persistence)
        else:
            # Database-only persistence
            persistence_manager.set_conversation_persistence(db_conv_persistence)
        
        persistence_manager.set_persona_persistence(db_persona_persistence)
    
    # Configure conversation state manager
    conversation_state_manager.state_persistence = persistence_manager
    
    # Configure persona manager
    persona_manager.persona_persistence = persistence_manager
    
    print("🚀 Conversational AI Phase 1 + Phase 2 initialized successfully!")
    
    return {
        "phase": __phase__,
        "version": __version__,
        "components": [
            "ConversationStateManager",
            "SlotManager", 
            "PersonaManager",
            "PersistenceManager",
            "PatternDetector",
            "ContextSwitchManager",
            "ProactiveSuggestionEngine",
            "IntelligentDialogueManager"
        ],
        "features": [
            "Rasa-inspired state tracking",
            "Intelligent slot management",
            "User persona modeling",
            "Cross-service persistence",
            "Pattern recognition",
            "Context switching management",
            "Proactive suggestions",
            "Intelligent dialogue flows"
        ]
    }

# Export all main components
__all__ = [
    # Phase 1 - State Management
    'ConversationState',
    'ConversationStateType', 
    'ConversationSlot',
    'IntentHistory',
    'IntentConfidence',
    'ConversationStateManager',
    'conversation_state_manager',
    
    # Phase 1 - Slot Management
    'SlotType',
    'SlotExtractionMethod',
    'SlotDefinition',
    'SlotExtractor',
    'SlotManager',
    'slot_manager',
    
    # Phase 1 - Persona Modeling
    'UserPersonaType',
    'ExperienceLevel',
    'EngagementStyle',
    'PersonaSignal',
    'UserPersona',
    'PersonaDetector',
    'PersonaManager',
    'persona_manager',
    
    # Phase 1 - Persistence
    'ConversationPersistenceInterface',
    'PersonaPersistenceInterface',
    'DatabaseConversationPersistence',
    'DatabasePersonaPersistence',
    'RedisConversationPersistence',
    'HybridPersistence',
    'ConversationPersistenceManager',
    'persistence_manager',
    'create_conversation_tables',
    
    # Phase 2 - Pattern Recognition
    'ConversationPatternDetector',
    'PatternMatch',
    'ConversationPattern',
    'PatternConfidence',
    'PatternPrediction',
    'pattern_detector',
    
    # Phase 2 - Context Switching
    'ContextSwitchManager',
    'ContextSwitchResult',
    'TransitionPlan',
    'ContextSwitchType',
    'SwitchConfidence',
    'context_switch_manager',
    
    # Phase 2 - Proactive Suggestions
    'ProactiveSuggestionEngine',
    'ProactiveSuggestion',
    'SuggestionType',
    'SuggestionPriority',
    'SuggestionContext',
    'proactive_suggestion_engine',
    
    # Phase 2 - Dialogue Management
    'IntelligentDialogueManager',
    'DialogueFlowResult',
    'intelligent_dialogue_manager',
    
    # Initialization
    'initialize_conversational_ai'
]