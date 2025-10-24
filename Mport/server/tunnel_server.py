"""
Mport Tunnel Server - "Your Port to the World"
Phase 1, Week 1 Day 2: SIMPLIFIED - One tunnel per connection

This is the server that runs on your VPS (or localhost for testing).
It accepts connections from:
1. Internet users (port 8080) - people accessing your tunneled service
2. Mport clients (port 8081) - your PC that forwards to local phone
"""

import asyncio
import logging
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
    Simple Mport server - one client connection handles one user connection.
    Week 1: Basic proof of concept.
    """
    
    def __init__(self, public_port=8080, control_port=8081):
        self.public_port = public_port
        self.control_port = control_port
        self.waiting_clients = asyncio.Queue()  # Queue of available clients
        
        logger.info(f"{Fore.CYAN}Initializing Mport Server{Style.RESET_ALL}")
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
            # Wait for an available client
            logger.info(f"{Fore.YELLOW}[PUBLIC] Waiting for available Mport client...{Style.RESET_ALL}")
            client_reader, client_writer = await self.waiting_clients.get()
            
            logger.info(f"{Fore.GREEN}[PUBLIC] Got client! Starting tunnel for {addr}{Style.RESET_ALL}")
            
            # Start bidirectional forwarding
            await asyncio.gather(
                self.forward_data(user_reader, client_writer, f"USER->{addr}"),
                self.forward_data(client_reader, user_writer, f"CLIENT->{addr}"),
                return_exceptions=True
            )
            
        except Exception as e:
            logger.error(f"{Fore.RED}[PUBLIC] Error with {addr}: {e}{Style.RESET_ALL}")
        
        finally:
            logger.info(f"{Fore.YELLOW}[PUBLIC] Connection closed: {addr}{Style.RESET_ALL}")
            user_writer.close()
            await user_writer.wait_closed()
    
    async def handle_client_connection(self, client_reader, client_writer):
        """
        Handle connection from Mport client.
        Each client connection is added to queue for next public connection.
        """
        addr = client_writer.get_extra_info('peername')
        logger.info(f"{Fore.MAGENTA}[CLIENT] New Mport client from {addr}{Style.RESET_ALL}")
        
        try:
            # Client handshake
            data = await client_reader.read(1024)
            
            if not data:
                logger.warning(f"{Fore.YELLOW}[CLIENT] Empty handshake{Style.RESET_ALL}")
                return
            
            message = data.decode('utf-8').strip()
            logger.info(f"{Fore.CYAN}[CLIENT] Handshake: {message}{Style.RESET_ALL}")
            
            # Send acknowledgment
            client_id = f"client_{datetime.now().strftime('%H%M%S')}"
            response = f"MPORT_ACK:{client_id}\n".encode('utf-8')
            client_writer.write(response)
            await client_writer.drain()
            
            logger.info(f"{Fore.GREEN}[CLIENT] Registered as {client_id}, adding to queue{Style.RESET_ALL}")
            
            # Add this client to the queue for the next public connection
            await self.waiting_clients.put((client_reader, client_writer))
            logger.info(f"{Fore.CYAN}[CLIENT] {client_id} ready for tunnel{Style.RESET_ALL}")
            
        except Exception as e:
            logger.error(f"{Fore.RED}[CLIENT] Error: {e}{Style.RESET_ALL}")
            client_writer.close()
            await client_writer.wait_closed()
    
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
        """Start the control server for Mport clients."""
        server = await asyncio.start_server(
            self.handle_client_connection,
            '0.0.0.0',
            self.control_port
        )
        
        addr = server.sockets[0].getsockname()
        logger.info(f"{Fore.MAGENTA}[CONTROL SERVER] Listening on {addr}{Style.RESET_ALL}")
        
        async with server:
            await server.serve_forever()
    
    async def run(self):
        """Run both servers concurrently."""
        print(f"\n{Fore.CYAN}╔═══════════════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║   🚀 MPORT SERVER - YOUR PORT TO THE WORLD          ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚═══════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")
        
        print(f"{Fore.GREEN}Starting Mport Server...{Style.RESET_ALL}")
        print(f"  • Public port:  {self.public_port} (for internet users)")
        print(f"  • Control port: {self.control_port} (for Mport clients)")
        print(f"\n{Fore.YELLOW}Phase 1 - Week 1 Day 2: SIMPLIFIED TUNNEL{Style.RESET_ALL}")
        print(f"{Style.DIM}Each client connection handles ONE user connection{Style.RESET_ALL}")
        print(f"Press Ctrl+C to stop\n")
        
        try:
            await asyncio.gather(
                self.start_public_server(),
                self.start_control_server()
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
