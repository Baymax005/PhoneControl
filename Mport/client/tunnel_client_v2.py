"""
Mport Tunnel Client - "Your Port to the World"
Phase 1, Week 1 Day 2: SIMPLIFIED - Connect when needed

This runs on your PC and creates a NEW connection for each tunnel request.
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
    """Simple Mport client - creates one connection per tunnel."""
    
    def __init__(self, server_host, server_port, local_host, local_port):
        self.server_host = server_host
        self.server_port = server_port
        self.local_host = local_host
        self.local_port = local_port
        self.running = True
        
        logger.info(f"{Fore.CYAN}Initializing Mport Client{Style.RESET_ALL}")
        logger.info(f"Server: {server_host}:{server_port}")
        logger.info(f"Local service: {local_host}:{local_port}")
    
    async def forward_data(self, reader_src, writer_dst, direction):
        """Forward data bidirectionally."""
        try:
            while True:
                data = await reader_src.read(8192)
                if not data:
                    break
                
                logger.info(f"{Fore.CYAN}[{direction}] {len(data)} bytes{Style.RESET_ALL}")
                writer_dst.write(data)
                await writer_dst.drain()
        
        except Exception as e:
            logger.error(f"{Fore.RED}[{direction}] Error: {e}{Style.RESET_ALL}")
        
        finally:
            try:
                writer_dst.close()
                await writer_dst.wait_closed()
            except:
                pass
    
    async def handle_one_tunnel(self):
        """Create one tunnel: Server <-> Local Service."""
        try:
            # 1. Connect to server
            logger.info(f"{Fore.CYAN}Connecting to server...{Style.RESET_ALL}")
            server_reader, server_writer = await asyncio.open_connection(
                self.server_host,
                self.server_port
            )
            
            logger.info(f"{Fore.GREEN}✅ Connected to server{Style.RESET_ALL}")
            
            # 2. Send handshake
            handshake = b"MPORT_CLIENT:HELLO"
            server_writer.write(handshake)
            await server_writer.drain()
            
            # 3. Get acknowledgment
            data = await server_reader.read(1024)
            response = data.decode('utf-8').strip()
            
            if response.startswith('MPORT_ACK:'):
                client_id = response.split(':')[1]
                logger.info(f"{Fore.GREEN}Registered as: {client_id}{Style.RESET_ALL}")
            
            # 4. Connect to local service
            logger.info(f"{Fore.CYAN}Connecting to local {self.local_host}:{self.local_port}{Style.RESET_ALL}")
            local_reader, local_writer = await asyncio.open_connection(
                self.local_host,
                self.local_port
            )
            
            logger.info(f"{Fore.GREEN}✅ Connected to local service{Style.RESET_ALL}")
            logger.info(f"{Fore.GREEN}🚀 TUNNEL ACTIVE!{Style.RESET_ALL}")
            
            # 5. Start bidirectional forwarding
            await asyncio.gather(
                self.forward_data(server_reader, local_writer, "SERVER->LOCAL"),
                self.forward_data(local_reader, server_writer, "LOCAL->SERVER"),
                return_exceptions=True
            )
            
            logger.info(f"{Fore.YELLOW}Tunnel closed{Style.RESET_ALL}")
            
        except ConnectionRefusedError as e:
            if "8081" in str(e) or self.server_port == 8081:
                logger.error(f"{Fore.RED}Cannot connect to server {self.server_host}:{self.server_port}{Style.RESET_ALL}")
                logger.error(f"{Fore.YELLOW}Is the Mport server running?{Style.RESET_ALL}")
            else:
                logger.error(f"{Fore.RED}Cannot connect to local {self.local_host}:{self.local_port}{Style.RESET_ALL}")
                logger.error(f"{Fore.YELLOW}Is your phone connected? Try: adb connect {self.local_host}:{self.local_port}{Style.RESET_ALL}")
        
        except Exception as e:
            logger.error(f"{Fore.RED}Tunnel error: {e}{Style.RESET_ALL}")
    
    async def run(self):
        """Keep creating tunnels as needed."""
        print(f"\n{Fore.CYAN}╔═══════════════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║   🚀 MPORT CLIENT - YOUR PORT TO THE WORLD          ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚═══════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")
        
        print(f"{Fore.GREEN}Starting Mport Client...{Style.RESET_ALL}")
        print(f"  • Server:  {self.server_host}:{self.server_port}")
        print(f"  • Local:   {self.local_host}:{self.local_port}")
        print(f"\n{Fore.YELLOW}Phase 1 - Week 1 Day 2: SIMPLIFIED TUNNEL{Style.RESET_ALL}")
        print(f"{Style.DIM}Creating new connections as needed{Style.RESET_ALL}")
        print(f"Press Ctrl+C to stop\n")
        
        try:
            while self.running:
                await self.handle_one_tunnel()
                
                if self.running:
                    logger.info(f"{Fore.CYAN}Waiting 2 seconds before reconnecting...{Style.RESET_ALL}")
                    await asyncio.sleep(2)
        
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Stopping client...{Style.RESET_ALL}")
            self.running = False


async def main():
    """Main entry point."""
    print(f"{Fore.YELLOW}Mport Client Configuration:{Style.RESET_ALL}\n")
    
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
