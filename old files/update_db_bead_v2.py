from db_manager import DBManager

def update_bead_schema_v2():
    print("--- 🔧 Updating Bead Master Schema (Mould-Specific) ---")

    # 1. Drop the old table because the Primary Key structure needs to change
    # (Old PK was just tyre_size, New PK needs tyre_size + mould_id)
    drop_sql = "DROP TABLE IF EXISTS bead_master;"
    
    # 2. Create the new table structure
    # We use mould_id with DEFAULT '' (empty string) to handle the "Generic" case 
    # This allows it to be part of the Primary Key
    create_sql = """
    CREATE TABLE bead_master (
        tyre_size VARCHAR(50),
        mould_id VARCHAR(50) DEFAULT '', 
        bead_size VARCHAR(50),
        bead_count INT DEFAULT 0,
        weight_per_bead DECIMAL(10,3) DEFAULT 0.0,
        core_size_ref VARCHAR(50), -- Storing for reference
        
        PRIMARY KEY (tyre_size, mould_id)
    );
    """

    if DBManager.execute_query(drop_sql):
        print("🗑️  Old 'bead_master' table dropped.")
    
    if DBManager.execute_query(create_sql):
        print("✅ New 'bead_master' table created with Mould ID & Weight support.")
    else:
        print("❌ Failed to create table.")

if __name__ == "__main__":
    update_bead_schema_v2()