#!/usr/bin/env python3
"""
Fixed Flask App for NSO Multi-Agent
===================================

This is the Flask app from your notebook with the async fix applied.
"""

# Import all the necessary modules from your notebook
import os
import sys
import asyncio
import logging
from flask import Flask, request, render_template_string, redirect, url_for

# Set up logging
logging.basicConfig(
    stream=sys.stdout, level=logging.INFO
)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# Set NSO environment variables (same as your notebook)
NSO_DIR = "/Users/gudeng/NCS-614"
os.environ['NCS_DIR'] = NSO_DIR
os.environ['DYLD_LIBRARY_PATH'] = f'{NSO_DIR}/lib'
os.environ['PYTHONPATH'] = f'{NSO_DIR}/src/ncs/pyapi'

# Add NSO Python API to Python path
nso_pyapi_path = f'{NSO_DIR}/src/ncs/pyapi'
if nso_pyapi_path not in sys.path:
    sys.path.insert(0, nso_pyapi_path)

# Import NSO modules
import ncs
import ncs.maapi as maapi
import ncs.maagic as maagic

# Import LlamaIndex modules
from llama_index.core.agent import ReActAgent
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.core.tools import FunctionTool
from llama_index.core import Settings

# Import your environment variables
from dotenv import load_dotenv
load_dotenv()

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
token_url = os.getenv('TOKEN_URL')
llm_endpoint = os.getenv('LLM_ENDPOINT')
appkey = os.getenv('APP_KEY')

# Initialize NSO connection
m = maapi.Maapi()
m.start_user_session('admin','test_context_1')
t = m.start_write_trans()
root = maagic.get_root(t)

# Get Cisco OAuth token
import base64
import requests
import json

auth_key = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("utf-8")
headers = {
    "Accept": "*/*",
    "Content-Type": "application/x-www-form-urlencoded",
    "Authorization": f"Basic {auth_key}",
}

token_response = requests.post(token_url, headers=headers, data="grant_type=client_credentials")
token = token_response.json().get("access_token")

# Initialize LLM
llm = AzureOpenAI(
    azure_endpoint=llm_endpoint,
    api_version="2024-07-01-preview",
    deployment_name='gpt-4o-mini',
    api_key=token,
    max_tokens=3000,
    temperature=0.1,
    additional_kwargs={"user": f'{{"appkey": "{appkey}"}}'}
)

Settings.llm = llm
Settings.context_window = 8000

# Define your NSO functions (simplified versions)
def show_all_devices():
    """Find out all available routers in the lab"""
    if hasattr(root, 'devices') and hasattr(root.devices, 'device'):
        router_names = [device.name for device in root.devices.device]
        for name in router_names:
            print(name)
        return ', '.join(router_names)
    else:
        print("No devices found.")
        return "No devices found."

def execute_command_on_router(router_name, command):
    """Execute a single command on a specific router using NSO"""
    try:
        with ncs.maapi.single_write_trans('admin', 'python', groups=['ncsadmin']) as t:
            root = ncs.maagic.get_root(t)
            device = root.devices.device[router_name]
            show = device.live_status.__getitem__('exec').any
            inp = show.get_input()
            inp.args = [command]
            r = show.request(inp)
            result = f'Result of Show Command "{command}" for Router "{router_name}": {r.result}'
            print(result)
            return result
    except KeyError:
        error_msg = f"Device '{router_name}' not found in NSO."
        print(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Failed to execute command '{command}' on device '{router_name}': {e}"
        print(error_msg)
        return error_msg

def get_router_version(router_name):
    """Get router version"""
    command = "show version"
    return execute_command_on_router(router_name, command)

def iterate_devices_AND_cmd(cmd):
    """Execute a command on all devices"""
    results = []
    with ncs.maapi.single_write_trans('admin', 'python', groups=['ncsadmin']) as t:
        root = ncs.maagic.get_root(t)
        for box in root.devices.device:
            try:
                show = box.live_status.__getitem__('exec').any
                inp = show.get_input()
                inp.args = [cmd]
                r = show.request(inp)
                show_cmd = 'Result of Show Command "{}" for Router Name {}: {}'.format(cmd, box.name, r.result)
                print(show_cmd)
                results.append(show_cmd)
            except Exception as e:
                print(f"Failed to execute command '{cmd}' on device {box.name}: {e}")
    return results

# Create tools
all_router_tool = FunctionTool.from_defaults(fn=show_all_devices)
version_tool = FunctionTool.from_defaults(fn=get_router_version)
iterate_tool = FunctionTool.from_defaults(fn=iterate_devices_AND_cmd)

# Create tools list
List_Tools = [all_router_tool, version_tool, iterate_tool]

# Create agent
agent = ReActAgent(
    tools=List_Tools,
    llm=llm,
    verbose=True,
    max_iterations=1000
)

# Flask app
app = Flask(__name__)

# HTML template
form_template = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Query Interface</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 20px;
    }
    h1 {
      font-size: 24px;
      color: #333;
    }
    form {
      margin-bottom: 20px;
    }
    textarea {
      width: 100%;
      height: 50px;
      padding: 10px;
      font-size: 16px;
      border: 1px solid #ccc;
      border-radius: 4px;
      resize: none;
    }
    input[type="submit"] {
      padding: 10px 20px;
      background-color: #4CAF50;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 16px;
    }
    input[type="submit"]:hover {
      background-color: #45a049;
    }
    pre {
      background-color: #f4f4f4;
      padding: 15px;
      border-radius: 4px;
      white-space: pre-wrap;
      word-wrap: break-word;
      font-family: 'Courier New', Courier, monospace;
      font-size: 14px;
      color: #333;
    }
  </style>
</head>
<body>
  <h1>Query the Agent</h1>
  <form action="/" method="post">
    <textarea name="text" placeholder="Enter your query here" required></textarea>
    <br><br>
    <input type="submit" value="Submit">
  </form>
  {% if response %}
    <h2>Response:</h2>
    <pre>{{ response }}</pre>
  {% endif %}
</body>
</html>
"""

# Home route with THREAD-BASED ASYNC FIX
@app.route("/", methods=["GET", "POST"])
def home():
    response = None
    if request.method == "POST":
        query_text = request.form.get("text", "")
        if query_text:
            # Query the agent using thread-based approach - THIS IS THE FIX!
            try:
                import concurrent.futures
                
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
                
                response = run_agent_in_thread(query_text)
                print(f"✅ Agent response: {response}")
            except Exception as e:
                response = f"Error processing query: {str(e)}"
                print(f"❌ Error: {e}")
    return render_template_string(form_template, response=response)

if __name__ == "__main__":
    print("🚀 Starting Fixed Flask App")
    print("🔧 Async fix applied: using asyncio.run(agent.run())")
    print("🌐 Access: http://localhost:5606")
    print("🔒 Press CTRL+C to stop")
    
    # Run on port 5606 as requested
    app.run(host="0.0.0.0", port=5606, debug=True)
