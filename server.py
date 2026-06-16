import asyncio
import logging
import socket
import json

# Charger la configuration
with open("config.json", "r") as f:
    config = json.load(f)

PORTS = config.get("ports", [53, 443, 8080])
EXCLUDE = config.get("exclude", [])

# Charger les clients
CLIENTS_FILE = "clients.json"
def load_clients():
    try:
        with open(CLIENTS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_clients(clients):
    with open(CLIENTS_FILE, "w") as f:
        json.dump(clients, f, indent=4)

logging.basicConfig(
    filename="/var/log/udp-custom.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

class UDPProtocol(asyncio.DatagramProtocol):
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode(errors="ignore").strip()
        logging.info(f"Reçu de {addr}: {message}")

        # Format attendu: "username:password:payload"
        parts = message.split(":", 2)
        if len(parts) < 3:
            self.transport.sendto(b"Format invalide", addr)
            return

        username, password, payload = parts
        clients = load_clients()

        if username not in clients:
            self.transport.sendto(b"Utilisateur inconnu", addr)
            return

        client = clients[username]

        # Vérifier expiration
        if datetime.fromisoformat(client["expiry"]) < datetime.now():
            self.transport.sendto(b"Compte expiré", addr)
            return

        # Vérifier mot de passe
        if client["password"] != password:
            self.transport.sendto(b"Mot de passe incorrect", addr)
            return

        # Vérifier limite de connexions
        if client["online"] >= client["max_conn"]:
            self.transport.sendto(b"Limite de connexions atteinte", addr)
            return

        # Autoriser connexion
        client["online"] += 1
        save_clients(clients)

        response = f"OK {username} | payload reçu: {payload}".encode()
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
    from datetime import datetime
    asyncio.run(main())
