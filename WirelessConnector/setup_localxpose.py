"""
🌐 LOCALXPOSE TUNNEL SETUP - FREE TCP TUNNELS!
Better than ngrok - supports TCP on free tier!
"""

import subprocess
import time
import os
import json
from colorama import Fore, Style, init
import re

init(autoreset=True)

def run_cmd(cmd):
    """Run command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1

print(f"{Fore.CYAN}╔═══════════════════════════════════════════════════════╗{Style.RESET_ALL}")
print(f"{Fore.CYAN}║   LOCALXPOSE TUNNEL - 100% FREE TCP SUPPORT!          ║{Style.RESET_ALL}")
print(f"{Fore.CYAN}╚═══════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")

print(f"{Fore.GREEN}Benefits:{Style.RESET_ALL}")
print(f"  ✅ 100% FREE - TCP tunnels included!")
print(f"  ✅ No credit card needed")
print(f"  ✅ Easy to use")
print(f"  ✅ Better than ngrok for free tier")
print()

# Step 1: Check if loclx is installed
print(f"{Fore.CYAN}[*] Checking for LocalXpose (loclx)...{Style.RESET_ALL}")
out, err, code = run_cmd("loclx --version")

if code != 0:
    print(f"{Fore.YELLOW}[!] LocalXpose not found, installing...{Style.RESET_ALL}\n")
    
    print(f"{Fore.YELLOW}Installation Options:{Style.RESET_ALL}")
    print(f"1. Download from: {Fore.CYAN}https://localxpose.io/download{Style.RESET_ALL}")
    print(f"2. Run installer and add to PATH")
    print()
    
    install = input(f"{Fore.YELLOW}Open download page? (y/n): {Style.RESET_ALL}").strip().lower()
    
    if install == 'y':
        os.system('start https://localxpose.io/download')
        print(f"\n{Fore.YELLOW}After installing:{Style.RESET_ALL}")
        print(f"1. Download and extract loclx")
        print(f"2. Move loclx.exe to C:\\loclx\\")
        print(f"3. Add C:\\loclx\\ to PATH")
        print(f"4. Run this script again")
        input(f"\n{Fore.YELLOW}Press Enter to exit...{Style.RESET_ALL}")
        exit(0)
    else:
        print(f"{Fore.YELLOW}Please install LocalXpose manually and run this script again{Style.RESET_ALL}")
        exit(1)
else:
    print(f"{Fore.GREEN}[✓] LocalXpose installed{Style.RESET_ALL}\n")

# Step 2: Check auth token
print(f"{Fore.CYAN}[*] Checking authentication...{Style.RESET_ALL}")

# Try to read config
config_path = os.path.expanduser("~/.localxpose/config.yaml")
token_exists = False

if os.path.exists(config_path):
    try:
        with open(config_path, 'r') as f:
            content = f.read()
            if 'token:' in content or 'access_token:' in content:
                token_exists = True
                print(f"{Fore.GREEN}[✓] Already authenticated{Style.RESET_ALL}")
    except:
        pass

if not token_exists:
    print(f"{Fore.YELLOW}[!] Not authenticated{Style.RESET_ALL}")
    print(f"\n{Fore.YELLOW}You mentioned you have an account!{Style.RESET_ALL}")
    print(f"Get your access token:")
    print(f"  1. Visit: {Fore.CYAN}https://localxpose.io/dashboard{Style.RESET_ALL}")
    print(f"  2. Login with your account")
    print(f"  3. Copy your access token")
    
    token = input(f"\n{Fore.YELLOW}Paste your access token here: {Style.RESET_ALL}").strip()
    
    if token:
        print(f"\n{Fore.CYAN}[*] Configuring token...{Style.RESET_ALL}")
        out, err, code = run_cmd(f'loclx account login -t {token}')
        
        if code == 0 or "success" in out.lower() or "logged" in out.lower():
            print(f"{Fore.GREEN}[✓] Authentication successful!{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}[!] Authentication result: {out}{Style.RESET_ALL}")
            if err:
                print(f"{Fore.YELLOW}Error: {err}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}[✗] No token provided{Style.RESET_ALL}")
        exit(1)

# Step 3: Get phone IP
print(f"\n{Fore.CYAN}[*] Getting phone information...{Style.RESET_ALL}")

config_file = "wireless_devices.json"
phone_ip = None

if os.path.exists(config_file):
    with open(config_file, 'r') as f:
        devices = json.load(f)
    
    if devices:
        print(f"\n{Fore.GREEN}[✓] Found saved devices:{Style.RESET_ALL}")
        device_list = list(devices.items())
        for i, (name, info) in enumerate(device_list, 1):
            print(f"  {i}. {name} - {info['ip']}:{info['port']}")
        
        choice = input(f"\n{Fore.YELLOW}Select device (1-{len(device_list)}): {Style.RESET_ALL}").strip()
        
        if choice:
            try:
                idx = int(choice) - 1
                name, info = device_list[idx]
                phone_ip = info['ip']
                print(f"{Fore.GREEN}[✓] Using {name}: {phone_ip}{Style.RESET_ALL}")
            except:
                pass

if not phone_ip:
    phone_ip = input(f"\n{Fore.YELLOW}Enter phone's IP address: {Style.RESET_ALL}").strip()
    if not phone_ip:
        phone_ip = "192.168.100.148"  # Default
        print(f"{Fore.GREEN}[✓] Using default: {phone_ip}{Style.RESET_ALL}")

# Step 4: Start LocalXpose tunnel
print(f"\n{Fore.GREEN}╔════════════════════════════════════════════════════╗{Style.RESET_ALL}")
print(f"{Fore.GREEN}║   STARTING LOCALXPOSE TUNNEL                       ║{Style.RESET_ALL}")
print(f"{Fore.GREEN}╚════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")

print(f"{Fore.CYAN}[*] Starting TCP tunnel for {phone_ip}:5555...{Style.RESET_ALL}")
print(f"{Fore.YELLOW}[!] Keep this window open!{Style.RESET_ALL}\n")

# Create batch file to run loclx in background
batch_content = f'@echo off\ntitle LocalXpose Tunnel - DO NOT CLOSE!\ncolor 0A\necho.\necho ========================================\necho    LOCALXPOSE TUNNEL ACTIVE\necho ========================================\necho.\necho Tunneling: {phone_ip}:5555\necho.\nloclx tunnel tcp --to {phone_ip}:5555\npause'

with open('start_localxpose.bat', 'w') as f:
    f.write(batch_content)

# Start loclx in new window
print(f"{Fore.YELLOW}Starting LocalXpose in a new window...{Style.RESET_ALL}\n")
os.system('start start_localxpose.bat')

print(f"{Fore.CYAN}[*] Waiting for tunnel to start...{Style.RESET_ALL}")
time.sleep(3)

# Try to get tunnel URL from loclx
print(f"\n{Fore.YELLOW}Looking for tunnel URL...{Style.RESET_ALL}")

# loclx doesn't have API like ngrok, so we'll ask user to copy it
print(f"\n{Fore.GREEN}╔════════════════════════════════════════════════════╗{Style.RESET_ALL}")
print(f"{Fore.GREEN}║   ✅ LOCALXPOSE TUNNEL STARTED!                   ║{Style.RESET_ALL}")
print(f"{Fore.GREEN}╚════════════════════════════════════════════════════╝{Style.RESET_ALL}")

print(f"\n{Fore.CYAN}Instructions:{Style.RESET_ALL}")
print(f"1. Look at the LocalXpose window that opened")
print(f"2. Find the line that shows:")
print(f"   {Fore.GREEN}TCP URL: xxxx.loclx.io:xxxxx{Style.RESET_ALL}")
print(f"3. Copy that URL")
print()

url = input(f"{Fore.YELLOW}Paste the LocalXpose URL here: {Style.RESET_ALL}").strip()

if url:
    # Parse URL
    if '://' in url:
        url = url.split('://')[-1]
    
    print(f"\n{Fore.GREEN}╔════════════════════════════════════════════════════╗{Style.RESET_ALL}")
    print(f"{Fore.GREEN}║   READY TO CONNECT!                                ║{Style.RESET_ALL}")
    print(f"{Fore.GREEN}╚════════════════════════════════════════════════════╝{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}📡 Public URL: {Fore.GREEN}{url}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🔗 Forwarding: {Fore.GREEN}{url} → {phone_ip}:5555{Style.RESET_ALL}")
    
    print(f"\n{Fore.YELLOW}Connect from ANYWHERE:{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}adb connect {url}{Style.RESET_ALL}")
    
    # Try to connect
    connect = input(f"\n{Fore.YELLOW}Connect now? (y/n): {Style.RESET_ALL}").strip().lower()
    
    if connect == 'y':
        print(f"\n{Fore.CYAN}[*] Connecting to {url}...{Style.RESET_ALL}")
        result = subprocess.run(['adb', 'connect', url], capture_output=True, text=True)
        
        print(result.stdout)
        
        if 'connected' in result.stdout.lower():
            print(f"{Fore.GREEN}[✓] Connected successfully!{Style.RESET_ALL}")
            
            # Save device
            save = input(f"\n{Fore.YELLOW}Save as remote device? (y/n): {Style.RESET_ALL}").strip().lower()
            if save == 'y':
                config_file = 'wireless_devices.json'
                devices = {}
                
                if os.path.exists(config_file):
                    with open(config_file, 'r') as f:
                        devices = json.load(f)
                
                # Parse host and port
                if ':' in url:
                    host, port = url.rsplit(':', 1)
                else:
                    host = url
                    port = "5555"
                
                device_name = input(f"Device name (default: Phone_LocalXpose): ").strip() or "Phone_LocalXpose"
                devices[device_name] = {
                    "ip": host,
                    "port": int(port)
                }
                
                with open(config_file, 'w') as f:
                    json.dump(devices, f, indent=2)
                
                print(f"{Fore.GREEN}[✓] Saved as '{device_name}'!{Style.RESET_ALL}")
            
            # Open remote control
            control = input(f"\n{Fore.YELLOW}Open remote control menu? (y/n): {Style.RESET_ALL}").strip().lower()
            if control == 'y':
                os.chdir('..')  # Go back to parent directory
                os.system("python WirelessConnector\\wireless_connector.py")
        else:
            print(f"{Fore.YELLOW}[!] Connection result: {result.stdout}{Style.RESET_ALL}")
            if result.stderr:
                print(f"{Fore.YELLOW}Error: {result.stderr}{Style.RESET_ALL}")

print(f"\n{Fore.YELLOW}📝 NOTES:{Style.RESET_ALL}")
print(f"  • Keep the LocalXpose window open")
print(f"  • 100% FREE - No credit card!")
print(f"  • TCP support on free tier (better than ngrok)")
print(f"  • Works from anywhere in the world!")
print(f"  • URL stays same unless you restart")

print(f"\n{Fore.CYAN}Dashboard: {Fore.GREEN}https://localxpose.io/dashboard{Style.RESET_ALL}")

input(f"\n{Fore.YELLOW}Press Enter to exit (LocalXpose will keep running)...{Style.RESET_ALL}")
