#!/usr/bin/env python3
"""Delete OSPF link service instances using MCP tool pattern"""

import os
import sys

# Set NSO environment variables (same as MCP tools)
NSO_DIR = "/Users/gudeng/NCS-614"
os.environ['NCS_DIR'] = NSO_DIR
os.environ['DYLD_LIBRARY_PATH'] = f'{NSO_DIR}/lib'
os.environ['PYTHONPATH'] = f'{NSO_DIR}/src/ncs/pyapi'

# Add NSO Python API to Python path
nso_pyapi_path = f'{NSO_DIR}/src/ncs/pyapi'
if nso_pyapi_path not in sys.path:
    sys.path.insert(0, nso_pyapi_path)

# Import NSO modules (same as MCP tools)
import ncs
import ncs.maapi as maapi
import ncs.maagic as maagic

def main():
    print("="*80)
    print("Delete OSPF Link Service Instances (MCP Tool Style)")
    print("="*80)
    
    try:
        # Use same pattern as MCP tools
        m = maapi.Maapi()
        m.start_user_session('cisco', 'test_context_1')
        t = m.start_write_trans()
        root = maagic.get_root(t)
        
        # Check if OSPF service package exists
        if hasattr(root, 'ospf') and hasattr(root.ospf, 'link'):
            link_keys = list(root.ospf.link.keys())
            
            if link_keys:
                print(f"\n📋 Found {len(link_keys)} OSPF link(s):")
                for link_key in link_keys:
                    print(f"  - {link_key}")
                
                print("\n🗑️  Deleting OSPF links...")
                for link_key in link_keys:
                    try:
                        del root.ospf.link[link_key]
                        print(f"  ✅ Deleted link: {link_key}")
                    except Exception as e:
                        print(f"  ❌ Error deleting link {link_key}: {e}")
                
                # Apply changes (same as MCP tools)
                t.apply()
                print("\n✅ All OSPF links deleted from NSO database")
                print("   Note: Use NSO CLI 'commit' command to push to routers")
            else:
                print("\n✅ No OSPF links found")
        else:
            print("\n✅ No OSPF link service container found")
        
        m.end_user_session()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        try:
            m.end_user_session()
        except:
            pass

if __name__ == "__main__":
    main()

