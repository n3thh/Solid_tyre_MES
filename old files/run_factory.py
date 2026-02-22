import psycopg2
from psycopg2.extras import RealDictCursor
import datetime
import sys

# --- CONFIGURATION ---
DB_CONFIG = {
    'dbname': 'factory_production',
    'user': 'factory_admin',
    'password': 'factory123',
    'host': 'localhost',
    'port': '5432'
}

def get_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        return conn
    except Exception as e:
        print(f"❌ Database Connection Failed: {e}")
        sys.exit(1)

# --- HELPER: VERIFY ID EXISTS ---
def verify_id(cursor, table, column, value, prompt_name):
    query = f"SELECT 1 FROM {table} WHERE {column} = %s"
    cursor.execute(query, (value,))
    if cursor.fetchone():
        return True
    print(f"❌ Error: {prompt_name} '{value}' not found in {table}.")
    return False

# ==========================================
# 🏭 STATION 1: BUILD (PC1)
# ==========================================
def run_pc1():
    print("\n--- 🏭 PC1: BUILD STATION ---")
    conn = get_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    op_id = input("Operator ID: ").strip()
    if not verify_id(cursor, "users", "user_id", op_id, "User"): return

    print("\n--- Select Product ---")
    cursor.execute("SELECT sku_id, brand_name, size_spec FROM master_sku")
    products = cursor.fetchall()
    for p in products:
        print(f"[{p['sku_id']}] {p['brand_name']} {p['size_spec']}")
    
    try:
        sku_id = int(input("Enter SKU ID: "))
    except ValueError: return

    b_id = f"GT-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    machine = input("Building Machine ID: ").strip()
    batch_c = input("Core Batch: ")
    batch_m = input("Middle Batch: ")
    batch_t = input("Tread Batch: ")
    
    try:
        w_green = float(input("Green Weight (kg): "))
        w_flash = float(input("Flash Weight (kg): "))
    except ValueError:
        print("❌ Weight must be a number.")
        return

    try:
        cursor.execute('''
            INSERT INTO pc1_building (
                b_id, sku_id, operator_id, machine_id, 
                batch_core, batch_mid, batch_tread, 
                weight_green, weight_flash, qc_status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'OK')
        ''', (b_id, sku_id, op_id, machine, batch_c, batch_m, batch_t, w_green, w_flash))
        
        print(f"\n✅ GREEN TYRE BUILT: {b_id}")
        print("👉 Write this on the Green Tyre Tag.")
    except Exception as e:
        print(f"❌ Error: {e}")
    conn.close()

# ==========================================
# ♨️ STATION 2: CURING PRESS (PC2-A)
# ==========================================
def run_press():
    print("\n--- ♨️ PC2: PRESS STATION ---")
    conn = get_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    op_id = input("Operator ID: ").strip()
    if not verify_id(cursor, "users", "user_id", op_id, "User"): return

    press_id = input("Press ID (e.g. P-03): ").strip()
    if not verify_id(cursor, "machines", "machine_id", press_id, "Press"): return

    b_id = input("Scan Green Tyre Label: ").strip()
    
    cursor.execute('''
        SELECT m.oven_cure_min, m.size_spec 
        FROM pc1_building b
        JOIN master_sku m ON b.sku_id = m.sku_id
        WHERE b.b_id = %s
    ''', (b_id,))
    result = cursor.fetchone()
    
    if not result:
        print("❌ Error: Green Tyre not found!")
        return
        
    needs_oven = result['oven_cure_min'] > 0
    print(f"ℹ️  Product: {result['size_spec']}")
    print(f"ℹ️  Oven Required: {'YES' if needs_oven else 'NO'}")

    serial_no = input("Enter STENCIL Serial No: ").strip()
    # FIX: .title() forces "TOP" to "Top" to match Database Constraint
    cavity = input("Cavity (Top/Bot/Single): ").strip().title()

    try:
        cursor.execute('''
            INSERT INTO pc2_curing (
                serial_no, b_id, press_id, cavity_pos, 
                press_start_time, is_oven_required, status, operator_id
            ) VALUES (%s, %s, %s, %s, NOW(), %s, %s, %s)
        ''', (serial_no, b_id, press_id, cavity, needs_oven, 
              'Ready for Oven' if needs_oven else 'Done', op_id))
        
        print(f"\n✅ PRESS STARTED: {serial_no}")
        print("👉 Apply Stencil. Remove Paper Label.")
    except Exception as e:
        print(f"❌ Error: {e}")
    conn.close()

# ==========================================
# 🔥 STATION 3: OVEN LOADING (PC2-B)
# ==========================================
def run_oven():
    print("\n--- 🔥 OVEN LOADING STATION ---")
    conn = get_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    print("\n📋 Tyres Waiting for Oven:")
    cursor.execute("SELECT serial_no, press_id FROM pc2_curing WHERE status='Ready for Oven'")
    waiting = cursor.fetchall()
    
    if not waiting:
        print("   (No tyres waiting)")
        return

    for t in waiting:
        print(f"   [ ] {t['serial_no']} (from {t['press_id']})")

    print("\nENTER Serial Numbers to load into Oven (comma separated):")
    selection = input(">> ").strip()
    
    if not selection: return
    
    serials = [s.strip() for s in selection.split(',')]
    oven_batch = f"OV-{datetime.datetime.now().strftime('%H%M%S')}"

    count = 0
    for s in serials:
        cursor.execute('''
            UPDATE pc2_curing 
            SET status='In Oven', oven_start_time=NOW(), oven_batch_id=%s 
            WHERE serial_no=%s AND status='Ready for Oven'
        ''', (oven_batch, s))
        count += cursor.rowcount
    
    print(f"\n✅ LOADED {count} tyres into Batch {oven_batch}")
    conn.close()

# ==========================================
# 🔍 STATION 4: QC (PC3)
# ==========================================
def run_qc():
    print("\n--- 🔍 QC STATION ---")
    conn = get_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    insp_id = input("Inspector ID: ").strip()
    if not verify_id(cursor, "users", "user_id", insp_id, "User"): return

    serial_no = input("Scan Serial No: ").strip()
    
    cursor.execute("SELECT status FROM pc2_curing WHERE serial_no=%s", (serial_no,))
    tyre = cursor.fetchone()
    if not tyre:
        print("❌ Tyre not found.")
        return
    
    print(f"ℹ️  Current Status: {tyre['status']}")

    status = input("Verdict (PASS/FAIL): ").upper()
    grade = input("Grade (A/B/SCRAP): ").upper()
    
    defect = None
    if status == 'FAIL':
        defect = input("Defect Code (e.g. D-01): ")

    try:
        cursor.execute('''
            INSERT INTO pc3_qc (
                serial_no, status, grade, defect_code, inspector_id
            ) VALUES (%s, %s, %s, %s, %s)
        ''', (serial_no, status, grade, defect, insp_id))
        
        cursor.execute("UPDATE pc2_curing SET status='QC Done' WHERE serial_no=%s", (serial_no,))
        
        print("\n✅ QC SAVED.")
    except Exception as e:
        print(f"❌ Error: {e}")
    conn.close()

while True:
    print("\n==============================")
    print("   🏭 SOLID TYRE FACTORY OS   ")
    print("==============================")
    print("1. Build Tyre (PC1)")
    print("2. Start Press (PC2-A)")
    print("3. Load Oven (PC2-B)")
    print("4. Final QC (PC3)")
    print("q. Quit")
    
    choice = input("Select >> ")
    
    if choice == '1': run_pc1()
    elif choice == '2': run_press()
    elif choice == '3': run_oven()
    elif choice == '4': run_qc()
    elif choice == 'q': break