from db_manager import DBManager

def diagnose_tables():
    tables = ["production_plan", "pc1_building", "master_orders"]
    
    print("\n🔍 --- DATABASE STRUCTURE DIAGNOSTIC ---")
    for table in tables:
        print(f"\n📋 Table: {table}")
        # This query works specifically for PostgreSQL
        q = f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table}'
            ORDER BY ordinal_position;
        """
        columns = DBManager.fetch_data(q)
        if columns:
            for col in columns:
                print(f"   - {col[0]} ({col[1]})")
        else:
            print(f"   ❌ Table '{table}' not found!")
    print("\n----------------------------------------")

if __name__ == "__main__":
    diagnose_tables()
