#!/bin/bash

# ======= 設定 ========
VENV_DIR="/opt/ipreporter-venv"
SCRIPT_PATH="/usr/local/bin/report_ip.py"
SERVICE_PATH="/etc/systemd/system/report-ip.service"
TIMER_PATH="/etc/systemd/system/report-ip.timer"
FIREBASE_KEY_DIR="/etc/firebase"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_SCRIPT="$REPO_DIR/report_ip.py"
# =====================

# 引数確認
if [ -z "$1" ]; then
  echo "⚠️ 使用方法: ./install-ip-reporter.sh <path/to/service-account.json>"
  exit 1
fi

FIREBASE_KEY_SOURCE="$1"
FIREBASE_KEY_BASENAME=$(basename "$FIREBASE_KEY_SOURCE")

set -e

echo "[1] 仮想環境を作成: $VENV_DIR"
sudo python3 -m venv "$VENV_DIR"
sudo "$VENV_DIR/bin/pip" install --upgrade pip
sudo "$VENV_DIR/bin/pip" install firebase-admin

echo "[2] Pythonスクリプトを配置: $SCRIPT_PATH"
sudo cp "$PYTHON_SCRIPT" "$SCRIPT_PATH"
sudo chmod +x "$SCRIPT_PATH"

echo "[3] Firebase サービスアカウントキーを配置: $FIREBASE_KEY_DIR/$FIREBASE_KEY_BASENAME"
sudo mkdir -p "$FIREBASE_KEY_DIR"
sudo cp "$FIREBASE_KEY_SOURCE" "$FIREBASE_KEY_DIR/$FIREBASE_KEY_BASENAME"
sudo chmod 600 "$FIREBASE_KEY_DIR/$FIREBASE_KEY_BASENAME"

echo "[4] systemd サービスを配置"
sudo tee "$SERVICE_PATH" >/dev/null <<EOF
[Unit]
Description=Send IP address to Firebase (via virtualenv)

[Service]
Type=oneshot
ExecStart=$VENV_DIR/bin/python $SCRIPT_PATH
EOF

echo "[5] systemd タイマーを配置"
sudo tee "$TIMER_PATH" >/dev/null <<EOF
[Unit]
Description=Timer to send IP address to Firebase every minute

[Timer]
OnBootSec=30sec
OnUnitActiveSec=60sec
Persistent=true

[Install]
WantedBy=timers.target
EOF

echo "[6] systemd 再読み込み・有効化"
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable --now report-ip.timer

echo "[✅ 完了] 1分ごとに Firebase にIPを送信します。"
echo "確認方法: journalctl -u report-ip.service -f"