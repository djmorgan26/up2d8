# ADR-001: Free Tier Development Strategy

**Status**: Accepted
**Date**: 2025-10-23
**Author**: Development Team

## Context

Building an AI-powered platform typically requires:
- LLM API access (Claude, GPT-4) - $50-100/month
- Embedding APIs (OpenAI) - $10/month
- Vector database (Pinecone) - $70/month
- Email service (AWS SES) - $5/month
- Infrastructure (AWS) - $30/month

**Total**: ~$165-215/month during 3-month development

This creates barriers:
1. **Cost Barrier**: Developers need API keys and incur costs from day 1
2. **Onboarding Friction**: New team members need multiple accounts and credentials
3. **Development Speed**: Network latency and rate limits slow iteration
4. **Vendor Lock-in**: Code becomes tied to specific providers

## Decision

**We will build a provider abstraction layer that enables 100% free local development while maintaining production-ready code.**

Key components:
1. **LLM Provider Abstraction**: Support Ollama (free/local), Groq (free tier), Anthropic (paid), OpenAI (paid)
2. **Embedding Provider Abstraction**: Support sentence-transformers (free/local) and OpenAI (paid)
3. **Vector DB Abstraction**: Support ChromaDB (free/local), pgvector (free), Pinecone (paid)
4. **Email Provider Abstraction**: Support console logging (free), Mailgun (free tier), SES (paid)
5. **Environment-Based Switching**: All configuration via .env files, zero code changes

## Consequences

### Positive
- **Zero Development Cost**: Developers can build for $0/month using local services
- **Fast Onboarding**: New developers need: `ollama serve` + `docker-compose up` + start coding
- **Rapid Iteration**: No API latency, no rate limits, works offline
- **No Vendor Lock-in**: Switch providers by changing one environment variable
- **Production Ready**: Same code runs in dev and prod
- **Cost Control**: Pay only when ready to scale
- **Team Friendly**: Everyone can develop without API keys
- **Gradual Migration**: Add paid services incrementally (free → free tier → paid)

### Negative
- **Additional Abstraction Layer**: More code to maintain
- **Dev/Prod Parity**: Local models (llama3.2) ≠ production quality (Claude)
- **Testing Overhead**: Must test with multiple providers
- **Initial Complexity**: Developers need to understand abstraction pattern

### Neutral
- **Model Quality Trade-off**: Development uses smaller models (3B params vs 175B), but this is acceptable for development
- **Local Resources**: Ollama requires 4-8GB disk space for models
- **Learning Curve**: Team needs to understand when to use which provider

## Alternatives Considered

### Alternative 1: Pay-from-Day-1 Approach
- **Description**: Use paid APIs (Claude, Pinecone) from start of development
- **Pros**:
  - Dev/prod parity
  - No abstraction complexity
  - Best quality immediately
- **Cons**:
  - $165-215/month during development
  - API key management required
  - Onboarding friction
  - Vendor lock-in
- **Why Not**: Unnecessary cost and complexity for MVP development

### Alternative 2: Mock Everything
- **Description**: Mock all external services during development
- **Pros**:
  - Fast tests
  - No external dependencies
- **Cons**:
  - Can't actually test AI quality
  - Mocks don't match real behavior
  - Integration issues discovered late
- **Why Not**: Need real AI inference to validate prompts and results

### Alternative 3: Shared Dev Account
- **Description**: One paid account shared by team
- **Pros**:
  - Lower cost than individual accounts
  - Real services
- **Cons**:
  - Still costs money
  - API key management
  - Rate limit contention
  - Security risk
- **Why Not**: Still has costs and coordination overhead

## Implementation Notes

### Provider Interface Pattern

All providers implement a common abstract base class:

```python
class BaseLLMClient(ABC):
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        pass
```

Factory pattern creates the appropriate implementation:

```python
def get_llm_client() -> BaseLLMClient:
    provider = os.getenv("LLM_PROVIDER")
    if provider == "ollama":
        return OllamaClient()
    elif provider == "anthropic":
        return AnthropicClient()
    # etc.
```

### Environment Configuration

**Development** (.env.development):
```bash
LLM_PROVIDER=ollama
EMBEDDING_PROVIDER=sentence-transformers
VECTOR_DB_PROVIDER=chroma
EMAIL_PROVIDER=console
```

**Production** (.env.production):
```bash
LLM_PROVIDER=anthropic
EMBEDDING_PROVIDER=openai
VECTOR_DB_PROVIDER=pinecone
EMAIL_PROVIDER=ses
```

### Migration Path

1. **Weeks 1-8**: Pure local (Ollama + ChromaDB) - $0/month
2. **Weeks 9-10**: Add free tier APIs (Groq + Mailgun) - $0/month
3. **Weeks 11-12**: Beta with paid APIs (Claude) - ~$20/month
4. **Month 4+**: Production (all paid services) - ~$50-100/month

### Testing Strategy

- Unit tests: Mock all providers
- Integration tests: Use free providers (Ollama, ChromaDB)
- Production validation: Test with paid providers before launch

## References

- Implementation: `backend/api/services/llm_provider.py`
- Implementation: `backend/api/services/embeddings.py`
- Implementation: `backend/api/services/vector_db.py`
- Implementation: `backend/api/services/email_provider.py`
- Documentation: `docs/development/DEVELOPMENT_SETUP.md`
- Documentation: `docs/development/FREE_TIER_SUMMARY.md`

---

## Revision History

| Date | Author | Change |
|------|--------|--------|
| 2025-10-23 | Development Team | Created - Established free tier development strategy |
