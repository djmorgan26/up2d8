# UP2D8 - Backend API Service

This repository contains the FastAPI backend service for the UP2D8 application. This service is responsible for handling all live user requests from the frontend, managing database interactions, and securely calling the Google Gemini API.

## 1. Prerequisites

-   Python 3.9+
-   Pip & venv
-   Azure CLI (for local development authentication)
-   An Azure Key Vault with the required secrets configured.

## 2. Configuration & Secrets

This service is designed for maximum security using Azure Key Vault. **No secrets are stored in this repository or in environment variables.**

### Secret Management
-   **In Azure:** The deployed App Service uses a **Managed Identity** to authenticate with Key Vault.
-   **Locally:** The service uses `DefaultAzureCredential`, which will use the credentials of the developer currently logged into the Azure CLI.

### Local Setup
1.  **Log in to Azure:**
    ```bash
    az login
    ```
    Ensure the logged-in user has "Get" permissions on secrets in the project's Key Vault.

2.  **Create `.env` file:**
    Create a file named `.env` in the root of the project by copying `.env.example`. The only variable you need to set is the URI of your Key Vault.

    ```ini
    # .env
    KEY_VAULT_URI="https://personal-key-vault1.vault.azure.net/"
    ```

## 3. Installation & Local Execution

1.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: a `requirements.txt` file will need to be created containing `fastapi`, `uvicorn`, `pymongo`, `google-generativeai`, `azure-identity`, `azure-keyvault-secrets`, `python-dotenv`)*

3.  **Run the local server:**
    ```bash
    uvicorn main:app --reload
    ```
    The API will be available at `http://127.0.0.1:8000`.

## 4. API Endpoints

This service provides the core API for the UP2D8 application. See the `PRD.md` for detailed request/response schemas.

-   `POST /api/chat`: Proxies a prompt to the Gemini API with search grounding.
-   `POST /api/users`: Subscribes a new user.
-   `PUT /api/users/{user_id}`: Updates user preferences.
-   `GET /api/users/{user_id}/sessions`: Gets all chat sessions for a user.
-   `GET /api/sessions/{session_id}/messages`: Gets all messages for a session.
-   `POST /api/sessions/{session_id}/messages`: Creates a new message and gets a model response.
-   `POST /api/feedback`: Records user feedback.
-   `POST /api/analytics`: Logs an analytics event.

## 5. Deployment to Azure App Service

1.  **Create App Service:** In the Azure Portal, create a new "Web App" resource.
    -   **Publish:** Code
    -   **Runtime stack:** Python 3.9 (or newer)
    -   **Operating System:** Linux

2.  **Enable Managed Identity:**
    -   Go to your new App Service.
    -   Under **Settings > Identity**, enable the **System assigned** identity.
    -   Grant this identity **"Get"** permissions on secrets in your Key Vault's Access Policies.

3.  **Configure Application Settings:**
    -   In your App Service, go to **Settings > Configuration**.
    -   Add a new Application Setting:
        -   **Name:** `KEY_VAULT_URI`
        -   **Value:** `https://personal-key-vault1.vault.azure.net/`

4.  **Deploy Code:**
    -   Use the "Deployment Center" in your App Service to connect to your Git repository (e.g., GitHub Actions) for CI/CD.
    -   Alternatively, use the Azure CLI or the VS Code Azure extension to deploy your code.
