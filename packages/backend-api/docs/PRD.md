# PRD: UP2D8 Backend API Service

**Version:** 1.0
**Status:** Definition

## 1. Objective

This document outlines the product requirements for the UP2D8 Backend API service. The primary objective of this service is to act as the central, secure hub for the entire UP2D8 application. It will manage all user data, handle real-time chat interactions by securely proxying requests to the Gemini API, and provide a stable interface for the frontend client and other backend services.

## 2. User Personas & Stories

-   **As a new user,** I want to be able to subscribe to the newsletter with my email and topics so that I can receive personalized digests.
-   **As a returning user,** I want to update my topic preferences and settings so that my digest remains relevant to my changing interests.
-   **As an application user,** I want to have a real-time conversation with an AI assistant to get up-to-date answers on any topic.
-   **As an application user,** I want my chat conversations to be saved so I can review them later.
-   **As an application user,** I want to provide feedback on the AI's responses so the system can be improved.
-   **As a frontend developer,** I need a clear, secure, and well-documented set of API endpoints to build the user interface against.

## 3. Functional Requirements

The API must expose the following RESTful endpoints.

### 3.1. User Management

-   **Endpoint:** `POST /api/users`
    -   **Description:** Creates a new user record or updates an existing one (upsert). Used for initial subscription.
    -   **Request Body:** `{ "email": "string", "topics": ["string"] }`
    -   **Success Response (200):** `{ "message": "Subscription confirmed.", "user_id": "string" }`

-   **Endpoint:** `PUT /api/users/{user_id}`
    -   **Description:** Updates a user's topics and preferences.
    -   **Request Body:** `{ "topics": ["string"], "preferences": { "newsletter_format": "concise|detailed" } }`
    -   **Success Response (200):** `{ "message": "Preferences updated." }`

### 3.2. Chat Interaction

-   **Endpoint:** `POST /api/chat`
    -   **Description:** This is a stateless endpoint that proxies a prompt to the Gemini API with search grounding. It does not persist messages. This provides the core chat functionality.
    -   **Request Body:** `{ "prompt": "string" }`
    -   **Success Response (200):** `{ "text": "string", "sources": [{"web": {"uri": "...", "title": "..."}}] }`

-   **Endpoint:** `GET /api/users/{user_id}/sessions`
    -   **Description:** Retrieves a list of all past chat sessions for a given user.
    -   **Success Response (200):** `[{ "session_id": "string", "title": "string", "created_at": "date" }]`

-   **Endpoint:** `GET /api/sessions/{session_id}/messages`
    -   **Description:** Retrieves all messages for a specific chat session.
    -   **Success Response (200):** `[{ "message_id": "string", "role": "user|model", "content": "string", "timestamp": "date" }]`

-   **Endpoint:** `POST /api/sessions/{session_id}/messages`
    -   **Description:** Sends a new message in a session, gets a response from the model, and persists both messages.
    -   **Request Body:** `{ "content": "string" }`
    -   **Success Response (200):** `{ "user_message": {...}, "model_message": {...} }`

### 3.3. Feedback & Analytics

-   **Endpoint:** `POST /api/feedback`
    -   **Description:** Records user feedback for a specific chat message.
    -   **Request Body:** `{ "message_id": "string", "user_id": "string", "rating": "thumbs_up|thumbs_down" }`
    -   **Success Response (201):** `{ "message": "Feedback received." }`

-   **Endpoint:** `POST /api/analytics`
    -   **Description:** A generic endpoint for the frontend to log key user interaction events.
    -   **Request Body:** `{ "user_id": "string", "event_type": "string", "details": {} }`
    -   **Success Response (202):** `{ "message": "Event logged." }`


## 4. Non-Functional Requirements

-   **Security:** The API must not handle secrets directly. All credentials must be fetched from Azure Key Vault at runtime using a Managed Identity.
-   **Performance:** API responses, especially for `/api/chat`, should have a p95 latency of less than 3 seconds.
-   **Scalability:** The service should be stateless and horizontally scalable to handle increasing user load.

## 5. Success Metrics

-   API Uptime: > 99.9%
-   API Error Rate: < 0.1%
-   Average Chat Response Latency: < 2 seconds
