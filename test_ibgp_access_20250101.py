#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, '/Users/gudeng/NCS-614/src/ncs/pyapi')
os.environ['NCS_DIR'] = '/Users/gudeng/NCS-614'
from ncs import maapi, maagic

print("=== Testing iBGP Service Access Methods ===\n")

m = maapi.Maapi()
m.start_user_session('cisco', 'test_context_1')
t = m.start_read_trans()
root = maagic.get_root(t)

try:
    # Try different access methods
    print("Method 1: Direct attribute access")
    try:
        svc = root.ibgp__ibgp
        print(f"✅ Success! Type: {type(svc)}, Length: {len(svc)}")
    except AttributeError as e:
        print(f"❌ Failed: {e}")
    
    print("\nMethod 2: getattr")
    try:
        svc = getattr(root, 'ibgp__ibgp')
        print(f"✅ Success! Type: {type(svc)}, Length: {len(svc)}")
    except AttributeError as e:
        print(f"❌ Failed: {e}")
    
    print("\nMethod 3: Dictionary access")
    try:
        svc = root.__dict__['ibgp__ibgp']
        print(f"✅ Success! Type: {type(svc)}")
    except (KeyError, AttributeError) as e:
        print(f"❌ Failed: {e}")
    
    print("\nMethod 4: Using maagic.get_node")
    try:
        from ncs.maagic import get_node
        svc = get_node(t, '/ibgp:ibgp/ibgp')
        print(f"✅ Success! Type: {type(svc)}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    print("\nMethod 5: List all root attributes matching ibgp")
    attrs = [a for a in dir(root) if 'ibgp' in a.lower() and not a.startswith('_')]
    print(f"Found attributes: {attrs}")
    
    m.end_user_session()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    try:
        m.end_user_session()
    except:
        pass

