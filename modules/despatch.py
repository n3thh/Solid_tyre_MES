import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from db_manager import DBManager
from tkinter import ttk, messagebox, filedialog
import csv

# ================= CONFIGURATION =================
C_BG = "#F4F6F7"       
C_CARD = "#FFFFFF"     
C_HEADER = "#2980B9"   # Blue Header
C_SUCCESS = "#27AE60"  
C_ERR = "#E74C3C"      
C_WARN = "#F39C12"

class DespatchApp:
    def __init__(self, root, current_user="LOGISTICS"):
        self.root = root
        self.root.title(f"PC4 | Tyre Despatch Manager (User: {current_user})")
        self.root.geometry("1300x800")
        self.root.configure(bg=C_BG)
        self.current_user = current_user

        # --- VARIABLES ---
        self.var_customer = tk.StringVar()
        self.var_size = tk.StringVar()
        self.var_brand = tk.StringVar()
        self.var_quality = tk.StringVar()
        self.var_qty = tk.StringVar()
        self.var_scan = tk.StringVar()
        
        self.order_lines = [] # Stores dicts: {size, brand, quality, req, scanned, tree_id}
        self.is_scanning = False

        self.setup_ui()
        self.load_dropdowns()

    def setup_ui(self):
        # HEADER
        header = tk.Frame(self.root, bg=C_HEADER, height=70)
        header.pack(fill="x")
        tk.Label(header, text="🚚 PC4 - LOGISTICS & DESPATCH", font=("Segoe UI", 20, "bold"), bg=C_HEADER, fg="white").pack(pady=15)

        # MAIN CONTENT
        content = tk.Frame(self.root, bg=C_BG)
        content.pack(fill="both", expand=True, padx=20, pady=20)

        # ================= LEFT: ORDER BUILDER =================
        self.f_left = tk.Frame(content, bg=C_BG, width=500)
        self.f_left.pack(side="left", fill="y", expand=False, padx=(0, 10))
        
        card_order = self.create_card(self.f_left, "1. BUILD CUSTOMER ORDER")
        
        tk.Label(card_order, text="Customer / Order Ref:", bg=C_CARD, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.ent_cust = tk.Entry(card_order, textvariable=self.var_customer, font=("Segoe UI", 12), bg="#EAF2F8")
        self.ent_cust.pack(fill="x", pady=(0, 15))

        # Inputs
        f_inputs = tk.Frame(card_order, bg=C_CARD)
        f_inputs.pack(fill="x")
        
        self.create_input_row(f_inputs, "Tyre Size:", self.var_size, 0)
        self.create_input_row(f_inputs, "Brand:", self.var_brand, 1)
        self.create_input_row(f_inputs, "Grade/Quality:", self.var_quality, 2)
        
        tk.Label(f_inputs, text="Quantity:", bg=C_CARD, font=("Segoe UI", 9, "bold")).grid(row=3, column=0, sticky="w", pady=5)
        tk.Entry(f_inputs, textvariable=self.var_qty, font=("Segoe UI", 12), width=10).grid(row=3, column=1, sticky="w", pady=5)

        self.btn_add = tk.Button(card_order, text="➕ ADD TO ORDER", command=self.add_to_order, bg="#34495E", fg="white", font=("Segoe UI", 10, "bold"))
        self.btn_add.pack(fill="x", pady=15)

        # Order Grid
        cols_o = ("Size", "Brand", "Grade", "Req", "Scan")
        self.tree_order = ttk.Treeview(card_order, columns=cols_o, show="headings", height=8)
        self.tree_order.heading("Size", text="Size"); self.tree_order.column("Size", width=120)
        self.tree_order.heading("Brand", text="Brand"); self.tree_order.column("Brand", width=100)
        self.tree_order.heading("Grade", text="Grade"); self.tree_order.column("Grade", width=90)
        self.tree_order.heading("Req", text="Req"); self.tree_order.column("Req", width=50, anchor="center")
        self.tree_order.heading("Scan", text="Scan"); self.tree_order.column("Scan", width=50, anchor="center")
        self.tree_order.pack(fill="both", expand=True)

        self.btn_lock = tk.Button(card_order, text="🔒 LOCK ORDER & START SCANNING", command=self.start_scanning, bg=C_WARN, fg="white", font=("Segoe UI", 12, "bold"), pady=10)
        self.btn_lock.pack(fill="x", pady=15)

        # ================= RIGHT: SCANNER QUEUE =================
        self.f_right = tk.Frame(content, bg=C_BG)
        self.f_right.pack(side="right", fill="both", expand=True, padx=(10, 0))

        card_scan = self.create_card(self.f_right, "2. SCAN & VERIFY")
        
        self.lbl_scan_status = tk.Label(card_scan, text="AWAITING ORDER SETUP...", font=("Segoe UI", 14, "bold"), fg="gray", bg=C_CARD)
        self.lbl_scan_status.pack(pady=10)

        self.ent_scan = tk.Entry(card_scan, textvariable=self.var_scan, font=("Segoe UI", 24, "bold"), justify="center", bg="#D5F5E3", state="disabled")
        self.ent_scan.pack(fill="x", pady=10, padx=50)
        self.ent_scan.bind("<Return>", self.process_scan)

        tk.Label(card_scan, text="Successfully Despatched Tyres:", bg=C_CARD, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(15, 5))
        
        cols_s = ("Time", "Serial No", "Size", "Grade")
        self.tree_scan = ttk.Treeview(card_scan, columns=cols_s, show="headings", height=15)
        for c in cols_s: self.tree_scan.heading(c, text=c)
        self.tree_scan.column("Time", width=100); self.tree_scan.column("Serial No", width=150)
        self.tree_scan.pack(fill="both", expand=True)
        
        # Reset Button
        # Action Buttons Frame
        f_actions = tk.Frame(card_scan, bg=C_CARD)
        f_actions.pack(fill="x", pady=10)
        
        # NEW: Finish Button
        tk.Button(f_actions, text="✅ FINISH & CLEAR", command=self.finish_despatch, bg="#2980B9", fg="white", font=("Segoe UI", 10, "bold")).pack(side="left", padx=5)
        
        # Existing Buttons
        tk.Button(f_actions, text="🔄 CANCEL ORDER", command=self.reset_system, bg=C_ERR, fg="white", font=("Segoe UI", 10)).pack(side="left", padx=5)
        tk.Button(f_actions, text="🌐 EXPORT HTML", command=self.export_html, bg="#8E44AD", fg="white", font=("Segoe UI", 10, "bold")).pack(side="right", padx=5)
        tk.Button(f_actions, text="📄 EXPORT CSV", command=self.export_csv, bg="#27AE60", fg="white", font=("Segoe UI", 10, "bold")).pack(side="right", padx=5)

    # --- LOGIC ---
    def load_dropdowns(self):
        try:
            sizes = DBManager.fetch_data("SELECT DISTINCT tyre_size FROM production_plan")
            brands = DBManager.fetch_data("SELECT DISTINCT brand FROM production_plan")
            if sizes: self.combo_size['values'] = [r[0] for r in sizes]
            if brands: self.combo_brand['values'] = [r[0] for r in brands]
            self.combo_quality['values'] = ["A-GRADE", "B-GRADE"]
        except: pass

    def add_to_order(self):
        size = self.var_size.get().strip()
        brand = self.var_brand.get().strip()
        quality = self.var_quality.get().strip()
        try: qty = int(self.var_qty.get())
        except: return messagebox.showerror("Error", "Quantity must be a number.")

        if not size or not brand or not quality or qty <= 0:
            return messagebox.showerror("Error", "Fill all fields with valid data.")

        # Check for duplicates in the list
        for line in self.order_lines:
            if line['size'] == size and line['brand'] == brand and line['quality'] == quality:
                return messagebox.showwarning("Duplicate", "This requirement is already in the order.")

        item_id = self.tree_order.insert("", "end", values=(size, brand, quality, qty, 0))
        self.order_lines.append({
            'size': size, 'brand': brand, 'quality': quality, 
            'req': qty, 'scanned': 0, 'tree_id': item_id
        })
        self.var_qty.set("") # Clear qty for next entry

    def start_scanning(self):
        if not self.var_customer.get().strip():
            return messagebox.showerror("Error", "Enter Customer Name.")
        if not self.order_lines:
            return messagebox.showerror("Error", "Add at least one item to the order.")

        self.is_scanning = True
        self.ent_cust.config(state="disabled")
        self.btn_add.config(state="disabled")
        self.btn_lock.config(state="disabled")
        
        self.ent_scan.config(state="normal")
        self.ent_scan.focus_set()
        self.lbl_scan_status.config(text="READY TO SCAN", fg=C_SUCCESS)

    def process_scan(self, event):
        if not self.is_scanning: return
        serial = self.var_scan.get().strip().upper()
        self.var_scan.set("") # Clear immediately
        if not serial: return

        # 1. Fetch Tyre Data (Checking Curing + Building + QC)
        q = """
            SELECT c.serial_no, b.tyre_size, b.brand, q.grade, q.despatched_at 
            FROM pc2_curing c 
            JOIN pc1_building b ON c.b_id = b.b_id 
            LEFT JOIN pc3_quality q ON c.serial_no = q.tyre_id 
            WHERE c.serial_no = %s
        """
        res = DBManager.fetch_data(q, (serial,))

        if not res:
            return self.flash_status(f"❌ {serial}: NOT FOUND", C_ERR)
        
        r = res[0]
        t_serial, t_size, t_brand, t_grade, t_despatched = r

        # 2. Hard Validations
        if not t_grade: return self.flash_status(f"❌ {serial}: PENDING QC", C_ERR)
        if t_grade == "SCRAP": return self.flash_status(f"❌ {serial}: SCRAP TYRE!", C_ERR)
        if t_despatched: return self.flash_status(f"❌ {serial}: ALREADY SHIPPED!", C_ERR)

        # 3. Matchmaker (Does it fit the order?)
        matched_line = None
        for line in self.order_lines:
            if line['size'] == t_size and line['brand'] == t_brand and line['quality'] == t_grade:
                if line['scanned'] < line['req']:
                    matched_line = line
                    break

        if not matched_line:
            # Check if it matches specs but we are full
            for line in self.order_lines:
                if line['size'] == t_size and line['brand'] == t_brand and line['quality'] == t_grade:
                    return self.flash_status(f"⚠️ {serial}: QUOTA FULL FOR THIS SIZE", C_WARN)
            return self.flash_status(f"❌ {serial}: WRONG SIZE/BRAND/GRADE FOR ORDER", C_ERR)

        # 4. SUCCESS - Update Database
        q_upd = "UPDATE pc3_quality SET customer_name=%s, despatched_at=NOW() WHERE tyre_id=%s"
        if DBManager.execute_query(q_upd, (self.var_customer.get().strip(), serial)):
            # Update Internal Logic
            matched_line['scanned'] += 1
            
            # Update Left Grid
            self.tree_order.item(matched_line['tree_id'], values=(matched_line['size'], matched_line['brand'], matched_line['quality'], matched_line['req'], matched_line['scanned']))
            
            # Update Right Grid
            t_now = datetime.datetime.now().strftime("%H:%M:%S")
            self.tree_scan.insert("", "0", values=(t_now, serial, t_size, t_grade)) # Insert at top
            
            self.flash_status(f"✅ {serial} DESPATCHED", C_SUCCESS)
            self.check_order_complete()

    def check_order_complete(self):
        complete = all(line['scanned'] == line['req'] for line in self.order_lines)
        if complete:
            self.lbl_scan_status.config(text="🎉 ORDER COMPLETE!", fg=C_SUCCESS)
            self.ent_scan.config(state="disabled")
            messagebox.showinfo("Success", "All tyres for this order have been successfully scanned and despatched!")

    def flash_status(self, msg, color):
        self.lbl_scan_status.config(text=msg, fg=color)
        self.root.bell() # System beep for awareness

    def reset_system(self):
        if self.is_scanning and not messagebox.askyesno("Cancel Order", "Are you sure you want to CANCEL this active order?"):
            return
        self.is_scanning = False
        self.var_customer.set(""); self.var_size.set(""); self.var_brand.set(""); self.var_quality.set(""); self.var_qty.set(""); self.var_scan.set("")
        self.order_lines = []
        for i in self.tree_order.get_children(): self.tree_order.delete(i)
        for i in self.tree_scan.get_children(): self.tree_scan.delete(i)
        self.ent_cust.config(state="normal"); self.btn_add.config(state="normal"); self.btn_lock.config(state="normal")
        self.ent_scan.config(state="disabled")
        self.lbl_scan_status.config(text="AWAITING ORDER SETUP...", fg="gray")

    def finish_despatch(self):
        if not self.is_scanning and not self.order_lines:
            return messagebox.showinfo("Info", "No active order to finish.")

        # Check if they scanned everything they promised
        is_short = any(line['scanned'] < line['req'] for line in self.order_lines)
        
        msg = "Are you sure you want to finish this despatch?"
        if is_short:
            msg = "⚠️ WARNING: You have NOT scanned the full required quantity for this order!\n\nAre you sure you want to short-ship and finish?"

        if messagebox.askyesno("Finish Despatch", msg):
            # Ask if they want a manifest before clearing
            if messagebox.askyesno("Export", "Do you want to export an HTML Manifest before clearing the screen?"):
                self.export_html()
            
            # Force the reset without the cancel warning
            self.is_scanning = False
            self.reset_system()
            messagebox.showinfo("Success", "Despatch complete and screen cleared for the next order.")

    def export_csv(self):
        if not self.var_customer.get().strip():
            return messagebox.showwarning("Warning", "No customer order to export.")
        
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile=f"Manifest_{self.var_customer.get().strip()}.csv")
        if not path: return
        
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["🚚 DESPATCH MANIFEST"])
                writer.writerow(["CUSTOMER:", self.var_customer.get().strip(), "DATE:", datetime.datetime.now().strftime("%Y-%m-%d %H:%M")])
                writer.writerow([])
                
                # Write Order Summary
                writer.writerow(["--- 1. ORDER SUMMARY ---"])
                writer.writerow(["Size", "Brand", "Grade", "Required", "Scanned"])
                for line in self.order_lines:
                    writer.writerow([line['size'], line['brand'], line['quality'], line['req'], line['scanned']])
                
                writer.writerow([])
                
                # Write Scanned Tyres
                writer.writerow(["--- 2. SCANNED TYRES ---"])
                writer.writerow(["Time", "Serial No", "Size", "Grade"])
                for child in self.tree_scan.get_children():
                    writer.writerow(self.tree_scan.item(child)["values"])
                    
            messagebox.showinfo("Success", "CSV Exported Successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save CSV: {e}")

    def export_html(self):
        if not self.var_customer.get().strip():
            return messagebox.showwarning("Warning", "No customer order to export.")
            
        path = filedialog.asksaveasfilename(defaultextension=".html", initialfile=f"Manifest_{self.var_customer.get().strip()}.html")
        if not path: return

        cust = self.var_customer.get().strip()
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Build Summary Table
        sum_rows = ""
        for l in self.order_lines:
            status_color = "#27AE60" if l['scanned'] >= l['req'] else "#E67E22"
            sum_rows += f"<tr><td>{l['size']}</td><td>{l['brand']}</td><td>{l['quality']}</td><td>{l['req']}</td><td style='color:{status_color}; font-weight:bold;'>{l['scanned']}</td></tr>"

        # Build Scan Table
        scan_rows = ""
        for child in self.tree_scan.get_children():
            v = self.tree_scan.item(child)["values"]
            scan_rows += f"<tr><td>{v[0]}</td><td>{v[1]}</td><td>{v[2]}</td><td>{v[3]}</td></tr>"

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; background-color: #f4f6f7; padding: 20px; }}
                .card {{ background: white; max-width: 800px; margin: auto; padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
                h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
                h2 {{ color: #2980b9; margin-top: 25px; border-left: 5px solid #2980b9; padding-left: 10px; font-size: 18px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ecf0f1; }}
                th {{ background-color: #34495e; color: white; }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #95a5a6; text-align: center; border-top: 1px solid #ecf0f1; padding-top: 10px; }}
            </style>
        </head>
        <body>
            <div class="card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h1>🚚 Despatch Manifest</h1>
                    <span style="background:#27ae60; color:white; padding:5px 15px; border-radius:5px; font-weight:bold;">{cust}</span>
                </div>
                <p style="color:#7f8c8d; font-weight:bold;">Date: {date_str}</p>
                
                <h2>1. Order Summary</h2>
                <table>
                    <tr><th>Size</th><th>Brand</th><th>Grade</th><th>Required</th><th>Scanned</th></tr>
                    {sum_rows}
                </table>

                <h2>2. Scanned Tyres</h2>
                <table>
                    <tr><th>Time</th><th>Serial No</th><th>Size</th><th>Grade</th></tr>
                    {scan_rows}
                </table>
                
                <div class="footer">Generated by Factory OS</div>
            </div>
        </body>
        </html>
        """
        
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            messagebox.showinfo("Success", "HTML Manifest Saved!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save HTML: {e}")    

    # --- HELPERS ---
    def create_card(self, parent, title): 
        f = tk.Frame(parent, bg=C_CARD, bd=1, relief="solid", padx=15, pady=15); f.pack(fill="both", expand=True, pady=5)
        tk.Label(f, text=title, font=("Segoe UI", 12, "bold"), bg=C_CARD, fg=C_HEADER).pack(anchor="w", pady=(0, 10)); return f

    def create_input_row(self, parent, label, var, row):
        tk.Label(parent, text=label, bg=C_CARD, font=("Segoe UI", 9, "bold")).grid(row=row, column=0, sticky="w", pady=5)
        cb = ttk.Combobox(parent, textvariable=var, font=("Segoe UI", 11), width=20)
        cb.grid(row=row, column=1, sticky="w", pady=5)
        if "Size" in label: self.combo_size = cb
        elif "Brand" in label: self.combo_brand = cb
        elif "Grade" in label: self.combo_quality = cb

if __name__ == "__main__":
    root = tk.Tk(); app = DespatchApp(root); root.mainloop()