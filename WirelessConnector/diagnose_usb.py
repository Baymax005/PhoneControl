"""
🔍 ADB USB CONNECTION DIAGNOSTICS
Quick check to see why phone isn't connecting
"""

import subprocess
import os
from colorama import Fore, Style, init

init(autoreset=True)

def run_cmd(cmd):
    """Run command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1

print(f"{Fore.CYAN}╔═══════════════════════════════════════╗{Style.RESET_ALL}")
print(f"{Fore.CYAN}║   ADB USB DIAGNOSTICS                 ║{Style.RESET_ALL}")
print(f"{Fore.CYAN}╚═══════════════════════════════════════╝{Style.RESET_ALL}\n")

# 1. Check if ADB exists
print(f"{Fore.YELLOW}[1] Checking ADB installation...{Style.RESET_ALL}")
out, err, code = run_cmd("adb version")
if code == 0:
    version = out.split('\n')[0]
    print(f"{Fore.GREEN}    ✓ ADB found: {version}{Style.RESET_ALL}")
else:
    print(f"{Fore.RED}    ✗ ADB not found!{Style.RESET_ALL}")
    print(f"{Fore.RED}    Install with: scoop install adb{Style.RESET_ALL}")
    exit(1)

# 2. Check ADB server
print(f"\n{Fore.YELLOW}[2] Checking ADB server...{Style.RESET_ALL}")
out, err, code = run_cmd("adb start-server")
if "daemon started" in out.lower() or "daemon not running" in out.lower():
    print(f"{Fore.GREEN}    ✓ ADB server started{Style.RESET_ALL}")
else:
    print(f"{Fore.GREEN}    ✓ ADB server already running{Style.RESET_ALL}")

# 3. Check for connected devices
print(f"\n{Fore.YELLOW}[3] Checking for USB devices...{Style.RESET_ALL}")
out, err, code = run_cmd("adb devices -l")
print(f"\n{Fore.CYAN}Raw output:{Style.RESET_ALL}")
print(out)

lines = [line for line in out.strip().split('\n')[1:] if line.strip()]
if not lines:
    print(f"{Fore.RED}    ✗ No devices found!{Style.RESET_ALL}")
    print(f"\n{Fore.YELLOW}🔧 TROUBLESHOOTING STEPS:{Style.RESET_ALL}\n")
    
    print(f"{Fore.CYAN}Step 1: Enable Developer Options{Style.RESET_ALL}")
    print("  • Settings → About Phone")
    print("  • Tap 'Build Number' 7 times")
    print("  • You'll see 'You are now a developer!'")
    
    print(f"\n{Fore.CYAN}Step 2: Enable USB Debugging{Style.RESET_ALL}")
    print("  • Settings → Developer Options")
    print("  • Toggle 'USB Debugging' ON")
    
    print(f"\n{Fore.CYAN}Step 3: Check USB Connection{Style.RESET_ALL}")
    print("  • Use a DATA cable (not charging-only cable)")
    print("  • Try different USB port on PC")
    print("  • Check phone notification - select 'File Transfer' mode")
    
    print(f"\n{Fore.CYAN}Step 4: Install Drivers (if needed){Style.RESET_ALL}")
    print("  • Some phones need specific USB drivers")
    print("  • Check manufacturer website")
    print("  • Google: '[Your Phone Model] USB drivers'")
    
    print(f"\n{Fore.CYAN}Step 5: Restart Everything{Style.RESET_ALL}")
    print("  • Unplug USB")
    print("  • Run: adb kill-server")
    print("  • Run: adb start-server")
    print("  • Plug USB back in")
    
    print(f"\n{Fore.CYAN}Step 6: Check Authorization{Style.RESET_ALL}")
    print("  • Look for popup on phone: 'Allow USB debugging?'")
    print("  • Check 'Always allow from this computer'")
    print("  • Tap 'Allow'")
    
else:
    for line in lines:
        parts = line.split('\t')
        if len(parts) >= 2:
            device_id = parts[0]
            state = parts[1]
            
            if state == "device":
                print(f"{Fore.GREEN}    ✓ Device found: {device_id}{Style.RESET_ALL}")
                print(f"{Fore.GREEN}    ✓ Status: Authorized and ready!{Style.RESET_ALL}")
                
                # Get device info
                out2, _, _ = run_cmd(f"adb -s {device_id} shell getprop ro.product.model")
                if out2:
                    print(f"{Fore.GREEN}    ✓ Model: {out2.strip()}{Style.RESET_ALL}")
                
                print(f"\n{Fore.GREEN}✅ DEVICE IS READY FOR WIRELESS SETUP!{Style.RESET_ALL}")
                print(f"\n{Fore.YELLOW}Next step:{Style.RESET_ALL}")
                print(f"  Run: python wireless_connector.py")
                print(f"  Choose: Option 3 (USB to Wireless)")
                
            elif state == "unauthorized":
                print(f"{Fore.RED}    ✗ Device found but UNAUTHORIZED!{Style.RESET_ALL}")
                print(f"\n{Fore.YELLOW}⚠️  FIX:{Style.RESET_ALL}")
                print(f"  1. Check your phone screen")
                print(f"  2. You should see: 'Allow USB debugging?'")
                print(f"  3. Tap 'Always allow from this computer'")
                print(f"  4. Tap 'Allow'")
                print(f"  5. Run this script again")
                
            elif state == "offline":
                print(f"{Fore.RED}    ✗ Device is OFFLINE!{Style.RESET_ALL}")
                print(f"\n{Fore.YELLOW}⚠️  FIX:{Style.RESET_ALL}")
                print(f"  1. Unplug USB cable")
                print(f"  2. Restart phone")
                print(f"  3. Reconnect USB")
                
            else:
                print(f"{Fore.YELLOW}    ! Device state: {state}{Style.RESET_ALL}")

# 4. Test ADB command
if lines and "device" in out:
    print(f"\n{Fore.YELLOW}[4] Testing ADB commands...{Style.RESET_ALL}")
    device_id = lines[0].split('\t')[0]
    out, err, code = run_cmd(f"adb -s {device_id} shell echo 'Connection test'")
    if code == 0 and "Connection test" in out:
        print(f"{Fore.GREEN}    ✓ ADB commands working!{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}    ✗ ADB commands failing{Style.RESET_ALL}")

print(f"\n{Fore.CYAN}{'='*40}{Style.RESET_ALL}")
print(f"{Fore.CYAN}Diagnostics complete!{Style.RESET_ALL}")
input(f"\n{Fore.YELLOW}Press Enter to exit...{Style.RESET_ALL}")
