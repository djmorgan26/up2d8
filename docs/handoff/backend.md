# Backend API Documentation (Updated)

This document provides details on the main backend API endpoints for the Up2D8 application, reflecting the latest changes.

## Endpoints

### 1. Chat with Gemini

-   **Endpoint:** `POST /api/chat`
-   **Description:** This endpoint receives a user's prompt and communicates with the Gemini API to get a response. It now explicitly includes a `sources` array.
-   **Request Body:**
    ```json
    {
      "prompt": "string"
    }
    ```
-   **Success Response:**
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
    The `sources` array is optional and may be empty if no sources are available.

-   **Error Response:**
    ```json
    {
      "message": "string"
    }
    ```

### 2. User Management

-   **Endpoint:** `POST /api/users`
    -   **Description:** Creates a new user or updates an existing user's topics.
    -   **Request Body:**
        ```json
        {
          "email": "user@example.com",
          "topics": ["Tech", "AI"]
        }
        ```
    -   **Success Response:**
        ```json
        {
          "message": "Subscription confirmed." | "User already exists, topics updated.",
          "user_id": "string"
        }
        ```

-   **Endpoint:** `GET /api/users/{user_id}`
    -   **Description:** Retrieves a user's profile by their ID.
    -   **Success Response:**
        ```json
        {
            "user_id": "string",
            "email": "user@example.com",
            "topics": ["Tech", "AI", "Science"],
            "created_at": "2023-10-27T10:00:00Z",
            "preferences": {} // Optional
        }
        ```
    -   **Error Response:** `404 Not Found` if user does not exist.

-   **Endpoint:** `PUT /api/users/{user_id}`
    -   **Description:** Updates a user's preferences or topics. The `updated_at` field is automatically managed.
    -   **Request Body:**
        ```json
        {
          "topics": ["Tech", "AI"], // Optional
          "preferences": { "newsletter_style": "concise" } // Optional
        }
        ```
    -   **Success Response:**
        ```json
        {
          "message": "Preferences updated."
        }
        ```
    -   **Error Response:** `404 Not Found` if user does not exist, `400 Bad Request` if no fields to update are provided.

-   **Endpoint:** `DELETE /api/users/{user_id}`
    -   **Description:** Deletes a user's profile by their ID.
    -   **Success Response:**
        ```json
        {
          "message": "User deleted."
        }
        ```
    -   **Error Response:** `404 Not Found` if user does not exist.

### 3. Article Management (Read-Only)

-   **Endpoint:** `GET /api/articles`
    -   **Description:** Retrieves a list of all articles.
    -   **Success Response:**
        ```json
        [
          {
            "id": "string",
            "title": "string",
            "link": "string",
            "summary": "string",
            "published": "2023-10-27T09:00:00Z",
            "processed": false,
            "tags": ["string"],
            "created_at": "2023-10-27T09:30:00Z"
          }
        ]
        ```

-   **Endpoint:** `GET /api/articles/{article_id}`
    -   **Description:** Retrieves a single article by its ID.
    -   **Success Response:**
        ```json
        {
          "id": "string",
          "title": "string",
          "link": "string",
          "summary": "string",
          "published": "2023-10-27T09:00:00Z",
          "processed": false,
          "tags": ["string"],
          "created_at": "2023-10-27T09:30:00Z"
        }
        ```
    -   **Error Response:** `404 Not Found` if article does not exist.

### 4. RSS Feed Management (Admin Only)

-   **Endpoint:** `POST /api/rss_feeds`
    -   **Description:** Creates a new RSS feed entry.
    -   **Request Body:**
        ```json
        {
          "url": "https://example.com/rss_feed",
          "category": "Tech" // Optional
        }
        ```
    -   **Success Response:**
        ```json
        {
          "message": "RSS Feed created successfully.",
          "id": "string"
        }
        ```

-   **Endpoint:** `GET /api/rss_feeds`
    -   **Description:** Retrieves a list of all RSS feeds.
    -   **Success Response:**
        ```json
        [
          {
            "id": "string",
            "url": "https://example.com/rss_feed",
            "category": "string", // Optional
            "created_at": "2023-10-27T08:00:00Z"
          }
        ]
        ```

-   **Endpoint:** `GET /api/rss_feeds/{feed_id}`
    -   **Description:** Retrieves a single RSS feed by its ID.
    -   **Success Response:**
        ```json
        {
          "id": "string",
          "url": "https://example.com/rss_feed",
          "category": "string", // Optional
          "created_at": "2023-10-27T08:00:00Z"
        }
        ```
    -   **Error Response:** `404 Not Found` if RSS feed does not exist.

-   **Endpoint:** `PUT /api/rss_feeds/{feed_id}`
    -   **Description:** Updates an existing RSS feed's URL or category. The `updated_at` field is automatically managed.
    -   **Request Body:**
        ```json
        {
          "url": "https://updated.com/rss_feed", // Optional
          "category": "Updated Category" // Optional
        }
        ```
    -   **Success Response:**
        ```json
        {
          "message": "RSS Feed updated successfully."
        }
        ```
    -   **Error Response:** `404 Not Found` if RSS feed does not exist, `400 Bad Request` if no fields to update are provided.

-   **Endpoint:** `DELETE /api/rss_feeds/{feed_id}`
    -   **Description:** Deletes an RSS feed by its ID.
    -   **Success Response:**
        ```json
        {
          "message": "RSS Feed deleted successfully."
        }
        ```
    -   **Error Response:** `404 Not Found` if RSS feed does not exist.
