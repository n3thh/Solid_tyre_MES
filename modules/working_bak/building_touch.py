import tkinter as tk
from tkinter import messagebox, ttk
import datetime
import platform
from db_manager import DBManager

# --- UI CONSTANTS ---
C_BG       = "#1A1A2E"
C_SIDEBAR  = "#16213E"
C_IDLE     = "#D5DBDB"
C_SELECTED = "#E74C3C"
C_PROCEED  = "#27AE60"
C_CARD_BG  = "#0F3460"
C_WARN     = "#E67E22"
LINUX_PRINTER_PATH = "/dev/usb/lp4"

PAGE_MACHINE = "MACHINE"
PAGE_BATCHES = "BATCHES"
PAGE_FINISH  = "FINISH"
PAGE_UPDATE  = "UPDATE"


class PC1TouchApp:
    def __init__(self, root, current_user="OPERATOR"):
        self.root         = root
        self.current_user = current_user
        self.current_page = PAGE_MACHINE

        # --- State ---
        self.sel_press    = ""
        self.sel_daylight = ""
        self.plan_data = {
            "size": "—", "core": "—", "brand": "—", "quality": "—", "pattern": "—", "mould": "—",
            "target_wt": 0.0, "type": "—", "is_pob": False, "order_id": None
        }
        self.targets = {"core": 0.0, "mid": 0.0, "ct": 0.0,
                        "gum": 0.0, "tread": 0.0, "bead": "—"}

        self.selected_core_batches  = []
        self.selected_mid_batches   = []
        self.selected_tread_batches = []
        self.selected_gum_batches   = []

        # Variables for user input
        self.sel_tread_type = tk.StringVar(value="VT001")
        self.weight_var     = tk.StringVar(value="")
        self.var_ms_rim_wt  = tk.StringVar(value="0")
        self.upd_bid_var    = tk.StringVar()
        
        # Track which entry the numpad should type into
        self.active_entry_var = self.weight_var 

        # --- Single DB fetch at startup ---
        self._press_list  = []
        self._batch_cache = {}
        self._batch_cache_ts = {}
        self._CACHE_TTL = 300

        self._load_press_list()
        self._prefetch_all_batches()

        self._build_ui()
        self.render_page_1()

    # =========================================================
    # DATA LOADING & FILTERING
    # =========================================================
    def _load_press_list(self):
        res = DBManager.fetch_data(
            "SELECT press_id, daylight FROM press_master WHERE status='ACTIVE' ORDER BY press_id, daylight"
        )
        self._press_list = [(r[0], r[1]) for r in res] if res else []

    def _prefetch_all_batches(self):
        res = DBManager.fetch_data(
            "SELECT material_type, batch_no FROM raw_material_qc WHERE status='APPROVED' ORDER BY batch_no DESC"
        )
        grouped = {}
        for mat, batch in (res or []):
            grouped.setdefault(mat.upper(), []).append(batch)
        now = datetime.datetime.now()
        for mat, batches in grouped.items():
            self._batch_cache[mat]    = batches
            self._batch_cache_ts[mat] = now

    def _fetch_batches(self, material_type):
        """Optimized SQL: Core (24h) | Others (Active status only)."""
        key = material_type.upper()
        if "CORE" in key:
            q = """SELECT batch_no FROM raw_material_qc 
                   WHERE material_type ILIKE %s AND status = 'APPROVED'
                     AND updated_at > NOW() - INTERVAL '24 hours'
                   ORDER BY updated_at DESC LIMIT 30"""
        else:
            q = """SELECT batch_no FROM raw_material_qc 
                   WHERE material_type ILIKE %s AND status = 'APPROVED' AND is_active = TRUE
                   ORDER BY updated_at DESC LIMIT 30"""
        
        res = DBManager.fetch_data(q, (f"%{material_type}%",))
        return [r[0].strip() for r in res] if res else []

    # =========================================================
    # UI SHELL & SIDEBAR
    # =========================================================
    def _build_ui(self):
        hdr = tk.Frame(self.root, bg=C_SIDEBAR, height=70)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"🏗️ PC1 BUILDING | {self.current_user} | {self._get_shift()}", 
                 fg="white", bg=C_SIDEBAR, font=("Segoe UI", 16, "bold")).pack(side="left", padx=25)
        
        self.btn_bar = tk.Frame(self.root, bg=C_BG, height=110) 
        self.btn_bar.pack(fill="x", side="bottom")
        self.btn_bar.pack_propagate(False)

        body = tk.Frame(self.root, bg=C_BG)
        body.pack(fill="both", expand=True)

        self._sidebar = tk.Frame(body, bg=C_CARD_BG, width=420)
        self._sidebar.pack(side="left", fill="y", padx=(20, 10), pady=20)
        self._sidebar.pack_propagate(False)

        self.workspace = tk.Frame(body, bg=C_BG)
        self.workspace.pack(side="left", fill="both", expand=True, padx=(0, 20), pady=20)
        self._build_sidebar_widgets()

    def _build_sidebar_widgets(self):
        s = self._sidebar
        self._sb_title = tk.Label(s, text="", fg="#E94560", bg=C_CARD_BG, font=("Segoe UI", 18, "bold"))
        self._sb_title.pack(pady=10)

        self._sb_btn_home = tk.Button(s, text="🏠 HOME / RESET", bg="#2980B9", fg="white", font=("Segoe UI", 12, "bold"), 
                                      command=self.reset_workflow, height=2)

        info = tk.Frame(s, bg=C_CARD_BG)
        info.pack(fill="x", padx=20, pady=5)
        self._sb_size = tk.Label(info, text="", bg=C_CARD_BG, fg="white", font=("Segoe UI", 14, "bold"))
        self._sb_size.pack(anchor="w")
        self._sb_grade = tk.Label(info, text="", bg=C_CARD_BG, fg="white", font=("Segoe UI", 14, "bold"))
        self._sb_grade.pack(anchor="w")

        f_tgt = tk.Frame(s, bg="#16213E", padx=15, pady=15)
        f_tgt.pack(fill="x", padx=20, pady=10)
        self._tgt_labels = {}
        for lbl, key in [("CORE","core"),("MIDDLE","mid"),("C+T","ct"),("TREAD","tread"),("GUM","gum")]:
            row = tk.Frame(f_tgt, bg="#16213E"); row.pack(fill="x")
            tk.Label(row, text=lbl, bg="#16213E", fg="#BDC3C7", font=("Segoe UI", 10, "bold")).pack(side="left")
            lv = tk.Label(row, text="0.00", bg="#16213E", fg="white", font=("Segoe UI", 18, "bold"))
            lv.pack(side="right")
            self._tgt_labels[key] = lv

        self._sb_target_wt = tk.Label(s, text="", bg=C_CARD_BG, fg="#27AE60", font=("Segoe UI", 24, "bold"))
        self._sb_target_wt.pack(pady=10)

    def _refresh_sidebar(self, title):
        self._sb_title.config(text=title)
        self._sb_size.config(text=f"SIZE: {self.plan_data['size']}")
        self._sb_grade.config(text=f"GRADE: {self.plan_data['quality']}")
        self._sb_target_wt.config(text=f"TARGET: {self.plan_data['target_wt']:.2f} KG")
        for key, lv in self._tgt_labels.items():
            lv.config(text=f"{self.targets[key]:.2f}")

    # =========================================================
    # PAGE 1 — MACHINE SELECTION (BOT/TOP Standardized)
    # =========================================================
    def render_page_1(self):
        self.current_page = PAGE_MACHINE
        self._clear_workspace(); self._clear_btn_bar()
        self._refresh_sidebar("STEP 1: MACHINE")
        canvas, right = self._make_scrollable_workspace()

        tk.Label(right, text="SELECT PRESS:", fg="white", bg=C_BG, font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=20)
        p_grid = tk.Frame(right, bg=C_BG); p_grid.pack(pady=10)
        for i, pid in enumerate(self._get_unique_presses()):
            tk.Button(p_grid, text=pid, font=("Segoe UI", 14, "bold"), width=8, height=3,
                bg=C_SELECTED if self.sel_press == pid else C_IDLE,
                command=lambda p=pid: self.select_press(p)).grid(row=i//4, column=i%4, padx=10, pady=10)

        if self.sel_press:
            tk.Label(right, text="SELECT DAYLIGHT:", fg="white", bg=C_BG, font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=20)
            dl_row = tk.Frame(right, bg=C_BG); dl_row.pack(pady=10)
            # Use Standardized DB naming: BOT instead of BOTTOM
            for dl in ["SINGLE", "TOP", "BOT"]:
                tk.Button(dl_row, text=dl, font=("Segoe UI", 14, "bold"), width=12, height=2,
                          bg=C_SELECTED if self.sel_daylight == dl else C_IDLE, 
                          command=lambda d=dl: self.select_daylight(d)).pack(side="left", padx=10)

        if self.plan_data["size"] != "—":
            card_color = "#5B2C6F" if self.plan_data["is_pob"] else "#0F3460"
            f_plan = tk.Frame(right, bg=card_color, padx=15, pady=15)
            f_plan.pack(fill="x", padx=20, pady=10)
            tk.Label(f_plan, text=f"{self.plan_data['size']} | Pattern: {self.plan_data['pattern']}", 
                     fg="white", bg=card_color, font=("Segoe UI", 12, "bold")).pack(anchor="w")
            self._add_btn("NEXT: BATCHES ➔", self.render_page_2)

    # =========================================================
    # PAGE 2 — BATCH SELECTION (Gatekeeper logic)
    # =========================================================
    def render_page_2(self):
        self.current_page = PAGE_BATCHES
        self._clear_workspace(); self._clear_btn_bar()
        self._refresh_sidebar("STEP 2: BATCHES")
        canvas, right = self._make_scrollable_workspace()

        row = 0
        tk.Label(right, text="CORE BATCH(ES):", fg="white", bg=C_BG, font=("Segoe UI", 13, "bold")).grid(row=row, column=0, sticky="w", padx=15)
        row += 1
        row = self._render_tile_grid(right, "CORE", self.selected_core_batches, row, cols=6)

        tk.Label(right, text="MIDDLE LAYER(S):", fg="white", bg=C_BG, font=("Segoe UI", 13, "bold")).grid(row=row, column=0, sticky="w", padx=15, pady=(15,0))
        row += 1
        row = self._render_tile_grid(right, "MID", self.selected_mid_batches, row, cols=6)

        if self.plan_data["is_pob"]:
            tk.Label(right, text="GUM BATCH (POB MANDATORY):", fg="#E74C3C", bg=C_BG, font=("Segoe UI", 13, "bold")).grid(row=row, column=0, sticky="w", padx=15, pady=(15,0))
            row += 1
            row = self._render_tile_grid(right, "GUM", self.selected_gum_batches, row, cols=6)

        self._add_btn("NEXT: FINISH ➔", self.validate_page_2_and_next)

    def validate_page_2_and_next(self):
        """Enforces Core (Standard) or Gum (POB) mandatory picking."""
        if self.plan_data.get("is_pob"):
            if not self.selected_gum_batches:
                return messagebox.showwarning("Incomplete", "POB Tyre requires at least one GUM batch.")
        else:
            if not self.selected_core_batches:
                return messagebox.showwarning("Incomplete", "Standard Tyre requires at least one CORE batch.")
        self.render_page_3()

    # =========================================================
    # PAGE 3 — FINISH (Numpad focus & combined weight)
    # =========================================================
    def render_page_3(self):
        self.current_page = PAGE_FINISH
        self._clear_workspace(); self._clear_btn_bar()
        self._refresh_sidebar("STEP 3: FINISH")
        canvas, right = self._make_scrollable_workspace()

        # Tread selection
        t_f = tk.Frame(right, bg=C_BG); t_f.pack(fill="x", pady=10)
        for t in ["VT001", "VT002", "VT003", "NMW"]:
            tk.Button(t_f, text=t, font=("Segoe UI", 11, "bold"), width=8,
                bg=C_SELECTED if self.sel_tread_type.get() == t else C_IDLE,
                command=lambda x=t: [self.sel_tread_type.set(x), self.render_page_3()]).pack(side="left", padx=5)
        
        tb_f = tk.Frame(right, bg=C_BG); tb_f.pack(fill="x")
        self._render_tile_grid(tb_f, self.sel_tread_type.get(), self.selected_tread_batches, 0, 5)

        # POB Specific: Rim Weight
        if self.plan_data["is_pob"]:
            pob_f = tk.Frame(right, bg="#2E1A3E", padx=15, pady=10)
            pob_f.pack(fill="x", padx=20, pady=10)
            tk.Label(pob_f, text="MS RIM WEIGHT (KG):", fg="white", bg="#2E1A3E", font=("Segoe UI", 12, "bold")).pack(side="left")
            rim_ent = tk.Entry(pob_f, textvariable=self.var_ms_rim_wt, font=("Segoe UI", 24, "bold"), width=8, justify="center", bg="#F5EEF8")
            rim_ent.pack(side="left", padx=20)
            rim_ent.bind("<FocusIn>", lambda e: setattr(self, 'active_entry_var', self.var_ms_rim_wt))

        # Main Weight
        f_entry = tk.Frame(right, bg=C_BG); f_entry.pack(pady=10)
        tk.Label(f_entry, text="FINAL TYRE WEIGHT (KG):", fg="#BDC3C7", bg=C_BG, font=("Segoe UI", 10, "bold")).pack()
        wt_ent = tk.Entry(f_entry, textvariable=self.weight_var, font=("Segoe UI", 36, "bold"), width=8, justify="center", bg="#D5F5E3")
        wt_ent.pack()
        wt_ent.bind("<FocusIn>", lambda e: setattr(self, 'active_entry_var', self.weight_var))

        # Numpad
        n_grid = tk.Frame(right, bg=C_BG); n_grid.pack()
        for i, k in enumerate(['7','8','9','4','5','6','1','2','3','0','.','CLR']):
            tk.Button(n_grid, text=k, font=("Segoe UI", 16, "bold"), width=5, height=1, bg="#34495E", fg="white",
                      command=lambda x=k: self.numpad_press(x)).grid(row=i//3, column=i%3, padx=3, pady=3)

        self._complete_btn = self._add_btn("✅ BUILD COMPLETE", self.finalize_submission, bg="#2ECC71", width=20)
        self._update_complete_button_state()

    # =========================================================
    # LOGIC HELPERS
    # =========================================================
    def numpad_press(self, key):
        target = self.active_entry_var
        if key == 'CLR': target.set("")
        else:
            cur = target.get()
            if key == '.' and '.' in cur: return
            target.set(cur + key)
        self._update_complete_button_state()

    def _update_complete_button_state(self):
        """Mandatory Tread + Weight (+ Rim Weight if POB)."""
        is_pob = self.plan_data.get("is_pob", False)
        has_tread = len(self.selected_tread_batches) > 0
        try: has_weight = float(self.weight_var.get()) > 0
        except: has_weight = False
        
        rim_ok = True
        if is_pob:
            try: rim_ok = float(self.var_ms_rim_wt.get()) > 0
            except: rim_ok = False

        state = "normal" if (has_tread and has_weight and rim_ok) else "disabled"
        self._complete_btn.config(state=state, bg=C_PROCEED if state=="normal" else "#555")

    def fetch_plan_details(self):
        """Unified fetch with 'BOT' and POB logic."""
        res = DBManager.fetch_data(
            "SELECT tyre_size, brand, pattern, quality, mould_id_marks, type, tyre_weight, order_id "
            "FROM production_plan WHERE TRIM(press_id)=%s AND TRIM(daylight)=%s LIMIT 1",
            (self.sel_press, self.sel_daylight)
        )
        if res:
            r = res[0]
            self.plan_data.update({
                "size": r[0], "brand": r[1], "pattern": r[2], "quality": r[3], "mould": r[4],
                "type": r[5], "target_wt": float(r[6] or 0.0), "is_pob": "POB" in str(r[5]).upper(),
                "order_id": r[7]
            })
            self.calculate_material_targets()
            self.render_page_1()

    def calculate_material_targets(self):
        grade = self.plan_data["quality"]; size = self.plan_data["size"]
        spec = DBManager.fetch_data("SELECT core_pct, mid_pct, ct_pct, tread_pct, gum_pct FROM tyre_specs WHERE grade=%s", (grade,))
        
        b_wt, b_cnt = 0.0, 0
        if self.plan_data["is_pob"]: self.targets['bead'] = "N/A (POB)"
        else:
            res_b = DBManager.fetch_data("SELECT bead_count, weight_per_bead FROM bead_master WHERE UPPER(tyre_size)=%s LIMIT 1", (str(size).upper(),))
            if res_b: b_cnt, b_wt = int(res_b[0][0]), float(res_b[0][1])

        net = self.plan_data["target_wt"] - (b_wt * b_cnt)
        if spec and net > 0:
            s = spec[0]
            for i, key in enumerate(['core','mid','ct','tread','gum']):
                self.targets[key] = net * (float(s[i] or 0) / 100)

    def finalize_submission(self):
        bid = self._get_next_bid()
        ms_wt = float(self.var_ms_rim_wt.get() or 0) if self.plan_data["is_pob"] else 0
        actual = float(self.weight_var.get())
        
        # 15% Tolerance check
        target = self.plan_data["target_wt"] + ms_wt
        if not (target * 0.85 <= actual <= target * 1.15):
            if not messagebox.askyesno("Weight Alert", f"Weight {actual}kg is outside ±15% tolerance of {target}kg. Save anyway?"):
                return

        q = """INSERT INTO pc1_building (b_id, press_id, daylight, tyre_size, quality, 
               batch_core, batch_mid, batch_tread, batch_gum, ms_rim_weight, green_tyre_weight, 
               is_pob, status, birth_time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'COMPLETED',NOW())"""
        
        data = (bid, self.sel_press, self.sel_daylight, self.plan_data["size"], self.plan_data["quality"],
                ",".join(self.selected_core_batches), ",".join(self.selected_mid_batches),
                ",".join(self.selected_tread_batches), ",".join(self.selected_gum_batches),
                ms_wt, actual, self.plan_data["is_pob"])

        if DBManager.execute_query(q, data):
            self.print_label(bid, self.plan_data["size"], self.sel_press, self.sel_daylight)
            self.reset_workflow()
            messagebox.showinfo("Success", f"Tyre {bid} saved.")

    def reset_workflow(self):
        self.selected_core_batches, self.selected_mid_batches, self.selected_tread_batches, self.selected_gum_batches = [],[],[],[]
        self.weight_var.set(""); self.var_ms_rim_wt.set("0")
        self.sel_press = ""; self.sel_daylight = ""
        self.render_page_1()

    # =========================================================
    # SYSTEM UTILS
    # =========================================================
    def _render_tile_grid(self, parent, material_type, selection_list, start_row, cols):
        batches = self._fetch_batches(material_type)
        if not batches:
            tk.Label(parent, text=f"No {material_type} batches", fg="orange", bg=C_BG).grid(row=start_row, column=0)
            return start_row + 1
        
        btn_refs = {}
        def toggle(b_no):
            if b_no in selection_list: selection_list.remove(b_no)
            else: selection_list.append(b_no)
            for bn, btn in btn_refs.items():
                btn.config(bg=C_SELECTED if bn in selection_list else C_IDLE)
            self._refresh_sidebar(self._sb_title.cget("text"))
            if self.current_page == PAGE_FINISH: self._update_complete_button_state()

        for i, b_no in enumerate(batches):
            btn = tk.Button(parent, text=b_no, font=("Segoe UI", 10, "bold"), width=12, height=2,
                            bg=C_SELECTED if b_no in selection_list else C_IDLE, 
                            command=lambda b=b_no: toggle(b))
            btn.grid(row=start_row + i//cols, column=i%cols, padx=3, pady=3)
            btn_refs[b_no] = btn
        return start_row + (len(batches) + cols - 1) // cols

    def _make_scrollable_workspace(self):
        canvas = tk.Canvas(self.workspace, bg=C_BG, highlightthickness=0)
        v_scroll = ttk.Scrollbar(self.workspace, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=C_BG)
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")
        return canvas, scroll_frame

    def select_press(self, p_id): self.sel_press = p_id; self.render_page_1()
    def select_daylight(self, dl): self.sel_daylight = dl; self.fetch_plan_details()
    def _get_unique_presses(self): return sorted(list(set([p[0] for p in self._press_list])))
    def _get_daylights_for_press(self, p_id): return [p[1] for p in self._press_list if p[0] == p_id]
    def _get_shift(self): return "A" if 7 <= datetime.datetime.now().hour < 15 else ("B" if 15 <= datetime.datetime.now().hour < 23 else "C")
    def _clear_workspace(self): [w.destroy() for w in self.workspace.winfo_children()]
    def _clear_btn_bar(self): [w.destroy() for w in self.btn_bar.winfo_children()]
    def _get_next_bid(self):
        res = DBManager.fetch_data("SELECT b_id FROM pc1_building ORDER BY created_at DESC LIMIT 1")
        try: return f"B-{int(res[0][0].split('-')[1]) + 1:06d}" if res else "B-000001"
        except: return "B-000001"
    def print_label(self, bid, size, press, daylight):
        epl = f'N\nq464\nQ200,24\nA47,30,0,3,1,1,N,"{size} | {press}-{daylight}"\nB60,70,0,1,2,5,90,B,"{bid}"\nP1\n'
        try:
            if platform.system() == "Linux":
                with open(LINUX_PRINTER_PATH, "wb") as f: f.write(epl.encode())
        except: pass

if __name__ == "__main__":
    root = tk.Tk()
    root.title("PC1 Building Station")
    root.geometry("1200x800")
    app = PC1TouchApp(root)
    root.mainloop()