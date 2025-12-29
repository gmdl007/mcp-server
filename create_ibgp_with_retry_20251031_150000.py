#!/usr/bin/env python3
"""Create iBGP service with retry logic using NSO's run_with_retry"""

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
from ncs.maapi import run_with_retry

def create_ibgp_service_with_retry():
    """Create iBGP service using run_with_retry to handle conflicts"""
    m = None
    try:
        print("=" * 60)
        print("iBGP Service Creation with Retry Logic")
        print("=" * 60)
        print()
        
        overall_start = time.time()
        
        print("[STEP 1/7] Creating MAAPI connection...")
        step_start = time.time()
        print(f"   Timestamp: {time.strftime('%H:%M:%S')}")
        m = maapi.Maapi()
        elapsed = time.time() - step_start
        print(f"✅ [STEP 1/7] MAAPI connection created (took {elapsed:.2f}s)")
        print()
        
        print("[STEP 2/7] Starting user session...")
        step_start = time.time()
        print(f"   Timestamp: {time.strftime('%H:%M:%S')}")
        print(f"   Calling: m.start_user_session('cisco', 'test_context_1')")
        m.start_user_session('cisco', 'test_context_1')
        elapsed = time.time() - step_start
        print(f"✅ [STEP 2/7] User session started (took {elapsed:.2f}s)")
        print()
        
        # Service parameters
        router1 = 'xr9kv-1'
        router2 = 'xr9kv-2'
        service_name = 'peer1-2'
        as_number = 65000
        router1_lo0_ip = '1.1.1.1'
        router1_router_id = '1.1.1.1'
        router2_lo0_ip = '1.1.1.2'
        router2_router_id = '1.1.1.2'
        
        print("[STEP 3/7] Defining service creation function...")
        print(f"   Service: {service_name}")
        print(f"   AS Number: {as_number}")
        print(f"   Router1: {router1} (Lo0: {router1_lo0_ip}, RID: {router1_router_id})")
        print(f"   Router2: {router2} (Lo0: {router2_lo0_ip}, RID: {router2_router_id})")
        print()
        
        # Define the provisioning operation as a class or function
        class IbgpProvisioningOp:
            """Provisioning operation for iBGP service creation"""
            def __init__(self, m, router1, router2, service_name, as_number,
                         router1_lo0_ip, router1_router_id, router2_lo0_ip, router2_router_id):
                self.m = m
                self.router1 = router1
                self.router2 = router2
                self.service_name = service_name
                self.as_number = as_number
                self.router1_lo0_ip = router1_lo0_ip
                self.router1_router_id = router1_router_id
                self.router2_lo0_ip = router2_lo0_ip
                self.router2_router_id = router2_router_id
            
            def __call__(self):
                """Execute the provisioning operation"""
                print(f"   [RETRY] Starting write transaction...")
                t = self.m.start_write_trans()
                print(f"   [RETRY] Write transaction started")
                
                print(f"   [RETRY] Getting root object...")
                root = maagic.get_root(t)
                
                # Validate routers exist
                print(f"   [RETRY] Validating routers...")
                if self.router1 not in root.devices.device:
                    raise ValueError(f"Router '{self.router1}' not found")
                if self.router2 not in root.devices.device:
                    raise ValueError(f"Router '{self.router2}' not found")
                
                # Access iBGP service
                print(f"   [RETRY] Accessing iBGP service package...")
                try:
                    services = root.ibgp__ibgp
                except AttributeError as e:
                    raise ValueError(f"iBGP service package not loaded: {e}")
                
                # Create or update service instance
                print(f"   [RETRY] Creating/updating service instance '{self.service_name}'...")
                if self.service_name in services:
                    svc = services[self.service_name]
                    print(f"   [RETRY] Service exists, updating...")
                else:
                    svc = services.create(self.service_name)
                    print(f"   [RETRY] Created new service instance")
                
                # Set service parameters
                print(f"   [RETRY] Setting service parameters...")
                svc.as_number = self.as_number
                svc.router1 = self.router1
                svc.router1_lo0_ip = self.router1_lo0_ip
                svc.router1_router_id = self.router1_router_id
                svc.router2 = self.router2
                svc.router2_lo0_ip = self.router2_lo0_ip
                svc.router2_router_id = self.router2_router_id
                
                print(f"   [RETRY] Applying transaction...")
                t.apply()
                print(f"   [RETRY] Transaction applied successfully!")
                
                return True
        
        print("[STEP 4/7] Creating provisioning operation...")
        step_start = time.time()
        provisioning_op = IbgpProvisioningOp(
            m, router1, router2, service_name, as_number,
            router1_lo0_ip, router1_router_id, router2_lo0_ip, router2_router_id
        )
        elapsed = time.time() - step_start
        print(f"✅ [STEP 4/7] Provisioning operation created (took {elapsed:.2f}s)")
        print()
        
        print("[STEP 5/7] Executing provisioning with retry logic...")
        print(f"   Timestamp: {time.strftime('%H:%M:%S')}")
        print(f"   Using: run_with_retry() with automatic retry on conflicts")
        print()
        step_start = time.time()
        
        # Use run_with_retry to handle conflicts automatically
        result = run_with_retry(provisioning_op, timeout=30, retries=3)
        
        elapsed = time.time() - step_start
        print()
        print(f"✅ [STEP 5/7] Provisioning completed (took {elapsed:.2f}s)")
        print()
        
        print("[STEP 6/7] Verifying service creation...")
        step_start = time.time()
        t_read = m.start_read_trans()
        root = maagic.get_root(t_read)
        services = root.ibgp__ibgp
        if service_name in services:
            svc = services[service_name]
            print(f"✅ Service '{service_name}' verified:")
            print(f"   AS Number: {svc.as_number}")
            print(f"   Router1: {svc.router1} (Lo0: {svc.router1_lo0_ip}, RID: {svc.router1_router_id})")
            print(f"   Router2: {svc.router2} (Lo0: {svc.router2_lo0_ip}, RID: {svc.router2_router_id})")
        else:
            print(f"⚠️  Warning: Service '{service_name}' not found after creation")
        t_read.finish()
        elapsed = time.time() - step_start
        print(f"✅ [STEP 6/7] Verification complete (took {elapsed:.2f}s)")
        print()
        
        print("[STEP 7/7] Closing user session...")
        m.end_user_session()
        print("✅ User session closed")
        print()
        
        total_time = time.time() - overall_start
        print("=" * 60)
        print("✅ SUCCESS: iBGP service created successfully!")
        print("=" * 60)
        print(f"Service: {service_name}")
        print(f"Total time: {total_time:.2f} seconds")
        print()
        
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
    success = create_ibgp_service_with_retry()
    sys.exit(0 if success else 1)

