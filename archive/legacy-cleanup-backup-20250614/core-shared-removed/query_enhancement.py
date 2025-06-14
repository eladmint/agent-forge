"""
Advanced query enhancement and understanding for improved search quality.
Part of Search Quality Improvements implementation.
"""

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)


class QueryIntent(Enum):
    """Detected user intent from query analysis."""

    FIND_EVENTS = "find_events"
    FIND_SPEAKERS = "find_speakers"
    FIND_ORGANIZERS = "find_organizers"
    GENERAL_INFO = "general_info"
    DATE_SPECIFIC = "date_specific"
    TOPIC_SPECIFIC = "topic_specific"
    PERSON_SPECIFIC = "person_specific"
    COMPANY_SPECIFIC = "company_specific"


class QueryComplexity(Enum):
    """Query complexity classification."""

    SIMPLE = "simple"  # Single keyword or simple phrase
    COMPOUND = "compound"  # Multiple related concepts
    COMPLEX = "complex"  # Multiple entities with relationships
    CONVERSATIONAL = "conversational"  # Natural language question


@dataclass
class QueryAnalysis:
    """Comprehensive analysis of user query."""

    original_query: str
    cleaned_query: str
    intent: QueryIntent
    complexity: QueryComplexity
    confidence: float
    entities: Dict[str, List[str]] = field(default_factory=dict)
    keywords: List[str] = field(default_factory=list)
    semantic_concepts: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    context_boost_terms: List[str] = field(default_factory=list)


class QueryEnhancer:
    """Advanced query enhancement and understanding system."""

    def __init__(self):
        """Initialize query enhancer with knowledge patterns."""
        self.blockchain_domains = {
            "defi": [
                "defi",
                "decentralized finance",
                "yield farming",
                "liquidity",
                "amm",
                "dex",
                "lending",
                "borrowing",
                "staking",
            ],
            "nft": [
                "nft",
                "non-fungible token",
                "digital art",
                "collectibles",
                "marketplace",
                "opensea",
                "metadata",
            ],
            "layer2": [
                "layer 2",
                "l2",
                "scaling",
                "rollup",
                "optimism",
                "arbitrum",
                "polygon",
                "sidechains",
            ],
            "web3": [
                "web3",
                "decentralized web",
                "dapp",
                "smart contracts",
                "blockchain applications",
            ],
            "gaming": [
                "blockchain gaming",
                "play to earn",
                "p2e",
                "gamefi",
                "in-game assets",
                "virtual worlds",
            ],
            "infrastructure": [
                "blockchain infrastructure",
                "nodes",
                "validators",
                "consensus",
                "protocols",
            ],
            "regulation": [
                "regulation",
                "compliance",
                "legal",
                "policy",
                "government",
                "regulatory",
            ],
            "institutional": [
                "institutional",
                "enterprise",
                "corporate",
                "banking",
                "traditional finance",
                "adoption",
            ],
        }

        self.intent_patterns = {
            QueryIntent.FIND_EVENTS: [
                r"\b(events?|sessions?|panels?|workshops?|talks?|presentations?)\b",
                r"\b(happening|scheduled|taking place|occurring)\b",
                r"\bwhen is\b",
                r"\bwhat.*events?\b",
                # FIXED: Add investor/fundraising patterns to ensure these route to events
                r"\bevents?\s+(for|about|related to)\s+(investor|fundraising|funding|capital|venture|investment|vc)\b",
                r"\b(investor|fundraising|funding|venture|investment|vc)\s+(events?|opportunities|sessions?)\b",
            ],
            QueryIntent.FIND_SPEAKERS: [
                r"\b(speakers?|presenters?|panelists?|experts?|keynotes?)\b",
                r"\bwho is (speaking|presenting|talking)\b",
                r"\bwho are the (speakers?|experts?)\b",
                r"\btell me about.*speaker\b",
            ],
            QueryIntent.DATE_SPECIFIC: [
                r"\b(today|tomorrow|yesterday)\b",
                r"\b\d{1,2}(st|nd|rd|th)?\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b",
                r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}\b",
                r"\b\d{4}-\d{2}-\d{2}\b",
                r"\bon\s+\w+day\b",
            ],
            QueryIntent.PERSON_SPECIFIC: [
                r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b",  # Name patterns
                r"\bCEO|CTO|founder|director\b",
                r"\btell me about\s+[A-Z]\w+\b",
            ],
            QueryIntent.COMPANY_SPECIFIC: [
                r"\b[A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*\s+(Labs?|Protocol|Foundation|Inc|Corp|Ltd)\b",
                r"\bcompany|organization|project|protocol\b",
            ],
        }

        self.complexity_indicators = {
            QueryComplexity.SIMPLE: ["single word", "basic term"],
            QueryComplexity.COMPOUND: ["and", "or", "with", "about"],
            QueryComplexity.COMPLEX: [
                "relationship",
                "comparison",
                "versus",
                "between",
            ],
            QueryComplexity.CONVERSATIONAL: [
                "what",
                "how",
                "why",
                "when",
                "where",
                "can you",
                "tell me",
            ],
        }

    def analyze_query(self, query: str) -> QueryAnalysis:
        """
        Perform comprehensive analysis of user query.

        Args:
            query: Raw user query string

        Returns:
            QueryAnalysis: Comprehensive query analysis
        """
        logger.debug(f"Analyzing query: '{query}'")

        # Clean and normalize query
        cleaned_query = self._clean_query(query)

        # Detect intent
        intent, intent_confidence = self._detect_intent(cleaned_query)

        # Assess complexity
        complexity = self._assess_complexity(cleaned_query)

        # Extract entities and concepts
        entities = self._extract_entities(cleaned_query)
        keywords = self._extract_keywords(cleaned_query)
        semantic_concepts = self._extract_semantic_concepts(cleaned_query)

        # Generate enhancement suggestions
        suggestions = self._generate_suggestions(cleaned_query, intent, entities)

        # Identify context boost terms
        context_boost_terms = self._identify_context_boost_terms(cleaned_query)

        analysis = QueryAnalysis(
            original_query=query,
            cleaned_query=cleaned_query,
            intent=intent,
            complexity=complexity,
            confidence=intent_confidence,
            entities=entities,
            keywords=keywords,
            semantic_concepts=semantic_concepts,
            suggestions=suggestions,
            context_boost_terms=context_boost_terms,
        )

        logger.info(
            f"Query analysis complete - Intent: {intent.value}, Confidence: {intent_confidence:.2f}, Complexity: {complexity.value}"
        )
        return analysis

    def enhance_query_for_search(self, analysis: QueryAnalysis) -> Dict[str, Any]:
        """
        Generate enhanced search parameters based on query analysis.

        Args:
            analysis: Query analysis result

        Returns:
            Dict containing enhanced search parameters
        """
        enhanced_params = {
            "primary_query": analysis.cleaned_query,
            "expanded_terms": [],
            "boost_terms": analysis.context_boost_terms,
            "similarity_threshold": 0.60,  # Default threshold
            "result_limit": 8,
            "search_strategy": "hybrid",
            "intent_specific_filters": {},
        }

        # Intent-specific enhancements
        if analysis.intent == QueryIntent.FIND_EVENTS:
            enhanced_params["expanded_terms"].extend(
                ["event", "session", "workshop", "panel", "talk"]
            )
            enhanced_params["similarity_threshold"] = 0.55
            enhanced_params["result_limit"] = 12
            enhanced_params["intent_specific_filters"]["type"] = "events"

            # FIXED: For investor/fundraising queries, include past events since Token2049 was historical
            investor_keywords = [
                "investor",
                "fundraising",
                "funding",
                "capital",
                "venture",
                "investment",
                "vc",
            ]
            if any(
                keyword in analysis.cleaned_query.lower()
                for keyword in investor_keywords
            ):
                enhanced_params["include_past_events"] = True
                enhanced_params["expanded_terms"].extend(
                    ["funding", "capital", "venture", "investment", "startup", "pitch"]
                )
                enhanced_params["similarity_threshold"] = (
                    0.45  # Lower threshold for broader matches
                )

        elif analysis.intent == QueryIntent.FIND_SPEAKERS:
            enhanced_params["expanded_terms"].extend(
                ["speaker", "presenter", "expert", "founder", "CEO"]
            )
            enhanced_params["similarity_threshold"] = 0.65
            enhanced_params["result_limit"] = 6
            enhanced_params["intent_specific_filters"]["type"] = "speakers"

        elif analysis.intent == QueryIntent.TOPIC_SPECIFIC:
            # Add domain-specific terms for better context
            for domain, terms in self.blockchain_domains.items():
                for term in terms:
                    if term.lower() in analysis.cleaned_query.lower():
                        enhanced_params["expanded_terms"].extend(
                            terms[:3]
                        )  # Top 3 related terms
                        break
            enhanced_params["similarity_threshold"] = 0.50

        elif analysis.intent == QueryIntent.DATE_SPECIFIC:
            enhanced_params["search_strategy"] = "date_focused"
            enhanced_params["similarity_threshold"] = (
                0.40  # More lenient for date searches
            )

        # Complexity-based adjustments
        if analysis.complexity == QueryComplexity.SIMPLE:
            enhanced_params["expanded_terms"].extend(analysis.semantic_concepts)
            enhanced_params[
                "similarity_threshold"
            ] -= 0.05  # More lenient for simple queries

        elif analysis.complexity == QueryComplexity.COMPLEX:
            enhanced_params[
                "similarity_threshold"
            ] += 0.05  # More strict for complex queries
            enhanced_params["result_limit"] = min(enhanced_params["result_limit"], 6)

        # Entity-based enhancements
        if "technologies" in analysis.entities:
            enhanced_params["boost_terms"].extend(analysis.entities["technologies"])

        if "companies" in analysis.entities:
            enhanced_params["boost_terms"].extend(analysis.entities["companies"])

        # Confidence-based adjustments
        if analysis.confidence < 0.7:
            enhanced_params["similarity_threshold"] -= 0.05
            enhanced_params["result_limit"] += 2
            enhanced_params["expanded_terms"].extend(analysis.suggestions[:2])

        logger.info(
            f"Enhanced search parameters: threshold={enhanced_params['similarity_threshold']}, strategy={enhanced_params['search_strategy']}"
        )
        return enhanced_params

    def _clean_query(self, query: str) -> str:
        """Clean and normalize query text."""
        if not query:
            return ""

        # Remove extra whitespace
        cleaned = re.sub(r"\s+", " ", query.strip())

        # Remove special characters that don't add meaning
        cleaned = re.sub(r"[^\w\s\-\.]", " ", cleaned)

        # Normalize common abbreviations
        abbreviations = {
            r"\bdefi\b": "decentralized finance",
            r"\bnft\b": "non-fungible token",
            r"\bdapp\b": "decentralized application",
            r"\bl2\b": "layer 2",
            r"\bp2e\b": "play to earn",
            r"\bai\b": "artificial intelligence",
            r"\bml\b": "machine learning",
        }

        for abbrev, expansion in abbreviations.items():
            cleaned = re.sub(abbrev, expansion, cleaned, flags=re.IGNORECASE)

        return cleaned

    def _detect_intent(self, query: str) -> Tuple[QueryIntent, float]:
        """Detect user intent from query patterns."""
        intent_scores = {}

        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, query, re.IGNORECASE))
                score += matches
            intent_scores[intent] = score

        # Apply priority logic for overlapping intents
        query_lower = query.lower()

        # FIXED: Conference queries should route to events, not speakers
        conference_indicators = [
            "token 2049",
            "token2049",
            "ethcc",
            "devcon",
            "consensus",
        ]
        if any(conf in query_lower for conf in conference_indicators):
            intent_scores[
                QueryIntent.FIND_EVENTS
            ] += 3  # Strong boost for conference queries

        # Event-related queries take priority if they contain event keywords
        if any(
            word in query_lower
            for word in [
                "events",
                "sessions",
                "workshops",
                "panels",
                "happening",
                "scheduled",
            ]
        ):
            if (
                intent_scores.get(QueryIntent.FIND_EVENTS, 0) > 0
                or "event" in query_lower
            ):
                intent_scores[QueryIntent.FIND_EVENTS] += 2

        # FIXED: Investor/fundraising queries should route to events
        investor_indicators = [
            "investor",
            "fundraising",
            "funding",
            "capital",
            "venture",
            "investment",
            "vc",
        ]
        if (
            any(inv in query_lower for inv in investor_indicators)
            and "event" in query_lower
        ):
            intent_scores[QueryIntent.FIND_EVENTS] += 2

        # Speaker-related queries take priority if they contain speaker keywords
        if any(
            word in query_lower
            for word in ["speakers", "who are", "presenters", "experts", "keynote"]
        ):
            if intent_scores.get(QueryIntent.FIND_SPEAKERS, 0) > 0 or any(
                word in query_lower for word in ["speakers", "presenters"]
            ):
                intent_scores[QueryIntent.FIND_SPEAKERS] += 2

        # Date-specific queries get priority if they have clear date patterns
        if any(
            word in query_lower for word in ["april", "may", "tomorrow", "today", "on"]
        ):
            date_patterns = [r"\d{1,2}", r"april|may|june|tomorrow|today"]
            if any(re.search(pattern, query_lower) for pattern in date_patterns):
                intent_scores[QueryIntent.DATE_SPECIFIC] += 2

        # Default intent if no specific patterns match
        if not any(intent_scores.values()):
            return QueryIntent.GENERAL_INFO, 0.5

        # Find highest scoring intent
        best_intent = max(intent_scores, key=intent_scores.get)
        max_score = intent_scores[best_intent]

        # Calculate confidence based on score and query length
        total_words = len(query.split())
        confidence = min(0.95, max_score / total_words + 0.3)

        return best_intent, confidence

    def _assess_complexity(self, query: str) -> QueryComplexity:
        """Assess query complexity."""
        word_count = len(query.split())

        # Check for conversational patterns
        if any(
            word in query.lower()
            for word in ["what", "how", "why", "when", "where", "can you", "tell me"]
        ):
            return QueryComplexity.CONVERSATIONAL

        # Check for complex relationship words
        if any(
            word in query.lower()
            for word in ["versus", "compared to", "difference between", "relationship"]
        ):
            return QueryComplexity.COMPLEX

        # Check for compound indicators
        if (
            any(word in query.lower() for word in ["and", "or", "with", "about"])
            or word_count > 5
        ):
            return QueryComplexity.COMPOUND

        return QueryComplexity.SIMPLE

    def _extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extract different types of entities from query."""
        entities = {"technologies": [], "companies": [], "people": [], "topics": []}

        # Technology patterns
        tech_patterns = [
            r"\b(blockchain|ethereum|bitcoin|solana|polygon|avalanche|cardano)\b",
            r"\b(smart contracts?|defi|nft|dao|web3|metaverse)\b",
            r"\b(layer [12]|scaling|rollups?|sidechains?)\b",
        ]

        for pattern in tech_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            entities["technologies"].extend(
                [
                    match.lower() if isinstance(match, str) else match[0].lower()
                    for match in matches
                ]
            )

        # Company/project patterns
        company_patterns = [
            r"\b[A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*\s+(Labs?|Protocol|Foundation|Network)\b",
            r"\b(Uniswap|Compound|Aave|MakerDAO|Chainlink|OpenSea)\b",
        ]

        for pattern in company_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            entities["companies"].extend(matches)

        # People patterns (basic name detection)
        name_pattern = r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b"
        names = re.findall(name_pattern, query)
        entities["people"] = names

        return entities

    def _extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords from query."""
        # Remove stop words and extract meaningful terms
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "can",
            "about",
            "what",
            "how",
            "when",
            "where",
            "why",
            "who",
        }

        # Keep original casing for important terms
        words = []
        for word in query.split():
            if len(word) > 2 and word.lower() not in stop_words:
                # Keep important acronyms in original case
                if word.upper() in ["DEFI", "NFT", "DAO", "AI", "ML"] or word in [
                    "DeFi"
                ]:
                    words.append(word.lower())  # Normalize for consistency
                else:
                    words.append(word.lower())

        # Add domain-specific keywords if found in cleaned query
        cleaned_lower = self._clean_query(query).lower()
        domain_keywords = []
        for domain, terms in self.blockchain_domains.items():
            for term in terms:
                if term in cleaned_lower and term not in words:
                    domain_keywords.append(term)

        # Filter out common question words
        keywords = [
            word
            for word in words
            if word
            not in {"what", "how", "when", "where", "why", "who", "tell", "me", "about"}
        ]

        # Add domain keywords
        keywords.extend(domain_keywords[:3])  # Add top 3 domain-specific terms

        return keywords[:10]  # Limit to top 10 keywords

    def _extract_semantic_concepts(self, query: str) -> List[str]:
        """Extract semantic concepts for query expansion."""
        concepts = []

        # Map query terms to broader concepts
        for domain, terms in self.blockchain_domains.items():
            for term in terms:
                if term.lower() in query.lower():
                    concepts.append(domain)
                    # Add related terms from the same domain
                    concepts.extend([t for t in terms[:3] if t.lower() != term.lower()])
                    break

        return list(set(concepts))

    def _generate_suggestions(
        self, query: str, intent: QueryIntent, entities: Dict[str, List[str]]
    ) -> List[str]:
        """Generate query improvement suggestions."""
        suggestions = []

        # Intent-based suggestions
        if intent == QueryIntent.GENERAL_INFO:
            suggestions.append(
                "Try being more specific - are you looking for events, speakers, or topics?"
            )

        if intent == QueryIntent.FIND_EVENTS and not entities.get("topics"):
            suggestions.append(
                "Consider adding a topic like 'DeFi', 'NFT', or 'Layer 2' to your search"
            )

        if intent == QueryIntent.FIND_SPEAKERS and not entities.get("topics"):
            suggestions.append(
                "Try adding an expertise area like 'blockchain development' or 'cryptocurrency'"
            )

        # Query length suggestions
        if len(query.split()) < 2:
            suggestions.append("Try using more descriptive terms for better results")

        if len(query.split()) > 10:
            suggestions.append(
                "Consider simplifying your query to focus on key concepts"
            )

        return suggestions

    def _identify_context_boost_terms(self, query: str) -> List[str]:
        """Identify terms that should boost search relevance."""
        boost_terms = []

        # Add blockchain/crypto context terms
        if any(
            term in query.lower() for term in ["blockchain", "crypto", "web3", "defi"]
        ):
            boost_terms.extend(
                ["blockchain", "cryptocurrency", "web3", "decentralized"]
            )

        # Add conference-specific terms
        boost_terms.extend(["token2049", "conference", "event", "dubai"])

        # Add technical depth terms if query seems technical
        technical_terms = [
            "protocol",
            "consensus",
            "algorithm",
            "architecture",
            "implementation",
        ]
        if any(term in query.lower() for term in technical_terms):
            boost_terms.extend(technical_terms)

        return list(set(boost_terms))


def analyze_and_enhance_query(query: str) -> Tuple[QueryAnalysis, Dict[str, Any]]:
    """
    Convenience function to analyze and enhance a query in one call.

    Args:
        query: Raw user query string

    Returns:
        Tuple of (QueryAnalysis, enhanced_search_params)
    """
    enhancer = QueryEnhancer()
    analysis = enhancer.analyze_query(query)
    enhanced_params = enhancer.enhance_query_for_search(analysis)

    return analysis, enhanced_params
