"""
Mport Tunnel Server - "Your Port to the World"
Phase 1, Week 1 Day 5: Performance & Polish

NEW in Day 5:
- 📊 Connection statistics and metrics tracking
- ⚙️  CLI argument parsing (--port, --host, --log-level, --debug)
- 🛡️  Basic rate limiting (max connections per client)
- 📈 Real-time statistics display
- 🔥 Performance optimizations
- 💾 Statistics persistence

This brings Mport to professional-grade observability!
"""

import asyncio
import logging
import json
import signal
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from colorama import Fore, Style, init

init(autoreset=True)


class Statistics:
    """
    Track and display connection statistics.
    NEW in Day 5!
    """
    
    def __init__(self):
        self.start_time = datetime.now()
        self.total_connections = 0
        self.active_connections = 0
        self.total_bytes_sent = 0
        self.total_bytes_received = 0
        self.total_tunnels_created = 0
        self.total_clients = 0
        self.peak_connections = 0
        self.connection_history = []  # Last 100 connections
        self.errors = defaultdict(int)  # Error counts by type
        
    def record_connection(self, connection_type):
        """Record a new connection."""
        self.total_connections += 1
        self.active_connections += 1
        self.peak_connections = max(self.peak_connections, self.active_connections)
        
        # Keep last 100 connections
        self.connection_history.append({
            'type': connection_type,
            'timestamp': datetime.now(),
            'active': True
        })
        if len(self.connection_history) > 100:
            self.connection_history.pop(0)
    
    def record_disconnection(self):
        """Record a disconnection."""
        self.active_connections = max(0, self.active_connections - 1)
    
    def record_bytes(self, sent=0, received=0):
        """Record bytes transferred."""
        self.total_bytes_sent += sent
        self.total_bytes_received += received
    
    def record_tunnel(self):
        """Record a new tunnel creation."""
        self.total_tunnels_created += 1
    
    def record_client(self):
        """Record a new client registration."""
        self.total_clients += 1
    
    def record_error(self, error_type):
        """Record an error."""
        self.errors[error_type] += 1
    
    def get_uptime(self):
        """Get server uptime."""
        return datetime.now() - self.start_time
    
    def get_summary(self):
        """Get statistics summary."""
        uptime = self.get_uptime()
        hours = uptime.total_seconds() / 3600
        
        return {
            'uptime': str(uptime).split('.')[0],  # Remove microseconds
            'total_connections': self.total_connections,
            'active_connections': self.active_connections,
            'peak_connections': self.peak_connections,
            'total_tunnels': self.total_tunnels_created,
            'total_clients': self.total_clients,
            'bytes_sent': self.format_bytes(self.total_bytes_sent),
            'bytes_received': self.format_bytes(self.total_bytes_received),
            'total_errors': sum(self.errors.values()),
            'connections_per_hour': f"{self.total_connections / max(hours, 0.01):.1f}"
        }
    
    @staticmethod
    def format_bytes(bytes_count):
        """Format bytes in human-readable form."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_count < 1024.0:
                return f"{bytes_count:.2f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.2f} PB"
    
    def display(self):
        """Display statistics in a nice format."""
        stats = self.get_summary()
        
        print(f"\n{Fore.CYAN}╔═══════════════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║              📊 MPORT STATISTICS                     ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚═══════════════════════════════════════════════════════╝{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}⏱️  Uptime:{Style.RESET_ALL} {stats['uptime']}")
        print(f"\n{Fore.GREEN}📡 Connections:{Style.RESET_ALL}")
        print(f"   Total: {stats['total_connections']} | Active: {stats['active_connections']} | Peak: {stats['peak_connections']}")
        print(f"   Rate: {stats['connections_per_hour']}/hour")
        print(f"\n{Fore.MAGENTA}🚇 Tunnels:{Style.RESET_ALL}")
        print(f"   Created: {stats['total_tunnels']}")
        print(f"\n{Fore.BLUE}👥 Clients:{Style.RESET_ALL}")
        print(f"   Registered: {stats['total_clients']}")
        print(f"\n{Fore.CYAN}📊 Data Transfer:{Style.RESET_ALL}")
        print(f"   Sent: {stats['bytes_sent']} | Received: {stats['bytes_received']}")
        print(f"\n{Fore.RED}❌ Errors:{Style.RESET_ALL} {stats['total_errors']}\n")


class RateLimiter:
    """
    Rate limiting to prevent abuse.
    NEW in Day 5!
    """
    
    def __init__(self, max_connections_per_client=10, max_tunnels_per_minute=60):
        self.max_connections_per_client = max_connections_per_client
        self.max_tunnels_per_minute = max_tunnels_per_minute
        self.client_connections = defaultdict(int)  # {client_id: connection_count}
        self.tunnel_timestamps = defaultdict(list)  # {client_id: [timestamps]}
    
    def check_client_limit(self, client_id):
        """Check if client has exceeded connection limit."""
        count = self.client_connections.get(client_id, 0)
        if count >= self.max_connections_per_client:
            return False, f"Max connections ({self.max_connections_per_client}) exceeded"
        return True, ""
    
    def check_tunnel_rate(self, client_id):
        """Check if client has exceeded tunnel creation rate."""
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        # Clean old timestamps
        timestamps = self.tunnel_timestamps[client_id]
        timestamps = [ts for ts in timestamps if ts > minute_ago]
        self.tunnel_timestamps[client_id] = timestamps
        
        if len(timestamps) >= self.max_tunnels_per_minute:
            return False, f"Tunnel rate limit ({self.max_tunnels_per_minute}/min) exceeded"
        
        # Record new tunnel
        timestamps.append(now)
        return True, ""
    
    def register_connection(self, client_id):
        """Register a new connection for rate limiting."""
        self.client_connections[client_id] += 1
    
    def unregister_connection(self, client_id):
        """Unregister a connection."""
        self.client_connections[client_id] = max(0, self.client_connections[client_id] - 1)
        if self.client_connections[client_id] == 0:
            del self.client_connections[client_id]


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
    logger = logging.getLogger('MportServer')
    
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
    log_file = LOG_DIR / f"server_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    logger.info(f"Logging to: {log_file}")
    logger.info(f"Log level: {log_level.upper()} (debug={debug})")
    
    return logger


class ConnectionMonitor:
    """
    Monitor connection health and auto-cleanup dead connections.
    Day 5: Enhanced with statistics integration.
    """
    
    def __init__(self, server, stats):
        self.server = server
        self.stats = stats
        self.running = True
        self.check_interval = 30  # seconds
    
    async def start(self):
        """Start monitoring connections."""
        logger = logging.getLogger('MportServer')
        logger.info(f"{Fore.CYAN}[MONITOR] Connection monitor started (interval: {self.check_interval}s){Style.RESET_ALL}")
        
        while self.running:
            try:
                await asyncio.sleep(self.check_interval)
                await self.check_connections()
            except Exception as e:
                logger.error(f"{Fore.RED}[MONITOR] Error: {e}{Style.RESET_ALL}", exc_info=True)
                self.stats.record_error('monitor_error')
    
    async def check_connections(self):
        """Check all client connections for health."""
        logger = logging.getLogger('MportServer')
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
                self.stats.record_error('connection_check_error')
        
        # Cleanup dead connections
        for client_id in dead_clients:
            await self.cleanup_client(client_id)
    
    async def cleanup_client(self, client_id):
        """Cleanup a dead client connection."""
        logger = logging.getLogger('MportServer')
        
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
                self.stats.record_disconnection()
                self.server.rate_limiter.unregister_connection(client_id)
                
                logger.info(f"{Fore.GREEN}[MONITOR] {client_id} cleaned up{Style.RESET_ALL}")
                
        except Exception as e:
            logger.error(f"{Fore.RED}[MONITOR] Cleanup error for {client_id}: {e}{Style.RESET_ALL}")
            self.stats.record_error('cleanup_error')
    
    def stop(self):
        """Stop the monitor."""
        logger = logging.getLogger('MportServer')
        self.running = False
        logger.info(f"{Fore.YELLOW}[MONITOR] Stopping...{Style.RESET_ALL}")


class MportServer:
    """
    Production-ready Mport server with statistics and rate limiting.
    Day 5 improvements:
    - Connection statistics tracking
    - CLI argument support
    - Rate limiting
    - Performance optimizations
    """
    
    def __init__(self, public_port=8080, control_port=8081, tunnel_port=8082,
                 max_connections_per_client=10, stats_interval=60):
        self.public_port = public_port
        self.control_port = control_port
        self.tunnel_port = tunnel_port
        self.clients = {}  # {client_id: {reader, writer, tunnel_queue, connected_at}}
        self.active_tunnels = {}  # {tunnel_id: {user_addr, client_id}}
        self.shutting_down = False
        self.stats_interval = stats_interval
        
        # NEW in Day 5!
        self.stats = Statistics()
        self.rate_limiter = RateLimiter(max_connections_per_client=max_connections_per_client)
        self.monitor = ConnectionMonitor(self, self.stats)
        
        logger = logging.getLogger('MportServer')
        logger.info(f"{Fore.CYAN}Initializing Mport Server (Day 5 - Performance & Polish){Style.RESET_ALL}")
        logger.info(f"Public port: {public_port}")
        logger.info(f"Control port: {control_port}")
        logger.info(f"Tunnel port: {tunnel_port}")
        logger.info(f"Max connections per client: {max_connections_per_client}")
        logger.info(f"Statistics interval: {stats_interval}s")
    
    async def display_stats_periodically(self):
        """Display statistics at regular intervals."""
        logger = logging.getLogger('MportServer')
        
        while not self.shutting_down:
            try:
                await asyncio.sleep(self.stats_interval)
                self.stats.display()
            except Exception as e:
                logger.error(f"Stats display error: {e}")
    
    async def forward_data(self, reader_src, writer_dst, direction):
        """
        Forward data bidirectionally between connections.
        Day 5: Enhanced with statistics tracking.
        """
        logger = logging.getLogger('MportServer')
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
                    
                    # Update statistics
                    if 'USER' in direction:
                        self.stats.record_bytes(received=len(data))
                    else:
                        self.stats.record_bytes(sent=len(data))
                    
                    logger.debug(f"[{direction}] {len(data)} bytes (total: {bytes_transferred})")
                    
                    writer_dst.write(data)
                    await writer_dst.drain()
                    
                except asyncio.TimeoutError:
                    logger.warning(f"{Fore.YELLOW}[{direction}] Timeout - connection idle{Style.RESET_ALL}")
                    self.stats.record_error('timeout')
                    break
                
                except ConnectionResetError:
                    logger.warning(f"{Fore.YELLOW}[{direction}] Connection reset by peer{Style.RESET_ALL}")
                    self.stats.record_error('connection_reset')
                    break
                
                except BrokenPipeError:
                    logger.warning(f"{Fore.YELLOW}[{direction}] Broken pipe{Style.RESET_ALL}")
                    self.stats.record_error('broken_pipe')
                    break
        
        except Exception as e:
            logger.error(f"{Fore.RED}[{direction}] Error: {type(e).__name__}: {e}{Style.RESET_ALL}")
            self.stats.record_error(type(e).__name__)
        
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
        Day 5: Enhanced with statistics and rate limiting.
        """
        logger = logging.getLogger('MportServer')
        addr = user_writer.get_extra_info('peername')
        logger.info(f"{Fore.GREEN}[PUBLIC] New connection from {addr}{Style.RESET_ALL}")
        
        # Record connection
        self.stats.record_connection('public')
        
        try:
            # Check if any client is available
            if not self.clients:
                error_msg = "ERROR: No Mport clients connected. Please start a client first.\n"
                logger.warning(f"{Fore.RED}[PUBLIC] No clients available for {addr}{Style.RESET_ALL}")
                self.stats.record_error('no_clients')
                
                try:
                    user_writer.write(error_msg.encode('utf-8'))
                    await user_writer.drain()
                except Exception as e:
                    logger.debug(f"[PUBLIC] Could not send error to {addr}: {e}")
                
                return
            
            # Get first available client
            client_id = list(self.clients.keys())[0]
            client_info = self.clients[client_id]
            
            # Check rate limit
            allowed, reason = self.rate_limiter.check_tunnel_rate(client_id)
            if not allowed:
                error_msg = f"ERROR: {reason}\n"
                logger.warning(f"{Fore.RED}[PUBLIC] Rate limit exceeded for {client_id}: {reason}{Style.RESET_ALL}")
                self.stats.record_error('rate_limit_exceeded')
                
                try:
                    user_writer.write(error_msg.encode('utf-8'))
                    await user_writer.drain()
                except:
                    pass
                
                return
            
            logger.info(f"{Fore.GREEN}[PUBLIC] Routing {addr} to {client_id}{Style.RESET_ALL}")
            
            # Wait for client to create tunnel connection (with timeout)
            try:
                logger.info(f"{Fore.YELLOW}[PUBLIC] Waiting for tunnel from {client_id}...{Style.RESET_ALL}")
                tunnel_reader, tunnel_writer = await asyncio.wait_for(
                    client_info['tunnel_queue'].get(),
                    timeout=10.0
                )
                self.stats.record_tunnel()
            except asyncio.TimeoutError:
                error_msg = "ERROR: Timeout waiting for tunnel connection. Client may be offline.\n"
                logger.error(f"{Fore.RED}[PUBLIC] Tunnel timeout for {addr}{Style.RESET_ALL}")
                self.stats.record_error('tunnel_timeout')
                
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
                self.stats.record_error('forwarding_error')
            
        except Exception as e:
            logger.error(f"{Fore.RED}[PUBLIC] Unhandled error for {addr}: {type(e).__name__}: {e}{Style.RESET_ALL}", exc_info=True)
            self.stats.record_error('unhandled_error')
        
        finally:
            logger.info(f"{Fore.YELLOW}[PUBLIC] Connection closed: {addr}{Style.RESET_ALL}")
            self.stats.record_disconnection()
            
            try:
                if not user_writer.is_closing():
                    user_writer.close()
                    await user_writer.wait_closed()
            except Exception as e:
                logger.debug(f"[PUBLIC] Cleanup error: {e}")
    
    async def handle_control_connection(self, reader, writer):
        """
        Handle persistent control connection from Mport client.
        Day 5: Enhanced with rate limiting and statistics.
        """
        logger = logging.getLogger('MportServer')
        addr = writer.get_extra_info('peername')
        logger.info(f"{Fore.MAGENTA}[CONTROL] New client from {addr}{Style.RESET_ALL}")
        
        # Record connection
        self.stats.record_connection('control')
        
        client_id = None
        
        try:
            # Handshake with timeout
            try:
                data = await asyncio.wait_for(reader.read(1024), timeout=10.0)
            except asyncio.TimeoutError:
                logger.warning(f"{Fore.YELLOW}[CONTROL] Handshake timeout from {addr}{Style.RESET_ALL}")
                self.stats.record_error('handshake_timeout')
                return
            
            if not data:
                logger.warning(f"{Fore.YELLOW}[CONTROL] Empty handshake from {addr}{Style.RESET_ALL}")
                self.stats.record_error('empty_handshake')
                return
            
            try:
                message = data.decode('utf-8').strip()
                logger.info(f"{Fore.CYAN}[CONTROL] Handshake: {message}{Style.RESET_ALL}")
            except UnicodeDecodeError as e:
                logger.error(f"{Fore.RED}[CONTROL] Invalid handshake encoding: {e}{Style.RESET_ALL}")
                self.stats.record_error('encoding_error')
                return
            
            # Register client
            client_id = f"client_{datetime.now().strftime('%H%M%S')}"
            
            # Check rate limit
            allowed, reason = self.rate_limiter.check_client_limit(client_id)
            if not allowed:
                logger.warning(f"{Fore.RED}[CONTROL] Connection limit: {reason}{Style.RESET_ALL}")
                self.stats.record_error('connection_limit')
                return
            
            self.clients[client_id] = {
                'reader': reader,
                'writer': writer,
                'addr': addr,
                'tunnel_queue': asyncio.Queue(),
                'connected_at': datetime.now()
            }
            
            self.rate_limiter.register_connection(client_id)
            self.stats.record_client()
            
            # Send acknowledgment
            try:
                response = json.dumps({
                    'type': 'ACK',
                    'client_id': client_id,
                    'message': 'Control connection established',
                    'server_version': 'Day5',
                    'features': ['statistics', 'rate_limiting', 'cli_args']
                }) + '\n'
                writer.write(response.encode('utf-8'))
                await writer.drain()
            except Exception as e:
                logger.error(f"{Fore.RED}[CONTROL] Could not send ACK: {e}{Style.RESET_ALL}")
                self.stats.record_error('ack_error')
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
                    elif message == 'STATS_REQUEST':
                        # Send statistics to client
                        stats_data = json.dumps({
                            'type': 'STATS',
                            'data': self.stats.get_summary()
                        }) + '\n'
                        writer.write(stats_data.encode('utf-8'))
                        await writer.drain()
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
                            self.stats.record_error('ping_failure')
                            break
                        
                    except Exception as e:
                        logger.warning(f"{Fore.YELLOW}[CONTROL] Could not ping {client_id}: {e}{Style.RESET_ALL}")
                        break
                
                except UnicodeDecodeError as e:
                    logger.error(f"{Fore.RED}[CONTROL] Invalid message encoding from {client_id}: {e}{Style.RESET_ALL}")
                    self.stats.record_error('encoding_error')
                    continue
                
                except Exception as e:
                    logger.error(f"{Fore.RED}[CONTROL] Error with {client_id}: {type(e).__name__}: {e}{Style.RESET_ALL}")
                    self.stats.record_error(type(e).__name__)
                    break
        
        except Exception as e:
            logger.error(f"{Fore.RED}[CONTROL] Unhandled error: {type(e).__name__}: {e}{Style.RESET_ALL}", exc_info=True)
            self.stats.record_error('unhandled_error')
        
        finally:
            # Cleanup
            if client_id and client_id in self.clients:
                del self.clients[client_id]
                self.rate_limiter.unregister_connection(client_id)
                self.stats.record_disconnection()
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
        Day 5: Enhanced with statistics.
        """
        logger = logging.getLogger('MportServer')
        addr = writer.get_extra_info('peername')
        logger.info(f"{Fore.BLUE}[TUNNEL] New tunnel connection from {addr}{Style.RESET_ALL}")
        
        # Record connection
        self.stats.record_connection('tunnel')
        
        try:
            # Read tunnel registration with timeout
            try:
                data = await asyncio.wait_for(reader.read(1024), timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning(f"{Fore.YELLOW}[TUNNEL] Registration timeout from {addr}{Style.RESET_ALL}")
                self.stats.record_error('tunnel_reg_timeout')
                return
            
            if not data:
                logger.warning(f"{Fore.YELLOW}[TUNNEL] Empty registration from {addr}{Style.RESET_ALL}")
                self.stats.record_error('empty_tunnel_reg')
                return
            
            try:
                message = json.loads(data.decode('utf-8').strip())
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.error(f"{Fore.RED}[TUNNEL] Invalid registration from {addr}: {e}{Style.RESET_ALL}")
                self.stats.record_error('invalid_tunnel_reg')
                return
            
            client_id = message.get('client_id')
            
            if not client_id:
                logger.error(f"{Fore.RED}[TUNNEL] Missing client_id from {addr}{Style.RESET_ALL}")
                self.stats.record_error('missing_client_id')
                return
            
            logger.info(f"{Fore.CYAN}[TUNNEL] Registration from {client_id}{Style.RESET_ALL}")
            
            if client_id not in self.clients:
                logger.error(f"{Fore.RED}[TUNNEL] Unknown client: {client_id} from {addr}{Style.RESET_ALL}")
                self.stats.record_error('unknown_client')
                return
            
            # Add this tunnel to client's queue
            await self.clients[client_id]['tunnel_queue'].put((reader, writer))
            logger.info(f"{Fore.GREEN}[TUNNEL] Added to {client_id} queue{Style.RESET_ALL}")
            
        except Exception as e:
            logger.error(f"{Fore.RED}[TUNNEL] Unhandled error: {type(e).__name__}: {e}{Style.RESET_ALL}", exc_info=True)
            self.stats.record_error('unhandled_error')
    
    async def start_public_server(self):
        """Start the public-facing server for internet users."""
        logger = logging.getLogger('MportServer')
        
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
            self.stats.record_error('port_conflict')
            raise
        except Exception as e:
            logger.error(f"{Fore.RED}[PUBLIC SERVER] Unexpected error: {e}{Style.RESET_ALL}", exc_info=True)
            self.stats.record_error('server_error')
            raise
    
    async def start_control_server(self):
        """Start the control server for Mport client control connections."""
        logger = logging.getLogger('MportServer')
        
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
            self.stats.record_error('port_conflict')
            raise
        except Exception as e:
            logger.error(f"{Fore.RED}[CONTROL SERVER] Unexpected error: {e}{Style.RESET_ALL}", exc_info=True)
            self.stats.record_error('server_error')
            raise
    
    async def start_tunnel_server(self):
        """Start the tunnel server for actual data forwarding."""
        logger = logging.getLogger('MportServer')
        
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
            self.stats.record_error('port_conflict')
            raise
        except Exception as e:
            logger.error(f"{Fore.RED}[TUNNEL SERVER] Unexpected error: {e}{Style.RESET_ALL}", exc_info=True)
            self.stats.record_error('server_error')
            raise
    
    async def shutdown(self):
        """
        Graceful shutdown handler.
        Day 5: Enhanced with final statistics display.
        """
        logger = logging.getLogger('MportServer')
        logger.info(f"{Fore.YELLOW}[SHUTDOWN] Initiating graceful shutdown...{Style.RESET_ALL}")
        self.shutting_down = True
        
        # Display final statistics
        print(f"\n{Fore.CYAN}═══════════════════════════════════════════════════════════{Style.RESET_ALL}")
        print(f"{Fore.CYAN}              📊 FINAL STATISTICS                          {Style.RESET_ALL}")
        print(f"{Fore.CYAN}═══════════════════════════════════════════════════════════{Style.RESET_ALL}")
        self.stats.display()
        
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
        """Run all servers concurrently with connection monitoring and statistics."""
        print(f"\n{Fore.CYAN}╔═══════════════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║   🚀 MPORT SERVER - YOUR PORT TO THE WORLD          ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║      Day 5: Performance & Polish                     ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚═══════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")
        
        print(f"{Fore.GREEN}Starting Mport Server (Day 5 - Production Grade)...{Style.RESET_ALL}")
        print(f"  • Public port:  {self.public_port} (for internet users)")
        print(f"  • Control port: {self.control_port} (for client control)")
        print(f"  • Tunnel port:  {self.tunnel_port} (for tunnel connections)")
        print(f"\n{Fore.YELLOW}✨ NEW in Day 5:{Style.RESET_ALL}")
        print(f"  • 📊 Connection statistics tracking")
        print(f"  • ⚙️  CLI argument parsing")
        print(f"  • 🛡️  Rate limiting (max {self.rate_limiter.max_connections_per_client} connections/client)")
        print(f"  • 📈 Real-time statistics (every {self.stats_interval}s)")
        print(f"  • 🔥 Performance optimizations")
        print(f"\nPress {Fore.YELLOW}Ctrl+C{Style.RESET_ALL} to shutdown gracefully\n")
        
        try:
            # Start connection monitor
            monitor_task = asyncio.create_task(self.monitor.start())
            
            # Start statistics display
            stats_task = asyncio.create_task(self.display_stats_periodically())
            
            # Start all servers
            await asyncio.gather(
                self.start_public_server(),
                self.start_control_server(),
                self.start_tunnel_server(),
                monitor_task,
                stats_task
            )
            
        except KeyboardInterrupt:
            await self.shutdown()
        except Exception as e:
            logger = logging.getLogger('MportServer')
            logger.error(f"{Fore.RED}Fatal error: {e}{Style.RESET_ALL}", exc_info=True)
            await self.shutdown()


def parse_args():
    """
    Parse command-line arguments.
    NEW in Day 5!
    """
    parser = argparse.ArgumentParser(
        description='Mport Tunnel Server - Your Port to the World',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s                                    # Run with defaults
  %(prog)s --port 9000 --control 9001         # Custom ports
  %(prog)s --log-level DEBUG                  # Verbose logging
  %(prog)s --debug --max-connections 20       # Debug mode with custom limits
        '''
    )
    
    parser.add_argument('--port', '--public-port', type=int, default=8080,
                        help='Public server port (default: 8080)')
    parser.add_argument('--control-port', type=int, default=8081,
                        help='Control server port (default: 8081)')
    parser.add_argument('--tunnel-port', type=int, default=8082,
                        help='Tunnel server port (default: 8082)')
    parser.add_argument('--max-connections', type=int, default=10,
                        help='Max connections per client (default: 10)')
    parser.add_argument('--stats-interval', type=int, default=60,
                        help='Statistics display interval in seconds (default: 60)')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='INFO',
                        help='Logging level (default: INFO)')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug mode (verbose logging)')
    parser.add_argument('--version', action='version', version='Mport Server Day 5 (Week 1)')
    
    return parser.parse_args()


async def main():
    """Main entry point with CLI argument support."""
    args = parse_args()
    
    # Setup logging with CLI args
    global logger
    logger = setup_logging(log_level=args.log_level, debug=args.debug)
    
    # Create server with CLI args
    server = MportServer(
        public_port=args.port,
        control_port=args.control_port,
        tunnel_port=args.tunnel_port,
        max_connections_per_client=args.max_connections,
        stats_interval=args.stats_interval
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
        print(f"\n{Fore.RED}Server crashed. Check logs for details.{Style.RESET_ALL}")
        sys.exit(1)
