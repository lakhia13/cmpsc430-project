import os
import cx_Oracle
from dotenv import load_dotenv

load_dotenv()

def connect():
    """Establish connection to Oracle database using environment variables."""
    try:
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASS")
        dsn = os.getenv("DB_DSN")

        return cx_Oracle.connect(user, password, dsn)
    except cx_Oracle.DatabaseError as e:
        print("Connection failed:", e)
        return None

def create_tables(conn):
    """Create all necessary tables for the loan management system."""
    cursor = conn.cursor()
    
    # Create Customer table
    cursor.execute("""
        BEGIN
           EXECUTE IMMEDIATE 'DROP TABLE MortgageLoan';
        EXCEPTION
           WHEN OTHERS THEN NULL;
        END;
    """)
    cursor.execute("""
        BEGIN
           EXECUTE IMMEDIATE 'DROP TABLE AutoLoan';
        EXCEPTION
           WHEN OTHERS THEN NULL;
        END;
    """)
    cursor.execute("""
        BEGIN
           EXECUTE IMMEDIATE 'DROP TABLE PersonalLoan';
        EXCEPTION
           WHEN OTHERS THEN NULL;
        END;
    """)
    cursor.execute("""
        BEGIN
           EXECUTE IMMEDIATE 'DROP TABLE StudentLoan';
        EXCEPTION
           WHEN OTHERS THEN NULL;
        END;
    """)
    cursor.execute("""
        BEGIN
           EXECUTE IMMEDIATE 'DROP TABLE Loan';
        EXCEPTION
           WHEN OTHERS THEN NULL;
        END;
    """)
    cursor.execute("""
        BEGIN
           EXECUTE IMMEDIATE 'DROP TABLE Customer';
        EXCEPTION
           WHEN OTHERS THEN NULL;
        END;
    """)
    
    # Create Customer table
    cursor.execute("""
        CREATE TABLE Customer (
            CustomerID NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            Name VARCHAR2(100) NOT NULL,
            Email VARCHAR2(100) UNIQUE NOT NULL,
            Phone VARCHAR2(20) NOT NULL,
            RegistrationDate DATE DEFAULT SYSDATE
        )
    """)
    
    # Create Loan table (base table with common fields)
    cursor.execute("""
        CREATE TABLE Loan (
            LoanID NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            CustomerID NUMBER NOT NULL,
            LoanType VARCHAR2(20) NOT NULL,
            LoanAmount NUMBER(15,2) NOT NULL,
            InterestRate NUMBER(5,2) NOT NULL,
            AmountPaid NUMBER(15,2) DEFAULT 0,
            StartDate DATE NOT NULL,
            EndDate DATE NOT NULL,
            NumPayments NUMBER,
            FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID)
        )
    """)
    
    # Create MortgageLoan table
    cursor.execute("""
        CREATE TABLE MortgageLoan (
            LoanID NUMBER PRIMARY KEY,
            HouseAddress VARCHAR2(200) NOT NULL,
            HouseArea NUMBER,
            NumBedrooms NUMBER,
            HousePrice NUMBER(15,2) NOT NULL,
            FOREIGN KEY (LoanID) REFERENCES Loan(LoanID)
        )
    """)
    
    # Create AutoLoan table
    cursor.execute("""
        CREATE TABLE AutoLoan (
            LoanID NUMBER PRIMARY KEY,
            Make VARCHAR2(50) NOT NULL,
            Model VARCHAR2(50) NOT NULL,
            Year NUMBER(4) NOT NULL,
            VIN VARCHAR2(30) UNIQUE NOT NULL,
            FOREIGN KEY (LoanID) REFERENCES Loan(LoanID)
        )
    """)
    
    # Create PersonalLoan table
    cursor.execute("""
        CREATE TABLE PersonalLoan (
            LoanID NUMBER PRIMARY KEY,
            LoanPurpose VARCHAR2(200) NOT NULL,
            FOREIGN KEY (LoanID) REFERENCES Loan(LoanID)
        )
    """)
    
    # Create StudentLoan table
    cursor.execute("""
        CREATE TABLE StudentLoan (
            LoanID NUMBER PRIMARY KEY,
            LoanTerm VARCHAR2(50) NOT NULL,
            DisbursementDate DATE NOT NULL,
            RepaymentStartDate DATE NOT NULL,
            RepaymentEndDate DATE NOT NULL,
            MonthlyPayment NUMBER(10,2) NOT NULL,
            GracePeriod NUMBER,
            FOREIGN KEY (LoanID) REFERENCES Loan(LoanID)
        )
    """)
    
    conn.commit()
    print("Tables created successfully!")

def initialize_sample_data(conn):
    """Insert sample data for testing."""
    cursor = conn.cursor()
    
    # Add sample customers
    cursor.execute("""
        INSERT INTO Customer (Name, Email, Phone)
        VALUES ('John Doe', 'john.doe@example.com', '123-456-7890')
    """)
    cursor.execute("""
        INSERT INTO Customer (Name, Email, Phone)
        VALUES ('Jane Smith', 'jane.smith@example.com', '987-654-3210')
    """)
    
    # Get the generated customer IDs
    cursor.execute("SELECT CustomerID FROM Customer WHERE Name = 'John Doe'")
    john_id = cursor.fetchone()[0]
    
    cursor.execute("SELECT CustomerID FROM Customer WHERE Name = 'Jane Smith'")
    jane_id = cursor.fetchone()[0]
    
    # Add a sample mortgage loan
    cursor.execute("""
        INSERT INTO Loan (CustomerID, LoanType, LoanAmount, InterestRate, AmountPaid, StartDate, EndDate, NumPayments)
        VALUES (:1, 'Mortgage', 250000, 4.5, 20000, TO_DATE('2023-01-01', 'YYYY-MM-DD'), 
                TO_DATE('2053-01-01', 'YYYY-MM-DD'), 360)
    """, (john_id,))
    
    # Get the loan ID for the mortgage
    cursor.execute("SELECT MAX(LoanID) FROM Loan WHERE CustomerID = :1 AND LoanType = 'Mortgage'", (john_id,))
    mortgage_id = cursor.fetchone()[0]
    
    cursor.execute("""
        INSERT INTO MortgageLoan (LoanID, HouseAddress, HouseArea, NumBedrooms, HousePrice)
        VALUES (:1, '123 Main Street, Anytown, USA', 2000, 3, 300000)
    """, (mortgage_id,))
    
    # Add a sample auto loan
    cursor.execute("""
        INSERT INTO Loan (CustomerID, LoanType, LoanAmount, InterestRate, AmountPaid, StartDate, EndDate, NumPayments)
        VALUES (:1, 'Auto', 25000, 3.9, 5000, TO_DATE('2024-01-01', 'YYYY-MM-DD'), 
                TO_DATE('2029-01-01', 'YYYY-MM-DD'), 60)
    """, (jane_id,))
    
    # Get the loan ID for the auto loan
    cursor.execute("SELECT MAX(LoanID) FROM Loan WHERE CustomerID = :1 AND LoanType = 'Auto'", (jane_id,))
    auto_id = cursor.fetchone()[0]
    
    cursor.execute("""
        INSERT INTO AutoLoan (LoanID, Make, Model, Year, VIN)
        VALUES (:1, 'Toyota', 'Camry', 2023, 'ABC12345678901234')
    """, (auto_id,))
    
    conn.commit()
    print("Sample data inserted successfully!")

if __name__ == "__main__":
    conn = connect()
    if conn:
        create_tables(conn)
        initialize_sample_data(conn)
        conn.close()