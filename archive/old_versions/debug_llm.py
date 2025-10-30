#!/usr/bin/env python3
"""
Debug script to test LLM authentication
"""

import base64
import requests
import json

# Configuration from the standalone script
CLIENT_ID = "cG9jLXRyaWFsMjAyM09jdG9iZXIxNwff_540f3843f35f87eeb7b238fc2f8807"
CLIENT_SECRET = "b-mQoS2NXZe4I15lVXtY7iBHCAg9u7ufZFx7MZiOHAFlzRBkFmOaenUI2buRpRBb"
TOKEN_URL = "https://id.cisco.com/oauth2/default/v1/token"
LLM_ENDPOINT = "https://chat-ai.cisco.com"
APP_KEY = "egai-prd-wws-log-chat-data-analysis-1"

print("🔍 Debugging LLM Authentication")
print("=" * 50)

# Step 1: Test OAuth token request
print("📋 Step 1: Testing OAuth token request...")

auth_key = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode("utf-8")).decode("utf-8")
print(f"Auth Key: {auth_key[:20]}...")

headers = {
    "Accept": "*/*",
    "Content-Type": "application/x-www-form-urlencoded",
    "Authorization": f"Basic {auth_key}",
}

print(f"Headers: {headers}")
print(f"Token URL: {TOKEN_URL}")

try:
    print("Making POST request...")
    token_response = requests.post(TOKEN_URL, headers=headers, data="grant_type=client_credentials")
    
    print(f"Status Code: {token_response.status_code}")
    print(f"Response Headers: {dict(token_response.headers)}")
    print(f"Response Text: {token_response.text}")
    
    if token_response.status_code == 200:
        response_json = token_response.json()
        print(f"Response JSON: {json.dumps(response_json, indent=2)}")
        
        token = response_json.get("access_token")
        if token:
            print(f"✅ Token received: {token[:20]}...")
            
            # Step 2: Test LLM creation
            print("\n📋 Step 2: Testing LLM creation...")
            
            from llama_index.llms.azure_openai import AzureOpenAI
            
            llm = AzureOpenAI(
                azure_endpoint=LLM_ENDPOINT,
                api_version="2024-07-01-preview",
                deployment_name='gpt-4o-mini',
                api_key=token,
                max_tokens=3000,
                temperature=0.1,
                additional_kwargs={"user": f'{{"appkey": "{APP_KEY}"}}'}
            )
            
            print("✅ LLM created successfully!")
            
            # Step 3: Test LLM call
            print("\n📋 Step 3: Testing LLM call...")
            
            response = llm.complete("Hello, this is a test. Please respond with 'Test successful'.")
            print(f"✅ LLM Response: {response}")
            
        else:
            print("❌ No access_token in response")
    else:
        print(f"❌ HTTP Error: {token_response.status_code}")
        
except Exception as e:
    print(f"❌ Exception: {e}")
    import traceback
    traceback.print_exc()

print("\n🎉 Debug completed!")
