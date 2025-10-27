"""
Groq LLM Client
FREE cloud-based LLM provider (replaces Ollama for Azure deployment)

Groq Free Tier:
- 14,400 requests/day
- Models: Llama 3.2, Mixtral, Gemma
- Fast inference (fastest LLM API available)
- Get API key: https://console.groq.com/
"""
import os
from typing import Optional, List, Dict, Any
import structlog
from groq import Groq

logger = structlog.get_logger()


class GroqClient:
    """
    Groq LLM client for FREE cloud deployment

    Compatible with existing LLMClient interface for easy swapping
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.3-70b-versatile"):
        """
        Initialize Groq client

        Args:
            api_key: Groq API key (or set GROQ_API_KEY env var)
            model: Model to use (default: llama-3.3-70b-versatile - fast and free)

        Available FREE models:
        - llama-3.3-70b-versatile (recommended: fast, best quality)
        - llama-3.1-8b-instant (faster, good quality)
        - mixtral-8x7b-32768 (good quality)
        - gemma2-9b-it (good balance)
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")

        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY environment variable must be set. "
                "Get your free API key at: https://console.groq.com/"
            )

        self.client = Groq(api_key=self.api_key)
        self.model = model

        logger.info("groq_client_initialized", model=model)

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        system_message: Optional[str] = None
    ) -> str:
        """
        Generate text completion

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Randomness (0.0 = deterministic, 1.0 = creative)
            system_message: Optional system message

        Returns:
            Generated text
        """
        try:
            messages = []

            if system_message:
                messages.append({
                    "role": "system",
                    "content": system_message
                })

            messages.append({
                "role": "user",
                "content": prompt
            })

            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )

            generated_text = response.choices[0].message.content

            # Log usage for monitoring free tier limits
            logger.info(
                "groq_generation_complete",
                model=self.model,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens
            )

            return generated_text

        except Exception as e:
            logger.error("groq_generation_failed", error=str(e))
            raise

    async def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """
        Chat completion with conversation history

        Args:
            messages: List of message dicts with 'role' and 'content'
                Example: [
                    {"role": "system", "content": "You are a helpful assistant"},
                    {"role": "user", "content": "Hello!"},
                    {"role": "assistant", "content": "Hi! How can I help?"},
                    {"role": "user", "content": "What's the weather?"}
                ]
            max_tokens: Maximum tokens to generate
            temperature: Randomness

        Returns:
            Assistant's response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )

            generated_text = response.choices[0].message.content

            logger.info(
                "groq_chat_complete",
                model=self.model,
                total_tokens=response.usage.total_tokens
            )

            return generated_text

        except Exception as e:
            logger.error("groq_chat_failed", error=str(e))
            raise

    async def summarize(self, text: str, max_length: int = 200) -> str:
        """
        Summarize text

        Args:
            text: Text to summarize
            max_length: Maximum summary length in tokens

        Returns:
            Summary text
        """
        system_message = "You are an expert at creating concise, informative summaries."
        prompt = f"Summarize the following text in {max_length} tokens or less:\n\n{text}"

        return await self.generate(
            prompt=prompt,
            max_tokens=max_length,
            temperature=0.3,  # Lower temp for more factual summaries
            system_message=system_message
        )

    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get current usage stats

        Note: Groq doesn't provide a usage API yet, so this is a placeholder
        You should track usage manually in your database

        Returns:
            Usage statistics
        """
        return {
            "provider": "groq",
            "model": self.model,
            "free_tier_limit": "14,400 requests/day",
            "note": "Track usage manually in database"
        }


# Factory function for easy integration
def get_groq_client(model: str = "llama-3.3-70b-versatile") -> GroqClient:
    """
    Get Groq LLM client

    Args:
        model: Model to use

    Returns:
        GroqClient instance
    """
    return GroqClient(model=model)


if __name__ == "__main__":
    import asyncio

    async def test_groq():
        """Test Groq client"""
        try:
            client = get_groq_client()

            # Test generation
            print("\n=== Testing Generation ===")
            response = await client.generate(
                prompt="What are the benefits of AI?",
                max_tokens=100
            )
            print(f"Response: {response}")

            # Test chat
            print("\n=== Testing Chat ===")
            messages = [
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "Tell me a short joke about programming"}
            ]
            chat_response = await client.chat(messages, max_tokens=100)
            print(f"Chat Response: {chat_response}")

            # Test summarization
            print("\n=== Testing Summarization ===")
            long_text = """
            Artificial Intelligence has transformed the way we interact with technology.
            Machine learning algorithms can now process vast amounts of data, identify patterns,
            and make predictions with remarkable accuracy. From natural language processing to
            computer vision, AI applications are becoming increasingly sophisticated and accessible.
            """
            summary = await client.summarize(long_text, max_length=50)
            print(f"Summary: {summary}")

            print("\n✅ All Groq tests passed!")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("\nMake sure to set GROQ_API_KEY environment variable")
            print("Get your free API key at: https://console.groq.com/")

    # Run tests
    asyncio.run(test_groq())
