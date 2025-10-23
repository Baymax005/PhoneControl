"""
Mport Tunnel Server - "Your Port to the World"
Phase 1, Week 1: Basic TCP Tunnel Server

This is the server component that runs on a VPS (DigitalOcean).
It accepts connections from:
1. Internet users (public access)
2. Mport clients (your PC)

Then forwards traffic between them.
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
    Main Mport tunnel server.
    
    Architecture:
    1. Listens on public port (e.g., 8080) for internet users
    2. Listens on control port (e.g., 8081) for Mport clients
    3. Forwards traffic between internet users → client → local service
    """
    
    def __init__(self, public_port=8080, control_port=8081):
        self.public_port = public_port
        self.control_port = control_port
        self.clients = {}  # Connected Mport clients
        self.tunnels = {}  # Active tunnels
        
        logger.info(f"{Fore.CYAN}Initializing Mport Server{Style.RESET_ALL}")
        logger.info(f"Public port: {public_port}")
        logger.info(f"Control port: {control_port}")
    
    async def handle_public_connection(self, reader, writer):
        """
        Handle incoming connections from internet users.
        These are people trying to access the tunneled service.
        """
        addr = writer.get_extra_info('peername')
        logger.info(f"{Fore.GREEN}[PUBLIC] New connection from {addr}{Style.RESET_ALL}")
        
        try:
            # Read the request
            data = await reader.read(1024)
            
            if not data:
                logger.warning(f"{Fore.YELLOW}[PUBLIC] Empty request from {addr}{Style.RESET_ALL}")
                writer.close()
                await writer.wait_closed()
                return
            
            logger.info(f"{Fore.CYAN}[PUBLIC] Received {len(data)} bytes from {addr}{Style.RESET_ALL}")
            
            # TODO: Forward to appropriate client
            # For now, just echo back
            response = b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nMport Server - Phase 1\nYour Port to the World!\n"
            writer.write(response)
            await writer.drain()
            
            logger.info(f"{Fore.GREEN}[PUBLIC] Sent response to {addr}{Style.RESET_ALL}")
            
        except Exception as e:
            logger.error(f"{Fore.RED}[PUBLIC] Error handling {addr}: {e}{Style.RESET_ALL}")
        
        finally:
            writer.close()
            await writer.wait_closed()
            logger.info(f"{Fore.YELLOW}[PUBLIC] Connection closed: {addr}{Style.RESET_ALL}")
    
    async def handle_client_connection(self, reader, writer):
        """
        Handle connections from Mport clients (your PC).
        These are the tunnel endpoints that forward to local services.
        """
        addr = writer.get_extra_info('peername')
        logger.info(f"{Fore.MAGENTA}[CLIENT] New Mport client from {addr}{Style.RESET_ALL}")
        
        try:
            # Client handshake
            data = await reader.read(1024)
            
            if not data:
                logger.warning(f"{Fore.YELLOW}[CLIENT] Empty handshake from {addr}{Style.RESET_ALL}")
                writer.close()
                await writer.wait_closed()
                return
            
            message = data.decode('utf-8').strip()
            logger.info(f"{Fore.CYAN}[CLIENT] Handshake: {message}{Style.RESET_ALL}")
            
            # Store client connection
            client_id = f"client_{len(self.clients) + 1}"
            self.clients[client_id] = {
                'reader': reader,
                'writer': writer,
                'addr': addr,
                'connected_at': datetime.now()
            }
            
            # Send acknowledgment
            response = f"MPORT_ACK:{client_id}\n".encode('utf-8')
            writer.write(response)
            await writer.drain()
            
            logger.info(f"{Fore.GREEN}[CLIENT] Registered as {client_id}{Style.RESET_ALL}")
            
            # Keep connection alive
            while True:
                data = await reader.read(1024)
                if not data:
                    break
                
                # Handle client messages
                logger.info(f"{Fore.CYAN}[CLIENT] Message from {client_id}: {len(data)} bytes{Style.RESET_ALL}")
            
        except Exception as e:
            logger.error(f"{Fore.RED}[CLIENT] Error with {addr}: {e}{Style.RESET_ALL}")
        
        finally:
            # Remove client
            if client_id in self.clients:
                del self.clients[client_id]
                logger.info(f"{Fore.YELLOW}[CLIENT] Disconnected: {client_id}{Style.RESET_ALL}")
            
            writer.close()
            await writer.wait_closed()
    
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
        print(f"\n{Fore.YELLOW}Phase 1 - Week 1: Basic TCP Tunnel{Style.RESET_ALL}")
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
