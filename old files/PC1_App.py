import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import csv
import os
import platform
from db_manager import DBManager

# =================================================
# CONFIGURATION
# =================================================
# Validated Connection: Direct USB to /dev/usb/lp4
LINUX_PRINTER_PATH = "/dev/usb/lp4" 

# COLORS
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
        self.root.title(f"PC1 | Smart Builder (EPL Mode - {LINUX_PRINTER_PATH})")
        self.root.geometry("1300x900")
        self.root.configure(bg=C_BG)
        
        self.current_is_pob = False 
        self.target_weight = 0.0

        # --- VARIABLES ---
        self.var_press = tk.StringVar()
        self.var_daylight = tk.StringVar()
        self.var_operator = tk.StringVar()
        self.var_shift = tk.StringVar(value=self.get_current_shift())
        
        # Plan Vars
        self.var_size = tk.StringVar(value="—")
        self.var_brand = tk.StringVar(value="—")
        self.var_pattern = tk.StringVar(value="—")
        self.var_quality = tk.StringVar(value="—") 
        self.var_mould = tk.StringVar(value="—")
        self.var_type = tk.StringVar(value="—") 
        self.var_plan_weight = tk.StringVar(value="—")
        self.var_core_size = tk.StringVar(value="—")
        
        # Spec Display Vars
        self.disp_core_tgt = tk.StringVar(value="—")
        self.disp_mid_tgt = tk.StringVar(value="—")
        self.disp_ct_tgt = tk.StringVar(value="—")
        self.disp_tread_tgt = tk.StringVar(value="—")
        self.disp_bead = tk.StringVar(value="—")
        
        # Material Selection
        self.sel_core = tk.StringVar()
        self.sel_mid = tk.StringVar()
        self.sel_gum = tk.StringVar()
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

    def get_current_shift(self):
        h = datetime.datetime.now().hour
        if 7 <= h < 15: return "A"
        elif 15 <= h < 23: return "B"
        else: return "C"

    def connect_and_load(self):
        try:
            DBManager.get_connection()
            print("✅ Database Connected")
            self.load_operators()
            self.load_press_list()
            self.load_materials()
            self.refresh_today_list()
        except Exception as e:
            messagebox.showerror("Error", f"DB Connection Failed:\n{e}")

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
        left = tk.Frame(self.tab1, bg=C_BG)
        left.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # 1. SETUP CARD
        card_setup = self.create_card(left, "1. SETUP & DETAILS")
        self.add_label(card_setup, "Operator:")
        self.combo_op = ttk.Combobox(card_setup, textvariable=self.var_operator, font=("Segoe UI", 11))
        self.combo_op.pack(fill="x", pady=2)
        
        f_pd = tk.Frame(card_setup, bg=C_CARD); f_pd.pack(fill="x", pady=2)
        self.combo_press = ttk.Combobox(f_pd, textvariable=self.var_press, width=10, font=("Segoe UI", 11))
        self.combo_press.pack(side="left", padx=(0,5))
        self.combo_press.bind("<<ComboboxSelected>>", self.on_press_change)
        self.combo_daylight = ttk.Combobox(f_pd, textvariable=self.var_daylight, width=10, font=("Segoe UI", 11))
        self.combo_daylight.pack(side="left")
        self.combo_daylight.bind("<<ComboboxSelected>>", self.fetch_plan_details)
        
        self.lbl_plan_status = tk.Label(card_setup, text="Select Plan...", fg="gray", bg=C_CARD)
        self.lbl_plan_status.pack(pady=5)
        
        self.create_kv(card_setup, "Size:", self.var_size, True)
        self.create_kv(card_setup, "Grade:", self.var_quality, True)
        self.create_kv(card_setup, "Brand:", self.var_brand)
        self.create_kv(card_setup, "Core Size:", self.var_core_size)
        self.create_kv(card_setup, "Type:", self.var_type)
        self.create_kv(card_setup, "Plan Wt:", self.var_plan_weight, True)

        # 2. TARGETS CARD
        card_spec = self.create_card(left, "2. TARGETS (Calculated)")
        self.row_core_tgt = self.create_kv(card_spec, "Core Tgt:", self.disp_core_tgt)
        self.row_mid_tgt = self.create_kv(card_spec, "Middle Tgt:", self.disp_mid_tgt)
        self.row_ct_tgt = self.create_kv(card_spec, "C+T Tgt:", self.disp_ct_tgt)
        self.row_tread_tgt = self.create_kv(card_spec, "Tread Tgt:", self.disp_tread_tgt)
        self.row_bead_tgt = self.create_kv(card_spec, "Bead Req:", self.disp_bead, True)

        # RIGHT: Materials
        right = tk.Frame(self.tab1, bg=C_BG)
        right.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        card_mat = self.create_card(right, "3. MATERIALS")
        
        self.row_core_input = self.create_multi_select(card_mat, "Core Batch(es):", self.sel_core, "list_core")
        self.row_mid_input = self.create_multi_select(card_mat, "Middle Layer(s):", self.sel_mid, "list_mid")
        
        tk.Label(card_mat, text="--- Tread & Gum ---", bg=C_CARD, fg="gray").pack(pady=10)
        self.add_label(card_mat, "Tread Type:")
        self.combo_tt = ttk.Combobox(card_mat, textvariable=self.sel_tread_type, values=["VT001", "VT002", "VT003", "NMW"])
        self.combo_tt.pack(fill="x")
        self.combo_tt.bind("<<ComboboxSelected>>", self.on_tread_type_change)
        self.create_multi_select(card_mat, "Tread Batch(es):", self.sel_tread, "list_tread")

        self.frame_gum = tk.Frame(card_mat, bg=C_CARD, pady=5)
        self.frame_gum.pack(fill="x", pady=5)
        tk.Label(self.frame_gum, text="Bonding Gum (POB Only):", fg=C_POB, bg=C_CARD, font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.combo_gum_widget = ttk.Combobox(self.frame_gum, textvariable=self.sel_gum, height=5)
        self.combo_gum_widget.pack(fill="x")
        self.frame_gum.pack_forget() 

        self.add_label(card_mat, "Final Green Weight (Kg):")
        tk.Entry(card_mat, textvariable=self.var_weight, font=("Segoe UI", 12), bg="#EBF5FB").pack(fill="x")
        
        f_btn = tk.Frame(right, bg=C_BG)
        f_btn.pack(fill="x", pady=20)
        self.btn_partial = tk.Button(f_btn, text="⚠️ SAVE PARTIAL\n(Core Only)", command=lambda: self.submit_build("PARTIAL"), bg=C_PARTIAL, fg="white", width=15)
        self.btn_partial.pack(side="left", padx=5)
        self.btn_complete = tk.Button(f_btn, text="✅ SAVE COMPLETE\n(Full Build)", command=lambda: self.submit_build("COMPLETED"), bg=C_SUCCESS, fg="white", width=20)
        self.btn_complete.pack(side="right", padx=5)

    def build_tab2(self):
        # --- TAB 2: UPDATE ---
        card = self.create_card(self.tab2, "APPLY TREAD TO PARTIAL TYRE")
        card.pack(fill="both", expand=True, padx=100, pady=50)
        self.add_label(card, "Scan Partial Tyre (B-ID):")
        
        # SCAN INPUT BOX
        e_scan = tk.Entry(card, textvariable=self.upd_bid, font=("Segoe UI", 16), bg="#FFF8DC", bd=2)
        e_scan.pack(fill="x", pady=5)
        
        # --- SMART SCAN LOGIC ---
        e_scan.bind("<Return>", self.lookup_partial) # Trigger on Enter key
        e_scan.bind("<Tab>", self.lookup_partial)    # Trigger on Tab (some scanners do this)
        self.upd_bid.trace_add("write", self.check_scan_length) # Trigger if text hits 8 chars
        
        e_scan.focus_set() # Auto-focus this box

        self.lbl_partial_info = tk.Label(card, text="Waiting...", font=("Segoe UI", 12), bg=C_CARD, fg="gray")
        self.lbl_partial_info.pack(pady=10)
        
        self.add_label(card, "Select Tread Type:")
        self.combo_upd_tt = ttk.Combobox(card, textvariable=self.upd_tread_type, values=["VT001", "VT002", "VT003", "NMW"])
        self.combo_upd_tt.pack(fill="x")
        self.combo_upd_tt.bind("<<ComboboxSelected>>", self.on_upd_tread_type_change)
        
        self.create_multi_select(card, "Tread Batch(es):", self.upd_tread, "list_upd_tread")
        self.add_label(card, "Final Green Weight (Kg):")
        tk.Entry(card, textvariable=self.upd_weight, font=("Segoe UI", 14), bg="#EBF5FB").pack(fill="x")
        tk.Button(card, text="💾 UPDATE & COMPLETE", command=self.submit_update, bg=C_SUCCESS, fg="white", pady=10).pack(fill="x", pady=20)

    def check_scan_length(self, *args):
        # Automatically trigger if the text looks like a full ID (B-000001 is 8 chars)
        text = self.upd_bid.get().strip().upper()
        if len(text) == 8 and text.startswith("B-"):
            self.lookup_partial(None)

    def build_tab3(self):
        left = tk.Frame(self.tab3, bg=C_BG); left.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        card_reprint = self.create_card(left, "3.1 TODAY'S PRODUCTION (Reprint)")
        
        cols = ("B-ID", "Time", "Size", "Status")
        self.tree = ttk.Treeview(card_reprint, columns=cols, show="headings", height=15)
        for c in cols: self.tree.heading(c, text=c)
        self.tree.column("B-ID", width=120)
        self.tree.pack(fill="both", expand=True, pady=10)
        
        btn_f = tk.Frame(card_reprint, bg=C_CARD); btn_f.pack(fill="x", pady=10)
        tk.Button(btn_f, text="🔄 Refresh", command=self.refresh_today_list).pack(side="left", padx=5)
        tk.Button(btn_f, text="🖨️ Reprint SELECTED", command=self.reprint_selected, bg=C_WARN, fg="white").pack(side="left", padx=5)
        tk.Button(btn_f, text="⏪ Reprint LAST", command=self.reprint_last, bg=C_PRIMARY, fg="white").pack(side="right", padx=5)

        right = tk.Frame(self.tab3, bg=C_BG); right.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        card_report = self.create_card(right, "3.2 SHIFT REPORT (Hardcopy)")
        
        self.add_label(card_report, "Select Date (YYYY-MM-DD):")
        tk.Entry(card_report, textvariable=self.rep_date, font=("Segoe UI", 12)).pack(fill="x", pady=5)
        self.add_label(card_report, "Select Shift:")
        ttk.Combobox(card_report, textvariable=self.rep_shift, values=["A", "B", "C", "ALL"], font=("Segoe UI", 12)).pack(fill="x", pady=5)
        tk.Button(card_report, text="📄 GENERATE REPORT", command=self.generate_report, bg=C_SUCCESS, fg="white", font=("Segoe UI", 12, "bold"), pady=10).pack(fill="x", pady=20)

    # ================= LOGIC: Reprint & Reports =================
    def refresh_today_list(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        res = DBManager.fetch_data("SELECT b_id, to_char(created_at, 'HH24:MI'), tyre_size, status FROM pc1_building WHERE date(created_at) = CURRENT_DATE ORDER BY created_at DESC")
        if res:
            for r in res: self.tree.insert("", "end", values=r)

    def reprint_selected(self):
        sel = self.tree.selection()
        if not sel: return messagebox.showwarning("Warning", "Select a record first!")
        bid = self.tree.item(sel[0])['values'][0]
        q = "SELECT tyre_size, press_id, daylight FROM pc1_building WHERE b_id=%s"
        res = DBManager.fetch_data(q, (bid,))
        if res: self.print_label(bid, res[0][0], res[0][1], res[0][2])
        else: messagebox.showerror("Error", "Could not fetch details")

    def reprint_last(self):
        q = "SELECT b_id, tyre_size, press_id, daylight FROM pc1_building ORDER BY created_at DESC LIMIT 1"
        res = DBManager.fetch_data(q)
        if res: self.print_label(res[0][0], res[0][1], res[0][2], res[0][3])
        else: messagebox.showinfo("Info", "No records found.")

    def generate_report(self):
        dt = self.rep_date.get(); sh = self.rep_shift.get()
        q = "SELECT b_id, created_at, shift, operator_id, tyre_size, quality, status, green_tyre_weight, is_pob FROM pc1_building WHERE date(created_at) = %s"
        p = [dt]
        if sh != "ALL": q += " AND shift = %s"; p.append(sh)
        res = DBManager.fetch_data(q, tuple(p))
        if not res: return messagebox.showinfo("Empty", "No data found.")
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile=f"Report_{dt}_{sh}.csv")
        if path:
            with open(path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["B-ID", "Time", "Shift", "Operator", "Size", "Grade", "Status", "Weight", "Is POB"])
                writer.writerows(res)
            messagebox.showinfo("Success", f"Report saved!\n{path}")

    # ================= LOGIC: Specs & Validation =================
    def fetch_plan_details(self, event):
        p = self.var_press.get(); d = self.var_daylight.get()
        if not p or not d: return
        res = DBManager.fetch_data("SELECT tyre_size, brand, pattern, quality, mould_id_marks, type, tyre_weight, core_size FROM production_plan WHERE press_id=%s AND daylight=%s", (p, d))
        if res:
            r = res[0]
            self.var_size.set(r[0]); self.var_brand.set(r[1]); self.var_pattern.set(r[2]); self.var_quality.set(r[3]); self.var_mould.set(r[4]); self.var_type.set(r[5] if r[5] else "—"); self.var_core_size.set(r[7] if r[7] else "—")
            self.target_weight = float(r[6]) if r[6] else 0.0
            self.var_plan_weight.set(f"{self.target_weight} kg")
            self.lbl_plan_status.config(text="✅ Plan Loaded", fg=C_SUCCESS)
            self.load_specs(r[3], r[0], r[5], r[4]) 
        else:
            self.lbl_plan_status.config(text="❌ Not Found", fg=C_ERROR)

    def load_specs(self, grade, size, p_type, mould_id):
        clean_size = str(size).upper().strip()
        clean_mould = str(mould_id).strip()
        query_grade = "SELECT core_pct, mid_pct, ct_pct, tread_pct, is_pob FROM tyre_specs WHERE grade=%s"
        res_grade = DBManager.fetch_data(query_grade, (grade,))
        
        # Smart Bead Lookup
        query_bead_spec = "SELECT bead_size, bead_count, weight_per_bead FROM bead_master WHERE UPPER(tyre_size)=%s AND mould_id=%s"
        res_bead = DBManager.fetch_data(query_bead_spec, (clean_size, clean_mould))
        if not res_bead: res_bead = DBManager.fetch_data("SELECT bead_size, bead_count, weight_per_bead FROM bead_master WHERE UPPER(tyre_size)=%s AND (mould_id='' OR mould_id IS NULL)", (clean_size,))
        if not res_bead: res_bead = DBManager.fetch_data("SELECT bead_size, bead_count, weight_per_bead FROM bead_master WHERE UPPER(tyre_size)=%s LIMIT 1", (clean_size,))

        bead_wt_unit = 0.0; bead_count = 0
        if res_bead:
            b = res_bead[0]; self.disp_bead.set(f"{b[0]} x {b[1]}"); bead_count = int(b[1] or 0); bead_wt_unit = float(b[2] or 0.0)
        else: self.disp_bead.set("⚠️ Bead Spec Missing")

        is_pob_plan = p_type and "POB" in str(p_type).upper()
        self.current_is_pob = is_pob_plan
        
        if res_grade:
            r = res_grade[0]
            if r[4] is not None: self.current_is_pob = r[4]
            net_rubber = self.target_weight - (bead_count * bead_wt_unit)
            if net_rubber > 0:
                self.disp_core_tgt.set(f"{net_rubber*(float(r[0] or 0)/100.0):.2f} kg")
                self.disp_mid_tgt.set(f"{net_rubber*(float(r[1] or 0)/100.0):.2f} kg")
                self.disp_ct_tgt.set(f"{net_rubber*(float(r[2] or 0)/100.0):.2f} kg")
                self.disp_tread_tgt.set(f"{net_rubber*(float(r[3] or 0)/100.0):.2f} kg")
            else: self.disp_core_tgt.set("Wt Error")

        if self.current_is_pob:
            self.row_core_tgt.pack_forget(); self.row_mid_tgt.pack_forget(); self.row_bead_tgt.pack_forget()
            self.row_core_input.pack_forget(); self.row_mid_input.pack_forget(); self.frame_gum.pack(fill="x", pady=5) 
        else:
            self.row_core_tgt.pack(fill="x"); self.row_mid_tgt.pack(fill="x"); self.row_bead_tgt.pack(fill="x")
            self.row_core_input.pack(fill="x"); self.row_mid_input.pack(fill="x"); self.frame_gum.pack_forget()

    def submit_build(self, mode):
        if self.var_size.get() == "—": return messagebox.showerror("Error", "Select Plan")
        if not self.var_operator.get(): return messagebox.showerror("Error", "Select Operator")
        if self.sel_core.get(): self.add_item("list_core", self.sel_core)
        if self.sel_mid.get(): self.add_item("list_mid", self.sel_mid)
        if self.sel_tread.get(): self.add_item("list_tread", self.sel_tread)

        # --- VALIDATION ---
        # 1. Check Core (Always Required for non-POB)
        if not self.current_is_pob:
            if not self.get_list_values("list_core"): 
                return messagebox.showerror("Error", "Core Batch Required!")
            
            # 2. Check Middle Layer (Smart Warning)
            # If the calculated Target Weight for Middle Layer is > 0.0, it means this spec NEEDS a middle layer.
            # We check if the user actually added any batches to the list.
            mid_target_str = self.disp_mid_tgt.get()  # e.g., "12.5 kg (15%)" or "—"
            
            # Extract the number from the string (if it exists)
            needs_middle_layer = False
            if "kg" in mid_target_str:
                try:
                    val = float(mid_target_str.split(" ")[0]) # Get the "12.5" part
                    if val > 0.1: needs_middle_layer = True
                except:
                    pass

            # If it needs a layer but the list is empty -> WARN USER
            if needs_middle_layer and not self.get_list_values("list_mid"):
                # Ask for confirmation (Yes/No)
                confirm = messagebox.askyesno("Missing Middle Layer", 
                    "⚠️ WARNING: This spec requires a MIDDLE LAYER!\n\n"
                    "You have not scanned any Middle Layer batches.\n\n"
                    "Do you want to save anyway?")
                if not confirm:
                    return # Cancel the save if they say No
        else:
            if not self.sel_gum.get(): return messagebox.showerror("Error", "Gum Req")
        if mode == "COMPLETED":
            if not self.get_list_values("list_tread") or not self.var_weight.get(): return messagebox.showerror("Error", "Tread & Weight Req")

        bid = self.get_next_bid()
        q = """INSERT INTO pc1_building (b_id, press_id, daylight, tyre_size, brand, pattern, quality, mould_id_marks, core_batch, mid_batch, gum_batch, is_pob, tread_batch, tread_type, operator_id, shift, status, green_tyre_weight, birth_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        d = (bid, self.var_press.get(), self.var_daylight.get(), self.var_size.get(), self.var_brand.get(), self.var_pattern.get(), self.var_quality.get(), self.var_mould.get(), self.get_list_values("list_core"), self.get_list_values("list_mid"), self.sel_gum.get(), self.current_is_pob, self.get_list_values("list_tread"), self.sel_tread_type.get(), self.var_operator.get(), self.var_shift.get(), mode, self.var_weight.get() if self.var_weight.get() else None, datetime.datetime.now() if mode=="COMPLETED" else None)
        
        if DBManager.execute_query(q, d):
            self.print_label(bid, self.var_size.get(), self.var_press.get(), self.var_daylight.get())
            self.var_weight.set(""); self.sel_tread.set(""); self.sel_gum.set("")
            getattr(self, "list_tread").delete(0, tk.END)
            self.refresh_today_list()
            messagebox.showinfo("Success", f"Saved {bid}")

    def submit_update(self):
        bid = self.upd_bid.get().strip()
        batches = self.get_list_values("list_upd_tread")
        wt = self.upd_weight.get()
        tt = self.upd_tread_type.get()
        if not bid or not batches or not wt: return messagebox.showerror("Error", "All fields required!")
        query = "UPDATE pc1_building SET tread_batch=%s, tread_type=%s, green_tyre_weight=%s, status='COMPLETED', updated_at=NOW(), birth_time=NOW() WHERE b_id=%s"
        if DBManager.execute_query(query, (batches, tt, wt, bid)):
            messagebox.showinfo("Success", "Tyre Updated!")
            self.upd_bid.set(""); self.upd_weight.set(""); getattr(self, "list_upd_tread").delete(0, tk.END)
            self.refresh_today_list()

    def lookup_partial(self, event):
        bid = self.upd_bid.get().strip()
        if not bid: return
        
        # FETCH FULL DETAILS (Includes Tread info & Weight now)
        q = "SELECT tyre_size, quality, status, tread_type, tread_batch, green_tyre_weight FROM pc1_building WHERE b_id=%s"
        res = DBManager.fetch_data(q, (bid,))
        
        if res:
            r = res[0]
            status = r[2]
            
            # Clear fields first to avoid confusion
            self.upd_tread_type.set("")
            self.upd_weight.set("")
            getattr(self, "list_upd_tread").delete(0, tk.END)

            if status == "COMPLETED":
                # --- EDIT MODE TRIGGER ---
                self.lbl_partial_info.config(text=f"⚠️ EDITING: {r[0]}", fg=C_WARN)
                
                # 1. Show Warning
                messagebox.showwarning("Edit Mode", f"⚠️ Tyre {bid} is ALREADY COMPLETED.\n\nYou are now editing the existing record.")
                
                # 2. Pre-fill the Existing Data (So you don't have to re-type it)
                if r[3]: self.upd_tread_type.set(r[3])  # Tread Type
                if r[5]: self.upd_weight.set(r[5])      # Existing Weight
                
                # 3. Pre-fill Tread Batches (Split the string back into list items)
                if r[4]:
                    batches = r[4].split(", ")
                    for b in batches:
                        getattr(self, "list_upd_tread").insert(tk.END, b)

            else:
                # --- NORMAL PARTIAL MODE ---
                self.lbl_partial_info.config(text=f"✅ Found: {r[0]} | {r[1]}", fg=C_SUCCESS)
                # Auto-fill Tread Type if we can guess it (Optional, usually manual)
                
        else:
            self.lbl_partial_info.config(text="❌ Not Found", fg=C_ERROR)
            
    # ================= HELPER METHODS =================
    def create_card(self, parent, title):
        frame = tk.Frame(parent, bg=C_CARD, bd=1, relief="solid", padx=10, pady=10)
        frame.pack(fill="x", pady=5)
        tk.Label(frame, text=title, font=("Segoe UI", 11, "bold"), bg=C_CARD, fg=C_PRIMARY).pack(anchor="w")
        return frame
    
    def create_kv(self, parent, label, var, bold=False):
        f = tk.Frame(parent, bg=C_CARD); f.pack(fill="x")
        tk.Label(f, text=label, width=15, anchor="w", bg=C_CARD).pack(side="left")
        font = ("Segoe UI", 11, "bold") if bold else ("Segoe UI", 10)
        tk.Label(f, textvariable=var, anchor="w", bg=C_CARD, font=font, fg=C_ACCENT if bold else "black").pack(side="left"); return f
    
    def create_multi_select(self, parent, label, var_sel, list_attr):
        f = tk.Frame(parent, bg=C_CARD); f.pack(fill="x")
        tk.Label(f, text=label, bg=C_CARD, font=("Segoe UI", 9)).pack(anchor="w", pady=(5,0))
        row = tk.Frame(f, bg=C_CARD); row.pack(fill="x")
        cb = ttk.Combobox(row, textvariable=var_sel, height=5); cb.pack(side="left", fill="x", expand=True)
        setattr(self, f"combo_{list_attr}", cb)
        tk.Button(row, text="+", command=lambda l=list_attr, v=var_sel: self.add_item(l, v), bg=C_ACCENT, fg="white", width=3).pack(side="right")
        lb = tk.Listbox(f, height=2, bg="#FAFAFA"); lb.pack(fill="x"); setattr(self, list_attr, lb)
        tk.Button(f, text="Clear", command=lambda: getattr(self, list_attr).delete(0, tk.END), font=("Segoe UI", 7)).pack(anchor="e"); return f

    def add_item(self, list_attr, var):
        val = var.get().strip()
        if val: getattr(self, list_attr).insert(tk.END, val); var.set("")
            
    def get_list_values(self, list_attr): return ", ".join(getattr(self, list_attr).get(0, tk.END))
    def add_label(self, parent, text): tk.Label(parent, text=text, bg=C_CARD).pack(anchor="w", pady=(5,0))
    def load_operators(self): self.combo_op['values'] = [r[0] for r in DBManager.fetch_data("SELECT full_name FROM users WHERE is_active=TRUE")]
    def load_press_list(self): self.combo_press['values'] = [r[0] for r in DBManager.fetch_data("SELECT DISTINCT press_id FROM production_plan")]
    def on_press_change(self, event): self.combo_daylight['values'] = [r[0] for r in DBManager.fetch_data("SELECT daylight FROM production_plan WHERE press_id=%s", (self.var_press.get(),))]
    def load_materials(self):
        self.combo_gum_widget['values'] = [r[0] for r in DBManager.fetch_data("SELECT batch_no FROM raw_material_qc WHERE material_type='GUM' AND status='APPROVED'")]
        getattr(self, "combo_list_core")['values'] = [r[0] for r in DBManager.fetch_data("SELECT batch_no FROM raw_material_qc WHERE material_type='CORE' AND status='APPROVED'")]
        getattr(self, "combo_list_mid")['values'] = [r[0] for r in DBManager.fetch_data("SELECT batch_no FROM raw_material_qc WHERE (material_type='MIDDLE_LAYER' OR material_type='MIDDLE LAYER') AND status='APPROVED'")]
    def on_tread_type_change(self, event): getattr(self, "combo_list_tread")['values'] = [r[0] for r in DBManager.fetch_data("SELECT batch_no FROM raw_material_qc WHERE material_type=%s AND status='APPROVED'", (self.sel_tread_type.get(),))]
    def on_upd_tread_type_change(self, event): getattr(self, "combo_list_upd_tread")['values'] = [r[0] for r in DBManager.fetch_data("SELECT batch_no FROM raw_material_qc WHERE material_type=%s AND status='APPROVED'", (self.upd_tread_type.get(),))]
    def get_next_bid(self):
        res = DBManager.fetch_data("SELECT b_id FROM pc1_building ORDER BY created_at DESC LIMIT 1")
        if res and res[0][0].startswith("B-"):
            try: return f"B-{int(res[0][0].split('-')[1]) + 1:06d}"
            except: return "B-000001"
        return "B-000001"
    
    def print_label(self, bid, size, press, daylight):
        # EPL COMMANDS
        # q464 = Width 58mm
        # Q200,24 = Length 25mm (Calibrated to stop skipping)
        # B... 2,5 = Narrow 2 dots, Wide 5 dots (Standard readable 1:2.5 ratio)
        epl_data = f"""
N
q464
Q200,24
A47,30,0,3,1,1,N,"{size} | {press}-{daylight}"
B60,70,0,1,2,8,90,B,"{bid}"
P1
"""
        try:
            if platform.system() == "Linux":
                with open(LINUX_PRINTER_PATH, "wb") as f:
                    f.write(epl_data.encode())
                print(f"✅ Label Sent: {bid}")
            else:
                print("Windows Printing not implemented")
        except Exception as e:
            messagebox.showerror("Print Error", f"Check Printer USB!\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PC1SmartApp(root)
    root.mainloop()