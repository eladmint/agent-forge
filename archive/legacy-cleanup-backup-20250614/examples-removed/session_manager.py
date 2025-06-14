"""
Session Management for Multi-Agent Regional Architecture

This module provides session lifecycle management, cleanup coordination, and 
session pool optimization for the distributed agent system.
"""

import asyncio
import logging
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set

import aiohttp
from playwright.async_api import BrowserContext, Page

from .base_agent import RegionalSession

logger = logging.getLogger(__name__)


class SessionPool:
    """Manages a pool of regional sessions for optimal resource utilization"""
    
    def __init__(self, region: str, max_size: int = 5):
        self.region = region
        self.max_size = max_size
        self.sessions: List[RegionalSession] = []
        self.active_sessions: Set[str] = set()
        self.creation_lock = asyncio.Lock()
        
    async def get_session(self) -> Optional[RegionalSession]:
        """Get an available session from the pool"""
        # Find unused healthy session
        for session in self.sessions:
            if (session.session_id not in self.active_sessions and 
                session.is_active and
                await self._is_session_healthy(session)):
                self.active_sessions.add(session.session_id)
                session.last_used = datetime.now()
                return session
        
        # Create new session if pool not full
        if len(self.sessions) < self.max_size:
            async with self.creation_lock:
                if len(self.sessions) < self.max_size:  # Double-check after acquiring lock
                    session = await self._create_new_session()
                    if session:
                        self.sessions.append(session)
                        self.active_sessions.add(session.session_id)
                        return session
        
        return None
    
    def release_session(self, session_id: str):
        """Release a session back to the pool"""
        self.active_sessions.discard(session_id)
    
    async def cleanup_expired_sessions(self):
        """Remove expired or unhealthy sessions from the pool"""
        current_time = datetime.now()
        healthy_sessions = []
        
        for session in self.sessions:
            if (session.is_active and 
                await self._is_session_healthy(session) and
                (current_time - session.last_used) < timedelta(minutes=30)):
                healthy_sessions.append(session)
            else:
                await self._close_session(session)
                self.active_sessions.discard(session.session_id)
        
        self.sessions = healthy_sessions
    
    async def _create_new_session(self) -> Optional[RegionalSession]:
        """Create a new session for this region"""
        # This will be implemented with actual browser/HTTP session creation
        # For now, return a mock session
        session_id = str(uuid.uuid4())
        return RegionalSession(
            region=self.region,
            session_id=session_id,
            browser_context=None,  # Will be created by RegionManager
            http_session=None,     # Will be created by RegionManager
            created_at=datetime.now(),
            last_used=datetime.now(),
            request_count=0,
            rate_limit_remaining=100,
            is_active=True
        )
    
    async def _is_session_healthy(self, session: RegionalSession) -> bool:
        """Check if a session is healthy and usable"""
        if not session.is_active:
            return False
        
        # Check if session is too old
        if (datetime.now() - session.created_at) > timedelta(hours=2):
            return False
        
        # Check request count limits
        if session.request_count > 1000:
            return False
        
        # Check rate limit status
        if session.rate_limit_remaining <= 0:
            return False
        
        return True
    
    async def _close_session(self, session: RegionalSession):
        """Close and cleanup a session"""
        try:
            if session.browser_context:
                await session.browser_context.close()
            if session.http_session:
                await session.http_session.close()
            session.is_active = False
        except Exception as e:
            logger.warning(f"Error closing session {session.session_id}: {e}")


class SessionManager:
    """
    Comprehensive session management across all regions and agents
    
    Provides:
    - Session pool management per region
    - Lifecycle coordination across agents
    - Resource cleanup and optimization
    - Session health monitoring and recovery
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        
        # Session pools by region
        self.session_pools: Dict[str, SessionPool] = {}
        
        # Global session tracking
        self.active_session_count = defaultdict(int)
        self.total_sessions_created = 0
        self.total_sessions_destroyed = 0
        
        # Cleanup scheduling
        self.cleanup_task: Optional[asyncio.Task] = None
        self.cleanup_interval = self.config.get("cleanup_interval", 300)  # 5 minutes
        
        # Performance metrics
        self.session_metrics = {
            "total_created": 0,
            "total_destroyed": 0,
            "average_lifetime": 0,
            "peak_concurrent": 0,
            "current_active": 0
        }
        
        logger.info("SessionManager initialized")
    
    async def initialize(self, regions: List[str]):
        """Initialize session pools for all regions"""
        logger.info(f"Initializing session pools for regions: {regions}")
        
        for region in regions:
            pool_size = self.config.get("pool_size_per_region", 3)
            self.session_pools[region] = SessionPool(region, pool_size)
            logger.info(f"Session pool created for {region} with max size {pool_size}")
        
        # Start cleanup task
        self.cleanup_task = asyncio.create_task(self._periodic_cleanup())
        logger.info("Session cleanup task started")
    
    async def cleanup(self):
        """Cleanup all session resources"""
        logger.info("Starting SessionManager cleanup")
        
        # Cancel cleanup task
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Cleanup all session pools
        for region, pool in self.session_pools.items():
            logger.info(f"Cleaning up session pool for {region}")
            await pool.cleanup_expired_sessions()
        
        logger.info("SessionManager cleanup completed")
    
    async def get_session(self, region: str) -> Optional[RegionalSession]:
        """
        Get a session for the specified region
        
        Args:
            region: Target region for the session
            
        Returns:
            RegionalSession or None if unavailable
        """
        if region not in self.session_pools:
            logger.error(f"No session pool for region {region}")
            return None
        
        session = await self.session_pools[region].get_session()
        
        if session:
            self.active_session_count[region] += 1
            self.session_metrics["current_active"] = sum(self.active_session_count.values())
            
            # Update peak concurrent
            if self.session_metrics["current_active"] > self.session_metrics["peak_concurrent"]:
                self.session_metrics["peak_concurrent"] = self.session_metrics["current_active"]
            
            logger.debug(f"Session {session.session_id} acquired for region {region}")
        else:
            logger.warning(f"No available session for region {region}")
        
        return session
    
    def release_session(self, session: RegionalSession):
        """
        Release a session back to its pool
        
        Args:
            session: The session to release
        """
        if session.region in self.session_pools:
            self.session_pools[session.region].release_session(session.session_id)
            self.active_session_count[session.region] -= 1
            self.session_metrics["current_active"] = sum(self.active_session_count.values())
            logger.debug(f"Session {session.session_id} released for region {session.region}")
    
    async def force_cleanup_region(self, region: str):
        """Force cleanup of all sessions in a specific region"""
        if region in self.session_pools:
            logger.info(f"Force cleaning up sessions for region {region}")
            await self.session_pools[region].cleanup_expired_sessions()
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """Get comprehensive session statistics"""
        region_stats = {}
        for region, pool in self.session_pools.items():
            region_stats[region] = {
                "total_sessions": len(pool.sessions),
                "active_sessions": len(pool.active_sessions),
                "available_sessions": len(pool.sessions) - len(pool.active_sessions),
                "max_pool_size": pool.max_size
            }
        
        return {
            "global_metrics": self.session_metrics,
            "regional_distribution": region_stats,
            "active_count_by_region": dict(self.active_session_count),
            "total_regions": len(self.session_pools)
        }
    
    async def _periodic_cleanup(self):
        """Periodic cleanup task for expired sessions"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                logger.debug("Starting periodic session cleanup")
                
                for region, pool in self.session_pools.items():
                    await pool.cleanup_expired_sessions()
                
                logger.debug("Periodic session cleanup completed")
                
            except asyncio.CancelledError:
                logger.info("Periodic cleanup task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in periodic cleanup: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default session management configuration"""
        return {
            "pool_size_per_region": 3,
            "cleanup_interval": 300,  # 5 minutes
            "session_timeout": 1800,  # 30 minutes
            "max_requests_per_session": 1000,
            "health_check_interval": 60  # 1 minute
        } 