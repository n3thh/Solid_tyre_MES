import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

try:
    from modules.despatch import DespatchApp
except ImportError as e:
    DespatchApp = None
    print(f"⚠️ PC4 Module missing or has errors: {e}")

# --- ATTEMPT IMPORTS (Safe Mode) ---
# This prevents the Main App from crashing if a sub-module has an error
try:
    from db_manager import DBManager
except ImportError as e:
    print(f"CRITICAL ERROR: DBManager not found. {e}")

# We import these inside the functions or wrap them to catch errors early
try:
    from modules.building import PC1SmartApp
except ImportError:
    PC1SmartApp = None
    print("⚠️ PC1 Module missing or has errors")

try:
    from modules.curing import CuringApp
except ImportError:
    CuringApp = None
    print("⚠️ PC2 Module missing or has errors")

try:
    from modules.qc import FinalQCApp
except ImportError:
    FinalQCApp = None
    print("⚠️ PC3 Module missing or has errors")

try:
    from modules.admin_dashboard import AdminDashboard
except ImportError as e:
    AdminDashboard = None
    print(f"⚠️ Admin Module missing or has errors: {e}")

# CONFIGURATION
C_BG = "#2C3E50"       # Dark Blue Background
C_ACCENT = "#E74C3C"   # Red Accent
C_TEXT = "#ECF0F1"     # White    Text

class MainLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Tyre Factory | Main System Launcher")
        self.root.geometry("600x500")
        self.root.configure(bg=C_BG)

        self.current_user_name = "ADMIN"
        self.current_role = "ADMIN"
        self.user_map = {}

        self.setup_login_ui()

    def setup_login_ui(self):
        # Clear existing widgets (if returning from logout)
        for widget in self.root.winfo_children():
            widget.destroy()

        # Header
        tk.Label(self.root, text="🏭 FACTORY SMART SYSTEM", font=("Segoe UI", 24, "bold"), bg=C_BG, fg="white").pack(pady=(50, 10))
        tk.Label(self.root, text="Production & Traceability Suite", font=("Segoe UI", 12), bg=C_BG, fg="#BDC3C7").pack(pady=(0, 30))

        # Login Card
        f_login = tk.Frame(self.root, bg="white", padx=40, pady=40, bd=2, relief="solid")
        f_login.pack(padx=20, pady=10)

        tk.Label(f_login, text="Select User Profile:", font=("Segoe UI", 11, "bold"), bg="white", fg="#2C3E50").pack(anchor="w")
        
        # User Dropdown
        self.combo_user = ttk.Combobox(f_login, font=("Segoe UI", 14), width=30, state="readonly")
        self.combo_user.pack(pady=15)

        # Password Input
        tk.Label(f_login, text="Password:", font=("Segoe UI", 11, "bold"), bg="white", fg="#2C3E50").pack(anchor="w", pady=(10, 0))
        self.var_password = tk.StringVar()
        self.ent_password = tk.Entry(f_login, textvariable=self.var_password, font=("Segoe UI", 14), width=30, show="*")
        self.ent_password.pack(pady=5)
        
        # Login Button
        btn = tk.Button(f_login, text="🔓 SECURE LOGIN", bg=C_ACCENT, fg="white", font=("Segoe UI", 12, "bold"), 
                        width=25, command=self.do_login, relief="flat")
        btn.pack(pady=10)
        
        # Status Footer
        self.lbl_status = tk.Label(self.root, text="Connecting to DB...", bg=C_BG, fg="#95A5A6", font=("Segoe UI", 9))
        self.lbl_status.pack(side="bottom", pady=10)

        # Load Data
        self.root.after(500, self.load_users)

    def load_users(self):
        try:
            # Check DB Connection
            if not DBManager.get_connection():
                raise Exception("No Connection")

            # Fetch active users including passwords
            query = "SELECT user_id, full_name, role, password FROM users WHERE is_active=TRUE ORDER BY role, full_name"
            res = DBManager.fetch_data(query)
            
            self.user_map = {}
            display_list = []

            if res:
                for r in res:
                    uid, name, role, pwd = r
                    display_text = f"{role} | {name} ({uid})"
                    # We now store the password in the map as well
                    self.user_map[display_text] = (uid, name, role, pwd)
                    display_list.append(display_text) # <-- This was the missing piece!
                
                self.combo_user['values'] = display_list
                if display_list:
                    self.combo_user.current(0)
                self.lbl_status.config(text="✅ Database Connected", fg="#2ECC71")
            else:
                self.load_fallback_user()

        except Exception as e:
            print(f"DB Error: {e}")
            self.load_fallback_user()
            self.lbl_status.config(text="⚠️ Offline Mode / DB Error", fg="#F1C40F")

    def load_fallback_user(self):
        # Fallback if DB fails so you can still test UI
        fallback = "ADMIN | System Admin (LOCAL)"
        # ADDED "1234" as the 4th value so unpacking works!
        self.user_map = {fallback: ("ADMIN", "System Admin", "ADMIN", "1234")} 
        self.combo_user['values'] = [fallback]
        self.combo_user.current(0)

    def do_login(self):
        selection = self.combo_user.get()
        typed_password = self.var_password.get()

        if not selection:
            messagebox.showwarning("Login", "Please select a user first.")
            return

        user_data = self.user_map.get(selection)
        if user_data:
            # Unpack the 4 variables now
            uid, name, role, db_password = user_data
            
            # Verify Password
            if typed_password != db_password:
                messagebox.showerror("Access Denied", "Incorrect Password!")
                self.var_password.set("") # Clear the box
                return

            # If password is correct, proceed
            self.current_user_name = name
            self.current_role = role
            self.open_main_menu()

    def open_main_menu(self):
        for widget in self.root.winfo_children(): widget.destroy()
        
        # Header
        header = tk.Frame(self.root, bg="#34495E", height=80)
        header.pack(fill="x")
        tk.Label(header, text=f"👤 {self.current_user_name}", font=("Segoe UI", 14, "bold"), bg="#34495E", fg="white").pack(side="left", padx=20)
        tk.Label(header, text=f"ROLE: {self.current_role}", font=("Segoe UI", 10, "bold"), bg="#34495E", fg="#F1C40F").pack(side="right", padx=20)

        tk.Label(self.root, text="SELECT WORKSTATION", font=("Segoe UI", 16, "bold"), bg=C_BG, fg="white").pack(pady=(40,20))

        # Menu Buttons
        f_menu = tk.Frame(self.root, bg=C_BG)
        f_menu.pack(pady=10)

        # 1. PC1 - BUILDING (Operators + Admin)
        self.create_menu_btn(f_menu, "🏗️ PC1 - BUILDING STATION", "#27AE60", self.launch_building)

        # 2. PC2 - CURING (Operators + Admin)
        self.create_menu_btn(f_menu, "🔥 PC2 - CURING STATION", "#E67E22", self.launch_curing)

        # 3. PC3 - QC (QC + Admin)
        if self.current_role in ["SUPERVISOR", "MANAGER", "ADMIN", "QC"]:
            self.create_menu_btn(f_menu, "🛡️ PC3 - FINAL QC", "#8E44AD", self.launch_qc)

        # 4. PC4 - DESPATCH (Logistics, QC + Admin)
        if self.current_role in ["LOGISTICS", "SUPERVISOR", "MANAGER", "ADMIN", "QC"]:
            self.create_menu_btn(f_menu, "🚚 PC4 - DESPATCH MANAGER", "#34495E", self.launch_despatch)


        # 5. ADMIN DASHBOARD (Admin Only)
        if self.current_role in ["MANAGER", "ADMIN"]:
            self.create_menu_btn(f_menu, "⚙️ ADMIN DASHBOARD & SETUP", "#2C3E50", self.launch_admin)

        

        # Logout
        tk.Button(self.root, text="⬅ LOGOUT", command=self.setup_login_ui, bg="#95A5A6", fg="white", font=("Segoe UI", 10)).pack(side="bottom", pady=30)

    def create_menu_btn(self, parent, text, color, command):
        btn = tk.Button(parent, text=text, bg=color, fg="white", font=("Segoe UI", 14, "bold"), width=35, height=2, command=command, relief="flat", cursor="hand2")
        btn.pack(pady=8)

    # --- LAUNCHERS ---
    def launch_building(self):
        if PC1SmartApp:
            win = tk.Toplevel(self.root)
            app = PC1SmartApp(win)
        else:
            messagebox.showerror("Error", "Building Module (modules/building.py) missing!")

    def launch_curing(self):
        if CuringApp:
            win = tk.Toplevel(self.root)
            # Pass the logged-in user's name
            app = CuringApp(win, current_user=self.current_user_name)
        else:
            messagebox.showerror("Error", "Curing Module (modules/curing.py) missing!")

    def launch_qc(self):
        if FinalQCApp:
            win = tk.Toplevel(self.root)
            app = FinalQCApp(win, current_user=self.current_user_name)
        else:
            messagebox.showerror("Error", "QC Module (modules/qc.py) missing!")

    def launch_despatch(self):
        if DespatchApp:
            win = tk.Toplevel(self.root)
            app = DespatchApp(win, current_user=self.current_user_name)
        else:
            messagebox.showerror("Error", "Despatch Module (modules/despatch.py) missing or has errors!")        

    def launch_admin(self):
        if AdminDashboard:
            win = tk.Toplevel(self.root)
            app = AdminDashboard(win)
        else:
            messagebox.showerror("Error", "Admin Module (modules/admin_dashboard.py) missing or has errors!")

if __name__ == "__main__":
    root = tk.Tk()
    app = MainLauncher(root)
    root.mainloop()