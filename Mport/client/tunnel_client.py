"""
Mport Tunnel Client - "Your Port to the World"
Phase 1, Week 1 Day 3: Persistent client with multiple tunnels

Architecture:
- One persistent control connection to server
- Spawns separate tunnel connections on demand
- Stays alive 24/7
"""

import asyncio
import logging
import json
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
    Production-ready Mport client.
    - Persistent control connection
    - Multiple simultaneous tunnels
    """
    
    def __init__(self, server_host, server_port, local_host, local_port):
        self.server_host = server_host
        self.server_port = server_port
        self.local_host = local_host
        self.local_port = local_port
        self.client_id = None
        self.running = True
        
        logger.info(f"{Fore.CYAN}Initializing Mport Client (Day 3){Style.RESET_ALL}")
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
    
    async def handle_tunnel_request(self):
        """
        Create a new tunnel connection when server needs one.
        This is spawned as a separate task for each tunnel.
        """
        try:
            # 1. Connect to tunnel port
            logger.info(f"{Fore.CYAN}[TUNNEL] Connecting to server tunnel port...{Style.RESET_ALL}")
            tunnel_reader, tunnel_writer = await asyncio.open_connection(
                self.server_host,
                8082  # Tunnel port
            )
            
            logger.info(f"{Fore.GREEN}[TUNNEL] Connected to server{Style.RESET_ALL}")
            
            # 2. Register tunnel
            registration = json.dumps({
                'type': 'TUNNEL_REGISTER',
                'client_id': self.client_id
            }) + '\n'
            tunnel_writer.write(registration.encode('utf-8'))
            await tunnel_writer.drain()
            
            logger.info(f"{Fore.CYAN}[TUNNEL] Registered with server{Style.RESET_ALL}")
            
            # 3. Connect to local service
            logger.info(f"{Fore.CYAN}[TUNNEL] Connecting to local {self.local_host}:{self.local_port}{Style.RESET_ALL}")
            local_reader, local_writer = await asyncio.open_connection(
                self.local_host,
                self.local_port
            )
            
            logger.info(f"{Fore.GREEN}[TUNNEL] ✅ Tunnel ACTIVE!{Style.RESET_ALL}")
            
            # 4. Start bidirectional forwarding
            await asyncio.gather(
                self.forward_data(tunnel_reader, local_writer, "SERVER->LOCAL"),
                self.forward_data(local_reader, tunnel_writer, "LOCAL->SERVER"),
                return_exceptions=True
            )
            
            logger.info(f"{Fore.YELLOW}[TUNNEL] Tunnel closed{Style.RESET_ALL}")
            
        except ConnectionRefusedError:
            logger.error(f"{Fore.RED}[TUNNEL] Cannot connect to local {self.local_host}:{self.local_port}{Style.RESET_ALL}")
            logger.error(f"{Fore.YELLOW}Is your phone connected? Try: adb connect {self.local_host}:{self.local_port}{Style.RESET_ALL}")
        
        except Exception as e:
            logger.error(f"{Fore.RED}[TUNNEL] Error: {e}{Style.RESET_ALL}")
    
    async def maintain_control_connection(self):
        """
        Maintain persistent control connection to server.
        This stays alive and spawns tunnels on demand.
        """
        while self.running:
            try:
                # Connect to control port
                logger.info(f"{Fore.CYAN}[CONTROL] Connecting to server...{Style.RESET_ALL}")
                reader, writer = await asyncio.open_connection(
                    self.server_host,
                    self.server_port
                )
                
                logger.info(f"{Fore.GREEN}[CONTROL] ✅ Connected to server{Style.RESET_ALL}")
                
                # Send handshake
                handshake = "MPORT_CLIENT:HELLO\n"
                writer.write(handshake.encode('utf-8'))
                await writer.drain()
                
                # Get acknowledgment
                data = await reader.read(1024)
                response = json.loads(data.decode('utf-8').strip())
                
                if response.get('type') == 'ACK':
                    self.client_id = response.get('client_id')
                    logger.info(f"{Fore.GREEN}[CONTROL] Registered as: {self.client_id}{Style.RESET_ALL}")
                
                # Immediately spawn a tunnel (for backward compatibility)
                asyncio.create_task(self.handle_tunnel_request())
                
                # Listen for commands
                while self.running:
                    data = await reader.read(1024)
                    
                    if not data:
                        logger.warning(f"{Fore.YELLOW}[CONTROL] Server disconnected{Style.RESET_ALL}")
                        break
                    
                    message = data.decode('utf-8').strip()
                    
                    if message == 'PING':
                        # Respond to ping
                        writer.write(b"PONG\n")
                        await writer.drain()
                    
                    elif message.startswith('NEW_TUNNEL'):
                        # Server requests new tunnel
                        logger.info(f"{Fore.YELLOW}[CONTROL] New tunnel requested{Style.RESET_ALL}")
                        asyncio.create_task(self.handle_tunnel_request())
                
            except ConnectionRefusedError:
                logger.error(f"{Fore.RED}[CONTROL] Cannot connect to server{Style.RESET_ALL}")
                logger.error(f"{Fore.YELLOW}Is the server running?{Style.RESET_ALL}")
            
            except Exception as e:
                logger.error(f"{Fore.RED}[CONTROL] Error: {e}{Style.RESET_ALL}")
            
            # Reconnect after delay
            if self.running:
                logger.info(f"{Fore.CYAN}[CONTROL] Reconnecting in 5 seconds...{Style.RESET_ALL}")
                await asyncio.sleep(5)
    
    async def run(self):
        """Run the client."""
        print(f"\n{Fore.CYAN}╔═══════════════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║   🚀 MPORT CLIENT - YOUR PORT TO THE WORLD          ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚═══════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")
        
        print(f"{Fore.GREEN}Starting Mport Client (Day 3 - Persistent)...{Style.RESET_ALL}")
        print(f"  • Server:  {self.server_host}:{self.server_port}")
        print(f"  • Local:   {self.local_host}:{self.local_port}")
        print(f"\n{Fore.YELLOW}Week 1 Day 3: Persistent + Multiple tunnels{Style.RESET_ALL}")
        print(f"Press Ctrl+C to stop\n")
        
        try:
            await self.maintain_control_connection()
        
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
