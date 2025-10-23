"""
🌐 WIRELESS CONNECTION MANAGER
Connect to Android device from anywhere using IP address
Supports: Local WiFi, Remote IP, MAC Address discovery
"""

import subprocess
import re
import socket
import json
import os
from colorama import Fore, Style, init

init(autoreset=True)

class WirelessConnector:
    def __init__(self):
        self.config_file = "wireless_devices.json"
        self.devices = self.load_devices()
        
    def load_devices(self):
        """Load saved devices"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_device(self, name, ip, port=5555):
        """Save device configuration"""
        # Check if name already exists
        if name in self.devices:
            overwrite = input(f"{Fore.YELLOW}Device '{name}' already exists. Overwrite? (y/n): {Style.RESET_ALL}").strip().lower()
            if overwrite != 'y':
                print(f"{Fore.YELLOW}[!] Device not saved{Style.RESET_ALL}")
                return False
        
        self.devices[name] = {"ip": ip, "port": port}
        with open(self.config_file, 'w') as f:
            json.dump(self.devices, f, indent=2)
        print(f"{Fore.GREEN}[✓] Device '{name}' saved to {self.config_file}!{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[✓] Next time use Option 1 to connect instantly!{Style.RESET_ALL}")
        return True
    
    def run_command(self, cmd):
        """Execute shell command"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout, result.stderr, result.returncode
        except Exception as e:
            return "", str(e), 1
    
    def get_adb_path(self):
        """Find ADB executable"""
        paths = [
            "adb",
            os.path.expanduser("~\\scoop\\shims\\adb.exe"),
            "C:\\Android\\platform-tools\\adb.exe",
        ]
        for path in paths:
            out, err, code = self.run_command(f'"{path}" version')
            if code == 0:
                return path
        return "adb"
    
    def scan_network(self):
        """Scan local network for Android devices"""
        print(f"\n{Fore.CYAN}[*] Scanning local network for Android devices...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[!] This may take 1-2 minutes...{Style.RESET_ALL}\n")
        
        # Get local IP to determine network range
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        network_prefix = '.'.join(local_ip.split('.')[:-1])
        
        print(f"{Fore.GREEN}[+] Your PC IP: {local_ip}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] Scanning network: {network_prefix}.0/24{Style.RESET_ALL}\n")
        
        found_devices = []
        
        # Try common Android device ports
        for i in range(1, 255):
            ip = f"{network_prefix}.{i}"
            if ip == local_ip:
                continue
            
            # Try to connect to ADB port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)
            result = sock.connect_ex((ip, 5555))
            sock.close()
            
            if result == 0:
                print(f"{Fore.GREEN}[✓] Found device at {ip}:5555{Style.RESET_ALL}")
                found_devices.append(f"{ip}:5555")
        
        if found_devices:
            print(f"\n{Fore.GREEN}[✓] Found {len(found_devices)} device(s)!{Style.RESET_ALL}")
            return found_devices
        else:
            print(f"\n{Fore.YELLOW}[!] No devices found on local network{Style.RESET_ALL}")
            return []
    
    def connect_by_ip(self, ip_address, port=5555, auto_save=True):
        """Connect to device using IP address"""
        adb = self.get_adb_path()
        connection_string = f"{ip_address}:{port}"
        
        # Warning for wrong port
        if port != 5555:
            print(f"\n{Fore.YELLOW}⚠️  WARNING: You're using port {port}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}⚠️  ADB typically uses port 5555 for device control{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}⚠️  Port 5000 is for Flask web server (not ADB){Style.RESET_ALL}")
            
            correct = input(f"\n{Fore.YELLOW}Change to port 5555? (recommended) (y/n): {Style.RESET_ALL}").strip().lower()
            if correct == 'y':
                port = 5555
                connection_string = f"{ip_address}:{port}"
                print(f"{Fore.GREEN}[✓] Using correct ADB port: 5555{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}[*] Connecting to {connection_string}...{Style.RESET_ALL}")
        
        out, err, code = self.run_command(f'"{adb}" connect {connection_string}')
        
        if "connected" in out.lower() or "already connected" in out.lower():
            print(f"{Fore.GREEN}[✓] Successfully connected to {connection_string}!{Style.RESET_ALL}")
            
            # Get device info
            model = "Unknown Device"
            out2, _, _ = self.run_command(f'"{adb}" -s {connection_string} shell getprop ro.product.model')
            if out2:
                model = out2.strip()
                print(f"{Fore.GREEN}[✓] Device Model: {model}{Style.RESET_ALL}")
            
            # Check if already saved
            already_saved = False
            for saved_name, info in self.devices.items():
                if info['ip'] == ip_address and info['port'] == port:
                    already_saved = True
                    print(f"{Fore.GREEN}[✓] Device already saved as '{saved_name}'{Style.RESET_ALL}")
                    break
            
            # Ask to save if not already saved
            if not already_saved and auto_save:
                save = input(f"\n{Fore.YELLOW}Save this device for quick connect? (y/n): {Style.RESET_ALL}").strip().lower()
                if save == 'y':
                    name = input(f"Enter device name (e.g., '{model}'): ").strip()
                    if not name:
                        # Generate default name
                        name = model.replace(' ', '_') + f"_{ip_address.split('.')[-1]}"
                    self.save_device(name, ip_address, port)
            
            return True
        else:
            print(f"{Fore.RED}[✗] Connection failed!{Style.RESET_ALL}")
            if err:
                print(f"{Fore.RED}Error: {err}{Style.RESET_ALL}")
            return False
    
    def auto_enable_usb_debugging(self):
        """Attempt to auto-enable USB debugging when cable is connected"""
        adb = self.get_adb_path()
        
        print(f"\n{Fore.CYAN}[*] Auto-detecting USB connection...{Style.RESET_ALL}")
        
        # Start ADB server
        self.run_command(f'"{adb}" start-server')
        
        import time
        for i in range(5):
            out, err, code = self.run_command(f'"{adb}" devices')
            lines = [line for line in out.strip().split('\n')[1:] if line.strip()]
            
            if lines:
                for line in lines:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        device_id = parts[0]
                        state = parts[1]
                        
                        if state == "unauthorized":
                            print(f"{Fore.YELLOW}[!] Device detected but unauthorized{Style.RESET_ALL}")
                            print(f"{Fore.YELLOW}[!] Please check your phone and tap 'Allow'{Style.RESET_ALL}")
                            time.sleep(2)
                            continue
                        elif state == "device":
                            print(f"{Fore.GREEN}[✓] Device auto-detected: {device_id}{Style.RESET_ALL}")
                            return True, device_id
            
            if i < 4:
                print(f"{Fore.CYAN}[*] Waiting for device... ({i+1}/5){Style.RESET_ALL}")
                time.sleep(1)
        
        return False, None
    
    def usb_to_wireless(self):
        """Convert USB connection to wireless"""
        adb = self.get_adb_path()
        
        print(f"\n{Fore.CYAN}╔═══════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║   USB TO WIRELESS CONVERSION          ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚═══════════════════════════════════════╝{Style.RESET_ALL}")
        
        # Try auto-detection first
        auto_mode = input(f"\n{Fore.YELLOW}Try auto-detection? (Y/n): {Style.RESET_ALL}").strip().lower()
        
        if auto_mode != 'n':
            print(f"\n{Fore.CYAN}🔌 Plug in your USB cable now...{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[!] When you see popup on phone, tap 'Allow USB debugging'{Style.RESET_ALL}\n")
            
            detected, device_id = self.auto_enable_usb_debugging()
            
            if detected:
                print(f"{Fore.GREEN}[✓] Auto-detection successful!{Style.RESET_ALL}")
                # Continue with wireless setup
            else:
                print(f"{Fore.RED}[✗] Auto-detection failed{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}[!] Switching to manual mode...{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.YELLOW}� MANUAL MODE:{Style.RESET_ALL}")
            print("  1. Connect phone via USB cable")
            print("  2. Enable USB Debugging on phone")
            print("  3. Accept 'Allow USB debugging' popup")
            print("  4. Select File Transfer mode")
            
            input(f"\n{Fore.YELLOW}Press Enter when ready...{Style.RESET_ALL}")
        
        # Check for devices with retry
        print(f"\n{Fore.CYAN}[*] Checking for USB devices...{Style.RESET_ALL}")
        
        for attempt in range(3):
            out, err, code = self.run_command(f'"{adb}" devices')
            
            # Parse output
            lines = [line for line in out.strip().split('\n')[1:] if line.strip()]
            
            if lines:
                # Check device state
                for line in lines:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        device_id = parts[0]
                        state = parts[1]
                        
                        if state == "unauthorized":
                            print(f"{Fore.RED}[✗] Device is UNAUTHORIZED!{Style.RESET_ALL}")
                            print(f"{Fore.YELLOW}[!] Check your phone - there should be a popup:{Style.RESET_ALL}")
                            print(f"{Fore.YELLOW}    'Allow USB debugging?'{Style.RESET_ALL}")
                            print(f"{Fore.YELLOW}[!] Tap 'Allow' or 'Always allow from this computer'{Style.RESET_ALL}")
                            input(f"\n{Fore.YELLOW}Press Enter after allowing...{Style.RESET_ALL}")
                            continue
                        elif state == "device":
                            print(f"{Fore.GREEN}[✓] USB device detected: {device_id}{Style.RESET_ALL}")
                            
                            # Enable TCP/IP mode
                            print(f"\n{Fore.CYAN}[*] Enabling wireless mode (port 5555)...{Style.RESET_ALL}")
                            out, err, code = self.run_command(f'"{adb}" -s {device_id} tcpip 5555')
                            
                            if code != 0:
                                print(f"{Fore.RED}[✗] Failed to enable wireless mode{Style.RESET_ALL}")
                                if err:
                                    print(f"{Fore.RED}Error: {err}{Style.RESET_ALL}")
                                return False
                            
                            if "restarting" in out.lower() or "5555" in out:
                                print(f"{Fore.GREEN}[✓] Wireless mode enabled!{Style.RESET_ALL}")
                                break
                            else:
                                print(f"{Fore.YELLOW}[!] Unexpected response: {out}{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.YELLOW}[!] Device state: {state}{Style.RESET_ALL}")
                break
            else:
                if attempt < 2:
                    print(f"{Fore.YELLOW}[!] No devices found, retrying ({attempt + 1}/3)...{Style.RESET_ALL}")
                    import time
                    time.sleep(1)
                else:
                    print(f"{Fore.RED}[✗] No USB devices found!{Style.RESET_ALL}")
                    print(f"\n{Fore.YELLOW}🔧 TROUBLESHOOTING:{Style.RESET_ALL}")
                    print(f"  1. {Fore.CYAN}Disconnect and reconnect USB cable{Style.RESET_ALL}")
                    print(f"  2. {Fore.CYAN}On phone: Settings → Developer Options → USB Debugging → ON{Style.RESET_ALL}")
                    print(f"  3. {Fore.CYAN}Try different USB cable (data cable, not charging-only){Style.RESET_ALL}")
                    print(f"  4. {Fore.CYAN}Install phone drivers (some phones need specific drivers){Style.RESET_ALL}")
                    print(f"  5. {Fore.CYAN}Run: adb kill-server then adb start-server{Style.RESET_ALL}")
                    
                    retry = input(f"\n{Fore.YELLOW}Try again? (y/n): {Style.RESET_ALL}").strip().lower()
                    if retry == 'y':
                        return self.usb_to_wireless()
                    return False
        
        import time
        time.sleep(2)
        
        # Get device IP
        print(f"{Fore.CYAN}[*] Getting device IP address...{Style.RESET_ALL}")
        out, err, code = self.run_command(f'"{adb}" shell ip addr show wlan0')
        
        if out:
            # Extract IP address
            match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', out)
            if match:
                device_ip = match.group(1)
                print(f"{Fore.GREEN}[✓] Device IP: {device_ip}{Style.RESET_ALL}")
                
                print(f"\n{Fore.YELLOW}[*] You can now DISCONNECT the USB cable!{Style.RESET_ALL}")
                input(f"{Fore.YELLOW}Press Enter after disconnecting USB...{Style.RESET_ALL}")
                
                # Connect wirelessly and auto-save
                if self.connect_by_ip(device_ip, 5555, auto_save=True):
                    return True
            else:
                print(f"{Fore.RED}[✗] Could not find IP address{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}[!] Manual IP method:{Style.RESET_ALL}")
                print("1. On phone: Settings → About Phone → Status → IP Address")
                print("2. Note the IP address")
                manual_ip = input(f"\n{Fore.YELLOW}Enter IP address manually: {Style.RESET_ALL}").strip()
                if manual_ip:
                    return self.connect_by_ip(manual_ip, 5555, auto_save=True)
        else:
            print(f"{Fore.RED}[✗] Could not get device IP{Style.RESET_ALL}")
        
        return False
    
    def connect_saved_device(self):
        """Connect to a saved device"""
        if not self.devices:
            print(f"{Fore.YELLOW}[!] No saved devices found{Style.RESET_ALL}")
            return False
        
        # Reload devices to get latest
        self.devices = self.load_devices()
        
        print(f"\n{Fore.CYAN}[*] Saved Devices:{Style.RESET_ALL}\n")
        device_list = list(self.devices.items())
        for i, (name, info) in enumerate(device_list, 1):
            print(f"{i}. {Fore.GREEN}{name}{Style.RESET_ALL} - {info['ip']}:{info['port']}")
        
        choice = input(f"\n{Fore.YELLOW}Select device (1-{len(device_list)}): {Style.RESET_ALL}").strip()
        
        try:
            idx = int(choice) - 1
            name, info = device_list[idx]
            return self.connect_by_ip(info['ip'], info['port'], auto_save=False)
        except:
            print(f"{Fore.RED}[✗] Invalid choice{Style.RESET_ALL}")
            return False
    
    def remote_connection_guide(self):
        """Guide for connecting from remote location (outside local network)"""
        print(f"\n{Fore.CYAN}╔═══════════════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║   REMOTE CONNECTION GUIDE (From Anywhere!)            ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚═══════════════════════════════════════════════════════╝{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}[METHOD 1] Port Forwarding on Router:{Style.RESET_ALL}")
        print("""
1. Setup phone on wireless first (use USB to wireless method)
2. Login to your router admin panel (usually 192.168.1.1 or 192.168.0.1)
3. Find "Port Forwarding" or "Virtual Server" section
4. Add new rule:
   - External Port: 5555 (or any port you choose)
   - Internal Port: 5555
   - Internal IP: [Your Phone's IP]
   - Protocol: TCP
5. Save and apply

6. Find your public IP: Visit https://whatismyip.com
7. Connect from anywhere using:
   adb connect YOUR_PUBLIC_IP:5555
        """)
        
        print(f"\n{Fore.YELLOW}[METHOD 2] VPN (Recommended for Security):{Style.RESET_ALL}")
        print("""
1. Setup a VPN server on your home network (e.g., WireGuard, OpenVPN)
2. Connect your phone to home VPN
3. Connect your remote PC to same VPN
4. Both devices now on same virtual network
5. Connect using phone's VPN IP address
        """)
        
        print(f"\n{Fore.YELLOW}[METHOD 3] Reverse Tunnel (Advanced):{Style.RESET_ALL}")
        print("""
1. Use a cloud server as bridge (e.g., AWS, DigitalOcean)
2. Setup SSH tunnel from phone → cloud server
3. Setup reverse tunnel from cloud server → your PC
4. Connect through the tunnel
        """)
        
        print(f"\n{Fore.RED}[!] SECURITY WARNING:{Style.RESET_ALL}")
        print("Exposing ADB to the internet is a security risk!")
        print("Recommendations:")
        print("  - Change default port (5555) to something random")
        print("  - Use VPN instead of port forwarding")
        print("  - Enable firewall rules")
        print("  - Use only when needed, then disconnect")
        
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def disconnect_all(self):
        """Disconnect all devices"""
        adb = self.get_adb_path()
        print(f"\n{Fore.CYAN}[*] Disconnecting all devices...{Style.RESET_ALL}")
        self.run_command(f'"{adb}" disconnect')
        print(f"{Fore.GREEN}[✓] All devices disconnected{Style.RESET_ALL}")
    
    def list_connected_devices(self):
        """List all connected devices"""
        adb = self.get_adb_path()
        print(f"\n{Fore.CYAN}[*] Connected Devices:{Style.RESET_ALL}\n")
        out, err, code = self.run_command(f'"{adb}" devices -l')
        print(out)
    
    def get_device_info(self, device_id=None):
        """Get detailed device information"""
        adb = self.get_adb_path()
        device_cmd = f"-s {device_id}" if device_id else ""
        
        print(f"\n{Fore.CYAN}╔═══════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║        DEVICE INFORMATION             ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚═══════════════════════════════════════╝{Style.RESET_ALL}\n")
        
        info_commands = {
            "Model": "shell getprop ro.product.model",
            "Brand": "shell getprop ro.product.brand",
            "Android Version": "shell getprop ro.build.version.release",
            "SDK Version": "shell getprop ro.build.version.sdk",
            "Serial": "shell getprop ro.serialno",
            "Battery Level": "shell dumpsys battery | grep level",
            "Screen Resolution": "shell wm size",
            "IP Address": "shell ip addr show wlan0 | grep inet",
        }
        
        for label, cmd in info_commands.items():
            out, _, code = self.run_command(f'"{adb}" {device_cmd} {cmd}')
            if code == 0 and out.strip():
                value = out.strip().split('\n')[0]
                print(f"{Fore.GREEN}[+] {label}:{Style.RESET_ALL} {value}")
    
    def take_screenshot(self, device_id=None):
        """Capture device screenshot"""
        adb = self.get_adb_path()
        device_cmd = f"-s {device_id}" if device_id else ""
        
        print(f"\n{Fore.CYAN}[*] Taking screenshot...{Style.RESET_ALL}")
        
        # Take screenshot on device
        self.run_command(f'"{adb}" {device_cmd} shell screencap -p /sdcard/screenshot.png')
        
        # Pull to PC
        import time
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        local_file = f"screenshot_{timestamp}.png"
        
        out, err, code = self.run_command(f'"{adb}" {device_cmd} pull /sdcard/screenshot.png {local_file}')
        
        if code == 0:
            print(f"{Fore.GREEN}[✓] Screenshot saved: {local_file}{Style.RESET_ALL}")
            # Clean up device
            self.run_command(f'"{adb}" {device_cmd} shell rm /sdcard/screenshot.png')
        else:
            print(f"{Fore.RED}[✗] Screenshot failed{Style.RESET_ALL}")
    
    def screen_record(self, device_id=None, duration=10):
        """Record device screen"""
        adb = self.get_adb_path()
        device_cmd = f"-s {device_id}" if device_id else ""
        
        print(f"\n{Fore.CYAN}[*] Recording screen for {duration} seconds...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[!] Recording started - do your actions on phone{Style.RESET_ALL}")
        
        # Record on device
        self.run_command(f'"{adb}" {device_cmd} shell screenrecord --time-limit {duration} /sdcard/recording.mp4')
        
        # Pull to PC
        import time
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        local_file = f"recording_{timestamp}.mp4"
        
        print(f"\n{Fore.CYAN}[*] Downloading recording...{Style.RESET_ALL}")
        out, err, code = self.run_command(f'"{adb}" {device_cmd} pull /sdcard/recording.mp4 {local_file}')
        
        if code == 0:
            print(f"{Fore.GREEN}[✓] Recording saved: {local_file}{Style.RESET_ALL}")
            # Clean up device
            self.run_command(f'"{adb}" {device_cmd} shell rm /sdcard/recording.mp4')
        else:
            print(f"{Fore.RED}[✗] Recording failed{Style.RESET_ALL}")
    
    def install_app(self, apk_path, device_id=None):
        """Install APK on device"""
        adb = self.get_adb_path()
        device_cmd = f"-s {device_id}" if device_id else ""
        
        if not os.path.exists(apk_path):
            print(f"{Fore.RED}[✗] APK file not found: {apk_path}{Style.RESET_ALL}")
            return False
        
        print(f"\n{Fore.CYAN}[*] Installing {os.path.basename(apk_path)}...{Style.RESET_ALL}")
        
        out, err, code = self.run_command(f'"{adb}" {device_cmd} install -r "{apk_path}"')
        
        if "Success" in out:
            print(f"{Fore.GREEN}[✓] App installed successfully!{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}[✗] Installation failed{Style.RESET_ALL}")
            if err:
                print(f"{Fore.RED}{err}{Style.RESET_ALL}")
            return False
    
    def file_manager(self, device_id=None):
        """File manager - browse and transfer files"""
        adb = self.get_adb_path()
        device_cmd = f"-s {device_id}" if device_id else ""
        
        while True:
            print(f"\n{Fore.CYAN}╔═══════════════════════════════════════╗{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║         FILE MANAGER                  ║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╚═══════════════════════════════════════╝{Style.RESET_ALL}")
            
            print(f"\n{Fore.YELLOW}1. Pull file from device (download){Style.RESET_ALL}")
            print(f"{Fore.YELLOW}2. Push file to device (upload){Style.RESET_ALL}")
            print(f"{Fore.YELLOW}3. List files on device{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}4. Delete file on device{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}0. Back{Style.RESET_ALL}")
            
            choice = input(f"\n{Fore.YELLOW}Choose: {Style.RESET_ALL}").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                # Quick paths
                print(f"\n{Fore.CYAN}Quick paths:{Style.RESET_ALL}")
                print("  Examples: /sdcard/Download/file.pdf")
                print("           /sdcard/DCIM/Camera/IMG_1234.jpg")
                print("           /sdcard/Documents/doc.txt")
                
                remote = input(f"\n{Fore.YELLOW}Device file path: {Style.RESET_ALL}").strip()
                local = input(f"{Fore.YELLOW}Save as (press Enter for same name): {Style.RESET_ALL}").strip()
                if remote:
                    local = local or os.path.basename(remote)
                    print(f"{Fore.CYAN}[*] Downloading {remote}...{Style.RESET_ALL}")
                    out, err, code = self.run_command(f'"{adb}" {device_cmd} pull "{remote}" "{local}"')
                    if code == 0:
                        print(f"{Fore.GREEN}[✓] Downloaded: {local}{Style.RESET_ALL}")
                        
                        # Show file size
                        if os.path.exists(local):
                            size = os.path.getsize(local)
                            if size < 1024:
                                size_str = f"{size} B"
                            elif size < 1024*1024:
                                size_str = f"{size/1024:.2f} KB"
                            else:
                                size_str = f"{size/(1024*1024):.2f} MB"
                            print(f"{Fore.GREEN}[✓] File size: {size_str}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}[✗] Failed: {err}{Style.RESET_ALL}")
            elif choice == "2":
                local = input(f"{Fore.YELLOW}Local file path: {Style.RESET_ALL}").strip()
                remote = input(f"{Fore.YELLOW}Device destination: {Style.RESET_ALL}").strip()
                if local and os.path.exists(local):
                    remote = remote or f"/sdcard/{os.path.basename(local)}"
                    print(f"{Fore.CYAN}[*] Uploading...{Style.RESET_ALL}")
                    out, err, code = self.run_command(f'"{adb}" {device_cmd} push "{local}" "{remote}"')
                    if code == 0:
                        print(f"{Fore.GREEN}[✓] Uploaded to: {remote}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}[✗] Failed: {err}{Style.RESET_ALL}")
            elif choice == "3":
                # Show storage options
                print(f"\n{Fore.CYAN}Common Storage Locations:{Style.RESET_ALL}")
                print(f"  1. {Fore.GREEN}/sdcard/{Style.RESET_ALL} - Internal storage (user accessible)")
                print(f"  2. {Fore.GREEN}/storage/emulated/0/{Style.RESET_ALL} - Internal storage (full path)")
                print(f"  3. {Fore.GREEN}/sdcard/DCIM/{Style.RESET_ALL} - Camera photos")
                print(f"  4. {Fore.GREEN}/sdcard/Download/{Style.RESET_ALL} - Downloads")
                print(f"  5. {Fore.GREEN}/sdcard/Documents/{Style.RESET_ALL} - Documents")
                print(f"  6. {Fore.GREEN}/data/data/{Style.RESET_ALL} - App data (requires root)")
                print(f"  7. {Fore.GREEN}Custom path{Style.RESET_ALL}")
                
                loc_choice = input(f"\n{Fore.YELLOW}Choose location (1-7, default 1): {Style.RESET_ALL}").strip()
                
                paths = {
                    "1": "/sdcard/",
                    "2": "/storage/emulated/0/",
                    "3": "/sdcard/DCIM/",
                    "4": "/sdcard/Download/",
                    "5": "/sdcard/Documents/",
                    "6": "/data/data/",
                }
                
                if loc_choice == "7":
                    path = input(f"{Fore.YELLOW}Enter custom path: {Style.RESET_ALL}").strip()
                else:
                    path = paths.get(loc_choice, "/sdcard/")
                
                print(f"\n{Fore.CYAN}[*] Files in {path}:{Style.RESET_ALL}\n")
                out, err, code = self.run_command(f'"{adb}" {device_cmd} shell ls -lah "{path}"')
                if code == 0:
                    print(out)
                    
                    # Show storage info
                    print(f"\n{Fore.CYAN}[*] Storage Usage:{Style.RESET_ALL}")
                    out2, _, _ = self.run_command(f'"{adb}" {device_cmd} shell df -h "{path}"')
                    if out2:
                        print(out2)
                else:
                    print(f"{Fore.RED}[✗] Failed: {err}{Style.RESET_ALL}")
                    if "Permission denied" in str(err):
                        print(f"{Fore.YELLOW}[!] Tip: This path requires root access{Style.RESET_ALL}")
            elif choice == "4":
                path = input(f"{Fore.YELLOW}File to delete: {Style.RESET_ALL}").strip()
                confirm = input(f"{Fore.RED}Delete {path}? (yes/no): {Style.RESET_ALL}").strip().lower()
                if confirm == "yes" and path:
                    out, err, code = self.run_command(f'"{adb}" {device_cmd} shell rm "{path}"')
                    if code == 0:
                        print(f"{Fore.GREEN}[✓] Deleted{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}[✗] Failed: {err}{Style.RESET_ALL}")
    
    def send_notification(self, title, message, device_id=None):
        """Send notification to device"""
        adb = self.get_adb_path()
        device_cmd = f"-s {device_id}" if device_id else ""
        
        print(f"\n{Fore.CYAN}[*] Sending notification...{Style.RESET_ALL}")
        
        # Use broadcast intent to show notification
        cmd = f'"{adb}" {device_cmd} shell am broadcast -a android.intent.action.VIEW -d "notification://{title}/{message}"'
        self.run_command(cmd)
        
        print(f"{Fore.GREEN}[✓] Notification sent!{Style.RESET_ALL}")
    
    def live_screen_monitor(self, device_id=None):
        """Live screen monitoring - continuous screenshot stream"""
        adb = self.get_adb_path()
        device_cmd = f"-s {device_id}" if device_id else ""
        
        print(f"\n{Fore.CYAN}╔═══════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║   LIVE SCREEN MONITORING              ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚═══════════════════════════════════════╝{Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}Options:{Style.RESET_ALL}")
        print(f"1. {Fore.GREEN}Continuous Screenshots (save every 2 seconds){Style.RESET_ALL}")
        print(f"2. {Fore.GREEN}Live Mirror with scrcpy (recommended){Style.RESET_ALL}")
        print(f"3. {Fore.GREEN}Single Screenshot{Style.RESET_ALL}")
        
        mode = input(f"\n{Fore.YELLOW}Choose mode (1-3): {Style.RESET_ALL}").strip()
        
        if mode == "1":
            print(f"\n{Fore.CYAN}[*] Starting continuous monitoring...{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[!] Press Ctrl+C to stop{Style.RESET_ALL}\n")
            
            import time
            count = 0
            try:
                while True:
                    count += 1
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = f"monitor_{timestamp}.png"
                    
                    # Take screenshot
                    self.run_command(f'"{adb}" {device_cmd} shell screencap -p /sdcard/temp_monitor.png')
                    out, err, code = self.run_command(f'"{adb}" {device_cmd} pull /sdcard/temp_monitor.png {filename}')
                    
                    if code == 0:
                        print(f"{Fore.GREEN}[{count}] Captured: {filename}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}[{count}] Failed to capture{Style.RESET_ALL}")
                    
                    time.sleep(2)
            except KeyboardInterrupt:
                print(f"\n{Fore.CYAN}[*] Monitoring stopped{Style.RESET_ALL}")
                print(f"{Fore.GREEN}[✓] Captured {count} screenshots{Style.RESET_ALL}")
                # Cleanup
                self.run_command(f'"{adb}" {device_cmd} shell rm /sdcard/temp_monitor.png')
        
        elif mode == "2":
            print(f"\n{Fore.CYAN}[*] Checking for scrcpy...{Style.RESET_ALL}")
            
            out, err, code = self.run_command("scrcpy --version")
            
            if code == 0:
                print(f"{Fore.GREEN}[✓] scrcpy found!{Style.RESET_ALL}")
                print(f"\n{Fore.CYAN}[*] Starting live mirror...{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}[!] Close window or press Ctrl+C to stop{Style.RESET_ALL}\n")
                
                # Start scrcpy with device ID if specified
                if device_id:
                    os.system(f'scrcpy -s {device_id} --window-title "Phone Monitor"')
                else:
                    os.system('scrcpy --window-title "Phone Monitor"')
            else:
                print(f"{Fore.RED}[✗] scrcpy not found!{Style.RESET_ALL}")
                print(f"\n{Fore.YELLOW}Install scrcpy for live mirroring:{Style.RESET_ALL}")
                print(f"  {Fore.CYAN}scoop install scrcpy{Style.RESET_ALL}")
                print(f"  or visit: https://github.com/Genymobile/scrcpy")
        
        elif mode == "3":
            self.take_screenshot(device_id)
        
        else:
            print(f"{Fore.RED}[✗] Invalid choice{Style.RESET_ALL}")
    
    def disable_power_button(self, device_id=None):
        """Disable power button to prevent power off"""
        adb = self.get_adb_path()
        device_cmd = f"-s {device_id}" if device_id else ""
        
        print(f"\n{Fore.CYAN}╔═══════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║   POWER BUTTON CONTROL                ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚═══════════════════════════════════════╝{Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}Options:{Style.RESET_ALL}")
        print(f"1. {Fore.RED}Disable Power Button (prevent power off){Style.RESET_ALL}")
        print(f"2. {Fore.GREEN}Enable Power Button (restore normal){Style.RESET_ALL}")
        print(f"3. {Fore.CYAN}Keep Screen Always On{Style.RESET_ALL}")
        print(f"4. {Fore.YELLOW}Lock Screen Now{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.YELLOW}Choose option (1-4): {Style.RESET_ALL}").strip()
        
        if choice == "1":
            print(f"\n{Fore.CYAN}[*] Disabling power button...{Style.RESET_ALL}")
            
            # Method 1: Disable power menu (requires root or system permissions)
            out1, _, _ = self.run_command(f'"{adb}" {device_cmd} shell settings put global power_button_suppression 1')
            
            # Method 2: Keep screen awake (doesn't disable button but prevents auto-sleep)
            out2, _, _ = self.run_command(f'"{adb}" {device_cmd} shell svc power stayon true')
            
            # Method 3: Disable shutdown option (may not work on all devices)
            out3, _, _ = self.run_command(f'"{adb}" {device_cmd} shell pm disable-user com.android.systemui/.power.PowerUI')
            
            print(f"{Fore.GREEN}[✓] Power button restrictions applied{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[!] Note: This may not work on all devices without root{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[!] Screen will stay awake and power menu may be disabled{Style.RESET_ALL}")
        
        elif choice == "2":
            print(f"\n{Fore.CYAN}[*] Re-enabling power button...{Style.RESET_ALL}")
            
            # Restore power button
            self.run_command(f'"{adb}" {device_cmd} shell settings put global power_button_suppression 0')
            self.run_command(f'"{adb}" {device_cmd} shell svc power stayon false')
            self.run_command(f'"{adb}" {device_cmd} shell pm enable com.android.systemui/.power.PowerUI')
            
            print(f"{Fore.GREEN}[✓] Power button restored to normal{Style.RESET_ALL}")
        
        elif choice == "3":
            print(f"\n{Fore.CYAN}[*] Keeping screen always on...{Style.RESET_ALL}")
            
            # Keep screen on while charging
            self.run_command(f'"{adb}" {device_cmd} shell svc power stayon true')
            
            # Disable auto-sleep
            self.run_command(f'"{adb}" {device_cmd} shell settings put system screen_off_timeout 2147483647')
            
            print(f"{Fore.GREEN}[✓] Screen will stay on{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[!] Battery will drain faster{Style.RESET_ALL}")
        
        elif choice == "4":
            print(f"\n{Fore.CYAN}[*] Locking screen...{Style.RESET_ALL}")
            self.run_command(f'"{adb}" {device_cmd} shell input keyevent 26')
            print(f"{Fore.GREEN}[✓] Screen locked{Style.RESET_ALL}")
        
        else:
            print(f"{Fore.RED}[✗] Invalid choice{Style.RESET_ALL}")
    
    def remote_control_menu(self, device_id=None):
        """Remote control menu after connection"""
        adb = self.get_adb_path()
        device_cmd = f"-s {device_id}" if device_id else ""
        
        while True:
            print(f"\n{Fore.CYAN}╔════════════════════════════════════════════╗{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║    📱 REMOTE DEVICE CONTROL 📱             ║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╚════════════════════════════════════════════╝{Style.RESET_ALL}")
            
            print(f"\n{Fore.YELLOW}[INFORMATION]{Style.RESET_ALL}")
            print(f"1. {Fore.GREEN}View Device Info{Style.RESET_ALL}")
            print(f"2. {Fore.GREEN}Take Screenshot{Style.RESET_ALL}")
            print(f"3. {Fore.GREEN}Screen Recording{Style.RESET_ALL}")
            
            print(f"\n{Fore.YELLOW}[FILE MANAGEMENT]{Style.RESET_ALL}")
            print(f"4. {Fore.GREEN}File Manager (Upload/Download){Style.RESET_ALL}")
            print(f"5. {Fore.GREEN}Install APK{Style.RESET_ALL}")
            
            print(f"\n{Fore.YELLOW}[ACTIONS]{Style.RESET_ALL}")
            print(f"6. {Fore.GREEN}Send Text/SMS{Style.RESET_ALL}")
            print(f"7. {Fore.GREEN}Make Call{Style.RESET_ALL}")
            print(f"8. {Fore.GREEN}Open URL{Style.RESET_ALL}")
            print(f"9. {Fore.GREEN}Vibrate Device{Style.RESET_ALL}")
            
            print(f"\n{Fore.YELLOW}[SCREEN CONTROL]{Style.RESET_ALL}")
            print(f"10. {Fore.CYAN}Live Screen Monitoring{Style.RESET_ALL}")
            print(f"11. {Fore.RED}Lock Screen{Style.RESET_ALL}")
            print(f"12. {Fore.RED}Disable Power Button (Prevent Power Off){Style.RESET_ALL}")
            
            print(f"\n{Fore.YELLOW}[SHELL ACCESS]{Style.RESET_ALL}")
            print(f"13. {Fore.CYAN}Open Interactive Shell{Style.RESET_ALL}")
            print(f"14. {Fore.CYAN}Execute Custom Command{Style.RESET_ALL}")
            
            print(f"\n{Fore.YELLOW}[APPS]{Style.RESET_ALL}")
            print(f"15. {Fore.GREEN}List Installed Apps{Style.RESET_ALL}")
            print(f"16. {Fore.GREEN}Launch App{Style.RESET_ALL}")
            print(f"17. {Fore.GREEN}Uninstall App{Style.RESET_ALL}")
            
            print(f"\n0. {Fore.RED}Back to Main Menu{Style.RESET_ALL}")
            
            choice = input(f"\n{Fore.YELLOW}Enter choice: {Style.RESET_ALL}").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self.get_device_info(device_id)
            elif choice == "2":
                self.take_screenshot(device_id)
            elif choice == "3":
                duration = input(f"{Fore.YELLOW}Duration in seconds (default 10): {Style.RESET_ALL}").strip()
                duration = int(duration) if duration else 10
                self.screen_record(device_id, duration)
            elif choice == "4":
                self.file_manager(device_id)
            elif choice == "5":
                apk = input(f"{Fore.YELLOW}APK file path: {Style.RESET_ALL}").strip()
                if apk:
                    self.install_app(apk, device_id)
            elif choice == "6":
                number = input(f"{Fore.YELLOW}Phone number: {Style.RESET_ALL}").strip()
                message = input(f"{Fore.YELLOW}Message: {Style.RESET_ALL}").strip()
                if number and message:
                    cmd = f'"{adb}" {device_cmd} shell am start -a android.intent.action.SENDTO -d sms:{number} --es sms_body "{message}"'
                    self.run_command(cmd)
                    print(f"{Fore.GREEN}[✓] SMS app opened with message{Style.RESET_ALL}")
            elif choice == "7":
                number = input(f"{Fore.YELLOW}Phone number: {Style.RESET_ALL}").strip()
                if number:
                    cmd = f'"{adb}" {device_cmd} shell am start -a android.intent.action.CALL -d tel:{number}'
                    self.run_command(cmd)
                    print(f"{Fore.GREEN}[✓] Calling {number}...{Style.RESET_ALL}")
            elif choice == "8":
                url = input(f"{Fore.YELLOW}URL: {Style.RESET_ALL}").strip()
                if url:
                    cmd = f'"{adb}" {device_cmd} shell am start -a android.intent.action.VIEW -d "{url}"'
                    self.run_command(cmd)
                    print(f"{Fore.GREEN}[✓] Opening {url}{Style.RESET_ALL}")
            elif choice == "9":
                duration = input(f"{Fore.YELLOW}Duration in ms (default 1000): {Style.RESET_ALL}").strip()
                duration = duration or "1000"
                cmd = f'"{adb}" {device_cmd} shell input keyevent 82'  # Menu key vibrates
                self.run_command(cmd)
                print(f"{Fore.GREEN}[✓] Vibration sent{Style.RESET_ALL}")
            elif choice == "10":
                self.live_screen_monitor(device_id)
            elif choice == "11":
                print(f"\n{Fore.CYAN}[*] Locking screen...{Style.RESET_ALL}")
                self.run_command(f'"{adb}" {device_cmd} shell input keyevent 26')  # Power button (lock)
                print(f"{Fore.GREEN}[✓] Screen locked{Style.RESET_ALL}")
            elif choice == "12":
                self.disable_power_button(device_id)
            elif choice == "13":
                print(f"\n{Fore.CYAN}[*] Opening interactive shell...{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}[!] Type 'exit' to return{Style.RESET_ALL}\n")
                os.system(f'"{adb}" {device_cmd} shell')
            elif choice == "14":
                cmd = input(f"{Fore.YELLOW}Command: {Style.RESET_ALL}").strip()
                if cmd:
                    print(f"\n{Fore.CYAN}[*] Executing...{Style.RESET_ALL}\n")
                    out, err, code = self.run_command(f'"{adb}" {device_cmd} shell {cmd}')
                    if out:
                        print(out)
                    if err:
                        print(f"{Fore.RED}{err}{Style.RESET_ALL}")
            elif choice == "15":
                print(f"\n{Fore.CYAN}[*] Installed apps:{Style.RESET_ALL}\n")
                out, _, _ = self.run_command(f'"{adb}" {device_cmd} shell pm list packages')
                if out:
                    packages = [line.replace('package:', '') for line in out.strip().split('\n')]
                    for i, pkg in enumerate(packages[:50], 1):  # Show first 50
                        print(f"{i}. {pkg}")
                    if len(packages) > 50:
                        print(f"\n{Fore.YELLOW}... and {len(packages) - 50} more apps{Style.RESET_ALL}")
            elif choice == "16":
                package = input(f"{Fore.YELLOW}Package name (e.g., com.android.chrome): {Style.RESET_ALL}").strip()
                if package:
                    cmd = f'"{adb}" {device_cmd} shell monkey -p {package} -c android.intent.category.LAUNCHER 1'
                    out, err, code = self.run_command(cmd)
                    if code == 0:
                        print(f"{Fore.GREEN}[✓] App launched{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}[✗] Failed to launch app{Style.RESET_ALL}")
            elif choice == "17":
                package = input(f"{Fore.YELLOW}Package name to uninstall: {Style.RESET_ALL}").strip()
                confirm = input(f"{Fore.RED}Uninstall {package}? (yes/no): {Style.RESET_ALL}").strip().lower()
                if confirm == "yes" and package:
                    out, err, code = self.run_command(f'"{adb}" {device_cmd} uninstall {package}')
                    if "Success" in out:
                        print(f"{Fore.GREEN}[✓] App uninstalled{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}[✗] Uninstall failed{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}[✗] Invalid choice{Style.RESET_ALL}")
            
            if choice != "0":
                input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def main_menu(self):
        """Main menu"""
        while True:
            print(f"\n{Fore.CYAN}╔════════════════════════════════════════════╗{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║    🌐 WIRELESS CONNECTION MANAGER 🌐       ║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╚════════════════════════════════════════════╝{Style.RESET_ALL}")
            
            print(f"\n{Fore.YELLOW}[QUICK CONNECT]{Style.RESET_ALL}")
            print(f"1. {Fore.GREEN}Connect to Saved Device (Same WiFi){Style.RESET_ALL}")
            print(f"2. {Fore.GREEN}Connect by IP Address{Style.RESET_ALL}")
            print(f"10. {Fore.CYAN}🌐 Connect from Anywhere (Remote Access){Style.RESET_ALL}")
            
            print(f"\n{Fore.YELLOW}[SETUP]{Style.RESET_ALL}")
            print(f"3. {Fore.GREEN}USB to Wireless (First Time Setup){Style.RESET_ALL}")
            print(f"4. {Fore.GREEN}Scan Network for Devices{Style.RESET_ALL}")
            print(f"11. {Fore.CYAN}Setup Remote Access (Port Forwarding){Style.RESET_ALL}")
            
            print(f"\n{Fore.YELLOW}[ADVANCED]{Style.RESET_ALL}")
            print(f"5. {Fore.CYAN}Remote Connection Guide (Connect from Anywhere){Style.RESET_ALL}")
            print(f"9. {Fore.CYAN}Manage Saved Devices{Style.RESET_ALL}")
            
            print(f"\n{Fore.YELLOW}[REMOTE CONTROL]{Style.RESET_ALL}")
            print(f"6. {Fore.GREEN}📱 Access Connected Device (Remote Control){Style.RESET_ALL}")
            
            print(f"\n{Fore.YELLOW}[STATUS]{Style.RESET_ALL}")
            print(f"7. {Fore.GREEN}List Connected Devices{Style.RESET_ALL}")
            print(f"8. {Fore.RED}Disconnect All{Style.RESET_ALL}")
            
            print(f"\n0. {Fore.RED}Exit{Style.RESET_ALL}")
            
            choice = input(f"\n{Fore.YELLOW}Enter choice: {Style.RESET_ALL}").strip()
            
            if choice == "0":
                print(f"\n{Fore.GREEN}Goodbye!{Style.RESET_ALL}")
                break
            elif choice == "1":
                self.connect_saved_device()
            elif choice == "2":
                ip = input(f"\n{Fore.YELLOW}Enter IP address: {Style.RESET_ALL}").strip()
                port = input(f"{Fore.YELLOW}Enter port (default 5555): {Style.RESET_ALL}").strip()
                port = int(port) if port else 5555
                if ip:
                    self.connect_by_ip(ip, port, auto_save=True)
            elif choice == "3":
                self.usb_to_wireless()
            elif choice == "4":
                devices = self.scan_network()
                if devices:
                    print(f"\n{Fore.YELLOW}Connect to a device?{Style.RESET_ALL}")
                    for i, dev in enumerate(devices, 1):
                        print(f"{i}. {dev}")
                    sel = input(f"\n{Fore.YELLOW}Select device (1-{len(devices)}) or press Enter to skip: {Style.RESET_ALL}").strip()
                    if sel:
                        try:
                            idx = int(sel) - 1
                            ip, port = devices[idx].split(':')
                            self.connect_by_ip(ip, int(port), auto_save=True)
                        except:
                            pass
            elif choice == "5":
                self.remote_connection_guide()
            elif choice == "6":
                # Remote control menu
                adb = self.get_adb_path()
                out, _, _ = self.run_command(f'"{adb}" devices')
                
                # Debug: Show raw output
                print(f"\n{Fore.CYAN}[DEBUG] ADB devices output:{Style.RESET_ALL}")
                print(out)
                
                if "device" in out and out.count('\n') >= 2:
                    # Extract device IDs - look for lines with "device" (not "devices" header)
                    lines = []
                    for line in out.strip().split('\n')[1:]:  # Skip first line (header)
                        if '\tdevice' in line or ':5000\tdevice' in line or ':5555\tdevice' in line:
                            lines.append(line)
                    
                    if len(lines) == 1:
                        device_id = lines[0].split('\t')[0]
                        print(f"\n{Fore.GREEN}[✓] Using device: {device_id}{Style.RESET_ALL}")
                        self.remote_control_menu(device_id)
                    elif len(lines) > 1:
                        print(f"\n{Fore.YELLOW}[*] Multiple devices connected:{Style.RESET_ALL}\n")
                        for i, line in enumerate(lines, 1):
                            device_id = line.split('\t')[0]
                            print(f"{i}. {device_id}")
                        sel = input(f"\n{Fore.YELLOW}Select device (1-{len(lines)}): {Style.RESET_ALL}").strip()
                        try:
                            idx = int(sel) - 1
                            device_id = lines[idx].split('\t')[0]
                            self.remote_control_menu(device_id)
                        except:
                            print(f"{Fore.RED}[✗] Invalid selection{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}[✗] No devices found in ADB output!{Style.RESET_ALL}")
                        print(f"{Fore.YELLOW}[!] Tip: Check if connection is still active{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}[✗] No devices connected! Connect a device first.{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}[!] Use Option 1, 2, 3, or 4 to connect first{Style.RESET_ALL}")
            elif choice == "7":
                self.list_connected_devices()
            elif choice == "8":
                self.disconnect_all()
            elif choice == "9":
                self.manage_devices()
            elif choice == "10":
                self.remote_access_connect()
            elif choice == "11":
                self.setup_remote_access()
            else:
                print(f"{Fore.RED}[✗] Invalid choice{Style.RESET_ALL}")
            
            if choice != "0":
                input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    
    def setup_remote_access(self):
        """Remote access setup with LocalXpose"""
        print(f"\n{Fore.CYAN}╔═══════════════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║   REMOTE ACCESS SETUP (FROM ANYWHERE)                 ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚═══════════════════════════════════════════════════════╝{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}Choose your method:{Style.RESET_ALL}\n")
        print(f"1. {Fore.GREEN}LocalXpose Tunnel{Style.RESET_ALL} (✨ RECOMMENDED - Free TCP!)")
        print(f"2. {Fore.YELLOW}Router Port Forwarding{Style.RESET_ALL} (Manual, exposes IP)")
        
        choice = input(f"\n{Fore.YELLOW}Choose (1-2): {Style.RESET_ALL}").strip()
        
        if choice == "1":
            # Run LocalXpose setup
            print(f"\n{Fore.CYAN}[*] Launching LocalXpose setup...{Style.RESET_ALL}")
            import os
            os.system("python setup_localxpose.py")
        elif choice == "2":
            # Open port forwarding guide
            if os.path.exists("../REMOTE_ACCESS_GUIDE.txt"):
                os.system("notepad ../REMOTE_ACCESS_GUIDE.txt")
            else:
                self.setup_port_forwarding()
    
    def setup_port_forwarding(self):
        """Setup router port forwarding"""
        print(f"\n{Fore.CYAN}╔═══════════════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║   ROUTER PORT FORWARDING SETUP                        ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚═══════════════════════════════════════════════════════╝{Style.RESET_ALL}")
        
        # Get phone's local IP
        print(f"\n{Fore.YELLOW}Step 1: Get your phone's local IP{Style.RESET_ALL}")
        phone_ip = input(f"{Fore.CYAN}Enter phone's local IP (e.g., 192.168.1.42): {Style.RESET_ALL}").strip()
        
        # Get router IP
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        router_ip = '.'.join(local_ip.split('.')[:-1]) + '.1'
        
        print(f"\n{Fore.YELLOW}Step 2: Login to your router{Style.RESET_ALL}")
        print(f"  • Open browser: {Fore.CYAN}http://{router_ip}{Style.RESET_ALL}")
        print(f"  • Or try: {Fore.CYAN}http://192.168.1.1{Style.RESET_ALL} or {Fore.CYAN}http://192.168.0.1{Style.RESET_ALL}")
        print(f"  • Login with router credentials (often on router sticker)")
        
        print(f"\n{Fore.YELLOW}Step 3: Setup Port Forwarding{Style.RESET_ALL}")
        print(f"  • Find: 'Port Forwarding' or 'Virtual Server' section")
        print(f"  • Add new rule:")
        print(f"      {Fore.GREEN}External Port:{Style.RESET_ALL} 5555")
        print(f"      {Fore.GREEN}Internal IP:{Style.RESET_ALL} {phone_ip}")
        print(f"      {Fore.GREEN}Internal Port:{Style.RESET_ALL} 5555")
        print(f"      {Fore.GREEN}Protocol:{Style.RESET_ALL} TCP")
        print(f"      {Fore.GREEN}Description:{Style.RESET_ALL} ADB Remote")
        print(f"  • Save and apply")
        
        print(f"\n{Fore.YELLOW}Step 4: Get your public IP{Style.RESET_ALL}")
        print(f"  • Visit: {Fore.CYAN}https://whatismyip.com{Style.RESET_ALL}")
        print(f"  • Or run: {Fore.CYAN}curl ifconfig.me{Style.RESET_ALL}")
        
        public_ip = input(f"\n{Fore.CYAN}Enter your public IP: {Style.RESET_ALL}").strip()
        
        if public_ip:
            print(f"\n{Fore.GREEN}✅ Setup Complete!{Style.RESET_ALL}")
            print(f"\n{Fore.YELLOW}From anywhere, connect with:{Style.RESET_ALL}")
            print(f"  {Fore.CYAN}adb connect {public_ip}:5555{Style.RESET_ALL}")
            
            save = input(f"\n{Fore.YELLOW}Save as remote device? (y/n): {Style.RESET_ALL}").strip().lower()
            if save == 'y':
                name = input(f"Device name (e.g., 'MyPhone_Remote'): ").strip()
                if name:
                    self.save_device(name, public_ip, 5555)
        
        print(f"\n{Fore.RED}⚠️  SECURITY WARNING:{Style.RESET_ALL}")
        print(f"  • Your phone is now accessible from the internet!")
        print(f"  • Only use on trusted networks")
        print(f"  • Consider changing port 5555 to something random")
        print(f"  • Disable when not needed")
    
    def setup_ngrok_tunnel(self):
        """Setup Cloudflare Tunnel (100% free alternative to ngrok)"""
        print(f"\n{Fore.CYAN}╔═══════════════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║   CLOUDFLARE TUNNEL SETUP (100% FREE!)                ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚═══════════════════════════════════════════════════════╝{Style.RESET_ALL}")
        
        print(f"\n{Fore.GREEN}Why Cloudflare Tunnel over ngrok:{Style.RESET_ALL}")
        print(f"  ✅ 100% FREE - No credit card required!")
        print(f"  ✅ TCP tunnels included (ngrok charges for TCP)")
        print(f"  ✅ Unlimited bandwidth")
        print(f"  ✅ Cloudflare's global network (faster)")
        print(f"  ✅ Hides your real IP address")
        print(f"  ✅ Works behind any firewall")
        print(f"  ✅ More stable connections")
        
        print(f"\n{Fore.YELLOW}Step 1: Install cloudflared{Style.RESET_ALL}")
        print(f"  Option A: {Fore.CYAN}scoop install cloudflared{Style.RESET_ALL}")
        print(f"  Option B: Download from {Fore.CYAN}https://github.com/cloudflare/cloudflared/releases{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}Step 2: Login to Cloudflare (free account){Style.RESET_ALL}")
        print(f"  Run: {Fore.CYAN}cloudflared tunnel login{Style.RESET_ALL}")
        print(f"  (Opens browser - sign up for free if needed)")
        
        print(f"\n{Fore.YELLOW}Step 3: Get phone's local IP{Style.RESET_ALL}")
        phone_ip = input(f"{Fore.CYAN}Enter phone's local IP (or press Enter for 192.168.100.148): {Style.RESET_ALL}").strip()
        
        if not phone_ip:
            phone_ip = "192.168.100.148"
        
        print(f"\n{Fore.YELLOW}Step 4: Start tunnel{Style.RESET_ALL}")
        print(f"  First connect phone locally:")
        print(f"    {Fore.CYAN}adb connect {phone_ip}:5555{Style.RESET_ALL}")
        print(f"\n  Then start Cloudflare tunnel:")
        print(f"    {Fore.GREEN}cloudflared tunnel --url tcp://localhost:5555{Style.RESET_ALL}")
        print(f"\n  You'll see output like:")
        print(f"    {Fore.CYAN}https://xxxxx.trycloudflare.com{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}Step 5: Connect from anywhere{Style.RESET_ALL}")
        print(f"  Use the Cloudflare URL shown above")
        print(f"  {Fore.CYAN}adb connect THE_CLOUDFLARE_URL{Style.RESET_ALL}")
        
        print(f"\n{Fore.GREEN}✨ AUTOMATED SETUP:{Style.RESET_ALL}")
        print(f"  Run: {Fore.CYAN}python setup_cloudflare.py{Style.RESET_ALL}")
        print(f"  (Does everything automatically!)")
        
        print(f"\n{Fore.GREEN}✅ 100% Free - No credit card ever!{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✅ Your IP is hidden behind Cloudflare!{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✅ Access from anywhere without exposing your network!{Style.RESET_ALL}")
    
    def setup_vpn_guide(self):
        """VPN setup guide"""
        print(f"\n{Fore.CYAN}╔═══════════════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║   VPN SETUP (MOST SECURE)                             ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚═══════════════════════════════════════════════════════╝{Style.RESET_ALL}")
        
        print(f"\n{Fore.GREEN}Best for:{Style.RESET_ALL}")
        print(f"  ✅ Maximum security")
        print(f"  ✅ Multiple devices")
        print(f"  ✅ Always-on access")
        
        print(f"\n{Fore.YELLOW}Option 1: WireGuard (Recommended){Style.RESET_ALL}")
        print(f"  1. Install WireGuard on your router or PC")
        print(f"  2. Install WireGuard app on phone")
        print(f"  3. Generate keys and config")
        print(f"  4. Phone and PC on same virtual network")
        print(f"  5. Connect normally with local IP")
        
        print(f"\n{Fore.YELLOW}Option 2: OpenVPN{Style.RESET_ALL}")
        print(f"  1. Setup OpenVPN server on router")
        print(f"  2. Install OpenVPN app on phone")
        print(f"  3. Import config file")
        print(f"  4. Connect to VPN from anywhere")
        
        print(f"\n{Fore.YELLOW}Option 3: Tailscale (Easiest){Style.RESET_ALL}")
        print(f"  1. Install Tailscale on PC and phone")
        print(f"  2. Sign in to same account")
        print(f"  3. Both devices get virtual IPs")
        print(f"  4. Connect using Tailscale IP")
        print(f"\n  Website: {Fore.CYAN}https://tailscale.com{Style.RESET_ALL}")
    
    def setup_ssh_tunnel(self):
        """SSH tunnel setup"""
        print(f"\n{Fore.CYAN}╔═══════════════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║   SSH TUNNEL (ADVANCED)                               ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚═══════════════════════════════════════════════════════╝{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}Requirements:{Style.RESET_ALL}")
        print(f"  • Cloud server (AWS, DigitalOcean, etc.)")
        print(f"  • SSH access")
        print(f"  • Reverse tunnel setup")
        
        print(f"\n{Fore.YELLOW}Setup:{Style.RESET_ALL}")
        print(f"  1. On home PC, run:")
        print(f"     {Fore.CYAN}ssh -R 5555:PHONE_IP:5555 user@yourserver.com{Style.RESET_ALL}")
        print(f"\n  2. From anywhere, connect to:")
        print(f"     {Fore.CYAN}ssh user@yourserver.com{Style.RESET_ALL}")
        print(f"     {Fore.CYAN}adb connect localhost:5555{Style.RESET_ALL}")
    
    def remote_access_connect(self):
        """Connect using remote access methods"""
        print(f"\n{Fore.CYAN}╔═══════════════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║   REMOTE ACCESS CONNECTION                            ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚═══════════════════════════════════════════════════════╝{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}How are you connecting?{Style.RESET_ALL}\n")
        print(f"1. {Fore.GREEN}LocalXpose URL (e.g., xxxx.loclx.io:xxxxx){Style.RESET_ALL}")
        print(f"2. {Fore.GREEN}Public IP (Port Forwarding){Style.RESET_ALL}")
        print(f"3. {Fore.GREEN}ngrok/Cloudflare URL{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.YELLOW}Choose (1-3): {Style.RESET_ALL}").strip()
        
        if choice == "1":
            print(f"\n{Fore.YELLOW}LocalXpose URL format: xxxx.loclx.io:xxxxx{Style.RESET_ALL}")
            url = input(f"{Fore.CYAN}Enter LocalXpose URL: {Style.RESET_ALL}").strip()
            if url:
                # Remove protocol if present
                if '://' in url:
                    url = url.split('://')[-1]
                
                if ':' in url:
                    parts = url.split(':')
                    ip = parts[0]
                    port = int(parts[1])
                    self.connect_by_ip(ip, port, auto_save=True)
                else:
                    print(f"{Fore.RED}[✗] Invalid URL format{Style.RESET_ALL}")
        
        elif choice == "2":
            ip = input(f"{Fore.CYAN}Enter public IP: {Style.RESET_ALL}").strip()
            port = input(f"{Fore.CYAN}Enter port (default 5555): {Style.RESET_ALL}").strip()
            port = int(port) if port else 5555
            if ip:
                self.connect_by_ip(ip, port, auto_save=True)
        
        elif choice == "3":
            print(f"\n{Fore.YELLOW}URL format: 0.tcp.ngrok.io:12345 or xxxxx.trycloudflare.com{Style.RESET_ALL}")
            url = input(f"{Fore.CYAN}Enter tunnel URL: {Style.RESET_ALL}").strip()
            if url:
                # Remove protocol if present
                if '://' in url:
                    url = url.split('://')[-1]
                
                if ':' in url:
                    parts = url.split(':')
                    ip = parts[0]
                    port = int(parts[1])
                    self.connect_by_ip(ip, port, auto_save=True)
                else:
                    print(f"{Fore.RED}[✗] Invalid URL format (needs host:port){Style.RESET_ALL}")
    
    def manage_devices(self):
        """Manage saved devices"""
        # Reload to get latest
        self.devices = self.load_devices()
        
        if not self.devices:
            print(f"{Fore.YELLOW}[!] No saved devices{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}[*] Saved Devices:{Style.RESET_ALL}\n")
        device_list = list(self.devices.items())
        for i, (name, info) in enumerate(device_list, 1):
            print(f"{i}. {Fore.GREEN}{name}{Style.RESET_ALL} - {info['ip']}:{info['port']}")
        
        print(f"\n{Fore.YELLOW}Actions:{Style.RESET_ALL}")
        print("1. Delete a device")
        print("2. Edit a device")
        print("3. Back")
        
        action = input(f"\n{Fore.YELLOW}Choose action: {Style.RESET_ALL}").strip()
        
        if action == "1":
            idx = input(f"{Fore.YELLOW}Device number to delete: {Style.RESET_ALL}").strip()
            try:
                name = device_list[int(idx) - 1][0]
                del self.devices[name]
                with open(self.config_file, 'w') as f:
                    json.dump(self.devices, f, indent=2)
                print(f"{Fore.GREEN}[✓] Device deleted{Style.RESET_ALL}")
            except:
                print(f"{Fore.RED}[✗] Invalid selection{Style.RESET_ALL}")
        elif action == "2":
            idx = input(f"{Fore.YELLOW}Device number to edit: {Style.RESET_ALL}").strip()
            try:
                name = device_list[int(idx) - 1][0]
                info = self.devices[name]
                print(f"\n{Fore.CYAN}Editing: {name}{Style.RESET_ALL}")
                print(f"Current IP: {info['ip']}")
                print(f"Current Port: {info['port']}")
                
                new_ip = input(f"\n{Fore.YELLOW}New IP (press Enter to keep): {Style.RESET_ALL}").strip()
                new_port = input(f"{Fore.YELLOW}New Port (press Enter to keep): {Style.RESET_ALL}").strip()
                
                if new_ip:
                    info['ip'] = new_ip
                if new_port:
                    info['port'] = int(new_port)
                
                with open(self.config_file, 'w') as f:
                    json.dump(self.devices, f, indent=2)
                print(f"{Fore.GREEN}[✓] Device updated{Style.RESET_ALL}")
            except:
                print(f"{Fore.RED}[✗] Invalid selection{Style.RESET_ALL}")

if __name__ == "__main__":
    connector = WirelessConnector()
    connector.main_menu()
