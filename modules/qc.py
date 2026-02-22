import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import platform
import os
from db_manager import DBManager

# ================= CONFIGURATION =================
LINUX_PRINTER_PATH = "/dev/usb/lp4" 

# COLOR PALETTE (Modern & Colorful)
C_BG = "#F4F6F7"       # Light Grey Background
C_CARD = "#FFFFFF"     # White Card Background
C_HEADER = "#2C3E50"   # Dark Blue Header
C_SCAN_BG = "#D6EAF8"  # Light Blue for Scanner
C_ID_FG = "#2980B9"    # Blue Text for Identity
C_STAT_FG = "#E67E22"  # Orange Text for Status
C_WT_FG = "#27AE60"    # Green Text for Weights
C_ERR = "#E74C3C"      # Red for Errors

class FinalQCApp:
    def __init__(self, root, current_user="QC_ENGINEER"):
        self.root = root
        self.root.title(f"PC3 | Final Quality Control (User: {current_user})")
        self.root.geometry("1300x850")
        self.root.configure(bg=C_BG)
        self.current_user = current_user
        
        # --- VARIABLES ---
        self.var_scan = tk.StringVar()
        self.info_status_msg = tk.StringVar(value="Ready to Scan")
        
        # UI Basic Details
        self.ui_size = tk.StringVar(value="—")
        self.ui_mould = tk.StringVar(value="—")
        self.ui_core = tk.StringVar(value="—")
        self.ui_brand = tk.StringVar(value="—")
        self.ui_quality = tk.StringVar(value="—")
        self.ui_age = tk.StringVar(value="—")
        self.ui_fin_wt = tk.StringVar(value="—")
        self.ui_flash_wt = tk.StringVar(value="—")
        
        # Inspection Inputs
        self.var_remarks = tk.StringVar()
        self.var_defect_type = tk.StringVar(value="DIRECT")
        self.var_selected_defect = tk.StringVar()
        self.defect_list_store = []
        
        # Hardness Vars
        self.h_core_min = tk.StringVar(); self.h_core_max = tk.StringVar()
        self.h_tread_min = tk.StringVar(); self.h_tread_max = tk.StringVar()
        
        # Store full data for HTML export
        self.current_tyre_data = None

        self.ensure_db_columns()
        self.setup_ui()
        self.update_defect_list()

    def ensure_db_columns(self):
        sqls = [
            "ALTER TABLE pc3_quality ADD COLUMN IF NOT EXISTS hardness_core_min INTEGER",
            "ALTER TABLE pc3_quality ADD COLUMN IF NOT EXISTS hardness_core_max INTEGER",
            "ALTER TABLE pc3_quality ADD COLUMN IF NOT EXISTS hardness_tread_min INTEGER",
            "ALTER TABLE pc3_quality ADD COLUMN IF NOT EXISTS hardness_tread_max INTEGER",
            "ALTER TABLE pc3_quality ADD COLUMN IF NOT EXISTS customer_name VARCHAR(100)",
            "ALTER TABLE pc3_quality ADD COLUMN IF NOT EXISTS despatched_at TIMESTAMP"
        ]
        for s in sqls:
            try: DBManager.execute_query(s)
            except: pass

    def setup_ui(self):
        # HEADER
        header = tk.Frame(self.root, bg=C_HEADER, height=70)
        header.pack(fill="x")
        tk.Label(header, text="🛡️ PC3 - DIGITAL PASSPORT & QC", font=("Segoe UI", 20, "bold"), bg=C_HEADER, fg="white").pack(pady=15)

        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True, padx=15, pady=15)
        self.tab_qc = tk.Frame(nb, bg=C_BG); nb.add(self.tab_qc, text="  🔍 INSPECTION  ")
        self.tab_hist = tk.Frame(nb, bg=C_BG); nb.add(self.tab_hist, text="  📜 TYRE DETAILS (HISTORY)  ")
        
        self.build_qc_tab()
        self.build_history_tab()

    def build_qc_tab(self):
        # --- SCANNER BAR ---
        f_scan = tk.Frame(self.tab_qc, bg=C_SCAN_BG, pady=15, bd=1, relief="solid")
        f_scan.pack(fill="x", padx=15, pady=15)
        tk.Label(f_scan, text="SCAN SERIAL NO:", bg=C_SCAN_BG, font=("Segoe UI", 12, "bold"), fg="#2C3E50").pack(side="left", padx=20)
        e_scan = tk.Entry(f_scan, textvariable=self.var_scan, font=("Segoe UI", 16, "bold"), width=25, justify="center")
        e_scan.pack(side="left", padx=10); e_scan.bind("<Return>", self.lookup_tyre); e_scan.focus_set()
        tk.Label(f_scan, textvariable=self.info_status_msg, font=("Segoe UI", 14, "bold"), fg=C_HEADER, bg=C_SCAN_BG).pack(side="left", padx=30)

        # --- MAIN CONTENT ---
        content = tk.Frame(self.tab_qc, bg=C_BG); content.pack(fill="both", expand=True, padx=15)
        
        # LEFT: TYRE DETAILS (Colorful Cards)
        left_col = tk.Frame(content, bg=C_BG); left_col.pack(side="left", fill="both", expand=True, padx=(0,10))
        
        # Identity Card (Blue)
        c1 = tk.LabelFrame(left_col, text=" IDENTITY & SPECS ", font=("Segoe UI", 10, "bold"), fg=C_ID_FG, bg="white", padx=10, pady=10)
        c1.pack(fill="x", pady=5)
        self.create_kv(c1, "Tyre Size:", self.ui_size)
        self.create_kv(c1, "Brand:", self.ui_brand)
        self.create_kv(c1, "Mould ID:", self.ui_mould)
        self.create_kv(c1, "Quality:", self.ui_quality)
        self.create_kv(c1, "Core Size:", self.ui_core)

        # Status Card (Orange)
        c2 = tk.LabelFrame(left_col, text=" PROCESS STATUS ", font=("Segoe UI", 10, "bold"), fg=C_STAT_FG, bg="white", padx=10, pady=10)
        c2.pack(fill="x", pady=10)
        self.create_kv(c2, "Green Age:", self.ui_age)
        self.create_kv(c2, "Final Weight:", self.ui_fin_wt, color=C_WT_FG)
        self.create_kv(c2, "Flash Weight:", self.ui_flash_wt, color=C_ERR)

        # RIGHT: INSPECTION INPUTS
        right_col = tk.Frame(content, bg=C_BG); right_col.pack(side="right", fill="both", expand=True, padx=(10,0))
        
        # Hardness Card
        c3 = tk.LabelFrame(right_col, text=" HARDNESS TEST (Shore A) ", font=("Segoe UI", 10, "bold"), bg="white", padx=10, pady=10)
        c3.pack(fill="x", pady=5)
        f_h = tk.Frame(c3, bg="white"); f_h.pack(fill="x", pady=5)
        
        # Core Hardness
        tk.Label(f_h, text="CORE:", bg="white", font=("Segoe UI", 9, "bold")).pack(side="left")
        tk.Entry(f_h, textvariable=self.h_core_min, width=5, bg="#EBDEF0", font=("Segoe UI", 11)).pack(side="left", padx=5)
        tk.Label(f_h, text="-", bg="white").pack(side="left")
        tk.Entry(f_h, textvariable=self.h_core_max, width=5, bg="#EBDEF0", font=("Segoe UI", 11)).pack(side="left", padx=5)
        
        # Tread Hardness
        tk.Label(f_h, text="TREAD:", bg="white", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(20,0))
        tk.Entry(f_h, textvariable=self.h_tread_min, width=5, bg="#D4E6F1", font=("Segoe UI", 11)).pack(side="left", padx=5)
        tk.Label(f_h, text="-", bg="white").pack(side="left")
        tk.Entry(f_h, textvariable=self.h_tread_max, width=5, bg="#D4E6F1", font=("Segoe UI", 11)).pack(side="left", padx=5)

        # Defects Card
        c4 = tk.LabelFrame(right_col, text=" VISUAL DEFECTS ", font=("Segoe UI", 10, "bold"), bg="white", padx=10, pady=10)
        c4.pack(fill="x", pady=10)
        
        f_rad = tk.Frame(c4, bg="white"); f_rad.pack(fill="x")
        tk.Radiobutton(f_rad, text="Direct (DD)", variable=self.var_defect_type, value="DIRECT", command=self.update_defect_list, bg="white").pack(side="left")
        tk.Radiobutton(f_rad, text="Indirect (DI)", variable=self.var_defect_type, value="INDIRECT", command=self.update_defect_list, bg="white").pack(side="left", padx=20)
        
        self.combo_defect = ttk.Combobox(c4, textvariable=self.var_selected_defect, font=("Segoe UI", 11), state="readonly"); self.combo_defect.pack(fill="x", pady=5)
        tk.Button(c4, text="⬇ ADD DEFECT TO LIST", command=self.add_defect, bg="#95A5A6", fg="white", font=("Segoe UI", 9, "bold")).pack(fill="x", pady=2)
        
        self.list_defects = tk.Listbox(c4, height=4, bg="#F4F6F7", bd=0, font=("Segoe UI", 10)); self.list_defects.pack(fill="x", pady=5)
        tk.Button(c4, text="Clear List", command=self.clear_defects, font=("Segoe UI", 8)).pack(anchor="e")
        
        tk.Label(c4, text="QC Remarks:", bg="white", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(5,0))
        tk.Entry(c4, textvariable=self.var_remarks, bg="#FDEDEC", font=("Segoe UI", 11)).pack(fill="x")

        # Buttons
        bot = tk.Frame(self.tab_qc, bg=C_BG, pady=20); bot.pack(fill="x")
        tk.Button(bot, text="✅ A-GRADE", bg=C_WT_FG, fg="white", font=("Segoe UI", 12, "bold"), width=15, height=2, command=lambda: self.submit_qc("A-GRADE")).pack(side="left", padx=10, expand=True)
        tk.Button(bot, text="🛠️ B-GRADE", bg=C_STAT_FG, fg="white", font=("Segoe UI", 12, "bold"), width=15, height=2, command=lambda: self.submit_qc("B-GRADE")).pack(side="left", padx=10, expand=True)
        tk.Button(bot, text="❌ SCRAP", bg=C_ERR, fg="white", font=("Segoe UI", 12, "bold"), width=15, height=2, command=lambda: self.submit_qc("SCRAP")).pack(side="left", padx=10, expand=True)

    def build_history_tab(self):
        f = tk.Frame(self.tab_hist, bg=C_BG, pady=20, padx=20); f.pack(fill="both", expand=True)
        
        # HTML Export Button
        btn_html = tk.Button(f, text="📄 GENERATE HISTORY CARD (HTML)", command=self.generate_html_card, bg="#8E44AD", fg="white", font=("Segoe UI", 11, "bold"), pady=5)
        btn_html.pack(anchor="ne", pady=(0,10))
        
        # History Text Area
        self.txt_history = tk.Text(f, font=("Consolas", 11), bg="white", padx=15, pady=15, relief="flat", bd=2); self.txt_history.pack(fill="both", expand=True)

    # --- LOGIC ---
    def lookup_tyre(self, event):
        serial = self.var_scan.get().strip().upper()
        if not serial: return
        
        # Check QC Status
        res_qc = DBManager.fetch_data("SELECT grade FROM pc3_quality WHERE tyre_id=%s", (serial,))
        qc_status_msg = f"⚠️ ALREADY QC: {res_qc[0][0]}" if res_qc else "✅ READY FOR QC"
        self.info_status_msg.set(qc_status_msg)

        # MAIN QUERY: Fetches Core Size from Plan if Building is empty!
        # ADDED: is_pob, defect_codes
        q = """
            SELECT 
                b.b_id, b.tyre_size, 
                COALESCE(b.core_size, (SELECT core_size FROM production_plan p WHERE p.tyre_size = b.tyre_size LIMIT 1)), 
                b.brand, b.quality, b.created_at, b.building_remarks, b.green_tyre_weight,
                b.batch_core, b.batch_tread, b.batch_mid, b.batch_gum, b.operator_id, b.is_pob,
                c.serial_no, c.mould_no, c.start_time, c.end_time, c.visual_qc_remarks, c.final_cured_weight, c.flash_waste, 
                c.temperature, c.pressure, c.operator_name,
                q.grade, q.inspected_at, q.inspector_name, q.qc_remarks, 
                q.hardness_core_min, q.hardness_core_max, q.hardness_tread_min, q.hardness_tread_max, q.defect_codes,
                q.customer_name, q.despatched_at
            FROM pc2_curing c
            JOIN pc1_building b ON c.b_id = b.b_id
            LEFT JOIN pc3_quality q ON c.serial_no = q.tyre_id
            WHERE c.serial_no=%s OR c.b_id=%s
        """
        res = DBManager.fetch_data(q, (serial, serial))
        
        if res:
            r = res[0]
            self.current_tyre_data = r 
            
            # 1. Fill Basic UI
            self.ui_size.set(r[1])
            self.ui_core.set(r[2] if r[2] else "—") 
            self.ui_brand.set(r[3])
            self.ui_quality.set(r[4])
            self.ui_mould.set(r[15]) # Curing Mould
            
            # Age
            age_str = "0h"
            if r[5] and r[16]: 
                diff = r[16] - r[5]
                age_str = f"{int(diff.total_seconds()//3600)}h {int((diff.total_seconds()%3600)//60)}m"
            self.ui_age.set(age_str)
            
            self.ui_fin_wt.set(f"{r[19]} kg" if r[19] else "—")
            self.ui_flash_wt.set(f"{r[20]} kg" if r[20] else "—")
            
            # 2. Update History
            self.update_history_text(r)
        else:
            self.info_status_msg.set("❌ NOT FOUND")
            self.reset_ui()

    def update_history_text(self, r):
        self.txt_history.delete(1.0, tk.END)
        is_pob = r[13] # Boolean Flag
        
        # Build -> Cure -> QC
        hist = f"""
======================================================
       🏭 TYRE HISTORY LOG: {r[14]}
======================================================

--- 1. BUILDING HISTORY (PC1) ---
• Green ID    : {r[0]}
• Tyre Size   : {r[1]}
• Core Size   : {r[2]}
• Brand       : {r[3]}
• Quality     : {r[4]}
• Green Wt    : {r[7]} kg
• Created At  : {r[5]}
• Builder     : {r[12]}
• MATERIAL BATCHES:
   - Tread : {r[9] if r[9] else 'N/A'}
   - Core  : {r[8] if r[8] else 'N/A'}
   - Mid   : {r[10] if r[10] else '-'}
"""
        # CONDITIONAL GUM DISPLAY
        if is_pob:
            hist += f"   - GUM   : {r[11] if r[11] else 'N/A'}\n"
            
        hist += f"• REMARKS     : {r[6] if r[6] else 'None'}\n"

        hist += f"""
--- 2. CURING HISTORY (PC2) ---
• Serial No   : {r[14]}
• Mould ID    : {r[15]}
• Cycle Start : {r[16]}
• Cycle End   : {r[17]}
• Params      : {r[21]}°C | {r[22]} Bar
• Operator    : {r[23]}
• Final Wt    : {r[19]} kg (Flash: {r[20]} kg)
• REMARKS     : {r[18] if r[18] else 'None'}

--- 3. QC HISTORY (PC3) ---
"""
        if r[24]: # If Graded
            hist += f"• Grade       : {r[24]}\n"
            hist += f"• Inspected   : {r[25]}\n"
            hist += f"• Inspector   : {r[26]}\n"
            hist += f"• Hardness    : Core {r[28]}-{r[29]} | Tread {r[30]}-{r[31]}\n"
            if r[32]: # Defect Codes
                hist += f"• DEFECTS     : {r[32]}\n"
            hist += f"• REMARKS     : {r[27]}\n"
        else:
            hist += "• Status      : PENDING INSPECTION\n"

        hist += "\n--- 4. LOGISTICS & DESPATCH ---\n"
        if len(r) > 33 and r[33]: # Check if customer_name exists
            hist += f"• Status      : DISPATCHED\n"
            hist += f"• Customer    : {r[33]}\n"
            hist += f"• Shipped On  : {r[34]}\n"
        else:
            hist += "• Status      : IN WAREHOUSE\n"    
            
        hist += "======================================================"
        self.txt_history.insert(tk.END, hist)

    def generate_html_card(self):
        if not self.current_tyre_data: return messagebox.showerror("Error", "Scan a tyre first!")
        r = self.current_tyre_data
        is_pob = r[13]
        
        # Prepare Strings
        hardness_txt = "Not Tested"
        if r[28] or r[30]: hardness_txt = f"Core: {r[28]}-{r[29]} | Tread: {r[30]}-{r[31]}"
        
        # Gum Row Logic
        gum_html = ""
        if is_pob:
            gum_html = f'<div class="row"><span class="label">Gum Batch:</span><span class="val">{r[11] if r[11] else "-"}</span></div>'

        # Defect Row Logic
        defect_html = ""
        if r[32]:
            defect_html = f'<div class="row" style="background:#FDEDEC"><span class="label" style="color:#C0392B">DEFECTS:</span><span class="val" style="color:#C0392B">{r[32]}</span></div>'

        # Logistics Row Logic
        logistics_html = ""
        if len(r) > 33 and r[33]:
            logistics_html = f'''
            <h2>4. Logistics & Despatch</h2>
            <div class="row"><span class="label">Status:</span><span class="val" style="color:#27AE60;">DISPATCHED</span></div>
            <div class="row"><span class="label">Customer:</span><span class="val">{r[33]}</span></div>
            <div class="row"><span class="label">Shipped On:</span><span class="val">{r[34]}</span></div>
            '''
        else:
            logistics_html = f'''
            <h2>4. Logistics & Despatch</h2>
            <div class="row"><span class="label">Status:</span><span class="val" style="color:#E67E22;">IN WAREHOUSE</span></div>
            '''

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; background-color: #f4f6f7; padding: 20px; }}
                .card {{ background: white; max-width: 800px; margin: auto; padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
                h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
                h2 {{ color: #2980b9; margin-top: 25px; border-left: 5px solid #2980b9; padding-left: 10px; font-size: 18px; }}
                .row {{ display: flex; justify-content: space-between; margin-bottom: 8px; border-bottom: 1px solid #ecf0f1; padding-bottom: 4px; }}
                .label {{ font-weight: bold; color: #7f8c8d; min-width: 150px; }}
                .val {{ font-weight: bold; color: #2c3e50; text-align: right; }}
                .tag {{ background: #27ae60; color: white; padding: 5px 10px; border-radius: 4px; font-size: 14px; }}
                .batch-box {{ background: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 5px; border: 1px solid #bdc3c7; }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #95a5a6; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h1>Tyre Digital Passport</h1>
                    <span class="tag">{r[24] if r[24] else 'IN PROGRESS'}</span>
                </div>
                
                <h2>1. Building Genetics</h2>
                <div class="row"><span class="label">Green ID:</span><span class="val">{r[0]}</span></div>
                <div class="row"><span class="label">Tyre Size:</span><span class="val">{r[1]}</span></div>
                <div class="row"><span class="label">Core Size:</span><span class="val">{r[2]}</span></div>
                <div class="row"><span class="label">Brand:</span><span class="val">{r[3]}</span></div>
                <div class="row"><span class="label">Quality:</span><span class="val">{r[4]}</span></div>
                <div class="row"><span class="label">Green Weight:</span><span class="val">{r[7]} kg</span></div>
                <div class="row"><span class="label">Built Time:</span><span class="val">{r[5]}</span></div>
                <div class="row"><span class="label">Builder:</span><span class="val">{r[12]}</span></div>
                <div class="row"><span class="label">Building Remarks:</span><span class="val">{r[6] if r[6] else 'None'}</span></div>
                
                <div class="batch-box">
                    <div class="row"><span class="label">Tread Batch:</span><span class="val">{r[9] if r[9] else 'N/A'}</span></div>
                    <div class="row"><span class="label">Core Batch:</span><span class="val">{r[8] if r[8] else 'N/A'}</span></div>
                    <div class="row"><span class="label">Middle Batch:</span><span class="val">{r[10] if r[10] else '-'}</span></div>
                    {gum_html}
                </div>

                <h2>2. Curing Process</h2>
                <div class="row"><span class="label">Serial No:</span><span class="val">{r[14]}</span></div>
                <div class="row"><span class="label">Mould ID:</span><span class="val">{r[15]}</span></div>
                <div class="row"><span class="label">Cycle Start:</span><span class="val">{r[16]}</span></div>
                <div class="row"><span class="label">Cycle End:</span><span class="val">{r[17]}</span></div>
                <div class="row"><span class="label">Params:</span><span class="val">{r[21]}°C / {r[22]} Bar</span></div>
                <div class="row"><span class="label">Curing Remarks:</span><span class="val">{r[18] if r[18] else 'None'}</span></div>

                <h2>3. Final Quality</h2>
                <div class="row"><span class="label">Inspection Date:</span><span class="val">{r[25] if r[25] else '-'}</span></div>
                <div class="row"><span class="label">Inspector:</span><span class="val">{r[26] if r[26] else '-'}</span></div>
                <div class="row"><span class="label">Hardness:</span><span class="val">{hardness_txt}</span></div>
                {defect_html}
                <div class="row"><span class="label">QC Remarks:</span><span class="val">{r[27] if r[27] else 'None'}</span></div>
                
                {logistics_html}
                
                <div class="footer">Generated by Factory OS | {datetime.datetime.now()}</div>
            </div>
        </body>
        </html>
        """
        
        path = filedialog.asksaveasfilename(defaultextension=".html", initialfile=f"Passport_{r[14]}.html")
        if path:
            with open(path, "w") as f: f.write(html)
            messagebox.showinfo("Success", "Passport Saved!")

    def submit_qc(self, grade):
        serial = self.var_scan.get().strip()
        if not serial: return messagebox.showerror("Error", "Scan Tyre First")
        
        defects = "|".join(self.defect_list_store)
        remarks = self.var_remarks.get().strip()
        q_ins = """INSERT INTO pc3_quality (tyre_id, grade, defect_codes, inspector_name, qc_remarks, inspected_at, is_finalized, hardness_core_min, hardness_core_max, hardness_tread_min, hardness_tread_max) VALUES (%s, %s, %s, %s, %s, NOW(), TRUE, %s, %s, %s, %s)"""
        
        # Safe Int conversion
        def g_int(v): return int(v.get()) if v.get().isdigit() else 0
        
        if DBManager.execute_query(q_ins, (serial, grade, defects, self.current_user, remarks, g_int(self.h_core_min), g_int(self.h_core_max), g_int(self.h_tread_min), g_int(self.h_tread_max))):
            DBManager.execute_query("UPDATE pc2_curing SET status='QC_COMPLETED' WHERE serial_no=%s", (serial,))
            self.print_qc_label(serial, grade)
            messagebox.showinfo("Saved", f"Tyre {grade}"); self.reset_ui()

    # --- Helpers ---
    def update_defect_list(self):
        try:
            res = DBManager.fetch_data("SELECT defect_code, defect_name FROM qc_defects_master WHERE defect_type=%s ORDER BY defect_code", (self.var_defect_type.get(),))
            self.combo_defect['values'] = [f"{r[0]} - {r[1]}" for r in res] if res else []
            if res: self.combo_defect.current(0)
        except: pass

    def add_defect(self):
        if self.var_selected_defect.get(): self.list_defects.insert(tk.END, self.var_selected_defect.get()); self.defect_list_store.append(self.var_selected_defect.get())

    def clear_defects(self): self.list_defects.delete(0, tk.END); self.defect_list_store = []

    def reset_ui(self):
        self.var_scan.set(""); self.info_status_msg.set("Ready")
        self.ui_size.set("—"); self.ui_mould.set("—"); self.ui_core.set("—"); self.ui_brand.set("—")
        self.ui_quality.set("—"); self.ui_age.set("—"); self.ui_fin_wt.set("—"); self.ui_flash_wt.set("—")
        self.h_core_min.set(""); self.h_core_max.set(""); self.h_tread_min.set(""); self.h_tread_max.set("")
        self.clear_defects(); self.var_remarks.set("")

    def print_qc_label(self, serial, grade):
        try:
            if platform.system() == "Linux":
                with open(LINUX_PRINTER_PATH, "wb") as f: f.write(f'N\nq464\nQ200,24\nA20,10,0,4,1,1,N,"QC {grade}"\nB20,60,0,1,2,5,80,B,"{serial}"\nP1\n'.encode())
        except: pass

    def create_card(self, parent, title): 
        f = tk.Frame(parent, bg=C_CARD, bd=1, relief="solid", padx=10, pady=10); 
        tk.Label(f, text=title, font=("Segoe UI", 10, "bold"), bg=C_CARD, fg=C_PRIMARY).pack(anchor="w", pady=5); return f
    def create_kv(self, parent, label, var, color="#2C3E50"): 
        f = tk.Frame(parent, bg="white"); f.pack(fill="x")
        tk.Label(f, text=label, width=15, anchor="w", bg="white", fg="#7F8C8D").pack(side="left")
        tk.Label(f, textvariable=var, anchor="w", bg="white", font=("Segoe UI", 10, "bold"), fg=color).pack(side="left")

if __name__ == "__main__":
    root = tk.Tk(); app = FinalQCApp(root); root.mainloop()