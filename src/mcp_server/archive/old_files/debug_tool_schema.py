#!/usr/bin/env python3
"""
Debug LlamaIndex Tool Schema
"""

from llama_index.core.tools import FunctionTool

def test_function():
    return "test"

# Create a tool with schema
tool = FunctionTool.from_defaults(
    fn=test_function,
    name="test_tool",
    description="Test tool",
    fn_schema={
        "type": "object",
        "properties": {
            "param": {"type": "string"}
        },
        "required": ["param"]
    }
)

print("Tool metadata:")
print(f"  Name: {tool.metadata.name}")
print(f"  Description: {tool.metadata.description}")
print(f"  fn_schema type: {type(tool.metadata.fn_schema)}")
print(f"  fn_schema value: {tool.metadata.fn_schema}")
print(f"  fn_schema dict: {tool.metadata.fn_schema.__dict__ if hasattr(tool.metadata.fn_schema, '__dict__') else 'No __dict__'}")
print(f"  fn_schema dir: {[attr for attr in dir(tool.metadata.fn_schema) if not attr.startswith('_')]}")
