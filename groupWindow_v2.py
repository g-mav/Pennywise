import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
#from ExpenseSplitterWindow_v2 import ExpenseSplitterWindow

class GroupManager:
    def __init__(self):
        self.conn = sqlite3.connect('group_manager.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                group_id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                member_id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER,
                member_name TEXT NOT NULL,
                FOREIGN KEY (group_id) REFERENCES groups (group_id)
            )
        ''')
        self.conn.commit()

    def create_group(self, group_name):
        self.cursor.execute('INSERT INTO groups (group_name) VALUES (?)', (group_name,))
        self.conn.commit()

    def get_group_members(self, group_id):
        self.cursor.execute('SELECT member_name FROM members WHERE group_id = ?', (group_id,))
        return [row[0] for row in self.cursor.fetchall()]

    def get_group_name(self, group_id):
        self.cursor.execute("SELECT group_name FROM groups WHERE group_id=?", (group_id,))
        result = self.cursor.fetchone()
        return result[0] if result else "Default Group"

    def delete_group(self, group_id):
        try:
            # Delete members first
            self.cursor.execute('DELETE FROM members WHERE group_id = ?', (group_id,))

            # Now, delete the group
            self.cursor.execute('DELETE FROM groups WHERE group_id = ?', (group_id,))

            rows_affected = self.cursor.rowcount
            self.conn.commit()
            return rows_affected > 0  # Return True if at least one row was affected
        except Exception as e:
            print(f"Error deleting group: {e}")
            return False

    def add_member(self, group_id, member_name):
        # Implement the logic to add a member to the database
        self.cursor.execute("INSERT INTO members (group_id, name) VALUES (?, ?)", (group_id, member_name))
        self.connection.commit()

    def get_groups(self):
        self.cursor.execute('SELECT * FROM groups')
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

class GroupWindow(tk.Toplevel):  # Use Toplevel instead of Frame
    def __init__(self, master, group_manager, main_app):
        super().__init__(master)
        self.group_manager = group_manager
        self.main_app = main_app
        self.selected_group_id = None
        self.selected_group_name = None
        self.create_widgets()

    def create_widgets(self):
        self.label_group_name = tk.Label(self, text="Group Name:")
        self.label_group_name.pack(pady=5)

        self.entry_group_name = tk.Entry(self)
        self.entry_group_name.pack(pady=5)

        self.button_create_group = tk.Button(self, text="Create Group", command=self.create_group)
        self.button_create_group.pack(pady=5)

        self.tree_groups = ttk.Treeview(self, columns=("Group ID", "Group Name"))
        self.tree_groups.heading("#0", text="Group ID")
        self.tree_groups.heading("#1", text="Group Name")
        self.tree_groups.pack(pady=10)

        self.button_view_group = tk.Button(self, text="View Group", command=self.view_group)
        self.button_view_group.pack(pady=5)

        self.button_delete_group = tk.Button(self, text="Delete Group", command=self.delete_group)
        self.button_delete_group.pack(pady=5)

        self.populate_groups()

    def create_group(self):
        group_name = self.entry_group_name.get()
        if group_name:
            self.group_manager.create_group(group_name)
            messagebox.showinfo("Group Created", f"Group '{group_name}' created successfully.")
            self.entry_group_name.delete(0, tk.END)
            self.populate_groups()
        else:
            messagebox.showwarning("Error", "Group Name cannot be empty.")

    def view_group(self):
        selected_item = self.tree_groups.selection()
        if selected_item:
            self.selected_group_id, self.selected_group_name = self.tree_groups.item(selected_item, "values")

            # Get group members from the GroupManager
            group_members = self.group_manager.get_group_members(self.selected_group_id)

            # Call open_expense_splitter method of the MainApp instance
            self.main_app.open_expense_splitter(self.selected_group_id, self.selected_group_name, group_members)
        else:
            messagebox.showwarning("Error", "Please select a group.")

    """def on_expense_splitter_close(self, expense_splitter_window):
        # This function is called when ExpenseSplitterWindow is closed
        self.main_app.deiconify()  # Show the main app again
        expense_splitter_window.destroy()"""

    def delete_group(self):
        selected_item = self.tree_groups.selection()
        if selected_item:
            group_id, group_name = self.tree_groups.item(selected_item, "values")
            confirmation = messagebox.askokcancel("Delete Group", f"Do you want to delete group '{group_name}'?")
            if confirmation:
                success = self.group_manager.delete_group(group_id)
                if success:
                    self.populate_groups()
                    messagebox.showinfo("Group Deleted", f"Group '{group_name}' deleted successfully.")
                else:
                    messagebox.showerror("Error", f"Failed to delete group '{group_name}'.")
        else:
            messagebox.showwarning("Error", "Please select a group.")

    def populate_groups(self):
        for item in self.tree_groups.get_children():
            self.tree_groups.delete(item)

        groups = self.group_manager.get_groups()

        for group in groups:
            self.tree_groups.insert("", "end", values=group)

    def close_group_manager(self):
        self.group_manager.close()
        self.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = GroupWindow(root, GroupManager(), None)
    root.mainloop()
