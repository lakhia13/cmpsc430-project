import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

class CustomerView(tk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.conn = conn
        self.selected_customer_id = None
        
        # Main frame with two columns
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left side - Customer Form
        form_frame = tk.LabelFrame(main_frame, text="Customer Information")
        form_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)
        
        # Customer form
        self.name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        
        form = tk.Frame(form_frame)
        form.pack(padx=10, pady=10)
        
        tk.Label(form, text="Name:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(form, textvariable=self.name_var, width=25).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(form, text="Email:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(form, textvariable=self.email_var, width=25).grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(form, text="Phone:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(form, textvariable=self.phone_var, width=25).grid(row=2, column=1, padx=5, pady=5)
        
        # Buttons frame
        btn_frame = tk.Frame(form_frame)
        btn_frame.pack(pady=10)
        
        self.add_btn = tk.Button(btn_frame, text="Add New Customer", command=self.add_customer)
        self.add_btn.grid(row=0, column=0, padx=5)
        
        self.update_btn = tk.Button(btn_frame, text="Update Customer", command=self.update_customer, state=tk.DISABLED)
        self.update_btn.grid(row=0, column=1, padx=5)
        
        self.delete_btn = tk.Button(btn_frame, text="Delete Customer", command=self.delete_customer, state=tk.DISABLED)
        self.delete_btn.grid(row=0, column=2, padx=5)
        
        self.clear_btn = tk.Button(btn_frame, text="Clear Form", command=self.clear_form)
        self.clear_btn.grid(row=0, column=3, padx=5)
        
        # Right side - Customer List
        list_frame = tk.LabelFrame(main_frame, text="Customer List")
        list_frame.pack(side=tk.RIGHT, fill="both", expand=True, padx=5, pady=5)
        
        # Search frame
        search_frame = tk.Frame(list_frame)
        search_frame.pack(fill='x', padx=10, pady=(10, 0))
        
        tk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_customers)
        tk.Entry(search_frame, textvariable=self.search_var, width=20).pack(side=tk.LEFT, fill='x', expand=True)
        
        # Treeview for customer list
        tree_frame = tk.Frame(list_frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Name", "Email", "Phone"), show="headings", height=10)
        self.tree.pack(side=tk.LEFT, fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Phone", text="Phone")
        
        self.tree.column("ID", width=50)
        self.tree.column("Name", width=150)
        self.tree.column("Email", width=200)
        self.tree.column("Phone", width=100)
        
        self.tree.bind('<<TreeviewSelect>>', self.on_customer_select)
        
        # View customer loans button
        view_loans_btn = tk.Button(list_frame, text="View Customer Loans", command=self.view_customer_loans)
        view_loans_btn.pack(pady=10)
        
        # Populate the customer list
        self.load_customers()

    def load_customers(self):
        """Load all customers into the treeview."""
        # Clear the tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get all customers from database
        cursor = self.conn.cursor()
        cursor.execute("SELECT CustomerID, Name, Email, Phone FROM Customer ORDER BY Name")
        
        for customer in cursor.fetchall():
            self.tree.insert("", "end", values=customer)

    def filter_customers(self, *args):
        """Filter the customer list based on search text."""
        search_text = self.search_var.get().lower()
        
        # Clear the tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get filtered customers
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT CustomerID, Name, Email, Phone FROM Customer 
            WHERE LOWER(Name) LIKE :1 OR LOWER(Email) LIKE :1 OR LOWER(Phone) LIKE :1
            ORDER BY Name
        """, (f'%{search_text}%',))
        
        for customer in cursor.fetchall():
            self.tree.insert("", "end", values=customer)

    def on_customer_select(self, event):
        """Handle customer selection from treeview."""
        selected_items = self.tree.selection()
        if selected_items:
            item = selected_items[0]
            customer_id = self.tree.item(item, "values")[0]
            self.selected_customer_id = customer_id
            
            # Get customer details
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT Name, Email, Phone FROM Customer WHERE CustomerID = :1
            """, (customer_id,))
            
            customer = cursor.fetchone()
            if customer:
                self.name_var.set(customer[0])
                self.email_var.set(customer[1])
                self.phone_var.set(customer[2])
                
                # Enable update and delete buttons
                self.update_btn.config(state=tk.NORMAL)
                self.delete_btn.config(state=tk.NORMAL)
        else:
            self.clear_form()

    def add_customer(self):
        """Add a new customer to the database."""
        name = self.name_var.get().strip()
        email = self.email_var.get().strip()
        phone = self.phone_var.get().strip()
        
        if not (name and email and phone):
            messagebox.showerror("Error", "All fields are required.")
            return
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO Customer (Name, Email, Phone)
                VALUES (:1, :2, :3)
            """, (name, email, phone))
            self.conn.commit()
            messagebox.showinfo("Success", "Customer added successfully.")
            self.clear_form()
            self.load_customers()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def update_customer(self):
        """Update the currently selected customer."""
        if not self.selected_customer_id:
            messagebox.showerror("Error", "No customer selected.")
            return
        
        name = self.name_var.get().strip()
        email = self.email_var.get().strip()
        phone = self.phone_var.get().strip()
        
        if not (name and email and phone):
            messagebox.showerror("Error", "All fields are required.")
            return
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE Customer
                SET Name = :1, Email = :2, Phone = :3
                WHERE CustomerID = :4
            """, (name, email, phone, self.selected_customer_id))
            self.conn.commit()
            messagebox.showinfo("Success", "Customer updated successfully.")
            self.clear_form()
            self.load_customers()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def delete_customer(self):
        """Delete the currently selected customer."""
        if not self.selected_customer_id:
            messagebox.showerror("Error", "No customer selected.")
            return
        
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this customer? This will also delete all associated loans.")
        if not confirm:
            return
        
        try:
            cursor = self.conn.cursor()
            
            # Check if customer has loans
            cursor.execute("SELECT COUNT(*) FROM Loan WHERE CustomerID = :1", (self.selected_customer_id,))
            loan_count = cursor.fetchone()[0]
            
            if loan_count > 0:
                # Get all loan IDs for this customer
                cursor.execute("SELECT LoanID, LoanType FROM Loan WHERE CustomerID = :1", (self.selected_customer_id,))
                loans = cursor.fetchall()
                
                # Delete from specific loan type tables
                for loan_id, loan_type in loans:
                    if loan_type == 'Mortgage':
                        cursor.execute("DELETE FROM MortgageLoan WHERE LoanID = :1", (loan_id,))
                    elif loan_type == 'Auto':
                        cursor.execute("DELETE FROM AutoLoan WHERE LoanID = :1", (loan_id,))
                    elif loan_type == 'Personal':
                        cursor.execute("DELETE FROM PersonalLoan WHERE LoanID = :1", (loan_id,))
                    elif loan_type == 'Student':
                        cursor.execute("DELETE FROM StudentLoan WHERE LoanID = :1", (loan_id,))
                
                # Delete all loans for this customer
                cursor.execute("DELETE FROM Loan WHERE CustomerID = :1", (self.selected_customer_id,))
            
            # Delete the customer
            cursor.execute("DELETE FROM Customer WHERE CustomerID = :1", (self.selected_customer_id,))
            self.conn.commit()
            messagebox.showinfo("Success", "Customer deleted successfully.")
            self.clear_form()
            self.load_customers()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def clear_form(self):
        """Clear the customer form."""
        self.name_var.set("")
        self.email_var.set("")
        self.phone_var.set("")
        self.selected_customer_id = None
        self.update_btn.config(state=tk.DISABLED)
        self.delete_btn.config(state=tk.DISABLED)
        
        # Deselect any selected item in the tree
        for selected_item in self.tree.selection():
            self.tree.selection_remove(selected_item)

    def view_customer_loans(self):
        """Show the loans for the selected customer."""
        if not self.selected_customer_id:
            messagebox.showerror("Error", "No customer selected.")
            return
        
        # Get the customer name
        cursor = self.conn.cursor()
        cursor.execute("SELECT Name FROM Customer WHERE CustomerID = :1", (self.selected_customer_id,))
        customer_name = cursor.fetchone()[0]
        
        # Create a popup window to show the loans
        loan_window = tk.Toplevel(self)
        loan_window.title(f"Loans for {customer_name}")
        loan_window.geometry("800x400")
        
        # Create a treeview to show the loans
        tree_frame = tk.Frame(loan_window)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        loan_tree = ttk.Treeview(tree_frame, columns=("ID", "Type", "Amount", "Interest", "Start", "End", "Status"), show="headings")
        loan_tree.pack(side=tk.LEFT, fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=loan_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        loan_tree.configure(yscrollcommand=scrollbar.set)
        
        loan_tree.heading("ID", text="ID")
        loan_tree.heading("Type", text="Type")
        loan_tree.heading("Amount", text="Amount")
        loan_tree.heading("Interest", text="Interest Rate")
        loan_tree.heading("Start", text="Start Date")
        loan_tree.heading("End", text="End Date")
        loan_tree.heading("Status", text="Status")
        
        loan_tree.column("ID", width=50)
        loan_tree.column("Type", width=100)
        loan_tree.column("Amount", width=100)
        loan_tree.column("Interest", width=100)
        loan_tree.column("Start", width=100)
        loan_tree.column("End", width=100)
        loan_tree.column("Status", width=100)
        
        # Get all loans for this customer
        cursor.execute("""
            SELECT LoanID, LoanType, LoanAmount, InterestRate, 
                   TO_CHAR(StartDate, 'YYYY-MM-DD') as StartDate, 
                   TO_CHAR(EndDate, 'YYYY-MM-DD') as EndDate,
                   CASE
                       WHEN EndDate < SYSDATE THEN 'Closed'
                       ELSE 'Active'
                   END AS Status
            FROM Loan 
            WHERE CustomerID = :1
            ORDER BY StartDate DESC
        """, (self.selected_customer_id,))
        
        for loan in cursor.fetchall():
            loan_tree.insert("", "end", values=loan)
        
        # Add a button to view loan details
        btn_frame = tk.Frame(loan_window)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        def view_loan_details():
            selected_items = loan_tree.selection()
            if not selected_items:
                messagebox.showerror("Error", "No loan selected.")
                return
                
            loan_id = loan_tree.item(selected_items[0], "values")[0]
            loan_type = loan_tree.item(selected_items[0], "values")[1]
            
            # Get general loan details
            cursor.execute("""
                SELECT l.*, c.Name as CustomerName
                FROM Loan l
                JOIN Customer c ON l.CustomerID = c.CustomerID
                WHERE l.LoanID = :1
            """, (loan_id,))
            loan_details = cursor.fetchone()
            
            # Get specific loan type details
            specific_details = None
            if loan_type == "Mortgage":
                cursor.execute("SELECT * FROM MortgageLoan WHERE LoanID = :1", (loan_id,))
                specific_details = cursor.fetchone()
            elif loan_type == "Auto":
                cursor.execute("SELECT * FROM AutoLoan WHERE LoanID = :1", (loan_id,))
                specific_details = cursor.fetchone()
            elif loan_type == "Personal":
                cursor.execute("SELECT * FROM PersonalLoan WHERE LoanID = :1", (loan_id,))
                specific_details = cursor.fetchone()
            elif loan_type == "Student":
                cursor.execute("SELECT * FROM StudentLoan WHERE LoanID = :1", (loan_id,))
                specific_details = cursor.fetchone()
            
            # Display the details in a new window
            details_window = tk.Toplevel(loan_window)
            details_window.title(f"{loan_type} Loan Details")
            details_window.geometry("500x400")
            
            details_frame = tk.Frame(details_window)
            details_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            row = 0
            
            # Display common loan details
            tk.Label(details_frame, text="Loan ID:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", pady=2)
            tk.Label(details_frame, text=str(loan_details[0])).grid(row=row, column=1, sticky="w", pady=2)
            row += 1
            
            tk.Label(details_frame, text="Customer:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", pady=2)
            tk.Label(details_frame, text=loan_details[-1]).grid(row=row, column=1, sticky="w", pady=2)
            row += 1
            
            tk.Label(details_frame, text="Loan Type:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", pady=2)
            tk.Label(details_frame, text=loan_details[2]).grid(row=row, column=1, sticky="w", pady=2)
            row += 1
            
            tk.Label(details_frame, text="Loan Amount:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", pady=2)
            tk.Label(details_frame, text=f"${loan_details[3]:,.2f}").grid(row=row, column=1, sticky="w", pady=2)
            row += 1
            
            tk.Label(details_frame, text="Interest Rate:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", pady=2)
            tk.Label(details_frame, text=f"{loan_details[4]}%").grid(row=row, column=1, sticky="w", pady=2)
            row += 1
            
            tk.Label(details_frame, text="Amount Paid:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", pady=2)
            tk.Label(details_frame, text=f"${loan_details[5]:,.2f}").grid(row=row, column=1, sticky="w", pady=2)
            row += 1
            
            tk.Label(details_frame, text="Start Date:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", pady=2)
            tk.Label(details_frame, text=loan_details[6].strftime("%Y-%m-%d")).grid(row=row, column=1, sticky="w", pady=2)
            row += 1
            
            tk.Label(details_frame, text="End Date:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", pady=2)
            tk.Label(details_frame, text=loan_details[7].strftime("%Y-%m-%d")).grid(row=row, column=1, sticky="w", pady=2)
            row += 1
            
            tk.Label(details_frame, text="Number of Payments:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", pady=2)
            tk.Label(details_frame, text=str(loan_details[8])).grid(row=row, column=1, sticky="w", pady=2)
            row += 1
            
            # Separator
            ttk.Separator(details_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky="ew", pady=10)
            row += 1
            
            tk.Label(details_frame, text="Specific Details:", font=("Arial", 12, "bold")).grid(row=row, column=0, columnspan=2, sticky="w", pady=5)
            row += 1
            
            # Display specific loan type details
            if loan_type == "Mortgage":
                fields = [
                    ("House Address", specific_details[1]),
                    ("House Area (sq ft)", specific_details[2]),
                    ("Number of Bedrooms", specific_details[3]),
                    ("House Price", f"${specific_details[4]:,.2f}")
                ]
            elif loan_type == "Auto":
                fields = [
                    ("Make", specific_details[1]),
                    ("Model", specific_details[2]),
                    ("Year", specific_details[3]),
                    ("VIN", specific_details[4])
                ]
            elif loan_type == "Personal":
                fields = [("Loan Purpose", specific_details[1])]
            elif loan_type == "Student":
                fields = [
                    ("Loan Term", specific_details[1]),
                    ("Disbursement Date", specific_details[2].strftime("%Y-%m-%d")),
                    ("Repayment Start Date", specific_details[3].strftime("%Y-%m-%d")),
                    ("Repayment End Date", specific_details[4].strftime("%Y-%m-%d")),
                    ("Monthly Payment", f"${specific_details[5]:,.2f}"),
                    ("Grace Period (months)", specific_details[6])
                ]
            
            for label, value in fields:
                tk.Label(details_frame, text=f"{label}:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", pady=2)
                tk.Label(details_frame, text=str(value)).grid(row=row, column=1, sticky="w", pady=2)
                row += 1
            
            # Close button
            tk.Button(details_frame, text="Close", command=details_window.destroy).grid(row=row, column=0, columnspan=2, pady=10)
        
        view_btn = tk.Button(btn_frame, text="View Loan Details", command=view_loan_details)
        view_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = tk.Button(btn_frame, text="Close", command=loan_window.destroy)
        close_btn.pack(side=tk.RIGHT, padx=5)