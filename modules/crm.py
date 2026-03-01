import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import csv
import math
from db_manager import DBManager

# ================= CONFIGURATION =================
C_BG = "#F4F6F7"
C_CARD = "#FFFFFF"
C_HEADER = "#D35400"   # Burnt Orange for CRM/Sales
C_SUCCESS = "#27AE60"
C_WARN = "#F39C12"
C_ERR = "#E74C3C"
C_TEXT = "#2C3E50"

class CRMApp:
    def __init__(self, root, current_user="MANAGER"):
        self.root = root
        self.root.title(f"CRM & Sales Console (User: {current_user})")
        self.root.geometry("1300x850")
        self.root.configure(bg=C_BG)
        
        self.ensure_db_schema()

        # --- VARIABLES ---
        # Customer Vars
        self.c_id = tk.StringVar()
        self.c_name = tk.StringVar()
        self.c_region = tk.StringVar(value="DOMESTIC")
        self.c_market = tk.StringVar(value="LOCAL")
        self.c_currency = tk.StringVar(value="INR")
        
        # Currency Vars
        self.cur_rate_usd = tk.StringVar()
        
        # Order Vars
        self.o_pi = tk.StringVar()
        self.o_cust = tk.StringVar()
        self.o_size = tk.StringVar()
        self.o_core = tk.StringVar()
        self.o_brand = tk.StringVar()
        self.o_qual = tk.StringVar()
        self.o_type = tk.StringVar(value="CUSHION") # Updated Default
        self.o_pattern = tk.StringVar(value="VXT-01") # Updated Default
        self.o_qty = tk.StringVar()
        self.o_price = tk.StringVar()
        self.o_date = tk.StringVar(value=(datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d"))
        self.o_priority = tk.StringVar(value="3") # 1=Critical, 5=Low
        
        self.customer_map = {} # Maps name -> (id, currency)
        self.exchange_rates = {'INR': 1.0}

        self.setup_ui()
        self.load_initial_data()

    def ensure_db_schema(self):
        """Automatically builds the CRM tables and upgrades Master Orders if missing."""
        queries = [
            """CREATE TABLE IF NOT EXISTS currency_rates (
                currency_code VARCHAR(10) PRIMARY KEY,
                rate_to_inr NUMERIC(10,2) DEFAULT 1.00,
                last_updated TIMESTAMP DEFAULT NOW()
            )""",
            """INSERT INTO currency_rates (currency_code, rate_to_inr) 
               VALUES ('INR', 1.00), ('USD', 83.50) ON CONFLICT DO NOTHING""",
            """CREATE TABLE IF NOT EXISTS customer_master (
                customer_id VARCHAR(50) PRIMARY KEY,
                customer_name VARCHAR(100) UNIQUE NOT NULL,
                region VARCHAR(50),
                market_type VARCHAR(20),
                default_currency VARCHAR(10) DEFAULT 'INR'
            )"""
        ]
        
        alter_orders = [
            "ALTER TABLE master_orders ADD COLUMN IF NOT EXISTS priority_level INTEGER DEFAULT 3",
            "ALTER TABLE master_orders ADD COLUMN IF NOT EXISTS committed_date DATE",
            "ALTER TABLE master_orders ADD COLUMN IF NOT EXISTS unit_price_foreign NUMERIC(10,2) DEFAULT 0.00",
            "ALTER TABLE master_orders ADD COLUMN IF NOT EXISTS currency VARCHAR(10) DEFAULT 'INR'",
            "ALTER TABLE master_orders ADD COLUMN IF NOT EXISTS unit_price_inr NUMERIC(10,2) DEFAULT 0.00",
            "ALTER TABLE master_orders ADD COLUMN IF NOT EXISTS tyre_type VARCHAR(50)",
            "ALTER TABLE master_orders ADD COLUMN IF NOT EXISTS pattern VARCHAR(50)"
        ]
        
        for q in queries:
            try: DBManager.execute_query(q)
            except: pass
            
        for q in alter_orders:
            try: DBManager.execute_query(q)
            except: pass

    def setup_ui(self):
        header = tk.Frame(self.root, bg=C_HEADER, height=70)
        header.pack(fill="x")
        tk.Label(header, text="💼 CRM & SALES COMMAND CENTER", font=("Segoe UI", 20, "bold"), bg=C_HEADER, fg="white").pack(pady=15)

        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.tab_dash = tk.Frame(nb, bg=C_BG); nb.add(self.tab_dash, text="  📈 SALES DASHBOARD  ")
        self.tab_orders = tk.Frame(nb, bg=C_BG); nb.add(self.tab_orders, text="  📦 MASTER ORDERS  ")
        self.tab_cust = tk.Frame(nb, bg=C_BG); nb.add(self.tab_cust, text="  🏢 CUSTOMERS  ")
        self.tab_curr = tk.Frame(nb, bg=C_BG); nb.add(self.tab_curr, text="  💱 CURRENCY  ")
        self.tab_prog = tk.Frame(nb, bg=C_BG)
        nb.add(self.tab_prog, text="  📊 ORDER PROGRESS  ")
        # Create an Alert Button that shows the count of lagging orders
        self.btn_alerts = tk.Button(header, text="🚨 0 ALERTS", command=self.show_notification_center, 
                            bg="#C0392B", fg="white", font=("Segoe UI", 10, "bold"), padx=10)
        self.btn_alerts.pack(side="right", padx=20, pady=15)

        # Start a background timer to refresh alerts every 60 seconds
        self.update_alert_count()
        
        self.build_dash_tab()
        self.build_orders_tab()
        self.build_cust_tab()
        self.build_curr_tab()
        self.build_progress_tab()
        
        nb.bind("<<NotebookTabChanged>>", self.on_tab_change)

    # ================= TAB 1: DASHBOARD =================
    def build_dash_tab(self):
        f_kpi = tk.Frame(self.tab_dash, bg=C_BG)
        f_kpi.pack(fill="x", pady=10)
        
        self.lbl_kpi_val = self.create_kpi_card(f_kpi, "TOTAL PENDING VALUE", "₹ 0.00 Lakhs", "#2980B9")
        self.lbl_kpi_ord = self.create_kpi_card(f_kpi, "ACTIVE ORDERS", "0", "#27AE60")
        self.lbl_kpi_late = self.create_kpi_card(f_kpi, "OVERDUE/CRITICAL", "0", "#C0392B")
        
        tk.Button(f_kpi, text="🔄 REFRESH DASHBOARD", command=self.refresh_dashboard, bg="#34495E", fg="white", font=("Segoe UI", 10, "bold")).pack(side="right", padx=20)

        card = self.create_card(self.tab_dash, "🔥 PRIORITY HOT LIST (Production Targets)")
        cols = ("Priority", "PI Number", "Customer", "Deadline", "Pending Qty", "Pending Value (₹)")
        self.tree_dash = ttk.Treeview(card, columns=cols, show="headings", height=15)
        for c in cols: self.tree_dash.heading(c, text=c)
        self.tree_dash.column("Priority", width=80, anchor="center")
        self.tree_dash.column("Deadline", width=100, anchor="center")
        self.tree_dash.column("Pending Qty", width=100, anchor="center")
        self.tree_dash.column("Pending Value (₹)", width=150, anchor="e")
        self.tree_dash.pack(fill="both", expand=True)

        self.tree_dash.tag_configure('p1', background='#FDEDEC', foreground='#C0392B')
        self.tree_dash.tag_configure('late', background='#F5B041', foreground='black')

    def create_kpi_card(self, parent, title, val, color):
        f = tk.Frame(parent, bg=color, padx=20, pady=15); f.pack(side="left", fill="x", expand=True, padx=10)
        tk.Label(f, text=title, font=("Segoe UI", 10, "bold"), bg=color, fg="white").pack()
        lbl = tk.Label(f, text=val, font=("Segoe UI", 20, "bold"), bg=color, fg="white")
        lbl.pack(pady=5)
        return lbl

    def refresh_dashboard(self):
        for i in self.tree_dash.get_children(): self.tree_dash.delete(i)
        
        # FIX: Added (status IS NULL OR status != 'CLOSED')
        q = """
            SELECT 
                priority_level, pi_number, customer_name, committed_date,
                SUM(req_qty - COALESCE(produced_qty, 0)) as pending_qty,
                SUM((req_qty - COALESCE(produced_qty, 0)) * unit_price_inr) as pending_value
            FROM master_orders
            WHERE (status IS NULL OR status != 'CLOSED') AND (req_qty - COALESCE(produced_qty, 0)) > 0
            GROUP BY priority_level, pi_number, customer_name, committed_date
            ORDER BY priority_level ASC, committed_date ASC
        """
        res = DBManager.fetch_data(q)
        
        tot_val = 0.0; tot_ord = 0; tot_late = 0
        today = datetime.date.today()
        
        if res:
            for r in res:
                pri, pi, cust, c_date, p_qty, p_val = r
                tot_val += float(p_val) if p_val else 0.0
                tot_ord += 1
                
                tag = ""
                if pri == 1: tag = "p1"
                if c_date and c_date < today: 
                    tag = "late"
                    tot_late += 1
                
                fmt_val = f"₹ {float(p_val):,.2f}" if p_val else "₹ 0.00"
                self.tree_dash.insert("", "end", values=(pri, pi, cust, c_date, p_qty, fmt_val), tags=(tag,))
        
        lakhs = tot_val / 100000.0
        self.lbl_kpi_val.config(text=f"₹ {lakhs:.2f} Lakhs")
        self.lbl_kpi_ord.config(text=str(tot_ord))
        self.lbl_kpi_late.config(text=str(tot_late))

    # ================= TAB 2: ORDERS =================
    def build_orders_tab(self):
        f_top = tk.Frame(self.tab_orders, bg=C_CARD, pady=10, padx=10, relief="solid", bd=1)
        f_top.pack(fill="x", pady=5)
        
        # --- ROW 1: Identity ---
        self.create_entry(f_top, "PI Number:", self.o_pi, 0, 0)
        tk.Label(f_top, text="Customer:", bg=C_CARD, font=("Segoe UI", 9, "bold")).grid(row=0, column=2, sticky="w", padx=5)
        self.combo_cust = ttk.Combobox(f_top, textvariable=self.o_cust, state="readonly", width=18)
        self.combo_cust.grid(row=1, column=2, padx=5)
        
        self.create_entry(f_top, "Tyre Size:", self.o_size, 0, 4)
        self.create_entry(f_top, "Core Size:", self.o_core, 0, 6)
        self.create_entry(f_top, "Brand:", self.o_brand, 0, 8)
        self.create_entry(f_top, "Grade:", self.o_qual, 0, 10)
        
        # --- ROW 2 & 3: Details (With User's Specific Tyre Types & Patterns) ---
        self.create_entry(f_top, "Req Qty:", self.o_qty, 2, 0)
        self.create_entry(f_top, "Unit Price:", self.o_price, 2, 2)
        
        tk.Label(f_top, text="Tyre Type:", bg=C_CARD, font=("Segoe UI", 9, "bold")).grid(row=2, column=4, sticky="w", padx=5)
        ttk.Combobox(f_top, textvariable=self.o_type, values=["CUSHION", "PRESS-ON-BAND(POB)", "APERTURE", "SKID-STEER"], width=15, state="readonly").grid(row=3, column=4, padx=5)

        tk.Label(f_top, text="Pattern:", bg=C_CARD, font=("Segoe UI", 9, "bold")).grid(row=2, column=6, sticky="w", padx=5)
        ttk.Combobox(f_top, textvariable=self.o_pattern, values=["VXT-01", "VXT-02", "VXR-01", "VXM-01", "VXS-01"], width=12, state="readonly").grid(row=3, column=6, padx=5)

        tk.Label(f_top, text="Deadline (YYYY-MM-DD):", bg=C_CARD, font=("Segoe UI", 9, "bold")).grid(row=2, column=8, sticky="w", padx=5)
        tk.Entry(f_top, textvariable=self.o_date, width=14, bg="#FEF9E7").grid(row=3, column=8, padx=5)
        
        tk.Label(f_top, text="Pri (1=Hi, 5=Lo):", bg=C_CARD, font=("Segoe UI", 9, "bold")).grid(row=2, column=10, sticky="w", padx=5)
        ttk.Combobox(f_top, textvariable=self.o_priority, values=["1", "2", "3", "4", "5"], width=8, state="readonly").grid(row=3, column=10, padx=5)

        # --- ROW 4: ACTION BUTTONS ---
        btn_frame = tk.Frame(f_top, bg=C_CARD)
        btn_frame.grid(row=4, column=0, columnspan=12, pady=(15, 5), sticky="we", padx=15)
        
        tk.Button(btn_frame, text="🧹 CLEAR FORM", command=self.clear_order_form, bg="#95A5A6", fg="white", font=("Segoe UI", 10, "bold"), width=15).pack(side="left", padx=5)
        tk.Button(btn_frame, text="➕ ADD / 💾 UPDATE ORDER", command=self.save_order, bg=C_SUCCESS, fg="white", font=("Segoe UI", 10, "bold")).pack(side="left", padx=5, expand=True, fill="x")
        tk.Button(btn_frame, text="🗑️ DELETE ORDER", command=self.delete_order, bg=C_ERR, fg="white", font=("Segoe UI", 10, "bold"), width=15).pack(side="right", padx=5)

        # CSV Upload Frame
        f_csv = tk.Frame(self.tab_orders, bg=C_BG)
        f_csv.pack(fill="x", pady=5)
        tk.Button(f_csv, text="📂 Upload CSV", command=self.upload_orders_csv, bg="#8E44AD", fg="white").pack(side="left")
        tk.Button(f_csv, text="⬇ Sample CSV", command=self.download_sample_orders).pack(side="left", padx=10)

        # Treeview
        cols = ("PI Number", "Customer", "Size", "Type", "Pattern", "Qty", "Price", "Val (INR)", "Deadline")
        self.tree_ord = ttk.Treeview(self.tab_orders, columns=cols, show="headings", height=15)
        for c in cols: self.tree_ord.heading(c, text=c)
        self.tree_ord.column("Qty", width=50, anchor="center")
        self.tree_ord.column("Price", width=80, anchor="e")
        self.tree_ord.column("Val (INR)", width=100, anchor="e")
        self.tree_ord.column("Deadline", width=90, anchor="center")
        self.tree_ord.pack(fill="both", expand=True, pady=10)
        
        self.tree_ord.bind('<ButtonRelease-1>', self.select_order_row)

    # --- Form Controls ---
    def clear_order_form(self):
        self.o_pi.set("")
        self.o_cust.set("")
        self.o_size.set("")
        self.o_core.set("")
        self.o_brand.set("")
        self.o_qual.set("")
        self.o_type.set("CUSHION") # Updated Default
        self.o_pattern.set("VXT-01") # Updated Default
        self.o_qty.set("")
        self.o_price.set("")
        self.o_date.set((datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d"))
        self.o_priority.set("3")

    def select_order_row(self, event):
        sel = self.tree_ord.selection()
        if not sel: return
        
        pi = str(self.tree_ord.item(sel[0])['values'][0])
        
        # Use %s so the DB driver adds the quotes for you
        q = """SELECT pi_number, customer_name, tyre_size, core_size, brand, quality, tyre_type, pattern, 
                    req_qty, unit_price_foreign, committed_date, priority_level 
            FROM master_orders WHERE pi_number = %s"""
        res = DBManager.fetch_data(q, (pi,))
        
        if res:
            r = res[0]
            self.o_pi.set(r[0])
            self.o_cust.set(r[1])
            self.o_size.set(r[2])
            self.o_core.set(r[3] if r[3] else "")
            self.o_brand.set(r[4] if r[4] else "")
            self.o_qual.set(r[5] if r[5] else "")
            self.o_type.set(r[6] if r[6] else "CUSHION")
            self.o_pattern.set(r[7] if r[7] else "VXT-01")
            self.o_qty.set(str(r[8]))
            self.o_price.set(str(r[9]))
            self.o_date.set(str(r[10]))
            self.o_priority.set(str(r[11]))

    def delete_order(self):
        pi = self.o_pi.get().strip().upper()
        if not pi:
            return messagebox.showwarning("Warning", "Please select an order to delete.",parent=self.root)
            
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to permanently delete PI Number: {pi}?", parent=self.root):
            if DBManager.execute_query("DELETE FROM master_orders WHERE pi_number = %s", (pi,)):
                messagebox.showinfo("Deleted", f"Order {pi} has been deleted.",parent=self.root)
                self.clear_order_form()
                self.refresh_orders()
                self.refresh_dashboard()

    # --- Smart Save (Insert or Update) ---
    def save_order(self):
        pi = self.o_pi.get().strip().upper()
        cust = self.o_cust.get().strip()
        size = self.o_size.get().strip().upper()
        core = self.o_core.get().strip().upper()
        brand = self.o_brand.get().strip().upper()
        qual = self.o_qual.get().strip().upper()
        t_type = self.o_type.get().strip()
        t_pattern = self.o_pattern.get().strip()
        deadline = self.o_date.get().strip()
        
        try: 
            qty = int(self.o_qty.get())
            price_for = float(self.o_price.get())
            pri = int(self.o_priority.get())
        except ValueError:
            return messagebox.showerror("Error", "Qty, Price, and Priority must be valid numbers.",parent=self.root)
            
        if not all([pi, cust, size, brand, deadline]): 
            return messagebox.showerror("Error", "Missing required fields.",parent=self.root)

        curr = "INR"
        if cust in self.customer_map: curr = self.customer_map[cust][1]
        rate = self.exchange_rates.get(curr, 1.0)
        price_inr = price_for * rate

        check_q = "SELECT order_id FROM master_orders WHERE pi_number = %s"
        existing = DBManager.fetch_data(check_q, (pi,))
        
        if existing:
            update_q = """UPDATE master_orders SET 
                            customer_name=%s, tyre_size=%s, core_size=%s, brand=%s, quality=%s, 
                            tyre_type=%s, pattern=%s, req_qty=%s, priority_level=%s, committed_date=%s, 
                            unit_price_foreign=%s, currency=%s, unit_price_inr=%s
                          WHERE pi_number=%s"""
            success = DBManager.execute_query(update_q, (cust, size, core, brand, qual, t_type, t_pattern, 
                                                         qty, pri, deadline, price_for, curr, price_inr, pi))
            msg = f"Order {pi} Updated Successfully!"
        else:
            # FIX: Adding 'OPEN' to the status so it shows up in the tables immediately
            insert_q = """INSERT INTO master_orders (
                            pi_number, customer_name, tyre_size, core_size, brand, quality, tyre_type, pattern, 
                            req_qty, priority_level, committed_date, unit_price_foreign, currency, unit_price_inr, status) 
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'OPEN')"""
            success = DBManager.execute_query(insert_q, (pi, cust, size, core, brand, qual, t_type, t_pattern, 
                                                         qty, pri, deadline, price_for, curr, price_inr))
            msg = f"New Order Added!\nTotal Value: ₹{price_inr * qty:,.2f}"

        if success:
            self.refresh_orders()
            self.refresh_dashboard()
            messagebox.showinfo("Success", msg, parent=self.root)
            self.clear_order_form() 

    def refresh_orders(self):
        for i in self.tree_ord.get_children(): self.tree_ord.delete(i)
        
        # FIX: Added (status IS NULL OR status != 'CLOSED')
        q = "SELECT pi_number, customer_name, tyre_size, tyre_type, pattern, req_qty, CONCAT(currency, ' ', unit_price_foreign), unit_price_inr * req_qty, committed_date FROM master_orders WHERE status IS NULL OR status != 'CLOSED' ORDER BY order_id DESC"
        
        res = DBManager.fetch_data(q)
        if res:
            for r in res:
                fmt_r = list(r)
                if r[7]: fmt_r[7] = f"₹ {float(r[7]):,.2f}"
                self.tree_ord.insert("", "end", values=fmt_r)

    def upload_orders_csv(self):
        rows = self._read_csv()
        if not rows: return
        count = 0
        for r in rows:
            cust = r.get('CUSTOMER', '')
            curr = "INR"
            if cust in self.customer_map: curr = self.customer_map[cust][1]
            rate = self.exchange_rates.get(curr, 1.0)
            
            try: qty = int(r.get('QTY', 0))
            except: qty = 0
            
            try: price_for = float(r.get('UNIT_PRICE', 0))
            except: price_for = 0.0
            
            price_inr = price_for * rate
            try: pri = int(r.get('PRIORITY', 3))
            except: pri = 3

            # FIX: Inserts 'OPEN' status
            q = """INSERT INTO master_orders (
                    pi_number, customer_name, tyre_size, core_size, brand, quality, tyre_type, pattern, req_qty, 
                    priority_level, committed_date, unit_price_foreign, currency, unit_price_inr, status) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'OPEN')"""
            
            if DBManager.execute_query(q, (r.get('PI_NUMBER'), cust, r.get('SIZE'), r.get('CORE'), r.get('BRAND'), r.get('GRADE'), r.get('TYPE', 'CUSHION'), r.get('PATTERN', 'VXT-01'), qty, pri, r.get('DEADLINE'), price_for, curr, price_inr)):
                count += 1
        self.refresh_orders(); self.refresh_dashboard()
        messagebox.showinfo("Success", f"Uploaded {count} Orders",parent=self.root)

    def download_sample_orders(self):
        self._save_csv("Sample_Orders_CRM.csv", 
                       ["PI_NUMBER", "CUSTOMER", "SIZE", "CORE", "BRAND", "GRADE", "TYPE", "PATTERN", "QTY", "UNIT_PRICE", "DEADLINE", "PRIORITY"], 
                       [["PI-001", "BOSON RUSSIA", "5.00-8", "3.00", "BOSON", "PREMIUM", "CUSHION", "VXT-01", "100", "1500.50", "2026-03-01", "1"]])

    # ================= TAB 3: CUSTOMERS =================
    def build_cust_tab(self):
        card = self.create_card(self.tab_cust, "Customer Master Directory")
        
        f_inp = tk.Frame(card, bg=C_CARD)
        f_inp.pack(fill="x", pady=5)
        
        self.create_entry(f_inp, "Customer ID:", self.c_id, 0, 0)
        self.create_entry(f_inp, "Customer Name:", self.c_name, 0, 2)
        
        tk.Label(f_inp, text="Region:", bg=C_CARD, font=("Segoe UI", 9, "bold")).grid(row=0, column=4, sticky="w", padx=5)
        ttk.Combobox(f_inp, textvariable=self.c_region, values=["DOMESTIC", "MIDDLE EAST", "EUROPE", "RUSSIA", "AMERICAS", "ASIA"], width=15).grid(row=1, column=4, padx=5)
        
        tk.Label(f_inp, text="Market:", bg=C_CARD, font=("Segoe UI", 9, "bold")).grid(row=0, column=6, sticky="w", padx=5)
        ttk.Combobox(f_inp, textvariable=self.c_market, values=["LOCAL", "EXPORT"], width=10, state="readonly").grid(row=1, column=6, padx=5)
        
        tk.Label(f_inp, text="Default Currency:", bg=C_CARD, font=("Segoe UI", 9, "bold")).grid(row=0, column=8, sticky="w", padx=5)
        ttk.Combobox(f_inp, textvariable=self.c_currency, values=["INR", "USD", "EUR"], width=10, state="readonly").grid(row=1, column=8, padx=5)

        tk.Button(f_inp, text="💾 SAVE", command=self.save_customer, bg=C_SUCCESS, fg="white", font=("Segoe UI", 9, "bold")).grid(row=1, column=10, padx=15)

        cols = ("Cust ID", "Name", "Region", "Market", "Currency")
        self.tree_cust = ttk.Treeview(card, columns=cols, show="headings", height=15)
        for c in cols: self.tree_cust.heading(c, text=c)
        self.tree_cust.pack(fill="both", expand=True, pady=10)

    def save_customer(self):
        cid = self.c_id.get().strip().upper()
        cname = self.c_name.get().strip().upper()
        
        if not cid or not cname: return messagebox.showerror("Error", "ID and Name required.",parent=self.root)
        
        q = """INSERT INTO customer_master (customer_id, customer_name, region, market_type, default_currency) 
               VALUES (%s, %s, %s, %s, %s) 
               ON CONFLICT (customer_id) DO UPDATE 
               SET customer_name=EXCLUDED.customer_name, region=EXCLUDED.region, market_type=EXCLUDED.market_type, default_currency=EXCLUDED.default_currency"""
        if DBManager.execute_query(q, (cid, cname, self.c_region.get(), self.c_market.get(), self.c_currency.get())):
            self.load_customers()
            self.c_id.set(""); self.c_name.set("")

    def load_customers(self):
        for i in self.tree_cust.get_children(): self.tree_cust.delete(i)
        res = DBManager.fetch_data("SELECT customer_id, customer_name, region, market_type, default_currency FROM customer_master ORDER BY customer_name")
        self.customer_map = {}
        cust_list = []
        if res:
            for r in res:
                self.tree_cust.insert("", "end", values=r)
                self.customer_map[r[1]] = (r[0], r[4])
                cust_list.append(r[1])
        if hasattr(self, 'combo_cust'): self.combo_cust['values'] = cust_list

    # ================= TAB 4: CURRENCY =================
    def build_curr_tab(self):
        card = self.create_card(self.tab_curr, "Exchange Rates (Auto-Calculates Order Value)")
        
        f = tk.Frame(card, bg=C_CARD)
        f.pack(pady=10)
        tk.Label(f, text="USD to INR Rate:", bg=C_CARD, font=("Segoe UI", 12, "bold")).pack(side="left")
        tk.Entry(f, textvariable=self.cur_rate_usd, font=("Segoe UI", 14), width=10, bg="#EAF2F8").pack(side="left", padx=10)
        tk.Button(f, text="💾 UPDATE RATE", command=self.update_currency, bg=C_HEADER, fg="white", font=("Segoe UI", 10, "bold")).pack(side="left")

        cols = ("Currency", "Rate to INR", "Last Updated")
        self.tree_curr = ttk.Treeview(card, columns=cols, show="headings", height=5)
        for c in cols: self.tree_curr.heading(c, text=c)
        self.tree_curr.pack(fill="x", pady=20)
        
       
    def update_currency(self):
        try: rate = float(self.cur_rate_usd.get())
        except: return messagebox.showerror("Error", "Invalid Rate",parent=self.root)
        
        q = "UPDATE currency_rates SET rate_to_inr=%s, last_updated=NOW() WHERE currency_code='USD'"
        if DBManager.execute_query(q, (rate,)):
            self.load_currency()
            messagebox.showinfo("Success", "Rate Updated! Future orders will use this rate.",parent=self.root)

    def load_currency(self):
        for i in self.tree_curr.get_children(): self.tree_curr.delete(i)
        res = DBManager.fetch_data("SELECT currency_code, rate_to_inr, TO_CHAR(last_updated, 'YYYY-MM-DD HH12:MI') FROM currency_rates")
        self.exchange_rates = {}
        if res:
            for r in res:
                self.tree_curr.insert("", "end", values=r)
                self.exchange_rates[r[0]] = float(r[1])
                if r[0] == 'USD': self.cur_rate_usd.set(str(r[1]))

    def build_progress_tab(self):
        """Creates the Progress Tracking tab with synchronized headers."""
        search_f = tk.Frame(self.tab_prog, bg=C_BG, pady=15)
        search_f.pack(fill="x")

        tk.Label(search_f, text="🔍 SEARCH BY PI, CUSTOMER, OR BRAND:", font=("Segoe UI", 10, "bold"), 
                bg=C_BG, fg=C_TEXT).pack(side="left", padx=(20, 10))

        self.prog_search_var = tk.StringVar()
        ent = tk.Entry(search_f, textvariable=self.prog_search_var, font=("Segoe UI", 12), width=35)
        ent.pack(side="left", padx=5)
        ent.bind("<Return>", lambda e: self.update_progress_table())

        # Action Buttons
        tk.Button(search_f, text="CHECK PROGRESS", command=self.update_progress_table, 
                bg=C_HEADER, fg="white", font=("Segoe UI", 10, "bold"), padx=15).pack(side="left", padx=10)
        
        # This button triggers the 'Priority Request' to the factory
        tk.Button(search_f, text="⚡ BOOST PRIORITY", command=self.boost_selected_order, 
                bg="#F1C40F", fg="black", font=("Segoe UI", 10, "bold"), padx=15).pack(side="left", padx=10)

        card = self.create_card(self.tab_prog, "Real-time Order Status & Predictions")
    
        # 9 COLUMNS: Visual and Data-driven
        cols = ("PI Number", "Brand", "Tyre Size", "Status", "Order Qty", "Finished", "Progress Bar", "Projected Finish", "Deadline")
    
        self.tree_prog = ttk.Treeview(card, columns=cols, show="headings", height=20)
        for c in cols:
            self.tree_prog.heading(c, text=c)
            if "Progress" in c: w = 180
            elif "Projected" in c: w = 150
            elif "Tyre Size" in c: w = 130
            else: w = 100
            self.tree_prog.column(c, width=w, anchor="center")
    
        self.tree_prog.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(card, orient="vertical", command=self.tree_prog.yview)
        self.tree_prog.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")

    def boost_selected_order(self):
        """Manually increases the priority of a selected order."""
        selected_item = self.tree_prog.selection()
        if not selected_item:
            messagebox.showwarning("Selection Required", "Please select an order to boost.", parent=self.root)
            return

        # Get the PI Number from the selected row
        pi_number = self.tree_prog.item(selected_item[0])['values'][0]

        # Update the order status to "URGENT" in the database
        # This will make it appear in red in the dashboard
        q = "UPDATE master_orders SET status='URGENT' WHERE pi_number=%s"
        if DBManager.execute_query(q, (pi_number,)):
            messagebox.showinfo("Boosted", f"Order {pi_number} has been marked as URGENT!", parent=self.root)
            self.update_progress_table() # Refresh the table to show the change

    def update_progress_table(self):
        
        search = self.prog_search_var.get().strip()
        if not search: return messagebox.showwarning("Input Required", "Enter search term")
        
        for i in self.tree_prog.get_children(): self.tree_prog.delete(i)

        # SQL calculates daily rate based on actual PC1 Building timestamps
        q = """
            SELECT 
                mo.pi_number, mo.brand, mo.tyre_size, mo.req_qty,
                COALESCE((SELECT COUNT(*) FROM pc1_building pb WHERE (TRIM(pb.pi_number) = TRIM(mo.pi_number) OR (TRIM(pb.brand) = TRIM(mo.brand) AND TRIM(pb.tyre_size) = TRIM(mo.tyre_size))) AND pb.status = 'COMPLETED'), 0) as total_fin,
                COALESCE((SELECT COUNT(*) FROM pc1_building pb WHERE (TRIM(pb.pi_number) = TRIM(mo.pi_number) OR (TRIM(pb.brand) = TRIM(mo.brand) AND TRIM(pb.tyre_size) = TRIM(mo.tyre_size))) AND pb.status = 'COMPLETED' AND pb.created_at >= NOW() - INTERVAL '24 HOURS'), 0) as daily_rate,
                mo.committed_date, mo.priority_level
            FROM master_orders mo
            WHERE mo.pi_number ILIKE %s OR mo.brand ILIKE %s OR mo.customer_name ILIKE %s
        """
        
        term = f"%{search}%"
        res = DBManager.fetch_data(q, (term, term, term))
        today = datetime.date.today()

        if not res:
            return messagebox.showinfo("No Results", f"No records found for: {search}")

        for r in res:
            pi, brand, size, o_qty, f_qty, daily_rate, deadline, priority = r
            o_qty, f_qty, daily_rate = int(o_qty or 0), int(f_qty or 0), int(daily_rate or 0)
            balance = o_qty - f_qty
            
            # --- PREDICTION LOGIC ---
            if f_qty >= o_qty:
                projected = "✅ COMPLETE"
            elif daily_rate > 0:
                days_needed = math.ceil(balance / daily_rate)
                proj_date = today + datetime.timedelta(days=days_needed)
                projected = proj_date.strftime("%Y-%m-%d")
            else:
                projected = "🛑 NO SPEED DATA"

            # --- VISUALS ---
            percent = int((f_qty / o_qty) * 100) if o_qty > 0 else 0
            progress_display = f"{'🟩' * (percent // 10)}{'⬜' * (10 - (percent // 10))} {percent}%"
            
            status = "✅ READY" if percent >= 100 else "⏳ IN PROG"
            tag = 'complete' if percent >= 100 else 'normal'

            # Smart Tag: Check if we will miss the deadline
            if projected not in ["✅ COMPLETE", "🛑 NO SPEED DATA"]:
                proj_dt_obj = datetime.datetime.strptime(projected, "%Y-%m-%d").date()
                if deadline and proj_dt_obj > deadline:
                    tag = 'danger'
                    status = "⚠️ LAGGING"
            
            if priority == 1 and percent < 100:
                tag = 'urgent'

            # INSERT: Matches the 9 columns exactly
            self.tree_prog.insert("", "end", 
                                values=(pi, brand, size, status, o_qty, f_qty, progress_display, projected, deadline),
                                tags=(tag,))

        # Final Styling
        self.tree_prog.tag_configure('complete', background='#E8F8F5', foreground='#1B5E20')
        self.tree_prog.tag_configure('urgent', background='#FFF9C4', foreground='#F57F17', font=("Segoe UI", 9, "bold"))
        self.tree_prog.tag_configure('danger', background='#FFEBEE', foreground='#B71C1C', font=("Segoe UI", 9, "bold"))

    def get_lagging_summary(self):
        """Scans all active orders to find health risks."""
        q = """
            SELECT 
                mo.pi_number, mo.customer_name, mo.committed_date, mo.req_qty,
                -- Total Finished
                COALESCE((SELECT COUNT(*) FROM pc1_building pb 
                          WHERE (TRIM(pb.pi_number) = TRIM(mo.pi_number) OR (TRIM(pb.brand) = TRIM(mo.brand) AND TRIM(pb.tyre_size) = TRIM(mo.tyre_size))) 
                          AND pb.status = 'COMPLETED'), 0) as total_fin,
                -- Production speed (last 24h)
                COALESCE((SELECT COUNT(*) FROM pc1_building pb 
                          WHERE (TRIM(pb.pi_number) = TRIM(mo.pi_number) OR (TRIM(pb.brand) = TRIM(mo.brand) AND TRIM(pb.tyre_size) = TRIM(mo.tyre_size))) 
                          AND pb.status = 'COMPLETED' AND pb.created_at >= NOW() - INTERVAL '24 HOURS'), 0) as daily_rate
            FROM master_orders mo
            WHERE mo.status != 'CLOSED'
        """
        res = DBManager.fetch_data(q)
        lagging_orders = []
        today = datetime.date.today()

        if res:
            for r in res:
                pi, cust, deadline, o_qty, f_qty, daily_rate = r
                balance = o_qty - f_qty
                
                if f_qty < o_qty and daily_rate > 0:
                    days_needed = math.ceil(balance / daily_rate)
                    proj_date = today + datetime.timedelta(days=days_needed)
                    
                    # If projected finish is past the promised date, it's a risk
                    if deadline and proj_date > deadline:
                        lagging_orders.append({
                            "pi": pi, "cust": cust, "delay": (proj_date - deadline).days
                        })
                elif daily_rate == 0 and f_qty < o_qty:
                    # Risk: No work being done on an open order
                    lagging_orders.append({"pi": pi, "cust": cust, "delay": "STALLED"})
        
        return lagging_orders    

    def show_notification_center(self):
        """Displays a list of all orders that need immediate attention."""
        alerts = self.get_lagging_summary()
        
        win = tk.Toplevel(self.root)
        win.title("🚨 CRITICAL ALERTS: LAGGING ORDERS")
        win.geometry("500x400")
        win.configure(bg="#FDF2F4") # Light red warning background
        
        tk.Label(win, text="ORDERS AT RISK OF DELAY", font=("Segoe UI", 12, "bold"), 
                 bg="#FDF2F4", fg="#B71C1C").pack(pady=10)
        
        if not alerts:
            tk.Label(win, text="✅ All production is on track!", bg="#FDF2F4").pack(pady=20)
            return

        frame = tk.Frame(win, bg="white", bd=1, relief="solid")
        frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        for a in alerts:
            row = tk.Frame(frame, bg="white", pady=5)
            row.pack(fill="x", padx=10)
            
            msg = f"PI: {a['pi']} | {a['cust']}"
            tk.Label(row, text=msg, bg="white", font=("Segoe UI", 9, "bold")).pack(side="left")
            
            detail = f"Delayed by {a['delay']} days" if isinstance(a['delay'], int) else "PRODUCTION STOPPED"
            tk.Label(row, text=detail, bg="white", fg="#E74C3C").pack(side="right")
            
            tk.Frame(frame, height=1, bg="#F2F3F4").pack(fill="x") # Separator line    
        
    # ================= HELPERS =================
    def load_initial_data(self):
        self.load_customers()
        self.load_currency()
        self.refresh_orders()
        self.refresh_dashboard()

    def on_tab_change(self, event):
        tab = event.widget.tab(event.widget.select(), "text")
        if "DASHBOARD" in tab: 
            self.refresh_dashboard()
        elif "ORDERS" in tab: 
            self.refresh_orders()
        elif "PROGRESS" in tab: 
            # Auto-refresh the table if a search term already exists
            if self.prog_search_var.get():
                self.update_progress_table()

    def create_card(self, parent, title): 
        f = tk.Frame(parent, bg=C_CARD, bd=1, relief="solid", padx=15, pady=15); f.pack(fill="both", expand=True, pady=10, padx=10)
        tk.Label(f, text=title, font=("Segoe UI", 12, "bold"), bg=C_CARD, fg=C_TEXT).pack(anchor="w", pady=(0, 10)); return f

    def create_entry(self, parent, label, var, r, c):
        tk.Label(parent, text=label, bg=C_CARD, font=("Segoe UI", 9, "bold")).grid(row=r, column=c, sticky="w", padx=5, pady=2)
        tk.Entry(parent, textvariable=var, width=15).grid(row=r+1, column=c, padx=5, pady=2)

    def _read_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if not path: return None
        data = []
        try:
            with open(path, newline='', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                reader.fieldnames = [str(n).strip().upper() for n in reader.fieldnames]
                for row in reader: data.append(row)
        except Exception as e: messagebox.showerror("Error", f"CSV Error: {e}",parent=self.root); return None
        return data

    def _save_csv(self, fname, header, rows):
        path = filedialog.asksaveasfilename(initialfile=fname, defaultextension=".csv")
        if path:
            with open(path, 'w', newline='') as f:
                w = csv.writer(f); w.writerow(header); w.writerows(rows)
            messagebox.showinfo("Success", "File Saved",parent=self.root)

    def update_alert_count(self):
        """Automatically updates the alert badge every minute."""
        alerts = self.get_lagging_summary()
        count = len(alerts)
        self.btn_alerts.config(text=f"🚨 {count} ALERTS")
        # Blink the button if there are critical alerts
        color = "#C0392B" if count > 0 else "#34495E"
        self.btn_alerts.config(bg=color)
        self.root.after(60000, self.update_alert_count) # Refresh every 60 seconds        

if __name__ == "__main__":
    root = tk.Tk(); app = CRMApp(root); root.mainloop()