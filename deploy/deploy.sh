#!/usr/bin/env bash
# Run this ON the EC2 instance, from inside the cloned repo directory
# (Amazon Linux 2023). Sets up a venv, installs deps, and registers
# gunicorn as a systemd service on 127.0.0.1:8000.
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$APP_DIR"

sudo dnf install -y python3-pip python3-virtualenv nginx

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r deploy/requirements-prod.txt
deactivate

sudo cp deploy/lta-commuter.service /etc/systemd/system/lta-commuter.service
sudo systemctl daemon-reload
sudo systemctl enable --now lta-commuter

sudo cp deploy/nginx.conf /etc/nginx/conf.d/lta-commuter.conf
sudo rm -f /etc/nginx/conf.d/default.conf
sudo systemctl enable --now nginx
sudo systemctl reload nginx

echo "Deployed. App should be reachable on http://<ec2-public-ip>/"
echo "Check status with: sudo systemctl status lta-commuter"
