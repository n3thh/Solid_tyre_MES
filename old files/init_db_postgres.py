import psycopg2
from psycopg2 import sql
import pandas as pd
import os
import sys

# --- CONFIGURATION ---
DB_CONFIG = {
    'dbname': 'factory_production',
    'user': 'factory_admin',
    'password': 'factory123',
    'host': 'localhost',
    'port': '5432'
}

DATA_DIR = "data"
CSV_FILES = {
    "master_sku": "master_products.csv",
    "defect_codes": "defect_codes.csv",
    "machines": "machines.csv",
    "users": "users.csv"
}

def create_schema():
    print("🐘 Connecting to PostgreSQL...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True 
        cursor = conn.cursor()
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        sys.exit(1)

    print(f"🔧 Building Database Schema...")

    # --- DROP TABLES (Cascade deletes dependants) ---
    tables = ['pc3_qc', 'pc2_curing', 'pc1_building', 'master_sku', 'users', 'machines', 'defect_codes']
    for t in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {t} CASCADE;")

    # --- CREATE TABLES ---
    
    # 1. Users
    cursor.execute('''CREATE TABLE users (
        user_id VARCHAR(20) PRIMARY KEY,
        full_name VARCHAR(100),
        role VARCHAR(50),
        pin_code INTEGER
    );''')

    # 2. Machines
    cursor.execute('''CREATE TABLE machines (
        machine_id VARCHAR(20) PRIMARY KEY,
        type VARCHAR(50),
        capacity VARCHAR(50),
        location VARCHAR(100)
    );''')

    # 3. Defect Codes
    cursor.execute('''CREATE TABLE defect_codes (
        code VARCHAR(20) PRIMARY KEY,
        description VARCHAR(255),
        category VARCHAR(50),
        severity VARCHAR(50)
    );''')

    # 4. Master SKU
    cursor.execute('''CREATE TABLE master_sku (
        sku_id INTEGER PRIMARY KEY,
        brand_name VARCHAR(100),
        size_spec VARCHAR(100),
        lug_type VARCHAR(50),
        compound_type VARCHAR(50),
        target_weight_kg DECIMAL(10,2),
        press_cure_min INTEGER,
        oven_cure_min INTEGER
    );''')

    # 5. PC1: Building
    cursor.execute('''CREATE TABLE pc1_building (
        b_id VARCHAR(50) PRIMARY KEY,
        build_date DATE DEFAULT CURRENT_DATE,
        build_time TIME DEFAULT CURRENT_TIME,
        sku_id INTEGER REFERENCES master_sku(sku_id),
        operator_id VARCHAR(20) REFERENCES users(user_id),
        shift VARCHAR(10),
        machine_id VARCHAR(20),
        batch_core VARCHAR(50),
        batch_mid VARCHAR(50),
        batch_tread VARCHAR(50),
        weight_green DECIMAL(10,2),
        weight_flash DECIMAL(10,2),
        qc_status VARCHAR(20),
        remarks TEXT
    );''')

    # 6. PC2: Curing
    cursor.execute('''CREATE TABLE pc2_curing (
        serial_no VARCHAR(50) PRIMARY KEY,
        b_id VARCHAR(50) UNIQUE REFERENCES pc1_building(b_id),
        press_id VARCHAR(20) REFERENCES machines(machine_id),
        cavity_pos VARCHAR(20) CHECK (cavity_pos IN ('Top', 'Bot', 'Single')),
        press_start_time TIMESTAMP,
        press_end_time TIMESTAMP,
        is_oven_required BOOLEAN DEFAULT FALSE,
        oven_batch_id VARCHAR(50),
        oven_start_time TIMESTAMP,
        oven_end_time TIMESTAMP,
        status VARCHAR(50) DEFAULT 'In Press',
        operator_id VARCHAR(20) REFERENCES users(user_id)
    );''')

    # 7. PC3: QC
    cursor.execute('''CREATE TABLE pc3_qc (
        qc_id SERIAL PRIMARY KEY,
        serial_no VARCHAR(50) REFERENCES pc2_curing(serial_no),
        qc_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status VARCHAR(20),
        grade VARCHAR(20),
        defect_code VARCHAR(20) REFERENCES defect_codes(code),
        hardness INTEGER,
        final_weight DECIMAL(10,2),
        inspector_id VARCHAR(20) REFERENCES users(user_id)
    );''')

    print("✅ Schema Built Successfully (PostgreSQL).")
    return conn

def import_csv_data(conn):
    print("\n📥 Importing CSVs into PostgreSQL...")
    cursor = conn.cursor()
    
    for table, filename in CSV_FILES.items():
        file_path = os.path.join(DATA_DIR, filename)
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)
                
                # --- NEW ROBUST CLEANING METHOD ---
                # 1. Strip whitespace from headers
                df.columns = df.columns.str.strip()
                
                # 2. Strip whitespace from all TEXT columns (Works on all Pandas versions)
                for col in df.select_dtypes(['object']):
                    df[col] = df[col].str.strip()
                # ----------------------------------

                # Prepare data for Postgres
                cols = ', '.join(df.columns)
                placeholders = ', '.join(['%s'] * len(df.columns))
                
                # Handle NaN (Empty cells) by converting to None for SQL
                df = df.where(pd.notnull(df), None)
                data = [tuple(row) for row in df.to_numpy()]
                
                # Insert
                query = f"INSERT INTO {table} ({cols}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
                cursor.executemany(query, data)
                
                print(f"   👉 Imported {len(data)} rows into '{table}'")
            except Exception as e:
                print(f"   ❌ Error {filename}: {e}")
        else:
            print(f"   ⚠️ Missing: {filename}")

if __name__ == "__main__":
    connection = create_schema()
    import_csv_data(connection)
    connection.close()
    print("\n🚀 SYSTEM RESET COMPLETE.")