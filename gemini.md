# Gemini Integration Documentation

This document outlines how the Up2D8 frontend integrates with the Gemini API through a backend service.

## Overview

The frontend application does not directly call the Gemini API. Instead, it communicates with a custom backend endpoint (`/api/chat`), which then securely handles the interaction with the Gemini API. This approach helps in managing API keys, implementing business logic, and potentially adding features like rate limiting or data pre-processing/post-processing.

## Frontend Interaction

The primary function for interacting with the Gemini-powered backend is `askGeminiWithSearch` located in `services/geminiService.ts`.

### `askGeminiWithSearch` Function

- **Purpose:** Sends a user's prompt to the backend's `/api/chat` endpoint and processes the response.
- **Request:**
  - **Method:** `POST`
  - **Endpoint:** `/api/chat`
  - **Body:** JSON object with a `prompt` field (string).
    ```json
    {
      "prompt": "Your question or message here."
    }
    ```
- **Response:**
  - **Success:** A JSON object conforming to the `GeminiResponse` interface.
    ```typescript
    interface GeminiResponse {
      text: string;
      sources: GroundingChunk[] | undefined;
    }
    ```
  - **Error:** A JSON object with a `message` field (string) describing the error.
    ```json
    {
      "message": "Error description."
    }
    ```

## Data Structures

### `GroundingChunk`

This interface represents a piece of information used for grounding the Gemini model's response, typically from web search results. It is defined in `types.ts`.

```typescript
export interface GroundingChunk {
  web: {
    uri: string;
    title: string;
  };
}
```

### `Message`

While not directly part of the API response, the `Message` interface (also in `types.ts`) is used internally by the frontend to represent chat messages, including those received from Gemini.

```typescript
export interface Message {
  id: string;
  role: Role; // e.g., 'user', 'model', 'error'
  text: string;
  sources?: GroundingChunk[];
}
```

## Backend Responsibilities (Conceptual)

The backend service (which is not part of this frontend repository but is called by it) is responsible for:

1.  Receiving the prompt from the frontend.
2.  Making secure, authenticated calls to the Gemini API.
3.  Handling any necessary pre-processing of the prompt or post-processing of the Gemini response.
4.  Extracting and formatting grounding sources if provided by the Gemini API.
5.  Returning the `text` and `sources` (if any) back to the frontend.
6.  Handling errors from the Gemini API and returning appropriate error messages to the frontend.


## Other Repositories

This project spans 3 repositories (frontend, backend, function app). When doing work that involves integrating with the other repos of this greater project, refer to these handoff documents first.

- **UP2D8-FUNCTION** The handoff document for this repo is `docs/handoff/function.md`.
- **UP2D8-FRONTEND** The handoff document for this repo is `docs/handoff/backend.md`.