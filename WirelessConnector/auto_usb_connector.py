
"""
🔌 ONE-TIME SETUP WIZARD
First time setup (5 minutes), then everything is automatic forever!

IMPORTANT: Android security prevents apps from enabling USB debugging automatically.
This is a GOOD security feature! But we only need to do it ONCE.
"""

import subprocess
import time
import os
from colorama import Fore, Style, init

init(autoreset=True)

def run_cmd(cmd):
    """Run command"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1

print(f"{Fore.CYAN}╔═══════════════════════════════════════════════════╗{Style.RESET_ALL}")
print(f"{Fore.CYAN}║   ONE-TIME SETUP WIZARD                           ║{Style.RESET_ALL}")
print(f"{Fore.CYAN}╚═══════════════════════════════════════════════════╝{Style.RESET_ALL}\n")

print(f"{Fore.RED}⚠️  IMPORTANT - READ THIS:{Style.RESET_ALL}\n")
print(f"{Fore.YELLOW}Android BLOCKS automatic USB debugging for security.{Style.RESET_ALL}")
print(f"{Fore.YELLOW}This prevents malware from taking control of your phone.{Style.RESET_ALL}")
print(f"{Fore.YELLOW}You MUST enable it manually on your phone (ONE TIME ONLY).{Style.RESET_ALL}\n")

print(f"{Fore.GREEN}✅ After this setup, everything is automatic forever!{Style.RESET_ALL}\n")

print(f"{Fore.CYAN}This wizard will:{Style.RESET_ALL}")
print("  1. Guide you to enable USB debugging (ONE TIME)")
print("  2. Enable wireless ADB")
print("  3. Save your device")
print("  4. Then you NEVER need USB cable again!")
print()

# Check if already set up
config_file = "wireless_devices.json"
if os.path.exists(config_file):
    import json
    with open(config_file, 'r') as f:
        devices = json.load(f)
    if devices:
        print(f"{Fore.GREEN}[✓] Found {len(devices)} saved device(s):{Style.RESET_ALL}")
        for name in devices:
            print(f"    • {name}")
        print()
        skip = input(f"{Fore.YELLOW}Skip setup and use saved devices? (Y/n): {Style.RESET_ALL}").strip().lower()
        if skip != 'n':
            print(f"\n{Fore.GREEN}Run: python wireless_connector.py{Style.RESET_ALL}")
            print(f"{Fore.GREEN}Then choose: Option 1 (Connect to Saved Device){Style.RESET_ALL}")
            input(f"\n{Fore.YELLOW}Press Enter to exit...{Style.RESET_ALL}")
            exit(0)

print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")

print(f"{Fore.YELLOW}📱 STEP 1: ENABLE USB DEBUGGING (5 MINUTES){Style.RESET_ALL}\n")

print(f"{Fore.CYAN}On your phone, do this:{Style.RESET_ALL}\n")

print(f"{Fore.GREEN}A. Enable Developer Options:{Style.RESET_ALL}")
print("   1. Open Settings")
print("   2. Go to 'About Phone' (or 'About Device')")
print("   3. Find 'Build Number'")
print("   4. Tap it 7 TIMES quickly")
print("   5. You'll see: 'You are now a developer!'")
print()

print(f"{Fore.GREEN}B. Enable USB Debugging:{Style.RESET_ALL}")
print("   1. Go back to Settings")
print("   2. Find 'Developer Options' (usually under System)")
print("   3. Toggle 'USB Debugging' to ON")
print("   4. Confirm when it asks")
print()

print(f"{Fore.GREEN}C. Optional but recommended:{Style.RESET_ALL}")
print("   • Enable 'Stay awake' (screen stays on while charging)")
print("   • Enable 'USB debugging (Security settings)'")
print()

done_settings = input(f"{Fore.YELLOW}Done with settings? Press Enter...{Style.RESET_ALL}")

print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")

# Start ADB server
print(f"{Fore.CYAN}[*] Starting ADB server...{Style.RESET_ALL}")
run_cmd("adb start-server")

print(f"{Fore.YELLOW}� STEP 2: CONNECT USB CABLE{Style.RESET_ALL}\n")

print(f"{Fore.GREEN}1. Plug USB cable into phone and PC{Style.RESET_ALL}")
print(f"{Fore.GREEN}2. On phone notification: Select 'File Transfer' or 'MTP' mode{Style.RESET_ALL}")
print(f"{Fore.GREEN}3. IMPORTANT: A popup will appear on phone:{Style.RESET_ALL}")
print(f"   {Fore.CYAN}'Allow USB debugging?'{Style.RESET_ALL}")
print(f"   {Fore.CYAN}→ Check 'Always allow from this computer'{Style.RESET_ALL}")
print(f"   {Fore.CYAN}→ Tap 'Allow' or 'OK'{Style.RESET_ALL}")
print()

print(f"{Fore.YELLOW}🔌 PLUG IN YOUR USB CABLE NOW!{Style.RESET_ALL}\n")

print(f"{Fore.CYAN}Waiting for device...{Style.RESET_ALL}\n")

device_id = None
detected = False

# Wait for device (30 seconds)
for i in range(30):
    out, err, code = run_cmd("adb devices")
    
    lines = [line for line in out.strip().split('\n')[1:] if line.strip()]
    
    for line in lines:
        parts = line.split('\t')
        if len(parts) >= 2:
            dev_id = parts[0]
            state = parts[1]
            
            if state == "unauthorized":
                print(f"{Fore.YELLOW}[{i+1}/30] Device detected but UNAUTHORIZED{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}        → Check phone screen and tap 'Allow'!{Style.RESET_ALL}")
            elif state == "device":
                device_id = dev_id
                detected = True
                print(f"\n{Fore.GREEN}[✓] Device authorized: {device_id}{Style.RESET_ALL}")
                break
    
    if detected:
        break
    
    if i % 3 == 0 and i > 0:
        print(f"{Fore.CYAN}[{i+1}/30] Still waiting... Is cable plugged in?{Style.RESET_ALL}")
    
    time.sleep(1)

if not detected:
    print(f"\n{Fore.RED}[✗] No device detected after 30 seconds{Style.RESET_ALL}")
    print(f"\n{Fore.YELLOW}🔧 COMMON ISSUES:{Style.RESET_ALL}\n")
    
    print(f"{Fore.CYAN}Issue 1: USB Debugging not enabled{Style.RESET_ALL}")
    print("  → Go back to Step 1 and enable it")
    print()
    
    print(f"{Fore.CYAN}Issue 2: Didn't tap 'Allow' on popup{Style.RESET_ALL}")
    print("  → Check phone screen for popup")
    print("  → Tap 'Allow USB debugging'")
    print()
    
    print(f"{Fore.CYAN}Issue 3: Wrong USB mode{Style.RESET_ALL}")
    print("  → Pull down phone notification")
    print("  → Tap USB notification")
    print("  → Select 'File Transfer' or 'MTP'")
    print()
    
    print(f"{Fore.CYAN}Issue 4: Bad USB cable{Style.RESET_ALL}")
    print("  → Try different cable (must be DATA cable)")
    print("  → Charging-only cables won't work")
    print()
    
    print(f"{Fore.CYAN}Issue 5: Drivers not installed{Style.RESET_ALL}")
    print("  → Some phones need specific USB drivers")
    print("  → Google: '[Your Phone Brand] USB drivers Windows'")
    print()
    
    retry = input(f"{Fore.YELLOW}Try again? (y/n): {Style.RESET_ALL}").strip().lower()
    if retry == 'y':
        print(f"\n{Fore.CYAN}Running diagnostics first...{Style.RESET_ALL}\n")
        os.system("python diagnose_usb.py")
        retry2 = input(f"\n{Fore.YELLOW}Run setup again? (y/n): {Style.RESET_ALL}").strip().lower()
        if retry2 == 'y':
            os.system("python auto_usb_connector.py")
    
    input(f"\n{Fore.YELLOW}Press Enter to exit...{Style.RESET_ALL}")
    exit(1)

# Get device model
print(f"\n{Fore.CYAN}[*] Getting device info...{Style.RESET_ALL}")
out, _, _ = run_cmd(f"adb -s {device_id} shell getprop ro.product.model")
model = out.strip() or "Unknown Device"
print(f"{Fore.GREEN}[✓] Model: {model}{Style.RESET_ALL}")

# Enable wireless mode
print(f"\n{Fore.CYAN}[*] Enabling wireless mode...{Style.RESET_ALL}")
out, err, code = run_cmd(f"adb -s {device_id} tcpip 5555")

if code != 0:
    print(f"{Fore.RED}[✗] Failed to enable wireless mode: {err}{Style.RESET_ALL}")
    input(f"\n{Fore.YELLOW}Press Enter to exit...{Style.RESET_ALL}")
    exit(1)

print(f"{Fore.GREEN}[✓] Wireless mode enabled on port 5555{Style.RESET_ALL}")

# Wait for TCP mode to fully initialize
time.sleep(3)

# Verify device is still authorized
print(f"\n{Fore.CYAN}[*] Verifying authorization...{Style.RESET_ALL}")
out, err, code = run_cmd(f"adb -s {device_id} shell echo test")
if "unauthorized" in err.lower() or "unauthorized" in out.lower():
    print(f"{Fore.RED}[✗] Device became unauthorized!{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[!] Check your phone for authorization popup{Style.RESET_ALL}")
    input(f"{Fore.YELLOW}Press Enter after allowing...{Style.RESET_ALL}")
    
    # Restart ADB and reconnect
    run_cmd("adb kill-server")
    time.sleep(1)
    run_cmd("adb start-server")
    time.sleep(2)
    
    # Wait for device again
    print(f"{Fore.CYAN}[*] Reconnecting...{Style.RESET_ALL}")
    for i in range(10):
        out, _, _ = run_cmd("adb devices")
        if device_id in out and "device" in out:
            print(f"{Fore.GREEN}[✓] Re-authorized!{Style.RESET_ALL}")
            break
        time.sleep(1)
    
    # Re-enable wireless mode
    print(f"{Fore.CYAN}[*] Re-enabling wireless mode...{Style.RESET_ALL}")
    run_cmd(f"adb -s {device_id} tcpip 5555")
    time.sleep(2)
elif "test" in out:
    print(f"{Fore.GREEN}[✓] Device authorized and responsive{Style.RESET_ALL}")

# Get IP address
print(f"\n{Fore.CYAN}[*] Getting phone IP address...{Style.RESET_ALL}")

# Try multiple methods to get IP
device_ip = None
import re

# Method -1: Simple test first to ensure shell works
test_out, test_err, test_code = run_cmd(f"adb -s {device_id} shell echo 'connection_test'")
if "unauthorized" in test_err.lower():
    print(f"{Fore.RED}[✗] Still unauthorized! Please check phone screen{Style.RESET_ALL}")
    input(f"{Fore.YELLOW}Tap 'Allow' on phone, then press Enter...{Style.RESET_ALL}")
    run_cmd("adb kill-server")
    time.sleep(1)
    run_cmd("adb start-server")
    time.sleep(2)
    # Try to enable tcpip again
    run_cmd(f"adb -s {device_id} tcpip 5555")
    time.sleep(2)

# Method 0: Direct shell command with quotes (works on most devices)
print(f"{Fore.CYAN}[*] Trying method 0: Direct shell...{Style.RESET_ALL}")
out, _, _ = run_cmd(f'adb -s {device_id} shell "ip addr show wlan0"')
if out:
    ip_match = re.search(r'inet\s+(\d+\.\d+\.\d+\.\d+)', out)
    if ip_match:
        device_ip = ip_match.group(1)
        print(f"{Fore.GREEN}[✓] Phone IP (direct shell): {device_ip}{Style.RESET_ALL}")

# Method 1: ip addr show wlan0
if not device_ip:
    print(f"{Fore.CYAN}[*] Trying method 1: ip addr show wlan0...{Style.RESET_ALL}")
    out, _, _ = run_cmd(f"adb -s {device_id} shell ip addr show wlan0")
if out:
    # Look for: inet 192.168.x.x/24
    ip_match = re.search(r'inet\s+(\d+\.\d+\.\d+\.\d+)', out)
    if ip_match:
        device_ip = ip_match.group(1)
        print(f"{Fore.GREEN}[✓] Phone IP (wlan0): {device_ip}{Style.RESET_ALL}")

# Method 2: netcfg (older Android)
if not device_ip:
    print(f"{Fore.CYAN}[*] Trying method 2: netcfg...{Style.RESET_ALL}")
    out, _, _ = run_cmd(f"adb -s {device_id} shell netcfg")
    if out:
        # Look for wlan0 line with IP
        for line in out.split('\n'):
            if 'wlan0' in line:
                ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                if ip_match:
                    ip = ip_match.group(1)
                    if not ip.startswith('0.') and not ip.startswith('127.'):
                        device_ip = ip
                        print(f"{Fore.GREEN}[✓] Phone IP (netcfg): {device_ip}{Style.RESET_ALL}")
                        break

# Method 3: ifconfig wlan0
if not device_ip:
    print(f"{Fore.CYAN}[*] Trying method 3: ifconfig wlan0...{Style.RESET_ALL}")
    out, _, _ = run_cmd(f"adb -s {device_id} shell ifconfig wlan0")
    if out:
        # Look for: inet addr:192.168.x.x
        ip_match = re.search(r'inet\s+addr:(\d+\.\d+\.\d+\.\d+)', out)
        if not ip_match:
            # Some versions use just: inet 192.168.x.x
            ip_match = re.search(r'inet\s+(\d+\.\d+\.\d+\.\d+)', out)
        if ip_match:
            device_ip = ip_match.group(1)
            print(f"{Fore.GREEN}[✓] Phone IP (ifconfig): {device_ip}{Style.RESET_ALL}")

# Method 4: ip route (get source IP)
if not device_ip:
    print(f"{Fore.CYAN}[*] Trying method 4: ip route...{Style.RESET_ALL}")
    out, _, _ = run_cmd(f"adb -s {device_id} shell ip route")
    if out:
        # Look for: src 192.168.x.x
        ip_match = re.search(r'src\s+(\d+\.\d+\.\d+\.\d+)', out)
        if ip_match:
            device_ip = ip_match.group(1)
            print(f"{Fore.GREEN}[✓] Phone IP (route): {device_ip}{Style.RESET_ALL}")

# Method 5: getprop dhcp.wlan0 (some phones store it here)
if not device_ip:
    print(f"{Fore.CYAN}[*] Trying method 5: getprop...{Style.RESET_ALL}")
    out, _, _ = run_cmd(f"adb -s {device_id} shell getprop dhcp.wlan0.ipaddress")
    if out and out.strip():
        device_ip = out.strip()
        print(f"{Fore.GREEN}[✓] Phone IP (getprop): {device_ip}{Style.RESET_ALL}")

# Method 6: dumpsys wifi (last resort)
if not device_ip:
    print(f"{Fore.CYAN}[*] Trying method 6: dumpsys wifi...{Style.RESET_ALL}")
    out, _, _ = run_cmd(f"adb -s {device_id} shell dumpsys wifi")
    if out:
        # Look for mIpAddress or IP address pattern
        ip_match = re.search(r'mIpAddress["\s:=]+(\d+\.\d+\.\d+\.\d+)', out)
        if not ip_match:
            # Try to find any IP in the output
            ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', out)
            if ip_match:
                ip = ip_match.group(1)
                # Make sure it's not 0.0.0.0 or 127.x.x.x
                if not ip.startswith('0.') and not ip.startswith('127.'):
                    device_ip = ip
                    print(f"{Fore.GREEN}[✓] Phone IP (dumpsys): {device_ip}{Style.RESET_ALL}")
        elif ip_match:
            device_ip = ip_match.group(1)
            print(f"{Fore.GREEN}[✓] Phone IP (dumpsys): {device_ip}{Style.RESET_ALL}")

# Method 7: Scan local network (fallback)
if not device_ip:
    print(f"{Fore.CYAN}[*] Trying method 7: Network scan...{Style.RESET_ALL}")
    # Get PC's IP to determine network
    import socket
    try:
        hostname = socket.gethostname()
        pc_ip = socket.gethostbyname(hostname)
        network_prefix = '.'.join(pc_ip.split('.')[:-1])
        
        print(f"{Fore.CYAN}[*] Your PC IP: {pc_ip}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[*] Scanning network {network_prefix}.0/24 for phone...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[!] This may take 30 seconds...{Style.RESET_ALL}")
        
        # Get phone's MAC or serial for identification
        mac_out, _, _ = run_cmd(f'adb -s {device_id} shell "cat /sys/class/net/wlan0/address"')
        phone_mac = mac_out.strip().replace(':', '').lower() if mac_out else None
        
        # Quick scan of likely IPs
        for i in range(2, 255):
            test_ip = f"{network_prefix}.{i}"
            # Try to connect briefly
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.05)
            result = sock.connect_ex((test_ip, 5555))
            sock.close()
            
            if result == 0:
                print(f"{Fore.YELLOW}[?] Found device at {test_ip} (testing...){Style.RESET_ALL}")
                device_ip = test_ip
                break
    except Exception as e:
        print(f"{Fore.RED}[✗] Network scan failed: {e}{Style.RESET_ALL}")

if not device_ip:
    print(f"{Fore.RED}[✗] Could not find IP address automatically{Style.RESET_ALL}")
    
    # Debug: Show raw command output
    debug = input(f"\n{Fore.YELLOW}Show debug info? (y/n): {Style.RESET_ALL}").strip().lower()
    if debug == 'y':
        print(f"\n{Fore.CYAN}Debug - Testing different command formats:{Style.RESET_ALL}\n")
        
        print("1. adb shell ip addr show wlan0:")
        out, err, code = run_cmd(f"adb -s {device_id} shell ip addr show wlan0")
        print(f"   Output: {out[:500] if out else '(empty)'}")
        print(f"   Error: {err[:200] if err else '(none)'}")
        print(f"   Code: {code}")
        
        print("\n2. adb shell 'ip addr show wlan0':")
        out, err, code = run_cmd(f"adb -s {device_id} shell 'ip addr show wlan0'")
        print(f"   Output: {out[:500] if out else '(empty)'}")
        print(f"   Error: {err[:200] if err else '(none)'}")
        
        print('\n3. adb shell "ip route | grep src":')
        out, err, code = run_cmd(f'adb -s {device_id} shell "ip route | grep src"')
        print(f"   Output: {out[:500] if out else '(empty)'}")
        
        print("\n4. adb shell (interactive test):")
        print("   Running: getprop dhcp.wlan0.ipaddress")
        out, err, code = run_cmd(f"adb -s {device_id} shell getprop dhcp.wlan0.ipaddress")
        print(f"   Output: {out[:500] if out else '(empty)'}")
        
        print("\n5. Direct ADB command:")
        print("   Running: adb shell getprop")
        out, err, code = run_cmd(f"adb -s {device_id} shell getprop | findstr wlan")
        print(f"   Output: {out[:500] if out else '(empty)'}")
        
        print()
    
    print(f"\n{Fore.YELLOW}Manual method:{Style.RESET_ALL}")
    print("  1. On phone: Settings → About → Status → IP Address")
    print("  2. Or: Settings → WiFi → Tap connected network → IP Address")
    manual_ip = input(f"\n{Fore.YELLOW}Enter IP address: {Style.RESET_ALL}").strip()
    device_ip = manual_ip

# Disconnect USB
print(f"\n{Fore.GREEN}✅ Setup complete!{Style.RESET_ALL}")
print(f"{Fore.YELLOW}[!] Keep USB cable connected for wireless authentication{Style.RESET_ALL}")
print(f"{Fore.CYAN}[*] Testing wireless connection first...{Style.RESET_ALL}\n")

# Connect wirelessly BEFORE disconnecting USB
time.sleep(1)
out, err, code = run_cmd(f"adb connect {device_ip}:5555")

connection_success = False

if "connected" in out.lower() or "already connected" in out.lower():
    print(f"{Fore.GREEN}[✓] Wireless connection successful!{Style.RESET_ALL}")
    connection_success = True
else:
    # Failed - try troubleshooting
    print(f"{Fore.RED}[✗] Initial wireless connection failed{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[!] Trying to fix authentication...{Style.RESET_ALL}\n")
    
    # Make sure wireless ADB is properly enabled
    print(f"{Fore.CYAN}[*] Re-enabling wireless mode...{Style.RESET_ALL}")
    run_cmd(f"adb -s {device_id} tcpip 5555")
    time.sleep(3)
    
    # Try connecting again
    print(f"{Fore.CYAN}[*] Attempting wireless connection...{Style.RESET_ALL}")
    out, err, code = run_cmd(f"adb connect {device_ip}:5555")
    
    if "connected" in out.lower():
        print(f"{Fore.GREEN}[✓] Connection successful!{Style.RESET_ALL}")
        connection_success = True
    else:
        print(f"{Fore.RED}[✗] Wireless connection failed: {out}{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}🔧 TROUBLESHOOTING:{Style.RESET_ALL}")
        print(f"  1. {Fore.CYAN}Make sure phone and PC are on SAME WiFi network{Style.RESET_ALL}")
        print(f"  2. {Fore.CYAN}Check if IP is correct: {device_ip}{Style.RESET_ALL}")
        print(f"  3. {Fore.CYAN}Try disabling firewall temporarily{Style.RESET_ALL}")
        print(f"  4. {Fore.CYAN}Some routers block ADB port 5555{Style.RESET_ALL}")
        
        manual = input(f"\n{Fore.YELLOW}Try manual connection after disconnecting USB? (y/n): {Style.RESET_ALL}").strip().lower()
        if manual == 'y':
            print(f"\n{Fore.CYAN}Disconnect USB cable now...{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter after disconnecting...{Style.RESET_ALL}")
            
            print(f"\n{Fore.CYAN}[*] Attempting connection...{Style.RESET_ALL}")
            for attempt in range(3):
                out, err, code = run_cmd(f"adb connect {device_ip}:5555")
                if "connected" in out.lower():
                    print(f"{Fore.GREEN}[✓] Connected on attempt {attempt + 1}!{Style.RESET_ALL}")
                    connection_success = True
                    break
                time.sleep(2)

if connection_success:
    # Now safe to disconnect USB if not already done
    print(f"\n{Fore.GREEN}✅ Now you can DISCONNECT the USB cable!{Style.RESET_ALL}")
    input(f"{Fore.YELLOW}Press Enter after disconnecting USB...{Style.RESET_ALL}")
    
    # Verify wireless still works after USB disconnect
    print(f"\n{Fore.CYAN}[*] Verifying wireless connection...{Style.RESET_ALL}")
    out2, _, _ = run_cmd(f"adb -s {device_ip}:5555 shell echo 'test'")
    
    if "test" in out2:
        print(f"{Fore.GREEN}[✓] Wireless connection verified!{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}[!] Connection may have dropped, reconnecting...{Style.RESET_ALL}")
        run_cmd(f"adb connect {device_ip}:5555")
    
    # Save device
    import json
    config_file = "wireless_devices.json"
    
    devices = {}
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            devices = json.load(f)
    
    # Generate device name
    device_name = model.replace(' ', '_')
    if device_name in devices:
        device_name = f"{device_name}_{device_ip.split('.')[-1]}"
    
    devices[device_name] = {
        "ip": device_ip,
        "port": 5555
    }
    
    with open(config_file, 'w') as f:
        json.dump(devices, f, indent=2)
    
    print(f"{Fore.GREEN}[✓] Device saved as '{device_name}'{Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}╔════════════════════════════════════════════════════╗{Style.RESET_ALL}")
    print(f"{Fore.GREEN}║   ✅ SETUP COMPLETE! YOU NEVER NEED USB AGAIN!    ║{Style.RESET_ALL}")
    print(f"{Fore.GREEN}╚════════════════════════════════════════════════════╝{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}📱 Your phone is now saved as: {Fore.GREEN}'{device_name}'{Style.RESET_ALL}")
    print(f"{Fore.CYAN}📡 IP Address: {Fore.GREEN}{device_ip}:5555{Style.RESET_ALL}")
    
    print(f"\n{Fore.YELLOW}🎉 FROM NOW ON (NO USB NEEDED):{Style.RESET_ALL}\n")
    
    print(f"{Fore.GREEN}Just run:{Style.RESET_ALL}")
    print(f"  {Fore.CYAN}python wireless_connector.py{Style.RESET_ALL}")
    print(f"  → Option 1: Connect to Saved Device")
    print(f"  → Select '{device_name}'")
    print(f"  → Option 6: Remote Control")
    print()
    
    print(f"{Fore.YELLOW}💡 Your phone and PC just need to be on same WiFi!{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}💡 No USB cable ever again!{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}💡 This setup was ONE TIME ONLY!{Style.RESET_ALL}")
    
    # Test the saved connection
    print(f"\n{Fore.CYAN}[*] Testing saved connection...{Style.RESET_ALL}")
    out_test, _, _ = run_cmd(f"adb -s {device_ip}:5555 shell getprop ro.build.version.release")
    if out_test.strip():
        print(f"{Fore.GREEN}[✓] Connection working! Android version: {out_test.strip()}{Style.RESET_ALL}")

else:
    print(f"\n{Fore.RED}[✗] Setup incomplete - wireless connection failed{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[!] You can try connecting manually later with:{Style.RESET_ALL}")
    print(f"{Fore.CYAN}    adb connect {device_ip}:5555{Style.RESET_ALL}")
    print(f"\n{Fore.YELLOW}[!] Or run this script again{Style.RESET_ALL}")

input(f"\n{Fore.YELLOW}Press Enter to exit...{Style.RESET_ALL}")
