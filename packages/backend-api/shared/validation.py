"""
Validation utilities and constraints for API endpoints.

Provides reusable validators, custom field types, and validation error handling.
"""

import re
from typing import Any, Callable
from pydantic import Field, field_validator, ValidationInfo
from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated


# ============================================================================
# Common Constants
# ============================================================================

# String length constraints
MIN_PROMPT_LENGTH = 1
MAX_PROMPT_LENGTH = 10000  # 10K characters for chat prompts

MIN_QUERY_LENGTH = 1
MAX_QUERY_LENGTH = 500  # 500 characters for search queries

MIN_TITLE_LENGTH = 1
MAX_TITLE_LENGTH = 200  # 200 characters for titles

MIN_MESSAGE_LENGTH = 1
MAX_MESSAGE_LENGTH = 5000  # 5K characters for messages

MIN_TOPIC_LENGTH = 2
MAX_TOPIC_LENGTH = 100  # 100 characters for individual topics

MAX_CATEGORY_LENGTH = 50  # 50 characters for categories

# List size constraints
MAX_TOPICS_LIST = 50  # Maximum number of topics a user can have
MAX_INTERESTS_LIST = 20  # Maximum interests for topic suggestions

# Dict size constraints
MAX_DICT_KEYS = 50  # Maximum keys in preferences/details dicts
MAX_DICT_VALUE_LENGTH = 1000  # Maximum string length for dict values

# Allowed values
ALLOWED_FEEDBACK_RATINGS = ["positive", "negative", "neutral", "thumbs_up", "thumbs_down"]
ALLOWED_EVENT_TYPES = [
    "article_view",
    "article_save",
    "article_share",
    "chat_message",
    "topic_subscribe",
    "topic_unsubscribe",
    "rss_feed_add",
    "rss_feed_remove",
    "user_login",
    "user_logout",
]


# ============================================================================
# Validator Functions
# ============================================================================

def validate_non_empty_string(value: str) -> str:
    """Ensure string is not empty or whitespace-only."""
    if not value or not value.strip():
        raise ValueError("String cannot be empty or whitespace-only")
    return value.strip()


def validate_uuid_format(value: str) -> str:
    """Validate UUID format (loose validation for compatibility)."""
    value = value.strip()
    # UUID regex pattern (accepts both with and without hyphens)
    uuid_pattern = r'^[a-f0-9]{8}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{12}$'
    if not re.match(uuid_pattern, value, re.IGNORECASE):
        raise ValueError(f"Invalid UUID format: {value}")
    return value


def validate_string_list(
    values: list[str],
    min_items: int = 0,
    max_items: int = 100,
    min_item_length: int = 1,
    max_item_length: int = 200
) -> list[str]:
    """
    Validate a list of strings.

    Args:
        values: List of strings to validate
        min_items: Minimum number of items
        max_items: Maximum number of items
        min_item_length: Minimum length of each string
        max_item_length: Maximum length of each string

    Returns:
        Validated and cleaned list of strings

    Raises:
        ValueError: If validation fails
    """
    if len(values) < min_items:
        raise ValueError(f"List must contain at least {min_items} items")

    if len(values) > max_items:
        raise ValueError(f"List cannot contain more than {max_items} items")

    cleaned_values = []
    for idx, value in enumerate(values):
        if not isinstance(value, str):
            raise ValueError(f"Item at index {idx} must be a string")

        value = value.strip()

        if len(value) < min_item_length:
            raise ValueError(f"Item at index {idx} must be at least {min_item_length} characters")

        if len(value) > max_item_length:
            raise ValueError(f"Item at index {idx} cannot exceed {max_item_length} characters")

        cleaned_values.append(value)

    return cleaned_values


def validate_dict_constraints(
    value: dict,
    max_keys: int = MAX_DICT_KEYS,
    max_value_length: int = MAX_DICT_VALUE_LENGTH
) -> dict:
    """
    Validate dictionary constraints.

    Args:
        value: Dictionary to validate
        max_keys: Maximum number of keys allowed
        max_value_length: Maximum string length for values

    Returns:
        Validated dictionary

    Raises:
        ValueError: If validation fails
    """
    if not isinstance(value, dict):
        raise ValueError("Value must be a dictionary")

    if len(value) > max_keys:
        raise ValueError(f"Dictionary cannot have more than {max_keys} keys")

    for key, val in value.items():
        if not isinstance(key, str):
            raise ValueError(f"Dictionary key '{key}' must be a string")

        if len(key) > 100:
            raise ValueError(f"Dictionary key '{key}' is too long (max 100 characters)")

        if isinstance(val, str) and len(val) > max_value_length:
            raise ValueError(f"Dictionary value for key '{key}' is too long (max {max_value_length} characters)")

    return value


def validate_event_type(value: str) -> str:
    """Validate analytics event type."""
    value = value.strip().lower()
    if value not in ALLOWED_EVENT_TYPES:
        raise ValueError(
            f"Invalid event type: '{value}'. Must be one of: {', '.join(ALLOWED_EVENT_TYPES)}"
        )
    return value


def validate_feedback_rating(value: str) -> str:
    """Validate feedback rating."""
    value = value.strip().lower()
    if value not in ALLOWED_FEEDBACK_RATINGS:
        raise ValueError(
            f"Invalid rating: '{value}'. Must be one of: {', '.join(ALLOWED_FEEDBACK_RATINGS)}"
        )
    return value


# ============================================================================
# Annotated Types (Reusable Field Types)
# ============================================================================

# Prompt field (for chat messages)
PromptField = Annotated[
    str,
    Field(
        min_length=MIN_PROMPT_LENGTH,
        max_length=MAX_PROMPT_LENGTH,
        description="Chat prompt or message content"
    ),
    AfterValidator(validate_non_empty_string)
]

# Query field (for search queries)
QueryField = Annotated[
    str,
    Field(
        min_length=MIN_QUERY_LENGTH,
        max_length=MAX_QUERY_LENGTH,
        description="Search query string"
    ),
    AfterValidator(validate_non_empty_string)
]

# Title field (for session/feed titles)
TitleField = Annotated[
    str,
    Field(
        min_length=MIN_TITLE_LENGTH,
        max_length=MAX_TITLE_LENGTH,
        description="Title or name"
    ),
    AfterValidator(validate_non_empty_string)
]

# Message field (for chat messages)
MessageField = Annotated[
    str,
    Field(
        min_length=MIN_MESSAGE_LENGTH,
        max_length=MAX_MESSAGE_LENGTH,
        description="Message content"
    ),
    AfterValidator(validate_non_empty_string)
]

# Topic field (single topic string)
TopicField = Annotated[
    str,
    Field(
        min_length=MIN_TOPIC_LENGTH,
        max_length=MAX_TOPIC_LENGTH,
        description="Topic name or tag"
    )
]

# Category field
CategoryField = Annotated[
    str,
    Field(
        max_length=MAX_CATEGORY_LENGTH,
        description="Category name"
    )
]

# UUID field (loose validation)
UUIDField = Annotated[
    str,
    Field(description="UUID identifier"),
    AfterValidator(validate_uuid_format)
]

# Topics list (for user topics)
TopicsListField = Annotated[
    list[TopicField],
    Field(
        max_length=MAX_TOPICS_LIST,
        description="List of topic names"
    )
]

# Interests list (for topic suggestions)
InterestsListField = Annotated[
    list[TopicField],
    Field(
        max_length=MAX_INTERESTS_LIST,
        description="List of user interests"
    )
]

# Event type field
EventTypeField = Annotated[
    str,
    Field(description="Analytics event type"),
    AfterValidator(validate_event_type)
]

# Feedback rating field
FeedbackRatingField = Annotated[
    str,
    Field(description="Feedback rating"),
    AfterValidator(validate_feedback_rating)
]

# Preferences dict
PreferencesField = Annotated[
    dict,
    Field(description="User preferences dictionary"),
    AfterValidator(validate_dict_constraints)
]

# Analytics details dict
DetailsField = Annotated[
    dict,
    Field(description="Event details dictionary"),
    AfterValidator(validate_dict_constraints)
]


# ============================================================================
# Validation Error Messages
# ============================================================================

def get_validation_error_message(field_name: str, error_type: str, **kwargs) -> str:
    """
    Get a user-friendly validation error message.

    Args:
        field_name: Name of the field that failed validation
        error_type: Type of validation error
        **kwargs: Additional context for the error message

    Returns:
        User-friendly error message
    """
    messages = {
        "required": f"The field '{field_name}' is required",
        "empty": f"The field '{field_name}' cannot be empty",
        "too_short": f"The field '{field_name}' must be at least {kwargs.get('min_length')} characters",
        "too_long": f"The field '{field_name}' cannot exceed {kwargs.get('max_length')} characters",
        "invalid_format": f"The field '{field_name}' has an invalid format",
        "invalid_value": f"The field '{field_name}' has an invalid value: {kwargs.get('value')}",
        "list_too_long": f"The field '{field_name}' cannot contain more than {kwargs.get('max_items')} items",
        "list_too_short": f"The field '{field_name}' must contain at least {kwargs.get('min_items')} items",
    }

    return messages.get(error_type, f"Validation error in field '{field_name}'")
