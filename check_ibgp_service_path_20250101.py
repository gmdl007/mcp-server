#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, '/Users/gudeng/NCS-614/src/ncs/pyapi')
os.environ['NCS_DIR'] = '/Users/gudeng/NCS-614'
from ncs import maapi, maagic

print("=== Checking iBGP Service Path ===\n")

m = maapi.Maapi()
m.start_user_session('cisco', 'test_context_1')
t = m.start_read_trans()
root = maagic.get_root(t)

try:
    print("Checking root attributes...")
    attrs = dir(root)
    
    # Check for ibgp
    if 'ibgp' in attrs:
        print("✅ Found 'ibgp' attribute in root")
        ibgp_obj = root.ibgp
        print(f"  Type: {type(ibgp_obj)}")
        print(f"  Attributes: {[a for a in dir(ibgp_obj) if not a.startswith('_')]}")
        
        if hasattr(ibgp_obj, 'ibgp'):
            print("  ✅ Found 'ibgp' list in ibgp container")
            services = ibgp_obj.ibgp
            print(f"  Number of services: {len(services)}")
    else:
        print("❌ 'ibgp' not found in root")
        print("\nAvailable root attributes (filtered):")
        service_attrs = [a for a in attrs if not a.startswith('_') and a not in ['apply', 'commit', 'delete', 'validate', 'exists']]
        for attr in sorted(service_attrs)[:20]:
            print(f"  - {attr}")
    
    # Check services container
    if hasattr(root, 'services'):
        print("\n✅ Found 'services' container")
        services = root.services
        print(f"  Type: {type(services)}")
        attrs_services = [a for a in dir(services) if not a.startswith('_')]
        print(f"  Attributes: {attrs_services[:10]}")
    
    m.end_user_session()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    try:
        m.end_user_session()
    except:
        pass

