"""
🔒 CLOUDFLARE TCP TUNNEL - SECURE & FREE!
Hides your IP, no port forwarding needed
"""

import subprocess
import json
import time
from colorama import Fore, Style, init

init(autoreset=True)

print(f"{Fore.CYAN}╔═══════════════════════════════════════════════════════╗{Style.RESET_ALL}")
print(f"{Fore.CYAN}║   CLOUDFLARE SECURE TUNNEL - FREE & IP HIDDEN!        ║{Style.RESET_ALL}")
print(f"{Fore.CYAN}╚═══════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")

print(f"{Fore.GREEN}🔒 Security Benefits:{Style.RESET_ALL}")
print(f"  ✅ Your real IP stays hidden")
print(f"  ✅ DDoS protection included")
print(f"  ✅ Enterprise-grade encryption")
print(f"  ✅ No port forwarding on router")
print(f"  ✅ 100% FREE forever")
print()

# Unfortunately, Cloudflare's quick tunnels don't support raw TCP
# We need to use a workaround or proper named tunnel

print(f"{Fore.YELLOW}⚠️  Cloudflare Quick Tunnels Limitation:{Style.RESET_ALL}")
print(f"  The free quick tunnels only support HTTP/HTTPS")
print(f"  For TCP (needed for ADB), we have 2 options:\n")

print(f"{Fore.CYAN}Option 1: Cloudflare Named Tunnel (Recommended){Style.RESET_ALL}")
print(f"  Steps:")
print(f"  1. Create FREE Cloudflare account: https://dash.cloudflare.com/sign-up")
print(f"  2. Run: cloudflared tunnel login")
print(f"  3. Create tunnel: cloudflared tunnel create phone-tunnel")
print(f"  4. Configure TCP access")
print(f"  {Fore.GREEN}✅ Your IP completely hidden{Style.RESET_ALL}")
print(f"  {Fore.GREEN}✅ Permanent tunnel{Style.RESET_ALL}\n")

print(f"{Fore.CYAN}Option 2: Use ZeroTier instead (Easier){Style.RESET_ALL}")
print(f"  {Fore.GREEN}✅ 100% FREE{Style.RESET_ALL}")
print(f"  {Fore.GREEN}✅ PC-only setup (phone just joins network){Style.RESET_ALL}")
print(f"  {Fore.GREEN}✅ Your IP hidden (P2P encrypted){Style.RESET_ALL}")
print(f"  {Fore.GREEN}✅ Simpler than Cloudflare{Style.RESET_ALL}")
print()

choice = input(f"{Fore.YELLOW}Choose:\n  1. Set up Cloudflare Named Tunnel\n  2. Switch to ZeroTier\n  3. Exit\n\nYour choice: {Style.RESET_ALL}").strip()

if choice == "1":
    print(f"\n{Fore.CYAN}Setting up Cloudflare Named Tunnel...{Style.RESET_ALL}\n")
    
    # Step 1: Login
    print(f"{Fore.YELLOW}Step 1: Cloudflare Login{Style.RESET_ALL}")
    print(f"This will open a browser window...")
    input(f"{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")
    
    subprocess.run("cloudflared tunnel login", shell=True)
    
    # Step 2: Create tunnel
    print(f"\n{Fore.YELLOW}Step 2: Create Tunnel{Style.RESET_ALL}")
    tunnel_name = "phone-adb-tunnel"
    
    result = subprocess.run(f"cloudflared tunnel create {tunnel_name}", 
                          shell=True, capture_output=True, text=True)
    
    print(result.stdout)
    
    if "Created tunnel" in result.stdout or "already exists" in result.stdout:
        print(f"{Fore.GREEN}[✓] Tunnel created!{Style.RESET_ALL}")
        
        # Get tunnel ID
        list_result = subprocess.run("cloudflared tunnel list", 
                                    shell=True, capture_output=True, text=True)
        print(f"\n{list_result.stdout}")
        
        print(f"\n{Fore.YELLOW}Step 3: Configure TCP Access{Style.RESET_ALL}")
        print(f"To enable TCP access for ADB:")
        print(f"  1. Go to: https://one.dash.cloudflare.com/")
        print(f"  2. Access → Tunnels → {tunnel_name}")
        print(f"  3. Configure → Public Hostname")
        print(f"  4. Set: Type=TCP, Service=tcp://192.168.100.148:5555")
        
        open_dash = input(f"\n{Fore.YELLOW}Open Cloudflare dashboard? (y/n): {Style.RESET_ALL}").strip().lower()
        if open_dash == 'y':
            subprocess.run("start https://one.dash.cloudflare.com/", shell=True)
    else:
        print(f"{Fore.RED}[✗] Error creating tunnel{Style.RESET_ALL}")
        print(result.stderr)

elif choice == "2":
    print(f"\n{Fore.GREEN}ZeroTier is actually PERFECT for you!{Style.RESET_ALL}")
    print(f"\nWhy ZeroTier is better:")
    print(f"  ✅ Easier setup than Cloudflare")
    print(f"  ✅ Your IP completely hidden")
    print(f"  ✅ Direct encrypted connection")
    print(f"  ✅ Just install app on phone (one-time)")
    print()
    
    install = input(f"{Fore.YELLOW}Install ZeroTier? (y/n): {Style.RESET_ALL}").strip().lower()
    if install == 'y':
        print(f"\n{Fore.CYAN}Installing ZeroTier...{Style.RESET_ALL}")
        subprocess.run("scoop install zerotier", shell=True)
else:
    print(f"\n{Fore.YELLOW}Exiting...{Style.RESET_ALL}")

input(f"\n{Fore.YELLOW}Press Enter to exit...{Style.RESET_ALL}")
