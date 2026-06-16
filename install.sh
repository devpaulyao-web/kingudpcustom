#!/bin/bash

sudo apt update
sudo apt install -y python3 python3-pip

pip3 install -r requirements.txt

sudo tee /usr/local/bin/udp > /dev/null <<EOL
#!/bin/bash
cd $(pwd)
python3 manager.py
EOL
sudo chmod +x /usr/local/bin/udp

SERVICE_FILE=/etc/systemd/system/udp.service
sudo tee $SERVICE_FILE > /dev/null <<EOL
[Unit]
Description=UDP Custom Server
After=network.target

[Service]
ExecStart=/usr/bin/python3 $(pwd)/server.py
WorkingDirectory=$(pwd)
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOL

sudo systemctl daemon-reexec
sudo systemctl enable udp.service
sudo systemctl start udp.service

echo "✅ Installation terminée."
echo "➡️ Le serveur UDP démarre automatiquement au boot."
echo "➡️ Tapez 'udp' pour lancer le manager interactif."
