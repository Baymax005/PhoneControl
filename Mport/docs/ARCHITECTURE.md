# 🏗️ Mport Architecture Documentation

**Version:** Week 1 (Production)  
**Last Updated:** November 2, 2025  
**Status:** Complete & Tested

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [High-Level Architecture](#high-level-architecture)
3. [Component Details](#component-details)
4. [Data Flow](#data-flow)
5. [Protocol Specification](#protocol-specification)
6. [Class Structure](#class-structure)
7. [Deployment Architecture](#deployment-architecture)
8. [Performance Characteristics](#performance-characteristics)
9. [Security Model](#security-model)
10. [Scalability & Limits](#scalability--limits)

---

## 🎯 System Overview

### What is Mport?

**Mport** is a production-grade TCP tunneling service that enables remote access to local services through firewall and NAT. It creates secure tunnels that allow users to access devices (specifically Android phones via ADB) from anywhere in the world.

### Core Concepts

```
┌─────────────────────────────────────────────────────────────────┐
│                     TUNNELING CONCEPT                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  WITHOUT MPORT:                                                 │
│  ──────────────                                                 │
│  Internet User → [FIREWALL/NAT] ✗ Can't reach → Phone@Home     │
│                                                                 │
│  WITH MPORT:                                                    │
│  ──────────                                                     │
│  Internet User → Mport Server → Mport Client → Phone@Home ✓    │
│                                                                 │
│  The tunnel bypasses NAT and firewall restrictions!            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Key Features (Week 1)

- ✅ **3-port architecture** (public, control, tunnel)
- ✅ **Persistent connections** (24/7 capable)
- ✅ **Multiple simultaneous tunnels** (queue-based distribution)
- ✅ **Real-time statistics** (connections, bytes, errors, uptime)
- ✅ **Rate limiting** (prevent abuse)
- ✅ **Auto-recovery** (exponential backoff reconnection)
- ✅ **Connection monitoring** (health checks every 30s)
- ✅ **Comprehensive logging** (console + file)
- ✅ **CLI configuration** (15+ options)

---

## 🏛️ High-Level Architecture

### System Topology

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         MPORT SYSTEM TOPOLOGY                              │
└────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────────────────┐
                    │      INTERNET / NETWORK         │
                    └─────────────────────────────────┘
                                   │
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ▼                          ▼                          ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│  ADB Users    │         │  HTTP Users   │         │  TCP Users    │
│  (Developers) │         │  (Browsers)   │         │  (Apps)       │
└───────────────┘         └───────────────┘         └───────────────┘
        │                          │                          │
        └──────────────────────────┼──────────────────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │      MPORT SERVER            │
                    │  (localhost / VPS future)    │
                    │                              │
                    │  ┌────────────────────────┐  │
                    │  │   Port 8080 (Public)   │  │ ◄── Users connect here
                    │  └────────────────────────┘  │
                    │  ┌────────────────────────┐  │
                    │  │   Port 8081 (Control)  │  │ ◄── Clients register here
                    │  └────────────────────────┘  │
                    │  ┌────────────────────────┐  │
                    │  │   Port 8082 (Tunnel)   │  │ ◄── Data forwarding
                    │  └────────────────────────┘  │
                    │                              │
                    │  Core Components:            │
                    │  • Statistics Tracker        │
                    │  • Rate Limiter              │
                    │  • Connection Monitor        │
                    │  • Client Registry           │
                    └──────────────────────────────┘
                                   │
                                   │ Control + Tunnel
                                   │ (Persistent)
                                   ▼
                    ┌──────────────────────────────┐
                    │     MPORT CLIENT             │
                    │     (Your PC)                │
                    │                              │
                    │  • Control Connection        │
                    │  • Tunnel Creator            │
                    │  • Auto-Reconnect            │
                    │  • Heartbeat (PING/PONG)     │
                    └──────────────────────────────┘
                                   │
                                   │ Local Network
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │     LOCAL SERVICE            │
                    │     (Android Phone)          │
                    │                              │
                    │  Phone: BE2029               │
                    │  IP: 192.168.100.148:5555    │
                    │  ADB Daemon Listening        │
                    └──────────────────────────────┘
```

### Network Layers

```
┌────────────────────────────────────────────────────────────────┐
│                    OSI MODEL MAPPING                           │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Layer 7 (Application):  ADB Protocol, HTTP                   │
│                           ↓                                    │
│  Layer 5-6 (Session):     Mport Protocol (JSON messages)      │
│                           ↓                                    │
│  Layer 4 (Transport):     TCP (asyncio streams)               │
│                           ↓                                    │
│  Layer 3 (Network):       IP (IPv4)                           │
│                           ↓                                    │
│  Layer 1-2 (Physical):    Ethernet / WiFi                     │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Component Details

### 1. Server Components

#### **MportServer (Main Class)**

```python
class MportServer:
    """
    Main server orchestrator.
    Manages 3 async TCP servers and coordinates all operations.
    """
    
    # State Management
    clients: dict           # {client_id: ClientInfo}
    active_tunnels: dict    # {tunnel_id: TunnelInfo}
    shutting_down: bool     # Graceful shutdown flag
    
    # Components
    stats: Statistics           # Metrics tracker
    rate_limiter: RateLimiter   # Abuse prevention
    monitor: ConnectionMonitor  # Health checks
    
    # Configuration
    public_port: int = 8080     # User connections
    control_port: int = 8081    # Client registration
    tunnel_port: int = 8082     # Data forwarding
```

**Responsibilities:**
- Start/stop 3 async servers
- Accept connections on all 3 ports
- Route traffic between users and clients
- Coordinate tunnel creation
- Handle graceful shutdown

**Key Methods:**
```python
async def start():
    """Start all 3 servers concurrently"""
    
async def handle_public_connection(reader, writer):
    """
    Handle incoming user connection.
    1. Check if clients available
    2. Check rate limits
    3. Request tunnel from client
    4. Wait for tunnel connection
    5. Start bidirectional forwarding
    """
    
async def handle_control_connection(reader, writer):
    """
    Handle persistent client control connection.
    1. Receive handshake
    2. Register client
    3. Send ACK with client_id
    4. Keep alive with PING/PONG
    5. Listen for STATS_REQUEST
    """
    
async def handle_tunnel_connection(reader, writer):
    """
    Handle tunnel data connection.
    1. Receive tunnel registration (JSON)
    2. Validate client_id
    3. Add to client's tunnel queue
    4. Used for data forwarding
    """
    
async def forward_data(src_reader, dst_writer, label):
    """
    Bidirectional data forwarding.
    1. Read from source
    2. Write to destination
    3. Track bytes in statistics
    4. Handle errors gracefully
    """
```

#### **Statistics Class**

```python
class Statistics:
    """
    Real-time metrics tracking and display.
    Thread-safe counters for all server operations.
    """
    
    # Counters
    start_time: datetime
    total_connections: int
    active_connections: int
    peak_connections: int
    total_bytes_sent: int
    total_bytes_received: int
    total_tunnels_created: int
    total_clients: int
    errors: defaultdict(int)  # {error_type: count}
    connection_history: list  # Last 100 connections
```

**Features:**
- Human-readable byte formatting (KB, MB, GB, TB)
- Connection rate calculation (per hour)
- Uptime tracking
- Error categorization
- Real-time display with colorized output

**Display Output:**
```
╔═══════════════════════════════════════════════════════╗
║              📊 MPORT STATISTICS                     ║
╚═══════════════════════════════════════════════════════╝

⏱️  Uptime: 0:15:32

📡 Connections:
   Total: 50 | Active: 3 | Peak: 8
   Rate: 193.5/hour

🚇 Tunnels:
   Created: 45

👥 Clients:
   Registered: 2

📊 Data Transfer:
   Sent: 1.23 MB | Received: 2.45 MB

❌ Errors: 0
```

#### **RateLimiter Class**

```python
class RateLimiter:
    """
    Prevent abuse and DoS attacks.
    Per-client connection and tunnel rate limits.
    """
    
    max_connections_per_client: int = 10
    max_tunnels_per_minute: int = 60
    
    # Tracking
    client_connections: defaultdict(int)
    tunnel_timestamps: defaultdict(list)
```

**Algorithms:**
```python
# Connection Limit Check:
if connections[client_id] >= MAX_CONNECTIONS:
    return False, "Max connections exceeded"

# Tunnel Rate Limit (Sliding Window):
now = datetime.now()
minute_ago = now - timedelta(minutes=1)
recent_tunnels = [ts for ts in timestamps if ts > minute_ago]
if len(recent_tunnels) >= MAX_TUNNELS_PER_MINUTE:
    return False, "Rate limit exceeded"
```

**Protection Against:**
- Connection flooding (max 10 per client)
- Tunnel creation spam (max 60/minute)
- Resource exhaustion attacks
- Accidental infinite loops

#### **ConnectionMonitor Class**

```python
class ConnectionMonitor:
    """
    Health monitoring and auto-cleanup.
    Runs every 30 seconds to detect dead connections.
    """
    
    check_interval: int = 30  # seconds
```

**Health Check Process:**
```
1. Iterate all registered clients
2. Check writer.is_closing()
3. Calculate uptime
4. Detect stale connections
5. Cleanup dead clients:
   - Close writer
   - Remove from registry
   - Update statistics
   - Unregister from rate limiter
```

---

### 2. Client Components

#### **MportClient (Main Class)**

```python
class MportClient:
    """
    Persistent tunnel client.
    Maintains control connection and creates tunnels on-demand.
    """
    
    # Configuration
    server_host: str = "localhost"
    server_port: int = 8081  # Control port
    tunnel_port: int = 8082
    local_host: str = "192.168.100.148"
    local_port: int = 5555
    
    # State
    client_id: str          # Assigned by server
    running: bool
    reconnect_delay: int    # Exponential backoff
```

**Key Methods:**
```python
async def start():
    """
    Main entry point.
    1. Start control connection
    2. Start tunnel listener
    3. Handle reconnection on failure
    """
    
async def control_connection():
    """
    Persistent control connection to server.
    1. Send handshake (MPCTRL)
    2. Receive ACK with client_id
    3. Listen for server messages:
       - PING → respond PONG
       - STATS → send statistics
    4. Auto-reconnect on disconnect
    """
    
async def listen_for_tunnels():
    """
    Listen on control connection for tunnel requests.
    When server needs tunnel:
    1. Create new connection to tunnel_port
    2. Send tunnel registration (JSON with client_id)
    3. Forward data between server and local service
    """
    
async def reconnect():
    """
    Exponential backoff reconnection.
    Delays: 5s → 10s → 20s → 40s → 60s (max)
    """
```

#### **Connection Flow (Client Side)**

```
┌─────────────────────────────────────────────────────────────┐
│              CLIENT CONNECTION LIFECYCLE                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. START                                                   │
│     ↓                                                       │
│  2. Connect to server:8081 (control)                       │
│     ↓                                                       │
│  3. Send handshake: "MPCTRL\n"                             │
│     ↓                                                       │
│  4. Receive ACK with client_id                             │
│     ↓                                                       │
│  5. PERSISTENT LOOP:                                        │
│     │                                                       │
│     ├─► Wait for server message (60s timeout)              │
│     │                                                       │
│     ├─► If PING received → send PONG                       │
│     │                                                       │
│     ├─► If STATS_REQUEST → send statistics                 │
│     │                                                       │
│     ├─► If timeout → server sends PING                     │
│     │                                                       │
│     ├─► If 3 PINGs fail → disconnect                       │
│     │                                                       │
│     └─► On disconnect → RECONNECT (exponential backoff)    │
│                                                             │
│  6. TUNNEL CREATION (parallel async task):                 │
│     │                                                       │
│     ├─► Listen on control connection                       │
│     │                                                       │
│     ├─► When tunnel needed:                                │
│     │   • Connect to server:8082                           │
│     │   • Send: {"type": "TUNNEL_REG", "client_id": ...}  │
│     │   • Start data forwarding                            │
│     │                                                       │
│     └─► Repeat for each tunnel request                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Data Flow

### Complete Request Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                    MPORT DATA FLOW (Step-by-Step)                    │
└──────────────────────────────────────────────────────────────────────┘

STEP 1: User Initiates Connection
──────────────────────────────────
   User (ADB)
      │
      │ adb connect localhost:8080
      │
      ▼
   [Server:8080]
      │
      ├─► Check: Any clients registered?
      │   NO → Send error, close
      │   YES → Continue
      │
      ├─► Check: Rate limit OK?
      │   NO → Send error, close
      │   YES → Continue
      │
      └─► Record statistics (connection count)


STEP 2: Server Requests Tunnel from Client
───────────────────────────────────────────
   [Server:8080]
      │
      │ Get first available client
      │
      ▼
   [Client Queue]
      │
      │ Signal: "Need tunnel for user"
      │ (via existing control connection)
      │
      ▼
   [Client]


STEP 3: Client Creates Tunnel
──────────────────────────────
   [Client]
      │
      ├─► Connect to Server:8082
      │
      ├─► Send registration:
      │   {
      │     "type": "TUNNEL_REG",
      │     "client_id": "client_173045",
      │     "timestamp": "2025-11-02T14:30:45"
      │   }
      │
      └─► Wait for pairing


STEP 4: Server Pairs Connections
─────────────────────────────────
   [Server:8082] receives tunnel
      │
      ├─► Validate client_id
      │
      ├─► Add to client's tunnel_queue
      │
      ▼
   [Server:8080] waiting for tunnel
      │
      ├─► Dequeue tunnel from client's queue
      │
      ├─► Pair: User(:8080) ↔ Tunnel(:8082)
      │
      └─► Record statistics (tunnel created)


STEP 5: Bidirectional Forwarding Begins
────────────────────────────────────────
   User(:8080) ←──────────────────→ Server ←──────────────────→ Client
      │                                                            │
      │                                                            │
      ▼                                                            ▼
   [Forward Loop 1]                                        [Forward Loop 2]
   User → Server → Tunnel                                 Tunnel → Client → Phone
      │              │                                        │              │
      │              │ Record bytes_sent                      │              │
      │              │                                        │              │
      │              └─► Data →                              ← Data ─────────┘
      │                                                        │
      └─────────────────── Continuous ───────────────────────┘


STEP 6: Connection Termination
───────────────────────────────
   Either side closes:
      │
      ├─► Forward loops detect EOF
      │
      ├─► Close both connections gracefully
      │
      ├─► Update statistics:
      │   • Record disconnection
      │   • Decrement active_connections
      │
      └─► Cleanup resources
```

### Data Packet Journey

```
┌────────────────────────────────────────────────────────────────┐
│                  PACKET-LEVEL DATA FLOW                        │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Example: ADB command "getprop ro.product.model"              │
│                                                                │
│  1. User Types:                                               │
│     $ adb -s localhost:8080 shell getprop ro.product.model    │
│                                                                │
│  2. ADB Client → Server:8080                                  │
│     Packet: [ADB Protocol Header][Command Payload]            │
│     Size: ~100 bytes                                          │
│     Time: T+0ms                                               │
│                                                                │
│  3. Server:8080 → Server:8082 (internal)                      │
│     Forwarding through tunnel connection                      │
│     Time: T+5ms (queue wait + context switch)                 │
│                                                                │
│  4. Server:8082 → Client                                      │
│     Over network (local or internet)                          │
│     Time: T+10ms (local) or T+50ms (internet)                 │
│                                                                │
│  5. Client → Phone:5555                                       │
│     Local network connection                                  │
│     Time: T+15ms                                              │
│                                                                │
│  6. Phone ADB Daemon Processes Command                        │
│     Time: T+20ms                                              │
│                                                                │
│  7. Response: "BE2029" (Reverse Path)                         │
│     Phone → Client → Server → User                            │
│     Time: T+40ms                                              │
│                                                                │
│  Total Round Trip: ~40-100ms                                  │
│  (Depends on network latency)                                 │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## 📡 Protocol Specification

### Control Protocol (Port 8081)

#### **Client → Server (Handshake)**

```
Message: "MPCTRL\n"
Format: Plain text with newline
Purpose: Identify as Mport client
```

#### **Server → Client (ACK)**

```json
{
  "type": "ACK",
  "client_id": "client_173045",
  "message": "Control connection established",
  "server_version": "Day5",
  "features": ["statistics", "rate_limiting", "cli_args"]
}
```

#### **Server → Client (PING)**

```
Message: "PING\n"
Format: Plain text with newline
Purpose: Keep-alive check
Expected Response: "PONG\n"
Frequency: Every 60s if no data
Timeout: 3 failed PINGs → disconnect
```

#### **Client → Server (PONG)**

```
Message: "PONG\n"
Format: Plain text with newline
Purpose: Acknowledge keep-alive
```

#### **Client → Server (STATS_REQUEST)**

```
Message: "STATS_REQUEST\n"
Format: Plain text with newline
Purpose: Request server statistics
```

#### **Server → Client (STATS)**

```json
{
  "type": "STATS",
  "data": {
    "uptime": "0:15:32",
    "total_connections": 50,
    "active_connections": 3,
    "peak_connections": 8,
    "total_tunnels": 45,
    "total_clients": 2,
    "bytes_sent": "1.23 MB",
    "bytes_received": "2.45 MB",
    "total_errors": 0,
    "connections_per_hour": "193.5"
  }
}
```

### Tunnel Protocol (Port 8082)

#### **Client → Server (Tunnel Registration)**

```json
{
  "type": "TUNNEL_REG",
  "client_id": "client_173045",
  "timestamp": "2025-11-02T14:30:45.123456"
}
```

**Validation:**
- `client_id` must match registered client
- Timestamp within 5 minutes of current time
- JSON must be valid

#### **Data Forwarding**

```
Format: Raw TCP stream (no framing)
Protocol: Application-specific (ADB, HTTP, etc.)
Encoding: Binary transparent (8-bit clean)
```

**Forwarding Rules:**
1. Read up to 8KB chunks
2. Write immediately to destination
3. Track bytes in statistics
4. Handle errors gracefully (log + close)
5. No buffering (minimize latency)

---

## 🏛️ Class Structure

### Server Class Hierarchy

```
MportServer (main orchestrator)
├── Statistics (metrics tracking)
│   ├── record_connection()
│   ├── record_disconnection()
│   ├── record_bytes()
│   ├── record_tunnel()
│   ├── record_client()
│   ├── record_error()
│   └── get_summary()
│
├── RateLimiter (abuse prevention)
│   ├── check_client_limit()
│   ├── check_tunnel_rate()
│   ├── register_connection()
│   └── unregister_connection()
│
├── ConnectionMonitor (health checks)
│   ├── start()
│   ├── check_connections()
│   └── cleanup_client()
│
└── Methods:
    ├── start()
    ├── handle_public_connection()
    ├── handle_control_connection()
    ├── handle_tunnel_connection()
    ├── forward_data()
    └── shutdown()
```

### Client Class Hierarchy

```
MportClient
├── control_connection()
│   ├── Send handshake
│   ├── Receive ACK
│   ├── PING/PONG loop
│   └── Auto-reconnect
│
├── listen_for_tunnels()
│   ├── Create tunnel connection
│   ├── Register with server
│   └── Forward data
│
├── handle_tunnel()
│   ├── Connect to local service
│   ├── Bidirectional forwarding
│   └── Error handling
│
└── reconnect()
    └── Exponential backoff
```

### Data Structures

```python
# Server State
clients = {
    "client_173045": {
        "reader": StreamReader,
        "writer": StreamWriter,
        "addr": ("192.168.1.100", 54321),
        "tunnel_queue": AsyncQueue(),
        "connected_at": datetime(2025, 11, 2, 14, 30, 0)
    }
}

active_tunnels = {
    "tunnel_abc123": {
        "user_addr": ("203.0.113.1", 12345),
        "client_id": "client_173045",
        "created_at": datetime(2025, 11, 2, 14, 30, 15)
    }
}

# Statistics State
stats = {
    "start_time": datetime(2025, 11, 2, 14, 0, 0),
    "total_connections": 50,
    "active_connections": 3,
    "peak_connections": 8,
    "total_bytes_sent": 1290240,  # bytes
    "total_bytes_received": 2568960,
    "total_tunnels_created": 45,
    "total_clients": 2,
    "errors": {
        "tunnel_timeout": 2,
        "connection_limit": 1,
        "invalid_handshake": 0
    }
}

# Rate Limiter State
rate_limiter = {
    "client_connections": {
        "client_173045": 3,
        "client_174512": 5
    },
    "tunnel_timestamps": {
        "client_173045": [
            datetime(2025, 11, 2, 14, 29, 50),
            datetime(2025, 11, 2, 14, 30, 15),
            datetime(2025, 11, 2, 14, 30, 45)
        ]
    }
}
```

---

## 🚀 Deployment Architecture

### Current Deployment (Week 1)

```
┌──────────────────────────────────────────────┐
│         LOCAL DEVELOPMENT SETUP              │
├──────────────────────────────────────────────┤
│                                              │
│  Machine: Your PC (Windows)                 │
│  Network: Home WiFi                         │
│                                              │
│  ┌────────────────────────────────────┐     │
│  │  Terminal 1: Server                │     │
│  │  python server/tunnel_server.py    │     │
│  │  Ports: 8080, 8081, 8082          │     │
│  │  Listening on: 0.0.0.0            │     │
│  └────────────────────────────────────┘     │
│                                              │
│  ┌────────────────────────────────────┐     │
│  │  Terminal 2: Client                │     │
│  │  python client/quick_start.py      │     │
│  │  Connects to: localhost:8081       │     │
│  │  Local service: 192.168.100.148    │     │
│  └────────────────────────────────────┘     │
│                                              │
│  ┌────────────────────────────────────┐     │
│  │  Terminal 3: ADB User              │     │
│  │  adb connect localhost:8080        │     │
│  │  adb shell getprop ...             │     │
│  └────────────────────────────────────┘     │
│                                              │
└──────────────────────────────────────────────┘
```

### Planned Deployment (Week 2+)

```
┌───────────────────────────────────────────────────────────────────┐
│                    PRODUCTION DEPLOYMENT                          │
└───────────────────────────────────────────────────────────────────┘

                         ┌─────────────────┐
                         │   INTERNET      │
                         └────────┬────────┘
                                  │
                      ┌───────────┴───────────┐
                      │                       │
                      ▼                       ▼
              ┌──────────────┐        ┌──────────────┐
              │  DNS Server  │        │  CDN         │
              │  mport.app   │        │  (Optional)  │
              └──────┬───────┘        └──────────────┘
                     │
                     │ A Record → VPS IP
                     │
                     ▼
         ┌────────────────────────────┐
         │   DigitalOcean VPS         │
         │   Bangalore, India         │
         │   Ubuntu 22.04 LTS         │
         │   $6/month (1GB RAM)       │
         ├────────────────────────────┤
         │                            │
         │  ┌──────────────────────┐  │
         │  │   Nginx (Reverse    │  │
         │  │   Proxy + SSL)      │  │
         │  │   Port 443 → 8080   │  │
         │  └──────────────────────┘  │
         │            │               │
         │            ▼               │
         │  ┌──────────────────────┐  │
         │  │  Mport Server        │  │
         │  │  (systemd service)   │  │
         │  │  Ports: 8080-8082    │  │
         │  └──────────────────────┘  │
         │            │               │
         │  ┌──────────────────────┐  │
         │  │  PostgreSQL          │  │
         │  │  (users, tunnels)    │  │
         │  └──────────────────────┘  │
         │            │               │
         │  ┌──────────────────────┐  │
         │  │  Logs Directory      │  │
         │  │  /var/log/mport/     │  │
         │  └──────────────────────┘  │
         │                            │
         └────────────────────────────┘
                     │
                     │ Internet
                     │
                     ▼
         ┌────────────────────────────┐
         │   Your PC (Client)         │
         │   Windows / Linux / Mac    │
         ├────────────────────────────┤
         │  Mport Client              │
         │  Connects to: mport.app    │
         └────────────────────────────┘
                     │
                     │ Local Network
                     │
                     ▼
         ┌────────────────────────────┐
         │   Phone (192.168.x.x)      │
         │   ADB Daemon :5555         │
         └────────────────────────────┘
```

### Docker Deployment (Future)

```yaml
# docker-compose.yml

version: '3.8'

services:
  mport-server:
    build: ./server
    ports:
      - "8080:8080"
      - "8081:8081"
      - "8082:8082"
    environment:
      - LOG_LEVEL=INFO
      - STATS_INTERVAL=60
      - MAX_CONNECTIONS=10
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - mport-network

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=mport
      - POSTGRES_USER=mport
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - mport-network

  redis:
    image: redis:7-alpine
    networks:
      - mport-network

volumes:
  postgres-data:

networks:
  mport-network:
    driver: bridge
```

---

## ⚡ Performance Characteristics

### Measured Performance (Week 1 Stress Tests)

```
┌──────────────────────────────────────────────────────────────┐
│              STRESS TEST RESULTS (Oct 25, 2025)              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Test 1: Rapid Connections (50 cycles)                      │
│  ────────────────────────────────────                       │
│  Success Rate: 50/50 (100%)                                 │
│  Average Time: 9.71ms per connection                        │
│  Min Time: 0.63ms                                           │
│  Max Time: 28.14ms                                          │
│  Result: ✅ PASS - Excellent connection speed               │
│                                                              │
│  Test 2: Concurrent Commands (20 parallel)                  │
│  ───────────────────────────────────────                    │
│  Success Rate: 20/20 (100%)                                 │
│  Average Response: 191.17ms                                 │
│  Commands: ADB getprop, dumpsys battery                     │
│  Result: ✅ PASS - Handles concurrency well                 │
│                                                              │
│  Test 3: Data Throughput                                    │
│  ─────────────────────────                                  │
│  Total Transferred: 131,244 bytes                           │
│  Average Throughput: 143.2 KB/s                             │
│  Largest Transfer: 72,198 bytes (process list)              │
│  Result: ✅ PASS - Adequate for ADB operations              │
│                                                              │
│  Test 4: Sustained Load (30 seconds)                        │
│  ──────────────────────────────────                         │
│  Total Commands: 32                                         │
│  Success Rate: 32/32 (100%)                                 │
│  Commands/Second: 1.0                                       │
│  Errors: 0                                                  │
│  Result: ✅ PASS - Rock solid stability                     │
│                                                              │
│  Test 5: Connection Recovery                                │
│  ─────────────────────────────                              │
│  Invalid Command Recovery: ✅ PASS                           │
│  Rapid Burst (10 commands): 10/10 (100%)                   │
│  Result: ✅ PASS - Excellent resilience                     │
│                                                              │
│  OVERALL: 5/5 tests passed (100%) 🔥                        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Performance Bottlenecks

```
Component                 | Latency    | Bottleneck Factor
─────────────────────────┼────────────┼──────────────────────
TCP Connection Setup      | ~5-10ms    | Network RTT
Control Message Exchange  | ~1-2ms     | Python async overhead
Tunnel Creation          | ~10-20ms   | Queue wait + connection
Data Forwarding (8KB)    | ~0.5-1ms   | Memory copy + syscall
Statistics Recording     | ~0.01ms    | Dict update (O(1))
Rate Limit Check         | ~0.01ms    | Dict lookup (O(1))
Connection Monitor       | 30s cycle  | Sleep interval
─────────────────────────┴────────────┴──────────────────────

Critical Path (User Request → Response):
  Network (user → server): ~10-50ms
  Queue wait: ~5-10ms
  Tunnel creation: ~10-20ms
  Forwarding: ~1-2ms
  Network (server → client): ~10-50ms
  Local network (client → phone): ~5-10ms
  Phone processing: ~10-50ms
  ─────────────────────────────────
  Total: ~51-192ms (typical: ~100ms)
```

### Scalability Projections

```
┌──────────────────────────────────────────────────────────────┐
│                    SCALABILITY ANALYSIS                      │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Current (Week 1 - Python, Local):                          │
│  ────────────────────────────────                           │
│  • Concurrent Connections: 20+ (tested)                     │
│  • Theoretical Max (Python): 100-500                        │
│  • Memory per Connection: ~50KB                             │
│  • CPU per Connection: ~0.1% (idle)                         │
│                                                              │
│  Projected (Week 2+ - VPS $6/mo):                           │
│  ──────────────────────────────────                         │
│  • VPS Specs: 1 vCPU, 1GB RAM                               │
│  • Max Connections: ~200-300                                │
│  • Memory Overhead: 512MB (OS) + 50KB×300 = ~650MB         │
│  • CPU Bottleneck: ~30-50 connections at 100% CPU          │
│                                                              │
│  Optimized (Week 4+ - Better VPS):                          │
│  ────────────────────────────────────                       │
│  • VPS Specs: 2 vCPU, 2GB RAM                               │
│  • Max Connections: ~500-1000                               │
│  • With Redis Caching: +50% performance                     │
│  • With Load Balancer: Linear scaling                       │
│                                                              │
│  Golang Rewrite (Future):                                   │
│  ───────────────────────                                    │
│  • Same VPS (2 vCPU, 2GB): 5,000-10,000 connections        │
│  • Memory per Connection: ~10KB (5x less)                   │
│  • CPU per Connection: ~0.02% (5x less)                     │
│  • Throughput: 10x faster                                   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔒 Security Model

### Current Security (Week 1)

```
┌──────────────────────────────────────────────────────────────┐
│                   SECURITY FEATURES (WEEK 1)                 │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ✅ Implemented:                                             │
│  ───────────────                                             │
│  • Rate Limiting (10 conn/client, 60 tunnels/min)           │
│  • Connection Limits (prevent resource exhaustion)           │
│  • Input Validation (JSON parsing, client_id checks)        │
│  • Timeout Handling (5s handshake, 60s keepalive)           │
│  • Graceful Error Handling (no crashes)                     │
│  • Logging (audit trail)                                    │
│                                                              │
│  ❌ Not Implemented (Week 2+):                               │
│  ───────────────────────────                                 │
│  • TLS/SSL Encryption (plain TCP)                           │
│  • Authentication (no tokens)                                │
│  • Authorization (no user system)                            │
│  • Input Sanitization (SQL injection if DB added)           │
│  • DDoS Protection (basic rate limiting only)               │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Security Architecture (Week 2+)

```
┌──────────────────────────────────────────────────────────────┐
│              PLANNED SECURITY ARCHITECTURE                   │
└──────────────────────────────────────────────────────────────┘

Layer 1: Network Security
─────────────────────────
  ┌─────────────────────────────────────────┐
  │  Firewall (UFW)                         │
  │  • Allow: 22 (SSH), 443 (HTTPS)         │
  │  • Allow: 8080-8082 (Mport)             │
  │  • Deny: Everything else                │
  └─────────────────────────────────────────┘

Layer 2: Transport Security (TLS/SSL)
──────────────────────────────────────
  ┌─────────────────────────────────────────┐
  │  Let's Encrypt Certificate              │
  │  • Domain: mport.app                    │
  │  • TLS 1.3 (modern cipher suites)       │
  │  • Perfect Forward Secrecy (PFS)        │
  │  • Auto-renewal every 90 days           │
  └─────────────────────────────────────────┘

Layer 3: Application Security
──────────────────────────────
  ┌─────────────────────────────────────────┐
  │  Token-Based Authentication             │
  │  • User registers → gets auth token     │
  │  • Client sends token on connect        │
  │  • Server validates before accepting    │
  │  • Tokens expire after 30 days          │
  └─────────────────────────────────────────┘

Layer 4: Data Security
──────────────────────
  ┌─────────────────────────────────────────┐
  │  Database Security                      │
  │  • Password hashing (bcrypt, cost=12)   │
  │  • SQL injection prevention (ORM)       │
  │  • Regular backups (encrypted)          │
  │  • Minimal privileges principle         │
  └─────────────────────────────────────────┘

Layer 5: Rate Limiting & Abuse Prevention
──────────────────────────────────────────
  ┌─────────────────────────────────────────┐
  │  Multi-Tier Rate Limiting               │
  │  • Per IP: 100 requests/hour            │
  │  • Per User: 1000 tunnels/day           │
  │  • Global: 10,000 connections/hour      │
  │  • Dynamic blacklisting (abuse)         │
  └─────────────────────────────────────────┘
```

### Threat Model

```
┌──────────────────────────────────────────────────────────────┐
│                        THREAT MODEL                          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Threat 1: Unauthorized Access                              │
│  ─────────────────────────────                              │
│  Attack: Anyone can connect as client                        │
│  Impact: Resource theft, data interception                   │
│  Mitigation (Week 2): Token authentication                   │
│  Status: ❌ Vulnerable (no auth yet)                         │
│                                                              │
│  Threat 2: Man-in-the-Middle (MITM)                         │
│  ───────────────────────────────────                         │
│  Attack: Network eavesdropping                               │
│  Impact: Data theft (passwords, keys)                       │
│  Mitigation (Week 2): TLS/SSL encryption                    │
│  Status: ❌ Vulnerable (plain TCP)                           │
│                                                              │
│  Threat 3: Denial of Service (DoS)                          │
│  ──────────────────────────────                              │
│  Attack: Connection/tunnel flooding                          │
│  Impact: Service unavailable for others                     │
│  Mitigation (Week 1): Rate limiting ✅                       │
│  Status: ✅ Partially mitigated                              │
│                                                              │
│  Threat 4: Resource Exhaustion                              │
│  ─────────────────────────────                               │
│  Attack: Many slow connections                               │
│  Impact: Memory/CPU exhaustion                              │
│  Mitigation (Week 1): Connection limits ✅                   │
│  Status: ✅ Partially mitigated                              │
│                                                              │
│  Threat 5: Data Injection                                   │
│  ────────────────────────                                    │
│  Attack: Malicious payloads in forwarded data               │
│  Impact: Phone compromise                                   │
│  Mitigation: None (transparent forwarding)                  │
│  Status: ⚠️ Accepted risk (user responsibility)             │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 📈 Scalability & Limits

### Current Limits (Week 1)

```python
# Hard Limits (Configurable via CLI)
MAX_CONNECTIONS_PER_CLIENT = 10      # --max-connections
MAX_TUNNELS_PER_MINUTE = 60          # Rate limiter
PING_TIMEOUT = 60                    # seconds
MAX_PING_FAILURES = 3                # before disconnect
CONNECTION_CHECK_INTERVAL = 30       # seconds
HANDSHAKE_TIMEOUT = 5                # seconds
TUNNEL_WAIT_TIMEOUT = 10             # seconds

# Soft Limits (Performance-based)
CONCURRENT_CONNECTIONS = ~20-100     # Tested: 20, Theory: 100-500
DATA_CHUNK_SIZE = 8192               # 8KB per read
STATISTICS_DISPLAY_INTERVAL = 60     # seconds (configurable)

# System Limits (Python/OS)
FILE_DESCRIPTORS = 1024              # ulimit -n (default)
MEMORY_PER_CONNECTION = ~50KB        # Estimated
CONTEXT_SWITCHES = ~1000/sec         # Python asyncio
```

### Scaling Strategies

```
┌──────────────────────────────────────────────────────────────┐
│                     SCALING ROADMAP                          │
└──────────────────────────────────────────────────────────────┘

Phase 1: Vertical Scaling (Months 1-3)
───────────────────────────────────────
  Current: $6/mo VPS (1 vCPU, 1GB RAM)
  ↓
  Upgrade: $12/mo VPS (1 vCPU, 2GB RAM)
  Capacity: 100 → 300 concurrent users
  ↓
  Upgrade: $24/mo VPS (2 vCPU, 4GB RAM)
  Capacity: 300 → 500 concurrent users

Phase 2: Optimization (Months 4-6)
───────────────────────────────────
  • Add Redis caching (reduce DB load)
  • Optimize Python code (profile, fix bottlenecks)
  • Connection pooling
  • Lazy statistics (reduce overhead)
  • Batch operations
  Capacity: 500 → 1,000 concurrent users

Phase 3: Horizontal Scaling (Months 7-9)
─────────────────────────────────────────
  • Add load balancer (Nginx)
  • Multiple Mport servers (round-robin)
  • Shared PostgreSQL + Redis
  • Session affinity (sticky clients)
  Capacity: 1,000 → 5,000 concurrent users

Phase 4: Golang Rewrite (Months 10-12)
───────────────────────────────────────
  • Rewrite core in Go (optional)
  • 5-10x performance improvement
  • Lower memory footprint
  • Goroutines vs Python threads
  Capacity: 5,000 → 50,000 concurrent users
```

### Database Schema (Future)

```sql
-- Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    auth_token VARCHAR(64) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    max_tunnels INT DEFAULT 1,
    max_bandwidth_gb INT DEFAULT 10,
    tier VARCHAR(20) DEFAULT 'free' -- free, pro, business
);

-- Tunnels Table
CREATE TABLE tunnels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    name VARCHAR(100),
    port INT UNIQUE,
    subdomain VARCHAR(100) UNIQUE,
    status VARCHAR(20) DEFAULT 'active', -- active, stopped, paused
    created_at TIMESTAMP DEFAULT NOW(),
    last_used TIMESTAMP,
    bytes_sent BIGINT DEFAULT 0,
    bytes_received BIGINT DEFAULT 0,
    total_connections INT DEFAULT 0
);

-- Statistics Table (aggregated)
CREATE TABLE stats_hourly (
    id SERIAL PRIMARY KEY,
    hour TIMESTAMP NOT NULL,
    user_id UUID REFERENCES users(id),
    tunnel_id UUID REFERENCES tunnels(id),
    connections INT DEFAULT 0,
    bytes_sent BIGINT DEFAULT 0,
    bytes_received BIGINT DEFAULT 0,
    errors INT DEFAULT 0,
    UNIQUE(hour, user_id, tunnel_id)
);

-- Indexes for performance
CREATE INDEX idx_tunnels_user_id ON tunnels(user_id);
CREATE INDEX idx_tunnels_status ON tunnels(status);
CREATE INDEX idx_stats_hour ON stats_hourly(hour);
CREATE INDEX idx_stats_user ON stats_hourly(user_id);
```

---

## 📚 References & Resources

### Internal Documentation
- `README.md` - Project overview and features
- `TESTING.md` - Comprehensive test results
- `PROGRESS.md` - Development timeline
- `CHANGELOG.md` - Version history
- `ROADMAP.md` - 12-week development plan
- `BRANDING.md` - Brand identity and positioning

### External References
- **Python asyncio**: https://docs.python.org/3/library/asyncio.html
- **TCP/IP Sockets**: https://realpython.com/python-sockets/
- **ngrok Architecture**: https://ngrok.com/docs (inspiration)
- **frp Source Code**: https://github.com/fatedier/frp (Go implementation)
- **DigitalOcean Tutorials**: https://www.digitalocean.com/community/tutorials

### Similar Projects (Study)
- **frp** (Go) - Fast reverse proxy, mature codebase
- **inlets** (Go) - Kubernetes-native tunneling
- **bore** (Rust) - Simple TCP tunneling
- **localtunnel** (Node.js) - HTTP tunneling service

---

## 📊 Metrics & Monitoring

### Key Performance Indicators (KPIs)

```
Technical KPIs:
───────────────
• Uptime: Target 99.9% (8.76 hours downtime/year)
• Latency: Target <100ms (p95)
• Throughput: Target >100 KB/s per connection
• Connection Success Rate: Target >99%
• Error Rate: Target <0.1%

Business KPIs (Future):
──────────────────────
• Total Users: Track growth
• Active Users (DAU/MAU): Engagement metric
• Paid Conversion Rate: Target 5-10%
• Churn Rate: Target <5%/month
• Revenue: Track MRR (Monthly Recurring Revenue)
```

### Monitoring Dashboard (Future)

```
┌────────────────────────────────────────────────────────────┐
│              MPORT MONITORING DASHBOARD                    │
│              (Grafana + Prometheus)                        │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  System Health:                                            │
│  • CPU Usage: ████████░░ 80%                               │
│  • Memory: ██████░░░░ 60%                                  │
│  • Disk: ███░░░░░░░ 30%                                    │
│  • Network: ███████░░░ 70%                                 │
│                                                            │
│  Active Connections: 347 / 500                             │
│  Active Tunnels: 289                                       │
│  Registered Clients: 156                                   │
│                                                            │
│  Last 24 Hours:                                            │
│  • Total Requests: 45,678                                  │
│  • Data Transferred: 12.3 GB                               │
│  • Errors: 23 (0.05%)                                      │
│  • Avg Latency: 87ms                                       │
│                                                            │
│  Top Users (by bandwidth):                                 │
│  1. user_abc123: 2.1 GB                                    │
│  2. user_def456: 1.8 GB                                    │
│  3. user_ghi789: 1.2 GB                                    │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## 🔄 Upgrade Path

### Migration Strategy (Week 1 → Production)

```
Step 1: Configuration Migration
────────────────────────────────
  Current: CLI arguments only
  ↓
  Add: .env file support
  ↓
  Add: Config file (YAML/JSON)
  ↓
  Result: Flexible configuration management

Step 2: Database Integration
─────────────────────────────
  Current: In-memory state only
  ↓
  Add: SQLite for development
  ↓
  Add: PostgreSQL for production
  ↓
  Result: Persistent state across restarts

Step 3: Authentication Layer
─────────────────────────────
  Current: No authentication
  ↓
  Add: Token-based auth
  ↓
  Add: User registration/login
  ↓
  Result: Multi-user support

Step 4: Web Dashboard
─────────────────────
  Current: CLI only
  ↓
  Add: REST API (Flask)
  ↓
  Add: Web UI (React/Vue)
  ↓
  Result: User-friendly management

Step 5: Containerization
────────────────────────
  Current: Manual deployment
  ↓
  Add: Dockerfile
  ↓
  Add: docker-compose.yml
  ↓
  Result: One-command deployment

Step 6: CI/CD Pipeline
──────────────────────
  Current: Manual git push
  ↓
  Add: GitHub Actions workflow
  ↓
  Add: Automated tests
  ↓
  Add: Automated deployment
  ↓
  Result: Continuous delivery
```

---

## 🎓 Learning Path

### Skills Demonstrated

```
Architecture & Design:
──────────────────────
✓ Client-server architecture
✓ Multi-port design
✓ Queue-based distribution
✓ State management
✓ Protocol design
✓ Scalability planning

Python Programming:
───────────────────
✓ Asyncio (async/await)
✓ TCP socket programming
✓ Class-based design
✓ Error handling
✓ Logging
✓ CLI argument parsing
✓ Type hints (future)

DevOps:
───────
✓ Server deployment
✓ Process management
✓ Log management
✓ Monitoring (basics)
✓ Docker (future)
✓ CI/CD (future)

Networking:
───────────
✓ TCP/IP protocol
✓ Port forwarding
✓ Tunneling concepts
✓ NAT traversal
✓ Reverse proxy
✓ Load balancing (future)

Security:
─────────
✓ Rate limiting
✓ Input validation
✓ Error handling
✓ TLS/SSL (future)
✓ Authentication (future)
✓ Authorization (future)
```

---

## 📝 Conclusion

### Current State Summary

**Mport Week 1** is a fully functional, production-ready TCP tunneling service that demonstrates:

1. ✅ **Solid Architecture** - Clean 3-port design with clear separation of concerns
2. ✅ **Professional Code** - 2,016 lines of well-structured Python
3. ✅ **Real Testing** - 100% stress test pass rate with comprehensive metrics
4. ✅ **Production Features** - Statistics, rate limiting, monitoring, logging
5. ✅ **Complete Documentation** - 5 major docs totaling 2,500+ lines

### What Makes This Special

- **Not a Tutorial Clone** - Original architecture and design decisions
- **Real-World Testing** - Validated with actual Android phone (BE2029)
- **Professional Quality** - Error handling, logging, graceful shutdown
- **Comprehensive Docs** - Architecture, testing, progress tracking
- **Growth Potential** - Clear path from MVP to production scale

### Next Steps

**Immediate (Week 2):**
1. Deploy to DigitalOcean VPS
2. Add TLS/SSL encryption
3. Implement token authentication
4. Set up domain (mport.app)

**Near-term (Weeks 3-6):**
5. Multi-user support
6. PostgreSQL database
7. Web dashboard
8. Beta testing

**Long-term (Weeks 7-12):**
9. Advanced features (HTTP tunneling, custom domains)
10. Monitoring & alerts
11. CI/CD pipeline
12. Public launch

---

**Document Version:** 1.0  
**Last Updated:** November 2, 2025  
**Maintained By:** Muhammad (Baymax005)  
**Status:** Complete & Ready for Week 2

---

*Mport - Your Port to the World* 🚀
