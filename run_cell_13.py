#!/usr/bin/env python3
"""
Run Cell 13 from NSO Multi-Agent Notebook
==========================================

This script runs the specific cell 13 that contains NSO imports
with proper environment setup.
"""

import os
import sys
import subprocess

def setup_nso_environment():
    """Setup NSO environment variables"""
    print("🔧 Setting up NSO environment...")
    
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
    print(f"   - DYLD_LIBRARY_PATH: {os.environ.get('DYLD_LIBRARY_PATH')}")

def run_cell_13():
    """Run the code from cell 13"""
    print("\n📱 Running Cell 13 - NSO Imports and Connection...")
    
    try:
        # Import NSO modules
        print("📦 Importing NSO modules...")
        import ncs
        print("✅ ncs imported successfully")
        
        import ncs.maapi as maapi
        print("✅ ncs.maapi imported successfully")
        
        import ncs.maagic as maagic
        print("✅ ncs.maagic imported successfully")
        
        # Additional imports from cell 13
        import io
        import sys
        import re
        import os
        print("✅ Additional modules imported successfully")
        
        # Create MAAPI connection
        print("\n🔌 Creating NSO connection...")
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
        print("\n📱 Testing device discovery...")
        devices = []
        for device in root.devices.device:
            devices.append(device.name)
        
        print(f"✅ Found {len(devices)} devices: {devices}")
        
        # Keep connection open for further use
        print("\n✅ Cell 13 executed successfully!")
        print("🔗 NSO connection is ready for use")
        print("ℹ️  Connection objects: m (MAAPI), t (Transaction), root (Root)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error running cell 13: {e}")
        return False

def main():
    """Main execution function"""
    print("🚀 Running Cell 13 from NSO Multi-Agent Notebook")
    print("=" * 55)
    
    # Setup environment
    setup_nso_environment()
    
    # Run cell 13
    success = run_cell_13()
    
    if success:
        print("\n🎉 Cell 13 completed successfully!")
        print("✅ NSO imports and connection are working correctly")
        print("\n💡 You can now run this cell in Jupyter with the same environment setup")
    else:
        print("\n❌ Cell 13 failed")
        print("🔧 Please check the NSO installation and environment setup")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
