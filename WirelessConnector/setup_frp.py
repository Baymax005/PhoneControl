"""
🚀 FRP TUNNEL SETUP - FREE & WORKS IN PAKISTAN!
Using free public FRP servers
"""

import subprocess
import os
import time
from colorama import Fore, Style, init
import json

init(autoreset=True)

print(f"{Fore.CYAN}╔═══════════════════════════════════════════════════════╗{Style.RESET_ALL}")
print(f"{Fore.CYAN}║   FRP TUNNEL - FREE & UNRESTRICTED!                   ║{Style.RESET_ALL}")
print(f"{Fore.CYAN}╚═══════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")

print(f"{Fore.GREEN}✅ Benefits:{Style.RESET_ALL}")
print(f"  ✅ 100% FREE")
print(f"  ✅ Works in Pakistan (not blocked)")
print(f"  ✅ IP hidden (server's IP shown)")
print(f"  ✅ TCP support for ADB")
print(f"  ✅ PC-only setup")
print()

# Get phone IP
config_file = "wireless_devices.json"
phone_ip = None

if os.path.exists(config_file):
    with open(config_file, 'r') as f:
        devices = json.load(f)
    
    if devices:
        print(f"{Fore.GREEN}Found saved devices:{Style.RESET_ALL}")
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
    phone_ip = input(f"\n{Fore.YELLOW}Enter phone's IP address (default: 192.168.100.148): {Style.RESET_ALL}").strip()
    if not phone_ip:
        phone_ip = "192.168.100.148"

print(f"\n{Fore.CYAN}[*] Using phone IP: {phone_ip}{Style.RESET_ALL}")

# Free FRP servers to try
print(f"\n{Fore.YELLOW}Available FREE FRP Servers:{Style.RESET_ALL}\n")
servers = [
    {
        "name": "OpenFRP (China - Fast for Asia)",
        "server": "frp.freefrp.net",
        "port": 7000,
        "token": "",  # Public, no token needed
        "type": "tcp"
    },
    {
        "name": "SAKURA FRP (Japan - Good for Pakistan)",
        "server": "cn-hk-bgp-3.sakurafrp.com",
        "port": 7000,
        "token": "sakura_frp_free",
        "type": "tcp"
    },
    {
        "name": "Custom Server",
        "server": "custom",
        "port": 7000,
        "token": "",
        "type": "tcp"
    }
]

for i, server in enumerate(servers, 1):
    print(f"{i}. {Fore.GREEN}{server['name']}{Style.RESET_ALL}")
    print(f"   Server: {server['server']}:{server['port']}")
    print()

choice = input(f"{Fore.YELLOW}Choose server (1-{len(servers)}, default: 1): {Style.RESET_ALL}").strip()

if not choice:
    choice = "1"

try:
    server_idx = int(choice) - 1
    selected_server = servers[server_idx]
except:
    selected_server = servers[0]

if selected_server['server'] == 'custom':
    selected_server['server'] = input(f"{Fore.YELLOW}Enter FRP server address: {Style.RESET_ALL}").strip()
    selected_server['port'] = int(input(f"{Fore.YELLOW}Enter FRP server port (default: 7000): {Style.RESET_ALL}").strip() or "7000")
    selected_server['token'] = input(f"{Fore.YELLOW}Enter auth token (leave empty if none): {Style.RESET_ALL}").strip()

print(f"\n{Fore.GREEN}╔════════════════════════════════════════════════════╗{Style.RESET_ALL}")
print(f"{Fore.GREEN}║   CREATING FRP CONFIGURATION                       ║{Style.RESET_ALL}")
print(f"{Fore.GREEN}╚════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")

# Create FRP client config
frpc_config_path = os.path.join(os.path.expanduser("~"), "scoop", "persist", "frp", "frpc.toml")

# Generate random port for remote
import random
remote_port = random.randint(10000, 65000)

config_content = f"""# FRP Client Configuration for Android ADB
serverAddr = "{selected_server['server']}"
serverPort = {selected_server['port']}
"""

if selected_server['token']:
    config_content += f'auth.token = "{selected_server["token"]}"\n'

config_content += f"""
[[proxies]]
name = "android-adb"
type = "tcp"
localIP = "{phone_ip}"
localPort = 5555
remotePort = {remote_port}
"""

print(f"{Fore.CYAN}[*] Creating config at: {frpc_config_path}{Style.RESET_ALL}")

try:
    with open(frpc_config_path, 'w') as f:
        f.write(config_content)
    print(f"{Fore.GREEN}[✓] Config created!{Style.RESET_ALL}")
except Exception as e:
    print(f"{Fore.RED}[✗] Error creating config: {e}{Style.RESET_ALL}")
    print(f"\n{Fore.YELLOW}Creating in current directory instead...{Style.RESET_ALL}")
    frpc_config_path = "frpc.toml"
    with open(frpc_config_path, 'w') as f:
        f.write(config_content)
    print(f"{Fore.GREEN}[✓] Config created: {frpc_config_path}{Style.RESET_ALL}")

print(f"\n{Fore.YELLOW}Configuration:{Style.RESET_ALL}")
print(config_content)

print(f"\n{Fore.GREEN}╔════════════════════════════════════════════════════╗{Style.RESET_ALL}")
print(f"{Fore.GREEN}║   STARTING FRP TUNNEL                              ║{Style.RESET_ALL}")
print(f"{Fore.GREEN}╚════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")

print(f"{Fore.CYAN}[*] Starting FRP client...{Style.RESET_ALL}")
print(f"{Fore.YELLOW}[!] Keep the FRP window open!{Style.RESET_ALL}\n")

# Create batch file to run frpc
batch_content = f"""@echo off
title FRP Tunnel - DO NOT CLOSE!
color 0A
echo.
echo ========================================
echo    FRP TUNNEL ACTIVE
echo ========================================
echo.
echo Server: {selected_server['server']}:{selected_server['port']}
echo Tunneling: {phone_ip}:5555
echo Remote Port: {remote_port}
echo.
echo Connect with: adb connect {selected_server['server']}:{remote_port}
echo.
frpc -c "{os.path.abspath(frpc_config_path)}"
pause
"""

with open('start_frp.bat', 'w') as f:
    f.write(batch_content)

print(f"{Fore.YELLOW}Starting FRP in new window...{Style.RESET_ALL}\n")
os.system('start start_frp.bat')

time.sleep(2)

print(f"\n{Fore.GREEN}╔════════════════════════════════════════════════════╗{Style.RESET_ALL}")
print(f"{Fore.GREEN}║   ✅ FRP TUNNEL STARTED!                          ║{Style.RESET_ALL}")
print(f"{Fore.GREEN}╚════════════════════════════════════════════════════╝{Style.RESET_ALL}")

print(f"\n{Fore.CYAN}📡 Connection Details:{Style.RESET_ALL}")
print(f"  {Fore.GREEN}Server: {selected_server['server']}{Style.RESET_ALL}")
print(f"  {Fore.GREEN}Port: {remote_port}{Style.RESET_ALL}")
print(f"  {Fore.GREEN}Forwarding: {phone_ip}:5555{Style.RESET_ALL}")

print(f"\n{Fore.YELLOW}🌍 Connect from ANYWHERE:{Style.RESET_ALL}")
print(f"  {Fore.GREEN}adb connect {selected_server['server']}:{remote_port}{Style.RESET_ALL}")

print(f"\n{Fore.YELLOW}⚠️  IMPORTANT:{Style.RESET_ALL}")
print(f"  • Keep the FRP window open")
print(f"  • If connection fails, try different server")
print(f"  • Free servers may have limited bandwidth")
print(f"  • Your IP is hidden behind FRP server")

# Try to connect
connect = input(f"\n{Fore.YELLOW}Try connecting now? (y/n): {Style.RESET_ALL}").strip().lower()

if connect == 'y':
    print(f"\n{Fore.CYAN}[*] Connecting to {selected_server['server']}:{remote_port}...{Style.RESET_ALL}")
    
    # Wait a bit for tunnel to establish
    print(f"{Fore.YELLOW}[*] Waiting for tunnel to establish (5 seconds)...{Style.RESET_ALL}")
    time.sleep(5)
    
    result = subprocess.run(
        ['adb', 'connect', f"{selected_server['server']}:{remote_port}"],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    
    if 'connected' in result.stdout.lower():
        print(f"{Fore.GREEN}[✓] Connected successfully!{Style.RESET_ALL}")
        
        # Save device
        save = input(f"\n{Fore.YELLOW}Save as remote device? (y/n): {Style.RESET_ALL}").strip().lower()
        if save == 'y':
            devices = {}
            
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    devices = json.load(f)
            
            device_name = input(f"Device name (default: Phone_FRP): ").strip() or "Phone_FRP"
            devices[device_name] = {
                "ip": selected_server['server'],
                "port": remote_port
            }
            
            with open(config_file, 'w') as f:
                json.dump(devices, f, indent=2)
            
            print(f"{Fore.GREEN}[✓] Saved as '{device_name}'!{Style.RESET_ALL}")
        
        # Open remote control
        control = input(f"\n{Fore.YELLOW}Open remote control menu? (y/n): {Style.RESET_ALL}").strip().lower()
        if control == 'y':
            os.system("python wireless_connector.py")
    else:
        print(f"{Fore.YELLOW}[!] Connection result: {result.stdout}{Style.RESET_ALL}")
        if result.stderr:
            print(f"{Fore.YELLOW}Error: {result.stderr}{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}💡 Troubleshooting:{Style.RESET_ALL}")
        print(f"  1. Check the FRP window for errors")
        print(f"  2. Try a different server")
        print(f"  3. Make sure phone is on same WiFi")
        print(f"  4. Check firewall settings")

input(f"\n{Fore.YELLOW}Press Enter to exit (FRP will keep running)...{Style.RESET_ALL}")
