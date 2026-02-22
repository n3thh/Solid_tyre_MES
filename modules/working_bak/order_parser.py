import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
import difflib
import docx # Requires: pip install python-docx
from db_manager import DBManager

class SmartOrderParser:
    def __init__(self, parent_root):
        self.top = tk.Toplevel(parent_root)
        self.top.title("Smart DOCX Order Parser")
        self.top.geometry("1100x600")
        self.top.configure(bg="#ECF0F1")
        
        self.parsed_data = []
        
        # Load known database values for matching
        self.known_sizes = [r[0] for r in DBManager.fetch_data("SELECT DISTINCT tyre_size FROM production_plan") or []]
        self.known_brands = [r[0] for r in DBManager.fetch_data("SELECT DISTINCT brand FROM production_plan") or []]
        
        self.setup_ui()

    def setup_ui(self):
        # Header
        header = tk.Frame(self.top, bg="#2C3E50", pady=15)
        header.pack(fill="x")
        tk.Label(header, text="📄 SMART ORDER IMPORTER", font=("Segoe UI", 16, "bold"), fg="white", bg="#2C3E50").pack(side="left", padx=20)
        tk.Button(header, text="📂 SELECT DOCX FILE", command=self.load_docx, bg="#E67E22", fg="white", font=("Segoe UI", 10, "bold")).pack(side="right", padx=20)

        # Main Grid
        f_grid = tk.Frame(self.top, bg="white", padx=10, pady=10)
        f_grid.pack(fill="both", expand=True, padx=10, pady=10)
        
        cols = ("Raw Description", "Extracted Qty", "Matched Size", "Size %", "Matched Brand", "Brand %")
        self.tree = ttk.Treeview(f_grid, columns=cols, show="headings", height=15)
        
        self.tree.heading("Raw Description", text="Raw Text from File")
        self.tree.column("Raw Description", width=350)
        
        self.tree.heading("Extracted Qty", text="Qty")
        self.tree.column("Extracted Qty", width=80, anchor="center")
        
        self.tree.heading("Matched Size", text="DB Size Match")
        self.tree.column("Matched Size", width=150)
        
        self.tree.heading("Size %", text="Match %")
        self.tree.column("Size %", width=80, anchor="center")

        self.tree.heading("Matched Brand", text="DB Brand Match")
        self.tree.column("Matched Brand", width=150)
        
        self.tree.heading("Brand %", text="Match %")
        self.tree.column("Brand %", width=80, anchor="center")
        
        self.tree.pack(fill="both", expand=True)
        
        # Color coding tags
        self.tree.tag_configure('high', background='#EAFAF1') # Green-ish
        self.tree.tag_configure('med', background='#FCF3CF')  # Yellow-ish
        self.tree.tag_configure('low', background='#FDEDEC')  # Red-ish

        # Verification Editor Frame
        f_edit = tk.LabelFrame(self.top, text=" VERIFY & EDIT SELECTED ROW ", bg="white", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        f_edit.pack(fill="x", padx=10, pady=10)
        
        tk.Label(f_edit, text="Verified Size:", bg="white").pack(side="left")
        self.var_v_size = tk.StringVar()
        ttk.Combobox(f_edit, textvariable=self.var_v_size, values=self.known_sizes, width=15).pack(side="left", padx=5)
        
        tk.Label(f_edit, text="Verified Brand:", bg="white").pack(side="left", padx=(15,0))
        self.var_v_brand = tk.StringVar()
        ttk.Combobox(f_edit, textvariable=self.var_v_brand, values=self.known_brands, width=15).pack(side="left", padx=5)
        
        tk.Button(f_edit, text="✅ UPDATE ROW", command=self.update_row, bg="#3498DB", fg="white").pack(side="left", padx=20)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

    def load_docx(self):
        path = filedialog.askopenfilename(filetypes=[("Word Documents", "*.docx")])
        if not path: return
        
        self.parsed_data.clear()
        for i in self.tree.get_children(): self.tree.delete(i)
        
        try:
            doc = docx.Document(path)
            for table in doc.tables:
                for row in table.rows:
                    cells = [cell.text.strip().replace('\n', ' ') for cell in row.cells]
                    self.process_row(cells)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file: {e}")

    def process_row(self, cells):
        # Flatten the row into a single string to find the description
        full_text = " ".join(cells).upper()
        
        # Skip header rows or empty rows
        if "DESCRIPTION" in full_text or "QUANTITY" in full_text or len(full_text) < 5:
            return

        # 1. Regex to find Quantity (Assuming it's a standalone number in one of the cells)
        qty = "0"
        for cell in reversed(cells): # Qty is usually on the right side
            if cell.isdigit() and int(cell) > 0:
                qty = cell
                break

        # 2. Regex to extract the raw Tyre Size (e.g., 16X6-8, 5.00-8, 300-15)
        # Looks for digits, an X or dot, and dashes
        size_match = re.search(r'\b\d{1,4}(?:\.\d{1,2})?[X*-]\d{1,4}(?:\.\d{1,2})?(?:[X*-]\d{1,2})?\b|\b\d{3,4}-\d{2}\b', full_text)
        raw_size = size_match.group(0) if size_match else ""

        # 3. Fuzzy Matching against Database
        best_size, size_score = self.fuzzy_match(raw_size, self.known_sizes)
        best_brand, brand_score = self.fuzzy_match(full_text, self.known_brands)

        # Determine Row Color based on confidence
        tag = 'high'
        if size_score < 80 or brand_score < 80: tag = 'med'
        if size_score < 50: tag = 'low'

        self.tree.insert("", "end", values=(full_text[:60]+"...", qty, best_size, f"{size_score}%", best_brand, f"{brand_score}%"), tags=(tag,))

    def fuzzy_match(self, search_term, known_list):
        if not search_term or not known_list: return "UNKNOWN", 0
        matches = difflib.get_close_matches(search_term, known_list, n=1, cutoff=0.1)
        if matches:
            best_match = matches[0]
            score = int(difflib.SequenceMatcher(None, search_term, best_match).ratio() * 100)
            return best_match, score
        return "UNKNOWN", 0

    def on_row_select(self, event):
        sel = self.tree.selection()
        if sel:
            vals = self.tree.item(sel[0])['values']
            self.var_v_size.set(vals[2])
            self.var_v_brand.set(vals[4])

    def update_row(self):
        sel = self.tree.selection()
        if sel:
            item_id = sel[0]
            vals = list(self.tree.item(item_id)['values'])
            vals[2] = self.var_v_size.get()
            vals[3] = "100% (Verified)"
            vals[4] = self.var_v_brand.get()
            vals[5] = "100% (Verified)"
            self.tree.item(item_id, values=vals, tags=('high',))