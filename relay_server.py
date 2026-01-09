#!/usr/bin/env python3
"""Simple TCP relay server for LAN-Messenger-P2P (cross-campus mode).

Protocol: length-prefixed frames
- 4-byte big-endian length N
- N bytes payload (Base64-encoded JSON), forwarded as-is to other clients

Run:
  python relay_server.py --host 0.0.0.0 --port 9000

Then clients:
  python client-tk.py --relay <SERVER_IP>:9000
  python client-pyside.py --relay <SERVER_IP>:9000
"""

from __future__ import annotations

import argparse
import socket
import struct
import threading
from typing import List


def recv_exact(conn: socket.socket, n: int) -> bytes | None:
    data = b""
    while len(data) < n:
        chunk = conn.recv(n - len(data))
        if not chunk:
            return None
        data += chunk
    return data


class RelayServer:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.clients: List[socket.socket] = []
        self.lock = threading.Lock()

    def broadcast(self, sender: socket.socket, frame: bytes) -> None:
        with self.lock:
            dead = []
            for c in self.clients:
                if c is sender:
                    continue
                try:
                    c.sendall(frame)
                except OSError:
                    dead.append(c)
            for d in dead:
                try:
                    d.close()
                except OSError:
                    pass
                if d in self.clients:
                    self.clients.remove(d)

    def handle(self, conn: socket.socket, addr) -> None:
        with self.lock:
            self.clients.append(conn)

        try:
            while True:
                header = recv_exact(conn, 4)
                if not header:
                    break
                (n,) = struct.unpack("!I", header)
                if n <= 0 or n > 1024 * 1024:
                    break
                payload = recv_exact(conn, n)
                if not payload:
                    break
                self.broadcast(conn, header + payload)
        finally:
            with self.lock:
                if conn in self.clients:
                    self.clients.remove(conn)
            try:
                conn.close()
            except OSError:
                pass

    def serve(self) -> None:
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((self.host, self.port))
        srv.listen()
        print(f"[*] Relay listening on {self.host}:{self.port}")

        try:
            while True:
                conn, addr = srv.accept()
                conn.settimeout(30.0)
                print(f"[+] client {addr}")
                threading.Thread(target=self.handle, args=(conn, addr), daemon=True).start()
        finally:
            try:
                srv.close()
            except OSError:
                pass


def parse_args():
    p = argparse.ArgumentParser(description="TCP relay server for LAN-Messenger-P2P")
    p.add_argument("--host", default="0.0.0.0", help="Bind host")
    p.add_argument("--port", type=int, default=9000, help="Bind port")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    RelayServer(args.host, args.port).serve()


if __name__ == "__main__":
    main()
