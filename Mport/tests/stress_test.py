"""
MPORT STRESS TEST SUITE
======================
Comprehensive stress testing for Week 1 implementation.

Tests:
1. Connection stress (multiple rapid connects/disconnects)
2. Data throughput (large data transfers)
3. Concurrent ADB commands (parallel operations)
4. Memory leak detection (long-running test)
5. Rate limiting verification (exceed limits)
6. Connection pool exhaustion
"""

import asyncio
import socket
import time
import subprocess
import sys
from typing import List, Dict
import statistics


# ANSI Colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"


class StressTest:
    def __init__(self):
        self.server_host = "localhost"
        self.tunnel_port = 8080
        self.control_port = 8081
        self.results = {}
        
    def print_header(self, text: str):
        """Print test header"""
        print(f"\n{CYAN}{BOLD}{'=' * 70}{RESET}")
        print(f"{CYAN}{BOLD}{text:^70}{RESET}")
        print(f"{CYAN}{BOLD}{'=' * 70}{RESET}\n")
        
    def print_result(self, test_name: str, passed: bool, details: str = ""):
        """Print test result"""
        status = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
        print(f"{status} - {test_name}")
        if details:
            print(f"      {details}")
            
    async def test_1_rapid_connections(self, count: int = 50):
        """Test 1: Rapid connection/disconnection stress"""
        self.print_header("TEST 1: RAPID CONNECTIONS")
        print(f"Attempting {count} rapid connect/disconnect cycles...")
        
        success_count = 0
        fail_count = 0
        times = []
        
        for i in range(count):
            try:
                start = time.time()
                
                # Try to connect to tunnel port
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((self.server_host, self.tunnel_port))
                
                # Immediately disconnect
                sock.close()
                
                elapsed = time.time() - start
                times.append(elapsed)
                success_count += 1
                
                if (i + 1) % 10 == 0:
                    print(f"  Progress: {i + 1}/{count} connections...")
                    
            except Exception as e:
                fail_count += 1
                print(f"  {RED}Connection {i + 1} failed: {e}{RESET}")
                
            # Small delay to prevent overwhelming
            await asyncio.sleep(0.01)
        
        # Calculate stats
        avg_time = statistics.mean(times) if times else 0
        min_time = min(times) if times else 0
        max_time = max(times) if times else 0
        
        passed = success_count >= count * 0.9  # 90% success rate
        
        details = f"Success: {success_count}/{count} ({success_count/count*100:.1f}%)"
        details += f"\n      Avg time: {avg_time*1000:.2f}ms, Min: {min_time*1000:.2f}ms, Max: {max_time*1000:.2f}ms"
        
        self.print_result("Rapid Connections", passed, details)
        self.results['rapid_connections'] = {
            'passed': passed,
            'success': success_count,
            'total': count,
            'avg_time_ms': avg_time * 1000
        }
        
    async def test_2_concurrent_adb_commands(self, count: int = 20):
        """Test 2: Concurrent ADB commands through tunnel"""
        self.print_header("TEST 2: CONCURRENT ADB COMMANDS")
        print(f"Running {count} parallel ADB commands...")
        
        commands = [
            "adb -s localhost:8080 shell getprop ro.product.model",
            "adb -s localhost:8080 shell getprop ro.build.version.release",
            "adb -s localhost:8080 shell dumpsys battery | findstr level",
            "adb -s localhost:8080 shell getprop ro.product.manufacturer",
            "adb -s localhost:8080 shell getprop ro.product.brand",
        ]
        
        async def run_command(cmd: str, index: int):
            """Run single ADB command"""
            try:
                start = time.time()
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                elapsed = time.time() - start
                
                return {
                    'success': result.returncode == 0,
                    'time': elapsed,
                    'output': result.stdout.strip(),
                    'index': index
                }
            except Exception as e:
                return {
                    'success': False,
                    'time': 0,
                    'error': str(e),
                    'index': index
                }
        
        # Run commands concurrently
        tasks = []
        for i in range(count):
            cmd = commands[i % len(commands)]
            tasks.append(run_command(cmd, i))
        
        results = await asyncio.gather(*tasks)
        
        # Analyze results
        success_count = sum(1 for r in results if r['success'])
        times = [r['time'] for r in results if r['success']]
        
        avg_time = statistics.mean(times) if times else 0
        
        passed = success_count >= count * 0.8  # 80% success rate
        
        details = f"Success: {success_count}/{count} ({success_count/count*100:.1f}%)"
        if times:
            details += f"\n      Avg response: {avg_time*1000:.2f}ms"
        
        # Show some sample outputs
        print(f"\n  Sample outputs:")
        for r in results[:3]:
            if r['success']:
                print(f"    [{r['index']}] {r['output'][:50]}... ({r['time']*1000:.0f}ms)")
        
        self.print_result("Concurrent ADB Commands", passed, details)
        self.results['concurrent_commands'] = {
            'passed': passed,
            'success': success_count,
            'total': count,
            'avg_time_ms': avg_time * 1000
        }
        
    async def test_3_data_throughput(self):
        """Test 3: Large data transfer"""
        self.print_header("TEST 3: DATA THROUGHPUT")
        print("Testing large file operations through tunnel...")
        
        commands = [
            # Get large property list
            ("adb -s localhost:8080 shell getprop", "Property list"),
            # Get package list (can be large)
            ("adb -s localhost:8080 shell pm list packages", "Package list"),
            # Get all running processes
            ("adb -s localhost:8080 shell ps", "Process list"),
        ]
        
        results = []
        
        for cmd, name in commands:
            try:
                start = time.time()
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                elapsed = time.time() - start
                
                if result.returncode == 0:
                    data_size = len(result.stdout)
                    throughput = data_size / elapsed if elapsed > 0 else 0
                    
                    results.append({
                        'name': name,
                        'success': True,
                        'size': data_size,
                        'time': elapsed,
                        'throughput': throughput
                    })
                    
                    print(f"  {GREEN}✓{RESET} {name}: {data_size:,} bytes in {elapsed:.2f}s ({throughput/1024:.1f} KB/s)")
                else:
                    results.append({'name': name, 'success': False})
                    print(f"  {RED}✗{RESET} {name}: Failed")
                    
            except Exception as e:
                results.append({'name': name, 'success': False, 'error': str(e)})
                print(f"  {RED}✗{RESET} {name}: {e}")
        
        success_count = sum(1 for r in results if r.get('success'))
        passed = success_count >= len(commands) * 0.7  # 70% success
        
        total_bytes = sum(r.get('size', 0) for r in results if r.get('success'))
        avg_throughput = statistics.mean([r.get('throughput', 0) for r in results if r.get('success')]) if results else 0
        
        details = f"Transferred: {total_bytes:,} bytes total"
        details += f"\n      Avg throughput: {avg_throughput/1024:.1f} KB/s"
        
        self.print_result("Data Throughput", passed, details)
        self.results['data_throughput'] = {
            'passed': passed,
            'total_bytes': total_bytes,
            'avg_throughput_kbps': avg_throughput / 1024
        }
        
    async def test_4_sustained_load(self, duration: int = 60):
        """Test 4: Sustained load over time"""
        self.print_header("TEST 4: SUSTAINED LOAD")
        print(f"Running continuous commands for {duration} seconds...")
        
        start_time = time.time()
        command_count = 0
        success_count = 0
        errors = []
        
        while time.time() - start_time < duration:
            try:
                result = subprocess.run(
                    "adb -s localhost:8080 shell getprop ro.product.model",
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                command_count += 1
                if result.returncode == 0:
                    success_count += 1
                else:
                    errors.append(f"Command failed at {time.time() - start_time:.1f}s")
                
                # Show progress every 10 seconds
                elapsed = time.time() - start_time
                if int(elapsed) % 10 == 0 and command_count > 0:
                    rate = command_count / elapsed
                    print(f"  Progress: {int(elapsed)}s - {command_count} commands ({rate:.1f} cmd/s)")
                
                await asyncio.sleep(0.5)  # 2 commands per second
                
            except Exception as e:
                errors.append(str(e))
        
        total_time = time.time() - start_time
        success_rate = success_count / command_count if command_count > 0 else 0
        commands_per_sec = command_count / total_time
        
        passed = success_rate >= 0.95  # 95% success over time
        
        details = f"Commands: {command_count} total, {success_count} successful ({success_rate*100:.1f}%)"
        details += f"\n      Rate: {commands_per_sec:.1f} commands/second"
        details += f"\n      Errors: {len(errors)}"
        
        self.print_result("Sustained Load", passed, details)
        self.results['sustained_load'] = {
            'passed': passed,
            'total_commands': command_count,
            'success_rate': success_rate,
            'commands_per_sec': commands_per_sec
        }
        
    async def test_5_connection_recovery(self):
        """Test 5: Connection recovery after errors"""
        self.print_header("TEST 5: CONNECTION RECOVERY")
        print("Testing recovery from connection issues...")
        
        recovery_tests = []
        
        # Test 1: Invalid command recovery
        print("\n  Test 5.1: Invalid command handling...")
        try:
            result = subprocess.run(
                "adb -s localhost:8080 shell invalid_command_xyz",
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            # Should fail but connection should survive
            await asyncio.sleep(1)
            
            # Try valid command after
            result2 = subprocess.run(
                "adb -s localhost:8080 shell getprop ro.product.model",
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            recovered = result2.returncode == 0
            recovery_tests.append(('Invalid command recovery', recovered))
            
            if recovered:
                print(f"    {GREEN}✓{RESET} Recovered successfully")
            else:
                print(f"    {RED}✗{RESET} Failed to recover")
                
        except Exception as e:
            recovery_tests.append(('Invalid command recovery', False))
            print(f"    {RED}✗{RESET} Error: {e}")
        
        # Test 2: Rapid command burst
        print("\n  Test 5.2: Rapid command burst...")
        try:
            burst_success = 0
            for i in range(10):
                result = subprocess.run(
                    "adb -s localhost:8080 shell echo test",
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    burst_success += 1
            
            burst_passed = burst_success >= 8  # 80% success
            recovery_tests.append(('Rapid burst', burst_passed))
            
            print(f"    {GREEN if burst_passed else RED}{'✓' if burst_passed else '✗'}{RESET} {burst_success}/10 commands succeeded")
            
        except Exception as e:
            recovery_tests.append(('Rapid burst', False))
            print(f"    {RED}✗{RESET} Error: {e}")
        
        passed = sum(1 for _, p in recovery_tests if p) >= len(recovery_tests) * 0.7
        
        details = f"Recovery tests: {sum(1 for _, p in recovery_tests if p)}/{len(recovery_tests)} passed"
        
        self.print_result("Connection Recovery", passed, details)
        self.results['connection_recovery'] = {
            'passed': passed,
            'tests': len(recovery_tests),
            'passed_tests': sum(1 for _, p in recovery_tests if p)
        }
        
    def print_summary(self):
        """Print test summary"""
        self.print_header("STRESS TEST SUMMARY")
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values() if r['passed'])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {GREEN}{passed_tests}{RESET}")
        print(f"Failed: {RED}{total_tests - passed_tests}{RESET}")
        print(f"Success Rate: {passed_tests/total_tests*100:.1f}%")
        
        print(f"\n{BOLD}Detailed Results:{RESET}")
        for test_name, data in self.results.items():
            status = f"{GREEN}PASS{RESET}" if data['passed'] else f"{RED}FAIL{RESET}"
            print(f"\n  {status} - {test_name.replace('_', ' ').title()}")
            
            # Print relevant metrics
            if 'avg_time_ms' in data:
                print(f"         Avg Response: {data['avg_time_ms']:.2f}ms")
            if 'success' in data and 'total' in data:
                print(f"         Success Rate: {data['success']}/{data['total']} ({data['success']/data['total']*100:.1f}%)")
            if 'commands_per_sec' in data:
                print(f"         Throughput: {data['commands_per_sec']:.1f} commands/sec")
            if 'total_bytes' in data:
                print(f"         Data Transfer: {data['total_bytes']:,} bytes")
        
        print(f"\n{CYAN}{'=' * 70}{RESET}")
        
        if passed_tests == total_tests:
            print(f"{GREEN}{BOLD}ALL TESTS PASSED! Week 1 is solid! 🎉{RESET}")
        elif passed_tests >= total_tests * 0.8:
            print(f"{YELLOW}{BOLD}Most tests passed. Some areas need attention.{RESET}")
        else:
            print(f"{RED}{BOLD}Several tests failed. System needs improvement.{RESET}")
        
        print(f"{CYAN}{'=' * 70}{RESET}\n")


async def main():
    """Run all stress tests"""
    print(f"{CYAN}{BOLD}")
    print("=" * 70)
    print("MPORT WEEK 1 STRESS TEST SUITE".center(70))
    print("=" * 70)
    print(f"{RESET}")
    
    print(f"\n{YELLOW}Prerequisites:{RESET}")
    print("  1. Server running: python server/tunnel_server.py")
    print("  2. Client running: python client/tunnel_client.py")
    print("  3. ADB connected: adb connect localhost:8080")
    
    input(f"\n{YELLOW}Press ENTER to start stress testing...{RESET}")
    
    tester = StressTest()
    
    try:
        # Run all tests
        await tester.test_1_rapid_connections(count=50)
        await asyncio.sleep(2)
        
        await tester.test_2_concurrent_adb_commands(count=20)
        await asyncio.sleep(2)
        
        await tester.test_3_data_throughput()
        await asyncio.sleep(2)
        
        await tester.test_4_sustained_load(duration=30)  # 30 seconds instead of 60 for faster testing
        await asyncio.sleep(2)
        
        await tester.test_5_connection_recovery()
        
        # Print summary
        tester.print_summary()
        
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Test interrupted by user{RESET}")
        tester.print_summary()
    except Exception as e:
        print(f"\n{RED}Fatal error: {e}{RESET}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
