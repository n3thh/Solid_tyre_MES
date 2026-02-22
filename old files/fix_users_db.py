from db_manager import DBManager

def fix_users_table():
    print("--- 🔧 Fixing Users Table Schema ---")

    # 1. Drop the old table (CASCADE to remove any links)
    sql_drop = "DROP TABLE IF EXISTS users CASCADE;"
    
    # 2. Create the CORRECT table
    sql_create = """
    CREATE TABLE users (
        user_id VARCHAR(50) PRIMARY KEY,  -- This was missing!
        full_name VARCHAR(100),
        role VARCHAR(50),                 -- OPERATOR, SUPERVISOR, MANAGER
        is_active BOOLEAN DEFAULT TRUE,   -- Used for Soft Delete
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # 3. Add a default Supervisor for testing
    sql_insert = """
    INSERT INTO users (user_id, full_name, role, is_active)
    VALUES ('SUP-01', 'System Supervisor', 'SUPERVISOR', TRUE);
    """

    if DBManager.execute_query(sql_drop):
        print("🗑️  Old 'users' table dropped.")
    
    if DBManager.execute_query(sql_create):
        print("✅ New 'users' table created with 'user_id' column.")
        
    if DBManager.execute_query(sql_insert):
        print("👤 Default Supervisor (SUP-01) added.")
    else:
        print("❌ Failed to create table.")

if __name__ == "__main__":
    fix_users_table()