import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
from groupWindow_v2 import GroupManager

class ExpenseSplitterWindow:
    def __init__(self, master, group_id, group_name, group_members):
        self.master = master
        self.master.title(f"{group_name} - Expense Splitter")

        self.button_add_member_expense = tk.Button(master, text="Add Group Member", command=self.add_member_expense)
        self.button_add_member_expense.grid(row=3, column=5, columnspan=3, pady=2)

        self.group_id = group_id
        self.group_name = group_name
        self.group_members = group_members

        # SQLite database setup
        self.connection = sqlite3.connect("expense_splitter.db")
        self.cursor = self.connection.cursor()
        self.create_tables()

        self.group_expenses = {}
        self.group_members = set()

        self.label_description = tk.Label(master, text="Expense Splitter", font=("Helvetica", 16))
        self.label_description.grid(row=0, column=0, columnspan=3, pady=10)

        self.label_amount = tk.Label(master, text="Amount:")
        self.label_amount.grid(row=1, column=0, padx=10, pady=5, sticky=tk.E)

        self.entry_amount = tk.Entry(master)
        self.entry_amount.grid(row=1, column=1, padx=10, pady=5)

        self.label_paid_by = tk.Label(master, text="Paid by:")
        self.label_paid_by.grid(row=2, column=0, padx=10, pady=5, sticky=tk.E)

        self.entry_paid_by = tk.Entry(master)
        self.entry_paid_by.grid(row=2, column=1, padx=10, pady=5)

        # Move the balances box to the top right
        self.label_balances = tk.Label(master, text="Balances:")
        self.label_balances.grid(row=1, column=5, columnspan=3, pady=5, sticky=tk.W)

        self.text_balances = tk.Text(master, height=10, width=30)
        self.text_balances.grid(row=2, column=3, columnspan=5, padx=10, pady=5)

        self.label_split_among = tk.Label(master, text="Split Among:")
        self.label_split_among.grid(row=3, column=0, padx=2, pady=2, sticky=tk.E)

        self.split_among_var = tk.StringVar()
        self.split_among_checkboxes = {}
        self.update_split_among_checkboxes()

        self.button_add_expense = tk.Button(master, text="Add Expense", command=self.add_expense)
        self.button_add_expense.grid(row=3, column=3, columnspan=3, pady=10)

        # Center the application on the screen initially
        self.center_window()

    def create_tables(self):
        # Create tables if not exists
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER,
                amount REAL,
                paid_by TEXT,
                FOREIGN KEY (group_id) REFERENCES groups(id)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER,
                name TEXT,
                FOREIGN KEY (group_id) REFERENCES groups(id)
            )
        ''')

        self.connection.commit()

    def get_group_members(self):
        self.cursor.execute("SELECT name FROM members WHERE group_id=?", (self.group_id,))
        return [row[0] for row in self.cursor.fetchall()]

    def add_member_expense(self):
        member = simpledialog.askstring("Add Member", "Enter member name:")
        if member:
            # Insert the member into the database
            self.cursor.execute("INSERT INTO members (group_id, name) VALUES (?, ?)", (self.group_id, member))
            self.connection.commit()

            self.group_members.add(member)
            self.update_split_among_checkboxes()
            messagebox.showinfo("Member Added", f"Member '{member}' added to the group.")
        else:
            messagebox.showwarning("Error", "Member Name cannot be empty.")


    def add_expense(self):
        amount = float(self.entry_amount.get())
        paid_by = self.entry_paid_by.get()
        split_among = [member for member, var in self.split_among_checkboxes.items() if var.get() == 1]

        if not paid_by or not split_among:
            messagebox.showwarning("Error", "Please specify the payer and select members to split the expense.")
            return

        if paid_by not in self.group_members:
            messagebox.showwarning("Error",
                                   f"'{paid_by}' is not part of the group. Add the payer as a group member first.")
            return

        # Insert the expense into the database
        self.cursor.execute("INSERT INTO expenses (group_id, amount, paid_by) VALUES (?, ?, ?)", (self.group_id, amount, paid_by))
        self.connection.commit()

        if paid_by not in self.group_expenses:
            self.group_expenses[paid_by] = 0

        self.group_expenses[paid_by] += amount

        share_per_person = amount / len(split_among)
        for member in split_among:
            if member not in self.group_expenses:
                self.group_expenses[member] = 0
            self.group_expenses[member] -= share_per_person

        self.update_balances(paid_by)

    def update_split_among_checkboxes(self):
        # Remove existing checkboxes and labels only in row 3, not the entire column
        for widget in self.master.grid_slaves(row=3, column=1):
            widget.destroy()

        # Create a Frame to act as the table
        table_frame = tk.Frame(self.master)
        table_frame.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)

        row_num = 0
        col_num = 0

        for member in sorted(self.group_members):
            var = tk.IntVar()  # Use IntVar instead of StringVar
            checkbox = tk.Checkbutton(table_frame, text=member, variable=var)
            checkbox.grid(row=row_num, column=col_num, padx=5, pady=2, sticky=tk.W)  # Adjust padx and pady as needed
            self.split_among_checkboxes[member] = var

            col_num += 1
            if col_num >= 3:  # Adjust the number of columns as needed
                col_num = 0
                row_num += 1

        # Adjust row configuration to minimize vertical space
        table_frame.grid_rowconfigure(row_num, weight=1, minsize=1)

    def update_balances(self, paid_by):
        self.text_balances.delete(1.0, tk.END)

        for person, balance in self.group_expenses.items():
            if person != paid_by:
                amount_text = f"₹{abs(balance):.2f}"
                payer_text = f"{person} -> {paid_by}"

                # Determine the color based on the balance
                color = "red" if balance < 0 else "green"

                # Apply color tags only to the amount part
                self.text_balances.tag_configure(color, foreground=color)
                self.text_balances.insert(tk.END, amount_text, color)
                self.text_balances.insert(tk.END, f" {payer_text}\n")

    def center_window(self):
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x_cordinate = int((screen_width / 2) - (600 / 2))
        y_cordinate = int((screen_height / 2) - (500 / 2))
        self.master.geometry("{}x{}+{}+{}".format(600, 500, x_cordinate, y_cordinate))

    def __del__(self):
        # Close the database connection when the application is closed
        self.connection.close()

# ExpenseSplitterWindow_v2.py

if __name__ == "__main__":
    root = tk.Tk()
    group_id_to_open = 1  # Replace this with the actual group_id you want to open

    # Create an instance of GroupManager to fetch group members and name
    group_manager_for_members = GroupManager()

    # Replace the line below with the actual call to fetch group members and name
    group_members_to_open = group_manager_for_members.get_group_members(group_id_to_open)
    group_name_to_open = group_manager_for_members.get_group_name(group_id_to_open)

    # Close the temporary instance of GroupManager
    group_manager_for_members.close()

    app = ExpenseSplitterWindow(root, group_id_to_open, group_name_to_open, group_members_to_open)
    root.mainloop()