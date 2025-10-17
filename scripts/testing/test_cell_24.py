#!/usr/bin/env python3
"""
Test Cell 24 - iterate('show ipv4 int brief')
==============================================

This script tests the iterate function to identify the syntax error.
"""

import os
import sys

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
    
    print(f"✅ NSO environment configured")

def test_iterate_function():
    """Test the iterate function from cell 24"""
    print("\n📱 Testing iterate function...")
    
    try:
        # Import NSO modules
        import ncs
        import ncs.maapi as maapi
        import ncs.maagic as maagic
        print("✅ NSO modules imported successfully")
        
        # Define the iterate_devices_AND_cmd function
        def iterate_devices_AND_cmd(cmd):
            """
            Execute a single command on all devices in NSO and print the results.

            Args:
                cmd (str): The command to execute on each device.

            Returns:
                list: A list of strings containing the results of the command execution.
            """
            results = []  # Initialize a list to store the results
            with ncs.maapi.single_write_trans('admin', 'python', groups=['ncsadmin']) as t:
                root = ncs.maagic.get_root(t)
                for box in root.devices.device:
                    try:
                        # Get the 'show' action object
                        show = box.live_status.__getitem__('exec').any
                        
                        # Prepare the input for the command
                        inp = show.get_input()
                        inp.args = [cmd]
                        
                        # Execute the command and get the result
                        r = show.request(inp)
                        
                        # Format the result and print it
                        show_cmd = 'Result of Show Command "{}" for Router Name {}: {}'.format(cmd, box.name, r.result)
                        print(show_cmd)
                        
                        # Append the result to the list
                        results.append(show_cmd)
                        
                    except Exception as e:
                        error_msg = f"Error executing command '{cmd}' on device '{box.name}': {e}"
                        print(error_msg)
                        results.append(error_msg)
            
            return results
        
        # Define the iterate function
        def iterate(cmds):
            """
            iterate the commands on every router.
            
            Args:
                the cmds are the commands to be executed on every router
            
            Returns:
                str: the output of command of every router.
            """
            return iterate_devices_AND_cmd(cmds)
        
        print("✅ Functions defined successfully")
        
        # Test the iterate function
        print("\n🔍 Testing: iterate('show ipv4 int brief')")
        try:
            result = iterate('show ipv4 int brief')
            print(f"✅ Function executed successfully")
            print(f"📊 Result type: {type(result)}")
            print(f"📊 Result length: {len(result) if isinstance(result, list) else 'N/A'}")
            
            if isinstance(result, list) and result:
                print("📋 Results:")
                for i, res in enumerate(result):
                    print(f"  {i+1}. {res[:100]}...")
            
        except Exception as e:
            print(f"❌ Error executing iterate function: {e}")
            print(f"❌ Error type: {type(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error in test_iterate_function: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main execution function"""
    print("🚀 Testing Cell 24 - iterate('show ipv4 int brief')")
    print("=" * 55)
    
    # Setup environment
    setup_nso_environment()
    
    # Test the iterate function
    success = test_iterate_function()
    
    if success:
        print("\n🎉 Cell 24 test completed successfully!")
        print("✅ The iterate function is working correctly")
    else:
        print("\n❌ Cell 24 test failed")
        print("🔧 Please check the error messages above")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
