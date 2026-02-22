from db_manager import DBManager

def update_schema_final():
    print("--- 🔧 Final Database Update (Specs + POB + Gum) ---")

    # 1. Create Tyre Specs Table (The Recipe)
    sql_specs = """
    CREATE TABLE IF NOT EXISTS tyre_specs (
        spec_id SERIAL PRIMARY KEY,
        tyre_size VARCHAR(50),
        quality VARCHAR(50),      -- e.g., 'Premium', 'Standard'
        
        -- Construction Flags
        is_pob BOOLEAN DEFAULT FALSE,  -- TRUE for POB (Requires Gum)
        
        -- Material Weights (Kg)
        bead_weight DECIMAL(10,3),    -- Weight per bead
        bead_count INT,               -- Number of beads
        bead_size VARCHAR(50),        -- Text description (e.g. '8 inch')
        
        -- Percentage Splits (Total = 100%)
        core_pct DECIMAL(5,2),
        mid_pct DECIMAL(5,2),
        ct_pct DECIMAL(5,2),
        gum_pct DECIMAL(5,2),         -- New: Bonding Gum %
        tread_pct DECIMAL(5,2),
        
        drum_size VARCHAR(100),       -- Instruction
        UNIQUE(tyre_size, quality)
    );
    """

    # 2. Update PC1 Table (The Log)
    # We add columns for the new data points
    alter_cmds = [
        "ALTER TABLE pc1_building ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'COMPLETED';",
        "ALTER TABLE pc1_building ADD COLUMN IF NOT EXISTS ct_batch TEXT;",
        "ALTER TABLE pc1_building ADD COLUMN IF NOT EXISTS gum_batch TEXT;",  # <-- New Gum Field
        "ALTER TABLE pc1_building ADD COLUMN IF NOT EXISTS is_pob BOOLEAN DEFAULT FALSE;",
        "ALTER TABLE pc1_building ADD COLUMN IF NOT EXISTS birth_time TIMESTAMP;",
        "ALTER TABLE pc1_building ADD COLUMN IF NOT EXISTS final_weight DECIMAL(10,2);"
    ]

    # Execute
    if DBManager.execute_query(sql_specs):
        print("✅ Table 'tyre_specs' created.")
    
    for cmd in alter_cmds:
        try:
            DBManager.execute_query(cmd)
        except Exception as e:
            print(f"⚠️ Note: {e}")
            
    print("✅ PC1 Table updated with Gum & POB columns.")

    # 3. Add Dummy Specs (Standard vs POB)
    # Standard 18x7-8
    sql_std = """
    INSERT INTO tyre_specs (tyre_size, quality, is_pob, bead_weight, bead_count, bead_size, core_pct, mid_pct, tread_pct)
    VALUES ('18x7-8', 'Premium', FALSE, 0.25, 2, '8 inch', 54.0, 5.0, 35.0)
    ON CONFLICT DO NOTHING;
    """
    
    # POB 22x10x16 (Example)
    sql_pob = """
    INSERT INTO tyre_specs (tyre_size, quality, is_pob, gum_pct, ct_pct, tread_pct)
    VALUES ('22x10x16', 'Premium', TRUE, 2.0, 10.0, 88.0)
    ON CONFLICT DO NOTHING;
    """
    
    DBManager.execute_query(sql_std)
    DBManager.execute_query(sql_pob)
    print("✅ Dummy Specs added (1 Standard, 1 POB).")

if __name__ == "__main__":
    update_schema_final()