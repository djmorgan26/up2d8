# UP2D8 - Full Stack Implementation Guide (Secure Edition)

This document provides the complete, security-hardened instructions to build, configure, and deploy the backend services for the UP2D8 application. All secrets are managed centrally in Azure Key Vault and accessed securely at runtime.

The frontend is already built and expects the API endpoints defined here.

## Table of Contents
1.  [Architecture Overview](#1-architecture-overview)
2.  [A Note on Logging & Debugging](#2-a-note-on-logging--debugging)
3.  [Security: Connecting to Azure Key Vault](#3-security-connecting-to-azure-key-vault)
4.  [Application Configuration](#4-application-configuration)
5.  [Backend API Setup (FastAPI)](#5-backend-api-setup-fastapi)
6.  [Database Setup (Azure Cosmos DB)](#6-database-setup-azure-cosmos-db)
7.  [Automated Daily Tasks (Azure Functions)](#7-automated-daily-tasks-azure-functions)
    - [Function 1: Daily Article Scraper](#function-1-daily-article-scraper)
    - [Function 2: Newsletter Generator & Sender](#function-2-newsletter-generator--sender)
8.  [Deployment Plan](#8-deployment-plan)

---

## 1. Architecture Overview

-   **React Frontend**: The user interface (already built). Deployed on Azure Static Web Apps.
-   **Azure Key Vault**: The central, secure storage for all application secrets. Your Key Vault URI is: `https://personal-key-vault1.vault.azure.net/`
-   **FastAPI Backend**: A Python API that handles live requests. It authenticates to Key Vault using a **Managed Identity**. Deployed on Azure App Service.
-   **Azure Cosmos DB**: A NoSQL database to store user subscriptions and scraped articles.
-   **Azure Functions**: Two serverless functions running on a schedule. They also authenticate to Key Vault using a **Managed Identity**.

---

## 2. A Note on Logging & Debugging

Setting up a multi-service application in the cloud involves many moving parts. You will inevitably need to debug issues during setup and operation. **Good logging is your most powerful tool.**

The Python code provided in this guide includes basic `logging` statements for key events:
-   Function start and end times.
-   Successful operations (e.g., "Scraping complete," "Successfully sent email").
-   Critical errors (e.g., "Failed to process feed," "Database error").

### How to Access Logs in Azure

Both Azure App Service and Azure Function Apps integrate deeply with **Azure Monitor** and **Application Insights**.

1.  **Enable Application Insights**: When you create your App Service and Function App in Azure, you will be prompted to enable Application Insights. **It is highly recommended that you do this.** It provides rich, searchable logs, performance metrics, and failure analysis.

2.  **Viewing Live Logs (Log Stream)**: For real-time debugging during deployment or testing, you can stream logs directly from your services:
    -   In the Azure Portal, go to your App Service or Function App.
    -   In the left-hand menu, under "Monitoring", click **"Log stream"**.
    -   You will see a live console output of all `print` and `logging` statements from your code as they happen. This is invaluable for spotting immediate errors.

3.  **Querying Historical Logs (Application Insights)**:
    -   Go to the Application Insights resource associated with your service.
    -   Under "Monitoring", click **"Logs"**.
    -   This opens the powerful Kusto Query Language (KQL) editor. You can query for specific log messages, exceptions, and traces. For example:
        ```kql
        traces
        | where message contains "Failed"
        | order by timestamp desc
        ```

When you encounter an issue (e.g., an API call fails, a newsletter isn't sent), your first step should always be to check the logs for the relevant service.

---

## 3. Security: Connecting to Azure Key Vault

This is the most critical setup step. Instead of placing secrets in environment variables, we give our Azure services an identity and grant them permission to read secrets from your Key Vault.

### Step 1: Enable Managed Identity for Azure Services

For **both** your Azure App Service (for the FastAPI backend) and your Azure Function App:
1.  Go to the resource in the Azure Portal.
2.  In the left-hand menu, under "Settings", click **"Identity"**.
3.  Under the **"System assigned"** tab, switch the status to **"On"** and click **"Save"**.
4.  Azure will create an identity for your service. Copy the **"Object (principal) ID"** - you will need it in the next step.

### Step 2: Grant Identities Access to Key Vault

1.  Go to your Key Vault (`personal-key-vault1`) in the Azure Portal.
2.  In the left-hand menu, click **"Access policies"**.
3.  Click **"+ Create"**.
4.  Under "Secret permissions", check the **"Get"** box.
5.  Click "Next". In the "Principal" tab, paste the **Object (principal) ID** you copied from your App Service or Function App. Select the identity when it appears.
6.  Click "Next", then "Next" again, then **"Create"**.
7.  **Repeat this process** for the Managed Identity of your *other* service. Both the App Service and the Function App need their own access policy.

### Step 3: Local Development Setup

For local development, the code uses `DefaultAzureCredential`, which automatically detects how to authenticate. The easiest way is:
1.  Install the Azure CLI: `https://docs.microsoft.com/en-us/cli/azure/install-azure-cli`
2.  Log in to your Azure account: `az login`
3.  Your local Python script will now be able to access the Key Vault using your personal Azure credentials, as long as you have given your own user account "Get" permissions on secrets in the Key Vault's access policies.

---

## 4. Application Configuration

Your applications now only need a few configuration values set as environment variables.

#### Key Vault Secret Names

Ensure your secrets in `personal-key-vault1` are named exactly as follows:
-   `UP2D8-GEMINI-API-Key`
-   `COSMOS-DB-CONNECTION-STRING-UP2D8`
-   `UP2D8-SMTP-KEY`

#### Environment Variables

These are the non-secret values your applications need.
```ini
# The URI of your Key Vault. This is the only "secret pointer" needed.
KEY_VAULT_URI="https://personal-key-vault1.vault.azure.net/"

# Non-secret SMTP configuration
BREVO_SMTP_HOST="smtp-relay.brevo.com"
BREVO_SMTP_PORT="587"
BREVO_SMTP_USER="9a9964001@smtp-brevo.com" 
SENDER_EMAIL="newsletter@yourdomain.com" # Use a verified sender email
```

---

## 5. Backend API Setup (FastAPI)

**Step 1: Install Dependencies**
```bash
pip install fastapi "uvicorn[standard]" python-dotenv pymongo google-generativeai azure-identity azure-keyvault-secrets
```

**Step 2: Create `main.py`**
```python
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
import google.generativeai as genai
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

# --- Initial Configuration & Secret Loading ---
load_dotenv()

# Get the Key Vault URI from environment variables
key_vault_uri = os.getenv("KEY_VAULT_URI")
if not key_vault_uri:
    raise ValueError("KEY_VAULT_URI environment variable not set.")

# Authenticate to Key Vault using DefaultAzureCredential
# In Azure, this uses the Managed Identity. Locally, it uses your Azure CLI login.
credential = DefaultAzureCredential()
secret_client = SecretClient(vault_url=key_vault_uri, credential=credential)

# Fetch secrets from Key Vault
gemini_api_key = secret_client.get_secret("UP2D8-GEMINI-API-Key").value
cosmos_db_connection_string = secret_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8").value

# --- Service Initialization ---
app = FastAPI()
genai.configure(api_key=gemini_api_key)
client = MongoClient(cosmos_db_connection_string)
db = client['up2d8_db']
subscriptions_collection = db['subscriptions']

# --- Pydantic Models ---
class ChatRequest(BaseModel):
    prompt: str

class SubscribeRequest(BaseModel):
    email: str
    topics: list[str]

# --- API Endpoints ---
@app.post("/api/chat")
async def chat_handler(req: ChatRequest):
    # (Rest of the endpoint code is the same as before)
    if not req.prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
    try:
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            tools=[genai.Tool(google_search=genai.GoogleSearch())]
        )
        response = model.generate_content(req.prompt)
        
        sources = []
        if response.candidates and response.candidates[0].grounding_metadata:
            for chunk in response.candidates[0].grounding_metadata.grounding_chunks:
                if chunk.web:
                    sources.append({"web": {"uri": chunk.web.uri, "title": chunk.web.title}})

        return {"text": response.text, "sources": sources}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


@app.post("/api/subscribe")
async def subscribe_handler(req: SubscribeRequest):
    # (Rest of the endpoint code is the same as before)
    if not req.email or not req.topics:
        raise HTTPException(status_code=400, detail="Email and topics are required.")
    try:
        subscriptions_collection.update_one(
            {'email': req.email},
            {'$set': {'topics': req.topics, 'email': req.email}},
            upsert=True
        )
        return {"message": "Successfully subscribed!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# To run locally: uvicorn main:app --reload
```

---

## 6. Database Setup (Azure Cosmos DB)

(This section remains the same)
1.  In the Azure Portal, create an "Azure Cosmos DB" resource.
2.  Choose the **"Azure Cosmos DB for MongoDB"** API.
3.  Once created, go to "Connection String" and copy the "PRIMARY CONNECTION STRING". Store this value in your Azure Key Vault secret named `COSMOS-DB-CONNECTION-STRING-UP2D8`.

---

## 7. Automated Daily Tasks (Azure Functions)

### Function 1: Daily Article Scraper

**Step 1: Create a Timer Trigger Function**
-   Schedule: `0 0 8 * * *` (8:00 AM UTC daily)

**Step 2: `requirements.txt`**
```txt
azure-functions
pymongo
feedparser
azure-identity
azure-keyvault-secrets
```

**Step 3: `function_app.py` or `__init__.py`**
```python
import datetime
import logging
import os
import feedparser
from pymongo import MongoClient
import azure.functions as func
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

# --- Config & Secret Loading ---
key_vault_uri = os.environ["KEY_VAULT_URI"]
credential = DefaultAzureCredential()
secret_client = SecretClient(vault_url=key_vault_uri, credential=credential)
cosmos_db_connection_string = secret_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8").value

RSS_FEEDS = [
    "http://rss.slashdot.org/Slashdot/slashdotMain",
    "https://www.techcrunch.com/feed/",
    "https://feeds.wired.com/wired/index",
]

# --- Database Connection ---
client = MongoClient(cosmos_db_connection_string)
db = client['up2d8_db']
articles_collection = db['articles']
articles_collection.create_index("link", unique=True)

def main(mytimer: func.TimerRequest) -> None:
    logging.info('Python timer trigger function ran.')
    # (Rest of the function code is the same as before)
    articles_added = 0
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                try:
                    article_doc = {
                        "title": entry.title, "link": entry.link, "summary": entry.summary,
                        "published": entry.get("published", datetime.datetime.utcnow().isoformat()),
                        "source": feed.feed.title, "scraped_at": datetime.datetime.utcnow(),
                        "processed": False
                    }
                    articles_collection.insert_one(article_doc)
                    articles_added += 1
                except Exception:
                    pass # Ignore duplicates
        except Exception as e:
            logging.error(f"Failed to process feed {feed_url}: {e}")
    
    logging.info(f"Scraping complete. Added {articles_added} new articles.")
```

### Function 2: Newsletter Generator & Sender

**Step 1: Create a Timer Trigger Function**
-   Schedule: `0 0 9 * * *` (9:00 AM UTC daily)

**Step 2: `requirements.txt`**
```txt
azure-functions
pymongo
google-generativeai
azure-identity
azure-keyvault-secrets
```

**Step 3: `function_app.py` or `__init__.py`**
```python
import datetime
import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pymongo import MongoClient
import google.generativeai as genai
import azure.functions as func
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

# --- Config & Secret Loading ---
key_vault_uri = os.environ["KEY_VAULT_URI"]
credential = DefaultAzureCredential()
secret_client = SecretClient(vault_url=key_vault_uri, credential=credential)

# Fetch Secrets
gemini_api_key = secret_client.get_secret("UP2D8-GEMINI-API-Key").value
cosmos_db_connection_string = secret_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8").value
smtp_password = secret_client.get_secret("UP2D8-SMTP-KEY").value

# Fetch Non-Secrets from environment
smtp_host = os.environ["BREVO_SMTP_HOST"]
smtp_port = os.environ["BREVO_SMTP_PORT"]
smtp_user = os.environ["BREVO_SMTP_USER"]
sender_email = os.environ["SENDER_EMAIL"]

# --- Service Initialization ---
genai.configure(api_key=gemini_api_key)
client = MongoClient(cosmos_db_connection_string)
db = client['up2d8_db']
articles_collection = db['articles']
subscriptions_collection = db['subscriptions']

# (The rest of the functions: generate_newsletter_content, send_email, and main are the same as before)
def generate_newsletter_content(user_topics, articles):
    model = genai.GenerativeModel('gemini-2.5-flash')
    article_summaries = "\n\n".join([f"Title: {a['title']}\nSummary: {a['summary']}\nLink: {a['link']}" for a in articles])
    prompt = f"""You are a helpful news editor creating a personalized daily digest. Your tone should be professional, engaging, and concise. The user is interested in the following topics: {', '.join(user_topics)}. Based on these topics, summarize the following articles into a newsletter. Use Markdown for formatting. Include the title (as a bold heading), a brief summary, and the original link for each article. Start with a friendly greeting. Articles to summarize: {article_summaries}"""
    response = model.generate_content(prompt)
    return response.text

def send_email(recipient_email, content):
    message = MIMEMultipart("alternative")
    message["Subject"] = f"Your UP2D8 Daily Digest for {datetime.date.today().strftime('%B %d, %Y')}"
    message["From"] = sender_email
    message["To"] = recipient_email
    part = MIMEText(content, "plain")
    message.attach(part)
    try:
        with smtplib.SMTP(smtp_host, int(smtp_port)) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        logging.info(f"Successfully sent email to {recipient_email}")
    except Exception as e:
        logging.error(f"Failed to send email to {recipient_email}: {e}")

def main(mytimer: func.TimerRequest) -> None:
    logging.info('Newsletter generation and sending process started.')
    subscribers = list(subscriptions_collection.find({}))
    if not subscribers:
        logging.info("No subscribers found. Exiting.")
        return
    unprocessed_articles = list(articles_collection.find({"processed": False}))
    if not unprocessed_articles:
        logging.info("No new articles to process. Exiting.")
        return
    for sub in subscribers:
        user_email = sub['email']
        user_topics = [topic.lower() for topic in sub['topics']]
        relevant_articles = []
        for article in unprocessed_articles:
            content_to_search = (article['title'] + article['summary']).lower()
            if any(topic in content_to_search for topic in user_topics):
                relevant_articles.append(article)
        if not relevant_articles:
            continue
        newsletter_content = generate_newsletter_content(user_topics, relevant_articles)
        send_email(user_email, newsletter_content)
    article_ids_to_update = [a['_id'] for a in unprocessed_articles]
    if article_ids_to_update:
        articles_collection.update_many(
            {"_id": {"$in": article_ids_to_update}},
            {"$set": {"processed": True}}
        )
    logging.info("Newsletter process finished.")
```

---

## 8. Deployment Plan

1.  **React Frontend**: Deploy to **Azure Static Web App**.
2.  **FastAPI Backend**: Deploy to **Azure App Service**. Enable its **Managed Identity** and configure its **Application Settings** with the non-secret environment variables.
3.  **Azure Functions**: Deploy to **Azure Function App**. Enable its **Managed Identity** and configure its **Application Settings** with the non-secret environment variables.
