# ADR-003: Hybrid Search Strategy (Vector + Keyword Fallback)

**Date:** 2025-04-25

**Status:** Accepted

## Context

The initial chatbot API design relied primarily on semantic vector search (`pg_vector` cosine distance via `match_events` RPC) to retrieve relevant events based on user queries. During testing, it was found that vector search alone performed poorly for queries targeting specific keywords or proper nouns present only in certain fields (like the event `name`) when other fields (like `description`) contained semantically different text. For example, querying for "NEAR" failed to retrieve an event named "...Featuring Illia Polosukhin, Co-Founder, NEAR Protocol" because the event description focused on unrelated topics ("Decentralized AI"). Lowering the vector similarity threshold (`match_threshold`) did not reliably resolve these keyword-specific misses. Relying solely on semantic search resulted in poor recall for keyword-based queries.

## Decision

Implement a **Hybrid Search Strategy** for event retrieval (`vector_search_events` tool):

1.  **Primary Search:** Perform the semantic vector search using the `match_events` RPC function in Supabase.
2.  **Fallback Trigger:** If the primary vector search returns **zero results**, trigger a secondary search.
3.  **Secondary Search (Keyword Fallback):** Execute a traditional SQL keyword search using `ILIKE` (case-insensitive) against the event `name` and `description` fields. This is implemented via a synchronous helper function (`_sync_keyword_search_events`) called using `asyncio.to_thread`.
4.  **Return:** Return the results from the first search method that yields matches (either vector search or keyword fallback).

This approach leverages the strengths of semantic search for understanding intent and variations, while ensuring high recall for specific keywords via the fallback.

## Consequences

*   **Positive:**
    *   **Improved Recall:** Significantly increases the likelihood of finding relevant events for queries based on specific keywords or names that might be missed by pure semantic search.
    *   **Robustness:** Provides a fallback mechanism when semantic search fails or embeddings don't capture specific terms adequately.
    *   **Maintains Semantic Benefits:** Still utilizes vector search as the primary method for handling synonyms, paraphrasing, and broader topic queries.
*   **Negative/Risks:**
    *   **Increased Latency (on Fallback):** Queries that trigger the fallback will incur the latency of both the initial vector search *and* the subsequent keyword search.
    *   **Potential for Less Relevant Fallback Results:** Keyword matches might sometimes be less contextually relevant than semantic matches would have been (though this is mitigated by it being a fallback).
    *   **Complexity:** Adds complexity to the retrieval logic within the `vector_search_events` tool implementation.
*   **Neutral/Trade-offs:**
    *   Prioritizes recall for keyword queries over potentially slightly higher precision of pure semantic search in some edge cases.

## Alternatives Considered

*   **Tune Vector Search Parameters Only:** Attempting further tuning of `match_threshold` or `match_count`. (Rejected as initial attempts showed this was insufficient for keyword-specific misses).
*   **Embed Different Text Combinations:** Experimenting with different text combinations (e.g., only name, name + description + speakers) for event embeddings. (Rejected as potentially complex to manage and still not guaranteed to capture all specific keywords effectively).
*   **Always Run Both Searches (Parallel Fusion):** Running vector and keyword searches simultaneously and then merging/re-ranking the results using algorithms like Reciprocal Rank Fusion (RRF). (Rejected for MVP due to increased implementation complexity compared to the fallback strategy).
*   **Cross-Encoder Re-ranking:** Using both vector and keyword search to generate candidates, then employing a more powerful (but slower) cross-encoder model to re-rank the combined list. (Rejected for MVP due to complexity and latency concerns).
*   **Alternative Keyword Search Methods:** Using more sophisticated keyword search algorithms like BM25 (commonly used for sparse vectors) or PostgreSQL's Full-Text Search (FTS) features instead of simple `ILIKE`. (Rejected `ILIKE` was deemed sufficient and simpler for the fallback scenario in the MVP).

## Links

*   @07-techContext.md (See "Keyword Fallback" under Chatbot Constraints/Challenges)
*   @06-systemPatterns.md (See "Keyword Fallback" under Chatbot Pattern Description)
*   @02-activeContext.md (Reflects successful testing with this pattern)
*   @learnings/debugging_learnings.md (See "April 25, 2025: Semantic Search Keyword Failure (NEAR Query)")
*   @learnings/lessons.md (See "Technical Lessons - Vector Search Limitations") 