# 🧪 Mport Testing Suite

## Overview

This directory contains automated stress tests for Mport Week 1 implementation.

## Files

### `stress_test.py` - Comprehensive Stress Test Suite
**Purpose**: Full stress testing of Mport tunnel system  
**Duration**: ~2 minutes  
**Tests**: 5 comprehensive tests

**What it tests:**
1. **Rapid Connections** (50 cycles) - Connection speed and stability
2. **Concurrent Commands** (20 parallel) - Multi-threading capability  
3. **Data Throughput** - Large data transfers
4. **Sustained Load** (30 seconds) - Long-term stability
5. **Connection Recovery** - Error resilience

**Usage:**
```bash
# Make sure server and client are running first!
python tests/stress_test.py
```

**Results:** ✅ 100% Pass Rate (5/5 tests passed)

## How to Run Tests

### Method 1: Manual (Recommended)

```powershell
# Terminal 1: Start server
python server/tunnel_server.py

# Terminal 2: Start client
python client/quick_start.py

# Terminal 3: Run tests using helper script
.\stress_test_manual.ps1
```

### Method 2: Direct Python

```powershell
# After server and client are running
python tests/stress_test.py
```

## Test Requirements

**Prerequisites:**
- ✅ Server running (`python server/tunnel_server.py`)
- ✅ Client running (`python client/quick_start.py`)
- ✅ Phone connected to WiFi (192.168.100.148:5555)
- ✅ ADB installed and accessible

**Environment:**
- Python 3.13+
- asyncio support
- PowerShell (for helper scripts)

## Test Results (October 25, 2025)

### Performance Metrics
- **Connection Speed**: 9.71ms average
- **Concurrent Capacity**: 20+ parallel commands
- **Data Throughput**: 143 KB/s average
- **Stability**: 100% uptime (30s sustained load)
- **Success Rate**: 100% (all tests passed)

### Status: ✅ PRODUCTION READY

Week 1 implementation passed all stress tests with perfect scores. System is:
- Fast (sub-10ms connections)
- Stable (zero crashes)
- Concurrent (handles 20+ parallel operations)
- Resilient (recovers from errors)

See `../TESTING.md` for detailed test results and analysis.

## Future Tests

Planned for Week 2+:
- Security testing (TLS/SSL)
- Authentication tests
- Multi-user scenarios
- VPS deployment validation
- Load balancing tests
