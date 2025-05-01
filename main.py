import os
import tkinter as tk
from tkinter import ttk, messagebox

import cx_Oracle
from dotenv import load_dotenv

from views.customer_view import CustomerView
from views.loan_view import LoanView
from views.customer_login_view import CustomerLoginView
from db import connect, create_tables, initialize_sample_data

load_dotenv()


class LoanManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Loan Management System")
        self.geometry("1200x700")

        # Connect to the database
        self.conn = self.setup_database()
        if not self.conn:
            messagebox.showerror(
                "Database Error", 
                "Could not connect to the database. Please check your configuration."
            )
            self.destroy()
            return

        # Create a notebook (tabbed interface)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)
        
        # Admin views
        admin_frame = ttk.Frame(self.notebook)
        self.notebook.add(admin_frame, text="Admin")
        
        # Customer login view
        customer_login = CustomerLoginView(self.notebook, self.conn)
        self.notebook.add(customer_login, text="Customer Login")
        
        # Admin navigation
        nav_frame = ttk.Frame(admin_frame)
        nav_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(nav_frame, text="Manage Customers", command=lambda: self.show_frame("customers")).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="Manage Loans", command=lambda: self.show_frame("loans")).pack(side=tk.LEFT, padx=5)
        
        # Container for admin views
        self.container = ttk.Frame(admin_frame)
        self.container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initialize views
        self.customer_view = CustomerView(self.container, self.conn)
        self.loan_view = LoanView(self.container, self.conn)
        
        # Show customer view by default
        self.show_frame("customers")
        
        # Bind close event
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_database(self):
        """Connect to the database and set up tables if needed."""
        conn = connect()
        if conn:
            try:
                # Check if tables exist by querying user_tables
                cursor = conn.cursor()
                cursor.execute("SELECT table_name FROM user_tables WHERE table_name = 'CUSTOMER'")
                if not cursor.fetchone():
                    create_tables(conn)
                    initialize_sample_data(conn)
            except Exception as e:
                messagebox.showerror("Database Error", f"Error setting up database: {str(e)}")
        return conn

    def show_frame(self, frame_name):
        """Show the specified frame and hide others."""
        if frame_name == "customers":
            self.loan_view.pack_forget()
            self.customer_view.pack(fill="both", expand=True)
        elif frame_name == "loans":
            self.customer_view.pack_forget()
            self.loan_view.pack(fill="both", expand=True)

    def on_close(self):
        """Clean up before closing the application."""
        try:
            if self.conn:
                self.conn.close()
                print("Database connection closed.")
        except:
            pass
        self.destroy()


if __name__ == "__main__":
    app = LoanManagerApp()
    app.mainloop()