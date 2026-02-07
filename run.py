"""
GLOF Monitoring System - Main Runner
Starts both frontend and backend services with a single command.

Usage:
    python run.py          # Start all services
    python run.py --backend   # Start backend only
    python run.py --frontend  # Start frontend only
"""

import subprocess
import sys
import os
import signal
import threading
from pathlib import Path

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

# Get base directory
BASE_DIR = Path(__file__).parent

# Service configurations
SERVICES = {
    'gateway': {
        'name': 'API Gateway',
        'cwd': BASE_DIR / 'Backend' / 'gateway',
        'cmd': [sys.executable, 'main.py'],
        'port': 8000,
        'color': Colors.BLUE
    },
    'glof': {
        'name': 'GLOF Service',
        'cwd': BASE_DIR / 'Backend' / 'GLOF',
        'cmd': [sys.executable, 'main.py'],
        'port': 8001,
        'color': Colors.GREEN
    },
    'sar': {
        'name': 'SAR Service',
        'cwd': BASE_DIR / 'Backend' / 'SAR',
        'cmd': [sys.executable, 'main.py'],
        'port': 8002,
        'color': Colors.CYAN
    },
    'lake': {
        'name': 'Lake Service',
        'cwd': BASE_DIR / 'Backend' / 'lake_size',
        'cmd': [sys.executable, 'main.py'],
        'port': 8003,
        'color': Colors.WARNING
    },
    'terrain': {
        'name': 'Terrain Service',
        'cwd': BASE_DIR / 'Backend' / 'srtm & motionOfWaves',
        'cmd': [sys.executable, 'main.py'],
        'port': 8004,
        'color': Colors.HEADER
    },
    'frontend': {
        'name': 'Frontend',
        'cwd': BASE_DIR / 'Frontend' / 'glof-dashboard',
        'cmd': ['npm', 'run', 'dev'],
        'port': 5173,
        'color': Colors.FAIL
    }
}

processes = []


def print_banner():
    """Print startup banner."""
    banner = f"""
{Colors.BOLD}{Colors.CYAN}
╔══════════════════════════════════════════════════════════════╗
║                   GLOF MONITORING SYSTEM                     ║
║                     Startup Manager                          ║
╚══════════════════════════════════════════════════════════════╝
{Colors.END}
"""
    print(banner)


def print_status(service_name, message, color=Colors.GREEN):
    """Print colored status message."""
    print(f"{color}[{service_name}]{Colors.END} {message}")


def run_service(service_key):
    """Run a single service."""
    service = SERVICES[service_key]
    
    if not service['cwd'].exists():
        print_status(service['name'], f"Directory not found: {service['cwd']}", Colors.FAIL)
        return None
    
    try:
        # Use shell=True on Windows for npm commands
        use_shell = sys.platform == 'win32' and service_key == 'frontend'
        
        process = subprocess.Popen(
            service['cmd'],
            cwd=str(service['cwd']),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=use_shell,
            bufsize=1,
            universal_newlines=True
        )
        
        print_status(service['name'], f"Started on port {service['port']}", service['color'])
        processes.append(process)
        
        # Stream output in a thread
        def stream_output():
            for line in iter(process.stdout.readline, ''):
                if line:
                    print(f"{service['color']}[{service['name']}]{Colors.END} {line.strip()}")
        
        thread = threading.Thread(target=stream_output, daemon=True)
        thread.start()
        
        return process
        
    except FileNotFoundError as e:
        print_status(service['name'], f"Command not found: {e}", Colors.FAIL)
        return None
    except Exception as e:
        print_status(service['name'], f"Error: {e}", Colors.FAIL)
        return None


def start_backend():
    """Start all backend services."""
    print(f"\n{Colors.BOLD}Starting Backend Services...{Colors.END}\n")
    
    # Start gateway first
    run_service('gateway')
    
    # Optionally start individual services
    # Uncomment these to run all services:
    # run_service('glof')
    # run_service('sar')
    # run_service('lake')
    # run_service('terrain')


def start_frontend():
    """Start frontend development server."""
    print(f"\n{Colors.BOLD}Starting Frontend...{Colors.END}\n")
    run_service('frontend')


def cleanup(signum=None, frame=None):
    """Clean up all processes on exit."""
    print(f"\n{Colors.WARNING}Shutting down all services...{Colors.END}")
    
    for process in processes:
        try:
            if sys.platform == 'win32':
                process.terminate()
            else:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        except:
            pass
    
    print(f"{Colors.GREEN}All services stopped.{Colors.END}")
    sys.exit(0)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='GLOF Monitoring System Runner')
    parser.add_argument('--backend', action='store_true', help='Start backend only')
    parser.add_argument('--frontend', action='store_true', help='Start frontend only')
    parser.add_argument('--all-services', action='store_true', help='Start all individual services (not just gateway)')
    args = parser.parse_args()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, cleanup)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, cleanup)
    
    print_banner()
    
    # Determine what to start
    start_be = not args.frontend or args.backend
    start_fe = not args.backend or args.frontend
    
    if not args.backend and not args.frontend:
        start_be = True
        start_fe = True
    
    if start_be:
        start_backend()
        if args.all_services:
            run_service('glof')
            run_service('sar')
            run_service('lake')
            run_service('terrain')
    
    if start_fe:
        start_frontend()
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}═══════════════════════════════════════════════════════════════{Colors.END}")
    print(f"{Colors.BOLD}Services Running:{Colors.END}")
    if start_be:
        print(f"  {Colors.BLUE}• API Gateway:{Colors.END}  http://localhost:8000")
    if start_fe:
        print(f"  {Colors.FAIL}• Frontend:{Colors.END}     http://localhost:5173")
    print(f"{Colors.BOLD}{Colors.GREEN}═══════════════════════════════════════════════════════════════{Colors.END}")
    print(f"\n{Colors.WARNING}Press Ctrl+C to stop all services{Colors.END}\n")
    
    # Keep main thread alive
    try:
        while True:
            for process in processes:
                if process.poll() is not None:
                    processes.remove(process)
            if not processes:
                print(f"{Colors.WARNING}All services have stopped.{Colors.END}")
                break
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()


if __name__ == '__main__':
    main()
