import asyncio
import logging
import socket
import json

# Charger la configuration
with open("config.json", "r") as f:
    config = json.load(f)

PORTS = config.get("ports", [53, 443, 8080])
EXCLUDE = config.get("exclude", [])

logging.basicConfig(
    filename="/var/log/udp-custom.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

class UDPProtocol(asyncio.DatagramProtocol):
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode(errors="ignore")
        logging.info(f"Reçu de {addr}: {message}")
        response = f"Réponse UDP VPS sur port {self.transport.get_extra_info('sockname')[1]}".encode()
        self.transport.sendto(response, addr)

async def main():
    loop = asyncio.get_running_loop()
    for port in PORTS:
        if port in EXCLUDE:
            continue
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1048576)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576)
        sock.bind(("0.0.0.0", port))
        await loop.create_datagram_endpoint(lambda: UDPProtocol(), sock=sock)
        logging.info(f"Serveur UDP actif sur port {port}")
    await asyncio.sleep(3600*24)

if __name__ == "__main__":
    asyncio.run(main())
