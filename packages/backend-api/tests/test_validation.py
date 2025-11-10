"""
Tests for input validation across all API endpoints.

Tests that validation errors are properly caught and return meaningful error messages.
"""

import pytest
from pydantic import ValidationError

from api.chat import ChatRequest, SessionCreate, MessageContent
from api.topics import TopicSuggestRequest
from api.users import UserCreate, UserUpdate
from api.analytics import AnalyticsEvent
from api.feedback import FeedbackCreate
from api.rss_feeds import RssFeedCreate, RssFeedUpdate, RssFeedSuggestRequest


class TestChatValidation:
    """Test validation for chat endpoint models."""

    def test_chat_request_valid(self):
        """Test valid chat request."""
        request = ChatRequest(prompt="What is AI?")
        assert request.prompt == "What is AI?"

    def test_chat_request_empty_prompt(self):
        """Test chat request with empty prompt fails."""
        with pytest.raises(ValidationError) as exc_info:
            ChatRequest(prompt="")

        errors = exc_info.value.errors()
        assert any("prompt" in str(error["loc"]) for error in errors)

    def test_chat_request_prompt_too_long(self):
        """Test chat request with prompt exceeding max length fails."""
        long_prompt = "a" * 10001  # Max is 10000
        with pytest.raises(ValidationError) as exc_info:
            ChatRequest(prompt=long_prompt)

        errors = exc_info.value.errors()
        assert any("prompt" in str(error["loc"]) for error in errors)

    def test_chat_request_whitespace_only(self):
        """Test chat request with whitespace-only prompt fails."""
        with pytest.raises(ValidationError) as exc_info:
            ChatRequest(prompt="   \n\t  ")

        errors = exc_info.value.errors()
        assert any("prompt" in str(error["loc"]) for error in errors)

    def test_session_create_invalid_uuid(self):
        """Test session create with invalid UUID format fails."""
        with pytest.raises(ValidationError) as exc_info:
            SessionCreate(user_id="not-a-uuid", title="Test Session")

        errors = exc_info.value.errors()
        assert any("user_id" in str(error["loc"]) for error in errors)

    def test_session_create_title_too_long(self):
        """Test session create with title exceeding max length fails."""
        long_title = "a" * 201  # Max is 200
        with pytest.raises(ValidationError) as exc_info:
            SessionCreate(user_id="550e8400-e29b-41d4-a716-446655440000", title=long_title)

        errors = exc_info.value.errors()
        assert any("title" in str(error["loc"]) for error in errors)

    def test_message_content_valid(self):
        """Test valid message content."""
        message = MessageContent(content="Hello, how are you?")
        assert message.content == "Hello, how are you?"


class TestTopicsValidation:
    """Test validation for topics endpoint models."""

    def test_topic_suggest_valid_with_query(self):
        """Test valid topic suggestion request with query."""
        request = TopicSuggestRequest(query="AI technology")
        assert request.query == "AI technology"
        assert request.interests == []

    def test_topic_suggest_valid_with_interests(self):
        """Test valid topic suggestion request with interests."""
        request = TopicSuggestRequest(interests=["AI", "ML", "Tech"])
        assert len(request.interests) == 3

    def test_topic_suggest_too_many_interests(self):
        """Test topic suggestion request with too many interests fails."""
        # Max interests is 20
        too_many_interests = [f"Topic{i}" for i in range(21)]
        with pytest.raises(ValidationError) as exc_info:
            TopicSuggestRequest(interests=too_many_interests)

        errors = exc_info.value.errors()
        assert any("interests" in str(error["loc"]) for error in errors)

    def test_topic_suggest_query_too_long(self):
        """Test topic suggestion request with query too long fails."""
        long_query = "a" * 501  # Max is 500
        with pytest.raises(ValidationError) as exc_info:
            TopicSuggestRequest(query=long_query)

        errors = exc_info.value.errors()
        assert any("query" in str(error["loc"]) for error in errors)


class TestUsersValidation:
    """Test validation for users endpoint models."""

    def test_user_create_valid(self):
        """Test valid user creation."""
        user = UserCreate(topics=["Tech", "Science", "Business"])
        assert len(user.topics) == 3

    def test_user_create_too_many_topics(self):
        """Test user creation with too many topics fails."""
        # Max topics is 50
        too_many_topics = [f"Topic{i}" for i in range(51)]
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(topics=too_many_topics)

        errors = exc_info.value.errors()
        assert any("topics" in str(error["loc"]) for error in errors)

    def test_user_update_valid_preferences(self):
        """Test valid user update with preferences."""
        user = UserUpdate(preferences={"theme": "dark", "notifications": "enabled"})
        assert user.preferences["theme"] == "dark"

    def test_user_update_too_many_preference_keys(self):
        """Test user update with too many preference keys fails."""
        # Max dict keys is 50
        too_many_keys = {f"key{i}": f"value{i}" for i in range(51)}
        with pytest.raises(ValidationError) as exc_info:
            UserUpdate(preferences=too_many_keys)

        errors = exc_info.value.errors()
        assert any("preferences" in str(error["loc"]) for error in errors)


class TestAnalyticsValidation:
    """Test validation for analytics endpoint models."""

    def test_analytics_event_valid(self):
        """Test valid analytics event."""
        event = AnalyticsEvent(
            user_id="550e8400-e29b-41d4-a716-446655440000",
            event_type="article_view",
            details={"article_id": "123", "duration": 45}
        )
        assert event.event_type == "article_view"

    def test_analytics_event_invalid_type(self):
        """Test analytics event with invalid type fails."""
        with pytest.raises(ValidationError) as exc_info:
            AnalyticsEvent(
                user_id="550e8400-e29b-41d4-a716-446655440000",
                event_type="invalid_event_type",
                details={}
            )

        errors = exc_info.value.errors()
        assert any("event_type" in str(error["loc"]) for error in errors)

    def test_analytics_event_invalid_uuid(self):
        """Test analytics event with invalid UUID fails."""
        with pytest.raises(ValidationError) as exc_info:
            AnalyticsEvent(
                user_id="not-a-uuid",
                event_type="article_view",
                details={}
            )

        errors = exc_info.value.errors()
        assert any("user_id" in str(error["loc"]) for error in errors)


class TestFeedbackValidation:
    """Test validation for feedback endpoint models."""

    def test_feedback_create_valid(self):
        """Test valid feedback creation."""
        feedback = FeedbackCreate(
            message_id="550e8400-e29b-41d4-a716-446655440000",
            user_id="550e8400-e29b-41d4-a716-446655440001",
            rating="positive"
        )
        assert feedback.rating == "positive"

    def test_feedback_create_invalid_rating(self):
        """Test feedback creation with invalid rating fails."""
        with pytest.raises(ValidationError) as exc_info:
            FeedbackCreate(
                message_id="550e8400-e29b-41d4-a716-446655440000",
                user_id="550e8400-e29b-41d4-a716-446655440001",
                rating="invalid_rating"
            )

        errors = exc_info.value.errors()
        assert any("rating" in str(error["loc"]) for error in errors)

    def test_feedback_create_invalid_uuid(self):
        """Test feedback creation with invalid UUID fails."""
        with pytest.raises(ValidationError) as exc_info:
            FeedbackCreate(
                message_id="not-a-uuid",
                user_id="550e8400-e29b-41d4-a716-446655440001",
                rating="positive"
            )

        errors = exc_info.value.errors()
        assert any("message_id" in str(error["loc"]) for error in errors)


class TestRSSFeedsValidation:
    """Test validation for RSS feeds endpoint models."""

    def test_rss_feed_create_valid(self):
        """Test valid RSS feed creation."""
        feed = RssFeedCreate(url="https://techcrunch.com/feed/")
        assert str(feed.url) == "https://techcrunch.com/feed/"

    def test_rss_feed_create_invalid_url(self):
        """Test RSS feed creation with invalid URL fails."""
        with pytest.raises(ValidationError) as exc_info:
            RssFeedCreate(url="not-a-valid-url")

        errors = exc_info.value.errors()
        assert any("url" in str(error["loc"]) for error in errors)

    def test_rss_feed_create_title_too_long(self):
        """Test RSS feed creation with title too long fails."""
        long_title = "a" * 201  # Max is 200
        with pytest.raises(ValidationError) as exc_info:
            RssFeedCreate(url="https://techcrunch.com/feed/", title=long_title)

        errors = exc_info.value.errors()
        assert any("title" in str(error["loc"]) for error in errors)

    def test_rss_feed_suggest_valid(self):
        """Test valid RSS feed suggestion request."""
        request = RssFeedSuggestRequest(query="technology news")
        assert request.query == "technology news"

    def test_rss_feed_suggest_query_too_long(self):
        """Test RSS feed suggestion with query too long fails."""
        long_query = "a" * 501  # Max is 500
        with pytest.raises(ValidationError) as exc_info:
            RssFeedSuggestRequest(query=long_query)

        errors = exc_info.value.errors()
        assert any("query" in str(error["loc"]) for error in errors)
