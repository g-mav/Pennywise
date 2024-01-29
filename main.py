# app.py

import tkinter as tk
from groupWindow_v2 import GroupWindow
from ExpenseSplitterWindow_v2 import ExpenseSplitterWindow, GroupManager

class MainApp:
    def __init__(self):
        self.root = tk.Tk()
        self.group_manager = GroupManager()
        self.group_window = GroupWindow(self.root, self.group_manager, self)
        self.root.mainloop()

    def open_expense_splitter(self, group_id, group_name, group_members):
        expense_splitter_window = ExpenseSplitterWindow(self.root, group_id, group_name, group_members)
        expense_splitter_window.wm_protocol("WM_DELETE_WINDOW",
                                            lambda: self.on_expense_splitter_close(expense_splitter_window))
        self.group_window.withdraw()  # Hide the GroupWindow while ExpenseSplitterWindow is open

    def on_expense_splitter_close(self, expense_splitter_window):
        # This function is called when ExpenseSplitterWindow is closed
        self.group_window.deiconify()  # Show the GroupWindow again
        expense_splitter_window.destroy()


if __name__ == "__main__":
    app = MainApp()
