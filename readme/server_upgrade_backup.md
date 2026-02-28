Taking a backup of a PostgreSQL server is a critical task for any factory environment. You want to ensure that even if the server hardware fails, your production data from PC1, PC2, and QC is safe.

The most common and reliable way to do this in a Linux environment is using the `pg_dump` tool.

### 🏗️ 1. The Manual Backup (Single Database)

If you want to take an immediate backup of your `tyre_factory_db`, run this command in your terminal:

```bash
# -U: Username
# -d: Database Name
# -f: Output file path
pg_dump -U postgres -d tyre_factory_db -f ~/Documents/factory_backup_$(date +%Y-%m-%d).sql

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

This is a common "Schema Migration" challenge. When you have a live PC with old table structures and you want to upgrade them to the new format (adding columns like `core_size` or changing data types) without losing the existing production data, you have two main strategies.

### 🛡️ Strategy 1: The `ALTER` Method (Safest & Fastest)

Instead of deleting and restoring, you simply run SQL commands on the working PC to "patch" the existing tables. This preserves all your old data exactly where it is.

#### **Example: Adding missing columns**

If your new structure added `core_size` to `pc1_building`, run this in `psql`:

```sql
ALTER TABLE pc1_building ADD COLUMN IF NOT EXISTS core_size VARCHAR(50);
ALTER TABLE pc1_building ADD COLUMN IF NOT EXISTS tread_batch VARCHAR(100);

```

#### **Example: Fixing Type Mismatches**

If you need to change a column type (e.g., making a numeric column into a string):

```sql
ALTER TABLE pc2_curing ALTER COLUMN pi_number TYPE VARCHAR(50);

```

---

### 🔄 Strategy 2: The "Export, Drop, Map" Method

Use this if the structural changes are too complex for simple `ALTER` commands. This involves moving the data out, changing the "box," and putting it back in.

#### **Step 1: Export only the Data (Inserts)**

On the working PC, export the data as `INSERT` statements. This ensures the data is captured independently of the table structure.

```bash
pg_dump -U postgres --column-inserts --data-only -t pc1_building tyre_factory_db > old_data.sql

```

#### **Step 2: Update the Structure**

1. Open your `schema.sql` (your new structure file).
2. Run it on the PC to create the new table formats. (You may need to `DROP` the old table or rename it first: `ALTER TABLE pc1_building RENAME TO pc1_old;`).

#### **Step 3: Import and Map**

If you renamed the old table, you can move data internally using SQL. This is the most reliable way to ensure no data is lost:

```sql
-- Move data from the old structure to the new structure
INSERT INTO pc1_building (serial_no, tyre_size, brand, weight)
SELECT serial_no, tyre_size, brand, weight FROM pc1_old;

```

---

### 📋 Checklist for "No-Loss" Integration

1. **Backup First:** Never touch a working PC without running `pg_dump` first. If something goes wrong, you can revert in 60 seconds.
2. **Use `DEFAULT` values:** If you add a new column (like `is_pob`) to a table with 10,000 rows, set a default so the old rows aren't just "NULL":
```sql
ALTER TABLE pc1_building ADD COLUMN is_pob BOOLEAN DEFAULT FALSE;

```


3. **Check Constraints:** Ensure your new structure doesn't have `NOT NULL` requirements on columns that didn't exist in the old data, or the import will fail.

---

### 🏁 Which table is giving you the most trouble?

If you tell me the specific table name and the columns you added/changed, I can give you the **exact SQL script** to run on that PC so you don't have to guess.

**Would you like me to write a "Migration Script" for a specific table?**
