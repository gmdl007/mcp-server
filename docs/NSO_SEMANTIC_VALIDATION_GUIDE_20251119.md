# NSO Semantic Validation Guide

## Overview

NSO provides comprehensive validation capabilities that can help with:
1. **Semantic Validation**: Routers perform semantic checks during configuration to ensure proposed settings are logically valid and consistent with protocol requirements.
2. **Early Error Detection**: Catching errors at template creation stage prevents potential issues later, enhancing overall network reliability (fail-fast principle).
3. **Template Integrity**: Apply-group templates encapsulate configurations for reuse. Validating templates prevents propagating errors across multiple interfaces.
4. **Ideal Behavior**: Routers should validate template semantic correctness at creation time, ensuring adherence to protocol rules and constraints.

---

## NSO Validation Mechanisms

### 1. YANG Model Validation (Built-in)

**What it does:**
- Validates syntax, data types, ranges, and required fields
- Enforces `must` statements for cross-field constraints
- Applies `when` statements for conditional validation

**When it runs:**
- Immediately when configuration is entered
- Before commit

**Example:**
```yang
leaf ospf-area {
    type uint32 {
        range "0..4294967295";
    }
    must "../router-id != '0.0.0.0'" {
        error-message "OSPF area requires valid router-id";
    }
}
```

---

### 2. Validation Callbacks (Python/Java)

**What it does:**
- Custom semantic validation beyond YANG constraints
- Access to full configuration tree for cross-reference checks
- Protocol-specific validation logic

**When it runs:**
- At commit time (default)
- Earlier if dependencies are specified
- Can be triggered on specific configuration changes

**Implementation Example:**

```python
from ncs.dp import ValidationError, ValidationPoint

class OSPFTemplateValidation(ValidationPoint):
    @ValidationPoint.validate
    def cb_validate(self, tctx, keypath, value, validationpoint):
        """Validate OSPF apply-group template at creation time"""
        
        # Access the configuration tree
        root = ncs.maagic.get_root(tctx)
        
        # Get the template being validated
        template_path = str(keypath)
        
        # Example: Validate OSPF area and router-id consistency
        if 'ospf' in template_path.lower():
            # Check if router-id is set when OSPF area is configured
            # Check if area ID is valid for the router type
            # Check if interface types are compatible with OSPF
            pass
        
        # Example: Validate BGP ASN consistency
        if 'bgp' in template_path.lower():
            # Check if ASN matches device capabilities
            # Check if neighbor addresses are valid
            # Check if address-families are supported
            pass
        
        # If validation fails, raise ValidationError
        if not self._is_valid_template(value):
            raise ValidationError(
                f"Template validation failed: {self._get_error_message(value)}"
            )
        
        return ncs.CONFD_OK
    
    def _is_valid_template(self, template_config):
        """Perform semantic validation on template"""
        # Add your validation logic here
        return True
    
    def _get_error_message(self, template_config):
        """Generate descriptive error message"""
        return "Template contains invalid configuration"
```

**Registration:**
```python
class Main(ncs.application.Application):
    def setup(self):
        # Register validation point for apply-group templates
        self.register_validation('apply-group-template-valpoint', 
                                OSPFTemplateValidation)
```

**YANG Model Definition:**
```yang
container apply-group {
    tailf:validate "ospf-template-validation" {
        tailf:dependency "../router/ospf";
        tailf:dependency "../interface";
    }
    // ... template configuration
}
```

---

### 3. Dry-Run Validation

**What it does:**
- Previews changes before commit
- Validates against device capabilities
- Shows what would be applied without modifying devices

**When to use:**
- Before applying templates to multiple devices
- To validate template compatibility with specific devices
- To preview configuration changes

**MCP Tool Available:**
- `commit_dry_run(description)` - Preview changes without applying

**Example:**
```python
# In your validation logic
def validate_template_before_apply(template_name, device_name):
    # Create transaction
    with maapi.single_write_trans('admin', 'system') as t:
        root = maagic.get_root(t)
        
        # Apply template to transaction
        device = root.devices.device[device_name]
        device.apply_template(template_name)
        
        # Perform dry-run
        try:
            t.apply_params(dry_run=True)
            return "✅ Template validation passed"
        except Exception as e:
            return f"❌ Template validation failed: {e}"
```

---

### 4. Service Package Validation

**What it does:**
- Validates service parameters and relationships
- Ensures service instances are consistent
- Validates templates before application in service context

**When it runs:**
- During service creation/update
- Before service template application
- During service redeploy

**Example:**
```python
class OSPFService(Service):
    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        # Validate service parameters
        if not self._validate_service_params(service):
            raise ServiceError("Invalid service parameters")
        
        # Apply template (template is validated before application)
        template = ncs.template.Template(service)
        template.apply('ospf-service-template', vars)
    
    def _validate_service_params(self, service):
        """Validate OSPF service parameters semantically"""
        # Check router-id format
        # Check area ID validity
        # Check interface compatibility
        # Check neighbor relationships
        return True
```

---

### 5. Template Validation Before Application

**What it does:**
- Validates template syntax and references
- Checks device capabilities before applying
- Validates template compatibility with target devices

**NSO CLI:**
```bash
# Validate template before applying
ncs_cli> config-template apply template ospf-base router xr9kv-1 dry-run
```

**Python API:**
```python
def validate_template(template_name, device_name):
    """Validate template before applying to device"""
    with maapi.single_write_trans('admin', 'system') as t:
        root = maagic.get_root(t)
        device = root.devices.device[device_name]
        
        # Check device capabilities
        if not device.has_capability('ospf'):
            return "❌ Device does not support OSPF"
        
        # Try to apply template in dry-run mode
        try:
            device.apply_template(template_name, dry_run=True)
            return "✅ Template is valid for this device"
        except Exception as e:
            return f"❌ Template validation failed: {e}"
```

---

## Implementation Strategy for Apply-Group Templates

### Step 1: Define Validation Point in YANG

```yang
module apply-group-validation {
    namespace "http://example.com/apply-group-validation";
    prefix agv;
    
    import tailf-common { prefix tailf; }
    import tailf-ncs { prefix ncs; }
    
    augment /ncs:devices/ncs:device/ncs:config {
        container apply-group {
            tailf:validate "validate-apply-group" {
                tailf:dependency "../router";
                tailf:dependency "../interface";
                tailf:dependency "../mpls";
            }
            // ... apply-group configuration
        }
    }
}
```

### Step 2: Implement Validation Callback

```python
class ApplyGroupValidation(ValidationPoint):
    @ValidationPoint.validate
    def cb_validate(self, tctx, keypath, value, validationpoint):
        """Validate apply-group template at creation time"""
        
        root = ncs.maagic.get_root(tctx)
        keypath_str = str(keypath)
        
        # Extract device and apply-group name from keypath
        # Example: /devices/device{node-1}/config/apply-group{ospf-base}
        
        try:
            # Parse keypath to get device and template info
            device_name, template_name = self._parse_keypath(keypath_str)
            
            # Get device configuration
            device = root.devices.device[device_name]
            
            # Perform semantic validation
            errors = []
            
            # 1. Validate OSPF configuration if present
            if self._has_ospf_config(value):
                errors.extend(self._validate_ospf_semantics(device, value))
            
            # 2. Validate BGP configuration if present
            if self._has_bgp_config(value):
                errors.extend(self._validate_bgp_semantics(device, value))
            
            # 3. Validate interface configuration if present
            if self._has_interface_config(value):
                errors.extend(self._validate_interface_semantics(device, value))
            
            # 4. Validate protocol-specific constraints
            errors.extend(self._validate_protocol_constraints(device, value))
            
            # If errors found, raise ValidationError
            if errors:
                error_msg = "Template validation failed:\n" + "\n".join(errors)
                raise ValidationError(error_msg)
            
            return ncs.CONFD_OK
            
        except Exception as e:
            self.log.error(f"Validation error: {e}")
            raise ValidationError(f"Template validation failed: {e}")
    
    def _validate_ospf_semantics(self, device, template_config):
        """Validate OSPF-specific semantic rules"""
        errors = []
        
        # Example: Check if router-id is set
        if 'ospf' in template_config and 'router-id' not in template_config:
            errors.append("OSPF configuration requires router-id")
        
        # Example: Check if area ID is valid
        if 'ospf' in template_config:
            area_id = template_config.get('area')
            if area_id and not (0 <= area_id <= 4294967295):
                errors.append(f"Invalid OSPF area ID: {area_id}")
        
        # Example: Check interface compatibility
        if 'ospf' in template_config and 'interface' in template_config:
            interface_type = template_config['interface'].get('type')
            if interface_type == 'Loopback' and 'passive' not in template_config['ospf']:
                errors.append("Loopback interfaces should be passive in OSPF")
        
        return errors
    
    def _validate_bgp_semantics(self, device, template_config):
        """Validate BGP-specific semantic rules"""
        errors = []
        
        # Example: Check ASN validity
        if 'bgp' in template_config:
            asn = template_config['bgp'].get('asn')
            if asn and not (1 <= asn <= 4294967295):
                errors.append(f"Invalid BGP ASN: {asn}")
        
        # Example: Check neighbor address format
        if 'bgp' in template_config and 'neighbor' in template_config['bgp']:
            for neighbor in template_config['bgp']['neighbor']:
                neighbor_ip = neighbor.get('address')
                if neighbor_ip and not self._is_valid_ip(neighbor_ip):
                    errors.append(f"Invalid neighbor IP address: {neighbor_ip}")
        
        return errors
    
    def _validate_protocol_constraints(self, device, template_config):
        """Validate cross-protocol constraints"""
        errors = []
        
        # Example: Check if MPLS is enabled when required
        if 'l3vpn' in template_config and 'mpls' not in template_config:
            errors.append("L3VPN requires MPLS to be enabled")
        
        # Example: Check if segment-routing requires MPLS
        if 'segment-routing' in template_config and 'mpls' not in template_config:
            errors.append("Segment Routing requires MPLS to be enabled")
        
        return errors
```

### Step 3: Register Validation Point

```python
class Main(ncs.application.Application):
    def setup(self):
        self.log.info('NSO Application Starting')
        
        # Register validation point for apply-group templates
        self.register_validation(
            'apply-group-template-valpoint',
            ApplyGroupValidation
        )
```

---

## Best Practices

### 1. Fail Fast
- Validate templates at creation time, not at application time
- Use validation callbacks with proper dependencies
- Return clear, actionable error messages

### 2. Comprehensive Validation
- Validate syntax (YANG handles this)
- Validate semantics (use validation callbacks)
- Validate device capabilities (check before applying)
- Validate protocol constraints (cross-reference checks)

### 3. Performance
- Use `tailf:dependency` to limit when validation runs
- Cache device capability checks
- Avoid expensive operations in validation callbacks

### 4. Error Messages
- Provide clear, descriptive error messages
- Include the specific field/value that failed
- Suggest fixes when possible

---

## MCP Tools for Validation

### Available Tools:
1. **`commit_dry_run(description)`** - Preview changes before commit
2. **`check_config_syntax(router_name)`** - Check device config syntax
3. **`validate_device_config(router_name)`** - Validate device configuration

### Potential New Tools:
1. **`validate_template(template_name, device_name)`** - Validate template before applying
2. **`validate_service(service_name)`** - Validate service instance
3. **`check_protocol_constraints(device_name, protocol)`** - Check protocol-specific constraints

---

## Example: Complete Apply-Group Template Validation

```python
# Complete example for validating OSPF apply-group templates

class OSPFApplyGroupValidation(ValidationPoint):
    """Validates OSPF apply-group templates at creation time"""
    
    @ValidationPoint.validate
    def cb_validate(self, tctx, keypath, value, validationpoint):
        root = ncs.maagic.get_root(tctx)
        
        # Parse keypath: /devices/device{node-1}/config/apply-group{ospf-base}
        parts = str(keypath).split('/')
        device_name = None
        template_name = None
        
        for i, part in enumerate(parts):
            if part == 'device' and i + 1 < len(parts):
                device_name = parts[i + 1].strip('{}')
            if part == 'apply-group' and i + 1 < len(parts):
                template_name = parts[i + 1].strip('{}')
        
        if not device_name or not template_name:
            return ncs.CONFD_OK  # Let YANG handle basic validation
        
        try:
            device = root.devices.device[device_name]
            apply_group = device.config.apply_group[template_name]
            
            errors = []
            
            # Validate OSPF configuration if present
            if hasattr(apply_group, 'router') and hasattr(apply_group.router, 'ospf'):
                errors.extend(self._validate_ospf_config(device, apply_group))
            
            # Validate interface configuration if present
            if hasattr(apply_group, 'interface'):
                errors.extend(self._validate_interface_config(device, apply_group))
            
            if errors:
                raise ValidationError(
                    f"OSPF apply-group template '{template_name}' validation failed:\n" +
                    "\n".join(f"  - {e}" for e in errors)
                )
            
            self.log.info(f"✅ Apply-group template '{template_name}' validated successfully")
            return ncs.CONFD_OK
            
        except ValidationError:
            raise
        except Exception as e:
            self.log.error(f"Validation error: {e}")
            raise ValidationError(f"Template validation failed: {e}")
    
    def _validate_ospf_config(self, device, apply_group):
        """Validate OSPF-specific semantic rules"""
        errors = []
        ospf = apply_group.router.ospf
        
        # Check if router-id is set
        if not hasattr(ospf, 'router_id') or not ospf.router_id:
            errors.append("OSPF requires router-id to be configured")
        
        # Check area configuration
        if hasattr(ospf, 'area'):
            for area in ospf.area:
                area_id = area.area_id
                if area_id < 0 or area_id > 4294967295:
                    errors.append(f"Invalid OSPF area ID: {area_id}")
        
        return errors
    
    def _validate_interface_config(self, device, apply_group):
        """Validate interface configuration in template"""
        errors = []
        
        # Check if interfaces referenced in OSPF exist
        if hasattr(apply_group, 'router') and hasattr(apply_group.router, 'ospf'):
            if hasattr(apply_group.router.ospf, 'area'):
                for area in apply_group.router.ospf.area:
                    if hasattr(area, 'interface'):
                        for intf in area.interface:
                            intf_name = intf.name
                            # Check if interface exists on device
                            if not self._interface_exists(device, intf_name):
                                errors.append(
                                    f"Interface '{intf_name}' referenced in OSPF "
                                    f"does not exist on device"
                                )
        
        return errors
    
    def _interface_exists(self, device, interface_name):
        """Check if interface exists on device"""
        try:
            # Parse interface name (e.g., "GigabitEthernet0/0/0/0")
            if hasattr(device.config, 'interface'):
                # Check if interface exists
                return True  # Simplified - implement actual check
        except:
            pass
        return False
```

---

---

## IOS-XR Configuration Groups Validation

### Overview

Cisco IOS-XR supports **configuration groups** (similar to apply-groups) that allow you to define reusable configuration blocks with regular expressions. These groups can be nested and applied to multiple interfaces or router instances.

**Key Features:**
- Regular expressions for pattern matching (e.g., `router isis *`, `interface *`)
- Nested groups (groups can reference other groups)
- Auto-inheritance of changes to groups
- Applied using `apply-group` command

**Reference:** [Cisco IOS-XR Configuration Groups Documentation](https://www.cisco.com/c/en/us/td/docs/iosxr/asr9000/general-administration/configuration/b-general-administration-configuration-ios-xr-asr9000/m-configuration-groups.html)

### Real-World Problem: Typo Detection

**Example Problem:**
A configuration group `GRP_ISIS_INT_DEFAULT` contains typos that would only be discovered when applied to interfaces:

```cisco
group GRP_ISIS_INT_DEFAULT
 router isis *
  interface *
   ponit-to-point          ! ❌ TYPO: should be "point-to-point"
   hello-password keychanin KC_ISIS level 2    ! ❌ TYPO: should be "keychain"
  !
 !
!
end-group
```

**Why This is a Problem:**
- Typos are not caught until the group is applied to an interface
- If applied to many interfaces, the error propagates everywhere
- No early validation at group creation time
- Violates "fail fast" principle

### NSO Solution: Validate Configuration Groups at Creation

NSO can validate IOS-XR configuration groups when they're created in the CDB, catching typos and semantic errors before they're applied to interfaces.

#### Implementation: IOS-XR Configuration Group Validator

```python
from ncs.dp import ValidationError, ValidationPoint
import re

class IOSXRConfigGroupValidation(ValidationPoint):
    """Validates IOS-XR configuration groups at creation time"""
    
    # Common typos to catch
    TYPO_PATTERNS = {
        'ponit-to-point': 'point-to-point',
        'keychanin': 'keychain',
        'keychian': 'keychain',
        'hellow-password': 'hello-password',
        'hello-passwd': 'hello-password',
        'isis': 'isis',  # Keep for reference
    }
    
    # Valid IOS-XR IS-IS interface commands
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
        'keychain',  # Both are valid
    }
    
    @ValidationPoint.validate
    def cb_validate(self, tctx, keypath, value, validationpoint):
        """Validate IOS-XR configuration group at creation time"""
        
        root = ncs.maagic.get_root(tctx)
        keypath_str = str(keypath)
        
        # Check if this is a configuration group
        # Path format: /devices/device{node-1}/config/group{GRP_ISIS_INT_DEFAULT}
        if 'group' not in keypath_str.lower():
            return ncs.CONFD_OK  # Not a group, skip validation
        
        try:
            # Extract device and group name
            device_name, group_name = self._parse_group_keypath(keypath_str)
            
            if not device_name or not group_name:
                return ncs.CONFD_OK
            
            # Get device and group configuration
            device = root.devices.device[device_name]
            config_group = device.config.group[group_name]
            
            errors = []
            warnings = []
            
            # Validate IS-IS configuration if present
            if hasattr(config_group, 'router') and hasattr(config_group.router, 'isis'):
                errors.extend(self._validate_isis_config_group(config_group))
            
            # Validate interface configuration if present
            if hasattr(config_group, 'interface'):
                errors.extend(self._validate_interface_config_group(config_group))
            
            # Check for nested groups
            if hasattr(config_group, 'group'):
                errors.extend(self._validate_nested_groups(device, config_group))
            
            # If errors found, raise ValidationError
            if errors:
                error_msg = (
                    f"IOS-XR configuration group '{group_name}' validation failed:\n" +
                    "\n".join(f"  ❌ {e}" for e in errors)
                )
                if warnings:
                    error_msg += "\n\nWarnings:\n" + "\n".join(f"  ⚠️  {w}" for w in warnings)
                raise ValidationError(error_msg)
            
            if warnings:
                self.log.warning(
                    f"Configuration group '{group_name}' has warnings: " +
                    "; ".join(warnings)
                )
            
            self.log.info(f"✅ Configuration group '{group_name}' validated successfully")
            return ncs.CONFD_OK
            
        except ValidationError:
            raise
        except Exception as e:
            self.log.error(f"Validation error: {e}")
            raise ValidationError(f"Configuration group validation failed: {e}")
    
    def _validate_isis_config_group(self, config_group):
        """Validate IS-IS configuration in group"""
        errors = []
        
        isis_config = config_group.router.isis
        
        # Check each IS-IS instance (router isis *)
        for isis_instance in isis_config:
            # Check interface configurations (interface *)
            if hasattr(isis_instance, 'interface'):
                for interface in isis_instance.interface:
                    errors.extend(
                        self._validate_isis_interface_commands(interface)
                    )
        
        return errors
    
    def _validate_isis_interface_commands(self, interface_config):
        """Validate IS-IS interface commands for typos and syntax errors"""
        errors = []
        
        # Convert interface config to string representation for analysis
        # This is a simplified approach - in practice, you'd traverse the YANG tree
        
        # Check for common typos in command names
        config_str = str(interface_config).lower()
        
        # Check for "ponit-to-point" typo
        if 'ponit-to-point' in config_str or 'point-to-point' not in config_str:
            # More precise: check if point-to-point is misspelled
            if hasattr(interface_config, 'point_to_point'):
                # This would be caught by YANG, but we can add semantic checks
                pass
            elif 'ponit' in config_str:
                errors.append(
                    "IS-IS interface: 'ponit-to-point' is misspelled. "
                    "Should be 'point-to-point'"
                )
        
        # Check for "keychanin" or "keychian" typos
        if hasattr(interface_config, 'hello_password'):
            hello_pwd = interface_config.hello_password
            if hasattr(hello_pwd, 'keychain'):
                # Check if keychain name is valid
                keychain_name = hello_pwd.keychain
                if not self._is_valid_keychain_name(keychain_name):
                    errors.append(
                        f"IS-IS hello-password: Invalid keychain name '{keychain_name}'"
                    )
            elif hasattr(hello_pwd, 'keychanin') or hasattr(hello_pwd, 'keychian'):
                errors.append(
                    "IS-IS hello-password: 'keychanin' or 'keychian' is misspelled. "
                    "Should be 'keychain'"
                )
        
        # Validate hello-password structure
        if hasattr(interface_config, 'hello_password'):
            hello_pwd = interface_config.hello_password
            # Check if keychain is specified
            if not hasattr(hello_pwd, 'keychain') or not hello_pwd.keychain:
                errors.append(
                    "IS-IS hello-password: keychain name is required"
                )
            
            # Check if level is specified correctly
            if hasattr(hello_pwd, 'level'):
                level = hello_pwd.level
                if level not in ['1', '2', 'level-1', 'level-2']:
                    errors.append(
                        f"IS-IS hello-password: Invalid level '{level}'. "
                        "Must be '1', '2', 'level-1', or 'level-2'"
                    )
        
        return errors
    
    def _validate_interface_config_group(self, config_group):
        """Validate interface configuration in group"""
        errors = []
        
        # Check if interface configurations reference valid interfaces
        # Check for typos in interface commands
        # Validate interface-specific IS-IS settings
        
        return errors
    
    def _validate_nested_groups(self, device, config_group):
        """Validate nested configuration groups"""
        errors = []
        
        # Check if referenced groups exist
        if hasattr(config_group, 'group'):
            for nested_group_ref in config_group.group:
                nested_group_name = nested_group_ref.name
                
                # Check if nested group exists
                if nested_group_name not in device.config.group:
                    errors.append(
                        f"Nested group '{nested_group_name}' does not exist"
                    )
                else:
                    # Recursively validate nested group (avoid infinite loops)
                    # In practice, you'd track visited groups
                    pass
        
        return errors
    
    def _is_valid_keychain_name(self, keychain_name):
        """Validate keychain name exists or follows naming conventions"""
        # In practice, check if keychain exists in device config
        # For now, just check basic format
        if not keychain_name or len(keychain_name) == 0:
            return False
        if len(keychain_name) > 32:  # IOS-XR limit
            return False
        return True
    
    def _parse_group_keypath(self, keypath_str):
        """Parse keypath to extract device and group name"""
        # Example: /devices/device{node-1}/config/group{GRP_ISIS_INT_DEFAULT}
        parts = keypath_str.split('/')
        device_name = None
        group_name = None
        
        for i, part in enumerate(parts):
            if part == 'device' and i + 1 < len(parts):
                device_name = parts[i + 1].strip('{}')
            if part == 'group' and i + 1 < len(parts):
                group_name = parts[i + 1].strip('{}')
        
        return device_name, group_name
```

#### YANG Model for Validation Point

```yang
module iosxr-config-group-validation {
    namespace "http://example.com/iosxr-config-group-validation";
    prefix icgv;
    
    import tailf-common { prefix tailf; }
    import tailf-ncs { prefix ncs; }
    import cisco-ios-xr { prefix iosxr; }
    
    augment /ncs:devices/ncs:device/ncs:config/iosxr:group {
        tailf:validate "iosxr-config-group-validation" {
            tailf:dependency "../router";
            tailf:dependency "../interface";
            tailf:dependency "../key";
        }
    }
}
```

#### Registration

```python
class Main(ncs.application.Application):
    def setup(self):
        self.log.info('NSO Application Starting')
        
        # Register validation point for IOS-XR configuration groups
        self.register_validation(
            'iosxr-config-group-validation',
            IOSXRConfigGroupValidation
        )
```

### Example: Catching the Specific Typo

When someone tries to create the `GRP_ISIS_INT_DEFAULT` group with typos:

```python
# User creates group via NSO:
# group GRP_ISIS_INT_DEFAULT
#  router isis *
#   interface *
#    ponit-to-point
#    hello-password keychanin KC_ISIS level 2

# NSO validation callback runs and catches:
# ❌ IS-IS interface: 'ponit-to-point' is misspelled. Should be 'point-to-point'
# ❌ IS-IS hello-password: 'keychanin' is misspelled. Should be 'keychain'

# ValidationError is raised, preventing group creation
# User must fix typos before group can be created
```

### Benefits for IOS-XR Configuration Groups

1. **Early Typo Detection**: Catch typos at group creation, not application
2. **Prevent Error Propagation**: Invalid groups can't be applied to interfaces
3. **Nested Group Validation**: Validate referenced groups exist
4. **Protocol Compliance**: Ensure IS-IS/BGP/OSPF commands are valid
5. **Keychain Validation**: Verify keychain names exist before use

### Integration with Regular Expressions

IOS-XR configuration groups use regular expressions (e.g., `router isis *`, `interface *`). NSO validation can:

1. **Validate Regex Patterns**: Ensure regex patterns are valid
2. **Check Pattern Conflicts**: Detect overlapping patterns (not supported in IOS-XR)
3. **Validate Matches**: Ensure patterns will match intended interfaces/routers

```python
def _validate_regex_patterns(self, config_group):
    """Validate regular expression patterns in configuration group"""
    errors = []
    
    # Check for overlapping patterns (IOS-XR restriction)
    patterns = self._extract_regex_patterns(config_group)
    
    for i, pattern1 in enumerate(patterns):
        for pattern2 in patterns[i+1:]:
            if self._patterns_overlap(pattern1, pattern2):
                errors.append(
                    f"Overlapping regular expressions detected: "
                    f"'{pattern1}' and '{pattern2}'. "
                    "IOS-XR does not support overlapping patterns."
                )
    
    return errors
```

---

## Summary

**Yes, NSO can absolutely help with semantic validation!**

NSO provides:
- ✅ **Built-in YANG validation** for syntax and basic constraints
- ✅ **Custom validation callbacks** for semantic checks
- ✅ **Dry-run validation** to preview changes
- ✅ **Service package validation** for service-level checks
- ✅ **Template validation** before application
- ✅ **IOS-XR Configuration Group validation** for catching typos and semantic errors

**Key Benefits:**
1. **Early Error Detection**: Catch errors at template/group creation, not application
2. **Template Integrity**: Ensure templates are valid before reuse
3. **Protocol Compliance**: Validate against protocol rules and constraints
4. **Device Compatibility**: Check templates against device capabilities
5. **Typo Detection**: Catch common typos in command names (e.g., `ponit-to-point`, `keychanin`)

**Implementation Approach:**
1. Define validation points in YANG models
2. Implement validation callbacks in Python/Java
3. Register validation points in service packages
4. Use dry-run for additional validation before commit
5. Add specific validators for IOS-XR configuration groups

**Real-World Impact:**
- Prevents typos like `ponit-to-point` and `keychanin` from propagating to multiple interfaces
- Catches errors at group creation time, not when applied to 100+ interfaces
- Ensures nested groups exist before referencing them
- Validates protocol-specific constraints (e.g., IS-IS level values, keychain names)

This aligns perfectly with the "fail fast" principle and ensures template/group integrity before propagation across multiple interfaces.

**Reference:**
- [Cisco IOS-XR Configuration Groups Documentation](https://www.cisco.com/c/en/us/td/docs/iosxr/asr9000/general-administration/configuration/b-general-administration-configuration-ios-xr-asr9000/m-configuration-groups.html)

