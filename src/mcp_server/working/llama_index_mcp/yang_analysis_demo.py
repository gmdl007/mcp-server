#!/usr/bin/env python3
"""
YANG Model Analysis Demo

This script demonstrates the complete YANG model analysis and MCP tool generation
capabilities for NSO service models.
"""

import os
import sys
from typing import Dict, List, Any

# Add the current directory to Python path
sys.path.append('/Users/gudeng/MCP_Server/src/mcp_server/working/llama_index_mcp')

from universal_yang_analyzer import YangModelAnalyzer, analyze_yang_model_from_file
from nso_runtime_analyzer import NSORuntimeModelAnalyzer
from ospf_tool_generator import generate_ospf_service_tools

def demonstrate_yang_analysis():
    """Demonstrate YANG model analysis capabilities."""
    
    print("🔍 YANG Model Analysis and MCP Tool Generation Demo")
    print("=" * 60)
    
    # 1. NSO Runtime Analysis
    print("\n1️⃣ NSO Runtime Model Analysis")
    print("-" * 40)
    
    runtime_analyzer = NSORuntimeModelAnalyzer()
    runtime_analysis = runtime_analyzer.analyze_nso_runtime()
    
    print(f"✅ Found {len(runtime_analysis.get('services', {}))} services:")
    for service_name, service_info in runtime_analysis.get('services', {}).items():
        print(f"   - {service_name}: {len(service_info.get('parameters', []))} parameters")
    
    print(f"✅ Found {len(runtime_analysis.get('device_configs', {}))} device configs:")
    for config_name, config_info in runtime_analysis.get('device_configs', {}).items():
        print(f"   - {config_name}: {len(config_info.get('parameters', []))} parameters")
    
    # 2. OSPF Service Analysis
    print("\n2️⃣ OSPF Service Analysis")
    print("-" * 40)
    
    ospf_tools = generate_ospf_service_tools()
    print(f"✅ Generated {len(ospf_tools)} OSPF service tools:")
    for tool in ospf_tools:
        print(f"   - {tool['name']}: {tool['description']}")
    
    # 3. YANG Model Analysis
    print("\n3️⃣ YANG Model Analysis")
    print("-" * 40)
    
    yang_analyzer = YangModelAnalyzer()
    
    # Find YANG models
    ncs_path = os.path.expanduser("~/NCS-614")
    yang_files = {}
    
    # Search for YANG files
    for root, dirs, files in os.walk(ncs_path):
        for file in files:
            if file.endswith('.yang'):
                full_path = os.path.join(root, file)
                yang_files[file] = full_path
    
    print(f"✅ Found {len(yang_files)} YANG models in NSO installation")
    
    # Analyze a few key models
    key_models = [
        'tailf-ned-cisco-nx-router-ospf.yang',
        'tailf-ncs-services.yang'
    ]
    
    for model_file in key_models:
        if model_file in yang_files:
            print(f"\n📋 Analyzing {model_file}:")
            result = analyze_yang_model_from_file(yang_files[model_file])
            
            if result:
                model = result['model']
                tools = result['tools']
                
                print(f"   - Model: {model.name}")
                print(f"   - Containers: {len(model.containers)}")
                print(f"   - Lists: {len(model.lists)}")
                print(f"   - RPCs: {len(model.rpcs)}")
                print(f"   - Generated {len(tools)} MCP tools")
                
                # Show first few tools
                for i, tool in enumerate(tools[:3]):
                    print(f"     • {tool['name']}: {tool['description']}")
                if len(tools) > 3:
                    print(f"     • ... and {len(tools) - 3} more tools")
    
    # 4. Generated Files Summary
    print("\n4️⃣ Generated Files Summary")
    print("-" * 40)
    
    generated_files = [
        "/Users/gudeng/MCP_Server/src/mcp_server/working/llama_index_mcp/auto_generated_nso_tools.py",
        "/Users/gudeng/MCP_Server/src/mcp_server/working/llama_index_mcp/auto_generated_ospf_tools.py",
        "/Users/gudeng/MCP_Server/src/mcp_server/working/llama_index_mcp/auto_generated_tailf-ned-cisco-nx-router-ospf_tools.py"
    ]
    
    for file_path in generated_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✅ {os.path.basename(file_path)}: {file_size:,} bytes")
        else:
            print(f"❌ {os.path.basename(file_path)}: Not found")
    
    # 5. Usage Examples
    print("\n5️⃣ Usage Examples")
    print("-" * 40)
    
    print("""
🔧 How to Use YANG Model Analysis:

1. **For NSO Runtime Analysis:**
   ```python
   from nso_runtime_analyzer import NSORuntimeModelAnalyzer
   analyzer = NSORuntimeModelAnalyzer()
   analysis = analyzer.analyze_nso_runtime()
   tools = analyzer.generate_mcp_tools_from_analysis(analysis)
   ```

2. **For YANG Model Analysis:**
   ```python
   from universal_yang_analyzer import analyze_yang_model_from_file
   result = analyze_yang_model_from_file('path/to/model.yang')
   tools = result['tools']
   python_code = result['python_code']
   ```

3. **For Service-Specific Tools:**
   ```python
   from ospf_tool_generator import generate_ospf_service_tools
   ospf_tools = generate_ospf_service_tools()
   ```

4. **Integration with FastMCP:**
   ```python
   from fastmcp import FastMCP
   mcp = FastMCP("NSO Server")
   
   # Register generated tools
   for tool in generated_tools:
       mcp.tool(tool['function_name'])
   ```
    """)
    
    # 6. Benefits and Capabilities
    print("\n6️⃣ Benefits and Capabilities")
    print("-" * 40)
    
    benefits = [
        "🔍 **Automatic Discovery**: Analyzes NSO runtime to discover all available services",
        "📋 **YANG Model Parsing**: Parses any YANG model to understand structure and parameters",
        "🛠️ **Tool Generation**: Automatically generates MCP tools based on model structure",
        "🔧 **Parameter Extraction**: Extracts all configuration parameters with types and descriptions",
        "📝 **Code Generation**: Generates complete Python code for MCP tools",
        "🎯 **Service-Specific**: Creates specialized tools for specific services (e.g., OSPF)",
        "🔄 **Runtime Analysis**: Analyzes actual NSO runtime model structure",
        "📊 **Comprehensive Coverage**: Handles containers, lists, RPCs, and parameters"
    ]
    
    for benefit in benefits:
        print(f"   {benefit}")
    
    print("\n🎉 YANG Model Analysis Demo Complete!")
    print("=" * 60)

def create_yang_model_example():
    """Create an example YANG model for demonstration."""
    
    example_yang = """
module example-service {
    namespace "http://example.com/ns/example-service";
    prefix ex-svc;
    
    description "Example service model for demonstration";
    
    container service {
        description "Example service configuration";
        
        leaf service-name {
            type string;
            description "Name of the service instance";
            mandatory true;
        }
        
        leaf service-id {
            type uint32;
            description "Unique service identifier";
            default 1;
        }
        
        leaf enabled {
            type boolean;
            description "Whether the service is enabled";
            default true;
        }
        
        list endpoint {
            key "address";
            description "Service endpoints";
            
            leaf address {
                type string;
                description "Endpoint IP address";
            }
            
            leaf port {
                type uint16;
                description "Endpoint port number";
                default 80;
            }
            
            leaf protocol {
                type enumeration {
                    enum "http";
                    enum "https";
                    enum "tcp";
                    enum "udp";
                }
                description "Protocol type";
                default "http";
            }
        }
        
        container authentication {
            description "Authentication configuration";
            
            leaf method {
                type enumeration {
                    enum "none";
                    enum "basic";
                    enum "oauth2";
                    enum "jwt";
                }
                description "Authentication method";
                default "none";
            }
            
            leaf username {
                type string;
                description "Username for authentication";
            }
            
            leaf password {
                type string;
                description "Password for authentication";
            }
        }
    }
    
    rpc start-service {
        description "Start the service";
        
        input {
            leaf service-name {
                type string;
                description "Name of service to start";
                mandatory true;
            }
        }
        
        output {
            leaf status {
                type string;
                description "Service start status";
            }
        }
    }
    
    rpc stop-service {
        description "Stop the service";
        
        input {
            leaf service-name {
                type string;
                description "Name of service to stop";
                mandatory true;
            }
        }
        
        output {
            leaf status {
                type string;
                description "Service stop status";
            }
        }
    }
}
"""
    
    # Save example YANG model
    example_file = "/Users/gudeng/MCP_Server/src/mcp_server/working/llama_index_mcp/example-service.yang"
    with open(example_file, 'w') as f:
        f.write(example_yang)
    
    print(f"📝 Created example YANG model: {example_file}")
    
    # Analyze the example model
    print("\n🔍 Analyzing example YANG model:")
    result = analyze_yang_model_from_file(example_file)
    
    if result:
        model = result['model']
        tools = result['tools']
        
        print(f"   - Model: {model.name}")
        print(f"   - Description: {model.description}")
        print(f"   - Containers: {len(model.containers)}")
        print(f"   - Lists: {len(model.lists)}")
        print(f"   - RPCs: {len(model.rpcs)}")
        print(f"   - Generated {len(tools)} MCP tools")
        
        for tool in tools:
            print(f"     • {tool['name']}: {tool['description']}")
        
        # Save generated code
        output_file = f"/Users/gudeng/MCP_Server/src/mcp_server/working/llama_index_mcp/auto_generated_{model.name}_tools.py"
        with open(output_file, 'w') as f:
            f.write(result['python_code'])
        
        print(f"\n💾 Generated Python code saved to: {output_file}")

if __name__ == "__main__":
    demonstrate_yang_analysis()
    print("\n" + "="*60)
    create_yang_model_example()
