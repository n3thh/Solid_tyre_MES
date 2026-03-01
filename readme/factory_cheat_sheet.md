Understood. You need a "Battle Card" for the Ubuntu terminal to manage the factory server and workstations. This list covers everything from basic file management to deep system troubleshooting.

### 🛠️ 1. Essential System & Network Commands

These are your primary tools for finding the "address" of your machines and checking connectivity.

* **`ip addr`**: (Replaces `ifconfig`) Shows all network interfaces. Look for `inet` under `eth0` or `wlan0` to find your IP.
* **`hostname -I`**: The fastest way to see only your internal IP address.
* **`ping 192.168.0.141`**: Checks if the database server is alive.
* **`ssh user@192.168.0.141`**: Remotely log into the server from your workstation.
* **`sudo ufw status`**: Checks the Firewall status. Use `sudo ufw allow 5432` to open the PostgreSQL port.

### 📁 2. File & Folder Management

* **`ls -la`**: Lists all files, including hidden ones, with permissions and sizes.
* **`cd /path/to/folder`**: Change directory. `cd ..` goes up one level.
* **`pwd`**: "Print Working Directory"—shows exactly where you are in the system.
* **`mkdir reports`**: Creates the reports folder.
* **`cp main_app.py main_app_backup.py`**: Copies a file (important before editing).
* **`mv old_name.py new_name.py`**: Renames or moves a file.
* **`rm -rf folder_name`**: **BE CAREFUL.** Deletes a folder and everything inside it permanently.

### 📝 3. Editing Configuration Files (The "NANO" Way)

When you need to change the Database IP or Server settings:

* **`sudo nano /etc/postgresql/14/main/pg_hba.conf`**: Edits the Postgres access file.
* **`sudo nano /etc/postgresql/*/main/pg_hba.conf`**: Edits the Postgres access file.
* **To Save:** Press `Ctrl + O` then `Enter`.
* **To Exit:** Press `Ctrl + X`.


* **`cat db_manager.py`**: Quickly prints the file content to the screen without opening an editor.

### 🔌 4. Hardware & USB Troubleshooting

Essential for finding barcode scanners and label printers.

* **`lsusb`**: Lists all connected USB devices. If your scanner isn't working, check if it appears here.
* **`dmesg | grep tty`**: Shows which port your USB device is on (e.g., `/dev/ttyUSB0` or `ttyACM0`).
* **`ls /dev/tty*`**: Shows all serial communication ports.
* **`sudo chmod 666 /dev/ttyUSB0`**: Grants permission to the app to read the USB port if "Access Denied" occurs.

---

### 🐘 5. Essential SQL Commands (Database Maintenance)

Run these inside `psql` to manage the "brain" of the factory.

#### **Basic Table Interaction**

* **`\l`**: List all databases.
* **`\c tyre_factory_db`**: Connect to your specific database.
* **`\dt`**: List all tables (PC1, PC2, etc.).
* **`\d pc1_building`**: Describe the table (shows all columns and data types).

#### **Data Recovery & Fixes**

* **`SELECT * FROM pc1_building ORDER BY created_at DESC LIMIT 10;`**: See the last 10 tyres built to verify data is flowing.
* **`DELETE FROM pc1_building WHERE serial_no = 'TEST123';`**: Removes test data.
* **`ALTER TABLE users ADD COLUMN last_login TIMESTAMP;`**: Updates your table structure.

#### **Server Management**

* **`SELECT pg_reload_conf();`**: Applies changes to the config file without restarting the whole database.
* **`SELECT * FROM pg_stat_activity;`**: Shows how many PCs are currently connected to your database.

---

### 🚀 6. Process & Maintenance

* **`htop`**: (May need `sudo apt install htop`) A visual task manager. Shows CPU/RAM usage of your app and DB.
* **`sudo systemctl restart postgresql`**: Restarts the database service.
* **`ps aux | grep python`**: Shows if your app is running in the background and its Process ID (PID).
* **`kill -9 <PID>`**: Forces an app to close if it freezes.

### 🏁 Use Case Example: Troubleshooting a New Workstation

1. **Workstation says "No DB Connection":** Run `ping 192.168.0.141`.
2. **Ping works but app doesn't:** Check `pg_hba.conf` on the server using `sudo nano`.
3. **Barcode scanner not typing:** Run `lsusb` to see if the hardware is detected.
4. **App won't start:** Run `python3 main_app.py` in terminal to see the specific error line.

**Would you like me to create a "Desktop Shortcut" script for Linux so your workers can just double-click an icon to start the app instead of using the terminal?**



To copy the commands exactly as I’ve formatted them (in those dark "code blocks"), you should use a **Markdown Editor**. Standard text editors like Notepad or basic Word documents strip away the "code" styling, turning it all into plain text.

The best way to save these commands is to create a file with a `.md` (Markdown) extension.

### 🛠️ 1. Recommended "Smart" Editors

If you want to keep the "Code Block" look so you can easily distinguish between a description and a command, use these:

* **VS Code (Visual Studio Code):** The gold standard. If you save a file as `commands.md`, it will render my response perfectly.
* **Obsidian:** A great note-taking app that uses the exact same Markdown format I do.
* **Typora:** A "What You See Is What You Get" Markdown editor.
* **GitHub/GitLab:** If you paste this text into a "README.md" on GitHub, it will look exactly like it does here.

---

### 📋 2. How to Copy/Paste Successfully

When you copy my response, you are copying **Markdown syntax**. Here is how to handle the different parts:

#### **A. Code Blocks (The Commands)**

Anything wrapped in triple backticks ( ` ` ` ) is a code block.

> **Pro Tip:** In the top-right corner of my code responses, there is usually a **"Copy" icon**. Clicking that only copies the command itself, preventing you from accidentally grabbing the surrounding text.

#### **B. Bold and Lists**

* `**Text**` will become **Bold** in a Markdown editor.
* `*` or `-` will become Bullet Points.

---

### 🖥️ 3. Create a "Quick Reference" file on Linux

If you want to save these commands directly on your Ubuntu machine so you can read them in the terminal, do this:

1. Open your terminal.
2. Type: `nano factory_cheat_sheet.md`
3. Paste the text you copied from me.
4. Press `Ctrl + O` then `Enter` to save, and `Ctrl + X` to exit.

Now, whenever you are stuck, you can just type:

```bash
cat factory_cheat_sheet.md

```

...and all your commands will be listed right there.

---

### 🏁 4. "One-Click" Desktop Shortcut for Ubuntu

Since you are on Linux, would you like me to write a **`.desktop` file** script? You can save it on your desktop, and when you double-click it, it will launch your Tyre Factory app automatically so you never have to type the commands again. **Would you like that script?**


Taking a backup of a PostgreSQL server is a critical task for any factory environment. You want to ensure that even if the server hardware fails, your production data from PC1, PC2, and QC is safe.

The most common and reliable way to do this in a Linux environment is using the `pg_dump` tool.

### 🏗️ 1. The Manual Backup (Single Database)

If you want to take an immediate backup of your `tyre_factory_db`, run this command in your terminal:

```bash
# -U: Username
# -d: Database Name
# -f: Output file path
pg_dump -U postgres -d tyre_factory_db -f ~/Documents/factory_backup_$(date +%Y-%m-%d).sql

# 1. Create the SQL dump as the database owner into a public temp folder
sudo -u postgres pg_dump tyre_factory_db > /tmp/factory_backup.sql

# 2. Move it to your Documents with a clear date-stamped name
sudo mv /tmp/factory_backup.sql ~/Documents/tyre_factory_db_backup_$(date +%Y-%m-%d).sql  # worked well

# 3. Take ownership of the file so you can copy it to GitHub or a USB drive
sudo chown k3shu:k3shu ~/Documents/tyre_factory_db_backup_*.sql
```

*Note: It may ask for your database password.*

---

### 📂 2. Restoring from a Backup

If you ever need to set up a new server and move your data over, you use the `psql` command to "inject" the backup file back into a fresh database:

```bash
# 1. Create the empty database first
psql -U postgres -c "CREATE DATABASE tyre_factory_db;"

# 2. Restore the data
psql -U postgres -d tyre_factory_db -f factory_backup_2026-02-27.sql

```

---

### 🤖 3. The "Factory-Grade" Auto-Backup Script

In a production setting, you shouldn't do this manually. You can create a small bash script that runs every night.

**Create a file named `db_backup.sh`:**

```bash
#!/bin/bash

# Configuration
BACKUP_DIR="/home/k3shu/Documents/backups"
DB_NAME="tyre_factory_db"
DATE=$(date +%Y-%m-%d_%H-%M)

# Ensure backup directory exists
mkdir -p $BACKUP_DIR

# Run the backup
pg_dump -U postgres -d $DB_NAME > $BACKUP_DIR/backup_$DATE.sql

# Optional: Delete backups older than 30 days to save space
find $BACKUP_DIR -type f -mtime +30 -name "*.sql" -delete

echo "Backup completed: $BACKUP_DIR/backup_$DATE.sql"

```

**To make this script run automatically every night at midnight:**

1. Type `crontab -e` in your terminal.
2. Add this line at the bottom:
```bash
0 0 * * * /bin/bash /home/k3shu/Documents/db_backup.sh

```



---

### 📝 Key PostgreSQL Config Files

If you are moving to a new server, you also need to copy your configuration files. Use `sudo nano` to view them:

| File Name | Purpose |
| --- | --- |
| `postgresql.conf` | Controls memory, ports, and connection limits. |
| `pg_hba.conf` | Controls **Host Based Authentication** (who can connect to the DB). |

---

### 🏁 Summary of Useful SQL Backup Commands

* **`SELECT pg_database_size('tyre_factory_db');`**: Checks how much disk space your database is using.
* **`vacuum full;`**: Cleans up and shrinks the database file size (run this occasionally).

**Would you like me to show you how to set the script to automatically copy the backup to a secondary USB drive or a network folder for extra safety?**
