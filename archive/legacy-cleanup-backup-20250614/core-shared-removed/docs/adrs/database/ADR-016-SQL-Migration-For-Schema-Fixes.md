# ADR-016: SQL Migration for Database Schema Fixes

**Date:** 2025-05-24

**Status:** Accepted

## Context

The Nuru AI API had been experiencing database-related issues stemming from inconsistent column naming in the database schema. Specifically:

1. The code was referencing a column named `user_id` in the `users` table, while some database operations were using a column named `user_identifier`.
2. The `id` column in the `users` table was not configured with a default UUID generation function, leading to NULL value constraint violations when creating new users.

Multiple code-level hotfixes (Hotfix 19 and 20) were implemented to handle both column names in the application code, but these fixes were insufficient due to PostgREST's schema cache in Supabase. The API continued to encounter errors like "Could not find the 'user_identifier' column of 'users' in the schema cache" and "null value in column 'id' of relation 'users' violates not-null constraint".

These issues were severely impacting the API's ability to manage users and track interactions, essentially breaking core functionality.

## Decision

We decided to address the database schema issues directly through SQL migration scripts rather than continuing with code-level workarounds. This approach involved two key migration scripts:

1. **hotfix21-migration.sql**:
   - Added the missing column (`user_id` or `user_identifier`) where needed
   - Copied data between the columns to ensure consistency
   - Reloaded the PostgREST schema cache to recognize both columns

2. **hotfix22-migration.sql**:
   - Added the `uuid-ossp` extension for UUID generation
   - Created a `create_user_with_id` SQL function to properly generate UUIDs
   - Added a `DEFAULT uuid_generate_v4()` constraint to the `id` column
   - Fixed existing rows with NULL IDs by updating them with generated UUIDs

These migration scripts were executed directly on the database through Supabase's SQL editor, without requiring any changes to the API code or deployment.

## Consequences

### Positive:
- **Immediate Resolution**: The database schema issues were resolved without requiring a new API deployment.
- **Direct Control**: We gained direct control over the database schema, allowing us to make precise changes.
- **Schema Cache Resolution**: We were able to explicitly reload the PostgREST schema cache, resolving the cached column issue.
- **Data Consistency**: We ensured data consistency by copying values between columns.
- **Proper Defaults**: We established proper default UUID generation for future records.
- **Backward Compatibility**: The solution maintained compatibility with both column naming conventions.
- **Simplified Codebase**: We avoided further complexity in the application code by handling the issue at the database level.

### Negative/Risks:
- **Manual Database Intervention**: The approach required direct SQL execution, which can be error-prone.
- **Potential Data Loss**: If not carefully executed, SQL migrations can result in data loss (though this was mitigated through proper planning).
- **Documentation Requirement**: The changes need to be well-documented to ensure future developers understand the schema decisions.
- **Schema Duplication**: Having two columns serving the same purpose is not ideal for database design.

### Neutral/Trade-offs:
- **Migration Management**: We chose manual SQL execution over an automated migration system, which was simpler for this one-time fix but less robust for ongoing schema management.
- **Temporary vs. Long-term Solution**: This approach addresses immediate issues but doesn't establish a long-term schema migration strategy.
- **Column Standardization**: We chose to support both column names rather than standardize on one, prioritizing backward compatibility over schema cleanliness.

## Alternatives Considered

### Alternative 1: Continue with Code-Level Fixes
We could have continued attempting to fix the issues through code adjustments in the API. This was not chosen because:
- Previous attempts (Hotfix 19 and 20) had not fully resolved the issues.
- The root cause was in the schema cache, which couldn't be directly accessed through the API code.
- It would have resulted in increasingly complex code to work around a database issue.

### Alternative 2: Complete Database Redesign
We could have redesigned the database schema more thoroughly, standardizing on column names and removing duplications. This was not chosen because:
- It would have been more disruptive to existing data and functionality.
- The immediate priority was to restore service functionality with minimal risk.
- A more comprehensive redesign can still be planned for a future phase.

### Alternative 3: Rebuild and Redeploy the API with Fixed Schema
We could have rebuilt the database with the correct schema and redeployed the API. This was not chosen because:
- It would have been more time-consuming and potentially disruptive.
- It might have resulted in data loss or required complex data migration.
- Direct SQL migration offered a faster, more targeted solution.

## Links

- **Related Memory Bank Documents**: memory-bank/testing.md, memory-bank/02-activeContext.md
- **Related Hotfixes**: Hotfix 19, Hotfix 20, hotfix21-migration.sql, hotfix22-migration.sql
- **Related Error Messages**: 
  - "Could not find the 'user_identifier' column of 'users' in the schema cache"
  - "null value in column 'id' of relation 'users' violates not-null constraint" 