from db_manager import DBManager

def check_system():
    print("--- 1. CHECKING OPERATORS ---")
    # Building App looks for: role='OPERATOR' and is_active=TRUE
    ops = DBManager.fetch_data("SELECT user_id, full_name, role FROM users")
    if not ops:
        print("❌ TABLE 'users' IS EMPTY!")
    else:
        for op in ops:
            status = "✅ VISIBLE" if op[2] == 'OPERATOR' else "❌ HIDDEN (Wrong Role)"
            print(f"User: {op[1]} | Role: {op[2]} -> {status}")

    print("\n--- 2. CHECKING PRODUCTION PLAN ---")
    # Building App looks for any row in production_plan
    plans = DBManager.fetch_data("SELECT press_id, tyre_size FROM production_plan")
    if not plans:
        print("❌ TABLE 'production_plan' IS EMPTY!")
    else:
        print(f"✅ Found {len(plans)} Active Plans.")

    print("\n--- 3. CHECKING MATERIALS (BATCHES) ---")
    # Building App looks for: status='APPROVED'
    mats = DBManager.fetch_data("SELECT batch_no, material_type, status FROM raw_material_qc")
    if not mats:
        print("❌ TABLE 'raw_material_qc' IS EMPTY!")
    else:
        for m in mats:
            status_check = "✅ VISIBLE" if m[2] == 'APPROVED' else f"❌ HIDDEN (Status is '{m[2]}', needs 'APPROVED')"
            print(f"Batch: {m[0]} | Type: {m[1]} | Status: {m[2]} -> {status_check}")

if __name__ == "__main__":
    check_system()