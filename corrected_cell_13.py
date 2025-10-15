#!/usr/bin/env python3
"""
Corrected Cell 13 for NSO Multi-Agent Notebook
===============================================

This script provides the corrected code for cell 13 that properly sets up
the NSO environment using Python instead of shell commands.
"""

# =============================================================================
# CORRECTED CELL 13 CODE
# =============================================================================

def setup_nso_environment():
    """Setup NSO environment variables using Python"""
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
    
    print(f"✅ NSO environment configured:")
    print(f"   - NCS_DIR: {NSO_DIR}")
    print(f"   - PYTHONPATH: {nso_pyapi_path}")

# Setup NSO environment
setup_nso_environment()

# Import NSO modules
import ncs
import ncs.maapi as maapi
import ncs.maagic as maagic
import io
import sys
import re
import os

print("✅ NSO modules imported successfully")

# Create MAAPI connection
m = maapi.Maapi()
print("✅ MAAPI object created")

# Start user session
m.start_user_session('admin', 'test_context_1')
print("✅ User session started")

# Start transaction
t = m.start_write_trans()
print("✅ Write transaction started")

# Get root object
root = maagic.get_root(t)
print("✅ Root object obtained")

# Test device discovery
devices = []
for device in root.devices.device:
    devices.append(device.name)

print(f"📱 Found {len(devices)} devices: {devices}")

print("\n🎉 Cell 13 completed successfully!")
print("🔗 NSO connection is ready for use")
print("ℹ️  Available objects: m (MAAPI), t (Transaction), root (Root)")

# =============================================================================
# INSTRUCTIONS FOR JUPYTER NOTEBOOK
# =============================================================================

print("\n" + "="*60)
print("📝 INSTRUCTIONS FOR JUPYTER NOTEBOOK:")
print("="*60)
print("""
To fix the import error in cell 13 of your Jupyter notebook:

1. Replace the shell commands (!) with Python code:

   REMOVE THESE LINES:
   !eval "$(/Users/gudeng/miniforge3/bin/conda shell.zsh hook)"
   !conda activate base
   !export DYLD_LIBRARY_PATH=""
   !export PYTHONPATH=""
   !source /Users/gudeng/NCS-614/ncsrc

   REPLACE WITH THIS PYTHON CODE:
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

2. The rest of the cell (imports and connection) should work fine.

3. Make sure to restart the Jupyter kernel after making changes.

4. Run the cell again - it should work without import errors.
""")

if __name__ == "__main__":
    print("✅ Corrected cell 13 code executed successfully!")
