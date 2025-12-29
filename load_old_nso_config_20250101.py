#!/usr/bin/env python3
"""
Load old NSO 6.1.4 configuration into NSO 6.4.1.3
This script loads the complete backup configuration and updates NED IDs to be compatible with NSO 6.4.1.3
"""

import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# NSO 6.4.1.3 paths
NSO_DIR = '/Users/gudeng/NCS-6413'
NSO_RUN = '/Users/gudeng/ncs-run-6413'
BACKUP_FILE = '/Users/gudeng/MCP_Server/backups/nso_configs/ncs_complete_backup_20251119_000310.xml'

# Set up NSO environment
os.environ['NCS_DIR'] = NSO_DIR
os.environ['DYLD_LIBRARY_PATH'] = f'{NSO_DIR}/lib'
sys.path.insert(0, f'{NSO_DIR}/src/ncs/pyapi')

try:
    import ncs.maapi as maapi
    import ncs.maagic as maagic
except ImportError as e:
    print(f"❌ Error importing NSO Python API: {e}")
    print(f"   Make sure NSO 6.4.1.3 is installed at {NSO_DIR}")
    sys.exit(1)

# NED ID mapping: old NED IDs -> new NED IDs for NSO 6.4.1.3
NED_ID_MAPPING = {
    'cisco-iosxr-cli-7.52': 'cisco-iosxr-cli-7.61:cisco-iosxr-cli-7.61',
    'cisco-iosxr-cli-3.5': 'cisco-iosxr-cli-7.61:cisco-iosxr-cli-7.61',
    'cisco-iosxr_netconf-7.10.1.1': 'cisco-iosxr-cli-7.61:cisco-iosxr-cli-7.61',  # Fallback to CLI if NETCONF not available
}

def update_ned_ids_in_xml(xml_file, output_file):
    """Update NED IDs in XML file to be compatible with NSO 6.4.1.3"""
    print(f"Reading backup file: {xml_file}")
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Find all ned-id elements and update them
    updated_count = 0
    for ned_id_elem in root.iter():
        if ned_id_elem.tag.endswith('ned-id') or (ned_id_elem.tag == 'ned-id'):
            old_ned_id = ned_id_elem.text
            if old_ned_id:
                # Check if we need to update this NED ID
                for old_ned, new_ned in NED_ID_MAPPING.items():
                    if old_ned in old_ned_id:
                        print(f"  Updating NED ID: {old_ned_id} -> {new_ned}")
                        ned_id_elem.text = new_ned
                        updated_count += 1
                        break
    
    # Save updated XML
    tree.write(output_file, encoding='utf-8', xml_declaration=True)
    print(f"✅ Updated {updated_count} NED IDs")
    print(f"✅ Saved updated configuration to: {output_file}")
    return output_file

def load_config_via_api(xml_file):
    """Load configuration into NSO using Python API"""
    print(f"\n{'='*60}")
    print("Loading configuration into NSO 6.4.1.3...")
    print(f"{'='*60}\n")
    
    try:
        m = maapi.Maapi()
        m.start_user_session('admin', 'load_old_config')
        t = m.start_write_trans()
        
        # Load the XML file
        print(f"Loading XML file: {xml_file}")
        t.load_config(maapi.CONFIG_XML, xml_file, merge=True)
        
        # Apply the transaction
        print("Applying configuration...")
        t.apply()
        
        print("✅ Configuration loaded successfully!")
        
        # Show summary
        root = maagic.get_root(t)
        device_count = len(root.devices.device)
        authgroup_count = len(root.devices.authgroups.group)
        
        print(f"\n📊 Configuration Summary:")
        print(f"   Devices: {device_count}")
        print(f"   Authgroups: {authgroup_count}")
        
        m.end_user_session()
        return True
        
    except Exception as e:
        print(f"\n❌ Error loading configuration: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*60)
    print("NSO Configuration Migration: 6.1.4 -> 6.4.1.3")
    print("="*60)
    print(f"Backup file: {BACKUP_FILE}")
    print(f"NSO 6.4.1.3: {NSO_DIR}")
    print(f"NSO Runtime: {NSO_RUN}")
    print()
    
    # Check if backup file exists
    if not os.path.exists(BACKUP_FILE):
        print(f"❌ Error: Backup file not found: {BACKUP_FILE}")
        sys.exit(1)
    
    # Check if NSO is running (basic check)
    print("⚠️  Note: Make sure NSO 6.4.1.3 is running before loading configuration")
    print("   Start NSO with: ncs-start (or manually)")
    print()
    
    # Create updated XML file
    updated_xml = os.path.join(NSO_RUN, 'ncs-cdb', 'old_config_migrated.xml')
    os.makedirs(os.path.dirname(updated_xml), exist_ok=True)
    
    # Update NED IDs in the backup file
    updated_file = update_ned_ids_in_xml(BACKUP_FILE, updated_xml)
    
    # Load configuration
    if load_config_via_api(updated_file):
        print("\n" + "="*60)
        print("✅ Migration completed successfully!")
        print("="*60)
        print("\nNext steps:")
        print("1. Verify devices: ncs_cli -u admin -C 'show devices device'")
        print("2. Check authgroups: ncs_cli -u admin -C 'show devices authgroups'")
        print("3. Update device NED IDs if needed (some may need manual update)")
        print("4. Reload packages: ncs_cli -u admin -C 'packages reload'")
        sys.exit(0)
    else:
        print("\n❌ Migration failed. Please check the errors above.")
        sys.exit(1)

if __name__ == '__main__':
    main()

