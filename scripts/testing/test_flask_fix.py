#!/usr/bin/env python3
"""
Quick Test: Simple asyncio.run() Fix
===================================

This tests the exact fix you need to apply to your notebook.
"""

import asyncio

# Mock agent for testing
class MockAgent:
    async def run(self, query):
        await asyncio.sleep(0.1)  # Simulate async work
        return f"Agent response to: {query}"

# Test the fix
agent = MockAgent()

def test_flask_route():
    """Simulate the Flask route with the fix"""
    query_text = "test query"
    
    # This is the FIXED code you need in your notebook:
    response = asyncio.run(agent.run(query_text))
    
    print(f"✅ SUCCESS: {response}")
    return response

if __name__ == "__main__":
    print("🧪 Testing the Flask fix...")
    result = test_flask_route()
    print("🎯 This is exactly what you need in your notebook Flask cell!")
