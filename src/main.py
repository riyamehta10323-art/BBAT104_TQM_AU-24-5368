
import re
import tkinter as tk
from tkinter import ttk, messagebox

from src.database import (
    initialize_database,
    add_employee,
    get_all_employees,
    get_employee_by_id,
    search_employees,
    update_employee,
    delete_employee,
)


class EmployeeManagementApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Employee Management System - Q06")
        self.root.geometry("1050x650")
        self.root.minsize(850, 550)

        self.fields = (
            "Employee ID",
            "First Name",
            "Last Name",
            "Department",
            "Email",
            "City",
        )

        self.entries = {}
        self.selected_employee_id = None

        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        heading = ttk.Label(
            self.root,
            text="Employee Management System",
            font=("Arial", 20, "bold"),
        )
        heading.pack(pady=(15, 3))

        subtitle = ttk.Label(
            self.root,
            text="TQM Quality Goal Q06: Reduce Duplicate Entries",
            font=("Arial", 10),
        )
        subtitle.pack(pady=(0, 12))

        # Employee form
        form = ttk.LabelFrame(
            self.root, text="Employee Details", padding=12
        )
        form.pack(fill="x", padx=18, pady=5)

        for index, field in enumerate(self.fields):
            row = index // 3
            column = (index % 3) * 2

            ttk.Label(form, text=field + ":").grid(
                row=row, column=column, padx=6, pady=8, sticky="w"
            )

            entry = ttk.Entry(form, width=25)
            entry.grid(
                row=row, column=column + 1,
                padx=6, pady=8, sticky="ew"
            )
            self.entries[field] = entry

        for column in (1, 3, 5):
            form.columnconfigure(column, weight=1)

        # Action buttons
        actions = ttk.Frame(self.root)
        actions.pack(fill="x", padx=18, pady=8)

        ttk.Button(
            actions, text="Add Employee",
            command=self.add_record
        ).pack(side="left", padx=4)

        ttk.Button(
            actions, text="Update Selected",
            command=self.update_record
        ).pack(side="left", padx=4)

        ttk.Button(
            actions, text="Delete Selected",
            command=self.delete_record
        ).pack(side="left", padx=4)

        ttk.Button(
            actions, text="Clear Form",
            command=self.clear_form
        ).pack(side="left", padx=4)

        # Search bar
        search_frame = ttk.Frame(self.root)
        search_frame.pack(fill="x", padx=18, pady=8)

        ttk.Label(search_frame, text="Search employees:").pack(
            side="left", padx=(0, 8)
        )

        self.search_entry = ttk.Entry(search_frame, width=35)
        self.search_entry.pack(side="left", padx=4)

        ttk.Button(
            search_frame, text="Search",
            command=self.search_records
        ).pack(side="left", padx=4)

        ttk.Button(
            search_frame, text="Show All",
            command=self.refresh_table
        ).pack(side="left", padx=4)

        self.search_entry.bind(
            "<Return>", lambda event: self.search_records()
        )

        # Employee table
        table_frame = ttk.LabelFrame(
            self.root, text="Employee Records", padding=8
        )
        table_frame.pack(
            fill="both", expand=True, padx=18, pady=(4, 12)
        )

        columns = (
            "employee_id", "first_name", "last_name",
            "department", "email", "city"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=12,
        )

        headings = {
            "employee_id": "Employee ID",
            "first_name": "First Name",
            "last_name": "Last Name",
            "department": "Department",
            "email": "Email",
            "city": "City",
        }

        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=135, minwidth=90)

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(
            side="left", fill="both", expand=True
        )
        scrollbar.pack(side="right", fill="y")

        self.tree.bind(
            "<<TreeviewSelect>>", self.select_record
        )

        self.status = ttk.Label(
            self.root, text="Ready", anchor="w"
        )
        self.status.pack(fill="x", padx=20, pady=(0, 8))

    def get_form_values(self):
        values = [
            self.entries[field].get().strip()
            for field in self.fields
        ]

        if not all(values):
            raise ValueError("Please fill in all six fields.")

        email = values[4]
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            raise ValueError("Please enter a valid email address.")

        return values

   
    def clear_form(self):
        # Enable the ID field before clearing it.
        self.entries["Employee ID"].configure(state="normal")

        for entry in self.entries.values():
            entry.delete(0, tk.END)

        self.selected_employee_id = None

        for item in self.tree.selection():
            self.tree.selection_remove(item)

        self.status.config(text="Form cleared")
    def refresh_table(self):
        self.show_records(get_all_employees())
        self.status.config(text="Showing all employees")

    def show_records(self, employees):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for employee in employees:
            self.tree.insert("", tk.END, values=employee)

    def add_record(self):
        try:
            values = self.get_form_values()
            employee_id = values[0]

            # Search by exact ID before attempting to add.
            if get_employee_by_id(employee_id) is not None:
                raise ValueError(
                    f"Employee ID {employee_id} already exists."
                )

            if not messagebox.askyesno(
                "Confirm Addition",
                f"Add employee {values[1]} {values[2]}?"
            ):
                return

            add_employee(*values)
            self.refresh_table()
            self.clear_form()

            messagebox.showinfo(
                "Success", "Employee added successfully."
            )

        except ValueError as error:
            messagebox.showerror("Cannot Add Employee", str(error))

        except Exception as error:
            messagebox.showerror(
                "Error", f"Something went wrong:\n{error}"
            )

    def select_record(self, event=None):
        selected = self.tree.selection()

        if not selected:
            return

        values = self.tree.item(selected[0], "values")
        if not values:
            return

        self.selected_employee_id = values[0]

        for field, value in zip(self.fields, values):
            entry = self.entries[field]
            entry.delete(0, tk.END)
            entry.insert(0, value)

        # The ID identifies the record and should not be edited.
        self.entries["Employee ID"].configure(state="disabled")
        self.status.config(
            text=f"Selected employee: {self.selected_employee_id}"
        )

    def update_record(self):
        if not self.selected_employee_id:
            messagebox.showwarning(
                "Select Employee",
                "Select an employee from the table first."
            )
            return

        try:
            values = self.get_form_values()

            if not messagebox.askyesno(
                "Confirm Update",
                f"Save changes for {self.selected_employee_id}?"
            ):
                return

            update_employee(*values)
            self.refresh_table()
            self.clear_form()

            messagebox.showinfo(
                "Success", "Employee updated successfully."
            )

        except ValueError as error:
            messagebox.showerror("Cannot Update Employee", str(error))

        except Exception as error:
            messagebox.showerror(
                "Error", f"Something went wrong:\n{error}"
            )

    def delete_record(self):
        if not self.selected_employee_id:
            messagebox.showwarning(
                "Select Employee",
                "Select an employee from the table first."
            )
            return

        if not messagebox.askyesno(
            "Confirm Deletion",
            f"Delete employee {self.selected_employee_id}?\n"
            "This action cannot be undone."
        ):
            return

        try:
            delete_employee(self.selected_employee_id)
            self.refresh_table()
            self.clear_form()

            messagebox.showinfo(
                "Success", "Employee deleted successfully."
            )

        except ValueError as error:
            messagebox.showerror("Cannot Delete Employee", str(error))

        except Exception as error:
            messagebox.showerror(
                "Error", f"Something went wrong:\n{error}"
            )

    def search_records(self):
        query = self.search_entry.get().strip()
        self.show_records(search_employees(query))
        self.status.config(
            text=f"Search results for: {query or 'all employees'}"
        )


if __name__ == "__main__":
    initialize_database()

    root = tk.Tk()
    app = EmployeeManagementApp(root)
    root.mainloop()