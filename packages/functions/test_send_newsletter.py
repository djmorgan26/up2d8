#!/usr/bin/env python3
"""Test script to send newsletter immediately."""
import os
import sys

# Add the functions directory to the path so we can import the newsletter function
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

# Set required environment variables
os.environ['KEY_VAULT_URI'] = os.getenv('KEY-VAULT-URI')
os.environ['BREVO_SMTP_USER'] = os.getenv('BREVO-SMTP-USER')
os.environ['BREVO_SMTP_HOST'] = os.getenv('BREVO-SMTP-HOST')
os.environ['BREVO_SMTP_PORT'] = os.getenv('BREVO-SMTP-PORT')
os.environ['SENDER_EMAIL'] = os.getenv('SENDER-EMAIL')

# Import the newsletter function
from NewsletterGenerator import main

# Create a mock timer object
class MockTimer:
    def __init__(self):
        self.past_due = False

print("=" * 80)
print("SENDING TEST NEWSLETTER NOW")
print("=" * 80)

# Run the newsletter function
try:
    main(MockTimer())
    print("\n" + "=" * 80)
    print("✅ Newsletter function executed successfully!")
    print("Check your email at: davidjmorgan26@gmail.com")
    print("=" * 80)
except Exception as e:
    print("\n" + "=" * 80)
    print(f"❌ Error sending newsletter: {e}")
    print("=" * 80)
    import traceback
    traceback.print_exc()
