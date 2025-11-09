import logging

import google.generativeai as genai
from dependencies import get_gemini_api_key
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter()
logger = logging.getLogger(__name__)


class TopicSuggestRequest(BaseModel):
    interests: list[str] = []
    query: str = ""


class TopicSuggestResponse(BaseModel):
    suggestions: list[str]


@router.post(
    "/api/topics/suggest", status_code=status.HTTP_200_OK, response_model=TopicSuggestResponse
)
async def suggest_topics(request: TopicSuggestRequest):
    """
    Suggest relevant topics based on user interests or a search query.
    Uses Google Gemini to generate intelligent topic suggestions.
    """
    try:
        gemini_key = get_gemini_api_key()
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel("gemini-2.0-flash-exp")

        if request.query:
            # User provided a search query
            prompt = f"""Based on the search query "{request.query}", suggest 5-8 specific, relevant news topics
            that someone interested in this area would want to follow. Return ONLY the topic names as a
            comma-separated list, no explanations or numbering."""
        elif request.interests:
            # User has existing interests, suggest related topics
            interests_str = ", ".join(request.interests)
            prompt = f"""A user is interested in: {interests_str}.
            Suggest 5-8 additional related news topics they might want to follow.
            Return ONLY the topic names as a comma-separated list, no explanations or numbering."""
        else:
            # No input provided, suggest popular topics
            prompt = """Suggest 8 popular news topics that most people would be interested in following.
            Return ONLY the topic names as a comma-separated list, no explanations or numbering."""

        response = model.generate_content(prompt)
        suggestions_text = response.text.strip()

        # Parse comma-separated suggestions
        suggestions = [s.strip() for s in suggestions_text.split(",") if s.strip()]

        # Clean up any numbering or bullets that might have been included
        cleaned_suggestions = []
        for suggestion in suggestions:
            # Remove common prefixes like "1.", "- ", etc.
            cleaned = suggestion
            if ". " in cleaned:
                cleaned = cleaned.split(". ", 1)[-1]
            if cleaned.startswith("- "):
                cleaned = cleaned[2:]
            cleaned_suggestions.append(cleaned.strip())

        logger.info(
            f"Generated {len(cleaned_suggestions)} topic suggestions for query='{request.query}', interests={request.interests}"
        )

        return TopicSuggestResponse(suggestions=cleaned_suggestions[:8])

    except Exception as e:
        logger.error(f"Failed to generate topic suggestions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate topic suggestions",
        )
