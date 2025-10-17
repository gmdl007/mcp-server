#!/usr/bin/env python3
"""
Set environment variables and test LLM authentication
"""

import os
import subprocess
import sys

# Set environment variables (you need to provide the correct values)
print("🔧 Setting up environment variables...")

# You need to provide the correct CLIENT_SECRET here
# The current one in the standalone script is invalid
os.environ['CLIENT_ID'] = "cG9jLXRyaWFsMjAyM09jdG9iZXIxNwff_540f3843f35f87eeb7b238fc2f8807"
os.environ['CLIENT_SECRET'] = "b-mQoS2NXZe4I15lVXtY7iBHCAg9u7ufZFx7MZiOHAFlzRBkFmOaenUI2buRpRBc"  # This might be invalid
os.environ['TOKEN_URL'] = "https://id.cisco.com/oauth2/default/v1/token"
os.environ['LLM_ENDPOINT'] = "https://chat-ai.cisco.com"
os.environ['APP_KEY'] = "egai-prd-wws-log-chat-data-analysis-1"

print("✅ Environment variables set")

# Test the LLM authentication
print("\n🧪 Testing LLM authentication...")

try:
    from debug_llm import *
    print("Running debug_llm.py with environment variables...")
except Exception as e:
    print(f"Error: {e}")

print("\n💡 To fix the LLM issue:")
print("1. Get valid CLIENT_ID and CLIENT_SECRET from Cisco")
print("2. Set them as environment variables:")
print("   export CLIENT_ID='your_valid_client_id'")
print("   export CLIENT_SECRET='your_valid_client_secret'")
print("3. Or update the hardcoded values in the standalone script")
