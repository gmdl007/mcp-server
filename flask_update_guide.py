#!/usr/bin/env python3
"""
Flask App Update for Simple asyncio.run()
========================================

This shows exactly what to change in your notebook Flask app.
"""

# BEFORE (your current code):
"""
@app.route("/", methods=["GET", "POST"])
def home():
    response = None
    if request.method == "POST":
        query_text = request.form.get("text", "")
        if query_text:
            # Query the agent
            response = agent.chat(query_text)
    return render_template_string(form_template, response=response)
"""

# AFTER (updated code with simple asyncio.run()):
"""
@app.route("/", methods=["GET", "POST"])
def home():
    response = None
    if request.method == "POST":
        query_text = request.form.get("text", "")
        if query_text:
            # Query the agent using simple asyncio.run()
            import asyncio
            response = asyncio.run(agent.run(query_text))
    return render_template_string(form_template, response=response)
"""

print("✅ Change Summary:")
print("1. Replace 'agent.chat(query_text)' with 'asyncio.run(agent.run(query_text))'")
print("2. Add 'import asyncio' at the top of the cell")
print("3. Update the comment to reflect the new approach")
print("\n🎯 This is the SIMPLE asyncio.run() approach you requested!")
print("📝 Just make these changes in your notebook Flask app cell.")
