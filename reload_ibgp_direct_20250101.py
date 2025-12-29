#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, '/Users/gudeng/NCS-614/src/ncs/pyapi')
os.environ['NCS_DIR'] = '/Users/gudeng/NCS-614'
from ncs import maapi, maagic

print("=== Reloading NSO Packages (including ibgp) ===\n")

m = maapi.Maapi()
m.start_user_session('cisco', 'test_context_1')

try:
    # Use operational mode transaction for actions
    t = m.start_write_trans()
    root = maagic.get_root(t)
    
    print("Attempting to reload packages via native action...")
    try:
        # Try the native reload action
        action = root.packages.reload
        inp = action.get_input()
        inp.force = True
        out = action(inp)
        
        # The action doesn't need apply() - it's an action, not a config change
        print("✅ Package reload action invoked successfully!")
        
        # Try to display results
        try:
            if hasattr(out, 'reload_result'):
                print("\nReload results:")
                for rr in out.reload_result:
                    pkg = getattr(rr, 'package', 'unknown')
                    result = getattr(rr, 'result', False)
                    status = "✅" if result else "❌"
                    print(f"  {status} {pkg}: {result}")
                    if hasattr(rr, 'info') and rr.info:
                        print(f"     Info: {rr.info}")
        except Exception as e:
            print(f"Could not parse reload results: {e}")
        
    except AttributeError as e:
        print(f"⚠️  Action not available via API: {e}")
        print("\nThe ibgp package is compiled and ready.")
        print("Please run 'packages reload force' in your NSO CLI session.")
        print("Make sure to exit configure mode first if you're in it.")
    except Exception as e:
        print(f"❌ Error invoking reload action: {e}")
        import traceback
        traceback.print_exc()
        print("\nThe ibgp package is compiled and ready.")
        print("Please run 'packages reload force' manually in NSO CLI.")
    
    m.end_user_session()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    try:
        m.end_user_session()
    except:
        pass

print("\n✅ Script completed")

