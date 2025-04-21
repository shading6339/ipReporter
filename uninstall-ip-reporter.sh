#!/bin/bash

# ======= 設定 ========
VENV_DIR="/opt/ipreporter-venv"
SCRIPT_PATH="/usr/local/bin/report_ip.py"
SERVICE_PATH="/etc/systemd/system/report-ip.service"
TIMER_PATH="/etc/systemd/system/report-ip.timer"
FIREBASE_KEY_DIR="/etc/firebase"
# =====================

echo "🧹 ipReporter をアンインストールします。root権限が必要です。"
read -p "続行しますか？ (y/N): " confirm

if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
  echo "中止しました。"
  exit 0
fi

set -e

echo "[1] systemd サービスとタイマーを停止・無効化"
sudo systemctl disable --now report-ip.timer || true
sudo systemctl disable --now report-ip.service || true

echo "[2] systemd ファイルを削除"
sudo rm -f "$SERVICE_PATH" "$TIMER_PATH"
sudo systemctl daemon-reload

echo "[3] Python 仮想環境を削除: $VENV_DIR"
sudo rm -rf "$VENV_DIR"

echo "[4] スクリプトを削除: $SCRIPT_PATH"
sudo rm -f "$SCRIPT_PATH"

# Firebase鍵削除（確認付き）
echo "[5] Firebase サービスアカウントキーを削除しますか？（/etc/firebase/*.json）"
read -p "削除する場合は y を押してください: " del_keys

if [[ "$del_keys" == "y" || "$del_keys" == "Y" ]]; then
  sudo rm -f "$FIREBASE_KEY_DIR"/*.json
  echo "✅ サービスアカウントキーを削除しました。"
else
  echo "⚠️ 鍵ファイルはそのまま残しました。"
fi

echo "✅ アンインストール完了"