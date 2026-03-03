import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import csv
from db_manager import DBManager

# Professional Lab Palette
C_BG = "#F4F6F7"
C_CARD = "#FFFFFF"
C_HEADER = "#8E44AD"   # Purple for Lab
C_SUCCESS = "#27AE60"
C_WARN = "#F39C12"
C_ERR = "#C0392B"

class LabQCApp:
    def __init__(self, root, current_user="LAB_TECH"):
        self.root = root
        self.root.title(f"Factory Lab | Raw Material QC (User: {current_user})")
        self.root.geometry("1300x800")
        self.root.configure(bg=C_BG)
        self.current_user = current_user
        
        self.ensure_db_schema()

        # --- Materials List ---
        self.materials = ["CORE", "MIDDLE", "VT001", "VT002", "VT003", "NMW", "GUM"]
        self.qc_trees = {} # Dictionary to hold the Treeviews for each material

        # --- Variables ---
        self.var_mat_type = tk.StringVar(value="CORE")
        self.var_status = tk.StringVar(value="PENDING")
        self.var_single_batch = tk.StringVar()
        self.var_prefix = tk.StringVar()
        self.var_start_num = tk.StringVar()
        self.var_end_num = tk.StringVar()
        self.ent_search_qc = None

        self.setup_ui()
        self.refresh_all_lists()

    def ensure_db_schema(self):
        query = """
            CREATE TABLE IF NOT EXISTS raw_material_qc (
                batch_no VARCHAR(100) PRIMARY KEY,
                material_type VARCHAR(50),
                status VARCHAR(20),
                updated_at TIMESTAMP DEFAULT NOW()
            );
        """
        DBManager.execute_query(query)

    def setup_ui(self):
        header = tk.Frame(self.root, bg=C_HEADER, height=70)
        header.pack(fill="x")
        tk.Label(header, text="🧪 FACTORY LAB COMMAND CENTER", font=("Segoe UI", 20, "bold"), bg=C_HEADER, fg="white").pack(pady=15)

        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill="both", expand=True, padx=10, pady=10)

        # 1. BATCH ENTRY TAB
        self.tab_entry = tk.Frame(self.nb, bg=C_BG)
        self.nb.add(self.tab_entry, text=" 📦 BATCH ENTRY ")
        self.build_entry_interface()

        # 2. DYNAMIC MATERIAL TABS (Core, Middle, VT001, etc.)
        for mat in self.materials:
            tab = tk.Frame(self.nb, bg=C_BG)
            self.nb.add(tab, text=f" {mat} ")
            self.build_material_tab(tab, mat)

        # 3. QC HISTORY TAB
        self.tab_records = tk.Frame(self.nb, bg=C_BG)
        self.nb.add(self.tab_records, text=" 📜 QC HISTORY ")
        self.build_records_interface()

    # ================= TAB 1: BATCH ENTRY =================
    def build_entry_interface(self):
        content = tk.Frame(self.tab_entry, bg=C_BG)
        content.pack(fill="both", expand=True, padx=20, pady=20)

        left_f = tk.Frame(content, bg=C_BG, width=450)
        left_f.pack(side="left", fill="y", padx=(0, 10))

        # 1. Global Settings
        card_setup = self.create_card(left_f, "1. MATERIAL TYPE")
        tk.Label(card_setup, text="Compound / Material:", bg=C_CARD, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.combo_mat = ttk.Combobox(card_setup, textvariable=self.var_mat_type, font=("Segoe UI", 12), state="readonly")
        self.combo_mat['values'] = self.materials
        self.combo_mat.pack(fill="x", pady=(0, 10))

        # 2. Single Batch
        card_single = self.create_card(left_f, "2A. SINGLE ENTRY")
        tk.Label(card_single, text="Scan/Type Batch No:", bg=C_CARD, font=("Segoe UI", 9)).pack(anchor="w")
        self.ent_single = tk.Entry(card_single, textvariable=self.var_single_batch, font=("Segoe UI", 14), bg="#EAF2F8")
        self.ent_single.pack(fill="x", pady=5)
        tk.Button(card_single, text="💾 SAVE SINGLE BATCH", command=self.save_single, bg="#2980B9", fg="white", font=("Segoe UI", 10, "bold")).pack(fill="x", pady=5)

        # 3. Bulk Entry
        card_range = self.create_card(left_f, "2B. BULK RANGE ENTRY")
        tk.Label(card_range, text="Prefix (e.g., 'VT01-B'):", bg=C_CARD, font=("Segoe UI", 9)).pack(anchor="w")
        tk.Entry(card_range, textvariable=self.var_prefix, font=("Segoe UI", 12), bg="#FEF9E7").pack(fill="x", pady=2)
        
        f_nums = tk.Frame(card_range, bg=C_CARD)
        f_nums.pack(fill="x", pady=5)
        tk.Label(f_nums, text="Start No:", bg=C_CARD, font=("Segoe UI", 9)).pack(side="left")
        tk.Entry(f_nums, textvariable=self.var_start_num, font=("Segoe UI", 12), width=10).pack(side="left", padx=5)
        tk.Label(f_nums, text="End No:", bg=C_CARD, font=("Segoe UI", 9)).pack(side="left")
        tk.Entry(f_nums, textvariable=self.var_end_num, font=("Segoe UI", 12), width=10).pack(side="left", padx=5)
        
        tk.Button(card_range, text="🚀 GENERATE BULK RANGE", command=self.save_range, bg=C_HEADER, fg="white", font=("Segoe UI", 10, "bold")).pack(fill="x", pady=10)

        # Right: Live Inventory (Shows everything)
        right_f = self.create_card(content, "📋 RECENTLY ENTERED BATCHES (ALL)")
        right_f.pack(side="right", fill="both", expand=True)

        cols = ("Batch No", "Material Type", "Status")
        self.tree_entry = ttk.Treeview(right_f, columns=cols, show="headings", height=20)
        for c in cols: self.tree_entry.heading(c, text=c)
        self.tree_entry.column("Batch No", width=200)
        self.tree_entry.column("Material Type", width=150, anchor="center")
        self.tree_entry.column("Status", width=100, anchor="center")
        self.tree_entry.pack(fill="both", expand=True, pady=10)
        
        f_btns = tk.Frame(right_f, bg=C_CARD)
        f_btns.pack(fill="x")
        tk.Button(f_btns, text="🗑️ Delete Selected", command=self.delete_batch, bg=C_ERR, fg="white").pack(side="left", padx=5)

    # ================= DYNAMIC MATERIAL TABS =================
    def build_material_tab(self, parent_frame, material_name):
        """Generates a dedicated touch interface for ONE specific material."""
        list_frame = tk.Frame(parent_frame, bg="white", bd=1, relief="solid")
        list_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        # Notice: We don't need a "Material" column here because the whole tab is dedicated to it.
        cols = ("Batch No", "Status", "Last Updated")
        tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=20)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, anchor="center")
        
        tree.pack(fill="both", expand=True)
        
        # Color coding for the specific material tree
        tree.tag_configure('APPROVED', background='#EAFAF1')
        tree.tag_configure('REJECTED', background='#FDEDEC', foreground='#C0392B')
        tree.tag_configure('HOLD', background='#FEF9E7', foreground='#B9770E')
        
        # Save this specific tree to our dictionary so we can update it later
        self.qc_trees[material_name] = tree

        # Action Buttons specific to this material
        btn_frame = tk.Frame(parent_frame, bg=C_BG, width=300)
        btn_frame.pack(side="right", fill="y", padx=20, pady=20)

        tk.Label(btn_frame, text=f"{material_name} DECISION", font=("Segoe UI", 16, "bold"), bg=C_BG).pack(pady=20)
        
        # The 'lambda m=material_name' ensures the button knows exactly which tab it belongs to
        tk.Button(btn_frame, text="✅ PASS", command=lambda m=material_name: self.log_qc(m, "APPROVED"), bg=C_SUCCESS, fg="white", font=("Segoe UI", 20, "bold"), height=3, width=12).pack(pady=10)
        tk.Button(btn_frame, text="⚠️ HOLD", command=lambda m=material_name: self.log_qc(m, "HOLD"), bg=C_WARN, fg="white", font=("Segoe UI", 18, "bold"), height=2, width=12).pack(pady=10)
        tk.Button(btn_frame, text="❌ REJECT", command=lambda m=material_name: self.log_qc(m, "REJECTED"), bg=C_ERR, fg="white", font=("Segoe UI", 18, "bold"), height=2, width=12).pack(pady=10)

    # ================= TAB: QC HISTORY =================
    def build_records_interface(self):
        search_f = tk.Frame(self.tab_records, bg=C_BG, pady=10)
        search_f.pack(fill="x")
        
        tk.Label(search_f, text="🔍 BATCH:", font=("Segoe UI", 10, "bold"), bg=C_BG).pack(side="left", padx=(20, 5))
        self.ent_search_qc = tk.Entry(search_f, font=("Segoe UI", 12), width=20)
        self.ent_search_qc.pack(side="left", padx=5)
        
        tk.Button(search_f, text="SEARCH", command=self.search_qc_history, bg=C_HEADER, fg="white").pack(side="left", padx=5)
        tk.Button(search_f, text="📥 EXPORT CSV", command=self.export_qc_csv, bg=C_SUCCESS, fg="white").pack(side="right", padx=20)

        card = tk.Frame(self.tab_records, bg="white", bd=1, relief="solid")
        card.pack(fill="both", expand=True, padx=20, pady=10)

        cols = ("Batch No", "Material", "Status", "Timestamp")
        self.tree_history = ttk.Treeview(card, columns=cols, show="headings")
        for c in cols:
            self.tree_history.heading(c, text=c)
            self.tree_history.column(c, anchor="center")
        self.tree_history.pack(fill="both", expand=True)

    # ================= LOGIC & DATABASE =================
    def save_single(self):
        batch = self.var_single_batch.get().strip().upper()
        mat = self.var_mat_type.get()
        if not batch: return messagebox.showerror("Error", "Enter a Batch No.", parent=self.root)

        q = """INSERT INTO raw_material_qc (batch_no, material_type, status) VALUES (%s, %s, 'PENDING') 
               ON CONFLICT (batch_no) DO UPDATE SET material_type=EXCLUDED.material_type, updated_at=NOW()"""
        if DBManager.execute_query(q, (batch, mat)):
            self.var_single_batch.set("")
            self.refresh_all_lists()
            self.ent_single.focus_set()

    def save_range(self):
        prefix = self.var_prefix.get().strip().upper()
        try:
            start, end = int(self.var_start_num.get().strip()), int(self.var_end_num.get().strip())
        except ValueError: return messagebox.showerror("Error", "Start and End must be numbers.", parent=self.root)

        if start > end: return messagebox.showerror("Error", "Start must be less than End.", parent=self.root)
        if not messagebox.askyesno("Confirm Bulk", f"Generate {end-start+1} PENDING batches?", parent=self.root): return

        q = """INSERT INTO raw_material_qc (batch_no, material_type, status) VALUES (%s, %s, 'PENDING') 
               ON CONFLICT (batch_no) DO UPDATE SET material_type=EXCLUDED.material_type, updated_at=NOW()"""
        count = 0
        conn = DBManager.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                for i in range(start, end + 1):
                    cursor.execute(q, (f"{prefix}{i}", self.var_mat_type.get()))
                    count += 1
                conn.commit()
                cursor.close()
                self.var_start_num.set(""); self.var_end_num.set("")
                self.refresh_all_lists()
                messagebox.showinfo("Success", f"Bulk uploaded {count} batches!", parent=self.root)
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Database Error", str(e), parent=self.root)
            finally:
                DBManager.return_connection(conn)

    def log_qc(self, material_name, decision):
        """Grabs the selected batch from the specific material tab and approves it."""
        tree = self.qc_trees[material_name] # Get the specific tree for this tab
        sel = tree.selection()
        
        if not sel: 
            return messagebox.showwarning("Warning", f"Select a {material_name} batch to process.", parent=self.root)
            
        batch_no = tree.item(sel[0])['values'][0]
        
        q = "UPDATE raw_material_qc SET status=%s, updated_at=NOW() WHERE batch_no=%s AND material_type=%s"
        if DBManager.execute_query(q, (decision, batch_no, material_name)):
            self.refresh_all_lists()

    def delete_batch(self):
        sel = self.tree_entry.selection()
        if not sel: return messagebox.showwarning("Warning", "Select a batch to delete.", parent=self.root)
        batch = self.tree_entry.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirm", f"Delete batch {batch}?", parent=self.root):
            if DBManager.execute_query("DELETE FROM raw_material_qc WHERE batch_no=%s", (batch,)):
                self.refresh_all_lists()

    def refresh_all_lists(self):
        """Updates the Entry tab, ALL Material tabs, and the History tab simultaneously."""
        # 1. Update Entry Tab
        for i in self.tree_entry.get_children(): self.tree_entry.delete(i)
        res_entry = DBManager.fetch_data("SELECT batch_no, material_type, status FROM raw_material_qc ORDER BY updated_at DESC LIMIT 50")
        if res_entry:
            for r in res_entry: self.tree_entry.insert("", "end", values=r)

        # 2. Update Every Dedicated Material Tab
        for mat in self.materials:
            tree = self.qc_trees[mat]
            for i in tree.get_children(): tree.delete(i)
            
            # Fetch only records for THIS specific material
            res_mat = DBManager.fetch_data("SELECT batch_no, status, TO_CHAR(updated_at, 'YYYY-MM-DD HH24:MI') FROM raw_material_qc WHERE material_type=%s ORDER BY updated_at DESC LIMIT 50", (mat,))
            if res_mat:
                for r in res_mat:
                    tree.insert("", "end", values=r, tags=(r[1],)) # Tag by status for color coding

        # 3. Update History Tab
        self.search_qc_history()

    def search_qc_history(self):
        term = self.ent_search_qc.get().strip().upper() if self.ent_search_qc else ""
        for i in self.tree_history.get_children(): self.tree_history.delete(i)
        q = "SELECT batch_no, material_type, status, TO_CHAR(updated_at, 'YYYY-MM-DD HH24:MI') FROM raw_material_qc WHERE batch_no LIKE %s ORDER BY updated_at DESC"
        res = DBManager.fetch_data(q, (f"%{term}%",))
        if res:
            for r in res: self.tree_history.insert("", "end", values=r)

    def export_qc_csv(self):
        res = DBManager.fetch_data("SELECT batch_no, material_type, status, updated_at FROM raw_material_qc ORDER BY updated_at DESC")
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="QC_Audit_Report.csv")
        if path:
            with open(path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Batch", "Material", "Status", "Timestamp"])
                writer.writerows(res)
            messagebox.showinfo("Export Success", "Audit report saved.", parent=self.root)

    def create_card(self, parent, title): 
        f = tk.Frame(parent, bg=C_CARD, bd=1, relief="solid", padx=15, pady=15)
        f.pack(fill="x", pady=10)
        tk.Label(f, text=title, font=("Segoe UI", 11, "bold"), bg=C_CARD, fg=C_HEADER).pack(anchor="w", pady=(0, 10))
        return f

if __name__ == "__main__":
    root = tk.Tk(); app = LabQCApp(root); root.mainloop()