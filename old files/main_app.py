import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# --- MODERN COLOR PALETTE ---
C_BG = "#1A1A2E"        # Deep Midnight Blue
C_CARD = "#16213E"      # Dark Navy Card
C_ACCENT = "#E74C3C"    # Red Accent for Login
C_TEXT = "#E1E1E1"      # Off-white
C_HIGHLIGHT = "#0F3460" # Subtle Darker Blue
C_NAVY_ACCENT = "#3282B8" # Steel Blue

# --- MODULE IMPORTS (Safe Mode) ---
try:
    from db_manager import DBManager
except ImportError as e:
    print(f"CRITICAL ERROR: DBManager not found. {e}")

# Sub-modules
modules = {
    "PC1": ("modules.building", "PC1SmartApp"),
    "PC2": ("modules.curing", "CuringApp"),
    "PC3": ("modules.qc", "FinalQCApp"),
    "PC4": ("modules.despatch", "DespatchApp"),
    "LAB": ("modules.lab", "LabQCApp"),
    "ADMIN": ("modules.admin_dashboard", "AdminDashboard")
}

# Dynamically import and handle missing modules
for key, (path, attr) in modules.items():
    try:
        mod = __import__(path, fromlist=[attr])
        globals()[attr] = getattr(mod, attr)
    except Exception as e:
        globals()[attr] = None
        print(f"⚠️ {key} Module ({path}) missing or has errors: {e}")

class MainLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Tyre Factory | Main System Launcher")
        self.root.geometry("1200x800")
        self.root.configure(bg=C_BG)

        self.current_user_name = "ADMIN"
        self.current_role = "ADMIN"
        self.user_map = {}

        self.setup_login_ui()

    def setup_login_ui(self):
        for widget in self.root.winfo_children(): widget.destroy()
        self.root.configure(bg=C_BG)

        # Header
        tk.Label(self.root, text="🏭 FACTORY SMART SYSTEM", font=("Segoe UI", 24, "bold"), bg=C_BG, fg="white").pack(pady=(50, 10))
        tk.Label(self.root, text="Production & Traceability Suite", font=("Segoe UI", 12), bg=C_BG, fg="#BDC3C7").pack(pady=(0, 30))

        # Login Card
        f_login = tk.Frame(self.root, bg="white", padx=40, pady=40, bd=0)
        f_login.pack(padx=20, pady=10)

        tk.Label(f_login, text="Select User Profile:", font=("Segoe UI", 11, "bold"), bg="white", fg="#2C3E50").pack(anchor="w")
        self.combo_user = ttk.Combobox(f_login, font=("Segoe UI", 14), width=30, state="readonly")
        self.combo_user.pack(pady=15)

        tk.Label(f_login, text="Password:", font=("Segoe UI", 11, "bold"), bg="white", fg="#2C3E50").pack(anchor="w", pady=(10, 0))
        self.var_password = tk.StringVar()
        self.ent_password = tk.Entry(f_login, textvariable=self.var_password, font=("Segoe UI", 14), width=30, show="*")
        self.ent_password.pack(pady=5)
        
        # UI Polish: Auto-focus and Enter-key Binding
        self.ent_password.focus_set()
        self.ent_password.bind("<Return>", lambda event: self.do_login())

        btn = tk.Button(f_login, text="🔓 SECURE LOGIN", bg=C_ACCENT, fg="white", font=("Segoe UI", 12, "bold"), 
                        width=25, command=self.do_login, relief="flat", cursor="hand2")
        btn.pack(pady=20)
        
        self.lbl_status = tk.Label(self.root, text="Connecting to DB...", bg=C_BG, fg="#95A5A6", font=("Segoe UI", 9))
        self.lbl_status.pack(side="bottom", pady=10)

        self.root.after(500, self.load_users)

    def load_users(self):
        try:
            if not DBManager.get_connection(): raise Exception("No Connection")
            query = "SELECT user_id, full_name, role, password FROM users WHERE is_active=TRUE ORDER BY role, full_name"
            res = DBManager.fetch_data(query)
            
            self.user_map = {}
            display_list = []
            if res:
                for uid, name, role, pwd in res:
                    display_text = f"{role} | {name} ({uid})"
                    self.user_map[display_text] = (uid, name, role, pwd)
                    display_list.append(display_text)
                self.combo_user['values'] = display_list
                if display_list: self.combo_user.current(0)
                self.lbl_status.config(text="✅ Database Connected", fg="#2ECC71")
            else:
                self.load_fallback_user()
        except Exception as e:
            self.load_fallback_user()
            self.lbl_status.config(text="⚠️ Offline Mode / DB Error", fg="#F1C40F")

    def load_fallback_user(self):
        fallback = "ADMIN | System Admin (LOCAL)"
        self.user_map = {fallback: ("ADMIN", "System Admin", "ADMIN", "1234")} 
        self.combo_user['values'] = [fallback]
        self.combo_user.current(0)

    def do_login(self):
        selection = self.combo_user.get()
        typed_password = self.var_password.get()
        user_data = self.user_map.get(selection)

        if user_data:
            uid, name, role, db_password = user_data
            if typed_password == str(db_password):
                self.current_user_name = name
                self.current_role = role
                self.open_main_menu()
            else:
                messagebox.showerror("Access Denied", "Incorrect Password!")
                self.var_password.set("")

    def open_main_menu(self):
        for widget in self.root.winfo_children(): widget.destroy()
        self.root.configure(bg=C_BG)
        
        # Top Nav Bar
        header = tk.Frame(self.root, bg=C_HIGHLIGHT, height=60)
        header.pack(fill="x")
        tk.Label(header, text=f"👤 {self.current_user_name}", font=("Segoe UI", 12, "bold"), 
                 bg=C_HIGHLIGHT, fg="white").pack(side="left", padx=30)
        tk.Button(header, text="LOGOUT", command=self.setup_login_ui, bg="#E74C3C", fg="white", 
                  font=("Segoe UI", 9, "bold"), relief="flat", padx=15).pack(side="right", padx=20, pady=10)

        # Content Title
        tk.Label(self.root, text="FACTORY CONTROL CENTER", font=("Segoe UI", 22, "bold"), 
                 bg=C_BG, fg=C_TEXT).pack(pady=(40,10))

        f_grid = tk.Frame(self.root, bg=C_BG)
        f_grid.pack(expand=True)

        # Card Config
        stations = [
            ("🏗️", "PC1 - BUILDING", "#27AE60", self.launch_building, True),
            ("🔥", "PC2 - CURING", "#E67E22", self.launch_curing, True),
            ("🛡️", "PC3 - FINAL QC", "#2980B9", self.launch_qc, self.current_role in ["SUPERVISOR", "MANAGER", "ADMIN", "QC"]),
            ("🚚", "PC4 - DESPATCH", "#34495E", self.launch_despatch, self.current_role in ["LOGISTICS", "SUPERVISOR", "MANAGER", "ADMIN", "QC"]),
            ("🧪", "LAB - APPROVAL", "#8E44AD", self.launch_lab, self.current_role in ["QC", "SUPERVISOR", "MANAGER", "ADMIN"]),
            ("⚙️", "ADMIN PANEL", "#34495E", self.launch_admin, self.current_role in ["MANAGER", "ADMIN"])
        ]

        r, c = 0, 0
        for icon, label, color, cmd, has_perm in stations:
            if has_perm:
                self.create_modern_card(f_grid, icon, label, color, cmd, r, c)
                c += 1
                if c > 2:
                    c = 0; r += 1

    def create_modern_card(self, parent, icon, label, color, command, r, c):
        card = tk.Frame(parent, bg=C_CARD, highlightthickness=1, highlightbackground=color)
        card.grid(row=r, column=c, padx=15, pady=15)
        
        btn = tk.Button(card, text=f"{icon}\n{label}", font=("Segoe UI", 12, "bold"), bg=C_CARD, fg="white",
                       width=20, height=5, relief="flat", command=command, cursor="hand2",
                       activebackground=color)
        btn.pack()
        tk.Frame(card, bg=color, height=5).pack(fill="x", side="bottom")

    # --- LAUNCHERS ---
    def launch_building(self): self._launch(PC1SmartApp, "PC1")
    def launch_curing(self): self._launch(CuringApp, "PC2", True)
    def launch_qc(self): self._launch(FinalQCApp, "PC3", True)
    def launch_despatch(self): self._launch(DespatchApp, "PC4", True)
    def launch_lab(self): self._launch(LabQCApp, "LAB", True)
    def launch_admin(self): self._launch(AdminDashboard, "ADMIN")

    def _launch(self, app_class, name, pass_user=False):
        if app_class:
            win = tk.Toplevel(self.root)
            if pass_user: app_class(win, current_user=self.current_user_name)
            else: app_class(win)
        else:
            messagebox.showerror("Error", f"{name} Module missing or corrupted!")

if __name__ == "__main__":
    root = tk.Tk()
    
    # --- CROSS-PLATFORM MAXIMIZE ---
    if sys.platform == "win32":
        root.state('zoomed') # Works on Windows
    else:
        root.attributes('-zoomed', True) # Works on Linux (Ubuntu/Raspberry Pi)
    
    app = MainLauncher(root)
    root.mainloop()