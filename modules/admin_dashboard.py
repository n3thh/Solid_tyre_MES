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
        self.root.geometry("1300x800")
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
        self.tab_master = tk.Frame(nb, bg="white") # NEW MASTER ORDERS TAB
        self.tab_catalog = tk.Frame(nb, bg="white") # NEW TYRE CATALOG TAB
        self.tab_spec = tk.Frame(nb, bg="white")
        self.tab_bead = tk.Frame(nb, bg="white")
        self.tab_mould = tk.Frame(nb, bg="white")
        self.tab_presses = tk.Frame(nb, bg="white")
        self.tab_defects = tk.Frame(nb, bg="white") 
        
        nb.add(self.tab_users, text=" 👥 Users ")
        nb.add(self.tab_qc, text=" 1. Raw Materials ")
        nb.add(self.tab_plan, text=" 2. Prod Plan ")
        nb.add(self.tab_master, text=" 📦 Master Orders ") # ADDED TO NOTEBOOK
        nb.add(self.tab_catalog, text=" 📚 Tyre Master ")
        nb.add(self.tab_spec, text=" 3. Tyre Specs ")
        nb.add(self.tab_bead, text=" 4. Bead Master ")
        nb.add(self.tab_mould, text=" 5. Moulds ")
        nb.add(self.tab_presses, text=" 🎰 Press Master ")
        nb.add(self.tab_defects, text=" 6. Defects ") 
        
        self.setup_user_tab()
        self.setup_qc_tab()
        self.setup_plan_tab()
        self.setup_master_orders_tab() # SETUP CALL
        self.setup_catalog_tab() # SETUP CALL
        self.setup_spec_tab()
        self.setup_bead_tab()
        self.setup_mould_tab()
        self.setup_press_master_tab()
        self.setup_defects_tab()

        # Bind the tab change event to an auto-refresh function
        self.nb = nb 
        self.nb.bind("<<NotebookTabChanged>>", self.on_tab_change)

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

        tk.Label(frame_input, text="Password:", font=("Segoe UI", 9, "bold"), bg="#ECF0F1").grid(row=0, column=3, sticky="w")
        self.ent_pwd = tk.Entry(frame_input, font=("Segoe UI", 11), width=15)
        self.ent_pwd.insert(0, "1234") 
        self.ent_pwd.grid(row=1, column=3, padx=5, pady=5)

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
            messagebox.showerror("Error", "Parser module missing or python-docx is not installed.",)  

    def on_tab_change(self, event):
        """Automatically refreshes data and clears inputs when switching tabs."""
        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, "text")

        if "Users" in tab_text:
            self.load_users()
            self.ent_uid.delete(0, tk.END); self.ent_name.delete(0, tk.END)
        elif "Raw Materials" in tab_text:
            self.refresh_qc_list()
        elif "Prod Plan" in tab_text:
            self.refresh_plan_list()
            self.load_master_dropdown()
            self.load_active_presses()
        elif "Master Orders" in tab_text:
            self.load_master_orders()
            for ent in [self.mo_pi, self.mo_cust, self.mo_size, self.mo_core, self.mo_brand, self.mo_qual, self.mo_qty]:
                ent.delete(0, tk.END)
        elif "Tyre Master" in tab_text:
            self.load_catalog()
            for ent in [self.cat_size, self.cat_core, self.cat_brand, self.cat_qual, self.cat_wt]:
                ent.delete(0, tk.END)
        elif "Tyre Specs" in tab_text:
            self.refresh_spec_list()
        elif "Bead Master" in tab_text:
            self.refresh_bead_list()
        elif "Moulds" in tab_text:
            self.refresh_mould_list()
        elif "Defects" in tab_text:
            self.refresh_defect_list()              

    def add_user(self):
        uid = self.ent_uid.get().strip().upper()
        name = self.ent_name.get().strip()
        role = self.combo_role.get()
        pwd = self.ent_pwd.get().strip()
        
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
            self.ent_pwd.insert(0, "1234")

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

# --- 2. DAILY PROD PLAN (THE LIVE BOARD) ---
    def setup_plan_tab(self):
        # Split Screen Layout
        f_left = tk.Frame(self.tab_plan, bg="#F4F6F7", width=350, relief="ridge", bd=1)
        f_left.pack(side="left", fill="y", padx=10, pady=10)
        
        f_right = tk.Frame(self.tab_plan, bg="white")
        f_right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # ================= LEFT: MACHINE ASSIGNER =================
        tk.Label(f_left, text="🛠️ Assign Machine", font=("Segoe UI", 14, "bold"), bg="#F4F6F7", fg="#2980B9").pack(pady=(10, 5))

        # --- TOGGLE SWITCH ---
        self.plan_mode = tk.StringVar(value="MTO")
        f_toggle = tk.Frame(f_left, bg="#F4F6F7")
        f_toggle.pack(fill="x", padx=15, pady=5)
        tk.Radiobutton(f_toggle, text="📦 Fulfill Master Order", variable=self.plan_mode, value="MTO", command=self.toggle_plan_mode, bg="#F4F6F7", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Radiobutton(f_toggle, text="🏭 Make to Stock (Local)", variable=self.plan_mode, value="MTS", command=self.toggle_plan_mode, bg="#F4F6F7", font=("Segoe UI", 9, "bold")).pack(anchor="w")

        # --- MTO FRAME (Master Orders) ---
        self.f_mto = tk.Frame(f_left, bg="#F4F6F7")
        tk.Label(self.f_mto, text="Select Master Order:", bg="#F4F6F7", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=15)
        self.plan_mo_cb = ttk.Combobox(self.f_mto, state="readonly", font=("Segoe UI", 10))
        self.plan_mo_cb.pack(fill="x", padx=15, pady=5)
        self.plan_mo_cb.bind("<<ComboboxSelected>>", self.autofill_plan_from_order)

        # --- MTS FRAME (Cascading Dropdowns) ---
        self.f_mts = tk.Frame(f_left, bg="#F4F6F7")
        tk.Label(self.f_mts, text="Size:", bg="#F4F6F7", font=("Segoe UI", 8, "bold")).grid(row=0, column=0, sticky="w", padx=(15,2))
        self.cb_size = ttk.Combobox(self.f_mts, state="readonly", width=12); self.cb_size.grid(row=1, column=0, padx=(15,2), pady=2)
        self.cb_size.bind("<<ComboboxSelected>>", self.on_size_select)

        tk.Label(self.f_mts, text="Core:", bg="#F4F6F7", font=("Segoe UI", 8, "bold")).grid(row=0, column=1, sticky="w", padx=2)
        self.cb_core = ttk.Combobox(self.f_mts, state="readonly", width=8); self.cb_core.grid(row=1, column=1, padx=2, pady=2)
        self.cb_core.bind("<<ComboboxSelected>>", self.on_core_select)

        tk.Label(self.f_mts, text="Brand:", bg="#F4F6F7", font=("Segoe UI", 8, "bold")).grid(row=2, column=0, sticky="w", padx=(15,2))
        self.cb_brand = ttk.Combobox(self.f_mts, state="readonly", width=12); self.cb_brand.grid(row=3, column=0, padx=(15,2), pady=2)
        self.cb_brand.bind("<<ComboboxSelected>>", self.on_brand_select)

        tk.Label(self.f_mts, text="Quality:", bg="#F4F6F7", font=("Segoe UI", 8, "bold")).grid(row=2, column=1, sticky="w", padx=2)
        self.cb_qual = ttk.Combobox(self.f_mts, state="readonly", width=8); self.cb_qual.grid(row=3, column=1, padx=2, pady=2)
        self.cb_qual.bind("<<ComboboxSelected>>", self.on_quality_select)

        # --- SHARED ASSIGNMENT FRAME ---
        self.f_shared = tk.Frame(f_left, bg="#F4F6F7")
        self.f_shared.pack(fill="x", pady=5)

        tk.Label(self.f_shared, text="Press ID (e.g., P-01):", bg="#F4F6F7", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=15)
        self.plan_press = ttk.Combobox(self.f_shared, state="readonly", font=("Segoe UI", 11))
        self.plan_press.pack(fill="x", padx=15, pady=2)
        self.plan_press.bind("<<ComboboxSelected>>", self.on_plan_press_select)

        tk.Label(self.f_shared, text="Daylight:", bg="#F4F6F7", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=15)
        # REMOVED the hardcoded values and added state="readonly"
        self.plan_dl = ttk.Combobox(self.f_shared, state="readonly", font=("Segoe UI", 11))
        self.plan_dl.pack(fill="x", padx=15, pady=2)

        tk.Label(self.f_shared, text="Target Green Wt (kg):", bg="#F4F6F7", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=15)
        self.plan_wt = tk.Entry(self.f_shared, font=("Segoe UI", 11))
        self.plan_wt.pack(fill="x", padx=15, pady=2)

        tk.Label(self.f_shared, text="Target Qty:", bg="#F4F6F7", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=15)
        self.plan_qty = tk.Entry(self.f_shared, font=("Segoe UI", 11))
        self.plan_qty.pack(fill="x", padx=15, pady=2)

        self.hidden_plan_data = {}
        self.current_baseline_weight = 0.0

        tk.Button(f_left, text="🚀 ASSIGN TO PRESS", command=self.add_manual_plan, bg="#27AE60", fg="white", font=("Segoe UI", 11, "bold"), pady=5).pack(fill="x", padx=15, pady=15)

        # ================= RIGHT: LIVE PLAN GRID =================
        tk.Label(f_right, text="📋 Live Production Board", font=("Segoe UI", 14, "bold"), bg="white", fg="#2C3E50").pack(anchor="w", pady=(0, 10))
        
        cols = ("Press", "Daylight", "Size", "Brand", "Target Wt", "Target Qty")
        self.tree_plan = ttk.Treeview(f_right, columns=cols, show="headings", height=20)
        for c in cols: self.tree_plan.heading(c, text=c)
        
        self.tree_plan.column("Press", width=70, anchor="center")
        self.tree_plan.column("Daylight", width=80, anchor="center")
        self.tree_plan.column("Size", width=120, anchor="center")
        self.tree_plan.column("Target Wt", width=80, anchor="center")
        self.tree_plan.column("Target Qty", width=80, anchor="center")
        self.tree_plan.pack(fill="both", expand=True)
        
        f_grid_btns = tk.Frame(f_right, bg="white")
        f_grid_btns.pack(fill="x", pady=10)
        tk.Button(f_grid_btns, text="🗑️ Clear Selected Press", command=self.delete_plan, bg="#E74C3C", fg="white", font=("Segoe UI", 9, "bold")).pack(side="left")
        tk.Button(f_grid_btns, text="🔄 Refresh Board", command=self.refresh_plan_list, bg="#2980B9", fg="white", font=("Segoe UI", 9, "bold")).pack(side="right")

        self.refresh_plan_list()
        self.load_master_dropdown()
        self.toggle_plan_mode() # Initialize UI state
        self.load_active_presses()

    # --- PLAN LOGIC & DROPDOWNS ---
    def toggle_plan_mode(self):
        mode = self.plan_mode.get()
        if mode == "MTO":
            self.f_mts.pack_forget()
            self.f_mto.pack(fill="x", pady=5, before=self.f_shared)
        else:
            self.f_mto.pack_forget()
            self.f_mts.pack(fill="x", pady=5, before=self.f_shared)
            self.load_catalog_sizes()

    def load_master_dropdown(self):
        query = "SELECT order_id, pi_number, tyre_size, brand, req_qty, produced_qty FROM master_orders WHERE status != 'CLOSED'"
        res = DBManager.fetch_data(query)
        self.master_order_map = {}
        vals = []
        if res:
            for r in res:
                oid, pi, size, brand, req, prod = r
                pending = req - (prod if prod else 0)
                display_text = f"[{oid}] {pi} | {size} {brand} (Pending: {pending})"
                vals.append(display_text)
                self.master_order_map[display_text] = oid
        self.plan_mo_cb['values'] = vals

    def load_active_presses(self):
        """Populate the Press dropdown with distinct active presses"""
        res = DBManager.fetch_data("SELECT DISTINCT press_id FROM press_master WHERE status='ACTIVE' ORDER BY press_id")
        
        # We only grab r[0] because we only asked the database for the press_id!
        self.plan_press['values'] = [r[0] for r in res] if res else []
        
        # Clear daylight box safely when refreshing
        if hasattr(self, 'plan_dl'):
            self.plan_dl.set('')

    def on_plan_press_select(self, event):
        """Update the Daylight dropdown based on the selected Press"""
        selected_press = self.plan_press.get()
        res = DBManager.fetch_data("SELECT daylight FROM press_master WHERE press_id=%s AND status='ACTIVE' ORDER BY daylight", (selected_press,))
        
        self.plan_dl['values'] = [r[0] for r in res] if res else []
        
        # Auto-select the first available daylight if there is one
        if self.plan_dl['values']:
            self.plan_dl.current(0)
        else:
            self.plan_dl.set('')


    def autofill_plan_from_order(self, event):
        selection = self.plan_mo_cb.get()
        if not selection or selection not in self.master_order_map: return
        
        order_id = self.master_order_map[selection]
        
        # 1. UPDATED SQL: Now we also fetch the produced_qty
        q = "SELECT tyre_size, core_size, brand, quality, req_qty, produced_qty FROM master_orders WHERE order_id = %s"
        res = DBManager.fetch_data(q, (order_id,))
        
        if res:
            size, core, brand, qual, req, prod = res[0]
            
            # 2. THE MATH: Calculate how many are actually left to build
            prod_val = prod if prod else 0 
            pending = req - prod_val
            
            # Prevent negative numbers just in case of overproduction
            if pending < 0: pending = 0 
            
            self.hidden_plan_data = {'size': size, 'core': core, 'brand': brand, 'qual': qual}
            
            # 3. AUTO-FILL: Insert the PENDING amount, not the original total!
            self.plan_qty.delete(0, tk.END)
            self.plan_qty.insert(0, str(pending))
            
            # Fetch baseline weight from catalog
            wq = "SELECT baseline_weight FROM product_catalog WHERE tyre_size=%s AND core_size=%s AND brand=%s LIMIT 1"
            w_res = DBManager.fetch_data(wq, (size, core, brand))
            self.current_baseline_weight = float(w_res[0][0]) if w_res else 0.0
            
            self.plan_wt.delete(0, tk.END)
            self.plan_wt.insert(0, str(self.current_baseline_weight))
            
            # Optional: Pop up a quick notification if the order is already partially done
            if prod_val > 0 and pending > 0:
                messagebox.showinfo("Progress Update", f"Order in progress!\n\nTotal Required: {req}\nAlready Produced: {prod_val}\n\nTarget quantity auto-filled to remaining: {pending}")
            elif pending == 0:
                messagebox.showwarning("Order Complete", "Warning: This Master Order has already hit its required production target!")

    def load_catalog_sizes(self):
        res = DBManager.fetch_data("SELECT DISTINCT tyre_size FROM product_catalog WHERE is_active=TRUE ORDER BY tyre_size")
        self.cb_size['values'] = [r[0] for r in res] if res else []
        self.cb_core.set(''); self.cb_brand.set(''); self.cb_qual.set(''); self.plan_wt.delete(0, tk.END)

    def on_size_select(self, event):
        size = self.cb_size.get()
        res = DBManager.fetch_data("SELECT DISTINCT core_size FROM product_catalog WHERE tyre_size=%s AND is_active=TRUE", (size,))
        self.cb_core['values'] = [r[0] for r in res] if res else []
        self.cb_core.set(''); self.cb_brand.set(''); self.cb_qual.set('')

    def on_core_select(self, event):
        size = self.cb_size.get(); core = self.cb_core.get()
        res = DBManager.fetch_data("SELECT DISTINCT brand FROM product_catalog WHERE tyre_size=%s AND core_size=%s AND is_active=TRUE", (size, core))
        self.cb_brand['values'] = [r[0] for r in res] if res else []
        self.cb_brand.set(''); self.cb_qual.set('')

    def on_brand_select(self, event):
        size = self.cb_size.get(); core = self.cb_core.get(); brand = self.cb_brand.get()
        res = DBManager.fetch_data("SELECT DISTINCT quality FROM product_catalog WHERE tyre_size=%s AND core_size=%s AND brand=%s AND is_active=TRUE", (size, core, brand))
        self.cb_qual['values'] = [r[0] for r in res] if res else []
        self.cb_qual.set('')

    def on_quality_select(self, event):
        size = self.cb_size.get(); core = self.cb_core.get(); brand = self.cb_brand.get(); qual = self.cb_qual.get()
        self.hidden_plan_data = {'size': size, 'core': core, 'brand': brand, 'qual': qual}
        
        res = DBManager.fetch_data("SELECT baseline_weight FROM product_catalog WHERE tyre_size=%s AND core_size=%s AND brand=%s AND quality=%s LIMIT 1", (size, core, brand, qual))
        if res:
            self.current_baseline_weight = float(res[0][0])
            self.plan_wt.delete(0, tk.END)
            self.plan_wt.insert(0, str(self.current_baseline_weight))

    def add_manual_plan(self):
        press = self.plan_press.get().strip().upper()
        dl = self.plan_dl.get().strip().upper()
        
        try: 
            qty = int(self.plan_qty.get().strip())
            target_wt = float(self.plan_wt.get().strip())
        except ValueError: 
            return messagebox.showerror("Error", "Quantity and Target Weight must be numeric.")
            
        if not press or not dl or not self.hidden_plan_data:
            return messagebox.showerror("Error", "Please complete all fields (Order/Catalog, Press, Daylight).")

        # --- GRAB THE ORDER ID (IF MTO) ---
        order_id = None
        if self.plan_mode.get() == "MTO":
            selection = self.plan_mo_cb.get()
            if selection in self.master_order_map:
                order_id = self.master_order_map[selection]

        # --- THE 15% GUARDRAIL CHECK ---
        warning_note = ""
        if self.current_baseline_weight > 0:
            diff = target_wt - self.current_baseline_weight
            pct_diff = (abs(diff) / self.current_baseline_weight) * 100
            
            if pct_diff > 15.0:
                msg = f"⚠️ WEIGHT TOLERANCE ALERT\n\nEntered Weight: {target_wt} kg\nDatabase Baseline: {self.current_baseline_weight} kg\n\nThis is {pct_diff:.1f}% off standard! Are you absolutely sure you want to assign this?"
                if not messagebox.askyesno("Confirm Deviation", msg): return
            elif pct_diff > 0:
                warning_note = f"\n(Note: Weight is {pct_diff:.1f}% off standard)"

        # Assign to Press
        DBManager.execute_query("DELETE FROM production_plan WHERE press_id=%s AND daylight=%s", (press, dl))

        # --- UPDATED SQL: Now includes order_id ---
        q = """INSERT INTO production_plan (press_id, daylight, tyre_size, core_size, brand, quality, tyre_weight, production_requirement, order_id) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
               
        if DBManager.execute_query(q, (press, dl, self.hidden_plan_data['size'], self.hidden_plan_data['core'], self.hidden_plan_data['brand'], self.hidden_plan_data['qual'], target_wt, qty, order_id)):
            self.refresh_plan_list()
            self.plan_qty.delete(0, tk.END)
            messagebox.showinfo("Success", f"{press} ({dl}) Assigned!{warning_note}")

    def delete_plan(self):
        sel = self.tree_plan.selection()
        if not sel: return messagebox.showwarning("Warning", "Select a Press assignment to clear.")
        item = self.tree_plan.item(sel[0])['values']
        
        if messagebox.askyesno("Confirm", f"Clear plan for {item[0]} ({item[1]})?"):
            DBManager.execute_query("DELETE FROM production_plan WHERE press_id=%s AND daylight=%s", (item[0], item[1]))
            self.refresh_plan_list()

    def refresh_plan_list(self): 
        self._refresh_tree(self.tree_plan, "SELECT press_id, daylight, tyre_size, brand, tyre_weight, production_requirement FROM production_plan ORDER BY press_id, daylight")
        self.load_master_dropdown()



    def upload_plan(self):
        rows = self._read_csv_file()
        if not rows: return
        DBManager.execute_query("DELETE FROM production_plan")
        count = 0
        for r in rows:
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
        self._save_csv("Sample_Plan.csv", 
                       ["PRESS", "DAYLIGHT", "TYRE_SIZE", "CORE_SIZE", "BRAND", "PATTERN", "QUALITY", "MOULD_ID", "TYPE", "TYRE WEIGHT", "PRODUCTION_REQUIREMENT"], 
                       [["P-01", "1", "12.00-20", "10", "BRAND-X", "LUG", "A-GRADE", "M123", "STD", "45.5", "20"]])

    # --- NEW: MASTER ORDERS ---
    def setup_master_orders_tab(self):
        tk.Label(self.tab_master, text="📦 Master Order Book", font=("Segoe UI", 12, "bold"), bg="white").pack(pady=15)
        
        f_top = tk.Frame(self.tab_master, bg="#F4F6F7", pady=10, padx=10, relief="ridge", bd=1)
        f_top.pack(fill="x", padx=20, pady=5)
        
        # Form Elements
        tk.Label(f_top, text="PI Number:", bg="#F4F6F7", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", padx=2)
        self.mo_pi = tk.Entry(f_top, width=18); self.mo_pi.grid(row=1, column=0, padx=2)

        tk.Label(f_top, text="Customer:", bg="#F4F6F7", font=("Segoe UI", 9, "bold")).grid(row=0, column=1, sticky="w", padx=2)
        self.mo_cust = tk.Entry(f_top, width=18); self.mo_cust.grid(row=1, column=1, padx=2)

        tk.Label(f_top, text="Size:", bg="#F4F6F7", font=("Segoe UI", 9, "bold")).grid(row=0, column=2, sticky="w", padx=2)
        self.mo_size = tk.Entry(f_top, width=12); self.mo_size.grid(row=1, column=2, padx=2)

        tk.Label(f_top, text="Core:", bg="#F4F6F7", font=("Segoe UI", 9, "bold")).grid(row=0, column=3, sticky="w", padx=2)
        self.mo_core = tk.Entry(f_top, width=8); self.mo_core.grid(row=1, column=3, padx=2)

        tk.Label(f_top, text="Brand:", bg="#F4F6F7", font=("Segoe UI", 9, "bold")).grid(row=0, column=4, sticky="w", padx=2)
        self.mo_brand = tk.Entry(f_top, width=12); self.mo_brand.grid(row=1, column=4, padx=2)
        
        tk.Label(f_top, text="Quality:", bg="#F4F6F7", font=("Segoe UI", 9, "bold")).grid(row=0, column=5, sticky="w", padx=2)
        self.mo_qual = tk.Entry(f_top, width=12); self.mo_qual.grid(row=1, column=5, padx=2)

        tk.Label(f_top, text="Req Qty:", bg="#F4F6F7", font=("Segoe UI", 9, "bold")).grid(row=0, column=6, sticky="w", padx=2)
        self.mo_qty = tk.Entry(f_top, width=8); self.mo_qty.grid(row=1, column=6, padx=2)

        # Buttons Grid
        tk.Button(f_top, text="➕ ADD MANUAL", command=self.add_master_order, bg="#27AE60", fg="white", font=("Segoe UI", 9, "bold")).grid(row=1, column=7, padx=10)
        
        # CSV Actions directly below form
        f_csv = tk.Frame(self.tab_master, bg="white")
        f_csv.pack(pady=5)
        tk.Button(f_csv, text="⬇ Sample CSV", command=self.download_sample_master_csv).pack(side="left", padx=5)
        tk.Button(f_csv, text="📂 Upload CSV", command=self.upload_master_csv, bg="#8E44AD", fg="white").pack(side="left", padx=5)
        tk.Button(f_csv, text="🔄 Refresh", command=self.load_master_orders).pack(side="left", padx=5)

        # Treeview
        cols = ("ID", "PI Number", "Customer", "Size", "Brand", "Req Qty", "Produced", "Status")
        self.tree_mo = ttk.Treeview(self.tab_master, columns=cols, show="headings", height=15)
        for c in cols: self.tree_mo.heading(c, text=c)
        
        self.tree_mo.column("ID", width=40, anchor="center")
        self.tree_mo.column("Req Qty", width=80, anchor="center")
        self.tree_mo.column("Produced", width=80, anchor="center")
        self.tree_mo.column("Status", width=100, anchor="center")
        self.tree_mo.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.load_master_orders()

    # ==========================================
    # --- 📚 TYRE MASTER (PRODUCT CATALOG) ---
    # ==========================================
    def setup_catalog_tab(self):
        tk.Label(self.tab_catalog, text="📚 Master Tyre Catalog", font=("Segoe UI", 12, "bold"), bg="white").pack(pady=15)
        
        f_top = tk.Frame(self.tab_catalog, bg="#F4F6F7", pady=10, padx=10, relief="ridge", bd=1)
        f_top.pack(fill="x", padx=20, pady=5)
        
        # Form Elements
        tk.Label(f_top, text="Tyre Size:", bg="#F4F6F7", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", padx=2)
        self.cat_size = tk.Entry(f_top, width=15); self.cat_size.grid(row=1, column=0, padx=2)

        tk.Label(f_top, text="Core Size:", bg="#F4F6F7", font=("Segoe UI", 9, "bold")).grid(row=0, column=1, sticky="w", padx=2)
        self.cat_core = tk.Entry(f_top, width=10); self.cat_core.grid(row=1, column=1, padx=2)

        tk.Label(f_top, text="Brand:", bg="#F4F6F7", font=("Segoe UI", 9, "bold")).grid(row=0, column=2, sticky="w", padx=2)
        self.cat_brand = tk.Entry(f_top, width=15); self.cat_brand.grid(row=1, column=2, padx=2)

        tk.Label(f_top, text="Quality:", bg="#F4F6F7", font=("Segoe UI", 9, "bold")).grid(row=0, column=3, sticky="w", padx=2)
        self.cat_qual = tk.Entry(f_top, width=15); self.cat_qual.grid(row=1, column=3, padx=2)

        tk.Label(f_top, text="Target Wt (kg):", bg="#F4F6F7", font=("Segoe UI", 9, "bold")).grid(row=0, column=4, sticky="w", padx=2)
        self.cat_wt = tk.Entry(f_top, width=12); self.cat_wt.grid(row=1, column=4, padx=2)

        # Buttons Grid
        tk.Button(f_top, text="➕ ADD TYRE", command=self.add_catalog_item, bg="#27AE60", fg="white", font=("Segoe UI", 9, "bold")).grid(row=1, column=5, padx=15)
        
        # CSV Actions directly below form
        f_csv = tk.Frame(self.tab_catalog, bg="white")
        f_csv.pack(pady=5)
        tk.Button(f_csv, text="⬇ Sample CSV", command=self.download_sample_catalog_csv).pack(side="left", padx=5)
        tk.Button(f_csv, text="📂 Upload CSV", command=self.upload_catalog_csv, bg="#8E44AD", fg="white").pack(side="left", padx=5)
        tk.Button(f_csv, text="🗑️ Delete Selected", command=self.delete_catalog_item, bg="#E74C3C", fg="white").pack(side="left", padx=5)
        tk.Button(f_csv, text="🔄 Refresh", command=self.load_catalog).pack(side="left", padx=5)

        # Treeview
        cols = ("SKU ID", "Tyre Size", "Core Size", "Brand", "Quality", "Baseline Wt", "Status")
        self.tree_cat = ttk.Treeview(self.tab_catalog, columns=cols, show="headings", height=15)
        for c in cols: self.tree_cat.heading(c, text=c)
        
        self.tree_cat.column("SKU ID", width=60, anchor="center")
        self.tree_cat.column("Core Size", width=80, anchor="center")
        self.tree_cat.column("Baseline Wt", width=100, anchor="center")
        self.tree_cat.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.load_catalog()

    def load_catalog(self):
        for i in self.tree_cat.get_children(): self.tree_cat.delete(i)
        query = "SELECT sku_id, tyre_size, core_size, brand, quality, baseline_weight, CASE WHEN is_active THEN 'ACTIVE' ELSE 'INACTIVE' END FROM product_catalog ORDER BY tyre_size, core_size"
        res = DBManager.fetch_data(query)
        if res:
            for r in res: self.tree_cat.insert("", "end", values=r)

    def add_catalog_item(self):
        size = self.cat_size.get().strip().upper()
        core = self.cat_core.get().strip().upper()
        brand = self.cat_brand.get().strip().upper()
        qual = self.cat_qual.get().strip().upper()
        
        try: wt = float(self.cat_wt.get().strip())
        except ValueError: return messagebox.showerror("Error", "Baseline Weight must be a number.")
            
        if not all([size, core, brand, qual]):
            return messagebox.showerror("Error", "Please fill all text fields.")
            
        q = "INSERT INTO product_catalog (tyre_size, core_size, brand, quality, baseline_weight) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (tyre_size, core_size, brand, quality) DO UPDATE SET baseline_weight=EXCLUDED.baseline_weight"
        if DBManager.execute_query(q, (size, core, brand, qual, wt)):
            self.load_catalog()
            for ent in [self.cat_size, self.cat_core, self.cat_brand, self.cat_qual, self.cat_wt]:
                ent.delete(0, tk.END)
            messagebox.showinfo("Success", "Tyre added to Master Catalog.")

    def delete_catalog_item(self):
        sel = self.tree_cat.selection()
        if not sel: return messagebox.showwarning("Warning", "Select a Tyre to delete.")
        sku = self.tree_cat.item(sel[0])['values'][0]
        
        if messagebox.askyesno("Confirm", f"Delete SKU {sku} from Catalog?"):
            DBManager.execute_query("DELETE FROM product_catalog WHERE sku_id=%s", (sku,))
            self.load_catalog()

    def upload_catalog_csv(self):
        rows = self._read_csv_file()
        if not rows: return
        count = 0
        for r in rows:
            try: wt = float(r.get('BASELINE_WT', 0))
            except: wt = 0.0
            
            q = "INSERT INTO product_catalog (tyre_size, core_size, brand, quality, baseline_weight) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (tyre_size, core_size, brand, quality) DO UPDATE SET baseline_weight=EXCLUDED.baseline_weight"
            if DBManager.execute_query(q, (r.get('TYRE_SIZE'), r.get('CORE_SIZE'), r.get('BRAND'), r.get('QUALITY'), wt)):
                count += 1
        messagebox.showinfo("Success", f"Uploaded/Updated {count} Tyres in Master Catalog")
        self.load_catalog()

    def download_sample_catalog_csv(self):
        self._save_csv("Sample_Tyre_Master.csv", 
                       ["TYRE_SIZE", "CORE_SIZE", "BRAND", "QUALITY", "BASELINE_WT"], 
                       [["16X6-8", "4.33", "BOSON", "PREMIUM", "45.50"], ["5.00-8", "3.00", "BOSON", "STANDARD", "22.10"]])    

    def load_master_orders(self):
        for i in self.tree_mo.get_children(): self.tree_mo.delete(i)
        query = "SELECT order_id, pi_number, customer_name, tyre_size, brand, req_qty, produced_qty, status FROM master_orders ORDER BY order_id DESC"
        res = DBManager.fetch_data(query)
        if res:
            for r in res: self.tree_mo.insert("", "end", values=r)

    def add_master_order(self):
        pi = self.mo_pi.get().strip(); cust = self.mo_cust.get().strip()
        size = self.mo_size.get().strip(); core = self.mo_core.get().strip()
        brand = self.mo_brand.get().strip(); qual = self.mo_qual.get().strip()
        
        try: qty = int(self.mo_qty.get().strip())
        except ValueError: return messagebox.showerror("Error", "Required Quantity must be a number.")
            
        if not all([pi, cust, size, core, brand, qty]):
            return messagebox.showerror("Error", "Please fill all required fields.")
            
        q = "INSERT INTO master_orders (pi_number, customer_name, tyre_size, core_size, brand, quality, req_qty) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        if DBManager.execute_query(q, (pi, cust, size, core, brand, qual, qty)):
            self.load_master_orders()
            # Clear fields after success
            for ent in [self.mo_pi, self.mo_cust, self.mo_size, self.mo_core, self.mo_brand, self.mo_qual, self.mo_qty]:
                ent.delete(0, tk.END)
            messagebox.showinfo("Success", "Order added to Master Book.")

    def upload_master_csv(self):
        rows = self._read_csv_file()
        if not rows: return
        count = 0
        for r in rows:
            req = r.get('REQ_QTY', 0)
            if not req: req = 0
            q = "INSERT INTO master_orders (pi_number, customer_name, tyre_size, core_size, brand, quality, req_qty) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            if DBManager.execute_query(q, (r.get('PI_NUMBER'), r.get('CUSTOMER'), r.get('SIZE'), r.get('CORE'), r.get('BRAND'), r.get('QUALITY'), req)):
                count += 1
        messagebox.showinfo("Success", f"Uploaded {count} Master Orders")
        self.load_master_orders()

    def download_sample_master_csv(self):
        self._save_csv("Sample_Master_Orders.csv", 
                       ["PI_NUMBER", "CUSTOMER", "SIZE", "CORE", "BRAND", "QUALITY", "REQ_QTY"], 
                       [["VTPL/EX/PI/15A", "BOSON RUSSIA", "16X6-8", "4.33", "BOSON", "PREMIUM", "50"]])

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
        
    def refresh_defect_list(self): 
        self._refresh_tree(self.tree_defects, "SELECT defect_code, defect_name, defect_type, defect_reason FROM qc_defects_master ORDER BY defect_code")
        
    
    def download_sample_defect(self): 
        self._save_csv("Sample_Defects.csv", ["DEFECT_CODE", "DEFECT_NAME", "DEFECT_TYPE", "REASON"], [["DD001", "UNDER CURE", "DIRECT", "LESS TEMP"]])    

    def upload_defects(self):
        rows = self._read_csv_file()
        if not rows: return
        count = 0
        for r in rows:
            if DBManager.execute_query("INSERT INTO qc_defects_master (defect_code, defect_name, defect_type, defect_reason) VALUES (%s, %s, %s, %s) ON CONFLICT (defect_code) DO UPDATE SET defect_name=EXCLUDED.defect_name", 
                                       (r.get('DEFECT_CODE'), r.get('DEFECT_NAME'), r.get('DEFECT_TYPE'), r.get('REASON'))): count += 1
        messagebox.showinfo("Success", f"Uploaded {count} defects"); self.refresh_defect_list()

    # ==========================================
    # --- 🎰 PRESS MASTER (WITH DAYLIGHT) ---
    # ==========================================
    def setup_press_master_tab(self):
        tk.Label(self.tab_presses, text="🎰 Manage Factory Presses & Daylights", font=("Segoe UI", 12, "bold"), bg="white").pack(pady=15)
        
        f_top = tk.Frame(self.tab_presses, bg="#F4F6F7", pady=10, padx=10, relief="ridge", bd=1)
        f_top.pack(fill="x", padx=20, pady=5)
        
        tk.Label(f_top, text="Press ID:", bg="#F4F6F7", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", padx=2)
        self.pm_id = tk.Entry(f_top, width=12); self.pm_id.grid(row=1, column=0, padx=2)

        # --- NEW: Daylight Dropdown ---
        tk.Label(f_top, text="Daylight:", bg="#F4F6F7", font=("Segoe UI", 9, "bold")).grid(row=0, column=1, sticky="w", padx=2)
        self.pm_dl = ttk.Combobox(f_top, values=["TOP", "BOTTOM", "SINGLE", "1", "2", "3", "4"], width=10)
        self.pm_dl.grid(row=1, column=1, padx=2)

        tk.Label(f_top, text="Status:", bg="#F4F6F7", font=("Segoe UI", 9, "bold")).grid(row=0, column=2, sticky="w", padx=2)
        self.pm_status = ttk.Combobox(f_top, values=["ACTIVE", "MAINTENANCE", "INACTIVE"], state="readonly", width=15)
        self.pm_status.current(0); self.pm_status.grid(row=1, column=2, padx=2)

        tk.Label(f_top, text="Remarks:", bg="#F4F6F7", font=("Segoe UI", 9, "bold")).grid(row=0, column=3, sticky="w", padx=2)
        self.pm_remarks = tk.Entry(f_top, width=30); self.pm_remarks.grid(row=1, column=3, padx=2)

        tk.Button(f_top, text="💾 SAVE", command=self.save_press, bg="#27AE60", fg="white", font=("Segoe UI", 9, "bold")).grid(row=1, column=4, padx=15)
        # --- NEW: Delete Button ---
        tk.Button(f_top, text="❌ DELETE", command=self.delete_press, bg="#C0392B", fg="white", font=("Segoe UI", 9, "bold")).grid(row=1, column=5, padx=5)
        
        cols = ("Press ID", "Daylight", "Status", "Remarks")
        self.tree_pm = ttk.Treeview(self.tab_presses, columns=cols, show="headings", height=15)
        for c in cols: self.tree_pm.heading(c, text=c)
        
        self.tree_pm.column("Press ID", width=100, anchor="center")
        self.tree_pm.column("Daylight", width=100, anchor="center")
        self.tree_pm.column("Status", width=120, anchor="center")
        self.tree_pm.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.load_press_master()

    def save_press(self):
        pid = self.pm_id.get().strip().upper()
        dl = self.pm_dl.get().strip().upper() # Grab daylight
        status = self.pm_status.get()
        rem = self.pm_remarks.get().strip()
        
        if not pid or not dl: return messagebox.showerror("Error", "Enter both Press ID and Daylight", parent=self.root)
        
        # Notice the ON CONFLICT now checks both press_id AND daylight
        q = """INSERT INTO press_master (press_id, daylight, status, remarks) 
               VALUES (%s, %s, %s, %s) 
               ON CONFLICT (press_id, daylight) DO UPDATE 
               SET status=EXCLUDED.status, remarks=EXCLUDED.remarks"""
               
        if DBManager.execute_query(q, (pid, dl, status, rem)):
            self.pm_id.delete(0, tk.END); self.pm_dl.set(''); self.pm_remarks.delete(0, tk.END)
            self.load_press_master()
            messagebox.showinfo("Success", f"{pid} ({dl}) Saved!", parent=self.root)

    def delete_press(self):
        sel = self.tree_pm.selection()
        if not sel: 
            return messagebox.showwarning("Warning", "Select a Press to delete from the list first.", parent=self.root)
            
        # Get the specific Press ID and Daylight from the clicked row
        item = self.tree_pm.item(sel[0])['values']
        press_id = str(item[0])
        daylight = str(item[1])
        
        # Ask for confirmation so nobody accidentally deletes a machine!
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to permanently delete {press_id} ({daylight})?", parent=self.root):
            
            # Execute the SQL delete command
            q = "DELETE FROM press_master WHERE press_id=%s AND daylight=%s"
            if DBManager.execute_query(q, (press_id, daylight)):
                self.load_press_master()
                messagebox.showinfo("Success", f"{press_id} ({daylight}) has been deleted.", parent=self.root)        

    def load_press_master(self):
        for i in self.tree_pm.get_children(): self.tree_pm.delete(i)
        res = DBManager.fetch_data("SELECT press_id, daylight, status, remarks FROM press_master ORDER BY press_id, daylight")
        if res:
            for r in res: self.tree_pm.insert("", "end", values=r)

    

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
            messagebox.showinfo("Success", "File Saved",parent=self.root)

    def _refresh_tree(self, tree, query):
        for i in tree.get_children(): tree.delete(i)
        res = DBManager.fetch_data(query)
        if res:
            for r in res: tree.insert("", "end", values=r)

if __name__ == "__main__":
    root = tk.Tk(); app = AdminDashboard(root); root.mainloop()