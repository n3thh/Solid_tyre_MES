import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from db_manager import DBManager  # <--- The Bridge to Ubuntu

# =================================================
# CONFIGURATION
# =================================================
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# STATION SETTINGS
STATION_ID = "PC1-BUILD"
MACHINE_ID = "M-01"  # You can change this per machine

# =================================================
# DATABASE LOGIC (NO MORE EXCEL!)
# =================================================
def save_to_sql(tyre_id, size, brand, pattern, operator, shift):
    """Sends the data directly to the Ubuntu Server."""
    
    query = """
        INSERT INTO pc1_building 
        (tyre_id, tyre_size, brand, pattern, operator_name, shift, machine_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    params = (tyre_id, size, brand, pattern, operator, shift, MACHINE_ID)
    
    # Execute and check result
    if DBManager.execute_query(query, params):
        return True
    else:
        return False

def check_duplicate(tyre_id):
    """Asks Ubuntu: 'Does this barcode exist already?'"""
    query = "SELECT count(*) FROM pc1_building WHERE tyre_id = %s"
    result = DBManager.fetch_data(query, (tyre_id,))
    
    if result and result[0][0] > 0:
        return True # It exists!
    return False

# =================================================
# UI LOGIC
# =================================================
class PC1App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"PC1 | GREEN TYRE BUILDING | {STATION_ID}")
        self.geometry("600x650")

        # Title
        self.lbl_title = ctk.CTkLabel(self, text="GREEN TYRE REGISTRATION", 
                                      font=("Arial", 24, "bold"), text_color="#3B8ED0")
        self.lbl_title.pack(pady=20)

        # Form Frame
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(pady=10, padx=20, fill="both", expand=True)

        # 1. Barcode (Tyre ID)
        ctk.CTkLabel(self.frame, text="Scan Barcode (Tyre ID):").pack(pady=(15, 5))
        self.ent_barcode = ctk.CTkEntry(self.frame, width=300, placeholder_text="Scan here...")
        self.ent_barcode.pack(pady=5)
        self.ent_barcode.bind("<Return>", self.on_barcode_scan) # Auto-submit on Enter

        # 2. Tyre Size
        ctk.CTkLabel(self.frame, text="Tyre Size:").pack(pady=5)
        self.combo_size = ctk.CTkComboBox(self.frame, width=300, 
                                          values=["18x7-8", "6.00-9", "7.00-12", "23x9-10"])
        self.combo_size.pack(pady=5)

        # 3. Brand
        ctk.CTkLabel(self.frame, text="Brand:").pack(pady=5)
        self.combo_brand = ctk.CTkComboBox(self.frame, width=300, 
                                           values=["TVS", "SOLIDO", "GLOBE_STAR"])
        self.combo_brand.pack(pady=5)
        
        # 4. Pattern
        ctk.CTkLabel(self.frame, text="Pattern:").pack(pady=5)
        self.combo_pattern = ctk.CTkComboBox(self.frame, width=300, 
                                           values=["LUG", "RIB", "SMOOTH"])
        self.combo_pattern.pack(pady=5)

        # 5. Operator
        ctk.CTkLabel(self.frame, text="Operator Name:").pack(pady=5)
        self.ent_operator = ctk.CTkEntry(self.frame, width=300, placeholder_text="Enter ID or Name")
        self.ent_operator.pack(pady=5)

        # 6. Shift
        ctk.CTkLabel(self.frame, text="Shift:").pack(pady=5)
        self.seg_shift = ctk.CTkSegmentedButton(self.frame, values=["A", "B", "C"], width=300)
        self.seg_shift.set("A")
        self.seg_shift.pack(pady=5)

        # Submit Button
        self.btn_submit = ctk.CTkButton(self, text="REGISTER TYRE", command=self.submit_data, 
                                        height=50, font=("Arial", 16, "bold"), fg_color="green")
        self.btn_submit.pack(pady=20, padx=20, fill="x")

        # Status Label
        self.lbl_status = ctk.CTkLabel(self, text="Ready to Scan...", text_color="gray")
        self.lbl_status.pack(pady=5)
        
        self.ent_barcode.focus()

    def on_barcode_scan(self, event):
        self.submit_data()

    def submit_data(self):
        # 1. Get Values
        tyre_id = self.ent_barcode.get().strip()
        size = self.combo_size.get()
        brand = self.combo_brand.get()
        pattern = self.combo_pattern.get()
        operator = self.ent_operator.get().strip()
        shift = self.seg_shift.get()

        # 2. Validate
        if not tyre_id or not operator:
            messagebox.showwarning("Missing Data", "Please scan barcode and enter operator name.")
            return

        # 3. Check Duplicate (SQL Query)
        self.lbl_status.configure(text="Checking Database...", text_color="yellow")
        self.update() # Force UI update
        
        if check_duplicate(tyre_id):
            messagebox.showerror("Duplicate", f"Tyre ID {tyre_id} is ALREADY registered!")
            self.ent_barcode.delete(0, "end")
            self.lbl_status.configure(text="Error: Duplicate Found", text_color="red")
            return

        # 4. Save to SQL
        success = save_to_sql(tyre_id, size, brand, pattern, operator, shift)

        if success:
            # 5. Success Feedback
            print(f"✅ Saved: {tyre_id} | {size} | {operator}")
            self.lbl_status.configure(text=f"Last Saved: {tyre_id}", text_color="#00E676")
            
            # Clear for next
            self.ent_barcode.delete(0, "end")
            self.ent_barcode.focus()
        else:
            messagebox.showerror("Database Error", "Could not connect to Ubuntu Server!\nCheck Wifi.")
            self.lbl_status.configure(text="Connection Failed", text_color="red")

if __name__ == "__main__":
    app = PC1App()
    app.mainloop()