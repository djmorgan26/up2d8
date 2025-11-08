# Backend API Documentation

This document provides details on the main backend API endpoints for the Up2D8 application.

## Endpoints

### 1. Chat with Gemini

- **Endpoint:** `POST /api/chat`
- **Description:** This endpoint receives a user's prompt and communicates with the Gemini API to get a response. It may also include grounding sources.
- **Request Body:**
  ```json
  {
    "prompt": "string"
  }
  ```
- **Success Response:**
  ```json
  {
    "text": "string",
    "sources": [
      {
        "web": {
          "uri": "string",
          "title": "string"
        }
      }
    ]
  }
  ```
  The `sources` array is optional.

- **Error Response:**
  ```json
  {
    "message": "string"
  }
  ```
