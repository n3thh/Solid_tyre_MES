import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import csv
from db_manager import DBManager

class AdminUploaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin DB Tool | PC1 System")
        self.root.geometry("500x500")
        self.root.configure(bg="#f0f0f0")

        tk.Label(root, text="ADMIN DATA MANAGEMENT", font=("Segoe UI", 16, "bold"), bg="#f0f0f0").pack(pady=20)

        # --- SECTION 1: QC ---
        frame_qc = tk.LabelFrame(root, text="1. Raw Material QC Upload", font=("Segoe UI", 10, "bold"), padx=15, pady=15, bg="white")
        frame_qc.pack(fill="x", padx=20, pady=10)
        
        btn_frame_qc = tk.Frame(frame_qc, bg="white")
        btn_frame_qc.pack(fill="x", pady=5)
        tk.Button(btn_frame_qc, text="⬇ Get Sample CSV", command=self.download_sample_qc, bg="#E0E0E0", width=15).pack(side="left", padx=5)
        tk.Button(btn_frame_qc, text="📂 Upload Data", command=self.upload_qc, bg="#FF9800", fg="white", font=("Segoe UI", 9, "bold"), width=15).pack(side="left", padx=5)

        # --- SECTION 2: PRODUCTION PLAN ---
        frame_plan = tk.LabelFrame(root, text="2. Production Plan", font=("Segoe UI", 10, "bold"), padx=15, pady=15, bg="white")
        frame_plan.pack(fill="x", padx=20, pady=10)
        tk.Label(frame_plan, text="Defines P1, P2, P7 (Single) and P3-P8 (Top/Bot)", bg="white", fg="gray").pack(anchor="w")

        btn_frame_plan = tk.Frame(frame_plan, bg="white")
        btn_frame_plan.pack(fill="x", pady=5)
        tk.Button(btn_frame_plan, text="⬇ Get Sample CSV", command=self.download_sample_plan, bg="#E0E0E0", width=15).pack(side="left", padx=5)
        tk.Button(btn_frame_plan, text="📅 Upload Plan", command=self.upload_plan, bg="#2196F3", fg="white", font=("Segoe UI", 9, "bold"), width=15).pack(side="left", padx=5)

        self.status_var = tk.StringVar(value="Ready.")
        tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#ddd").pack(side=tk.BOTTOM, fill=tk.X)

    def download_sample_qc(self):
        save_path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="Sample_QC.csv")
        if not save_path: return
        try:
            with open(save_path, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["BATCH NO", "STATUS"])
                writer.writerows([["S0001", "APPROVED"], ["S0002", "HOLD"], ["12", "APPROVED"]])
            messagebox.showinfo("Success", "Sample Saved!")
        except Exception as e: messagebox.showerror("Error", str(e))

    def download_sample_plan(self):
        """Generates a realistic Plan based on user's Press setup"""
        save_path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="Sample_Production_Plan.csv")
        if not save_path: return
        
        headers = ["PRESS", "DAYLIGHT", "TYRE_SIZE", "CORE_SIZE", "BRAND", "PATTERN", "QUALITY", "MOULD_ID"]
        data = [
            # Single Daylight Presses
            ["P-01", "SINGLE", "18x7-8", "4.33\"", "SOLIDO", "LUG", "Premium", "M-101-L"],
            ["P-02", "SINGLE", "6.00-9", "4.00\"", "TVS", "RIB", "Standard", "M-205-R"],
            ["P-07", "SINGLE", "23x9-10", "6.50\"", "GLOBE", "SMOOTH", "Premium", "M-330-X"],
            
            # Double Daylight Presses
            ["P-03", "TOP", "18x7-8", "4.33\"", "SOLIDO", "LUG", "Premium", "M-102-T"],
            ["P-03", "BOT", "18x7-8", "4.33\"", "SOLIDO", "LUG", "Premium", "M-102-B"],
            ["P-04", "TOP", "5.00-8", "3.00\"", "TVS", "LUG", "Standard", "M-401-T"]
        ]
        try:
            with open(save_path, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(data)
            messagebox.showinfo("Success", "Sample Plan Saved!")
        except Exception as e: messagebox.showerror("Error", str(e))

    def upload_qc(self):
        self._upload_generic("QC")

    def upload_plan(self):
        self._upload_generic("PLAN")

    def _upload_generic(self, mode):
        # ... [Logic is the same as previous code, just cleaner] ...
        # Use previous upload logic here (omitted for brevity)
        # If you need the full paste again, let me know!
        pass 
    
    # [Paste the upload_qc and upload_plan logic from previous response here if running fresh]
    # For now, I assume you have the upload logic from the previous step.