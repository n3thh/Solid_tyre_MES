import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import datetime
import platform
from db_manager import DBManager

class GlobalDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("📊 Global Factory Analytics & Traceability")
        self.root.geometry("1400x900")
        self.root.configure(bg="#F4F6F7")

        # 1. Initialize Variables first
        self.start_date = tk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))
        self.end_date = tk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))
        self.search_var = tk.StringVar()

        # 2. Build the UI (This creates tree_sum and tree_det)
        self.setup_ui()

        # 3. NOW refresh the data
        self.refresh_data()

    def setup_ui(self):
        # Header & Filter Bar
        header = tk.Frame(self.root, bg="#16A085", pady=10)
        header.pack(fill="x")
        
        # Search Box
        f_search = tk.Frame(header, bg="#16A085")
        f_search.pack(side="left", padx=20)
        tk.Label(f_search, text="🔍 SEARCH:", font=("Segoe UI", 9, "bold"), fg="white", bg="#16A085").pack(side="left")
        self.ent_search = tk.Entry(f_search, textvariable=self.search_var, width=25)
        self.ent_search.pack(side="left", padx=10)
        self.ent_search.bind("<KeyRelease>", self.filter_grid)
        
        # Date Filters
        f_date = tk.Frame(header, bg="#16A085")
        f_date.pack(side="right", padx=20)
        tk.Label(f_date, text="From:", bg="#16A085", fg="white").pack(side="left")
        tk.Entry(f_date, textvariable=self.start_date, width=12).pack(side="left", padx=5)
        tk.Label(f_date, text="To:", bg="#16A085", fg="white").pack(side="left")
        tk.Entry(f_date, textvariable=self.end_date, width=12).pack(side="left", padx=5)
        tk.Button(f_date, text="🔄 REFRESH DATA", command=self.refresh_data, bg="#1ABC9C", fg="white", font=("Segoe UI", 9, "bold")).pack(side="left", padx=10)

        # Tabs
        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.tab_summary = tk.Frame(self.nb, bg="white")
        self.tab_detailed = tk.Frame(self.nb, bg="white")
        
        self.nb.add(self.tab_summary, text=" 📈 Executive Summary ")
        self.nb.add(self.tab_detailed, text=" 📋 Full Traceability Grid ")

        # Grid Styling
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#FFFFFF", foreground="black", rowheight=28, fieldbackground="#FFFFFF", font=("Segoe UI", 10))
        style.map("Treeview", background=[('selected', '#3498DB')])
        
        # --- TAB 1: SUMMARY ---
        cols_sum = ("Process", "Total Count", "A-Grade", "B-Grade", "Scrap", "Yield %")
        self.tree_sum = ttk.Treeview(self.tab_summary, columns=cols_sum, show="headings")
        for c in cols_sum: 
            self.tree_sum.heading(c, text=c)
            self.tree_sum.column(c, anchor="center")
        self.tree_sum.pack(fill="both", expand=True, padx=10, pady=10)

        # --- TAB 2: DETAILED TRACEABILITY GRID ---
        f_master = tk.Frame(self.tab_detailed, bg="white")
        f_master.pack(fill="both", expand=True, padx=10, pady=10)

        self.cols_det = (
            "B-ID", "Serial", "Size", "Brand", "Grade", "Status",
            "Built At", "Builder", "Tread Batch", "Core Batch", "Green Wt",
            "Cured At", "Curing Op", "Press", "Mould", "Cured Wt", "Flash",
            "QC At", "Inspector", "QC Grade", "Core Hard", "Tread Hard", 
            "Defects", "Remarks", "Customer", "Despatch Date"
        )

        scroll_y = tk.Scrollbar(f_master, orient="vertical")
        scroll_x = tk.Scrollbar(f_master, orient="horizontal")
        
        self.tree_det = ttk.Treeview(
            f_master, columns=self.cols_det, show="headings", 
            yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set
        )

        scroll_y.config(command=self.tree_det.yview)
        scroll_x.config(command=self.tree_det.xview)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        self.tree_det.pack(side="left", fill="both", expand=True)

        for c in self.cols_det:
            self.tree_det.heading(c, text=c)
            self.tree_det.column(c, width=140, anchor="center")

        # Zebra Striping Tags
        self.tree_det.tag_configure('odd', background='#F9F9F9')
        self.tree_det.tag_configure('even', background='#FFFFFF')
        self.tree_det.tag_configure('A-GRADE', foreground='#27AE60', font=('Segoe UI', 10, 'bold'))
        self.tree_det.tag_configure('SCRAP', foreground='#E74C3C', font=('Segoe UI', 10, 'bold'))

        # --- BIND DOUBLE CLICK ---
        self.tree_det.bind("<Double-1>", self.show_digital_passport)

        # Footer
        footer = tk.Frame(self.root, bg="#F4F6F7", pady=10)
        footer.pack(fill="x", padx=20)
        tk.Label(footer, text="💡 Double-click any row to view Full Digital Passport", font=("Segoe UI", 9, "italic"), bg="#F4F6F7", fg="#7F8C8D").pack(side="left")
        tk.Button(footer, text="📥 EXPORT FILTERED CSV", command=self.export_global_csv, bg="#27AE60", fg="white", font=("Segoe UI", 11, "bold"), padx=20).pack(side="right")

    def show_digital_passport(self, event):
        item = self.tree_det.selection()
        if not item: return
        
        data = self.tree_det.item(item[0])['values']
        
        # Pop-up Window
        pop = tk.Toplevel(self.root)
        pop.title(f"Digital Passport: {data[1]}")
        pop.geometry("600x800")
        pop.configure(bg="white")
        
        # Header color based on grade
        header_color = "#27AE60" if data[19] == "A-GRADE" else "#E74C3C"
        f_head = tk.Frame(pop, bg=header_color, pady=15)
        f_head.pack(fill="x")
        tk.Label(f_head, text="TYRE DIGITAL PASSPORT", font=("Segoe UI", 16, "bold"), fg="white", bg=header_color).pack()
        tk.Label(f_head, text=f"Serial No: {data[1]}", font=("Segoe UI", 11), fg="white", bg=header_color).pack()

        f_body = tk.Frame(pop, bg="white", padx=30, pady=20)
        f_body.pack(fill="both", expand=True)

        def add_section(title):
            tk.Label(f_body, text=f"\n{title}", font=("Segoe UI", 11, "bold"), fg="#2980B9", bg="white").pack(anchor="w")
            tk.Frame(f_body, height=2, bg="#ECF0F1").pack(fill="x", pady=2)

        def add_field(label, val):
            row = tk.Frame(f_body, bg="white")
            row.pack(fill="x", pady=2)
            tk.Label(row, text=f"{label}:", font=("Segoe UI", 10, "bold"), fg="#7F8C8D", bg="white", width=18, anchor="w").pack(side="left")
            tk.Label(row, text=val, font=("Segoe UI", 10), fg="#2C3E50", bg="white").pack(side="left")

        # Section 1: Building
        add_section("1. BUILDING DETAILS (PC1)")
        add_field("B-ID", data[0])
        add_field("Tyre Size", data[2])
        add_field("Brand", data[3])
        add_field("Built Time", data[6])
        add_field("Builder", data[7])
        add_field("Green Wt", f"{data[10]} kg")

        # Section 2: Curing
        add_section("2. CURING DETAILS (PC2)")
        add_field("Cured Time", data[11])
        add_field("Curing Op", data[12])
        add_field("Press/Mould", f"{data[13]} / {data[14]}")
        add_field("Final Wt", f"{data[15]} kg")

        # Section 3: Quality (Existing)
        add_section("3. QUALITY CONTROL (PC3)")
        add_field("Inspector", data[18])
        add_field("Final Grade", data[19])
        add_field("Hardness", f"Core: {data[20]} | Tread: {data[21]}")
        add_field("Remarks", data[22] if data[22] else "None")

        # Section 4: Logistics & Despatch
        add_section("4. LOGISTICS & DESPATCH")

        # Correcting the indexing based on the query above
        # Index 23 = customer_name, Index 24 = despatched_at
        cust_name = data[23] if len(data) > 23 and data[23] not in [None, "None", ""] else "IN STOCK"
        disp_date = data[24] if len(data) > 24 and data[24] not in [None, "None", ""] else "WAREHOUSE"

        # Only show SHIPPED if there is actually a despatch date
        is_shipped = (disp_date != "WAREHOUSE")

        add_field("Customer", cust_name)
        add_field("Despatch Date", disp_date)
        add_field("Status", "🚚 SHIPPED" if is_shipped else "📦 IN WAREHOUSE")

    def refresh_data(self):
        sd = self.start_date.get()
        ed = self.end_date.get()
        
        # Safe clearing of trees
        for i in self.tree_sum.get_children(): self.tree_sum.delete(i)
        for i in self.tree_det.get_children(): self.tree_det.delete(i)

        # 1. Summary Metrics
        build_count = DBManager.fetch_data("SELECT COUNT(*) FROM pc1_building WHERE DATE(created_at) BETWEEN %s AND %s", (sd, ed))[0][0]
        cure_count = DBManager.fetch_data("SELECT COUNT(*) FROM pc2_curing WHERE DATE(start_time) BETWEEN %s AND %s", (sd, ed))[0][0]
        qc_data = DBManager.fetch_data("SELECT grade, COUNT(*) FROM pc3_quality WHERE DATE(inspected_at) BETWEEN %s AND %s GROUP BY grade", (sd, ed))
        
        qc_map = {r[0]: r[1] for r in qc_data} if qc_data else {}
        a_grade, b_grade, scrap = qc_map.get("A-GRADE", 0), qc_map.get("B-GRADE", 0), qc_map.get("SCRAP", 0)
        total_qc = a_grade + b_grade + scrap
        yield_pct = (a_grade / total_qc * 100) if total_qc > 0 else 0

        self.tree_sum.insert("", "end", values=("BUILDING (PC1)", build_count, "-", "-", "-", "-"))
        self.tree_sum.insert("", "end", values=("CURING (PC2)", cure_count, "-", "-", "-", "-"))
        self.tree_sum.insert("", "end", values=("QUALITY (PC3)", total_qc, a_grade, b_grade, scrap, f"{yield_pct:.1f}%"))

        # 2. Detailed Data
        # Inside refresh_data(self):
        query = """
            SELECT 
                b.b_id, COALESCE(c.serial_no, 'PENDING'), b.tyre_size, b.brand, b.quality, b.status,
                TO_CHAR(b.created_at, 'YYYY-MM-DD HH24:MI'), b.operator_id, b.batch_tread, b.batch_core, b.green_tyre_weight,
                TO_CHAR(c.end_time, 'YYYY-MM-DD HH24:MI'), c.operator_name, c.press_no, c.mould_no, c.final_cured_weight, c.flash_waste,
                TO_CHAR(q.inspected_at, 'YYYY-MM-DD HH24:MI'), q.inspector_name, q.grade, 
                -- Concatenating hardness results for the grid
                (COALESCE(q.hardness_core_min,0) || '-' || COALESCE(q.hardness_core_max,0)) as core_hard, 
                (COALESCE(q.hardness_tread_min,0) || '-' || COALESCE(q.hardness_tread_max,0)) as tread_hard, 
                COALESCE(q.defect_codes, 'NONE') as defects,
                q.qc_remarks,
                COALESCE(q.customer_name, 'IN STOCK'), 
                CASE WHEN q.despatched_at IS NOT NULL THEN TO_CHAR(q.despatched_at, 'YYYY-MM-DD') ELSE 'WAREHOUSE' END
            FROM pc1_building b
            LEFT JOIN pc2_curing c ON b.b_id = c.b_id
            LEFT JOIN pc3_quality q ON c.serial_no = q.tyre_id
            WHERE DATE(b.created_at) BETWEEN %s AND %s
            ORDER BY b.created_at DESC
        """
        self.master_data = DBManager.fetch_data(query, (sd, ed))
        self.populate_grid(self.master_data)

    def populate_grid(self, data_list):
        for i in self.tree_det.get_children(): self.tree_det.delete(i)
        if not data_list: return
        for idx, row in enumerate(data_list):
            tag_list = ['even' if idx % 2 == 0 else 'odd']
            if row[19]: tag_list.append(row[19])
            self.tree_det.insert("", "end", values=row, tags=tag_list)

    def filter_grid(self, event):
        search_term = self.search_var.get().strip().upper()
        if not search_term:
            self.populate_grid(self.master_data)
            return
        filtered = [row for row in self.master_data if any(search_term in str(cell).upper() for cell in row)]
        self.populate_grid(filtered)

    def export_global_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile=f"Global_Report_{self.start_date.get()}.csv")
        if not path: return
        with open(path, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(self.cols_det)
            for child in self.tree_det.get_children():
                w.writerow(self.tree_det.item(child)["values"])
        messagebox.showinfo("Success", "Report Exported!")