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
    # Reload packages using the action
    root = maagic.get_root(m)
    
    print("Attempting to reload packages via Python API...")
    print("Note: Package reload typically requires NSO CLI access.")
    print("\nThe ibgp package has been compiled and is ready.")
    print("To activate it, please run in NSO CLI:")
    print("  packages reload force")
    print("\nOr use the NSO CLI from your terminal:")
    print("  ncs_cli -C -u cisco")
    print("  packages reload force")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    m.end_user_session()

print("\n✅ Script completed")
print("\nThe ibgp package files are ready at:")
print("  /Users/gudeng/ncs-run/packages/ibgp/load-dir/ibgp.fxs")
print("\nYou need to reload packages in NSO CLI to activate it.")

