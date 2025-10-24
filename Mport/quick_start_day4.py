"""
Quick Start script for Mport Day 4 Testing
Launches server and client in separate windows for easy testing
"""

import subprocess
import sys
from pathlib import Path
from colorama import Fore, Style, init

init(autoreset=True)

def main():
    print(f"\n{Fore.CYAN}╔═══════════════════════════════════════════════════════╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║   🚀 MPORT DAY 4 - QUICK START                      ║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚═══════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")
    
    print(f"{Fore.YELLOW}This will launch:{Style.RESET_ALL}")
    print(f"  1. Server (Day 4 version) - Port 8080/8081/8082")
    print(f"  2. Client (Day 4 version) - Connects to localhost:8081")
    print(f"\n{Fore.GREEN}Starting in separate windows...{Style.RESET_ALL}\n")
    
    # Get script directory
    script_dir = Path(__file__).parent
    server_script = script_dir / "server" / "tunnel_server_day4.py"
    client_script = script_dir / "client" / "tunnel_client_day4.py"
    
    # Check if scripts exist
    if not server_script.exists():
        print(f"{Fore.RED}Error: Server script not found at {server_script}{Style.RESET_ALL}")
        return
    
    if not client_script.exists():
        print(f"{Fore.RED}Error: Client script not found at {client_script}{Style.RESET_ALL}")
        return
    
    try:
        # Launch server in new PowerShell window
        print(f"{Fore.CYAN}[1/2] Launching server...{Style.RESET_ALL}")
        server_cmd = f"python {server_script}"
        subprocess.Popen(
            ["powershell", "-Command", f"Start-Process powershell -ArgumentList '-NoExit', '-Command', '{server_cmd}'"],
            shell=True
        )
        
        # Launch client in new PowerShell window (with defaults)
        print(f"{Fore.CYAN}[2/2] Launching client...{Style.RESET_ALL}")
        
        # Use defaults: localhost:8081, 192.168.100.148:5555
        client_cmd = (
            f"echo 'Using defaults: localhost:8081 -> 192.168.100.148:5555'; "
            f"echo ''; "
            f"echo 'localhost' | python {client_script}"
        )
        
        subprocess.Popen(
            ["powershell", "-Command", f"Start-Process powershell -ArgumentList '-NoExit', '-Command', '{client_cmd}'"],
            shell=True
        )
        
        print(f"\n{Fore.GREEN}✓ Launched!{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Testing:{Style.RESET_ALL}")
        print(f"  Terminal 3: {Fore.CYAN}adb connect localhost:8080{Style.RESET_ALL}")
        print(f"  Terminal 3: {Fore.CYAN}adb -s localhost:8080 shell getprop ro.product.model{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Check the logs folder for detailed logs!{Style.RESET_ALL}\n")
        
    except Exception as e:
        print(f"{Fore.RED}Error launching: {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()
