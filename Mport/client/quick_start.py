"""
Quick start client with defaults - no prompts needed.
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the client class
from tunnel_client_v2 import MportClient
from colorama import Fore, Style

async def main():
    """Main entry point with defaults."""
    print(f"{Fore.CYAN}Mport Client - Using Defaults{Style.RESET_ALL}\n")
    
    client = MportClient(
        server_host="localhost",
        server_port=8081,
        local_host="192.168.100.148",
        local_port=5555
    )
    
    await client.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.GREEN}Mport Client stopped.{Style.RESET_ALL}")
