import psycopg2
from psycopg2.extras import RealDictCursor
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
        return conn
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        sys.exit(1)

def show_traceability():
    conn = get_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    print("\n========================================")
    print("   📊 FACTORY PRODUCTION REPORT        ")
    print("========================================")
    
    # We join all 3 tables to show the full life of the tyre
    query = '''
        SELECT 
            pc3.qc_time,
            pc2.serial_no,
            pc2.b_id,
            sku.size_spec,
            pc2.press_id,
            pc2.oven_batch_id,
            pc3.status as qc_verdict,
            pc3.grade
        FROM pc3_qc pc3
        JOIN pc2_curing pc2 ON pc3.serial_no = pc2.serial_no
        JOIN pc1_building pc1 ON pc2.b_id = pc1.b_id
        JOIN master_sku sku ON pc1.sku_id = sku.sku_id
        ORDER BY pc3.qc_time DESC
    '''
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    if not rows:
        print("No completed tyres found yet.")
    else:
        print(f"{'TIME':<20} | {'SERIAL':<10} | {'SIZE':<15} | {'PRESS':<6} | {'OVEN BATCH':<10} | {'QC'}")
        print("-" * 90)
        for r in rows:
            print(f"{str(r['qc_time'])[:19]:<20} | {r['serial_no']:<10} | {r['size_spec']:<15} | {r['press_id']:<6} | {r['oven_batch_id'] or 'N/A':<10} | {r['qc_verdict']} ({r['grade']})")

    print("\n")
    conn.close()

if __name__ == "__main__":
    show_traceability()