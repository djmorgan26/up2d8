import os
from pymongo import MongoClient
from shared.key_vault_client import KeyVaultClient
from dotenv import load_dotenv

load_dotenv()

_db_client = None
_key_vault_client = None

def get_key_vault_client() -> KeyVaultClient:
    """Get or create Key Vault client singleton"""
    global _key_vault_client
    if _key_vault_client is None:
        _key_vault_client = KeyVaultClient()
    return _key_vault_client

def get_db_client():
    """Get or create MongoDB client singleton"""
    global _db_client
    if _db_client is None:
        # Try to get connection string from environment (for local dev)
        connection_string = os.getenv("MONGODB_CONNECTION_STRING")

        # If not in env, try to get from Key Vault
        if not connection_string:
            try:
                kv_client = get_key_vault_client()
                connection_string = kv_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8")
            except Exception as e:
                print(f"Warning: Could not retrieve MongoDB connection from Key Vault: {e}")
                # Fall back to localhost for local development
                connection_string = "mongodb://localhost:27017/"

        client = MongoClient(connection_string)
        database_name = os.getenv("MONGODB_DATABASE", "up2d8")
        _db_client = client[database_name]

    return _db_client

def get_gemini_api_key() -> str:
    """Get Gemini API key from environment or Key Vault"""
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        try:
            kv_client = get_key_vault_client()
            api_key = kv_client.get_secret("UP2D8-GEMINI-API-KEY")
        except Exception as e:
            print(f"Error: Could not retrieve Gemini API key: {e}")
            raise

    return api_key
