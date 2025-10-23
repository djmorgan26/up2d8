"""
Unit tests for LLM Provider abstraction
Tests the provider factory and individual client implementations
"""
import pytest
import os
from unittest.mock import Mock, patch, AsyncMock
from api.services.llm_provider import (
    LLMFactory,
    OllamaClient,
    GroqClient,
    get_llm_client,
    LLMProvider
)


class TestLLMFactory:
    """Test the LLM factory pattern"""

    def test_create_ollama_client(self):
        """Test factory creates OllamaClient when provider is ollama"""
        with patch.dict(os.environ, {"LLM_PROVIDER": "ollama"}):
            client = LLMFactory.create_client()
            assert isinstance(client, OllamaClient)

    def test_create_groq_client(self):
        """Test factory creates GroqClient when provider is groq"""
        with patch.dict(os.environ, {
            "LLM_PROVIDER": "groq",
            "GROQ_API_KEY": "test_key"
        }):
            client = LLMFactory.create_client()
            assert isinstance(client, GroqClient)

    def test_factory_raises_on_invalid_provider(self):
        """Test factory raises ValueError for unsupported provider"""
        with patch.dict(os.environ, {"LLM_PROVIDER": "invalid_provider"}):
            with pytest.raises(ValueError, match="Unsupported LLM provider"):
                LLMFactory.create_client()

    def test_factory_raises_on_missing_api_key(self):
        """Test factory raises ValueError when required API key is missing"""
        with patch.dict(os.environ, {"LLM_PROVIDER": "groq"}, clear=True):
            with pytest.raises(ValueError, match="GROQ_API_KEY"):
                LLMFactory.create_client()


class TestOllamaClient:
    """Test OllamaClient implementation"""

    @pytest.mark.asyncio
    @pytest.mark.requires_ollama
    async def test_ollama_generate_success(self):
        """Test OllamaClient.generate returns text (requires Ollama running)"""
        client = OllamaClient(
            base_url="http://localhost:11434",
            model="llama3.2:3b"
        )

        result = await client.generate(
            prompt="Say hello in one word",
            max_tokens=10,
            temperature=0.7
        )

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_ollama_generate_with_system_prompt(self):
        """Test OllamaClient.generate with system prompt"""
        client = OllamaClient(
            base_url="http://localhost:11434",
            model="llama3.2:3b"
        )

        # Mock the HTTP client to avoid actual API call
        with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "message": {"content": "Test response"}
            }
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response

            result = await client.generate(
                prompt="Test prompt",
                system_prompt="You are a helpful assistant",
                max_tokens=50
            )

            assert result == "Test response"
            # Verify system prompt was included
            call_args = mock_post.call_args
            messages = call_args[1]["json"]["messages"]
            assert messages[0]["role"] == "system"
            assert messages[1]["role"] == "user"

    @pytest.mark.asyncio
    async def test_ollama_streaming(self):
        """Test OllamaClient.generate_streaming"""
        client = OllamaClient()

        # Mock streaming response
        async def mock_aiter_lines():
            yield '{"message": {"content": "Hello"}}'
            yield '{"message": {"content": " World"}}'

        mock_response = Mock()
        mock_response.aiter_lines = mock_aiter_lines

        with patch.object(client.client, 'stream') as mock_stream:
            mock_stream.return_value.__aenter__.return_value = mock_response

            chunks = []
            async for chunk in client.generate_streaming("Test prompt"):
                chunks.append(chunk)

            assert len(chunks) == 2
            assert chunks[0] == "Hello"
            assert chunks[1] == " World"


class TestGroqClient:
    """Test GroqClient implementation"""

    @pytest.mark.asyncio
    async def test_groq_generate_success(self):
        """Test GroqClient.generate with mocked response"""
        client = GroqClient(api_key="test_key", model="llama-3.1-8b-instant")

        # Mock the HTTP response
        with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "choices": [
                    {"message": {"content": "Test response"}}
                ]
            }
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response

            result = await client.generate(
                prompt="Test prompt",
                max_tokens=100
            )

            assert result == "Test response"

    @pytest.mark.asyncio
    async def test_groq_generate_with_system_prompt(self):
        """Test GroqClient includes system prompt correctly"""
        client = GroqClient(api_key="test_key")

        with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Response"}}]
            }
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response

            await client.generate(
                prompt="Test",
                system_prompt="System instruction"
            )

            # Verify system prompt in request
            call_args = mock_post.call_args
            messages = call_args[1]["json"]["messages"]
            assert len(messages) == 2
            assert messages[0]["role"] == "system"
            assert messages[0]["content"] == "System instruction"


class TestLLMClientSingleton:
    """Test singleton pattern for get_llm_client"""

    def test_get_llm_client_returns_singleton(self):
        """Test that get_llm_client returns the same instance"""
        from api.services import llm_provider

        # Reset singleton
        llm_provider._llm_client = None

        with patch.dict(os.environ, {"LLM_PROVIDER": "ollama"}):
            client1 = get_llm_client()
            client2 = get_llm_client()

            assert client1 is client2

    def test_get_llm_client_creates_new_after_reset(self):
        """Test that resetting singleton creates new instance"""
        from api.services import llm_provider

        with patch.dict(os.environ, {"LLM_PROVIDER": "ollama"}):
            client1 = get_llm_client()

            # Reset singleton
            llm_provider._llm_client = None

            client2 = get_llm_client()

            assert client1 is not client2
            assert type(client1) == type(client2)


class TestProviderInterface:
    """Test that all providers implement the same interface"""

    @pytest.mark.asyncio
    async def test_all_providers_have_generate_method(self):
        """Test all provider classes have generate method"""
        providers = [OllamaClient, GroqClient]

        for provider_class in providers:
            assert hasattr(provider_class, 'generate')
            # Check it's async
            import inspect
            assert inspect.iscoroutinefunction(provider_class.generate)

    @pytest.mark.asyncio
    async def test_all_providers_have_streaming_method(self):
        """Test all provider classes have generate_streaming method"""
        providers = [OllamaClient, GroqClient]

        for provider_class in providers:
            assert hasattr(provider_class, 'generate_streaming')
            import inspect
            assert inspect.isasyncgenfunction(provider_class.generate_streaming)


# Integration test (requires Ollama running)
@pytest.mark.integration
@pytest.mark.requires_ollama
class TestOllamaIntegration:
    """Integration tests with real Ollama instance"""

    @pytest.mark.asyncio
    async def test_real_ollama_summarization(self):
        """Test real summarization with Ollama (slow test)"""
        client = OllamaClient()

        prompt = """Summarize this in one sentence:
        OpenAI announced GPT-5 today with 50% faster inference and improved reasoning capabilities.
        The model is available via API at $0.03 per 1K tokens.
        """

        result = await client.generate(prompt, max_tokens=100)

        assert isinstance(result, str)
        assert len(result) > 20
        assert any(keyword in result.lower() for keyword in ["gpt", "openai", "model", "faster"])
