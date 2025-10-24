"""
Mport Tunnel Server - "Your Port to the World"
Phase 1, Week 1 Day 4: Error Handling & Recovery

NEW in Day 4:
- Comprehensive error handling for all operations
- Enhanced logging system (file + console)
- Connection health monitoring
- Graceful shutdown handling
- Auto-cleanup of dead connections
- User-friendly error messages
"""

import asyncio
import logging
import json
import signal
import sys
from datetime import datetime
from pathlib import Path
from colorama import Fore, Style, init

init(autoreset=True)

# Setup enhanced logging system
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Create formatters
console_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
file_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Setup logger
logger = logging.getLogger('MportServer')
logger.setLevel(logging.DEBUG)  # Capture all levels

# Console handler (INFO and above)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(console_formatter)

# File handler (DEBUG and above)
log_file = LOG_DIR / f"server_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(file_formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

logger.info(f"Logging to: {log_file}")


class ConnectionMonitor:
    """
    Monitor connection health and auto-cleanup dead connections.
    NEW in Day 4!
    """
    
    def __init__(self, server):
        self.server = server
        self.running = True
    
    async def start(self):
        """Start monitoring connections."""
        logger.info(f"{Fore.CYAN}[MONITOR] Connection monitor started{Style.RESET_ALL}")
        
        while self.running:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                await self.check_connections()
            except Exception as e:
                logger.error(f"{Fore.RED}[MONITOR] Error: {e}{Style.RESET_ALL}", exc_info=True)
    
    async def check_connections(self):
        """Check all client connections for health."""
        dead_clients = []
        
        for client_id, client_info in self.server.clients.items():
            try:
                writer = client_info['writer']
                
                # Check if connection is still alive
                if writer.is_closing():
                    logger.warning(f"{Fore.YELLOW}[MONITOR] {client_id} connection is closing{Style.RESET_ALL}")
                    dead_clients.append(client_id)
                    continue
                
                # Calculate uptime
                uptime = (datetime.now() - client_info['connected_at']).total_seconds()
                logger.debug(f"[MONITOR] {client_id} uptime: {uptime:.0f}s")
                
            except Exception as e:
                logger.error(f"{Fore.RED}[MONITOR] Error checking {client_id}: {e}{Style.RESET_ALL}")
                dead_clients.append(client_id)
        
        # Cleanup dead connections
        for client_id in dead_clients:
            await self.cleanup_client(client_id)
    
    async def cleanup_client(self, client_id):
        """Cleanup a dead client connection."""
        try:
            if client_id in self.server.clients:
                logger.info(f"{Fore.YELLOW}[MONITOR] Cleaning up {client_id}{Style.RESET_ALL}")
                
                client_info = self.server.clients[client_id]
                writer = client_info['writer']
                
                # Close connection
                if not writer.is_closing():
                    writer.close()
                    await writer.wait_closed()
                
                # Remove from registry
                del self.server.clients[client_id]
                logger.info(f"{Fore.GREEN}[MONITOR] {client_id} cleaned up{Style.RESET_ALL}")
                
        except Exception as e:
            logger.error(f"{Fore.RED}[MONITOR] Cleanup error for {client_id}: {e}{Style.RESET_ALL}")
    
    def stop(self):
        """Stop the monitor."""
        self.running = False
        logger.info(f"{Fore.YELLOW}[MONITOR] Stopping...{Style.RESET_ALL}")


class MportServer:
    """
    Production-ready Mport server with comprehensive error handling.
    Day 4 improvements:
    - Try/except blocks on all operations
    - Connection health monitoring
    - Enhanced logging
    - Graceful shutdown
    """
    
    def __init__(self, public_port=8080, control_port=8081, tunnel_port=8082):
        self.public_port = public_port
        self.control_port = control_port
        self.tunnel_port = tunnel_port
        self.clients = {}  # {client_id: {reader, writer, tunnel_queue, connected_at}}
        self.active_tunnels = {}  # {tunnel_id: {user_addr, client_id}}
        self.shutting_down = False
        self.monitor = ConnectionMonitor(self)
        
        logger.info(f"{Fore.CYAN}Initializing Mport Server (Day 4 - Error Handling){Style.RESET_ALL}")
        logger.info(f"Public port: {public_port}")
        logger.info(f"Control port: {control_port}")
        logger.info(f"Tunnel port: {tunnel_port}")
    
    async def forward_data(self, reader_src, writer_dst, direction):
        """
        Forward data bidirectionally between connections.
        Day 4: Enhanced error handling and logging.
        """
        bytes_transferred = 0
        
        try:
            while True:
                try:
                    # Read with timeout to detect dead connections
                    data = await asyncio.wait_for(reader_src.read(8192), timeout=300.0)
                    
                    if not data:
                        logger.debug(f"[{direction}] Connection closed (no data)")
                        break
                    
                    bytes_transferred += len(data)
                    logger.debug(f"[{direction}] {len(data)} bytes (total: {bytes_transferred})")
                    
                    writer_dst.write(data)
                    await writer_dst.drain()
                    
                except asyncio.TimeoutError:
                    logger.warning(f"{Fore.YELLOW}[{direction}] Timeout - connection idle{Style.RESET_ALL}")
                    break
                
                except ConnectionResetError:
                    logger.warning(f"{Fore.YELLOW}[{direction}] Connection reset by peer{Style.RESET_ALL}")
                    break
                
                except BrokenPipeError:
                    logger.warning(f"{Fore.YELLOW}[{direction}] Broken pipe{Style.RESET_ALL}")
                    break
        
        except Exception as e:
            logger.error(f"{Fore.RED}[{direction}] Error: {type(e).__name__}: {e}{Style.RESET_ALL}")
        
        finally:
            logger.info(f"{Fore.CYAN}[{direction}] Transferred {bytes_transferred} bytes total{Style.RESET_ALL}")
            
            # Clean shutdown
            try:
                if not writer_dst.is_closing():
                    writer_dst.close()
                    await writer_dst.wait_closed()
            except Exception as e:
                logger.debug(f"[{direction}] Cleanup error: {e}")
    
    async def handle_public_connection(self, user_reader, user_writer):
        """
        Handle incoming connection from internet user.
        Day 4: Better error messages and recovery.
        """
        addr = user_writer.get_extra_info('peername')
        logger.info(f"{Fore.GREEN}[PUBLIC] New connection from {addr}{Style.RESET_ALL}")
        
        try:
            # Check if any client is available
            if not self.clients:
                error_msg = "ERROR: No Mport clients connected. Please start a client first.\n"
                logger.warning(f"{Fore.RED}[PUBLIC] No clients available for {addr}{Style.RESET_ALL}")
                
                try:
                    user_writer.write(error_msg.encode('utf-8'))
                    await user_writer.drain()
                except Exception as e:
                    logger.debug(f"[PUBLIC] Could not send error to {addr}: {e}")
                
                return
            
            # Get first available client
            client_id = list(self.clients.keys())[0]
            client_info = self.clients[client_id]
            
            logger.info(f"{Fore.GREEN}[PUBLIC] Routing {addr} to {client_id}{Style.RESET_ALL}")
            
            # Wait for client to create tunnel connection (with timeout)
            try:
                logger.info(f"{Fore.YELLOW}[PUBLIC] Waiting for tunnel from {client_id}...{Style.RESET_ALL}")
                tunnel_reader, tunnel_writer = await asyncio.wait_for(
                    client_info['tunnel_queue'].get(),
                    timeout=10.0
                )
            except asyncio.TimeoutError:
                error_msg = "ERROR: Timeout waiting for tunnel connection. Client may be offline.\n"
                logger.error(f"{Fore.RED}[PUBLIC] Tunnel timeout for {addr}{Style.RESET_ALL}")
                
                try:
                    user_writer.write(error_msg.encode('utf-8'))
                    await user_writer.drain()
                except:
                    pass
                
                return
            
            logger.info(f"{Fore.GREEN}[PUBLIC] Tunnel established for {addr}!{Style.RESET_ALL}")
            
            # Start bidirectional forwarding
            try:
                await asyncio.gather(
                    self.forward_data(user_reader, tunnel_writer, f"USER[{addr}]->TUNNEL"),
                    self.forward_data(tunnel_reader, user_writer, f"TUNNEL->USER[{addr}]"),
                    return_exceptions=True
                )
            except Exception as e:
                logger.error(f"{Fore.RED}[PUBLIC] Forwarding error for {addr}: {e}{Style.RESET_ALL}")
            
        except Exception as e:
            logger.error(f"{Fore.RED}[PUBLIC] Unhandled error for {addr}: {type(e).__name__}: {e}{Style.RESET_ALL}", exc_info=True)
        
        finally:
            logger.info(f"{Fore.YELLOW}[PUBLIC] Connection closed: {addr}{Style.RESET_ALL}")
            
            try:
                if not user_writer.is_closing():
                    user_writer.close()
                    await user_writer.wait_closed()
            except Exception as e:
                logger.debug(f"[PUBLIC] Cleanup error: {e}")
    
    async def handle_control_connection(self, reader, writer):
        """
        Handle persistent control connection from Mport client.
        Day 4: Enhanced error handling and graceful degradation.
        """
        addr = writer.get_extra_info('peername')
        logger.info(f"{Fore.MAGENTA}[CONTROL] New client from {addr}{Style.RESET_ALL}")
        
        client_id = None
        
        try:
            # Handshake with timeout
            try:
                data = await asyncio.wait_for(reader.read(1024), timeout=10.0)
            except asyncio.TimeoutError:
                logger.warning(f"{Fore.YELLOW}[CONTROL] Handshake timeout from {addr}{Style.RESET_ALL}")
                return
            
            if not data:
                logger.warning(f"{Fore.YELLOW}[CONTROL] Empty handshake from {addr}{Style.RESET_ALL}")
                return
            
            try:
                message = data.decode('utf-8').strip()
                logger.info(f"{Fore.CYAN}[CONTROL] Handshake: {message}{Style.RESET_ALL}")
            except UnicodeDecodeError as e:
                logger.error(f"{Fore.RED}[CONTROL] Invalid handshake encoding: {e}{Style.RESET_ALL}")
                return
            
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
            try:
                response = json.dumps({
                    'type': 'ACK',
                    'client_id': client_id,
                    'message': 'Control connection established',
                    'server_version': 'Day4'
                }) + '\n'
                writer.write(response.encode('utf-8'))
                await writer.drain()
            except Exception as e:
                logger.error(f"{Fore.RED}[CONTROL] Could not send ACK: {e}{Style.RESET_ALL}")
                return
            
            logger.info(f"{Fore.GREEN}[CONTROL] Registered {client_id} from {addr}{Style.RESET_ALL}")
            
            # Keep connection alive - listen for responses
            ping_failures = 0
            max_ping_failures = 3
            
            while not self.shutting_down:
                try:
                    # Wait for data with timeout
                    data = await asyncio.wait_for(reader.read(1024), timeout=60.0)
                    
                    if not data:
                        logger.warning(f"{Fore.YELLOW}[CONTROL] {client_id} disconnected{Style.RESET_ALL}")
                        break
                    
                    message = data.decode('utf-8').strip()
                    
                    if message == 'PONG':
                        logger.debug(f"[CONTROL] {client_id} alive (ping_failures reset)")
                        ping_failures = 0  # Reset on successful pong
                    else:
                        logger.debug(f"[CONTROL] {client_id} sent: {message}")
                
                except asyncio.TimeoutError:
                    # Send ping
                    try:
                        writer.write(b"PING\n")
                        await writer.drain()
                        ping_failures += 1
                        logger.debug(f"[CONTROL] Sent PING to {client_id} (failures: {ping_failures})")
                        
                        if ping_failures >= max_ping_failures:
                            logger.warning(f"{Fore.YELLOW}[CONTROL] {client_id} not responding (max failures){Style.RESET_ALL}")
                            break
                        
                    except Exception as e:
                        logger.warning(f"{Fore.YELLOW}[CONTROL] Could not ping {client_id}: {e}{Style.RESET_ALL}")
                        break
                
                except UnicodeDecodeError as e:
                    logger.error(f"{Fore.RED}[CONTROL] Invalid message encoding from {client_id}: {e}{Style.RESET_ALL}")
                    continue
                
                except Exception as e:
                    logger.error(f"{Fore.RED}[CONTROL] Error with {client_id}: {type(e).__name__}: {e}{Style.RESET_ALL}")
                    break
        
        except Exception as e:
            logger.error(f"{Fore.RED}[CONTROL] Unhandled error: {type(e).__name__}: {e}{Style.RESET_ALL}", exc_info=True)
        
        finally:
            # Cleanup
            if client_id and client_id in self.clients:
                del self.clients[client_id]
                logger.info(f"{Fore.YELLOW}[CONTROL] Disconnected: {client_id}{Style.RESET_ALL}")
            
            try:
                if not writer.is_closing():
                    writer.close()
                    await writer.wait_closed()
            except Exception as e:
                logger.debug(f"[CONTROL] Cleanup error: {e}")
    
    async def handle_tunnel_connection(self, reader, writer):
        """
        Handle tunnel connection from client.
        Day 4: Better validation and error handling.
        """
        addr = writer.get_extra_info('peername')
        logger.info(f"{Fore.BLUE}[TUNNEL] New tunnel connection from {addr}{Style.RESET_ALL}")
        
        try:
            # Read tunnel registration with timeout
            try:
                data = await asyncio.wait_for(reader.read(1024), timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning(f"{Fore.YELLOW}[TUNNEL] Registration timeout from {addr}{Style.RESET_ALL}")
                return
            
            if not data:
                logger.warning(f"{Fore.YELLOW}[TUNNEL] Empty registration from {addr}{Style.RESET_ALL}")
                return
            
            try:
                message = json.loads(data.decode('utf-8').strip())
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.error(f"{Fore.RED}[TUNNEL] Invalid registration from {addr}: {e}{Style.RESET_ALL}")
                return
            
            client_id = message.get('client_id')
            
            if not client_id:
                logger.error(f"{Fore.RED}[TUNNEL] Missing client_id from {addr}{Style.RESET_ALL}")
                return
            
            logger.info(f"{Fore.CYAN}[TUNNEL] Registration from {client_id}{Style.RESET_ALL}")
            
            if client_id not in self.clients:
                logger.error(f"{Fore.RED}[TUNNEL] Unknown client: {client_id} from {addr}{Style.RESET_ALL}")
                return
            
            # Add this tunnel to client's queue
            await self.clients[client_id]['tunnel_queue'].put((reader, writer))
            logger.info(f"{Fore.GREEN}[TUNNEL] Added to {client_id} queue{Style.RESET_ALL}")
            
        except Exception as e:
            logger.error(f"{Fore.RED}[TUNNEL] Unhandled error: {type(e).__name__}: {e}{Style.RESET_ALL}", exc_info=True)
    
    async def start_public_server(self):
        """Start the public-facing server for internet users."""
        try:
            server = await asyncio.start_server(
                self.handle_public_connection,
                '0.0.0.0',
                self.public_port
            )
            
            addr = server.sockets[0].getsockname()
            logger.info(f"{Fore.GREEN}[PUBLIC SERVER] Listening on {addr}{Style.RESET_ALL}")
            
            async with server:
                await server.serve_forever()
                
        except OSError as e:
            logger.error(f"{Fore.RED}[PUBLIC SERVER] Could not bind to port {self.public_port}: {e}{Style.RESET_ALL}")
            logger.error(f"{Fore.RED}Port may already be in use. Please check and try again.{Style.RESET_ALL}")
            raise
        except Exception as e:
            logger.error(f"{Fore.RED}[PUBLIC SERVER] Unexpected error: {e}{Style.RESET_ALL}", exc_info=True)
            raise
    
    async def start_control_server(self):
        """Start the control server for Mport client control connections."""
        try:
            server = await asyncio.start_server(
                self.handle_control_connection,
                '0.0.0.0',
                self.control_port
            )
            
            addr = server.sockets[0].getsockname()
            logger.info(f"{Fore.MAGENTA}[CONTROL SERVER] Listening on {addr}{Style.RESET_ALL}")
            
            async with server:
                await server.serve_forever()
                
        except OSError as e:
            logger.error(f"{Fore.RED}[CONTROL SERVER] Could not bind to port {self.control_port}: {e}{Style.RESET_ALL}")
            logger.error(f"{Fore.RED}Port may already be in use. Please check and try again.{Style.RESET_ALL}")
            raise
        except Exception as e:
            logger.error(f"{Fore.RED}[CONTROL SERVER] Unexpected error: {e}{Style.RESET_ALL}", exc_info=True)
            raise
    
    async def start_tunnel_server(self):
        """Start the tunnel server for actual data forwarding."""
        try:
            server = await asyncio.start_server(
                self.handle_tunnel_connection,
                '0.0.0.0',
                self.tunnel_port
            )
            
            addr = server.sockets[0].getsockname()
            logger.info(f"{Fore.BLUE}[TUNNEL SERVER] Listening on {addr}{Style.RESET_ALL}")
            
            async with server:
                await server.serve_forever()
                
        except OSError as e:
            logger.error(f"{Fore.RED}[TUNNEL SERVER] Could not bind to port {self.tunnel_port}: {e}{Style.RESET_ALL}")
            logger.error(f"{Fore.RED}Port may already be in use. Please check and try again.{Style.RESET_ALL}")
            raise
        except Exception as e:
            logger.error(f"{Fore.RED}[TUNNEL SERVER] Unexpected error: {e}{Style.RESET_ALL}", exc_info=True)
            raise
    
    async def shutdown(self):
        """
        Graceful shutdown handler.
        NEW in Day 4!
        """
        logger.info(f"{Fore.YELLOW}[SHUTDOWN] Initiating graceful shutdown...{Style.RESET_ALL}")
        self.shutting_down = True
        
        # Stop monitor
        self.monitor.stop()
        
        # Close all client connections
        logger.info(f"[SHUTDOWN] Closing {len(self.clients)} client connections...")
        
        for client_id, client_info in list(self.clients.items()):
            try:
                writer = client_info['writer']
                
                # Send shutdown notification
                try:
                    writer.write(b"SERVER_SHUTDOWN\n")
                    await writer.drain()
                except:
                    pass
                
                # Close connection
                if not writer.is_closing():
                    writer.close()
                    await writer.wait_closed()
                
                logger.info(f"[SHUTDOWN] Closed {client_id}")
                
            except Exception as e:
                logger.debug(f"[SHUTDOWN] Error closing {client_id}: {e}")
        
        self.clients.clear()
        logger.info(f"{Fore.GREEN}[SHUTDOWN] All connections closed{Style.RESET_ALL}")
    
    async def run(self):
        """Run all servers concurrently with connection monitoring."""
        print(f"\n{Fore.CYAN}╔═══════════════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║   🚀 MPORT SERVER - YOUR PORT TO THE WORLD          ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║      Day 4: Error Handling & Recovery                ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚═══════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")
        
        print(f"{Fore.GREEN}Starting Mport Server (Day 4 - Production Ready)...{Style.RESET_ALL}")
        print(f"  • Public port:  {self.public_port} (for internet users)")
        print(f"  • Control port: {self.control_port} (for client control)")
        print(f"  • Tunnel port:  {self.tunnel_port} (for tunnel connections)")
        print(f"\n{Fore.YELLOW}✨ NEW in Day 4:{Style.RESET_ALL}")
        print(f"  • Comprehensive error handling")
        print(f"  • Connection health monitoring")
        print(f"  • Enhanced logging (console + file)")
        print(f"  • Graceful shutdown (Ctrl+C)")
        print(f"  • Auto-cleanup dead connections")
        print(f"\nLogging to: {Fore.CYAN}{log_file}{Style.RESET_ALL}")
        print(f"Press {Fore.YELLOW}Ctrl+C{Style.RESET_ALL} to shutdown gracefully\n")
        
        try:
            # Start connection monitor
            monitor_task = asyncio.create_task(self.monitor.start())
            
            # Start all servers
            await asyncio.gather(
                self.start_public_server(),
                self.start_control_server(),
                self.start_tunnel_server(),
                monitor_task
            )
            
        except KeyboardInterrupt:
            await self.shutdown()
        except Exception as e:
            logger.error(f"{Fore.RED}Fatal error: {e}{Style.RESET_ALL}", exc_info=True)
            await self.shutdown()


async def main():
    """Main entry point with signal handling."""
    server = MportServer(
        public_port=8080,
        control_port=8081,
        tunnel_port=8082
    )
    
    # Setup signal handlers for graceful shutdown
    loop = asyncio.get_running_loop()
    
    def signal_handler():
        logger.info("Received shutdown signal")
        asyncio.create_task(server.shutdown())
    
    # Register signal handlers (Windows compatible)
    try:
        loop.add_signal_handler(signal.SIGINT, signal_handler)
        loop.add_signal_handler(signal.SIGTERM, signal_handler)
    except NotImplementedError:
        # Windows doesn't support add_signal_handler
        pass
    
    await server.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.GREEN}Mport Server stopped gracefully.{Style.RESET_ALL}")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n{Fore.RED}Server crashed. Check logs for details.{Style.RESET_ALL}")
        sys.exit(1)
