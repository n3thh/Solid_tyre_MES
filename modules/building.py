import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Toplevel
import datetime
import csv
import os
import platform
import math
from db_manager import DBManager

# ================= CONFIGURATION =================
LINUX_PRINTER_PATH = "/dev/usb/lp4" 
C_BG = "#F4F6F7"       
C_CARD = "#FFFFFF"     
C_PRIMARY = "#2C3E50"  
C_ACCENT = "#3498DB"   
C_SUCCESS = "#27AE60"  
C_POB = "#8E44AD"      
C_PARTIAL = "#E67E22"  
C_ERROR = "#C0392B"
C_WARN = "#F39C12"

class PC1SmartApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"PC1 | Smart Builder (Full Logic)")
        self.root.geometry("1300x900")
        self.root.configure(bg=C_BG)
        self.current_is_pob = False 
        self.target_weight = 0.0 # Stores Plan Weight for Validation

        # --- VARIABLES ---
        self.var_press = tk.StringVar()
        self.var_daylight = tk.StringVar()
        self.var_operator = tk.StringVar()
        self.var_shift = tk.StringVar(value=self.get_current_shift())
        self.var_remarks = tk.StringVar()
        
        # Plan Vars
        self.var_size = tk.StringVar(value="—")
        self.var_brand = tk.StringVar(value="—")
        self.var_pattern = tk.StringVar(value="—")
        self.var_quality = tk.StringVar(value="—") 
        self.var_mould = tk.StringVar(value="—")
        self.var_type = tk.StringVar(value="—") 
        self.var_plan_weight = tk.StringVar(value="—")
        self.var_core_size = tk.StringVar(value="—")
        
        # Production Balance Var (NEW)
        self.disp_balance = tk.StringVar(value="—")

        # Spec Display Vars
        self.disp_core_tgt = tk.StringVar(value="—")
        self.disp_mid_tgt = tk.StringVar(value="—")
        self.disp_ct_tgt = tk.StringVar(value="—")      
        self.disp_gum_tgt = tk.StringVar(value="—")     
        self.disp_tread_tgt = tk.StringVar(value="—")
        self.disp_bead = tk.StringVar(value="—")
        
        # Material Selection
        self.sel_core = tk.StringVar()
        self.sel_mid = tk.StringVar()
        self.sel_gum = tk.StringVar()
        self.var_ms_rim_wt = tk.StringVar()
        self.sel_tread_type = tk.StringVar()
        self.sel_tread = tk.StringVar()
        self.var_weight = tk.StringVar()
        
        # Update Tab Vars
        self.upd_bid = tk.StringVar()
        self.upd_tread_type = tk.StringVar()
        self.upd_tread = tk.StringVar()
        self.upd_weight = tk.StringVar()

        # Report Vars
        self.rep_date = tk.StringVar(value=datetime.datetime.now().strftime("%Y-%m-%d"))
        self.rep_shift = tk.StringVar(value="ALL")

        self.setup_ui()
        self.root.after(500, self.connect_and_load)

        self.var_weight.trace_add("write", self.check_completion_status)

    def get_current_shift(self):
        h = datetime.datetime.now().hour
        if 7 <= h < 15: return "A"
        elif 15 <= h < 23: return "B"
        else: return "C"

    def connect_and_load(self):
        try:
            DBManager.get_connection()
            self.load_operators()
            self.load_press_list()
            self.load_materials()
            self.refresh_today_list()
        except Exception as e:
            messagebox.showerror("Error", f"DB Connection Failed:\n{e}",parent=self.root)

    def on_upd_tread_type_change(self, event):
        t_type = self.upd_tread_type.get()
        q = "SELECT batch_no FROM raw_material_qc WHERE material_type=%s AND status='APPROVED'"
        res = DBManager.fetch_data(q, (t_type,))
        if hasattr(self, "combo_list_upd_tread"):
            if res: self.combo_list_upd_tread['values'] = [r[0] for r in res]
            else: self.combo_list_upd_tread['values'] = []

    # ================= UI SETUP =================
    def setup_ui(self):
        header = tk.Frame(self.root, bg=C_PRIMARY, height=70)
        header.pack(fill="x")
        tk.Label(header, text="🏭 PC1 BUILDING STATION", font=("Segoe UI", 20, "bold"), bg=C_PRIMARY, fg="white").pack(side="left", padx=20)
        
        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab1 = tk.Frame(nb, bg=C_BG)
        self.tab2 = tk.Frame(nb, bg=C_BG)
        self.tab3 = tk.Frame(nb, bg=C_BG)
        
        nb.add(self.tab1, text="  ➕ BUILD NEW TYRE  ")
        nb.add(self.tab2, text="  🔄 APPLY TREAD (UPDATE)  ")
        nb.add(self.tab3, text="  🖨️ REPRINT & REPORTS  ")
        
        self.build_tab1()
        self.build_tab2()
        self.build_tab3()

    def build_tab1(self):
        left = tk.Frame(self.tab1, bg=C_BG); left.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        card_setup = self.create_card(left, "1. SETUP & DETAILS")
        self.add_label(card_setup, "Operator:")
        self.combo_op = ttk.Combobox(card_setup, textvariable=self.var_operator, font=("Segoe UI", 11)); self.combo_op.pack(fill="x", pady=2)
        f_pd = tk.Frame(card_setup, bg=C_CARD); f_pd.pack(fill="x", pady=2)
        self.combo_press = ttk.Combobox(f_pd, textvariable=self.var_press, width=10, font=("Segoe UI", 11)); self.combo_press.pack(side="left", padx=(0,5)); self.combo_press.bind("<<ComboboxSelected>>", self.on_press_change)
        self.combo_daylight = ttk.Combobox(f_pd, textvariable=self.var_daylight, width=10, font=("Segoe UI", 11)); self.combo_daylight.pack(side="left"); self.combo_daylight.bind("<<ComboboxSelected>>", self.fetch_plan_details)
        self.lbl_plan_status = tk.Label(card_setup, text="Select Plan...", fg="gray", bg=C_CARD); self.lbl_plan_status.pack(pady=5)
        self.create_kv(card_setup, "Size:", self.var_size, True); self.create_kv(card_setup, "Grade:", self.var_quality, True); self.create_kv(card_setup, "Brand:", self.var_brand); self.create_kv(card_setup, "Type:", self.var_type); self.create_kv(card_setup, "Plan Wt:", self.var_plan_weight, True)
        
        # --- TARGETS CARD (Updated with Balance) ---
        card_spec = self.create_card(left, "2. TARGETS")
        
        # BALANCE DISPLAY ROW
        f_bal = tk.Frame(card_spec, bg="#D6EAF8", pady=5, bd=1, relief="solid")
        f_bal.pack(fill="x", pady=(0, 10))
        tk.Label(f_bal, text="REQ. BALANCE:", font=("Segoe UI", 10, "bold"), bg="#D6EAF8").pack(side="left", padx=10)
        tk.Label(f_bal, textvariable=self.disp_balance, font=("Segoe UI", 12, "bold"), bg="#D6EAF8", fg=C_PRIMARY).pack(side="right", padx=10)

        self.create_kv(card_spec, "Core Tgt:", self.disp_core_tgt)
        self.create_kv(card_spec, "Middle Tgt:", self.disp_mid_tgt)
        self.create_kv(card_spec, "C+T Tgt:", self.disp_ct_tgt)  
        self.create_kv(card_spec, "Gum Tgt:", self.disp_gum_tgt) 
        self.create_kv(card_spec, "Tread Tgt:", self.disp_tread_tgt)
        self.create_kv(card_spec, "Bead Req:", self.disp_bead, True)
        
        right = tk.Frame(self.tab1, bg=C_BG); right.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        card_mat = self.create_card(right, "3. MATERIALS")
        self.row_core_input = self.create_multi_select(card_mat, "Core Batch(es):", self.sel_core, "list_core"); self.row_mid_input = self.create_multi_select(card_mat, "Middle Layer(s):", self.sel_mid, "list_mid")
        self.add_label(card_mat, "Tread Type:")
        self.combo_tt = ttk.Combobox(card_mat, textvariable=self.sel_tread_type, values=["VT001", "VT002", "VT003", "NMW"]); self.combo_tt.pack(fill="x"); self.combo_tt.bind("<<ComboboxSelected>>", self.on_tread_type_change); self.create_multi_select(card_mat, "Tread Batch(es):", self.sel_tread, "list_tread")
        
        self.frame_gum = tk.Frame(card_mat, bg=C_CARD, pady=5); self.frame_gum.pack(fill="x", pady=5); tk.Label(self.frame_gum, text="Bonding Gum (POB):", fg=C_POB, bg=C_CARD).pack(anchor="w"); self.combo_gum_widget = ttk.Combobox(self.frame_gum, textvariable=self.sel_gum); self.combo_gum_widget.pack(fill="x"); self.frame_gum.pack_forget() 
        
        # MS Rim Input Frame (Hidden by default)
        self.frame_ms_rim = tk.Frame(card_mat, bg=C_CARD, pady=5)
        self.frame_ms_rim.pack(fill="x", pady=5)
        tk.Label(self.frame_ms_rim, text="MS Rim Weight (Kg):", fg=C_POB, bg=C_CARD).pack(anchor="w")
        tk.Entry(self.frame_ms_rim, textvariable=self.var_ms_rim_wt, font=("Segoe UI", 12), bg="#F5EEF8").pack(fill="x")
        self.frame_ms_rim.pack_forget()
        
        self.add_label(card_mat, "Green Weight (Kg):"); tk.Entry(card_mat, textvariable=self.var_weight, font=("Segoe UI", 12), bg="#EBF5FB").pack(fill="x")
        self.add_label(card_mat, "Building Remarks / Notes:")
        tk.Entry(card_mat, textvariable=self.var_remarks, font=("Segoe UI", 11), bg="#FCF3CF").pack(fill="x", pady=(0, 10))
        
        f_btn = tk.Frame(right, bg=C_BG); f_btn.pack(fill="x", pady=20)
        
        # Save Partial remains active
        tk.Button(f_btn, text="⚠️ SAVE PARTIAL", command=lambda: self.submit_build("PARTIAL"), 
                  bg=C_PARTIAL, fg="white", width=15).pack(side="left", padx=5)
        
        # SAVE COMPLETE starts disabled and greyed out
        self.btn_save_complete = tk.Button(f_btn, text="✅ SAVE COMPLETE", command=lambda: self.submit_build("COMPLETED"), 
                                           bg="#BDC3C7", fg="white", width=20, state="disabled")
        self.btn_save_complete.pack(side="right", padx=5)

    def build_tab2(self):
        card = self.create_card(self.tab2, "APPLY TREAD TO PARTIAL TYRE"); card.pack(fill="both", expand=True, padx=100, pady=50)
        self.add_label(card, "Scan Partial Tyre (B-ID):"); e_scan = tk.Entry(card, textvariable=self.upd_bid, font=("Segoe UI", 16), bg="#FFF8DC", bd=2); e_scan.pack(fill="x", pady=5); e_scan.bind("<Return>", self.lookup_partial); self.lbl_partial_info = tk.Label(card, text="Waiting...", font=("Segoe UI", 12), bg=C_CARD, fg="gray"); self.lbl_partial_info.pack(pady=10); self.add_label(card, "Select Tread Type:"); self.combo_upd_tt = ttk.Combobox(card, textvariable=self.upd_tread_type, values=["VT001", "VT002", "VT003", "NMW"]); self.combo_upd_tt.pack(fill="x"); self.combo_upd_tt.bind("<<ComboboxSelected>>", self.on_upd_tread_type_change); self.create_multi_select(card, "Tread Batch(es):", self.upd_tread, "list_upd_tread"); self.add_label(card, "Final Green Weight (Kg):"); tk.Entry(card, textvariable=self.upd_weight, font=("Segoe UI", 14), bg="#EBF5FB").pack(fill="x"); tk.Button(card, text="💾 UPDATE & COMPLETE", command=self.submit_update, bg=C_SUCCESS, fg="white", pady=10).pack(fill="x", pady=20)

    def build_tab3(self):
        left = tk.Frame(self.tab3, bg=C_BG); left.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        card_reprint = self.create_card(left, "3.1 TODAY'S PRODUCTION (Reprint)"); cols = ("B-ID", "Time", "Size", "Status"); self.tree = ttk.Treeview(card_reprint, columns=cols, show="headings", height=15)
        for c in cols: self.tree.heading(c, text=c)
        self.tree.column("B-ID", width=120); self.tree.pack(fill="both", expand=True, pady=10); btn_f = tk.Frame(card_reprint, bg=C_CARD); btn_f.pack(fill="x", pady=10); tk.Button(btn_f, text="🔄 Refresh", command=self.refresh_today_list).pack(side="left", padx=5); tk.Button(btn_f, text="🖨️ Reprint SELECTED", command=self.reprint_selected, bg=C_WARN, fg="white").pack(side="left", padx=5); tk.Button(btn_f, text="⏪ Reprint LAST", command=self.reprint_last, bg=C_PRIMARY, fg="white").pack(side="right", padx=5)
        right = tk.Frame(self.tab3, bg=C_BG); right.pack(side="right", fill="both", expand=True, padx=20, pady=20); card_report = self.create_card(right, "3.2 SHIFT REPORTS"); self.add_label(card_report, "Select Date (YYYY-MM-DD):"); tk.Entry(card_report, textvariable=self.rep_date, font=("Segoe UI", 12)).pack(fill="x", pady=5); ttk.Combobox(card_report, textvariable=self.rep_shift, values=["A", "B", "C", "ALL"], font=("Segoe UI", 12)).pack(fill="x", pady=5)
        
        # --- DASHBOARD BUTTONS ---
        tk.Button(card_report, text="📊 VIEW VISUAL DASHBOARD", command=self.open_material_dashboard, bg="#8E44AD", fg="white", font=("Segoe UI", 11, "bold"), pady=10).pack(fill="x", pady=5)
        tk.Button(card_report, text="📄 EXPORT LOG (CSV)", command=self.generate_report, bg=C_SUCCESS, fg="white", font=("Segoe UI", 10), pady=5).pack(fill="x", pady=5)
        tk.Button(card_report, text="📄 EXPORT MATERIAL (CSV)", command=self.generate_material_report, bg=C_ACCENT, fg="white", font=("Segoe UI", 10), pady=5).pack(fill="x", pady=5)

    # ================= LOGIC: Dashboard =================
    def open_material_dashboard(self):
        dt = self.rep_date.get(); sh = self.rep_shift.get()
        q = "SELECT tyre_size, quality, green_tyre_weight, is_pob, tread_type, b_id FROM pc1_building WHERE date(created_at)=%s"
        params = [dt]
        if sh != "ALL": q += " AND shift=%s"; params.append(sh)
        builds = DBManager.fetch_data(q, tuple(params))
        
        if not builds: return messagebox.showinfo("Info", "No data found for this date/shift.",parent=self.root)

        missing_grades = set(); missing_beads = set(); zero_weights = 0
        tot_core=0.0; tot_mid=0.0; tot_ct=0.0; tot_gum=0.0; tot_tread=0.0; tot_wt=0.0
        bead_map = {}; tread_usage = {}; spec_cache = {}; bead_cache = {}
        sum_core_pct = 0; sum_mid_pct = 0; sum_gum_pct = 0

        for b in builds:
            size, grade, wt, is_pob, t_type, bid = b
            try: wt = float(wt) if wt is not None else 0.0
            except: wt = 0.0
            if wt <= 0: zero_weights += 1
            tot_wt += wt
            
            clean_size = str(size).upper().strip()
            b_cnt = 0; b_u_wt = 0.0; b_name = "N/A"

            if not is_pob:
                if clean_size not in bead_cache:
                    res = DBManager.fetch_data("SELECT bead_size, bead_count, weight_per_bead FROM bead_master WHERE UPPER(tyre_size)=%s LIMIT 1", (clean_size,))
                    if res:
                        try: bead_cache[clean_size] = (str(res[0][0]), int(res[0][1]), float(res[0][2]))
                        except: bead_cache[clean_size] = ("Error", 0, 0.0)
                    else:
                        bead_cache[clean_size] = ("MISSING", 0, 0.0); missing_beads.add(clean_size)
                b_name, b_cnt, b_u_wt = bead_cache[clean_size]
                if b_cnt > 0: bead_map[b_name] = bead_map.get(b_name, 0) + b_cnt
            
            rubber_net = max(0.0, wt - (b_cnt * b_u_wt))
            
            if grade not in spec_cache:
                res = DBManager.fetch_data("SELECT core_pct, mid_pct, ct_pct, gum_pct, tread_pct FROM tyre_specs WHERE grade=%s", (grade,))
                if res:
                    c_p = float(res[0][0]) if res[0][0] is not None else 0.0
                    m_p = float(res[0][1]) if res[0][1] is not None else 0.0
                    ct_p = float(res[0][2]) if res[0][2] is not None else 0.0
                    g_p = float(res[0][3]) if res[0][3] is not None else 0.0
                    t_p = float(res[0][4]) if res[0][4] is not None else 0.0
                    spec_cache[grade] = (c_p, m_p, ct_p, g_p, t_p)
                else:
                    spec_cache[grade] = (0.0, 0.0, 0.0, 0.0, 0.0); missing_grades.add(grade)
            
            c_pct, m_pct, ct_pct, g_pct, t_pct = spec_cache[grade]
            sum_core_pct += c_pct; sum_mid_pct += m_pct; sum_gum_pct += g_pct

            this_core = rubber_net * (c_pct / 100.0)
            this_mid = rubber_net * (m_pct / 100.0)
            this_ct = rubber_net * (ct_pct / 100.0)
            this_gum = rubber_net * (g_pct / 100.0)
            this_tread = rubber_net * (t_pct / 100.0)
            
            tot_core += this_core; tot_mid += this_mid; tot_ct += this_ct
            tot_gum += this_gum; tot_tread += this_tread
            
            clean_tt = str(t_type).strip().upper() if t_type else "UNSPECIFIED"
            if this_tread > 0: tread_usage[clean_tt] = tread_usage.get(clean_tt, 0.0) + this_tread

        error_msg = ""
        if zero_weights > 0: error_msg += f"⚠️ {zero_weights} Tyres have 0.0 KG Weight.\n"
        if missing_grades: error_msg += f"⚠️ Missing Specs for Grades: {', '.join(str(x) for x in missing_grades)}\n"
        if missing_beads: error_msg += f"⚠️ Missing Bead Master for Sizes: {', '.join(str(x) for x in missing_beads)}\n"
        if error_msg: messagebox.showwarning("Diagnostics", error_msg,parent=self.root)

        num_tyres = len(builds) if len(builds) > 0 else 1
        avg_core_pct = sum_core_pct / num_tyres
        avg_mid_pct = sum_mid_pct / num_tyres
        avg_gum_pct = sum_gum_pct / num_tyres

        top = Toplevel(self.root); top.title(f"Material Dashboard | {dt}"); top.geometry("1100x750"); top.configure(bg="#ECF0F1")
        tk.Label(top, text=f"📊 CONSUMPTION: {dt} ({sh})", font=("Segoe UI", 16, "bold"), bg="#ECF0F1", fg="#2C3E50").pack(pady=10)
        
        f_kpi = tk.Frame(top, bg="#ECF0F1"); f_kpi.pack(fill="x", pady=5)
        self.create_dash_card(f_kpi, "TOTAL TYRES", str(len(builds)), "#2980B9")
        self.create_dash_card(f_kpi, "TOTAL WEIGHT", f"{tot_wt:.1f} kg", "#27AE60")
        self.create_dash_card(f_kpi, "TREAD RUBBER", f"{tot_tread:.1f} kg", "#E67E22")
        
        content = tk.Frame(top, bg="#ECF0F1"); content.pack(fill="both", expand=True, padx=20, pady=10)
        f_left = tk.Frame(content, bg="#ECF0F1"); f_left.pack(side="left", fill="both", expand=True, padx=(0,10))
        
        fr = tk.LabelFrame(f_left, text="Rubber Breakdown", bg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        fr.pack(fill="x", pady=(0, 10))
        
        max_val = max(tot_core, tot_mid, tot_ct, tot_gum, tot_tread)
        if max_val <= 0 or math.isnan(max_val): max_val = 1.0

        self.create_bar(fr, f"Core ({avg_core_pct:.1f}%)", tot_core, max_val, "#E74C3C")
        self.create_bar(fr, f"Middle ({avg_mid_pct:.1f}%)", tot_mid, max_val, "#F39C12")
        self.create_bar(fr, "C+T (Cushion)", tot_ct, max_val, "#16A085")
        self.create_bar(fr, f"Bonding Gum ({avg_gum_pct:.1f}%)", tot_gum, max_val, "#8E44AD")
        self.create_bar(fr, "Tread", tot_tread, max_val, "#3498DB")
        
        ft = tk.LabelFrame(f_left, text="Tread Type Usage (kg)", bg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        ft.pack(fill="both", expand=True)
        cols_t = ("Type", "Weight"); tree_t = ttk.Treeview(ft, columns=cols_t, show="headings", height=8)
        tree_t.heading("Type", text="Tread Code"); tree_t.column("Type", width=120)
        tree_t.heading("Weight", text="Used (kg)"); tree_t.column("Weight", width=100)
        tree_t.pack(fill="both", expand=True)
        if tread_usage:
            for tt, tw in tread_usage.items(): tree_t.insert("", "end", values=(tt, f"{tw:.1f}"))
        else: tree_t.insert("", "end", values=("No Data", "0.0"))

        f_right = tk.LabelFrame(content, text="Bead Wire Usage (Units)", bg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        f_right.pack(side="right", fill="both", expand=True)
        cols = ("Type", "Qty"); tree = ttk.Treeview(f_right, columns=cols, show="headings", height=15)
        tree.heading("Type", text="Bead Size"); tree.column("Type", width=200)
        tree.heading("Qty", text="Count"); tree.column("Qty", width=80)
        tree.pack(fill="both", expand=True)
        if bead_map:
            for name, count in bead_map.items(): tree.insert("", "end", values=(name, count))
        else: tree.insert("", "end", values=("No Beads", "0"))

    # ================= VISUAL HELPERS =================
    def create_dash_card(self, parent, title, value, color):
        f = tk.Frame(parent, bg=color, padx=20, pady=15); f.pack(side="left", fill="x", expand=True, padx=10)
        tk.Label(f, text=title, font=("Segoe UI", 10), bg=color, fg="white").pack()
        tk.Label(f, text=value, font=("Segoe UI", 18, "bold"), bg=color, fg="white").pack()

    def create_bar(self, parent, label, val, max_val, color):
        f = tk.Frame(parent, bg="white"); f.pack(fill="x", pady=5)
        try:
            val = float(val)
            if math.isnan(val) or math.isinf(val): val = 0.0
        except: val = 0.0
        try:
            max_val = float(max_val)
            if math.isnan(max_val) or math.isinf(max_val) or max_val <= 0: max_val = 1.0
        except: max_val = 1.0
        tk.Label(f, text=f"{label}: {val:.3f} kg", bg="white", font=("Segoe UI", 10)).pack(anchor="w")
        s = ttk.Style()
        s.theme_use('clam')
        s.configure(f"{label}.Horizontal.TProgressbar", foreground=color, background=color)
        ttk.Progressbar(f, style=f"{label}.Horizontal.TProgressbar", value=val, maximum=max_val, length=300).pack(fill="x")
    
    # ================= RESET FORM (SAFE) =================
    def reset_form(self):
        try:
            if not self.root.winfo_exists(): return
            
            # Reset Vars
            self.var_press.set(""); self.var_daylight.set(""); 
            self.var_size.set("—"); self.var_brand.set("—"); self.var_pattern.set("—"); 
            self.var_quality.set("—"); self.var_mould.set("—"); self.var_type.set("—"); 
            self.var_plan_weight.set("—"); self.var_core_size.set("—")
            self.var_remarks.set("")
            
            # Reset Targets
            self.disp_core_tgt.set("—"); self.disp_mid_tgt.set("—"); 
            self.disp_ct_tgt.set("—"); self.disp_gum_tgt.set("—");
            self.disp_tread_tgt.set("—"); self.disp_bead.set("—")
            
            self.disp_balance.set("—") # Reset Balance
            
            self.sel_core.set(""); self.sel_mid.set(""); self.sel_gum.set(""); 
            self.sel_tread_type.set(""); self.sel_tread.set(""); self.var_weight.set("")
            
            # Safe Combo Clear
            if hasattr(self, 'combo_daylight'):
                if self.combo_daylight.winfo_exists(): self.combo_daylight['values'] = []

            # Safe Listbox Clear
            for lst in ['list_core', 'list_mid', 'list_tread']:
                if hasattr(self, lst):
                    w = getattr(self, lst)
                    if w.winfo_exists(): w.delete(0, tk.END)
            
            if hasattr(self, 'lbl_plan_status') and self.lbl_plan_status.winfo_exists():
                self.lbl_plan_status.config(text="Select Plan...", fg="gray")
                
            if hasattr(self, 'frame_gum') and self.frame_gum.winfo_exists():
                self.frame_gum.pack_forget()
                
            self.current_is_pob = False; self.target_weight = 0.0

            # Add these lines inside reset_form
            self.var_ms_rim_wt.set("")
            if hasattr(self, 'frame_ms_rim') and self.frame_ms_rim.winfo_exists():
                self.frame_ms_rim.pack_forget()
            
        except Exception as e: print(f"Reset Error: {e}")

    # ================= EXISTING LOGIC =================
    def refresh_today_list(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        res = DBManager.fetch_data("SELECT b_id, to_char(created_at, 'HH12:MI PM'), tyre_size, status FROM pc1_building WHERE date(created_at) = CURRENT_DATE ORDER BY created_at DESC")
        if res:
            for r in res: self.tree.insert("", "end", values=r)

    def reprint_selected(self):
        sel = self.tree.selection()
        if not sel: return
        bid = self.tree.item(sel[0])['values'][0]
        res = DBManager.fetch_data("SELECT tyre_size, press_id, daylight FROM pc1_building WHERE b_id=%s", (bid,))
        if res: self.print_label(bid, res[0][0], res[0][1], res[0][2])

    def reprint_last(self):
        res = DBManager.fetch_data("SELECT b_id, tyre_size, press_id, daylight FROM pc1_building ORDER BY created_at DESC LIMIT 1")
        if res: self.print_label(res[0][0], res[0][1], res[0][2], res[0][3])

    def on_press_change(self, e): self.combo_daylight['values'] = [r[0] for r in DBManager.fetch_data("SELECT daylight FROM production_plan WHERE press_id=%s", (self.var_press.get(),))]

    # ================= FETCH PLAN DETAILS (UPDATED) =================
    def fetch_plan_details(self, e):
        press = self.var_press.get()
        dl = self.var_daylight.get()
        
        # 1. ADDED order_id to the end of the query (it is now index 9)
        q = """SELECT tyre_size, brand, pattern, quality, mould_id_marks, type, 
                      tyre_weight, core_size, production_requirement, order_id 
               FROM production_plan 
               WHERE press_id=%s AND daylight=%s"""
               
        res = DBManager.fetch_data(q, (press, dl))
        
        if res:
            r = res[0]
            
            # 2. THE SAFETY FIX: Safely handle text fields (prevents crashes if blank)
            self.var_size.set(r[0] if r[0] else "—")
            self.var_brand.set(r[1] if r[1] else "—")
            self.var_pattern.set(r[2] if r[2] else "—")
            self.var_quality.set(r[3] if r[3] else "—")
            self.var_mould.set(r[4] if r[4] else "—")
            self.var_type.set(r[5] if r[5] else "—")
            
            # 3. Safely handle the numeric weight field (Index 6)
            weight_val = r[6] if r[6] is not None else 0.0
            self.target_weight = float(weight_val)
            self.var_plan_weight.set(f"{self.target_weight} kg")
            
            # 4. Load the specs using the safely extracted variables
            self.load_specs(r[3], r[0], r[5], r[4])
            
            # Status update
            self.lbl_plan_status.config(text="✅ Plan Loaded", fg="#27AE60") # Using direct hex just in case C_SUCCESS isn't defined globally
            
            # 5. BALANCE LOGIC (Index 8)
            target_qty = int(r[8]) if r[8] else 0
            self.update_balance_display(target_qty)
            
            # 6. CATCH THE BATON: Store the Order ID for tracing (Index 9)
            self.current_order_id = r[9] if (len(r) > 9 and r[9] is not None) else None
            
        else:
            # If no plan is assigned to this press, clear the ID
            self.current_order_id = None
            self.lbl_plan_status.config(text="❌ No Plan", fg="#E74C3C")
            # If you have a self.reset_ui() function, uncomment the line below:
            # self.reset_ui()

    def update_balance_display(self, target_qty):
        if target_qty <= 0:
            self.disp_balance.set("N/A")
            return

        # Count built today for this plan
        press_id = self.var_press.get()
        daylight = self.var_daylight.get()
        
        q_count = "SELECT COUNT(*) FROM pc1_building WHERE press_id=%s AND daylight=%s AND date(created_at) = CURRENT_DATE"
        res_count = DBManager.fetch_data(q_count, (press_id, daylight))
        
        built_qty = int(res_count[0][0]) if res_count else 0
        remaining = target_qty - built_qty
        
        self.disp_balance.set(f"{remaining} / {target_qty}")

    def load_specs(self, grade, size, p_type, mould):
        res_grade = DBManager.fetch_data("SELECT core_pct, mid_pct, ct_pct, tread_pct, is_pob, gum_pct FROM tyre_specs WHERE grade=%s", (grade,))
        
        self.current_is_pob = "POB" in str(p_type).upper()
        if res_grade:
            r = res_grade[0]
            if r[4] is not None: self.current_is_pob = r[4]

        # FIX: ONLY LOAD BEADS IF NOT POB
        b_wt = 0.0; b_cnt = 0
        if self.current_is_pob:
            self.disp_bead.set("N/A (POB)")
        else:
            res_bead = DBManager.fetch_data("SELECT bead_size, bead_count, weight_per_bead FROM bead_master WHERE UPPER(tyre_size)=%s LIMIT 1", (str(size).upper(),))
            if res_bead:
                b_wt, b_cnt = float(res_bead[0][2]), int(res_bead[0][1])
                self.disp_bead.set(f"{res_bead[0][0]} x {b_cnt}")
            else:
                self.disp_bead.set("⚠️ Missing")

        if res_grade:
            ct_pct = float(r[2]) if len(r) > 2 and r[2] else 0.0
            gum_pct = float(r[5]) if len(r) > 5 and r[5] else 0.0
            
            net = self.target_weight - (b_wt * b_cnt)
            if net > 0:
                self.disp_core_tgt.set(f"{net*(float(r[0])/100):.2f} kg"); 
                self.disp_mid_tgt.set(f"{net*(float(r[1])/100):.2f} kg"); 
                self.disp_ct_tgt.set(f"{net*(ct_pct/100):.2f} kg")
                self.disp_gum_tgt.set(f"{net*(gum_pct/100):.2f} kg")
                self.disp_tread_tgt.set(f"{net*(float(r[3])/100):.2f} kg")
        
        if self.current_is_pob:
            self.frame_gum.pack(fill="x")
            self.frame_ms_rim.pack(fill="x")
        else:
            self.frame_gum.pack_forget()
            self.frame_ms_rim.pack_forget()
            self.var_ms_rim_wt.set("") # Clear it safely

    # ================= MODIFIED: WEIGHT VALIDATION LOGIC =================
    def submit_build(self, mode):
        # 1. Setup Checks
        if self.var_size.get() == "—" or not self.var_operator.get(): 
            return messagebox.showerror("Error", "Missing Setup", parent=self.root)
        
        # --- NEW MANDATORY GATEKEEPER VALIDATION ---
        # Check if mandatory 'Completion' criteria are met
        tread_batches = self.get_list_values("list_tread")
        wt_val = self.var_weight.get().strip()
        
        # If trying to save as COMPLETED, verify tread and weight exist
        if mode == "COMPLETED":
            missing_items = []
            if not tread_batches: missing_items.append("Tread Batch")
            if not wt_val: missing_items.append("Green Weight")
            
            if missing_items:
                msg = f"⚠️ CANNOT COMPLETE: Missing {', '.join(missing_items)}.\n\nWould you like to save this as a 'PARTIAL' build instead?"
                if messagebox.askyesno("Incomplete Data", msg, parent=self.root):
                    mode = "PARTIAL"
                else:
                    return # Exit if they don't want to save as partial
        # -------------------------------------------

        # 2. Get Weights & Validate
        final_wt = None
        ms_wt = 0.0
        if self.current_is_pob and self.var_ms_rim_wt.get().strip():
            try: 
                ms_wt = float(self.var_ms_rim_wt.get().strip())
            except ValueError: 
                return messagebox.showerror("Error", "Invalid MS Rim Weight Format", parent=self.root)

        if wt_val:
            try:
                final_wt = float(wt_val)
                target_combined = self.target_weight + ms_wt

                # 15% Tolerance Check
                if target_combined > 0:
                    tolerance = 0.15 
                    min_w = target_combined * (1 - tolerance)
                    max_w = target_combined * (1 + tolerance)
                    
                    if final_wt < min_w or final_wt > max_w:
                        msg = f"⚠️ WEIGHT WARNING!\n\nTarget Expected: {target_combined} kg\nEntered: {final_wt} kg\n\nOutside 15% Tolerance. Proceed?"
                        if not messagebox.askyesno("Weight Check", msg, parent=self.root):
                            return
            except ValueError:
                return messagebox.showerror("Error", "Invalid Weight Format", parent=self.root)

        # 3. Save to DB
        bid = self.get_next_bid()
        
        q = """INSERT INTO pc1_building (b_id, press_id, daylight, tyre_size, brand, pattern, quality, mould_id_marks, batch_core, batch_mid, batch_gum, is_pob, batch_tread, tread_type, operator_id, shift, status, green_tyre_weight, ms_rim_weight, building_remarks, birth_time, order_id) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        
        # d tuple uses the validated 'mode' (might have been changed to PARTIAL)
        d = (bid, self.var_press.get(), self.var_daylight.get(), self.var_size.get(), self.var_brand.get(), self.var_pattern.get(), self.var_quality.get(), self.var_mould.get(), self.get_list_values("list_core"), self.get_list_values("list_mid"), self.sel_gum.get(), self.current_is_pob, tread_batches, self.sel_tread_type.get(), self.var_operator.get(), self.var_shift.get(), mode, final_wt, ms_wt, self.var_remarks.get().strip(), datetime.datetime.now() if mode=="COMPLETED" else None, self.current_order_id)
        
        if DBManager.execute_query(q, d):
            self.print_label(bid, self.var_size.get(), self.var_press.get(), self.var_daylight.get())
            self.refresh_today_list()
            messagebox.showinfo("Saved", f"B-ID: {bid}\nStatus: {mode}", parent=self.root)
            self.reset_form()

    # ================= MODIFIED: UPDATE VALIDATION LOGIC =================
    def submit_update(self):
        wt_val = self.upd_weight.get().strip()
        final_wt = None

        if wt_val:
            try:
                final_wt = float(wt_val)
                # Validation (Only if we successfully fetched target_weight in lookup_partial)
                if hasattr(self, 'partial_target_weight') and self.partial_target_weight > 0:
                    min_w = self.partial_target_weight * 0.85
                    max_w = self.partial_target_weight * 1.15
                    if final_wt < min_w or final_wt > max_w:
                         msg = f"⚠️ WEIGHT WARNING!\n\nTarget: {self.partial_target_weight} kg\nEntered: {final_wt} kg\n\nOutside 15% Tolerance.\nProceed?"
                         if not messagebox.askyesno("Weight Check", msg,parent=self.root):
                             return
            except ValueError:
                return messagebox.showerror("Error", "Invalid Weight Format",parent=self.root)

        if DBManager.execute_query("UPDATE pc1_building SET batch_tread=%s, tread_type=%s, green_tyre_weight=%s, status='COMPLETED', birth_time=NOW() WHERE b_id=%s", (self.get_list_values("list_upd_tread"), self.upd_tread_type.get(), final_wt, self.upd_bid.get().strip())):
            messagebox.showinfo("Success", "Updated",parent=self.root); self.refresh_today_list()
            # Clear fields
            self.upd_bid.set(""); self.upd_weight.set(""); self.upd_tread_type.set("")
            if hasattr(self, 'list_upd_tread'): self.list_upd_tread.delete(0, tk.END)
            self.lbl_partial_info.config(text="Waiting...", fg="gray")

    # ================= MODIFIED: LOOKUP PARTIAL TO GET TARGET WEIGHT =================
    def lookup_partial(self, event):
        raw_val = self.upd_bid.get().strip().upper(); self.upd_bid.set(raw_val); bid = raw_val
        if not bid: return
        res = DBManager.fetch_data("SELECT tyre_size, quality, status, tread_type, batch_tread, green_tyre_weight FROM pc1_building WHERE UPPER(b_id)=%s", (bid,))
        if res:
            r = res[0]; status = r[2]; tyre_size = r[0]
            saved_tread_type = r[3] if r[3] else ""; self.upd_tread_type.set(saved_tread_type)
            if saved_tread_type: self.on_upd_tread_type_change(None)
            self.upd_weight.set(str(r[5]) if r[5] else "")
            
            # --- NEW: Fetch Target Weight for Validation ---
            self.partial_target_weight = 0.0
            res_plan = DBManager.fetch_data("SELECT tyre_weight FROM production_plan WHERE tyre_size=%s LIMIT 1", (tyre_size,))
            if res_plan and res_plan[0][0]:
                try: self.partial_target_weight = float(res_plan[0][0])
                except: pass
            # -----------------------------------------------

            if hasattr(self, 'list_upd_tread'):
                self.list_upd_tread.delete(0, tk.END)
                if r[4]:
                    for b in str(r[4]).split(","): 
                        if b.strip(): self.list_upd_tread.insert(tk.END, b.strip())
            self.lbl_partial_info.config(text=f"✅ {r[0]} | {status}", fg=C_SUCCESS if status != "COMPLETED" else C_WARN)
        else: self.lbl_partial_info.config(text="❌ ID NOT FOUND", fg=C_ERROR)

    def generate_report(self):
        res = DBManager.fetch_data("SELECT b_id, created_at, operator_id, tyre_size, status, green_tyre_weight FROM pc1_building WHERE date(created_at) = %s", (self.rep_date.get(),))
        if res:
            path = filedialog.asksaveasfilename(defaultextension=".csv")
            if path:
                with open(path, 'w', newline='') as f:
                    w = csv.writer(f); w.writerow(["ID", "Time", "Op", "Size", "Status", "Weight"]); w.writerows(res)

    def generate_material_report(self):
        self.open_material_dashboard() 

    def get_next_bid(self):
        res = DBManager.fetch_data("SELECT b_id FROM pc1_building ORDER BY created_at DESC LIMIT 1")
        try: return f"B-{int(res[0][0].split('-')[1]) + 1:06d}" if res and res[0][0].startswith("B-") else "B-000001"
        except: return "B-000001"

    def print_label(self, bid, size, press, daylight):
        epl = f'N\nq464\nQ200,24\nA47,30,0,3,1,1,N,"{size} | {press}-{daylight}"\nB60,70,0,1,2,5,90,B,"{bid}"\nP1\n'
        try:
            if platform.system() == "Linux":
                with open(LINUX_PRINTER_PATH, "wb") as f: f.write(epl.encode())
        except: pass

    # HELPERS
    def create_card(self, parent, title):
        f = tk.Frame(parent, bg=C_CARD, bd=1, relief="solid", padx=10, pady=10); f.pack(fill="x", pady=5)
        tk.Label(f, text=title, font=("Segoe UI", 11, "bold"), bg=C_CARD, fg=C_PRIMARY).pack(anchor="w"); return f
    def create_kv(self, p, l, v, b=False):
        f = tk.Frame(p, bg=C_CARD); f.pack(fill="x")
        tk.Label(f, text=l, width=15, anchor="w", bg=C_CARD).pack(side="left")
        tk.Label(f, textvariable=v, font=("Segoe UI", 10, "bold") if b else ("Segoe UI", 10), bg=C_CARD).pack(side="left"); return f
    
    def check_completion_status(self, *args):
        """
        Dynamically enables/disables the 'Save Complete' button.
        Requires: At least 1 Tread Batch AND a Green Weight entry.
        """
        try:
            # Check if the listbox for Tread has any items
            has_tread = self.list_tread.size() > 0
            # Check if the Green Weight entry variable has text
            has_weight = len(self.var_weight.get().strip()) > 0
            
            if has_tread and has_weight:
                # Turn button Green and enable it
                self.btn_save_complete.config(state="normal", bg="#27AE60") 
            else:
                # Grey out button and disable it
                self.btn_save_complete.config(state="disabled", bg="#BDC3C7") 
        except Exception as e:
            print(f"Error updating button state: {e}")

    # --- UPDATED MULTI-SELECT WITH SCANNER BINDING ---
    def create_multi_select(self, p, l, v_sel, attr):
        f = tk.Frame(p, bg=C_CARD); f.pack(fill="x")
        tk.Label(f, text=l, bg=C_CARD, font=("Segoe UI", 9)).pack(anchor="w", pady=(5,0))
        row = tk.Frame(f, bg=C_CARD); row.pack(fill="x")
        cb = ttk.Combobox(row, textvariable=v_sel, height=5); cb.pack(side="left", fill="x", expand=True); setattr(self, f"combo_{attr}", cb)
        
        # BIND ENTER KEY (Scanner Support)
        cb.bind("<Return>", lambda e: self.add_item(attr, v_sel))
        
        tk.Button(row, text="+", command=lambda: self.add_item(attr, v_sel), bg=C_ACCENT, fg="white", width=3).pack(side="right")
        lb = tk.Listbox(f, height=2, bg="#FAFAFA"); lb.pack(fill="x"); setattr(self, attr, lb)
        tk.Button(f, text="Clear", command=lambda: [getattr(self, attr).delete(0, tk.END), self.check_completion_status()], font=("Segoe UI", 7)).pack(anchor="e")

    # --- UPDATED ADD ITEM (Force Uppercase) ---
    def add_item(self, attr, var): 
        val = var.get().strip().upper()
        if val: 
            getattr(self, attr).insert(tk.END, val)
            var.set("")
            # TRIGGER CHECK AFTER ADDING BATCH
            self.check_completion_status()

    def get_list_values(self, attr): return ", ".join(getattr(self, attr).get(0, tk.END))
    def add_label(self, p, t): tk.Label(p, text=t, bg=C_CARD).pack(anchor="w", pady=(5,0))
    def load_operators(self): 
        self.combo_op['values'] = [r[0] for r in DBManager.fetch_data("SELECT full_name FROM users WHERE role='OPERATOR' AND is_active=TRUE")]
    def load_press_list(self): self.combo_press['values'] = [r[0] for r in DBManager.fetch_data("SELECT DISTINCT press_id FROM production_plan")]
    def load_materials(self):
        self.combo_gum_widget['values'] = [r[0] for r in DBManager.fetch_data("SELECT batch_no FROM raw_material_qc WHERE material_type='GUM' AND status='APPROVED'")]
        self.combo_list_core['values'] = [r[0] for r in DBManager.fetch_data("SELECT batch_no FROM raw_material_qc WHERE material_type='CORE' AND status='APPROVED'")]
        self.combo_list_mid['values'] = [r[0] for r in DBManager.fetch_data("SELECT batch_no FROM raw_material_qc WHERE material_type LIKE 'MID%' AND status='APPROVED'")]
    def on_tread_type_change(self, e): self.combo_list_tread['values'] = [r[0] for r in DBManager.fetch_data("SELECT batch_no FROM raw_material_qc WHERE material_type=%s AND status='APPROVED'", (self.sel_tread_type.get(),))]

if __name__ == "__main__":
    root = tk.Tk(); app = PC1SmartApp(root); root.mainloop()