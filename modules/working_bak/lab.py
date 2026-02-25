import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from db_manager import DBManager

C_BG = "#F4F6F7"
C_CARD = "#FFFFFF"
C_HEADER = "#8E44AD"   # Purple for Lab
C_SUCCESS = "#27AE60"
C_ERR = "#C0392B"

class LabQCApp:
    def __init__(self, root, current_user="LAB_TECH"):
        self.root = root
        self.root.title(f"Factory Lab | Raw Material QC (User: {current_user})")
        self.root.geometry("1200x700")
        self.root.configure(bg=C_BG)
        self.current_user = current_user

        # Variables
        self.var_mat_type = tk.StringVar(value="CORE")
        self.var_status = tk.StringVar(value="APPROVED")
        
        # Single Entry Vars
        self.var_single_batch = tk.StringVar()
        
        # Range Entry Vars
        self.var_prefix = tk.StringVar()
        self.var_start_num = tk.StringVar()
        self.var_end_num = tk.StringVar()

        self.setup_ui()
        self.load_recent_batches()

    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg=C_HEADER, height=70)
        header.pack(fill="x")
        tk.Label(header, text="🧪 FACTORY LAB - MATERIAL APPROVAL", font=("Segoe UI", 20, "bold"), bg=C_HEADER, fg="white").pack(pady=15)

        content = tk.Frame(self.root, bg=C_BG)
        content.pack(fill="both", expand=True, padx=20, pady=20)

        # ================= LEFT: ENTRY FORMS =================
        left_f = tk.Frame(content, bg=C_BG, width=450)
        left_f.pack(side="left", fill="y", padx=(0, 10))

        # 1. Global Settings
        card_setup = self.create_card(left_f, "1. MATERIAL TYPE & STATUS")
        tk.Label(card_setup, text="Compound / Material:", bg=C_CARD, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.combo_mat = ttk.Combobox(card_setup, textvariable=self.var_mat_type, font=("Segoe UI", 12), state="readonly")
        self.combo_mat['values'] = ["CORE", "MIDDLE", "VT001", "VT002", "VT003", "NMW", "GUM"]
        self.combo_mat.pack(fill="x", pady=(0, 10))

        tk.Label(card_setup, text="Lab Decision:", bg=C_CARD, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        f_rad = tk.Frame(card_setup, bg=C_CARD)
        f_rad.pack(fill="x", pady=5)
        tk.Radiobutton(f_rad, text="✅ APPROVED", variable=self.var_status, value="APPROVED", bg=C_CARD, fg=C_SUCCESS, font=("Segoe UI", 10, "bold")).pack(side="left", padx=10)
        tk.Radiobutton(f_rad, text="❌ REJECTED", variable=self.var_status, value="REJECTED", bg=C_CARD, fg=C_ERR, font=("Segoe UI", 10, "bold")).pack(side="left", padx=10)

        # 2. Single Batch Mode
        card_single = self.create_card(left_f, "2A. SINGLE BATCH ENTRY")
        tk.Label(card_single, text="Scan/Type Batch No:", bg=C_CARD, font=("Segoe UI", 9)).pack(anchor="w")
        self.ent_single = tk.Entry(card_single, textvariable=self.var_single_batch, font=("Segoe UI", 14), bg="#EAF2F8")
        self.ent_single.pack(fill="x", pady=5)
        tk.Button(card_single, text="💾 SAVE SINGLE BATCH", command=self.save_single, bg="#2980B9", fg="white", font=("Segoe UI", 10, "bold")).pack(fill="x", pady=5)

        # 3. Range Batch Mode
        card_range = self.create_card(left_f, "2B. BULK RANGE APPROVAL")
        tk.Label(card_range, text="Common Prefix (e.g., 'VT01-B'):", bg=C_CARD, font=("Segoe UI", 9)).pack(anchor="w")
        tk.Entry(card_range, textvariable=self.var_prefix, font=("Segoe UI", 12), bg="#FEF9E7").pack(fill="x", pady=2)
        
        f_nums = tk.Frame(card_range, bg=C_CARD)
        f_nums.pack(fill="x", pady=5)
        tk.Label(f_nums, text="Start No:", bg=C_CARD, font=("Segoe UI", 9)).pack(side="left")
        tk.Entry(f_nums, textvariable=self.var_start_num, font=("Segoe UI", 12), width=10).pack(side="left", padx=5)
        tk.Label(f_nums, text="End No:", bg=C_CARD, font=("Segoe UI", 9)).pack(side="left")
        tk.Entry(f_nums, textvariable=self.var_end_num, font=("Segoe UI", 12), width=10).pack(side="left", padx=5)
        
        tk.Button(card_range, text="🚀 GENERATE & SAVE RANGE", command=self.save_range, bg="#8E44AD", fg="white", font=("Segoe UI", 10, "bold")).pack(fill="x", pady=10)

        # ================= RIGHT: LIVE INVENTORY =================
        right_f = self.create_card(content, "📋 LIVE BATCH INVENTORY")
        right_f.pack(side="right", fill="both", expand=True)

        cols = ("Batch No", "Material Type", "Status")
        self.tree = ttk.Treeview(right_f, columns=cols, show="headings", height=20)
        for c in cols: self.tree.heading(c, text=c)
        self.tree.column("Batch No", width=200)
        self.tree.column("Material Type", width=150, anchor="center")
        self.tree.column("Status", width=100, anchor="center")
        
        self.tree.tag_configure('APPROVED', background='#EAFAF1')
        self.tree.tag_configure('REJECTED', background='#FDEDEC', foreground='#C0392B')
        
        self.tree.pack(fill="both", expand=True, pady=10)
        
        f_btns = tk.Frame(right_f, bg=C_CARD)
        f_btns.pack(fill="x")
        tk.Button(f_btns, text="🗑️ Delete Selected", command=self.delete_batch, bg=C_ERR, fg="white").pack(side="left", padx=5)
        tk.Button(f_btns, text="🔄 Refresh List", command=self.load_recent_batches, bg="#34495E", fg="white").pack(side="right", padx=5)

    # --- LOGIC ---
    def save_single(self):
        batch = self.var_single_batch.get().strip().upper()
        mat = self.var_mat_type.get()
        stat = self.var_status.get()

        if not batch: return messagebox.showerror("Error", "Enter a Batch No.", parent=self.root)

        q = """INSERT INTO raw_material_qc (batch_no, material_type, status) 
               VALUES (%s, %s, %s) 
               ON CONFLICT (batch_no) DO UPDATE 
               SET material_type=EXCLUDED.material_type, status=EXCLUDED.status"""
               
        if DBManager.execute_query(q, (batch, mat, stat)):
            self.var_single_batch.set("")
            self.load_recent_batches()
            self.ent_single.focus_set() # Keep focus for fast barcode scanning

    def save_range(self):
        prefix = self.var_prefix.get().strip().upper()
        try:
            start = int(self.var_start_num.get().strip())
            end = int(self.var_end_num.get().strip())
        except ValueError:
            return messagebox.showerror("Error", "Start and End numbers must be integers.", parent=self.root)

        if start > end: return messagebox.showerror("Error", "Start number must be less than End number.", parent=self.root)
        if (end - start) > 500: return messagebox.showwarning("Limit", "Please generate ranges of 500 or less to prevent locking.", parent=self.root)

        mat = self.var_mat_type.get()
        stat = self.var_status.get()
        
        if not messagebox.askyesno("Confirm Bulk", f"Generate and mark {end-start+1} batches as {stat}?\n\nFrom: {prefix}{start}\nTo: {prefix}{end}", parent=self.root):
            return

        q = """INSERT INTO raw_material_qc (batch_no, material_type, status) 
               VALUES (%s, %s, %s) 
               ON CONFLICT (batch_no) DO UPDATE 
               SET material_type=EXCLUDED.material_type, status=EXCLUDED.status"""
               
        count = 0
        conn = DBManager.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                for i in range(start, end + 1):
                    batch = f"{prefix}{i}"
                    cursor.execute(q, (batch, mat, stat))
                    count += 1
                conn.commit()
                cursor.close()
                self.var_start_num.set(""); self.var_end_num.set("")
                self.load_recent_batches()
                messagebox.showinfo("Success", f"Bulk uploaded {count} batches!", parent=self.root)
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Database Error", str(e), parent=self.root)
            finally:
                DBManager.return_connection(conn)

    def load_recent_batches(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        # Fetch the latest 100 batches to keep the UI fast
        res = DBManager.fetch_data("SELECT batch_no, material_type, status FROM raw_material_qc ORDER BY batch_no DESC LIMIT 100")
        if res:
            for r in res:
                self.tree.insert("", "end", values=r, tags=(r[2],))

    def delete_batch(self):
        sel = self.tree.selection()
        if not sel: return messagebox.showwarning("Warning", "Select a batch to delete.", parent=self.root)
        
        batch = self.tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirm", f"Delete batch {batch}?", parent=self.root):
            if DBManager.execute_query("DELETE FROM raw_material_qc WHERE batch_no=%s", (batch,)):
                self.load_recent_batches()

    def create_card(self, parent, title): 
        f = tk.Frame(parent, bg=C_CARD, bd=1, relief="solid", padx=15, pady=15)
        f.pack(fill="x", pady=10)
        tk.Label(f, text=title, font=("Segoe UI", 11, "bold"), bg=C_CARD, fg=C_HEADER).pack(anchor="w", pady=(0, 10))
        return f

if __name__ == "__main__":
    root = tk.Tk()
    app = LabQCApp(root)
    root.mainloop()