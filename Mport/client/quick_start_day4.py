"""
No-prompt quick start for Mport Day 4 Client
Uses defaults for easy testing
"""

import asyncio
import logging
import json
import sys
from datetime import datetime
from pathlib import Path
from colorama import Fore, Style, init

# Import the client class
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from tunnel_client_day4 import MportClient, logger

async def main():
    """Main entry point with defaults."""
    print(f"{Fore.CYAN}Mport Client - Day 4 (No-Prompt Mode){Style.RESET_ALL}\n")
    
    # Use defaults
    server_host = "localhost"
    server_port = 8081
    local_host = "192.168.100.148"
    local_port = 5555
    
    print(f"{Fore.GREEN}Using defaults:{Style.RESET_ALL}")
    print(f"  Server: {server_host}:{server_port}")
    print(f"  Local:  {local_host}:{local_port}\n")
    
    # Create and run client
    client = MportClient(server_host, server_port, local_host, local_port)
    await client.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.GREEN}Mport Client stopped gracefully.{Style.RESET_ALL}")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n{Fore.RED}Client crashed. Check logs for details.{Style.RESET_ALL}")
        sys.exit(1)
