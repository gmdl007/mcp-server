#!/usr/bin/env python3
"""
Fix Cell 13 in NSO Multi-Agent Notebook
=======================================

This script automatically fixes the import error in cell 13 by replacing
the shell commands with proper Python environment setup code.
"""

import json
import os
import shutil
from datetime import datetime

def backup_notebook():
    """Create a backup of the original notebook"""
    original_file = "/Users/gudeng/myproject/NSO_python_multi-agend.ipynb"
    backup_file = f"/Users/gudeng/myproject/NSO_python_multi-agend_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ipynb"
    
    shutil.copy2(original_file, backup_file)
    print(f"✅ Backup created: {backup_file}")
    return backup_file

def fix_cell_13():
    """Fix cell 13 by replacing shell commands with Python code"""
    notebook_file = "/Users/gudeng/myproject/NSO_python_multi-agend.ipynb"
    
    # Create backup first
    backup_file = backup_notebook()
    
    try:
        # Read the notebook
        with open(notebook_file, 'r') as f:
            notebook = json.load(f)
        
        # Find cell 13 (the one with NSO imports)
        cell_13_found = False
        for i, cell in enumerate(notebook['cells']):
            if cell['cell_type'] == 'code' and 'source' in cell:
                source = ''.join(cell['source'])
                if '!conda activate base' in source and 'import ncs' in source:
                    print(f"✅ Found cell 13 at index {i}")
                    cell_13_found = True
                    
                    # Replace the problematic shell commands with Python code
                    new_source = [
                        "# NSO Environment Setup (Fixed)\n",
                        "import os\n",
                        "import sys\n",
                        "\n",
                        "# Set NSO environment variables\n",
                        "NSO_DIR = \"/Users/gudeng/NCS-614\"\n",
                        "os.environ['NCS_DIR'] = NSO_DIR\n",
                        "os.environ['DYLD_LIBRARY_PATH'] = f'{NSO_DIR}/lib'\n",
                        "os.environ['PYTHONPATH'] = f'{NSO_DIR}/src/ncs/pyapi'\n",
                        "\n",
                        "# Add NSO Python API to Python path\n",
                        "nso_pyapi_path = f'{NSO_DIR}/src/ncs/pyapi'\n",
                        "if nso_pyapi_path not in sys.path:\n",
                        "    sys.path.insert(0, nso_pyapi_path)\n",
                        "\n",
                        "print(f\"✅ NSO environment configured:\")\n",
                        "print(f\"   - NCS_DIR: {NSO_DIR}\")\n",
                        "print(f\"   - PYTHONPATH: {nso_pyapi_path}\")\n",
                        "\n",
                        "# NSO Imports\n",
                        "import ncs\n",
                        "import ncs.maapi as maapi\n",
                        "import ncs.maagic as maagic\n",
                        "m = maapi.Maapi()\n",
                        "import io\n",
                        "import sys\n",
                        "import re\n",
                        "import os\n",
                        "\n",
                        "print(\"✅ NSO modules imported successfully\")\n",
                        "\n",
                        "# NSO Connection\n",
                        "m.start_user_session('admin','test_context_1')\n",
                        "t = m.start_write_trans()\n",
                        "root = maagic.get_root(t)\n",
                        "\n",
                        "print(\"✅ NSO connection established successfully\")\n",
                        "\n",
                        "# Test device discovery\n",
                        "devices = []\n",
                        "for device in root.devices.device:\n",
                        "    devices.append(device.name)\n",
                        "\n",
                        "print(f\"📱 Found {len(devices)} devices: {devices}\")\n",
                        "print(\"\\n🎉 Cell 13 completed successfully!\")\n"
                    ]
                    
                    # Update the cell
                    cell['source'] = new_source
                    cell['execution_count'] = None
                    cell['outputs'] = []
                    
                    print("✅ Cell 13 fixed successfully")
                    break
        
        if not cell_13_found:
            print("❌ Cell 13 not found in the notebook")
            return False
        
        # Write the fixed notebook
        with open(notebook_file, 'w') as f:
            json.dump(notebook, f, indent=2)
        
        print("✅ Notebook updated successfully")
        print(f"📁 Original notebook backed up to: {backup_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing notebook: {e}")
        return False

def main():
    """Main execution function"""
    print("🔧 Fixing Cell 13 in NSO Multi-Agent Notebook")
    print("=" * 50)
    
    success = fix_cell_13()
    
    if success:
        print("\n🎉 Cell 13 has been fixed successfully!")
        print("\n📝 Next steps:")
        print("1. Restart your Jupyter kernel")
        print("2. Run cell 13 again - it should work without import errors")
        print("3. The NSO environment will be set up automatically")
        print("\n💡 The fix replaces shell commands with Python code that properly")
        print("   sets up the NSO environment variables and Python path.")
    else:
        print("\n❌ Failed to fix cell 13")
        print("🔧 Please check the notebook file and try again")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
