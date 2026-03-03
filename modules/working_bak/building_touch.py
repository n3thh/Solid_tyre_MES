import tkinter as tk
from tkinter import messagebox, ttk
import datetime
import platform
from db_manager import DBManager
import csv
import os
import json

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
CONFIG_FILE = "press_config.json"
C_OVEN = "#F39C12"   # Orange for oven‑capable presses


class PC1TouchApp:
    def __init__(self, root, current_user="OPERATOR"):
        self.root         = root
        self.current_user = current_user
        self.current_page = PAGE_MACHINE

        self.var_ms_rim_wt = tk.StringVar(value="0")
        self.weight_var     = tk.StringVar(value="")
        self.selected_gum_batches = [] # To store bonding gum
        self.active_entry_var = self.weight_var         # Default focus for numpad

        

        self.selected_core_batches  = []
        self.selected_mid_batches   = []
        self.selected_tread_batches = []
        self.selected_gum_batches   = []

        # --- State ---
        self.sel_press    = ""
        self.sel_daylight = ""
        self.plan_data = {
            "size": "—", "core": "—", "brand": "—", "quality": "—",
            "target_wt": 0.0, "type": "—", "is_pob": False, "pi_number": None
        }
        self.targets = {"core": 0.0, "mid": 0.0, "ct": 0.0,
                        "gum": 0.0, "tread": 0.0, "bead": "—"}

        self.sel_tread_type = tk.StringVar(value="VT001")
        
        self.upd_bid_var    = tk.StringVar()

        # --- Single DB fetch at startup (no repeated queries) ---
        self._press_list  = []   # [(press_id, daylight), ...]
        self._batch_cache = {}   # {material_type: [batch_no, ...]}
        self._batch_cache_ts = {}  # {material_type: datetime}
        self._CACHE_TTL = 300    # seconds

        self._load_press_list()
        self._prefetch_all_batches()   # <-- fetch ALL batch types once at startup

        self._build_ui()
        self.render_page_1()
        self.last_print_data = None # Stores (bid, size, press, daylight)


    def load_config(self):
        default = {"P1": "STD", "P2": "STD", "P3": "STD", "P7": "STD"}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return default    

        
    # =========================================================
    # STARTUP DATA LOADING
    # =========================================================
    def _load_press_list(self):
        res = DBManager.fetch_data(
            "SELECT press_id, daylight FROM press_master "
            "WHERE status='ACTIVE' ORDER BY press_id, daylight"
        )
        self._press_list = [(r[0], r[1]) for r in res] if res else []

    def _prefetch_all_batches(self):
        """One query to load all approved batches grouped by type."""
        res = DBManager.fetch_data(
            "SELECT material_type, batch_no FROM raw_material_qc "
            "WHERE status='APPROVED' ORDER BY batch_no DESC"
        )
        grouped = {}
        for mat, batch in (res or []):
            grouped.setdefault(mat.upper(), []).append(batch)
        now = datetime.datetime.now()
        for mat, batches in grouped.items():
            self._batch_cache[mat]    = batches
            self._batch_cache_ts[mat] = now

    def _fetch_batches(self, material_type):
        """
        Final Production Version:
        - Instant performance.
        - Core is strictly 24h.
        - Others are Active-only.
        - No code changes needed for 'Fresh Starts'.
        """
        key = material_type.upper()
        
        # CORE Logic: Strictly the last 24 hours
        if "CORE" in key:
            q = """
                SELECT batch_no FROM raw_material_qc 
                WHERE material_type ILIKE %s 
                  AND status = 'APPROVED'
                  AND updated_at > NOW() - INTERVAL '24 hours'
                ORDER BY updated_at DESC LIMIT 30
            """
        else:
            # ALL OTHER MATERIALS: Active status only
            # Simply mark batches as is_active=FALSE in DB to 'Start Fresh'
            q = """
                SELECT batch_no FROM raw_material_qc 
                WHERE material_type ILIKE %s 
                  AND status = 'APPROVED'
                  AND is_active = TRUE
                ORDER BY updated_at DESC LIMIT 30
            """
        
        res = DBManager.fetch_data(q, (f"%{material_type}%",))
        return [r[0].strip() for r in res] if res else []
        self.press_modes = self.load_config()    


    def _get_unique_presses(self):
        seen, out = set(), []
        for pid, _ in self._press_list:
            if pid not in seen:
                seen.add(pid); out.append(pid)
        return out

    def _get_daylights_for_press(self, press_id):
        return [dl for pid, dl in self._press_list if pid == press_id]

    def _get_shift(self):
        h = datetime.datetime.now().hour
        if 7 <= h < 15:  return "A"
        if 15 <= h < 23: return "B"
        return "C"

    # =========================================================
    # STATIC UI SHELL  (built once, never torn down)
    # =========================================================
    def _build_ui(self):
        # ---- Header (static) ----
        hdr = tk.Frame(self.root, bg=C_SIDEBAR, height=70)
        hdr.pack(fill="x")
        self._lbl_header = tk.Label(
            hdr,
            text=f"🏗️ PC1 BUILDING | {self.current_user}  |  Shift {self._get_shift()}",
            fg="white", bg=C_SIDEBAR, font=("Segoe UI", 16, "bold"))
        self._lbl_header.pack(side="left", padx=25)
        tk.Button(hdr, text="BACK TO MENU", font=("Segoe UI", 10, "bold"),
                  bg="#C0392B", fg="white", relief="flat", padx=20, pady=10,
                  command=self.root.destroy).pack(side="right", padx=20, pady=15)

        
        # ---- NEW: PACK BOTTOM ACTION BAR FIRST ----
        # Reserve space at the bottom so it doesn't get pushed out of view
        self.btn_bar = tk.Frame(self.root, bg=C_BG, height=110) 
        self.btn_bar.pack(fill="x", side="bottom")
        self.btn_bar.pack_propagate(False) # Prevents children from resizing this frame

        # ---- Body: sidebar + workspace side by side ----
        # Use fill="both" and expand=True ONLY for the body now
        body = tk.Frame(self.root, bg=C_BG)
        body.pack(fill="both", expand=True)

        # Sidebar 
        self._sidebar = tk.Frame(body, bg=C_CARD_BG, width=420)
        self._sidebar.pack(side="left", fill="y", padx=(20, 10), pady=20)
        self._sidebar.pack_propagate(False)

        # Workspace 
        self.workspace = tk.Frame(body, bg=C_BG)
        self.workspace.pack(side="left", fill="both", expand=True, padx=(0, 20), pady=20)

        self._build_sidebar_widgets()
        
    def _build_sidebar_widgets(self):
        """Create all sidebar labels once. Update with _refresh_sidebar()."""
        s = self._sidebar

        self._sb_title = tk.Label(s, text="", fg="#E94560", bg=C_CARD_BG,
                                  font=("Segoe UI", 18, "bold"))
        self._sb_title.pack(pady=10)

        self._sb_btn_update = tk.Button(
            s, text="🔍 APPLY TREAD\nUPDATE", bg="#F39C12", fg="white",
            font=("Segoe UI", 12, "bold"), height=3, relief="flat",
            command=self.render_update_tread_page)

        self._sb_btn_home = tk.Button(
            s, text="🏠 HOME / RESET", font=("Segoe UI", 12, "bold"),
            bg="#2980B9", fg="white", command=self.reset_workflow, height=2)

        self._sb_btn_back = tk.Button(
            s, text="⬅ GO BACK", font=("Segoe UI", 12, "bold"),
            bg="#34495E", fg="white", height=1)

        self._sb_remaining = tk.Label(s, text="", bg=C_CARD_BG, fg="#F39C12",
                               font=("Segoe UI", 16, "bold"))
        self._sb_remaining.pack(pady=5)    

        tk.Button(s, text="🖨️ LAST REPRINT", bg="#16A085", fg="white", 
          font=("Segoe UI", 12, "bold"), height=2,
          command=lambda: self.print_label(*self.last_print_data) if self.last_print_data else None
          ).pack(fill="x", padx=40, pady=(20, 5))

        # 2. Open History for older ones
        tk.Button(s, text="🔍 SELECT REPRINT", bg="#34495E", fg="white",
                font=("Segoe UI", 12, "bold"), height=2,
                command=self.open_reprint_manager
                ).pack(fill="x", padx=40, pady=5)    

        info = tk.Frame(s, bg=C_CARD_BG)
        info.pack(fill="x", padx=20, pady=5)
        self._sb_size  = tk.Label(info, text="", bg=C_CARD_BG, fg="white",
                                  font=("Segoe UI", 14, "bold"))
        self._sb_size.pack(anchor="w", pady=3)
        self._sb_grade = tk.Label(info, text="", bg=C_CARD_BG, fg="white",
                                  font=("Segoe UI", 14, "bold"))
        self._sb_grade.pack(anchor="w", pady=3)

        tk.Label(s, text="MATERIAL TARGETS (KG)", bg=C_CARD_BG,
                 fg="#F39C12", font=("Segoe UI", 12, "bold")).pack(pady=(15, 5))

        f_tgt = tk.Frame(s, bg="#16213E", padx=15, pady=15)
        f_tgt.pack(fill="x", padx=20)
        self._tgt_labels = {}
        for lbl, key in [("CORE","core"),("MIDDLE","mid"),("C+T","ct"),
                          ("TREAD","tread"),("GUM","gum")]:
            row = tk.Frame(f_tgt, bg="#16213E"); row.pack(fill="x", pady=2)
            tk.Label(row, text=lbl, bg="#16213E", fg="#BDC3C7",
                     font=("Segoe UI", 12, "bold")).pack(side="left")
            lv = tk.Label(row, text="0.00", bg="#16213E", fg="#555",
                          font=("Segoe UI", 22, "bold"))
            lv.pack(side="right")
            self._tgt_labels[key] = lv

        self._sb_btn_summary = tk.Button(
            s, text="📊 SHIFT SUMMARY", font=("Segoe UI", 12, "bold"),
            bg="#8E44AD", fg="white", height=2, relief="flat",
            command=self.generate_shift_summary)
        self._sb_btn_summary.pack(fill="x", padx=40, pady=10)

        self._btn_csv = tk.Button(
            s, text="📥 DOWNLOAD CSV", font=("Segoe UI", 12, "bold"),
            bg="#2980B9", fg="white", height=2, relief="flat",
            command=self.export_shift_to_csv)
        self._btn_csv.pack(fill="x", padx=40, pady=10)       

        self._sb_bead = tk.Label(s, text="", bg=C_CARD_BG, fg="#BDC3C7",
                                 font=("Segoe UI", 13, "bold"))
        self._sb_bead.pack(pady=5)

        self._sb_target_wt = tk.Label(s, text="", bg=C_CARD_BG, fg="#27AE60",
                                      font=("Segoe UI", 28, "bold"))
        self._sb_target_wt.pack(pady=15)

    def _refresh_sidebar(self, title, prev_command=None):

        """Update sidebar text/buttons — NO widget recreation."""
        self._sb_title.config(text=title)
        self._sb_size.config( text=f"SIZE:  {self.plan_data['size']}")
        self._sb_grade.config(text=f"GRADE: {self.plan_data['quality']}")
        self._sb_bead.config( text=f"BEAD: {self.targets['bead']}")
        self._sb_target_wt.config(
            text=f"TARGET WT: {self.plan_data['target_wt']:.2f} KG")

        # Update remaining count
        if self.plan_data.get('production_requirement', 0) > 0:
            remaining = self.plan_data['production_requirement'] - self.plan_data.get('produced_qty', 0)
            self._sb_remaining.config(text=f"REMAINING: {remaining} / {self.plan_data['production_requirement']}")
        else:
            self._sb_remaining.config(text="")    

        for key, lv in self._tgt_labels.items():
            val = self.targets[key]
            lv.config(text=f"{val:.2f}",
                      fg="white" if val > 0 else "#555")

        # Toggle home/update button
        self._sb_btn_update.pack_forget()
        self._sb_btn_home.pack_forget()
        if self.current_page == PAGE_MACHINE:
            self._sb_btn_update.pack(fill="x", padx=40, pady=10,
                                     after=self._sb_title)
        else:
            self._sb_btn_home.pack(fill="x", padx=40, pady=10,
                                   after=self._sb_title)

        # Back button
        self._sb_btn_back.pack_forget()
        if prev_command:
            self._sb_btn_back.config(command=prev_command)
            self._sb_btn_back.pack(fill="x", padx=40, pady=5)

    # =========================================================
    # WORKSPACE & BTN_BAR HELPERS
    # =========================================================
    def _clear_workspace(self):
        for w in self.workspace.winfo_children(): w.destroy()

    def _clear_btn_bar(self):
        for w in self.btn_bar.winfo_children(): w.destroy()

    def _add_btn(self, text, command, bg=C_PROCEED, side="right", width=22):
        """Standardized button to ensure labels are never clipped."""
        btn = tk.Button(self.btn_bar, text=text, command=command, bg=bg, fg="white", 
                        font=("Segoe UI", 16, "bold"), height=2, width=width,
                        relief="flat")
        # Increase pady to ensure the text isn't touching the frame edges
        btn.pack(side=side, padx=20, pady=15) 
        return btn

    # =========================================================
    # PAGE 1 — MACHINE SELECTION
    # =========================================================
    def render_page_1(self):
        self.current_page = PAGE_MACHINE
        self._clear_workspace()
        self._clear_btn_bar()
        self._refresh_sidebar("STEP 1: MACHINE")
        self.press_modes = self.load_config()

        canvas, scroll_frame = self._make_scrollable_workspace()
        right = scroll_frame

        # Machine Selection Grid
        tk.Label(right, text="SELECT PRESS:", fg="white", bg=C_BG,
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=20)

        press_ids = self._get_unique_presses()
        p_grid = tk.Frame(right, bg=C_BG); p_grid.pack(pady=10)

        for i, pid in enumerate(press_ids):
            mode = self.press_modes.get(pid, "STD")
            # Determine button colour
            if self.sel_press == pid:
                bg = C_SELECTED
            elif mode == "OVEN":
                bg = C_OVEN
            else:
                bg = C_IDLE

            tk.Button(
                p_grid, text=pid, font=("Segoe UI", 14, "bold"), width=8, height=3,
                bg=bg,
                command=lambda p=pid: self.select_press(p)
            ).grid(row=i // 4, column=i % 4, padx=10, pady=10)

        # Daylight Selection
        if self.sel_press:
            daylights = self._get_daylights_for_press(self.sel_press)
            tk.Label(right, text=f"SELECT DAYLIGHT ({self.sel_press}):",
                     fg="white", bg=C_BG, font=("Segoe UI", 14, "bold")).pack(
                         anchor="w", padx=20, pady=(20, 0))
            dl_row = tk.Frame(right, bg=C_BG); dl_row.pack(pady=10)
            for dl in daylights:
                tk.Button(
                    dl_row, text=dl, font=("Segoe UI", 14, "bold"), width=12, height=2,
                    # Matches selection based on the DB string
                    bg=C_SELECTED if self.sel_daylight == dl else C_IDLE, 
                    command=lambda d=dl: self.select_daylight(d)
                ).pack(side="left", padx=10)
                
        # Detailed Plan Confirmation
        if self.plan_data["size"] != "—":
            # Dynamic color: Purple for POB, Dark Blue for Standard
            card_color = "#5B2C6F" if self.plan_data["is_pob"] else "#0F3460"
            status_text = "✅ POB PLAN LOADED" if self.plan_data["is_pob"] else "✅ PLAN LOADED"
            
            f_plan = tk.Frame(right, bg=card_color, padx=15, pady=15)
            f_plan.pack(fill="x", padx=20, pady=10)
            
            tk.Label(f_plan, text=status_text, fg="#27AE60",
                     bg=card_color, font=("Segoe UI", 12, "bold")).pack(anchor="w")
            
            # Show Size, Brand, Pattern, and Grade
            detail_str = (f"{self.plan_data['size']} | {self.plan_data['brand']}\n"
                          f"Pattern: {self.plan_data['pattern']} | Grade: {self.plan_data['quality']}")
            
            tk.Label(f_plan, text=detail_str, fg="white", bg=card_color,
                     font=("Segoe UI", 11), justify="left").pack(anchor="w", pady=5)
            
            self._add_btn("NEXT: BATCHES ➔", self.render_page_2)

    # =========================================================
    # PAGE 2 — BATCH SELECTION
    # =========================================================
    def render_page_2(self):
        self.current_page = PAGE_BATCHES
        self._clear_workspace()
        self._clear_btn_bar()
        self._refresh_sidebar("STEP 2: BATCHES", prev_command=self.render_page_1)

        canvas, scroll_frame = self._make_scrollable_workspace()
        right = scroll_frame

        row = 0
        tk.Label(right, text="CORE BATCH(ES):", fg="white", bg=C_BG,
                 font=("Segoe UI", 13, "bold")).grid(
            row=row, column=0, sticky="w", padx=15, pady=(10, 5))
        row += 1
        row = self._render_tile_grid(right, "CORE",
                                     self.selected_core_batches, row, cols=6)

        tk.Label(right, text="MIDDLE LAYER(S):", fg="white", bg=C_BG,
                 font=("Segoe UI", 13, "bold")).grid(
            row=row, column=0, sticky="w", padx=15, pady=(15, 5))
        row += 1
        row = self._render_tile_grid(right, "MID",
                                     self.selected_mid_batches, row, cols=6)

        if self.plan_data["is_pob"]:
            tk.Label(right, text="GUM BATCH (POB):", fg="#E74C3C",
                     bg=C_BG, font=("Segoe UI", 13, "bold")).grid(
                row=row, column=0, sticky="w", padx=15, pady=(15, 5))
            row += 1
            self._render_tile_grid(right, "GUM",
                                   self.selected_gum_batches, row, cols=6)

        self._add_btn("⚠️ SAVE PARTIAL",
                      lambda: self.finalize_submission(status="PARTIAL"),
                      bg=C_WARN, side="left", width=16)
        self._add_btn("NEXT: FINISH ➔", self.validate_page_2_and_next)

    def validate_page_2_and_next(self):
        """Hard-gate validation for mandatory batches."""
        is_pob = self.plan_data.get("is_pob", False)
        
        if is_pob:
            # POB must have Bonding Gum
            if not self.selected_gum_batches:
                return messagebox.showwarning("Missing Data", "POB Tyre requires a GUM batch.")
        else:
            # Standard must have Core
            if not self.selected_core_batches:
                return messagebox.showwarning("Missing Data", "Standard Tyre requires a CORE batch.")
        
        self.render_page_3()
            
   

    # =========================================================
    # PAGE 3 — FINISH
    # =========================================================
    def render_page_3(self):
        self.current_page = PAGE_FINISH
        self._clear_workspace()
        self._clear_btn_bar()
        self._refresh_sidebar("STEP 3: FINISH", prev_command=self.render_page_2)

        canvas, scroll_frame = self._make_scrollable_workspace()
        right = scroll_frame

        # --- Tread Type Selection ---
        t_f = tk.Frame(right, bg=C_BG); t_f.pack(fill="x", pady=10)
        tk.Label(t_f, text="TREAD TYPE:", fg="white", bg=C_BG, font=("Segoe UI", 12, "bold")).pack(side="left", padx=20)
        for t in ["VT001", "VT002", "VT003", "NMW"]:
            tk.Button(t_f, text=t, font=("Segoe UI", 11, "bold"), width=8,
                bg=C_SELECTED if self.sel_tread_type.get() == t else C_IDLE,
                command=lambda x=t: [self.sel_tread_type.set(x), self.render_page_3()]
            ).pack(side="left", padx=5)

        # --- Tread Batch Tiles ---
        tk.Label(right, text="TREAD BATCH(ES):", fg="white", bg=C_BG, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=20)
        tb_f = tk.Frame(right, bg=C_BG); tb_f.pack(fill="x", pady=5)
        self._render_tile_grid(tb_f, self.sel_tread_type.get(), self.selected_tread_batches, start_row=0, cols=5)

        # --- POB Special Fields ---
        if self.plan_data.get("is_pob"):
            pob_f = tk.Frame(right, bg="#2E1A3E", padx=15, pady=10)
            pob_f.pack(fill="x", padx=20, pady=10)
            tk.Label(pob_f, text="MS RIM WEIGHT (KG):", fg="white", bg="#2E1A3E", font=("Segoe UI", 12, "bold")).pack(side="left")
            self.entry_ms_rim = tk.Entry(pob_f, textvariable=self.var_ms_rim_wt, font=("Segoe UI", 24, "bold"), 
                                        width=8, justify="center", bg="#F5EEF8")
            self.entry_ms_rim.pack(side="left", padx=20)
            self.entry_ms_rim.bind("<FocusIn>", lambda e: setattr(self, 'active_entry_var', self.var_ms_rim_wt))

            # Show selected gum batches (from page 2)
            tk.Label(right, text="BONDING GUM (PICKED):", fg="#E94560", bg=C_BG, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=20)
            gum_f = tk.Frame(right, bg=C_BG); gum_f.pack(fill="x", pady=5)
            self._render_tile_grid(gum_f, "GUM", self.selected_gum_batches, start_row=0, cols=6)

        # --- Target Weight Display (NEW) ---
        target_frame = tk.Frame(right, bg=C_BG)
        target_frame.pack(fill="x", padx=20, pady=(20, 5))
        tk.Label(target_frame, text="TARGET WT:", fg="#F39C12", bg=C_BG,
                font=("Segoe UI", 12, "bold")).pack(side="left")
        self.lbl_target_wt_finish = tk.Label(target_frame,
                                            text=f"{self.plan_data['target_wt']:.2f} kg" if self.plan_data['target_wt'] > 0 else "---",
                                            fg="white", bg=C_BG, font=("Segoe UI", 18, "bold"))
        self.lbl_target_wt_finish.pack(side="left", padx=10)

        # --- Weight Entry & Numpad ---
        bot = tk.Frame(right, bg=C_BG); bot.pack(fill="both", expand=True, pady=10)
        f_entry = tk.Frame(bot, bg=C_BG); f_entry.pack(side="left", padx=20)

        self.weight_entry = tk.Entry(f_entry, textvariable=self.weight_var, font=("Segoe UI", 36, "bold"), 
                                    justify="center", width=8, bg="#D5F5E3")
        self.weight_entry.pack(pady=5)
        self.weight_entry.bind("<FocusIn>", lambda e: setattr(self, 'active_entry_var', self.weight_var))

        # Numpad
        num_grid = tk.Frame(f_entry, bg=C_BG); num_grid.pack()
        for idx, k in enumerate(['7','8','9','4','5','6','1','2','3','0','.','CLR']):
            tk.Button(num_grid, text=k, font=("Segoe UI", 16, "bold"), width=4, height=1, bg="#34495E", fg="white",
                    command=lambda x=k: self.numpad_press(x)).grid(row=idx // 3, column=idx % 3, padx=3, pady=3)

        # --- Build Button (hidden initially) ---
        tk.Frame(self.btn_bar, bg=C_BG).pack(side="left", expand=True, fill="x")
        self._complete_btn = self._add_btn("✅ BUILD COMPLETE", self.finalize_submission, bg="#2ECC71", side="left", width=20)
        tk.Frame(self.btn_bar, bg=C_BG).pack(side="left", expand=True, fill="x")

        # Initial validation
        self._update_complete_button_state()
    # =========================================================
    # UPDATE PAGE
    # =========================================================
    def render_update_tread_page(self):
        self.current_page = PAGE_UPDATE
        self._clear_workspace()
        self._clear_btn_bar()
        self._refresh_sidebar("TREAD UPDATE", prev_command=self.render_page_1)

        canvas, scroll_frame = self._make_scrollable_workspace()
        right = scroll_frame

        tk.Label(right, text="SCAN B-ID BARCODE:", fg="white", bg=C_BG,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=20)
        entry_bid = tk.Entry(right, textvariable=self.upd_bid_var,
                             font=("Segoe UI", 28), width=18,
                             justify="center", bg="#FBFCFC")
        entry_bid.pack(pady=15)
        entry_bid.bind("<Return>", self.lookup_partial)
        entry_bid.focus_set()

        self.lbl_partial_info = tk.Label(
            right, text="[ Awaiting Barcode Scan ]",
            fg="#BDC3C7", bg=C_BG, font=("Segoe UI", 14, "italic"))
        self.lbl_partial_info.pack(pady=10)

        t_f = tk.Frame(right, bg=C_BG); t_f.pack(fill="x", pady=10)
        tk.Label(t_f, text="TREAD TYPE:", fg="white", bg=C_BG,
                 font=("Segoe UI", 12, "bold")).pack(side="left", padx=20)
        for t in ["VT001", "VT002", "VT003", "NMW"]:
            tk.Button(
                t_f, text=t, font=("Segoe UI", 11, "bold"), width=8,
                bg=C_SELECTED if self.sel_tread_type.get() == t else C_IDLE,
                command=lambda x=t: [self.sel_tread_type.set(x),
                                     self.render_update_tread_page()]
            ).pack(side="left", padx=5)

        tk.Label(right, text="SELECT TREAD BATCH(ES):", fg="white", bg=C_BG,
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=20)
        tb_f = tk.Frame(right, bg=C_BG); tb_f.pack(fill="x", pady=5)
        self._render_tile_grid(tb_f, self.sel_tread_type.get(),
                               self.selected_tread_batches, start_row=0, cols=5)

        tk.Label(right, text="FINAL GREEN WEIGHT (KG):", fg="white", bg=C_BG,
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 0))
        self.weight_entry = tk.Entry(right, textvariable=self.weight_var,
                                      font=("Segoe UI", 28, "bold"), justify="center",
                                      width=10, bg="#D5F5E3")
        self.weight_entry.pack(pady=5)

        # Add the UPDATE button (centered as well)
        tk.Frame(self.btn_bar, bg=C_BG).pack(side="left", expand=True, fill="x")
        self._add_btn("💾 UPDATE & COMPLETE", self.submit_tread_update, side="left", width=20)
        tk.Frame(self.btn_bar, bg=C_BG).pack(side="left", expand=True, fill="x")

        # Trace weight changes for highlighting (optional on this page)
        self.weight_var.trace_add("write", lambda *args: self._highlight_weight_entry())
        self._highlight_weight_entry()

    # =========================================================
    # TILE GRID — recolor only, never re-renders page
    # =========================================================
    def _render_tile_grid(self, parent, material_type, selection_list,
                          start_row=0, cols=4):
        """Draw batch tiles with instant-feedback toggle logic."""
        batches = self._fetch_batches(material_type)
        if not batches:
            tk.Label(parent, text=f"No active/unused batches for {material_type}",
                     fg="orange", bg=C_BG, font=("Segoe UI", 10)).grid(
                row=start_row, column=0, columnspan=cols, padx=10, pady=5)
            return start_row + 1

        btn_refs = {}

        def toggle(b_no):
            """In-place update: Changes only button colors and sidebar stats."""
            if b_no in selection_list:
                selection_list.remove(b_no)
            else:
                selection_list.append(b_no)
            
            # Instant visual feedback: only recolor the buttons
            for bn, btn in btn_refs.items():
                btn.config(bg=C_SELECTED if bn in selection_list else C_IDLE)
            
            # Update the sidebar labels WITHOUT re-rendering the whole page
            self._refresh_sidebar(self._sb_title.cget("text"))
            
            if self.current_page == PAGE_FINISH:
                self._update_complete_button_state()

        for i, b_no in enumerate(batches):
            btn = tk.Button(
                parent, text=b_no, font=("Segoe UI", 10, "bold"),
                width=12, height=2,
                bg=C_SELECTED if b_no in selection_list else C_IDLE,
                activebackground=C_SELECTED, # Better touch feel
                command=lambda b=b_no: toggle(b)
            )
            btn.grid(row=start_row + i // cols, column=i % cols, padx=3, pady=3)
            btn_refs[b_no] = btn

        return start_row + (len(batches) + cols - 1) // cols
        
    # =========================================================
    # PRESS & PLAN LOGIC
    # =========================================================
    def select_press(self, p_id):
        if self.sel_press != p_id:
            self.sel_daylight = ""
            self.plan_data = {
                "size": "—", "core": "—", "brand": "—", "quality": "—",
                "target_wt": 0.0, "type": "—", "is_pob": False, "pi_number": None
            }
        self.sel_press = p_id
        
        # Check if it's an Oven to show the slot grid
        if "OVEN" in p_id.upper():
            self.render_oven_slot_page()
        else:
            self.render_page_1()

    def render_oven_slot_page(self):
        self.current_page = PAGE_MACHINE
        self._clear_workspace()
        self._clear_btn_bar()
        self._refresh_sidebar(f"SELECT {self.sel_press} SLOT")

        canvas, scroll_frame = self._make_scrollable_workspace()
        f_grid = tk.Frame(scroll_frame, bg=C_BG)
        f_grid.pack(pady=20, padx=20)

        # Fetch all planned slots for this specific Oven from the database
        q = """SELECT daylight, tyre_size, brand, quality 
            FROM production_plan 
            WHERE press_id = %s ORDER BY daylight"""
        planned_slots = DBManager.fetch_data(q, (self.sel_press,))

        if not planned_slots:
            tk.Label(f_grid, text="⚠️ NO SLOTS PLANNED FOR THIS OVEN", 
                    fg="orange", bg=C_BG, font=("Segoe UI", 14, "bold")).pack()
            return

        # Determine grid layout: fixed 2 columns, rows calculated
        cols = 2
        for i, (slot, size, brand, qual) in enumerate(planned_slots):
            row = i // cols
            col = i % cols

            # Create a large tile for each slot
            btn_text = f"{slot}\n{size}\n{brand}"
            btn = tk.Button(f_grid, text=btn_text, font=("Segoe UI", 11, "bold"),
                            width=15, height=5,
                            bg=C_SELECTED if self.sel_daylight == slot else C_IDLE,
                            fg="black",
                            command=lambda s=slot: self.select_oven_slot(s))

            btn.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        # Configure grid columns to expand equally
        for col in range(cols):
            f_grid.columnconfigure(col, weight=1)

        # If a slot is selected, show the Next button
        if self.sel_daylight:
            self._add_btn("NEXT: BATCHES ➔", self.proceed_from_oven_slot)

    def select_oven_slot(self, slot):
        """Select a slot on the oven page – updates highlight only, does NOT fetch plan yet."""
        self.sel_daylight = slot
        # Re‑render the oven page to reflect the new selection (button turns red)
        self.render_oven_slot_page()

    def proceed_from_oven_slot(self):
        """After a slot is selected, fetch plan and go to page 2."""
        if self.sel_daylight and self.fetch_plan_details():
            self.render_page_2()        

    def select_daylight(self, dl_id):
        self.sel_daylight = dl_id
        if self.fetch_plan_details():
            # If this is an oven press, go directly to batches page
            if "OVEN" in self.sel_press.upper():
                self.render_page_2()
            else:
                self.render_page_1()

    def fetch_plan_details(self):
        """Fetch plan details and update self.plan_data. Returns True if found."""
        q = """SELECT tyre_size, brand, pattern, quality, mould_id_marks, type,
                    tyre_weight, core_size, production_requirement, pi_number, produced_qty
            FROM production_plan
            WHERE TRIM(press_id)=%s AND TRIM(daylight)=%s LIMIT 1"""
        res = DBManager.fetch_data(q, (self.sel_press, self.sel_daylight))
        if res:
            r = res[0]
            is_pob_detected = "POB" in str(r[5]).upper()
            self.plan_data.update({
                "size":      r[0] if r[0] else "—",
                "brand":     r[1] if r[1] else "—",
                "pattern":   r[2] if r[2] else "—",
                "quality":   r[3] if r[3] else "—",
                "mould":     r[4] if r[4] else "—",
                "type":      r[5] if r[5] else "—",
                "target_wt": float(r[6] or 0.0),
                "core_size": r[7] if r[7] else "—",
                "production_requirement": int(r[8] or 0),
                "pi_number": r[9],
                "produced_qty": int(r[10] or 0),
                "is_pob":    is_pob_detected
            })
            self.calculate_material_targets()
            return True
        else:
            messagebox.showwarning(
                "No Plan",
                f"No production plan for {self.sel_press} / {self.sel_daylight}.",
                parent=self.root)
            return False

    def calculate_material_targets(self):
        grade = self.plan_data["quality"]
        size  = self.plan_data["size"]
        spec  = DBManager.fetch_data(
            "SELECT core_pct, mid_pct, ct_pct, tread_pct, gum_pct "
            "FROM tyre_specs WHERE grade=%s", (grade,))

        b_wt, b_cnt = 0.0, 0
        if not self.plan_data["is_pob"]:
            bead = DBManager.fetch_data(
                "SELECT bead_size, bead_count, weight_per_bead "
                "FROM bead_master WHERE UPPER(tyre_size)=%s LIMIT 1",
                (str(size).upper(),))
            if bead:
                b_cnt = int(bead[0][1]); b_wt = float(bead[0][2])
                self.targets['bead'] = f"{bead[0][0]} x {b_cnt}"
            else:
                self.targets['bead'] = "⚠️ MISSING"
        else:
            self.targets['bead'] = "N/A (POB)"

        for key in ['core','mid','ct','tread','gum']:
            self.targets[key] = 0.0
        if spec:
            net = self.plan_data["target_wt"] - (b_wt * b_cnt)
            if net > 0:
                for idx, key in enumerate(['core','mid','ct','tread','gum']):
                    self.targets[key] = net * (float(spec[0][idx] or 0) / 100)

    # =========================================================
    # SAVE LOGIC
    # =========================================================
    def _validate_weight(self, actual):
        tgt = self.plan_data["target_wt"]
        if tgt <= 0 or actual <= 0: return True, None
        lo, hi = tgt * 0.85, tgt * 1.15
        if actual < lo or actual > hi:
            pct = abs(actual - tgt) / tgt * 100
            return False, (
                f"⚠️ WEIGHT OUT OF TOLERANCE\n\n"
                f"Entered : {actual:.2f} kg\n"
                f"Target  : {tgt:.2f} kg\n"
                f"Deviation: {pct:.1f}%  (limit ±15%)\n\nProceed anyway?")
        return True, None

    def finalize_submission(self, status="COMPLETED"):
        """Production version with MS Rim Weight and POB logic."""
        # 1. Basic Setup Validation
        if not self.sel_press or self.plan_data["size"] == "—":
            return messagebox.showerror("Error", "No plan loaded.", parent=self.root)

        # 2. Extract Weights and POB Data
        try:
            actual_wt = float(self.weight_var.get() or 0.0)
            # MS Rim weight only applies to POB tires
            ms_rim_wt = float(self.var_ms_rim_wt.get() or 0.0) if self.plan_data.get("is_pob") else 0.0
        except ValueError:
            return messagebox.showerror("Error", "Invalid weight entry.", parent=self.root)

        # 3. Completion Check Logic
        if status == "COMPLETED":
            # Mandatory check for Tread Batch
            if not self.selected_tread_batches:
                if not messagebox.askyesno("No Tread Batch", 
                    "No tread batch selected. Save as PARTIAL instead?", parent=self.root):
                    return
                status = "PARTIAL"
            
            # Mandatory check for Bonding Gum if POB
            elif self.plan_data.get("is_pob") and not self.selected_gum_batches:
                if not messagebox.askyesno("No Gum Batch", 
                    "POB requires Bonding Gum. Save as PARTIAL instead?", parent=self.root):
                    return
                status = "PARTIAL"

        # Increment produced_qty in production_plan
        DBManager.execute_query(
            "UPDATE production_plan SET produced_qty = produced_qty + 1 WHERE press_id=%s AND daylight=%s",
            (self.sel_press, self.sel_daylight)
        )

        # If this order has a PI number, also update master_orders
        if self.plan_data.get('pi_number'):
            DBManager.execute_query(
                "UPDATE master_orders SET produced_qty = produced_qty + 1 WHERE pi_number=%s",
                (self.plan_data['pi_number'],)
            )

        # Refresh local plan data (or increment locally)
        self.plan_data['produced_qty'] = self.plan_data.get('produced_qty', 0) + 1

        # Update sidebar immediately
        self._refresh_sidebar(self._sb_title.cget("text"))

        # Check if target reached
        remaining = self.plan_data['production_requirement'] - self.plan_data['produced_qty']
        if remaining <= 0:
            messagebox.showinfo("Target Achieved",
                                f"Production target for {self.sel_press}-{self.sel_daylight} has been met!",
                                parent=self.root)        

        # 4. Target Weight Validation (15% Tolerance)
        if status == "COMPLETED":
            # Combined target for POB; Standard target for others
            combined_target = self.plan_data["target_wt"] + ms_rim_wt
            
            if combined_target > 0:
                tolerance = 0.15
                min_w = combined_target * (1 - tolerance)
                max_w = combined_target * (1 + tolerance)
                
                if actual_wt < min_w or actual_wt > max_w:
                    msg = (f"⚠️ WEIGHT WARNING!\n\nTarget Expected: {combined_target:.2f} kg\n"
                           f"Actual Entered: {actual_wt:.2f} kg\n\nOutside 15% Tolerance. Proceed?")
                    if not messagebox.askyesno("Weight Check", msg, parent=self.root):
                        return

        # 5. Database Insertion
        bid = self._get_next_bid()
        
        # Consistent SQL query using standardized 'BOT', 'TOP', or 'SINGLE'
        q = """INSERT INTO pc1_building (
                   b_id, press_id, daylight, tyre_size, core_size, brand, quality,
                   pattern, mould_id_marks, batch_core, batch_mid, batch_tread, batch_gum,
                   tread_type, green_tyre_weight, ms_rim_weight, operator_id, shift,
                   is_pob, status, pi_number, birth_time
               ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        
        data = (
            bid, 
            self.sel_press, 
            self.sel_daylight, # Now standardized as BOT, TOP, or SINGLE
            self.plan_data["size"], 
            self.plan_data.get("core_size", "—"),
            self.plan_data["brand"], 
            self.plan_data["quality"],
            self.plan_data.get("pattern", "—"), 
            self.plan_data.get("mould", "—"),
            ", ".join(self.selected_core_batches),
            ", ".join(self.selected_mid_batches),
            ", ".join(self.selected_tread_batches),
            ", ".join(self.selected_gum_batches),
            self.sel_tread_type.get(),
            actual_wt if actual_wt > 0 else None,
            ms_rim_wt if ms_rim_wt > 0 else None,
            self.current_user, 
            self._get_shift(),
            self.plan_data["is_pob"], 
            status,
            self.plan_data["pi_number"],
            datetime.datetime.now() if status == "COMPLETED" else None
        )

        if DBManager.execute_query(q, data):
            # Store data for the 'Last Reprint' button
            self.last_print_data = (bid, self.plan_data["size"], self.sel_press, self.sel_daylight)
            self.print_label(*self.last_print_data)

            # Print label using correct press-daylight strings
            # self.print_label(bid, self.plan_data["size"], self.sel_press, self.sel_daylight)
            messagebox.showinfo("Saved ✅", f"B-ID: {bid}\nStatus: {status}", parent=self.root)
            self.reset_workflow()
        else:
            messagebox.showerror("DB Error", "Failed to save record.", parent=self.root)
    def submit_tread_update(self):
        bid = self.upd_bid_var.get().strip().upper()
        if not bid:
            return messagebox.showerror("Error", "No B-ID scanned.", parent=self.root)
        if not self.selected_tread_batches:
            return messagebox.showerror(
                "Error", "Select at least one tread batch.", parent=self.root)
        try:
            actual = float(self.weight_var.get() or 0.0)
        except ValueError:
            return messagebox.showerror(
                "Error", "Invalid weight entry.", parent=self.root)

        ok, warn = self._validate_weight(actual)
        if not ok and not messagebox.askyesno(
                "Weight Warning", warn, parent=self.root):
            return

        if not messagebox.askyesno("Confirm Update",
                                   f"Update tyre {bid} to COMPLETED with weight {actual:.2f} kg?",
                                   parent=self.root):
            return

        q = """UPDATE pc1_building
               SET batch_tread=%s, tread_type=%s, green_tyre_weight=%s,
                   status='COMPLETED', birth_time=NOW()
               WHERE b_id=%s AND status='PARTIAL'"""
        if DBManager.execute_query(q, (
            ", ".join(self.selected_tread_batches),
            self.sel_tread_type.get(),
            actual if actual > 0 else None, bid
        )):
            messagebox.showinfo(
                "Updated ✅", f"Tyre {bid} is now COMPLETED.", parent=self.root)
            self.reset_workflow()
        else:
            messagebox.showerror(
                "Error",
                f"Could not update {bid}. Not found or not PARTIAL.",
                parent=self.root)

    def lookup_partial(self, event=None):
        bid = self.upd_bid_var.get().strip().upper()
        if not bid: return
        q = """SELECT b.tyre_size, b.quality, b.status, pp.tyre_weight
               FROM pc1_building b
               LEFT JOIN production_plan pp
                      ON TRIM(pp.press_id)=TRIM(b.press_id)
                     AND TRIM(pp.daylight) =TRIM(b.daylight)
               WHERE b.b_id=%s AND b.status='PARTIAL' LIMIT 1"""
        res = DBManager.fetch_data(q, (bid,))
        if res:
            self.plan_data.update({
                "size":      res[0][0],
                "quality":   res[0][1] or "—",
                "target_wt": float(res[0][3] or 0)
            })
            self.calculate_material_targets()
            self._refresh_sidebar("TREAD UPDATE", prev_command=self.render_page_1)
            self.lbl_partial_info.config(
                text=f"✅ FOUND: {res[0][0]}  |  {res[0][1]}", fg=C_PROCEED)
            self.upd_bid_var.set(bid)
        else:
            self.lbl_partial_info.config(
                text=f"❌ NOT FOUND (must be PARTIAL): {bid}", fg=C_SELECTED)
            self.upd_bid_var.set("")

    # =========================================================
    # RESET
    # =========================================================
    def reset_workflow(self):
        self.sel_press = ""; self.sel_daylight = ""
        self.plan_data = {
            "size": "—", "core_size": "—", "brand": "—", "quality": "—",
            "target_wt": 0.0, "type": "—", "is_pob": False, "pi_number": None
        }
        self.targets = {"core":0.0,"mid":0.0,"ct":0.0,
                        "gum":0.0,"tread":0.0,"bead":"—"}
        self.selected_core_batches  = []
        self.selected_mid_batches   = []
        self.selected_tread_batches = []
        self.selected_gum_batches   = []
        self.var_ms_rim_wt.set("0")     # Reset Rim Weight to 0
        self.weight_var.set("")
        self.active_entry_var = self.weight_var  # Reset focus to Tyre Weight
        self.upd_bid_var.set("")
        self.render_page_1()
        self.plan_data.update({
            "production_requirement": 0,
            "produced_qty": 0
        })
        self._refresh_sidebar(self._sb_title.cget("text"))

    # =========================================================
    # UTILS
    # =========================================================
    def _make_scrollable_workspace(self):
        """Create a canvas with scrollbar inside self.workspace and return (canvas, scroll_frame)."""
        canvas = tk.Canvas(self.workspace, bg=C_BG, highlightthickness=0)
        v_scroll = ttk.Scrollbar(self.workspace, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=C_BG)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scroll.set)

        canvas.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")

        # No extra padding binding – it caused errors
        return canvas, scroll_frame

    # ---------------------------------------------------------
    # These two methods were missing – now they are restored
    # ---------------------------------------------------------
    def _update_complete_button_state(self):
        """Strictly controls the 'BUILD COMPLETE' button activation."""
        is_pob = self.plan_data.get("is_pob", False)
        
        # Mandatory for all
        has_tread = len(self.selected_tread_batches) > 0
        try:
            has_weight = float(self.weight_var.get()) > 0
        except:
            has_weight = False

        # 2. Check MS Rim Weight (if POB)
        # Mandatory for all
        # Mandatory for POB only
        rim_wt_ok = True
        if is_pob:
            try:
                # This will now work because self.var_ms_rim_wt is initialized
                rim_wt_ok = float(self.var_ms_rim_wt.get()) > 0
            except:
                rim_wt_ok = False

        # Update Button
        if hasattr(self, '_complete_btn'):
            if has_tread and has_weight and rim_wt_ok:
                self._complete_btn.config(state="normal", bg="#2ECC71")
            else:
                self._complete_btn.config(state="disabled", bg="#BDC3C7")
                
    def _highlight_weight_entry(self):
        """Change weight entry background based on tolerance."""
        if not hasattr(self, 'weight_entry'):
            return
        try:
            actual = float(self.weight_var.get())
            tgt = self.plan_data["target_wt"]
            if tgt > 0:
                lo, hi = tgt * 0.85, tgt * 1.15
                if lo <= actual <= hi:
                    self.weight_entry.config(bg="#D5F5E3")  # light green
                else:
                    self.weight_entry.config(bg="#FADBD8")  # light red
            else:
                self.weight_entry.config(bg="#D5F5E3")
        except:
            self.weight_entry.config(bg="#D5F5E3")

    def numpad_press(self, key):
        """Directs touch input to the focused field (Rim or Tyre weight)."""
        # Uses the variable set by the <FocusIn> event
        target_var = getattr(self, 'active_entry_var', self.weight_var)
        if key == 'CLR':
            target_var.set("")
        else:
            cur = target_var.get()
            if key == '.' and '.' in cur:
                return
            target_var.set(cur + key)
        # Re-verify the 'Build Complete' button state after every key press
        self._update_complete_button_state()    

    def _get_next_bid(self):
        res = DBManager.fetch_data(
            "SELECT b_id FROM pc1_building "
            "WHERE b_id LIKE 'B-%' ORDER BY created_at DESC LIMIT 1")
        try:
            if res and res[0][0].startswith("B-"):
                return f"B-{int(res[0][0].split('-')[1]) + 1:06d}"
        except (IndexError, ValueError): pass
        return "B-000001"

    def print_label(self, bid, size, press, daylight):
        epl = (f'N\nq464\nQ200,24\n'
               f'A47,30,0,3,1,1,N,"{size} | {press}-{daylight}"\n'
               f'B60,70,0,1,2,5,90,B,"{bid}"\nP1\n')
        try:
            if platform.system() == "Linux":
                with open(LINUX_PRINTER_PATH, "wb") as f:
                    f.write(epl.encode())
        except Exception as e:
            print(f"Printer error: {e}")

    def generate_shift_summary(self):
        """Generates a summary of today's production for the current shift."""
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        shift = self._get_shift()
        
        # Query to fetch today's production for this shift
        q = """
            SELECT b_id, tyre_size, quality, status, 
                   green_tyre_weight, ms_rim_weight, to_char(birth_time, 'HH12:MI AM')
            FROM pc1_building 
            WHERE date(created_at) = CURRENT_DATE 
              AND shift = %s
            ORDER BY birth_time DESC
        """
        res = DBManager.fetch_data(q, (shift,))
        
        if not res:
            return messagebox.showinfo("Summary", f"No tyres built yet for Shift {shift} today.")

        # Calculate Totals
        total_tyres = len(res)
        pob_count = sum(1 for r in res if r[5] and r[5] > 0)
        
        # Create the display string
        summary_text = f"--- SHIFT {shift} SUMMARY ({today}) ---\n"
        summary_text += f"Total Tyres Built: {total_tyres}\n"
        summary_text += f"POB Tyres: {pob_count}  |  Standard: {total_tyres - pob_count}\n"
        summary_text += "-" * 40 + "\n"
        summary_text += f"{'B-ID':<10} {'SIZE':<15} {'GW (kg)':<10} {'RIM (kg)':<10}\n"
        
        for r in res:
            gw = f"{r[4]:.2f}" if r[4] else "PARTIAL"
            rim = f"{r[5]:.2f}" if r[5] else "0.00"
            summary_text += f"{r[0]:<10} {r[1]:<15} {gw:<10} {rim:<10}\n"

        # Show in a scrollable popup or print to console
        self.show_custom_report_popup(summary_text)

    def open_reprint_manager(self):
        """Opens a touch-friendly list of recent builds for reprinting."""
        top = tk.Toplevel(self.root)
        top.title("Select Reprint")
        top.geometry("600x700")
        top.configure(bg=C_BG)

        tk.Label(top, text="SELECT RECENT BUILD TO REPRINT", fg="#F39C12", 
                bg=C_BG, font=("Segoe UI", 14, "bold")).pack(pady=15)

        # Fetch last 10 builds from DB
        q = """SELECT b_id, tyre_size, press_id, daylight, 
                    to_char(created_at, 'HH12:MI AM') as time
            FROM pc1_building 
            ORDER BY created_at DESC LIMIT 10"""
        recent_builds = DBManager.fetch_data(q)

        # Container for tiles
        list_frame = tk.Frame(top, bg=C_BG)
        list_frame.pack(fill="both", expand=True, padx=20)

        for b in recent_builds:
            bid, size, press, dl, time = b
            # Create a large 'Tile' for each build
            btn_text = f"🕒 {time} | {bid}\n{size} ({press}-{dl})"
            tk.Button(list_frame, text=btn_text, font=("Segoe UI", 12, "bold"),
                    bg=C_CARD_BG, fg="white", height=3, pady=10, relief="flat",
                    command=lambda b=b: [self.print_label(b[0], b[1], b[2], b[3]), top.destroy()]
                    ).pack(fill="x", pady=5)

        tk.Button(top, text="❌ CLOSE", command=top.destroy, bg="#C0392B", 
                fg="white", font=("Segoe UI", 12, "bold"), height=2).pack(fill="x", padx=20, pady=20)           

    def show_custom_report_popup(self, text_content):
        """Creates a professional scrollable window for the shift report."""
        top = tk.Toplevel(self.root)
        top.title("Shift Production Summary")
        top.geometry("700x500")
        top.configure(bg=C_BG)

        # Header
        tk.Label(top, text="LIVE PRODUCTION LOG", fg="white", bg=C_BG, 
                font=("Segoe UI", 16, "bold")).pack(pady=10)

        # Scrollable Text Area
        txt_frame = tk.Frame(top, bg=C_BG)
        txt_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        scr = tk.Scrollbar(txt_frame)
        scr.pack(side="right", fill="y")
        
        # Using a Monospaced font (Courier) is critical so the columns stay aligned
        display = tk.Text(txt_frame, bg="#0F3460", fg="white", font=("Courier New", 11),
                        yscrollcommand=scr.set, wrap="none", padx=10, pady=10)
        display.insert("1.0", text_content)
        display.config(state="disabled") # Prevent operator from editing the report
        display.pack(side="left", fill="both", expand=True)
        scr.config(command=display.yview)

        # Close Button
        tk.Button(top, text="CLOSE", command=top.destroy, bg="#C0392B", fg="white",
                font=("Segoe UI", 12, "bold"), width=15).pack(pady=15)    

    def export_shift_to_csv(self):
        """Fetches shift data and saves it with perfect column alignment."""
        shift = self._get_shift()
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        filename = f"Shift_{shift}_Report_{today}.csv"
        
        # 1. The SQL query returns exactly 10 columns
        q = """
            SELECT 
                b_id, press_id, daylight, tyre_size, quality, 
                green_tyre_weight, ms_rim_weight, status, operator_id, birth_time
            FROM pc1_building 
            WHERE date(created_at) = CURRENT_DATE AND shift = %s
            ORDER BY birth_time DESC
        """
        res = DBManager.fetch_data(q, (shift,))
        
        if not res:
            return messagebox.showinfo("Export", "No data found to export.")

        try:
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                
                # 2. The Header Row now matches the 10 columns perfectly
                # Note: Combined 'Green Weight' into one header to prevent shifting
                writer.writerow([
                    'B-ID', 'Press', 'Daylight', 'Size', 'Grade', 
                    'Green Weight (kg)', 'Rim Weight (kg)', 'Status', 'Operator', 'Time'
                ])
                
                # 3. Write the data
                for r in res:
                    writer.writerow(r)
            
            messagebox.showinfo("Export Success ✅", f"Report saved to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Could not save CSV: {e}")