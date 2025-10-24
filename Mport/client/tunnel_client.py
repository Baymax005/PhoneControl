"""
Mport Tunnel Client - "Your Port to the World"
Phase 1, Week 1 Day 5: Performance & Polish

NEW in Day 5:
- ⚙️  CLI argument parsing (--server-host, --server-port, --local-host, --local-port, --log-level, --debug)
- 📊 Statistics request support (can query server stats)
- 🔥 Performance optimizations
- 💾 Better configuration management

Compatible with Day 5 server features!
"""

import asyncio
import logging
import json
import sys
import argparse
from datetime import datetime
from pathlib import Path
from colorama import Fore, Style, init

init(autoreset=True)


def setup_logging(log_level='INFO', debug=False):
    """
    Setup enhanced logging system with CLI configuration.
    NEW in Day 5: Configurable log levels!
    """
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
    
    # Set level based on CLI args
    if debug:
        logger.setLevel(logging.DEBUG)
        console_level = logging.DEBUG
    else:
        logger.setLevel(getattr(logging, log_level.upper()))
        console_level = logging.INFO
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(console_formatter)
    
    # File handler (always DEBUG in file)
    log_file = LOG_DIR / f"client_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    logger.info(f"Logging to: {log_file}")
    logger.info(f"Log level: {log_level.upper()} (debug={debug})")
    
    return logger


class MportClient:
    """
    Production-ready Mport client.
    Day 5 improvements:
    - CLI argument support
    - Server statistics requests
    - Enhanced configuration
    """
    
    def __init__(self, server_host, server_port, local_host, local_port, tunnel_port=8082):
        self.server_host = server_host
        self.server_port = server_port
        self.local_host = local_host
        self.local_port = local_port
        self.tunnel_port = tunnel_port
        self.client_id = None
        self.running = True
        self.reconnect_delay = 5  # Initial reconnect delay
        self.max_reconnect_delay = 60  # Max 60 seconds
        
        logger = logging.getLogger('MportClient')
        logger.info(f"{Fore.CYAN}Initializing Mport Client (Day 5 - Performance & Polish){Style.RESET_ALL}")
        logger.info(f"Server: {server_host}:{server_port}")
        logger.info(f"Tunnel port: {tunnel_port}")
        logger.info(f"Local service: {local_host}:{local_port}")
    
    async def forward_data(self, reader_src, writer_dst, direction):
        """
        Forward data bidirectionally.
        Day 5: Same as Day 4, optimized for performance.
        """
        logger = logging.getLogger('MportClient')
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
        """
        logger = logging.getLogger('MportClient')
        
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
    
    async def request_server_stats(self, control_writer):
        """
        Request statistics from server.
        NEW in Day 5!
        """
        logger = logging.getLogger('MportClient')
        
        try:
            logger.info(f"{Fore.CYAN}[STATS] Requesting server statistics...{Style.RESET_ALL}")
            control_writer.write(b"STATS_REQUEST\n")
            await control_writer.drain()
        except Exception as e:
            logger.error(f"{Fore.RED}[STATS] Could not request stats: {e}{Style.RESET_ALL}")
    
    async def handle_tunnel_request(self):
        """
        Handle tunnel request from server.
        Day 5: Same as Day 4, optimized.
        """
        logger = logging.getLogger('MportClient')
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
        Day 5: Enhanced with server feature detection.
        """
        logger = logging.getLogger('MportClient')
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
                    handshake = f"MPORT_CLIENT v1.0 Day5\n"
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
                    features = response.get('features', [])
                    
                    logger.info(f"{Fore.GREEN}[CONTROL] Registered as: {self.client_id}{Style.RESET_ALL}")
                    logger.info(f"{Fore.CYAN}[CONTROL] Server version: {server_version}{Style.RESET_ALL}")
                    if features:
                        logger.info(f"{Fore.CYAN}[CONTROL] Server features: {', '.join(features)}{Style.RESET_ALL}")
                    
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
                        
                        elif message.startswith('{'):
                            # JSON message (likely stats response)
                            try:
                                json_data = json.loads(message)
                                if json_data.get('type') == 'STATS':
                                    logger.info(f"{Fore.GREEN}[STATS] Received server statistics:{Style.RESET_ALL}")
                                    for key, value in json_data.get('data', {}).items():
                                        logger.info(f"  {key}: {value}")
                            except json.JSONDecodeError:
                                logger.debug(f"[CONTROL] Received: {message}")
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
        """
        logger = logging.getLogger('MportClient')
        logger.info(f"{Fore.YELLOW}[SHUTDOWN] Initiating graceful shutdown...{Style.RESET_ALL}")
        self.running = False
        
        # Give connections time to close
        await asyncio.sleep(1)
        
        logger.info(f"{Fore.GREEN}[SHUTDOWN] Shutdown complete{Style.RESET_ALL}")
    
    async def run(self):
        """Run the client with error handling."""
        print(f"\n{Fore.CYAN}╔═══════════════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║   🚀 MPORT CLIENT - YOUR PORT TO THE WORLD          ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║      Day 5: Performance & Polish                     ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚═══════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")
        
        print(f"{Fore.GREEN}Starting Mport Client (Day 5 - Production Grade)...{Style.RESET_ALL}")
        print(f"  • Server:        {self.server_host}:{self.server_port}")
        print(f"  • Tunnel port:   {self.tunnel_port}")
        print(f"  • Local service: {self.local_host}:{self.local_port}")
        print(f"\n{Fore.YELLOW}✨ NEW in Day 5:{Style.RESET_ALL}")
        print(f"  • ⚙️  CLI argument parsing")
        print(f"  • 📊 Server statistics requests")
        print(f"  • 🔥 Performance optimizations")
        print(f"  • 💾 Enhanced configuration")
        print(f"\nPress {Fore.YELLOW}Ctrl+C{Style.RESET_ALL} to shutdown gracefully\n")
        
        # Validate local service first
        if not await self.validate_local_service():
            logger = logging.getLogger('MportClient')
            logger.error(f"{Fore.RED}Cannot proceed without local service. Exiting.{Style.RESET_ALL}")
            return
        
        try:
            await self.maintain_control_connection()
        except KeyboardInterrupt:
            await self.shutdown()
        except Exception as e:
            logger = logging.getLogger('MportClient')
            logger.error(f"{Fore.RED}Fatal error: {e}{Style.RESET_ALL}", exc_info=True)
            await self.shutdown()


def parse_args():
    """
    Parse command-line arguments.
    NEW in Day 5!
    """
    parser = argparse.ArgumentParser(
        description='Mport Tunnel Client - Your Port to the World',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s                                          # Run with defaults
  %(prog)s --server localhost --port 8081           # Connect to local server
  %(prog)s --local-host 192.168.1.100 --local-port 5555   # Custom local service
  %(prog)s --log-level DEBUG                        # Verbose logging
  %(prog)s --debug                                  # Debug mode
        '''
    )
    
    parser.add_argument('--server', '--server-host', type=str, default='localhost',
                        help='Server hostname/IP (default: localhost)')
    parser.add_argument('--port', '--server-port', type=int, default=8081,
                        help='Server control port (default: 8081)')
    parser.add_argument('--tunnel-port', type=int, default=8082,
                        help='Server tunnel port (default: 8082)')
    parser.add_argument('--local-host', type=str, default='192.168.100.148',
                        help='Local service host (default: 192.168.100.148)')
    parser.add_argument('--local-port', type=int, default=5555,
                        help='Local service port (default: 5555)')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='INFO',
                        help='Logging level (default: INFO)')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug mode (verbose logging)')
    parser.add_argument('--version', action='version', version='Mport Client Day 5 (Week 1)')
    
    return parser.parse_args()


async def main():
    """Main entry point with CLI argument support."""
    args = parse_args()
    
    # Setup logging with CLI args
    global logger
    logger = setup_logging(log_level=args.log_level, debug=args.debug)
    
    # Create client with CLI args
    client = MportClient(
        server_host=args.server,
        server_port=args.port,
        local_host=args.local_host,
        local_port=args.local_port,
        tunnel_port=args.tunnel_port
    )
    
    await client.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.GREEN}Mport Client stopped gracefully.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Client crashed. Check logs for details.{Style.RESET_ALL}")
        sys.exit(1)
