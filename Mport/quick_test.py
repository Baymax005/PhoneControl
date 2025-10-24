"""
Quick test script to verify Mport tunnel works.
This simulates what ADB would do.
"""

import socket
import sys

def test_tunnel():
    print("\n🧪 Testing Mport Tunnel...")
    print("Connecting to localhost:8080 (public port)...")
    
    try:
        # Connect to the tunnel's public port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(('localhost', 8080))
        
        print("✅ Connected to Mport server!")
        
        # Send test data
        test_message = b"HELLO MPORT TEST\n"
        print(f"📤 Sending: {test_message.decode().strip()}")
        sock.send(test_message)
        
        # Try to receive response
        print("📥 Waiting for response...")
        response = sock.recv(1024)
        
        if response:
            print(f"✅ Received: {len(response)} bytes")
            print(f"   Data: {response[:100]}")
        else:
            print("⚠️  No response received")
        
        sock.close()
        print("\n✅ Test completed!")
        
    except ConnectionRefusedError:
        print("❌ Connection refused! Is the server running?")
        sys.exit(1)
    except socket.timeout:
        print("⚠️  Timeout waiting for response")
        print("   (This might be normal if local service isn't responding)")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_tunnel()
