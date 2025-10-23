"""
Quick script to fix saved device ports from 5000 to 5555
"""

import json

# Load devices
with open('wireless_devices.json', 'r') as f:
    devices = json.load(f)

# Fix ports
fixed_count = 0
for name, info in devices.items():
    if info['port'] == 5000:
        print(f"Fixing {name}: port 5000 → 5555")
        info['port'] = 5555
        fixed_count += 1

# Save
if fixed_count > 0:
    with open('wireless_devices.json', 'w') as f:
        json.dump(devices, f, indent=2)
    print(f"\n✓ Fixed {fixed_count} device(s)!")
    print("✓ Now your saved devices use the correct ADB port (5555)")
else:
    print("All devices already have correct ports!")

print("\nUpdated devices:")
print(json.dumps(devices, indent=2))
