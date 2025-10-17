#!/usr/bin/env python3
"""
Test Simple asyncio.run() Approach
==================================

This script tests the simple asyncio.run() approach for Flask.
"""

import asyncio
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Mock async function (simulates agent.run)
async def mock_agent_run(query):
    """Mock async function that simulates agent.run()"""
    await asyncio.sleep(0.5)  # Simulate async work
    return f"Agent response to: {query}"

# HTML template
form_template = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Simple Async Test</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    h1 { color: #333; }
    form { margin-bottom: 20px; }
    textarea { width: 100%; height: 100px; margin-bottom: 10px; }
    button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
    .response { background: #f8f9fa; padding: 15px; border-left: 4px solid #007bff; margin-top: 20px; }
  </style>
</head>
<body>
  <h1>Simple Async Test</h1>
  <form method="POST">
    <textarea name="text" placeholder="Enter your query..."></textarea><br>
    <button type="submit">Submit Query</button>
  </form>
  
  {% if response %}
  <div class="response">
    <h3>Response:</h3>
    <p>{{ response }}</p>
  </div>
  {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    response = None
    if request.method == "POST":
        query_text = request.form.get("text", "")
        if query_text:
            # Simple asyncio.run() approach
            response = asyncio.run(mock_agent_run(query_text))
    return render_template_string(form_template, response=response)

if __name__ == '__main__':
    print("🧪 Testing Simple asyncio.run() Approach")
    print("🌐 Access: http://localhost:5002")
    app.run(host='0.0.0.0', port=5002, debug=True)
