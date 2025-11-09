---
type: pattern
name: Entra ID User Migration Pattern
status: implemented
created: 2025-11-09
updated: 2025-11-09
files:
  - packages/backend-api/api/users.py
  - packages/backend-api/tests/api/test_users.py
related:
  - .ai/knowledge/features/entra-id-authentication.md
  - .ai/knowledge/features/user-preferences-management.md
tags: [migration, entra-id, authentication, users, backend, pattern]
---

# Entra ID User Migration Pattern

## What It Is

A backend pattern for seamlessly migrating legacy user accounts (identified by email only) to the new Entra ID authentication system (identified by user_id/sub from token). Handles three scenarios: existing Entra users, legacy email-only users, and completely new users.

## The Problem

**Before Entra ID integration:**
- Users identified by email field only
- No user_id field in database
- Email extracted from request body

**After Entra ID integration:**
- Users identified by `user_id` (sub from token)
- Email from token claims (not request body)
- Need to link existing email-based users to new Entra ID identities

**Challenge:**
Without migration logic, existing users can't be found because:
1. Database has email but no user_id
2. New API looks up by user_id first
3. Result: Duplicate user creation or "user not found" errors

## How It Works

### Three-Path Lookup Logic (`packages/backend-api/api/users.py:20-67`)

```python
POST /api/users
```

**Path 1: Existing Entra ID User (by user_id)**
```python
existing_user_by_id = users_collection.find_one({"user_id": user_id})

if existing_user_by_id:
    # User exists and is properly indexed
    users_collection.update_one(
        {"user_id": user_id},
        {"$addToSet": {"topics": {"$each": user_create.topics}}}
    )
    return "User topics updated."
```

**Path 2: Legacy User Migration (by email)**
```python
else:
    existing_user_by_email = users_collection.find_one({"email": email})

    if existing_user_by_email:
        # User exists but is missing user_id - MIGRATION
        users_collection.update_one(
            {"email": email},
            {
                "$set": {"user_id": user_id, "email": email},
                "$addToSet": {"topics": {"$each": user_create.topics}}
            }
        )
        return "User account linked and topics updated."
```

**Path 3: Completely New User**
```python
    else:
        # Brand new user - create from scratch
        new_user = {
            "user_id": user_id,
            "email": email,
            "topics": user_create.topics,
            "created_at": datetime.now(UTC)
        }
        users_collection.insert_one(new_user)
        return "New user created."
```

### Flow Diagram

```
POST /api/users
      |
      v
Extract user_id (sub) and email from token
      |
      v
Lookup by user_id
      |
      +----> Found? --> Update topics --> "User topics updated."
      |
      +----> Not found? --> Lookup by email
                                  |
                                  +----> Found? --> Add user_id + Update topics --> "User account linked."
                                  |
                                  +----> Not found? --> Create new user --> "New user created."
```

## Important Decisions

### 1. Two-Step Lookup (user_id then email)
**Why**: Performance and correctness
- Try user_id first (primary key, indexed, fast)
- Fall back to email only if user_id fails
- Prevents duplicate users during migration period

**Alternative rejected**: Always lookup both (wasteful, two DB queries every time)

### 2. Add user_id via $set (not replace)
**Why**: Preserve existing user data during migration
```python
{
    "$set": {"user_id": user_id, "email": email},
    "$addToSet": {"topics": {"$each": user_create.topics}}
}
```
- Updates user_id in place
- Preserves existing topics, preferences, created_at
- Only adds new topics via $addToSet

**Alternative rejected**: Delete and recreate (loses user history)

### 3. Different Success Messages
**Why**: Visibility into what happened
- "User topics updated." = Found by user_id (normal case)
- "User account linked and topics updated." = Migration happened
- "New user created." = Brand new user

**Benefit**: Can monitor migration activity via logs

### 4. Email Validation from Token
**Why**: Ensure email is available before proceeding
```python
if not email:
    raise HTTPException(
        status_code=400,
        detail="Email not available in user token. Ensure 'email' scope is included."
    )
```
- Fails fast if email scope missing from token
- Clear error message for debugging
- Prevents null email in database

### 5. user_id as Primary Identifier
**Why**: user_id (sub) is stable across token refreshes
- Email can change (user updates it in Entra ID)
- Sub claim is permanent per user
- Email is supplementary (for display/communication)

## Usage Example

**Scenario 1: Existing Entra ID user adding topics**
```python
# Request (authenticated via Entra ID)
POST /api/users
{
  "topics": ["AI", "startups"]
}

# Token contains: sub="abc123", email="user@example.com"
# Database has: { user_id: "abc123", email: "user@example.com", topics: ["tech"] }

# Response
{
  "message": "User topics updated.",
  "user_id": "abc123"
}

# Database after: { user_id: "abc123", topics: ["tech", "AI", "startups"] }
```

**Scenario 2: Legacy user migrating**
```python
# Request (authenticated via Entra ID for first time)
POST /api/users
{
  "topics": ["science"]
}

# Token contains: sub="xyz789", email="legacy@example.com"
# Database has: { email: "legacy@example.com", topics: ["tech"] }  # No user_id!

# Response
{
  "message": "User account linked and topics updated.",
  "user_id": "xyz789"
}

# Database after: { user_id: "xyz789", email: "legacy@example.com", topics: ["tech", "science"] }
```

**Scenario 3: Brand new user**
```python
# Request (first-time user)
POST /api/users
{
  "topics": ["music"]
}

# Token contains: sub="new456", email="new@example.com"
# Database has: (no matching user)

# Response
{
  "message": "New user created.",
  "user_id": "new456"
}

# Database after: { user_id: "new456", email: "new@example.com", topics: ["music"], created_at: "2025-11-09..." }
```

## Testing

**Backend tests** (`packages/backend-api/tests/api/test_users.py`):

```python
def test_create_user_new_user():
    # Path 3: Brand new user
    mock_users_collection.find_one.return_value = None
    mock_user = User(sub="new_user_sub", email="new@example.com")
    app.dependency_overrides[get_current_user] = lambda: mock_user

    response = client.post("/api/users", json={"topics": ["tech"]})

    assert response.json()["message"] == "New user created."
    assert inserted_user["user_id"] == "new_user_sub"

def test_create_user_existing_user_by_id():
    # Path 1: Existing Entra ID user
    mock_users_collection.find_one.return_value = {
        "user_id": "existing_sub",
        "email": "existing@example.com"
    }
    mock_user = User(sub="existing_sub", email="existing@example.com")

    response = client.post("/api/users", json={"topics": ["new_topic"]})

    assert response.json()["message"] == "User topics updated."

def test_create_user_existing_user_by_email_migration():
    # Path 2: Legacy user migration
    mock_users_collection.find_one.side_effect = [
        None,  # Not found by user_id
        {"email": "legacy@example.com", "topics": ["old_topic"]}  # Found by email
    ]
    mock_user = User(sub="new_sub_for_legacy_user", email="legacy@example.com")

    response = client.post("/api/users", json={"topics": ["new_topic"]})

    assert response.json()["message"] == "User account linked and topics updated."
    assert update_data["$set"]["user_id"] == "new_sub_for_legacy_user"
```

**Key testing pattern:**
- Use `find_one.side_effect` to simulate different lookup results
- Mock `get_current_user` dependency with test user
- Verify correct database operations called
- Clean up `app.dependency_overrides` after each test

## Common Issues

**Issue**: Migration happens every time user visits
**Solution**: Once user_id is set, Path 1 matches on next request (migration is one-time)

**Issue**: Email changes in Entra ID, user can't be found
**Solution**: user_id is primary key, email is supplementary
- If email changes, user_id still matches (Path 1)
- Could update email in database on each request for consistency

**Issue**: Duplicate users (same email, different user_ids)
**Solution**: Shouldn't happen if:
1. Email is unique in Entra ID
2. Migration logic runs before creating new user
3. Could add unique constraint on email for safety

**Issue**: Missing email scope in token
**Solution**: Backend validation catches this:
```python
if not email:
    raise HTTPException(status_code=400, detail="Email not available...")
```

## When to Use This Pattern

**Use when:**
- Migrating from one auth system to another (e.g., email-based → Entra ID)
- Users identified by different fields in old vs new system
- Need to preserve existing user data
- Can't do offline migration (users migrate on first login)

**Don't use when:**
- Starting fresh with no legacy users
- Can do offline migration (batch update all users)
- Old and new identifiers are the same

## Related Knowledge

- [Entra ID Authentication](../features/entra-id-authentication.md) - Auth system this pattern supports
- [User Preferences Management](../features/user-preferences-management.md) - Feature using this pattern

## Future Ideas

- [ ] Add database migration to proactively add user_id field to all users
- [ ] Log migration events to separate collection for analytics
- [ ] Add unique constraint on user_id (after migration complete)
- [ ] Consider composite key (user_id + email) for safety
- [ ] Update email on every request (keep in sync with Entra ID)
- [ ] Monitor and alert if same email appears with different user_ids
- [ ] Batch migration script for known email-to-user_id mappings
- [ ] Deprecation timeline: Remove email fallback after 100% migration
