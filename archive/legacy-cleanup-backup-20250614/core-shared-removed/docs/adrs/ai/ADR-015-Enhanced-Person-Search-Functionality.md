# ADR-015: Enhanced Person Search Functionality

## Status

Accepted (2025-05-23)

## Context

The Nuru AI API was returning generic responses for specific questions about people, particularly when users asked about speakers at Token 2049 events (e.g., "Who is Vyas Raina?"). This provided poor user experience as it did not leverage our speaker database for direct, factual answers.

During the consolidation process after hotfixes 4-14, we needed to improve the API's ability to answer specific questions about people rather than relying solely on the LLM, which was returning generic introductory messages.

## Decision

We have implemented an enhanced person search functionality in the `process_chat_with_llm` function that:

1. Detects "who is" and "who's" questions using simple heuristics
2. Extracts the person's name from such queries
3. Makes a direct database call to the `search_speakers_by_name` RPC function in Supabase
4. If speaker information is found, constructs a detailed response including:
   - The speaker's title and organization
   - Their biography
   - Sessions they are speaking at (with dates)
5. Falls back to the standard LLM processing if:
   - The query is not a person search
   - No speaker information is found
   - Any error occurs during the database search

Additionally, we:
- Added system prompt injection to improve LLM context
- Added empty response detection and fallback to a default response
- Improved error handling to return friendly messages instead of throwing exceptions

## Consequences

### Positive

- Significantly improved response quality for speaker-related queries
- Reduced dependency on the LLM for factual information stored in our database
- More consistent and reliable answers for questions about Token 2049 speakers
- Better user experience with detailed, structured information
- Graceful fallback to LLM when specific speaker data isn't available

### Negative

- Increased complexity in the chat processing function
- Added dependency on the `search_speakers_by_name` RPC function in Supabase
- Simple heuristic detection may miss some person queries with different phrasing

### Neutral

- The function now performs more processing before reaching the LLM, which could slightly increase latency for person queries but improves quality

## Related

- ADR-013: FastAPI App State for Dependency Injection (used for DB access)
- ADR-014: Pydantic Model Validation Best Practices
- Consolidation Plan Phase 1 Implementation 