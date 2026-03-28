"""Find available network ports."""

import socket
from typing import List


def is_port_available(port: int, host: str = "127.0.0.1") -> bool:
    """Check if a port is available for binding."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind((host, port))
            return True
        except OSError:
            return False


def find_available_ports(start: int = 3000, end: int = 9000, count: int = 5, host: str = "127.0.0.1") -> List[int]:
    """Find available ports in a range."""
    available = []
    for port in range(start, end + 1):
        if is_port_available(port, host):
            available.append(port)
            if len(available) >= count:
                break
    return available
