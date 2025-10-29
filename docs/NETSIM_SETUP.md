# Netsim Setup Guide

Complete guide for setting up and managing Cisco NSO Netsim devices for testing and development.

---

## What is Netsim?

Netsim (Network Simulator) is NSO's built-in virtual device simulator that creates virtual Cisco IOS XR routers for testing NSO automation without physical hardware. Netsim devices run lightweight IOS XR images in containers.

---

## Netsim Device Configuration

### Device Details

The setup includes 3 virtual routers:

| Device Name | Netsim Dir | SSH Port | Status |
|------------|------------|----------|--------|
| xr9kv-1     | xr9kv0     | 10022    | Virtual |
| xr9kv-2     | xr9kv1     | 10023    | Virtual |
| xr9kv-3     | xr9kv2     | 10024    | Virtual |

**Device Specifications:**
- Platform: Cisco IOS XR 7.52.2
- NED Type: `cisco-iosxr-cli-7.52:cisco-iosxr-cli-7.52`
- Protocol: SSH (CLI)
- Credentials: `admin` / `admin`

---

## Starting Netsim Devices

### Method 1: Individual Start

```bash
cd /Users/gudeng/MCP_Server/netsim/xr9kv

# Start each device
./xr9kv0/start.sh &  # xr9kv-1
./xr9kv1/start.sh &  # xr9kv-2
./xr9kv2/start.sh &  # xr9kv-3

# Wait for devices to boot (30-60 seconds)
```

### Method 2: Start All at Once

```bash
cd /Users/gudeng/MCP_Server/netsim/xr9kv

for dir in xr9kv0 xr9kv1 xr9kv2; do
    cd $dir && ./start.sh & && cd ..
done
```

### Verify Devices are Running

```bash
# Check processes
ps aux | grep xr9kv

# Check logs (wait for "NSO netsim ready" message)
tail -f netsim/xr9kv/xr9kv0/xr9kv0.log
```

---

## Adding Devices to NSO

### Step-by-Step Device Addition

```bash
# Connect to NSO CLI
ncs_cli -u admin -C

# Enter configuration mode
admin@ncs# config

# Add device xr9kv-1
admin@ncs(config)# devices device xr9kv-1
admin@ncs(config-device-xr9kv-1)# device-type cli ned-id cisco-iosxr-cli-7.52:cisco-iosxr-cli-7.52
admin@ncs(config-device-xr9kv-1)# state admin-state unlocked
admin@ncs(config-device-xr9kv-1)# authgroup default
admin@ncs(config-device-xr9kv-1)# ned-settings
admin@ncs(config-device-xr9kv-1-ned-settings)# ssh
admin@ncs(config-device-xr9kv-1-ned-settings-ssh)# host-key-check false
admin@ncs(config-device-xr9kv-1-ned-settings-ssh)# exit
admin@ncs(config-device-xr9kv-1)# address localhost
admin@ncs(config-device-xr9kv-1)# port 10022
admin@ncs(config-device-xr9kv-1)# exit
admin@ncs(config)# commit

# Repeat for xr9kv-2 (port 10023) and xr9kv-3 (port 10024)
```

### Quick Script for All Devices

You can use this Python script to add all devices:

```python
# add_netsim_devices.py
import ncs.maapi as maapi
import ncs.maagic as maagic

devices = [
    ('xr9kv-1', 10022),
    ('xr9kv-2', 10023),
    ('xr9kv-3', 10024),
]

m = maapi.Maapi()
m.start_user_session('admin', 'python')
t = m.start_write_trans()
root = maagic.get_root(t)

for device_name, port in devices:
    device = root.devices.device.create(device_name)
    device.device_type.cli.ned_id = 'cisco-iosxr-cli-7.52:cisco-iosxr-cli-7.52'
    device.state.admin_state = 'unlocked'
    device.authgroup = 'default'
    device.ned_settings.ssh.host_key_check = False
    device.address = 'localhost'
    device.port = port

t.apply()
m.end_user_session()
print("✅ All devices added to NSO")
```

---

## Connecting and Syncing

### Connect to Devices

```bash
ncs_cli -u admin -C

# Connect to a device
admin@ncs# devices device xr9kv-1 connect

# Connect to all devices
admin@ncs# devices device * connect
```

### Sync Configuration

```bash
# Pull configuration from device to NSO
admin@ncs# devices device xr9kv-1 sync-from

# Push configuration from NSO to device
admin@ncs# devices device xr9kv-1 sync-to

# Sync all devices
admin@ncs# devices device * sync-from
```

### Verify Device Status

```bash
# Check device state
admin@ncs# show devices device * state

# Check device configuration
admin@ncs# show running-config devices device xr9kv-1 config

# Check sync status
admin@ncs# devices device xr9kv-1 check-sync
```

---

## SSH Access to Netsim Devices

### Direct SSH

```bash
# SSH to netsim devices
ssh -p 10022 admin@localhost  # xr9kv-1
ssh -p 10023 admin@localhost  # xr9kv-2
ssh -p 10024 admin@localhost  # xr9kv-3

# Credentials: admin / admin
```

### From SSH Session

Once connected, you can execute IOS XR commands:

```bash
# Show version
show version

# Show interfaces
show interfaces brief

# Show running configuration
show running-config

# Configure (if needed)
configure terminal
interface GigabitEthernet0/0/0/0
ip address 192.168.1.1 255.255.255.0
no shutdown
commit
```

---

## Stopping Netsim Devices

### Method 1: Individual Stop

```bash
cd /Users/gudeng/MCP_Server/netsim/xr9kv

./xr9kv0/stop.sh
./xr9kv1/stop.sh
./xr9kv2/stop.sh
```

### Method 2: Stop All

```bash
cd /Users/gudeng/MCP_Server/netsim/xr9kv

for dir in xr9kv0 xr9kv1 xr9kv2; do
    cd $dir && ./stop.sh && cd ..
done
```

### Method 3: Force Stop (if needed)

```bash
# Kill processes manually
pkill -f xr9kv
```

---

## Netsim Limitations

### Operational Data

Netsim devices have limited operational data compared to real hardware:

- **Live-status paths exist** but may be empty
- **Interface statistics** may not be populated
- **CDP/LLDP neighbors** will be empty (no real neighbors)
- **Hardware inventory** may be minimal

**Workaround**: Use `exec.any` to execute show commands for operational data.

### Command Support

Some show commands may not work fully on netsim:

- `show interfaces` - May show script errors
- `show ip ospf neighbor` - May show syntax errors
- `show platform` - May show element does not exist

**Working commands**:
- `show version` ✅
- `show inventory` ✅
- Basic configuration commands ✅

---

## Troubleshooting

### Device Won't Start

```bash
# Check if port is in use
lsof -i :10022
lsof -i :10023
lsof -i :10024

# Check netsim logs
tail -f netsim/xr9kv/xr9kv0/xr9kv0.log

# Verify NSO is running
ps aux | grep ncs
```

### Device Won't Connect in NSO

```bash
# Check device reachability
ping localhost  # Should work

# Check SSH connectivity
ssh -p 10022 admin@localhost

# Verify device configuration in NSO
ncs_cli -u admin -C
admin@ncs# show devices device xr9kv-1 config
```

### Sync Fails

```bash
# Ensure device is connected
admin@ncs# devices device xr9kv-1 connect

# Check device state
admin@ncs# show devices device xr9kv-1 state

# Try sync again
admin@ncs# devices device xr9kv-1 sync-from
```

---

## Best Practices

1. **Start devices before NSO operations** - Wait 30-60 seconds after starting
2. **Connect before sync** - Use `devices device * connect` first
3. **Sync-from regularly** - Keep NSO in sync with device state
4. **Use dry-run** - Test sync operations with `sync-from dry-run`
5. **Monitor logs** - Check netsim logs if issues occur

---

## Example Workflow

```bash
# 1. Start netsim devices
cd /Users/gudeng/MCP_Server/netsim/xr9kv
./xr9kv0/start.sh &
./xr9kv1/start.sh &
./xr9kv2/start.sh &
sleep 60  # Wait for boot

# 2. Add devices to NSO (if not already added)
# Use NSO CLI or Python script above

# 3. Connect and sync
ncs_cli -u admin -C
admin@ncs# devices device * connect
admin@ncs# devices device * sync-from

# 4. Verify
admin@ncs# show devices device * state
admin@ncs# devices device * check-sync

# 5. Use MCP tools
# Tools will now work with netsim devices
```

---

*Last Updated: 2025-01-21*
*NSO Version: 6.1.4*
*Netsim: Cisco IOS XR 7.52.2*

