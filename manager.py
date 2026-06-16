import json
import os
import subprocess
from datetime import datetime, timedelta

CLIENTS_FILE = "clients.json"

# Codes de couleur ANSI
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

def load_clients():
    try:
        with open(CLIENTS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_clients(clients):
    with open(CLIENTS_FILE, "w") as f:
        json.dump(clients, f, indent=4)

def add_client():
    username = input(f"{CYAN}Nom du client: {RESET}")
    password = input(f"{CYAN}Mot de passe: {RESET}")
    days = int(input(f"{CYAN}Durée en jours: {RESET}"))
    max_conn = int(input(f"{CYAN}Nombre maximum de connexions simultanées: {RESET}"))
    expiry = (datetime.now() + timedelta(days=days)).isoformat()
    clients = load_clients()
    clients[username] = {
        "password": password,
        "expiry": expiry,
        "max_conn": max_conn,
        "online": 0
    }
    save_clients(clients)
    print(f"{GREEN}✅ Client {username} ajouté (expire le {expiry}, max {max_conn} connexions){RESET}")

def remove_client():
    username = input(f"{CYAN}Nom du client à supprimer: {RESET}")
    clients = load_clients()
    if username in clients:
        del clients[username]
        save_clients(clients)
        print(f"{RED}❌ Client {username} supprimé{RESET}")
    else:
        print(f"{YELLOW}Client introuvable{RESET}")

def list_clients():
    clients = load_clients()
    print(f"{CYAN}--- Liste des clients ---{RESET}")
    for user, info in clients.items():
        print(f"{GREEN}{user}{RESET} | expire: {info['expiry']} | max_conn: {info['max_conn']} | online: {info['online']}")

def uninstall():
    print(f"{RED}⚠️ Suppression complète de UDP Custom Manager...{RESET}")
    try:
        subprocess.run(["systemctl", "stop", "udp.service"], check=False)
        subprocess.run(["systemctl", "disable", "udp.service"], check=False)
        subprocess.run(["rm", "-f", "/etc/systemd/system/udp.service"], check=False)
        subprocess.run(["systemctl", "daemon-reload"], check=False)
        subprocess.run(["rm", "-f", "/usr/local/bin/udp"], check=False)
        project_path = os.path.dirname(os.path.abspath(__file__))
        subprocess.run(["rm", "-rf", project_path], check=False)
        print(f"{GREEN}✅ UDP Custom Manager désinstallé avec succès.{RESET}")
    except Exception as e:
        print(f"{RED}Erreur lors de la désinstallation: {e}{RESET}")

def menu():
    while True:
        os.system("clear")
        print(f"{RED}• UDP Custom Manager •{RESET}")
        print(f"{YELLOW}Version: 2.5-Lite | Nom: KingUser{RESET}\n")
        print(f"{CYAN}[1]{RESET} Ajouter un client")
        print(f"{CYAN}[2]{RESET} Supprimer un client")
        print(f"{CYAN}[3]{RESET} Lister les clients")
        print(f"{CYAN}[4]{RESET} Infos VPS")
        print(f"{CYAN}[10]{RESET} Désinstaller UDP Manager")
        print(f"{CYAN}[0]{RESET} Quitter\n")
        choice = input(f"{YELLOW}→ Choisissez une option: {RESET}")
        if choice == "1":
            add_client()
            input("Appuyez sur Entrée pour continuer...")
        elif choice == "2":
            remove_client()
            input("Appuyez sur Entrée pour continuer...")
        elif choice == "3":
            list_clients()
            input("Appuyez sur Entrée pour continuer...")
        elif choice == "4":
            os.system("uptime")
            input("Appuyez sur Entrée pour continuer...")
        elif choice == "10":
            uninstall()
            break
        elif choice == "0":
            break

if __name__ == "__main__":
    menu()
