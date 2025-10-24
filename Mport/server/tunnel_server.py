"""
Mport Tunnel Server - "Your Port to the World"
Phase 1, Week 1 Day 3: Persistent client with multiple tunnels

Architecture:
- Control connection: Client stays connected, receives tunnel requests
- Tunnel connections: Client spawns new connections for each tunnel
"""

import asyncio
import logging
import json
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MportServer:
    """
    Production-ready Mport server.
    - Persistent client connections
    - Multiple simultaneous tunnels per client
    """
    
    def __init__(self, public_port=8080, control_port=8081):
        self.public_port = public_port
        self.control_port = control_port
        self.clients = {}  # {client_id: {reader, writer, tunnel_queue}}
        self.active_tunnels = {}  # {tunnel_id: {user_addr, client_id}}
        
        logger.info(f"{Fore.CYAN}Initializing Mport Server (Day 3){Style.RESET_ALL}")
        logger.info(f"Public port: {public_port}")
        logger.info(f"Control port: {control_port}")
    
    async def forward_data(self, reader_src, writer_dst, direction):
        """Forward data bidirectionally between connections."""
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
    
    async def handle_public_connection(self, user_reader, user_writer):
        """Handle incoming connection from internet user."""
        addr = user_writer.get_extra_info('peername')
        logger.info(f"{Fore.GREEN}[PUBLIC] New connection from {addr}{Style.RESET_ALL}")
        
        try:
            # Check if any client is available
            if not self.clients:
                logger.warning(f"{Fore.RED}[PUBLIC] No clients connected!{Style.RESET_ALL}")
                user_writer.write(b"ERROR: No Mport clients available\n")
                await user_writer.drain()
                return
            
            # Get first available client
            client_id = list(self.clients.keys())[0]
            client_info = self.clients[client_id]
            
            logger.info(f"{Fore.GREEN}[PUBLIC] Routing to {client_id}{Style.RESET_ALL}")
            
            # Wait for client to create tunnel connection
            logger.info(f"{Fore.YELLOW}[PUBLIC] Waiting for tunnel from {client_id}...{Style.RESET_ALL}")
            tunnel_reader, tunnel_writer = await client_info['tunnel_queue'].get()
            
            logger.info(f"{Fore.GREEN}[PUBLIC] Tunnel established for {addr}!{Style.RESET_ALL}")
            
            # Start bidirectional forwarding
            await asyncio.gather(
                self.forward_data(user_reader, tunnel_writer, f"USER[{addr}]->TUNNEL"),
                self.forward_data(tunnel_reader, user_writer, f"TUNNEL->USER[{addr}]"),
                return_exceptions=True
            )
            
        except Exception as e:
            logger.error(f"{Fore.RED}[PUBLIC] Error with {addr}: {e}{Style.RESET_ALL}")
        
        finally:
            logger.info(f"{Fore.YELLOW}[PUBLIC] Connection closed: {addr}{Style.RESET_ALL}")
            user_writer.close()
            await user_writer.wait_closed()
    
    async def handle_control_connection(self, reader, writer):
        """
        Handle persistent control connection from Mport client.
        This connection stays alive and coordinates tunnel creation.
        """
        addr = writer.get_extra_info('peername')
        logger.info(f"{Fore.MAGENTA}[CONTROL] New client from {addr}{Style.RESET_ALL}")
        
        client_id = None
        
        try:
            # Handshake
            data = await reader.read(1024)
            if not data:
                logger.warning(f"{Fore.YELLOW}[CONTROL] Empty handshake{Style.RESET_ALL}")
                return
            
            message = data.decode('utf-8').strip()
            logger.info(f"{Fore.CYAN}[CONTROL] Handshake: {message}{Style.RESET_ALL}")
            
            # Register client
            client_id = f"client_{datetime.now().strftime('%H%M%S')}"
            self.clients[client_id] = {
                'reader': reader,
                'writer': writer,
                'addr': addr,
                'tunnel_queue': asyncio.Queue(),
                'connected_at': datetime.now()
            }
            
            # Send acknowledgment
            response = json.dumps({
                'type': 'ACK',
                'client_id': client_id,
                'message': 'Control connection established'
            }) + '\n'
            writer.write(response.encode('utf-8'))
            await writer.drain()
            
            logger.info(f"{Fore.GREEN}[CONTROL] Registered {client_id}{Style.RESET_ALL}")
            
            # Keep connection alive - listen for responses
            while True:
                try:
                    # Wait for data with timeout
                    data = await asyncio.wait_for(reader.read(1024), timeout=60.0)
                    
                    if not data:
                        logger.warning(f"{Fore.YELLOW}[CONTROL] {client_id} disconnected{Style.RESET_ALL}")
                        break
                    
                    message = data.decode('utf-8').strip()
                    if message == 'PONG':
                        logger.debug(f"{Fore.CYAN}[CONTROL] {client_id} alive{Style.RESET_ALL}")
                
                except asyncio.TimeoutError:
                    # Send ping
                    try:
                        writer.write(b"PING\n")
                        await writer.drain()
                    except:
                        logger.warning(f"{Fore.YELLOW}[CONTROL] {client_id} not responding{Style.RESET_ALL}")
                        break
                
                except Exception as e:
                    logger.error(f"{Fore.RED}[CONTROL] Error: {e}{Style.RESET_ALL}")
                    break
        
        except Exception as e:
            logger.error(f"{Fore.RED}[CONTROL] Error: {e}{Style.RESET_ALL}")
        
        finally:
            # Cleanup
            if client_id and client_id in self.clients:
                del self.clients[client_id]
                logger.info(f"{Fore.YELLOW}[CONTROL] Disconnected: {client_id}{Style.RESET_ALL}")
            
            writer.close()
            await writer.wait_closed()
    
    async def handle_tunnel_connection(self, reader, writer):
        """
        Handle tunnel connection from client.
        Each tunnel is a separate connection for one user.
        """
        addr = writer.get_extra_info('peername')
        logger.info(f"{Fore.BLUE}[TUNNEL] New tunnel connection from {addr}{Style.RESET_ALL}")
        
        try:
            # Read tunnel registration
            data = await reader.read(1024)
            if not data:
                logger.warning(f"{Fore.YELLOW}[TUNNEL] Empty registration{Style.RESET_ALL}")
                return
            
            message = json.loads(data.decode('utf-8').strip())
            client_id = message.get('client_id')
            
            logger.info(f"{Fore.CYAN}[TUNNEL] Registration from {client_id}{Style.RESET_ALL}")
            
            if client_id not in self.clients:
                logger.error(f"{Fore.RED}[TUNNEL] Unknown client: {client_id}{Style.RESET_ALL}")
                return
            
            # Add this tunnel to client's queue
            await self.clients[client_id]['tunnel_queue'].put((reader, writer))
            logger.info(f"{Fore.GREEN}[TUNNEL] Added to {client_id} queue{Style.RESET_ALL}")
            
        except Exception as e:
            logger.error(f"{Fore.RED}[TUNNEL] Error: {e}{Style.RESET_ALL}")
    
    async def start_public_server(self):
        """Start the public-facing server for internet users."""
        server = await asyncio.start_server(
            self.handle_public_connection,
            '0.0.0.0',
            self.public_port
        )
        
        addr = server.sockets[0].getsockname()
        logger.info(f"{Fore.GREEN}[PUBLIC SERVER] Listening on {addr}{Style.RESET_ALL}")
        
        async with server:
            await server.serve_forever()
    
    async def start_control_server(self):
        """Start the control server for Mport client control connections."""
        server = await asyncio.start_server(
            self.handle_control_connection,
            '0.0.0.0',
            self.control_port
        )
        
        addr = server.sockets[0].getsockname()
        logger.info(f"{Fore.MAGENTA}[CONTROL SERVER] Listening on {addr}{Style.RESET_ALL}")
        
        async with server:
            await server.serve_forever()
    
    async def start_tunnel_server(self):
        """Start the tunnel server for actual data forwarding."""
        # Use port 8082 for tunnel connections
        server = await asyncio.start_server(
            self.handle_tunnel_connection,
            '0.0.0.0',
            8082
        )
        
        addr = server.sockets[0].getsockname()
        logger.info(f"{Fore.BLUE}[TUNNEL SERVER] Listening on {addr}{Style.RESET_ALL}")
        
        async with server:
            await server.serve_forever()
    
    async def run(self):
        """Run all servers concurrently."""
        print(f"\n{Fore.CYAN}╔═══════════════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║   🚀 MPORT SERVER - YOUR PORT TO THE WORLD          ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚═══════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")
        
        print(f"{Fore.GREEN}Starting Mport Server (Day 3 - Persistent)...{Style.RESET_ALL}")
        print(f"  • Public port:  {self.public_port} (for internet users)")
        print(f"  • Control port: {self.control_port} (for client control)")
        print(f"  • Tunnel port:  8082 (for tunnel connections)")
        print(f"\n{Fore.YELLOW}Week 1 Day 3: Persistent clients + Multiple tunnels{Style.RESET_ALL}")
        print(f"Press Ctrl+C to stop\n")
        
        try:
            await asyncio.gather(
                self.start_public_server(),
                self.start_control_server(),
                self.start_tunnel_server()
            )
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Shutting down Mport Server...{Style.RESET_ALL}")
            logger.info("Server stopped by user")


async def main():
    """Main entry point."""
    server = MportServer(
        public_port=8080,
        control_port=8081
    )
    
    await server.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.GREEN}Mport Server stopped.{Style.RESET_ALL}")
