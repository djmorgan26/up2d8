# UP2D8 Backend API - Input Validation

This document describes the comprehensive input validation system for the UP2D8 Backend API.

## Overview

The API uses Pydantic v2 for request validation with custom validators and error handlers to ensure:

- **Data integrity**: All inputs meet expected formats and constraints
- **Security**: Protection against injection attacks and malformed data
- **User experience**: Clear, actionable error messages
- **Performance**: Early validation prevents unnecessary processing

## Validation Architecture

### Components

1. **`shared/validation.py`**: Reusable validation utilities, constants, and annotated field types
2. **`shared/error_handlers.py`**: Custom error handlers for user-friendly error messages
3. **API Models**: Pydantic models with validation constraints in each endpoint file
4. **Error Middleware**: Registered in `main.py` to intercept and format validation errors

### Flow

```
Client Request → FastAPI → Pydantic Validation → Custom Validators → Error Handler → Response
```

If validation fails at any stage, the custom error handler formats the errors into a structured JSON response.

## Validation Constraints

### String Fields

| Field Type | Min Length | Max Length | Additional Rules |
|------------|------------|------------|------------------|
| Prompt (chat) | 1 | 10,000 | No whitespace-only |
| Query (search) | 1 | 500 | No whitespace-only |
| Title | 1 | 200 | No whitespace-only |
| Message | 1 | 5,000 | No whitespace-only |
| Topic (single) | 2 | 100 | Trimmed |
| Category | - | 50 | - |

### List Fields

| Field Type | Max Items | Item Constraints |
|------------|-----------|------------------|
| Topics (user topics) | 50 | 2-100 chars each |
| Interests (topic suggestions) | 20 | 2-100 chars each |

### Dictionary Fields

| Field Type | Max Keys | Max Value Length | Additional Rules |
|------------|----------|------------------|------------------|
| Preferences (user) | 50 | 1,000 chars | String values only |
| Details (analytics) | 50 | 1,000 chars | String values only |

### Specialized Fields

**UUID Fields**:
- Format: Standard UUID v4 (with or without hyphens)
- Example: `550e8400-e29b-41d4-a716-446655440000`
- Used for: user_id, message_id, session_id

**Event Type (Analytics)**:
- Allowed values: `article_view`, `article_save`, `article_share`, `chat_message`, `topic_subscribe`, `topic_unsubscribe`, `rss_feed_add`, `rss_feed_remove`, `user_login`, `user_logout`
- Case insensitive (automatically lowercased)

**Feedback Rating**:
- Allowed values: `positive`, `negative`, `neutral`, `thumbs_up`, `thumbs_down`
- Case insensitive (automatically lowercased)

**URLs (RSS feeds)**:
- Must be valid HTTP/HTTPS URL
- Validated by Pydantic's `HttpUrl` type

## Using Validation in Code

### 1. Import Validation Types

```python
from pydantic import BaseModel, Field
from shared.validation import (
    PromptField,
    TitleField,
    UUIDField,
    TopicsListField,
    PreferencesField
)
```

### 2. Define Request Models

```python
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    prompt: PromptField = Field(
        ...,
        examples=["What are the latest developments in AI?"]
    )
```

The `...` indicates the field is required. Use `default=value` for optional fields.

### 3. Use Models in Endpoints

```python
@router.post("/api/chat")
async def chat(request: ChatRequest):
    # request.prompt is automatically validated
    # FastAPI will return 422 if validation fails
    ...
```

## Validation Error Responses

When validation fails, the API returns a structured error response:

### Error Response Format

```json
{
  "error": "Validation Error",
  "message": "The request contains invalid or missing fields",
  "details": [
    {
      "field": "prompt",
      "message": "Must be at least 1 characters long",
      "type": "String Too Short"
    },
    {
      "field": "user_id",
      "message": "Value error, Invalid UUID format: not-a-uuid",
      "type": "Value Error"
    }
  ],
  "path": "/api/chat",
  "method": "POST"
}
```

### Status Code

- `422 Unprocessable Entity` for all validation errors

### Error Fields

- **error**: Error category ("Validation Error")
- **message**: Human-readable description
- **details**: Array of field-level errors
  - **field**: Field name that failed validation
  - **message**: Specific validation failure message
  - **type**: Type of validation error
- **path**: API endpoint path
- **method**: HTTP method

## Common Validation Errors

### 1. Required Field Missing

**Request**:
```json
{
  "prompt": ""
}
```

**Response** (422):
```json
{
  "error": "Validation Error",
  "message": "The request contains invalid or missing fields",
  "details": [
    {
      "field": "prompt",
      "message": "This field is required",
      "type": "Field Required"
    }
  ],
  "path": "/api/chat",
  "method": "POST"
}
```

### 2. String Too Long

**Request**:
```json
{
  "prompt": "a...a" // 10,001 characters
}
```

**Response** (422):
```json
{
  "error": "Validation Error",
  "message": "The request contains invalid or missing fields",
  "details": [
    {
      "field": "prompt",
      "message": "Cannot exceed 10000 characters",
      "type": "String Too Long"
    }
  ],
  "path": "/api/chat",
  "method": "POST"
}
```

### 3. Invalid UUID Format

**Request**:
```json
{
  "user_id": "not-a-uuid",
  "event_type": "article_view",
  "details": {}
}
```

**Response** (422):
```json
{
  "error": "Validation Error",
  "message": "The request contains invalid or missing fields",
  "details": [
    {
      "field": "user_id",
      "message": "Value error, Invalid UUID format: not-a-uuid",
      "type": "Value Error"
    }
  ],
  "path": "/api/analytics",
  "method": "POST"
}
```

### 4. Invalid Enum Value

**Request**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "invalid_event",
  "details": {}
}
```

**Response** (422):
```json
{
  "error": "Validation Error",
  "message": "The request contains invalid or missing fields",
  "details": [
    {
      "field": "event_type",
      "message": "Invalid event type: 'invalid_event'. Must be one of: article_view, article_save, ...",
      "type": "Value Error"
    }
  ],
  "path": "/api/analytics",
  "method": "POST"
}
```

### 5. List Too Long

**Request**:
```json
{
  "topics": ["Topic1", "Topic2", ..., "Topic51"] // 51 items
}
```

**Response** (422):
```json
{
  "error": "Validation Error",
  "message": "The request contains invalid or missing fields",
  "details": [
    {
      "field": "topics",
      "message": "List cannot contain more than 50 items",
      "type": "Value Error"
    }
  ],
  "path": "/api/users",
  "method": "POST"
}
```

## Endpoint-Specific Validation

### Chat Endpoints

**POST /api/chat**
```python
{
  "prompt": str  # 1-10,000 chars, no whitespace-only
}
```

**POST /api/sessions**
```python
{
  "user_id": str,  # Valid UUID format
  "title": str     # 1-200 chars, no whitespace-only
}
```

**POST /api/sessions/{session_id}/messages**
```python
{
  "content": str  # 1-5,000 chars, no whitespace-only
}
```

### Topics Endpoints

**POST /api/topics/suggest**
```python
{
  "interests": list[str],  # Optional, max 20 items, 2-100 chars each
  "query": str             # Optional, max 500 chars
}
```

### Users Endpoints

**POST /api/users**
```python
{
  "topics": list[str]  # Required, max 50 items, 2-100 chars each
}
```

**PUT /api/users/{user_id}**
```python
{
  "topics": list[str] | None,      # Optional, max 50 items, 2-100 chars each
  "preferences": dict | None       # Optional, max 50 keys, max 1000 char values
}
```

### RSS Feeds Endpoints

**POST /api/rss_feeds**
```python
{
  "url": HttpUrl,           # Required, valid HTTP/HTTPS URL
  "category": str | None,   # Optional, max 50 chars
  "title": str | None       # Optional, 1-200 chars
}
```

**POST /api/rss_feeds/suggest**
```python
{
  "query": str  # 1-500 chars
}
```

### Analytics Endpoints

**POST /api/analytics**
```python
{
  "user_id": str,          # Valid UUID format
  "event_type": str,       # Must be from allowed list
  "details": dict          # Max 50 keys, max 1000 char values
}
```

### Feedback Endpoints

**POST /api/feedback**
```python
{
  "message_id": str,  # Valid UUID format
  "user_id": str,     # Valid UUID format
  "rating": str       # Must be from allowed list
}
```

## Custom Validators

### 1. Non-Empty String Validator

Ensures strings are not empty or whitespace-only:

```python
def validate_non_empty_string(value: str) -> str:
    if not value or not value.strip():
        raise ValueError("String cannot be empty or whitespace-only")
    return value.strip()
```

### 2. UUID Format Validator

Validates UUID format (accepts with or without hyphens):

```python
def validate_uuid_format(value: str) -> str:
    uuid_pattern = r'^[a-f0-9]{8}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{12}$'
    if not re.match(uuid_pattern, value, re.IGNORECASE):
        raise ValueError(f"Invalid UUID format: {value}")
    return value
```

### 3. String List Validator

Validates list of strings with constraints:

```python
def validate_string_list(
    values: list[str],
    min_items: int = 0,
    max_items: int = 100,
    min_item_length: int = 1,
    max_item_length: int = 200
) -> list[str]:
    # Validates list length and individual string constraints
    ...
```

### 4. Dictionary Constraints Validator

Validates dictionary size and content:

```python
def validate_dict_constraints(
    value: dict,
    max_keys: int = 50,
    max_value_length: int = 1000
) -> dict:
    # Validates number of keys and string value lengths
    ...
```

## Adding New Validation

To add validation to a new endpoint:

### 1. Define Constants (if needed)

In `shared/validation.py`:

```python
# Add to constants section
MIN_DESCRIPTION_LENGTH = 10
MAX_DESCRIPTION_LENGTH = 500
```

### 2. Create Annotated Type (optional)

```python
DescriptionField = Annotated[
    str,
    Field(
        min_length=MIN_DESCRIPTION_LENGTH,
        max_length=MAX_DESCRIPTION_LENGTH,
        description="Item description"
    ),
    AfterValidator(validate_non_empty_string)
]
```

### 3. Use in Request Model

```python
from shared.validation import DescriptionField

class ItemCreate(BaseModel):
    description: DescriptionField = Field(
        ...,
        examples=["A detailed description of the item"]
    )
```

### 4. Test Validation

Create tests in `tests/test_validation.py`:

```python
def test_item_create_valid():
    """Test valid item creation."""
    item = ItemCreate(description="Valid description")
    assert item.description == "Valid description"

def test_item_create_description_too_short():
    """Test item creation with description too short fails."""
    with pytest.raises(ValidationError) as exc_info:
        ItemCreate(description="Short")

    errors = exc_info.value.errors()
    assert any("description" in str(error["loc"]) for error in errors)
```

## Best Practices

### 1. Use Appropriate Field Types

- Use specialized types (`UUIDField`, `EventTypeField`) for consistency
- Use Pydantic's built-in types (`HttpUrl`, `EmailStr`) when available
- Create custom annotated types for domain-specific fields

### 2. Provide Examples

Always include examples in Field definitions:

```python
prompt: PromptField = Field(
    ...,
    examples=["What are the latest AI developments?"]
)
```

Examples appear in OpenAPI documentation and help users understand expected input.

### 3. Write Descriptive Docstrings

```python
class ChatRequest(BaseModel):
    """
    Request model for chat endpoint.

    The chat endpoint accepts a prompt and returns an AI-generated response
    with optional web search grounding.
    """
    prompt: PromptField
```

### 4. Test Edge Cases

Always test:
- Minimum/maximum lengths
- Empty values
- Whitespace-only values
- Invalid formats
- Boundary conditions

### 5. Keep Constraints Reasonable

- Don't make limits too restrictive (hurts UX)
- Don't make limits too permissive (security/performance risk)
- Consider real-world use cases

### 6. Document Changes

When adding or modifying validation:
- Update this documentation
- Update OpenAPI examples
- Add tests for new constraints
- Announce breaking changes

## Testing Validation

### Unit Tests

Test Pydantic models directly:

```python
def test_model_validation():
    # Valid case
    model = MyModel(field="valid value")
    assert model.field == "valid value"

    # Invalid case
    with pytest.raises(ValidationError):
        MyModel(field="")
```

### Integration Tests

Test via API endpoints:

```python
def test_endpoint_validation(test_client):
    client, _ = test_client

    # Valid request
    response = client.post("/api/endpoint", json={"field": "valid"})
    assert response.status_code == 200

    # Invalid request
    response = client.post("/api/endpoint", json={"field": ""})
    assert response.status_code == 422
    data = response.json()
    assert "Validation Error" in data["error"]
```

## Security Considerations

### 1. Input Sanitization

Validation provides the first line of defense against:

- **SQL Injection**: Constrained string lengths and formats
- **XSS**: Validation before storage (output escaping handled separately)
- **DoS**: Length limits prevent excessive memory usage
- **Type Confusion**: Strict type checking

### 2. What Validation Does NOT Prevent

Validation alone doesn't protect against:

- **Authentication/Authorization Issues**: Use separate auth middleware
- **Business Logic Bugs**: Validate business rules separately
- **Rate Limiting**: Use separate rate limiting middleware
- **Output Encoding**: Always escape output appropriately

### 3. Defense in Depth

Validation is one layer in a comprehensive security strategy:

```
Client → Rate Limiting → Authentication → Validation → Authorization → Business Logic → Output Encoding → Response
```

## Performance Considerations

### 1. Early Validation

Pydantic validates before endpoint logic runs, preventing wasted processing.

### 2. Compiled Validators

Pydantic v2 uses Rust-based validation for performance.

### 3. Caching

Validation results are not cached—each request is validated independently.

### 4. Optimization Tips

- Keep regex patterns simple
- Avoid expensive custom validators
- Use built-in Pydantic types when possible
- Limit maximum lengths appropriately

## Troubleshooting

### Issue: Validation Errors Not Being Caught

**Cause**: Exception handler not registered

**Solution**: Verify in `main.py`:

```python
from shared.error_handlers import validation_exception_handler
app.add_exception_handler(RequestValidationError, validation_exception_handler)
```

### Issue: Error Messages Not User-Friendly

**Cause**: Default Pydantic error messages

**Solution**: Check `shared/error_handlers.py` for message formatting logic. Update `format_validation_error()` to customize messages.

### Issue: Tests Failing with 422 Errors

**Cause**: Test data doesn't match new validation rules

**Solution**: Update test data to use valid values:

```python
# Before
{"user_id": "test_user"}

# After
{"user_id": "550e8400-e29b-41d4-a716-446655440000"}
```

## Summary

The validation system provides:

✅ **Comprehensive input validation** across all endpoints
✅ **Clear, actionable error messages** for developers
✅ **Security** against malformed and malicious input
✅ **Consistency** through reusable validation types
✅ **Performance** through early validation
✅ **Testability** with 80+ passing tests

All validation constraints are documented, tested, and enforced automatically by FastAPI and Pydantic.
