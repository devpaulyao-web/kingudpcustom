import asyncio
import logging
import socket
import json
from datetime import datetime

# Charger la configuration
with open("config.json", "r") as f:
    config = json.load(f)

PORTS = config.get("ports", [53, 443, 8080])
EXCLUDE = config.get("exclude", [])

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

        # Vérifier limite
