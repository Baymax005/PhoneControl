"""
Mport Tunnel Client - "Your Port to the World"
Phase 1, Week 1: Basic TCP Tunnel Client

This runs on your PC and:
1. Connects to Mport server (VPS)
2. Forwards traffic to your local service (e.g., phone at 192.168.100.148:5555)
"""

import asyncio
import logging
from colorama import Fore, Style, init

init(autoreset=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MportClient:
    """
    Mport tunnel client.
    
    Connects to Mport server and forwards traffic to local service.
    """
    
    def __init__(self, server_host, server_port, local_host, local_port):
        self.server_host = server_host
        self.server_port = server_port
        self.local_host = local_host
        self.local_port = local_port
        self.client_id = None
        
        logger.info(f"{Fore.CYAN}Initializing Mport Client{Style.RESET_ALL}")
        logger.info(f"Server: {server_host}:{server_port}")
        logger.info(f"Local service: {local_host}:{local_port}")
    
    async def connect_to_server(self):
        """Establish connection to Mport server."""
        print(f"\n{Fore.CYAN}Connecting to Mport Server...{Style.RESET_ALL}")
        
        try:
            reader, writer = await asyncio.open_connection(
                self.server_host,
                self.server_port
            )
            
            logger.info(f"{Fore.GREEN}Connected to {self.server_host}:{self.server_port}{Style.RESET_ALL}")
            
            # Send handshake
            handshake = f"MPORT_CLIENT:HELLO".encode('utf-8')
            writer.write(handshake)
            await writer.drain()
            
            logger.info(f"{Fore.CYAN}Sent handshake{Style.RESET_ALL}")
            
            # Receive acknowledgment
            data = await reader.read(1024)
            response = data.decode('utf-8').strip()
            
            if response.startswith('MPORT_ACK:'):
                self.client_id = response.split(':')[1]
                print(f"{Fore.GREEN}✅ Registered as: {self.client_id}{Style.RESET_ALL}")
                logger.info(f"Assigned client ID: {self.client_id}")
            else:
                logger.error(f"Unexpected response: {response}")
                return None, None
            
            return reader, writer
            
        except ConnectionRefusedError:
            print(f"{Fore.RED}❌ Connection refused. Is the server running?{Style.RESET_ALL}")
            logger.error(f"Could not connect to {self.server_host}:{self.server_port}")
            return None, None
        
        except Exception as e:
            print(f"{Fore.RED}❌ Connection error: {e}{Style.RESET_ALL}")
            logger.error(f"Error connecting: {e}")
            return None, None
    
    async def forward_to_local(self, data):
        """Forward data to local service (e.g., phone ADB)."""
        try:
            # Connect to local service
            local_reader, local_writer = await asyncio.open_connection(
                self.local_host,
                self.local_port
            )
            
            # Send data
            local_writer.write(data)
            await local_writer.drain()
            
            # Read response
            response = await local_reader.read(4096)
            
            # Close local connection
            local_writer.close()
            await local_writer.wait_closed()
            
            return response
            
        except Exception as e:
            logger.error(f"Error forwarding to local service: {e}")
            return None
    
    async def run(self):
        """Run the client."""
        print(f"\n{Fore.CYAN}╔═══════════════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║   🚀 MPORT CLIENT - YOUR PORT TO THE WORLD          ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚═══════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")
        
        print(f"{Fore.GREEN}Starting Mport Client...{Style.RESET_ALL}")
        print(f"  • Server:  {self.server_host}:{self.server_port}")
        print(f"  • Local:   {self.local_host}:{self.local_port}")
        print(f"\n{Fore.YELLOW}Phase 1 - Week 1: Basic TCP Tunnel{Style.RESET_ALL}")
        print(f"Press Ctrl+C to stop\n")
        
        reader, writer = await self.connect_to_server()
        
        if not reader or not writer:
            print(f"\n{Fore.RED}Failed to connect to server. Exiting.{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.GREEN}✅ Tunnel established!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Waiting for traffic...{Style.RESET_ALL}\n")
        
        try:
            # Keep connection alive and handle messages
            while True:
                data = await reader.read(4096)
                
                if not data:
                    print(f"\n{Fore.YELLOW}Server disconnected.{Style.RESET_ALL}")
                    break
                
                logger.info(f"Received {len(data)} bytes from server")
                
                # Forward to local service
                response = await self.forward_to_local(data)
                
                if response:
                    # Send response back to server
                    writer.write(response)
                    await writer.drain()
                    logger.info(f"Sent {len(response)} bytes back to server")
        
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Stopping client...{Style.RESET_ALL}")
        
        finally:
            writer.close()
            await writer.wait_closed()
            print(f"{Fore.GREEN}Disconnected from server.{Style.RESET_ALL}")


async def main():
    """Main entry point."""
    print(f"{Fore.YELLOW}Mport Client Configuration:{Style.RESET_ALL}\n")
    
    # For testing locally, both server and client on same machine
    # Later: server will be on VPS (DigitalOcean)
    server_host = input(f"Server host (default: localhost): ").strip() or "localhost"
    server_port = input(f"Server port (default: 8081): ").strip()
    server_port = int(server_port) if server_port else 8081
    
    local_host = input(f"Local service host (default: 192.168.100.148): ").strip() or "192.168.100.148"
    local_port = input(f"Local service port (default: 5555): ").strip()
    local_port = int(local_port) if local_port else 5555
    
    client = MportClient(
        server_host=server_host,
        server_port=server_port,
        local_host=local_host,
        local_port=local_port
    )
    
    await client.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.GREEN}Mport Client stopped.{Style.RESET_ALL}")
