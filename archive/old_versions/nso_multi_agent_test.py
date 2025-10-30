#!/usr/bin/env python3
"""
NSO Multi-Agent Test Application
===============================

A test version of the NSO Multi-Agent application that can run without NSO
for testing the web interface and basic functionality.

Author: AI Assistant
Version: 2.0-test
Date: 2025-01-15
"""

import os
import sys
import json
import base64
import requests
import logging
import asyncio
import nest_asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# =============================================================================
# CONFIGURATION
# =============================================================================

# Web Application Configuration
WEB_HOST = "0.0.0.0"
WEB_PORT = 5606
DEBUG_MODE = False

# =============================================================================
# LOGGING SETUP
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('nso_multi_agent_test.log')
    ]
)
logger = logging.getLogger(__name__)

# =============================================================================
# MOCK NSO FUNCTION TOOLS
# =============================================================================

class MockNSOFunctionTools:
    """Mock NSO function tools for testing without NSO."""
    
    def __init__(self):
        self.devices = ['xr9kv-1', 'xr9kv-2', 'xr9kv-3']
        logger.info("✅ Mock NSO function tools initialized")
    
    def show_all_devices(self) -> List[str]:
        """Mock device discovery."""
        logger.info(f"📱 Mock: Found {len(self.devices)} devices: {self.devices}")
        return self.devices
    
    def get_device_info(self, device_name: str) -> Dict[str, Any]:
        """Mock device information."""
        return {
            "name": device_name,
            "oper_state": "connected",
            "address": "127.0.0.1",
            "port": 830,
            "authgroup": "default",
            "device_type": "cisco-iosxr",
            "ned_id": "cisco-iosxr-cli-7.52",
            "state": {
                "admin-state": "unlocked",
                "oper-state": "in-sync"
            }
        }
    
    def execute_command_on_device(self, device_name: str, command: str) -> str:
        """Mock command execution."""
        if "show version" in command.lower():
            return f"""
Mock output for {device_name}:
Cisco IOS XR Software, Version 7.52
Copyright (c) 2013-2023 by Cisco Systems, Inc.

Build Information:
 Built By     : builder
 Built On     : Wed Oct 11 10:30:00 PDT 2023
 Build Host   : iox-lnx-059
 Workspace    : /auto/srcarchive12/prod/7.52.1/ncs-7.52.1
 Version      : 7.52.1
 Location     : /opt/cisco/XR/packages/
 Label        : 7.52.1

cisco IOS XRv 9000 () processor
System uptime is 0 days 0 hours 0 minutes
"""
        elif "show interfaces" in command.lower():
            return f"""
Mock output for {device_name}:
Interface                      Status         Protocol
GigabitEthernet0/0/0/0        up             up
GigabitEthernet0/0/0/1        up             up
GigabitEthernet0/0/0/2        administratively down down
Loopback0                      up             up
"""
        else:
            return f"Mock output for command '{command}' on {device_name}"

# =============================================================================
# WEB APPLICATION
# =============================================================================

def create_web_app(mock_tools):
    """Create Quart web application."""
    try:
        from quart import Quart, request, jsonify, render_template_string
        
        app = Quart(__name__)
        
        # HTML template for the web interface
        HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NSO Multi-Agent Test Interface</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
        }
        .status {
            background: #e8f5e8;
            border: 1px solid #4caf50;
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #333;
        }
        input[type="text"], textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        textarea {
            height: 100px;
            resize: vertical;
        }
        button {
            background: #007bff;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background: #0056b3;
        }
        .response {
            margin-top: 20px;
            padding: 15px;
            border-radius: 4px;
            white-space: pre-wrap;
            font-family: monospace;
        }
        .success {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        .error {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
        .info {
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            color: #0c5460;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 NSO Multi-Agent Test Interface</h1>
        
        <div class="status">
            <strong>Status:</strong> Test Mode (NSO not connected)<br>
            <strong>Available Devices:</strong> {{ devices|join(', ') }}<br>
            <strong>Mode:</strong> Mock responses for testing
        </div>
        
        <form id="queryForm">
            <div class="form-group">
                <label for="query">Enter your network query:</label>
                <textarea id="query" name="query" placeholder="e.g., Show me all devices, What interfaces are on xr9kv-1?, Execute show version on xr9kv-2"></textarea>
            </div>
            <button type="submit">Send Query</button>
        </form>
        
        <div id="response" class="response" style="display: none;"></div>
    </div>
    
    <script>
        document.getElementById('queryForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const query = document.getElementById('query').value;
            const responseDiv = document.getElementById('response');
            
            if (!query.trim()) {
                alert('Please enter a query');
                return;
            }
            
            responseDiv.style.display = 'block';
            responseDiv.className = 'response info';
            responseDiv.textContent = 'Processing query...';
            
            try {
                const response = await fetch('/query', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ query: query })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    responseDiv.className = 'response success';
                    responseDiv.textContent = data.response || 'Query processed successfully';
                } else {
                    responseDiv.className = 'response error';
                    responseDiv.textContent = data.error || 'An error occurred';
                }
            } catch (error) {
                responseDiv.className = 'response error';
                responseDiv.textContent = 'Network error: ' + error.message;
            }
        });
    </script>
</body>
</html>
        """
        
        @app.route('/')
        async def index():
            devices = mock_tools.show_all_devices()
            return await render_template_string(HTML_TEMPLATE, devices=devices)
        
        @app.route('/health')
        async def health():
            return jsonify({
                "status": "healthy",
                "service": "nso-multi-agent-test",
                "version": "2.0-test",
                "nso_connected": False,
                "mode": "test"
            })
        
        @app.route('/query', methods=['POST'])
        async def query():
            try:
                data = await request.get_json()
                query_text = data.get('query', '').strip()
                
                if not query_text:
                    return jsonify({"error": "No query provided"}), 400
                
                logger.info(f"🔍 Processing query: {query_text}")
                
                # Simple query processing
                response = "Mock response for testing:\n\n"
                
                if "show all devices" in query_text.lower() or "list devices" in query_text.lower() or "all devices" in query_text.lower():
                    devices = mock_tools.show_all_devices()
                    response += f"Found {len(devices)} devices:\n"
                    for device in devices:
                        response += f"- {device}\n"
                
                elif "show version" in query_text.lower():
                    # Extract device name if mentioned
                    device = "xr9kv-1"  # default
                    for d in mock_tools.devices:
                        if d in query_text:
                            device = d
                            break
                    response += mock_tools.execute_command_on_device(device, "show version")
                
                elif "show interfaces" in query_text.lower() or "interfaces" in query_text.lower():
                    device = "xr9kv-1"  # default
                    for d in mock_tools.devices:
                        if d in query_text:
                            device = d
                            break
                    response += mock_tools.execute_command_on_device(device, "show interfaces")
                
                elif "device info" in query_text.lower() or "device information" in query_text.lower():
                    device = "xr9kv-1"  # default
                    for d in mock_tools.devices:
                        if d in query_text:
                            device = d
                            break
                    info = mock_tools.get_device_info(device)
                    response += f"Device Information for {device}:\n"
                    response += json.dumps(info, indent=2)
                
                else:
                    response += f"Mock response to: '{query_text}'\n\n"
                    response += "This is a test mode response. In production, this would be processed by the AI agent.\n"
                    response += "Try queries like:\n"
                    response += "- Show me all devices\n"
                    response += "- Show version on xr9kv-1\n"
                    response += "- What interfaces are on xr9kv-2?\n"
                    response += "- Get device information for xr9kv-3"
                
                logger.info("✅ Query processed successfully")
                return jsonify({"response": response})
                
            except Exception as e:
                logger.error(f"❌ Query processing failed: {e}")
                return jsonify({"error": f"Query processing failed: {str(e)}"}), 500
        
        logger.info("✅ Quart web application created successfully")
        return app
        
    except Exception as e:
        logger.error(f"❌ Failed to create web application: {e}")
        return None

# =============================================================================
# MAIN APPLICATION
# =============================================================================

async def main():
    """Main application entry point."""
    logger.info("🚀 Starting NSO Multi-Agent Test Application")
    logger.info("=" * 60)
    
    # Step 1: Create mock NSO tools
    logger.info("📋 Step 1: Creating mock NSO function tools...")
    mock_tools = MockNSOFunctionTools()
    logger.info("✅ Mock NSO function tools created successfully")
    
    # Step 2: Create web application
    logger.info("📋 Step 2: Creating web application...")
    app = create_web_app(mock_tools)
    if not app:
        logger.error("❌ Failed to create web application. Exiting.")
        return
    
    # Step 3: Start the application
    logger.info("📋 Step 3: Starting web server...")
    logger.info("=" * 60)
    logger.info("🎉 NSO Multi-Agent Test Application Started Successfully!")
    logger.info(f"🌐 Web Interface: http://{WEB_HOST}:{WEB_PORT}")
    logger.info(f"🔍 Health Check: http://{WEB_HOST}:{WEB_PORT}/health")
    logger.info("🔒 Press CTRL+C to stop")
    logger.info("=" * 60)
    
    # Run the Quart application
    await app.run_task(host=WEB_HOST, port=WEB_PORT, debug=DEBUG_MODE)

# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    try:
        # Run the main application
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Application stopped by user")
    except Exception as e:
        logger.error(f"❌ Application failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
