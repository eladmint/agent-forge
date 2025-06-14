# ADR-027: UserInfo Model Field Naming

## Status
Accepted and Implemented (May 25, 2025)

## Context
The Nuru AI Telegram bot was experiencing HTTP 500 errors when attempting to interact with the backend API. Investigation showed that these errors were occurring because of Pydantic validation errors in the API. Specifically, the `UserInfo` model defined in `chatbot_api/core/models.py` was using a field named `user_id`, but the API code was expecting a field named `id`.

The validation error message was:
```
8 validation errors for UserInfo
id
  Field required [type=missing, input_value={'user_id': 'test123', ...}, input_type=dict]
  For further information visit https://errors.pydantic.dev/2.11/v/missing
user_id
  Extra inputs are not permitted [type=extra_forbidden, input_value='test123', input_type=str]
  For further information visit https://errors.pydantic.dev/2.11/v/extra_forbidden
...
```

This inconsistency between the model definition and the API expectations was causing the bot to fail with error status 500 whenever a user tried to interact with it.

## Decision
We decided to modify the `UserInfo` model in `chatbot_api/core/models.py` to use `id` instead of `user_id` as the field name. We also updated all functions that create `UserInfo` objects in `main.py` to use the `id` field name instead of `user_id`.

Key considerations that led to this decision:
1. The change minimizes the scope of the fix by only modifying the model and the functions that create model instances
2. The database schema still uses `user_id` as the column name, which is appropriate at that level
3. This approach maintains the separation between the database layer and the API model layer
4. It keeps the API behavior consistent with existing client expectations

The implementation was straightforward:
1. Update the `UserInfo` model in `chatbot_api/core/models.py` to use `id` instead of `user_id`
2. Update all instances of `UserInfo` object creation in `main.py` to use `id=user_data.get("user_id")` instead of `user_id=user_data.get("user_id")`
3. Deploy the changes to production using the standard deployment process
4. Verify that the Telegram bot now works correctly with the API

## Consequences

### Positive
- Fixed the Status 500 errors in the Telegram bot
- Restored the bot's functionality for all users
- Maintained database schema consistency
- Minimized the scope of the change to only what was necessary

### Negative
- Introduced a slight semantic disconnect between the database field name (`user_id`) and the model field name (`id`)
- Required changes in multiple files
- Required a full production deployment

## Implementation Details
The change was implemented by:
1. Modifying `chatbot_api/core/models.py` to change `user_id` to `id` in the `UserInfo` model:
   ```python
   class UserInfo(BaseModel):
       id: str  # Changed from 'user_id' to 'id' to match what the API expects
       credits: int
       calls: int = 0
       created_at: Optional[str] = None
       # ...
   ```

2. Updating the `get_user_info` and `create_new_user` functions in `chatbot_api/main.py` to use `id` instead of `user_id` when creating `UserInfo` objects:
   ```python
   return UserInfo(
       id=user_data.get("user_id"),  # Changed from user_id=user_data.get("user_id")
       credits=user_data.get("credits", 0),
       # ...
   )
   ```

3. Deploying the changes to production using the `deploy-refactored-production.sh` script
4. Verifying that the API returns HTTP 200 responses and the Telegram bot functions correctly

## References
- [ADR-026: Telegram Bot Authorization Strategy](ADR-026-Telegram-Bot-Authorization-Strategy.md)
- [ADR-025: Telegram Bot Parameter Compatibility](ADR-025-Telegram-Bot-Parameter-Compatibility.md)
- [ADR-014: Pydantic Model Validation Best Practices](ADR-014-Pydantic-Model-Validation-Best-Practices.md)
- [Pydantic Documentation](https://docs.pydantic.dev/latest/) 