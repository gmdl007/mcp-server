#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, '/Users/gudeng/NCS-614/src/ncs/pyapi')
os.environ['NCS_DIR'] = '/Users/gudeng/NCS-614'
from ncs import maapi, maagic

m = maapi.Maapi()
m.start_user_session('cisco', 'test_context_1')
t = m.start_write_trans()
root = maagic.get_root(t)

print('=== Creating OSPF Links Directly ===\n')

# Link 1: xr9kv-1 to xr9kv-2
print('Creating link: xr9kv-1::xr9kv-2')
link1 = root.ospf.link.create('xr9kv-1::xr9kv-2')
link1.area = '0'

# Device 1 (xr9kv-1)
dev1 = link1.device.create('xr9kv-1')
dev1.interface = '0/0/0/0'  # No prefix for template
dev1.ip = '10.0.0.1'
dev1.description = 'To xr9kv-2 GigabitEthernet0/0/0/0'

# Device 2 (xr9kv-2)
dev2 = link1.device.create('xr9kv-2')
dev2.interface = '0/0/0/0'  # No prefix for template
dev2.ip = '10.0.0.2'
dev2.description = 'To xr9kv-1 GigabitEthernet0/0/0/0'

print('  ✅ Link 1 created')

# Link 2: xr9kv-2 to xr9kv-3
print('Creating link: xr9kv-2::xr9kv-3')
link2 = root.ospf.link.create('xr9kv-2::xr9kv-3')
link2.area = '0'

# Device 1 (xr9kv-2)
dev1 = link2.device.create('xr9kv-2')
dev1.interface = '0/0/0/1'  # No prefix for template
dev1.ip = '10.0.1.2'
dev1.description = 'To xr9kv-3 GigabitEthernet0/0/0/0'

# Device 2 (xr9kv-3)
dev2 = link2.device.create('xr9kv-3')
dev2.interface = '0/0/0/0'  # No prefix for template
dev2.ip = '10.0.1.3'
dev2.description = 'To xr9kv-2 GigabitEthernet0/0/0/1'

print('  ✅ Link 2 created')

print('\n=== Applying changes ===')
try:
    t.apply()
    print('✅ All OSPF links created successfully!')
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()

m.end_user_session()

