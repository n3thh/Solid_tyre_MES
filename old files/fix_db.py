from db_manager import DBManager

def fix_pc1_table():
    print("--- 🔧 Fixing PC1 Table Schema ---")

    # 1. Drop the old table using CASCADE (Forces removal even if linked)
    sql_drop = "DROP TABLE IF EXISTS pc1_building CASCADE;"
    
    # 2. Create the CORRECT table
    sql_create = """
    CREATE TABLE pc1_building (
        b_id VARCHAR(50) PRIMARY KEY,
        press_id VARCHAR(50),
        daylight VARCHAR(50),
        tyre_size VARCHAR(50),
        core_size VARCHAR(50),
        brand VARCHAR(50),
        pattern VARCHAR(50),
        quality VARCHAR(50),
        mould_id_marks VARCHAR(100),
        
        -- Multi-Batch Support
        core_batch TEXT,
        mid_batch TEXT,
        tread_batch TEXT,
        
        tread_type VARCHAR(50),
        green_tyre_weight DECIMAL(10,2),
        operator_id VARCHAR(50),
        shift VARCHAR(10),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    if DBManager.execute_query(sql_drop):
        print("🗑️  Old table dropped (Cascade).")
    
    if DBManager.execute_query(sql_create):
        print("✅ New table 'pc1_building' created successfully.")
    else:
        print("❌ Failed to create table.")

if __name__ == "__main__":
    fix_pc1_table()