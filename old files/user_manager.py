import tkinter as tk
from tkinter import ttk, messagebox
from db_manager import DBManager

class UserManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin | User Manager")
        self.root.geometry("600x450")
        self.root.configure(bg="#F0F2F5")

        # Header
        tk.Label(root, text="👥 OPERATOR MANAGEMENT", font=("Segoe UI", 16, "bold"), bg="#1A5276", fg="white").pack(fill="x", pady=0, ipady=15)

        # Input Frame
        frame_input = tk.Frame(root, bg="white", padx=20, pady=20)
        frame_input.pack(fill="x", padx=20, pady=20)

        tk.Label(frame_input, text="User ID (e.g., OP-01):", font=("Segoe UI", 10, "bold"), bg="white").grid(row=0, column=0, sticky="w")
        self.ent_id = tk.Entry(frame_input, font=("Segoe UI", 11), bd=2, relief="groove")
        self.ent_id.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        tk.Label(frame_input, text="Full Name:", font=("Segoe UI", 10, "bold"), bg="white").grid(row=1, column=0, sticky="w")
        self.ent_name = tk.Entry(frame_input, font=("Segoe UI", 11), bd=2, relief="groove")
        self.ent_name.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        tk.Label(frame_input, text="Role:", font=("Segoe UI", 10, "bold"), bg="white").grid(row=2, column=0, sticky="w")
        self.combo_role = ttk.Combobox(frame_input, values=["OPERATOR", "SUPERVISOR", "MANAGER"], state="readonly", font=("Segoe UI", 11))
        self.combo_role.current(0)
        self.combo_role.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # Buttons
        btn_frame = tk.Frame(frame_input, bg="white")
        btn_frame.grid(row=3, column=1, pady=15, sticky="e")
        
        tk.Button(btn_frame, text="➕ ADD USER", command=self.add_user, bg="#27AE60", fg="white", font=("Segoe UI", 10, "bold")).pack(side="left", padx=5)
        tk.Button(btn_frame, text="❌ DELETE SELECTED", command=self.delete_user, bg="#C0392B", fg="white", font=("Segoe UI", 10, "bold")).pack(side="left", padx=5)

        # List of Users
        self.tree = ttk.Treeview(root, columns=("ID", "Name", "Role"), show="headings", height=8)
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Full Name")
        self.tree.heading("Role", text="Role")
        self.tree.column("ID", width=100)
        self.tree.column("Name", width=250)
        self.tree.column("Role", width=150)
        self.tree.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.load_users()

    def load_users(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        # Query matching your DB schema
        res = DBManager.fetch_data("SELECT user_id, full_name, role FROM users WHERE is_active=TRUE ORDER BY user_id")
        if res:
            for row in res:
                self.tree.insert("", "end", values=row)

    def add_user(self):
        uid = self.ent_id.get().strip()
        name = self.ent_name.get().strip()
        role = self.combo_role.get()

        if not uid or not name:
            messagebox.showerror("Error", "ID and Name are required!")
            return

        query = """
        INSERT INTO users (user_id, full_name, role, is_active) 
        VALUES (%s, %s, %s, TRUE)
        ON CONFLICT (user_id) DO UPDATE SET full_name=EXCLUDED.full_name, role=EXCLUDED.role, is_active=TRUE;
        """
        if DBManager.execute_query(query, (uid, name, role)):
            messagebox.showinfo("Success", f"User {name} Added!")
            self.ent_id.delete(0, tk.END)
            self.ent_name.delete(0, tk.END)
            self.load_users()
        else:
            messagebox.showerror("Error", "Could not save user.")

    def delete_user(self):
        sel = self.tree.selection()
        if not sel: return
        uid = self.tree.item(sel[0])['values'][0]
        
        if messagebox.askyesno("Confirm", f"Delete user {uid}?"):
            # We don't delete, we just deactivate (Soft Delete)
            query = "UPDATE users SET is_active=FALSE WHERE user_id=%s"
            if DBManager.execute_query(query, (uid,)):
                self.load_users()

if __name__ == "__main__":
    root = tk.Tk()
    app = UserManagerApp(root)
    root.mainloop()