# Master Prompt: Generate the Full-Stack UP2D8 Application

## 1. High-Level Goal

Your task is to generate a complete, full-stack, production-ready web application called "UP2D8". This application serves as a personalized daily news digest service and an AI-powered chat assistant. Users can subscribe to topics, browse popular interests, and chat with an AI that provides up-to-date, accurate answers from the web.

The application must be secure, scalable, and have a polished, modern, Google Material Design-inspired user interface with excellent UX. All code should be clean, well-documented, and ready for deployment on Microsoft Azure.

---

## 2. Core Functionality & User Experience

### a. Frontend UI/UX Style Guide
-   **Aesthetic**: Clean, modern, and inspired by Google's Material Design. Use generous whitespace, soft shadows, and rounded corners.
-   **Color Palette**:
    -   *Light Mode*: White/light-gray backgrounds (`#FFFFFF`, `#F8F9FA`), dark text (`#202124`), Google Blue accents (`#1A73E8`).
    -   *Dark Mode*: Dark charcoal backgrounds (`#202124`, `#303134`), light text (`#E8EAED`), light blue accents (`#8AB4F8`).
-   **Typography**: Use a clean, sans-serif font like Roboto or Google Sans.
-   **Interactivity**: All interactive elements must have clear hover, focus, and disabled states. Use smooth CSS transitions for all state changes.
-   **Responsiveness**: The application must be fully responsive and provide an excellent experience on all screen sizes, from mobile to desktop.
-   **Theme Support**: Implement a seamless Light/Dark/System theme switcher. The user's preference must be saved to `localStorage`.

### b. Frontend Pages (React)

#### i. Chat Page
-   **Purpose**: The main interface for interacting with the Gemini-powered AI assistant.
-   **Layout**: A classic chat interface with a message history view and an input form at the bottom.
-   **Features**:
    -   Display an initial welcome message from the bot.
    -   User messages are right-aligned; bot and error messages are left-aligned.
    -   Show a loading indicator (e.g., pulsing dots) while the bot is generating a response.
    -   Render markdown in bot responses (e.g., bold text).
    -   Display clickable "Source" chips below messages that used Google Search grounding.
    -   The message list should auto-scroll to the bottom.

#### ii. Browse Page
-   **Purpose**: A visually engaging page for users to discover topics for their digest.
-   **Layout**: Inspired by streaming services (like Netflix). Display categories (e.g., "Trending in Tech," "Business & Finance") as horizontally-scrolling rows.
-   **Components**: Each topic within a row should be a `TopicCard` component displaying a high-quality background image and the topic name with a subtle gradient overlay.

#### iii. Subscribe Page
-   **Purpose**: A form for users to sign up for their daily email digest.
-   **Layout**: A clean, single-column form.
-   **Features**:
    -   Input for email address.
    -   A section with clickable chips for popular, predefined topics.
    -   An input field for users to add their own custom topics.
    -   A display area showing all currently selected topics, with an option to remove each one.
    -   A submit button with a loading state.
    -   Provide clear success or error feedback to the user upon form submission.

---

## 3. Technology Stack & Architecture

-   **Frontend**: React with TypeScript, using Vite for bundling. Style with Tailwind CSS.
-   **Backend API**: Python with FastAPI.
-   **Database**: Azure Cosmos DB (using the MongoDB API).
-   **Scheduled Tasks**: Serverless Azure Functions (Python).
-   **AI Model**: Gemini (`gemini-2.5-flash` or similar) via the Google GenAI SDK.
-   **Email Service**: Brevo (formerly Sendinblue) via SMTP.
-   **Hosting**: Microsoft Azure (Static Web App, App Service, Function App).
-   **Security**: Azure Key Vault for all secret management.

---

## 4. Secure Backend Implementation

### a. Secret Management (Azure Key Vault)
-   **Principle**: NO secrets (API keys, connection strings) should ever be in code, config files, or environment variables.
-   **Implementation**:
    -   All services (FastAPI, Azure Functions) must connect to Azure Key Vault at runtime using a **Managed Identity**.
    -   The Python code must use `azure-identity` and `azure-keyvault-secrets` libraries with `DefaultAzureCredential()` to fetch secrets.
    -   The Key Vault URI is `https://personal-key-vault1.vault.azure.net/`.
    -   **Secret Names in Vault**:
        -   `UP2D8-GEMINI-API-Key`
        -   `COSMOS-DB-CONNECTION-STRING-UP2D8`
        -   `UP2D8-SMTP-KEY`

### b. Backend API (FastAPI)
-   **Purpose**: To serve requests from the React frontend, acting as a secure proxy to other services.
-   **Endpoint 1: `POST /api/chat`**
    -   **Request Body**: `{ "prompt": "user's question" }`
    -   **Logic**:
        1.  Receive the prompt.
        2.  Call the Gemini API using the `gemini-2.5-flash` model with the `googleSearch` tool enabled for grounding.
        3.  Extract the generated text and any source URLs from the grounding metadata.
    -   **Success Response (200)**: `{ "text": "...", "sources": [{"web": {"uri": "...", "title": "..."}}] }`
    -   **Error Response (500)**: `{ "message": "error details" }`
-   **Endpoint 2: `POST /api/subscribe`**
    -   **Request Body**: `{ "email": "...", "topics": ["topic1", "topic2"] }`
    -   **Logic**:
        1.  Connect to the Cosmos DB `subscriptions` collection.
        2.  Perform an "upsert": if the email exists, update its topics; otherwise, create a new document.
    -   **Success Response (200)**: `{ "message": "Successfully subscribed!" }`
    -   **Error Response (500)**: `{ "message": "error details" }`

### c. Database Schema (Cosmos DB for MongoDB)
-   **Database Name**: `up2d8_db`
Collection 1: users (replaces subscriptions)
_id: ObjectId
user_id: String (unique, corresponds to an auth provider ID in a future state)
email: String (indexed, unique)
topics: Array of String
preferences: Object (e.g., { "newsletter_format": "concise", "delivery_time": "morning" })
created_at: Date
Collection 2: articles
_id, link, title, summary, source, published, scraped_at, processed (as previously defined).
Collection 3: chat_sessions
_id: ObjectId
session_id: String (UUID, unique)
user_id: String (references users.user_id)
title: String (e.g., the first user message)
created_at: Date
Collection 4: chat_messages
_id: ObjectId
session_id: String (references chat_sessions.session_id)
role: String ('user' or 'model')
content: String
timestamp: Date
Collection 5: feedback
_id: ObjectId
message_id: String (references chat_messages._id)
user_id: String
rating: String ('thumbs_up' or 'thumbs_down')
timestamp: Date
Collection 6: analytics_events
_id: ObjectId
user_id: String
event_type: String (e.g., 'subscription', 'page_view', 'topic_add')
details: Object
timestamp: Date

### d. Automated Tasks (Azure Functions)

#### i. Function 1: Daily Article Scraper (Timer Trigger)
-   **Schedule**: Runs daily at 08:00 UTC.
-   **Logic**:
    1.  Connect to the Cosmos DB `articles` collection.
    2.  Iterate through a predefined list of RSS feeds (e.g., TechCrunch, Wired).
    3.  For each article in each feed, attempt to insert it into the `articles` collection. The unique index on `link` will prevent duplicates.
    4.  Log the number of new articles added.

#### ii. Function 2: Newsletter Generator & Sender (Timer Trigger)
-   **Schedule**: Runs daily at 09:00 UTC (after the scraper).
-   **Logic**:
    1.  Fetch all users from the `subscriptions` collection.
    2.  Fetch all articles where `processed` is `false`.
    3.  For each subscriber:
        a. Filter the unprocessed articles to find ones relevant to their subscribed topics (simple keyword match in title/summary).
        b. If relevant articles are found, construct a prompt for Gemini to summarize them into a newsletter.
        c. Call the Gemini API to generate the newsletter content in Markdown format.
        d. Connect to the Brevo SMTP server using the credentials from Key Vault.
        e. Send the generated newsletter to the user's email.
    4.  After processing all users, update the `processed` flag to `true` for all the articles that were just used.
    5.  Log all major steps and any errors.

---

## 5. Logging and Deployment

-   **Logging**: All backend services (FastAPI, Azure Functions) must implement structured logging (using Python's `logging` module). Logs should be accessible and searchable via Azure Application Insights.
-   **Deployment**:
    -   **Frontend**: Deploy the static build output to an **Azure Static Web App**.
    -   **Backend**: Deploy the FastAPI application to an **Azure App Service**.
    -   **Functions**: Deploy the automated tasks to an **Azure Function App**.
-   **Documentation**: Generate a `README.md` file that explains the architecture, setup, and deployment process, including how to configure Managed Identities and Key Vault Access Policies.
-   **Local Development**: Include a `.env.example` file to guide local setup, pointing to the Key Vault URI and explaining how to authenticate locally using `az login`.
