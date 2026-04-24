# 🛡️ Project Obsidian

**Project Obsidian** is a lightweight Windows security tool that monitors active network connections and gives you direct control over unknown or suspicious activity in real time.

Instead of blindly trusting system processes or relying on signatures, Obsidian puts the decision in your hands.

---

## ⚡ Features

* 🔍 **Real-time network monitoring**
* 🚨 **User-prompted alerts for unknown connections**
* 🧠 **Manual trust model (no automatic whitelisting)**
* 🗂️ **SQLite database for efficient tracking**
* ⛔ **Blacklist / Whitelist / Kill actions**
* 💤 **Temporary ignore system (cooldown-based)**
* 📊 **CSV reporting and export**
* 🔐 **Runs with admin privileges for deeper visibility**
* 🖥️ **Native Windows toast notifications**

---

## 🧩 How It Works

1. Scans active network connections using system-level access
2. Matches each connection against a local database
3. If unknown or suspicious:

   * Prompts the user via a Windows notification
4. User chooses an action:

   * ✅ Whitelist
   * ⛔ Blacklist
   * 💀 Kill Process
   * 💤 Ignore (temporary)

All decisions are stored locally and used in future scans.

---

## 📁 Project Structure

```
Project Obsidian/
│
├── project_obsidian.py     # Main entry point
├── scripts/
│   ├── network.py          # Connection scanning logic
│   ├── alerts.py           # Notification + user interaction
│   ├── db.py               # SQLite database management
│   ├── reports.py          # CSV export/reporting
│   ├── installer.py        # Setup & environment checks
│   └── utils.py            # Shared helpers/logging
```

---

## 🛠️ Installation (Source)

### Requirements

* Python 3.10+
* Windows OS

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run

```bash
python project_obsidian.py
```

---

## 📦 Build (Executable)

```bash
python -m PyInstaller --onefile --noconsole --uac-admin ^
  --hidden-import win11toast ^
  --collect-all win11toast ^
  project_obsidian.py
```

> ⚠️ If using PowerShell, replace `^` with `` ` ``

---

## 📊 Database

* Uses **SQLite3**
* Stores:

  * Process name & path
  * Ports and remote IP
  * Connection state
  * User decisions (whitelist / blacklist / ignore)

Designed to scale efficiently with large connection histories.

---

## ⚠️ Safety Notes

* Obsidian **does not auto-trust system processes**
* Users are responsible for decisions made
* Blacklisting critical processes **may impact system stability**
* Tool does **not modify firewall rules (yet)** — only monitors and reacts

---

## 🚧 Current Limitations

* No automatic threat scoring (manual review required)
* No persistent startup mode (intentional safety decision)
* No digital signature verification yet
* No firewall-level blocking (future feature)

---

## 🔮 Planned Features

* 🧠 Heuristic / risk scoring system
* 🔐 Process signature verification (trusted publishers)
* 🌐 IP reputation checks
* 🔥 Firewall integration (true blocking)
* 🖥️ GUI dashboard
* 📱 Remote notifications (optional)

---

## 🧑‍💻 Why This Exists

Most tools either:

* trust too much (whitelist system processes automatically), or
* overwhelm users with noise

Project Obsidian is built around one idea:

> **You should see what’s happening — and decide what to trust.**

---

## 📜 License

MIT License (or update as needed)

---

## 👤 Author

Built by Samuel Rodriguez
Focused on practical security, automation, and real-world tools.

---
