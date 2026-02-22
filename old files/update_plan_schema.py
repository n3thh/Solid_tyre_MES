from db_manager import DBManager

def update_plan_schema():
    print("--- 🔧 Updating Production Plan Schema ---")

    # 1. Add New Columns to Production Plan
    # We use ALTER to add them safely
    alter_cmds = [
        "ALTER TABLE production_plan ADD COLUMN IF NOT EXISTS type VARCHAR(50);",          # CUSHION / POB
        "ALTER TABLE production_plan ADD COLUMN IF NOT EXISTS tyre_weight DECIMAL(10,2);"  # Target Weight (Kg)
    ]

    for cmd in alter_cmds:
        try:
            DBManager.execute_query(cmd)
            print(f"✅ Executed: {cmd}")
        except Exception as e:
            print(f"⚠️ Note: {e}")

    # 2. Clear Old Plan Data (To prevent mix-ups with new format)
    if DBManager.execute_query("DELETE FROM production_plan;"):
        print("🗑️  Old Plan data cleared. Please Upload New Plan CSV.")

if __name__ == "__main__":
    update_plan_schema()