#!/usr/bin/env python3

import os
import glob
import socket
import datetime
import platform
import subprocess

import firebase_admin
from firebase_admin import credentials, firestore

# ===============================
# 🔑 Firebase 初期化
# ===============================
FIREBASE_KEY_DIR = "/etc/firebase"
json_files = glob.glob(os.path.join(FIREBASE_KEY_DIR, "*.json"))

if not json_files:
    raise FileNotFoundError(f"サービスアカウントキーが {FIREBASE_KEY_DIR} に存在しません")

SERVICE_ACCOUNT_PATH = json_files[0]

if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ===============================
# 🧠 システム情報取得関数
# ===============================

def get_ipv4():
    ip_list = os.popen("hostname -I").read().strip().split()
    for ip in ip_list:
        if "." in ip:
            return ip
    return "0.0.0.0"

def get_ipv6():
    output = os.popen("ip -6 addr show scope global").read()
    lines = [line.strip() for line in output.splitlines()]
    addrs = [line.split()[1] for line in lines if "inet6" in line]
    return addrs[0] if addrs else "N/A"

def get_macaddress():
    try:
        mac = open('/sys/class/net/$(ip route show default | awk \'/default/ {print $5}\')/address').read().strip()
        return mac
    except:
        import uuid
        return ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(40, -1, -8)])

def get_cpu_info():
    try:
        if platform.system() == "Darwin":
            return subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"]).decode().strip()
        else:
            output = subprocess.check_output("lscpu", shell=True).decode()
            for line in output.splitlines():
                if "Model name:" in line:
                    return line.split(":")[1].strip()
    except:
        return platform.processor() or "N/A"

def get_gpu_info():
    try:
        if platform.system() == "Darwin":
            output = subprocess.check_output(["system_profiler", "SPDisplaysDataType"]).decode()
            for line in output.splitlines():
                if "Chipset Model" in line or "Graphics" in line:
                    return line.split(":")[-1].strip()
        else:
            output = subprocess.check_output("nvidia-smi --query-gpu=name --format=csv,noheader", shell=True).decode()
            return output.strip()
    except:
        return "None"

def get_memory_mb():
    try:
        if platform.system() == "Darwin":
            output = subprocess.check_output(["sysctl", "-n", "hw.memsize"]).decode()
            return int(int(output.strip()) / (1024 * 1024))
        else:
            output = subprocess.check_output("free -m", shell=True).decode()
            for line in output.splitlines():
                if "Mem:" in line:
                    return int(line.split()[1])
    except:
        return -1

def get_uptime_sec():
    try:
        if platform.system() == "Darwin":
            output = subprocess.check_output(["sysctl", "-n", "kern.boottime"]).decode()
            import time, re
            sec = int(re.search(r"sec = (\d+)", output).group(1))
            return int(time.time()) - sec
        else:
            with open('/proc/uptime', 'r') as f:
                return int(float(f.readline().split()[0]))
    except:
        return -1

def get_os_info():
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "hostname": socket.gethostname()
    }

# ===============================
# 🔁 差分検知
# ===============================
IP_FILE = "/tmp/last_ipv4.txt"

def get_last_ipv4():
    if os.path.exists(IP_FILE):
        with open(IP_FILE, "r") as f:
            return f.read().strip()
    return ""

def save_ipv4(ip):
    with open(IP_FILE, "w") as f:
        f.write(ip)

# ===============================
# 🔄 Firestore 書き込み
# ===============================
def update_firestore(ipv4):
    now = datetime.datetime.now().isoformat()
    hostname = socket.gethostname()

    data = {
        "ipv4": ipv4,
        "ipv6": get_ipv6(),
        "macaddress": get_macaddress(),
        "cpu": get_cpu_info(),
        "gpu": get_gpu_info(),
        "memory_mb": get_memory_mb(),
        "uptime_sec": get_uptime_sec(),
        "tag": "lab-kiosk",
        "updated_at": now,
        "os": get_os_info()
    }

    # 最新情報を更新
    db.collection("hosts").document(hostname).set(data, merge=True)

    # 履歴ログ（サブコレクション）
    db.collection("history").document(hostname).collection("logs").document(now).set({
        "ipv4": ipv4,
        "ipv6": data["ipv6"],
        "macaddress": data["macaddress"],
        "timestamp": now,
        "cpu": data["cpu"],
        "gpu": data["gpu"],
        "uptime_sec": data["uptime_sec"]
    })

    print(f"[{now}] IPv4更新: {hostname} = {ipv4}")

# ===============================
# ▶️ メイン
# ===============================
if __name__ == "__main__":
    current_ipv4 = get_ipv4()
    last_ipv4 = get_last_ipv4()

    if current_ipv4 != last_ipv4:
        update_firestore(current_ipv4)
        save_ipv4(current_ipv4)
    else:
        print("IPv4変化なし: 送信省略")