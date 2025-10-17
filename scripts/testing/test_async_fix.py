#!/usr/bin/env python3
"""
Simple Test for Async Fix
=========================

This tests the thread-based async approach without Flask.
"""

import asyncio
import concurrent.futures

# Mock agent for testing
class MockAgent:
    async def run(self, query):
        await asyncio.sleep(0.1)  # Simulate async work
        return f"Agent response to: {query}"

def test_thread_based_async():
    """Test the thread-based async approach"""
    agent = MockAgent()
    query = "test query"
    
    def run_agent_in_thread(query):
        """Run the agent in a separate thread with its own event loop"""
        def run_in_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(agent.run(query))
            finally:
                loop.close()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            return future.result()
    
    try:
        response = run_agent_in_thread(query)
        print(f"✅ SUCCESS: {response}")
        return True
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Thread-Based Async Approach")
    print("=" * 50)
    
    success = test_thread_based_async()
    
    if success:
        print("\n🎉 The async fix works!")
        print("📝 You can now apply this to your notebook Flask app:")
        print("""
        # In your Flask home() function, replace:
        response = agent.run(query_text)
        
        # With:
        import concurrent.futures
        
        def run_agent_in_thread(query):
            def run_in_thread():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(agent.run(query))
                finally:
                    loop.close()
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_in_thread)
                return future.result()
        
        response = run_agent_in_thread(query_text)
        """)
    else:
        print("\n❌ The async fix needs more work.")