import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import csv
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
        self.o_qty = tk.StringVar()
        self.o_price = tk.StringVar()
        self.o_date = tk.StringVar(value=(datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d"))
        self.o_priority = tk.StringVar(value="3") # 1=Critical, 5=Low
        self.var_tyre_type = tk.StringVar(value="Standard Black")
        self.var_pattern = tk.StringVar(value="Traction")
        
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
            "ALTER TABLE master_orders ADD COLUMN IF NOT EXISTS unit_price_inr NUMERIC(10,2) DEFAULT 0.00"
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

        self.build_dash_tab()
        self.build_orders_tab()
        self.build_cust_tab()
        self.build_curr_tab()
        
        nb.bind("<<NotebookTabChanged>>", self.on_tab_change)

    # ================= TAB 1: DASHBOARD =================
    def build_dash_tab(self):
        # KPIs
        f_kpi = tk.Frame(self.tab_dash, bg=C_BG)
        f_kpi.pack(fill="x", pady=10)
        
        self.lbl_kpi_val = self.create_kpi_card(f_kpi, "TOTAL PENDING VALUE", "₹ 0.00 Lakhs", "#2980B9")
        self.lbl_kpi_ord = self.create_kpi_card(f_kpi, "ACTIVE ORDERS", "0", "#27AE60")
        self.lbl_kpi_late = self.create_kpi_card(f_kpi, "OVERDUE/CRITICAL", "0", "#C0392B")
        
        tk.Button(f_kpi, text="🔄 REFRESH DASHBOARD", command=self.refresh_dashboard, bg="#34495E", fg="white", font=("Segoe UI", 10, "bold")).pack(side="right", padx=20)

        # Hot List Grid
        card = self.create_card(self.tab_dash, "🔥 PRIORITY HOT LIST (Production Targets)")
        cols = ("Priority", "PI Number", "Customer", "Deadline", "Pending Qty", "Pending Value (₹)")
        self.tree_dash = ttk.Treeview(card, columns=cols, show="headings", height=15)
        for c in cols: self.tree_dash.heading(c, text=c)
        self.tree_dash.column("Priority", width=80, anchor="center")
        self.tree_dash.column("Deadline", width=100, anchor="center")
        self.tree_dash.column("Pending Qty", width=100, anchor="center")
        self.tree_dash.column("Pending Value (₹)", width=150, anchor="e")
        self.tree_dash.pack(fill="both", expand=True)

        # Color coding for priorities
        self.tree_dash.tag_configure('p1', background='#FDEDEC', foreground='#C0392B') # Critical
        self.tree_dash.tag_configure('late', background='#F5B041', foreground='black') # Late

    def create_kpi_card(self, parent, title, val, color):
        f = tk.Frame(parent, bg=color, padx=20, pady=15); f.pack(side="left", fill="x", expand=True, padx=10)
        tk.Label(f, text=title, font=("Segoe UI", 10, "bold"), bg=color, fg="white").pack()
        lbl = tk.Label(f, text=val, font=("Segoe UI", 20, "bold"), bg=color, fg="white")
        lbl.pack(pady=5)
        return lbl

    def refresh_dashboard(self):
        for i in self.tree_dash.get_children(): self.tree_dash.delete(i)
        
        q = """
            SELECT 
                priority_level, pi_number, customer_name, committed_date,
                SUM(req_qty - COALESCE(produced_qty, 0)) as pending_qty,
                SUM((req_qty - COALESCE(produced_qty, 0)) * unit_price_inr) as pending_value
            FROM master_orders
            WHERE status != 'CLOSED' AND (req_qty - COALESCE(produced_qty, 0)) > 0
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
        
        # Update KPIs
        lakhs = tot_val / 100000.0
        self.lbl_kpi_val.config(text=f"₹ {lakhs:.2f} Lakhs")
        self.lbl_kpi_ord.config(text=str(tot_ord))
        self.lbl_kpi_late.config(text=str(tot_late))

    # ================= TAB 2: ORDERS =================
    def build_orders_tab(self):
        f_top = tk.Frame(self.tab_orders, bg=C_CARD, pady=10, padx=10, relief="solid", bd=1)
        f_top.pack(fill="x", pady=5)
        
        # Row 1
        self.create_entry(f_top, "PI Number:", self.o_pi, 0, 0)
        tk.Label(f_top, text="Customer:", bg=C_CARD, font=("Segoe UI", 9, "bold")).grid(row=0, column=2, sticky="w", padx=5)
        self.combo_cust = ttk.Combobox(f_top, textvariable=self.o_cust, state="readonly", width=18)
        self.combo_cust.grid(row=1, column=2, padx=5)
        
        self.create_entry(f_top, "Tyre Size:", self.o_size, 0, 4)
        self.create_entry(f_top, "Core Size:", self.o_core, 0, 6)
        self.create_entry(f_top, "Brand:", self.o_brand, 0, 8)
        self.create_entry(f_top, "Grade:", self.o_qual, 0, 10)
        
        # Row 2 (Business Logic)
        self.create_entry(f_top, "Req Qty:", self.o_qty, 2, 0)
        self.create_entry(f_top, "Unit Price (Per Tyre):", self.o_price, 2, 2)
        
        tk.Label(f_top, text="Deadline (YYYY-MM-DD):", bg=C_CARD, font=("Segoe UI", 9, "bold")).grid(row=2, column=4, sticky="w", padx=5)
        tk.Entry(f_top, textvariable=self.o_date, width=12, bg="#FEF9E7").grid(row=3, column=4, padx=5)
        
        tk.Label(f_top, text="Priority (1=High, 5=Low):", bg=C_CARD, font=("Segoe UI", 9, "bold")).grid(row=2, column=6, sticky="w", padx=5)
        ttk.Combobox(f_top, textvariable=self.o_priority, values=["1", "2", "3", "4", "5"], width=5, state="readonly").grid(row=3, column=6, padx=5)

        tk.Button(f_top, text="➕ ADD/UPDATE ORDER", command=self.save_order, bg=C_SUCCESS, fg="white", font=("Segoe UI", 9, "bold")).grid(row=3, column=8, columnspan=3, padx=15)

        # CSV Upload Frame
        f_csv = tk.Frame(self.tab_orders, bg=C_BG)
        f_csv.pack(fill="x", pady=5)
        tk.Button(f_csv, text="📂 Upload CSV", command=self.upload_orders_csv, bg="#8E44AD", fg="white").pack(side="left")
        tk.Button(f_csv, text="⬇ Sample CSV", command=self.download_sample_orders).pack(side="left", padx=10)

        # Treeview
        cols = ("PI Number", "Customer", "Size", "Qty", "Price", "Val (INR)", "Deadline", "Pri")
        self.tree_ord = ttk.Treeview(self.tab_orders, columns=cols, show="headings", height=15)
        for c in cols: self.tree_ord.heading(c, text=c)
        self.tree_ord.column("Qty", width=50, anchor="center")
        self.tree_ord.column("Price", width=80, anchor="e")
        self.tree_ord.column("Val (INR)", width=100, anchor="e")
        self.tree_ord.column("Deadline", width=90, anchor="center")
        self.tree_ord.column("Pri", width=40, anchor="center")
        self.tree_ord.pack(fill="both", expand=True, pady=10)

    def save_order(self):
        pi = self.o_pi.get().strip().upper()
        cust = self.o_cust.get().strip()
        size = self.o_size.get().strip().upper()
        core = self.o_core.get().strip().upper()
        brand = self.o_brand.get().strip().upper()
        qual = self.o_qual.get().strip().upper()
        deadline = self.o_date.get().strip()
        
        try: 
            qty = int(self.o_qty.get())
            price_for = float(self.o_price.get())
            pri = int(self.o_priority.get())
        except ValueError:
            return messagebox.showerror("Error", "Qty, Price, and Priority must be numbers.",parent=self.root)
            
        if not all([pi, cust, size, brand, deadline]): return messagebox.showerror("Error", "Missing required fields.",parent=self.root)

        # Logic: Determine Currency and INR Value
        curr = "INR"
        if cust in self.customer_map: curr = self.customer_map[cust][1]
        
        rate = self.exchange_rates.get(curr, 1.0)
        price_inr = price_for * rate

        q = """INSERT INTO master_orders (
                pi_number, customer_name, tyre_size, core_size, brand, quality, req_qty, 
                priority_level, committed_date, unit_price_foreign, currency, unit_price_inr) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
               
        if DBManager.execute_query(q, (pi, cust, size, core, brand, qual, qty, pri, deadline, price_for, curr, price_inr)):
            self.refresh_orders()
            messagebox.showinfo("Success", f"Order Added!\nTotal Value: ₹{price_inr * qty:,.2f}",parent=self.root)

    def refresh_orders(self):
        for i in self.tree_ord.get_children(): self.tree_ord.delete(i)
        q = "SELECT pi_number, customer_name, tyre_size, req_qty, CONCAT(currency, ' ', unit_price_foreign), unit_price_inr * req_qty, committed_date, priority_level FROM master_orders WHERE status != 'CLOSED' ORDER BY order_id DESC"
        res = DBManager.fetch_data(q)
        if res:
            for r in res:
                fmt_r = list(r)
                if r[5]: fmt_r[5] = f"₹ {float(r[5]):,.2f}"
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

            q = """INSERT INTO master_orders (
                    pi_number, customer_name, tyre_size, core_size, brand, quality, req_qty, 
                    priority_level, committed_date, unit_price_foreign, currency, unit_price_inr) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            if DBManager.execute_query(q, (r.get('PI_NUMBER'), cust, r.get('SIZE'), r.get('CORE'), r.get('BRAND'), r.get('GRADE'), qty, pri, r.get('DEADLINE'), price_for, curr, price_inr)):
                count += 1
        self.refresh_orders(); self.refresh_dashboard()
        messagebox.showinfo("Success", f"Uploaded {count} Orders",parent=self.root)

    def download_sample_orders(self):
        self._save_csv("Sample_Orders_CRM.csv", 
                       ["PI_NUMBER", "CUSTOMER", "SIZE", "CORE", "BRAND", "GRADE", "QTY", "UNIT_PRICE", "DEADLINE", "PRIORITY"], 
                       [["PI-001", "BOSON RUSSIA", "5.00-8", "3.00", "BOSON", "PREMIUM", "100", "1500.50", "2026-03-01", "1"]])

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
        except: return messagebox.showerror("Error", "Invalid Rate")
        
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

    # ================= HELPERS =================
    def load_initial_data(self):
        self.load_customers()
        self.load_currency()
        self.refresh_orders()
        self.refresh_dashboard()

    def on_tab_change(self, event):
        tab = event.widget.tab(event.widget.select(), "text")
        if "DASHBOARD" in tab: self.refresh_dashboard()
        elif "ORDERS" in tab: self.refresh_orders()

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

if __name__ == "__main__":
    root = tk.Tk(); app = CRMApp(root); root.mainloop()