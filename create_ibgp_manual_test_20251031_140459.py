#!/usr/bin/env python3
"""Manual iBGP service creation test using MAAPI directly"""

import os
import sys
import time
import traceback

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

def create_ibgp_service_manual():
    """Create iBGP service manually using MAAPI"""
    m = None
    try:
        print("=" * 60)
        print("Manual iBGP Service Creation Test")
        print("=" * 60)
        print()
        
        overall_start = time.time()
        print("[STEP 1/8] Creating MAAPI connection...")
        step_start = time.time()
        print(f"   Timestamp: {time.strftime('%H:%M:%S')}")
        m = maapi.Maapi()
        elapsed = time.time() - step_start
        print(f"✅ [STEP 1/8] MAAPI connection created (took {elapsed:.2f}s)")
        print()
        
        print("[STEP 2/8] Starting user session...")
        step_start = time.time()
        print(f"   Timestamp: {time.strftime('%H:%M:%S')}")
        print(f"   Calling: m.start_user_session('cisco', 'test_context_1')")
        m.start_user_session('cisco', 'test_context_1')
        elapsed = time.time() - step_start
        print(f"✅ [STEP 2/8] User session started (took {elapsed:.2f}s)")
        print()
        
        print("[STEP 3/8] Starting write transaction...")
        step_start = time.time()
        print(f"   Timestamp: {time.strftime('%H:%M:%S')}")
        print(f"   Calling: m.start_write_trans()")
        t = m.start_write_trans()
        elapsed = time.time() - step_start
        print(f"✅ [STEP 3/8] Write transaction started (took {elapsed:.2f}s)")
        print()
        
        print("[STEP 4/8] Getting root object...")
        start_time = time.time()
        root = maagic.get_root(t)
        elapsed = time.time() - start_time
        print(f"✅ [STEP 4/8] Root object obtained (took {elapsed:.2f}s)")
        print()
        
        # Validate routers exist
        print("[STEP 5/8] Validating routers exist...")
        start_time = time.time()
        router1 = 'xr9kv-1'
        router2 = 'xr9kv-2'
        
        if router1 not in root.devices.device:
            print(f"❌ [STEP 5/8] Router '{router1}' not found")
            m.end_user_session()
            return False
        
        if router2 not in root.devices.device:
            print(f"❌ [STEP 5/8] Router '{router2}' not found")
            m.end_user_session()
            return False
        
        elapsed = time.time() - start_time
        print(f"✅ [STEP 5/8] Both routers validated: {router1}, {router2} (took {elapsed:.2f}s)")
        print()
        
        # Access iBGP service
        print("[STEP 6/8] Accessing iBGP service package...")
        start_time = time.time()
        try:
            services = root.ibgp__ibgp
            elapsed = time.time() - start_time
            print(f"✅ [STEP 6/8] iBGP service package accessed (took {elapsed:.2f}s)")
        except AttributeError as e:
            elapsed = time.time() - start_time
            print(f"❌ [STEP 6/8] iBGP service package not loaded: {e} (took {elapsed:.2f}s)")
            m.end_user_session()
            return False
        print()
        
        # Create service instance
        service_name = 'peer1-2'
        print(f"[STEP 7/8] Creating/updating service instance '{service_name}'...")
        start_time = time.time()
        
        if service_name in services:
            svc = services[service_name]
            print(f"ℹ️ [STEP 7/8] Service '{service_name}' already exists, updating...")
        else:
            print(f"[STEP 7/8] Creating new service instance...")
            svc = services.create(service_name)
            print(f"✅ [STEP 7/8] Created new iBGP service instance")
        
        print(f"[STEP 7/8] Setting service parameters...")
        # Set service parameters
        svc.as_number = 65000
        svc.router1 = router1
        svc.router1_lo0_ip = '1.1.1.1'
        svc.router1_router_id = '1.1.1.1'
        svc.router2 = router2
        svc.router2_lo0_ip = '1.1.1.2'
        svc.router2_router_id = '1.1.1.2'
        
        elapsed = time.time() - start_time
        print(f"✅ [STEP 7/8] Service parameters set (took {elapsed:.2f}s)")
        print()
        
        # Apply changes
        print("[STEP 8/8] Applying transaction (this may take a moment)...")
        step_start = time.time()
        print(f"   Timestamp: {time.strftime('%H:%M:%S')}")
        print(f"   Calling: t.apply()")
        sys.stdout.flush()  # Force output before potentially blocking call
        t.apply()
        elapsed = time.time() - step_start
        print(f"✅ [STEP 8/8] Transaction applied successfully (took {elapsed:.2f}s)")
        print()
        
        print("[CLEANUP] Closing user session...")
        m.end_user_session()
        print("✅ User session closed")
        print()
        
        print("=" * 60)
        print("✅ SUCCESS: iBGP service created successfully!")
        print("=" * 60)
        print(f"Service: {service_name}")
        print(f"AS Number: 65000")
        print(f"Router1: {router1} (Lo0: 1.1.1.1)")
        print(f"Router2: {router2} (Lo0: 1.1.1.2)")
        print()
        total_time = time.time() - overall_start
        print(f"Total time: {total_time:.2f} seconds")
        
        return True
        
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        print()
        print("=" * 60)
        print(f"❌ ERROR: {error_type}: {error_msg}")
        print("=" * 60)
        print()
        print("Full traceback:")
        traceback.print_exc()
        print()
        
        # Try to clean up
        if m:
            try:
                print("Attempting to clean up session...")
                m.end_user_session()
                print("✅ Session cleaned up")
            except Exception as cleanup_error:
                print(f"⚠️  Could not clean up session: {cleanup_error}")
        
        return False

if __name__ == "__main__":
    success = create_ibgp_service_manual()
    sys.exit(0 if success else 1)


