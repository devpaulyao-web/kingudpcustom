import asyncio
import logging
import socket
import json
from datetime import datetime

# Charger la configuration
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

        # Format attendu: ip:port@user:pass
        try:
            ip_port, creds = message.split("@", 1)
            ip, port = ip_port.split(":")
            username, password = creds.split(":", 1)
        except Exception:
            self.transport.sendto(b"Format invalide (ip:port@user:pass)", addr)
            return

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

        response = f"Connexion OK pour {username} sur {ip}:{port}".encode()
        self.transport.sendto(response, addr)

async def main():
    loop = asyncio.get_running_loop()
    # Ouvrir tous les ports de 1 à 65535
    for port in range(1, 65536):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1048576)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576)
            sock.bind(("0.0.0.0", port))
            await loop.create_datagram_endpoint(lambda: UDPProtocol(), sock=sock)
            logging.info(f"Serveur UDP actif sur port {port}")
        except Exception as e:
            logging.warning(f"Impossible d’ouvrir le port {port}: {e}")
    await asyncio.sleep(3600*24)

if __name__ == "__main__":
    asyncio.run(main())
