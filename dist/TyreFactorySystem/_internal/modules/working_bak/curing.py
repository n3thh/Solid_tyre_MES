import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import datetime
import json
import os
import platform
import re
import csv
from db_manager import DBManager

# ================= CONFIGURATION =================
LINUX_PRINTER_PATH = "/dev/usb/lp0" 
CONFIG_FILE = "press_config.json"

# COLORS
C_BG = "#2C3E50"       # Dark Blue
C_CARD = "#ECF0F1"     # Light Grey
C_ACCENT = "#E74C3C"   # Red (Heat/Action)
C_SUCCESS = "#27AE60"  # Green
C_WARN = "#F39C12"     # Orange (Oven/Warning)
C_HISTORY = "#34495E"  # Dark Slate
C_OVERDUE = "#C0392B"  # Dark Red for overdue text
C_COOLING = "#3498DB"  # Blue for Cooling Status

class CuringApp:
    def __init__(self, root, current_user="SUPERVISOR"):
        self.root = root
        self.root.title(f"PC2 | Curing Station (Logged in as: {current_user})")
        self.root.geometry("1200x850")
        self.root.configure(bg=C_BG)
        
        self.current_supervisor = current_user

        # --- VARIABLES ---
        self.var_bid = tk.StringVar()
        self.var_serial = tk.StringVar()
        self.var_operator = tk.StringVar()
        
        # Location Vars
        self.var_press = tk.StringVar()       
        self.var_mould = tk.StringVar() 
        
        # Params
        self.var_temp = tk.StringVar(value="160")
        self.var_pressure = tk.StringVar(value="150")
        self.var_time = tk.StringVar(value="45")
        
        # Internal Logic
        self.target_oven_id = None            
        
        # QC Vars
        self.var_cid = tk.StringVar()
        self.var_final_wt = tk.StringVar()
        self.var_flash = tk.StringVar(value="0.0")
        self.var_qc_status = tk.StringVar(value="OK")
        self.var_qc_remarks = tk.StringVar()
        
        # History
        self.hist_date = tk.StringVar(value=datetime.datetime.now().strftime("%Y-%m-%d"))
        self.hist_shift = tk.StringVar(value="ALL") 

        self.green_weight = 0.0
        
        # Load Press Config
        self.press_modes = self.load_config() 

        self.setup_ui()
        self.load_operators() 
        self.load_active_cures()
        self.root.after(30000, self.auto_refresh)

    def auto_refresh(self):
        self.load_active_cures()
        self.root.after(30000, self.auto_refresh)

    def load_config(self):
        default = {"P1": "STD", "P2": "STD", "P3": "STD", "P7": "STD"}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f: return json.load(f)
            except: pass
        return default

    def save_config(self):
        with open(CONFIG_FILE, 'w') as f: json.dump(self.press_modes, f)

    def normalize_press_id(self, raw_name):
        if not raw_name: return "UNKNOWN"
        match = re.search(r'P\D*0*(\d+)', str(raw_name).upper())
        if match: return f"P{match.group(1)}"
        return str(raw_name)

    def load_operators(self):
        q = "SELECT full_name FROM users WHERE role='OPERATOR' AND is_active=TRUE ORDER BY full_name"
        res = DBManager.fetch_data(q)
        if res:
            ops = [r[0] for r in res]
            self.combo_op['values'] = ops
        else:
            self.combo_op['values'] = ["Op1", "Op2"] 

    def setup_ui(self):
        # HEADER
        header = tk.Frame(self.root, bg=C_ACCENT, height=50)
        header.pack(fill="x")
        tk.Label(header, text=f"🔥 PC2 - CURING TRACEABILITY | Supervisor: {self.current_supervisor}", font=("Segoe UI", 14, "bold"), bg=C_ACCENT, fg="white").pack(pady=10)

        # SWITCHBOARD
        self.f_switch = tk.Frame(self.root, bg="#34495E", pady=10)
        self.f_switch.pack(fill="x")
        tk.Label(self.f_switch, text="MACHINE CONFIG:", fg="white", bg="#34495E", font=("Segoe UI", 10, "bold")).pack(side="left", padx=20)
        
        self.btn_switches = {}
        for p in ["P1", "P2", "P3", "P7"]:
            btn = tk.Button(self.f_switch, text=f"{p}: {self.press_modes.get(p, 'STD')}", width=12, font=("Segoe UI", 9, "bold"),
                            command=lambda x=p: self.toggle_press_mode(x))
            btn.pack(side="left", padx=5)
            self.update_switch_color(btn, self.press_modes.get(p, 'STD'))
            self.btn_switches[p] = btn

        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab1 = tk.Frame(nb, bg=C_BG); nb.add(self.tab1, text="  🔥 1. START & UNLOAD  ")
        self.tab2 = tk.Frame(nb, bg=C_BG); nb.add(self.tab2, text="  ⚖️ 2. QC & WEIGH  ")
        self.tab3 = tk.Frame(nb, bg=C_HISTORY); nb.add(self.tab3, text="  📜 3. REPORTS  ")
        
        # FIXED: 4. Pending Queue Tab 
        self.tab_pending = tk.Frame(nb, bg=C_BG)
        nb.add(self.tab_pending, text="  ⌛ 4. PENDING QUEUE  ")

        self.build_tab1()
        self.build_tab2()
        self.build_tab3()
        self.setup_pending_tab() # This builds the grid inside the new tab

    def toggle_press_mode(self, press_name):
        curr = self.press_modes.get(press_name, "STD")
        new_mode = "OVEN" if curr == "STD" else "STD"
        self.press_modes[press_name] = new_mode
        self.save_config()
        btn = self.btn_switches[press_name]
        btn.config(text=f"{press_name}: {new_mode}")
        self.update_switch_color(btn, new_mode)

    def setup_pending_tab(self):
        # Header & Action Buttons
        f_top = tk.Frame(self.tab_pending, bg="white", pady=10)
        f_top.pack(fill="x")
        tk.Label(f_top, text="🕒 PENDING GREEN TYRES (WIP)", font=("Segoe UI", 16, "bold"), bg="white", fg="#2C3E50").pack(side="left", padx=20)
        
        tk.Button(f_top, text="🔄 REFRESH QUEUE", command=self.load_pending_queue, bg="#2980B9", fg="white", font=("Segoe UI", 10, "bold")).pack(side="right", padx=20)
        tk.Button(f_top, text="🖨️ REPRINT LABEL", command=self.reprint_label, bg="#8E44AD", fg="white", font=("Segoe UI", 10, "bold")).pack(side="right", padx=10)
        # Pending Queue Treeview
        cols = ("Green ID", "Size", "Brand", "Built Time", "Age (Hrs)", "Status")
        self.tree_pending = ttk.Treeview(self.tab_pending, columns=cols, show="headings", height=20)
        
        for c in cols: self.tree_pending.heading(c, text=c)
        self.tree_pending.column("Green ID", width=120)
        self.tree_pending.column("Size", width=150)
        self.tree_pending.column("Brand", width=120)
        self.tree_pending.column("Built Time", width=150)
        self.tree_pending.column("Age (Hrs)", width=80, anchor="center")
        self.tree_pending.column("Status", width=120, anchor="center")
        
        self.tree_pending.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Color Tags based on your age rules
        self.tree_pending.tag_configure('ideal', background='#EAFAF1')  # 0-8 hrs (Light Green)
        self.tree_pending.tag_configure('okay', background='#FCF3CF')   # 8-24 hrs (Light Yellow)
        self.tree_pending.tag_configure('attention', background='#F5B041') # 24-72 hrs (Orange)
        self.tree_pending.tag_configure('risky', background='#E74C3C', foreground='white') # >72 hrs (Red)

        # Load data initially
        self.load_pending_queue()

    def load_pending_queue(self):
        # Clear existing rows
        for i in self.tree_pending.get_children(): self.tree_pending.delete(i)
            
        # SQL: Find tyres in PC1 that do NOT exist in PC2
        q = """
            SELECT b.b_id, b.tyre_size, b.brand, b.created_at, 
                   ROUND(CAST(EXTRACT(EPOCH FROM (NOW() - b.created_at))/3600 AS NUMERIC), 1) as age_hours
            FROM pc1_building b
            LEFT JOIN pc2_curing c ON b.b_id = c.b_id
            WHERE c.b_id IS NULL
            ORDER BY age_hours DESC;
        """
        res = DBManager.fetch_data(q)
        
        if res:
            for r in res:
                gid, size, brand, built_at, age = r
                age = float(age) if age else 0.0
                
                # Apply the rule thresholds
                if age <= 8:
                    tag, status = 'ideal', "IDEAL"
                elif age <= 24:
                    tag, status = 'okay', "OKAY"
                elif age <= 72:
                    tag, status = 'attention', "ATTENTION"
                else:
                    tag, status = 'risky', "RISKY"
                    
                self.tree_pending.insert("", "end", values=(gid, size, brand, built_at, age, status), tags=(tag,))

    def reprint_label(self):
        selected = self.tree_pending.selection()
        if not selected:
            return messagebox.showwarning("Warning", "Please select a tyre from the queue to reprint.",parent=self.root)
            
        # Get data DIRECTLY from the selected row on the screen
        row_data = self.tree_pending.item(selected[0])['values']
        green_id = str(row_data[0]).strip()
        size = str(row_data[1]).strip()
        brand = str(row_data[2]).strip()
        
        if messagebox.askyesno("Confirm Reprint", f"Are you sure you want to reprint the barcode label for:\n\nGreen ID: {green_id}\nSize: {size}\nBrand: {brand}",parent=self.root):
            try:
                # ==========================================
                # EPL PRINTER LOGIC
                # ==========================================
                import platform
                
                # Format: Size | Brand (REPRINT) and the Barcode
                epl = f'N\nq464\nQ200,30\nA30,10,0,3,1,1,N,"{size} | {brand} (REPRINT)"\nB60,60,0,1,2,5,100,B,"{green_id}"\nP1\n'
                
                if platform.system() == "Linux":
                    # Note: Ensure LINUX_PRINTER_PATH is defined at the top of your file
                    with open(LINUX_PRINTER_PATH, "wb") as f: 
                        f.write(epl.encode())
                else:
                    print(f"Simulated Print on Windows/Mac:\n{epl}")
                # ==========================================
                
                print(f"Reprinting: {green_id} | {size} | {brand}") # Terminal test
                messagebox.showinfo("Success", f"Label {green_id} sent to printer!",parent=self.root)
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reprint label: {e}",parent=self.root)

    def update_switch_color(self, btn, mode):
        if mode == "STD": btn.config(bg=C_SUCCESS, fg="white") 
        else: btn.config(bg=C_WARN, fg="black")    

    # ================= TAB 1: CURING PROCESS =================
    def build_tab1(self):
        left = tk.Frame(self.tab1, bg=C_BG); left.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        card = self.create_card(left, "START NEW CURE")
        
        # --- PERSONNEL SECTION ---
        f_ppl = tk.Frame(card, bg=C_CARD); f_ppl.pack(fill="x", pady=(0, 10))
        tk.Label(f_ppl, text="Operator:", bg=C_CARD, font=("Segoe UI", 10)).pack(side="left")
        self.combo_op = ttk.Combobox(f_ppl, textvariable=self.var_operator, width=20, font=("Segoe UI", 11))
        self.combo_op.pack(side="left", padx=5)
        
        # --- INPUTS ---
        tk.Label(card, text="Scan Green Tyre (B-ID):", bg=C_CARD, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        e_scan = tk.Entry(card, textvariable=self.var_bid, font=("Segoe UI", 16), bg="#F9E79F")
        e_scan.pack(fill="x", pady=5)
        e_scan.bind("<Return>", self.lookup_green_tyre)
        
        # --- GREEN TYRE PASSPORT DISPLAY ---
        self.f_green_info = tk.Frame(card, bg="#EAFAF1", bd=1, relief="solid", padx=5, pady=5)
        self.f_green_info.pack(fill="x", pady=5)
        
        self.lbl_gt_size = tk.Label(self.f_green_info, text="Size: —", bg="#EAFAF1", font=("Segoe UI", 10, "bold"), fg="#27AE60")
        self.lbl_gt_size.pack(anchor="w")
        
        self.lbl_gt_brand = tk.Label(self.f_green_info, text="Brand/Pattern: —", bg="#EAFAF1", font=("Segoe UI", 9))
        self.lbl_gt_brand.pack(anchor="w")
        
        # NEW: Operator Name instead of "Built By"
        self.lbl_gt_operator = tk.Label(self.f_green_info, text="Operator: —", bg="#EAFAF1", font=("Segoe UI", 9))
        self.lbl_gt_operator.pack(anchor="w")
        
        # NEW: Green Age Label
        self.lbl_gt_age = tk.Label(self.f_green_info, text="Age: —", bg="#EAFAF1", font=("Segoe UI", 9, "bold"), fg="#D35400")
        self.lbl_gt_age.pack(anchor="w")

        self.lbl_gt_weight = tk.Label(self.f_green_info, text="Weight: —", bg="#EAFAF1", font=("Segoe UI", 9, "bold"))
        self.lbl_gt_weight.pack(anchor="w")

        # --- PROCESS DETAILS ---
        tk.Label(card, text="Serial Number (F0...):", bg=C_CARD, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(10,0))
        tk.Entry(card, textvariable=self.var_serial, font=("Segoe UI", 14, "bold"), bg="#D5F5E3").pack(fill="x", pady=2)

        tk.Label(card, text="Loading Press / Location:", bg=C_CARD).pack(anchor="w", pady=(10,0))
        self.combo_press = ttk.Combobox(card, textvariable=self.var_press, font=("Segoe UI", 11))
        self.combo_press['values'] = ["P1-A", "P1-B", "P2-A", "P2-B", "P3-A", "P3-B", "P7-A", "P7-B"]
        self.combo_press.pack(fill="x")
        
        tk.Label(card, text="Mould ID:", bg=C_CARD).pack(anchor="w", pady=(5,0))
        self.combo_mould = ttk.Combobox(card, textvariable=self.var_mould, font=("Segoe UI", 12)); self.combo_mould.pack(fill="x")
        
        f_params = tk.Frame(card, bg=C_CARD); f_params.pack(fill="x", pady=15)
        self.create_param_box(f_params, "Temp (°C)", self.var_temp)
        self.create_param_box(f_params, "Press (Bar)", self.var_pressure)
        self.create_param_box(f_params, "Time (Min)", self.var_time)

        tk.Button(card, text="🔥 START CURING", command=self.start_curing, bg=C_ACCENT, fg="white", font=("Segoe UI", 12, "bold"), pady=10).pack(fill="x", pady=20)

        # RIGHT DASHBOARD
        right = tk.Frame(self.tab1, bg=C_BG); right.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        style = ttk.Style()
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
        style.map("Treeview", background=[('selected', '#3498DB')])

        tk.Label(right, text="🏭 ACTIVE PRESSES", bg=C_BG, fg="white", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        cols_p = ("Press", "Mould", "Size", "Status")
        self.tree_press = ttk.Treeview(right, columns=cols_p, show="headings", height=8)
        for c in cols_p: self.tree_press.heading(c, text=c); self.tree_press.column(c, width=90)
        self.tree_press.tag_configure('overdue', background=C_OVERDUE, foreground='white')
        self.tree_press.tag_configure('normal', background="white", foreground='black')
        self.tree_press.pack(fill="both", expand=True, pady=(0, 10))
        
        # UNLOAD BUTTON
        tk.Button(right, text="❄️ UNLOAD SELECTED PRESS (STOP TIMER)", command=self.unload_press, bg="#2980B9", fg="white", font=("Segoe UI", 11, "bold")).pack(fill="x", pady=5)

        tk.Label(right, text="🔥 OVEN QUEUE", bg=C_BG, fg="orange", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        cols_o = ("Oven", "Mould", "Size", "Status")
        self.tree_oven = ttk.Treeview(right, columns=cols_o, show="headings", height=8)
        self.tree_oven.column("Oven", width=140)
        for c in cols_o: self.tree_oven.heading(c, text=c)
        self.tree_oven.tag_configure('overdue', background=C_OVERDUE, foreground='white')
        self.tree_oven.tag_configure('normal', background="white", foreground='black')
        self.tree_oven.pack(fill="both", expand=True)
        
        tk.Button(right, text="🔄 Refresh Boards", command=self.load_active_cures).pack(fill="x")

    # ================= LOGIC =================
    def lookup_green_tyre(self, event):
        bid = self.var_bid.get().strip().upper()
        if not bid: return
        
        # 1. Check duplicate scan in Curing table
        q_check = "SELECT status, press_no, serial_no FROM pc2_curing WHERE b_id=%s"
        res_check = DBManager.fetch_data(q_check, (bid,))
        if res_check:
            self.lbl_gt_size.config(text=f"❌ PROCESSED: {res_check[0][2]}", fg="red")
            self.var_serial.set("")
            return

        # 2. Fetch Full Data from Building table
        # ADDED 'b.quality' to the query so we can display the grade
        q = """
            SELECT 
                b.tyre_size, b.brand, b.pattern, b.green_tyre_weight, 
                b.press_id, b.daylight, b.created_at, b.operator_id, b.tread_type,
                b.quality 
            FROM pc1_building b
            WHERE b.b_id = %s
        """
        res = DBManager.fetch_data(q, (bid,))
        
        if res:
            r = res[0]
            # Unpack data (Indices match the SELECT order)
            size = r[0]
            brand = r[1]
            pattern = r[2]
            weight = r[3]
            plan_press = r[4]
            daylight = r[5]
            build_time = r[6]
            builder_name = r[7] if r[7] else "Unknown"
            tread = r[8]
            grade = r[9] if r[9] else "STD"  # <--- FIXED: Now 'grade' is defined

            # Calculate Age
            age_str = "0h 0m"
            if build_time:
                diff = datetime.datetime.now() - build_time
                hrs = int(diff.total_seconds() // 3600)
                mins = int((diff.total_seconds() % 3600) // 60)
                age_str = f"{hrs}h {mins}m"

            # Update Labels
            self.lbl_gt_size.config(text=f"✅ Size: {size}", fg="#27AE60")
            # Now 'grade' works because we fetched it
            self.lbl_gt_brand.config(text=f"{brand} | {grade} | {tread}") 
            self.lbl_gt_operator.config(text=f"Operator: {builder_name}")
            self.lbl_gt_age.config(text=f"Age: {age_str}")
            self.lbl_gt_weight.config(text=f"Weight: {weight} kg")

            # Logic: Auto-fill fields based on Press Mode
            press_key = self.normalize_press_id(plan_press)
            mode = self.press_modes.get(press_key, "STD") 

            if mode == "OVEN":
                self.var_time.set("180")
                self.var_pressure.set("N/A")   
                # Ensure simpledialog is imported at top of file: from tkinter import simpledialog
                oven_choice = simpledialog.askstring("Target Oven", f"Plan: {plan_press} -> {press_key} (Oven Mode)\n\nWhich Oven?\n(Enter 1 or 2)", parent=self.root)
                if oven_choice:
                    clean_choice = ''.join(filter(str.isdigit, oven_choice)) 
                    if clean_choice: self.target_oven_id = f"OVEN-{clean_choice}"
            else:
                self.var_time.set("45")
                self.var_pressure.set("150")   
                self.target_oven_id = None

            # Handle Daylight naming (e.g., P01 -> P01-TOP)
            filled_press = str(plan_press)
            if daylight and daylight != "SINGLE": # Added check to avoid 'P01-SINGLE' if simpler naming is preferred
                filled_press += f"-{daylight}"
            self.var_press.set(filled_press)
            
            # Auto-Load Moulds
            q_moulds = "SELECT mould_id FROM pc1_mould_mapping WHERE tyre_size=%s ORDER BY mould_id"
            mould_list = DBManager.fetch_data(q_moulds, (size,))
            if mould_list:
                valid_moulds = [m[0] for m in mould_list]
                self.combo_mould['values'] = valid_moulds
                if len(valid_moulds) > 0: self.combo_mould.set(valid_moulds[0]) 
            
            self.generate_next_serial()
        else:
            self.lbl_gt_size.config(text="❌ ID NOT FOUND", fg="red")
            self.reset_gt_labels() # Helper to clear old data if ID is wrong

    def start_curing(self):
        bid = self.var_bid.get().strip().upper() 
        serial = self.var_serial.get(); 
        selected_press = self.var_press.get().strip(); mould = self.var_mould.get()
        operator = self.var_operator.get()

        if not bid or not serial or not selected_press or not operator: 
            return messagebox.showerror("Error", "Missing Fields/Operator",parent=self.root)

        build_info = DBManager.fetch_data("SELECT green_tyre_weight FROM pc1_building WHERE b_id=%s", (bid,))
        if not build_info: return messagebox.showerror("Error", "B-ID Not Found",parent=self.root)
        g_weight = build_info[0][0] 

        press_key = self.normalize_press_id(selected_press)
        mode = self.press_modes.get(press_key, "STD")
        is_oven_mode = (mode == "OVEN")

        if is_oven_mode:
            if not self.target_oven_id: return messagebox.showerror("Error", "Select Oven ID",parent=self.root)
            real_id_to_save = f"{self.target_oven_id} ({selected_press})"
            try: duration = int(self.var_time.get())
            except: duration = 180
        else:
            real_id_to_save = selected_press
            try: duration = int(self.var_time.get())
            except: duration = 45

        idle_mins = self.calculate_idle_time(real_id_to_save)
        
        # INSERT START TIME (End Time is NULL until Unload)
        q = """INSERT INTO pc2_curing (
                    b_id, serial_no, press_no, mould_no, temperature, 
                    pressure, curing_time_minutes, is_oven, start_time, 
                    idle_time_minutes, status, operator_name, supervisor_name, green_weight
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s, 'CURING', %s, %s, %s)"""
        
        data = (bid, serial, real_id_to_save, mould, self.var_temp.get(), 
                self.var_pressure.get(), duration, is_oven_mode, idle_mins, 
                operator, self.current_supervisor, g_weight)
        
        if DBManager.execute_query(q, data):
            est_unload = datetime.datetime.now() + datetime.timedelta(minutes=5+duration)
            self.print_c_label(serial, f"{real_id_to_save}-{mould} | {est_unload.strftime('%I:%M %p')}")
            self.target_oven_id = None 
            self.load_active_cures(); self.var_bid.set(""); self.var_serial.set("")
            self.lbl_gt_size.config(text="Size: —", fg="#27AE60") # Reset labels
            self.lbl_gt_brand.config(text="Brand/Pattern: —")
            self.lbl_gt_operator.config(text="Operator: —")
            self.lbl_gt_age.config(text="Age: —")
            self.lbl_gt_weight.config(text="Weight: —")
            messagebox.showinfo("Started", f"Curing Started: {real_id_to_save}",parent=self.root)

    def unload_press(self):
        sel_p = self.tree_press.selection()
        sel_o = self.tree_oven.selection()
        
        if not sel_p and not sel_o: return messagebox.showwarning("Select Press", "Select a Running Press to Unload.",parent=self.root)
        
        if sel_p: press_id = self.tree_press.item(sel_p[0])['values'][0]
        else: press_id = self.tree_oven.item(sel_o[0])['values'][0]

        if messagebox.askyesno("Confirm Unload", f"Unload {press_id}?\nThis stops the curing timer.",parent=self.root):
            # CALCULATE OVERCURE AND STOP TIMER
            q = """UPDATE pc2_curing SET status='COOLING', end_time=NOW(), 
                   overcure_minutes = ROUND(EXTRACT(EPOCH FROM (NOW() - start_time))/60 - curing_time_minutes)
                   WHERE press_no=%s AND status='CURING'"""
            if DBManager.execute_query(q, (press_id,)):
                self.load_active_cures()
                messagebox.showinfo("Unloaded", f"{press_id} is now COOLING.",parent=self.root)

    def load_active_cures(self):
        for i in self.tree_press.get_children(): self.tree_press.delete(i)
        for i in self.tree_oven.get_children(): self.tree_oven.delete(i)
        
        # SHOW ACTIVE CURING (Timer counts DOWN into NEGATIVE if late)
        q = """SELECT c.press_no, c.mould_no, b.tyre_size, c.curing_time_minutes, c.is_oven, 
               EXTRACT(EPOCH FROM (NOW() - c.start_time)) 
               FROM pc2_curing c JOIN pc1_building b ON c.b_id = b.b_id WHERE c.status='CURING'"""
        res = DBManager.fetch_data(q)
        if res:
            for r in res:
                press, mould, size, plan_min, is_oven, elapsed_sec = r
                plan_min = int(plan_min) if plan_min else 45
                elapsed_min = int(elapsed_sec / 60)
                remaining = plan_min - elapsed_min
                
                if remaining < 0:
                    status_txt = f"⚠️ OVERDUE ({remaining} min)"
                    row_tag = "overdue"
                else:
                    status_txt = f"{remaining} min"
                    row_tag = "normal"

                if is_oven: self.tree_oven.insert("", "end", values=(press, mould, size, status_txt), tags=(row_tag,))
                else: self.tree_press.insert("", "end", values=(press, mould, size, status_txt), tags=(row_tag,))

    # ================= FIXED SERIAL GENERATOR =================
    def generate_next_serial(self):
        try:
            today = datetime.datetime.now()
            yr = today.strftime("%y"); wk = today.strftime("%U") 
            q = "SELECT serial_no FROM pc2_curing WHERE UPPER(serial_no) LIKE 'F0%' ORDER BY c_id DESC LIMIT 1"
            res = DBManager.fetch_data(q)
            next_num = 1
            if res and res[0][0]:
                match = re.search(r'F0(\d+)', str(res[0][0]).upper())
                if match: next_num = int(match.group(1)) + 1
            self.var_serial.set(f"F0{next_num:05d} {wk}{yr}")
        except: self.var_serial.set(f"F000001 {datetime.datetime.now().strftime('%U%y')}")

    def calculate_idle_time(self, press_no):
        q = "SELECT end_time FROM pc2_curing WHERE press_no=%s AND status='DONE' ORDER BY end_time DESC LIMIT 1"
        res = DBManager.fetch_data(q, (press_no,))
        if res and res[0][0]: return int((datetime.datetime.now() - res[0][0]).total_seconds() / 60)
        return 0 

    def create_card(self, parent, title):
        f = tk.Frame(parent, bg=C_CARD, bd=1, relief="solid", padx=10, pady=10); f.pack(fill="x", pady=5)
        tk.Label(f, text=title, font=("Segoe UI", 11, "bold"), bg=C_CARD, fg=C_BG).pack(anchor="w"); return f
    def create_param_box(self, parent, label, var):
        f = tk.Frame(parent, bg=C_CARD); f.pack(side="left", padx=5)
        tk.Label(f, text=label, bg=C_CARD, font=("Segoe UI", 9)).pack(anchor="w")
        tk.Entry(f, textvariable=var, width=8, font=("Segoe UI", 11)).pack()

    def print_c_label(self, serial, top_text):
        epl = f'N\nq464\nQ200,24\nA40,30,0,3,1,1,N,"{top_text}"\nB20,60,0,1,2,5,90,B,"{serial}"\nP1\n'
        try:
            if platform.system() == "Linux":
                with open(LINUX_PRINTER_PATH, "wb") as f: f.write(epl.encode())
        except: pass
    
    # --- TAB 2: QC ---
    def build_tab2(self):
        card = self.create_card(self.tab2, "POST-CURING QC & WEIGHT")
        card.pack(fill="both", expand=True, padx=100, pady=20)
        tk.Label(card, text="1. Scan Cured Tyre (Serial No):", bg=C_CARD, font=("Segoe UI", 11, "bold")).pack(anchor="w")
        e_qc = tk.Entry(card, textvariable=self.var_cid, font=("Segoe UI", 16), bg="#D6EAF8"); e_qc.pack(fill="x", pady=5); e_qc.bind("<Return>", self.lookup_cured_tyre)
        self.lbl_qc_info = tk.Label(card, text="Waiting...", bg=C_CARD, font=("Segoe UI", 10)); self.lbl_qc_info.pack(pady=10)
        f_wt = tk.Frame(card, bg=C_CARD); f_wt.pack(fill="x", pady=10)
        w_box = tk.Frame(f_wt, bg=C_CARD); w_box.pack(side="left", fill="x", expand=True)
        tk.Label(w_box, text="Final Weight (Kg):", bg=C_CARD).pack(anchor="w")
        e_wt = tk.Entry(w_box, textvariable=self.var_final_wt, font=("Segoe UI", 14), bg="#EAFAF1"); e_wt.pack(fill="x"); e_wt.bind("<KeyRelease>", self.calc_flash)
        f_res = tk.Frame(f_wt, bg=C_CARD); f_res.pack(side="left", fill="x", expand=True, padx=10)
        tk.Label(f_res, text="Flash Waste:", bg=C_CARD).pack(anchor="w"); tk.Label(f_res, textvariable=self.var_flash, font=("Segoe UI", 14, "bold"), fg=C_WARN, bg=C_CARD).pack(anchor="w")
        tk.Label(card, text="Visual Inspection:", bg=C_CARD, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(15,5))
        f_btns = tk.Frame(card, bg=C_CARD); f_btns.pack(fill="x")
        modes = [("✅ OK", "OK", C_SUCCESS), ("⚠️ MILD DEFECT", "MILD", C_WARN), ("❌ REJECT", "REJECT", C_ACCENT)]
        for txt, val, col in modes: tk.Radiobutton(f_btns, text=txt, variable=self.var_qc_status, value=val, bg=C_CARD, fg=col, font=("Segoe UI", 10, "bold")).pack(side="left", padx=10)
        tk.Label(card, text="Remarks / Defects:", bg=C_CARD).pack(anchor="w", pady=(10,0)); tk.Entry(card, textvariable=self.var_qc_remarks, width=50).pack(fill="x")
        tk.Button(card, text="💾 SAVE QC & FINISH", command=self.save_qc, bg=C_SUCCESS, fg="white", font=("Segoe UI", 12, "bold"), pady=10).pack(fill="x", pady=20)

    def lookup_cured_tyre(self, event):
        sid = self.var_cid.get().strip()
        # Allows scanning COOLING or CURING (if forgotten unload) tyres
        q = "SELECT c.b_id, b.green_tyre_weight, c.status FROM pc2_curing c JOIN pc1_building b ON c.b_id = b.b_id WHERE c.serial_no=%s OR c.b_id=%s"
        res = DBManager.fetch_data(q, (sid, sid))
        if res:
            self.green_weight = float(res[0][1]) if res[0][1] else 0.0
            status = res[0][2]
            msg = f"✅ Found: {status}"
            if status == 'COOLING': msg += " (Ready for QC)"
            elif status == 'CURING': msg += " (⚠️ Not Unloaded Yet)"
            elif status == 'DONE': msg += " (⚠️ Already QC'd)"
            self.lbl_qc_info.config(text=msg, fg=C_SUCCESS)
        else: self.lbl_qc_info.config(text="❌ Not Found", fg=C_ACCENT)

    def calc_flash(self, event):
        try:
            final = float(self.var_final_wt.get())
            if self.green_weight > 0:
                flash = self.green_weight - final
                pct = (flash/self.green_weight)*100
                self.var_flash.set(f"{flash:.2f} kg ({pct:.1f}%)")
        except: pass

    def save_qc(self):
        sid = self.var_cid.get(); wt = self.var_final_wt.get(); status = self.var_qc_status.get()
        if not sid: return messagebox.showerror("Error", "Scan Serial Number first!",parent=self.root)
        if status == "REJECT": wt = 0.0; flash_val = 0.0
        else:
            if not wt: return messagebox.showerror("Error", "Enter Final Weight!",parent=self.root)
            try: flash_val = self.var_flash.get().split(" ")[0]
            except: flash_val = 0.0
        
        # QC Logic: Does NOT touch end_time (because Unload did that). 
        # Only updates QC fields and sets status to DONE.
        q = """UPDATE pc2_curing SET status='DONE', qc_time=NOW(), final_cured_weight=%s, flash_waste=%s, visual_qc_status=%s, visual_qc_remarks=%s WHERE serial_no=%s OR b_id=%s"""
        if DBManager.execute_query(q, (wt, flash_val, status, self.var_qc_remarks.get(), sid, sid)):
            messagebox.showinfo("Success", "QC Saved!"); self.var_cid.set(""); self.var_final_wt.set(""); self.load_active_cures()

    # --- TAB 3: REPORTS ---
    def build_tab3(self):
        f_ctrl = tk.Frame(self.tab3, bg=C_HISTORY, pady=15, padx=15); f_ctrl.pack(side="top", fill="x")
        tk.Label(f_ctrl, text="📅 Date:", bg=C_HISTORY, fg="white").pack(side="left")
        tk.Entry(f_ctrl, textvariable=self.hist_date, width=12).pack(side="left", padx=5)
        tk.Label(f_ctrl, text="🕒 Shift:", bg=C_HISTORY, fg="white").pack(side="left", padx=(20,5))
        self.combo_shift = ttk.Combobox(f_ctrl, textvariable=self.hist_shift, values=["ALL", "Shift A", "Shift B", "Shift C"], width=15); self.combo_shift.pack(side="left", padx=5)
        tk.Button(f_ctrl, text="🔍 VIEW", command=self.load_history, bg="#2980B9", fg="white").pack(side="left", padx=20)
        tk.Button(f_ctrl, text="📥 CSV", command=self.export_report, bg="#27AE60", fg="white").pack(side="right", padx=10)
        
        f_act = tk.Frame(self.tab3, bg=C_HISTORY, pady=10); f_act.pack(side="bottom", fill="x", padx=10)
        tk.Button(f_act, text="🖨️ REPRINT LAST", command=self.reprint_last, bg=C_ACCENT, fg="white").pack(side="right", padx=10)
        tk.Button(f_act, text="🖨️ REPRINT SEL", command=self.reprint_selected, bg=C_WARN, fg="white").pack(side="right", padx=10)

        cols = ("Serial", "Press", "Mould", "Size", "Start", "End", "Overcure", "QC")
        self.hist_tree = ttk.Treeview(self.tab3, columns=cols, show="headings", height=20)
        for c in cols: self.hist_tree.heading(c, text=c); self.hist_tree.column(c, width=100)
        self.hist_tree.pack(side="left", fill="both", expand=True, padx=10, pady=5)

    def load_history(self):
        for i in self.hist_tree.get_children(): self.hist_tree.delete(i)
        start_dt, end_dt = self.get_shift_times(self.hist_date.get(), self.hist_shift.get())
        if not start_dt: return
        q = """SELECT c.serial_no, c.press_no, c.mould_no, b.tyre_size, to_char(c.start_time, 'HH12:MI PM'), to_char(c.end_time, 'HH12:MI PM'), c.overcure_minutes || ' min', c.visual_qc_status FROM pc2_curing c JOIN pc1_building b ON c.b_id = b.b_id WHERE c.start_time >= %s AND c.start_time < %s ORDER BY c.start_time DESC"""
        res = DBManager.fetch_data(q, (start_dt, end_dt))
        if res:
            for r in res: self.hist_tree.insert("", "end", values=r)

    def export_report(self):
        start_dt, end_dt = self.get_shift_times(self.hist_date.get(), self.hist_shift.get())
        if not start_dt: return
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if not path: return
        q = """SELECT c.serial_no, c.b_id, b.tyre_size, c.press_no, c.mould_no, c.start_time, c.end_time, c.curing_time_minutes, c.overcure_minutes, c.final_cured_weight, c.flash_waste, c.visual_qc_status, c.operator_name FROM pc2_curing c JOIN pc1_building b ON c.b_id = b.b_id WHERE c.start_time >= %s AND c.start_time < %s ORDER BY c.start_time ASC"""
        res = DBManager.fetch_data(q, (start_dt, end_dt))
        try:
            with open(path, 'w', newline='') as f:
                writer = csv.writer(f); writer.writerow(["SERIAL", "BID", "SIZE", "PRESS", "MOULD", "START", "END", "PLAN", "OVERCURE", "WEIGHT", "FLASH", "QC", "OP"])
                if res: writer.writerows(res)
            messagebox.showinfo("Success", "Report Saved",parent=self.root)
        except Exception as e: messagebox.showerror("Error", str(e),parent=self.root)

    def reprint_selected(self):
        sel = self.hist_tree.selection()
        if sel:
            v = self.hist_tree.item(sel[0])['values']
            self.print_c_label(v[0], f"{v[1]}-{v[2]}")

    def reprint_last(self):
        res = DBManager.fetch_data("SELECT serial_no, press_no, mould_no FROM pc2_curing ORDER BY start_time DESC LIMIT 1")
        if res: self.print_c_label(res[0][0], f"{res[0][1]}-{res[0][2]}")

    def get_shift_times(self, d_str, s_name):
        try: dt = datetime.datetime.strptime(d_str, "%Y-%m-%d")
        except: return None, None
        if "Shift A" in s_name: return dt.replace(hour=7), dt.replace(hour=15)
        if "Shift B" in s_name: return dt.replace(hour=15), dt.replace(hour=23)
        if "Shift C" in s_name: return dt.replace(hour=23), (dt+datetime.timedelta(days=1)).replace(hour=7)
        return dt.replace(hour=7), (dt+datetime.timedelta(days=1)).replace(hour=7)
        
    def reset_gt_labels(self):
        # Safely tries to clear the screen if an invalid Green Tyre is scanned
        try:
            # Update the status label if it exists
            if hasattr(self, 'lbl_gt_info'):
                self.lbl_gt_info.config(text="❌ TYRE NOT FOUND OR ALREADY CURED", fg="#E74C3C")
            elif hasattr(self, 'lbl_gt_status'):
                self.lbl_gt_status.config(text="❌ TYRE NOT FOUND", fg="#E74C3C")
                
            # Clear standard variables if they exist in your UI
            if hasattr(self, 'var_gt_size'): self.var_gt_size.set("—")
            if hasattr(self, 'var_gt_brand'): self.var_gt_brand.set("—")
            if hasattr(self, 'var_gt_quality'): self.var_gt_quality.set("—")
            if hasattr(self, 'var_gt_weight'): self.var_gt_weight.set("—")
        except Exception as e:
            print(f"Reset labels ignored: {e}")

if __name__ == "__main__":
    root = tk.Tk(); app = CuringApp(root); root.mainloop()