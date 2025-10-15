#!/usr/bin/env python3
"""
Exact Fix for Your Flask App Cell
=================================

Here's exactly what you need to change in your notebook.
"""

print("🔧 EXACT FIX FOR YOUR FLASK APP CELL:")
print("=" * 50)
print()
print("📍 LOCATION: Flask app cell (starts with '# Flask app initialization')")
print()
print("🔍 FIND THIS CODE:")
print("-" * 30)
print("        if query_text:")
print("            # Query the agent")
print("            response = agent.run(query_text)")
print()
print("✏️  REPLACE WITH:")
print("-" * 30)
print("        if query_text:")
print("            # Query the agent using asyncio.run()")
print("            import asyncio")
print("            response = asyncio.run(agent.run(query_text))")
print()
print("🎯 ALSO UPDATE THE PORT:")
print("-" * 30)
print("FIND: app.run(host=\"0.0.0.0\", port=5602)")
print("REPLACE: app.run(host=\"0.0.0.0\", port=5606)")
print()
print("✅ COMPLETE FIXED CODE SECTION:")
print("-" * 30)
print("""
# Home route
@app.route("/", methods=["GET", "POST"])
def home():
    response = None
    if request.method == "POST":
        query_text = request.form.get("text", "")
        if query_text:
            # Query the agent using asyncio.run()
            import asyncio
            response = asyncio.run(agent.run(query_text))
    return render_template_string(form_template, response=response)
""")
print()
print("🧪 AFTER THE FIX:")
print("-" * 30)
print("1. Save the notebook")
print("2. Run the Flask app cell")
print("3. Test with queries - should work without async errors!")
print("4. Access at http://localhost:5606")
