# Gemini Context: UP2D8 Backend API Service

This document provides context for the Gemini CLI to understand the UP2D8 Backend API service project.

## 1. Project Overview

The project is a FastAPI backend service for the UP2D8 application. It serves as the central hub for managing user data, handling real-time chat interactions by proxying requests to the Gemini API, and providing a stable interface for the frontend client.

## 2. Key Technologies

- **Backend:** Python, FastAPI
- **Database:** MongoDB (local and Azure Hosted CosmosDB Cluster for MongoDB)
- **Authentication:** Azure Managed Identity and `DefaultAzureCredential` for local development.
- **Secrets Management:** Azure Key Vault `shared/key_vault_client.py`.
- **Chat:** Google Gemini API.

## 3. Core Functionality (API Endpoints)

- **User Management:**
    - `POST /api/users`: Create/update a user (for newsletter subscription).
    - `PUT /api/users/{user_id}`: Update user preferences.
- **Chat Interaction:**
    - `POST /api/chat`: Stateless proxy to Gemini API for chat.
    - `GET /api/users/{user_id}/sessions`: Get user's chat sessions.
    - `GET /api/sessions/{session_id}/messages`: Get messages for a session.
    - `POST /api/sessions/{session_id}/messages`: Send a message in a session.
- **Feedback & Analytics:**
    - `POST /api/feedback`: Record user feedback on chat messages.
    - `POST /api/analytics`: Log user interaction events.

## 4. Local Development Setup

1.  **Prerequisites:** Python 3.9+, Pip, venv, Azure CLI.
2.  **Authentication:** Log in to Azure CLI with `az login`.
3.  **Configuration:** Create a `.env` file with the `KEY_VAULT_URI` and `GEMINI_API_KEY`.
4.  **Dependencies:** Install dependencies from `requirements.txt` and use venv for local dev.
5.  **Run:** `uvicorn main:app --reload`.

## 5. Non-Functional Requirements

- **Security:** No hardcoded secrets. Uses Azure Key Vault.
- **Performance:** p95 latency for chat should be < 3 seconds.
- **Scalability:** The service should be stateless and horizontally scalable.

## 6. Other Repositories

This project spans 3 repositories (frontend, backend, function app). When doing work that involves integrating with the other repos of this greater project, refer to these handoff documents first.

- **UP2D8-FUNCTION** The handoff document for this repo is `docs/handoff/function.md`.
- **UP2D8-FRONTEND** The handoff document for this repo is `docs/handoff/frontend.md`.