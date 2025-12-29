#!/usr/bin/env python3
"""Delete all iBGP services"""

import os
import sys

# Set NSO environment variables
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

def main():
    print("=" * 80)
    print("Delete All iBGP Services")
    print("=" * 80)
    
    try:
        m = maapi.Maapi()
        m.start_user_session('cisco', 'test_context_1')
        t = m.start_write_trans()
        root = maagic.get_root(t)
        
        # Access iBGP service
        try:
            services = root.ibgp__ibgp
            print(f"\n✅ Found iBGP service package")
            
            # Get all service instance names
            service_names = list(services.keys())
            print(f"📋 Found {len(service_names)} iBGP service instance(s): {service_names}")
            
            # Delete each service
            for service_name in service_names:
                try:
                    del services[service_name]
                    print(f"✅ Deleted iBGP service: {service_name}")
                except Exception as e:
                    print(f"❌ Error deleting service {service_name}: {e}")
            
            # Apply changes
            t.apply()
            print(f"\n✅ All iBGP services deleted successfully")
            
        except AttributeError:
            print("❌ Error: iBGP service package not loaded")
        except Exception as e:
            print(f"❌ Error accessing iBGP services: {e}")
        
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

