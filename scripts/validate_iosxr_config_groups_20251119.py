#!/usr/bin/env python3
# -*- mode: python; python-indent: 4 -*-
"""
IOS-XR Configuration Group Validator

This script validates IOS-XR configuration groups in NSO, catching common typos
and semantic errors before they're applied to interfaces.

Example problem it catches:
  group GRP_ISIS_INT_DEFAULT
   router isis *
    interface *
     ponit-to-point          ! ❌ TYPO: should be "point-to-point"
     hello-password keychanin KC_ISIS level 2    ! ❌ TYPO: should be "keychain"
    !
   !
  !
  end-group

Usage:
    python validate_iosxr_config_groups_20251119.py <device_name> <group_name>
    python validate_iosxr_config_groups_20251119.py node-1 GRP_ISIS_INT_DEFAULT
"""

import sys
import os
import re

# Add NSO Python API to path
NCS_DIR = os.environ.get('NCS_DIR', '/opt/ncs')
sys.path.insert(0, f'{NCS_DIR}/src/ncs/pyapi')

try:
    import ncs
    from ncs import maapi, maagic
    from ncs.dp import ValidationError
except ImportError as e:
    print(f"❌ Error importing NSO Python API: {e}")
    print(f"   Make sure NCS_DIR is set correctly (current: {NCS_DIR})")
    sys.exit(1)


class IOSXRConfigGroupValidator:
    """Validates IOS-XR configuration groups for typos and semantic errors"""
    
    # Common typos in IOS-XR IS-IS commands
    TYPO_PATTERNS = {
        'ponit-to-point': 'point-to-point',
        'keychanin': 'keychain',
        'keychian': 'keychain',
        'hellow-password': 'hello-password',
        'hello-passwd': 'hello-password',
        'hello-pasword': 'hello-password',
    }
    
    # Valid IS-IS interface commands
    VALID_ISIS_INTERFACE_COMMANDS = {
        'point-to-point',
        'hello-password',
        'hello-interval',
        'hello-multiplier',
        'circuit-type',
        'metric',
        'priority',
        'authentication',
        'key-chain',
        'keychain',
    }
    
    def __init__(self, device_name, group_name):
        self.device_name = device_name
        self.group_name = group_name
        self.errors = []
        self.warnings = []
    
    def validate(self):
        """Main validation method"""
        try:
            with maapi.single_write_trans('admin', 'system') as t:
                root = maagic.get_root(t)
                
                # Get device
                if self.device_name not in root.devices.device:
                    self.errors.append(f"Device '{self.device_name}' not found")
                    return self._format_results()
                
                device = root.devices.device[self.device_name]
                
                # Get configuration group
                if not hasattr(device.config, 'group'):
                    self.errors.append("Device does not support configuration groups")
                    return self._format_results()
                
                if self.group_name not in device.config.group:
                    self.errors.append(f"Configuration group '{self.group_name}' not found")
                    return self._format_results()
                
                config_group = device.config.group[self.group_name]
                
                # Validate IS-IS configuration
                self._validate_isis_config(config_group)
                
                # Validate interface configuration
                self._validate_interface_config(config_group)
                
                # Validate nested groups
                self._validate_nested_groups(device, config_group)
                
                # Check for common typos in raw config
                self._check_typos_in_config(config_group)
                
        except Exception as e:
            self.errors.append(f"Validation error: {e}")
        
        return self._format_results()
    
    def _validate_isis_config(self, config_group):
        """Validate IS-IS configuration in group"""
        try:
            # Check if router isis exists
            if hasattr(config_group, 'router') and hasattr(config_group.router, 'isis'):
                isis_config = config_group.router.isis
                
                # Iterate through IS-IS instances (router isis *)
                for isis_tag in isis_config:
                    # Check interface configurations
                    if hasattr(isis_tag, 'interface'):
                        for interface in isis_tag.interface:
                            self._validate_isis_interface(interface)
        except Exception as e:
            self.warnings.append(f"Could not validate IS-IS config: {e}")
    
    def _validate_isis_interface(self, interface_config):
        """Validate IS-IS interface commands"""
        # Check for point-to-point configuration
        if hasattr(interface_config, 'point_to_point'):
            # Valid - point-to-point is correctly spelled
            pass
        else:
            # Check if there's a typo variant
            interface_str = str(interface_config).lower()
            if 'ponit' in interface_str and 'point' not in interface_str:
                self.errors.append(
                    "IS-IS interface: 'ponit-to-point' is misspelled. "
                    "Should be 'point-to-point'"
                )
        
        # Check hello-password configuration
        if hasattr(interface_config, 'hello_password'):
            hello_pwd = interface_config.hello_password
            
            # Check for keychain typo
            if hasattr(hello_pwd, 'keychain'):
                keychain_name = hello_pwd.keychain
                if not self._is_valid_keychain_name(keychain_name):
                    self.errors.append(
                        f"IS-IS hello-password: Invalid keychain name '{keychain_name}'"
                    )
            else:
                # Check for typo variants
                hello_pwd_str = str(hello_pwd).lower()
                if 'keychanin' in hello_pwd_str or 'keychian' in hello_pwd_str:
                    self.errors.append(
                        "IS-IS hello-password: 'keychanin' or 'keychian' is misspelled. "
                        "Should be 'keychain'"
                    )
            
            # Validate level
            if hasattr(hello_pwd, 'level'):
                level = str(hello_pwd.level)
                valid_levels = ['1', '2', 'level-1', 'level-2', 'level_1', 'level_2']
                if level not in valid_levels:
                    self.warnings.append(
                        f"IS-IS hello-password: Unusual level value '{level}'. "
                        f"Expected: {', '.join(valid_levels)}"
                    )
    
    def _validate_interface_config(self, config_group):
        """Validate interface configuration in group"""
        try:
            if hasattr(config_group, 'interface'):
                # Validate interface configurations
                for interface in config_group.interface:
                    # Add interface-specific validations here
                    pass
        except Exception as e:
            self.warnings.append(f"Could not validate interface config: {e}")
    
    def _validate_nested_groups(self, device, config_group):
        """Validate nested configuration groups"""
        try:
            if hasattr(config_group, 'group'):
                for nested_group_ref in config_group.group:
                    nested_group_name = str(nested_group_ref)
                    if nested_group_name not in device.config.group:
                        self.errors.append(
                            f"Nested group '{nested_group_name}' does not exist"
                        )
        except Exception as e:
            self.warnings.append(f"Could not validate nested groups: {e}")
    
    def _check_typos_in_config(self, config_group):
        """Check for common typos in configuration string representation"""
        try:
            config_str = str(config_group).lower()
            
            # Check for typo patterns
            for typo, correct in self.TYPO_PATTERNS.items():
                if typo in config_str:
                    self.errors.append(
                        f"Found typo: '{typo}' should be '{correct}'"
                    )
        except Exception as e:
            self.warnings.append(f"Could not check for typos: {e}")
    
    def _is_valid_keychain_name(self, keychain_name):
        """Validate keychain name"""
        if not keychain_name:
            return False
        if len(str(keychain_name)) > 32:  # IOS-XR limit
            return False
        # Add more validation as needed (e.g., check if keychain exists)
        return True
    
    def _format_results(self):
        """Format validation results"""
        result = []
        result.append(f"\n{'='*70}")
        result.append(f"Validation Results for Configuration Group: {self.group_name}")
        result.append(f"Device: {self.device_name}")
        result.append(f"{'='*70}\n")
        
        if not self.errors and not self.warnings:
            result.append("✅ Configuration group is valid!")
            return "\n".join(result)
        
        if self.errors:
            result.append("❌ ERRORS FOUND:")
            for i, error in enumerate(self.errors, 1):
                result.append(f"  {i}. {error}")
            result.append("")
        
        if self.warnings:
            result.append("⚠️  WARNINGS:")
            for i, warning in enumerate(self.warnings, 1):
                result.append(f"  {i}. {warning}")
            result.append("")
        
        result.append(f"{'='*70}\n")
        return "\n".join(result)


def main():
    """Main entry point"""
    if len(sys.argv) < 3:
        print("Usage: python validate_iosxr_config_groups_20251119.py <device_name> <group_name>")
        print("\nExample:")
        print("  python validate_iosxr_config_groups_20251119.py node-1 GRP_ISIS_INT_DEFAULT")
        sys.exit(1)
    
    device_name = sys.argv[1]
    group_name = sys.argv[2]
    
    print(f"🔍 Validating IOS-XR configuration group '{group_name}' on device '{device_name}'...")
    
    validator = IOSXRConfigGroupValidator(device_name, group_name)
    results = validator.validate()
    
    print(results)
    
    # Exit with error code if errors found
    if validator.errors:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()


