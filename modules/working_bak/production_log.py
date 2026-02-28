import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from db_manager import DBManager

class ProductionLog:
    def __init__(self, root):
        self.root = root
        self.root.title("📊 Module 9: Production Log (7-3-11 Shift Cycle)")
        self.root.geometry("1400x900")
        self.root.configure(bg="#F4F6F7")
        
        self.target_date = tk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))
        self.setup_ui()
        self.refresh_logs()

    def setup_ui(self):
        # Header Area
        header = tk.Frame(self.root, bg="#2C3E50", pady=15)
        header.pack(fill="x")
        
        f_date = tk.Frame(header, bg="#2C3E50")
        f_date.pack()
        tk.Label(f_date, text="SELECT PRODUCTION DATE:", fg="white", bg="#2C3E50", font=("Segoe UI", 10, "bold")).pack(side="left", padx=10)
        tk.Entry(f_date, textvariable=self.target_date, width=15, font=("Segoe UI", 12)).pack(side="left", padx=5)
        tk.Button(f_date, text="🔄 GENERATE SHIFT LOGS", command=self.refresh_logs, bg="#3498DB", fg="white", font=("Segoe UI", 10, "bold"), padx=20).pack(side="left", padx=15)
        tk.Button(f_date, text="📄 EXPORT PDF", command=self.export_pdf, bg="#E67E22", fg="white", font=("Segoe UI", 10, "bold"), padx=20).pack(side="left")

        # Shift Summary Top Cards
        self.f_cards = tk.Frame(self.root, bg="#F4F6F7", pady=20)
        self.f_cards.pack(fill="x", padx=20)
        
        self.shift_cards = {
            'SHIFT A': self.create_card("SHIFT A (07:00-15:00)", "#27AE60"),
            'SHIFT B': self.create_card("SHIFT B (15:00-23:00)", "#2980B9"),
            'SHIFT C': self.create_card("SHIFT C (23:00-07:00)", "#8E44AD")
        }

        # Detailed Table Area
        f_table = tk.Frame(self.root, bg="white", padx=20, pady=10)
        f_table.pack(fill="both", expand=True)
        
        cols = ("Shift", "Tyre Size", "Type", "Brand", "Quality", "Tread", "QTY (Pcs)", "Total Weight (Kg)")
        self.tree = ttk.Treeview(f_table, columns=cols, show="headings", height=20)
        
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor="center", width=140)
            
        self.tree.pack(fill="both", expand=True)
        
        # UI Styles
        self.tree.tag_configure('shift_total', background='#D5F5E3', font=("Segoe UI", 10, "bold"))
        self.tree.tag_configure('grand_total', background='#2C3E50', foreground='white', font=("Segoe UI", 11, "bold"))
        self.tree.tag_configure('odd', background='#F2F4F4')

    def create_card(self, title, color):
        f = tk.LabelFrame(self.f_cards, text=title, font=("Segoe UI", 10, "bold"), bg="white", fg=color, padx=15, pady=15)
        f.pack(side="left", fill="both", expand=True, padx=10)
        qty_val = tk.Label(f, text="0", font=("Segoe UI", 28, "bold"), bg="white", fg="#2C3E50")
        qty_val.pack()
        wt_val = tk.Label(f, text="0.00 kg", font=("Segoe UI", 14, "bold"), bg="white", fg=color)
        wt_val.pack(pady=(10,0))
        return {"qty": qty_val, "wt": wt_val}

    def refresh_logs(self):
        date_str = self.target_date.get()
        for i in self.tree.get_children(): self.tree.delete(i)
        
        for s in self.shift_cards:
            self.shift_cards[s]["qty"].config(text="0")
            self.shift_cards[s]["wt"].config(text="0.00 kg")

        query = """
            SELECT 
                CASE 
                    WHEN TO_CHAR(c.start_time, 'HH24:MI') >= '07:00' AND TO_CHAR(c.start_time, 'HH24:MI') < '15:00' THEN 'SHIFT A'
                    WHEN TO_CHAR(c.start_time, 'HH24:MI') >= '15:00' AND TO_CHAR(c.start_time, 'HH24:MI') < '23:00' THEN 'SHIFT B'
                    ELSE 'SHIFT C'
                END as shift_name,
                b.tyre_size, CASE WHEN b.is_pob THEN 'POB' ELSE 'Standard' END,
                b.brand, b.quality, b.tread_type,
                COUNT(*) as qty, SUM(COALESCE(c.final_cured_weight, 0)) as total_kg
            FROM pc2_curing c
            JOIN pc1_building b ON c.b_id = b.b_id
            WHERE DATE(c.start_time) = %s
            GROUP BY shift_name, b.tyre_size, b.is_pob, b.brand, b.quality, b.tread_type
            ORDER BY shift_name, b.tyre_size;
        """
        data = DBManager.fetch_data(query, (date_str,))
        
        current_shift, s_qty, s_wt = None, 0, 0.0
        grand_qty, grand_wt = 0, 0.0
        
        if data:
            for idx, r in enumerate(data):
                shift, size, ptype, brand, qual, tread, qty, wt = r
                if current_shift and shift != current_shift:
                    self.insert_total(current_shift, s_qty, s_wt)
                    s_qty, s_wt = 0, 0.0

                current_shift = shift
                s_qty += qty
                s_wt += float(wt)
                grand_qty += qty
                grand_wt += float(wt)
                
                tag = 'odd' if idx % 2 != 0 else ''
                self.tree.insert("", "end", values=(shift, size, ptype, brand, qual, tread, qty, f"{wt:.2f}"), tags=(tag,))

            if current_shift:
                self.insert_total(current_shift, s_qty, s_wt)
            
            # --- GRAND TOTAL ---
            self.tree.insert("", "end", values=("", "", "", "", "", "", "", ""))
            self.tree.insert("", "end", values=("🌟 GRAND TOTAL", "-", "-", "-", "-", "-", grand_qty, f"{grand_wt:.2f}"), tags=('grand_total',))

    def insert_total(self, shift_name, qty, wt):
        self.tree.insert("", "end", values=(f"TOTAL {shift_name}", "-", "-", "-", "-", "-", qty, f"{wt:.2f}"), tags=('shift_total',))
        self.shift_cards[shift_name]["qty"].config(text=str(qty))
        self.shift_cards[shift_name]["wt"].config(text=f"{wt:.2f} kg")

    def export_pdf(self):
        messagebox.showinfo("PDF Export", f"Production Report for {self.target_date.get()} has been generated and saved to /reports/")

    def export_pdf(self):
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            import os

            # Ensure reports directory exists
            if not os.path.exists("reports"):
                os.makedirs("reports")
            
            filename = f"reports/Production_Report_{self.target_date.get()}.pdf"
            c = canvas.Canvas(filename, pagesize=A4)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, 800, f"DAILY PRODUCTION LOG - {self.target_date.get()}")
            
            # Table Headers
            y = 770
            c.setFont("Helvetica-Bold", 9)
            header = " | ".join(self.tree['columns'])
            c.drawString(50, y, header)
            c.line(50, y-5, 550, y-5)
            
            # Data Rows
            y -= 25
            c.setFont("Helvetica", 9)
            for child in self.tree.get_children():
                row = self.tree.item(child)['values']
                line = " | ".join(str(x) for x in row)
                c.drawString(50, y, line)
                y -= 20
                if y < 50: # Handle New Page
                    c.showPage()
                    c.setFont("Helvetica", 9)
                    y = 800
                    
            c.save()
            messagebox.showinfo("Success", f"Report saved as {filename}")
        except ImportError:
            messagebox.showerror("Error", "Please install reportlab: pip install reportlab")
        except Exception as e:
            messagebox.showerror("Error", f"Could not generate PDF: {e}")