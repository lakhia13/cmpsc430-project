import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import re

class LoanView(tk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.conn = conn
        self.selected_loan_id = None
        
        # Main container with two panels
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill="both", expand=True, padx=10, pady=10)
        
        # === LEFT PANEL - Form for adding/editing loans ===
        self.form_frame = ttk.LabelFrame(main_pane, text="Loan Information")
        main_pane.add(self.form_frame, weight=1)
        
        form_inner = ttk.Frame(self.form_frame)
        form_inner.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Common loan fields
        self.common_frame = ttk.LabelFrame(form_inner, text="General Information")
        self.common_frame.pack(fill="x", expand=False, pady=(0, 10))
        
        # Variables for common fields
        self.customer_id = tk.StringVar()
        self.loan_type = tk.StringVar()
        self.loan_amount = tk.StringVar()
        self.interest_rate = tk.StringVar()
        self.amount_paid = tk.StringVar()
        self.start_date = tk.StringVar()
        self.end_date = tk.StringVar()
        self.num_payments = tk.StringVar()
        
        # Default values
        self.loan_type.set("Mortgage")  # Default loan type
        self.amount_paid.set("0.00")
        self.interest_rate.set("4.5")
        
        # Get today's date in YYYY-MM-DD format
        today = datetime.today().strftime('%Y-%m-%d')
        self.start_date.set(today)
        
        # Common form fields
        common_form_frame = ttk.Frame(self.common_frame)
        common_form_frame.pack(fill="x", expand=True, padx=10, pady=10)
        
        # First column of common fields
        col1 = ttk.Frame(common_form_frame)
        col1.pack(side=tk.LEFT, fill="x", expand=True, padx=(0, 5))
        
        # Customer selection dropdown
        ttk.Label(col1, text="Customer:").grid(row=0, column=0, sticky="w", pady=3)
        self.customer_combo = ttk.Combobox(col1, textvariable=self.customer_id, state="readonly")
        self.customer_combo.grid(row=0, column=1, sticky="ew", pady=3)
        self.load_customers()
        
        ttk.Label(col1, text="Loan Type:").grid(row=1, column=0, sticky="w", pady=3)
        loan_types = ["Mortgage", "Auto", "Personal", "Student"]
        self.loan_type_combo = ttk.Combobox(col1, textvariable=self.loan_type, values=loan_types, state="readonly")
        self.loan_type_combo.grid(row=1, column=1, sticky="ew", pady=3)
        self.loan_type_combo.bind("<<ComboboxSelected>>", self.on_loan_type_change)
        
        ttk.Label(col1, text="Loan Amount ($):").grid(row=2, column=0, sticky="w", pady=3)
        ttk.Entry(col1, textvariable=self.loan_amount).grid(row=2, column=1, sticky="ew", pady=3)
        
        ttk.Label(col1, text="Interest Rate (%):").grid(row=3, column=0, sticky="w", pady=3)
        ttk.Entry(col1, textvariable=self.interest_rate).grid(row=3, column=1, sticky="ew", pady=3)
        
        # Second column of common fields
        col2 = ttk.Frame(common_form_frame)
        col2.pack(side=tk.LEFT, fill="x", expand=True, padx=(5, 0))
        
        ttk.Label(col2, text="Amount Paid ($):").grid(row=0, column=0, sticky="w", pady=3)
        ttk.Entry(col2, textvariable=self.amount_paid).grid(row=0, column=1, sticky="ew", pady=3)
        
        ttk.Label(col2, text="Start Date (YYYY-MM-DD):").grid(row=1, column=0, sticky="w", pady=3)
        ttk.Entry(col2, textvariable=self.start_date).grid(row=1, column=1, sticky="ew", pady=3)
        
        ttk.Label(col2, text="End Date (YYYY-MM-DD):").grid(row=2, column=0, sticky="w", pady=3)
        ttk.Entry(col2, textvariable=self.end_date).grid(row=2, column=1, sticky="ew", pady=3)
        
        ttk.Label(col2, text="Number of Payments:").grid(row=3, column=0, sticky="w", pady=3)
        ttk.Entry(col2, textvariable=self.num_payments).grid(row=3, column=1, sticky="ew", pady=3)
        
        # Create specific loan type frames
        self.specific_frames = {}
        
        # Mortgage loan specific fields
        self.specific_frames["Mortgage"] = self.create_mortgage_frame(form_inner)
        
        # Auto loan specific fields
        self.specific_frames["Auto"] = self.create_auto_frame(form_inner)
        
        # Personal loan specific fields
        self.specific_frames["Personal"] = self.create_personal_frame(form_inner)
        
        # Student loan specific fields
        self.specific_frames["Student"] = self.create_student_frame(form_inner)
        
        # Show only the mortgage frame by default
        self.show_specific_loan_frame("Mortgage")
        
        # Buttons for actions
        btn_frame = ttk.Frame(form_inner)
        btn_frame.pack(fill="x", pady=10)
        
        self.add_btn = ttk.Button(btn_frame, text="Add Loan", command=self.add_loan)
        self.add_btn.pack(side=tk.LEFT, padx=5)
        
        self.update_btn = ttk.Button(btn_frame, text="Update Loan", command=self.update_loan, state="disabled")
        self.update_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_btn = ttk.Button(btn_frame, text="Delete Loan", command=self.delete_loan, state="disabled")
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(btn_frame, text="Clear Form", command=self.clear_form)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # === RIGHT PANEL - Loan List ===
        self.list_frame = ttk.LabelFrame(main_pane, text="Loan List")
        main_pane.add(self.list_frame, weight=1)
        
        # Search bar
        search_frame = ttk.Frame(self.list_frame)
        search_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_loans)
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side=tk.LEFT, fill="x", expand=True)
        
        # Filter by loan type
        ttk.Label(search_frame, text="  Loan Type:").pack(side=tk.LEFT, padx=(10, 5))
        self.filter_type = tk.StringVar()
        self.filter_type.set("All")
        filter_types = ["All", "Mortgage", "Auto", "Personal", "Student"]
        filter_combo = ttk.Combobox(search_frame, textvariable=self.filter_type, values=filter_types, state="readonly", width=10)
        filter_combo.pack(side=tk.LEFT)
        filter_combo.bind("<<ComboboxSelected>>", self.filter_loans)
        
        # Treeview for loan list
        self.tree_frame = ttk.Frame(self.list_frame)
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        columns = ("ID", "Customer", "Type", "Amount", "Interest", "Start Date", "End Date", "Payments")
        self.loan_tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", height=15)
        self.loan_tree.pack(side=tk.LEFT, fill="both", expand=True)
        
        # Set column headings and widths
        self.loan_tree.heading("ID", text="ID")
        self.loan_tree.heading("Customer", text="Customer")
        self.loan_tree.heading("Type", text="Loan Type")
        self.loan_tree.heading("Amount", text="Amount")
        self.loan_tree.heading("Interest", text="Interest")
        self.loan_tree.heading("Start Date", text="Start Date")
        self.loan_tree.heading("End Date", text="End Date")
        self.loan_tree.heading("Payments", text="Payments")
        
        self.loan_tree.column("ID", width=40)
        self.loan_tree.column("Customer", width=150)
        self.loan_tree.column("Type", width=80)
        self.loan_tree.column("Amount", width=80)
        self.loan_tree.column("Interest", width=60)
        self.loan_tree.column("Start Date", width=80)
        self.loan_tree.column("End Date", width=80)
        self.loan_tree.column("Payments", width=60)
        
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.loan_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.loan_tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind select event
        self.loan_tree.bind("<<TreeviewSelect>>", self.on_loan_select)
        
        # Load the loan list
        self.load_loans()

    def load_customers(self):
        """Load customers for the dropdown menu."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT CustomerID, Name FROM Customer ORDER BY Name")
        customers = cursor.fetchall()
        
        # Format as "ID - Name" for display
        customer_list = [f"{cust[0]} - {cust[1]}" for cust in customers]
        self.customer_combo['values'] = customer_list
        
        if customer_list:
            self.customer_combo.current(0)

    def load_loans(self):
        """Load all loans into the treeview."""
        # Clear existing items
        for item in self.loan_tree.get_children():
            self.loan_tree.delete(item)
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT l.LoanID, c.Name, l.LoanType, l.LoanAmount, l.InterestRate,
                   TO_CHAR(l.StartDate, 'YYYY-MM-DD'), TO_CHAR(l.EndDate, 'YYYY-MM-DD'), l.NumPayments
            FROM Loan l
            JOIN Customer c ON l.CustomerID = c.CustomerID
            ORDER BY l.LoanID DESC
        """)
        
        for loan in cursor.fetchall():
            self.loan_tree.insert("", "end", values=loan)

    def filter_loans(self, *args):
        """Filter loans based on search text and loan type."""
        search_text = self.search_var.get().lower()
        loan_type_filter = self.filter_type.get()
        
        # Clear existing items
        for item in self.loan_tree.get_children():
            self.loan_tree.delete(item)
        
        cursor = self.conn.cursor()
        
        # SQL query with appropriate filters
        if loan_type_filter == "All":
            cursor.execute("""
                SELECT l.LoanID, c.Name, l.LoanType, l.LoanAmount, l.InterestRate,
                       TO_CHAR(l.StartDate, 'YYYY-MM-DD'), TO_CHAR(l.EndDate, 'YYYY-MM-DD'), l.NumPayments
                FROM Loan l
                JOIN Customer c ON l.CustomerID = c.CustomerID
                WHERE (LOWER(c.Name) LIKE :1 OR LOWER(l.LoanType) LIKE :1 
                       OR TO_CHAR(l.LoanAmount) LIKE :1 OR TO_CHAR(l.LoanID) LIKE :1)
                ORDER BY l.LoanID DESC
            """, (f'%{search_text}%',))
        else:
            cursor.execute("""
                SELECT l.LoanID, c.Name, l.LoanType, l.LoanAmount, l.InterestRate,
                       TO_CHAR(l.StartDate, 'YYYY-MM-DD'), TO_CHAR(l.EndDate, 'YYYY-MM-DD'), l.NumPayments
                FROM Loan l
                JOIN Customer c ON l.CustomerID = c.CustomerID
                WHERE (LOWER(c.Name) LIKE :1 OR LOWER(l.LoanType) LIKE :1 
                       OR TO_CHAR(l.LoanAmount) LIKE :1 OR TO_CHAR(l.LoanID) LIKE :1)
                AND l.LoanType = :2
                ORDER BY l.LoanID DESC
            """, (f'%{search_text}%', loan_type_filter))
        
        for loan in cursor.fetchall():
            self.loan_tree.insert("", "end", values=loan)

    def create_mortgage_frame(self, parent):
        """Create frame for mortgage-specific fields."""
        frame = ttk.LabelFrame(parent, text="Mortgage Loan Details")
        
        # Mortgage loan variables
        self.house_address = tk.StringVar()
        self.house_area = tk.StringVar()
        self.num_bedrooms = tk.StringVar()
        self.house_price = tk.StringVar()
        
        # Set default values
        self.house_area.set("0")
        self.num_bedrooms.set("3")
        
        form = ttk.Frame(frame)
        form.pack(fill="both", expand=True, padx=10, pady=10)
        
        ttk.Label(form, text="House Address:").grid(row=0, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.house_address, width=40).grid(row=0, column=1, sticky="ew", pady=3)
        
        ttk.Label(form, text="House Area (sq ft):").grid(row=1, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.house_area).grid(row=1, column=1, sticky="ew", pady=3)
        
        ttk.Label(form, text="Number of Bedrooms:").grid(row=2, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.num_bedrooms).grid(row=2, column=1, sticky="ew", pady=3)
        
        ttk.Label(form, text="House Price ($):").grid(row=3, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.house_price).grid(row=3, column=1, sticky="ew", pady=3)
        
        return frame

    def create_auto_frame(self, parent):
        """Create frame for auto loan-specific fields."""
        frame = ttk.LabelFrame(parent, text="Auto Loan Details")
        
        # Auto loan variables
        self.car_make = tk.StringVar()
        self.car_model = tk.StringVar()
        self.car_year = tk.StringVar()
        self.car_vin = tk.StringVar()
        
        # Set default year to current year
        self.car_year.set(str(datetime.today().year))
        
        form = ttk.Frame(frame)
        form.pack(fill="both", expand=True, padx=10, pady=10)
        
        ttk.Label(form, text="Make:").grid(row=0, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.car_make).grid(row=0, column=1, sticky="ew", pady=3)
        
        ttk.Label(form, text="Model:").grid(row=1, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.car_model).grid(row=1, column=1, sticky="ew", pady=3)
        
        ttk.Label(form, text="Year:").grid(row=2, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.car_year).grid(row=2, column=1, sticky="ew", pady=3)
        
        ttk.Label(form, text="VIN:").grid(row=3, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.car_vin).grid(row=3, column=1, sticky="ew", pady=3)
        
        return frame

    def create_personal_frame(self, parent):
        """Create frame for personal loan-specific fields."""
        frame = ttk.LabelFrame(parent, text="Personal Loan Details")
        
        # Personal loan variables
        self.loan_purpose = tk.StringVar()
        
        form = ttk.Frame(frame)
        form.pack(fill="both", expand=True, padx=10, pady=10)
        
        ttk.Label(form, text="Loan Purpose:").grid(row=0, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.loan_purpose, width=40).grid(row=0, column=1, sticky="ew", pady=3)
        
        return frame

    def create_student_frame(self, parent):
        """Create frame for student loan-specific fields."""
        frame = ttk.LabelFrame(parent, text="Student Loan Details")
        
        # Student loan variables
        self.loan_term = tk.StringVar()
        self.disbursement_date = tk.StringVar()
        self.repayment_start_date = tk.StringVar()
        self.repayment_end_date = tk.StringVar()
        self.monthly_payment = tk.StringVar()
        self.grace_period = tk.StringVar()
        
        # Set default values
        today = datetime.today().strftime('%Y-%m-%d')
        self.disbursement_date.set(today)
        self.loan_term.set("4 years")
        self.grace_period.set("6")
        
        form = ttk.Frame(frame)
        form.pack(fill="both", expand=True, padx=10, pady=10)
        
        # First column
        col1 = ttk.Frame(form)
        col1.pack(side=tk.LEFT, fill="x", expand=True, padx=(0, 5))
        
        ttk.Label(col1, text="Loan Term:").grid(row=0, column=0, sticky="w", pady=3)
        ttk.Entry(col1, textvariable=self.loan_term).grid(row=0, column=1, sticky="ew", pady=3)
        
        ttk.Label(col1, text="Disbursement Date:").grid(row=1, column=0, sticky="w", pady=3)
        ttk.Entry(col1, textvariable=self.disbursement_date).grid(row=1, column=1, sticky="ew", pady=3)
        
        ttk.Label(col1, text="Repayment Start Date:").grid(row=2, column=0, sticky="w", pady=3)
        ttk.Entry(col1, textvariable=self.repayment_start_date).grid(row=2, column=1, sticky="ew", pady=3)
        
        # Second column
        col2 = ttk.Frame(form)
        col2.pack(side=tk.LEFT, fill="x", expand=True, padx=(5, 0))
        
        ttk.Label(col2, text="Repayment End Date:").grid(row=0, column=0, sticky="w", pady=3)
        ttk.Entry(col2, textvariable=self.repayment_end_date).grid(row=0, column=1, sticky="ew", pady=3)
        
        ttk.Label(col2, text="Monthly Payment ($):").grid(row=1, column=0, sticky="w", pady=3)
        ttk.Entry(col2, textvariable=self.monthly_payment).grid(row=1, column=1, sticky="ew", pady=3)
        
        ttk.Label(col2, text="Grace Period (months):").grid(row=2, column=0, sticky="w", pady=3)
        ttk.Entry(col2, textvariable=self.grace_period).grid(row=2, column=1, sticky="ew", pady=3)
        
        return frame

    def show_specific_loan_frame(self, loan_type):
        """Show the frame for the selected loan type and hide others."""
        for lt, frame in self.specific_frames.items():
            if lt == loan_type:
                frame.pack(fill="x", expand=False, pady=(0, 10))
            else:
                frame.pack_forget()

    def on_loan_type_change(self, event):
        """Handle loan type selection changes."""
        self.show_specific_loan_frame(self.loan_type.get())

    def get_customer_id_from_combo(self):
        """Extract customer ID from combo box selection."""
        selection = self.customer_combo.get()
        if selection:
            # Extract ID from format "ID - Name"
            return selection.split(' - ')[0]
        return None

    def validate_common_fields(self):
        """Validate the common loan fields."""
        # Check if all required fields are filled
        if not self.get_customer_id_from_combo():
            messagebox.showerror("Error", "Please select a customer")
            return False
        
        if not self.loan_type.get():
            messagebox.showerror("Error", "Please select a loan type")
            return False
        
        # Validate numeric fields
        try:
            amount = float(self.loan_amount.get())
            if amount <= 0:
                messagebox.showerror("Error", "Loan amount must be greater than 0")
                return False
        except ValueError:
            messagebox.showerror("Error", "Loan amount must be a number")
            return False
        
        try:
            rate = float(self.interest_rate.get())
            if rate < 0:
                messagebox.showerror("Error", "Interest rate cannot be negative")
                return False
        except ValueError:
            messagebox.showerror("Error", "Interest rate must be a number")
            return False
        
        try:
            paid = float(self.amount_paid.get())
            if paid < 0:
                messagebox.showerror("Error", "Amount paid cannot be negative")
                return False
        except ValueError:
            messagebox.showerror("Error", "Amount paid must be a number")
            return False
        
        # Validate dates
        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        if not date_pattern.match(self.start_date.get()):
            messagebox.showerror("Error", "Start date must be in format YYYY-MM-DD")
            return False
        
        if not date_pattern.match(self.end_date.get()):
            messagebox.showerror("Error", "End date must be in format YYYY-MM-DD")
            return False
        
        try:
            start = datetime.strptime(self.start_date.get(), '%Y-%m-%d')
            end = datetime.strptime(self.end_date.get(), '%Y-%m-%d')
            if end <= start:
                messagebox.showerror("Error", "End date must be after start date")
                return False
        except ValueError:
            messagebox.showerror("Error", "Invalid date format")
            return False
        
        try:
            payments = int(self.num_payments.get())
            if payments <= 0:
                messagebox.showerror("Error", "Number of payments must be greater than 0")
                return False
        except ValueError:
            messagebox.showerror("Error", "Number of payments must be a number")
            return False
        
        return True

    def validate_mortgage_fields(self):
        """Validate mortgage-specific fields."""
        if not self.house_address.get().strip():
            messagebox.showerror("Error", "House address is required")
            return False
        
        try:
            area = float(self.house_area.get())
            if area <= 0:
                messagebox.showerror("Error", "House area must be greater than 0")
                return False
        except ValueError:
            messagebox.showerror("Error", "House area must be a number")
            return False
        
        try:
            bedrooms = int(self.num_bedrooms.get())
            if bedrooms <= 0:
                messagebox.showerror("Error", "Number of bedrooms must be greater than 0")
                return False
        except ValueError:
            messagebox.showerror("Error", "Number of bedrooms must be a number")
            return False
        
        try:
            price = float(self.house_price.get())
            if price <= 0:
                messagebox.showerror("Error", "House price must be greater than 0")
                return False
        except ValueError:
            messagebox.showerror("Error", "House price must be a number")
            return False
        
        return True

    def validate_auto_fields(self):
        """Validate auto loan-specific fields."""
        if not self.car_make.get().strip():
            messagebox.showerror("Error", "Car make is required")
            return False
        
        if not self.car_model.get().strip():
            messagebox.showerror("Error", "Car model is required")
            return False
        
        try:
            year = int(self.car_year.get())
            current_year = datetime.today().year
            if year < 1900 or year > current_year + 1:
                messagebox.showerror("Error", f"Year must be between 1900 and {current_year + 1}")
                return False
        except ValueError:
            messagebox.showerror("Error", "Year must be a number")
            return False
        
        if not self.car_vin.get().strip():
            messagebox.showerror("Error", "VIN is required")
            return False
        
        return True

    def validate_personal_fields(self):
        """Validate personal loan-specific fields."""
        if not self.loan_purpose.get().strip():
            messagebox.showerror("Error", "Loan purpose is required")
            return False
        
        return True

    def validate_student_fields(self):
        """Validate student loan-specific fields."""
        if not self.loan_term.get().strip():
            messagebox.showerror("Error", "Loan term is required")
            return False
        
        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        
        if not date_pattern.match(self.disbursement_date.get()):
            messagebox.showerror("Error", "Disbursement date must be in format YYYY-MM-DD")
            return False
        
        if not date_pattern.match(self.repayment_start_date.get()):
            messagebox.showerror("Error", "Repayment start date must be in format YYYY-MM-DD")
            return False
        
        if not date_pattern.match(self.repayment_end_date.get()):
            messagebox.showerror("Error", "Repayment end date must be in format YYYY-MM-DD")
            return False
        
        try:
            disbursement = datetime.strptime(self.disbursement_date.get(), '%Y-%m-%d')
            start = datetime.strptime(self.repayment_start_date.get(), '%Y-%m-%d')
            end = datetime.strptime(self.repayment_end_date.get(), '%Y-%m-%d')
            
            if start <= disbursement:
                messagebox.showerror("Error", "Repayment start date must be after disbursement date")
                return False
            
            if end <= start:
                messagebox.showerror("Error", "Repayment end date must be after repayment start date")
                return False
        except ValueError:
            messagebox.showerror("Error", "Invalid date format")
            return False
        
        try:
            payment = float(self.monthly_payment.get())
            if payment <= 0:
                messagebox.showerror("Error", "Monthly payment must be greater than 0")
                return False
        except ValueError:
            messagebox.showerror("Error", "Monthly payment must be a number")
            return False
        
        try:
            grace = int(self.grace_period.get())
            if grace < 0:
                messagebox.showerror("Error", "Grace period cannot be negative")
                return False
        except ValueError:
            messagebox.showerror("Error", "Grace period must be a number")
            return False
        
        return True

    def add_loan(self):
        """Add a new loan to the database."""
        # Validate common fields first
        if not self.validate_common_fields():
            return
        
        # Validate specific fields based on loan type
        loan_type = self.loan_type.get()
        if loan_type == "Mortgage" and not self.validate_mortgage_fields():
            return
        elif loan_type == "Auto" and not self.validate_auto_fields():
            return
        elif loan_type == "Personal" and not self.validate_personal_fields():
            return
        elif loan_type == "Student" and not self.validate_student_fields():
            return
        
        try:
            cursor = self.conn.cursor()
            
            # Insert into Loan table with RETURNING clause
            loan_id_var = cursor.var(int)
            cursor.execute("""
                INSERT INTO Loan (
                    CustomerID, LoanType, LoanAmount, InterestRate, AmountPaid,
                    StartDate, EndDate, NumPayments
                )
                VALUES (:1, :2, :3, :4, :5, TO_DATE(:6, 'YYYY-MM-DD'), TO_DATE(:7, 'YYYY-MM-DD'), :8)
                RETURNING LoanID INTO :9
            """, (
                int(self.get_customer_id_from_combo()),
                self.loan_type.get(),
                float(self.loan_amount.get()),
                float(self.interest_rate.get()),
                float(self.amount_paid.get()),
                self.start_date.get(),
                self.end_date.get(),
                int(self.num_payments.get()),
                loan_id_var
            ))
            
            # Get the loan ID of the newly inserted loan
            loan_id = loan_id_var.getvalue()[0]
            # Insert into specific loan type table
            if loan_type == "Mortgage":
                cursor.execute("""
                    INSERT INTO MortgageLoan (
                        LoanID, HouseAddress, HouseArea, NumBedrooms, HousePrice
                    )
                    VALUES (:1, :2, :3, :4, :5)
                """, (
                    loan_id,
                    self.house_address.get(),
                    float(self.house_area.get()),
                    int(self.num_bedrooms.get()),
                    float(self.house_price.get())
                ))
            elif loan_type == "Auto":
                cursor.execute("""
                    INSERT INTO AutoLoan (
                        LoanID, Make, Model, Year, VIN
                    )
                    VALUES (:1, :2, :3, :4, :5)
                """, (
                    loan_id,
                    self.car_make.get(),
                    self.car_model.get(),
                    int(self.car_year.get()),
                    self.car_vin.get()
                ))
            elif loan_type == "Personal":
                cursor.execute("""
                    INSERT INTO PersonalLoan (
                        LoanID, LoanPurpose
                    )
                    VALUES (:1, :2)
                """, (
                    loan_id,
                    self.loan_purpose.get()
                ))
            elif loan_type == "Student":
                cursor.execute("""
                    INSERT INTO StudentLoan (
                        LoanID, LoanTerm, DisbursementDate, RepaymentStartDate,
                        RepaymentEndDate, MonthlyPayment, GracePeriod
                    )
                    VALUES (:1, :2, TO_DATE(:3, 'YYYY-MM-DD'), TO_DATE(:4, 'YYYY-MM-DD'),
                            TO_DATE(:5, 'YYYY-MM-DD'), :6, :7)
                """, (
                    loan_id,
                    self.loan_term.get(),
                    self.disbursement_date.get(),
                    self.repayment_start_date.get(),
                    self.repayment_end_date.get(),
                    float(self.monthly_payment.get()),
                    int(self.grace_period.get())
                ))
            
            self.conn.commit()
            messagebox.showinfo("Success", f"{loan_type} loan added successfully.")
            self.clear_form()
            self.load_loans()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.conn.rollback()

    def on_loan_select(self, event):
        """Handle loan selection from the loan list."""
        # Get the selected item
        selection = self.loan_tree.selection()
        if not selection:
            return
        
        # Get the loan ID
        loan_id = self.loan_tree.item(selection[0], "values")[0]
        self.selected_loan_id = loan_id
        
        try:
            cursor = self.conn.cursor()
            
            # Get the loan details
            cursor.execute("""
                SELECT l.*, c.Name
                FROM Loan l
                JOIN Customer c ON l.CustomerID = c.CustomerID
                WHERE l.LoanID = :1
            """, (loan_id,))
            
            loan = cursor.fetchone()
            if not loan:
                return
            
            # Fill in the common fields
            customer_name = loan[-1]  # Last column is customer name
            customer_id = loan[1]     # Second column is customer ID
            
            # Update customer dropdown - find the right entry
            for i, cust in enumerate(self.customer_combo['values']):
                if cust.startswith(f"{customer_id} - "):
                    self.customer_combo.current(i)
                    break
            
            # Set the rest of the common fields
            self.loan_type.set(loan[2])
            self.loan_amount.set(str(loan[3]))
            self.interest_rate.set(str(loan[4]))
            self.amount_paid.set(str(loan[5]))
            self.start_date.set(loan[6].strftime("%Y-%m-%d"))
            self.end_date.set(loan[7].strftime("%Y-%m-%d"))
            self.num_payments.set(str(loan[8]))
            
            # Show the appropriate loan type frame
            self.show_specific_loan_frame(loan[2])
            
            # Get the specific loan details based on loan type
            loan_type = loan[2]
            if loan_type == "Mortgage":
                cursor.execute("SELECT * FROM MortgageLoan WHERE LoanID = :1", (loan_id,))
                mortgage = cursor.fetchone()
                if mortgage:
                    self.house_address.set(mortgage[1])
                    self.house_area.set(str(mortgage[2]))
                    self.num_bedrooms.set(str(mortgage[3]))
                    self.house_price.set(str(mortgage[4]))
            elif loan_type == "Auto":
                cursor.execute("SELECT * FROM AutoLoan WHERE LoanID = :1", (loan_id,))
                auto = cursor.fetchone()
                if auto:
                    self.car_make.set(auto[1])
                    self.car_model.set(auto[2])
                    self.car_year.set(str(auto[3]))
                    self.car_vin.set(auto[4])
            elif loan_type == "Personal":
                cursor.execute("SELECT * FROM PersonalLoan WHERE LoanID = :1", (loan_id,))
                personal = cursor.fetchone()
                if personal:
                    self.loan_purpose.set(personal[1])
            elif loan_type == "Student":
                cursor.execute("SELECT * FROM StudentLoan WHERE LoanID = :1", (loan_id,))
                student = cursor.fetchone()
                if student:
                    self.loan_term.set(student[1])
                    self.disbursement_date.set(student[2].strftime("%Y-%m-%d"))
                    self.repayment_start_date.set(student[3].strftime("%Y-%m-%d"))
                    self.repayment_end_date.set(student[4].strftime("%Y-%m-%d"))
                    self.monthly_payment.set(str(student[5]))
                    self.grace_period.set(str(student[6]))
            
            # Enable the update and delete buttons
            self.update_btn.config(state="normal")
            self.delete_btn.config(state="normal")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_loan(self):
        """Update the selected loan."""
        if not self.selected_loan_id:
            messagebox.showerror("Error", "No loan selected.")
            return
        
        # Validate common fields
        if not self.validate_common_fields():
            return
        
        # Validate specific fields based on loan type
        loan_type = self.loan_type.get()
        if loan_type == "Mortgage" and not self.validate_mortgage_fields():
            return
        elif loan_type == "Auto" and not self.validate_auto_fields():
            return
        elif loan_type == "Personal" and not self.validate_personal_fields():
            return
        elif loan_type == "Student" and not self.validate_student_fields():
            return
        
        try:
            cursor = self.conn.cursor()
            
            # Get the current loan type
            cursor.execute("SELECT LoanType FROM Loan WHERE LoanID = :1", (self.selected_loan_id,))
            current_type = cursor.fetchone()[0]
            
            # Update the Loan table
            cursor.execute("""
                UPDATE Loan
                SET CustomerID = :1, LoanType = :2, LoanAmount = :3, InterestRate = :4,
                    AmountPaid = :5, StartDate = TO_DATE(:6, 'YYYY-MM-DD'), 
                    EndDate = TO_DATE(:7, 'YYYY-MM-DD'), NumPayments = :8
                WHERE LoanID = :9
            """, (
                int(self.get_customer_id_from_combo()),
                self.loan_type.get(),
                float(self.loan_amount.get()),
                float(self.interest_rate.get()),
                float(self.amount_paid.get()),
                self.start_date.get(),
                self.end_date.get(),
                int(self.num_payments.get()),
                self.selected_loan_id
            ))
            
            # If loan type has changed, delete from the old type table and insert into the new one
            if current_type != loan_type:
                # Delete from old loan type table
                if current_type == "Mortgage":
                    cursor.execute("DELETE FROM MortgageLoan WHERE LoanID = :1", (self.selected_loan_id,))
                elif current_type == "Auto":
                    cursor.execute("DELETE FROM AutoLoan WHERE LoanID = :1", (self.selected_loan_id,))
                elif current_type == "Personal":
                    cursor.execute("DELETE FROM PersonalLoan WHERE LoanID = :1", (self.selected_loan_id,))
                elif current_type == "Student":
                    cursor.execute("DELETE FROM StudentLoan WHERE LoanID = :1", (self.selected_loan_id,))
            
            # Update or insert into the appropriate loan type table
            if loan_type == "Mortgage":
                # Check if record exists
                cursor.execute("SELECT COUNT(*) FROM MortgageLoan WHERE LoanID = :1", (self.selected_loan_id,))
                exists = cursor.fetchone()[0] > 0
                
                if exists:
                    cursor.execute("""
                        UPDATE MortgageLoan
                        SET HouseAddress = :1, HouseArea = :2, NumBedrooms = :3, HousePrice = :4
                        WHERE LoanID = :5
                    """, (
                        self.house_address.get(),
                        float(self.house_area.get()),
                        int(self.num_bedrooms.get()),
                        float(self.house_price.get()),
                        self.selected_loan_id
                    ))
                else:
                    cursor.execute("""
                        INSERT INTO MortgageLoan (LoanID, HouseAddress, HouseArea, NumBedrooms, HousePrice)
                        VALUES (:1, :2, :3, :4, :5)
                    """, (
                        self.selected_loan_id,
                        self.house_address.get(),
                        float(self.house_area.get()),
                        int(self.num_bedrooms.get()),
                        float(self.house_price.get())
                    ))
            
            elif loan_type == "Auto":
                cursor.execute("SELECT COUNT(*) FROM AutoLoan WHERE LoanID = :1", (self.selected_loan_id,))
                exists = cursor.fetchone()[0] > 0
                
                if exists:
                    cursor.execute("""
                        UPDATE AutoLoan
                        SET Make = :1, Model = :2, Year = :3, VIN = :4
                        WHERE LoanID = :5
                    """, (
                        self.car_make.get(),
                        self.car_model.get(),
                        int(self.car_year.get()),
                        self.car_vin.get(),
                        self.selected_loan_id
                    ))
                else:
                    cursor.execute("""
                        INSERT INTO AutoLoan (LoanID, Make, Model, Year, VIN)
                        VALUES (:1, :2, :3, :4, :5)
                    """, (
                        self.selected_loan_id,
                        self.car_make.get(),
                        self.car_model.get(),
                        int(self.car_year.get()),
                        self.car_vin.get()
                    ))
            
            elif loan_type == "Personal":
                cursor.execute("SELECT COUNT(*) FROM PersonalLoan WHERE LoanID = :1", (self.selected_loan_id,))
                exists = cursor.fetchone()[0] > 0
                
                if exists:
                    cursor.execute("""
                        UPDATE PersonalLoan
                        SET LoanPurpose = :1
                        WHERE LoanID = :2
                    """, (
                        self.loan_purpose.get(),
                        self.selected_loan_id
                    ))
                else:
                    cursor.execute("""
                        INSERT INTO PersonalLoan (LoanID, LoanPurpose)
                        VALUES (:1, :2)
                    """, (
                        self.selected_loan_id,
                        self.loan_purpose.get()
                    ))
            
            elif loan_type == "Student":
                cursor.execute("SELECT COUNT(*) FROM StudentLoan WHERE LoanID = :1", (self.selected_loan_id,))
                exists = cursor.fetchone()[0] > 0
                
                if exists:
                    cursor.execute("""
                        UPDATE StudentLoan
                        SET LoanTerm = :1, DisbursementDate = TO_DATE(:2, 'YYYY-MM-DD'), 
                            RepaymentStartDate = TO_DATE(:3, 'YYYY-MM-DD'), 
                            RepaymentEndDate = TO_DATE(:4, 'YYYY-MM-DD'),
                            MonthlyPayment = :5, GracePeriod = :6
                        WHERE LoanID = :7
                    """, (
                        self.loan_term.get(),
                        self.disbursement_date.get(),
                        self.repayment_start_date.get(),
                        self.repayment_end_date.get(),
                        float(self.monthly_payment.get()),
                        int(self.grace_period.get()),
                        self.selected_loan_id
                    ))
                else:
                    cursor.execute("""
                        INSERT INTO StudentLoan (
                            LoanID, LoanTerm, DisbursementDate, RepaymentStartDate,
                            RepaymentEndDate, MonthlyPayment, GracePeriod
                        )
                        VALUES (:1, :2, TO_DATE(:3, 'YYYY-MM-DD'), TO_DATE(:4, 'YYYY-MM-DD'),
                                TO_DATE(:5, 'YYYY-MM-DD'), :6, :7)
                    """, (
                        self.selected_loan_id,
                        self.loan_term.get(),
                        self.disbursement_date.get(),
                        self.repayment_start_date.get(),
                        self.repayment_end_date.get(),
                        float(self.monthly_payment.get()),
                        int(self.grace_period.get())
                    ))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Loan updated successfully.")
            self.clear_form()
            self.load_loans()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.conn.rollback()

    def delete_loan(self):
        """Delete the selected loan."""
        if not self.selected_loan_id:
            messagebox.showerror("Error", "No loan selected.")
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this loan?"):
            return
        
        try:
            cursor = self.conn.cursor()
            
            # Get the loan type
            cursor.execute("SELECT LoanType FROM Loan WHERE LoanID = :1", (self.selected_loan_id,))
            loan_type = cursor.fetchone()[0]
            
            # Delete from specific loan type table first
            if loan_type == "Mortgage":
                cursor.execute("DELETE FROM MortgageLoan WHERE LoanID = :1", (self.selected_loan_id,))
            elif loan_type == "Auto":
                cursor.execute("DELETE FROM AutoLoan WHERE LoanID = :1", (self.selected_loan_id,))
            elif loan_type == "Personal":
                cursor.execute("DELETE FROM PersonalLoan WHERE LoanID = :1", (self.selected_loan_id,))
            elif loan_type == "Student":
                cursor.execute("DELETE FROM StudentLoan WHERE LoanID = :1", (self.selected_loan_id,))
            
            # Then delete from Loan table
            cursor.execute("DELETE FROM Loan WHERE LoanID = :1", (self.selected_loan_id,))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Loan deleted successfully.")
            self.clear_form()
            self.load_loans()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.conn.rollback()

    def clear_form(self):
        """Clear all form fields."""
        # Clear common fields (keeping customer and loan type selection)
        self.loan_amount.set("")
        self.amount_paid.set("0.00")
        self.interest_rate.set("4.5")
        today = datetime.today().strftime('%Y-%m-%d')
        self.start_date.set(today)
        self.end_date.set("")
        self.num_payments.set("")
        
        # Clear mortgage fields
        self.house_address.set("")
        self.house_area.set("0")
        self.num_bedrooms.set("3")
        self.house_price.set("")
        
        # Clear auto fields
        self.car_make.set("")
        self.car_model.set("")
        self.car_year.set(str(datetime.today().year))
        self.car_vin.set("")
        
        # Clear personal fields
        self.loan_purpose.set("")
        
        # Clear student fields
        self.loan_term.set("4 years")
        self.disbursement_date.set(today)
        self.repayment_start_date.set("")
        self.repayment_end_date.set("")
        self.monthly_payment.set("")
        self.grace_period.set("6")
        
        # Reset selection
        self.selected_loan_id = None
        
        # Disable update and delete buttons
        self.update_btn.config(state="disabled")
        self.delete_btn.config(state="disabled")
        
        # Deselect any selected item in the tree
        for selected_item in self.loan_tree.selection():
            self.loan_tree.selection_remove(selected_item)