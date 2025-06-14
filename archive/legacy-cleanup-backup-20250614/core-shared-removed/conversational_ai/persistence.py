# Conversational AI Persistence Layer
# Cross-service conversation state and persona persistence

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import asyncio
from abc import ABC, abstractmethod

from .state_management import ConversationState, ConversationStateType, IntentConfidence
from .persona_modeling import UserPersona, UserPersonaType, ExperienceLevel, EngagementStyle

class ConversationPersistenceInterface(ABC):
    """Interface for conversation state persistence"""
    
    @abstractmethod
    async def save_state(self, user_id: str, state: ConversationState) -> bool:
        """Save conversation state"""
        pass
    
    @abstractmethod
    async def load_state(self, user_id: str) -> Optional[ConversationState]:
        """Load conversation state"""
        pass
    
    @abstractmethod
    async def delete_state(self, user_id: str) -> bool:
        """Delete conversation state"""
        pass
    
    @abstractmethod
    async def cleanup_expired_states(self, max_age_hours: int = 24) -> int:
        """Clean up expired conversation states"""
        pass

class PersonaPersistenceInterface(ABC):
    """Interface for persona persistence"""
    
    @abstractmethod
    async def save_persona(self, user_id: str, persona: UserPersona) -> bool:
        """Save user persona"""
        pass
    
    @abstractmethod
    async def load_persona(self, user_id: str) -> Optional[UserPersona]:
        """Load user persona"""
        pass
    
    @abstractmethod
    async def delete_persona(self, user_id: str) -> bool:
        """Delete user persona"""
        pass

class DatabaseConversationPersistence(ConversationPersistenceInterface):
    """Database-based conversation state persistence"""
    
    def __init__(self, db_client):
        self.db = db_client
        self.table_name = "conversation_states"
        self._ensure_table_exists()
    
    def _ensure_table_exists(self):
        """Ensure the conversation states table exists"""
        # This would create the table if it doesn't exist
        # Implementation depends on the specific database client
        pass
    
    async def save_state(self, user_id: str, state: ConversationState) -> bool:
        """Save conversation state to database"""
        try:
            state_data = {
                "user_id": user_id,
                "state_data": json.dumps(state.to_dict()),
                "session_id": state.session_id,
                "current_state": state.current_state.value,
                "turn_count": state.turn_count,
                "created_at": state.created_at.isoformat(),
                "last_activity": state.last_activity.isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Upsert operation (insert or update)
            result = await self.db.table(self.table_name).upsert(
                state_data,
                on_conflict="user_id"
            ).execute()
            
            return result.data is not None
            
        except Exception as e:
            print(f"Error saving conversation state for {user_id}: {e}")
            return False
    
    async def load_state(self, user_id: str) -> Optional[ConversationState]:
        """Load conversation state from database"""
        try:
            result = await self.db.table(self.table_name).select("*").eq(
                "user_id", user_id
            ).execute()
            
            if result.data:
                state_data = json.loads(result.data[0]["state_data"])
                return ConversationState.from_dict(state_data)
            
            return None
            
        except Exception as e:
            print(f"Error loading conversation state for {user_id}: {e}")
            return None
    
    async def delete_state(self, user_id: str) -> bool:
        """Delete conversation state from database"""
        try:
            result = await self.db.table(self.table_name).delete().eq(
                "user_id", user_id
            ).execute()
            
            return True
            
        except Exception as e:
            print(f"Error deleting conversation state for {user_id}: {e}")
            return False
    
    async def cleanup_expired_states(self, max_age_hours: int = 24) -> int:
        """Clean up expired conversation states"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            cutoff_iso = cutoff_time.isoformat()
            
            result = await self.db.table(self.table_name).delete().lt(
                "last_activity", cutoff_iso
            ).execute()
            
            return len(result.data) if result.data else 0
            
        except Exception as e:
            print(f"Error cleaning up expired conversation states: {e}")
            return 0

class DatabasePersonaPersistence(PersonaPersistenceInterface):
    """Database-based persona persistence"""
    
    def __init__(self, db_client):
        self.db = db_client
        self.table_name = "user_personas"
        self._ensure_table_exists()
    
    def _ensure_table_exists(self):
        """Ensure the user personas table exists"""
        # This would create the table if it doesn't exist
        pass
    
    async def save_persona(self, user_id: str, persona: UserPersona) -> bool:
        """Save user persona to database"""
        try:
            persona_data = {
                "user_id": user_id,
                "persona_data": json.dumps(persona.to_dict()),
                "primary_persona": persona.primary_persona.value,
                "persona_confidence": persona.persona_confidence,
                "experience_level": persona.experience_level.value,
                "engagement_style": persona.engagement_style.value,
                "interests": json.dumps(persona.interests),
                "expertise_areas": json.dumps(persona.expertise_areas),
                "created_at": persona.created_at.isoformat(),
                "last_updated": persona.last_updated.isoformat(),
                "update_count": persona.update_count,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Upsert operation
            result = await self.db.table(self.table_name).upsert(
                persona_data,
                on_conflict="user_id"
            ).execute()
            
            return result.data is not None
            
        except Exception as e:
            print(f"Error saving persona for {user_id}: {e}")
            return False
    
    async def load_persona(self, user_id: str) -> Optional[UserPersona]:
        """Load user persona from database"""
        try:
            result = await self.db.table(self.table_name).select("*").eq(
                "user_id", user_id
            ).execute()
            
            if result.data:
                persona_dict = json.loads(result.data[0]["persona_data"])
                return self._dict_to_persona(persona_dict)
            
            return None
            
        except Exception as e:
            print(f"Error loading persona for {user_id}: {e}")
            return None
    
    async def delete_persona(self, user_id: str) -> bool:
        """Delete user persona from database"""
        try:
            result = await self.db.table(self.table_name).delete().eq(
                "user_id", user_id
            ).execute()
            
            return True
            
        except Exception as e:
            print(f"Error deleting persona for {user_id}: {e}")
            return False
    
    def _dict_to_persona(self, persona_dict: Dict[str, Any]) -> UserPersona:
        """Convert dictionary back to UserPersona object"""
        from .persona_modeling import PersonaSignal
        
        # Reconstruct signals
        signals = []
        for signal_dict in persona_dict.get("signals", []):
            signals.append(PersonaSignal(
                signal_type=signal_dict["signal_type"],
                value=signal_dict["value"],
                confidence=signal_dict["confidence"],
                timestamp=datetime.fromisoformat(signal_dict["timestamp"]),
                source=signal_dict["source"],
                weight=signal_dict.get("weight", 1.0)
            ))
        
        persona = UserPersona(
            user_id=persona_dict["user_id"],
            primary_persona=UserPersonaType(persona_dict["primary_persona"]),
            persona_confidence=persona_dict["persona_confidence"],
            experience_level=ExperienceLevel(persona_dict["experience_level"]),
            engagement_style=EngagementStyle(persona_dict["engagement_style"]),
            interests=persona_dict.get("interests", []),
            expertise_areas=persona_dict.get("expertise_areas", []),
            preferred_content_types=persona_dict.get("preferred_content_types", []),
            activity_patterns=persona_dict.get("activity_patterns", {}),
            signals=signals,
            created_at=datetime.fromisoformat(persona_dict["created_at"]),
            last_updated=datetime.fromisoformat(persona_dict["last_updated"]),
            update_count=persona_dict.get("update_count", 0),
            prediction_accuracy=persona_dict.get("prediction_accuracy", 0.0),
            adaptation_rate=persona_dict.get("adaptation_rate", 0.1)
        )
        
        return persona

class RedisConversationPersistence(ConversationPersistenceInterface):
    """Redis-based conversation state persistence for fast access"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.key_prefix = "conv_state:"
        self.expiration_seconds = 86400  # 24 hours
    
    async def save_state(self, user_id: str, state: ConversationState) -> bool:
        """Save conversation state to Redis"""
        try:
            key = f"{self.key_prefix}{user_id}"
            state_json = json.dumps(state.to_dict())
            
            await self.redis.setex(key, self.expiration_seconds, state_json)
            return True
            
        except Exception as e:
            print(f"Error saving conversation state to Redis for {user_id}: {e}")
            return False
    
    async def load_state(self, user_id: str) -> Optional[ConversationState]:
        """Load conversation state from Redis"""
        try:
            key = f"{self.key_prefix}{user_id}"
            state_json = await self.redis.get(key)
            
            if state_json:
                state_data = json.loads(state_json)
                return ConversationState.from_dict(state_data)
            
            return None
            
        except Exception as e:
            print(f"Error loading conversation state from Redis for {user_id}: {e}")
            return None
    
    async def delete_state(self, user_id: str) -> bool:
        """Delete conversation state from Redis"""
        try:
            key = f"{self.key_prefix}{user_id}"
            await self.redis.delete(key)
            return True
            
        except Exception as e:
            print(f"Error deleting conversation state from Redis for {user_id}: {e}")
            return False
    
    async def cleanup_expired_states(self, max_age_hours: int = 24) -> int:
        """Redis handles expiration automatically"""
        # Redis automatically expires keys, so no manual cleanup needed
        return 0

class HybridPersistence:
    """Hybrid persistence using both Redis (fast) and Database (durable)"""
    
    def __init__(self, redis_persistence: RedisConversationPersistence, 
                 db_persistence: DatabaseConversationPersistence):
        self.redis = redis_persistence
        self.db = db_persistence
        self.sync_interval = 300  # Sync to DB every 5 minutes
        self.last_sync = {}
    
    async def save_state(self, user_id: str, state: ConversationState) -> bool:
        """Save to Redis immediately, DB periodically"""
        # Always save to Redis for fast access
        redis_success = await self.redis.save_state(user_id, state)
        
        # Save to DB if enough time has passed or it's a new user
        should_sync_db = (
            user_id not in self.last_sync or
            (datetime.utcnow() - self.last_sync[user_id]).total_seconds() > self.sync_interval
        )
        
        db_success = True
        if should_sync_db:
            db_success = await self.db.save_state(user_id, state)
            if db_success:
                self.last_sync[user_id] = datetime.utcnow()
        
        return redis_success and db_success
    
    async def load_state(self, user_id: str) -> Optional[ConversationState]:
        """Try Redis first, fallback to DB"""
        # Try Redis first (fast)
        state = await self.redis.load_state(user_id)
        
        if state is None:
            # Fallback to database
            state = await self.db.load_state(user_id)
            
            # If found in DB, cache in Redis
            if state:
                await self.redis.save_state(user_id, state)
        
        return state
    
    async def delete_state(self, user_id: str) -> bool:
        """Delete from both Redis and DB"""
        redis_success = await self.redis.delete_state(user_id)
        db_success = await self.db.delete_state(user_id)
        
        # Remove from sync tracking
        self.last_sync.pop(user_id, None)
        
        return redis_success and db_success

class ConversationPersistenceManager:
    """Manages conversation persistence across the application"""
    
    def __init__(self):
        self.conversation_persistence: Optional[ConversationPersistenceInterface] = None
        self.persona_persistence: Optional[PersonaPersistenceInterface] = None
        self.cleanup_interval = 3600  # 1 hour
        self.last_cleanup = datetime.utcnow()
    
    def set_conversation_persistence(self, persistence: ConversationPersistenceInterface):
        """Set the conversation persistence implementation"""
        self.conversation_persistence = persistence
    
    def set_persona_persistence(self, persistence: PersonaPersistenceInterface):
        """Set the persona persistence implementation"""
        self.persona_persistence = persistence
    
    async def save_conversation_state(self, user_id: str, state: ConversationState) -> bool:
        """Save conversation state using configured persistence"""
        if self.conversation_persistence:
            return await self.conversation_persistence.save_state(user_id, state)
        return False
    
    async def load_conversation_state(self, user_id: str) -> Optional[ConversationState]:
        """Load conversation state using configured persistence"""
        if self.conversation_persistence:
            return await self.conversation_persistence.load_state(user_id)
        return None
    
    async def save_user_persona(self, user_id: str, persona: UserPersona) -> bool:
        """Save user persona using configured persistence"""
        if self.persona_persistence:
            return await self.persona_persistence.save_persona(user_id, persona)
        return False
    
    async def load_user_persona(self, user_id: str) -> Optional[UserPersona]:
        """Load user persona using configured persistence"""
        if self.persona_persistence:
            return await self.persona_persistence.load_persona(user_id)
        return None
    
    async def periodic_cleanup(self):
        """Perform periodic cleanup of expired data"""
        current_time = datetime.utcnow()
        if (current_time - self.last_cleanup).total_seconds() >= self.cleanup_interval:
            
            if self.conversation_persistence:
                cleaned = await self.conversation_persistence.cleanup_expired_states()
                print(f"Cleaned up {cleaned} expired conversation states")
            
            self.last_cleanup = current_time
    
    async def get_persistence_metrics(self) -> Dict[str, Any]:
        """Get persistence system metrics"""
        return {
            "conversation_persistence_configured": self.conversation_persistence is not None,
            "persona_persistence_configured": self.persona_persistence is not None,
            "last_cleanup": self.last_cleanup.isoformat(),
            "cleanup_interval_hours": self.cleanup_interval / 3600
        }

# Database schema creation functions
async def create_conversation_tables(db_client):
    """Create conversation-related database tables"""
    
    # Conversation states table
    conversation_states_schema = """
    CREATE TABLE IF NOT EXISTS conversation_states (
        id SERIAL PRIMARY KEY,
        user_id TEXT UNIQUE NOT NULL,
        state_data JSONB NOT NULL,
        session_id TEXT NOT NULL,
        current_state TEXT NOT NULL,
        turn_count INTEGER DEFAULT 0,
        created_at TIMESTAMPTZ NOT NULL,
        last_activity TIMESTAMPTZ NOT NULL,
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );
    
    CREATE INDEX IF NOT EXISTS idx_conversation_states_user_id ON conversation_states(user_id);
    CREATE INDEX IF NOT EXISTS idx_conversation_states_last_activity ON conversation_states(last_activity);
    CREATE INDEX IF NOT EXISTS idx_conversation_states_session_id ON conversation_states(session_id);
    """
    
    # User personas table
    user_personas_schema = """
    CREATE TABLE IF NOT EXISTS user_personas (
        id SERIAL PRIMARY KEY,
        user_id TEXT UNIQUE NOT NULL,
        persona_data JSONB NOT NULL,
        primary_persona TEXT NOT NULL,
        persona_confidence FLOAT DEFAULT 0.0,
        experience_level TEXT NOT NULL,
        engagement_style TEXT NOT NULL,
        interests JSONB DEFAULT '[]',
        expertise_areas JSONB DEFAULT '[]',
        created_at TIMESTAMPTZ NOT NULL,
        last_updated TIMESTAMPTZ NOT NULL,
        update_count INTEGER DEFAULT 0,
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );
    
    CREATE INDEX IF NOT EXISTS idx_user_personas_user_id ON user_personas(user_id);
    CREATE INDEX IF NOT EXISTS idx_user_personas_primary_persona ON user_personas(primary_persona);
    CREATE INDEX IF NOT EXISTS idx_user_personas_experience_level ON user_personas(experience_level);
    """
    
    try:
        # Execute schema creation
        await db_client.rpc('exec_sql', {'sql': conversation_states_schema})
        await db_client.rpc('exec_sql', {'sql': user_personas_schema})
        print("Conversation AI database tables created successfully")
        return True
    except Exception as e:
        print(f"Error creating conversation AI tables: {e}")
        return False

# Global persistence manager instance
persistence_manager = ConversationPersistenceManager()