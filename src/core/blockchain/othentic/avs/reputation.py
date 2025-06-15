"""
Reputation Validation AVS for Othentic integration.

Provides decentralized reputation scoring and validation services
with stake-based voting and performance tracking.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from dataclasses import dataclass, asdict
from enum import Enum
from decimal import Decimal

if TYPE_CHECKING:
    from ..client import OthenticAVSClient

logger = logging.getLogger(__name__)


class ReputationAction(Enum):
    """Reputation action enumeration."""
    TASK_COMPLETION = "task_completion"
    FRAUD_REPORT = "fraud_report"
    STAKE_SLASH = "stake_slash"
    VALIDATION_SUCCESS = "validation_success"
    VALIDATION_FAILURE = "validation_failure"
    PEER_REVIEW = "peer_review"
    DISPUTE_RESOLUTION = "dispute_resolution"


class ValidationVote(Enum):
    """Validation vote enumeration."""
    APPROVE = "approve"
    REJECT = "reject"
    ABSTAIN = "abstain"


class ReputationTier(Enum):
    """Reputation tier enumeration."""
    UNKNOWN = "unknown"
    NOVICE = "novice"
    APPRENTICE = "apprentice"
    SKILLED = "skilled"
    EXPERT = "expert"
    MASTER = "master"


@dataclass
class ReputationScore:
    """Agent reputation score information."""
    
    agent_id: str
    overall_score: Decimal
    tier: ReputationTier
    task_completion_rate: Decimal
    fraud_reports: int
    stake_amount: Decimal
    validation_accuracy: Decimal
    peer_review_score: Decimal
    last_updated: datetime
    score_history: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['overall_score'] = str(self.overall_score)
        data['task_completion_rate'] = str(self.task_completion_rate)
        data['stake_amount'] = str(self.stake_amount)
        data['validation_accuracy'] = str(self.validation_accuracy)
        data['peer_review_score'] = str(self.peer_review_score)
        data['tier'] = self.tier.value
        data['last_updated'] = self.last_updated.isoformat()
        return data


@dataclass
class ReputationEvent:
    """Reputation-affecting event."""
    
    event_id: str
    agent_id: str
    action: ReputationAction
    score_change: Decimal
    details: Dict[str, Any]
    validator_id: Optional[str]
    stake_weight: Decimal
    timestamp: datetime
    verified: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['action'] = self.action.value
        data['score_change'] = str(self.score_change)
        data['stake_weight'] = str(self.stake_weight)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class ValidationRequest:
    """Reputation validation request."""
    
    request_id: str
    agent_id: str
    action: ReputationAction
    evidence: Dict[str, Any]
    stake_requirement: Decimal
    voting_period: int  # seconds
    created_at: datetime
    expires_at: datetime
    votes: List[Dict[str, Any]]
    status: str = "pending"
    
    def __post_init__(self):
        if not hasattr(self, 'expires_at') or self.expires_at is None:
            self.expires_at = self.created_at + timedelta(seconds=self.voting_period)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['action'] = self.action.value
        data['stake_requirement'] = str(self.stake_requirement)
        data['created_at'] = self.created_at.isoformat()
        data['expires_at'] = self.expires_at.isoformat()
        return data


@dataclass
class ValidationVoteRecord:
    """Validation vote record."""
    
    vote_id: str
    request_id: str
    voter_id: str
    vote: ValidationVote
    stake_weight: Decimal
    justification: Optional[str]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['vote'] = self.vote.value
        data['stake_weight'] = str(self.stake_weight)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class ReputationValidationAVS:
    """
    Reputation Validation AVS service.
    
    Provides decentralized reputation scoring and validation services
    with stake-based voting and performance tracking.
    """
    
    def __init__(self, client: 'OthenticAVSClient'):
        """
        Initialize Reputation Validation AVS.
        
        Args:
            client: Parent Othentic AVS client
        """
        self.client = client
        self._initialized = False
        
    async def initialize(self):
        """Initialize the Reputation Validation AVS."""
        try:
            # Verify reputation contract connectivity
            await self._verify_contract_connection()
            self._initialized = True
            logger.info("Reputation Validation AVS initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Reputation Validation AVS: {e}")
            raise
            
    async def _verify_contract_connection(self):
        """Verify connection to the reputation validation contract."""
        if not self.client.session:
            raise RuntimeError("Client session not available")
            
        try:
            async with self.client.session.get(
                f"{self.client.config.base_url}/v1/reputation/health"
            ) as response:
                response.raise_for_status()
                result = await response.json()
                
                if not result.get("healthy", False):
                    raise RuntimeError("Reputation Validation AVS is not healthy")
                    
        except Exception as e:
            logger.error(f"Reputation validation health check failed: {e}")
            raise
            
    async def get_reputation_score(self, agent_id: str) -> Optional[ReputationScore]:
        """
        Get current reputation score for an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Reputation score or None if not found
        """
        if not self._initialized:
            raise RuntimeError("Reputation Validation AVS not initialized")
            
        if not self.client.session:
            raise RuntimeError("Client session not available")
            
        try:
            async with self.client.session.get(
                f"{self.client.config.base_url}/v1/reputation/agents/{agent_id}/score"
            ) as response:
                if response.status == 404:
                    return None
                    
                response.raise_for_status()
                data = await response.json()
                
                return ReputationScore(
                    agent_id=data['agent_id'],
                    overall_score=Decimal(data['overall_score']),
                    tier=ReputationTier(data['tier']),
                    task_completion_rate=Decimal(data['task_completion_rate']),
                    fraud_reports=data['fraud_reports'],
                    stake_amount=Decimal(data['stake_amount']),
                    validation_accuracy=Decimal(data['validation_accuracy']),
                    peer_review_score=Decimal(data['peer_review_score']),
                    last_updated=datetime.fromisoformat(data['last_updated']),
                    score_history=data.get('score_history', []),
                    metadata=data.get('metadata')
                )
                
        except Exception as e:
            logger.error(f"Failed to get reputation score for {agent_id}: {e}")
            raise
            
    async def submit_reputation_event(self, event: ReputationEvent) -> Dict[str, Any]:
        """
        Submit a reputation-affecting event for validation.
        
        Args:
            event: Reputation event to submit
            
        Returns:
            Submission result
        """
        if not self._initialized:
            raise RuntimeError("Reputation Validation AVS not initialized")
            
        if not self.client.session:
            raise RuntimeError("Client session not available")
            
        payload = event.to_dict()
        payload['submitter_id'] = self.client.config.agent_id
        
        try:
            async with self.client.session.post(
                f"{self.client.config.base_url}/v1/reputation/events",
                json=payload
            ) as response:
                response.raise_for_status()
                result = await response.json()
                
                logger.info(f"Reputation event submitted: {event.event_id}")
                return result
                
        except Exception as e:
            logger.error(f"Failed to submit reputation event {event.event_id}: {e}")
            raise
            
    async def create_validation_request(self, 
                                      agent_id: str,
                                      action: ReputationAction,
                                      evidence: Dict[str, Any],
                                      stake_requirement: Decimal,
                                      voting_period: int = 3600) -> ValidationRequest:
        """
        Create a validation request for reputation change.
        
        Args:
            agent_id: Agent to validate
            action: Reputation action being validated
            evidence: Supporting evidence
            stake_requirement: Minimum stake to vote
            voting_period: Voting period in seconds
            
        Returns:
            Validation request
        """
        if not self._initialized:
            raise RuntimeError("Reputation Validation AVS not initialized")
            
        if not self.client.session:
            raise RuntimeError("Client session not available")
            
        created_at = datetime.utcnow()
        expires_at = created_at + timedelta(seconds=voting_period)
        
        payload = {
            "agent_id": agent_id,
            "action": action.value,
            "evidence": evidence,
            "stake_requirement": str(stake_requirement),
            "voting_period": voting_period,
            "created_at": created_at.isoformat(),
            "expires_at": expires_at.isoformat(),
            "requester_id": self.client.config.agent_id
        }
        
        try:
            async with self.client.session.post(
                f"{self.client.config.base_url}/v1/reputation/validation/requests",
                json=payload
            ) as response:
                response.raise_for_status()
                data = await response.json()
                
                request = ValidationRequest(
                    request_id=data['request_id'],
                    agent_id=agent_id,
                    action=action,
                    evidence=evidence,
                    stake_requirement=stake_requirement,
                    voting_period=voting_period,
                    created_at=created_at,
                    expires_at=expires_at,
                    votes=[],
                    status=data.get('status', 'pending')
                )
                
                logger.info(f"Validation request created: {request.request_id}")
                return request
                
        except Exception as e:
            logger.error(f"Failed to create validation request: {e}")
            raise
            
    async def vote_on_validation(self, 
                               request_id: str,
                               vote: ValidationVote,
                               stake_amount: Decimal,
                               justification: Optional[str] = None) -> ValidationVoteRecord:
        """
        Vote on a reputation validation request.
        
        Args:
            request_id: Validation request identifier
            vote: Vote choice
            stake_amount: Stake weight for vote
            justification: Optional vote justification
            
        Returns:
            Vote record
        """
        if not self._initialized:
            raise RuntimeError("Reputation Validation AVS not initialized")
            
        if not self.client.session:
            raise RuntimeError("Client session not available")
            
        timestamp = datetime.utcnow()
        
        payload = {
            "request_id": request_id,
            "voter_id": self.client.config.agent_id,
            "vote": vote.value,
            "stake_amount": str(stake_amount),
            "justification": justification,
            "timestamp": timestamp.isoformat()
        }
        
        try:
            async with self.client.session.post(
                f"{self.client.config.base_url}/v1/reputation/validation/votes",
                json=payload
            ) as response:
                response.raise_for_status()
                data = await response.json()
                
                vote_record = ValidationVoteRecord(
                    vote_id=data['vote_id'],
                    request_id=request_id,
                    voter_id=self.client.config.agent_id,
                    vote=vote,
                    stake_weight=stake_amount,
                    justification=justification,
                    timestamp=timestamp
                )
                
                logger.info(f"Vote cast on validation request: {request_id}")
                return vote_record
                
        except Exception as e:
            logger.error(f"Failed to vote on validation request {request_id}: {e}")
            raise
            
    async def finalize_validation(self, request_id: str) -> Dict[str, Any]:
        """
        Finalize a validation request and apply reputation changes.
        
        Args:
            request_id: Validation request identifier
            
        Returns:
            Finalization result
        """
        if not self._initialized:
            raise RuntimeError("Reputation Validation AVS not initialized")
            
        if not self.client.session:
            raise RuntimeError("Client session not available")
            
        payload = {
            "request_id": request_id,
            "finalizer_id": self.client.config.agent_id,
            "finalized_at": datetime.utcnow().isoformat()
        }
        
        try:
            async with self.client.session.post(
                f"{self.client.config.base_url}/v1/reputation/validation/{request_id}/finalize",
                json=payload
            ) as response:
                response.raise_for_status()
                result = await response.json()
                
                logger.info(f"Validation request finalized: {request_id}")
                return result
                
        except Exception as e:
            logger.error(f"Failed to finalize validation request {request_id}: {e}")
            raise
            
    async def get_validation_requests(self, 
                                    status: Optional[str] = None,
                                    limit: int = 100,
                                    offset: int = 0) -> List[ValidationRequest]:
        """
        Get validation requests.
        
        Args:
            status: Optional status filter
            limit: Maximum number of records
            offset: Pagination offset
            
        Returns:
            List of validation requests
        """
        if not self._initialized:
            raise RuntimeError("Reputation Validation AVS not initialized")
            
        if not self.client.session:
            raise RuntimeError("Client session not available")
            
        params = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status
            
        try:
            async with self.client.session.get(
                f"{self.client.config.base_url}/v1/reputation/validation/requests",
                params=params
            ) as response:
                response.raise_for_status()
                data = await response.json()
                
                requests = []
                for req_data in data.get('requests', []):
                    requests.append(ValidationRequest(
                        request_id=req_data['request_id'],
                        agent_id=req_data['agent_id'],
                        action=ReputationAction(req_data['action']),
                        evidence=req_data['evidence'],
                        stake_requirement=Decimal(req_data['stake_requirement']),
                        voting_period=req_data['voting_period'],
                        created_at=datetime.fromisoformat(req_data['created_at']),
                        expires_at=datetime.fromisoformat(req_data['expires_at']),
                        votes=req_data.get('votes', []),
                        status=req_data.get('status', 'pending')
                    ))
                
                return requests
                
        except Exception as e:
            logger.error(f"Failed to get validation requests: {e}")
            raise
            
    async def get_reputation_leaderboard(self, 
                                       limit: int = 100,
                                       tier: Optional[ReputationTier] = None) -> List[ReputationScore]:
        """
        Get reputation leaderboard.
        
        Args:
            limit: Maximum number of records
            tier: Optional tier filter
            
        Returns:
            List of reputation scores ordered by rank
        """
        if not self._initialized:
            raise RuntimeError("Reputation Validation AVS not initialized")
            
        if not self.client.session:
            raise RuntimeError("Client session not available")
            
        params = {"limit": limit}
        if tier:
            params["tier"] = tier.value
            
        try:
            async with self.client.session.get(
                f"{self.client.config.base_url}/v1/reputation/leaderboard",
                params=params
            ) as response:
                response.raise_for_status()
                data = await response.json()
                
                scores = []
                for score_data in data.get('scores', []):
                    scores.append(ReputationScore(
                        agent_id=score_data['agent_id'],
                        overall_score=Decimal(score_data['overall_score']),
                        tier=ReputationTier(score_data['tier']),
                        task_completion_rate=Decimal(score_data['task_completion_rate']),
                        fraud_reports=score_data['fraud_reports'],
                        stake_amount=Decimal(score_data['stake_amount']),
                        validation_accuracy=Decimal(score_data['validation_accuracy']),
                        peer_review_score=Decimal(score_data['peer_review_score']),
                        last_updated=datetime.fromisoformat(score_data['last_updated']),
                        score_history=score_data.get('score_history', []),
                        metadata=score_data.get('metadata')
                    ))
                
                return scores
                
        except Exception as e:
            logger.error(f"Failed to get reputation leaderboard: {e}")
            raise
            
    async def calculate_score_preview(self, 
                                    agent_id: str,
                                    action: ReputationAction,
                                    details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate preview of reputation score change.
        
        Args:
            agent_id: Agent identifier
            action: Reputation action
            details: Action details
            
        Returns:
            Score change preview
        """
        if not self._initialized:
            raise RuntimeError("Reputation Validation AVS not initialized")
            
        if not self.client.session:
            raise RuntimeError("Client session not available")
            
        payload = {
            "agent_id": agent_id,
            "action": action.value,
            "details": details
        }
        
        try:
            async with self.client.session.post(
                f"{self.client.config.base_url}/v1/reputation/preview",
                json=payload
            ) as response:
                response.raise_for_status()
                return await response.json()
                
        except Exception as e:
            logger.error(f"Failed to calculate score preview for {agent_id}: {e}")
            raise
            
    async def get_reputation_stats(self) -> Dict[str, Any]:
        """
        Get overall reputation system statistics.
        
        Returns:
            Reputation statistics
        """
        if not self._initialized:
            raise RuntimeError("Reputation Validation AVS not initialized")
            
        if not self.client.session:
            raise RuntimeError("Client session not available")
            
        try:
            async with self.client.session.get(
                f"{self.client.config.base_url}/v1/reputation/stats"
            ) as response:
                response.raise_for_status()
                return await response.json()
                
        except Exception as e:
            logger.error(f"Failed to get reputation stats: {e}")
            raise