"""
Mport Tunnel Client - "Your Port to the World"
Phase 1, Week 1 Day 4: Error Handling & Recovery

NEW in Day 4:
- Comprehensive error handling for all operations
- Enhanced logging system (file + console)
- Better auto-reconnect with exponential backoff
- Graceful shutdown handling
- Connection validation and health checks
- User-friendly error messages
"""

import asyncio
import logging
import json
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
logger = logging.getLogger('MportClient')
logger.setLevel(logging.DEBUG)

# Console handler (INFO and above)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(console_formatter)

# File handler (DEBUG and above)
log_file = LOG_DIR / f"client_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(file_formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

logger.info(f"Logging to: {log_file}")


class MportClient:
    """
    Production-ready Mport client with comprehensive error handling.
    Day 4 improvements:
    - Try/except blocks on all operations
    - Exponential backoff for reconnects
    - Enhanced logging
    - Graceful shutdown
    """
    
    def __init__(self, server_host, server_port, local_host, local_port):
        self.server_host = server_host
        self.server_port = server_port
        self.local_host = local_host
        self.local_port = local_port
        self.client_id = None
        self.running = True
        self.reconnect_delay = 5  # Initial reconnect delay
        self.max_reconnect_delay = 60  # Max 60 seconds
        self.tunnel_port = 8082  # Tunnel server port
        
        logger.info(f"{Fore.CYAN}Initializing Mport Client (Day 4 - Error Handling){Style.RESET_ALL}")
        logger.info(f"Server: {server_host}:{server_port}")
        logger.info(f"Local service: {local_host}:{local_port}")
    
    async def forward_data(self, reader_src, writer_dst, direction):
        """
        Forward data bidirectionally.
        Day 4: Enhanced error handling and logging.
        """
        bytes_transferred = 0
        
        try:
            while True:
                try:
                    # Read with timeout
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
    
    async def validate_local_service(self):
        """
        Validate that local service is accessible.
        NEW in Day 4!
        """
        try:
            logger.info(f"{Fore.CYAN}[VALIDATE] Checking local service {self.local_host}:{self.local_port}...{Style.RESET_ALL}")
            
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.local_host, self.local_port),
                timeout=5.0
            )
            
            writer.close()
            await writer.wait_closed()
            
            logger.info(f"{Fore.GREEN}[VALIDATE] Local service is accessible ✓{Style.RESET_ALL}")
            return True
            
        except asyncio.TimeoutError:
            logger.error(f"{Fore.RED}[VALIDATE] Timeout connecting to local service{Style.RESET_ALL}")
            logger.error(f"{Fore.RED}Make sure {self.local_host}:{self.local_port} is running!{Style.RESET_ALL}")
            return False
        
        except ConnectionRefusedError:
            logger.error(f"{Fore.RED}[VALIDATE] Connection refused by {self.local_host}:{self.local_port}{Style.RESET_ALL}")
            logger.error(f"{Fore.RED}Is your local service running?{Style.RESET_ALL}")
            return False
        
        except Exception as e:
            logger.error(f"{Fore.RED}[VALIDATE] Error: {type(e).__name__}: {e}{Style.RESET_ALL}")
            return False
    
    async def handle_tunnel_request(self):
        """
        Handle tunnel request from server.
        Day 4: Better error handling and validation.
        """
        tunnel_reader = None
        tunnel_writer = None
        local_reader = None
        local_writer = None
        
        try:
            logger.info(f"{Fore.CYAN}[TUNNEL] Creating tunnel connection...{Style.RESET_ALL}")
            
            # Connect to tunnel server with timeout
            try:
                tunnel_reader, tunnel_writer = await asyncio.wait_for(
                    asyncio.open_connection(self.server_host, self.tunnel_port),
                    timeout=10.0
                )
            except asyncio.TimeoutError:
                logger.error(f"{Fore.RED}[TUNNEL] Timeout connecting to server{Style.RESET_ALL}")
                return
            except ConnectionRefusedError:
                logger.error(f"{Fore.RED}[TUNNEL] Connection refused by server{Style.RESET_ALL}")
                logger.error(f"{Fore.RED}Is the server running on {self.server_host}:{self.tunnel_port}?{Style.RESET_ALL}")
                return
            except OSError as e:
                logger.error(f"{Fore.RED}[TUNNEL] Network error: {e}{Style.RESET_ALL}")
                return
            
            logger.info(f"{Fore.GREEN}[TUNNEL] Connected to server{Style.RESET_ALL}")
            
            # Register tunnel with timeout
            try:
                registration = json.dumps({
                    'client_id': self.client_id,
                    'timestamp': datetime.now().isoformat()
                }) + '\n'
                
                tunnel_writer.write(registration.encode('utf-8'))
                await asyncio.wait_for(tunnel_writer.drain(), timeout=5.0)
                
            except asyncio.TimeoutError:
                logger.error(f"{Fore.RED}[TUNNEL] Timeout sending registration{Style.RESET_ALL}")
                return
            except Exception as e:
                logger.error(f"{Fore.RED}[TUNNEL] Registration error: {e}{Style.RESET_ALL}")
                return
            
            logger.info(f"{Fore.GREEN}[TUNNEL] Registered with server{Style.RESET_ALL}")
            
            # Connect to local service with timeout
            try:
                local_reader, local_writer = await asyncio.wait_for(
                    asyncio.open_connection(self.local_host, self.local_port),
                    timeout=5.0
                )
            except asyncio.TimeoutError:
                logger.error(f"{Fore.RED}[TUNNEL] Timeout connecting to local service{Style.RESET_ALL}")
                return
            except ConnectionRefusedError:
                logger.error(f"{Fore.RED}[TUNNEL] Local service not available{Style.RESET_ALL}")
                logger.error(f"{Fore.RED}Is {self.local_host}:{self.local_port} running?{Style.RESET_ALL}")
                return
            except Exception as e:
                logger.error(f"{Fore.RED}[TUNNEL] Error connecting to local service: {e}{Style.RESET_ALL}")
                return
            
            logger.info(f"{Fore.GREEN}[TUNNEL] Connected to local service{Style.RESET_ALL}")
            logger.info(f"{Fore.MAGENTA}[TUNNEL] Tunnel active!{Style.RESET_ALL}")
            
            # Start bidirectional forwarding
            try:
                await asyncio.gather(
                    self.forward_data(tunnel_reader, local_writer, "SERVER->LOCAL"),
                    self.forward_data(local_reader, tunnel_writer, "LOCAL->SERVER"),
                    return_exceptions=True
                )
            except Exception as e:
                logger.error(f"{Fore.RED}[TUNNEL] Forwarding error: {e}{Style.RESET_ALL}")
            
            logger.info(f"{Fore.YELLOW}[TUNNEL] Tunnel closed{Style.RESET_ALL}")
            
        except Exception as e:
            logger.error(f"{Fore.RED}[TUNNEL] Unhandled error: {type(e).__name__}: {e}{Style.RESET_ALL}", exc_info=True)
        
        finally:
            # Cleanup all connections
            for writer, name in [(tunnel_writer, 'tunnel'), (local_writer, 'local')]:
                if writer:
                    try:
                        if not writer.is_closing():
                            writer.close()
                            await writer.wait_closed()
                    except Exception as e:
                        logger.debug(f"[TUNNEL] Cleanup error ({name}): {e}")
    
    async def maintain_control_connection(self):
        """
        Maintain persistent control connection to server.
        Day 4: Enhanced reconnection with exponential backoff.
        """
        reconnect_attempts = 0
        
        while self.running:
            control_reader = None
            control_writer = None
            
            try:
                logger.info(f"{Fore.CYAN}[CONTROL] Connecting to {self.server_host}:{self.server_port}...{Style.RESET_ALL}")
                
                # Attempt connection with timeout
                try:
                    control_reader, control_writer = await asyncio.wait_for(
                        asyncio.open_connection(self.server_host, self.server_port),
                        timeout=10.0
                    )
                    
                    # Reset reconnect delay on successful connection
                    self.reconnect_delay = 5
                    reconnect_attempts = 0
                    
                except asyncio.TimeoutError:
                    raise ConnectionError("Connection timeout")
                except ConnectionRefusedError:
                    raise ConnectionError(f"Connection refused by {self.server_host}:{self.server_port}")
                except OSError as e:
                    raise ConnectionError(f"Network error: {e}")
                
                logger.info(f"{Fore.GREEN}[CONTROL] Connected!{Style.RESET_ALL}")
                
                # Send handshake with timeout
                try:
                    handshake = f"MPORT_CLIENT v1.0 Day4\n"
                    control_writer.write(handshake.encode('utf-8'))
                    await asyncio.wait_for(control_writer.drain(), timeout=5.0)
                except asyncio.TimeoutError:
                    raise ConnectionError("Handshake timeout")
                
                # Receive acknowledgment with timeout
                try:
                    data = await asyncio.wait_for(control_reader.read(1024), timeout=10.0)
                    if not data:
                        raise ConnectionError("Server closed connection during handshake")
                    
                    response = json.loads(data.decode('utf-8').strip())
                    self.client_id = response.get('client_id')
                    server_version = response.get('server_version', 'unknown')
                    
                    logger.info(f"{Fore.GREEN}[CONTROL] Registered as: {self.client_id}{Style.RESET_ALL}")
                    logger.info(f"{Fore.CYAN}[CONTROL] Server version: {server_version}{Style.RESET_ALL}")
                    
                except asyncio.TimeoutError:
                    raise ConnectionError("ACK timeout")
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    raise ConnectionError(f"Invalid server response: {e}")
                
                # Spawn initial tunnel (backward compatibility)
                logger.info(f"{Fore.YELLOW}[CONTROL] Spawning initial tunnel...{Style.RESET_ALL}")
                asyncio.create_task(self.handle_tunnel_request())
                
                # Listen for server messages
                while self.running:
                    try:
                        data = await asyncio.wait_for(control_reader.read(1024), timeout=30.0)
                        
                        if not data:
                            logger.warning(f"{Fore.YELLOW}[CONTROL] Server closed connection{Style.RESET_ALL}")
                            break
                        
                        message = data.decode('utf-8').strip()
                        
                        if message == 'PING':
                            logger.debug("[CONTROL] Received PING, sending PONG")
                            control_writer.write(b"PONG\n")
                            await control_writer.drain()
                        
                        elif message == 'TUNNEL_REQUEST':
                            logger.info(f"{Fore.CYAN}[CONTROL] Tunnel request received{Style.RESET_ALL}")
                            asyncio.create_task(self.handle_tunnel_request())
                        
                        elif message == 'SERVER_SHUTDOWN':
                            logger.warning(f"{Fore.YELLOW}[CONTROL] Server is shutting down{Style.RESET_ALL}")
                            break
                        
                        else:
                            logger.debug(f"[CONTROL] Received: {message}")
                    
                    except asyncio.TimeoutError:
                        logger.debug("[CONTROL] Timeout waiting for server message")
                        continue
                    
                    except UnicodeDecodeError as e:
                        logger.error(f"{Fore.RED}[CONTROL] Invalid message encoding: {e}{Style.RESET_ALL}")
                        continue
                    
                    except Exception as e:
                        logger.error(f"{Fore.RED}[CONTROL] Error: {type(e).__name__}: {e}{Style.RESET_ALL}")
                        break
            
            except ConnectionError as e:
                reconnect_attempts += 1
                logger.error(f"{Fore.RED}[CONTROL] Connection failed: {e}{Style.RESET_ALL}")
                
                if self.running:
                    # Exponential backoff
                    delay = min(self.reconnect_delay * (2 ** (reconnect_attempts - 1)), self.max_reconnect_delay)
                    logger.info(f"{Fore.YELLOW}[CONTROL] Reconnecting in {delay}s (attempt {reconnect_attempts})...{Style.RESET_ALL}")
                    await asyncio.sleep(delay)
            
            except Exception as e:
                logger.error(f"{Fore.RED}[CONTROL] Unhandled error: {type(e).__name__}: {e}{Style.RESET_ALL}", exc_info=True)
                
                if self.running:
                    logger.info(f"{Fore.YELLOW}[CONTROL] Reconnecting in {self.reconnect_delay}s...{Style.RESET_ALL}")
                    await asyncio.sleep(self.reconnect_delay)
            
            finally:
                # Cleanup
                if control_writer:
                    try:
                        if not control_writer.is_closing():
                            control_writer.close()
                            await control_writer.wait_closed()
                    except Exception as e:
                        logger.debug(f"[CONTROL] Cleanup error: {e}")
    
    async def shutdown(self):
        """
        Graceful shutdown handler.
        NEW in Day 4!
        """
        logger.info(f"{Fore.YELLOW}[SHUTDOWN] Initiating graceful shutdown...{Style.RESET_ALL}")
        self.running = False
        
        # Give connections time to close
        await asyncio.sleep(1)
        
        logger.info(f"{Fore.GREEN}[SHUTDOWN] Shutdown complete{Style.RESET_ALL}")
    
    async def run(self):
        """Run the client with error handling."""
        print(f"\n{Fore.CYAN}╔═══════════════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║   🚀 MPORT CLIENT - YOUR PORT TO THE WORLD          ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║      Day 4: Error Handling & Recovery                ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚═══════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")
        
        print(f"{Fore.GREEN}Starting Mport Client (Day 4 - Production Ready)...{Style.RESET_ALL}")
        print(f"  • Server:        {self.server_host}:{self.server_port}")
        print(f"  • Local service: {self.local_host}:{self.local_port}")
        print(f"\n{Fore.YELLOW}✨ NEW in Day 4:{Style.RESET_ALL}")
        print(f"  • Comprehensive error handling")
        print(f"  • Exponential backoff reconnection")
        print(f"  • Enhanced logging (console + file)")
        print(f"  • Graceful shutdown (Ctrl+C)")
        print(f"  • Local service validation")
        print(f"\nLogging to: {Fore.CYAN}{log_file}{Style.RESET_ALL}")
        print(f"Press {Fore.YELLOW}Ctrl+C{Style.RESET_ALL} to shutdown gracefully\n")
        
        # Validate local service first
        if not await self.validate_local_service():
            logger.error(f"{Fore.RED}Cannot proceed without local service. Exiting.{Style.RESET_ALL}")
            return
        
        try:
            await self.maintain_control_connection()
        except KeyboardInterrupt:
            await self.shutdown()
        except Exception as e:
            logger.error(f"{Fore.RED}Fatal error: {e}{Style.RESET_ALL}", exc_info=True)
            await self.shutdown()


async def main():
    """Main entry point with interactive configuration."""
    print(f"{Fore.CYAN}Mport Client Configuration{Style.RESET_ALL}\n")
    
    # Get configuration
    try:
        server_host = input(f"Server host [{Fore.YELLOW}localhost{Style.RESET_ALL}]: ").strip() or "localhost"
        server_port = input(f"Server port [{Fore.YELLOW}8081{Style.RESET_ALL}]: ").strip() or "8081"
        server_port = int(server_port)
        
        local_host = input(f"Local host [{Fore.YELLOW}192.168.100.148{Style.RESET_ALL}]: ").strip() or "192.168.100.148"
        local_port = input(f"Local port [{Fore.YELLOW}5555{Style.RESET_ALL}]: ").strip() or "5555"
        local_port = int(local_port)
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Configuration cancelled.{Style.RESET_ALL}")
        return
    except ValueError as e:
        print(f"\n{Fore.RED}Invalid port number: {e}{Style.RESET_ALL}")
        return
    
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
