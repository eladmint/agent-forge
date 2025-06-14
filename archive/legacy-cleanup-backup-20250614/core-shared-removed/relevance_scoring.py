"""
Advanced relevance scoring system for improved search result ranking.
Part of Search Quality Improvements implementation.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)


class RelevanceFactors(Enum):
    """Different factors that contribute to relevance scoring."""

    SEMANTIC_SIMILARITY = "semantic_similarity"
    KEYWORD_MATCH = "keyword_match"
    TITLE_MATCH = "title_match"
    DESCRIPTION_MATCH = "description_match"
    ENTITY_MATCH = "entity_match"
    CONTEXT_RELEVANCE = "context_relevance"
    FRESHNESS = "freshness"
    POPULARITY = "popularity"
    COMPLETENESS = "completeness"


@dataclass
class RelevanceScore:
    """Detailed relevance scoring breakdown."""

    total_score: float
    semantic_score: float
    keyword_score: float
    title_score: float
    description_score: float
    entity_score: float
    context_score: float
    freshness_score: float
    popularity_score: float
    completeness_score: float
    confidence: float
    explanation: List[str]


class AdvancedRelevanceScorer:
    """Advanced relevance scoring system with multiple ranking factors."""

    def __init__(self):
        """Initialize the relevance scorer with weights and patterns."""
        # Scoring weights for different factors
        self.weights = {
            RelevanceFactors.SEMANTIC_SIMILARITY: 0.35,  # Base similarity score
            RelevanceFactors.KEYWORD_MATCH: 0.20,  # Exact keyword matches
            RelevanceFactors.TITLE_MATCH: 0.15,  # Title relevance
            RelevanceFactors.DESCRIPTION_MATCH: 0.10,  # Description relevance
            RelevanceFactors.ENTITY_MATCH: 0.10,  # Named entity matches
            RelevanceFactors.CONTEXT_RELEVANCE: 0.05,  # Contextual relevance
            RelevanceFactors.FRESHNESS: 0.02,  # Content freshness
            RelevanceFactors.POPULARITY: 0.02,  # Popularity indicators
            RelevanceFactors.COMPLETENESS: 0.01,  # Data completeness
        }

        # Important field patterns for scoring
        self.important_patterns = {
            "blockchain_terms": [
                "blockchain",
                "cryptocurrency",
                "bitcoin",
                "ethereum",
                "defi",
                "nft",
                "web3",
                "smart contract",
                "dao",
                "protocol",
                "token",
                "dapp",
            ],
            "technical_terms": [
                "consensus",
                "mining",
                "staking",
                "validator",
                "node",
                "layer",
                "scaling",
                "interoperability",
                "cross-chain",
                "oracle",
            ],
            "business_terms": [
                "investment",
                "funding",
                "venture",
                "startup",
                "enterprise",
                "adoption",
                "regulation",
                "compliance",
                "institutional",
            ],
            "event_terms": [
                "conference",
                "summit",
                "workshop",
                "panel",
                "keynote",
                "presentation",
                "session",
                "networking",
                "demo",
            ],
        }

        # Quality indicators
        self.quality_indicators = {
            "high_quality": [
                "detailed",
                "comprehensive",
                "expert",
                "advanced",
                "deep dive",
            ],
            "medium_quality": ["overview", "introduction", "basics", "getting started"],
            "presentation_types": [
                "keynote",
                "panel",
                "workshop",
                "fireside chat",
                "demo",
            ],
        }

    def score_result(
        self,
        result: Dict[str, Any],
        query: str,
        query_keywords: List[str],
        boost_terms: List[str] = None,
        context: str = "",
    ) -> RelevanceScore:
        """
        Calculate comprehensive relevance score for a search result.

        Args:
            result: Search result data (event or speaker)
            query: Original search query
            query_keywords: Extracted query keywords
            boost_terms: Terms that should boost relevance
            context: Additional context for scoring

        Returns:
            RelevanceScore: Detailed scoring breakdown
        """
        logger.debug(
            f"Scoring result: {result.get('title', result.get('name', 'Unknown'))}"
        )

        boost_terms = boost_terms or []

        # Get base semantic similarity
        semantic_score = float(result.get("similarity", 0.0))

        # Calculate individual factor scores
        keyword_score = self._calculate_keyword_score(
            result, query_keywords, boost_terms
        )
        title_score = self._calculate_title_score(result, query, query_keywords)
        description_score = self._calculate_description_score(
            result, query, query_keywords
        )
        entity_score = self._calculate_entity_score(result, query_keywords, boost_terms)
        context_score = self._calculate_context_score(result, context, boost_terms)
        freshness_score = self._calculate_freshness_score(result)
        popularity_score = self._calculate_popularity_score(result)
        completeness_score = self._calculate_completeness_score(result)

        # Calculate weighted total score
        total_score = (
            semantic_score * self.weights[RelevanceFactors.SEMANTIC_SIMILARITY]
            + keyword_score * self.weights[RelevanceFactors.KEYWORD_MATCH]
            + title_score * self.weights[RelevanceFactors.TITLE_MATCH]
            + description_score * self.weights[RelevanceFactors.DESCRIPTION_MATCH]
            + entity_score * self.weights[RelevanceFactors.ENTITY_MATCH]
            + context_score * self.weights[RelevanceFactors.CONTEXT_RELEVANCE]
            + freshness_score * self.weights[RelevanceFactors.FRESHNESS]
            + popularity_score * self.weights[RelevanceFactors.POPULARITY]
            + completeness_score * self.weights[RelevanceFactors.COMPLETENESS]
        )

        # Calculate confidence based on multiple factors
        confidence = self._calculate_confidence(
            semantic_score, keyword_score, title_score, description_score
        )

        # Generate explanation
        explanation = self._generate_explanation(
            result,
            semantic_score,
            keyword_score,
            title_score,
            description_score,
            entity_score,
            context_score,
        )

        return RelevanceScore(
            total_score=min(1.0, max(0.0, total_score)),
            semantic_score=semantic_score,
            keyword_score=keyword_score,
            title_score=title_score,
            description_score=description_score,
            entity_score=entity_score,
            context_score=context_score,
            freshness_score=freshness_score,
            popularity_score=popularity_score,
            completeness_score=completeness_score,
            confidence=confidence,
            explanation=explanation,
        )

    def _calculate_keyword_score(
        self, result: Dict[str, Any], keywords: List[str], boost_terms: List[str]
    ) -> float:
        """Calculate score based on keyword matches."""
        if not keywords:
            return 0.0

        # Get searchable text from result
        searchable_text = self._get_searchable_text(result).lower()

        # Calculate keyword match score
        total_keywords = len(keywords)
        matched_keywords = 0
        match_scores = []

        for keyword in keywords:
            keyword_lower = keyword.lower()

            # Exact match gets full score
            if keyword_lower in searchable_text:
                matched_keywords += 1

                # Check for emphasis (title vs description)
                title_text = result.get("title", result.get("name", "")).lower()
                if keyword_lower in title_text:
                    match_scores.append(1.0)  # Full score for title match
                else:
                    match_scores.append(0.7)  # Partial score for description match

            # Partial match for stemmed/related terms
            elif any(keyword_lower in word for word in searchable_text.split()):
                matched_keywords += 0.5
                match_scores.append(0.5)

        # Boost score for boost terms
        boost_score = 0.0
        for boost_term in boost_terms:
            if boost_term.lower() in searchable_text:
                boost_score += 0.1

        # Calculate final score
        if total_keywords == 0:
            return 0.0

        base_score = matched_keywords / total_keywords
        average_match_quality = (
            sum(match_scores) / len(match_scores) if match_scores else 0.0
        )

        return min(1.0, base_score * average_match_quality + boost_score)

    def _calculate_title_score(
        self, result: Dict[str, Any], query: str, keywords: List[str]
    ) -> float:
        """Calculate score based on title relevance."""
        title = result.get("title", result.get("name", "")).lower()
        if not title:
            return 0.0

        query_lower = query.lower()

        # Direct title match
        if query_lower in title:
            return 1.0

        # Keyword match in title
        title_words = set(title.split())
        keyword_matches = sum(
            1 for keyword in keywords if keyword.lower() in title_words
        )

        if keywords:
            keyword_score = keyword_matches / len(keywords)
        else:
            keyword_score = 0.0

        # Check for important terms in title
        importance_boost = 0.0
        for category, terms in self.important_patterns.items():
            for term in terms:
                if term in title:
                    importance_boost += 0.1

        return min(1.0, keyword_score + importance_boost)

    def _calculate_description_score(
        self, result: Dict[str, Any], query: str, keywords: List[str]
    ) -> float:
        """Calculate score based on description relevance."""
        description = result.get("description", result.get("bio", "")).lower()
        if not description:
            return 0.0

        query_lower = query.lower()

        # Direct description match
        if query_lower in description:
            return 0.8  # Slightly lower than title match

        # Keyword density in description
        description_words = description.split()
        total_words = len(description_words)

        if total_words == 0:
            return 0.0

        keyword_count = sum(
            description_words.count(keyword.lower()) for keyword in keywords
        )

        # Calculate keyword density (with diminishing returns)
        density = keyword_count / total_words
        density_score = min(1.0, density * 10)  # Scale up density

        # Check for quality indicators
        quality_boost = 0.0
        for quality_type, indicators in self.quality_indicators.items():
            for indicator in indicators:
                if indicator in description:
                    quality_boost += 0.05

        return min(1.0, density_score + quality_boost)

    def _calculate_entity_score(
        self, result: Dict[str, Any], keywords: List[str], boost_terms: List[str]
    ) -> float:
        """Calculate score based on named entity matches."""
        searchable_text = self._get_searchable_text(result).lower()

        entity_score = 0.0

        # Check for blockchain/crypto entities
        for category, entities in self.important_patterns.items():
            for entity in entities:
                if entity in searchable_text:
                    entity_score += 0.1

        # Check for boost term entities
        for boost_term in boost_terms:
            if boost_term.lower() in searchable_text:
                entity_score += 0.15

        return min(1.0, entity_score)

    def _calculate_context_score(
        self, result: Dict[str, Any], context: str, boost_terms: List[str]
    ) -> float:
        """Calculate score based on contextual relevance."""
        if not context:
            return 0.5  # Neutral score if no context

        searchable_text = self._get_searchable_text(result).lower()
        context_lower = context.lower()

        # Context word overlap
        context_words = set(context_lower.split())
        result_words = set(searchable_text.split())

        overlap = len(context_words.intersection(result_words))
        if context_words:
            overlap_score = overlap / len(context_words)
        else:
            overlap_score = 0.0

        # Boost for conference context
        conference_boost = 0.0
        if any(
            term in searchable_text for term in ["token2049", "dubai", "conference"]
        ):
            conference_boost = 0.2

        return min(1.0, overlap_score + conference_boost)

    def _calculate_freshness_score(self, result: Dict[str, Any]) -> float:
        """Calculate score based on content freshness."""
        # For now, return neutral score
        # Could be enhanced with actual date information
        return 0.5

    def _calculate_popularity_score(self, result: Dict[str, Any]) -> float:
        """Calculate score based on popularity indicators."""
        # Check for popularity indicators
        popularity_score = 0.5  # Base score

        # Check for social links (indicates engagement)
        social_fields = ["twitter_url", "linkedin_url", "website_url"]
        social_count = sum(1 for field in social_fields if result.get(field))
        popularity_score += social_count * 0.1

        # Check for keynote/featured status
        title = result.get("title", "").lower()
        if any(term in title for term in ["keynote", "featured", "main", "opening"]):
            popularity_score += 0.2

        return min(1.0, popularity_score)

    def _calculate_completeness_score(self, result: Dict[str, Any]) -> float:
        """Calculate score based on data completeness."""
        required_fields = (
            ["title", "description"] if "title" in result else ["name", "bio"]
        )
        optional_fields = [
            "website_url",
            "twitter_url",
            "linkedin_url",
            "location",
            "time",
        ]

        # Check required fields
        required_complete = all(result.get(field) for field in required_fields)
        if not required_complete:
            return 0.3  # Low score for incomplete required data

        # Check optional fields
        optional_complete = sum(1 for field in optional_fields if result.get(field))
        completeness = 0.7 + (optional_complete / len(optional_fields)) * 0.3

        return completeness

    def _calculate_confidence(
        self,
        semantic_score: float,
        keyword_score: float,
        title_score: float,
        description_score: float,
    ) -> float:
        """Calculate confidence in the relevance score."""
        # High confidence when multiple factors agree
        scores = [semantic_score, keyword_score, title_score, description_score]

        # Remove zero scores for confidence calculation
        non_zero_scores = [s for s in scores if s > 0]

        if not non_zero_scores:
            return 0.1

        if len(non_zero_scores) == 1:
            # Only one factor, lower confidence
            return max(0.3, min(0.8, non_zero_scores[0]))

        # Calculate score agreement (low variance = high confidence)
        mean_score = sum(non_zero_scores) / len(non_zero_scores)
        variance = sum((s - mean_score) ** 2 for s in non_zero_scores) / len(
            non_zero_scores
        )

        # Convert variance to confidence (lower variance = higher confidence)
        # Use square root to reduce the impact of variance
        confidence = max(0.1, 1.0 - (variance**0.5))

        # Boost confidence for high scores but cap at reasonable level
        if mean_score > 0.7:
            confidence = min(0.95, confidence + 0.1)
        elif mean_score > 0.5:
            confidence = min(0.85, confidence + 0.05)

        return confidence

    def _generate_explanation(
        self,
        result: Dict[str, Any],
        semantic_score: float,
        keyword_score: float,
        title_score: float,
        description_score: float,
        entity_score: float,
        context_score: float,
    ) -> List[str]:
        """Generate human-readable explanation of scoring."""
        explanation = []

        # Semantic similarity explanation
        if semantic_score >= 0.7:
            explanation.append("Strong semantic similarity to query")
        elif semantic_score >= 0.5:
            explanation.append("Good semantic similarity to query")
        else:
            explanation.append("Moderate semantic similarity to query")

        # Keyword match explanation
        if keyword_score >= 0.8:
            explanation.append("Excellent keyword matches")
        elif keyword_score >= 0.6:
            explanation.append("Good keyword matches")
        elif keyword_score >= 0.3:
            explanation.append("Some keyword matches")

        # Title relevance explanation
        if title_score >= 0.8:
            explanation.append("Highly relevant title")
        elif title_score >= 0.5:
            explanation.append("Relevant title")

        # Description relevance explanation
        if description_score >= 0.6:
            explanation.append("Relevant description content")

        # Entity matching explanation
        if entity_score >= 0.5:
            explanation.append("Contains relevant entities/concepts")

        # Context explanation
        if context_score >= 0.7:
            explanation.append("Strong contextual relevance")

        return explanation

    def _get_searchable_text(self, result: Dict[str, Any]) -> str:
        """Extract all searchable text from a result."""
        text_parts = []

        # Add title/name
        text_parts.append(result.get("title", result.get("name", "")))

        # Add description/bio
        text_parts.append(result.get("description", result.get("bio", "")))

        # Add other relevant fields
        other_fields = ["location", "company", "topic", "theme"]
        for field in other_fields:
            if result.get(field):
                text_parts.append(str(result[field]))

        return " ".join(filter(None, text_parts))


def score_and_rank_results(
    results: List[Dict[str, Any]],
    query: str,
    query_keywords: List[str],
    boost_terms: List[str] = None,
    context: str = "",
) -> List[Tuple[Dict[str, Any], RelevanceScore]]:
    """
    Score and rank search results by relevance.

    Args:
        results: List of search results
        query: Original search query
        query_keywords: Extracted query keywords
        boost_terms: Terms that should boost relevance
        context: Additional context for scoring

    Returns:
        List of (result, score) tuples sorted by relevance
    """
    scorer = AdvancedRelevanceScorer()

    scored_results = []
    for result in results:
        score = scorer.score_result(result, query, query_keywords, boost_terms, context)
        scored_results.append((result, score))

    # Sort by total score descending
    scored_results.sort(key=lambda x: x[1].total_score, reverse=True)

    return scored_results
