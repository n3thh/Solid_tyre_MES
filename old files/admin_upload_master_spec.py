from db_manager import DBManager

def fix_master_spec_db():
    print("--- 🔧 Fixing Master Spec Table ---")

    # 1. Drop old spec table (it was based on Size+Quality, now we want Grade-based)
    DBManager.execute_query("DROP TABLE IF EXISTS tyre_specs CASCADE;")

    # 2. Create New Master Spec Table
    sql_create = """
    CREATE TABLE tyre_specs (
        grade VARCHAR(50) PRIMARY KEY,  -- e.g., 'VST01', 'V3P02'
        
        -- Percentages (Total should be ~100%)
        bead_weight DECIMAL(5,3),       -- Fixed deduction (e.g. 0.5kg)
        core_pct DECIMAL(5,2),
        mid_pct DECIMAL(5,2),
        ct_pct DECIMAL(5,2),
        tread_pct DECIMAL(5,2),
        gum_pct DECIMAL(5,2),
        
        is_pob BOOLEAN DEFAULT FALSE
    );
    """
    
    # 3. Create Bead Master Table (Size based)
    # Since Bead Count depends on Size, not just Grade
    sql_bead = """
    CREATE TABLE IF NOT EXISTS bead_master (
        tyre_size VARCHAR(50) PRIMARY KEY,
        bead_size VARCHAR(50),
        bead_count INT
    );
    """

    if DBManager.execute_query(sql_create):
        print("✅ New 'tyre_specs' table created (Grade-based).")
        
    if DBManager.execute_query(sql_bead):
        print("✅ New 'bead_master' table created.")

if __name__ == "__main__":
    fix_master_spec_db()