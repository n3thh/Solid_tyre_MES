import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import csv
from db_manager import DBManager

class AdminUploaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin DB Tool | PC1 System")
        self.root.geometry("700x700")
        self.root.configure(bg="#f4f6f7")

        # Styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=5)

        tk.Label(root, text="🏭 ADMIN DATA MANAGEMENT", font=("Segoe UI", 18, "bold"), bg="#f4f6f7", fg="#2c3e50").pack(pady=20)

        # TABS
        nb = ttk.Notebook(root)
        nb.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.tab_qc = tk.Frame(nb, bg="white")
        self.tab_plan = tk.Frame(nb, bg="white")
        self.tab_spec = tk.Frame(nb, bg="white")
        
        nb.add(self.tab_qc, text="1. QC Materials")
        nb.add(self.tab_plan, text="2. Production Plan")
        nb.add(self.tab_spec, text="3. Master Specs (Grades)")
        
        self.setup_qc_tab()
        self.setup_plan_tab()
        self.setup_spec_tab()

    # --- TAB 1: QC ---
    def setup_qc_tab(self):
        f = self.tab_qc
        tk.Label(f, text="Upload Approved Material Batches", font=("Segoe UI", 12, "bold"), bg="white").pack(pady=20)
        
        row = tk.Frame(f, bg="white")
        row.pack(pady=10)
        tk.Label(row, text="Material Type:", bg="white").pack(side="left")
        self.mat_types = ["CORE", "MIDDLE_LAYER", "GUM", "VT001", "VT002", "VT003", "NMW", "OTHER"]
        self.combo_mat = ttk.Combobox(row, values=self.mat_types, state="readonly")
        self.combo_mat.current(0)
        self.combo_mat.pack(side="left", padx=10)
        
        tk.Button(f, text="📂 Upload CSV", command=self.upload_qc, bg="#27AE60", fg="white").pack(pady=10)

    # --- TAB 2: PLAN ---
    def setup_plan_tab(self):
        f = self.tab_plan
        tk.Label(f, text="Upload Daily Production Plan", font=("Segoe UI", 12, "bold"), bg="white").pack(pady=20)
        tk.Label(f, text="Cols: PRESS, DAYLIGHT, TYRE_SIZE, QUALITY, TYPE, TYRE WEIGHT...", bg="white", fg="gray").pack()
        tk.Button(f, text="📂 Upload Plan CSV", command=self.upload_plan, bg="#2980B9", fg="white").pack(pady=20)

    # --- TAB 3: MASTER SPECS ---
    def setup_spec_tab(self):
        f = self.tab_spec
        tk.Label(f, text="Upload Grade Recipes (Percentages)", font=("Segoe UI", 12, "bold"), bg="white").pack(pady=20)
        
        btn_f = tk.Frame(f, bg="white")
        btn_f.pack(pady=10)
        tk.Button(btn_f, text="⬇ Get Sample Spec CSV", command=self.download_sample_spec).pack(side="left", padx=10)
        tk.Button(btn_f, text="📂 Upload Master Specs", command=self.upload_specs, bg="#8E44AD", fg="white").pack(side="left", padx=10)

        # Bead Master
        tk.Label(f, text="Upload Bead Master (Size vs Count)", font=("Segoe UI", 12, "bold"), bg="white").pack(pady=(30,10))
        tk.Button(f, text="📂 Upload Bead Master", command=self.upload_beads, bg="#E67E22", fg="white").pack()

    # --- LOGIC ---
    def download_sample_spec(self):
        save_path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="Sample_Grade_Specs.csv")
        if not save_path: return
        try:
            with open(save_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["GRADE", "BEAD_WT_DEDUCT", "CORE_%", "MID_%", "CT_%", "TREAD_%", "GUM_%", "IS_POB"])
                writer.writerows([
                    ["V3P02", 0.5, 54.0, 5.0, 6.0, 35.0, 0.0, "FALSE"],
                    ["POB-PREM", 0.0, 0.0, 0.0, 10.0, 88.0, 2.0, "TRUE"]
                ])
            messagebox.showinfo("Success", "Sample Saved!")
        except Exception as e: messagebox.showerror("Error", str(e))

    def upload_qc(self):
        m_type = self.combo_mat.get()
        path = filedialog.askopenfilename()
        if not path: return
        try:
            df = pd.read_csv(path) if path.endswith('.csv') else pd.read_excel(path)
            df.columns = [c.strip().upper() for c in df.columns]
            col_b = next((c for c in df.columns if "BATCH" in c), None)
            col_s = next((c for c in df.columns if "STATUS" in c), None)
            if not col_b or not col_s: return messagebox.showerror("Error", "Need BATCH and STATUS cols")
            
            count = 0
            for _, r in df.iterrows():
                q = "INSERT INTO raw_material_qc (batch_no, material_type, status) VALUES (%s, %s, %s) ON CONFLICT (batch_no) DO UPDATE SET status=EXCLUDED.status"
                if DBManager.execute_query(q, (str(r[col_b]), m_type, str(r[col_s]).upper())): count += 1
            messagebox.showinfo("Success", f"Uploaded {count} batches.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def upload_plan(self):
        path = filedialog.askopenfilename()
        if not path: return
        if messagebox.askyesno("Reset", "Clear old plan?"): DBManager.execute_query("DELETE FROM production_plan")
        try:
            df = pd.read_csv(path) if path.endswith('.csv') else pd.read_excel(path)
            df.columns = [c.strip().upper() for c in df.columns]
            count = 0
            for _, r in df.iterrows():
                q = """
                INSERT INTO production_plan (press_id, daylight, tyre_size, brand, pattern, quality, mould_id_marks, type, tyre_weight)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (press_id, daylight) DO UPDATE SET tyre_weight=EXCLUDED.tyre_weight, quality=EXCLUDED.quality
                """
                # Handle weight safely
                wt = r.get('TYRE WEIGHT', 0)
                try: wt = float(wt)
                except: wt = 0.0
                
                params = (
                    str(r.get('PRESS', '')), str(r.get('DAYLIGHT', '')), str(r.get('TYRE_SIZE', '')),
                    str(r.get('BRAND', '')), str(r.get('PATTERN', '')), str(r.get('QUALITY', '')),
                    str(r.get('MOULD_ID', '')), str(r.get('TYPE', '')), wt
                )
                if DBManager.execute_query(q, params): count += 1
            messagebox.showinfo("Success", f"Uploaded {count} plan entries.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def upload_specs(self):
        path = filedialog.askopenfilename()
        if not path: return
        try:
            df = pd.read_csv(path) if path.endswith('.csv') else pd.read_excel(path)
            df.columns = [c.strip().upper() for c in df.columns]
            count = 0
            for _, r in df.iterrows():
                q = """
                INSERT INTO tyre_specs (grade, bead_weight, core_pct, mid_pct, ct_pct, tread_pct, gum_pct, is_pob)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (grade) DO UPDATE SET core_pct=EXCLUDED.core_pct, tread_pct=EXCLUDED.tread_pct
                """
                params = (
                    str(r['GRADE']), float(r.get('BEAD_WT_DEDUCT', 0)), 
                    float(r.get('CORE_%', 0)), float(r.get('MID_%', 0)), float(r.get('CT_%', 0)),
                    float(r.get('TREAD_%', 0)), float(r.get('GUM_%', 0)), str(r.get('IS_POB', 'FALSE')).upper()=='TRUE'
                )
                if DBManager.execute_query(q, params): count += 1
            messagebox.showinfo("Success", f"Uploaded {count} Grades.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def upload_beads(self):
        # Format: TYRE_SIZE, BEAD_SIZE, BEAD_COUNT
        path = filedialog.askopenfilename()
        if not path: return
        try:
            df = pd.read_csv(path)
            df.columns = [c.strip().upper() for c in df.columns]
            count = 0
            for _, r in df.iterrows():
                q = "INSERT INTO bead_master (tyre_size, bead_size, bead_count) VALUES (%s, %s, %s) ON CONFLICT (tyre_size) DO UPDATE SET bead_count=EXCLUDED.bead_count"
                if DBManager.execute_query(q, (str(r['TYRE_SIZE']), str(r['BEAD_SIZE']), int(r['BEAD_COUNT']))): count += 1
            messagebox.showinfo("Success", f"Uploaded {count} Bead Rules.")
        except Exception as e: messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = AdminUploaderApp(root)
    root.mainloop()