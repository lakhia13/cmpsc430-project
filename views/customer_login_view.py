import tkinter as tk
from tkinter import ttk, messagebox

class CustomerLoginView(tk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.conn = conn
        self.parent = parent
        
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Center the login form
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(4, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(2, weight=1)
        
        # Login form
        login_frame = ttk.LabelFrame(self.main_frame, text="Customer Login")
        login_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        
        ttk.Label(login_frame, text="Please enter your credentials to view your loans", 
                 font=("Arial", 10)).pack(pady=(10, 20))
        
        # Email
        email_frame = ttk.Frame(login_frame)
        email_frame.pack(fill="x", padx=20, pady=5)
        ttk.Label(email_frame, text="Email:").pack(side=tk.LEFT)
        self.email_var = tk.StringVar()
        ttk.Entry(email_frame, textvariable=self.email_var, width=30).pack(side=tk.RIGHT)
        
        # Login button
        btn_frame = ttk.Frame(login_frame)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="Login", command=self.login).pack()
        
    def login(self):
        email = self.email_var.get().strip()
        
        if not email:
            messagebox.showerror("Error", "Please enter your email address")
            return
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT CustomerID, Name FROM Customer WHERE Email = :1", (email,))
            customer = cursor.fetchone()
            
            if customer:
                customer_id, customer_name = customer
                self.show_customer_dashboard(customer_id, customer_name)
            else:
                messagebox.showerror("Error", "Email not found. Please check your email and try again.")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
    
    def show_customer_dashboard(self, customer_id, customer_name):
        # Create a new top-level window for the dashboard
        dashboard = tk.Toplevel(self)
        dashboard.title(f"Loan Dashboard - {customer_name}")
        dashboard.geometry("800x500")
        
        # Main container
        main_frame = ttk.Frame(dashboard)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header = ttk.Frame(main_frame)
        header.pack(fill="x")
        
        ttk.Label(header, text=f"Welcome, {customer_name}", font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        ttk.Button(header, text="Logout", command=dashboard.destroy).pack(side=tk.RIGHT)
        
        # Loan list section
        loan_frame = ttk.LabelFrame(main_frame, text="Your Loans")
        loan_frame.pack(fill="both", expand=True, pady=10)
        
        # Create treeview for loans
        columns = ("ID", "Type", "Amount", "Interest", "Start", "End", "Status", "Paid")
        tree = ttk.Treeview(loan_frame, columns=columns, show="headings")
        tree.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(loan_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Set column headings
        tree.heading("ID", text="Loan ID")
        tree.heading("Type", text="Loan Type")
        tree.heading("Amount", text="Amount")
        tree.heading("Interest", text="Interest Rate")
        tree.heading("Start", text="Start Date")
        tree.heading("End", text="End Date") 
        tree.heading("Status", text="Status")
        tree.heading("Paid", text="Amount Paid")
        
        # Column widths
        tree.column("ID", width=50)
        tree.column("Type", width=80)
        tree.column("Amount", width=80)
        tree.column("Interest", width=80)
        tree.column("Start", width=80)
        tree.column("End", width=80)
        tree.column("Status", width=60)
        tree.column("Paid", width=80)
        
        # Load customer's loans
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT LoanID, LoanType, LoanAmount, InterestRate, 
                       TO_CHAR(StartDate, 'YYYY-MM-DD'), TO_CHAR(EndDate, 'YYYY-MM-DD'),
                       CASE
                           WHEN EndDate < SYSDATE THEN 'Closed'
                           ELSE 'Active'
                       END AS Status,
                       AmountPaid
                FROM Loan 
                WHERE CustomerID = :1
                ORDER BY StartDate DESC
            """, (customer_id,))
            
            for loan in cursor.fetchall():
                tree.insert("", "end", values=loan)
            
            # Add buttons below the tree
            btn_frame = ttk.Frame(main_frame)
            btn_frame.pack(fill="x", pady=5)
            
            def view_loan_details():
                selected = tree.selection()
                if not selected:
                    messagebox.showerror("Error", "Please select a loan to view details")
                    return
                
                loan_id = tree.item(selected[0], "values")[0]
                loan_type = tree.item(selected[0], "values")[1]
                
                # Fetch loan details
                cursor.execute("""
                    SELECT * FROM Loan 
                    WHERE LoanID = :1
                """, (loan_id,))
                
                loan_details = cursor.fetchone()
                
                # Fetch specific loan type details
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
                
                # Create detail window
                detail_window = tk.Toplevel(dashboard)
                detail_window.title(f"{loan_type} Loan Details")
                detail_window.geometry("500x400")
                
                detail_frame = ttk.Frame(detail_window)
                detail_frame.pack(fill="both", expand=True, padx=20, pady=20)
                
                # Common loan details
                ttk.Label(detail_frame, text=f"{loan_type} Loan Details", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
                
                row = 1
                
                # Add common loan details
                fields = [
                    ("Loan ID", loan_details[0]),
                    ("Loan Amount", f"${loan_details[3]:,.2f}"),
                    ("Interest Rate", f"{loan_details[4]}%"),
                    ("Amount Paid", f"${loan_details[5]:,.2f}"),
                    ("Start Date", loan_details[6].strftime("%Y-%m-%d")),
                    ("End Date", loan_details[7].strftime("%Y-%m-%d")),
                    ("Number of Payments", loan_details[8])
                ]
                
                for label, value in fields:
                    ttk.Label(detail_frame, text=f"{label}:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", pady=2)
                    ttk.Label(detail_frame, text=str(value)).grid(row=row, column=1, sticky="w", pady=2)
                    row += 1
                
                # Separator
                ttk.Separator(detail_frame, orient="horizontal").grid(row=row, column=0, columnspan=2, sticky="ew", pady=10)
                row += 1
                
                # Specific loan details
                ttk.Label(detail_frame, text="Specific Details", font=("Arial", 11, "bold")).grid(row=row, column=0, columnspan=2, sticky="w", pady=(5, 5))
                row += 1
                
                if loan_type == "Mortgage":
                    specific_fields = [
                        ("House Address", specific_details[1]),
                        ("House Area (sq ft)", specific_details[2]),
                        ("Number of Bedrooms", specific_details[3]),
                        ("House Price", f"${specific_details[4]:,.2f}")
                    ]
                elif loan_type == "Auto":
                    specific_fields = [
                        ("Make", specific_details[1]),
                        ("Model", specific_details[2]),
                        ("Year", specific_details[3]),
                        ("VIN", specific_details[4])
                    ]
                elif loan_type == "Personal":
                    specific_fields = [
                        ("Loan Purpose", specific_details[1])
                    ]
                elif loan_type == "Student":
                    specific_fields = [
                        ("Loan Term", specific_details[1]),
                        ("Disbursement Date", specific_details[2].strftime("%Y-%m-%d")),
                        ("Repayment Start Date", specific_details[3].strftime("%Y-%m-%d")),
                        ("Repayment End Date", specific_details[4].strftime("%Y-%m-%d")),
                        ("Monthly Payment", f"${specific_details[5]:,.2f}"),
                        ("Grace Period (months)", specific_details[6])
                    ]
                
                for label, value in specific_fields:
                    ttk.Label(detail_frame, text=f"{label}:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", pady=2)
                    ttk.Label(detail_frame, text=str(value)).grid(row=row, column=1, sticky="w", pady=2)
                    row += 1
                
                # Close button
                ttk.Button(detail_frame, text="Close", command=detail_window.destroy).grid(row=row, column=0, columnspan=2, pady=15)
            
            ttk.Button(btn_frame, text="View Loan Details", command=view_loan_details).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="Print Statement", command=lambda: messagebox.showinfo("Print", "Statement printing functionality would go here")).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            dashboard.destroy()