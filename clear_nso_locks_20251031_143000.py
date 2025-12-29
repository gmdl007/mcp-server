#!/usr/bin/env python3
"""Diagnose and clear NSO device locks and stuck sessions"""

import os
import sys
import time
import subprocess
import traceback
import re

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

def check_locks_via_cli():
    """Check locks using NSO CLI"""
    print("\n" + "=" * 60)
    print("Checking locks via NSO CLI...")
    print("=" * 60)
    
    try:
        # Use full path to ncs_cli
        ncs_cli_path = f'{NSO_DIR}/bin/ncs_cli'
        # Run ncs_cli to check locks
        cmd = [ncs_cli_path, '-C', '-u', 'cisco', '-c', 'show locks']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        print("Output:")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        return result.stdout
    except subprocess.TimeoutExpired:
        print("❌ Command timed out")
        return None
    except Exception as e:
        print(f"❌ Error running CLI command: {e}")
        return None

def check_sessions_via_cli():
    """Check active sessions using NSO CLI"""
    print("\n" + "=" * 60)
    print("Checking active sessions via NSO CLI...")
    print("=" * 60)
    
    try:
        # Use full path to ncs_cli
        ncs_cli_path = f'{NSO_DIR}/bin/ncs_cli'
        # Run ncs_cli to list sessions
        cmd = [ncs_cli_path, '-C', '-u', 'cisco', '-c', 'who']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        print("Output:")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        return result.stdout
    except subprocess.TimeoutExpired:
        print("❌ Command timed out")
        return None
    except Exception as e:
        print(f"❌ Error running CLI command: {e}")
        return None

def check_locks_via_maapi():
    """Check locks using MAAPI"""
    print("\n" + "=" * 60)
    print("Checking locks via MAAPI...")
    print("=" * 60)
    
    m = None
    try:
        m = maapi.Maapi()
        m.start_user_session('cisco', 'check_locks')
        t = m.start_read_trans()
        root = maagic.get_root(t)
        
        # Try to access locks
        if hasattr(root, 'locks'):
            locks = root.locks
            if hasattr(locks, 'lock'):
                lock_list = list(locks.lock.keys()) if hasattr(locks.lock, 'keys') else []
                
                if lock_list:
                    print(f"\n🔒 Found {len(lock_list)} active lock(s):\n")
                    for lock_id in lock_list:
                        lock = locks.lock[lock_id]
                        print(f"Lock ID: {lock_id}")
                        if hasattr(lock, 'user'):
                            print(f"  User: {lock.user}")
                        if hasattr(lock, 'when'):
                            print(f"  When: {lock.when}")
                        if hasattr(lock, 'path'):
                            print(f"  Path: {lock.path}")
                        print()
                    return lock_list
                else:
                    print("\n✅ No active locks found")
                    return []
            else:
                print("\n⚠️  Lock list not available via maagic")
                return None
        else:
            print("\n⚠️  Locks not accessible via this API")
            return None
            
    except Exception as e:
        print(f"\n❌ Error checking locks: {e}")
        traceback.print_exc()
        return None
    finally:
        if m:
            try:
                m.end_user_session()
            except:
                pass

def check_device_locks():
    """Check which devices are locked by trying to start a write transaction"""
    print("\n" + "=" * 60)
    print("Checking device locks (trying write transactions)...")
    print("=" * 60)
    
    m = None
    locked_devices = []
    
    try:
        m = maapi.Maapi()
        m.start_user_session('cisco', 'check_device_locks')
        
        # Get list of devices
        t_read = m.start_read_trans()
        root = maagic.get_root(t_read)
        devices = root.devices.device
        
        # Get device names as a list
        device_list = list(devices.keys())
        t_read.finish()
        
        print(f"\nTesting {len(device_list)} device(s) for locks...\n")
        
        for device_name in device_list:
            try:
                print(f"Testing {device_name}...", end=' ')
                # Try to start a write transaction with a timeout approach
                t_write = m.start_write_trans()
                # If we got here, device is not locked
                t_write.finish()
                print("✅ Not locked")
            except Exception as e:
                error_msg = str(e)
                if "locked" in error_msg.lower():
                    print(f"🔒 LOCKED: {error_msg}")
                    locked_devices.append((device_name, error_msg))
                else:
                    print(f"⚠️  Error: {error_msg}")
        
        if locked_devices:
            print(f"\n❌ Found {len(locked_devices)} locked device(s):")
            for device_name, error_msg in locked_devices:
                print(f"  - {device_name}: {error_msg}")
        else:
            print("\n✅ No locked devices found")
            
        return locked_devices
        
    except Exception as e:
        print(f"\n❌ Error checking device locks: {e}")
        traceback.print_exc()
        return []
    finally:
        if m:
            try:
                m.end_user_session()
            except:
                pass

def clear_locks_via_cli():
    """Try to clear locks using NSO CLI"""
    print("\n" + "=" * 60)
    print("Attempting to clear locks via NSO CLI...")
    print("=" * 60)
    
    try:
        # Use full path to ncs_cli
        ncs_cli_path = f'{NSO_DIR}/bin/ncs_cli'
        # Try to clear locks (requires admin)
        cmd = [ncs_cli_path, '-C', '-u', 'cisco', '-c', 'clear locks']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        print("Output:")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        if result.returncode == 0:
            print("✅ Locks cleared successfully")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error clearing locks: {e}")
        return False

def logout_session(session_id):
    """Logout a specific session using NSO CLI"""
    print(f"\nAttempting to logout session {session_id}...")
    try:
        # Use full path to ncs_cli
        ncs_cli_path = f'{NSO_DIR}/bin/ncs_cli'
        cmd = [ncs_cli_path, '-C', '-u', 'cisco', '-c', f'logout session {session_id}']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error logging out session: {e}")
        return False

def main():
    print("=" * 60)
    print("NSO Lock and Session Diagnostic Tool")
    print("=" * 60)
    
    # Step 1: Check locks via CLI
    cli_locks = check_locks_via_cli()
    
    # Step 2: Check sessions via CLI
    cli_sessions = check_sessions_via_cli()
    
    # Step 3: Check locks via MAAPI
    maapi_locks = check_locks_via_maapi()
    
    # Step 4: Check device locks by attempting transactions
    locked_devices = check_device_locks()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if locked_devices:
        print(f"\n❌ Found {len(locked_devices)} locked device(s)")
        print("\n💡 To clear locks, you can:")
        print("   1. Use NSO CLI:")
        print("      ncs_cli -C -u cisco")
        print("      show locks")
        print("      who")
        print("      logout session <session_id>")
        print("   2. Or try:")
        print("      clear locks")
        
        # Extract session IDs from error messages if possible
        session_ids = []
        for device_name, error_msg in locked_devices:
            # Try to extract session ID from error message
            # Format is usually: "Device is locked in a commit operation by session <id>"
            match = re.search(r'session\s+(\d+)', error_msg)
            if match:
                session_ids.append(match.group(1))
        
        if session_ids:
            print(f"\n🔍 Detected session IDs from error messages: {', '.join(set(session_ids))}")
            print("\n⚠️  Attempting to logout detected sessions...")
            for session_id in set(session_ids):
                if logout_session(session_id):
                    print(f"✅ Successfully logged out session {session_id}")
                else:
                    print(f"❌ Failed to logout session {session_id}")
    else:
        print("\n✅ No locked devices detected")
    
    # If locks exist, try to clear them
    if locked_devices:
        print("\n" + "=" * 60)
        print("Attempting automatic lock clearance...")
        print("=" * 60)
        if clear_locks_via_cli():
            print("\n✅ Locks cleared! Try your operation again.")
        else:
            print("\n⚠️  Automatic clearance failed. Please use NSO CLI manually.")
    
    print("\n" + "=" * 60)
    print("Diagnostic complete")
    print("=" * 60)

if __name__ == "__main__":
    main()
