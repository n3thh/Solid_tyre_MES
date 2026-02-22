import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
from db_manager import DBManager
try:
    from modules.order_parser import SmartOrderParser
except ImportError:
    SmartOrderParser = None

class AdminDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin | Factory Data Center")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f4f6f7")

        # Styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=5)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=25)

        # Header
        tk.Label(root, text="⚙️ SYSTEM ADMINISTRATION & MASTER DATA", font=("Segoe UI", 18, "bold"), bg="#f4f6f7", fg="#2c3e50").pack(pady=15)

        # Tabs
        nb = ttk.Notebook(root)
        nb.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.tab_users = tk.Frame(nb, bg="white")
        self.tab_qc = tk.Frame(nb, bg="white")
        self.tab_plan = tk.Frame(nb, bg="white")
        self.tab_spec = tk.Frame(nb, bg="white")
        self.tab_bead = tk.Frame(nb, bg="white")
        self.tab_mould = tk.Frame(nb, bg="white")
        self.tab_defects = tk.Frame(nb, bg="white") 
        
        nb.add(self.tab_users, text=" 👥 Users ")
        nb.add(self.tab_qc, text=" 1. Raw Materials ")
        nb.add(self.tab_plan, text=" 2. Prod Plan ")
        nb.add(self.tab_spec, text=" 3. Tyre Specs ")
        nb.add(self.tab_bead, text=" 4. Bead Master ")
        nb.add(self.tab_mould, text=" 5. Moulds ")
        nb.add(self.tab_defects, text=" 6. Defects ") 
        
        self.setup_user_tab()
        self.setup_qc_tab()
        self.setup_plan_tab()
        self.setup_spec_tab()
        self.setup_bead_tab()
        self.setup_mould_tab()
        self.setup_defects_tab()

    # --- USER MANAGER ---
    def setup_user_tab(self):
        f = self.tab_users
        tk.Label(f, text="Manage Operators & Supervisors", font=("Segoe UI", 12, "bold"), bg="white", fg="#2c3e50").pack(pady=15)
        frame_input = tk.Frame(f, bg="#ECF0F1", padx=15, pady=15, bd=1, relief="solid")
        frame_input.pack(fill="x", padx=20, pady=10)

        tk.Label(frame_input, text="User ID:", font=("Segoe UI", 9, "bold"), bg="#ECF0F1").grid(row=0, column=0, sticky="w")
        self.ent_uid = tk.Entry(frame_input, font=("Segoe UI", 11), width=15)
        self.ent_uid.grid(row=1, column=0, padx=5, pady=5)

        tk.Label(frame_input, text="Full Name:", font=("Segoe UI", 9, "bold"), bg="#ECF0F1").grid(row=0, column=1, sticky="w")
        self.ent_name = tk.Entry(frame_input, font=("Segoe UI", 11), width=25)
        self.ent_name.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame_input, text="Role:", font=("Segoe UI", 9, "bold"), bg="#ECF0F1").grid(row=0, column=2, sticky="w")
        self.combo_role = ttk.Combobox(frame_input, values=["OPERATOR", "SUPERVISOR", "MANAGER", "QC", "ADMIN"], state="readonly", font=("Segoe UI", 11), width=15)
        self.combo_role.current(0); self.combo_role.grid(row=1, column=2, padx=5, pady=5)

        # --- NEW: Password Field (Column 3) ---
        tk.Label(frame_input, text="Password:", font=("Segoe UI", 9, "bold"), bg="#ECF0F1").grid(row=0, column=3, sticky="w")
        self.ent_pwd = tk.Entry(frame_input, font=("Segoe UI", 11), width=15)
        self.ent_pwd.insert(0, "1234") # Sets default to 1234
        self.ent_pwd.grid(row=1, column=3, padx=5, pady=5)

        # --- SHIFTED: Buttons (Moved to Column 4) ---
        btn_frame = tk.Frame(frame_input, bg="#ECF0F1"); btn_frame.grid(row=1, column=4, padx=15, pady=5)
        tk.Button(btn_frame, text="➕ SAVE", command=self.add_user, bg="#27AE60", fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="❌ DELETE", command=self.delete_user, bg="#C0392B", fg="white").pack(side="left", padx=5)

        self.tree_users = ttk.Treeview(f, columns=("ID", "Name", "Role"), show="headings", height=12)
        self.tree_users.heading("ID", text="User ID"); self.tree_users.heading("Name", text="Full Name"); self.tree_users.heading("Role", text="Role")
        self.tree_users.pack(fill="both", expand=True, padx=20, pady=10)
        tk.Button(f, text="🔄 Refresh List", command=self.load_users).pack(pady=5)
        self.load_users()

    def load_users(self):
        for i in self.tree_users.get_children(): self.tree_users.delete(i)
        res = DBManager.fetch_data("SELECT user_id, full_name, role FROM users WHERE is_active=TRUE ORDER BY user_id")
        if res:
            for row in res: self.tree_users.insert("", "end", values=row)

    def open_smart_parser(self):
        if SmartOrderParser:
            SmartOrderParser(self.root)
        else:
            messagebox.showerror("Error", "Parser module missing or python-docx is not installed.")        

    def add_user(self):
        uid = self.ent_uid.get().strip().upper()
        name = self.ent_name.get().strip()
        role = self.combo_role.get()
        pwd = self.ent_pwd.get().strip()
        
        # Fallback if admin deletes the text completely
        if not pwd: pwd = "1234" 

        if not uid or not name: 
            return messagebox.showerror("Error", "Missing fields")
        
        q = """INSERT INTO users (user_id, full_name, role, password, is_active) 
               VALUES (%s, %s, %s, %s, TRUE) 
               ON CONFLICT (user_id) DO UPDATE SET 
               full_name=EXCLUDED.full_name, role=EXCLUDED.role, password=EXCLUDED.password, is_active=TRUE"""
               
        if DBManager.execute_query(q, (uid, name, role, pwd)):
            self.load_users()
            self.ent_uid.delete(0, tk.END)
            self.ent_name.delete(0, tk.END)
            self.ent_pwd.delete(0, tk.END)
            self.ent_pwd.insert(0, "1234") # Reset to default for the next entry

    def delete_user(self):
        sel = self.tree_users.selection()
        if sel and messagebox.askyesno("Confirm", "Delete User?"):
            uid = self.tree_users.item(sel[0])['values'][0]
            DBManager.execute_query("UPDATE users SET is_active=FALSE WHERE user_id=%s", (uid,))
            self.load_users()

    # --- 1. RAW MATERIALS ---
    def setup_qc_tab(self):
        self._build_upload_ui(self.tab_qc, "Raw Material Inventory", self.upload_qc, self.download_sample_qc, ["Batch No", "Material Type", "Status"], self.refresh_qc_list)
        self.tree_qc = ttk.Treeview(self.tab_qc, columns=("Batch", "Type", "Status"), show="headings", height=15)
        self.tree_qc.heading("Batch", text="Batch No"); self.tree_qc.heading("Type", text="Type"); self.tree_qc.heading("Status", text="Status")
        self.tree_qc.pack(fill="both", expand=True, padx=20, pady=10)
        self.refresh_qc_list()

    def upload_qc(self):
        rows = self._read_csv_file()
        if not rows: return
        count = 0
        for r in rows:
            if DBManager.execute_query("INSERT INTO raw_material_qc (batch_no, material_type, status) VALUES (%s, %s, %s) ON CONFLICT (batch_no) DO NOTHING", (r.get('BATCH_NO'), r.get('MATERIAL_TYPE'), r.get('STATUS', 'APPROVED'))): count += 1
        messagebox.showinfo("Success", f"Uploaded {count} materials"); self.refresh_qc_list()

    def refresh_qc_list(self): self._refresh_tree(self.tree_qc, "SELECT batch_no, material_type, status FROM raw_material_qc ORDER BY batch_no DESC LIMIT 50")
    def download_sample_qc(self): self._save_csv("Sample_Materials.csv", ["BATCH_NO", "MATERIAL_TYPE", "STATUS"], [["BATCH001", "RUBBER", "APPROVED"]])

    # --- 2. PROD PLAN (UPDATED WITH REQUIREMENT) ---
    
    def setup_plan_tab(self):
        # 1. The standard upload UI you already built
        self._build_upload_ui(self.tab_plan, "Daily Production Plan", self.upload_plan, self.download_sample_plan, ["Press", "Daylight", "Size", "Grade", "Req"], self.refresh_plan_list)
        
        # 2. NEW: Extra Frame just for the Smart Parser button
        f_extra = tk.Frame(self.tab_plan, bg="white")
        f_extra.pack(pady=5)
        tk.Button(f_extra, text="🤖 PARSE DOCX ORDER", command=self.open_smart_parser, bg="#8E44AD", fg="white", font=("Segoe UI", 10, "bold")).pack()

        # 3. Updated Treeview Columns (Your existing code continues here...)
        self.tree_plan = ttk.Treeview(self.tab_plan, columns=("Press", "DL", "Size", "Grade", "Req"), show="headings", height=15)

        # Updated Treeview Columns
        self.tree_plan = ttk.Treeview(self.tab_plan, columns=("Press", "DL", "Size", "Grade", "Req"), show="headings", height=15)
        self.tree_plan.heading("Press", text="Press"); self.tree_plan.column("Press", width=80)
        self.tree_plan.heading("DL", text="Daylight"); self.tree_plan.column("DL", width=80)
        self.tree_plan.heading("Size", text="Tyre Size"); self.tree_plan.column("Size", width=150)
        self.tree_plan.heading("Grade", text="Grade"); self.tree_plan.column("Grade", width=100)
        self.tree_plan.heading("Req", text="Req (Qty)"); self.tree_plan.column("Req", width=80) # New Column
        
        self.tree_plan.pack(fill="both", expand=True, padx=20, pady=10)
        self.refresh_plan_list()

    def upload_plan(self):
        rows = self._read_csv_file()
        if not rows: return
        DBManager.execute_query("DELETE FROM production_plan")
        count = 0
        for r in rows:
            # Added PRODUCTION_REQUIREMENT
            req = r.get('PRODUCTION_REQUIREMENT', 0)
            if not req: req = 0
            
            if DBManager.execute_query("""
                INSERT INTO production_plan (
                    press_id, daylight, tyre_size, brand, pattern, quality, type, 
                    tyre_weight, core_size, mould_id_marks, production_requirement
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
                (r.get('PRESS'), r.get('DAYLIGHT'), r.get('TYRE_SIZE'), r.get('BRAND'), 
                 r.get('PATTERN'), r.get('QUALITY'), r.get('TYPE'), r.get('TYRE WEIGHT'), 
                 r.get('CORE_SIZE'), r.get('MOULD_ID'), req)): count += 1
        messagebox.showinfo("Success", f"Uploaded {count} plans"); self.refresh_plan_list()

    def refresh_plan_list(self): 
        self._refresh_tree(self.tree_plan, "SELECT press_id, daylight, tyre_size, quality, production_requirement FROM production_plan ORDER BY press_id, daylight")
    
    def download_sample_plan(self): 
        # Updated Sample Headers
        self._save_csv("Sample_Plan.csv", 
                       ["PRESS", "DAYLIGHT", "TYRE_SIZE", "CORE_SIZE", "BRAND", "PATTERN", "QUALITY", "MOULD_ID", "TYPE", "TYRE WEIGHT", "PRODUCTION_REQUIREMENT"], 
                       [["P-01", "1", "12.00-20", "10", "BRAND-X", "LUG", "A-GRADE", "M123", "STD", "45.5", "20"]])

    # --- 3. SPECS ---
    def setup_spec_tab(self):
        self._build_upload_ui(self.tab_spec, "Tyre Specs (Rubber %)", self.upload_specs, self.download_sample_spec, ["Grade", "Core %", "Mid %", "C+T %", "Gum %", "Tread %"], self.refresh_spec_list)
        self.tree_spec = ttk.Treeview(self.tab_spec, columns=("Grade", "Core", "Mid", "CT", "Gum", "Tread", "POB"), show="headings", height=15)
        self.tree_spec.heading("Grade", text="Grade"); self.tree_spec.heading("Core", text="Core %"); self.tree_spec.heading("Mid", text="Mid %")
        self.tree_spec.heading("CT", text="C+T %"); self.tree_spec.heading("Gum", text="Gum %"); self.tree_spec.heading("Tread", text="Tread %"); self.tree_spec.heading("POB", text="Is POB?")
        self.tree_spec.pack(fill="both", expand=True, padx=20, pady=10)
        self.refresh_spec_list()

    def upload_specs(self):
        rows = self._read_csv_file()
        if not rows: return
        count = 0
        for r in rows:
            # Helper to get float
            def get_f(key):
                v = r.get(key, '').strip()
                try: return float(v) if v else 0.0
                except: return 0.0

            val_pob = str(r.get('IS_POB', '')).strip().upper()
            is_pob_bool = 'TRUE' if val_pob in ['TRUE', '1', 'YES', 'T'] else 'FALSE'

            if DBManager.execute_query("""INSERT INTO tyre_specs (grade, core_pct, mid_pct, ct_pct, gum_pct, tread_pct, is_pob) 
                                       VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (grade) DO UPDATE SET 
                                       core_pct=EXCLUDED.core_pct, mid_pct=EXCLUDED.mid_pct, 
                                       ct_pct=EXCLUDED.ct_pct, gum_pct=EXCLUDED.gum_pct, 
                                       tread_pct=EXCLUDED.tread_pct, is_pob=EXCLUDED.is_pob""", 
                                       (r.get('GRADE'), get_f('CORE_%'), get_f('MID_%'), get_f('CT_%'), get_f('GUM_%'), get_f('TREAD_%'), is_pob_bool)):
                count += 1
        messagebox.showinfo("Success", f"Uploaded {count} specs"); self.refresh_spec_list()

    def refresh_spec_list(self): self._refresh_tree(self.tree_spec, "SELECT grade, core_pct, mid_pct, ct_pct, gum_pct, tread_pct, is_pob FROM tyre_specs ORDER BY grade")
    
    def download_sample_spec(self): 
        self._save_csv("Sample_Grade_Specs.csv", 
                       ["GRADE", "CORE_%", "MID_%", "CT_%", "GUM_%", "TREAD_%", "IS_POB"], 
                       [["POB-TEST", "0", "0", "40", "3", "57", "TRUE"], ["STD-GRADE", "20", "20", "0", "0", "60", "FALSE"]])

    # --- 4. BEAD MASTER ---
    def setup_bead_tab(self):
        self._build_upload_ui(self.tab_bead, "Bead Master", self.upload_bead, self.download_sample_bead, ["Size", "Bead", "Count", "Wt"], self.refresh_bead_list)
        self.tree_bead = ttk.Treeview(self.tab_bead, columns=("Size", "Bead", "Count", "Wt"), show="headings", height=15)
        for c in ("Size", "Bead", "Count", "Wt"): self.tree_bead.heading(c, text=c)
        self.tree_bead.pack(fill="both", expand=True, padx=20, pady=10)
        self.refresh_bead_list()

    def upload_bead(self):
        rows = self._read_csv_file()
        if not rows: return
        count = 0
        for r in rows:
            if DBManager.execute_query("INSERT INTO bead_master (tyre_size, bead_size, bead_count, weight_per_bead) VALUES (%s, %s, %s, %s) ON CONFLICT (tyre_size) DO UPDATE SET bead_size=EXCLUDED.bead_size", 
                                       (r.get('TYRE_SIZE'), r.get('BEAD_SIZE'), r.get('BEAD_COUNT'), r.get('WEIGHT_PER_BEAD'))): count += 1
        messagebox.showinfo("Success", f"Uploaded {count} beads"); self.refresh_bead_list()

    def refresh_bead_list(self): self._refresh_tree(self.tree_bead, "SELECT tyre_size, bead_size, bead_count, weight_per_bead FROM bead_master ORDER BY tyre_size")
    def download_sample_bead(self): self._save_csv("Sample_Bead.csv", ["TYRE_SIZE", "BEAD_SIZE", "BEAD_COUNT", "WEIGHT_PER_BEAD"], [["12.00-20", "HEX-20", "2", "1.5"]])

    # --- 5. MOULD ---
    def setup_mould_tab(self):
        self._build_upload_ui(self.tab_mould, "Mould Master", self.upload_mould, self.download_sample_mould, ["Mould", "Size", "Pattern"], self.refresh_mould_list)
        self.tree_mould = ttk.Treeview(self.tab_mould, columns=("Mould", "Size", "Pattern"), show="headings", height=15)
        for c in ("Mould", "Size", "Pattern"): self.tree_mould.heading(c, text=c)
        self.tree_mould.pack(fill="both", expand=True, padx=20, pady=10)
        self.refresh_mould_list()

    def upload_mould(self):
        rows = self._read_csv_file()
        if not rows: return
        count = 0
        for r in rows:
            if DBManager.execute_query("INSERT INTO pc1_mould_mapping (mould_id, tyre_size, pattern) VALUES (%s, %s, %s) ON CONFLICT (mould_id) DO UPDATE SET tyre_size=EXCLUDED.tyre_size", 
                                       (r.get('MOULD_ID'), r.get('TYRE_SIZE'), r.get('PATTERN'))): count += 1
        messagebox.showinfo("Success", f"Uploaded {count} moulds"); self.refresh_mould_list()

    def refresh_mould_list(self): self._refresh_tree(self.tree_mould, "SELECT mould_id, tyre_size, pattern FROM pc1_mould_mapping ORDER BY mould_id")
    def download_sample_mould(self): self._save_csv("Sample_Moulds.csv", ["MOULD_ID", "TYRE_SIZE", "PATTERN"], [["M101", "12.00-20", "LUG"]])

    # --- 6. DEFECTS ---
    def setup_defects_tab(self):
        self._build_upload_ui(self.tab_defects, "Defects Master", self.upload_defects, self.download_sample_defect, ["Code", "Name", "Type", "Reason"], self.refresh_defect_list)
        self.tree_defects = ttk.Treeview(self.tab_defects, columns=("Code", "Name", "Type", "Reason"), show="headings", height=15)
        for c in ("Code", "Name", "Type", "Reason"): self.tree_defects.heading(c, text=c)
        self.tree_defects.pack(fill="both", expand=True, padx=20, pady=10)
        self.refresh_defect_list()

    def upload_defects(self):
        rows = self._read_csv_file()
        if not rows: return
        count = 0
        for r in rows:
            if DBManager.execute_query("INSERT INTO qc_defects_master (defect_code, defect_name, defect_type, defect_reason) VALUES (%s, %s, %s, %s) ON CONFLICT (defect_code) DO UPDATE SET defect_name=EXCLUDED.defect_name", 
                                       (r.get('DEFECT_CODE'), r.get('DEFECT_NAME'), r.get('DEFECT_TYPE'), r.get('REASON'))): count += 1
        messagebox.showinfo("Success", f"Uploaded {count} defects"); self.refresh_defect_list()

    def refresh_defect_list(self): self._refresh_tree(self.tree_defects, "SELECT defect_code, defect_name, defect_type, defect_reason FROM qc_defects_master ORDER BY defect_code")
    def download_sample_defect(self): self._save_csv("Sample_Defects.csv", ["DEFECT_CODE", "DEFECT_NAME", "DEFECT_TYPE", "REASON"], [["DD001", "UNDER CURE", "DIRECT", "LESS TEMP"]])

    # --- HELPERS ---
    def _build_upload_ui(self, parent, title, up_cmd, down_cmd, cols, refresh_cmd):
        tk.Label(parent, text=title, font=("Segoe UI", 12, "bold"), bg="white").pack(pady=15)
        f = tk.Frame(parent, bg="white"); f.pack(pady=5)
        tk.Button(f, text="⬇ Sample CSV", command=down_cmd).pack(side="left", padx=5)
        tk.Button(f, text="📂 Upload CSV", command=up_cmd, bg="#E74C3C", fg="white").pack(side="left", padx=5)
        tk.Button(f, text="🔄 Refresh", command=refresh_cmd).pack(side="left", padx=5)

    def _read_csv_file(self):
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if not path: return None
        data = []
        try:
            with open(path, newline='', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                # Normalize headers: remove spaces, uppercase
                reader.fieldnames = [str(n).strip().upper() for n in reader.fieldnames]
                for row in reader: data.append(row)
        except Exception as e: messagebox.showerror("Error", f"CSV Error: {e}"); return None
        return data

    def _save_csv(self, fname, header, rows):
        path = filedialog.asksaveasfilename(initialfile=fname, defaultextension=".csv")
        if path:
            with open(path, 'w', newline='') as f:
                w = csv.writer(f); w.writerow(header); w.writerows(rows)
            messagebox.showinfo("Success", "File Saved")

    def _refresh_tree(self, tree, query):
        for i in tree.get_children(): tree.delete(i)
        res = DBManager.fetch_data(query)
        if res:
            for r in res: tree.insert("", "end", values=r)

if __name__ == "__main__":
    root = tk.Tk(); app = AdminDashboard(root); root.mainloop()