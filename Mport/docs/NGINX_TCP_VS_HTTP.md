# Nginx Configuration: HTTP vs TCP Stream

## 🚨 THE CRITICAL PROBLEM YOU IDENTIFIED

**You are 100% CORRECT!** The original nginx.conf has a fatal protocol mismatch.

---

## ❌ ORIGINAL (BROKEN) - nginx.conf

```nginx
location /api/control {
    proxy_pass http://mport_control;  # ❌ SENDS HTTP REQUESTS
}
```

### What Happens:

```
Client → HTTPS → Nginx → HTTP proxy_pass → Your Server

Nginx sends:
    GET /api/control HTTP/1.1
    Host: mport.app
    Connection: keep-alive
    ...

Your server expects:
    MPCTRL\n
    (raw TCP, NOT HTTP!)

Result: ❌ 502 Bad Gateway or timeout
```

---

## ✅ SOLUTION 1: TCP Stream Proxy (nginx-stream.conf)

**Best for Week 2** - Zero code changes needed!

```nginx
stream {
    server {
        listen 8091 ssl;  # TLS-wrapped TCP
        proxy_pass localhost:8081;  # Forward to your raw TCP
    }
}
```

### Architecture:

```
┌─────────────────────────────────────────────────────────┐
│              TCP STREAM PROXY (CORRECT!)                │
└─────────────────────────────────────────────────────────┘

Client → TLS (8091) → Nginx (stream module) → Raw TCP (8081) → Your Server

Client sends:
    MPCTRL\n  (wrapped in TLS)
    
Nginx unwraps TLS:
    MPCTRL\n  (forwards as-is)
    
Your server receives:
    MPCTRL\n  ✅ CORRECT!

Result: ✅ Works perfectly!
```

### Ports:

| External (HTTPS) | Internal (TCP) | Purpose |
|------------------|----------------|---------|
| 8091 | 8081 | Control connections |
| 8092 | 8082 | Tunnel data |
| 8090 | 8080 | Public/user connections |

### Client Connection:

```python
# Client connects to HTTPS port (TLS-wrapped TCP)
server_host = "mport.app"
server_port = 8091  # Not 8081!

# Nginx handles TLS, forwards raw TCP to 8081
# Your protocol works unchanged!
```

---

## ✅ SOLUTION 2: WebSocket Proxy (Week 3+)

**Future** - Requires code changes but more HTTP-friendly.

### Change your protocol to WebSocket:

```python
# server/tunnel_server_websocket.py (Week 3)
import websockets

async def control_handler(websocket, path):
    # Receive WebSocket messages
    msg = await websocket.recv()
    
    # Parse JSON (instead of raw "MPCTRL\n")
    data = json.loads(msg)
    if data["type"] == "HANDSHAKE":
        # Handle connection
        ...
```

### Nginx config:

```nginx
location /api/control {
    proxy_pass http://localhost:8081;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;  # WebSocket upgrade
    proxy_set_header Connection "upgrade";
}
```

### Architecture:

```
Client → HTTPS → Nginx → WebSocket → Your Server (modified)

All HTTP-based, firewall-super-friendly!
```

---

## 📊 Comparison

| Approach | Week | Code Changes | Firewall | Complexity |
|----------|------|--------------|----------|------------|
| **TCP Stream** | 2 | ✅ None | Good | Low |
| **WebSocket** | 3 | ❌ Major | Excellent | Medium |
| **Original (broken)** | - | - | ❌ Crashes | - |

---

## 🚀 Recommended Implementation

### Week 2: TCP Stream (nginx-stream.conf)

**Why:**
- ✅ No code changes (your 2,016 lines stay intact)
- ✅ TLS encryption (HTTPS)
- ✅ Production-ready today
- ✅ Simple configuration

**Limitations:**
- ⚠️ Uses non-standard ports (8090-8092)
- ⚠️ Some strict firewalls block non-443 ports
- ⚠️ Can't use HTTP load balancers

### Week 3: Add WebSocket (Optional)

**Why:**
- ✅ Standard port 443 only
- ✅ Works through ANY firewall
- ✅ HTTP-based (easier debugging)
- ✅ Browser client possible

**Trade-offs:**
- ❌ Requires rewriting protocol layer
- ❌ More complex (WebSocket framing)
- ❌ Week of development time

---

## 🔧 How to Deploy

### Use nginx-stream.conf (Fixed version):

```bash
# On VPS
sudo cp nginx-stream.conf /etc/nginx/nginx.conf

# Test config
sudo nginx -t

# Restart
sudo systemctl restart nginx

# Your Python code runs UNCHANGED on 8080-8082
sudo systemctl start mport
```

### Update client connection:

```python
# client/tunnel_client.py
# Change port from 8081 to 8091 (HTTPS-wrapped)

server_port = 8091  # External HTTPS port
# Nginx forwards to internal 8081
```

---

## 📝 Summary

### Your Discovery:
✅ **Correct!** Original nginx.conf would crash with protocol mismatch.

### The Fix:
✅ Use `stream` module instead of `http proxy_pass`

### Result:
```
Old: HTTP proxy → Raw TCP server = ❌ CRASH
New: TLS stream → Raw TCP server = ✅ WORKS!
```

---

## 🎓 Key Learning

**HTTP Reverse Proxy ≠ TCP Proxy**

- `http { proxy_pass }` = HTTP-to-HTTP (Layer 7)
- `stream { proxy_pass }` = TCP-to-TCP (Layer 4)

Your server speaks **custom TCP protocol**, so you need **stream**, not **http proxy_pass**!

---

**Great catch! This would have been a deployment blocker!** 🎯
