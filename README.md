# Loan Management System

A simple loan management system built with Python and Tkinter that allows administrators to manage customers and various types of loans (mortgage, auto, personal, and student loans).

## Features

- Customer management (add, update, delete)
- Loan management for different loan types
- Customer login functionality
- Oracle database integration

## Requirements

- Python 3.x
- Docker (for running Oracle Database)
- Python packages listed in `requirements.txt`

## Setup Instructions

### 1. Run Oracle Database using Docker

You need to have Docker installed on your system. Run the following command to start an Oracle XE instance:

```bash
docker run -d --name oracle-xe -p 1521:1521 -p 5500:5500 -e ORACLE_PASSWORD=YourPassword123 gvenzl/oracle-xe
```

This will:
- Start an Oracle XE database in a container named `oracle-xe`
- Expose port 1521 for database connections and 5500 for Oracle Enterprise Manager Express
- Set the database system password to `YourPassword123` (change this to a secure password)

Wait a few minutes for the database to initialize completely.

To check if the database container is running:
```bash
docker ps
```

To view container logs:
```bash
docker logs oracle-xe
```

### 2. Set up environment variables

Create a `.env` file in the project root with the following variables:

```
DB_USER=system
DB_PASS=YourPassword123
DB_DSN=localhost:1521/XEPDB1
```

Note: Update the `DB_PASS` to match the password used in the Docker command.

### 3. Set up a Python virtual environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Initialize the database

The application will automatically create the necessary tables and sample data when you first run it.

### 6. Run the application

```bash
python main.py
```

## Usage

- Admin view: Allows management of customers and loans
- Customer login: Allows customers to view their own loans

## Docker Commands Reference

- Stop Oracle container: `docker stop oracle-xe`
- Start existing Oracle container: `docker start oracle-xe`
- Remove Oracle container: `docker rm oracle-xe` (will delete all data)
