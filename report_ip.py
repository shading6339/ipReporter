#!/usr/bin/env python3

import os
import glob
import socket
import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# ===== サービスアカウントJSONを自動検出 =====
FIREBASE_KEY_DIR = "/etc/firebase"
json_files = glob.glob(os.path.join(FIREBASE_KEY_DIR, "*.json"))

if not json_files:
    raise FileNotFoundError(f"サービスアカウントキーが {FIREBASE_KEY_DIR} に存在しません")

SERVICE_ACCOUNT_PATH = json_files[0]
# ============================================

if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()
hostname = socket.gethostname()
ip_path = "/tmp/last_ip.txt"
collection = "hosts"

def get_local_ip():
    try:
        return os.popen("hostname -I").read().strip().split()[0]
    except Exception as e:
        print(f"IP取得エラー: {e}")
        return "N/A"

def get_last_ip():
    if os.path.exists(ip_path):
        with open(ip_path, "r") as f:
            return f.read().strip()
    return ""

def save_ip(ip):
    with open(ip_path, "w") as f:
        f.write(ip)

def update_firestore(ip):
    now = datetime.datetime.now().isoformat()
    doc_ref = db.collection(collection).document(hostname)
    doc_ref.set({
        "ip": ip,
        "updated_at": now
    }, merge=True)
    print(f"[{now}] IP更新: {hostname} = {ip}")

if __name__ == "__main__":
    current_ip = get_local_ip()
    last_ip = get_last_ip()

    if current_ip != last_ip:
        update_firestore(current_ip)
        save_ip(current_ip)
    else:
        print("IP変化なし: 送信省略")