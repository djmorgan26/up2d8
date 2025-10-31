"""
LangGraph Conversational AI Agent

State-based agent that orchestrates 3-layer memory system and tools
for intelligent conversation about articles and digests.
"""
from typing import TypedDict, List, Dict, Any, Optional, Annotated
from datetime import datetime
from pymongo.database import Database
import structlog

from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

from api.services.memory import DigestContextMemory, ShortTermMemory, LongTermMemory
from api.services.llm_provider import get_llm_client
from api.services.groq_client import get_groq_client
from api.services.web_search import get_web_search_service

logger = structlog.get_logger()


# Agent State Schema
class AgentState(TypedDict):
    """
    State schema for the conversational agent

    This state is passed through all nodes in the LangGraph
    """
    # User input
    user_message: str
    user_id: str
    session_id: str

    # Memory contexts
    digest_context: Optional[str]  # Layer 1: Today's articles
    conversation_history: List[Dict[str, str]]  # Layer 2: Recent messages
    long_term_context: Optional[str]  # Layer 3: Historical search results
    web_search_context: Optional[str]  # Web search results for real-time info

    # Agent reasoning
    query_type: Optional[str]  # Type of query (greeting, question, command)
    memory_layers_used: List[str]  # Which memory layers were accessed
    tools_used: List[str]  # Which tools were called
    needs_web_search: bool  # Whether query needs web search

    # Response
    response: Optional[str]
    sources: List[Dict[str, Any]]  # Citation sources
    confidence: Optional[float]  # Response confidence score

    # Metadata
    timestamp: str
    step_count: int


class ConversationalAgent:
    """
    LangGraph-based conversational agent with 3-layer memory

    Architecture:
    - State-based graph execution
    - 3-layer memory system (Digest, Short-Term, Long-Term)
    - Tool integration (search, web, etc.)
    - Intelligent routing based on query type
    """

    def __init__(
        self,
        user_id: str,
        session_id: str,
        db: Database,
        use_groq: bool = False
    ):
        """
        Initialize conversational agent

        Args:
            user_id: User ID
            session_id: Chat session ID
            db: Database session
            use_groq: Use Groq LLM instead of Ollama
        """
        self.user_id = user_id
        self.session_id = session_id
        self.db = db

        # Initialize LLM client
        if use_groq:
            self.llm = get_groq_client()
        else:
            self.llm = get_llm_client()

        # Initialize 3-layer memory system
        self.digest_memory = DigestContextMemory(user_id=user_id, db=db)
        self.short_term_memory = ShortTermMemory(session_id=session_id, user_id=user_id, db=db)
        self.long_term_memory = LongTermMemory(user_id=user_id, db=db)

        # Initialize web search service
        self.web_search = get_web_search_service()

        # Build LangGraph
        self.graph = self._build_graph()

        logger.info(
            "conversational_agent_initialized",
            user_id=user_id,
            session_id=session_id,
            llm_type="groq" if use_groq else "ollama"
        )

    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph state machine

        Graph Flow:
        1. Classify Query → Determine query type and needed memory layers
        2. Load Context → Fetch from appropriate memory layers
        3. Generate Response → Use LLM with context
        4. Format Output → Add citations and metadata
        """
        # Create state graph
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("classify_query", self._classify_query_node)
        workflow.add_node("load_digest_context", self._load_digest_context_node)
        workflow.add_node("load_conversation_history", self._load_conversation_history_node)
        workflow.add_node("load_long_term_context", self._load_long_term_context_node)
        workflow.add_node("load_web_search", self._load_web_search_node)
        workflow.add_node("generate_response", self._generate_response_node)
        workflow.add_node("format_output", self._format_output_node)

        # Define edges (workflow)
        workflow.set_entry_point("classify_query")

        # After classification, load appropriate memory layers
        workflow.add_edge("classify_query", "load_digest_context")
        workflow.add_edge("load_digest_context", "load_conversation_history")
        workflow.add_edge("load_conversation_history", "load_long_term_context")

        # Add web search if needed
        workflow.add_edge("load_long_term_context", "load_web_search")

        # Generate response with all context
        workflow.add_edge("load_web_search", "generate_response")
        workflow.add_edge("generate_response", "format_output")

        # End after formatting
        workflow.add_edge("format_output", END)

        return workflow.compile()

    async def chat(self, message: str) -> Dict[str, Any]:
        """
        Process a user message through the agent

        Args:
            message: User's message

        Returns:
            Agent response with metadata
        """
        # Initialize state
        initial_state: AgentState = {
            "user_message": message,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "digest_context": None,
            "conversation_history": [],
            "long_term_context": None,
            "web_search_context": None,
            "query_type": None,
            "memory_layers_used": [],
            "tools_used": [],
            "needs_web_search": False,
            "response": None,
            "sources": [],
            "confidence": None,
            "timestamp": datetime.utcnow().isoformat(),
            "step_count": 0,
        }

        # Execute graph
        final_state = await self.graph.ainvoke(initial_state)

        # Save to short-term memory
        self.short_term_memory.add_message(role="user", content=message)
        self.short_term_memory.add_message(
            role="assistant",
            content=final_state["response"],
            metadata={
                "sources": final_state["sources"],
                "memory_layers_used": final_state["memory_layers_used"],
                "confidence": final_state["confidence"],
            }
        )

        logger.info(
            "agent_chat_completed",
            user_id=self.user_id,
            session_id=self.session_id,
            query_type=final_state["query_type"],
            memory_layers=final_state["memory_layers_used"],
            steps=final_state["step_count"]
        )

        return {
            "response": final_state["response"],
            "sources": final_state["sources"],
            "confidence": final_state["confidence"],
            "memory_layers_used": final_state["memory_layers_used"],
            "query_type": final_state["query_type"],
        }

    # ============================================
    # Graph Nodes
    # ============================================

    def _classify_query_node(self, state: AgentState) -> AgentState:
        """
        Node 1: Classify the user's query

        Determines:
        - Query type (greeting, question, command, etc.)
        - Which memory layers are needed
        """
        message = state["user_message"].lower()

        # Detect if web search is needed (current events, breaking news, external info)
        needs_web_search = any(keyword in message for keyword in [
            "current", "breaking", "news", "happening now", "just announced",
            "price", "stock", "weather", "latest news", "update on", "search for"
        ])

        # Simple classification (can be enhanced with LLM)
        if any(greeting in message for greeting in ["hello", "hi", "hey", "greetings"]):
            query_type = "greeting"
            layers = ["digest_context"]  # Just show today's summary
        elif any(word in message for word in ["today", "latest", "new", "recent"]):
            query_type = "today_question"
            layers = ["digest_context", "conversation_history"]
        elif any(word in message for word in ["history", "past", "previous", "earlier"]):
            query_type = "historical_question"
            layers = ["conversation_history", "long_term"]
        elif "?" in message or any(word in message for word in ["what", "how", "why", "when", "where", "who"]):
            query_type = "question"
            layers = ["digest_context", "conversation_history", "long_term"]
        else:
            query_type = "general"
            layers = ["conversation_history"]

        state["query_type"] = query_type
        state["memory_layers_used"] = layers
        state["needs_web_search"] = needs_web_search
        state["step_count"] += 1

        logger.debug("query_classified", query_type=query_type, layers=layers, needs_web_search=needs_web_search)

        return state

    def _load_digest_context_node(self, state: AgentState) -> AgentState:
        """
        Node 2: Load Layer 1 (Digest Context)
        """
        if "digest_context" not in state["memory_layers_used"]:
            state["step_count"] += 1
            return state

        # Get today's context
        context_summary = self.digest_memory.get_context_summary()
        state["digest_context"] = context_summary
        state["step_count"] += 1

        logger.debug("digest_context_loaded", length=len(context_summary))

        return state

    def _load_conversation_history_node(self, state: AgentState) -> AgentState:
        """
        Node 3: Load Layer 2 (Short-Term Memory)
        """
        if "conversation_history" not in state["memory_layers_used"]:
            state["step_count"] += 1
            return state

        # Get recent conversation
        messages = self.short_term_memory.get_langchain_messages(limit=10)
        state["conversation_history"] = messages
        state["step_count"] += 1

        logger.debug("conversation_history_loaded", message_count=len(messages))

        return state

    async def _load_long_term_context_node(self, state: AgentState) -> AgentState:
        """
        Node 4: Load Layer 3 (Long-Term Memory)
        """
        if "long_term" not in state["memory_layers_used"]:
            state["step_count"] += 1
            return state

        # Search historical articles
        context_text = await self.long_term_memory.get_context_for_query(
            query=state["user_message"],
            num_articles=3
        )

        # Also get the actual results for citations
        results = await self.long_term_memory.search(
            query=state["user_message"],
            top_k=3
        )

        state["long_term_context"] = context_text
        state["sources"] = results
        state["step_count"] += 1

        logger.debug("long_term_context_loaded", sources=len(results))

        return state

    async def _load_web_search_node(self, state: AgentState) -> AgentState:
        """
        Node 4.5: Load Web Search Results

        Performs web search if needed for current/breaking info
        """
        if not state["needs_web_search"] or not self.web_search.is_available():
            state["step_count"] += 1
            return state

        # Perform web search
        context_text = await self.web_search.search_for_context(
            query=state["user_message"],
            num_results=3
        )

        state["web_search_context"] = context_text
        state["tools_used"].append("web_search")
        state["step_count"] += 1

        logger.debug("web_search_loaded", has_results=bool(context_text))

        return state

    async def _generate_response_node(self, state: AgentState) -> AgentState:
        """
        Node 5: Generate response using LLM with all context
        """
        # Build system message with all context
        system_parts = [
            "You are a helpful AI assistant for UP2D8, a personalized news digest platform.",
            "You help users understand and explore their curated articles.",
            ""
        ]

        # Add digest context (Layer 1)
        if state.get("digest_context"):
            system_parts.append("=== TODAY'S ARTICLES ===")
            system_parts.append(state["digest_context"])
            system_parts.append("")

        # Add long-term context (Layer 3)
        if state.get("long_term_context"):
            system_parts.append("=== RELEVANT HISTORICAL ARTICLES ===")
            system_parts.append(state["long_term_context"])
            system_parts.append("")

        # Add web search context (if available)
        if state.get("web_search_context"):
            system_parts.append("=== WEB SEARCH RESULTS (CURRENT INFORMATION) ===")
            system_parts.append(state["web_search_context"])
            system_parts.append("")

        system_parts.append("Please provide a helpful, concise response based on the above context.")
        system_parts.append("If you reference specific articles, mention their titles.")

        system_message = "\n".join(system_parts)

        # Build conversation history (Layer 2)
        messages = state.get("conversation_history", [])

        # Generate response
        try:
            if hasattr(self.llm, 'chat'):
                # Groq client
                full_messages = [
                    {"role": "system", "content": system_message}
                ]
                full_messages.extend(messages)
                full_messages.append({"role": "user", "content": state["user_message"]})

                response = await self.llm.chat(
                    messages=full_messages,
                    max_tokens=500,
                    temperature=0.7
                )
            else:
                # Ollama client
                response = await self.llm.generate(
                    prompt=state["user_message"],
                    system_message=system_message,
                    max_tokens=500
                )

            state["response"] = response
            state["confidence"] = 0.85  # Placeholder (can be enhanced)
            state["step_count"] += 1

            logger.debug("response_generated", length=len(response))

        except Exception as e:
            logger.error("response_generation_failed", error=str(e))
            state["response"] = "I apologize, but I encountered an error generating a response. Please try again."
            state["confidence"] = 0.0
            state["step_count"] += 1

        return state

    def _format_output_node(self, state: AgentState) -> AgentState:
        """
        Node 6: Format final output with citations
        """
        # Add citation markers if sources were used
        if state.get("sources"):
            response = state["response"]
            response += "\n\n📚 Sources:"
            for i, source in enumerate(state["sources"][:3], 1):
                response += f"\n{i}. {source['title']} (Relevance: {source['relevance_score']:.0%})"

            state["response"] = response

        state["step_count"] += 1

        logger.debug("output_formatted", final_length=len(state["response"]))

        return state

    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "llm_type": self.llm.__class__.__name__,
            "memory_stats": {
                "digest": self.digest_memory.get_stats(),
                "short_term": self.short_term_memory.get_stats(),
                "long_term": self.long_term_memory.get_stats(),
            }
        }


# Helper function
def get_conversational_agent(
    user_id: str,
    session_id: str,
    db: Database,
    use_groq: bool = False
) -> ConversationalAgent:
    """
    Get a conversational agent instance

    Args:
        user_id: User ID
        session_id: Chat session ID
        db: Database session
        use_groq: Use Groq LLM (recommended for production)

    Returns:
        ConversationalAgent instance
    """
    return ConversationalAgent(
        user_id=user_id,
        session_id=session_id,
        db=db,
        use_groq=use_groq
    )
