import json
import os
from datetime import datetime, timedelta

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

def add_client():
    username = input("Nom du client: ")
    days = int(input("Durée en jours: "))
    expiry = (datetime.now() + timedelta(days=days)).isoformat()
    clients = load_clients()
    clients[username] = {"expiry": expiry, "online": False}
    save_clients(clients)
    print(f"✅ Client {username} ajouté (expire le {expiry})")

def remove_client():
    username = input("Nom du client à supprimer: ")
    clients = load_clients()
    if username in clients:
        del clients[username]
        save_clients(clients)
        print(f"❌ Client {username} supprimé")
    else:
        print("Client introuvable")

def list_clients():
    clients = load_clients()
    for user, info in clients.items():
        print(f"{user} | expire: {info['expiry']} | online: {info['online']}")

def menu():
    while True:
        os.system("clear")
        print("• UDP Custom Manager •\n")
        print("[1] Ajouter un client")
        print("[2] Supprimer un client")
        print("[3] Lister les clients")
        print("[4] Infos VPS")
        print("[0] Quitter\n")
        choice = input("→ Choisissez une option: ")
        if choice == "1":
            add_client()
        elif choice == "2":
            remove_client()
        elif choice == "3":
            list_clients()
            input("Appuyez sur Entrée pour continuer...")
        elif choice == "4":
            os.system("uptime")
            input("Appuyez sur Entrée pour continuer...")
        elif choice == "0":
            break

if __name__ == "__main__":
    menu()
