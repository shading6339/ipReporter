# 🛰️ ipReporter

`ipReporter` は、サーバや端末の IP アドレスを Firebase Firestore に定期送信するための簡易レポーターツールです。  
例えば、研究室内で複数台の機器のローカルIPを監視・表示したい場合などに利用できます。

## ✅ 機能

- サーバのローカルIPを 1分ごとに Firebase Firestore に自動送信
- IPアドレスが変更されたときのみ送信（差分検知）
- systemdタイマーで自動実行（再起動後も自動復旧）
- Firebase Admin SDK を用いた安全な送信
- 仮想環境による依存管理
- ログ・状態の確認が容易

---

## 📦 セットアップ手順

### 1. Firebase プロジェクトを作成

- [Firebase コンソール](https://console.firebase.google.com/) でプロジェクトを作成
- Firestore データベースを「**ネイティブモード / Standard Edition**」で有効化（[こちらから直接作成](https://console.cloud.google.com/datastore/setup)）

> ⚠️ Firestore を有効化しないと動作しません。

---

### 2. サービスアカウントキー（秘密鍵）の作成

1. Firebase コンソール > ⚙️ プロジェクト設定 > サービスアカウント
2. 「新しい秘密鍵を生成」 > `*.json` ファイルをダウンロード
3. Gitに含めないよう `.gitignore` を確認：

```gitignore
*.json
```

---

### 3. セットアップスクリプトの実行

```bash
git clone https://github.com/yourname/ipReporter.git
cd ipReporter
chmod +x install-ip-reporter.sh
./install-ip-reporter.sh /path/to/your-service-account.json
```

> 📁 鍵ファイルは `/etc/firebase/` に安全にコピーされ、以降はそこから読み取られます。

---

## 🔒 セキュリティについて

このツールは Firebase Admin SDK を使用します。**サービスアカウント鍵は「万能な管理鍵」であり、取り扱いには細心の注意が必要です。**

### ✅ 安全設計（このツールでの対策）

- 鍵ファイルは `/etc/firebase/` に配置
- パーミッションは `chmod 600`、所有者は `root` に制限
- Git には絶対に含めない（`.gitignore` 済み）
- `report_ip.py` は鍵のファイル名を固定せず、自動検出
- systemd + 仮想環境により外部パッケージの競合も回避

### 💡 運用上の注意

- 鍵ファイルが漏洩したら即時無効化し、再発行してください
- 本ツールは**内部ネットワーク利用**を前提としています。WAN越しの運用には追加の防御策が必要です
- 個別管理をしたい場合は、マシンごとに鍵を発行してください（IAM制御も可能）

---

## 📄 Firestore 構成（自動）

以下のように `hosts` コレクションが作成されます：

```
hosts/
└── <hostname>（例：irLab1607）
    ├── ip: "192.168.0.123"
    └── updated_at: "2025-04-21T12:34:56.789"
```

> Firestore に事前にコレクションを作成する必要はありません。

---

## 🔁 アンインストール

```bash
chmod +x uninstall-ip-reporter.sh
./uninstall-ip-reporter.sh
```

これにより、systemdのサービス・タイマー、仮想環境、鍵ファイルが削除されます。

---

## 📡 今後の拡張例

- Web UI や キオスク表示によるIP一覧表示
- IP履歴の保存・グラフ化
- Discord通知などのWebhook連携
- サーバ識別タグ、メタデータの追加保存

---

## 👤 ライセンス・貢献

MIT ライセンス（または自由に設定可）  
不具合報告や改善提案は Issue/Pull Request 大歓迎です！