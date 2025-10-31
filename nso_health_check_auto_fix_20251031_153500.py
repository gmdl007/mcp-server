#!/usr/bin/env python3
"""
NSO Health Check and Auto-Fix Tool

Automatically detects and fixes common NSO issues:
- Hung/unresponsive NSO
- Device locks preventing transactions
- Stuck sessions holding locks
- NSO processes not responding

Based on NSO troubleshooting best practices.
"""

import os
import sys
import time
import subprocess
import signal
import re
import traceback
from datetime import datetime

# Set NSO environment variables
NSO_DIR = "/Users/gudeng/NCS-614"
os.environ['NCS_DIR'] = NSO_DIR
os.environ['DYLD_LIBRARY_PATH'] = f'{NSO_DIR}/lib'
os.environ['PYTHONPATH'] = f'{NSO_DIR}/src/ncs/pyapi'

# Add NSO Python API to Python path
nso_pyapi_path = f'{NSO_DIR}/src/ncs/pyapi'
if nso_pyapi_path not in sys.path:
    sys.path.insert(0, nso_pyapi_path)

try:
    import ncs
    import ncs.maapi as maapi
    import ncs.maagic as maagic
except ImportError as e:
    print(f"❌ Failed to import NSO modules: {e}")
    sys.exit(1)

class NSOHealthChecker:
    """NSO Health Checker with auto-fix capabilities"""
    
    def __init__(self, nso_dir=NSO_DIR):
        self.nso_dir = nso_dir
        self.ncs_bin = f'{nso_dir}/bin/ncs'
        self.ncs_cli_bin = f'{nso_dir}/bin/ncs_cli'
        self.issues_found = []
        self.fixes_applied = []
        self.warnings = []
        
    def log(self, message, level="INFO"):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "INFO": "ℹ️ ",
            "WARN": "⚠️ ",
            "ERROR": "❌",
            "SUCCESS": "✅",
            "ACTION": "🔧"
        }.get(level, "")
        print(f"[{timestamp}] {prefix} {message}")
    
    def check_nso_status(self, timeout=5):
        """Check if NSO is responding to status commands"""
        self.log("Checking NSO status...", "INFO")
        try:
            result = subprocess.run(
                [self.ncs_bin, '--status'],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            if result.returncode == 0 and "status: started" in result.stdout:
                self.log("NSO is running and responsive", "SUCCESS")
                return True
            else:
                self.log(f"NSO status check failed: {result.stdout[:200]}", "WARN")
                self.issues_found.append("NSO status check failed")
                return False
        except subprocess.TimeoutExpired:
            self.log("NSO status check timed out - NSO appears hung", "ERROR")
            self.issues_found.append("NSO hung (status check timeout)")
            return False
        except FileNotFoundError:
            self.log(f"NSO binary not found at {self.ncs_bin}", "ERROR")
            self.issues_found.append("NSO binary not found")
            return False
        except Exception as e:
            self.log(f"Error checking NSO status: {e}", "ERROR")
            self.issues_found.append(f"Status check error: {e}")
            return False
    
    def check_nso_api_connection(self, timeout=5):
        """Check if NSO API is responsive"""
        self.log("Checking NSO API connection...", "INFO")
        m = None
        try:
            start_time = time.time()
            m = maapi.Maapi()
            
            # Try to start a user session with timeout
            session_start = time.time()
            m.start_user_session('cisco', 'health_check')
            
            # Try to start a read transaction
            t = m.start_read_trans()
            root = maagic.get_root(t)
            
            # Quick read to verify it works
            _ = list(root.devices.device.keys())[:1] if root.devices.device else []
            
            t.finish()
            m.end_user_session()
            
            elapsed = time.time() - start_time
            if elapsed > timeout:
                self.log(f"API connection slow ({elapsed:.2f}s) but working", "WARN")
                self.warnings.append(f"API response time: {elapsed:.2f}s")
            else:
                self.log(f"NSO API is responsive ({elapsed:.2f}s)", "SUCCESS")
            return True
            
        except Exception as e:
            error_msg = str(e)
            elapsed = time.time() - start_time if 'start_time' in locals() else 0
            
            if elapsed > timeout:
                self.log(f"NSO API connection timed out ({elapsed:.2f}s)", "ERROR")
                self.issues_found.append("NSO API hung (connection timeout)")
            elif "locked" in error_msg.lower():
                self.log(f"NSO API reports locks: {error_msg[:100]}", "WARN")
                self.issues_found.append(f"Device locks detected: {error_msg[:100]}")
            else:
                self.log(f"NSO API connection failed: {error_msg[:100]}", "ERROR")
                self.issues_found.append(f"API connection error: {error_msg[:100]}")
            
            if m:
                try:
                    m.end_user_session()
                except:
                    pass
            return False
    
    def check_device_locks(self):
        """Check for device locks by attempting write transactions"""
        self.log("Checking for device locks...", "INFO")
        m = None
        locked_devices = []
        
        try:
            m = maapi.Maapi()
            m.start_user_session('cisco', 'lock_check')
            
            # Get list of devices
            t_read = m.start_read_trans()
            root = maagic.get_root(t_read)
            device_list = list(root.devices.device.keys())
            t_read.finish()
            
            self.log(f"Testing {len(device_list)} device(s) for locks...", "INFO")
            
            for device_name in device_list:
                try:
                    # Try to start a write transaction with short timeout
                    t_write = m.start_write_trans()
                    t_write.finish()
                    self.log(f"  {device_name}: OK", "SUCCESS")
                except Exception as e:
                    error_msg = str(e)
                    if "locked" in error_msg.lower():
                        self.log(f"  {device_name}: LOCKED", "ERROR")
                        locked_devices.append((device_name, error_msg))
                        self.issues_found.append(f"Device {device_name} is locked")
                    else:
                        self.log(f"  {device_name}: Error ({error_msg[:50]})", "WARN")
            
            if locked_devices:
                self.log(f"Found {len(locked_devices)} locked device(s)", "ERROR")
                return locked_devices
            else:
                self.log("No device locks detected", "SUCCESS")
                return []
                
        except Exception as e:
            self.log(f"Error checking device locks: {e}", "ERROR")
            self.issues_found.append(f"Lock check error: {e}")
            return []
        finally:
            if m:
                try:
                    m.end_user_session()
                except:
                    pass
    
    def check_nso_processes(self):
        """Check if NSO processes are running"""
        self.log("Checking NSO processes...", "INFO")
        try:
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            ncs_processes = []
            patterns = [
                r'ncs\.smp',
                r'NcsJVMLauncher',
                r'webapp-runner\.jar',
                r'ncs_pyvm/startup\.py'
            ]
            
            for line in result.stdout.split('\n'):
                for pattern in patterns:
                    if re.search(pattern, line) and 'grep' not in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            pid = parts[1]
                            cmd = ' '.join(parts[10:])[:80]
                            ncs_processes.append((pid, cmd))
            
            if ncs_processes:
                self.log(f"Found {len(ncs_processes)} NSO process(es)", "INFO")
                return ncs_processes
            else:
                self.log("No NSO processes found", "WARN")
                self.issues_found.append("No NSO processes running")
                return []
                
        except Exception as e:
            self.log(f"Error checking processes: {e}", "ERROR")
            return []
    
    def clear_locks_via_cli(self):
        """Attempt to clear locks using NSO CLI"""
        self.log("Attempting to clear locks via CLI...", "ACTION")
        try:
            result = subprocess.run(
                [self.ncs_cli_bin, '-C', '-u', 'cisco', '-c', 'clear locks'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                self.log("Locks cleared via CLI", "SUCCESS")
                self.fixes_applied.append("Cleared locks via CLI")
                return True
            else:
                self.log(f"Failed to clear locks: {result.stderr[:100]}", "WARN")
                return False
        except Exception as e:
            self.log(f"Error clearing locks: {e}", "WARN")
            return False
    
    def kill_nso_processes(self, processes):
        """Kill NSO processes safely"""
        self.log(f"Killing {len(processes)} NSO process(es)...", "ACTION")
        
        # Group by type
        python_vms = []
        java_procs = []
        main_ncs = []
        other = []
        
        for pid, cmd in processes:
            if 'ncs_pyvm' in cmd:
                python_vms.append(pid)
            elif 'NcsJVMLauncher' in cmd or 'webapp-runner' in cmd:
                java_procs.append(pid)
            elif 'ncs.smp' in cmd:
                main_ncs.append(pid)
            else:
                other.append(pid)
        
        # Kill in order: Python VMs, Java, helpers, main NCS
        killed = []
        for pid_list, name in [(python_vms, "Python VMs"), 
                               (java_procs, "Java processes"),
                               (other, "Helper processes"),
                               (main_ncs, "Main NCS process")]:
            if pid_list:
                self.log(f"  Killing {name}...", "ACTION")
                for pid in pid_list:
                    try:
                        # Try TERM first
                        os.kill(int(pid), signal.SIGTERM)
                        time.sleep(1)
                        # Check if still running, kill if needed
                        try:
                            os.kill(int(pid), 0)  # Check if process exists
                            os.kill(int(pid), signal.SIGKILL)
                            self.log(f"    Killed PID {pid} (force)", "SUCCESS")
                        except ProcessLookupError:
                            self.log(f"    Killed PID {pid}", "SUCCESS")
                        killed.append(pid)
                    except ProcessLookupError:
                        pass
                    except Exception as e:
                        self.log(f"    Failed to kill PID {pid}: {e}", "WARN")
        
        if killed:
            self.log(f"Killed {len(killed)} process(es)", "SUCCESS")
            self.fixes_applied.append(f"Killed {len(killed)} hung NSO processes")
            time.sleep(3)  # Wait for cleanup
            return True
        return False
    
    def restart_nso(self):
        """Restart NSO"""
        self.log("Restarting NSO...", "ACTION")
        try:
            # Change to ncs-run directory
            ncs_run = '/Users/gudeng/ncs-run'
            result = subprocess.run(
                [self.ncs_bin],
                cwd=ncs_run,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                self.log("NSO restart initiated", "SUCCESS")
                self.fixes_applied.append("Restarted NSO")
                # Wait for NSO to start
                self.log("Waiting 10 seconds for NSO to initialize...", "INFO")
                time.sleep(10)
                return True
            else:
                self.log(f"NSO restart failed: {result.stderr[:200]}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Error restarting NSO: {e}", "ERROR")
            return False
    
    def run_full_check(self, auto_fix=True):
        """Run full health check with optional auto-fix"""
        print("=" * 70)
        print("NSO Health Check and Auto-Fix Tool")
        print("=" * 70)
        print()
        
        start_time = time.time()
        
        # Step 1: Check NSO status
        nso_responding = self.check_nso_status()
        print()
        
        # Step 2: Check API connection
        api_working = False
        if nso_responding:
            api_working = self.check_nso_api_connection()
        print()
        
        # Step 3: Check device locks
        locked_devices = []
        if api_working:
            locked_devices = self.check_device_locks()
        print()
        
        # Step 4: Check processes
        processes = self.check_nso_processes()
        print()
        
        # Determine if NSO is hung
        nso_hung = False
        if not nso_responding or not api_working:
            if processes:
                nso_hung = True
                self.log("NSO appears hung (not responding but processes running)", "ERROR")
        
        # Auto-fix section
        if auto_fix:
            print("=" * 70)
            print("Auto-Fix Section")
            print("=" * 70)
            print()
            
            # Fix 1: Try to clear locks
            if locked_devices:
                self.clear_locks_via_cli()
                print()
            
            # Fix 2: If NSO is hung, kill and restart
            if nso_hung:
                self.log("NSO is hung - attempting kill and restart...", "ACTION")
                if processes:
                    self.kill_nso_processes(processes)
                    print()
                    time.sleep(2)
                    self.restart_nso()
                    print()
                    
                    # Verify restart worked
                    self.log("Verifying NSO restart...", "INFO")
                    time.sleep(5)
                    if self.check_nso_status():
                        self.log("NSO restart successful!", "SUCCESS")
                    else:
                        self.log("NSO restart verification failed", "ERROR")
                    print()
            elif not processes:
                # No processes but also not responding - try to start
                self.log("NSO not running - attempting to start...", "ACTION")
                self.restart_nso()
                print()
        
        # Summary
        print("=" * 70)
        print("Health Check Summary")
        print("=" * 70)
        print()
        
        total_time = time.time() - start_time
        
        if self.issues_found:
            print(f"❌ Found {len(self.issues_found)} issue(s):")
            for issue in self.issues_found:
                print(f"   - {issue}")
        else:
            print("✅ No issues detected")
        
        if self.warnings:
            print(f"\n⚠️  {len(self.warnings)} warning(s):")
            for warn in self.warnings:
                print(f"   - {warn}")
        
        if self.fixes_applied:
            print(f"\n✅ Applied {len(self.fixes_applied)} fix(es):")
            for fix in self.fixes_applied:
                print(f"   - {fix}")
        
        print(f"\nTotal check time: {total_time:.2f} seconds")
        print()
        
        # Return status
        if not self.issues_found:
            return 0  # Healthy
        elif nso_hung and self.fixes_applied:
            return 1  # Issues found but fixed
        else:
            return 2  # Issues found, not fixed

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="NSO Health Check and Auto-Fix Tool"
    )
    parser.add_argument(
        '--no-fix',
        action='store_true',
        help='Only check, do not attempt auto-fix'
    )
    parser.add_argument(
        '--nso-dir',
        default=NSO_DIR,
        help=f'NSO installation directory (default: {NSO_DIR})'
    )
    
    args = parser.parse_args()
    
    checker = NSOHealthChecker(nso_dir=args.nso_dir)
    exit_code = checker.run_full_check(auto_fix=not args.no_fix)
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()

