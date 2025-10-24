# Conversational AI Agent Architecture (LangChain/LangGraph)

## Document Information
- **Version**: 1.0
- **Created**: 2025-10-24
- **Owner**: Engineering Team
- **Status**: Planning Phase - Implementation scheduled for Weeks 10-11
- **Dependencies**: Requires completion of content aggregation (Week 3-4), digest generation (Week 5-7), and vector database setup
- **Current MVP Phase**: Week 1 (Authentication complete) - This document is for future reference

---

## Overview

The UP2D8 conversational AI agent enables users to explore their daily digest content through natural conversation. When users click "Ask AI" links in their daily emails, they're taken to a web chat interface powered by a sophisticated agent with multi-layered memory, RAG capabilities, and web search integration.

**Key Features**:
- 3-layered memory system (digest context, short-term, long-term)
- Vector-based RAG over user's article history
- Web search capability for real-time information
- Link embedding and referencing for contextual exploration
- Streaming responses with citations
- Cost-effective implementation using free-tier tools during development

---

## Technology Stack

### Core Framework
- **Agent Framework**: LangGraph (preferred for state management and complex flows)
- **Fallback**: LangChain (if LangGraph proves too complex for MVP)
- **LLM Provider**: Ollama (llama3.2:3b) for development, Anthropic Claude for production
- **Vector Database**: ChromaDB (development), Pinecone (production)
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2 (free)

### Tools/Skills Integration
- **Web Search**: Brave Search API (free tier) or SerpAPI
- **Link Extraction**: BeautifulSoup4 + Playwright
- **URL Shortening**: TinyURL or custom shortener for tracking

---

## Architecture Overview

```
┌───────────────────────────────────────────────────────────────────┐
│                         User Chat Interface                        │
│                    (React + WebSocket/SSE)                         │
└────────────────────────────┬──────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────────┐
│                    LangGraph Agent Orchestrator                    │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                     State Management                         │ │
│  │  • Current conversation state                                │ │
│  │  • Active memory layers                                      │ │
│  │  • Tool call history                                         │ │
│  │  • User context & preferences                                │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                             │                                      │
│  ┌──────────────────────────┼──────────────────────────────────┐ │
│  │         Input Processing Node                                │ │
│  │  • Query understanding                                       │ │
│  │  • Intent classification                                     │ │
│  │  • Entity extraction                                         │ │
│  └──────────────────────────┬──────────────────────────────────┘ │
│                             │                                      │
│  ┌──────────────────────────▼──────────────────────────────────┐ │
│  │         Memory Retrieval Node (3 Layers)                     │ │
│  │                                                              │ │
│  │  Layer 1: Digest Context (Current Session)                  │ │
│  │  ├─ Today's digest articles                                 │ │
│  │  ├─ Article summaries & metadata                            │ │
│  │  └─ Pre-loaded on chat initialization                       │ │
│  │                                                              │ │
│  │  Layer 2: Short-Term Memory (Conversation)                  │ │
│  │  ├─ Last N messages in current session                      │ │
│  │  ├─ Recent tool calls & results                             │ │
│  │  └─ Working memory (in-context)                             │ │
│  │                                                              │ │
│  │  Layer 3: Long-Term Memory (User History)                   │ │
│  │  ├─ Vector search across all user's articles                │ │
│  │  ├─ Past conversation summaries                             │ │
│  │  └─ User preferences & interests                            │ │
│  └──────────────────────────┬──────────────────────────────────┘ │
│                             │                                      │
│  ┌──────────────────────────▼──────────────────────────────────┐ │
│  │         Tool Selection & Execution Node                      │ │
│  │                                                              │ │
│  │  Available Tools:                                            │ │
│  │  ├─ RAG Search (vector search over articles)                │ │
│  │  ├─ Web Search (real-time information)                      │ │
│  │  ├─ Link Extractor (extract & embed URLs)                   │ │
│  │  ├─ Article Fetcher (get full article content)              │ │
│  │  └─ Related Articles Finder (similarity search)             │ │
│  └──────────────────────────┬──────────────────────────────────┘ │
│                             │                                      │
│  ┌──────────────────────────▼──────────────────────────────────┐ │
│  │         Response Generation Node                             │ │
│  │  • Synthesize information from memory + tools                │ │
│  │  • Format with citations                                     │ │
│  │  • Generate follow-up suggestions                            │ │
│  │  • Stream response to user                                   │ │
│  └──────────────────────────┬──────────────────────────────────┘ │
│                             │                                      │
│  ┌──────────────────────────▼──────────────────────────────────┐ │
│  │         Memory Update Node                                   │ │
│  │  • Store conversation turn                                   │ │
│  │  • Update short-term memory                                  │ │
│  │  • Optionally summarize & store in long-term                 │ │
│  └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────┘
```

---

## Detailed Component Design

### 1. LangGraph State Schema

```python
from typing import TypedDict, Annotated, Sequence, Optional
from langchain_core.messages import BaseMessage
from operator import add

class AgentState(TypedDict):
    """State schema for the conversational agent"""

    # Core conversation
    messages: Annotated[Sequence[BaseMessage], add]  # Chat history
    user_query: str  # Current user question

    # Memory layers
    digest_context: dict  # Layer 1: Today's digest articles
    short_term_memory: list[dict]  # Layer 2: Recent conversation context
    long_term_context: list[dict]  # Layer 3: Retrieved from vector DB

    # User context
    user_id: str
    session_id: str
    user_preferences: dict  # Subscribed companies, interests

    # Tool results
    rag_results: Optional[list[dict]]  # RAG search results
    web_search_results: Optional[list[dict]]  # Web search results
    extracted_links: Optional[list[dict]]  # Embedded URL content

    # Response generation
    synthesized_response: Optional[str]
    citations: Optional[list[dict]]
    follow_up_questions: Optional[list[str]]

    # Metadata
    token_count: int
    tool_calls_made: list[str]
    error: Optional[str]
```

---

### 2. Memory Layer Implementation

#### Layer 1: Digest Context Memory

**Purpose**: Provides immediate context about today's digest articles that the user received.

**Implementation**:
```python
class DigestContextMemory:
    """
    Pre-loaded when user clicks "Ask AI" from email.
    Contains structured information about today's digest.
    """

    def __init__(self, user_id: str, digest_date: date):
        self.user_id = user_id
        self.digest_date = digest_date
        self.articles = []

    def load_digest_context(self) -> dict:
        """
        Load today's digest articles from database.
        This is called once at chat session initialization.
        """
        # Query database for today's digest
        digest = db.query(Digest).filter(
            Digest.user_id == self.user_id,
            Digest.date == self.digest_date
        ).first()

        if not digest:
            return {"articles": [], "summary": "No digest found for today"}

        # Load all articles in the digest
        articles = []
        for item in digest.items:
            article = item.article
            articles.append({
                "id": str(article.id),
                "title": article.title,
                "summary": article.summary,
                "source": article.source_name,
                "url": article.url,
                "published_at": article.published_at.isoformat(),
                "companies": article.companies,
                "categories": article.categories,
                "impact_score": article.impact_score
            })

        return {
            "digest_date": self.digest_date.isoformat(),
            "article_count": len(articles),
            "articles": articles,
            "companies_covered": list(set(
                company
                for article in articles
                for company in article.get("companies", [])
            )),
            "top_topics": self._extract_top_topics(articles)
        }

    def _extract_top_topics(self, articles: list[dict]) -> list[str]:
        """Extract most common topics from articles"""
        from collections import Counter
        all_categories = [
            cat
            for article in articles
            for cat in article.get("categories", [])
        ]
        return [topic for topic, _ in Counter(all_categories).most_common(5)]

    def format_for_llm(self, digest_context: dict) -> str:
        """Format digest context for LLM prompt"""
        articles = digest_context.get("articles", [])

        context = f"""# Today's Digest Context ({digest_context['digest_date']})

You are helping a user explore their personalized daily digest containing {len(articles)} articles.

**Companies covered**: {', '.join(digest_context.get('companies_covered', []))}
**Top topics**: {', '.join(digest_context.get('top_topics', []))}

## Articles in Today's Digest:

"""

        for idx, article in enumerate(articles, 1):
            context += f"""
### [{idx}] {article['title']}
- **Source**: {article['source']}
- **Published**: {article['published_at']}
- **Companies**: {', '.join(article.get('companies', []))}
- **Summary**: {article['summary']}
- **URL**: {article['url']}

"""

        return context
```

**Usage Pattern**:
- Loaded once when chat session starts (user clicks "Ask AI" from email)
- Stays in state for entire conversation
- Provides immediate answers about "What was in my digest today?"
- Low latency - no vector search needed

---

#### Layer 2: Short-Term Memory (Conversation Context)

**Purpose**: Maintains recent conversation flow and working memory.

**Implementation**:
```python
from langchain.memory import ConversationBufferWindowMemory

class ShortTermMemory:
    """
    Manages recent conversation history.
    Uses LangChain's built-in memory management.
    """

    def __init__(self, session_id: str, window_size: int = 10):
        self.session_id = session_id
        self.memory = ConversationBufferWindowMemory(
            k=window_size,  # Keep last N turns
            return_messages=True,
            memory_key="chat_history"
        )

        # Also track tool calls for context
        self.recent_tool_calls = []

    def add_turn(
        self,
        user_message: str,
        assistant_message: str,
        tool_calls: Optional[list[dict]] = None
    ):
        """Add a conversation turn to short-term memory"""
        self.memory.save_context(
            {"input": user_message},
            {"output": assistant_message}
        )

        if tool_calls:
            self.recent_tool_calls.extend(tool_calls)
            # Keep only last 20 tool calls
            self.recent_tool_calls = self.recent_tool_calls[-20:]

    def get_context(self) -> dict:
        """Get recent conversation context"""
        return {
            "recent_messages": self.memory.load_memory_variables({}),
            "recent_tools": self.recent_tool_calls[-5:]  # Last 5 tool calls
        }

    def format_for_llm(self) -> str:
        """Format short-term memory for LLM"""
        context = self.get_context()

        formatted = "# Recent Conversation:\n\n"

        messages = context["recent_messages"].get("chat_history", [])
        for msg in messages:
            role = "User" if msg.type == "human" else "Assistant"
            formatted += f"**{role}**: {msg.content}\n\n"

        if context["recent_tools"]:
            formatted += "\n# Recent Tool Calls:\n\n"
            for tool in context["recent_tools"]:
                formatted += f"- {tool['name']}: {tool.get('summary', 'executed')}\n"

        return formatted
```

**Usage Pattern**:
- Updated after every conversation turn
- In-memory during session
- Persisted to database for session resumption
- Used for maintaining conversation coherence

---

#### Layer 3: Long-Term Memory (User History RAG)

**Purpose**: Vector-based retrieval of relevant content from user's entire article history.

**Implementation**:
```python
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

class LongTermMemory:
    """
    Vector-based retrieval over user's complete article history.
    Includes past digests and conversation summaries.
    """

    def __init__(self, user_id: str):
        self.user_id = user_id

        # Initialize embeddings (free tier)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # Initialize vector store (ChromaDB for dev)
        self.vector_store = Chroma(
            collection_name=f"user_{user_id}_articles",
            embedding_function=self.embeddings,
            persist_directory=f"./data/chroma/user_{user_id}"
        )

    async def semantic_search(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[dict] = None
    ) -> list[dict]:
        """
        Perform semantic search over user's article history.

        Args:
            query: User's question or search query
            top_k: Number of results to return
            filters: Optional metadata filters (date range, companies, etc.)

        Returns:
            List of relevant articles with metadata
        """
        # Perform vector search
        results = self.vector_store.similarity_search_with_score(
            query=query,
            k=top_k * 2,  # Get more candidates for filtering
            filter=filters
        )

        # Format results
        formatted_results = []
        for doc, score in results[:top_k]:
            formatted_results.append({
                "article_id": doc.metadata.get("article_id"),
                "title": doc.metadata.get("title"),
                "summary": doc.page_content,
                "source": doc.metadata.get("source"),
                "url": doc.metadata.get("url"),
                "published_at": doc.metadata.get("published_at"),
                "companies": doc.metadata.get("companies", []),
                "relevance_score": float(score),
                "digest_date": doc.metadata.get("digest_date")
            })

        return formatted_results

    async def hybrid_search(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[dict] = None
    ) -> list[dict]:
        """
        Combine semantic search with keyword-based search.
        Better results than pure vector search.
        """
        # Semantic search
        semantic_results = await self.semantic_search(query, top_k, filters)

        # Keyword search (BM25 on PostgreSQL)
        keyword_results = await self._keyword_search(query, top_k, filters)

        # Merge using Reciprocal Rank Fusion
        merged = self._reciprocal_rank_fusion(
            semantic_results,
            keyword_results
        )

        return merged[:top_k]

    async def _keyword_search(
        self,
        query: str,
        top_k: int,
        filters: Optional[dict]
    ) -> list[dict]:
        """PostgreSQL full-text search"""
        from sqlalchemy import func

        # Build query
        search_query = db.query(Article).filter(
            Article.user_id == self.user_id,
            func.to_tsvector('english', Article.title + ' ' + Article.summary)
            .match(query)
        )

        # Apply filters
        if filters:
            if "companies" in filters:
                search_query = search_query.filter(
                    Article.companies.overlap(filters["companies"])
                )
            if "date_from" in filters:
                search_query = search_query.filter(
                    Article.published_at >= filters["date_from"]
                )

        # Execute
        results = search_query.order_by(
            func.ts_rank(
                func.to_tsvector('english', Article.title + ' ' + Article.summary),
                func.plainto_tsquery('english', query)
            ).desc()
        ).limit(top_k).all()

        return [self._article_to_dict(article) for article in results]

    def _reciprocal_rank_fusion(
        self,
        list1: list[dict],
        list2: list[dict],
        k: int = 60
    ) -> list[dict]:
        """
        Reciprocal Rank Fusion algorithm for combining search results.
        RRF score = sum(1 / (k + rank))
        """
        from collections import defaultdict

        scores = defaultdict(float)
        article_map = {}

        # Score from semantic search
        for rank, article in enumerate(list1, 1):
            article_id = article["article_id"]
            scores[article_id] += 1 / (k + rank)
            article_map[article_id] = article

        # Score from keyword search
        for rank, article in enumerate(list2, 1):
            article_id = article["article_id"]
            scores[article_id] += 1 / (k + rank)
            if article_id not in article_map:
                article_map[article_id] = article

        # Sort by combined score
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)

        return [article_map[aid] for aid in sorted_ids]

    def format_for_llm(self, results: list[dict]) -> str:
        """Format long-term memory retrieval results for LLM"""
        if not results:
            return "# Relevant Historical Context:\n\nNo relevant articles found in your history.\n"

        context = f"# Relevant Historical Context:\n\n"
        context += f"Found {len(results)} relevant articles from your past digests:\n\n"

        for idx, article in enumerate(results, 1):
            context += f"""
### [{idx}] {article['title']}
- **Source**: {article['source']}
- **Published**: {article['published_at']}
- **From Digest**: {article.get('digest_date', 'N/A')}
- **Relevance**: {article['relevance_score']:.2f}
- **Summary**: {article['summary']}
- **URL**: {article['url']}

"""

        return context

    async def store_conversation_summary(
        self,
        session_id: str,
        summary: str,
        key_topics: list[str],
        articles_discussed: list[str]
    ):
        """
        Store a summary of the conversation for future retrieval.
        Called at end of chat session.
        """
        from datetime import datetime

        # Create document for vector store
        metadata = {
            "type": "conversation_summary",
            "session_id": session_id,
            "user_id": self.user_id,
            "timestamp": datetime.now().isoformat(),
            "key_topics": key_topics,
            "articles_discussed": articles_discussed
        }

        # Add to vector store
        self.vector_store.add_texts(
            texts=[summary],
            metadatas=[metadata]
        )

        # Also store in PostgreSQL
        db.add(ConversationSummary(
            session_id=session_id,
            user_id=self.user_id,
            summary=summary,
            key_topics=key_topics,
            articles_discussed=articles_discussed,
            created_at=datetime.now()
        ))
        db.commit()
```

**Usage Pattern**:
- Queried dynamically based on user's question
- Runs in parallel with web search (async)
- Results cached per query to avoid duplicate searches
- Updated nightly with new digest articles

---

### 3. LangGraph Agent Implementation

```python
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage

class ConversationalAgent:
    """
    Main LangGraph agent orchestrating the 3-layer memory system.
    """

    def __init__(
        self,
        user_id: str,
        session_id: str,
        digest_date: date,
        llm_provider: str = "ollama"
    ):
        self.user_id = user_id
        self.session_id = session_id

        # Initialize memory layers
        self.digest_memory = DigestContextMemory(user_id, digest_date)
        self.short_term_memory = ShortTermMemory(session_id)
        self.long_term_memory = LongTermMemory(user_id)

        # Initialize LLM
        if llm_provider == "ollama":
            from langchain_community.llms import Ollama
            self.llm = Ollama(model="llama3.2:3b")
        else:
            from langchain_anthropic import ChatAnthropic
            self.llm = ChatAnthropic(model="claude-sonnet-4.5")

        # Initialize tools
        self.tools = self._initialize_tools()

        # Build LangGraph
        self.graph = self._build_graph()

    def _initialize_tools(self):
        """Initialize all tools available to the agent"""
        from langchain.tools import Tool

        tools = [
            Tool(
                name="rag_search",
                description="Search user's article history for relevant information. Use when user asks about past articles or topics they've received.",
                func=self._rag_search_tool
            ),
            Tool(
                name="web_search",
                description="Search the web for real-time information. Use when information is not in digest or history, or when user asks about very recent events.",
                func=self._web_search_tool
            ),
            Tool(
                name="extract_link_content",
                description="Extract and summarize content from a URL. Use when user asks about a specific link or wants more details from an article.",
                func=self._extract_link_tool
            ),
            Tool(
                name="find_related_articles",
                description="Find articles similar to a given article. Use when user wants to explore related content.",
                func=self._find_related_articles_tool
            )
        ]

        return tools

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine"""
        workflow = StateGraph(AgentState)

        # Define nodes
        workflow.add_node("initialize", self._initialize_node)
        workflow.add_node("understand_query", self._understand_query_node)
        workflow.add_node("retrieve_memory", self._retrieve_memory_node)
        workflow.add_node("select_tools", self._select_tools_node)
        workflow.add_node("execute_tools", self._execute_tools_node)
        workflow.add_node("generate_response", self._generate_response_node)
        workflow.add_node("update_memory", self._update_memory_node)

        # Define edges
        workflow.set_entry_point("initialize")
        workflow.add_edge("initialize", "understand_query")
        workflow.add_edge("understand_query", "retrieve_memory")
        workflow.add_edge("retrieve_memory", "select_tools")

        # Conditional: Execute tools or skip to response generation
        workflow.add_conditional_edges(
            "select_tools",
            self._should_use_tools,
            {
                "use_tools": "execute_tools",
                "skip_tools": "generate_response"
            }
        )

        workflow.add_edge("execute_tools", "generate_response")
        workflow.add_edge("generate_response", "update_memory")
        workflow.add_edge("update_memory", END)

        return workflow.compile()

    def _initialize_node(self, state: AgentState) -> AgentState:
        """Initialize conversation state"""
        # Load digest context (Layer 1) - only done once per session
        if not state.get("digest_context"):
            state["digest_context"] = self.digest_memory.load_digest_context()

        # Load user preferences
        if not state.get("user_preferences"):
            user = db.query(User).filter(User.id == self.user_id).first()
            state["user_preferences"] = {
                "companies": user.subscribed_companies,
                "industries": user.subscribed_industries,
                "digest_frequency": user.digest_frequency
            }

        return state

    def _understand_query_node(self, state: AgentState) -> AgentState:
        """Analyze user query for intent and entities"""
        query = state["user_query"]

        # Use LLM to understand query
        analysis_prompt = f"""Analyze this user question:

Question: {query}

Extract:
1. Intent: What is the user trying to do? (Options: get_info, explore_topic, compare, explain, find_related)
2. Entities: Companies, technologies, people mentioned
3. Time context: Is this about recent events, historical information, or no time constraint?
4. Scope: Does this require information from (digest, history, web, multiple)?

Return JSON:
{{
  "intent": "...",
  "entities": {{
    "companies": [],
    "technologies": [],
    "people": []
  }},
  "time_context": "...",
  "scope": []
}}
"""

        # Get analysis (implement actual LLM call)
        analysis = self._call_llm_for_json(analysis_prompt)

        state["query_analysis"] = analysis
        return state

    def _retrieve_memory_node(self, state: AgentState) -> AgentState:
        """Retrieve from all 3 memory layers"""
        query = state["user_query"]
        analysis = state.get("query_analysis", {})

        # Layer 1: Digest context (already loaded in state)
        # Already available in state["digest_context"]

        # Layer 2: Short-term memory (conversation history)
        state["short_term_memory"] = self.short_term_memory.get_context()

        # Layer 3: Long-term memory (semantic search)
        # Only search if query requires historical context
        if "history" in analysis.get("scope", []) or analysis.get("intent") == "explore_topic":
            # Build filters from analysis
            filters = {}
            if analysis.get("entities", {}).get("companies"):
                filters["companies"] = analysis["entities"]["companies"]

            # Perform hybrid search
            long_term_results = await self.long_term_memory.hybrid_search(
                query=query,
                top_k=5,
                filters=filters
            )

            state["long_term_context"] = long_term_results
        else:
            state["long_term_context"] = []

        return state

    def _select_tools_node(self, state: AgentState) -> AgentState:
        """Decide which tools to use based on query analysis"""
        analysis = state.get("query_analysis", {})
        scope = analysis.get("scope", [])

        tools_to_use = []

        # Determine which tools are needed
        if "web" in scope:
            tools_to_use.append("web_search")

        if analysis.get("intent") == "find_related":
            tools_to_use.append("find_related_articles")

        # Check if user mentioned a specific URL
        if "http" in state["user_query"]:
            tools_to_use.append("extract_link_content")

        state["tools_selected"] = tools_to_use
        return state

    def _should_use_tools(self, state: AgentState) -> str:
        """Conditional edge: determine if tools are needed"""
        if state.get("tools_selected"):
            return "use_tools"
        return "skip_tools"

    async def _execute_tools_node(self, state: AgentState) -> AgentState:
        """Execute selected tools in parallel"""
        tools_to_use = state.get("tools_selected", [])

        # Execute tools concurrently
        import asyncio
        results = await asyncio.gather(*[
            self._execute_tool(tool_name, state)
            for tool_name in tools_to_use
        ])

        # Store results
        for tool_name, result in zip(tools_to_use, results):
            state[f"{tool_name}_results"] = result

        state["tool_calls_made"] = tools_to_use
        return state

    async def _generate_response_node(self, state: AgentState) -> AgentState:
        """Generate final response using all context"""
        # Assemble full context from all layers + tool results
        full_context = self._assemble_context(state)

        # Build prompt
        system_prompt = """You are an AI assistant helping a professional explore their daily industry digest.

You have access to:
1. Today's digest articles (what the user received this morning)
2. Recent conversation history (what you've been discussing)
3. User's complete article history (past digests and articles)
4. Real-time web search (when needed)

Your job:
- Answer questions accurately using available context
- Always cite sources using [Source Name] format
- Be concise but thorough
- If information is uncertain or missing, say so
- Suggest related articles or topics when relevant
- Maintain conversation flow by referencing previous discussion

Formatting:
- Use markdown for readability
- Include clickable links
- Highlight key facts
- Provide citations at the end
"""

        user_prompt = f"""
{full_context}

User Question: {state['user_query']}

Provide a helpful, accurate response with citations.
"""

        # Generate response (with streaming)
        response_text = ""
        citations = []

        # Stream response
        async for chunk in self.llm.astream(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        ):
            response_text += chunk
            # Yield chunk for streaming to user
            yield {"type": "chunk", "content": chunk}

        # Extract citations
        citations = self._extract_citations(response_text, state)

        # Generate follow-up questions
        follow_ups = self._generate_follow_ups(state)

        state["synthesized_response"] = response_text
        state["citations"] = citations
        state["follow_up_questions"] = follow_ups

        return state

    def _update_memory_node(self, state: AgentState) -> AgentState:
        """Update short-term memory with this conversation turn"""
        self.short_term_memory.add_turn(
            user_message=state["user_query"],
            assistant_message=state["synthesized_response"],
            tool_calls=[
                {"name": tool, "result": "success"}
                for tool in state.get("tool_calls_made", [])
            ]
        )

        # Persist to database
        self._save_conversation_turn(state)

        return state

    def _assemble_context(self, state: AgentState) -> str:
        """Assemble all context layers into a single prompt"""
        context_parts = []

        # Layer 1: Digest context
        if state.get("digest_context"):
            context_parts.append(
                self.digest_memory.format_for_llm(state["digest_context"])
            )

        # Layer 2: Short-term memory
        if state.get("short_term_memory"):
            context_parts.append(
                self.short_term_memory.format_for_llm()
            )

        # Layer 3: Long-term context
        if state.get("long_term_context"):
            context_parts.append(
                self.long_term_memory.format_for_llm(state["long_term_context"])
            )

        # Tool results
        if state.get("web_search_results"):
            context_parts.append(
                self._format_web_search_results(state["web_search_results"])
            )

        if state.get("extract_link_content_results"):
            context_parts.append(
                self._format_link_content(state["extract_link_content_results"])
            )

        return "\n\n---\n\n".join(context_parts)

    # Tool implementations
    async def _rag_search_tool(self, query: str) -> list[dict]:
        """RAG search tool implementation"""
        return await self.long_term_memory.hybrid_search(query, top_k=5)

    async def _web_search_tool(self, query: str) -> list[dict]:
        """Web search tool implementation"""
        # Implement Brave Search API or SerpAPI
        pass

    async def _extract_link_tool(self, url: str) -> dict:
        """Extract content from URL"""
        # Implement with Playwright + BeautifulSoup
        pass

    async def _find_related_articles_tool(self, article_id: str) -> list[dict]:
        """Find similar articles"""
        # Vector similarity search
        pass
```

---

### 4. Tool Implementations

#### Web Search Tool

```python
from langchain.tools import Tool
import httpx

class WebSearchTool:
    """
    Real-time web search capability using Brave Search API.
    Free tier: 2000 queries/month
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.search.brave.com/res/v1/web/search"

    async def search(
        self,
        query: str,
        count: int = 5,
        freshness: str = "pd"  # past day
    ) -> list[dict]:
        """
        Perform web search and return results.

        Args:
            query: Search query
            count: Number of results
            freshness: Time filter (pd=past day, pw=past week, pm=past month)
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.base_url,
                headers={
                    "Accept": "application/json",
                    "X-Subscription-Token": self.api_key
                },
                params={
                    "q": query,
                    "count": count,
                    "freshness": freshness
                }
            )

            if response.status_code != 200:
                return []

            data = response.json()

            results = []
            for item in data.get("web", {}).get("results", []):
                results.append({
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "description": item.get("description"),
                    "published": item.get("age"),
                    "source": "web_search"
                })

            return results
```

#### Link Extraction Tool

```python
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

class LinkExtractionTool:
    """
    Extract and summarize content from URLs.
    Handles JavaScript-rendered pages using Playwright.
    """

    async def extract(self, url: str) -> dict:
        """
        Extract content from URL and generate summary.

        Returns:
            {
                "url": str,
                "title": str,
                "content": str,
                "summary": str,
                "images": list[str],
                "links": list[str]
            }
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            try:
                await page.goto(url, wait_until="networkidle")
                content = await page.content()
                await browser.close()
            except Exception as e:
                await browser.close()
                return {"error": f"Failed to load page: {str(e)}"}

        # Parse with BeautifulSoup
        soup = BeautifulSoup(content, "html.parser")

        # Extract text content
        for script in soup(["script", "style"]):
            script.decompose()

        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        text = '\n'.join(line for line in lines if line)

        # Extract title
        title = soup.find("title")
        title = title.text if title else "No title"

        # Extract images
        images = [img.get("src") for img in soup.find_all("img") if img.get("src")]

        # Extract links
        links = [a.get("href") for a in soup.find_all("a") if a.get("href")]

        # Generate summary using LLM
        summary = await self._summarize_content(text[:5000])  # Limit to first 5000 chars

        return {
            "url": url,
            "title": title,
            "content": text[:2000],  # Return first 2000 chars
            "summary": summary,
            "images": images[:5],
            "links": links[:10]
        }

    async def _summarize_content(self, content: str) -> str:
        """Generate summary of extracted content"""
        # Use LLM to summarize
        prompt = f"""Summarize this web page content in 2-3 sentences:

{content}

Summary:"""

        # Call LLM (implement actual call)
        summary = await llm.generate(prompt)
        return summary
```

---

### 5. Database Schema Extensions

```sql
-- Chat sessions
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    digest_id UUID REFERENCES digests(id) ON DELETE SET NULL,  -- Link to digest if started from email
    started_at TIMESTAMP DEFAULT NOW(),
    last_active_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'active',  -- active, ended
    metadata JSONB  -- Store any session-specific data
);

CREATE INDEX idx_chat_sessions_user ON chat_sessions(user_id, started_at DESC);

-- Chat messages
CREATE TABLE chat_messages (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,  -- user, assistant, system
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),

    -- Tool usage tracking
    tools_used TEXT[],  -- ['web_search', 'rag_search']

    -- Context tracking
    articles_referenced UUID[],  -- Article IDs mentioned/used

    -- Metadata
    token_count INTEGER,
    latency_ms INTEGER,
    metadata JSONB
);

CREATE INDEX idx_chat_messages_session ON chat_messages(session_id, created_at);

-- Conversation summaries (for long-term memory)
CREATE TABLE conversation_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    summary TEXT NOT NULL,
    key_topics TEXT[],
    articles_discussed UUID[],
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_conv_summaries_user ON conversation_summaries(user_id, created_at DESC);

-- Vector embeddings for conversations (if storing in PostgreSQL)
CREATE TABLE conversation_embeddings (
    id BIGSERIAL PRIMARY KEY,
    summary_id UUID REFERENCES conversation_summaries(id) ON DELETE CASCADE,
    embedding VECTOR(384),  -- MiniLM-L6-v2 produces 384-dim vectors
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_conv_embeddings_vector ON conversation_embeddings
USING ivfflat (embedding vector_cosine_ops);
```

---

### 6. API Endpoints

```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from api.utils.auth import get_current_user

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

@router.post("/sessions")
async def create_chat_session(
    digest_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new chat session.

    If digest_id is provided, pre-load that digest's context.
    """
    session = ChatSession(
        user_id=current_user.id,
        digest_id=digest_id,
        started_at=datetime.now()
    )
    db.add(session)
    db.commit()

    return {
        "session_id": str(session.id),
        "websocket_url": f"ws://localhost:8000/api/v1/chat/ws/{session.id}"
    }

@router.websocket("/ws/{session_id}")
async def chat_websocket(
    websocket: WebSocket,
    session_id: str,
    # Note: WebSocket auth is more complex, implement token in query params
):
    """
    WebSocket endpoint for streaming chat.

    Client sends: {"message": "user question"}
    Server streams: {"type": "chunk", "content": "..."} or
                    {"type": "complete", "citations": [...], "follow_ups": [...]}
    """
    await websocket.accept()

    # Verify session exists and belongs to user
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        await websocket.close(code=4004, reason="Session not found")
        return

    # Initialize agent
    agent = ConversationalAgent(
        user_id=str(session.user_id),
        session_id=session_id,
        digest_date=session.digest.date if session.digest else date.today(),
        llm_provider=settings.LLM_PROVIDER
    )

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            user_message = data.get("message")

            if not user_message:
                continue

            # Process through agent (streaming)
            state = {
                "user_query": user_message,
                "user_id": str(session.user_id),
                "session_id": session_id,
                "messages": [],
                "token_count": 0,
                "tool_calls_made": []
            }

            # Stream response chunks
            async for chunk in agent.process_query(state):
                if chunk["type"] == "chunk":
                    await websocket.send_json({
                        "type": "chunk",
                        "content": chunk["content"]
                    })
                elif chunk["type"] == "complete":
                    await websocket.send_json({
                        "type": "complete",
                        "citations": chunk["citations"],
                        "follow_ups": chunk["follow_ups"]
                    })

            # Update session last_active
            session.last_active_at = datetime.now()
            db.commit()

    except WebSocketDisconnect:
        # Handle disconnect
        pass

@router.get("/sessions/{session_id}/messages")
async def get_chat_history(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get conversation history for a session"""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at).all()

    return {
        "session_id": session_id,
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
                "tools_used": msg.tools_used
            }
            for msg in messages
        ]
    }

@router.delete("/sessions/{session_id}")
async def end_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """End a chat session and generate summary for long-term memory"""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Generate conversation summary
    summary = await generate_conversation_summary(session_id)

    # Store in long-term memory
    long_term_memory = LongTermMemory(str(current_user.id))
    await long_term_memory.store_conversation_summary(
        session_id=session_id,
        summary=summary["summary"],
        key_topics=summary["key_topics"],
        articles_discussed=summary["articles_discussed"]
    )

    # Mark session as ended
    session.status = "ended"
    db.commit()

    return {"status": "success", "summary": summary}
```

---

### 7. Frontend Integration

#### React Chat Component

```typescript
// frontend/src/components/Chat.tsx

import { useState, useEffect, useRef } from 'react'
import { useWebSocket } from '@/hooks/useWebSocket'

interface Message {
  role: 'user' | 'assistant'
  content: string
  citations?: Citation[]
  followUps?: string[]
}

interface Citation {
  title: string
  url: string
  source: string
}

export function Chat({ sessionId }: { sessionId: string }) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const { sendMessage, lastMessage } = useWebSocket(
    `ws://localhost:8000/api/v1/chat/ws/${sessionId}`
  )

  // Handle incoming WebSocket messages
  useEffect(() => {
    if (!lastMessage) return

    const data = JSON.parse(lastMessage.data)

    if (data.type === 'chunk') {
      // Append chunk to last assistant message
      setMessages(prev => {
        const last = prev[prev.length - 1]
        if (last && last.role === 'assistant') {
          return [
            ...prev.slice(0, -1),
            { ...last, content: last.content + data.content }
          ]
        } else {
          // Start new assistant message
          return [...prev, { role: 'assistant', content: data.content }]
        }
      })
    } else if (data.type === 'complete') {
      // Add citations and follow-ups
      setMessages(prev => {
        const last = prev[prev.length - 1]
        return [
          ...prev.slice(0, -1),
          {
            ...last,
            citations: data.citations,
            followUps: data.follow_ups
          }
        ]
      })
      setIsStreaming(false)
    }
  }, [lastMessage])

  const handleSend = () => {
    if (!input.trim()) return

    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: input }])

    // Send via WebSocket
    sendMessage(JSON.stringify({ message: input }))

    setInput('')
    setIsStreaming(true)
  }

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="flex flex-col h-screen">
      {/* Chat messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-3xl p-4 rounded-lg ${
                msg.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <div className="prose prose-sm">
                {msg.content}
              </div>

              {/* Citations */}
              {msg.citations && msg.citations.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-300">
                  <p className="text-xs font-semibold mb-2">Sources:</p>
                  {msg.citations.map((cite, i) => (
                    <div key={i} className="text-xs mb-1">
                      <a
                        href={cite.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline"
                      >
                        [{i + 1}] {cite.title}
                      </a>
                      <span className="text-gray-500 ml-2">({cite.source})</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Follow-up questions */}
              {msg.followUps && msg.followUps.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-300">
                  <p className="text-xs font-semibold mb-2">You might also ask:</p>
                  {msg.followUps.map((q, i) => (
                    <button
                      key={i}
                      onClick={() => setInput(q)}
                      className="block text-xs text-blue-600 hover:underline mb-1"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {isStreaming && (
          <div className="flex justify-start">
            <div className="bg-gray-100 p-4 rounded-lg">
              <div className="animate-pulse flex space-x-2">
                <div className="h-2 w-2 bg-gray-400 rounded-full"></div>
                <div className="h-2 w-2 bg-gray-400 rounded-full"></div>
                <div className="h-2 w-2 bg-gray-400 rounded-full"></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="border-t p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask about your digest..."
            className="flex-1 p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isStreaming}
          />
          <button
            onClick={handleSend}
            disabled={isStreaming || !input.trim()}
            className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  )
}
```

---

### 8. Cost Optimization Strategies

#### Development (Free Tier)
- **LLM**: Ollama (llama3.2:3b) - 100% free, runs locally
- **Embeddings**: sentence-transformers - Free, runs locally
- **Vector DB**: ChromaDB - Free, local persistence
- **Web Search**: Brave Search API - 2000 free queries/month

#### Production (Paid, but optimized)
- **LLM**: Claude Sonnet 4.5 with aggressive caching
  - Cache digest context per session (reuse for all queries)
  - Cache common questions/responses
  - Use prompt caching for system prompts
- **Embeddings**: OpenAI text-embedding-3-small ($0.02/1M tokens)
  - Embed only once per article
  - Cache embeddings forever
- **Vector DB**: Pinecone Starter ($70/month) or pgvector (free)
- **Web Search**: Brave Search Pro ($5/month for 20K queries)

#### Caching Strategy
```python
class ResponseCache:
    """Cache LLM responses for common queries"""

    def __init__(self):
        self.redis = Redis()

    async def get_cached_response(
        self,
        query: str,
        context_hash: str
    ) -> Optional[str]:
        """
        Check if we have a cached response for similar query.
        Use semantic similarity to find near-matches.
        """
        cache_key = f"llm_response:{context_hash}:{hash(query)}"
        cached = self.redis.get(cache_key)

        if cached:
            return cached.decode()

        # Check for semantically similar queries
        query_embedding = embed(query)
        similar_queries = self.redis.zrangebyscore(
            f"query_embeddings:{context_hash}",
            min=0.9,  # 90% similarity threshold
            max=1.0
        )

        if similar_queries:
            # Return cached response for similar query
            return self.redis.get(similar_queries[0]).decode()

        return None

    async def cache_response(
        self,
        query: str,
        context_hash: str,
        response: str,
        ttl: int = 86400  # 24 hours
    ):
        """Cache LLM response"""
        cache_key = f"llm_response:{context_hash}:{hash(query)}"
        self.redis.setex(cache_key, ttl, response)

        # Store query embedding for similarity search
        query_embedding = embed(query)
        self.redis.zadd(
            f"query_embeddings:{context_hash}",
            {cache_key: cosine_similarity(query_embedding, query_embedding)}
        )
```

---

### 9. Testing Strategy

```python
# backend/tests/unit/test_conversational_agent.py

import pytest
from api.services.conversational_agent import ConversationalAgent
from datetime import date

@pytest.fixture
def mock_digest_context():
    return {
        "digest_date": "2025-10-24",
        "article_count": 5,
        "articles": [
            {
                "id": "article-1",
                "title": "OpenAI announces GPT-5",
                "summary": "OpenAI has released GPT-5...",
                "source": "OpenAI Blog",
                "url": "https://openai.com/blog/gpt-5",
                "companies": ["openai"],
                "categories": ["ai", "llm"]
            }
        ]
    }

@pytest.mark.asyncio
async def test_digest_memory_loads_correctly(mock_digest_context):
    """Test that digest context loads correctly"""
    agent = ConversationalAgent(
        user_id="test-user",
        session_id="test-session",
        digest_date=date.today(),
        llm_provider="ollama"
    )

    # Initialize state
    state = agent._initialize_node({})

    assert "digest_context" in state
    assert state["digest_context"]["article_count"] > 0

@pytest.mark.asyncio
async def test_query_understanding():
    """Test query analysis"""
    agent = ConversationalAgent(
        user_id="test-user",
        session_id="test-session",
        digest_date=date.today()
    )

    state = {
        "user_query": "What did OpenAI announce this week?"
    }

    state = agent._understand_query_node(state)

    assert "query_analysis" in state
    assert "openai" in state["query_analysis"]["entities"]["companies"]
    assert "recent" in state["query_analysis"]["time_context"]

@pytest.mark.asyncio
async def test_three_layer_memory_retrieval():
    """Test that all 3 memory layers are retrieved"""
    agent = ConversationalAgent(
        user_id="test-user",
        session_id="test-session",
        digest_date=date.today()
    )

    state = {
        "user_query": "Tell me more about OpenAI",
        "query_analysis": {
            "intent": "explore_topic",
            "scope": ["digest", "history"]
        }
    }

    state = await agent._retrieve_memory_node(state)

    # Layer 1: Digest context should be present
    assert "digest_context" in state

    # Layer 2: Short-term memory
    assert "short_term_memory" in state

    # Layer 3: Long-term context
    assert "long_term_context" in state

@pytest.mark.asyncio
async def test_web_search_tool():
    """Test web search tool"""
    tool = WebSearchTool(api_key="test-key")

    results = await tool.search("OpenAI GPT-5", count=3)

    assert len(results) <= 3
    assert all("title" in r and "url" in r for r in results)
```

---

### 10. Deployment Considerations

#### Docker Configuration

```yaml
# docker-compose.yml

services:
  chat-service:
    build: ./backend
    command: uvicorn api.main:app --host 0.0.0.0 --port 8000
    environment:
      - LLM_PROVIDER=ollama
      - OLLAMA_BASE_URL=http://ollama:11434
      - VECTOR_DB_PROVIDER=chroma
      - CHROMA_PERSIST_DIR=/data/chroma
    volumes:
      - ./data/chroma:/data/chroma
    depends_on:
      - postgres
      - redis
      - ollama

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ./data/ollama:/root/.ollama
    command: serve

  chroma:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000"
    volumes:
      - ./data/chroma:/chroma/chroma
```

---

## Implementation Roadmap

### Week 10 (Current: Week 1 in MVP Roadmap - Backend development phase)

**Day 1-2: Core Infrastructure**
- [ ] Install LangChain/LangGraph dependencies
- [ ] Set up ChromaDB for development
- [ ] Create database tables for chat sessions and messages
- [ ] Implement basic memory layer interfaces

**Day 3-4: Layer Implementation**
- [ ] Implement Layer 1 (Digest Context Memory)
- [ ] Implement Layer 2 (Short-Term Memory)
- [ ] Implement Layer 3 (Long-Term Memory with vector search)

**Day 5: Basic Agent**
- [ ] Build simple LangGraph agent (without tools first)
- [ ] Test 3-layer memory integration
- [ ] Create basic chat API endpoint

### Week 11

**Day 1-2: Tool Integration**
- [ ] Implement RAG search tool
- [ ] Implement web search tool (Brave API)
- [ ] Implement link extraction tool

**Day 3-4: WebSocket & Streaming**
- [ ] Implement WebSocket endpoint
- [ ] Add streaming response support
- [ ] Test end-to-end conversation flow

**Day 5: Frontend Integration**
- [ ] Build React chat component
- [ ] Integrate with WebSocket
- [ ] Add citation and follow-up UI

### Week 12 (Polish)

- [ ] Performance optimization
- [ ] Response caching
- [ ] Error handling
- [ ] Rate limiting
- [ ] User testing

---

## Summary

This architecture provides:

1. **3-Layer Memory System**:
   - **Digest Context**: Immediate access to today's digest
   - **Short-Term**: Conversation coherence
   - **Long-Term**: Historical knowledge via RAG

2. **Tool Integration**:
   - RAG search over article history
   - Real-time web search
   - Link extraction and embedding
   - Related article discovery

3. **Cost-Effective Development**:
   - 100% free during development (Ollama + ChromaDB)
   - Easy migration to production providers
   - Aggressive caching to minimize costs

4. **Production-Ready**:
   - Streaming responses
   - WebSocket support
   - Proper error handling
   - Database persistence

5. **Future-Proof**:
   - Modular design (swap LLMs easily)
   - Provider abstraction pattern
   - Extensible tool system

---

**Status**: Ready for Implementation
**Next Steps**: Begin Week 10 tasks (infrastructure setup)
**Questions**: Discuss LangChain vs LangGraph preference, confirm Brave Search API for web search
